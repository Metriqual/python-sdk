"""Music generation API."""

from __future__ import annotations

from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ._client import HttpClient


class MusicAPI:
    """Generate music via Metriqual."""

    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def generate(self, **kwargs: Any) -> Dict[str, Any]:
        """Submit a music generation request. Pass ``model``, ``prompt``, ``lyrics``, etc."""
        return self._client.post("/v1/music/generations", kwargs)

    def generate_from_prompt(self, prompt: str) -> Dict[str, Any]:
        """Generate music from a text prompt."""
        return self._client.post("/v1/music/generations", {"prompt": prompt})

    def generate_with_lyrics(self, prompt: str, lyrics: str) -> Dict[str, Any]:
        """Generate music with custom lyrics."""
        return self._client.post("/v1/music/generations", {"prompt": prompt, "lyrics": lyrics})
