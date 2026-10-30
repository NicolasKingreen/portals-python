from __future__ import annotations

import httpx2
import pytest

from portals import (
    AccessDeniedError,
    APIError,
    AsyncPortalsClient,
    AuthenticationError,
    BetOutcomeUnknownError,
    MarketFeedUnavailableError,
    PortalsClient,
    RateLimitError,
    TransportError,
)


@pytest.mark.parametrize(
    ("status_code", "payload", "expected_cls"),
    [
        (401, {"code": "UNAUTHORIZED", "message": "bad key"}, AuthenticationError),
        (403, {"code": "FORBIDDEN", "message": "denied"}, AccessDeniedError),
        (429, {"code": "RATE_LIMIT", "message": "slow down"}, RateLimitError),
        (
            503,
            {"code": "MARKET_FEED_UNAVAILABLE", "message": "feed down"},
            MarketFeedUnavailableError,
        ),
        (503, {"code": "OTHER_503", "message": "other"}, APIError),
        (
            504,
            {"code": "BET_OUTCOME_UNKNOWN", "message": "timeout"},
            BetOutcomeUnknownError,
        ),
        (504, {"code": "OTHER_504", "message": "gateway"}, APIError),
        (400, {"code": "BAD_REQUEST", "message": "invalid"}, APIError),
    ],
)
def test_error_mapping(
    status_code: int,
    payload: dict[str, str],
    expected_cls: type[APIError],
) -> None:
    def handler(request: httpx2.Request) -> httpx2.Response:
        return httpx2.Response(
            status_code,
            json=payload,
            headers={
                "X-RateLimit-Limit": "100",
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": "30",
            },
            request=request,
        )

    transport = httpx2.MockTransport(handler)
    with PortalsClient("key", client=httpx2.Client(transport=transport)) as client:
        with pytest.raises(expected_cls) as exc_info:
            client.request("GET", "/partners/test")
        err = exc_info.value
        assert type(err) is expected_cls
        assert err.status_code == status_code
        assert err.code == payload["code"]
        assert err.message == payload["message"]
        assert err.response == payload
        assert err.rate_limit is not None
        assert err.rate_limit.reset_seconds == 30


def test_error_with_plain_text_and_empty_body() -> None:
    def handler(request: httpx2.Request) -> httpx2.Response:
        if request.url.path == "/partners/text":
            return httpx2.Response(502, text="Bad Gateway", request=request)
        return httpx2.Response(500, content=b"", request=request)

    transport = httpx2.MockTransport(handler)
    with PortalsClient("key", client=httpx2.Client(transport=transport)) as client:
        with pytest.raises(APIError) as text_err:
            client.request("GET", "/partners/text")
        assert text_err.value.message == "Bad Gateway"
        assert text_err.value.code is None
        assert text_err.value.response is None

        with pytest.raises(APIError) as empty_err:
            client.request("GET", "/partners/empty")
        assert empty_err.value.message == "Portals API request failed with HTTP 500"
        assert empty_err.value.code is None


def test_sync_transport_error_wraps_httpx_error() -> None:
    def failing_handler(request: httpx2.Request) -> httpx2.Response:
        raise httpx2.ConnectError("connection refused", request=request)

    transport = httpx2.MockTransport(failing_handler)
    with PortalsClient("key", client=httpx2.Client(transport=transport)) as client:
        with pytest.raises(TransportError, match="Could not reach the Portals API") as exc_info:
            client.wallet.get()
        assert isinstance(exc_info.value.original, httpx2.ConnectError)


async def test_async_transport_error_wraps_httpx_error() -> None:
    def failing_handler(request: httpx2.Request) -> httpx2.Response:
        raise httpx2.ConnectError("connection refused", request=request)

    transport = httpx2.MockTransport(failing_handler)
    async with AsyncPortalsClient("key", client=httpx2.AsyncClient(transport=transport)) as client:
        with pytest.raises(TransportError, match="Could not reach the Portals API") as exc_info:
            await client.wallet.get()
        assert isinstance(exc_info.value.original, httpx2.ConnectError)
