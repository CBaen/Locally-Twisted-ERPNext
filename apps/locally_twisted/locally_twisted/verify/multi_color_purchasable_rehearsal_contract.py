"""Rollback-only proof for multi-color recipe products entering checkout.

This verifier temporarily applies the local checkout contract in one ERPNext
transaction, proves source color-combo coverage after canonical color cleanup,
resolves every enabled live color-combo SKU through checkout with
``color_recipes``, proves Sales Order/Sales Invoice preservation, then rolls
everything back.
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import frappe
from frappe.utils import flt

from locally_twisted.catalog_contract.color_rules import canonical_color_name, is_balloon_color_axis
from locally_twisted.product_options import get_checkout_add_on_options, get_variant_attribute_options
from locally_twisted.verify import checkout_product_family_contract as checkout_family


MULTI_COLOR_PRODUCTS = {
    "7-epic-column": {
        "source_name": "7' Epic Column",
        "source_price": 100.0,
        "color_axes": ("latex colors",),
    },
    "baby-shower-combination-photo-opt": {
        "source_name": "Baby Shower Combination Photo opt",
        "source_price": 650.0,
        "color_axes": ("latex colors",),
    },
    "baby-table-decor": {
        "source_name": "Baby Table decor",
        "source_price": 30.0,
        "color_axes": ("Baby color",),
    },
    "classic-organic-for-easel": {
        "source_name": "classic organic for easel",
        "source_price": 100.0,
        "color_axes": ("latex colors",),
    },
    "number-balloon-columns": {
        "source_name": "Number Balloon Columns",
        "source_price": 55.0,
        "color_axes": ("Number colors", "latex colors"),
    },
    "sleepy-baby-column": {
        "source_name": "Sleepy Baby Column",
        "source_price": 220.0,
        "color_axes": ("latex colors",),
    },
}
EXPECTED_PRODUCT_COUNT = 6
EXPECTED_ENABLED_COLOR_SKUS = 563
SOURCE_CATALOG_PATHS = (
    Path("/tmp/lt-odoo-live-catalog.json"),
)


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
            raise ContractFail(f"generated multi-color rehearsal records survived rollback: {survivors}")
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
    source_by_slug = _source_products_by_slug()
    original_contracts = _snapshot_website_item_contracts()
    _apply_transactional_checkout_contracts()

    sales_order_lines: list[dict[str, Any]] = []
    product_results: list[dict[str, Any]] = []
    expected_sale_sku_count = 0

    for website_item_code, spec in MULTI_COLOR_PRODUCTS.items():
        product_result, lines = _assert_product_rehearsal(
            website_item_code,
            spec,
            source_by_slug.get(website_item_code),
        )
        product_results.append(product_result)
        sales_order_lines.extend(lines)
        expected_sale_sku_count += int(product_result["enabled_color_sku_count"])

    if expected_sale_sku_count != EXPECTED_ENABLED_COLOR_SKUS:
        raise ContractFail(
            f"expected {EXPECTED_ENABLED_COLOR_SKUS} enabled color SKUs, found {expected_sale_sku_count}"
        )

    sales_order = checkout_family._assert_sales_order_accepts_family_lines(
        token,
        sales_order_lines,
        expected_base_line_count=expected_sale_sku_count,
        expected_add_on_line_count=0,
        expected_color_recipe_line_count=expected_sale_sku_count,
    )
    sales_invoice_name = checkout_family._assert_invoice_preserves_family_lines(
        sales_order.name,
        expected_line_count=len(sales_order_lines),
        expected_base_line_count=expected_sale_sku_count,
        expected_add_on_line_count=0,
        expected_color_recipe_line_count=expected_sale_sku_count,
    )

    return {
        "multi_color_rehearsal_product_count": len(product_results),
        "multi_color_rehearsal_products": product_results,
        "original_contracts": original_contracts,
        "transactional_contract": "simple_product|checkout",
        "enabled_color_sku_count": expected_sale_sku_count,
        "sales_order": sales_order.name,
        "sales_invoice": sales_invoice_name,
        "sales_order_line_count": len(sales_order.items),
        "expected_sales_order_line_count": len(sales_order_lines),
        "add_on_line_count": 0,
        "color_recipe_line_count": expected_sale_sku_count,
        "line_fields": sorted(checkout_family.LINE_FIELDNAMES.values()),
        "schema_version": checkout_family.CONFIG_VERSION,
    }


def _assert_product_rehearsal(
    website_item_code: str,
    spec: dict[str, Any],
    source_product: dict[str, Any] | None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    from locally_twisted.www.checkout import _resolve_sale_lines

    if not source_product:
        raise ContractFail(f"{website_item_code} missing Odoo source row")
    if get_checkout_add_on_options(website_item_code):
        raise ContractFail(f"{website_item_code} should not expose checkout add-ons in the multi-color rehearsal")

    color_axes = tuple(spec["color_axes"])
    _assert_source_color_axes(website_item_code, source_product, color_axes)
    source_combos = _source_canonical_color_combos(source_product, color_axes)
    ui_coverage = _assert_live_ui_color_coverage(website_item_code, source_product, color_axes, source_combos)
    variant_item_codes = _enabled_variant_item_codes(website_item_code)

    sale_lines: list[dict[str, Any]] = []
    verified_variants: list[dict[str, Any]] = []
    live_combos: set[tuple[tuple[str, str], ...]] = set()
    for variant_item_code in variant_item_codes:
        checkout_family._assert_item_price(variant_item_code, float(spec["source_price"]))
        resolved = checkout_family._resolve_cart_item(variant_item_code, website_item_code)
        selected_options = checkout_family._variant_options_dict(resolved.get("variant_options") or [])
        color_options = _color_options_for_variant(website_item_code, variant_item_code, selected_options, color_axes)
        live_combos.add(_canonical_combo(color_options, color_axes))
        configuration = checkout_family._configuration_payload(
            item_code=variant_item_code,
            website_item_code=website_item_code,
            variant_options=resolved.get("variant_options") or [],
            color_recipes=[
                {
                    "axis": axis,
                    "label": axis,
                    "values": [color_options[axis]],
                }
                for axis in color_axes
            ],
        )
        lines, resolved_items = _resolve_sale_lines(
            [{"item_code": variant_item_code, "qty": 1, "configuration": configuration}]
        )
        if len(lines) != 1:
            raise ContractFail(f"{variant_item_code} should create one checkout line, found {len(lines)}")
        if len(resolved_items) != 1:
            raise ContractFail(f"{variant_item_code} display resolution should include one line, found {len(resolved_items)}")
        checkout_family._assert_base_line_payload(
            label=variant_item_code,
            line=lines[0],
            expected_item_code=variant_item_code,
            expected_website_item_code=website_item_code,
            expect_add_on=False,
            expected_selected_options={},
        )
        checkout_family._assert_color_recipe_payload(
            label=variant_item_code,
            line=lines[0],
            expected_color_options=color_options,
        )
        sale_lines.extend(lines)
        verified_variants.append(
            {
                "variant_item_code": variant_item_code,
                "color_recipes": color_options,
                "price": float(spec["source_price"]),
                "resolved_line_count": len(lines),
            }
        )

    if live_combos != source_combos:
        raise ContractFail(
            f"{website_item_code} live color combo coverage drifted: "
            f"missing={_format_combos(source_combos - live_combos)} "
            f"extra={_format_combos(live_combos - source_combos)}"
        )

    return (
        {
            "website_item_code": website_item_code,
            "source_name": spec["source_name"],
            "source_price": float(spec["source_price"]),
            "source_price_basis": "Odoo base price; color recipe choices do not change price",
            "source_valid_variant_count": len(source_product.get("valid_variants") or []),
            "source_canonical_color_combo_count": len(source_combos),
            "color_axes": list(color_axes),
            "source_axis_value_counts": _source_axis_value_counts(source_product, color_axes),
            "ui_axis_coverage": ui_coverage,
            "enabled_color_sku_count": len(variant_item_codes),
            "add_on_options": 0,
            "resolved_line_count": len(sale_lines),
            "verified_variant_count": len(verified_variants),
            "verified_variants": verified_variants,
        },
        sale_lines,
    )


def _assert_source_color_axes(
    website_item_code: str,
    source_product: dict[str, Any],
    color_axes: tuple[str, ...],
) -> None:
    attributes = source_product.get("attributes") or {}
    for axis in color_axes:
        if axis not in attributes:
            raise ContractFail(f"{website_item_code} source export missing color axis {axis}")
        if not is_balloon_color_axis(axis):
            raise ContractFail(f"{website_item_code} axis {axis} is not recognized as a balloon color axis")


def _assert_live_ui_color_coverage(
    website_item_code: str,
    source_product: dict[str, Any],
    color_axes: tuple[str, ...],
    source_combos: set[tuple[tuple[str, str], ...]],
) -> dict[str, Any]:
    rows = get_variant_attribute_options(website_item_code)
    by_axis = {str(row.get("attribute") or ""): row for row in rows}
    coverage: dict[str, Any] = {}
    for axis in color_axes:
        row = by_axis.get(axis)
        if not row:
            raise ContractFail(f"{website_item_code} UI options missing color axis {axis}")
        if row.get("lt_payload_target") != "color_recipes":
            raise ContractFail(f"{website_item_code} UI axis {axis} must target color_recipes, found {row}")
        if row.get("lt_selector_type") != "multi_color_recipe_builder":
            raise ContractFail(f"{website_item_code} UI axis {axis} must render a multi-color recipe builder")

        source_values = _source_canonical_values(source_product, axis)
        live_values = {
            canonical_color_name(_option_value(value))
            for value in row.get("values") or []
            if canonical_color_name(_option_value(value))
        }
        if source_values != live_values:
            raise ContractFail(
                f"{website_item_code} UI color values for {axis} drifted: "
                f"missing={sorted(source_values - live_values)} extra={sorted(live_values - source_values)}"
            )
        coverage[axis] = {
            "source_raw_value_count": len(_source_raw_values(source_product, axis)),
            "source_canonical_value_count": len(source_values),
            "ui_value_count": len(live_values),
            "payload_target": row.get("lt_payload_target"),
            "selector_type": row.get("lt_selector_type"),
        }

    if not source_combos:
        raise ContractFail(f"{website_item_code} source export produced no canonical color combos")
    return coverage


def _enabled_variant_item_codes(website_item_code: str) -> list[str]:
    rows = frappe.get_all(
        "Item",
        filters={"variant_of": website_item_code, "disabled": 0},
        fields=["item_code"],
        order_by="item_code asc",
    )
    item_codes = [row["item_code"] for row in rows]
    if not item_codes:
        raise ContractFail(f"{website_item_code} has no enabled color variants")
    return item_codes


def _color_options_for_variant(
    website_item_code: str,
    variant_item_code: str,
    selected_options: dict[str, str],
    color_axes: tuple[str, ...],
) -> dict[str, str]:
    missing = [axis for axis in color_axes if not selected_options.get(axis)]
    if missing:
        raise ContractFail(f"{variant_item_code} for {website_item_code} missing color axes: {missing}")
    extra_color_axes = sorted(axis for axis in selected_options if is_balloon_color_axis(axis) and axis not in color_axes)
    if extra_color_axes:
        raise ContractFail(f"{variant_item_code} exposed unexpected color axes: {extra_color_axes}")
    return {axis: selected_options[axis] for axis in color_axes}


def _source_canonical_color_combos(
    source_product: dict[str, Any],
    color_axes: tuple[str, ...],
) -> set[tuple[tuple[str, str], ...]]:
    combos: set[tuple[tuple[str, str], ...]] = set()
    for row in source_product.get("valid_variants") or []:
        combo = row.get("combo") or {}
        canonical = _canonical_combo({axis: combo.get(axis) for axis in color_axes}, color_axes)
        if canonical:
            combos.add(canonical)
    return combos


def _canonical_combo(
    combo: dict[str, Any],
    color_axes: tuple[str, ...],
) -> tuple[tuple[str, str], ...]:
    result: list[tuple[str, str]] = []
    for axis in color_axes:
        value = canonical_color_name(str(combo.get(axis) or ""))
        if value:
            result.append((axis, value))
    return tuple(result)


def _source_axis_value_counts(source_product: dict[str, Any], color_axes: tuple[str, ...]) -> dict[str, dict[str, int]]:
    return {
        axis: {
            "raw": len(_source_raw_values(source_product, axis)),
            "canonical": len(_source_canonical_values(source_product, axis)),
        }
        for axis in color_axes
    }


def _source_canonical_values(source_product: dict[str, Any], axis: str) -> set[str]:
    return {
        canonical_color_name(value)
        for value in _source_raw_values(source_product, axis)
        if canonical_color_name(value)
    }


def _source_raw_values(source_product: dict[str, Any], axis: str) -> list[str]:
    axis_row = (source_product.get("attributes") or {}).get(axis) or {}
    values = []
    for row in axis_row.get("values") or []:
        value = _option_value(row)
        if value:
            values.append(value)
    return values


def _option_value(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("name") or value.get("attribute_value") or value.get("value") or "").strip()
    return str(value or "").strip()


def _snapshot_website_item_contracts() -> dict[str, dict[str, Any]]:
    snapshots: dict[str, dict[str, Any]] = {}
    for website_item_code in MULTI_COLOR_PRODUCTS:
        row = frappe.db.get_value(
            "Website Item",
            {"item_code": website_item_code},
            [
                "name",
                "item_code",
                "web_item_name",
                "route",
                "item_group",
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
            "route": row.get("route"),
            "item_group": row.get("item_group"),
            "published": bool(row.get("published")),
            "product_page_type": row.get("lt_product_page_type"),
            "commerce_lane": row.get("lt_commerce_lane"),
        }
    return snapshots


def _apply_transactional_checkout_contracts() -> None:
    for website_item_code in MULTI_COLOR_PRODUCTS:
        frappe.db.set_value(
            "Website Item",
            {"item_code": website_item_code},
            {
                "lt_product_page_type": "simple_product",
                "lt_commerce_lane": "checkout",
            },
            update_modified=False,
        )


def _source_products_by_slug() -> dict[str, dict[str, Any]]:
    for path in SOURCE_CATALOG_PATHS:
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        products = data.get("products") if isinstance(data, dict) else None
        if isinstance(products, list):
            return {
                str(product.get("slug") or ""): product
                for product in products
                if isinstance(product, dict) and product.get("slug")
            }
    raise ContractFail(f"missing readable source catalog in {[str(path) for path in SOURCE_CATALOG_PATHS]}")


def _format_combos(combos: set[tuple[tuple[str, str], ...]]) -> list[dict[str, str]]:
    return [dict(combo) for combo in sorted(combos)]
