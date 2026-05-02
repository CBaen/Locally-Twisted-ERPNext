"""Product option helpers for customer-facing Webshop templates."""

from __future__ import annotations

from typing import Any

from webshop.webshop.variant_selector.utils import get_attributes_and_values


def get_variant_attribute_options(item_code: str | None) -> list[dict[str, Any]]:
    """Return Webshop's prepared variant attribute/value data for a template item."""
    if not item_code:
        return []
    return get_attributes_and_values(item_code) or []
