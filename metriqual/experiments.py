"""A/B testing experiments API."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ._client import HttpClient


class ExperimentsAPI:
    """Create and manage A/B testing experiments."""

    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def create(self, **data: Any) -> Dict[str, Any]:
        return self._client.post("/v1/experiments", data)

    def list(self) -> List[Dict[str, Any]]:
        return self._client.get("/v1/experiments")

    def get(self, experiment_id: str) -> Dict[str, Any]:
        return self._client.get(f"/v1/experiments/{experiment_id}")

    def update(self, experiment_id: str, **data: Any) -> Dict[str, Any]:
        return self._client.patch(f"/v1/experiments/{experiment_id}", data)

    def delete(self, experiment_id: str) -> Dict[str, Any]:
        return self._client.delete(f"/v1/experiments/{experiment_id}")

    def start(self, experiment_id: str) -> Dict[str, Any]:
        return self._client.post(f"/v1/experiments/{experiment_id}/start")

    def pause(self, experiment_id: str) -> Dict[str, Any]:
        return self._client.post(f"/v1/experiments/{experiment_id}/pause")

    def complete(self, experiment_id: str) -> Dict[str, Any]:
        return self._client.post(f"/v1/experiments/{experiment_id}/complete")

    # ── variants ──────────────────────────────────────────────────────

    def create_variant(self, experiment_id: str, **data: Any) -> Dict[str, Any]:
        return self._client.post(f"/v1/experiments/{experiment_id}/variants", data)

    def update_variant(self, experiment_id: str, variant_id: str, **data: Any) -> Dict[str, Any]:
        return self._client.patch(f"/v1/experiments/{experiment_id}/variants/{variant_id}", data)

    def delete_variant(self, experiment_id: str, variant_id: str) -> Dict[str, Any]:
        return self._client.delete(f"/v1/experiments/{experiment_id}/variants/{variant_id}")

    def get_analytics(self, experiment_id: str) -> Dict[str, Any]:
        return self._client.get(f"/v1/experiments/{experiment_id}/analytics")
