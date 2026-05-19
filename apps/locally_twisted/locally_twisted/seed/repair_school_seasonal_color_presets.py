"""Repair school/seasonal color products into preset checkout or quote request.

Run in-process:
    bench --site frontend execute locally_twisted.seed.repair_school_seasonal_color_presets.execute

This is idempotent. It keeps the two graduation products checkout-ready with
college color preset variants, moves high-cardinality color products to quote
request, and rebuilds Webshop's variant cache for touched templates.
"""

from __future__ import annotations

import json
from typing import Any

import frappe

from locally_twisted.color_preset_rules import (
    COLLEGE_COLOR_PRESET_ATTRIBUTE,
    COLLEGE_COLOR_PRESETS,
    COLLEGE_PRESET_LABELS,
    QUOTE_REQUEST_COLOR_PRODUCTS,
)
from locally_twisted.commerce_rules import PRICE_LIST
from locally_twisted.product_page_runtime import (
    WEBSITE_ITEM_COMMERCE_LANE_FIELD,
    WEBSITE_ITEM_PAGE_TYPE_FIELD,
)


GRADUATION_STANDS_ATTRIBUTE = "Graduation stands"
GRADUATION_STANDS_TEMPLATE = "6-graduation-stands"
GRADUATION_GRAB_TEMPLATE = "graduation-grab-n-go"


def execute() -> str:
    frappe.flags.ignore_permissions = True
    summary = {
        "college_attribute": _ensure_college_color_attribute(),
        "graduation_products": [
            _repair_graduation_grab_n_go(),
            _repair_graduation_stands(),
        ],
        "quote_request_products": _repair_quote_request_products(),
    }
    frappe.db.commit()
    return json.dumps(summary, indent=2, sort_keys=True)


def _ensure_college_color_attribute() -> dict[str, Any]:
    if frappe.db.exists("Item Attribute", COLLEGE_COLOR_PRESET_ATTRIBUTE):
        doc = frappe.get_doc("Item Attribute", COLLEGE_COLOR_PRESET_ATTRIBUTE)
    else:
        doc = frappe.get_doc(
            {
                "doctype": "Item Attribute",
                "attribute_name": COLLEGE_COLOR_PRESET_ATTRIBUTE,
                "numeric_values": 0,
                "item_attribute_values": [],
            }
        )

    existing = {
        row.attribute_value: row
        for row in (doc.get("item_attribute_values") or [])
        if row.attribute_value
    }
    added = []
    for preset in COLLEGE_COLOR_PRESETS:
        row = existing.get(preset.label)
        if row:
            if row.abbr != preset.abbr:
                row.abbr = preset.abbr
            continue
        doc.append(
            "item_attribute_values",
            {
                "attribute_value": preset.label,
                "abbr": preset.abbr,
            },
        )
        added.append(preset.label)

    if doc.is_new():
        doc.insert(ignore_permissions=True)
    else:
        doc.save(ignore_permissions=True)

    return {
        "name": COLLEGE_COLOR_PRESET_ATTRIBUTE,
        "values": list(COLLEGE_PRESET_LABELS),
        "added_values": added,
    }


def _set_template_required_attrs(template_code: str, required_attrs: list[str]) -> None:
    frappe.db.delete(
        "Item Variant Attribute",
        {
            "parent": template_code,
            "parenttype": "Item",
            "parentfield": "attributes",
        },
    )
    for idx, attr in enumerate(required_attrs, 1):
        frappe.get_doc(
            {
                "doctype": "Item Variant Attribute",
                "parent": template_code,
                "parenttype": "Item",
                "parentfield": "attributes",
                "idx": idx,
                "attribute": attr,
            }
        ).insert(ignore_permissions=True)
    frappe.db.set_value("Item", template_code, "has_variants", 1, update_modified=False)
    frappe.db.set_value("Item", template_code, "variant_based_on", "Item Attribute", update_modified=False)


