"""Webhook endpoint management."""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ._client import HttpClient

WebhookEvent = Literal[
    "failover",
    "circuit_breaker_open",
    "spend_cap_hit",
    "rate_limit_hit",
]


class WebhooksAPI:
    """
    Manage outbound webhook endpoints.

    Metriqual POSTs HMAC-SHA256 signed payloads to your URL when events like
    ``failover`` or ``circuit_breaker_open`` occur.

    Verify the signature::

        import hmac, hashlib
        sig_input = f"{timestamp}.{body}".encode()
        expected = "sha256=" + hmac.new(secret.encode(), sig_input, hashlib.sha256).hexdigest()
        assert hmac.compare_digest(expected, request.headers["X-MQL-Signature"])
    """

    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def list(self) -> List[Dict[str, Any]]:
        """Return all webhook endpoints for the authenticated user."""
        return self._client.get("/v1/user/webhooks")

    def create(
        self,
        *,
        url: str,
        events: Optional[List[WebhookEvent]] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a webhook endpoint. The signing secret is auto-generated.

        Example::

            wh = mql.webhooks.create(
                url="https://api.example.com/mql",
                events=["failover", "circuit_breaker_open"],
                description="PagerDuty bridge",
            )
            print(wh["secret_preview"])  # whsec_...****
        """
        body: Dict[str, Any] = {"url": url}
        if events is not None:
            body["events"] = events
        if description is not None:
            body["description"] = description
        return self._client.post("/v1/user/webhooks", body)

    def update(self, webhook_id: str, **fields: Any) -> Dict[str, Any]:
        """
        Update a webhook endpoint.

        Example::

            mql.webhooks.update("wh_id", enabled=False)
        """
        return self._client.patch(f"/v1/user/webhooks/{webhook_id}", fields)

    def delete(self, webhook_id: str) -> None:
        """Delete a webhook endpoint."""
        self._client.delete(f"/v1/user/webhooks/{webhook_id}")

    def test(self, webhook_id: str) -> Dict[str, Any]:
        """
        Send a test event to verify the endpoint is reachable.

        Returns ``{"success": bool, "status_code": int}``.
        """
        return self._client.post(f"/v1/user/webhooks/{webhook_id}/test", {})
