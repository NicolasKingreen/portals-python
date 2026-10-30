from __future__ import annotations

from collections.abc import Sequence

from .._models import Amount
from .._transport import AsyncTransport, SyncTransport
from ..models import UserActionsResponse, UserExistence
from ._helpers import market_query
from .market import _validate_feed_window


class Users:
    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def exists(self, user_id: int) -> UserExistence:
        return self._transport.request(
            "GET", f"/partners/users/{user_id}", response_model=UserExistence
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
        max_price: Amount | None = None,
        min_price: Amount | None = None,
        offset: int | None = 0,
        period: str | None = None,
        status: str | None = None,
    ) -> UserActionsResponse:
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
            status=status,
        )
        return self._transport.request(
            "GET",
            "/partners/users/actions",
            params=params,
            response_model=UserActionsResponse,
        )


class AsyncUsers:
    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def exists(self, user_id: int) -> UserExistence:
        return await self._transport.request(
            "GET", f"/partners/users/{user_id}", response_model=UserExistence
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
        max_price: Amount | None = None,
        min_price: Amount | None = None,
        offset: int | None = 0,
        period: str | None = None,
        status: str | None = None,
    ) -> UserActionsResponse:
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
            status=status,
        )
        return await self._transport.request(
            "GET",
            "/partners/users/actions",
            params=params,
            response_model=UserActionsResponse,
        )
