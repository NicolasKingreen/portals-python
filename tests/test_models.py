from __future__ import annotations

from decimal import Decimal

import pytest
from pydantic import TypeAdapter, ValidationError

import portals
from portals import (
    Amount,
    ArenaBetRequest,
    BuyDetail,
    ErrorResponse,
    NFTStatus,
    RateLimit,
    Wallet,
)
from portals._models import PortalsModel, PortalsRequest, PortalsResponse

_amount_adapter: TypeAdapter[Decimal] = TypeAdapter(Amount)


def test_amount_accepts_decimal_and_string() -> None:
    assert _amount_adapter.validate_python("12.50") == Decimal("12.50")
    assert _amount_adapter.validate_python(Decimal("0.00000001")) == Decimal("0.00000001")
    assert _amount_adapter.dump_python(Decimal("0.00000001")) == "0.00000001"
    assert _amount_adapter.dump_python(Decimal("12.50")) == "12.50"


@pytest.mark.parametrize(
    "bad_value",
    [12.5, 10, True, None, "not-a-number", "NaN", "Infinity", "-Infinity", Decimal("NaN")],
)
def test_amount_rejects_non_decimal_or_non_finite(bad_value: object) -> None:
    with pytest.raises(ValidationError):
        _amount_adapter.validate_python(bad_value)


def test_request_models_forbid_extra_fields() -> None:
    detail = BuyDetail(id="nft-1", price="10.5")
    assert isinstance(detail, PortalsRequest)
    assert isinstance(detail, PortalsModel)
    assert detail.price == Decimal("10.5")

    with pytest.raises(ValidationError):
        BuyDetail(id="nft-1", price="10.5", pirce="10.5")  # type: ignore[call-arg]

    with pytest.raises(ValidationError):
        ArenaBetRequest(room_id=1, bet_type="ton", amount="5", extra_field=1)  # type: ignore[call-arg]


def test_response_models_allow_extra_fields() -> None:
    wallet = Wallet.model_validate(
        {"balance": "100.25", "frozen_funds": "5.00", "future_field": "kept"}
    )
    assert isinstance(wallet, PortalsResponse)
    assert isinstance(wallet, PortalsModel)
    assert wallet.balance == Decimal("100.25")
    assert wallet.frozen_funds == Decimal("5.00")
    assert wallet.model_extra == {"future_field": "kept"}

    err = ErrorResponse.model_validate({"code": "ERR", "message": "oops", "trace_id": "abc"})
    assert err.model_extra == {"trace_id": "abc"}


def test_strenum_formats_as_value() -> None:
    value: str = NFTStatus.LISTED
    assert value == "listed"
    assert str(NFTStatus.LISTED) == "listed"
    assert f"{NFTStatus.LISTED}" == "listed"


def test_rate_limit_from_headers() -> None:
    rl = RateLimit.from_headers(
        {
            "X-RateLimit-Limit": "120",
            "x-ratelimit-remaining": "119",
            "X-Ratelimit-Reset": "45",
        }
    )
    assert rl == RateLimit(limit=120, remaining=119, reset_seconds=45)
    assert RateLimit.from_headers({}) is None
    assert RateLimit.from_headers({"X-RateLimit-Limit": "not-an-int"}) is None


def test_package_versions_exposed() -> None:
    from importlib.metadata import version

    assert portals.__version__ == version("portals-api")
    assert portals.__api_version__ == "1.0.0"
