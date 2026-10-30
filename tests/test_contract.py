from __future__ import annotations

import json
from pathlib import Path

from scripts.generate_models import CLASS_NAMES, classify_schemas
from scripts.update_spec import summarize, validate


def test_vendored_spec_matches_metadata() -> None:
    root = Path(__file__).resolve().parent.parent
    raw = (root / "specs" / "partners.en.json").read_bytes()
    meta = json.loads((root / "specs" / "partners.meta.json").read_text(encoding="utf-8"))
    spec = validate(raw)
    computed = summarize(spec, raw, meta["source"])
    assert computed == meta


def test_all_contract_schemas_are_classified_and_disjoint() -> None:
    root = Path(__file__).resolve().parent.parent
    spec = json.loads((root / "specs" / "partners.en.json").read_text(encoding="utf-8"))
    schemas = spec["components"]["schemas"]
    assert set(schemas) == set(CLASS_NAMES)
    request_schemas, response_schemas = classify_schemas(spec)
    assert request_schemas.isdisjoint(response_schemas)
    assert request_schemas | response_schemas == set(schemas)
