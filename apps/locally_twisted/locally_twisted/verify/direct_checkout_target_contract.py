"""Verify owner-required direct-checkout product targets after catalog import."""

from __future__ import annotations

from typing import Any

import frappe
from erpnext.controllers.item_variant import get_variant

from locally_twisted.api.cart import resolve_cart_item_for_sale_with_reason
from locally_twisted.catalog_contract.color_rules import is_balloon_color_axis
from locally_twisted.catalog_import_subset import OWNER_DIRECT_CHECKOUT_SLUGS, OWNER_EXPLICIT_EXCLUDED_SLUGS
from locally_twisted.commerce_rules import PRICE_LIST
from locally_twisted.product_page_runtime import (
    WEBSITE_ITEM_COMMERCE_LANE_FIELD,
    WEBSITE_ITEM_PAGE_TYPE_FIELD,
    product_page_contract_for_website_item,
)
from webshop.webshop.variant_selector.utils import get_attributes_and_values


def run() -> dict[str, Any]:
    rows = [_direct_checkout_status(slug) for slug in sorted(OWNER_DIRECT_CHECKOUT_SLUGS)]
    classic_rows = [_classic_status(slug) for slug in sorted(OWNER_EXPLICIT_EXCLUDED_SLUGS)]
    failures = []
    for row in rows:
        if row["runtime"].get("commerce_lane") != "checkout":
            failures.append(f"{row['slug']} runtime commerce_lane is {row['runtime'].get('commerce_lane')}, expected checkout")
        if not row.get("candidate_item_code"):
            failures.append(f"{row['slug']} could not resolve a candidate variant")
        if not row.get("candidate_price"):
            failures.append(f"{row['slug']} candidate variant has no Standard Selling Item Price")
        if not row.get("cart_resolver_ok"):
            failures.append(
                f"{row['slug']} cart resolver rejected candidate variant: {row.get('cart_resolver_reason')}"
            )
    for row in classic_rows:
        if row["runtime"].get("commerce_lane") == "checkout":
            failures.append(f"{row['slug']} is an explicit Classic exclusion but resolved to checkout")

    return {
        "ok": not failures,
        "direct_checkout_targets": rows,
        "explicit_classic_exclusions": classic_rows,
        "failures": failures,
    }


def _direct_checkout_status(slug: str) -> dict[str, Any]:
    website_item = _website_item(slug)
    attrs = get_attributes_and_values(slug) or []
    selection = _first_selection(attrs)
    candidate = get_variant(slug, args=selection) if selection else None
    price = None
    cart_resolution = None
    cart_reason = None
    if candidate:
        price = frappe.db.get_value(
            "Item Price",
            {"item_code": candidate, "price_list": PRICE_LIST, "selling": 1},
            "price_list_rate",
        )
        cart_resolution, cart_reason = resolve_cart_item_for_sale_with_reason(
            candidate,
            configuration=_checkout_configuration(slug=slug, item_code=candidate, selection=selection),
        )
    return {
        "slug": slug,
        "website_item": website_item,
        "runtime": product_page_contract_for_website_item(slug),
        "attribute_selection": selection,
        "candidate_item_code": candidate,
        "candidate_price": float(price) if price is not None else None,
        "cart_resolver_ok": bool(cart_resolution),
        "cart_resolver_reason": cart_reason,
        "attribute_count": len(attrs),
    }


def _classic_status(slug: str) -> dict[str, Any]:
    return {
        "slug": slug,
        "website_item": _website_item(slug),
        "runtime": product_page_contract_for_website_item(slug),
    }


def _website_item(slug: str) -> dict[str, Any]:
    return frappe.db.get_value(
        "Website Item",
        {"item_code": slug},
        [
            "name",
            "item_code",
            "route",
            "published",
            WEBSITE_ITEM_PAGE_TYPE_FIELD,
            WEBSITE_ITEM_COMMERCE_LANE_FIELD,
        ],
        as_dict=True,
    ) or {}


def _first_selection(attrs: list[dict[str, Any]]) -> dict[str, str]:
    selection: dict[str, str] = {}
    for row in attrs:
        values = row.get("values") or []
        if not values:
            continue
        value = values[0]
        if isinstance(value, dict):
            value = value.get("name") or value.get("attribute_value") or value.get("value")
        if value:
            selection[str(row.get("attribute"))] = str(value)
    return selection


def _checkout_configuration(*, slug: str, item_code: str, selection: dict[str, str]) -> dict[str, Any]:
    selected_options = {
        axis: value
        for axis, value in selection.items()
        if not is_balloon_color_axis(axis)
    }
    color_recipes = [
        {
            "axis": axis,
            "label": axis,
            "values": [value],
        }
        for axis, value in selection.items()
        if is_balloon_color_axis(axis)
    ]
    return {
        "schema_version": "lt-product-config-v1",
        "item_code": item_code,
        "website_item_code": slug,
        "selected_options": selected_options,
        "color_recipes": color_recipes,
        "add_ons": [],
        "customizations": [],
    }
