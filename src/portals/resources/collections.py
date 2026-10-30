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
    """Synchronous collections resource (`/partners/collections/*`)."""

    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def attribute_floors(self) -> AttributeFloorsResponse:
        """Fetch floor prices across all unique collection attributes."""
        return self._transport.request(
            "GET",
            "/partners/collections/attribute-floors",
            response_model=AttributeFloorsResponse,
        )

    def backdrop_floors(self) -> FloorPricesResponse:
        """Fetch floor prices grouped by backdrop."""
        return self._transport.request(
            "GET", "/partners/collections/backdrops/floors", response_model=FloorPricesResponse
        )

    def floors(self) -> FloorPricesResponse:
        """Fetch floor prices for all collections."""
        return self._transport.request(
            "GET", "/partners/collections/floors", response_model=FloorPricesResponse
        )

    def model_background_floors(self, models: Sequence[str]) -> ModelBackgroundFloorsResponse:
        """Fetch backdrop floor prices for specific model names."""
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
        """List collections with preview metadata and floor prices."""
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
        """Fetch historical volume and price metrics for a collection."""
        return self._transport.request(
            "GET",
            f"/partners/collections/{quote(collection_id, safe='')}/metrics",
            params={"from": from_, "group_by": group_by, "to": to},
            response_model=CollectionMetricsResponse,
        )


class AsyncCollections:
    """Asynchronous collections resource (`/partners/collections/*`)."""

    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def attribute_floors(self) -> AttributeFloorsResponse:
        """Fetch floor prices across all unique collection attributes."""
        return await self._transport.request(
            "GET",
            "/partners/collections/attribute-floors",
            response_model=AttributeFloorsResponse,
        )

    async def backdrop_floors(self) -> FloorPricesResponse:
        """Fetch floor prices grouped by backdrop."""
        return await self._transport.request(
            "GET", "/partners/collections/backdrops/floors", response_model=FloorPricesResponse
        )

    async def floors(self) -> FloorPricesResponse:
        """Fetch floor prices for all collections."""
        return await self._transport.request(
            "GET", "/partners/collections/floors", response_model=FloorPricesResponse
        )

    async def model_background_floors(self, models: Sequence[str]) -> ModelBackgroundFloorsResponse:
        """Fetch backdrop floor prices for specific model names."""
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
        """List collections with preview metadata and floor prices."""
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
        """Fetch historical volume and price metrics for a collection."""
        return await self._transport.request(
            "GET",
            f"/partners/collections/{quote(collection_id, safe='')}/metrics",
            params={"from": from_, "group_by": group_by, "to": to},
            response_model=CollectionMetricsResponse,
        )
