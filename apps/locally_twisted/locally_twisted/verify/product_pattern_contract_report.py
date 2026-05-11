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
from locally_twisted.catalog_contract.addon_rules import known_add_on_contracts_for_axis


EXPECTED_PUBLISHED_WEBSITE_ITEMS = 53


def run(source_catalog: dict[str, Any] | None = None, source_catalog_path: str | None = None) -> dict[str, Any]:
    source = source_catalog or _load_source_catalog(source_catalog_path)
    source_products = {
        str(product.get("slug") or ""): product
        for product in source.get("products") or []
        if product.get("slug")
    }
    add_on_prices = _add_on_prices_for_source(source_products.values())
    erpnext_products = _erpnext_published_website_items(add_on_prices)
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
    line_field_status = _line_field_status()
    inventory_failures = _inventory_failures(rows, source_products)
    checkout_failures = _checkout_gate_failures(rows, line_field_status)
    failures = inventory_failures + checkout_failures
    return {
        "ok": not failures,
        "inventory_ok": not inventory_failures,
        "checkout_gate_ok": not checkout_failures,
        "schema_version": SCHEMA_VERSION,
        "generated_at": now_datetime().isoformat(),
        "read_only": True,
        "destructive_allowed": False,
        "scope": "all published Website Items, including rows with missing Standard Selling prices",
        "expected_published_website_items": EXPECTED_PUBLISHED_WEBSITE_ITEMS,
        "published_website_item_count": len(rows),
        "priced_website_item_count": sum(1 for row in rows if row["pricing"]["priced_sale_units"] > 0),
        "summary": {
            "checkout_status_counts": dict(sorted(status_counts.items())),
            "fail_loud_state_counts": dict(sorted(fail_loud_counts.items())),
            "axis_role_counts": dict(sorted(axis_role_counts.items())),
            "source_product_count": len(source_products),
            "published_website_item_count": len(rows),
            "priced_website_item_count": sum(1 for row in rows if row["pricing"]["priced_sale_units"] > 0),
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
        "line_field_status": line_field_status,
        "inventory_failures": inventory_failures,
        "checkout_gate_failures": checkout_failures,
        "failures": failures,
        "products": rows,
    }


def _inventory_failures(rows: list[dict[str, Any]], source_products: dict[str, dict[str, Any]]) -> list[str]:
    failures = []
    if len(rows) != EXPECTED_PUBLISHED_WEBSITE_ITEMS:
        failures.append(
            f"expected {EXPECTED_PUBLISHED_WEBSITE_ITEMS} published Website Items, found {len(rows)}"
        )
    missing_source = sorted(row["slug"] for row in rows if row["slug"] not in source_products)
    if missing_source:
        failures.append(f"priced Website Items missing Odoo source artifact rows: {missing_source}")
    missing_routes = sorted(row["slug"] for row in rows if not row.get("route"))
    if missing_routes:
        failures.append(f"priced Website Items missing Website Item route: {missing_routes}")
    return failures


def _checkout_gate_failures(rows: list[dict[str, Any]], line_field_status: dict[str, Any]) -> list[str]:
    failures = []
    missing_price = sorted(row["slug"] for row in rows if row["pricing"]["status"] == "missing")
    if missing_price:
        failures.append(f"published Website Items missing Standard Selling prices: {missing_price}")
    unresolved_checkout = sorted(
        row["slug"]
        for row in rows
        if row.get("current_commerce_lane") == "checkout"
        and row["checkout_eligibility"]["status"] != "checkout_ready"
    )
    if unresolved_checkout:
        failures.append(f"checkout-lane products not checkout_ready: {unresolved_checkout}")
    fail_loud_checkout = sorted(
        row["slug"]
        for row in rows
        if row["checkout_eligibility"]["status"] == "checkout_ready"
        and row["checkout_eligibility"].get("fail_loud_states")
    )
    if fail_loud_checkout:
        failures.append(f"checkout_ready products still have fail-loud states: {fail_loud_checkout}")
    unpriced_addons = sorted(
        row["slug"]
        for row in rows
        for axis in row.get("axis_contracts") or []
        if axis.get("role") == "add_on" and not _add_on_contract_ready(axis.get("add_on_contract") or {})
    )
    if unpriced_addons:
        failures.append(f"products with unpriced add-on contracts: {sorted(set(unpriced_addons))}")
    lost_mapper = sorted(
        row["slug"]
        for row in rows
        if not row.get("source_patterns")
        or not row.get("source_integrity")
        or not row.get("source_import_requirements")
        or not row.get("source_pattern_contract")
    )
    if lost_mapper:
        failures.append(f"products missing carried Odoo mapper contract semantics: {lost_mapper}")
    missing_line_fields = line_field_status.get("missing") or {}
    if any(missing_line_fields.values()):
        failures.append(f"missing preservation line fields: {missing_line_fields}")
    return failures


def _add_on_contract_ready(contract: dict[str, Any]) -> bool:
    return bool(
        contract.get("ready_for_checkout")
        and contract.get("item_code")
        and contract.get("live_unit_price") not in (None, "")
        and contract.get("price_status") == "ready"
        and contract.get("quantity_min")
        and contract.get("quantity_max")
        and contract.get("receipt_label")
    )


def _load_source_catalog(source_catalog_path: str | None = None) -> dict[str, Any]:
    if source_catalog_path:
        path = Path(source_catalog_path)
    else:
        app_root = Path(frappe.get_app_path("locally_twisted")).parent
        path = app_root / "_resources" / "odoo-live" / "catalog.json"
    if not path.exists():
        frappe.throw(f"Missing Odoo source catalog artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _erpnext_published_website_items(add_on_prices: dict[str, Any]) -> list[dict[str, Any]]:
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
        variant_axes = _variant_axes([variant.name for variant in variants])
        representative = _representative_price(price_rows, variants, item_code)
        prices = [row.get("price_list_rate") for row in price_rows]
        rows.append(
            {
                **dict(website_item),
                "item_name": item.get("item_name") or website_item.get("web_item_name") or item_code,
                "item_image": item.get("image"),
                "has_variants": bool(item.get("has_variants")),
                "variant_count": len(variants),
                "template_price_count": sum(1 for row in price_rows if row.get("item_code") == item_code),
                "priced_variant_count": sum(1 for row in price_rows if row.get("item_code") != item_code),
                "price_min": min(prices) if prices else None,
                "price_max": max(prices) if prices else None,
                "representative_item_code": representative.get("item_code"),
                "representative_price": representative.get("price_list_rate"),
                "variant_image_count": sum(1 for variant in variants if variant.get("image")),
                "variant_axes": variant_axes,
                "add_on_prices_by_item": add_on_prices,
            }
        )
    return rows


def _add_on_prices_for_source(source_products: Any) -> dict[str, Any]:
    item_codes = sorted(
        {
            str(contract.get("item_code") or "")
            for product in source_products
            for axis_name in (product.get("attributes") or {})
            for contract in known_add_on_contracts_for_axis(str(axis_name))
            if contract.get("item_code")
        }
    )
    if not item_codes:
        return {}
    return {
        row.get("item_code"): row.get("price_list_rate")
        for row in frappe.get_all(
            "Item Price",
            filters={
                "item_code": ["in", item_codes],
                "price_list": STANDARD_PRICE_LIST,
                "selling": 1,
            },
            fields=["item_code", "price_list_rate"],
            limit_page_length=1000,
        )
    }


def _line_field_status() -> dict[str, Any]:
    required = {
        "Sales Order Item": {
            "custom_lt_product_template_item",
            "custom_lt_product_page_type",
            "custom_lt_configuration_version",
            "custom_lt_configuration_summary",
            "custom_lt_configuration_json",
        },
        "Sales Invoice Item": {
            "custom_lt_product_template_item",
            "custom_lt_product_page_type",
            "custom_lt_configuration_version",
            "custom_lt_configuration_summary",
            "custom_lt_configuration_json",
        },
    }
    present: dict[str, set[str]] = {doctype: set() for doctype in required}
    for doctype, fieldnames in required.items():
        custom_rows = frappe.get_all(
            "Custom Field",
            filters={"dt": doctype, "fieldname": ["in", sorted(fieldnames)]},
            fields=["fieldname"],
            limit_page_length=1000,
        )
        doc_rows = frappe.get_all(
            "DocField",
            filters={"parent": doctype, "fieldname": ["in", sorted(fieldnames)]},
            fields=["fieldname"],
            limit_page_length=1000,
        )
        present[doctype].update(str(row.fieldname) for row in [*custom_rows, *doc_rows])
    missing = {
        doctype: sorted(fieldnames - present[doctype])
        for doctype, fieldnames in required.items()
    }
    return {
        "ready": not any(missing.values()),
        "required": {doctype: sorted(fieldnames) for doctype, fieldnames in required.items()},
        "present": {doctype: sorted(fieldnames) for doctype, fieldnames in present.items()},
        "missing": missing,
    }


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
