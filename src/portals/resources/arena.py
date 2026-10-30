from __future__ import annotations

from collections.abc import Sequence
from typing import Literal

from .._models import Amount
from .._transport import AsyncTransport, SyncTransport
from ..models import (
    ArenaBetRequest,
    ArenaBetResponse,
    ArenaInventoryResponse,
    ArenaStateResponse,
)
from ._helpers import amount as _amount
from ._helpers import batch


class Arena:
    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def state(self) -> ArenaStateResponse:
        return self._transport.request(
            "GET", "/partners/arena/state", response_model=ArenaStateResponse
        )

    def inventory(
        self,
        *,
        limit: int | None = 150,
        offset: int | None = None,
        search: str | None = None,
        status: Literal["listed", "unlisted"] | None = None,
        statuses: Sequence[str] | None = None,
        collection: Sequence[str] | None = None,
        sort_by: str | None = None,
    ) -> ArenaInventoryResponse:
        if limit is not None and not 1 <= limit <= 150:
            raise ValueError("limit must be between 1 and 150")
        params = {
            "limit": limit,
            "offset": offset,
            "search": search,
            "status": status,
            "statuses": statuses,
            "collection": collection,
            "sort_by": sort_by,
        }
        return self._transport.request(
            "GET",
            "/partners/arena/inventory",
            params=params,
            response_model=ArenaInventoryResponse,
        )

    def bet(
        self,
        *,
        room_id: int,
        amount: Amount | str | None = None,
        gift_ids: Sequence[str] | None = None,
        team_id: str | None = None,
    ) -> ArenaBetResponse:
        request = _bet_request(room_id, amount, gift_ids, team_id)
        return self._transport.request(
            "POST", "/partners/arena/bet", json_data=request, response_model=ArenaBetResponse
        )


class AsyncArena:
    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def state(self) -> ArenaStateResponse:
        return await self._transport.request(
            "GET", "/partners/arena/state", response_model=ArenaStateResponse
        )

    async def inventory(
        self,
        *,
        limit: int | None = 150,
        offset: int | None = None,
        search: str | None = None,
        status: Literal["listed", "unlisted"] | None = None,
        statuses: Sequence[str] | None = None,
        collection: Sequence[str] | None = None,
        sort_by: str | None = None,
    ) -> ArenaInventoryResponse:
        if limit is not None and not 1 <= limit <= 150:
            raise ValueError("limit must be between 1 and 150")
        params = {
            "limit": limit,
            "offset": offset,
            "search": search,
            "status": status,
            "statuses": statuses,
            "collection": collection,
            "sort_by": sort_by,
        }
        return await self._transport.request(
            "GET",
            "/partners/arena/inventory",
            params=params,
            response_model=ArenaInventoryResponse,
        )

    async def bet(
        self,
        *,
        room_id: int,
        amount: Amount | str | None = None,
        gift_ids: Sequence[str] | None = None,
        team_id: str | None = None,
    ) -> ArenaBetResponse:
        request = _bet_request(room_id, amount, gift_ids, team_id)
        return await self._transport.request(
            "POST", "/partners/arena/bet", json_data=request, response_model=ArenaBetResponse
        )


def _bet_request(
    room_id: int,
    amount: Amount | str | None,
    gift_ids: Sequence[str] | None,
    team_id: str | None,
) -> ArenaBetRequest:
    if (amount is None) == (gift_ids is None):
        raise ValueError("Provide exactly one of amount or gift_ids")
    if amount is not None:
        return ArenaBetRequest(
            room_id=room_id, bet_type="ton", amount=_amount(amount), team_id=team_id
        )
    gifts = list(batch(gift_ids or (), "gift_ids"))
    return ArenaBetRequest(room_id=room_id, bet_type="gift", gift_ids=gifts, team_id=team_id)
