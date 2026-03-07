"""Metriqual API error classes."""

from __future__ import annotations

from typing import Any, Dict, Optional


class MQLAPIError(Exception):
    """Error returned by the Metriqual API."""

    def __init__(
        self,
        message: str,
        status: int,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.details = details

    @classmethod
    def from_response(cls, body: Dict[str, Any], status: int) -> MQLAPIError:
        error = body.get("error", body)
        if isinstance(error, str):
            return cls(message=error, status=status)
        return cls(
            message=error.get("message", str(body)),
            status=status,
            code=error.get("code"),
            details=error.get("details"),
        )

    def __repr__(self) -> str:
        return f"MQLAPIError(status={self.status}, code={self.code!r}, message={str(self)!r})"


class MQLTimeoutError(MQLAPIError):
    """Request timed out."""

    def __init__(self, message: str = "Request timed out") -> None:
        super().__init__(message=message, status=0, code="timeout")


class MQLConnectionError(MQLAPIError):
    """Could not connect to the API."""

    def __init__(self, message: str = "Connection failed") -> None:
        super().__init__(message=message, status=0, code="connection_error")
