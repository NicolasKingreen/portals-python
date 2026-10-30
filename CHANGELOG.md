# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-10-31

API contract: 1.0.0

### Added

- Synchronous (`PortalsClient`) and asynchronous (`AsyncPortalsClient`) clients covering all 35
  operations in the Portals Partners API (`arena`, `offers`, `collections`, `market`, `nfts`,
  `users`, `wallet`).
- Generated Pydantic v2 models for every schema in the contract (`PortalsRequest` with
  `extra="forbid"`, `PortalsResponse` with `extra="allow"`, and `StrEnum` enums).
- Exact `Decimal` amount validation and string serialization (`Amount`), plus parsed RFC 3339
  `datetime` fields.
- Typed exception hierarchy (`AuthenticationError`, `AccessDeniedError`, `RateLimitError`,
  `MarketFeedUnavailableError`, `BetOutcomeUnknownError`, `TransportError`, `InvalidResponseError`,
  `ResponseValidationError`) and `RateLimit` header parsing.
- `portals.__api_version__` exposing the OpenAPI contract version used to generate the models.
- Vendored OpenAPI contract under `specs/partners.en.json` with `scripts/update_spec.py` and
  `scripts/generate_models.py`.

[Unreleased]: https://github.com/NicolasKingreen/portals-python/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/NicolasKingreen/portals-python/releases/tag/v0.1.0
