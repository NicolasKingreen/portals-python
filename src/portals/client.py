from __future__ import annotations

from collections.abc import Mapping
from types import TracebackType
from typing import Any

import httpx

from ._models import RateLimit
from ._transport import AsyncTransport, SyncTransport
from .resources.arena import Arena, AsyncArena
from .resources.collection_offers import AsyncCollectionOffers, CollectionOffers
from .resources.collections import AsyncCollections, Collections
from .resources.market import AsyncMarket, Market
from .resources.nfts import AsyncNFTs, NFTs
from .resources.users import AsyncUsers, Users
from .resources.wallet import AsyncWalletResource, WalletResource


class PortalsClient:
    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://portal-market.com",
        timeout: float | httpx.Timeout = 30.0,
        client: httpx.Client | None = None,
    ) -> None:
        self._transport = SyncTransport(api_key, base_url=base_url, timeout=timeout, client=client)
        self.arena = Arena(self._transport)
        self.offers = CollectionOffers(self._transport)
        self.collections = Collections(self._transport)
        self.market = Market(self._transport)
        self.nfts = NFTs(self._transport)
        self.users = Users(self._transport)
        self.wallet = WalletResource(self._transport)

    @property
    def last_rate_limit(self) -> RateLimit | None:
        return self._transport.last_rate_limit

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json_data: Any = None,
        response_model: Any = None,
    ) -> Any:
        return self._transport.request(
            method,
            path,
            params=params,
            json_data=json_data,
            response_model=response_model,
        )

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> PortalsClient:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()


class AsyncPortalsClient:
    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://portal-market.com",
        timeout: float | httpx.Timeout = 30.0,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._transport = AsyncTransport(api_key, base_url=base_url, timeout=timeout, client=client)
        self.arena = AsyncArena(self._transport)
        self.offers = AsyncCollectionOffers(self._transport)
        self.collections = AsyncCollections(self._transport)
        self.market = AsyncMarket(self._transport)
        self.nfts = AsyncNFTs(self._transport)
        self.users = AsyncUsers(self._transport)
        self.wallet = AsyncWalletResource(self._transport)

    @property
    def last_rate_limit(self) -> RateLimit | None:
        return self._transport.last_rate_limit

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json_data: Any = None,
        response_model: Any = None,
    ) -> Any:
        return await self._transport.request(
            method,
            path,
            params=params,
            json_data=json_data,
            response_model=response_model,
        )

    async def aclose(self) -> None:
        await self._transport.aclose()

    async def __aenter__(self) -> AsyncPortalsClient:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.aclose()
