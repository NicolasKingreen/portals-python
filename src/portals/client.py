from __future__ import annotations

from collections.abc import Mapping
from types import TracebackType
from typing import Any, TypeVar, overload

import httpx2

from ._models import RateLimit
from ._transport import AsyncTransport, SyncTransport
from .resources.arena import Arena, AsyncArena
from .resources.collection_offers import AsyncCollectionOffers, CollectionOffers
from .resources.collections import AsyncCollections, Collections
from .resources.market import AsyncMarket, Market
from .resources.nfts import AsyncNFTs, NFTs
from .resources.users import AsyncUsers, Users
from .resources.wallet import AsyncWalletResource, WalletResource

_T = TypeVar("_T")


class PortalsClient:
    """Synchronous client for the Portals Partners API.

    Args:
        api_key: Partner API token sent as `Authorization: partners <api_key>`.
        base_url: Base URL for the Portals API.
        timeout: Request timeout in seconds or an `httpx2.Timeout` instance.
        client: Optional pre-configured `httpx2.Client`. When provided, the
            caller retains ownership and is responsible for closing it.

    Attributes:
        arena: Arena rooms, inventory, and bets.
        offers: Collection offers.
        collections: Collection previews, metrics, and floor prices.
        market: Marketplace configuration and activity.
        nfts: NFT search, ownership, trading, and withdrawals.
        users: User existence and activity history.
        wallet: TON wallet balance, deposits, and withdrawals.
    """

    arena: Arena
    offers: CollectionOffers
    collections: Collections
    market: Market
    nfts: NFTs
    users: Users
    wallet: WalletResource

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://portal-market.com",
        timeout: float | httpx2.Timeout = 30.0,
        client: httpx2.Client | None = None,
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
        """Rate-limit metadata parsed from the most recent HTTP response, if present."""
        return self._transport.last_rate_limit

    @overload
    def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json_data: Any = None,
        response_model: None = None,
    ) -> Any: ...

    @overload
    def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json_data: Any = None,
        response_model: type[_T],
    ) -> _T: ...

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json_data: Any = None,
        response_model: Any = None,
    ) -> Any:
        """Send an arbitrary request to the Portals API and optionally validate the response."""
        return self._transport.request(
            method,
            path,
            params=params,
            json_data=json_data,
            response_model=response_model,
        )

    def close(self) -> None:
        """Close the underlying HTTP client if it was created by this instance."""
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
    """Asynchronous client for the Portals Partners API.

    Args:
        api_key: Partner API token sent as `Authorization: partners <api_key>`.
        base_url: Base URL for the Portals API.
        timeout: Request timeout in seconds or an `httpx2.Timeout` instance.
        client: Optional pre-configured `httpx2.AsyncClient`. When provided, the
            caller retains ownership and is responsible for closing it.

    Attributes:
        arena: Arena rooms, inventory, and bets.
        offers: Collection offers.
        collections: Collection previews, metrics, and floor prices.
        market: Marketplace configuration and activity.
        nfts: NFT search, ownership, trading, and withdrawals.
        users: User existence and activity history.
        wallet: TON wallet balance, deposits, and withdrawals.
    """

    arena: AsyncArena
    offers: AsyncCollectionOffers
    collections: AsyncCollections
    market: AsyncMarket
    nfts: AsyncNFTs
    users: AsyncUsers
    wallet: AsyncWalletResource

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://portal-market.com",
        timeout: float | httpx2.Timeout = 30.0,
        client: httpx2.AsyncClient | None = None,
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
        """Rate-limit metadata parsed from the most recent HTTP response, if present."""
        return self._transport.last_rate_limit

    @overload
    async def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json_data: Any = None,
        response_model: None = None,
    ) -> Any: ...

    @overload
    async def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json_data: Any = None,
        response_model: type[_T],
    ) -> _T: ...

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json_data: Any = None,
        response_model: Any = None,
    ) -> Any:
        """Send an arbitrary request to the Portals API and optionally validate the response."""
        return await self._transport.request(
            method,
            path,
            params=params,
            json_data=json_data,
            response_model=response_model,
        )

    async def aclose(self) -> None:
        """Close the underlying async HTTP client if it was created by this instance."""
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
