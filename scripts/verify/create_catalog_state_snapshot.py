#!/usr/bin/env python3
"""Create a read-only ERPNext catalog state snapshot for import rollback planning.

This script reads the local ERPNext/Frappe site through `bench execute` in the
running backend container. It does not write, purge, import, or delete ERPNext
records. The only writes are JSON/Markdown evidence files under the audit
snapshot folder.
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
AUDIT_ROOT = ROOT / "audits" / "catalog-import-audit-2026-05-08"
SOURCE_ROOT = ROOT / "_resources" / "catalog-source"

DEFAULT_CONTAINER = "locally-twisted-erpnext-v15-backend-1"
DEFAULT_SITE = "frontend"

DOCTYPES: dict[str, dict[str, Any]] = {
    "item_groups": {
        "doctype": "Item Group",
        "fields": ["name", "item_group_name", "parent_item_group", "route", "image", "is_group"],
        "order_by": "name asc",
    },
    "website_items": {
        "doctype": "Website Item",
        "fields": [
            "name",
            "item_code",
            "web_item_name",
            "item_group",
            "published",
            "route",
            "website_image",
            "lt_product_page_type",
            "lt_commerce_lane",
        ],
        "order_by": "name asc",
    },
    "items": {
        "doctype": "Item",
        "fields": [
            "name",
            "item_code",
            "item_name",
            "item_group",
            "variant_of",
            "has_variants",
            "disabled",
            "is_sales_item",
            "is_stock_item",
            "image",
        ],
        "order_by": "name asc",
    },
    "item_prices": {
        "doctype": "Item Price",
        "fields": ["name", "item_code", "price_list", "price_list_rate", "currency", "selling"],
        "order_by": "item_code asc, name asc",
    },
    "item_variant_attributes": {
        "doctype": "Item Variant Attribute",
        "fields": ["name", "parent", "parenttype", "parentfield", "idx", "attribute", "attribute_value"],
        "order_by": "parent asc, idx asc",
    },
    "item_attributes": {
        "doctype": "Item Attribute",
        "fields": ["name", "attribute_name", "numeric_values", "disabled"],
        "order_by": "name asc",
    },
    "item_attribute_values": {
        "doctype": "Item Attribute Value",
        "fields": ["name", "parent", "parenttype", "parentfield", "idx", "attribute_value", "abbr"],
        "order_by": "parent asc, idx asc",
    },
    "files_product_related": {
        "doctype": "File",
        "fields": [
            "name",
            "file_name",
            "file_url",
            "is_private",
            "attached_to_doctype",
            "attached_to_name",
        ],
        "filters": [["attached_to_doctype", "in", ["Item", "Website Item"]]],
        "order_by": "attached_to_doctype asc, attached_to_name asc, name asc",
    },
    "website_slideshows": {
        "doctype": "Website Slideshow",
        "fields": ["name", "slideshow_name", "header"],
        "order_by": "name asc",
        "optional": True,
    },
    "website_slideshow_items": {
        "doctype": "Website Slideshow Item",
        "fields": ["name", "parent", "parenttype", "parentfield", "idx", "image", "heading", "description", "url"],
        "order_by": "parent asc, idx asc",
        "optional": True,
    },
    "website_item_groups_child_rows": {
        "doctype": "Website Item Group",
        "fields": ["name", "parent", "parenttype", "parentfield", "idx", "item_group"],
        "order_by": "parent asc, idx asc",
        "optional": True,
    },
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--container", default=DEFAULT_CONTAINER, help="Backend container name")
    parser.add_argument("--site", default=DEFAULT_SITE, help="Frappe site name")
    parser.add_argument("--snapshot-id", help="Override snapshot folder suffix")
    args = parser.parse_args()

    generated_at = datetime.now(UTC).replace(microsecond=0)
    snapshot_id = args.snapshot_id or generated_at.strftime("%Y-%m-%d-%H%M")
    snapshot_dir = AUDIT_ROOT / f"current-state-snapshot-{snapshot_id}"
    snapshot_dir.mkdir(parents=True, exist_ok=False)

    warnings: list[str] = []
    rows_by_name: dict[str, list[dict[str, Any]]] = {}
    for file_stem, spec in DOCTYPES.items():
        try:
            rows = _get_list(args.container, args.site, spec)
        except RuntimeError as exc:
            if spec.get("optional"):
                rows = []
                warnings.append(f"{file_stem}: optional doctype read failed: {exc}")
            else:
                raise
        rows_by_name[file_stem] = rows
        _write_json(snapshot_dir / f"{file_stem}.json", rows)

    _copy_source_reference(snapshot_dir)
    _write_route_category_map(snapshot_dir, rows_by_name["website_items"])
    _write_readme(snapshot_dir, generated_at, args.container, args.site)

    counts = {name: len(rows) for name, rows in rows_by_name.items()}
    summary = {
        "generated_at": generated_at.isoformat().replace("+00:00", "Z"),
        "read_only": True,
        "site": args.site,
        "container": args.container,
        "snapshot_dir": str(snapshot_dir.relative_to(ROOT)),
        "counts": counts,
        "warnings": warnings,
        "source_files": {
            "catalog": str((SOURCE_ROOT / "catalog.json").relative_to(ROOT)),
            "slug_to_group": str((SOURCE_ROOT / "slug_to_group.json").relative_to(ROOT)),
        },
    }
    _write_json(snapshot_dir / "summary.json", summary)

    print("[CATALOG STATE SNAPSHOT CREATE] PASS")
    print(f"snapshot={snapshot_dir.relative_to(ROOT)}")
    print("counts=" + json.dumps(counts, sort_keys=True))
    if warnings:
        print("warnings=" + json.dumps(warnings, sort_keys=True))
    return 0


def _get_list(container: str, site: str, spec: dict[str, Any]) -> list[dict[str, Any]]:
    kwargs = {
        "doctype": spec["doctype"],
        "fields": spec["fields"],
        "limit_page_length": 100000,
        "order_by": spec.get("order_by") or "name asc",
    }
    if spec.get("filters") is not None:
        kwargs["filters"] = spec["filters"]

    cmd = [
        "docker",
        "exec",
        container,
        "bench",
        "--site",
        site,
        "execute",
        "frappe.get_all",
        "--kwargs",
        json.dumps(kwargs),
    ]
    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise RuntimeError(detail or f"bench execute failed for {spec['doctype']}")
    return _parse_bench_json(result.stdout)


def _parse_bench_json(stdout: str) -> list[dict[str, Any]]:
    text = stdout.strip()
    if not text:
        return []
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        for line in reversed([line.strip() for line in text.splitlines() if line.strip()]):
            try:
                data = json.loads(line)
                break
            except json.JSONDecodeError:
                continue
        else:
            raise RuntimeError(f"Could not parse bench JSON output: {text[:500]}")
    if not isinstance(data, list):
        raise RuntimeError(f"Expected list output from bench, got {type(data).__name__}")
    return data


def _copy_source_reference(snapshot_dir: Path) -> None:
    source_pairs = {
        "source_catalog_reference.json": SOURCE_ROOT / "catalog.json",
        "source_slug_to_group.json": SOURCE_ROOT / "slug_to_group.json",
    }
    for output_name, source_path in source_pairs.items():
        if source_path.exists():
            _write_json(snapshot_dir / output_name, json.loads(source_path.read_text(encoding="utf-8")))
        else:
            _write_json(snapshot_dir / output_name, {"missing": str(source_path.relative_to(ROOT))})


def _write_route_category_map(snapshot_dir: Path, website_items: list[dict[str, Any]]) -> None:
    lines = [
        "# Route Category Map",
        "",
        "| Item Code | Name | Group | Route | Published | Page Type | Lane |",
        "|---|---|---|---|---:|---|---|",
    ]
    for row in website_items:
        lines.append(
            "| "
            + " | ".join(
                _table_cell(row.get(key))
                for key in (
                    "item_code",
                    "web_item_name",
                    "item_group",
                    "route",
                    "published",
                    "lt_product_page_type",
                    "lt_commerce_lane",
                )
            )
            + " |"
        )
    (snapshot_dir / "route_category_map.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_readme(snapshot_dir: Path, generated_at: datetime, container: str, site: str) -> None:
    lines = [
        "# Current ERPNext Catalog State Snapshot",
        "",
        f"- Generated at: `{generated_at.isoformat().replace('+00:00', 'Z')}`",
        f"- Frappe site: `{site}`",
        f"- Backend container: `{container}`",
        "- Mode: read-only ERPNext reads; no purge, import, delete, or record writes.",
        "",
        "This folder is the pre-import evidence packet used by the product import readiness gate and purge-scope dry run.",
    ]
    (snapshot_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def _table_cell(value: Any) -> str:
    return str(value if value is not None else "").replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    sys.exit(main())
