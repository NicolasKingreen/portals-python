from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

import httpx2
import pytest

from portals import (
    AsyncPortalsClient,
    BulkUpdateOfferItem,
    BuyDetail,
    NFTPriceDetail,
    OfferAttribute,
    PortalsClient,
)


@dataclass(frozen=True)
class Case:
    spec_method: str
    spec_path: str
    expected_path: str
    sync_call: Callable[[PortalsClient], Any]
    async_call: Callable[[AsyncPortalsClient], Awaitable[Any]]
    response_status: int
    response_json: Any
    expected_params: dict[str, str] | None = None
    expected_json: dict[str, Any] | None = None


CASES: tuple[Case, ...] = (
    # Arena (3)
    Case(
        spec_method="GET",
        spec_path="/partners/arena/state",
        expected_path="/partners/arena/state",
        sync_call=lambda c: c.arena.state(),
        async_call=lambda c: c.arena.state(),
        response_status=200,
        response_json={"rooms": [], "serverTime": 1700000000000},
    ),
    Case(
        spec_method="GET",
        spec_path="/partners/arena/inventory",
        expected_path="/partners/arena/inventory",
        sync_call=lambda c: c.arena.inventory(limit=10, status="listed"),
        async_call=lambda c: c.arena.inventory(limit=10, status="listed"),
        response_status=200,
        response_json={"items": [], "totalCount": 0},
        expected_params={"limit": "10", "status": "listed"},
    ),
    Case(
        spec_method="POST",
        spec_path="/partners/arena/bet",
        expected_path="/partners/arena/bet",
        sync_call=lambda c: c.arena.bet(room_id=1, amount=Decimal("5.5")),
        async_call=lambda c: c.arena.bet(room_id=1, amount=Decimal("5.5")),
        response_status=200,
        response_json={"acceptedAmount": "5.5", "betId": "b1", "gameId": 10},
        expected_json={"room_id": 1, "bet_type": "ton", "amount": "5.5"},
    ),
    # Collection offers (7)
    Case(
        spec_method="POST",
        spec_path="/partners/collection-offers/",
        expected_path="/partners/collection-offers/",
        sync_call=lambda c: c.offers.create(
            collection_id="col-1",
            amount="15.0",
            max_nfts=2,
            attributes=[OfferAttribute(type="model", value="Gold")],
            expiration_days=7,
        ),
        async_call=lambda c: c.offers.create(
            collection_id="col-1",
            amount="15.0",
            max_nfts=2,
            attributes=[OfferAttribute(type="model", value="Gold")],
            expiration_days=7,
        ),
        response_status=200,
        response_json={"id": "off-1", "amount": "15.0", "collection_id": "col-1"},
        expected_json={
            "collection_id": "col-1",
            "amount": "15.0",
            "max_nfts": 2,
            "attributes": [{"type": "model", "value": "Gold"}],
            "expiration_days": 7,
        },
    ),
    Case(
        spec_method="POST",
        spec_path="/partners/collection-offers/bulk/update",
        expected_path="/partners/collection-offers/bulk/update",
        sync_call=lambda c: c.offers.bulk_update([BulkUpdateOfferItem(id="off-1", amount="16.0")]),
        async_call=lambda c: c.offers.bulk_update([BulkUpdateOfferItem(id="off-1", amount="16.0")]),
        response_status=200,
        response_json={"updated": ["off-1"], "failed": []},
        expected_json={"offers": [{"id": "off-1", "amount": "16.0"}]},
    ),
    Case(
        spec_method="POST",
        spec_path="/partners/collection-offers/cancel",
        expected_path="/partners/collection-offers/cancel",
        sync_call=lambda c: c.offers.cancel("off-1"),
        async_call=lambda c: c.offers.cancel("off-1"),
        response_status=204,
        response_json=None,
        expected_json={"id": "off-1"},
    ),
    Case(
        spec_method="GET",
        spec_path="/partners/collection-offers/collections",
        expected_path="/partners/collection-offers/collections",
        sync_call=lambda c: c.offers.collections(),
        async_call=lambda c: c.offers.collections(),
        response_status=200,
        response_json={"collections": [], "total_count": 0},
    ),
    Case(
        spec_method="GET",
        spec_path="/partners/collection-offers/{collection_id}/all",
        expected_path="/partners/collection-offers/col-1/all",
        sync_call=lambda c: c.offers.all("col-1", limit=5, scope="broad"),
        async_call=lambda c: c.offers.all("col-1", limit=5, scope="broad"),
        response_status=200,
        response_json=[{"offers": [], "total_count": 0}],
        expected_params={"limit": "5", "scope": "broad"},
    ),
    Case(
        spec_method="GET",
        spec_path="/partners/collection-offers/{collection_id}/top",
        expected_path="/partners/collection-offers/col-1/top",
        sync_call=lambda c: c.offers.top("col-1", scope="trait"),
        async_call=lambda c: c.offers.top("col-1", scope="trait"),
        response_status=200,
        response_json={"id": "off-top", "amount": "20.0"},
        expected_params={"scope": "trait"},
    ),
    Case(
        spec_method="POST",
        spec_path="/partners/collection-offers/{offer_id}/accept",
        expected_path="/partners/collection-offers/off-1/accept",
        sync_call=lambda c: c.offers.accept("off-1", amount="20.0", nft_ids=["n1", "n2"]),
        async_call=lambda c: c.offers.accept("off-1", amount="20.0", nft_ids=["n1", "n2"]),
        response_status=204,
        response_json=None,
        expected_json={"amount": "20.0", "nft_ids": ["n1", "n2"]},
    ),
    # Collections (6)
    Case(
        spec_method="GET",
        spec_path="/partners/collections/attribute-floors",
        expected_path="/partners/collections/attribute-floors",
        sync_call=lambda c: c.collections.attribute_floors(),
        async_call=lambda c: c.collections.attribute_floors(),
        response_status=200,
        response_json={
            "models": [{"collection_name": "Plush", "floor_price": "10.0", "name": "Gold"}],
            "updated_at": "2026-10-31T00:00:00Z",
        },
    ),
    Case(
        spec_method="GET",
        spec_path="/partners/collections/backdrops/floors",
        expected_path="/partners/collections/backdrops/floors",
        sync_call=lambda c: c.collections.backdrop_floors(),
        async_call=lambda c: c.collections.backdrop_floors(),
        response_status=200,
        response_json={"floorPrices": {"Black": "12.0"}},
    ),
    Case(
        spec_method="GET",
        spec_path="/partners/collections/floors",
        expected_path="/partners/collections/floors",
        sync_call=lambda c: c.collections.floors(),
        async_call=lambda c: c.collections.floors(),
        response_status=200,
        response_json={"floorPrices": {"plush": "9.5"}},
    ),
    Case(
        spec_method="GET",
        spec_path="/partners/collections/models/backgrounds/floors",
        expected_path="/partners/collections/models/backgrounds/floors",
        sync_call=lambda c: c.collections.model_background_floors(["m1", "m2"]),
        async_call=lambda c: c.collections.model_background_floors(["m1", "m2"]),
        response_status=200,
        response_json={"model_backgrounds": {"m1": {"Black": "14.0"}}},
        expected_params={"models": "m1,m2"},
    ),
    Case(
        spec_method="GET",
        spec_path="/partners/collections/preview",
        expected_path="/partners/collections/preview",
        sync_call=lambda c: c.collections.preview(sort_by="floor_price", sort_order="asc"),
        async_call=lambda c: c.collections.preview(sort_by="floor_price", sort_order="asc"),
        response_status=200,
        response_json={"collections": [{"name": "Plush"}]},
        expected_params={"sort_by": "floor_price", "sort_order": "asc"},
    ),
    Case(
        spec_method="GET",
        spec_path="/partners/collections/{collection_id}/metrics",
        expected_path="/partners/collections/col-1/metrics",
        sync_call=lambda c: c.collections.metrics("col-1", group_by="day"),
        async_call=lambda c: c.collections.metrics("col-1", group_by="day"),
        response_status=200,
        response_json={
            "history": [{"avg_price": "10.0", "collection_id": "col-1", "total_volume": "100.0"}]
        },
        expected_params={"group_by": "day"},
    ),
    # Market (2)
    Case(
        spec_method="GET",
        spec_path="/partners/market/config",
        expected_path="/partners/market/config",
        sync_call=lambda c: c.market.config(),
        async_call=lambda c: c.market.config(),
        response_status=200,
        response_json={
            "commission": "0.05",
            "cooldown": "60s",
            "deposit_wallet": "EQD...",
            "rub_course": "300.0",
            "usd_course": "3.2",
            "user_cashback": "0.01",
        },
    ),
    Case(
        spec_method="GET",
        spec_path="/partners/market/actions/",
        expected_path="/partners/market/actions/",
        sync_call=lambda c: c.market.actions(limit=10, offset=0, min_price="1.5"),
        async_call=lambda c: c.market.actions(limit=10, offset=0, min_price="1.5"),
        response_status=200,
        response_json={"actions": []},
        expected_params={"limit": "10", "offset": "0", "min_price": "1.5"},
    ),
    # NFTs (11)
    Case(
        spec_method="GET",
        spec_path="/partners/nfts/search",
        expected_path="/partners/nfts/search",
        sync_call=lambda c: c.nfts.search(limit=5, max_price="25.0"),
        async_call=lambda c: c.nfts.search(limit=5, max_price="25.0"),
        response_status=200,
        response_json={"results": [], "total_count": 0},
        expected_params={"limit": "5", "max_price": "25.0"},
    ),
    Case(
        spec_method="GET",
        spec_path="/partners/nfts/owned",
        expected_path="/partners/nfts/owned",
        sync_call=lambda c: c.nfts.owned(limit=5, with_attributes=True),
        async_call=lambda c: c.nfts.owned(limit=5, with_attributes=True),
        response_status=200,
        response_json={"nfts": [], "total_count": 0},
        expected_params={"limit": "5", "with_attributes": "true"},
    ),
    Case(
        spec_method="POST",
        spec_path="/partners/nfts",
        expected_path="/partners/nfts",
        sync_call=lambda c: c.nfts.buy([BuyDetail(id="nft-1", price="12.5")]),
        async_call=lambda c: c.nfts.buy([BuyDetail(id="nft-1", price="12.5")]),
        response_status=200,
        response_json={"total_purchased": 1, "total_failed": 0, "total_spent": "12.5"},
        expected_json={"nft_details": [{"id": "nft-1", "price": "12.5"}]},
    ),
    Case(
        spec_method="POST",
        spec_path="/partners/nfts/bulk-list",
        expected_path="/partners/nfts/bulk-list",
        sync_call=lambda c: c.nfts.bulk_list([NFTPriceDetail(nft_id="nft-1", price="14.0")]),
        async_call=lambda c: c.nfts.bulk_list([NFTPriceDetail(nft_id="nft-1", price="14.0")]),
        response_status=200,
        response_json={"successful_nfts": ["nft-1"], "failed_nfts": []},
        expected_json={"nft_prices": [{"nft_id": "nft-1", "price": "14.0"}]},
    ),
    Case(
        spec_method="POST",
        spec_path="/partners/nfts/bulk-unlist",
        expected_path="/partners/nfts/bulk-unlist",
        sync_call=lambda c: c.nfts.bulk_unlist(["nft-1"]),
        async_call=lambda c: c.nfts.bulk_unlist(["nft-1"]),
        response_status=200,
        response_json={"successful_nfts": ["nft-1"], "failed_nfts": []},
        expected_json={"nft_ids": ["nft-1"]},
    ),
    Case(
        spec_method="GET",
        spec_path="/partners/nfts/stats",
        expected_path="/partners/nfts/stats",
        sync_call=lambda c: c.nfts.stats(),
        async_call=lambda c: c.nfts.stats(),
        response_status=200,
        response_json={"listed_count": 3, "unlisted_count": 7},
    ),
    Case(
        spec_method="POST",
        spec_path="/partners/nfts/transfer",
        expected_path="/partners/nfts/transfer",
        sync_call=lambda c: c.nfts.transfer(nft_ids=["nft-1"], recipient="alice", anonymous=True),
        async_call=lambda c: c.nfts.transfer(nft_ids=["nft-1"], recipient="alice", anonymous=True),
        response_status=200,
        response_json={"transferred_count": 1, "failed_items": []},
        expected_json={"nft_ids": ["nft-1"], "recipient": "alice", "anonymous": True},
    ),
    Case(
        spec_method="POST",
        spec_path="/partners/nfts/withdraw",
        expected_path="/partners/nfts/withdraw",
        sync_call=lambda c: c.nfts.withdraw(["nft-1"], recipient_id=42),
        async_call=lambda c: c.nfts.withdraw(["nft-1"], recipient_id=42),
        response_status=200,
        response_json={"withdrawals_ids": [101]},
        expected_json={"gift_ids": ["nft-1"], "recipient_id": 42},
    ),
    Case(
        spec_method="GET",
        spec_path="/partners/nfts/withdrawals/statuses",
        expected_path="/partners/nfts/withdrawals/statuses",
        sync_call=lambda c: c.nfts.withdrawal_statuses([101, 102]),
        async_call=lambda c: c.nfts.withdrawal_statuses([101, 102]),
        response_status=200,
        response_json={"statuses": [{"id": 101, "status": "completed"}]},
        expected_params={"ids": "101,102"},
    ),
    Case(
        spec_method="POST",
        spec_path="/partners/nfts/{nft_id}/list",
        expected_path="/partners/nfts/nft-1/list",
        sync_call=lambda c: c.nfts.list("nft-1", price="19.99"),
        async_call=lambda c: c.nfts.list("nft-1", price="19.99"),
        response_status=204,
        response_json=None,
        expected_json={"price": "19.99"},
    ),
    Case(
        spec_method="POST",
        spec_path="/partners/nfts/{nft_id}/unlist",
        expected_path="/partners/nfts/nft-1/unlist",
        sync_call=lambda c: c.nfts.unlist("nft-1"),
        async_call=lambda c: c.nfts.unlist("nft-1"),
        response_status=204,
        response_json=None,
    ),
    # Users (2)
    Case(
        spec_method="GET",
        spec_path="/partners/users/{user_id}",
        expected_path="/partners/users/12345",
        sync_call=lambda c: c.users.exists(12345),
        async_call=lambda c: c.users.exists(12345),
        response_status=200,
        response_json={"exists": True},
    ),
    Case(
        spec_method="GET",
        spec_path="/partners/users/actions",
        expected_path="/partners/users/actions",
        sync_call=lambda c: c.users.actions(limit=10, offset=0),
        async_call=lambda c: c.users.actions(limit=10, offset=0),
        response_status=200,
        response_json={"actions": []},
        expected_params={"limit": "10", "offset": "0"},
    ),
    # Wallet (4)
    Case(
        spec_method="GET",
        spec_path="/partners/users/wallets/",
        expected_path="/partners/users/wallets/",
        sync_call=lambda c: c.wallet.get(),
        async_call=lambda c: c.wallet.get(),
        response_status=200,
        response_json={"balance": "50.0", "frozen_funds": "2.0"},
    ),
    Case(
        spec_method="POST",
        spec_path="/partners/deposits",
        expected_path="/partners/deposits",
        sync_call=lambda c: c.wallet.create_deposit(),
        async_call=lambda c: c.wallet.create_deposit(),
        response_status=200,
        response_json={"id": "dep-1"},
    ),
    Case(
        spec_method="POST",
        spec_path="/partners/users/wallets/withdraw",
        expected_path="/partners/users/wallets/withdraw",
        sync_call=lambda c: c.wallet.withdraw(amount="10.0", external_address="EQD..."),
        async_call=lambda c: c.wallet.withdraw(amount="10.0", external_address="EQD..."),
        response_status=200,
        response_json={"id": "w-1"},
        expected_json={"amount": "10.0", "external_address": "EQD..."},
    ),
    Case(
        spec_method="GET",
        spec_path="/partners/users/wallets/withdrawals/statuses",
        expected_path="/partners/users/wallets/withdrawals/statuses",
        sync_call=lambda c: c.wallet.withdrawal_statuses(["w-1", "w-2"]),
        async_call=lambda c: c.wallet.withdrawal_statuses(["w-1", "w-2"]),
        response_status=200,
        response_json={"status": [{"id": "w-1", "status": "resolved"}]},
        expected_params={"ids": "w-1,w-2"},
    ),
)


