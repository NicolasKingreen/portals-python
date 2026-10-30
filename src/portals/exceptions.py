from __future__ import annotations

from typing import Any

from ._models import RateLimit


class PortalsError(Exception):
    pass


class TransportError(PortalsError):
    def __init__(self, message: str, *, original: BaseException | None = None) -> None:
        super().__init__(message)
        self.original = original


class InvalidResponseError(PortalsError):
    pass


class ResponseValidationError(InvalidResponseError):
    def __init__(self, message: str, *, response: Any = None) -> None:
        super().__init__(message)
        self.response = response


class APIError(PortalsError):
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
    pass


class AccessDeniedError(APIError):
    pass


class RateLimitError(APIError):
    pass


class MarketFeedUnavailableError(APIError):
    pass


class BetOutcomeUnknownError(APIError):
    pass
