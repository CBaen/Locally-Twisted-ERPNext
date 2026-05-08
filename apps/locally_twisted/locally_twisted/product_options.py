"""Product option helpers for customer-facing Webshop templates."""

from __future__ import annotations

from typing import Any

import frappe
from frappe.utils import flt, fmt_money

from locally_twisted.catalog_variant_rules import required_variant_attribute_names
from locally_twisted.catalog_contract.color_rules import grouped_colors, is_balloon_color_axis
from locally_twisted.commerce_rules import PRICE_LIST
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
    """Return distinct product/variant image slides for a product template.

    Current ERPNext has no Website Item slideshows, but many imported variants
    already carry source alternate images. This helper exposes those as a
    temporary product-page gallery while the rebuild pipeline learns to create
    proper Website Slideshow records.
    """
    if not item_code:
        return []

    rows = frappe.db.sql(
        """
        SELECT item_code, item_name, image
        FROM `tabItem`
        WHERE disabled = 0
          AND image IS NOT NULL
          AND image != ''
          AND (item_code = %(item_code)s OR variant_of = %(item_code)s)
        ORDER BY CASE WHEN item_code = %(item_code)s THEN 0 ELSE 1 END, item_code ASC
        """,
        {"item_code": item_code},
        as_dict=True,
    )

    seen: set[str] = set()
    slides: list[dict[str, str]] = []

    def add_slide(image: str | None, heading: str) -> None:
        image = str(image or "").strip()
        if not image or image in seen or len(slides) >= limit:
            return
        seen.add(image)
        slides.append({"image": image, "heading": heading})

    add_slide(primary_image, "Main product photo")
    for row in rows:
        add_slide(row.get("image"), row.get("item_name") or row.get("item_code") or "Product photo")

    return slides
