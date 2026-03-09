"""Model listing API."""

from __future__ import annotations

from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ._client import HttpClient


class ModelsAPI:
    """List available models by provider."""

    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def list(self, provider: str = "openai") -> Dict[str, Any]:
        return self._client.get(f"/{provider}/v1/pricing")

    def list_by_provider(self, provider: str) -> Dict[str, Any]:
        return self._client.get(f"/{provider}/v1/pricing")

    def get(self, model_id: str, provider: str = "openai") -> Optional[Dict[str, Any]]:
        """Get a specific model by ID (client-side filter)."""
        resp = self.list(provider)
        for model in resp.get("data", []):
            if model.get("id") == model_id:
                return model
        return None
