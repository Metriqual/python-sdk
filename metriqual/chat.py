"""Chat completions API."""

from __future__ import annotations

import json
from typing import Any, Callable, Dict, Iterator, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ._client import HttpClient


class ChatAPI:
    """Chat completions — OpenAI-compatible interface."""

    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def create(
        self,
        *,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        n: Optional[int] = None,
        stop: Optional[Any] = None,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        user: Optional[str] = None,
        functions: Optional[List[Dict[str, Any]]] = None,
        function_call: Optional[Any] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Create a chat completion (non-streaming)."""
        body = _build_body(locals())
        return self._client.post("/v1/chat/completions", body)

    def stream(
        self,
        *,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        n: Optional[int] = None,
        stop: Optional[Any] = None,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        user: Optional[str] = None,
        functions: Optional[List[Dict[str, Any]]] = None,
        function_call: Optional[Any] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Any] = None,
        on_chunk: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> Iterator[Dict[str, Any]]:
        """Stream chat completion chunks via SSE."""
        body = _build_body(locals())
        body["stream"] = True
        for raw in self._client.stream("/v1/chat/completions", body):
            chunk = json.loads(raw)
            if on_chunk:
                on_chunk(chunk)
            yield chunk

    def stream_to_completion(
        self,
        *,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Stream and collect all chunks, returning ``{"chunks": [...], "text": "..."}``."""
        chunks: List[Dict[str, Any]] = []
        text_parts: List[str] = []
        for chunk in self.stream(messages=messages, model=model, max_tokens=max_tokens, temperature=temperature, top_p=top_p, **kwargs):
            chunks.append(chunk)
            delta = chunk.get("choices", [{}])[0].get("delta", {})
            content = delta.get("content")
            if content:
                text_parts.append(content)
        return {"chunks": chunks, "text": "".join(text_parts)}

    def complete(
        self,
        messages: List[Dict[str, Any]],
        *,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs: Any,
    ) -> str:
        """Simple helper — returns just the text content."""
        resp = self.create(messages=messages, model=model, max_tokens=max_tokens, temperature=temperature, **kwargs)
        choices = resp.get("choices", [])
        if choices:
            return choices[0].get("message", {}).get("content", "")
        return ""


def _build_body(params: Dict[str, Any]) -> Dict[str, Any]:
    """Build request body from keyword args, dropping None values and internal keys."""
    skip = {"self", "on_chunk"}
    return {k: v for k, v in params.items() if k not in skip and v is not None}