def _first_active_price(template_code: str) -> float | None:
    row = frappe.db.sql(
        """
        SELECT ip.price_list_rate
        FROM `tabItem` item
        JOIN `tabItem Price` ip
          ON ip.item_code = item.name
         AND ip.price_list = %s
         AND ip.selling = 1
        WHERE item.variant_of = %s
          AND item.disabled = 0
          AND ip.price_list_rate IS NOT NULL
        ORDER BY ip.price_list_rate ASC, item.name ASC
        LIMIT 1
        """,
        (PRICE_LIST, template_code),
        as_dict=True,
    )
    if not row:
        return None
    return row[0].price_list_rate


def _upsert_item_price(item_code: str, rate: float | None) -> None:
    if rate is None:
        return
    existing = frappe.db.exists(
        "Item Price",
        {"item_code": item_code, "price_list": PRICE_LIST, "selling": 1},
    )
    if existing:
        frappe.db.set_value("Item Price", existing, "price_list_rate", rate)
        return
    frappe.get_doc(
        {
            "doctype": "Item Price",
            "item_code": item_code,
            "price_list": PRICE_LIST,
            "price_list_rate": rate,
            "currency": "USD",
            "selling": 1,
        }
    ).insert(ignore_permissions=True)


def _find_or_create_variant(template_code: str, combo: dict[str, str]) -> str:
    from erpnext.controllers.item_variant import create_variant, get_variant

    existing = get_variant(template_code, args=combo)
    if existing:
        frappe.db.set_value("Item", existing, "disabled", 0, update_modified=False)
        return existing

    variant = create_variant(template_code, args=combo)
    variant.insert(ignore_permissions=True)
    return variant.name


def _disable_variants_except(template_code: str, keep_codes: set[str]) -> dict[str, int]:
    rows = frappe.get_all(
        "Item",
        filters={"variant_of": template_code},
        fields=["name", "disabled"],
        limit_page_length=0,
    )
    disabled_now = 0
    active_after = 0
    for row in rows:
        if row.name in keep_codes:
            if row.disabled:
                frappe.db.set_value("Item", row.name, "disabled", 0, update_modified=False)
            active_after += 1
            continue
        if not row.disabled:
            frappe.db.set_value("Item", row.name, "disabled", 1, update_modified=False)
            disabled_now += 1
    return {"disabled_now": disabled_now, "active_after": active_after}


def _repair_graduation_grab_n_go() -> dict[str, Any]:
    _set_template_required_attrs(GRADUATION_GRAB_TEMPLATE, [COLLEGE_COLOR_PRESET_ATTRIBUTE])
    rate = _first_active_price(GRADUATION_GRAB_TEMPLATE)
    created_or_reused = []
    for preset in COLLEGE_COLOR_PRESETS:
        code = _find_or_create_variant(
            GRADUATION_GRAB_TEMPLATE,
            {COLLEGE_COLOR_PRESET_ATTRIBUTE: preset.label},
        )
        _upsert_item_price(code, rate)
        created_or_reused.append(code)
    stale = _disable_variants_except(GRADUATION_GRAB_TEMPLATE, set(created_or_reused))
    _set_website_item_contract(GRADUATION_GRAB_TEMPLATE, "simple_product", "checkout")
    _rebuild_variant_cache(GRADUATION_GRAB_TEMPLATE)
    return {
        "template": GRADUATION_GRAB_TEMPLATE,
        "required_attrs": [COLLEGE_COLOR_PRESET_ATTRIBUTE],
        "preset_variants": created_or_reused,
        "price_preserved": rate,
        **stale,
    }


