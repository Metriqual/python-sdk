"""Content filters API."""

from __future__ import annotations

from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ._client import HttpClient


class FiltersAPI:
    """Manage content filters applied to proxy keys."""

    def __init__(self, client: HttpClient) -> None:
        self._client = client

    # ── user-scoped ───────────────────────────────────────────────────

    def list(self) -> Dict[str, Any]:
        return self._client.get("/v1/user/filters")

    def create(
        self,
        *,
        name: str,
        filter_type: str,
        pattern: str,
        action: str,
        apply_to: Optional[str] = None,
    ) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "name": name,
            "filter_type": filter_type,
            "pattern": pattern,
            "action": action,
        }
        if apply_to is not None:
            body["apply_to"] = apply_to
        return self._client.post("/v1/user/filters", body)

    def update(self, filter_id: str, **fields: Any) -> Dict[str, Any]:
        return self._client.patch(f"/v1/user/filters/{filter_id}", fields)

    def toggle(self, filter_id: str) -> Dict[str, Any]:
        return self._client.post(f"/v1/user/filters/{filter_id}/toggle")

    def delete(self, filter_id: str) -> None:
        self._client.delete(f"/v1/user/filters/{filter_id}")

    def get_templates(self) -> Dict[str, Any]:
        return self._client.get("/v1/filters/templates")

    def create_from_template(self, *, template_id: str, proxy_key_id: Optional[str] = None) -> Dict[str, Any]:
        body: Dict[str, Any] = {"template_id": template_id}
        if proxy_key_id is not None:
            body["proxy_key_id"] = proxy_key_id
        return self._client.post("/v1/filters/from-template", body)

    def test(self, *, test_content: str, filter_type: str, pattern: str, action: str) -> Dict[str, Any]:
        return self._client.post("/v1/filters/test", {
            "test_content": test_content,
            "filter_type": filter_type,
            "pattern": pattern,
            "action": action,
        })

    # ── org-scoped ────────────────────────────────────────────────────

    def list_for_org(self, org_id: str) -> Dict[str, Any]:
        return self._client.get(f"/v1/organizations/{org_id}/filters")

    def create_for_org(self, org_id: str, **fields: Any) -> Dict[str, Any]:
        return self._client.post(f"/v1/organizations/{org_id}/filters", fields)
