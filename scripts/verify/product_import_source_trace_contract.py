#!/usr/bin/env python3
"""Verify V1 import manifest preserves source trace semantics.

Run:
  python scripts/verify/product_import_source_trace_contract.py
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from _cli import parse_noop_args


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "audits" / "odoo-erpnext-migration-audit-2026-05-08" / "25-v1-odoo-erpnext-import-manifest.json"


def main() -> int:
    parse_noop_args(__doc__)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    failures = _source_trace_failures(manifest)
    if failures:
        print("[PRODUCT IMPORT SOURCE TRACE CONTRACT] FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("[PRODUCT IMPORT SOURCE TRACE CONTRACT] PASS")
    return 0


def _source_trace_failures(manifest: dict[str, Any]) -> list[str]:
    failures = []
    products = manifest.get("products")
    if not isinstance(products, list) or not products:
        return ["manifest products must be a non-empty list"]

    for row in products:
        slug = str(row.get("slug") or "(missing slug)")
        trace = row.get("source_trace") or {}
        if not trace.get("odoo_product_id"):
            failures.append(f"{slug} missing source_trace.odoo_product_id")
        if not trace.get("source_url"):
            failures.append(f"{slug} missing source_trace.source_url")
        if not trace.get("source_integrity"):
            failures.append(f"{slug} missing source_trace.source_integrity")
        if not trace.get("source_pattern_class"):
            failures.append(f"{slug} missing source_trace.source_pattern_class")

        axis_hashes = trace.get("source_axis_hashes")
        if axis_hashes is None:
            failures.append(f"{slug} missing source_trace.source_axis_hashes")
        elif not isinstance(axis_hashes, list):
            failures.append(f"{slug} source_axis_hashes must be a list")
        else:
            for axis in axis_hashes:
                if not axis.get("name") or not axis.get("source_value_hash"):
                    failures.append(f"{slug} has an axis trace without name/source_value_hash")

        expected_variant_rows = int((row.get("product_contract") or {}).get("source_variant_rows") or 0)
        variant_pointers = trace.get("source_variant_pointers")
        if not isinstance(variant_pointers, dict):
            failures.append(f"{slug} source_variant_pointers must be a dict")
        elif int(variant_pointers.get("source_variant_count") or 0) != expected_variant_rows:
            failures.append(
                f"{slug} source_variant_pointers count mismatch: expected {expected_variant_rows}, got {variant_pointers.get('source_variant_count')}"
            )
        elif expected_variant_rows and not variant_pointers.get("source_variant_pointer_hash"):
            failures.append(f"{slug} source_variant_pointers missing source_variant_pointer_hash")
        elif expected_variant_rows:
            samples = variant_pointers.get("source_variant_pointer_samples") or []
            first = samples[0] if samples else {}
            if first.get("source_index") != 0 or "combo" not in first or "ptav_ids" not in first:
                failures.append(f"{slug} source_variant_pointers do not preserve source index, combo, and ptav_ids")

    validation_checks = set((manifest.get("validation") or {}).get("checks") or [])
    if "source_ids_axis_hashes_variant_pointers_and_pattern_class_preserved" not in validation_checks:
        failures.append("manifest validation is missing the source trace preservation check")
    return failures


if __name__ == "__main__":
    raise SystemExit(main())
