from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

import httpx2
import pytest

from portals import (
    AsyncPortalsClient,
    InvalidResponseError,
    MarketConfig,
    NFTStatus,
    PortalsClient,
    ResponseValidationError,
    Wallet,
)
from portals._transport import dump_model, prepare_params
from portals.models import ArenaBet, BuyDetail


def test_client_rejects_blank_api_key() -> None:
    with pytest.raises(ValueError, match="api_key must not be empty"):
        PortalsClient("   ")


def test_transport_rejects_relative_path() -> None:
    transport = httpx2.MockTransport(lambda req: httpx2.Response(200, json={}))
    with (
        PortalsClient("key", client=httpx2.Client(transport=transport)) as client,
        pytest.raises(ValueError, match="path must start with '/'"),
    ):
        client.request("GET", "partners/example")


def test_prepare_params_encoding() -> None:
    encoded = prepare_params(
        {
            "omitted": None,
            "flag_true": True,
            "flag_false": False,
            "amount": Decimal("0.00000005"),
            "status": NFTStatus.LISTED,
            "day": date(2026, 10, 31),
            "ts": datetime(2026, 10, 31, 12, 30, tzinfo=UTC),
            "items": ["a", NFTStatus.UNLISTED, Decimal("1.50"), True],
        }
    )
    assert encoded == {
        "flag_true": "true",
        "flag_false": "false",
        "amount": "0.00000005",
        "status": "listed",
        "day": "2026-10-31",
        "ts": "2026-10-31T12:30:00+00:00",
        "items": "a,unlisted,1.50,true",
    }


def test_dump_model_excludes_none_and_uses_aliases() -> None:
    detail = BuyDetail(id="nft-1", price=Decimal("3.25"))
    assert dump_model(detail) == {"id": "nft-1", "price": "3.25"}

    bet = ArenaBet(bet_type="ton", player_id="p1")
    assert dump_model(bet) == {"betType": "ton", "playerId": "p1"}


def test_headers_and_empty_responses() -> None:
    seen: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        seen.append(request)
        if request.url.path == "/partners/no-content":
            return httpx2.Response(204, request=request)
        if request.url.path == "/partners/empty":
            return httpx2.Response(200, content=b"", request=request)
        return httpx2.Response(
            200,
            json={"balance": "10.00", "frozen_funds": "1.50"},
            headers={
                "X-RateLimit-Limit": "60",
                "X-RateLimit-Remaining": "59",
                "X-RateLimit-Reset": "10",
            },
            request=request,
        )

    http_client = httpx2.Client(transport=httpx2.MockTransport(handler))
    with PortalsClient(
        "secret-key", base_url="https://example.test/", client=http_client
    ) as client:
        wallet = client.wallet.get()
        assert wallet == Wallet(balance=Decimal("10.00"), frozen_funds=Decimal("1.50"))
        assert client.last_rate_limit is not None
        assert client.last_rate_limit.remaining == 59

        assert client.request("POST", "/partners/no-content") is None
        assert client.request("POST", "/partners/empty") is None

    assert not http_client.is_closed
    http_client.close()

    first = seen[0]
    assert str(first.url) == "https://example.test/partners/users/wallets/"
    assert first.headers["Authorization"] == "partners secret-key"
    assert first.headers["Accept"] == "application/json"
    assert first.headers["User-Agent"].startswith("portals-api-python/")


def test_invalid_json_and_validation_error() -> None:
    def handler(request: httpx2.Request) -> httpx2.Response:
        if request.url.path == "/partners/bad-json":
            return httpx2.Response(200, content=b"not-json", request=request)
        return httpx2.Response(200, json={"unexpected": "shape"}, request=request)

    transport = httpx2.MockTransport(handler)
    with PortalsClient("key", client=httpx2.Client(transport=transport)) as client:
        with pytest.raises(InvalidResponseError, match="invalid JSON"):
            client.request("GET", "/partners/bad-json")

        with pytest.raises(ResponseValidationError) as exc_info:
            client.request("GET", "/partners/bad-model", response_model=MarketConfig)
        assert exc_info.value.response == {"unexpected": "shape"}


async def test_owned_vs_injected_async_client_lifecycle() -> None:
    transport = httpx2.MockTransport(
        lambda req: httpx2.Response(
            200, json={"balance": "1.0", "frozen_funds": "0.0"}, request=req
        )
    )
    injected = httpx2.AsyncClient(transport=transport)
    async with AsyncPortalsClient("key", client=injected) as client:
        wallet = await client.wallet.get()
        assert wallet.balance == Decimal("1.0")
    assert not injected.is_closed
    await injected.aclose()

    owned_client = AsyncPortalsClient("key")
    inner = await owned_client._transport._get_client()
    assert not inner.is_closed
    await owned_client.aclose()
    assert inner.is_closed


def test_owned_sync_client_lifecycle() -> None:
    owned_client = PortalsClient("key")
    inner = owned_client._transport._get_client()
    assert not inner.is_closed
    owned_client.close()
    assert inner.is_closed
