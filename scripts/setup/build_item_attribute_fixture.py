"""
build_item_attribute_fixture.py — Generate Item Attribute fixture from live catalog.

Reads _resources/odoo-live/catalog.json, deduplicates attribute values across
all products, generates collision-free abbr codes (per frappe-migration-guard
Agent 2: duplicate abbr → make_variant_item_code naming collision → variant
insert raises duplicate-key DB error), and writes:
  apps/locally_twisted/locally_twisted/fixtures/item_attribute.json

Re-run whenever catalog.json refreshes. Idempotent — overwrites the fixture file.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = PROJECT_ROOT / "_resources" / "odoo-live" / "catalog.json"
FIXTURE_PATH = PROJECT_ROOT / "apps" / "locally_twisted" / "locally_twisted" / "fixtures" / "item_attribute.json"
MODIFIED = "2026-04-30 12:00:00.000000"


def make_abbr(value_name: str, used: set[str]) -> str:
    """Generate a collision-free 3-6 char abbreviation.

    Per Agent 2 finding: Item Variant naming uses Item Attribute Value.abbr;
    duplicate abbrs across values within the same attribute cause make_variant_item_code
    to produce duplicate item_codes, which raise duplicate-key DB errors on insert.
    """
    # Strip non-alphanumeric, uppercase, take meaningful prefix
    cleaned = re.sub(r'[^A-Za-z0-9]+', '', value_name).upper()
    if not cleaned:
        cleaned = "X"

    # Try 3-char prefix first, then 4, 5, 6...
    for length in (3, 4, 5, 6):
        if length > len(cleaned):
            break
        candidate = cleaned[:length]
        if candidate not in used:
            return candidate

    # Fall back: prefix + counter
    base = cleaned[:3] if len(cleaned) >= 3 else cleaned
    n = 2
    while True:
        candidate = f"{base}{n}"
        if candidate not in used:
            return candidate
        n += 1


def collect_attributes_from_catalog(catalog: dict) -> tuple[dict[str, list[str]], dict[str, dict[str, str]]]:
    """For each attribute name, collect unique value names across all products.
    Preserves first-seen order (so balloon colors stay in Odoo's source order).

    Dedup is CASE-INSENSITIVE + whitespace-normalized: ERPNext's Item Attribute
    validate() rejects values that differ only in casing/whitespace. Odoo has e.g.
    'Blue Slate' (id 1357) and 'Blue slate' (id 1399) — same color, two ptav rows
    in Odoo. We keep first-seen casing as canonical and remap downstream variants.

    Returns:
      (attrs, normalize_map) where:
        attrs[attr_name] = [canonical_value_name, ...]
        normalize_map[attr_name][lowercased_value] = canonical_value_name
    """
    attrs: dict[str, list[str]] = {}
    canon_seen: dict[str, dict[str, str]] = {}  # attr_name -> {key -> canonical}
    for prod in catalog.get("products", []):
        for attr_name, attr_data in (prod.get("attributes") or {}).items():
            if attr_name not in attrs:
                attrs[attr_name] = []
                canon_seen[attr_name] = {}
            for val in attr_data.get("values", []):
                vname = val.get("name", "").strip()
                if not vname:
                    continue
                key = re.sub(r'\s+', ' ', vname).lower()
                if key not in canon_seen[attr_name]:
                    canon_seen[attr_name][key] = vname
                    attrs[attr_name].append(vname)
    return attrs, canon_seen


def build_fixture(attrs: dict[str, list[str]]) -> list[dict]:
    """Build the Item Attribute fixture records."""
    records = []
    for attr_name in sorted(attrs.keys()):
        values = attrs[attr_name]
        used_abbrs: set[str] = set()
        value_rows = []
        for vname in values:
            abbr = make_abbr(vname, used_abbrs)
            used_abbrs.add(abbr)
            value_rows.append({
                "attribute_value": vname,
                "abbr": abbr,
            })
        records.append({
            "doctype": "Item Attribute",
            "name": attr_name,
            "attribute_name": attr_name,
            "numeric_values": 0,
            "item_attribute_values": value_rows,
            "modified": MODIFIED,
        })
    return records


def main() -> int:
    if not CATALOG_PATH.exists():
        print(f"FATAL: catalog not found at {CATALOG_PATH}")
        return 1

    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    attrs = collect_attributes_from_catalog(catalog)

    print(f"=== Found {len(attrs)} unique attribute names ===")
    for name in sorted(attrs.keys()):
        print(f"  {name:<25} {len(attrs[name])} values")

    records = build_fixture(attrs)

    # Verification: every abbr unique within its attribute
    for rec in records:
        abbrs = [r["abbr"] for r in rec["item_attribute_values"]]
        if len(abbrs) != len(set(abbrs)):
            dups = [a for a in abbrs if abbrs.count(a) > 1]
            print(f"FATAL: duplicate abbrs in {rec['name']!r}: {dups}")
            return 1

    FIXTURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE_PATH.write_text(json.dumps(records, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    total_values = sum(len(r["item_attribute_values"]) for r in records)
    print(f"\nWrote {FIXTURE_PATH.relative_to(PROJECT_ROOT)} ({len(records)} attributes, {total_values} total values)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
