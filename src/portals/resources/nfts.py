from __future__ import annotations

from collections.abc import Sequence
from typing import TypeVar
from urllib.parse import quote

from .._models import Amount
from .._transport import AsyncTransport, SyncTransport
from ..models import (
    BulkDelistRequest,
    BulkListingResult,
    BulkListRequest,
    BuyDetail,
    BuyRequest,
    BuyResponse,
    ListNFTRequest,
    NFTPriceDetail,
    NFTStats,
    OwnedNFTsResponse,
    SearchNFTsResponse,
    TransferGiftsRequest,
    TransferGiftsResponse,
    WithdrawalStatusesResponse,
    WithdrawGiftsRequest,
    WithdrawGiftsResponse,
)
from ._helpers import amount as _amount
from ._helpers import batch, nft_query


class NFTs:
    """Synchronous NFTs resource (`/partners/nfts/*`)."""

    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def search(
        self,
        *,
        collection_id: str | None = None,
        collection_ids: Sequence[str] | None = None,
        external_collection_number: int | None = None,
        filter_by_backdrops: Sequence[str] | None = None,
        filter_by_models: Sequence[str] | None = None,
        filter_by_symbols: Sequence[str] | None = None,
        ids: Sequence[str] | None = None,
        is_owned: bool | None = None,
        limit: int | None = 20,
        max_price: Amount | str | None = None,
        min_price: Amount | str | None = None,
        mint_status: str | None = None,
        name_filter: str | None = None,
        offset: int | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        status: str | None = None,
        statuses: Sequence[str] | None = None,
        tg_ids: Sequence[str] | None = None,
    ) -> SearchNFTsResponse:
        """Search marketplace NFTs by collection, attributes, price range, or status."""
        params = nft_query(
            collection_id=collection_id,
            collection_ids=collection_ids,
            external_collection_number=external_collection_number,
            filter_by_backdrops=filter_by_backdrops,
            filter_by_models=filter_by_models,
            filter_by_symbols=filter_by_symbols,
            ids=ids,
            is_owned=is_owned,
            limit=limit,
            max_price=max_price,
            min_price=min_price,
            mint_status=mint_status,
            name_filter=name_filter,
            offset=offset,
            search=search,
            sort_by=sort_by,
            status=status,
            statuses=statuses,
            tg_ids=tg_ids,
        )
        return self._transport.request(
            "GET", "/partners/nfts/search", params=params, response_model=SearchNFTsResponse
        )

    def owned(
        self,
        *,
        collection_id: str | None = None,
        collection_ids: Sequence[str] | None = None,
        external_collection_number: int | None = None,
        filter_by_backdrops: Sequence[str] | None = None,
        filter_by_models: Sequence[str] | None = None,
        filter_by_symbols: Sequence[str] | None = None,
        ids: Sequence[str] | None = None,
        limit: int | None = 20,
        max_price: Amount | str | None = None,
        min_price: Amount | str | None = None,
        mint_status: str | None = None,
        name_filter: str | None = None,
        offset: int | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        status: str | None = None,
        statuses: Sequence[str] | None = None,
        tg_ids: Sequence[str] | None = None,
        with_attributes: bool | None = None,
    ) -> OwnedNFTsResponse:
        """List NFTs owned by the authenticated user."""
        params = nft_query(
            collection_id=collection_id,
            collection_ids=collection_ids,
            external_collection_number=external_collection_number,
            filter_by_backdrops=filter_by_backdrops,
            filter_by_models=filter_by_models,
            filter_by_symbols=filter_by_symbols,
            ids=ids,
            limit=limit,
            max_price=max_price,
            min_price=min_price,
            mint_status=mint_status,
            name_filter=name_filter,
            offset=offset,
            search=search,
            sort_by=sort_by,
            status=status,
            statuses=statuses,
            tg_ids=tg_ids,
            with_attributes=with_attributes,
        )
        return self._transport.request(
            "GET", "/partners/nfts/owned", params=params, response_model=OwnedNFTsResponse
        )

    def buy(self, nft_details: Sequence[BuyDetail]) -> BuyResponse:
        """Purchase 1 to 50 NFTs. Inspect `purchase_results` for per-NFT outcomes."""
        details = list(batch(nft_details, "nft_details"))
        request = BuyRequest(nft_details=details)
        return self._transport.request(
            "POST", "/partners/nfts", json_data=request, response_model=BuyResponse
        )

    def bulk_list(self, nft_prices: Sequence[NFTPriceDetail]) -> BulkListingResult:
        """List multiple owned NFTs for sale."""
        prices = _nonempty(nft_prices, "nft_prices")
        request = BulkListRequest(nft_prices=prices)
        return self._transport.request(
            "POST",
            "/partners/nfts/bulk-list",
            json_data=request,
            response_model=BulkListingResult,
        )

    def bulk_unlist(self, nft_ids: Sequence[str]) -> BulkListingResult:
        """Remove multiple owned NFTs from sale."""
        request = BulkDelistRequest(nft_ids=_nonempty(nft_ids, "nft_ids"))
        return self._transport.request(
            "POST",
            "/partners/nfts/bulk-unlist",
            json_data=request,
            response_model=BulkListingResult,
        )

    def stats(self) -> NFTStats:
        """Fetch counts of listed and unlisted NFTs owned by the authenticated user."""
        return self._transport.request("GET", "/partners/nfts/stats", response_model=NFTStats)

    def transfer(
        self,
        *,
        nft_ids: Sequence[str],
        recipient: str | None = None,
        recipient_token: str | None = None,
        anonymous: bool | None = None,
    ) -> TransferGiftsResponse:
        """Transfer owned NFTs to a recipient username/ID or recipient token."""
        if (recipient is None) == (recipient_token is None):
            raise ValueError("Provide exactly one of recipient or recipient_token")
        request = TransferGiftsRequest(
            nft_ids=_nonempty(nft_ids, "nft_ids"),
            recipient=recipient,
            recipient_token=recipient_token,
            anonymous=anonymous,
        )
        return self._transport.request(
            "POST",
            "/partners/nfts/transfer",
            json_data=request,
            response_model=TransferGiftsResponse,
        )

    def withdraw(
        self,
        gift_ids: Sequence[str],
        *,
        recipient_id: int | None = None,
        unsafe_transfer: bool | None = None,
    ) -> WithdrawGiftsResponse:
        """Withdraw owned gifts from Portals to Telegram."""
        request = WithdrawGiftsRequest(
            gift_ids=_nonempty(gift_ids, "gift_ids"),
            recipient_id=recipient_id,
            unsafe_transfer=unsafe_transfer,
        )
        return self._transport.request(
            "POST",
            "/partners/nfts/withdraw",
            json_data=request,
            response_model=WithdrawGiftsResponse,
        )

    def withdrawal_statuses(self, ids: Sequence[int]) -> WithdrawalStatusesResponse:
        """Fetch the status of one or more gift withdrawals by ID."""
        if not ids:
            raise ValueError("ids must not be empty")
        return self._transport.request(
            "GET",
            "/partners/nfts/withdrawals/statuses",
            params={"ids": ids},
            response_model=WithdrawalStatusesResponse,
        )

    def list(self, nft_id: str, *, price: Amount | str) -> None:
        """List a single owned NFT for sale at the specified price."""
        path = f"/partners/nfts/{quote(nft_id, safe='')}/list"
        request = ListNFTRequest(price=_amount(price))
        self._transport.request("POST", path, json_data=request)

    def unlist(self, nft_id: str) -> None:
        """Remove a single owned NFT from sale."""
        path = f"/partners/nfts/{quote(nft_id, safe='')}/unlist"
        self._transport.request("POST", path)