@pytest.mark.parametrize("case", CASES, ids=lambda c: f"{c.spec_method} {c.spec_path}")
async def test_resource_sync_and_async_parity(case: Case) -> None:
    seen: list[httpx2.Request] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        seen.append(request)
        if case.response_status == 204:
            return httpx2.Response(204, request=request)
        return httpx2.Response(case.response_status, json=case.response_json, request=request)

    transport = httpx2.MockTransport(handler)
    with PortalsClient("key", client=httpx2.Client(transport=transport)) as sync_client:
        sync_result = case.sync_call(sync_client)

    async with AsyncPortalsClient(
        "key", client=httpx2.AsyncClient(transport=transport)
    ) as async_client:
        async_result = await case.async_call(async_client)

    assert sync_result == async_result
    assert len(seen) == 2

    for req in seen:
        assert req.method == case.spec_method
        assert req.url.path == case.expected_path
        assert dict(req.url.params) == (case.expected_params or {})
        if case.expected_json is not None:
            assert json.loads(req.content) == case.expected_json
        else:
            assert req.content == b""


def test_cases_cover_every_openapi_operation() -> None:
    root = Path(__file__).resolve().parent.parent
    spec = json.loads((root / "specs" / "partners.en.json").read_text(encoding="utf-8"))
    spec_ops = {
        (method.upper(), path)
        for path, item in spec["paths"].items()
        for method in item
        if method.lower() in ("get", "post", "put", "patch", "delete")
    }
    tested_ops = {(case.spec_method, case.spec_path) for case in CASES}
    assert tested_ops == spec_ops
    assert len(tested_ops) == 35


