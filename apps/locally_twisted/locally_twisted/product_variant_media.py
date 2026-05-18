"""Customer-safe variant Item media helpers for LT ecommerce."""
from __future__ import annotations

from typing import Any

import frappe


PAGE_TYPE_SIMPLE = "simple_product"
COMMERCE_CHECKOUT = "checkout"


def approved_variant_item_media_for_codes(
    *,
    variant_item_code: str | None,
    website_item_code: str | None,
) -> dict[str, Any]:
    """Return approved customer media for a resolved simple-product variant."""
    variant_item_code = _text(variant_item_code)
    website_item_code = _text(website_item_code)
    if not variant_item_code or not website_item_code:
        return {}

    item = frappe.db.get_value(
        "Item",
        {"item_code": variant_item_code, "disabled": 0},
        ["item_code", "item_name", "variant_of", "image"],
        as_dict=True,
    )
    if not item:
        return {}

    website_item = _website_item_for_media(website_item_code)
    if not website_item:
        return {}

    return approved_variant_item_media(item=item, website_item=website_item)


def approved_variant_item_media(
    *,
    item: dict[str, Any],
    website_item: dict[str, Any],
    variant_options: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Approve direct Item.image rendering for simple checkout variants only.

    Product Setup media rules still own complex/custom image changes. This
    helper restores the older ready-to-order behavior where a resolved simple
    variant's own Item.image is the customer-facing selected media.
    """
    item_code = _text(item.get("item_code"))
    variant_of = _text(item.get("variant_of"))
    website_item_code = _text(website_item.get("item_code"))
    variant_image = _text(item.get("image"))
    fallback_image = _text(website_item.get("website_image"))
    if not item_code or not variant_of or variant_of != website_item_code:
        return {}
    if not variant_image or variant_image == fallback_image:
        return {}
    if _text(website_item.get("lt_product_page_type")) != PAGE_TYPE_SIMPLE:
        return {}
    if _text(website_item.get("lt_commerce_lane")) != COMMERCE_CHECKOUT:
        return {}

    options = variant_options if variant_options is not None else _variant_options(item_code)
    return {
        "image": variant_image,
        "label": item.get("item_name") or item_code,
        "media_role": "variant_item_image",
        "source": "item_image",
        "approved_for_customer": True,
        "render_policy": "show",
        "variant_item": item_code,
        "conditions": [
            {
                "group": row.get("attribute"),
                "value": row.get("attribute_value"),
            }
            for row in options
            if row.get("attribute") and row.get("attribute_value")
        ],
    }


def held_variant_item_media_reason(*, item: dict[str, Any], website_item: dict[str, Any]) -> str:
    """Explain why an Item.image exists but is not customer-renderable."""
    item_code = _text(item.get("item_code"))
    variant_of = _text(item.get("variant_of"))
    website_item_code = _text(website_item.get("item_code"))
    variant_image = _text(item.get("image"))
    fallback_image = _text(website_item.get("website_image"))
    if not item_code or not variant_image or variant_image == fallback_image:
        return ""
    if not variant_of or variant_of != website_item_code:
        return "Variant image is not attached to this product's resolved variant."
    if _text(website_item.get("lt_product_page_type")) != PAGE_TYPE_SIMPLE:
        return "Variant image is held until a Product Setup media rule approves this complex product image."
    if _text(website_item.get("lt_commerce_lane")) != COMMERCE_CHECKOUT:
        return "Variant image is held until this product is approved for checkout display."
    return ""


def _website_item_for_media(website_item_code: str) -> dict[str, Any] | None:
    fields = ["item_code", "web_item_name", "website_image"]
    meta = frappe.get_meta("Website Item")
    for fieldname in ("lt_product_page_type", "lt_commerce_lane"):
        if meta.has_field(fieldname):
            fields.append(fieldname)
    return frappe.db.get_value(
        "Website Item",
        {"item_code": website_item_code, "published": 1},
        fields,
        as_dict=True,
    )


def _variant_options(item_code: str) -> list[dict[str, str]]:
    rows = frappe.get_all(
        "Item Variant Attribute",
        filters={"parent": item_code},
        fields=["attribute", "attribute_value"],
        order_by="idx asc",
    )
    return [
        {
            "attribute": row.get("attribute"),
            "attribute_value": row.get("attribute_value"),
        }
        for row in rows
        if row.get("attribute") and row.get("attribute_value")
    ]


def _text(value: Any) -> str:
    return str(value or "").strip()
