from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import Literal
from urllib.parse import quote

from .._transport import AsyncTransport, SyncTransport
from ..models import (
    AttributeFloorsResponse,
    CollectionMetricsResponse,
    CollectionsPreviewResponse,
    FloorPricesResponse,
    ModelBackgroundFloorsResponse,
)


class Collections:
    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def attribute_floors(self) -> AttributeFloorsResponse:
        return self._transport.request(
            "GET",
            "/partners/collections/attribute-floors",
            response_model=AttributeFloorsResponse,
        )

    def backdrop_floors(self) -> FloorPricesResponse:
        return self._transport.request(
            "GET", "/partners/collections/backdrops/floors", response_model=FloorPricesResponse
        )

    def floors(self) -> FloorPricesResponse:
        return self._transport.request(
            "GET", "/partners/collections/floors", response_model=FloorPricesResponse
        )

    def model_background_floors(self, models: Sequence[str]) -> ModelBackgroundFloorsResponse:
        if not models:
            raise ValueError("models must not be empty")
        return self._transport.request(
            "GET",
            "/partners/collections/models/backgrounds/floors",
            params={"models": models},
            response_model=ModelBackgroundFloorsResponse,
        )

    def preview(
        self,
        *,
        sort_by: Literal["name", "floor_price"] | None = None,
        sort_order: Literal["asc", "desc"] | None = None,
    ) -> CollectionsPreviewResponse:
        return self._transport.request(
            "GET",
            "/partners/collections/preview",
            params={"sort_by": sort_by, "sort_order": sort_order},
            response_model=CollectionsPreviewResponse,
        )

    def metrics(
        self,
        collection_id: str,
        *,
        group_by: Literal["hour", "day", "week", "month"],
        from_: datetime | str | None = None,
        to: datetime | str | None = None,
    ) -> CollectionMetricsResponse:
        return self._transport.request(
            "GET",
            f"/partners/collections/{quote(collection_id, safe='')}/metrics",
            params={"from": from_, "group_by": group_by, "to": to},
            response_model=CollectionMetricsResponse,
        )


class AsyncCollections:
    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def attribute_floors(self) -> AttributeFloorsResponse:
        return await self._transport.request(
            "GET",
            "/partners/collections/attribute-floors",
            response_model=AttributeFloorsResponse,
        )

    async def backdrop_floors(self) -> FloorPricesResponse:
        return await self._transport.request(
            "GET", "/partners/collections/backdrops/floors", response_model=FloorPricesResponse
        )

    async def floors(self) -> FloorPricesResponse:
        return await self._transport.request(
            "GET", "/partners/collections/floors", response_model=FloorPricesResponse
        )

    async def model_background_floors(self, models: Sequence[str]) -> ModelBackgroundFloorsResponse:
        if not models:
            raise ValueError("models must not be empty")
        return await self._transport.request(
            "GET",
            "/partners/collections/models/backgrounds/floors",
            params={"models": models},
            response_model=ModelBackgroundFloorsResponse,
        )

    async def preview(
        self,
        *,
        sort_by: Literal["name", "floor_price"] | None = None,
        sort_order: Literal["asc", "desc"] | None = None,
    ) -> CollectionsPreviewResponse:
        return await self._transport.request(
            "GET",
            "/partners/collections/preview",
            params={"sort_by": sort_by, "sort_order": sort_order},
            response_model=CollectionsPreviewResponse,
        )

    async def metrics(
        self,
        collection_id: str,
        *,
        group_by: Literal["hour", "day", "week", "month"],
        from_: datetime | str | None = None,
        to: datetime | str | None = None,
    ) -> CollectionMetricsResponse:
        return await self._transport.request(
            "GET",
            f"/partners/collections/{quote(collection_id, safe='')}/metrics",
            params={"from": from_, "group_by": group_by, "to": to},
            response_model=CollectionMetricsResponse,
        )
