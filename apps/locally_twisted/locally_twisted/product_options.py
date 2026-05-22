"""Product option helpers for customer-facing Webshop templates."""

from __future__ import annotations

import json
from functools import lru_cache
import os
from pathlib import Path
from typing import Any

import frappe
from frappe.utils import flt, fmt_money

from locally_twisted.catalog_contract.axis_projection import live_variant_axis_projection
from locally_twisted.catalog_contract.pattern_mapper import build_product_pattern_contract as build_source_pattern_contract
from locally_twisted.catalog_contract.product_page_architecture_contract import (
    build_product_page_architecture_contract,
)
from locally_twisted.catalog_variant_rules import required_variant_attribute_names
from locally_twisted.catalog_contract.color_rules import grouped_colors, is_balloon_color_axis
from locally_twisted.catalog_contract.product_pattern_contract import LINE_CONFIGURATION_FIELDS
from locally_twisted.commerce_rules import PRICE_LIST
from locally_twisted.product_page_runtime import (
    checkout_add_on_contracts_for_item,
    product_page_contract_for_website_item,
)
from locally_twisted.product_setup_runtime import get_product_setup_schema_json
from webshop.webshop.variant_selector.utils import get_attributes_and_values


def get_variant_attribute_options(item_code: str | None) -> list[dict[str, Any]]:
    """Return Webshop's prepared variant attribute/value data for a template item."""
    if not item_code:
        return []
    rows = get_attributes_and_values(item_code) or []
    required_names = set(required_variant_attribute_names(row.get("attribute") for row in rows))
    source_axes = _source_axis_contracts_by_name(item_code)
    filtered = []
    for row in rows:
        attribute = str(row.get("attribute") or "").strip()
        if attribute not in required_names:
            continue
        projection = live_variant_axis_projection(
            attribute=attribute,
            values=[_option_value(value) for value in row.get("values") or []],
            source_axis_contract=source_axes.get(attribute),
        )
        filtered.append(
            {
                **row,
                "lt_axis_role": projection["role"],
                "lt_selector_type": projection["selector_type"],
                "lt_payload_target": "color_recipes"
                if projection["role"] == "customization" and is_balloon_color_axis(attribute)
                else "selected_options",
                "lt_allows_multiple_values": projection["allows_multiple_values"],
                "lt_axis_notes": projection["notes"],
            }
        )
    return filtered


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
    for key, spec in checkout_add_on_contracts_for_item(item_code).items():
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
                "input_type": spec.get("input_type") or "number_text",
                "quantity_min": int(spec.get("quantity_min") or 0),
                "quantity_max": int(spec.get("quantity_max") or 10),
                "help": "Optional upgrade. Each selected number is priced separately.",
            }
        )
    return options


def is_balloon_color_attribute(attribute: str | None) -> bool:
    """Return whether an attribute should render as visual multi-select colors."""
    return is_balloon_color_axis(attribute)


def get_balloon_color_groups(values, axis_name: str | None = None, item_code: str | None = None) -> list[dict[str, Any]]:
    """Group high-cardinality balloon colors for drawer/accordion rendering."""
    clean_values: list[str] = []
    for value in values or []:
        if isinstance(value, dict):
            value = value.get("name") or value.get("attribute_value") or value.get("value")
        if value:
            clean_values.append(str(value))
    return grouped_colors(clean_values, axis_name=axis_name, item_code=item_code)


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


def get_product_page_architecture_context(item_code: str | None) -> dict[str, Any]:
    """Return backend-emitted product-page receiving architecture for templates.

    This is the live Webshop projection of the deeper source/ProductPattern
    contract. It gives the browser a generic contract shape without making the
    browser the authority for checkout eligibility, pricing, or document
    preservation.
    """

    item_code = str(item_code or "").strip()
    runtime = product_page_contract_for_website_item(item_code)
    commerce_lane = runtime.get("commerce_lane") or "needs_review"
    page_type = runtime.get("product_page_type") or "needs_review"
    axes = _live_architecture_axes(item_code)
    checkout_status = "checkout_ready" if commerce_lane == "checkout" else "lane_mapping_only"
    architecture = build_product_page_architecture_contract(
        {
            "schema_version": "lt-live-product-page-architecture-projection-v1",
            "slug": item_code,
            "item_code": item_code,
            "source_name": runtime.get("web_item_name") or item_code,
            "route": "",
            "current_page_type": page_type,
            "current_commerce_lane": commerce_lane,
            "axis_contracts": axes,
            "checkout_eligibility": {
                "status": checkout_status,
                "current_page_type": page_type,
                "current_commerce_lane": commerce_lane,
                "fail_loud_states": [],
                "required_work": [],
            },
            "order_preservation_contract": {
                "line_fields": LINE_CONFIGURATION_FIELDS,
                "summary_required": True,
                "json_required": True,
                "receipt_label_source": "custom_lt_configuration_summary/custom_lt_configuration_json",
                "add_on_line_detail_required": True,
                "color_recipe_detail_required": True,
            },
        }
    ).to_dict()
    architecture["live_projection_note"] = (
        "Template render hint only. Source/ProductPatternContract and server runtime "
        "remain authority for import, checkout eligibility, pricing, and persistence."
    )
    return architecture