def _graduation_stands_prices() -> dict[str, float | None]:
    prices: dict[str, float | None] = {}
    rows = frappe.db.sql(
        """
        SELECT item.name, iva.attribute_value, ip.price_list_rate
        FROM `tabItem` item
        JOIN `tabItem Variant Attribute` iva
          ON iva.parent = item.name
         AND iva.attribute = %s
        LEFT JOIN `tabItem Price` ip
          ON ip.item_code = item.name
         AND ip.price_list = %s
         AND ip.selling = 1
        WHERE item.variant_of = %s
        ORDER BY item.disabled ASC, item.name ASC
        """,
        (GRADUATION_STANDS_ATTRIBUTE, PRICE_LIST, GRADUATION_STANDS_TEMPLATE),
        as_dict=True,
    )
    for row in rows:
        if row.attribute_value not in prices and row.price_list_rate is not None:
            prices[row.attribute_value] = row.price_list_rate
    return prices


def _graduation_stands_values() -> list[str]:
    values = frappe.get_all(
        "Item Attribute Value",
        filters={"parent": GRADUATION_STANDS_ATTRIBUTE},
        pluck="attribute_value",
        order_by="idx asc",
    )
    return [str(value) for value in values if value]


def _repair_graduation_stands() -> dict[str, Any]:
    values = _graduation_stands_values()
    prices = _graduation_stands_prices()
    fallback_rate = _first_active_price(GRADUATION_STANDS_TEMPLATE)
    _set_template_required_attrs(
        GRADUATION_STANDS_TEMPLATE,
        [GRADUATION_STANDS_ATTRIBUTE, COLLEGE_COLOR_PRESET_ATTRIBUTE],
    )
    created_or_reused = []
    for design in values:
        for preset in COLLEGE_COLOR_PRESETS:
            combo = {
                GRADUATION_STANDS_ATTRIBUTE: design,
                COLLEGE_COLOR_PRESET_ATTRIBUTE: preset.label,
            }
            code = _find_or_create_variant(GRADUATION_STANDS_TEMPLATE, combo)
            _upsert_item_price(code, prices.get(design, fallback_rate))
            created_or_reused.append(code)
    stale = _disable_variants_except(GRADUATION_STANDS_TEMPLATE, set(created_or_reused))
    _set_website_item_contract(GRADUATION_STANDS_TEMPLATE, "simple_product", "checkout")
    _rebuild_variant_cache(GRADUATION_STANDS_TEMPLATE)
    return {
        "template": GRADUATION_STANDS_TEMPLATE,
        "required_attrs": [GRADUATION_STANDS_ATTRIBUTE, COLLEGE_COLOR_PRESET_ATTRIBUTE],
        "design_values": values,
        "preset_variants": created_or_reused,
        "prices_preserved": prices,
        **stale,
    }


def _set_website_item_contract(item_code: str, product_page_type: str, commerce_lane: str) -> dict[str, Any]:
    meta = frappe.get_meta("Website Item")
    fields = {}
    if meta.has_field(WEBSITE_ITEM_PAGE_TYPE_FIELD):
        fields[WEBSITE_ITEM_PAGE_TYPE_FIELD] = product_page_type
    if meta.has_field(WEBSITE_ITEM_COMMERCE_LANE_FIELD):
        fields[WEBSITE_ITEM_COMMERCE_LANE_FIELD] = commerce_lane
    name = frappe.db.exists("Website Item", {"item_code": item_code})
    if name and fields:
        frappe.db.set_value("Website Item", name, dict(fields))
    return {"item_code": item_code, "name": name, "fields": fields}


def _repair_quote_request_products() -> list[dict[str, Any]]:
    rows = []
    for item_code in sorted(QUOTE_REQUEST_COLOR_PRODUCTS):
        rows.append(_set_website_item_contract(item_code, "complex_custom_product", "quote_first"))
    return rows


def _rebuild_variant_cache(template_code: str) -> None:
    try:
        from webshop.webshop.variant_selector.item_variants_cache import ItemVariantsCacheManager

        ItemVariantsCacheManager(template_code).build_cache()
    except Exception:
        frappe.log_error(frappe.get_traceback(), "LT school color preset variant cache rebuild failed")