def test_client_side_parameter_validation() -> None:
    transport = httpx2.MockTransport(lambda req: httpx2.Response(204, request=req))
    with PortalsClient("key", client=httpx2.Client(transport=transport)) as client:
        with pytest.raises(ValueError, match="limit must be between 1 and 150"):
            client.arena.inventory(limit=0)
        with pytest.raises(ValueError, match="Provide exactly one of amount or gift_ids"):
            client.arena.bet(room_id=1)
        with pytest.raises(ValueError, match="Provide exactly one of amount or gift_ids"):
            client.arena.bet(room_id=1, amount="1", gift_ids=["g1"])
        with pytest.raises(ValueError, match="gift_ids must contain between 1 and 50 items"):
            client.arena.bet(room_id=1, gift_ids=[])

        with pytest.raises(ValueError, match="offers must not contain duplicate IDs"):
            client.offers.bulk_update([BulkUpdateOfferItem(id="o1"), BulkUpdateOfferItem(id="o1")])
        with pytest.raises(ValueError, match="limit must be between 1 and 10"):
            client.offers.all("col", limit=11)
        with pytest.raises(ValueError, match="nft_ids must not contain duplicates"):
            client.offers.accept("o1", amount="5", nft_ids=["n1", "n1"])

        with pytest.raises(ValueError, match="models must not be empty"):
            client.collections.model_background_floors([])

        with pytest.raises(ValueError, match="limit must be between 1 and 20"):
            client.market.actions(limit=25)
        with pytest.raises(ValueError, match="offset must be between 0 and 700"):
            client.market.actions(offset=701)

        with pytest.raises(ValueError, match="nft_details must contain between 1 and 50 items"):
            client.nfts.buy([])
        with pytest.raises(ValueError, match="nft_prices must not be empty"):
            client.nfts.bulk_list([])
        with pytest.raises(ValueError, match="nft_ids must not be empty"):
            client.nfts.bulk_unlist([])
        with pytest.raises(ValueError, match="Provide exactly one of recipient or recipient_token"):
            client.nfts.transfer(nft_ids=["n1"])
        with pytest.raises(ValueError, match="gift_ids must not be empty"):
            client.nfts.withdraw([])
        with pytest.raises(ValueError, match="ids must not be empty"):
            client.nfts.withdrawal_statuses([])
        with pytest.raises(ValueError, match="ids must not be empty"):
            client.wallet.withdrawal_statuses([])
