"""Provider pricing API."""

from __future__ import annotations

from typing import Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from ._client import HttpClient


class PricingAPI:
    """Retrieve provider pricing information."""

    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def get_by_provider(self, provider: str) -> Dict[str, Any]:
        return self._client.get(f"/{provider}/v1/pricing")

    def get_openai(self) -> Dict[str, Any]:
        return self.get_by_provider("openai")

    def get_anthropic(self) -> Dict[str, Any]:
        return self.get_by_provider("anthropic")

    def get_mistral(self) -> Dict[str, Any]:
        return self.get_by_provider("mistral")

    def get_gemini(self) -> Dict[str, Any]:
        return self.get_by_provider("gemini")

    def get_cohere(self) -> Dict[str, Any]:
        return self.get_by_provider("cohere")
