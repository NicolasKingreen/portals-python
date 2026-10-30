# Contributing

Thank you for contributing to `portals-api`!

## Development setup

Install [uv](https://docs.astral.sh/uv/) and sync the project environment:

```bash
uv sync
```

## Running checks

Run the full check suite locally before opening a pull request:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest --cov=portals
uv build
```

## Updating the OpenAPI contract and generated models

The Portals Partners OpenAPI contract is vendored at `specs/partners.en.json` so builds and CI are
reproducible offline. Never edit `specs/partners.en.json`, `specs/partners.meta.json`,
`src/portals/models.py`, or `src/portals/_contract.py` by hand.

To check for upstream contract changes or refresh the vendored contract:

```bash
uv run python scripts/update_spec.py --check   # compare with upstream (exits 1 on drift)
uv run python scripts/update_spec.py           # fetch and update specs/partners.en.json
uv run python scripts/generate_models.py       # regenerate models.py and _contract.py
uv run ruff check --fix src/portals/models.py src/portals/_contract.py
uv run ruff format src/portals/models.py src/portals/_contract.py
```

If upstream adds a new schema in `components.schemas`, add its Python class name mapping to
`CLASS_NAMES` in `scripts/generate_models.py`.

## Releasing

1. Ensure `specs/partners.en.json` and generated models are up to date.
2. Bump the version in `pyproject.toml` and `uv.lock`:
   ```bash
   uv version --bump patch   # or minor / major / rc
   uv sync
   ```
3. Update `CHANGELOG.md` with the new version, release date, and `API contract: X.Y.Z`.
4. Run all local checks (`ruff`, `mypy`, `pytest`, `uv build`).
5. Commit the release preparation, create an annotated tag `vX.Y.Z`, and push the commit and tag.
   `.github/workflows/release.yml` verifies the tag matches the package version, publishes to
   TestPyPI, smoke-installs from TestPyPI, and publishes to PyPI via Trusted Publishing.
