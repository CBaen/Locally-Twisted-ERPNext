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
from locally_twisted.product_page_runtime import (
    LINE_FIELDNAMES,
    cart_line_key,
    normalize_client_configuration,
    product_page_contract_for_website_item,
    sales_order_add_on_lines,
)
from locally_twisted.product_setup_runtime import (
    product_setup_schema_for_website_item,
    resolve_product_setup_content,
    resolve_product_setup_media,
)
from locally_twisted.product_variant_media import approved_variant_item_media_for_codes


MAX_CART_LINES = 50
MAX_QTY_PER_LINE = 99
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
        return _("Tiny snag: this design needs a quote before checkout so details, timing, and pricing stay together.")
    if reason == "choose_options":
        return _("Please choose this item's options before adding it to cart.")
    if reason == "unpriced":
        return _("Tiny snag: this item is missing its checkout price. Please remove it or call (801) 285-0860.")
    return _("Tiny snag: this item is no longer available. Please remove it from your cart.")


def _resolve_cart_item_for_sale(item_code, configuration=None):
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

    product_page_contract = product_page_contract_for_website_item(website_item["item_code"])
    product_commerce_lane = product_page_contract.get("commerce_lane")
    checkout_lane = (
        "retail_checkout"
        if product_commerce_lane == "checkout"
        else checkout_lane_for_item_group(website_item.get("item_group"))
    )
    if product_commerce_lane != "checkout":
        return None, "quote_required"
    normalized_configuration = normalize_client_configuration(configuration)

    rate = frappe.db.get_value(
        "Item Price",
        {"item_code": item["item_code"], "price_list": PRICE_LIST, "selling": 1},
        ["price_list_rate"],
    )
    if not rate:
        return None, "unpriced"

    selected_context = _selected_product_setup_context(
        website_item_code=website_item["item_code"],
        variant_item_code=item["item_code"],
        configuration=normalized_configuration,
    )
    selected_media = selected_context.get("selected_media") or {}
    selected_content = selected_context.get("selected_content") or {}
    display_name = (
        selected_content.get("display_title")
        or website_item.get("web_item_name")
        or item.get("item_name")
        or item["item_code"]
    )

    return {
        "item_code": item["item_code"],
        "website_item_code": website_item["item_code"],
        "web_item_name": display_name,
        "website_image": selected_media.get("image") or item.get("image") or website_item.get("website_image") or None,
        "route": website_item.get("route") or ("shop/" + website_item["item_code"]),
        "short_description": website_item.get("short_description") or None,
        "item_group": website_item.get("item_group"),
        "checkout_lane": checkout_lane,
        "product_commerce_lane": product_commerce_lane,
        "product_page_type": product_page_contract.get("product_page_type"),
        "configuration": normalized_configuration,
        "selected_media": selected_media,
        "selected_content": selected_content,
        "price_list_rate": flt(rate),
        "available": True,
        "is_variant": bool(item.get("variant_of")),
        "variant_options": _variant_options(item["item_code"]) if item.get("variant_of") else [],
    }, None


def client_cart_line_key_for_display(item_code, configuration=None, submitted_line_key=None):
    """Return the browser cart-line key to use for display matching.

    The server may enrich a valid configuration, especially color recipes, while
    resolving display rows. Cart and checkout pages still need to match the
    exact localStorage line the browser submitted.
    """
    computed_line_key = cart_line_key(item_code, configuration)
    if not isinstance(submitted_line_key, str):
        return computed_line_key

    clean_line_key = submitted_line_key.strip()
    if not clean_line_key:
        return computed_line_key

    has_configuration = isinstance(configuration, dict)
    if has_configuration and clean_line_key.startswith(f"{item_code}::"):
        return clean_line_key
    if not has_configuration and clean_line_key in {item_code, f"{item_code}::"}:
        return clean_line_key
    return computed_line_key


def resolve_cart_item_for_sale(item_code, raise_on_missing=True, configuration=None):
    """Return the server-trusted cart line for one purchasable Item code."""
    resolved, reason = _resolve_cart_item_for_sale(item_code, configuration=configuration)
    if resolved or not raise_on_missing:
        return resolved

    frappe.throw(_missing_message(reason), frappe.ValidationError)


def resolve_cart_item_for_sale_with_reason(item_code, configuration=None):
    """Return the server-trusted cart line plus the fail-loud reason."""
    return _resolve_cart_item_for_sale(item_code, configuration=configuration)


