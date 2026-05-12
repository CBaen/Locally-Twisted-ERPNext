"""Product option helpers for customer-facing Webshop templates."""

from __future__ import annotations

from typing import Any

import frappe
from frappe.utils import flt, fmt_money

from locally_twisted.catalog_variant_rules import required_variant_attribute_names
from locally_twisted.catalog_contract.color_rules import grouped_colors, is_balloon_color_axis
from locally_twisted.commerce_rules import PRICE_LIST
from locally_twisted.product_page_runtime import ADD_ON_ITEM_CONTRACTS, product_page_contract_for_website_item
from webshop.webshop.variant_selector.utils import get_attributes_and_values


def get_variant_attribute_options(item_code: str | None) -> list[dict[str, Any]]:
    """Return Webshop's prepared variant attribute/value data for a template item."""
    if not item_code:
        return []
    rows = get_attributes_and_values(item_code) or []
    required_names = set(required_variant_attribute_names(row.get("attribute") for row in rows))
    return [row for row in rows if row.get("attribute") in required_names]


def get_variant_starting_price(item_code: str | None, price_list: str = PRICE_LIST) -> dict[str, Any] | None:
    """Return the lowest public selling price for a variant template."""
    if not item_code:
        return None

    rows = frappe.db.sql(
        """
        SELECT
            ip.price_list_rate,
            ip.currency
        FROM `tabItem` item
        JOIN `tabItem Price` ip
            ON ip.item_code = item.item_code
        WHERE item.variant_of = %s
          AND item.disabled = 0
          AND ip.price_list = %s
          AND ip.selling = 1
          AND ip.price_list_rate IS NOT NULL
        ORDER BY ip.price_list_rate ASC, item.item_code ASC
        LIMIT 1
        """,
        (item_code, price_list),
        as_dict=True,
    )
    if not rows:
        return None

    row = rows[0]
    rate = flt(row.get("price_list_rate"))
    currency = row.get("currency") or frappe.db.get_default("currency")
    formatted = fmt_money(rate, currency=currency)
    return {
        "price_list_rate": rate,
        "currency": currency,
        "formatted_price": formatted,
        "formatted_price_sales_uom": formatted,
    }


def get_variant_starting_price_display(item_code: str | None, price_list: str = PRICE_LIST) -> str:
    """Return display text for the lowest priced variant on a template."""
    price = get_variant_starting_price(item_code, price_list=price_list)
    if not price:
        return ""
    return f"from {price['formatted_price']}"


def apply_variant_starting_price(item: dict[str, Any], price_list: str = PRICE_LIST) -> dict[str, Any]:
    """Mutate a Website Item row so variant templates show a public starting price."""
    if not item or not item.get("has_variants"):
        return item

    price = get_variant_starting_price(item.get("item_code"), price_list=price_list)
    if not price:
        return item

    item["price_list_rate"] = price["price_list_rate"]
    item["currency"] = price["currency"]
    item["formatted_price"] = f"from {price['formatted_price']}"
    item["formatted_price_sales_uom"] = item["formatted_price"]
    item["price_is_from"] = True
    return item


def get_checkout_add_on_options(item_code: str | None, price_list: str = PRICE_LIST) -> list[dict[str, Any]]:
    """Return approved checkout add-ons for this product page template."""
    item_code = str(item_code or "").strip()
    if not item_code:
        return []
    contract = product_page_contract_for_website_item(item_code)
    if contract.get("commerce_lane") != "checkout":
        return []

    options = []
    for key, spec in ADD_ON_ITEM_CONTRACTS.items():
        eligible = tuple(spec.get("eligible_website_item_codes") or ())
        if eligible and item_code not in eligible:
            continue
        rate = frappe.db.get_value(
            "Item Price",
            {"item_code": spec["item_code"], "price_list": price_list, "selling": 1},
            "price_list_rate",
        )
        if rate in (None, ""):
            continue
        rate = flt(rate)
        options.append(
            {
                "key": key,
                "label": spec["label"],
                "item_code": spec["item_code"],
                "unit_price": rate,
                "formatted_unit_price": fmt_money(rate, currency=frappe.db.get_default("currency") or "USD"),
                "input_type": "number_text",
                "help": "Optional upgrade. Each selected number is priced separately.",
            }
        )
    return options


def is_balloon_color_attribute(attribute: str | None) -> bool:
    """Return whether an attribute should render as visual multi-select colors."""
    return is_balloon_color_axis(attribute)


def get_balloon_color_groups(values) -> list[dict[str, Any]]:
    """Group high-cardinality balloon colors for drawer/accordion rendering."""
    clean_values: list[str] = []
    for value in values or []:
        if isinstance(value, dict):
            value = value.get("name") or value.get("attribute_value") or value.get("value")
        if value:
            clean_values.append(str(value))
    return grouped_colors(clean_values)


def get_product_gallery_slides(item_code: str | None, primary_image: str | None = None, limit: int = 12) -> list[dict[str, str]]:
    """Return source-approved product gallery slides for a product template.

    Website Slideshow rows are the backend-approved gallery path. When no
    slideshow is supplied by Webshop, this fallback returns only the primary
    image. Live variant Item.image rows are intentionally held back here until
    the source media packet classifies them as `gallery` or `variant_image`.
    """
    if not item_code:
        return []

    seen: set[str] = set()
    slides: list[dict[str, str]] = []

    def add_slide(image: str | None, heading: str) -> None:
        image = str(image or "").strip()
        if not image or image in seen or len(slides) >= limit:
            return
        seen.add(image)
        slides.append({"image": image, "heading": heading})

    add_slide(primary_image, "Main product photo")
    return slides


def get_product_page_runtime_context(item_code: str | None) -> dict[str, Any]:
    """Return product-page type context for Jinja product templates."""
    contract = product_page_contract_for_website_item(item_code)
    product_page_type = contract.get("product_page_type") or "needs_review"
    commerce_lane = contract.get("commerce_lane") or "needs_review"
    return {
        "product_page_type": product_page_type,
        "commerce_lane": commerce_lane,
        "is_quote_first": commerce_lane == "quote_first",
        "is_ready_to_order": commerce_lane == "checkout",
        "is_complex_custom": product_page_type == "complex_custom_product",
        "is_simple_product": product_page_type == "simple_product",
        "needs_review": product_page_type == "needs_review" or commerce_lane == "needs_review",
    }
