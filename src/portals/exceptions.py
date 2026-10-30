from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from ._models import RateLimit


class PortalsError(Exception):
    """Base exception for all errors raised by the Portals client."""


class TransportError(PortalsError):
    """Raised when an underlying network or HTTP transport operation fails."""

    def __init__(self, message: str, *, original: BaseException | None = None) -> None:
        super().__init__(message)
        self.original = original


class InvalidResponseError(PortalsError):
    """Raised when the API returns non-JSON content where JSON was expected."""


class ResponseValidationError(InvalidResponseError):
    """Raised when a JSON response payload fails Pydantic model validation.

    Attributes:
        response: The decoded JSON payload that failed validation.
        errors: Pydantic error details (location, message, and input type).
    """

    def __init__(
        self,
        message: str,
        *,
        response: Any = None,
        errors: Sequence[Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.response = response
        self.errors = list(errors) if errors is not None else []


class APIError(PortalsError):
    """Raised when the Portals API returns an HTTP 4xx or 5xx error response."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        code: str | None = None,
        response: Any = None,
        rate_limit: RateLimit | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.response = response
        self.rate_limit = rate_limit


class AuthenticationError(APIError):
    """Raised on HTTP 401 responses when the API key is missing or invalid."""


class AccessDeniedError(APIError):
    """Raised on HTTP 403 responses when the API key lacks permission."""


class RateLimitError(APIError):
    """Raised on HTTP 429 responses when the rate limit is exceeded."""


class MarketFeedUnavailableError(APIError):
    """Raised on HTTP 503 `MARKET_FEED_UNAVAILABLE` responses."""


class BetOutcomeUnknownError(APIError):
    """Raised on HTTP 504 `BET_OUTCOME_UNKNOWN` when an Arena bet outcome timed out."""
