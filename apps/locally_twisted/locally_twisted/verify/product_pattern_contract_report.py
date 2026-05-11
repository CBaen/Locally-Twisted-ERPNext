"""Read-only ProductPatternContract capability report for priced Website Items."""

from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path
from typing import Any

import frappe
from frappe.utils import now_datetime

from locally_twisted.catalog_contract.product_pattern_contract import (
    SCHEMA_VERSION,
    STANDARD_PRICE_LIST,
    build_product_pattern_contract,
)


EXPECTED_PRICED_WEBSITE_ITEMS = 53


def run(source_catalog: dict[str, Any] | None = None, source_catalog_path: str | None = None) -> dict[str, Any]:
    source = source_catalog or _load_source_catalog(source_catalog_path)
    source_products = {
        str(product.get("slug") or ""): product
        for product in source.get("products") or []
        if product.get("slug")
    }
    erpnext_products = _erpnext_priced_website_items()
    contracts = [
        build_product_pattern_contract(
            source_product=source_products.get(row["item_code"]),
            erpnext_product=row,
        )
        for row in erpnext_products
    ]
    rows = [contract.to_dict() for contract in contracts]
    status_counts = Counter(row["checkout_eligibility"]["status"] for row in rows)
    fail_loud_counts = Counter(
        state
        for row in rows
        for state in row["checkout_eligibility"].get("fail_loud_states") or []
    )
    axis_role_counts = Counter(
        axis["role"]
        for row in rows
        for axis in row.get("axis_contracts") or []
    )
    failures = _failures(rows, source_products)
    return {
        "ok": not failures,
        "schema_version": SCHEMA_VERSION,
        "generated_at": now_datetime().isoformat(),
        "read_only": True,
        "destructive_allowed": False,
        "scope": "all published Website Items with Standard Selling prices",
        "expected_priced_website_items": EXPECTED_PRICED_WEBSITE_ITEMS,
        "priced_website_item_count": len(rows),
        "summary": {
            "checkout_status_counts": dict(sorted(status_counts.items())),
            "fail_loud_state_counts": dict(sorted(fail_loud_counts.items())),
            "axis_role_counts": dict(sorted(axis_role_counts.items())),
            "source_product_count": len(source_products),
        },
        "resolver_boundary": (
            "ProductPatternContract + selected_config -> exact item_code or priced representative item, "
            "validated add-on lines, customization payload validation, cart line key, and SO/SI summary fields."
        ),
        "preservation_fields": {
            "Sales Order Item": [
                "custom_lt_product_template_item",
                "custom_lt_product_page_type",
                "custom_lt_configuration_version",
                "custom_lt_configuration_summary",
                "custom_lt_configuration_json",
            ],
            "Sales Invoice Item": [
                "custom_lt_product_template_item",
                "custom_lt_product_page_type",
                "custom_lt_configuration_version",
                "custom_lt_configuration_summary",
                "custom_lt_configuration_json",
            ],
        },
        "failures": failures,
        "products": rows,
    }


def _failures(rows: list[dict[str, Any]], source_products: dict[str, dict[str, Any]]) -> list[str]:
    failures = []
    if len(rows) != EXPECTED_PRICED_WEBSITE_ITEMS:
        failures.append(
            f"expected {EXPECTED_PRICED_WEBSITE_ITEMS} priced Website Items, found {len(rows)}"
        )
    missing_source = sorted(row["slug"] for row in rows if row["slug"] not in source_products)
    if missing_source:
        failures.append(f"priced Website Items missing Odoo source artifact rows: {missing_source}")
    missing_routes = sorted(row["slug"] for row in rows if not row.get("route"))
    if missing_routes:
        failures.append(f"priced Website Items missing Website Item route: {missing_routes}")
    return failures


def _load_source_catalog(source_catalog_path: str | None = None) -> dict[str, Any]:
    if source_catalog_path:
        path = Path(source_catalog_path)
    else:
        app_root = Path(frappe.get_app_path("locally_twisted")).parent
        path = app_root / "_resources" / "odoo-live" / "catalog.json"
    if not path.exists():
        frappe.throw(f"Missing Odoo source catalog artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _erpnext_priced_website_items() -> list[dict[str, Any]]:
    website_items = frappe.get_all(
        "Website Item",
        filters={"published": 1},
        fields=[
            "name",
            "item_code",
            "web_item_name",
            "route",
            "website_image",
            "item_group",
            "lt_product_page_type",
            "lt_commerce_lane",
        ],
        limit_page_length=10000,
        order_by="item_code asc",
    )
    rows = []
    for website_item in website_items:
        item_code = website_item.get("item_code")
        item = frappe.db.get_value(
            "Item",
            item_code,
            ["name", "item_name", "has_variants", "disabled", "image"],
            as_dict=True,
        ) or {}
        variants = frappe.get_all(
            "Item",
            filters={"variant_of": item_code, "disabled": 0},
            fields=["name", "item_name", "image"],
            limit_page_length=20000,
            order_by="name asc",
        )
        price_rows = _price_rows(item_code, [variant.name for variant in variants])
        if not price_rows:
            continue
        variant_axes = _variant_axes([variant.name for variant in variants])
        representative = _representative_price(price_rows, variants, item_code)
        rows.append(
            {
                **dict(website_item),
                "item_name": item.get("item_name") or website_item.get("web_item_name") or item_code,
                "item_image": item.get("image"),
                "has_variants": bool(item.get("has_variants")),
                "variant_count": len(variants),
                "template_price_count": sum(1 for row in price_rows if row.get("item_code") == item_code),
                "priced_variant_count": sum(1 for row in price_rows if row.get("item_code") != item_code),
                "price_min": min(row.get("price_list_rate") for row in price_rows),
                "price_max": max(row.get("price_list_rate") for row in price_rows),
                "representative_item_code": representative.get("item_code"),
                "representative_price": representative.get("price_list_rate"),
                "variant_image_count": sum(1 for variant in variants if variant.get("image")),
                "variant_axes": variant_axes,
            }
        )
    return rows


def _price_rows(template_item_code: str, variant_codes: list[str]) -> list[dict[str, Any]]:
    item_codes = [template_item_code, *variant_codes]
    return [
        dict(row)
        for row in frappe.get_all(
            "Item Price",
            filters={
                "item_code": ["in", item_codes],
                "price_list": STANDARD_PRICE_LIST,
                "selling": 1,
            },
            fields=["item_code", "price_list_rate"],
            limit_page_length=30000,
        )
    ]


def _variant_axes(variant_codes: list[str]) -> dict[str, list[str]]:
    if not variant_codes:
        return {}
    axes: dict[str, set[str]] = defaultdict(set)
    for row in frappe.get_all(
        "Item Variant Attribute",
        filters={"parent": ["in", variant_codes]},
        fields=["attribute", "attribute_value"],
        limit_page_length=60000,
    ):
        if row.get("attribute") and row.get("attribute_value"):
            axes[str(row.attribute)].add(str(row.attribute_value))
    return {axis: sorted(values) for axis, values in sorted(axes.items())}


def _representative_price(
    price_rows: list[dict[str, Any]],
    variants: list[Any],
    template_item_code: str,
) -> dict[str, Any]:
    variant_order = {variant.name: index for index, variant in enumerate(variants)}
    sorted_rows = sorted(
        price_rows,
        key=lambda row: (
            0 if row.get("item_code") in variant_order else 1,
            variant_order.get(row.get("item_code"), 999999),
            str(row.get("item_code") or template_item_code),
        ),
    )
    return sorted_rows[0] if sorted_rows else {}
