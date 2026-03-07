"""Organizations API — teams, members, invitations."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ._client import HttpClient


class OrganizationsAPI:
    """Manage organizations, members, and invitations."""

    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def list(self) -> Dict[str, Any]:
        return self._client.get("/v1/organizations")

    def get(self, org_id: str) -> Dict[str, Any]:
        return self._client.get(f"/v1/organizations/{org_id}")

    def create(self, *, display_name: str, **fields: Any) -> Dict[str, Any]:
        return self._client.post("/v1/organizations", {"display_name": display_name, **fields})

    # ── members ───────────────────────────────────────────────────────

    def list_members(self, org_id: str) -> List[Dict[str, Any]]:
        return self._client.get(f"/v1/organizations/{org_id}/members")

    def update_member_role(self, org_id: str, user_id: str, *, role: str) -> None:
        self._client.patch(f"/v1/organizations/{org_id}/members/{user_id}", {"role": role})

    def remove_member(self, org_id: str, user_id: str) -> None:
        self._client.delete(f"/v1/organizations/{org_id}/members/{user_id}")

    # ── invites ───────────────────────────────────────────────────────

    def list_invites(self, org_id: str) -> List[Dict[str, Any]]:
        return self._client.get(f"/v1/organizations/{org_id}/invites")

    def invite_member(self, org_id: str, *, email: str, role: str = "member") -> Dict[str, Any]:
        return self._client.post(f"/v1/organizations/{org_id}/invites", {"email": email, "role": role})

    def resend_invite(self, org_id: str, invite_id: str) -> None:
        self._client.post(f"/v1/organizations/{org_id}/invites/{invite_id}/resend")

    def cancel_invite(self, org_id: str, invite_id: str) -> None:
        self._client.delete(f"/v1/organizations/{org_id}/invites/{invite_id}")

    def get_my_invites(self) -> List[Dict[str, Any]]:
        return self._client.get("/v1/invites/pending")

    def accept_invite(self, *, invite_id: str) -> Dict[str, Any]:
        return self._client.post("/v1/invites/accept", {"invite_id": invite_id})
