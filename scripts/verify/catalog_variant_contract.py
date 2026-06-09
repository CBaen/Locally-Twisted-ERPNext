#!/usr/bin/env python3
"""Compare captured legacy_source product variants to live ERPNext variants.

This is the per-product variant correctness diff called out in
MIRROR-REBUILD-PLAN.md. It verifies that the ERPNext catalog still matches the
normalized legacy_source scrape that seeded the shop.

Run:
  python scripts/verify/catalog_variant_contract.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from _cli import parse_noop_args


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "apps" / "locally_twisted"))

from locally_twisted.catalog_variant_rules import dedupe_required_variant_rows
from locally_twisted.color_preset_rules import COLLEGE_COLOR_PRESET_ATTRIBUTE, COLLEGE_PRESET_LABELS

CATALOG_PATH = ROOT / "_resources" / "catalog-source" / "catalog.json"
NORMALIZE_PATH = ROOT / "_resources" / "catalog-source" / "value_normalize_map.json"
CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
GRADUATION_GRAB_TEMPLATE = "graduation-grab-n-go"
GRADUATION_STANDS_TEMPLATE = "6-graduation-stands"
GRADUATION_STANDS_ATTRIBUTE = "Graduation stands"


class CatalogVariantFail(Exception):
    pass


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CatalogVariantFail(f"Missing required file: {path}") from exc


def normalize_value(attr_name: str, raw_value: str, normalize_map: dict[str, dict[str, str]]) -> str:
    key = " ".join(str(raw_value or "").split()).lower()
    return normalize_map.get(attr_name, {}).get(key, raw_value)


def combo_key(combo: dict[str, str], normalize_map: dict[str, dict[str, str]] | None = None) -> tuple[tuple[str, str], ...]:
    rows = []
    for attr_name, value in combo.items():
        clean_value = normalize_value(attr_name, value, normalize_map or {}) if normalize_map else value
        rows.append((attr_name, clean_value))
    return tuple(sorted(rows))


def expected_variants(catalog: dict[str, Any], normalize_map: dict[str, dict[str, str]]) -> dict[str, set[tuple[tuple[str, str], ...]]]:
    expected: dict[str, set[tuple[tuple[str, str], ...]]] = {}
    for prod in catalog.get("products") or []:
        slug = prod.get("slug")
        if not slug:
            continue
        projected = school_color_preset_expected_rows(prod)
        if projected is not None:
            expected[slug] = {combo_key(row, normalize_map) for row in projected}
            continue
        valid = dedupe_required_variant_rows(prod.get("valid_variants") or [])
        expected[slug] = {combo_key(row.get("combo") or {}, normalize_map) for row in valid}
    return expected


def school_color_preset_expected_rows(prod: dict[str, Any]) -> list[dict[str, str]] | None:
    """Project approved graduation products from raw colors to college presets."""
    slug = prod.get("slug")
    if slug == GRADUATION_GRAB_TEMPLATE:
        return [
            {COLLEGE_COLOR_PRESET_ATTRIBUTE: label}
            for label in COLLEGE_PRESET_LABELS
        ]
    if slug == GRADUATION_STANDS_TEMPLATE:
        design_values = source_axis_values(prod, GRADUATION_STANDS_ATTRIBUTE)
        return [
            {
                GRADUATION_STANDS_ATTRIBUTE: design,
                COLLEGE_COLOR_PRESET_ATTRIBUTE: label,
            }
            for design in design_values
            for label in COLLEGE_PRESET_LABELS
        ]
    return None


def source_axis_values(prod: dict[str, Any], axis_name: str) -> tuple[str, ...]:
    axis = (prod.get("attributes") or {}).get(axis_name) or {}
    values = axis.get("values") or []
    return tuple(
        str(value.get("name") or "").strip()
        for value in values
        if isinstance(value, dict) and value.get("name")
    )


def run_mariadb(query: str) -> str:
    query = "set SQL_SELECT_LIMIT=DEFAULT;\n" + query
    cmd = [
        "docker",
        "exec",
        CONTAINER,
        "bench",
        "--site",
        SITE,
        "mariadb",
        "--batch",
        "--raw",
        "--skip-column-names",
        "--execute",
        query,
    ]
    proc = subprocess.run(cmd, text=True, encoding="utf-8", capture_output=True, timeout=120)
    if proc.returncode != 0:
        raise CatalogVariantFail(
            "mariadb query failed\n"
            f"QUERY:\n{query}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    return proc.stdout


def live_variants() -> dict[str, dict[str, dict[str, str]]]:
    query = """