@frappe.whitelist(allow_guest=True, methods=["POST"])
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
            frappe.throw(
                _("Tiny snag: the cart details did not come through cleanly. Please refresh your cart and try again."),
                frappe.ValidationError,
            )

    if not isinstance(item_codes, list):
        frappe.throw(
            _("Tiny snag: the cart details did not come through cleanly. Please refresh your cart and try again."),
            frappe.ValidationError,
        )

    if len(item_codes) > MAX_CART_LINES:
        frappe.throw(
            _("Tiny snag: your cart has more than {0} items. Please remove a few items and try again.").format(MAX_CART_LINES),
            frappe.ValidationError,
        )

    # Preserve configured cart lines in order. Same SKU can appear more than
    # once when its option/add-on payload is different.
    clean_entries = []
    for entry in item_codes:
        configuration = None
        submitted_line_key = None
        qty = 1
        if isinstance(entry, dict):
            code = (entry.get("item_code") or "").strip()
            configuration = entry.get("configuration")
            submitted_line_key = entry.get("line_key")
            qty = _clean_qty(entry.get("qty") or 1)
        elif isinstance(entry, str):
            code = entry.strip()
        else:
            continue
        if not code:
            continue
        clean_entries.append(
            {
                "item_code": code,
                "qty": qty,
                "configuration": configuration,
                "cart_line_key": client_cart_line_key_for_display(code, configuration, submitted_line_key),
            }
        )

    if not clean_entries:
        return {"items": [], "missing": []}

    items = []
    missing = []
    for entry in clean_entries:
        row, reason = _resolve_cart_item_for_sale(entry["item_code"], configuration=entry.get("configuration"))
        if not row:
            missing.append(
                {
                    "item_code": entry["item_code"],
                    "cart_line_key": entry["cart_line_key"],
                    "reason": reason or "unavailable",
                }
            )
            continue
        row["cart_line_key"] = entry["cart_line_key"]
        row["qty"] = entry["qty"]
        row["display_lines"] = _cart_display_lines(row, entry["qty"])
        row["line_total"] = sum(flt(line.get("line_total") or 0) for line in row["display_lines"])
        row["add_on_total"] = sum(
            flt(line.get("line_total") or 0)
            for line in row["display_lines"]
            if line.get("is_add_on")
        )
        items.append(row)

    return {"items": items, "missing": missing}


def _clean_qty(value) -> int:
    try:
        qty = int(value)
    except (TypeError, ValueError):
        qty = 1
    return max(1, min(qty, MAX_QTY_PER_LINE))


def _selected_product_setup_context(
    *,
    website_item_code: str,
    variant_item_code: str,
    configuration: dict | None,
) -> dict:
    schema = product_setup_schema_for_website_item(website_item_code)
    setup_media = resolve_product_setup_media(
        schema,
        variant_item_code=variant_item_code,
        configuration=configuration,
    )
    setup_content = resolve_product_setup_content(
        schema,
        variant_item_code=variant_item_code,
        configuration=configuration,
    )
    return {
        "selected_media": setup_media
        or approved_variant_item_media_for_codes(
            variant_item_code=variant_item_code,
            website_item_code=website_item_code,
        ),
        "selected_content": setup_content or {},
    }


def _cart_display_lines(row: dict, qty: int) -> list[dict]:
    display_lines = [
        {
            "item_code": row["item_code"],
            "web_item_name": row.get("web_item_name") or row["item_code"],
            "display_label": row.get("web_item_name") or row["item_code"],
            "qty": qty,
            "price_list_rate": flt(row.get("price_list_rate") or 0),
            "line_total": flt(row.get("price_list_rate") or 0) * qty,
            "is_add_on": False,
        }
    ]
    for add_on_line in sales_order_add_on_lines(
        resolved_item=row,
        client_configuration=row.get("configuration"),
        parent_qty=qty,
    ):
        payload = _line_payload(add_on_line)
        value = payload.get("selected_value")
        display_label = payload.get("add_on_label") or add_on_line.get("item_name") or add_on_line["item_code"]
        if value not in (None, ""):
            display_label = f"{display_label}: {value}"
        display_lines.append(
            {
                "item_code": add_on_line["item_code"],
                "web_item_name": add_on_line.get("item_name") or add_on_line["item_code"],
                "display_label": display_label,
                "qty": int(add_on_line["qty"]),
                "price_list_rate": flt(add_on_line["rate"]),
                "line_total": flt(add_on_line["rate"]) * int(add_on_line["qty"]),
                "configuration_summary": add_on_line.get(LINE_FIELDNAMES["summary"]),
                "is_add_on": True,
            }
        )
    return display_lines


def _line_payload(line: dict) -> dict:
    try:
        return json.loads(line.get(LINE_FIELDNAMES["json"]) or "{}")
    except (TypeError, ValueError):
        return {}
