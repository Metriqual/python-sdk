"""Proxy key management API."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ._client import HttpClient


class ProxyKeysAPI:
    """Manage proxy keys for routing requests through Metriqual."""

    def __init__(self, client: HttpClient) -> None:
        self._client = client

    # ── user-scoped ───────────────────────────────────────────────────

    def list(self) -> Dict[str, Any]:
        return self._client.get("/v1/user/proxy-keys")

    def create(
        self,
        *,
        name: str,
        providers: List[Dict[str, Any]],
        filter_ids: Optional[List[str]] = None,
        system_prompt_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        body: Dict[str, Any] = {"name": name, "providers": providers}
        if filter_ids is not None:
            body["filter_ids"] = filter_ids
        if system_prompt_ids is not None:
            body["system_prompt_ids"] = system_prompt_ids
        return self._client.post("/v1/user/proxy-keys", body)

    def get_usage(self, key_id: str) -> Dict[str, Any]:
        return self._client.get(f"/v1/user/proxy-keys/{key_id}/usage")

    def delete(self, key_id: str) -> None:
        self._client.delete(f"/v1/user/proxy-keys/{key_id}")

    def regenerate(self, key_id: str) -> Dict[str, Any]:
        return self._client.post(f"/v1/user/proxy-keys/{key_id}/regenerate")

    def test(self, key_id: str, *, model: Optional[str] = None, messages: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        body: Dict[str, Any] = {}
        if model:
            body["model"] = model
        if messages:
            body["messages"] = messages
        return self._client.post(f"/v1/user/proxy-keys/{key_id}/test", body)

    # ── org-scoped ────────────────────────────────────────────────────

    def list_for_org(self, org_id: str) -> Dict[str, Any]:
        return self._client.get(f"/v1/organizations/{org_id}/proxy-keys")

    def create_for_org(
        self,
        org_id: str,
        *,
        name: str,
        providers: List[Dict[str, Any]],
        filter_ids: Optional[List[str]] = None,
        system_prompt_ids: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        body: Dict[str, Any] = {"name": name, "providers": providers}
        if filter_ids is not None:
            body["filter_ids"] = filter_ids
        if system_prompt_ids is not None:
            body["system_prompt_ids"] = system_prompt_ids
        return self._client.post(f"/v1/organizations/{org_id}/proxy-keys", body)

    def delete_for_org(self, org_id: str, key_id: str) -> None:
        self._client.delete(f"/v1/organizations/{org_id}/proxy-keys/{key_id}")

    def regenerate_for_org(self, org_id: str, key_id: str) -> Dict[str, Any]:
        return self._client.post(f"/v1/organizations/{org_id}/proxy-keys/{key_id}/regenerate")
