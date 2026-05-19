"""Verify school/seasonal color preset ecommerce behavior."""

from __future__ import annotations

from typing import Any

import frappe

from locally_twisted.api.cart import resolve_cart_item_for_sale_with_reason
from locally_twisted.color_preset_rules import (
    COLLEGE_COLOR_PRESET_ATTRIBUTE,
    COLLEGE_PRESET_LABELS,
    GRADUATION_PRESET_CHECKOUT_PRODUCTS,
    QUOTE_REQUEST_COLOR_PRODUCTS,
    college_preset_values,
)
from locally_twisted.commerce_rules import PRICE_LIST
from locally_twisted.product_page_runtime import (
    WEBSITE_ITEM_COMMERCE_LANE_FIELD,
    WEBSITE_ITEM_PAGE_TYPE_FIELD,
)


GRADUATION_GRAB_TEMPLATE = "graduation-grab-n-go"
GRADUATION_STANDS_TEMPLATE = "6-graduation-stands"
GRADUATION_STANDS_ATTRIBUTE = "Graduation stands"
LATEX_COLOR_ATTRIBUTE = "latex colors"


def run() -> dict[str, Any]:
    failures: list[str] = []
    report: dict[str, Any] = {
        "college_presets": college_preset_values(),
        "quote_request_products": sorted(QUOTE_REQUEST_COLOR_PRODUCTS),
        "graduation_checkout_products": sorted(GRADUATION_PRESET_CHECKOUT_PRODUCTS),
    }

    meta = frappe.get_meta("Website Item")
    for fieldname in (WEBSITE_ITEM_PAGE_TYPE_FIELD, WEBSITE_ITEM_COMMERCE_LANE_FIELD):
        if not meta.has_field(fieldname):
            failures.append(f"Website Item missing field: {fieldname}")

    raw_checkout_color_axes = _checkout_products_with_raw_color_axes()
    report["raw_checkout_color_axes"] = raw_checkout_color_axes
    for row in raw_checkout_color_axes:
        failures.append(
            f"checkout product still exposes {row['color_count']} raw latex colors: {row['item_code']}"
        )

    quote_classification = _classification_rows(
        sorted(QUOTE_REQUEST_COLOR_PRODUCTS),
        product_page_type="complex_custom_product",
        commerce_lane="quote_first",
    )
    report["quote_classification"] = quote_classification
    failures.extend(row["failure"] for row in quote_classification if row.get("failure"))

    graduation_classification = _classification_rows(
        sorted(GRADUATION_PRESET_CHECKOUT_PRODUCTS),
        product_page_type="simple_product",
        commerce_lane="checkout",
    )
    report["graduation_classification"] = graduation_classification
    failures.extend(row["failure"] for row in graduation_classification if row.get("failure"))

    graduation_variants = [
        _graduation_template_report(
            GRADUATION_GRAB_TEMPLATE,
            expected_attrs=[COLLEGE_COLOR_PRESET_ATTRIBUTE],
            expected_combos=[{COLLEGE_COLOR_PRESET_ATTRIBUTE: label} for label in COLLEGE_PRESET_LABELS],
        ),
        _graduation_template_report(
            GRADUATION_STANDS_TEMPLATE,
            expected_attrs=[GRADUATION_STANDS_ATTRIBUTE, COLLEGE_COLOR_PRESET_ATTRIBUTE],
            expected_combos=[
                {
                    GRADUATION_STANDS_ATTRIBUTE: design,
                    COLLEGE_COLOR_PRESET_ATTRIBUTE: label,
                }
                for design in _item_attribute_values(GRADUATION_STANDS_ATTRIBUTE)
                for label in COLLEGE_PRESET_LABELS
            ],
        ),
    ]
    report["graduation_variants"] = graduation_variants
    failures.extend(failure for row in graduation_variants for failure in row["failures"])

    quote_cart_guards = _quote_cart_guards()
    report["quote_cart_guards"] = quote_cart_guards
    failures.extend(row["failure"] for row in quote_cart_guards if row.get("failure"))

    graduation_cart_guards = _graduation_cart_guards()
    report["graduation_cart_guards"] = graduation_cart_guards
    failures.extend(row["failure"] for row in graduation_cart_guards if row.get("failure"))

    report["ok"] = not failures
    report["failures"] = failures
    return report


def _classification_rows(item_codes: list[str], *, product_page_type: str, commerce_lane: str) -> list[dict[str, Any]]:
    rows = []
    for item_code in item_codes:
        row = frappe.db.get_value(
            "Website Item",
            {"item_code": item_code},
            [
                "name",
                "item_code",
                "web_item_name",
                WEBSITE_ITEM_PAGE_TYPE_FIELD,
                WEBSITE_ITEM_COMMERCE_LANE_FIELD,
            ],
            as_dict=True,
        )
        if not row:
            rows.append({"item_code": item_code, "failure": f"missing Website Item: {item_code}"})
            continue
        actual = {
            "product_page_type": row.get(WEBSITE_ITEM_PAGE_TYPE_FIELD),
            "commerce_lane": row.get(WEBSITE_ITEM_COMMERCE_LANE_FIELD),
        }
        expected = {
            "product_page_type": product_page_type,
            "commerce_lane": commerce_lane,
        }
        record = {
            "item_code": item_code,
            "website_item": row.get("name"),
            "actual": actual,
            "expected": expected,
            "matches": actual == expected,
        }
        if actual != expected:
            record["failure"] = f"{item_code} classification {actual} != {expected}"
        rows.append(record)
    return rows


