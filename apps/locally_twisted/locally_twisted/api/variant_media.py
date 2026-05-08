"""Public helpers for variant-aware product media."""
from __future__ import annotations

import frappe
from frappe import _


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
def get_variant_media(item_code: str, template_item_code: str | None = None) -> dict:
    """Return the storefront image for an Item or variant Item.

    Variant Items are sellable rows, while the Website Item usually lives on
    the template. This method keeps the template image as fallback and only
    switches to the variant image when ERPNext has one on Item.image.
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
    image = variant_image or fallback_image

    return {
        "item_code": item["item_code"],
        "template_item_code": website_item["item_code"],
        "image": image,
        "fallback_image": fallback_image,
        "has_variant_image": bool(variant_image and variant_image != fallback_image),
        "alt": item.get("item_name") or website_item.get("web_item_name") or item["item_code"],
        "route": website_item.get("route"),
        "variant_options": _variant_options(item["item_code"]) if item.get("variant_of") else [],
    }
