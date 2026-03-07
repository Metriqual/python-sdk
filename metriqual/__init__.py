"""Metriqual Python SDK — official client for the Metriqual API.

Usage::

    from metriqual import MQL

    client = MQL(api_key="mql_...")
    response = client.chat.create(
        messages=[{"role": "user", "content": "Hello!"}],
        model="gpt-4o",
    )
"""

from ._errors import MQLAPIError, MQLConnectionError, MQLTimeoutError
from ._mql import MQL

__all__ = [
    "MQL",
    "MQLAPIError",
    "MQLConnectionError",
    "MQLTimeoutError",
]

__version__ = "1.0.0"
