from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, ConfigDict, PlainSerializer


def _amount(value: Any) -> Decimal:
    if not isinstance(value, (str, Decimal)):
        raise ValueError("Amounts must be decimal strings or Decimal instances")
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"Invalid decimal amount: {value!r}") from exc
    if not result.is_finite():
        raise ValueError("Amounts must be finite")
    return result


def _serialize_amount(value: Decimal) -> str:
    return format(value, "f")


Amount = Annotated[
    Decimal,
    BeforeValidator(_amount),
    PlainSerializer(_serialize_amount, return_type=str),
]


class PortalsModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class PortalsRequest(PortalsModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class PortalsResponse(PortalsModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)


@dataclass(frozen=True, slots=True)
class RateLimit:
    limit: int
    remaining: int
    reset_seconds: int

    @classmethod
    def from_headers(cls, headers: Mapping[str, str]) -> RateLimit | None:
        normalized = {key.lower(): value for key, value in headers.items()}
        try:
            return cls(
                limit=int(normalized["x-ratelimit-limit"]),
                remaining=int(normalized["x-ratelimit-remaining"]),
                reset_seconds=int(normalized["x-ratelimit-reset"]),
            )
        except (KeyError, TypeError, ValueError):
            return None
