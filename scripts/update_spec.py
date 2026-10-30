#!/usr/bin/env python3
"""Fetch and vendor the Portals Partners OpenAPI contract.

The contract is committed so builds, code generation, and CI are reproducible
and work offline. Run this script only when you intend to refresh it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = "https://docs.portals.tg/api/partners.en.json"
SPEC_PATH = ROOT / "specs" / "partners.en.json"
META_PATH = ROOT / "specs" / "partners.meta.json"
HTTP_METHODS = ("get", "post", "put", "patch", "delete")


class SpecError(RuntimeError):
    """The downloaded document is not a usable OpenAPI contract."""


def read_source(source: str) -> bytes:
    request = Request(
        source,
        headers={
            "Accept": "application/json",
            "Accept-Encoding": "identity",
            "User-Agent": "portals-api-spec-updater",
        },
    )
    with urlopen(request, timeout=30.0) as response:
        return response.read()


def normalize(raw: bytes) -> bytes:
    return raw.rstrip(b"\r\n") + b"\n"


def validate(raw: bytes) -> dict[str, Any]:
    try:
        spec = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SpecError(f"Source is not valid JSON: {exc}") from exc
    if not isinstance(spec, dict):
        raise SpecError("Source is not a JSON object")
    if not str(spec.get("openapi", "")).startswith("3."):
        raise SpecError("Missing or unsupported 'openapi' version")
    if not isinstance(spec.get("info"), dict):
        raise SpecError("Missing 'info' object")
    components = spec.get("components")
    if not isinstance(components, dict) or not isinstance(components.get("schemas"), dict):
        raise SpecError("Missing 'components.schemas' object")
    paths = spec.get("paths")
    if not isinstance(paths, dict) or not paths:
        raise SpecError("Missing or empty 'paths' object")
    return spec


def summarize(spec: dict[str, Any], raw: bytes, source: str) -> dict[str, Any]:
    paths = spec["paths"]
    operations = sum(
        1 for item in paths.values() for method in item if method.lower() in HTTP_METHODS
    )
    return {
        "source": source,
        "contract_version": spec["info"].get("version"),
        "openapi": spec.get("openapi"),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "schemas": len(spec["components"]["schemas"]),
        "paths": len(paths),
        "operations": operations,
    }


def write_meta(meta: dict[str, Any]) -> None:
    META_PATH.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")


def print_summary(meta: dict[str, Any]) -> None:
    print(f"Source:    {meta['source']}")
    print(f"Contract:  {meta['contract_version']} (OpenAPI {meta['openapi']})")
    print(
        f"Contents:  {meta['schemas']} schemas, {meta['paths']} paths, {meta['operations']} operations"
    )
    print(f"SHA-256:   {meta['sha256']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="compare the source with the vendored file instead of writing it",
    )
    parser.add_argument(
        "--source",
        default=DEFAULT_SOURCE,
        help=f"URL to fetch (default: {DEFAULT_SOURCE})",
    )
    parser.add_argument(
        "--from",
        dest="from_file",
        type=Path,
        help="read a local file instead of fetching --source",
    )
    args = parser.parse_args(argv)

    try:
        raw = (
            normalize(args.from_file.read_bytes())
            if args.from_file is not None
            else normalize(read_source(args.source))
        )
        spec = validate(raw)
    except (OSError, SpecError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    meta = summarize(spec, raw, args.source)

    current = normalize(SPEC_PATH.read_bytes()) if SPEC_PATH.exists() else b""

    if args.check:
        if raw == current:
            print(f"{SPEC_PATH.relative_to(ROOT)} is up to date.")
            print_summary(meta)
            return 0
        print(f"{SPEC_PATH.relative_to(ROOT)} differs from the source.", file=sys.stderr)
        print_summary(meta)
        if current and META_PATH.exists():
            old_meta = json.loads(META_PATH.read_text(encoding="utf-8"))
            print(
                f"Vendored contract: {old_meta.get('contract_version')} "
                f"({old_meta.get('schemas')} schemas, sha256 {old_meta.get('sha256')})"
            )
        return 1

    SPEC_PATH.parent.mkdir(parents=True, exist_ok=True)
    if raw == current:
        print(f"{SPEC_PATH.relative_to(ROOT)} is already up to date.")
    else:
        SPEC_PATH.write_bytes(raw)
        print(f"Wrote {SPEC_PATH.relative_to(ROOT)}.")
    write_meta(meta)
    print(f"Wrote {META_PATH.relative_to(ROOT)}.")
    print_summary(meta)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
