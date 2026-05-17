"""Public helpers for variant-aware product media."""
from __future__ import annotations

from typing import Any

import frappe
from frappe import _

from locally_twisted.product_setup_runtime import (
    product_setup_schema_for_website_item,
    resolve_product_setup_media,
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


@frappe.whitelist(allow_guest=True)
def get_variant_media(item_code: str, template_item_code: str | None = None, configuration: Any = None) -> dict:
    """Return the storefront image for an Item or variant Item.

    Variant Items are sellable rows, while the Website Item usually lives on
    the template. This method keeps the template image as fallback until a
    source-backed media role marks a variant image as approved for rendering.
    """
    item_code = (item_code or "").strip()
    template_item_code = (template_item_code or "").strip() or None
    if not item_code:
        frappe.throw(_("Please choose a product option first."), frappe.ValidationError)

    item = frappe.db.get_value(
        "Item",
        {"item_code": item_code, "disabled": 0},
        ["item_code", "item_name", "variant_of", "image"],
        as_dict=True,
    )
    if not item:
        frappe.throw(_("Tiny snag: this item is no longer available. Please choose another option."), frappe.ValidationError)

    website_item_code = item.get("variant_of") or item["item_code"]
    if template_item_code and website_item_code != template_item_code:
        frappe.throw(_("Tiny snag: that option does not match this product. Please choose again."), frappe.ValidationError)

    website_item = frappe.db.get_value(
        "Website Item",
        {"item_code": website_item_code, "published": 1},
        ["item_code", "web_item_name", "website_image", "route"],
        as_dict=True,
    )
    if not website_item:
        frappe.throw(_("Tiny snag: this product is not available right now. Please choose another option."), frappe.ValidationError)

    fallback_image = website_item.get("website_image") or None
    variant_image = item.get("image") or None
    setup_schema = product_setup_schema_for_website_item(website_item["item_code"])
    setup_media = resolve_product_setup_media(
        setup_schema,
        variant_item_code=item["item_code"],
        configuration=configuration,
    )
    approved_variant_image = setup_media.get("image") if setup_media else None
    image = approved_variant_image or fallback_image
    held_back_variant_image = bool(variant_image and variant_image != fallback_image)
    hold_reason = (
        "Variant image is held until source media classification approves the variant_image role."
        if held_back_variant_image
        else ""
    )

    return {
        "item_code": item["item_code"],
        "template_item_code": website_item["item_code"],
        "image": image,
        "fallback_image": fallback_image,
        "has_variant_image": bool(approved_variant_image and approved_variant_image != fallback_image),
        "held_back_variant_image": held_back_variant_image,
        "held_back_media_role": "ignored_artifact" if held_back_variant_image else "",
        "held_back_render_policy": "hold_back" if held_back_variant_image else "",
        "hold_reason": hold_reason,
        "role_reason": hold_reason,
        "media_role": "product_setup_media_rule" if approved_variant_image else "primary",
        "product_setup_media_rule": setup_media or {},
        "alt": item.get("item_name") or website_item.get("web_item_name") or item["item_code"],
        "route": website_item.get("route"),
        "variant_options": _variant_options(item["item_code"]) if item.get("variant_of") else [],
    }
