"""Usage analytics API."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ._client import HttpClient


class AnalyticsAPI:
    """Access usage analytics, timeseries, and provider stats."""

    def __init__(self, client: HttpClient) -> None:
        self._client = client

    # ── user-scoped ───────────────────────────────────────────────────

    def get_overview(
        self,
        *,
        start_date: Optional[Union[str, date, datetime]] = None,
        end_date: Optional[Union[str, date, datetime]] = None,
    ) -> Dict[str, Any]:
        return self._client.get("/v1/analytics/overview", _date_params(start_date, end_date))

    def get_timeseries(
        self,
        *,
        start_date: Optional[Union[str, date, datetime]] = None,
        end_date: Optional[Union[str, date, datetime]] = None,
    ) -> List[Dict[str, Any]]:
        return self._client.get("/v1/analytics/timeseries", _date_params(start_date, end_date))

    def get_provider_stats(self) -> List[Dict[str, Any]]:
        return self._client.get("/v1/analytics/providers")

    def get_usage_logs(self, proxy_key_id: str) -> Dict[str, Any]:
        return self._client.get(f"/v1/user/proxy-keys/{proxy_key_id}/logs")

    def get_usage_analytics(self, proxy_key_id: str) -> Dict[str, Any]:
        return self._client.get(f"/v1/user/proxy-keys/{proxy_key_id}/usage")

    # ── org-scoped ────────────────────────────────────────────────────

    def get_org_overview(
        self,
        org_id: str,
        *,
        start_date: Optional[Union[str, date, datetime]] = None,
        end_date: Optional[Union[str, date, datetime]] = None,
    ) -> Dict[str, Any]:
        return self._client.get(f"/v1/organizations/{org_id}/analytics/overview", _date_params(start_date, end_date))

    def get_org_timeseries(
        self,
        org_id: str,
        *,
        start_date: Optional[Union[str, date, datetime]] = None,
        end_date: Optional[Union[str, date, datetime]] = None,
    ) -> List[Dict[str, Any]]:
        return self._client.get(f"/v1/organizations/{org_id}/analytics/timeseries", _date_params(start_date, end_date))

    def get_org_provider_stats(self, org_id: str) -> List[Dict[str, Any]]:
        return self._client.get(f"/v1/organizations/{org_id}/analytics/providers")


def _date_params(
    start_date: Optional[Union[str, date, datetime]],
    end_date: Optional[Union[str, date, datetime]],
) -> Optional[Dict[str, str]]:
    params: Dict[str, str] = {}
    if start_date is not None:
        params["start_date"] = start_date.isoformat() if isinstance(start_date, (date, datetime)) else start_date
    if end_date is not None:
        params["end_date"] = end_date.isoformat() if isinstance(end_date, (date, datetime)) else end_date
    return params or None