def _checkout_products_with_raw_color_axes() -> list[dict[str, Any]]:
    return frappe.db.sql(
        f"""
        SELECT
            wi.item_code,
            COUNT(DISTINCT iva.attribute_value) AS color_count
        FROM `tabWebsite Item` wi
        JOIN `tabItem` item
          ON item.variant_of = wi.item_code
         AND item.disabled = 0
        JOIN `tabItem Variant Attribute` iva
          ON iva.parent = item.name
         AND iva.attribute = %s
        WHERE wi.`{WEBSITE_ITEM_COMMERCE_LANE_FIELD}` = 'checkout'
        GROUP BY wi.item_code
        HAVING color_count >= 50
        ORDER BY wi.item_code
        """,
        (LATEX_COLOR_ATTRIBUTE,),
        as_dict=True,
    )


def _template_attrs(template_code: str) -> list[str]:
    rows = frappe.get_all(
        "Item Variant Attribute",
        filters={
            "parent": template_code,
            "parenttype": "Item",
            "parentfield": "attributes",
        },
        fields=["attribute"],
        order_by="idx asc",
    )
    return [row.attribute for row in rows if row.attribute]


def _active_variant_attrs(template_code: str) -> dict[str, dict[str, str]]:
    rows = frappe.db.sql(
        """
        SELECT item.name, iva.attribute, iva.attribute_value
        FROM `tabItem` item
        LEFT JOIN `tabItem Variant Attribute` iva
          ON iva.parent = item.name
        WHERE item.variant_of = %s
          AND item.disabled = 0
        ORDER BY item.name ASC, iva.idx ASC
        """,
        (template_code,),
        as_dict=True,
    )
    variants: dict[str, dict[str, str]] = {}
    for row in rows:
        variants.setdefault(row.name, {})
        if row.attribute and row.attribute_value:
            variants[row.name][row.attribute] = row.attribute_value
    return variants


def _combo_key(combo: dict[str, str]) -> tuple[tuple[str, str], ...]:
    return tuple(sorted(combo.items()))


def _item_attribute_values(attribute: str) -> list[str]:
    return [
        str(value)
        for value in frappe.get_all(
            "Item Attribute Value",
            filters={"parent": attribute},
            pluck="attribute_value",
            order_by="idx asc",
        )
        if value
    ]


def _graduation_template_report(
    template_code: str,
    *,
    expected_attrs: list[str],
    expected_combos: list[dict[str, str]],
) -> dict[str, Any]:
    failures: list[str] = []
    template_attrs = _template_attrs(template_code)
    variants = _active_variant_attrs(template_code)
    actual_combos = {_combo_key(attrs) for attrs in variants.values()}
    expected_combo_keys = {_combo_key(combo) for combo in expected_combos}
    missing = expected_combo_keys - actual_combos
    extra = actual_combos - expected_combo_keys
    unpriced = [
        variant_code
        for variant_code in variants
        if frappe.db.get_value(
            "Item Price",
            {"item_code": variant_code, "price_list": PRICE_LIST, "selling": 1},
            "price_list_rate",
        )
        in (None, "")
    ]
    raw_color_variants = [
        variant_code
        for variant_code, attrs in variants.items()
        if LATEX_COLOR_ATTRIBUTE in attrs
    ]
    if template_attrs != expected_attrs:
        failures.append(f"{template_code} template attrs {template_attrs} != {expected_attrs}")
    if missing:
        failures.append(f"{template_code} missing preset combos: {len(missing)}")
    if extra:
        failures.append(f"{template_code} has unexpected active combos: {len(extra)}")
    if unpriced:
        failures.append(f"{template_code} has unpriced preset variants: {', '.join(unpriced[:5])}")
    if raw_color_variants:
        failures.append(f"{template_code} still has active raw latex-color variants: {len(raw_color_variants)}")
    return {
        "template": template_code,
        "template_attrs": template_attrs,
        "expected_attrs": expected_attrs,
        "expected_variant_count": len(expected_combo_keys),
        "active_variant_count": len(variants),
        "missing_count": len(missing),
        "extra_count": len(extra),
        "unpriced_count": len(unpriced),
        "raw_color_variant_count": len(raw_color_variants),
        "failures": failures,
    }


def _first_active_variant(template_code: str) -> str | None:
    return frappe.db.get_value(
        "Item",
        {"variant_of": template_code, "disabled": 0},
        "name",
        order_by="name asc",
    )


def _quote_cart_guards() -> list[dict[str, Any]]:
    rows = []
    for template_code in sorted(QUOTE_REQUEST_COLOR_PRODUCTS):
        variant_code = _first_active_variant(template_code)
        if not variant_code:
            rows.append(
                {
                    "template": template_code,
                    "failure": f"{template_code} has no active variant to prove quote cart guard",
                }
            )
            continue
        resolved, reason = resolve_cart_item_for_sale_with_reason(variant_code)
        record = {
            "template": template_code,
            "variant": variant_code,
            "reason": reason,
            "resolved": bool(resolved),
        }
        if reason != "quote_required" or resolved:
            record["failure"] = f"{template_code} cart guard reason {reason!r}, expected 'quote_required'"
        rows.append(record)
    return rows


def _graduation_cart_guards() -> list[dict[str, Any]]:
    rows = []
    for template_code in sorted(GRADUATION_PRESET_CHECKOUT_PRODUCTS):
        variant_code = _first_active_variant(template_code)
        if not variant_code:
            rows.append({"template": template_code, "failure": f"{template_code} has no active preset variant"})
            continue
        resolved, reason = resolve_cart_item_for_sale_with_reason(variant_code)
        record = {
            "template": template_code,
            "variant": variant_code,
            "reason": reason,
            "resolved": bool(resolved),
        }
        if not resolved or reason:
            record["failure"] = f"{template_code} checkout guard reason {reason!r}, expected sellable variant"
        rows.append(record)
    return rows
