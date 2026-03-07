"""Low-level HTTP client with retry, auth, streaming, and binary support."""

from __future__ import annotations

import json
import time
from typing import (
    Any,
    AsyncIterator,
    Dict,
    Iterator,
    Optional,
    Type,
    TypeVar,
)

import httpx

from ._errors import MQLAPIError, MQLConnectionError, MQLTimeoutError

T = TypeVar("T")

_DEFAULT_BASE_URL = "https://api.metriqual.com"
_DEFAULT_TIMEOUT = 30.0
_DEFAULT_MAX_RETRIES = 3
_RETRY_STATUS_CODES = {500, 502, 503, 504, 529}


class HttpClient:
    """Synchronous HTTP client for the Metriqual API."""

    def __init__(
        self,
        *,
        base_url: str = _DEFAULT_BASE_URL,
        api_key: Optional[str] = None,
        token: Optional[str] = None,
        timeout: float = _DEFAULT_TIMEOUT,
        max_retries: int = _DEFAULT_MAX_RETRIES,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.token = token
        self.timeout = timeout
        self.max_retries = max_retries
        self._client = httpx.Client(timeout=timeout)

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> HttpClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    # ── auth ──────────────────────────────────────────────────────────

    def _auth_headers(self) -> Dict[str, str]:
        auth = self.token or self.api_key
        if auth:
            return {"Authorization": f"Bearer {auth}"}
        return {}

    def clone(
        self,
        *,
        api_key: Optional[str] = None,
        token: Optional[str] = None,
    ) -> HttpClient:
        return HttpClient(
            base_url=self.base_url,
            api_key=api_key or self.api_key,
            token=token or self.token,
            timeout=self.timeout,
            max_retries=self.max_retries,
        )

    # ── core request ──────────────────────────────────────────────────

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Any] = None,
        data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        raw: bool = False,
    ) -> Any:
        url = f"{self.base_url}{path}"
        merged_headers = {**self._auth_headers(), **(headers or {})}

        last_exc: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            try:
                resp = self._client.request(
                    method,
                    url,
                    params=_clean_params(params),
                    json=json_body,
                    content=data if isinstance(data, bytes) else None,
                    headers=merged_headers,
                )
                if resp.status_code >= 400:
                    if resp.status_code in _RETRY_STATUS_CODES and attempt < self.max_retries:
                        _backoff(attempt)
                        continue
                    try:
                        body = resp.json()
                    except Exception:
                        body = {"error": resp.text}
                    raise MQLAPIError.from_response(body, resp.status_code)

                if raw:
                    return resp.content
                if not resp.content:
                    return None
                return resp.json()

            except MQLAPIError:
                raise
            except httpx.TimeoutException as exc:
                last_exc = exc
                if attempt < self.max_retries:
                    _backoff(attempt)
                    continue
                raise MQLTimeoutError(str(exc)) from exc
            except httpx.HTTPError as exc:
                last_exc = exc
                if attempt < self.max_retries:
                    _backoff(attempt)
                    continue
                raise MQLConnectionError(str(exc)) from exc

        raise MQLConnectionError(str(last_exc))  # pragma: no cover

    def _request_form(
        self,
        path: str,
        files: Dict[str, Any],
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        url = f"{self.base_url}{path}"
        merged_headers = {**self._auth_headers(), **(headers or {})}
        resp = self._client.post(url, files=files, data=data, headers=merged_headers)
        if resp.status_code >= 400:
            try:
                body = resp.json()
            except Exception:
                body = {"error": resp.text}
            raise MQLAPIError.from_response(body, resp.status_code)
        if not resp.content:
            return None
        return resp.json()

    # ── convenience methods ───────────────────────────────────────────

    def get(self, path: str, params: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        return self._request("GET", path, params=params, **kw)

    def post(self, path: str, body: Optional[Any] = None, **kw: Any) -> Any:
        return self._request("POST", path, json_body=body, **kw)

    def patch(self, path: str, body: Optional[Any] = None, **kw: Any) -> Any:
        return self._request("PATCH", path, json_body=body, **kw)

    def put(self, path: str, body: Optional[Any] = None, **kw: Any) -> Any:
        return self._request("PUT", path, json_body=body, **kw)

    def delete(self, path: str, **kw: Any) -> Any:
        return self._request("DELETE", path, **kw)

    def post_binary(self, path: str, body: Optional[Any] = None, **kw: Any) -> bytes:
        return self._request("POST", path, json_body=body, raw=True, **kw)

    def get_binary(self, path: str, **kw: Any) -> bytes:
        return self._request("GET", path, raw=True, **kw)

    def post_form(
        self,
        path: str,
        files: Dict[str, Any],
        data: Optional[Dict[str, Any]] = None,
        **kw: Any,
    ) -> Any:
        return self._request_form(path, files=files, data=data, **kw)

    # ── streaming (SSE) ───────────────────────────────────────────────

    def stream(
        self,
        path: str,
        body: Any,
        headers: Optional[Dict[str, str]] = None,
    ) -> Iterator[str]:
        url = f"{self.base_url}{path}"
        merged_headers = {**self._auth_headers(), **(headers or {})}
        with self._client.stream(
            "POST", url, json=body, headers=merged_headers
        ) as resp:
            if resp.status_code >= 400:
                resp.read()
                try:
                    err_body = resp.json()
                except Exception:
                    err_body = {"error": resp.text}
                raise MQLAPIError.from_response(err_body, resp.status_code)
            buffer = ""
            for chunk in resp.iter_text():
                buffer += chunk
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            return
                        yield data


class AsyncHttpClient:
    """Async HTTP client for the Metriqual API."""

    def __init__(
        self,
        *,
        base_url: str = _DEFAULT_BASE_URL,
        api_key: Optional[str] = None,
        token: Optional[str] = None,
        timeout: float = _DEFAULT_TIMEOUT,
        max_retries: int = _DEFAULT_MAX_RETRIES,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.token = token
        self.timeout = timeout
        self.max_retries = max_retries
        self._client = httpx.AsyncClient(timeout=timeout)

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> AsyncHttpClient:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    def _auth_headers(self) -> Dict[str, str]:
        auth = self.token or self.api_key
        if auth:
            return {"Authorization": f"Bearer {auth}"}
        return {}

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Any] = None,
        data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        raw: bool = False,
    ) -> Any:
        url = f"{self.base_url}{path}"
        merged_headers = {**self._auth_headers(), **(headers or {})}

        last_exc: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            try:
                resp = await self._client.request(
                    method,
                    url,
                    params=_clean_params(params),
                    json=json_body,
                    content=data if isinstance(data, bytes) else None,
                    headers=merged_headers,
                )
                if resp.status_code >= 400:
                    if resp.status_code in _RETRY_STATUS_CODES and attempt < self.max_retries:
                        _backoff(attempt)
                        continue
                    try:
                        body = resp.json()
                    except Exception:
                        body = {"error": resp.text}
                    raise MQLAPIError.from_response(body, resp.status_code)

                if raw:
                    return resp.content
                if not resp.content:
                    return None
                return resp.json()

            except MQLAPIError:
                raise
            except httpx.TimeoutException as exc:
                last_exc = exc
                if attempt < self.max_retries:
                    _backoff(attempt)
                    continue
                raise MQLTimeoutError(str(exc)) from exc
            except httpx.HTTPError as exc:
                last_exc = exc
                if attempt < self.max_retries:
                    _backoff(attempt)
                    continue
                raise MQLConnectionError(str(exc)) from exc

        raise MQLConnectionError(str(last_exc))  # pragma: no cover

    async def _request_form(
        self,
        path: str,
        files: Dict[str, Any],
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        url = f"{self.base_url}{path}"
        merged_headers = {**self._auth_headers(), **(headers or {})}
        resp = await self._client.post(url, files=files, data=data, headers=merged_headers)
        if resp.status_code >= 400:
            try:
                body = resp.json()
            except Exception:
                body = {"error": resp.text}
            raise MQLAPIError.from_response(body, resp.status_code)
        if not resp.content:
            return None
        return resp.json()

    async def get(self, path: str, params: Optional[Dict[str, Any]] = None, **kw: Any) -> Any:
        return await self._request("GET", path, params=params, **kw)

    async def post(self, path: str, body: Optional[Any] = None, **kw: Any) -> Any:
        return await self._request("POST", path, json_body=body, **kw)

    async def patch(self, path: str, body: Optional[Any] = None, **kw: Any) -> Any:
        return await self._request("PATCH", path, json_body=body, **kw)

    async def put(self, path: str, body: Optional[Any] = None, **kw: Any) -> Any:
        return await self._request("PUT", path, json_body=body, **kw)

    async def delete(self, path: str, **kw: Any) -> Any:
        return await self._request("DELETE", path, **kw)

    async def post_binary(self, path: str, body: Optional[Any] = None, **kw: Any) -> bytes:
        return await self._request("POST", path, json_body=body, raw=True, **kw)

    async def get_binary(self, path: str, **kw: Any) -> bytes:
        return await self._request("GET", path, raw=True, **kw)

    async def post_form(
        self,
        path: str,
        files: Dict[str, Any],
        data: Optional[Dict[str, Any]] = None,
        **kw: Any,
    ) -> Any:
        return await self._request_form(path, files=files, data=data, **kw)

    async def stream(
        self,
        path: str,
        body: Any,
        headers: Optional[Dict[str, str]] = None,
    ) -> AsyncIterator[str]:
        url = f"{self.base_url}{path}"
        merged_headers = {**self._auth_headers(), **(headers or {})}
        async with self._client.stream(
            "POST", url, json=body, headers=merged_headers
        ) as resp:
            if resp.status_code >= 400:
                await resp.aread()
                try:
                    err_body = resp.json()
                except Exception:
                    err_body = {"error": resp.text}
                raise MQLAPIError.from_response(err_body, resp.status_code)
            buffer = ""
            async for chunk in resp.aiter_text():
                buffer += chunk
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            return
                        yield data_str


# ── helpers ──────────────────────────────────────────────────────────────

def _backoff(attempt: int) -> None:
    time.sleep(min(2 ** attempt * 0.5, 8.0))


def _clean_params(params: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if params is None:
        return None
    return {k: v for k, v in params.items() if v is not None}
