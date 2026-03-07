"""Subscription & trial management API."""

from __future__ import annotations

from typing import Any, Dict, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ._client import HttpClient


class SubscriptionAPI:
    """Check subscription status, plan limits, features, and manage trials."""

    def __init__(self, client: HttpClient) -> None:
        self._client = client

    # ── status ────────────────────────────────────────────────────────

    def get_status(self, org_id: Optional[str] = None) -> Dict[str, Any]:
        if org_id:
            return self._client.get(f"/v1/organizations/{org_id}/subscription-status")
        return self._client.get("/v1/user/subscription-status")

    def get_plan_tier(self, org_id: Optional[str] = None) -> str:
        status = self.get_status(org_id)
        return status.get("tier", status.get("plan_tier", "free"))

    def get_limits(self, org_id: Optional[str] = None) -> Dict[str, Any]:
        status = self.get_status(org_id)
        return status.get("limits", {})

    def get_features(self, org_id: Optional[str] = None) -> Dict[str, Any]:
        status = self.get_status(org_id)
        return status.get("features", {})

    def has_feature(self, feature: str, org_id: Optional[str] = None) -> bool:
        features = self.get_features(org_id)
        return bool(features.get(feature))

    # ── trial ─────────────────────────────────────────────────────────

    def get_trial_status(self, org_id: Optional[str] = None) -> Dict[str, Any]:
        if org_id:
            return self._client.get(f"/v1/organizations/{org_id}/trial-status")
        return self._client.get("/v1/user/trial/status")

    def start_trial(
        self,
        *,
        company_name: str,
        company_size: Optional[str] = None,
        phone_number: Optional[str] = None,
        org_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        body: Dict[str, Any] = {"company_name": company_name}
        if company_size is not None:
            body["company_size"] = company_size
        if phone_number is not None:
            body["phone_number"] = phone_number
        body.update(kwargs)
        if org_id:
            return self._client.post(f"/v1/organizations/{org_id}/company-info", body)
        return self._client.post("/v1/user/company-info", body)

    def can_start_trial(self, org_id: Optional[str] = None) -> bool:
        status = self.get_trial_status(org_id)
        return status.get("can_start", False)

    # ── limit checks ─────────────────────────────────────────────────

    def is_at_limit(self, resource: str, org_id: Optional[str] = None) -> bool:
        status = self.get_status(org_id)
        limits = status.get("limits", {})
        usage = status.get("usage", {})
        limit_val = limits.get(resource)
        if limit_val is None or limit_val == "unlimited":
            return False
        current = usage.get(resource, 0)
        return current >= limit_val

    def get_remaining_quota(self, resource: str, org_id: Optional[str] = None) -> Union[int, str]:
        status = self.get_status(org_id)
        limits = status.get("limits", {})
        usage = status.get("usage", {})
        limit_val = limits.get(resource)
        if limit_val is None or limit_val == "unlimited":
            return "unlimited"
        current = usage.get(resource, 0)
        return max(0, limit_val - current)
