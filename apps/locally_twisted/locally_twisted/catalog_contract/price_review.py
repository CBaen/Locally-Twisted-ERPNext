"""Business price review packet for product-page import candidates.

This module is pure reporting code. It extracts live ERPNext snapshot price
candidates from the price-enrichment artifact and keeps them explicitly
unapproved until the business accepts or replaces them.
"""
from __future__ import annotations

from typing import Any


SCHEMA_VERSION = "lt-product-page-price-review-packet-v1"
SAFE_DEFAULT = "business_review_required"
LIVE_SNAPSHOT = "live_erpnext_snapshot"


def build_price_review_packet(price_enrichment_artifact: dict[str, Any]) -> dict[str, Any]:
    """Build a JSON-safe packet for unapproved live-snapshot price candidates."""
    products = [
        _product_row(product)
        for product in price_enrichment_artifact.get("products") or []
        if _review_units(product)
    ]
    review_unit_count = sum(product["review_unit_count"] for product in products)
    summary = price_enrichment_artifact.get("summary") or {}
    return {
        "schema_version": SCHEMA_VERSION,
        "purpose": "Business review packet for product-page prices sourced from current live ERPNext snapshot data.",
        "warning": (
            "This packet does not approve customer-facing prices. Live snapshot "
            "candidates preserve current ERPNext state only and must be accepted or replaced before import/reopen."
        ),
        "safe_default": SAFE_DEFAULT,
        "source_product_count": _int(summary.get("source_products") or price_enrichment_artifact.get("header", {}).get("source_product_count")),
        "expected_sale_units": _int(summary.get("expected_sale_units")),
        "candidate_sale_units": _int(summary.get("candidate_sale_units")),
        "review_unit_count": review_unit_count,
        "products_needing_review": len(products),
        "approved_for_public_price_count": 0,
        "products": products,
    }


def _product_row(product: dict[str, Any]) -> dict[str, Any]:
    units = _review_units(product)
    return {
        "slug": str(product.get("slug") or ""),
        "name": str(product.get("name") or product.get("slug") or ""),
        "product_page_type": str(product.get("product_page_type") or ""),
        "commerce_lane": str(product.get("commerce_lane") or ""),
        "required_axes": list(product.get("required_axes") or []),
        "review_unit_count": len(units),
        "safe_default": SAFE_DEFAULT,
        "decision_needed": "Approve this live-snapshot price for public use, replace it with a business-approved price, or keep the unit quote-only.",
        "review_units": units,
    }


def _review_units(product: dict[str, Any]) -> list[dict[str, Any]]:
    units = []
    for unit in product.get("sale_units") or []:
        if unit.get("price_source_kind") != LIVE_SNAPSHOT:
            continue
        units.append(
            {
                "sale_unit_key": str(unit.get("sale_unit_key") or ""),
                "projected_required_combo": dict(unit.get("projected_required_combo") or {}),
                "chosen_price": str(unit.get("chosen_price") or ""),
                "price_source_kind": LIVE_SNAPSHOT,
                "source_row_count": _int(unit.get("source_row_count")),
                "live_active_match_count": _int(unit.get("live_active_match_count")),
                "live_priced_match_count": _int(unit.get("live_priced_match_count")),
                "distinct_live_prices": list(unit.get("distinct_live_prices") or []),
                "safe_default": SAFE_DEFAULT,
            }
        )
    return units


def _int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0