class AsyncNFTs:
    """Asynchronous NFTs resource (`/partners/nfts/*`)."""

    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def search(
        self,
        *,
        collection_id: str | None = None,
        collection_ids: Sequence[str] | None = None,
        external_collection_number: int | None = None,
        filter_by_backdrops: Sequence[str] | None = None,
        filter_by_models: Sequence[str] | None = None,
        filter_by_symbols: Sequence[str] | None = None,
        ids: Sequence[str] | None = None,
        is_owned: bool | None = None,
        limit: int | None = 20,
        max_price: Amount | str | None = None,
        min_price: Amount | str | None = None,
        mint_status: str | None = None,
        name_filter: str | None = None,
        offset: int | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        status: str | None = None,
        statuses: Sequence[str] | None = None,
        tg_ids: Sequence[str] | None = None,
    ) -> SearchNFTsResponse:
        """Search marketplace NFTs by collection, attributes, price range, or status."""
        params = nft_query(
            collection_id=collection_id,
            collection_ids=collection_ids,
            external_collection_number=external_collection_number,
            filter_by_backdrops=filter_by_backdrops,
            filter_by_models=filter_by_models,
            filter_by_symbols=filter_by_symbols,
            ids=ids,
            is_owned=is_owned,
            limit=limit,
            max_price=max_price,
            min_price=min_price,
            mint_status=mint_status,
            name_filter=name_filter,
            offset=offset,
            search=search,
            sort_by=sort_by,
            status=status,
            statuses=statuses,
            tg_ids=tg_ids,
        )
        return await self._transport.request(
            "GET", "/partners/nfts/search", params=params, response_model=SearchNFTsResponse
        )

    async def owned(
        self,
        *,
        collection_id: str | None = None,
        collection_ids: Sequence[str] | None = None,
        external_collection_number: int | None = None,
        filter_by_backdrops: Sequence[str] | None = None,
        filter_by_models: Sequence[str] | None = None,
        filter_by_symbols: Sequence[str] | None = None,
        ids: Sequence[str] | None = None,
        limit: int | None = 20,
        max_price: Amount | str | None = None,
        min_price: Amount | str | None = None,
        mint_status: str | None = None,
        name_filter: str | None = None,
        offset: int | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        status: str | None = None,
        statuses: Sequence[str] | None = None,
        tg_ids: Sequence[str] | None = None,
        with_attributes: bool | None = None,
    ) -> OwnedNFTsResponse:
        """List NFTs owned by the authenticated user."""
        params = nft_query(
            collection_id=collection_id,
            collection_ids=collection_ids,
            external_collection_number=external_collection_number,
            filter_by_backdrops=filter_by_backdrops,
            filter_by_models=filter_by_models,
            filter_by_symbols=filter_by_symbols,
            ids=ids,
            limit=limit,
            max_price=max_price,
            min_price=min_price,
            mint_status=mint_status,
            name_filter=name_filter,
            offset=offset,
            search=search,
            sort_by=sort_by,
            status=status,
            statuses=statuses,
            tg_ids=tg_ids,
            with_attributes=with_attributes,
        )
        return await self._transport.request(
            "GET", "/partners/nfts/owned", params=params, response_model=OwnedNFTsResponse
        )

    async def buy(self, nft_details: Sequence[BuyDetail]) -> BuyResponse:
        """Purchase 1 to 50 NFTs. Inspect `purchase_results` for per-NFT outcomes."""
        details = list(batch(nft_details, "nft_details"))
        request = BuyRequest(nft_details=details)
        return await self._transport.request(
            "POST", "/partners/nfts", json_data=request, response_model=BuyResponse
        )

    async def bulk_list(self, nft_prices: Sequence[NFTPriceDetail]) -> BulkListingResult:
        """List multiple owned NFTs for sale."""
        prices = _nonempty(nft_prices, "nft_prices")
        request = BulkListRequest(nft_prices=prices)
        return await self._transport.request(
            "POST",
            "/partners/nfts/bulk-list",
            json_data=request,
            response_model=BulkListingResult,
        )

    async def bulk_unlist(self, nft_ids: Sequence[str]) -> BulkListingResult:
        """Remove multiple owned NFTs from sale."""
        request = BulkDelistRequest(nft_ids=_nonempty(nft_ids, "nft_ids"))
        return await self._transport.request(
            "POST",
            "/partners/nfts/bulk-unlist",
            json_data=request,
            response_model=BulkListingResult,
        )

    async def stats(self) -> NFTStats:
        """Fetch counts of listed and unlisted NFTs owned by the authenticated user."""
        return await self._transport.request("GET", "/partners/nfts/stats", response_model=NFTStats)

    async def transfer(
        self,
        *,
        nft_ids: Sequence[str],
        recipient: str | None = None,
        recipient_token: str | None = None,
        anonymous: bool | None = None,
    ) -> TransferGiftsResponse:
        """Transfer owned NFTs to a recipient username/ID or recipient token."""
        if (recipient is None) == (recipient_token is None):
            raise ValueError("Provide exactly one of recipient or recipient_token")
        request = TransferGiftsRequest(
            nft_ids=_nonempty(nft_ids, "nft_ids"),
            recipient=recipient,
            recipient_token=recipient_token,
            anonymous=anonymous,
        )
        return await self._transport.request(
            "POST",
            "/partners/nfts/transfer",
            json_data=request,
            response_model=TransferGiftsResponse,
        )

    async def withdraw(
        self,
        gift_ids: Sequence[str],
        *,
        recipient_id: int | None = None,
        unsafe_transfer: bool | None = None,
    ) -> WithdrawGiftsResponse:
        """Withdraw owned gifts from Portals to Telegram."""
        request = WithdrawGiftsRequest(
            gift_ids=_nonempty(gift_ids, "gift_ids"),
            recipient_id=recipient_id,
            unsafe_transfer=unsafe_transfer,
        )
        return await self._transport.request(
            "POST",
            "/partners/nfts/withdraw",
            json_data=request,
            response_model=WithdrawGiftsResponse,
        )

    async def withdrawal_statuses(self, ids: Sequence[int]) -> WithdrawalStatusesResponse:
        """Fetch the status of one or more gift withdrawals by ID."""
        if not ids:
            raise ValueError("ids must not be empty")
        return await self._transport.request(
            "GET",
            "/partners/nfts/withdrawals/statuses",
            params={"ids": ids},
            response_model=WithdrawalStatusesResponse,
        )

    async def list(self, nft_id: str, *, price: Amount | str) -> None:
        """List a single owned NFT for sale at the specified price."""
        path = f"/partners/nfts/{quote(nft_id, safe='')}/list"
        request = ListNFTRequest(price=_amount(price))
        await self._transport.request("POST", path, json_data=request)

    async def unlist(self, nft_id: str) -> None:
        """Remove a single owned NFT from sale."""
        path = f"/partners/nfts/{quote(nft_id, safe='')}/unlist"
        await self._transport.request("POST", path)


_T = TypeVar("_T")


def _nonempty(values: Sequence[_T], name: str) -> list[_T]:
    result = list(values)
    if not result:
        raise ValueError(f"{name} must not be empty")
    return result
