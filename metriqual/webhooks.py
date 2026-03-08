"""Webhook management API."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ._client import HttpClient


class WebhooksAPI:
    """Manage webhooks for event notifications."""

    def __init__(self, client: HttpClient) -> None:
        self._client = client

    # ── user-scoped ───────────────────────────────────────────────────

    def list(self) -> List[Dict[str, Any]]:
        return self._client.get("/v1/webhooks")

    def create(self, *, url: str, events: List[str], **kwargs: Any) -> Dict[str, Any]:
        return self._client.post("/v1/webhooks", {"url": url, "events": events, **kwargs})

    def update(self, webhook_id: str, **fields: Any) -> Dict[str, Any]:
        return self._client.patch(f"/v1/webhooks/{webhook_id}", fields)

    def delete(self, webhook_id: str) -> None:
        self._client.delete(f"/v1/webhooks/{webhook_id}")

    def get_deliveries(self, webhook_id: str) -> List[Dict[str, Any]]:
        return self._client.get(f"/v1/webhooks/{webhook_id}/deliveries")

    # ── org-scoped ────────────────────────────────────────────────────

    def list_for_org(self, org_id: str) -> List[Dict[str, Any]]:
        return self._client.get(f"/v1/organizations/{org_id}/webhooks")

    def create_for_org(self, org_id: str, *, url: str, events: List[str], **kwargs: Any) -> Dict[str, Any]:
        return self._client.post(f"/v1/organizations/{org_id}/webhooks", {"url": url, "events": events, **kwargs})

    def delete_for_org(self, org_id: str, webhook_id: str) -> None:
        self._client.delete(f"/v1/organizations/{org_id}/webhooks/{webhook_id}")
