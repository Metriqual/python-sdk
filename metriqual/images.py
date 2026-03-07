"""Image generation API."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ._client import HttpClient


class ImagesAPI:
    """Generate images via OpenAI-compatible and MiniMax endpoints."""

    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def generate(self, **kwargs: Any) -> Dict[str, Any]:
        """Generate images. Pass ``prompt``, ``model``, ``n``, ``size``, etc."""
        return self._client.post("/v1/images/generations", kwargs)

    def generate_base64(self, **kwargs: Any) -> Dict[str, Any]:
        """Generate images with base64 response format."""
        kwargs["response_format"] = "b64_json"
        return self._client.post("/v1/images/generations", kwargs)

    def generate_urls(self, **kwargs: Any) -> List[str]:
        """Generate images and return a list of URLs."""
        kwargs["response_format"] = "url"
        resp = self._client.post("/v1/images/generations", kwargs)
        return [d["url"] for d in resp.get("data", [])]

    def generate_minimax(self, *, model: str = "image-01", **kwargs: Any) -> Dict[str, Any]:
        """Generate images via MiniMax."""
        body: Dict[str, Any] = {"model": model, **kwargs}
        return self._client.post("/v1/images/minimax/generations", body)
