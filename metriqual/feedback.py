"""User feedback API."""

from __future__ import annotations

from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ._client import HttpClient


class FeedbackAPI:
    """Submit and retrieve user feedback on AI responses."""

    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def submit(self, **data: Any) -> Dict[str, Any]:
        """Submit feedback (``request_id``, ``rating``, ``comment``, etc.)."""
        return self._client.post("/v1/feedback", data)

    def get(self, request_id: str) -> Dict[str, Any]:
        return self._client.get(f"/v1/feedback/{request_id}")

    def get_analytics(
        self,
        *,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {**kwargs}
        if start_date is not None:
            params["start_date"] = start_date
        if end_date is not None:
            params["end_date"] = end_date
        return self._client.get("/v1/feedback/analytics", params or None)

    def export(
        self,
        *,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        format: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Export feedback data (returns raw text/CSV)."""
        params: Dict[str, Any] = {**kwargs}
        if start_date is not None:
            params["start_date"] = start_date
        if end_date is not None:
            params["end_date"] = end_date
        if format is not None:
            params["format"] = format
        headers = {"Accept": "text/csv"} if format == "csv" else None
        return self._client.get("/v1/feedback/export", params or None, headers=headers)
