"""Verify the saved ERPNext catalog state snapshot before purge/rebuild work.

This is a read-only artifact verifier. It proves the current transition state was
saved as evidence before treating product rows as rebuildable pipeline output.
"""

from __future__ import annotations

import json
from pathlib import Path

from _cli import parse_noop_args

AUDIT_ROOT = Path("audits/catalog-import-audit-2026-05-08")

REQUIRED_JSON_FILES = {
    "summary.json",
    "item_groups.json",
    "website_items.json",
    "items.json",
    "item_prices.json",
    "item_variant_attributes.json",
    "item_attributes.json",
    "item_attribute_values.json",
    "files_product_related.json",
    "website_slideshows.json",
    "website_slideshow_items.json",
    "website_item_groups_child_rows.json",
    "source_catalog_data.json",
    "source_slug_to_group.json",
}

REQUIRED_TEXT_FILES = {
    "README.md",
    "route_category_map.md",
}

EXPECTED_COUNTS = {
    "website_items": 53,
    "item_groups": 18,
    "website_slideshows": 0,
    "website_slideshow_items": 0,
}

MINIMUM_COUNTS = {
    "items": 10_000,
    "item_prices": 10_000,
    "item_variant_attributes": 30_000,
}


def _load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AssertionError(f"Invalid JSON: {path}: {exc}") from exc


def main() -> int:
    parse_noop_args(__doc__)

    failures: list[str] = []
    snapshots = sorted(AUDIT_ROOT.glob("current-state-snapshot-*"))
    snapshot = max(snapshots, key=lambda path: path.stat().st_mtime) if snapshots else None

    if snapshot is None:
        failures.append(f"Snapshot folder missing under: {AUDIT_ROOT}")
    else:
        for name in sorted(REQUIRED_JSON_FILES):
            path = snapshot / name
            if not path.exists():
                failures.append(f"Missing required JSON file: {name}")
                continue
            _load_json(path)

        for name in sorted(REQUIRED_TEXT_FILES):
            path = snapshot / name
            if not path.exists():
                failures.append(f"Missing required text file: {name}")
            elif not path.read_text(encoding="utf-8").strip():
                failures.append(f"Required text file is empty: {name}")

    if not failures and snapshot is not None:
        summary = _load_json(snapshot / "summary.json")
        counts = summary.get("counts") or {}
        for key, expected in EXPECTED_COUNTS.items():
            actual = counts.get(key)
            if actual != expected:
                failures.append(f"Count mismatch for {key}: expected {expected}, got {actual}")
        for key, minimum in MINIMUM_COUNTS.items():
            actual = counts.get(key, 0)
            if actual < minimum:
                failures.append(f"Count too low for {key}: expected >= {minimum}, got {actual}")

        route_map = (snapshot / "route_category_map.md").read_text(encoding="utf-8")
        if "| Item Code | Name | Group | Route |" not in route_map:
            failures.append("route_category_map.md is missing the expected table header")

    if failures:
        print("[CATALOG STATE SNAPSHOT] FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("[CATALOG STATE SNAPSHOT] PASS")
    print(f"snapshot={snapshot}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
