"""Compute a dry-run catalog purge scope from the saved current-state snapshot.

This script does not connect to ERPNext and does not delete anything. It uses the
snapshot as evidence to identify generated catalog rows likely owned by the
catalog pipeline.
"""

from __future__ import annotations

import json
from pathlib import Path

SNAPSHOT = Path(
    "audits/odoo-erpnext-migration-audit-2026-05-08/"
    "current-state-snapshot-2026-05-08-1102"
)
REPORT_PATH = Path(
    "audits/odoo-erpnext-migration-audit-2026-05-08/"
    "16-catalog-purge-scope-dry-run.md"
)

PROTECTED_ITEM_CODES = {
    "DELIVERY-STANDARD",
    "DELIVERY-PARK-CITY",
    "DELIVERY-PICKUP",
    "DELIVERY-OUT-OF-AREA",
}


def _load(name: str):
    return json.loads((SNAPSHOT / name).read_text(encoding="utf-8"))


def main() -> int:
    website_items = _load("website_items.json")
    items = _load("items.json")
    prices = _load("item_prices.json")
    variant_attrs = _load("item_variant_attributes.json")
    files = _load("files_product_related.json")

    template_codes = {row.get("item_code") for row in website_items if row.get("item_code")}
    protected_templates = sorted(code for code in template_codes if code in PROTECTED_ITEM_CODES)
    purge_templates = sorted(code for code in template_codes if code not in PROTECTED_ITEM_CODES)

    variant_codes = sorted(
        row.get("item_code")
        for row in items
        if row.get("variant_of") in purge_templates and row.get("item_code")
    )
    purge_item_codes = set(purge_templates) | set(variant_codes)

    purge_prices = [row for row in prices if row.get("item_code") in purge_item_codes]
    purge_variant_attrs = [row for row in variant_attrs if row.get("parent") in purge_item_codes]
    purge_files = [
        row for row in files
        if row.get("attached_to_doctype") in {"Item", "Website Item"}
        and row.get("attached_to_name") in purge_item_codes | set(purge_templates)
    ]

    lines = [
        "# Catalog Purge Scope Dry Run",
        "",
        "Read-only dry run from saved snapshot. No ERPNext connection and no deletes.",
        "",
        "## Proposed generated catalog purge scope",
        "",
        f"- Website Items: {len(purge_templates)}",
        f"- Item templates: {len(purge_templates)}",
        f"- Item variants: {len(variant_codes)}",
        f"- Item Prices: {len(purge_prices)}",
        f"- Item Variant Attribute rows: {len(purge_variant_attrs)}",
        f"- Product-related File rows attached to purge items/templates: {len(purge_files)}",
        "",
        "## Protected / excluded item codes",
        "",
    ]
    if protected_templates:
        for code in protected_templates:
            lines.append(f"- `{code}`")
    else:
        lines.append("- None of the Website Item templates matched protected service item codes.")

    lines.extend([
        "",
        "## First 60 template item codes in purge scope",
        "",
    ])
    for code in purge_templates[:60]:
        lines.append(f"- `{code}`")

    lines.extend([
        "",
        "## Safety interpretation",
        "",
        "This dry run defines the likely product-catalog-owned demolition set. It does not include Customers, Leads, Quotations, Sales Orders, Sales Invoices, Payment records, tax setup, workspaces, fixtures, or non-catalog business records.",
        "",
        "Before real destructive mode, rerun against live DB with backup/export and exact allowlist confirmation.",
        "",
        "## Gate result",
        "",
        "**DRY-RUN ONLY. Destructive purge still requires explicit approval.**",
    ])

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print("[CATALOG PURGE SCOPE DRY RUN] PASS")
    print(f"report={REPORT_PATH}")
    print(f"templates={len(purge_templates)} variants={len(variant_codes)} prices={len(purge_prices)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
