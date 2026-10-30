# Portals API Python client

A typed synchronous and asynchronous Python client for the [Portals Partners API](https://docs.portals.tg/developers/api/), the partner-facing programmatic API of the Portals marketplace.

## Features

- All 35 operations from the Portals Partners OpenAPI contract
- Matching `PortalsClient` and `AsyncPortalsClient` APIs
- Typed Pydantic v2 models for every schema in the contract (strict requests, forward-compatible responses)
- httpx2 connection pooling and injectable HTTP clients
- Exact `Decimal` amounts and parsed `datetime` timestamps
- Typed API errors and rate-limit metadata
- Python 3.11+ and a `py.typed` marker

## Installation

```bash
pip install portals-api
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add portals-api
```

From a local checkout:

```bash
pip install .
```

The distribution is named `portals-api`; the import package is `portals`.

## Quickstart

### Synchronous

```python
from portals import PortalsClient

with PortalsClient("your-api-key") as client:
    config = client.market.config()
    wallet = client.wallet.get()
    results = client.nfts.search(max_price="20", limit=20)

    print(config.deposit_wallet)
    print(wallet.balance)
    print(results.total_count)
```

### Asynchronous

```python
import asyncio

from portals import AsyncPortalsClient


async def main() -> None:
    async with AsyncPortalsClient("your-api-key") as client:
        wallet = await client.wallet.get()
        state = await client.arena.state()

        print(wallet.balance)
        print(state.server_time)


asyncio.run(main())
```

Get an API key from the Portals mini app under **Profile → Partner API**. Keep the key on your server and never commit it to source control.

## Resources

| Resource | Operations |
| --- | --- |
| `client.arena` | Arena state, inventory, and bets |
| `client.offers` | Create, update, cancel, inspect, and accept collection offers |
| `client.collections` | Collection previews, metrics, and attribute floor prices |
| `client.market` | Market configuration and activity |
| `client.nfts` | Search, owned NFTs, purchases, listings, transfers, and withdrawals |
| `client.users` | User existence and authenticated user activity |
| `client.wallet` | Balance, deposits, TON withdrawals, and withdrawal statuses |

Methods return typed models. For example:

```python
from decimal import Decimal

from portals import BuyDetail, PortalsClient

with PortalsClient("your-api-key") as client:
    purchase = client.nfts.buy(
        [
            BuyDetail(id="nft-id", price=Decimal("12.50")),
        ]
    )

    print(purchase.total_purchased)
    print(purchase.total_failed)
    print(purchase.total_spent)
```

Purchases may partially succeed. Inspect each item in `purchase.purchase_results` rather than assuming the whole request succeeded or failed.

## Amounts and timestamps

Pass amounts as decimal strings or `Decimal` instances. Floats are rejected to avoid binary floating-point errors. Amounts are serialized as strings on the wire and exposed as `Decimal` values by response models.

RFC 3339 timestamps are exposed as `datetime` instances. Arena timestamps remain integers because the API returns Unix milliseconds.

## Errors

```python
from portals import APIError, PortalsClient, RateLimitError

with PortalsClient("your-api-key") as client:
    try:
        client.market.actions()
    except RateLimitError as exc:
        if exc.rate_limit is not None:
            print(exc.rate_limit.reset_seconds)
    except APIError as exc:
        print(exc.status_code, exc.code, exc.message)
```

Specific exceptions cover authentication, access denial, rate limits, an unavailable market feed, and unknown Arena bet outcomes. Transport failures, invalid JSON, and response-validation failures have separate exception types.

Write operations are not automatically retried. In particular, an Arena bet that returns `504 BET_OUTCOME_UNKNOWN` or fails during network transmission may already have been placed; check `client.arena.state()` before trying again.

## Custom HTTP clients

Pass an `httpx2.Client` or `httpx2.AsyncClient` to customize transports, proxies, or test behavior. The library closes only clients it creates itself.

```python
import httpx2

from portals import PortalsClient

http_client = httpx2.Client(timeout=10)
client = PortalsClient("your-api-key", client=http_client)

client.close()
http_client.close()
```

## Low-level requests

Use `request()` for new endpoints that do not yet have a typed method:

```python
payload = client.request("GET", "/partners/example", params={"limit": 10})
```

Pass `response_model=YourModel` to validate the response with Pydantic.

## Development

Install the project and development tools with [uv](https://docs.astral.sh/uv/):

```bash
uv sync
```

Run the checks used by CI:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
uv build
```

The OpenAPI contract is vendored at `specs/partners.en.json`. Refresh it and regenerate the
models, then review the resulting changes:

```bash
uv run python scripts/update_spec.py
uv run python scripts/generate_models.py
uv run ruff check --fix src/portals/models.py
uv run ruff format src/portals/models.py
```

## License

MIT
