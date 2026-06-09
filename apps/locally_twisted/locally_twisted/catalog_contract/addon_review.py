"""Source-backed approval packet for review-only product add-on axes.

This module is pure reporting code. It does not approve add-ons, mutate
ERPNext, or infer checkout pricing. Its job is to turn vague add-on blockers
into row-level evidence GL/Locally Twisted can review.
"""
from __future__ import annotations

from typing import Any

from locally_twisted.catalog_contract.source_builder import build_product_page_contract


SAFE_DEFAULT = "quote_only_until_approved"
SCHEMA_VERSION = "lt-product-add-on-approval-packet-v1"


def build_add_on_approval_packet(
    products: list[dict[str, Any]],
    *,
    review_add_ons: dict[str, str],
    slug_to_group: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build a JSON-safe approval packet for unapproved source add-on axes."""
    slug_to_group = slug_to_group or {}
    rows = [
        _axis_row(axis_name, note, products, slug_to_group=slug_to_group)
        for axis_name, note in sorted(review_add_ons.items())
    ]
    rows = [row for row in rows if row["product_count"]]
    affected_slugs = {
        product["slug"]
        for row in rows
        for product in row["products"]
        if product.get("slug")
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "purpose": "Source-backed approval packet for legacy_source-derived add-on axes before ERPNext import/reopen.",
        "warning": (
            "This packet does not approve checkout. Every review-only add-on "
            "must stay quote-only until GL/Locally Twisted approves product-family mapping, pricing, quantity, and fulfillment behavior."
        ),
        "safe_default": SAFE_DEFAULT,
        "source_product_count": len(products),
        "review_axis_count": len(rows),
        "affected_product_count": len(affected_slugs),
        "approved_for_checkout_count": 0,
        "review_axes": rows,
    }


def _axis_row(
    axis_name: str,
    note: str,
    products: list[dict[str, Any]],
    *,
    slug_to_group: dict[str, str],
) -> dict[str, Any]:
    product_rows = [
        _product_row(product, axis_name, slug_to_group=slug_to_group)
        for product in products
        if _has_axis(product, axis_name)
    ]
    product_rows = [row for row in product_rows if row]
    source_values = sorted({value for row in product_rows for value in row["source_values"]}, key=_sort_value)
    variant_row_count = sum(int(row["variant_rows_with_axis"]) for row in product_rows)
    return {
        "axis": axis_name,
        "source_note": note,
        "decision_needed": _decision_needed(axis_name),
        "recommended_safe_default": SAFE_DEFAULT,
        "checkout_allowed": False,
        "approval_required_for_checkout": True,
        "product_count": len(product_rows),
        "source_value_count": len(source_values),
        "source_values": source_values,
        "variant_rows_with_axis": variant_row_count,
        "products": product_rows,
    }


def _product_row(
    product: dict[str, Any],
    axis_name: str,
    *,
    slug_to_group: dict[str, str],
) -> dict[str, Any]:
    slug = str(product.get("slug") or "").strip()
    contract = build_product_page_contract(product, category_hint=slug_to_group.get(slug, ""))
    values = _attribute_values(product, axis_name)
    combo_values = _combo_values(product, axis_name)
    return {
        "slug": slug,
        "title": str(product.get("name") or slug).strip(),
        "source_url": str(product.get("url") or product.get("source_url") or "").strip(),
        "category_hint": slug_to_group.get(slug, ""),
        "product_page_type": contract.product_page_type,
        "product_page_type_label": contract.product_page_type_label,
        "commerce_lane": contract.commerce_lane,
        "commerce_lane_label": contract.commerce_lane_label,
        "source_values": sorted(set(values) | set(combo_values), key=_sort_value),
        "attribute_value_count": len(values),
        "variant_rows_with_axis": _variant_rows_with_axis(product, axis_name),
        "current_runtime_behavior": "route_to_quote_before_paid_checkout",
        "checkout_allowed": False,
    }


def _has_axis(product: dict[str, Any], axis_name: str) -> bool:
    attributes = product.get("attributes") or {}
    return isinstance(attributes, dict) and axis_name in attributes


def _attribute_values(product: dict[str, Any], axis_name: str) -> tuple[str, ...]:
    axis = (product.get("attributes") or {}).get(axis_name) or {}
    values = axis.get("values") or []
    cleaned = [
        str(value.get("name") or "").strip()
        for value in values
        if isinstance(value, dict) and str(value.get("name") or "").strip()
    ]
    return tuple(dict.fromkeys(cleaned))


def _combo_values(product: dict[str, Any], axis_name: str) -> tuple[str, ...]:
    values = []
    for row in product.get("valid_variants") or []:
        combo = row.get("combo") if isinstance(row, dict) else {}
        if not isinstance(combo, dict):
            continue
        value = str(combo.get(axis_name) or "").strip()
        if value:
            values.append(value)
    return tuple(dict.fromkeys(values))


def _variant_rows_with_axis(product: dict[str, Any], axis_name: str) -> int:
    count = 0
    for row in product.get("valid_variants") or []:
        combo = row.get("combo") if isinstance(row, dict) else {}
        if isinstance(combo, dict) and str(combo.get(axis_name) or "").strip():
            count += 1
    return count


def _decision_needed(axis_name: str) -> str:
    decisions = {
        "Add ons": "Decide whether each value is a priced add-on, included decor choice, quote-only prompt, or source artifact to drop.",
        "Plush add ons": "Decide product eligibility, supplier/stock behavior, price, quantity rule, and whether plush should ever be paid checkout.",
        "Orbz toppers": "Decide topper eligibility, visual/media treatment, price, fulfillment notes, and quote-vs-checkout behavior.",
        "Add Bouquet": "Decide whether companion bouquets are product bundles, separate checkout lines, quote-only upsells, or removed from import.",
    }
    return decisions.get(axis_name, "Decide product eligibility, price, quantity, fulfillment, and checkout-vs-quote behavior.")


def _sort_value(value: str) -> tuple[int, str]:
    normalized = str(value or "").strip()
    if normalized.lower() in {"none", "no", "n/a"}:
        return (1, normalized.lower())
    return (0, normalized.lower())
