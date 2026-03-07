"""Video generation API."""

from __future__ import annotations

import time
from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ._client import HttpClient


class VideoAPI:
    """Generate and manage AI videos."""

    def __init__(self, client: HttpClient) -> None:
        self._client = client

    # ── core ──────────────────────────────────────────────────────────

    def create(self, **kwargs: Any) -> Dict[str, Any]:
        """Submit a video generation request."""
        return self._client.post("/v1/videos/generations", kwargs)

    def get_status(self, video_id: str) -> Dict[str, Any]:
        return self._client.get(f"/v1/videos/generations/{video_id}")

    def download(self, video_id: str) -> bytes:
        return self._client.get_binary(f"/v1/videos/{video_id}/content")

    def create_and_wait(
        self,
        *,
        poll_interval: float = 5.0,
        max_wait: float = 600.0,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Submit, poll until complete, return final status."""
        resp = self.create(**kwargs)
        video_id = resp.get("id") or resp.get("video_id") or resp.get("task_id")
        deadline = time.monotonic() + max_wait
        while time.monotonic() < deadline:
            status = self.get_status(video_id)
            st = status.get("status", "").lower()
            if st in ("completed", "success", "succeeded"):
                return status
            if st in ("failed", "error"):
                raise RuntimeError(f"Video generation failed: {status}")
            time.sleep(poll_interval)
        raise TimeoutError(f"Video generation did not complete within {max_wait}s")

    def create_and_download(
        self,
        *,
        poll_interval: float = 5.0,
        max_wait: float = 600.0,
        **kwargs: Any,
    ) -> bytes:
        """Submit, poll, and download the final video bytes."""
        status = self.create_and_wait(poll_interval=poll_interval, max_wait=max_wait, **kwargs)
        video_id = status.get("id") or status.get("video_id")
        return self.download(video_id)

    # ── MiniMax task-based ────────────────────────────────────────────

    def query_video_status(self, task_id: str, *, include_download_url: bool = False) -> Dict[str, Any]:
        params = {"include_download_url": "true"} if include_download_url else None
        return self._client.get(f"/v1/videos/query/{task_id}", params)

    def download_video(self, file_id: str) -> Dict[str, Any]:
        return self._client.get(f"/v1/videos/download/{file_id}")

    def query_and_wait(
        self,
        task_id: str,
        *,
        poll_interval: float = 5.0,
        max_wait: float = 600.0,
    ) -> Dict[str, Any]:
        """Poll a MiniMax video task until complete."""
        deadline = time.monotonic() + max_wait
        while time.monotonic() < deadline:
            status = self.query_video_status(task_id, include_download_url=True)
            st = status.get("status", "").lower()
            if st in ("completed", "success", "succeeded"):
                return status
            if st in ("failed", "error"):
                raise RuntimeError(f"Video task failed: {status}")
            time.sleep(poll_interval)
        raise TimeoutError(f"Video task did not complete within {max_wait}s")

    def query_and_download(
        self,
        task_id: str,
        *,
        poll_interval: float = 5.0,
        max_wait: float = 600.0,
    ) -> Dict[str, Any]:
        """Poll and download a MiniMax video."""
        status = self.query_and_wait(task_id, poll_interval=poll_interval, max_wait=max_wait)
        file_id = status.get("file_id")
        if file_id:
            return self.download_video(file_id)
        return status

    # ── MiniMax I2V ───────────────────────────────────────────────────

    def create_from_image(self, *, model: str = "MiniMax-Hailuo-2.3", **kwargs: Any) -> Dict[str, Any]:
        """Image-to-video via MiniMax."""
        body: Dict[str, Any] = {"model": model, **kwargs}
        return self._client.post("/v1/videos/minimax/generations", body)
