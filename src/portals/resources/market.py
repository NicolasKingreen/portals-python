from __future__ import annotations

from collections.abc import Sequence

from .._models import Amount
from .._transport import AsyncTransport, SyncTransport
from ..models import MarketActionsResponse, MarketConfig
from ._helpers import market_query


class Market:
    """Synchronous market resource (`/partners/market/*`)."""

    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def config(self) -> MarketConfig:
        """Fetch marketplace configuration, commission rates, and exchange rates."""
        return self._transport.request(
            "GET", "/partners/market/config", response_model=MarketConfig
        )

    def actions(
        self,
        *,
        action_types: Sequence[str] | None = None,
        collection_id: str | None = None,
        collection_ids: Sequence[str] | None = None,
        external_collection_number: int | None = None,
        filter_by_backdrops: Sequence[str] | None = None,
        filter_by_models: Sequence[str] | None = None,
        filter_by_symbols: Sequence[str] | None = None,
        limit: int | None = 20,
        max_price: Amount | str | None = None,
        min_price: Amount | str | None = None,
        offset: int | None = 0,
        period: str | None = None,
        sort_by: str | None = None,
        status: str | None = None,
    ) -> MarketActionsResponse:
        """Fetch the anonymized global marketplace activity feed (1 <= limit <= 20, 0 <= offset <= 700)."""
        _validate_feed_window(limit, offset)
        params = market_query(
            action_types=action_types,
            collection_id=collection_id,
            collection_ids=collection_ids,
            external_collection_number=external_collection_number,
            filter_by_backdrops=filter_by_backdrops,
            filter_by_models=filter_by_models,
            filter_by_symbols=filter_by_symbols,
            limit=limit,
            max_price=max_price,
            min_price=min_price,
            offset=offset,
            period=period,
            sort_by=sort_by,
            status=status,
        )
        return self._transport.request(
            "GET",
            "/partners/market/actions/",
            params=params,
            response_model=MarketActionsResponse,
        )


class AsyncMarket:
    """Asynchronous market resource (`/partners/market/*`)."""

    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def config(self) -> MarketConfig:
        """Fetch marketplace configuration, commission rates, and exchange rates."""
        return await self._transport.request(
            "GET", "/partners/market/config", response_model=MarketConfig
        )

    async def actions(
        self,
        *,
        action_types: Sequence[str] | None = None,
        collection_id: str | None = None,
        collection_ids: Sequence[str] | None = None,
        external_collection_number: int | None = None,
        filter_by_backdrops: Sequence[str] | None = None,
        filter_by_models: Sequence[str] | None = None,
        filter_by_symbols: Sequence[str] | None = None,
        limit: int | None = 20,
        max_price: Amount | str | None = None,
        min_price: Amount | str | None = None,
        offset: int | None = 0,
        period: str | None = None,
        sort_by: str | None = None,
        status: str | None = None,
    ) -> MarketActionsResponse:
        """Fetch the anonymized global marketplace activity feed (1 <= limit <= 20, 0 <= offset <= 700)."""
        _validate_feed_window(limit, offset)
        params = market_query(
            action_types=action_types,
            collection_id=collection_id,
            collection_ids=collection_ids,
            external_collection_number=external_collection_number,
            filter_by_backdrops=filter_by_backdrops,
            filter_by_models=filter_by_models,
            filter_by_symbols=filter_by_symbols,
            limit=limit,
            max_price=max_price,
            min_price=min_price,
            offset=offset,
            period=period,
            sort_by=sort_by,
            status=status,
        )
        return await self._transport.request(
            "GET",
            "/partners/market/actions/",
            params=params,
            response_model=MarketActionsResponse,
        )


def _validate_feed_window(limit: int | None, offset: int | None) -> None:
    if limit is not None and not 1 <= limit <= 20:
        raise ValueError("limit must be between 1 and 20")
    if offset is not None and not 0 <= offset <= 700:
        raise ValueError("offset must be between 0 and 700")
