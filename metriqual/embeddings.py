"""Text embeddings API."""

from __future__ import annotations

from typing import Any, Dict, Optional, TYPE_CHECKING, Union, List

if TYPE_CHECKING:
    from ._client import HttpClient


class EmbeddingsAPI:
    """Create text embeddings."""

    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def create(
        self,
        *,
        input: Union[str, List[str]],
        model: Optional[str] = None,
        encoding_format: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        body: Dict[str, Any] = {"input": input}
        if model is not None:
            body["model"] = model
        if encoding_format is not None:
            body["encoding_format"] = encoding_format
        body.update(kwargs)
        return self._client.post("/v1/embeddings", body)

    def create_with_dimensions(
        self,
        *,
        input: Union[str, List[str]],
        model: Optional[str] = None,
        dimensions: int,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        return self.create(input=input, model=model, dimensions=dimensions, **kwargs)

    def create_base64(
        self,
        *,
        input: Union[str, List[str]],
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        return self.create(input=input, model=model, encoding_format="base64", **kwargs)
