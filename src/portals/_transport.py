from __future__ import annotations

import asyncio
import threading
from collections.abc import Mapping, Sequence
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from functools import cache
from typing import Any

import httpx2
from pydantic import BaseModel, TypeAdapter, ValidationError

from ._models import RateLimit
from .exceptions import (
    AccessDeniedError,
    APIError,
    AuthenticationError,
    BetOutcomeUnknownError,
    InvalidResponseError,
    MarketFeedUnavailableError,
    RateLimitError,
    ResponseValidationError,
    TransportError,
)


@cache
def _adapter(model: Any) -> TypeAdapter[Any]:
    return TypeAdapter(model)


def dump_model(model: BaseModel) -> dict[str, Any]:
    return model.model_dump(mode="json", by_alias=True, exclude_none=True)


def prepare_params(params: Mapping[str, Any] | None) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in (params or {}).items():
        if value is None:
            continue
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            value = ",".join(str(_param_value(item)) for item in value)
        else:
            value = _param_value(value)
        result[key] = value
    return result


def _param_value(value: Any) -> Any:
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


class BaseTransport:
    def __init__(
        self,
        api_key: str,
        *,
        base_url: str,
        timeout: float | httpx2.Timeout,
    ) -> None:
        if not api_key.strip():
            raise ValueError("api_key must not be empty")
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._headers = {
            "Authorization": f"partners {api_key}",
            "Accept": "application/json",
            "User-Agent": "portals-api-python/0.1.0",
        }
        self.last_rate_limit: RateLimit | None = None

    def _url(self, path: str) -> str:
        if not path.startswith("/"):
            raise ValueError("path must start with '/'")
        return f"{self._base_url}{path}"

    def _handle_response(self, response: httpx2.Response, response_model: Any) -> Any:
        self.last_rate_limit = RateLimit.from_headers(response.headers)
        if response.status_code >= 400:
            self._raise_api_error(response)
        if response.status_code == 204 or not response.content:
            return None
        try:
            data = response.json()
        except ValueError as exc:
            raise InvalidResponseError("The Portals API returned invalid JSON") from exc
        if response_model is None:
            return data
        try:
            return _adapter(response_model).validate_python(data)
        except ValidationError as exc:
            raise ResponseValidationError(
                f"The response from {response.request.method} {response.request.url.path} "
                "does not match the expected model",
                response=data,
            ) from exc

    def _raise_api_error(self, response: httpx2.Response) -> None:
        try:
            data = response.json() if response.content else None
        except ValueError:
            data = None
        if isinstance(data, dict):
            message = str(
                data.get("message")
                or f"Portals API request failed with HTTP {response.status_code}"
            )
            code = str(data["code"]) if data.get("code") is not None else None
        else:
            message = response.text.strip() or (
                f"Portals API request failed with HTTP {response.status_code}"
            )
            code = None

        error_type: type[APIError] = APIError
        if response.status_code == 401:
            error_type = AuthenticationError
        elif response.status_code == 403:
            error_type = AccessDeniedError
        elif response.status_code == 429:
            error_type = RateLimitError
        elif response.status_code == 503 and code == "MARKET_FEED_UNAVAILABLE":
            error_type = MarketFeedUnavailableError
        elif response.status_code == 504 and code == "BET_OUTCOME_UNKNOWN":
            error_type = BetOutcomeUnknownError
        raise error_type(
            message,
            status_code=response.status_code,
            code=code,
            response=data,
            rate_limit=self.last_rate_limit,
        )


class SyncTransport(BaseTransport):
    def __init__(
        self,
        api_key: str,
        *,
        base_url: str,
        timeout: float | httpx2.Timeout,
        client: httpx2.Client | None = None,
    ) -> None:
        super().__init__(api_key, base_url=base_url, timeout=timeout)
        self._client = client
        self._owns_client = client is None
        self._lock = threading.Lock()

    def _get_client(self) -> httpx2.Client:
        if self._client is None:
            with self._lock:
                if self._client is None:
                    self._client = httpx2.Client(timeout=self._timeout)
        return self._client

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json_data: Any = None,
        response_model: Any = None,
    ) -> Any:
        if isinstance(json_data, BaseModel):
            json_data = dump_model(json_data)
        try:
            response = self._get_client().request(
                method,
                self._url(path),
                params=prepare_params(params),
                json=json_data,
                headers=self._headers,
                timeout=self._timeout,
            )
        except httpx2.HTTPError as exc:
            raise TransportError(f"Could not reach the Portals API: {exc}", original=exc) from exc
        return self._handle_response(response, response_model)

    def close(self) -> None:
        client, self._client = self._client, None
        if self._owns_client and client is not None:
            client.close()


class AsyncTransport(BaseTransport):
    def __init__(
        self,
        api_key: str,
        *,
        base_url: str,
        timeout: float | httpx2.Timeout,
        client: httpx2.AsyncClient | None = None,
    ) -> None:
        super().__init__(api_key, base_url=base_url, timeout=timeout)
        self._client = client
        self._owns_client = client is None
        self._lock = asyncio.Lock()

    async def _get_client(self) -> httpx2.AsyncClient:
        if self._client is None:
            async with self._lock:
                if self._client is None:
                    self._client = httpx2.AsyncClient(timeout=self._timeout)
        return self._client

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        json_data: Any = None,
        response_model: Any = None,
    ) -> Any:
        if isinstance(json_data, BaseModel):
            json_data = dump_model(json_data)
        try:
            client = await self._get_client()
            response = await client.request(
                method,
                self._url(path),
                params=prepare_params(params),
                json=json_data,
                headers=self._headers,
                timeout=self._timeout,
            )
        except httpx2.HTTPError as exc:
            raise TransportError(f"Could not reach the Portals API: {exc}", original=exc) from exc
        return self._handle_response(response, response_model)

    async def aclose(self) -> None:
        client, self._client = self._client, None
        if self._owns_client and client is not None:
            await client.aclose()
