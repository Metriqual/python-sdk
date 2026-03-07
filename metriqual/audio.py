"""Audio API — TTS, STT, voice cloning, voice design, voice management, lyrics."""

from __future__ import annotations

import time
from typing import Any, BinaryIO, Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ._client import HttpClient


class AudioAPI:
    """Text-to-speech, speech-to-text, voice cloning, voice design, and lyrics."""

    def __init__(self, client: HttpClient) -> None:
        self._client = client

    # ── TTS (sync) ────────────────────────────────────────────────────

    def speech(
        self,
        *,
        input: str,
        voice: str,
        model: Optional[str] = None,
        response_format: Optional[str] = None,
        speed: Optional[float] = None,
        **kwargs: Any,
    ) -> bytes:
        """Generate speech audio (returns raw bytes)."""
        body: Dict[str, Any] = {"input": input, "voice": voice}
        if model is not None:
            body["model"] = model
        if response_format is not None:
            body["response_format"] = response_format
        if speed is not None:
            body["speed"] = speed
        body.update(kwargs)
        return self._client.post_binary("/v1/audio/speech", body)

    # ── TTS (async) ───────────────────────────────────────────────────

    def speech_async(
        self,
        *,
        input: str,
        voice: str,
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Submit async TTS job, returns ``{"task_id": ...}``."""
        body: Dict[str, Any] = {"input": input, "voice": voice}
        if model is not None:
            body["model"] = model
        body.update(kwargs)
        return self._client.post("/v1/audio/speech/async", body)

    def speech_async_status(
        self, task_id: str, *, include_download_url: bool = False
    ) -> Dict[str, Any]:
        params = {"include_download_url": "true"} if include_download_url else None
        return self._client.get(f"/v1/audio/speech/async/{task_id}", params)

    def speech_async_download(self, task_id: str) -> bytes:
        return self._client.get_binary(f"/v1/audio/speech/async/{task_id}/download")

    def speech_async_and_wait(
        self,
        *,
        input: str,
        voice: str,
        model: Optional[str] = None,
        poll_interval: float = 2.0,
        max_wait: float = 300.0,
        **kwargs: Any,
    ) -> bytes:
        """Submit async TTS, poll until ready, return audio bytes."""
        resp = self.speech_async(input=input, voice=voice, model=model, **kwargs)
        task_id = resp["task_id"]
        deadline = time.monotonic() + max_wait
        while time.monotonic() < deadline:
            status = self.speech_async_status(task_id, include_download_url=True)
            if status.get("status") == "completed":
                return self.speech_async_download(task_id)
            if status.get("status") == "failed":
                raise RuntimeError(f"Async TTS failed: {status}")
            time.sleep(poll_interval)
        raise TimeoutError(f"Async TTS did not complete within {max_wait}s")

    # ── STT ───────────────────────────────────────────────────────────

    def transcribe(
        self,
        *,
        file: Union[BinaryIO, bytes, tuple],
        model: Optional[str] = None,
        language: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Transcribe audio to text."""
        files = {"file": file if isinstance(file, tuple) else ("audio.wav", file)}
        data: Dict[str, Any] = {}
        if model is not None:
            data["model"] = model
        if language is not None:
            data["language"] = language
        data.update(kwargs)
        return self._client.post_form("/v1/audio/transcriptions", files=files, data=data or None)

    def translate(
        self,
        *,
        file: Union[BinaryIO, bytes, tuple],
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Translate audio to English text."""
        files = {"file": file if isinstance(file, tuple) else ("audio.wav", file)}
        data: Dict[str, Any] = {}
        if model is not None:
            data["model"] = model
        data.update(kwargs)
        return self._client.post_form("/v1/audio/translations", files=files, data=data or None)

    # ── Voice Cloning ─────────────────────────────────────────────────

    def upload_voice_clone(self, file: Union[BinaryIO, bytes, tuple]) -> Dict[str, Any]:
        files = {"file": file if isinstance(file, tuple) else ("voice.wav", file)}
        return self._client.post_form("/v1/audio/voice-clone/upload", files=files)

    def clone_voice(
        self,
        *,
        voice_id: str,
        file_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        body: Dict[str, Any] = {"voice_id": voice_id}
        if file_id is not None:
            body["file_id"] = file_id
        body.update(kwargs)
        return self._client.post("/v1/audio/voice-clone", body)

    def upload_and_clone_voice(
        self,
        file: Union[BinaryIO, bytes, tuple],
        voice_id: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Upload a voice file and clone in one step."""
        upload = self.upload_voice_clone(file)
        return self.clone_voice(voice_id=voice_id, file_id=upload.get("file_id"), **kwargs)

    # ── Prompt Audio ──────────────────────────────────────────────────

    def upload_prompt_audio(self, file: Union[BinaryIO, bytes, tuple]) -> Dict[str, Any]:
        files = {"file": file if isinstance(file, tuple) else ("prompt.wav", file)}
        return self._client.post_form("/v1/audio/prompt-audio/upload", files=files)

    # ── Voice Design ──────────────────────────────────────────────────

    def design_voice(self, **kwargs: Any) -> Dict[str, Any]:
        return self._client.post("/v1/audio/voice-design", kwargs)

    # ── Voice Management ──────────────────────────────────────────────

    def get_voices(self, **kwargs: Any) -> Dict[str, Any]:
        return self._client.post("/v1/audio/voices", kwargs or None)

    def delete_voice(self, voice_id: str) -> Dict[str, Any]:
        return self._client.post("/v1/audio/voices/delete", {"voice_id": voice_id})

    def create_voice(
        self,
        *,
        file: Union[BinaryIO, bytes, tuple],
        name: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        files = {"file": file if isinstance(file, tuple) else ("voice.wav", file)}
        data: Dict[str, Any] = {}
        if name is not None:
            data["name"] = name
        data.update(kwargs)
        return self._client.post_form("/v1/audio/voices/create", files=files, data=data or None)

    # ── Voice Consents ────────────────────────────────────────────────

    def create_voice_consent(
        self,
        *,
        file: Union[BinaryIO, bytes, tuple],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        files = {"file": file if isinstance(file, tuple) else ("consent.wav", file)}
        return self._client.post_form("/v1/audio/voice_consents", files=files, data=kwargs or None)

    def get_voice_consent(self, consent_id: str) -> Dict[str, Any]:
        return self._client.get(f"/v1/audio/voice_consents/{consent_id}")

    def update_voice_consent(self, consent_id: str, **kwargs: Any) -> Dict[str, Any]:
        return self._client.post(f"/v1/audio/voice_consents/{consent_id}", kwargs)

    def delete_voice_consent(self, consent_id: str) -> Dict[str, Any]:
        return self._client.delete(f"/v1/audio/voice_consents/{consent_id}")

    def list_voice_consents(
        self,
        *,
        after: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        if after is not None:
            params["after"] = after
        if limit is not None:
            params["limit"] = limit
        return self._client.get("/v1/audio/voice_consents", params or None)

    # ── Lyrics ────────────────────────────────────────────────────────

    def generate_lyrics(
        self,
        *,
        mode: str,
        prompt: Optional[str] = None,
        lyrics: Optional[str] = None,
        title: Optional[str] = None,
    ) -> Dict[str, Any]:
        body: Dict[str, Any] = {"mode": mode}
        if prompt is not None:
            body["prompt"] = prompt
        if lyrics is not None:
            body["lyrics"] = lyrics
        if title is not None:
            body["title"] = title
        return self._client.post("/v1/audio/lyrics", body)