select
    i.variant_of,
    i.name,
    iva.attribute,
    iva.attribute_value
from tabItem i
left join `tabItem Variant Attribute` iva on iva.parent = i.name
where i.variant_of is not null
  and i.variant_of != ''
  and i.disabled = 0
order by i.variant_of, i.name, iva.idx;
""".strip()
    rows = run_mariadb(query)
    by_template: dict[str, dict[str, dict[str, str]]] = defaultdict(lambda: defaultdict(dict))
    for line in rows.splitlines():
        parts = line.split("\t")
        if len(parts) != 4:
            raise CatalogVariantFail(f"Unexpected mariadb row shape: {line!r}")
        template, item_code, attr_name, attr_value = parts
        if attr_name and attr_value:
            by_template[template][item_code][attr_name] = attr_value
        else:
            by_template[template].setdefault(item_code, {})
    return {template: dict(variants) for template, variants in by_template.items()}


def live_templates() -> set[str]:
    rows = run_mariadb("select name from tabItem where has_variants = 1 and disabled = 0 order by name;")
    return {line.strip() for line in rows.splitlines() if line.strip()}


def summarize_key(key: tuple[tuple[str, str], ...]) -> str:
    return ", ".join(f"{attr}={value}" for attr, value in key)


def compare() -> tuple[list[dict[str, Any]], dict[str, int]]:
    catalog = load_json(CATALOG_PATH)
    normalize_map = load_json(NORMALIZE_PATH)
    expected = expected_variants(catalog, normalize_map)
    actual_by_template = live_variants()
    actual_templates = live_templates()

    failures = []
    totals = {
        "products_checked": 0,
        "expected_variants": 0,
        "actual_variants": 0,
        "single_sku_products": 0,
    }

    for prod in catalog.get("products") or []:
        slug = prod["slug"]
        expected_set = expected.get(slug, set())
        actual_items = actual_by_template.get(slug, {})
        actual_set = {combo_key(attrs) for attrs in actual_items.values()}

        totals["products_checked"] += 1
        totals["expected_variants"] += len(expected_set)
        totals["actual_variants"] += len(actual_set)
        if not expected_set:
            totals["single_sku_products"] += 1

        if not expected_set:
            if slug in actual_templates or actual_set:
                failures.append(
                    {
                        "slug": slug,
                        "problem": "single_sku_has_variants",
                        "actual_count": len(actual_set),
                    }
                )
            continue

        missing = expected_set - actual_set
        extra = actual_set - expected_set
        duplicate_count = len(actual_items) - len(actual_set)
        if missing or extra or duplicate_count:
            failures.append(
                {
                    "slug": slug,
                    "expected_count": len(expected_set),
                    "actual_count": len(actual_set),
                    "duplicate_count": duplicate_count,
                    "missing_count": len(missing),
                    "extra_count": len(extra),
                    "missing_examples": [summarize_key(row) for row in sorted(missing)[:5]],
                    "extra_examples": [summarize_key(row) for row in sorted(extra)[:5]],
                }
            )

    extra_templates = set(actual_by_template) - set(expected)
    for slug in sorted(extra_templates):
        failures.append(
            {
                "slug": slug,
                "problem": "template_not_in_legacy_source_catalog",
                "actual_count": len(actual_by_template.get(slug, {})),
            }
        )

    return failures, totals


def main() -> int:
    parse_noop_args(__doc__)
    try:
        failures, totals = compare()
    except CatalogVariantFail as exc:
        print(f"[CATALOG VARIANT CONTRACT] ERROR: {exc}")
        return 2

    print(
        "[CATALOG VARIANT CONTRACT] checked "
        f"{totals['products_checked']} products, "
        f"{totals['expected_variants']} expected variants, "
        f"{totals['actual_variants']} live variants"
    )
    print(f"[CATALOG VARIANT CONTRACT] single-SKU products: {totals['single_sku_products']}")

    if failures:
        print(f"\n[CATALOG VARIANT CONTRACT] FAIL: {len(failures)} product mismatch(es)")
        for failure in failures:
            print(json.dumps(failure, ensure_ascii=False, indent=2))
        return 1

    print("\n[CATALOG VARIANT CONTRACT] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
