#!/usr/bin/env python3
"""Build the LT product source-repair map from checked-in source artifacts.

Run:
  python scripts/verify/product_source_repair_map.py
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
APP_PATH = ROOT / "apps" / "locally_twisted"
if str(APP_PATH) not in sys.path:
    sys.path.insert(0, str(APP_PATH))

from locally_twisted.catalog_contract.product_source_repair_map import (  # noqa: E402
    build_product_source_repair_map,
)


SOURCE_CATALOG = ROOT / "_resources" / "odoo-live" / "catalog.json"
PRICE_ENRICHMENT = ROOT / "audits" / "odoo-erpnext-migration-audit-2026-05-08" / "21-product-page-price-enrichment-candidates.json"
SCAFFOLD = ROOT / "output" / "complex-checkout-scaffold.json"
DEFAULT_JSON = ROOT / "workstreams" / "ecommerce-audit" / "product-source-repair-map-2026-05-17.json"
DEFAULT_MARKDOWN = ROOT / "workstreams" / "ecommerce-audit" / "product-source-repair-map-2026-05-17.md"


class RepairMapFail(Exception):
    pass


def main() -> int:
    args = _parse_args()
    output_path = _rooted(args.output)
    markdown_path = _rooted(args.markdown)
    try:
        if not args.skip_refresh:
            _refresh_scaffold()
        source_products = _source_products(_load_json(_rooted(args.source_catalog)))
        price_artifact = _load_json(_rooted(args.price_enrichment))
        scaffold_artifact = _load_json(_rooted(args.scaffold))
        report = build_product_source_repair_map(
            source_products=source_products,
            price_enrichment_artifact=price_artifact,
            scaffold_artifact=scaffold_artifact,
            metadata={
                "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                "source_catalog": _display_path(_rooted(args.source_catalog)),
                "price_enrichment": _display_path(_rooted(args.price_enrichment)),
                "scaffold": _display_path(_rooted(args.scaffold)),
                "business_rule": "Products target purchasable checkout; legacy quote_first values are internal holds.",
            },
        )
    except RepairMapFail as exc:
        print(f"[PRODUCT SOURCE REPAIR MAP] FAIL\n  - {exc}")
        return 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report.to_artifact(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(report.to_markdown(), encoding="utf-8")

    summary = report.summary()
    print("[PRODUCT SOURCE REPAIR MAP] " + ("PASS" if summary.get("ok") else "FAIL"))
    print(f"  - report: {_display_path(output_path)}")
    print(f"  - markdown: {_display_path(markdown_path)}")
    print(f"  - products: {summary.get('products')}")
    print(f"  - source export found: {summary.get('source_export_found')}")
    print(f"  - certified checkout: {summary.get('certified_checkout_products')}")
    print(f"  - blocked until certified: {summary.get('blocked_until_certified_products')}")
    for failure in report.contract_failures:
        print(f"  - {failure}")
    return 0 if summary.get("ok") else 2


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-catalog", default=str(SOURCE_CATALOG), help="Odoo source catalog JSON")
    parser.add_argument("--price-enrichment", default=str(PRICE_ENRICHMENT), help="Price enrichment JSON")
    parser.add_argument("--scaffold", default=str(SCAFFOLD), help="Complex checkout scaffold JSON")
    parser.add_argument("--output", default=str(DEFAULT_JSON), help="Output JSON artifact")
    parser.add_argument("--markdown", default=str(DEFAULT_MARKDOWN), help="Output Markdown report")
    parser.add_argument("--skip-refresh", action="store_true", help="Do not refresh complex checkout scaffold first")
    return parser.parse_args()


def _refresh_scaffold() -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "verify" / "complex_checkout_scaffold.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=300,
    )
    if proc.returncode != 0:
        raise RepairMapFail(
            "complex checkout scaffold refresh failed\n"
            f"STDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RepairMapFail(f"missing JSON input: {_display_path(path)}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise RepairMapFail(f"JSON input must be an object: {_display_path(path)}")
    return data


def _source_products(catalog: dict[str, Any]) -> list[dict[str, Any]]:
    products = catalog.get("products") if isinstance(catalog, dict) else None
    if not isinstance(products, list):
        raise RepairMapFail("Odoo source catalog missing products array")
    return [row for row in products if isinstance(row, dict)]


def _rooted(path: str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return candidate.resolve()


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
