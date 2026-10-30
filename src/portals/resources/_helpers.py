from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from pydantic import TypeAdapter

from .._models import Amount

_amount_adapter = TypeAdapter(Amount)


def amount(value: Amount) -> Any:
    return _amount_adapter.validate_python(value)


def batch(values: Sequence[Any], name: str, maximum: int = 50) -> tuple[Any, ...]:
    result = tuple(values)
    if not 1 <= len(result) <= maximum:
        raise ValueError(f"{name} must contain between 1 and {maximum} items")
    return result


def nft_query(
    *,
    collection_id: str | None,
    collection_ids: Sequence[str] | None,
    external_collection_number: int | None,
    filter_by_backdrops: Sequence[str] | None,
    filter_by_models: Sequence[str] | None,
    filter_by_symbols: Sequence[str] | None,
    ids: Sequence[str] | None,
    limit: int | None,
    max_price: Amount | None,
    min_price: Amount | None,
    mint_status: str | None,
    name_filter: str | None,
    offset: int | None,
    search: str | None,
    sort_by: str | None,
    status: str | None,
    statuses: Sequence[str] | None,
    tg_ids: Sequence[str] | None,
    is_owned: bool | None = None,
    with_attributes: bool | None = None,
) -> dict[str, Any]:
    return {
        "collection_id": collection_id,
        "collection_ids": collection_ids,
        "external_collection_number": external_collection_number,
        "filter_by_backdrops": filter_by_backdrops,
        "filter_by_models": filter_by_models,
        "filter_by_symbols": filter_by_symbols,
        "ids": ids,
        "is_owned": is_owned,
        "limit": limit,
        "max_price": amount(max_price) if max_price is not None else None,
        "min_price": amount(min_price) if min_price is not None else None,
        "mint_status": mint_status,
        "name_filter": name_filter,
        "offset": offset,
        "search": search,
        "sort_by": sort_by,
        "status": status,
        "statuses": statuses,
        "tg_ids": tg_ids,
        "with_attributes": with_attributes,
    }


def market_query(
    *,
    action_types: Sequence[str] | None,
    collection_id: str | None,
    collection_ids: Sequence[str] | None,
    external_collection_number: int | None,
    filter_by_backdrops: Sequence[str] | None,
    filter_by_models: Sequence[str] | None,
    filter_by_symbols: Sequence[str] | None,
    limit: int | None,
    max_price: Amount | None,
    min_price: Amount | None,
    offset: int | None,
    period: str | None,
    status: str | None,
    sort_by: str | None = None,
) -> dict[str, Any]:
    return {
        "action_types": action_types,
        "collection_id": collection_id,
        "collection_ids": collection_ids,
        "external_collection_number": external_collection_number,
        "filter_by_backdrops": filter_by_backdrops,
        "filter_by_models": filter_by_models,
        "filter_by_symbols": filter_by_symbols,
        "limit": limit,
        "max_price": amount(max_price) if max_price is not None else None,
        "min_price": amount(min_price) if min_price is not None else None,
        "offset": offset,
        "period": period,
        "sort_by": sort_by,
        "status": status,
    }
