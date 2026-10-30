from __future__ import annotations

from collections.abc import Sequence

from .._models import Amount
from .._transport import AsyncTransport, SyncTransport
from ..models import (
    Deposit,
    TONWithdrawal,
    TONWithdrawalStatuses,
    Wallet,
    WithdrawTONRequest,
)
from ._helpers import amount as _amount


class WalletResource:
    """Synchronous wallet resource (`/partners/users/wallets/*` and `/partners/deposits`)."""

    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport

    def get(self) -> Wallet:
        """Fetch the authenticated user's TON wallet balance and frozen funds."""
        return self._transport.request("GET", "/partners/users/wallets/", response_model=Wallet)

    def create_deposit(self) -> Deposit:
        """Generate a new deposit identifier."""
        return self._transport.request("POST", "/partners/deposits", response_model=Deposit)

    def withdraw(self, *, amount: Amount | str, external_address: str) -> TONWithdrawal:
        """Initiate a TON withdrawal to an external wallet address."""
        request = WithdrawTONRequest(amount=_amount(amount), external_address=external_address)
        return self._transport.request(
            "POST",
            "/partners/users/wallets/withdraw",
            json_data=request,
            response_model=TONWithdrawal,
        )

    def withdrawal_statuses(self, ids: Sequence[str]) -> TONWithdrawalStatuses:
        """Fetch the status of one or more TON withdrawals by ID."""
        if not ids:
            raise ValueError("ids must not be empty")
        return self._transport.request(
            "GET",
            "/partners/users/wallets/withdrawals/statuses",
            params={"ids": ids},
            response_model=TONWithdrawalStatuses,
        )


class AsyncWalletResource:
    """Asynchronous wallet resource (`/partners/users/wallets/*` and `/partners/deposits`)."""

    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport

    async def get(self) -> Wallet:
        """Fetch the authenticated user's TON wallet balance and frozen funds."""
        return await self._transport.request(
            "GET", "/partners/users/wallets/", response_model=Wallet
        )

    async def create_deposit(self) -> Deposit:
        """Generate a new deposit identifier."""
        return await self._transport.request("POST", "/partners/deposits", response_model=Deposit)

    async def withdraw(self, *, amount: Amount | str, external_address: str) -> TONWithdrawal:
        """Initiate a TON withdrawal to an external wallet address."""
        request = WithdrawTONRequest(amount=_amount(amount), external_address=external_address)
        return await self._transport.request(
            "POST",
            "/partners/users/wallets/withdraw",
            json_data=request,
            response_model=TONWithdrawal,
        )

    async def withdrawal_statuses(self, ids: Sequence[str]) -> TONWithdrawalStatuses:
        """Fetch the status of one or more TON withdrawals by ID."""
        if not ids:
            raise ValueError("ids must not be empty")
        return await self._transport.request(
            "GET",
            "/partners/users/wallets/withdrawals/statuses",
            params={"ids": ids},
            response_model=TONWithdrawalStatuses,
        )
