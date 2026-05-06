"""LT guest cart — server-side helper endpoints.

The cart itself lives in localStorage on the client. This module exposes
ONE guest-allowed endpoint that the /cart page (and checkout summary) use
to render line details: name, image, route, price, availability.

The client sends a list of item_codes; we look up each one and return
only the items that are currently published and priced. Anything missing
gets reported back as "unavailable" so the client can drop it from the
local cart with a notice.

Security posture:
  - Untrusted input (item_codes from client). Treated as opaque strings,
    never interpolated into SQL — we use frappe ORM with parametric filters.
  - Hard cap on input list size (DoS guard).
  - Only fields safe for public display are returned. No unpublished items.
  - Pricing always comes from server-side Item Price; client-supplied prices
    are ignored at every layer.
"""
import json

import frappe
from frappe import _
from frappe.utils import flt

from locally_twisted.commerce_rules import checkout_lane_for_item_group


MAX_CART_LINES = 50
PRICE_LIST = "Standard Selling"


def _variant_options(item_code):
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


def _missing_message(reason):
    if reason == "quote_required":
        return _("Standard checkout needs a delivery quote for this request.")
    if reason == "choose_options":
        return _("Please choose this item's options before adding it to cart.")
    if reason == "unpriced":
        return _("This item doesn't have a price right now. Please remove it and try again.")
    return _("This item is no longer available. Please remove it and try again.")


def _resolve_cart_item_for_sale(item_code):
    """Resolve one client-provided item code into a purchasable cart line.

    Variants are the sellable Item rows, but only the template usually has a
    Website Item record. Resolve display fields from the parent Website Item
    while preserving the variant item_code for pricing and Sales Order lines.
    """
    item_code = (item_code or "").strip()
    if not item_code:
        return None, "unavailable"

    item = frappe.db.get_value(
        "Item",
        {"item_code": item_code, "disabled": 0},
        ["item_code", "item_name", "variant_of", "has_variants", "image"],
        as_dict=True,
    )
    if not item:
        return None, "unavailable"

    if item.get("has_variants"):
        return None, "choose_options"

    website_item_code = item.get("variant_of") or item["item_code"]
    website_item = frappe.db.get_value(
        "Website Item",
        {"item_code": website_item_code, "published": 1},
        [
            "item_code",
            "web_item_name",
            "website_image",
            "route",
            "short_description",
            "item_group",
        ],
        as_dict=True,
    )
    if not website_item:
        return None, "unavailable"

    checkout_lane = checkout_lane_for_item_group(website_item.get("item_group"))

    rate = frappe.db.get_value(
        "Item Price",
        {"item_code": item["item_code"], "price_list": PRICE_LIST, "selling": 1},
        ["price_list_rate"],
    )
    if not rate:
        return None, "unpriced"

    return {
        "item_code": item["item_code"],
        "website_item_code": website_item["item_code"],
        "web_item_name": website_item.get("web_item_name") or item.get("item_name") or item["item_code"],
        "website_image": item.get("image") or website_item.get("website_image") or None,
        "route": website_item.get("route") or ("shop/" + website_item["item_code"]),
        "short_description": website_item.get("short_description") or None,
        "item_group": website_item.get("item_group"),
        "checkout_lane": checkout_lane,
        "price_list_rate": flt(rate),
        "available": True,
        "is_variant": bool(item.get("variant_of")),
        "variant_options": _variant_options(item["item_code"]) if item.get("variant_of") else [],
    }, None


def resolve_cart_item_for_sale(item_code, raise_on_missing=True):
    """Return the server-trusted cart line for one purchasable Item code."""
    resolved, reason = _resolve_cart_item_for_sale(item_code)
    if resolved or not raise_on_missing:
        return resolved

    frappe.throw(_missing_message(reason), frappe.ValidationError)


@frappe.whitelist(allow_guest=True)
def get_cart_items(item_codes=None):
    """Return display details for a list of item_codes.

    Args:
        item_codes: JSON list of strings, or already-parsed list. The client
            (lt-guest-cart.js → /cart page) sends this as a JSON-encoded list.

    Returns:
        {
            "items": [
                {
                    "item_code": str,
                    "web_item_name": str,
                    "website_image": str | None,
                    "route": str,
                    "short_description": str | None,
                    "price_list_rate": float,
                    "available": True,
                },
                ...
            ],
            "missing": [
                {"item_code": str, "reason": str},
                ...
            ],
        }

    Loud-failure behavior: invalid input raises frappe.ValidationError so
    the caller surfaces a real error message instead of a half-rendered
    cart. Items that exist but can't be sold (unpublished, unpriced) are
    returned in `missing` rather than thrown — the client uses the list
    to drop them from localStorage with a soft notice.
    """
    if item_codes is None:
        return {"items": [], "missing": []}

    # Frappe whitelisted endpoints receive form-encoded values as strings,
    # so JSON-stringified arrays are the safe wire format.
    if isinstance(item_codes, str):
        try:
            item_codes = json.loads(item_codes)
        except (ValueError, TypeError):
            frappe.throw(_("Cart payload is not valid JSON."), frappe.ValidationError)

    if not isinstance(item_codes, list):
        frappe.throw(_("Cart payload must be a list of item codes."), frappe.ValidationError)

    if len(item_codes) > MAX_CART_LINES:
        frappe.throw(
            _("Cart exceeds the {0}-item limit.").format(MAX_CART_LINES),
            frappe.ValidationError,
        )

    # De-duplicate while preserving insertion order — matters for cart
    # display order.
    seen = set()
    clean_codes = []
    for code in item_codes:
        if not isinstance(code, str):
            continue
        code = code.strip()
        if not code or code in seen:
            continue
        seen.add(code)
        clean_codes.append(code)

    if not clean_codes:
        return {"items": [], "missing": []}

    items = []
    missing = []
    for code in clean_codes:
        row, reason = _resolve_cart_item_for_sale(code)
        if not row:
            missing.append({"item_code": code, "reason": reason or "unavailable"})
            continue
        items.append(row)

    return {"items": items, "missing": missing}
