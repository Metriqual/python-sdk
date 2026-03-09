"""Prompt Hub API — create, share, and manage prompts."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ._client import HttpClient


class PromptHubAPI:
    """Full Prompt Hub lifecycle — CRUD, sharing, starring, forking, key attachment."""

    def __init__(self, client: HttpClient) -> None:
        self._client = client

    # ── CRUD ──────────────────────────────────────────────────────────

    def create(self, **data: Any) -> Dict[str, Any]:
        return self._client.post("/v1/prompt-hub/prompts", data)

    def list(self) -> List[Dict[str, Any]]:
        return self._client.get("/v1/prompt-hub/prompts")

    def get(self, prompt_id: str) -> Dict[str, Any]:
        return self._client.get(f"/v1/prompt-hub/prompts/{prompt_id}")

    def update(self, prompt_id: str, **data: Any) -> Dict[str, Any]:
        return self._client.patch(f"/v1/prompt-hub/prompts/{prompt_id}", data)

    def delete(self, prompt_id: str) -> Dict[str, Any]:
        return self._client.delete(f"/v1/prompt-hub/prompts/{prompt_id}")

    # ── publish / unpublish ───────────────────────────────────────────

    def publish(self, prompt_id: str) -> Dict[str, Any]:
        return self._client.post(f"/v1/prompt-hub/prompts/{prompt_id}/publish")

    def unpublish(self, prompt_id: str) -> Dict[str, Any]:
        return self._client.post(f"/v1/prompt-hub/prompts/{prompt_id}/unpublish")

    # ── sharing ───────────────────────────────────────────────────────

    def share(self, prompt_id: str, **data: Any) -> Dict[str, Any]:
        return self._client.post(f"/v1/prompt-hub/prompts/{prompt_id}/share", data)

    def list_shares(self, prompt_id: str) -> List[Dict[str, Any]]:
        return self._client.get(f"/v1/prompt-hub/prompts/{prompt_id}/shares")

    def revoke_share(self, prompt_id: str, share_id: str) -> Dict[str, Any]:
        return self._client.delete(f"/v1/prompt-hub/prompts/{prompt_id}/shares/{share_id}")

    def get_shared(self, share_token: str) -> Dict[str, Any]:
        return self._client.get(f"/v1/prompt-hub/shared/{share_token}")

    # ── starring ──────────────────────────────────────────────────────

    def star(self, prompt_id: str) -> Dict[str, Any]:
        return self._client.post(f"/v1/prompt-hub/prompts/{prompt_id}/star")

    def unstar(self, prompt_id: str) -> Dict[str, Any]:
        return self._client.delete(f"/v1/prompt-hub/prompts/{prompt_id}/star")

    def list_starred(self) -> List[Dict[str, Any]]:
        return self._client.get("/v1/prompt-hub/starred")

    # ── forking ───────────────────────────────────────────────────────

    def fork(self, prompt_id: str) -> Dict[str, Any]:
        return self._client.post(f"/v1/prompt-hub/prompts/{prompt_id}/fork")

    # ── proxy key attachment ──────────────────────────────────────────

    def attach_to_key(self, prompt_id: str, proxy_key: str) -> Dict[str, Any]:
        return self._client.post(f"/v1/proxy-keys/{proxy_key}/prompt-hub", {"prompt_id": prompt_id})

    def detach_from_key(self, prompt_id: str, proxy_key: str) -> Dict[str, Any]:
        return self._client.delete(f"/v1/proxy-keys/{proxy_key}/prompt-hub/{prompt_id}")

    def list_key_prompts(self, proxy_key: str) -> List[Dict[str, Any]]:
        return self._client.get(f"/v1/proxy-keys/{proxy_key}/prompt-hub")

    def get_prompts_for_key(self, proxy_key: str) -> List[Dict[str, Any]]:
        return self.list_key_prompts(proxy_key)
