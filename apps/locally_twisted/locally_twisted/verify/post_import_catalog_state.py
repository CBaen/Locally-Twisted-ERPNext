"""Read-only post-import catalog state checks for the corrected V1 import."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

try:
    import frappe
except ImportError:  # pragma: no cover - contract tests exercise pure helpers without Frappe installed.
    frappe = None


MANIFEST_PATH = Path(
    "/home/frappe/frappe-bench/apps/locally_twisted/locally_twisted/seed/_guard/"
    "25-v1-odoo-erpnext-import-manifest.json"
)
PRIORITY_SLUGS = [
    "easter-balloon-cups",
    "7-butterfly-column",
    "graduation-grab-n-go",
    "6-graduation-stands",
    "unicorn-bouquet",
]


def run() -> dict[str, Any]:
    _require_frappe()
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    included_slugs = [row["slug"] for row in manifest.get("products") or []]
    excluded_slugs = [row["slug"] for row in manifest.get("excluded_products") or []]

    variant_codes = [
        row.name
        for row in frappe.get_all(
            "Item",
            filters={"variant_of": ["in", included_slugs]},
            fields=["name"],
            limit_page_length=10000,
        )
    ]
    price_item_codes = included_slugs + variant_codes
    item_price_rows = frappe.get_all(
        "Item Price",
        filters={"item_code": ["in", price_item_codes], "price_list": "Standard Selling", "selling": 1},
        fields=["name", "item_code"],
        limit_page_length=12000,
    )
    distinct_priced_item_codes = sorted(
        {row.item_code for row in item_price_rows if getattr(row, "item_code", None)}
    )

    statuses_by_slug = {slug: _product_status(slug) for slug in included_slugs}
    for slug in PRIORITY_SLUGS:
        if slug not in statuses_by_slug:
            statuses_by_slug[slug] = _product_status(slug)

    return evaluate_catalog_state(
        manifest_path=MANIFEST_PATH,
        included_slugs=included_slugs,
        excluded_slugs=excluded_slugs,
        statuses_by_slug=statuses_by_slug,
        priority_slugs=PRIORITY_SLUGS,
        counts={
            "website_items_included": frappe.db.count("Website Item", {"item_code": ["in", included_slugs]}),
            "item_templates_included": frappe.db.count("Item", {"name": ["in", included_slugs]}),
            "item_variants_included": len(variant_codes),
            "item_prices_included": len(item_price_rows),
            "distinct_priced_item_codes_included": len(distinct_priced_item_codes),
            "manifest_source_ready_sale_units": _manifest_source_ready_sale_units(manifest),
        },
    )


def evaluate_catalog_state(
    *,
    included_slugs: Sequence[str],
    excluded_slugs: Sequence[str],
    statuses_by_slug: Mapping[str, Mapping[str, Any] | None],
    counts: Mapping[str, Any],
    priority_slugs: Sequence[str] = PRIORITY_SLUGS,
    manifest_path: str | Path | None = None,
) -> dict[str, Any]:
    """Return fail-loud catalog readiness evidence without touching the DB."""
    included = _unique_strings(included_slugs)
    excluded = _unique_strings(excluded_slugs)
    normalized_counts = dict(counts)
    included_statuses = {
        slug: _normalized_status(statuses_by_slug.get(slug), slug)
        for slug in included
    }
    priority_products = {
        slug: _normalized_status(statuses_by_slug.get(slug), slug)
        for slug in _unique_strings(priority_slugs)
    }

    missing_website_item_slugs = [
        slug for slug, status in included_statuses.items() if not status.get("website_item")
    ]
    unpublished_website_item_slugs = [
        slug
        for slug, status in included_statuses.items()
        if status.get("website_item") and not _truthy(_row_value(status["website_item"], "published"))
    ]
    missing_item_slugs = [
        slug for slug, status in included_statuses.items() if not status.get("item")
    ]
    disabled_item_slugs = [
        slug
        for slug, status in included_statuses.items()
        if status.get("item") and _truthy(_row_value(status["item"], "disabled"))
    ]
    unpriced_slugs = [
        slug for slug, status in included_statuses.items() if int(status.get("price_count") or 0) <= 0
    ]
    unready_priority_products = [
        slug for slug, status in priority_products.items() if not status.get("ready")
    ]

    count_blockers = _count_blockers(normalized_counts, included_count=len(included))
    blockers = []
    if missing_website_item_slugs:
        blockers.append("missing_website_items")
    if unpublished_website_item_slugs:
        blockers.append("unpublished_website_items")
    if missing_item_slugs:
        blockers.append("missing_items")
    if disabled_item_slugs:
        blockers.append("disabled_items")
    if unpriced_slugs:
        blockers.append("missing_prices")
    if unready_priority_products:
        blockers.append("unready_priority_products")
    blockers.extend(count_blockers)

    result = {
        "ok": not blockers,
        "included_count": len(included),
        "excluded_count": len(excluded),
        "explicit_excluded_slugs": excluded,
        "counts": normalized_counts,
        "priority_products": priority_products,
        "product_statuses": included_statuses,
        "blockers": blockers,
        "missing_website_item_slugs": missing_website_item_slugs,
        "unpublished_website_item_slugs": unpublished_website_item_slugs,
        "missing_item_slugs": missing_item_slugs,
        "disabled_item_slugs": disabled_item_slugs,
        "unpriced_slugs": unpriced_slugs,
        "unready_priority_products": unready_priority_products,
    }
    if manifest_path is not None:
        result["manifest_path"] = str(manifest_path)
    return result


def _product_status(slug: str) -> dict[str, Any]:
    _require_frappe()
    wi = frappe.db.get_value(
        "Website Item",
        {"item_code": slug},
        ["name", "item_code", "route", "published", "website_image", "lt_product_page_type", "lt_commerce_lane"],
        as_dict=True,
    )
    item = frappe.db.get_value(
        "Item",
        slug,
        ["name", "item_name", "item_group", "has_variants", "disabled", "image"],
        as_dict=True,
    )
    variant_codes = [
        row.name
        for row in frappe.get_all(
            "Item",
            filters={"variant_of": slug},
            fields=["name"],
            limit_page_length=10000,
        )
    ]
    price_codes = [slug] + variant_codes
    prices = [
        row.price_list_rate
        for row in frappe.get_all(
            "Item Price",
            filters={"item_code": ["in", price_codes], "price_list": "Standard Selling", "selling": 1},
            fields=["price_list_rate"],
            limit_page_length=10000,
        )
    ]
    return {
        "website_item": wi,
        "item": item,
        "variant_count": len(variant_codes),
        "price_count": len(prices),
        "price_min": min(prices) if prices else None,
        "price_max": max(prices) if prices else None,
        "ready": _status_ready({"website_item": wi, "item": item, "price_count": len(prices)}),
    }


def _require_frappe() -> None:
    if frappe is None:
        raise RuntimeError("Frappe is required for live post-import catalog state checks")


def _normalized_status(status: Mapping[str, Any] | None, slug: str) -> dict[str, Any]:
    normalized = dict(status or {})
    normalized.setdefault("website_item", None)
    normalized.setdefault("item", None)
    normalized.setdefault("variant_count", 0)
    normalized.setdefault("price_count", 0)
    normalized.setdefault("price_min", None)
    normalized.setdefault("price_max", None)
    normalized["ready"] = _status_ready(normalized)
    return normalized


def _status_ready(status: Mapping[str, Any]) -> bool:
    website_item = status.get("website_item")
    item = status.get("item")
    return bool(
        website_item
        and _truthy(_row_value(website_item, "published"))
        and item
        and not _truthy(_row_value(item, "disabled"))
        and int(status.get("price_count") or 0) > 0
    )


def _count_blockers(counts: Mapping[str, Any], *, included_count: int) -> list[str]:
    blockers = []
    if _count_value(counts, "website_items_included") != included_count:
        blockers.append("website_item_count_mismatch")
    if _count_value(counts, "item_templates_included") != included_count:
        blockers.append("item_template_count_mismatch")

    source_ready_units = _count_value(counts, "manifest_source_ready_sale_units")
    priced_codes = _count_value(counts, "distinct_priced_item_codes_included")
    if source_ready_units is not None and priced_codes is not None and priced_codes < source_ready_units:
        blockers.append("priced_item_coverage_below_manifest_sale_units")
    return blockers


def _manifest_source_ready_sale_units(manifest: Mapping[str, Any]) -> int:
    summary = manifest.get("summary") or {}
    by_source = summary.get("v1_price_units_by_source") or {}
    if by_source.get("source_price_ready") is not None:
        return int(by_source.get("source_price_ready") or 0)

    total = 0
    for product in manifest.get("products") or []:
        price_manifest = product.get("price_manifest") or {}
        for row in price_manifest.get("sale_units") or []:
            if row.get("price_resolution_status") == "source_price_ready":
                total += 1
    if total:
        return total

    v1_sale_units = int(summary.get("v1_sale_units") or 0)
    review_units = int(summary.get("v1_price_review_units") or 0)
    return max(0, v1_sale_units - review_units)


def _count_value(counts: Mapping[str, Any], key: str) -> int | None:
    if key not in counts:
        return None
    value = counts.get(key)
    if value is None:
        return None
    return int(value)


def _row_value(row: Any, key: str) -> Any:
    if isinstance(row, Mapping):
        return row.get(key)
    return getattr(row, key, None)


def _truthy(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() not in {"", "0", "false", "no"}
    return bool(value)


def _unique_strings(values: Sequence[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        text = str(value)
        if text in seen:
            continue
        seen.add(text)
        result.append(text)
    return result
