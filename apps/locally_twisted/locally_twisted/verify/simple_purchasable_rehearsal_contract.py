"""Rollback-only proof for simple held products entering checkout.

This verifier does not promote Website Items, open public ecommerce, create a
payment session, or send customer messages. It temporarily applies the checkout
contract inside one ERPNext transaction, proves the simple purchasable tranche
can resolve through Sales Order and Sales Invoice line fields, then rolls back.
"""
from __future__ import annotations

import time
from typing import Any

import frappe
from frappe.utils import flt

from locally_twisted.verify import checkout_product_family_contract as checkout_family


SIMPLE_REHEARSAL_PRODUCTS = {
    "large-head-missionary": {
        "source_name": "Large head Missionary",
        "source_price": 175.0,
        "source_variant_count": 30,
        "required_attributes": ("Missionary", "skin color", "Hair color"),
        "source_price_basis": "legacy_source base price; live ERPNext snapshot prices match every variant",
    },
    "mothers-day-front-yard-7-column": {
        "source_name": "Mother's day front yard 7' Column",
        "source_price": 140.0,
        "source_variant_count": 0,
        "required_attributes": (),
        "source_price_basis": "legacy_source base price",
    },
}


class ContractFail(Exception):
    pass


def run() -> dict[str, Any]:
    token = str(int(time.time() * 1000))
    original_commit = frappe.db.commit
    intercepted_commits: list[bool] = []

    def no_commit(*args, **kwargs):
        intercepted_commits.append(True)

    try:
        frappe.db.commit = no_commit
        result = _run_contract(token)
        result["commit_calls_intercepted"] = len(intercepted_commits)
        frappe.db.rollback()
        result["rolled_back"] = True
        result["survivor_counts"] = checkout_family._survivor_counts(token)
        survivors = {key: value for key, value in result["survivor_counts"].items() if value}
        if survivors:
            raise ContractFail(f"generated rehearsal records survived rollback: {survivors}")
        return {"ok": True, **result}
    except ContractFail as exc:
        frappe.db.rollback()
        return {"ok": False, "failures": [str(exc)], "survivor_counts": checkout_family._survivor_counts(token)}
    except Exception:
        frappe.db.rollback()
        return {"ok": False, "failures": [frappe.get_traceback()], "survivor_counts": checkout_family._survivor_counts(token)}
    finally:
        frappe.db.commit = original_commit
        frappe.db.rollback()


def _run_contract(token: str) -> dict[str, Any]:
    checkout_family._assert_line_schema()
    original_contracts = _snapshot_website_item_contracts()
    _apply_transactional_checkout_contracts()

    sales_order_lines: list[dict[str, Any]] = []
    product_results: list[dict[str, Any]] = []
    expected_sale_sku_count = 0

    for website_item_code, spec in SIMPLE_REHEARSAL_PRODUCTS.items():
        product_result, lines = _assert_product_rehearsal(website_item_code, spec)
        product_results.append(product_result)
        sales_order_lines.extend(lines)
        expected_sale_sku_count += int(product_result["sale_sku_count"])

    sales_order = checkout_family._assert_sales_order_accepts_family_lines(
        token,
        sales_order_lines,
        expected_base_line_count=expected_sale_sku_count,
        expected_add_on_line_count=0,
        expected_color_recipe_line_count=0,
    )
    sales_invoice_name = checkout_family._assert_invoice_preserves_family_lines(
        sales_order.name,
        expected_line_count=len(sales_order_lines),
        expected_base_line_count=expected_sale_sku_count,
        expected_add_on_line_count=0,
        expected_color_recipe_line_count=0,
    )

    return {
        "simple_rehearsal_product_count": len(product_results),
        "simple_rehearsal_products": product_results,
        "original_contracts": original_contracts,
        "transactional_contract": "simple_product|checkout",
        "enabled_sale_sku_count": expected_sale_sku_count,
        "sales_order": sales_order.name,
        "sales_invoice": sales_invoice_name,
        "sales_order_line_count": len(sales_order.items),
        "expected_sales_order_line_count": len(sales_order_lines),
        "add_on_line_count": 0,
        "color_recipe_line_count": 0,
        "line_fields": sorted(checkout_family.LINE_FIELDNAMES.values()),
        "schema_version": checkout_family.CONFIG_VERSION,
    }


