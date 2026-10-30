# Vendored OpenAPI contract

`partners.en.json` is a verbatim copy of the Portals Partners API contract:

<https://docs.portals.tg/api/partners.en.json>

It is committed to the repository so code generation, tests, and CI are reproducible and work
offline. Do not edit it by hand.

- Never fetch this file during `pip install`, `uv build`, or at runtime.
- `specs/partners.meta.json` records the source URL, contract version, SHA-256, and schema/path
  counts. It is maintained by `scripts/update_spec.py`.
- `src/portals/models.py` is generated from this file by `scripts/generate_models.py`.

## Refreshing

```bash
uv run python scripts/update_spec.py            # fetch and write
uv run python scripts/update_spec.py --check    # compare with upstream, exit 1 on drift
```

Then regenerate the models and review the diff:

```bash
uv run python scripts/generate_models.py
uv run ruff check --fix src/portals/models.py
uv run ruff format src/portals/models.py
```

`--from PATH` reads a locally saved contract instead of fetching, which is useful for offline
review. `--source URL` points at a mirror.

## Versioning

The contract version in `info.version` is independent of the `portals-api` package version.
The package follows [Semantic Versioning](https://semver.org/). Release notes record the
contract version each release was generated from.
