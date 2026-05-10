"""Pure labels for LT product-page runtime contracts."""
from __future__ import annotations

from typing import Any


PRODUCT_PAGE_TYPE_OPTIONS = (
    "needs_review",
    "simple_product",
    "complex_custom_product",
)

COMMERCE_LANE_OPTIONS = (
    "needs_review",
    "checkout",
    "quote_first",
    "hybrid",
)

PRODUCT_PAGE_TYPE_LABELS = {
    "needs_review": "Needs page review",
    "simple_product": "Ready-to-order page",
    "complex_custom_product": "Custom quote page",
}

COMMERCE_LANE_LABELS = {
    "needs_review": "Needs review before customers use it",
    "checkout": "Online checkout",
    "quote_first": "Quote request first",
    "hybrid": "Checkout or quote",
}


def product_page_type_label(value: Any) -> str:
    return PRODUCT_PAGE_TYPE_LABELS.get(str(value or "").strip(), PRODUCT_PAGE_TYPE_LABELS["needs_review"])


def commerce_lane_label(value: Any) -> str:
    return COMMERCE_LANE_LABELS.get(str(value or "").strip(), COMMERCE_LANE_LABELS["needs_review"])