def get_product_page_architecture_json(item_code: str | None) -> str:
    """Return HTML-safe JSON for the product-page architecture script tag."""

    text = json.dumps(
        get_product_page_architecture_context(item_code),
        sort_keys=True,
        default=str,
        ensure_ascii=False,
    )
    return (
        text.replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def _live_architecture_axes(item_code: str) -> list[dict[str, Any]]:
    axes: list[dict[str, Any]] = []
    for row in get_variant_attribute_options(item_code):
        attribute = str(row.get("attribute") or "").strip()
        if not attribute:
            continue
        values = [_option_value(value) for value in row.get("values") or []]
        values = [value for value in values if value]
        projection = live_variant_axis_projection(
            attribute=attribute,
            values=values,
            source_axis_contract=_source_axis_contracts_by_name(item_code).get(attribute),
        )
        axes.append(projection)
    for option in get_checkout_add_on_options(item_code):
        axes.append(
            {
                "name": option.get("label") or option.get("key"),
                "role": "add_on",
                "values": [],
                "selector_type": option.get("input_type") or "add_on_selector",
                "source": "erpnext_runtime",
                "status": "ready",
                "allows_multiple_values": False,
                "add_on_key": option.get("key"),
                "add_on_contract": {
                    "ready_for_checkout": True,
                    "item_code": option.get("item_code"),
                    "price_status": "ready",
                    "live_unit_price": option.get("unit_price"),
                    "quantity_min": option.get("quantity_min", 0),
                    "quantity_max": option.get("quantity_max", 10),
                    "receipt_label": option.get("label"),
                    "input_type": option.get("input_type"),
                },
            }
        )
    return axes


def _option_value(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("name") or value.get("attribute_value") or value.get("value") or "").strip()
    return str(value or "").strip()


@lru_cache(maxsize=256)
def _source_axis_contracts_by_name(item_code: str | None) -> dict[str, dict[str, Any]]:
    source_product = _source_product_for_item(item_code)
    if not source_product:
        return {}
    try:
        contract = build_source_pattern_contract(source_product).to_dict()
    except Exception:
        return {}
    return {
        str(axis.get("name") or "").strip(): axis
        for axis in contract.get("axis_contracts") or []
        if axis.get("name")
    }


@lru_cache(maxsize=1)
def _source_products_by_slug() -> dict[str, dict[str, Any]]:
    source = None
    for catalog_path in _source_catalog_paths():
        try:
            if catalog_path.exists():
                source = json.loads(catalog_path.read_text(encoding="utf-8"))
                break
        except Exception:
            continue
    if not source:
        return {}
    return {
        str(product.get("slug") or "").strip(): product
        for product in source.get("products") or []
        if product.get("slug")
    }


def _source_catalog_paths() -> tuple[Path, ...]:
    configured = []
    try:
        configured.append(frappe.conf.get("lt_source_catalog_path"))
    except Exception:
        pass
    configured.append(os.environ.get("LT_SOURCE_CATALOG_PATH"))
    paths = [Path(value) for value in configured if value]
    paths.append(Path("/tmp/lt-odoo-live-catalog.json"))
    paths.append(Path(__file__).resolve().parent / "seed" / "_data" / "catalog.json")
    try:
        app_root = Path(frappe.get_app_path("locally_twisted")).parent
        paths.append(Path(frappe.get_app_path("locally_twisted")) / "seed" / "_data" / "catalog.json")
        paths.append(app_root / "_resources" / "odoo-live" / "catalog.json")
    except Exception:
        pass
    return tuple(dict.fromkeys(paths))


def _source_product_for_item(item_code: str | None) -> dict[str, Any] | None:
    item_code = str(item_code or "").strip()
    if not item_code:
        return None
    return _source_products_by_slug().get(item_code)