def _assert_product_rehearsal(
    website_item_code: str,
    spec: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    required_attributes = tuple(spec.get("required_attributes") or ())
    if required_attributes:
        return _assert_variant_product_rehearsal(website_item_code, spec, required_attributes)
    return _assert_single_sku_product_rehearsal(website_item_code, spec)


def _assert_variant_product_rehearsal(
    website_item_code: str,
    spec: dict[str, Any],
    required_attributes: tuple[str, ...],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    from locally_twisted.product_options import get_checkout_add_on_options

    if get_checkout_add_on_options(website_item_code):
        raise ContractFail(f"{website_item_code} should not expose checkout add-ons in the simple rehearsal")

    variant_item_codes = _variant_item_codes_with_required_attributes(website_item_code, required_attributes)
    expected_variant_count = int(spec["source_variant_count"])
    if len(variant_item_codes) != expected_variant_count:
        raise ContractFail(
            f"{website_item_code} should have {expected_variant_count} enabled sale variants, "
            f"found {len(variant_item_codes)}"
        )

    sale_lines: list[dict[str, Any]] = []
    verified_variants: list[dict[str, Any]] = []
    for variant_item_code in variant_item_codes:
        checkout_family._assert_item_price(variant_item_code, float(spec["source_price"]))
        result, lines = checkout_family._assert_variant_simple_line(
            website_item_code=website_item_code,
            variant_item_code=variant_item_code,
            label=str(spec["source_name"]),
            no_add_on_failure=f"{website_item_code} should not expose checkout add-ons",
        )
        selected_options = result.get("selected_options") or {}
        missing_attributes = sorted(set(required_attributes) - set(selected_options))
        if missing_attributes:
            raise ContractFail(f"{variant_item_code} dropped required selected options: {missing_attributes}")
        sale_lines.extend(lines)
        verified_variants.append(
            {
                "variant_item_code": variant_item_code,
                "selected_options": selected_options,
                "price": float(spec["source_price"]),
                "resolved_line_count": len(lines),
            }
        )

    return (
        {
            "website_item_code": website_item_code,
            "source_name": spec["source_name"],
            "source_price": float(spec["source_price"]),
            "source_price_basis": spec["source_price_basis"],
            "required_attributes": list(required_attributes),
            "sale_sku_count": len(variant_item_codes),
            "add_on_options": 0,
            "resolved_line_count": len(sale_lines),
            "verified_variant_count": len(verified_variants),
            "verified_variants": verified_variants,
        },
        sale_lines,
    )


def _assert_single_sku_product_rehearsal(
    website_item_code: str,
    spec: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    checkout_family._assert_item_price(website_item_code, float(spec["source_price"]))
    result, lines = checkout_family._assert_single_sku_simple_line(
        website_item_code=website_item_code,
        label=str(spec["source_name"]),
        no_add_on_failure=f"{website_item_code} should not expose checkout add-ons",
    )
    rate = _item_price(website_item_code)
    if flt(rate) != flt(spec["source_price"]):
        raise ContractFail(f"{website_item_code} price should be {spec['source_price']}, found {rate}")
    return (
        {
            "website_item_code": website_item_code,
            "source_name": spec["source_name"],
            "source_price": float(spec["source_price"]),
            "source_price_basis": spec["source_price_basis"],
            "required_attributes": [],
            "sale_sku_count": 1,
            "add_on_options": 0,
            "resolved_line_count": len(lines),
            "item_code": result.get("item_code"),
        },
        lines,
    )


def _snapshot_website_item_contracts() -> dict[str, dict[str, Any]]:
    snapshots: dict[str, dict[str, Any]] = {}
    for website_item_code in SIMPLE_REHEARSAL_PRODUCTS:
        row = frappe.db.get_value(
            "Website Item",
            {"item_code": website_item_code},
            [
                "name",
                "item_code",
                "web_item_name",
                "published",
                "lt_product_page_type",
                "lt_commerce_lane",
            ],
            as_dict=True,
        )
        if not row:
            raise ContractFail(f"missing Website Item for {website_item_code}")
        if not int(row.get("published") or 0):
            raise ContractFail(f"{website_item_code} Website Item is not published")
        snapshots[website_item_code] = {
            "website_item_name": row.get("name"),
            "web_item_name": row.get("web_item_name"),
            "published": bool(row.get("published")),
            "product_page_type": row.get("lt_product_page_type"),
            "commerce_lane": row.get("lt_commerce_lane"),
        }
    return snapshots


def _apply_transactional_checkout_contracts() -> None:
    for website_item_code in SIMPLE_REHEARSAL_PRODUCTS:
        frappe.db.set_value(
            "Website Item",
            {"item_code": website_item_code},
            {
                "lt_product_page_type": "simple_product",
                "lt_commerce_lane": "checkout",
            },
            update_modified=False,
        )


def _variant_item_codes_with_required_attributes(
    website_item_code: str,
    required_attributes: tuple[str, ...],
) -> list[str]:
    rows = frappe.db.sql(
        """
        SELECT item.item_code, COUNT(DISTINCT attr.attribute) AS matched_attributes
        FROM `tabItem` item
        INNER JOIN `tabItem Variant Attribute` attr
            ON attr.parent = item.name
        WHERE item.variant_of = %(website_item_code)s
            AND item.disabled = 0
            AND attr.attribute IN %(required_attributes)s
            AND attr.attribute_value IS NOT NULL
            AND attr.attribute_value != ''
        GROUP BY item.item_code
        HAVING matched_attributes = %(required_attribute_count)s
        ORDER BY item.item_code
        """,
        {
            "website_item_code": website_item_code,
            "required_attributes": tuple(required_attributes),
            "required_attribute_count": len(required_attributes),
        },
        as_dict=True,
    )
    item_codes = [row["item_code"] for row in rows]
    if not item_codes:
        raise ContractFail(f"{website_item_code} has no enabled variants for {required_attributes}")
    return item_codes


def _item_price(item_code: str) -> float:
    rate = frappe.db.get_value(
        "Item Price",
        {"item_code": item_code, "price_list": checkout_family.PRICE_LIST, "selling": 1},
        "price_list_rate",
    )
    if rate in (None, ""):
        raise ContractFail(f"{item_code} has no selling Item Price in {checkout_family.PRICE_LIST}")
    return float(rate)
