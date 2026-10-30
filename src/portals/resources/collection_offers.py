from __future__ import annotations

from collections.abc import Sequence
from typing import Literal
from urllib.parse import quote

from .._models import Amount
from .._transport import AsyncTransport, SyncTransport
from ..models import (
    AcceptOfferRequest,
    BulkUpdateOfferItem,
    BulkUpdateOffersRequest,
    BulkUpdateOffersResponse,
    CancelOfferRequest,
    CollectionOffer,
    CollectionOffersResponse,
    CreateOfferRequest,
    OfferAttribute,
    OfferCollectionsResponse,
)
from ._helpers import amount as _amount
from ._helpers import batch


class CollectionOffers:
    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def create(
        self,
        *,
        collection_id: str,
        amount: Amount | str,
        max_nfts: int,
        attributes: Sequence[OfferAttribute] | None = None,
        expiration_days: Literal[1, 7] | None = None,
    ) -> CollectionOffer:
        request = CreateOfferRequest(
            collection_id=collection_id,
            amount=_amount(amount),
            max_nfts=max_nfts,
            attributes=list(attributes) if attributes is not None else None,
            expiration_days=expiration_days,
        )
        return self._transport.request(
            "POST",
            "/partners/collection-offers/",
            json_data=request,
            response_model=CollectionOffer,
        )

    def bulk_update(self, offers: Sequence[BulkUpdateOfferItem]) -> BulkUpdateOffersResponse:
        items = list(batch(offers, "offers"))
        if len({item.id for item in items}) != len(items):
            raise ValueError("offers must not contain duplicate IDs")
        request = BulkUpdateOffersRequest(offers=items)
        return self._transport.request(
            "POST",
            "/partners/collection-offers/bulk/update",
            json_data=request,
            response_model=BulkUpdateOffersResponse,
        )

    def cancel(self, offer_id: str) -> None:
        request = CancelOfferRequest(id=offer_id)
        self._transport.request("POST", "/partners/collection-offers/cancel", json_data=request)

    def collections(self) -> OfferCollectionsResponse:
        return self._transport.request(
            "GET",
            "/partners/collection-offers/collections",
            response_model=OfferCollectionsResponse,
        )

    def all(
        self,
        collection_id: str,
        *,
        limit: int | None = 10,
        scope: Literal["broad", "trait"] | None = None,
    ) -> list[CollectionOffersResponse]:
        if limit is not None and not 1 <= limit <= 10:
            raise ValueError("limit must be between 1 and 10")
        path = f"/partners/collection-offers/{quote(collection_id, safe='')}/all"
        return self._transport.request(
            "GET",
            path,
            params={"limit": limit, "scope": scope},
            response_model=list[CollectionOffersResponse],
        )

    def top(
        self, collection_id: str, *, scope: Literal["broad", "trait"] | None = None
    ) -> CollectionOffer:
        path = f"/partners/collection-offers/{quote(collection_id, safe='')}/top"
        return self._transport.request(
            "GET", path, params={"scope": scope}, response_model=CollectionOffer
        )

    def accept(self, offer_id: str, *, amount: Amount | str, nft_ids: Sequence[str]) -> None:
        ids = list(batch(nft_ids, "nft_ids"))
        if len(set(ids)) != len(ids):
            raise ValueError("nft_ids must not contain duplicates")
        request = AcceptOfferRequest(amount=_amount(amount), nft_ids=ids)
        path = f"/partners/collection-offers/{quote(offer_id, safe='')}/accept"
        self._transport.request("POST", path, json_data=request)


class AsyncCollectionOffers:
    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def create(
        self,
        *,
        collection_id: str,
        amount: Amount | str,
        max_nfts: int,
        attributes: Sequence[OfferAttribute] | None = None,
        expiration_days: Literal[1, 7] | None = None,
    ) -> CollectionOffer:
        request = CreateOfferRequest(
            collection_id=collection_id,
            amount=_amount(amount),
            max_nfts=max_nfts,
            attributes=list(attributes) if attributes is not None else None,
            expiration_days=expiration_days,
        )
        return await self._transport.request(
            "POST",
            "/partners/collection-offers/",
            json_data=request,
            response_model=CollectionOffer,
        )

    async def bulk_update(self, offers: Sequence[BulkUpdateOfferItem]) -> BulkUpdateOffersResponse:
        items = list(batch(offers, "offers"))
        if len({item.id for item in items}) != len(items):
            raise ValueError("offers must not contain duplicate IDs")
        request = BulkUpdateOffersRequest(offers=items)
        return await self._transport.request(
            "POST",
            "/partners/collection-offers/bulk/update",
            json_data=request,
            response_model=BulkUpdateOffersResponse,
        )

    async def cancel(self, offer_id: str) -> None:
        request = CancelOfferRequest(id=offer_id)
        await self._transport.request(
            "POST", "/partners/collection-offers/cancel", json_data=request
        )

    async def collections(self) -> OfferCollectionsResponse:
        return await self._transport.request(
            "GET",
            "/partners/collection-offers/collections",
            response_model=OfferCollectionsResponse,
        )

    async def all(
        self,
        collection_id: str,
        *,
        limit: int | None = 10,
        scope: Literal["broad", "trait"] | None = None,
    ) -> list[CollectionOffersResponse]:
        if limit is not None and not 1 <= limit <= 10:
            raise ValueError("limit must be between 1 and 10")
        path = f"/partners/collection-offers/{quote(collection_id, safe='')}/all"
        return await self._transport.request(
            "GET",
            path,
            params={"limit": limit, "scope": scope},
            response_model=list[CollectionOffersResponse],
        )

    async def top(
        self, collection_id: str, *, scope: Literal["broad", "trait"] | None = None
    ) -> CollectionOffer:
        path = f"/partners/collection-offers/{quote(collection_id, safe='')}/top"
        return await self._transport.request(
            "GET", path, params={"scope": scope}, response_model=CollectionOffer
        )

    async def accept(self, offer_id: str, *, amount: Amount | str, nft_ids: Sequence[str]) -> None:
        ids = list(batch(nft_ids, "nft_ids"))
        if len(set(ids)) != len(ids):
            raise ValueError("nft_ids must not contain duplicates")
        request = AcceptOfferRequest(amount=_amount(amount), nft_ids=ids)
        path = f"/partners/collection-offers/{quote(offer_id, safe='')}/accept"
        await self._transport.request("POST", path, json_data=request)
