#!/usr/bin/env python3
"""Build the reusable Odoo option-pattern contract artifact.

The mapper is non-mutating. It reads `_resources/odoo-live/catalog.json`,
classifies source option patterns into reusable ERPNext import requirements,
and writes a machine-readable ProductPatternContract artifact plus a short
Markdown verifier summary.

Run:
  python scripts/verify/odoo_option_pattern_mapper.py
  python scripts/verify/odoo_option_pattern_mapper.py --json
  python scripts/verify/odoo_option_pattern_mapper.py --report output/odoo-option-pattern-contract.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
APP_PATH = ROOT / "apps" / "locally_twisted"
if str(APP_PATH) not in sys.path:
    sys.path.insert(0, str(APP_PATH))

from locally_twisted.catalog_contract.pattern_mapper import build_product_pattern_report


SOURCE_CATALOG = ROOT / "_resources" / "odoo-live" / "catalog.json"
DEFAULT_REPORT = ROOT / "output" / "odoo-option-pattern-contract.json"
DEFAULT_MARKDOWN = ROOT / "output" / "odoo-option-pattern-contract.md"

REQUIRED_PRODUCT_KEYS = ("slug", "name")
REQUIRED_ARTIFACT_SUMMARY_KEYS = (
    "source_products",
    "pattern_counts",
    "axis_pattern_counts",
    "media_requirement_counts",
    "source_variant_rows",
    "source_extra_images",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true", help="Print full ProductPatternContract JSON")
    parser.add_argument("--report", help="Write ProductPatternContract JSON to this path")
    parser.add_argument("--markdown", help="Write Markdown verifier summary to this path")
    args = parser.parse_args()

    source = _read_source_catalog()
    products = _products(source)
    report = build_product_pattern_report(
        products,
        metadata={
            "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "source_catalog": str(SOURCE_CATALOG.relative_to(ROOT)),
            "source_scraped_at": source.get("scraped_at") if isinstance(source, dict) else "",
            "logic_note": "Product names are report examples only; classification uses source axes, prices, descriptions, and media shape.",
        },
    )
    artifact = report.to_artifact()
    failures = _contract_failures(artifact, products)

    report_path = _rooted(args.report) if args.report else DEFAULT_REPORT
    markdown_path = _rooted(args.markdown) if args.markdown else DEFAULT_MARKDOWN
    report_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(report.to_markdown(), encoding="utf-8")

    print(f"[ODOO OPTION PATTERN MAPPER] wrote {report_path.relative_to(ROOT)}")
    print(f"[ODOO OPTION PATTERN MAPPER] wrote {markdown_path.relative_to(ROOT)}")
    if args.json:
        print(json.dumps(artifact, indent=2, sort_keys=True))
    else:
        _print_summary(artifact, failures)

    return 0 if not failures else 1


def _read_source_catalog() -> Any:
    if not SOURCE_CATALOG.exists():
        raise SystemExit(f"FATAL: missing source catalog: {SOURCE_CATALOG.relative_to(ROOT)}")
    return json.loads(SOURCE_CATALOG.read_text(encoding="utf-8"))


def _products(source: Any) -> list[dict[str, Any]]:
    if isinstance(source, dict):
        rows = source.get("products") or []
    else:
        rows = source or []
    if not isinstance(rows, list):
        raise SystemExit("FATAL: source catalog products must be a list")
    return [row for row in rows if isinstance(row, dict)]


def _contract_failures(artifact: dict[str, Any], source_products: list[dict[str, Any]]) -> list[str]:
    failures: list[str] = []
    if artifact.get("schema_version") != "lt-odoo-option-pattern-contract-v1":
        failures.append("unexpected schema_version")
    if artifact.get("read_only") is not True:
        failures.append("artifact must be read_only")
    if artifact.get("destructive_allowed") is not False:
        failures.append("artifact must not allow destructive action")

    summary = artifact.get("summary") or {}
    for key in REQUIRED_ARTIFACT_SUMMARY_KEYS:
        if key not in summary:
            failures.append(f"summary missing {key}")
    _append_source_count_failures(failures, summary, source_products)
    products = artifact.get("products")
    if not isinstance(products, list):
        return failures + ["products must be a list"]
    if len(products) != len(source_products):
        failures.append(f"product count mismatch: artifact={len(products)} source={len(source_products)}")

    for index, (source, row) in enumerate(zip(source_products, products, strict=False)):
        for key in REQUIRED_PRODUCT_KEYS:
            if not source.get(key):
                failures.append(f"source product {index} missing {key}")
        if not row.get("slug"):
            failures.append(f"artifact product {index} missing slug")
        if not row.get("patterns"):
            failures.append(f"{row.get('slug') or index} missing patterns")
        if not isinstance(row.get("axis_contracts"), list):
            failures.append(f"{row.get('slug') or index} axis_contracts must be a list")
        if not isinstance(row.get("media_roles"), dict):
            failures.append(f"{row.get('slug') or index} media_roles must be an object")
        if not row.get("erpnext_contract_requirements"):
            failures.append(f"{row.get('slug') or index} missing erpnext_contract_requirements")
        if not row.get("import_implications"):
            failures.append(f"{row.get('slug') or index} missing import_implications")
        _append_product_semantic_failures(failures, source, row, index)

    return failures


def _append_source_count_failures(
    failures: list[str],
    summary: dict[str, Any],
    source_products: list[dict[str, Any]],
) -> None:
    expected_variant_rows = sum(len(row.get("valid_variants") or []) for row in source_products)
    expected_extra_images = sum(len(row.get("additional_image_urls") or []) for row in source_products)
    if summary.get("source_variant_rows") != expected_variant_rows:
        failures.append(
            "summary source_variant_rows mismatch: "
            f"artifact={summary.get('source_variant_rows')} source={expected_variant_rows}"
        )
    if summary.get("source_extra_images") != expected_extra_images:
        failures.append(
            "summary source_extra_images mismatch: "
            f"artifact={summary.get('source_extra_images')} source={expected_extra_images}"
        )


def _append_product_semantic_failures(
    failures: list[str],
    source: dict[str, Any],
    row: dict[str, Any],
    index: int,
) -> None:
    slug = row.get("slug") or source.get("slug") or str(index)
    if row.get("odoo_product_id") != _clean(source.get("odoo_id")):
        failures.append(f"{slug} odoo_product_id mismatch")
    if row.get("currency") != _clean(source.get("currency")):
        failures.append(f"{slug} currency mismatch")
    if row.get("source_variant_rows") != len(source.get("valid_variants") or []):
        failures.append(f"{slug} source_variant_rows mismatch")
    if row.get("source_declared_variant_count") != _int_or_none(source.get("variant_count")):
        failures.append(f"{slug} source_declared_variant_count mismatch")

    integrity = row.get("source_integrity")
    if not isinstance(integrity, dict):
        failures.append(f"{slug} missing source_integrity")
    else:
        for key in (
            "odoo_product_id",
            "currency",
            "source_declared_variant_count",
            "source_valid_variant_count",
            "axis_value_counts",
            "axis_value_hashes",
            "valid_variant_hash",
            "valid_variant_pointer",
        ):
            if key not in integrity:
                failures.append(f"{slug} source_integrity missing {key}")
        if integrity.get("source_valid_variant_count") != len(source.get("valid_variants") or []):
            failures.append(f"{slug} source_integrity source_valid_variant_count mismatch")

    priced = _source_is_priced(source)
    sale_unit = row.get("sale_unit_contract")
    if priced and not isinstance(sale_unit, dict):
        failures.append(f"{slug} priced product missing sale_unit_contract")
    elif priced and not sale_unit.get("path"):
        failures.append(f"{slug} priced product missing sale_unit_contract.path")
    elif priced and sale_unit.get("path") == "not_priced":
        failures.append(f"{slug} priced product incorrectly marked not_priced")

    axis_contracts = row.get("axis_contracts") if isinstance(row.get("axis_contracts"), list) else []
    for axis in axis_contracts:
        axis_name = axis.get("name") or "<unnamed axis>"
        patterns = set(axis.get("patterns") or [])
        for key in (
            "source_values",
            "source_value_hash",
            "primitive_key",
            "erpnext_primitive",
            "selector_key",
            "selector_requirement",
            "pricing_strategy",
            "import_implication",
        ):
            if axis.get(key) in (None, "", []):
                failures.append(f"{slug} axis {axis_name} missing {key}")
        if axis.get("source_value_count") != len(axis.get("source_values") or []):
            failures.append(f"{slug} axis {axis_name} source_value_count mismatch")
        if "review_only_axis" in patterns and not axis.get("review_reason"):
            failures.append(f"{slug} axis {axis_name} review_only_axis missing review_reason")
        if "freeform_customer_text_candidate" in patterns and not _axis_itself_has_freeform_signal(axis):
            failures.append(
                f"{slug} axis {axis_name} has freeform pattern without axis-name or axis-value signal"
            )


def _source_is_priced(source: dict[str, Any]) -> bool:
    if source.get("base_price") is not None:
        return True
    return any((row or {}).get("erpnext_variant_price", (row or {}).get("price")) is not None for row in source.get("valid_variants") or [])


def _axis_itself_has_freeform_signal(axis: dict[str, Any]) -> bool:
    tokens = ("custom", "logo", "message", "name", "school", "team", "theme", "text", "word", "upload")
    text = _clean(" ".join([str(axis.get("name") or ""), *[str(value) for value in axis.get("source_values") or []]])).lower()
    text = text.replace("-", " ").replace("_", " ")
    return any(token in text for token in tokens)


def _clean(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def _int_or_none(value: Any) -> int | None:
    try:
        if value in (None, ""):
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _print_summary(artifact: dict[str, Any], failures: list[str]) -> None:
    summary = artifact.get("summary") or {}
    print("[ODOO OPTION PATTERN MAPPER] " + ("PASS" if not failures else "FAIL"))
    print(f"  source_products: {summary.get('source_products')}")
    print(f"  source_variant_rows: {summary.get('source_variant_rows')}")
    print(f"  source_extra_images: {summary.get('source_extra_images')}")
    print(f"  product_patterns: {_format_counts(summary.get('pattern_counts') or {})}")
    print(f"  axis_patterns: {_format_counts(summary.get('axis_pattern_counts') or {})}")
    print(f"  media_requirements: {_format_counts(summary.get('media_requirement_counts') or {})}")
    if failures:
        print("  failures:")
        for failure in failures:
            print(f"    - {failure}")


def _format_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))


def _rooted(path: str) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = ROOT / candidate
    return candidate.resolve()


if __name__ == "__main__":
    sys.exit(main())
