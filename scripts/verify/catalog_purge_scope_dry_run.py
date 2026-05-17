"""Compute a dry-run catalog purge scope from the saved current-state snapshot.

This script does not connect to ERPNext and does not delete anything. It uses the
snapshot as evidence to identify product-catalog rows in the corrected import
subset. Odoo-imported products are product targets; variants and high-variant
products are allowed when the current backend schema can preserve their meaning.
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from _cli import parse_noop_args

ROOT = Path(__file__).resolve().parents[2]
APP_PATH = ROOT / "apps" / "locally_twisted"
if str(APP_PATH) not in sys.path:
    sys.path.insert(0, str(APP_PATH))

from locally_twisted.catalog_import_subset import (
    assert_must_work_products_included,
    import_exclusion_reasons,
    primary_exclusion_reason,
    reason_counts,
)
from locally_twisted.catalog_contract import build_product_page_contract

AUDIT_ROOT = ROOT / "audits" / "odoo-erpnext-migration-audit-2026-05-08"
SOURCE_ROOT = ROOT / "_resources" / "odoo-live"
REPORT_PATH = AUDIT_ROOT / "16-catalog-purge-scope-dry-run.md"
REPORT_JSON_PATH = AUDIT_ROOT / "16-catalog-purge-scope-dry-run.json"

PROTECTED_ITEM_CODES = {
    "DELIVERY-STANDARD",
    "DELIVERY-PARK-CITY",
    "DELIVERY-PICKUP",
    "DELIVERY-OUT-OF-AREA",
}


def main() -> int:
    parse_noop_args(__doc__)

    snapshot = _latest_snapshot()
    website_items = _load(snapshot, "website_items.json")
    items = _load(snapshot, "items.json")
    prices = _load(snapshot, "item_prices.json")
    variant_attrs = _load(snapshot, "item_variant_attributes.json")
    files = _load(snapshot, "files_product_related.json")

    subset = _import_subset()
    included_slugs = set(subset["included_slugs"])

    template_codes = {row.get("item_code") for row in website_items if row.get("item_code")}
    protected_templates = sorted(code for code in template_codes if code in PROTECTED_ITEM_CODES)
    purge_templates = sorted(code for code in template_codes if code in included_slugs)
    excluded_existing_templates = sorted(
        code
        for code in template_codes
        if code not in included_slugs and code not in PROTECTED_ITEM_CODES
    )

    variant_codes = sorted(
        row.get("item_code")
        for row in items
        if row.get("variant_of") in purge_templates and row.get("item_code")
    )
    purge_item_codes = set(purge_templates) | set(variant_codes)

    purge_prices = [row for row in prices if row.get("item_code") in purge_item_codes]
    purge_variant_attrs = [row for row in variant_attrs if row.get("parent") in purge_item_codes]
    purge_files = [
        row
        for row in files
        if row.get("attached_to_doctype") in {"Item", "Website Item"}
        and row.get("attached_to_name") in purge_item_codes
    ]

    report = {
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "read_only": True,
        "destructive_allowed": False,
        "snapshot": str(snapshot.relative_to(ROOT)),
        "v1_subset": subset,
        "purge_scope_counts": {
            "website_items": len(purge_templates),
            "item_templates": len(purge_templates),
            "item_variants": len(variant_codes),
            "item_prices": len(purge_prices),
            "item_variant_attribute_rows": len(purge_variant_attrs),
            "product_related_file_rows": len(purge_files),
            "protected_service_templates": len(protected_templates),
            "excluded_existing_templates_held": len(excluded_existing_templates),
        },
        "purge_template_item_codes": purge_templates,
        "protected_service_item_codes": protected_templates,
        "excluded_existing_template_item_codes_held": excluded_existing_templates,
    }
    _write_report(report)

    print("[CATALOG PURGE SCOPE DRY RUN] PASS")
    print(f"report={REPORT_PATH}")
    print(f"json={REPORT_JSON_PATH}")
    print(
        f"v1_included={len(subset['included_slugs'])} "
        f"v1_excluded={len(subset['excluded_products'])} "
        f"templates={len(purge_templates)} variants={len(variant_codes)} prices={len(purge_prices)}"
    )
    return 0


def _latest_snapshot() -> Path:
    snapshots = sorted(AUDIT_ROOT.glob("current-state-snapshot-*"))
    if not snapshots:
        raise SystemExit(f"FATAL: no current-state-snapshot-* folder found under {AUDIT_ROOT}")
    return max(snapshots, key=lambda path: path.stat().st_mtime)


def _load(snapshot: Path, name: str):
    return json.loads((snapshot / name).read_text(encoding="utf-8"))


def _import_subset() -> dict:
    catalog = json.loads((SOURCE_ROOT / "catalog.json").read_text(encoding="utf-8"))
    products = catalog.get("products") if isinstance(catalog, dict) else catalog
    slug_to_group_raw = json.loads((SOURCE_ROOT / "slug_to_group.json").read_text(encoding="utf-8"))
    slug_to_group = {k: v for k, v in slug_to_group_raw.items() if not k.startswith("_")}

    included: list[str] = []
    excluded: list[dict] = []
    rows: list[dict] = []

    for product in products:
        slug = str(product.get("slug") or "").strip()
        contract = build_product_page_contract(product, category_hint=slug_to_group.get(slug, ""))
        reasons = import_exclusion_reasons(product, contract)
        primary = primary_exclusion_reason(reasons)
        row = {
            "slug": slug,
            "name": product.get("name"),
            "primary_exclusion_reason": primary,
            "excluded_reason_codes": [reason["code"] for reason in reasons],
            "excluded_reason_details": reasons,
            "product_page_type": contract.product_page_type,
            "commerce_lane": contract.commerce_lane,
            "source_variant_rows": contract.source_variant_rows,
            "customization_axes": [axis.name for axis in contract.customization_axes],
            "required_axes": [axis.name for axis in contract.required_axes],
            "selected_for_v1_import": not reasons,
        }
        rows.append(row)
        if reasons:
            excluded.append(row)
        else:
            included.append(slug)

    validation_errors = assert_must_work_products_included(rows)
    if validation_errors:
        raise SystemExit("FATAL: " + "; ".join(validation_errors))

    return {
        "rule": "include Odoo-imported products that fit the current ERPNext backend schema; variants and high-variant products are allowed; exclude only proven schema/backend blockers",
        "included_slugs": included,
        "included_count": len(included),
        "excluded_products": excluded,
        "excluded_count": len(excluded),
        "excluded_counts_by_primary_reason": reason_counts(rows, primary=True),
        "excluded_counts_by_reason": reason_counts(rows, primary=False),
        "must_work_validation_errors": validation_errors,
        "rows": rows,
    }


def _write_report(report: dict) -> None:
    subset = report["v1_subset"]
    counts = report["purge_scope_counts"]
    lines = [
        "# Catalog Purge Scope Dry Run",
        "",
        "Read-only dry run from saved snapshot. No ERPNext connection and no deletes.",
        "",
        f"- Generated: `{report['generated_at']}`",
        f"- Snapshot: `{report['snapshot']}`",
        f"- Import subset rule: {subset['rule']}.",
        "- Variants, cups, and high-variant products are products and are not blanket exclusions.",
        "",
        "## Import source subset",
        "",
        f"- Included products: {len(subset['included_slugs'])}",
        f"- Excluded products: {len(subset['excluded_products'])}",
        f"- Excluded by primary reason: {_format_counts(subset['excluded_counts_by_primary_reason'])}",
        f"- Excluded by all reason flags: {_format_counts(subset['excluded_counts_by_reason'])}",
        "",
        "## Proposed generated catalog purge scope",
        "",
        f"- Website Items: {counts['website_items']}",
        f"- Item templates: {counts['item_templates']}",
        f"- Item variants: {counts['item_variants']}",
        f"- Item Prices: {counts['item_prices']}",
        f"- Item Variant Attribute rows: {counts['item_variant_attribute_rows']}",
        f"- Product-related File rows attached to purge items/templates: {counts['product_related_file_rows']}",
        f"- Existing excluded Website Item templates held out of purge scope: {counts['excluded_existing_templates_held']}",
        "",
        "## Protected service item codes",
        "",
    ]
    protected = report["protected_service_item_codes"]
    if protected:
        lines.extend(f"- `{code}`" for code in protected)
    else:
        lines.append("- None of the Website Item templates matched protected service item codes.")

    lines.extend(["", "## Template item codes in purge scope", ""])
    lines.extend(f"- `{code}`" for code in report["purge_template_item_codes"])

    lines.extend(["", "## Excluded source products held out of import", ""])
    for row in subset["excluded_products"]:
        lines.append(
            f"- `{row['slug']}` - {row['primary_exclusion_reason']} "
            f"({', '.join(row['excluded_reason_codes'])})"
        )

    lines.extend(
        [
            "",
            "## Safety interpretation",
            "",
            "This dry run defines only the product-catalog-owned demolition set for the corrected import subset. Service items remain protected. It does not include Customers, Leads, Quotations, Sales Orders, Sales Invoices, Payment records, tax setup, workspaces, fixtures, or non-catalog business records.",
            "",
            "Before real destructive mode, rerun against live DB with backup/export and exact allowlist confirmation.",
            "",
            "## Gate result",
            "",
            "**DRY-RUN ONLY. Destructive purge still requires explicit approval.**",
        ]
    )

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    REPORT_JSON_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _format_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "none"
    return ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))


if __name__ == "__main__":
    raise SystemExit(main())
