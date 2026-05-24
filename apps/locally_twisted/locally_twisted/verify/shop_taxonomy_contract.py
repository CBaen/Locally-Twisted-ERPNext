"""Verify public shop products match the approved taxonomy."""
from __future__ import annotations

from typing import Any

import frappe

from locally_twisted.shop_taxonomy import (
    INVALID_VISIBLE_CATEGORY_TERMS,
    LEGACY_PRIMARY_GROUPS,
    OCCASION_ROOT,
    PRIMARY_CATEGORY_NAMES,
    PRIMARY_CATEGORY_SPECS,
    PRODUCT_TAXONOMY,
    SECONDARY_CATEGORY_NAMES,
    SECONDARY_CATEGORY_SPECS,
    SHOP_ROOT,
    product_route,
)


def run() -> dict[str, Any]:
    failures: list[str] = []
    evidence: dict[str, Any] = {
        "expected_products": len(PRODUCT_TAXONOMY),
        "published_products_checked": 0,
        "primary_categories": list(PRIMARY_CATEGORY_NAMES),
        "secondary_categories": list(SECONDARY_CATEGORY_NAMES),
    }

    _check_active_primary_categories(failures)
    _check_secondary_categories(failures)
    _check_legacy_groups_hidden(failures)
    _check_published_products(failures, evidence)

    return {"ok": not failures, "failures": failures, "evidence": evidence}


def execute() -> dict[str, Any]:
    return run()


def _check_active_primary_categories(failures: list[str]) -> None:
    rows = frappe.get_all(
        "Item Group",
        filters={"parent_item_group": SHOP_ROOT, "show_in_website": 1},
        fields=["name", "route", "weightage"],
        order_by="weightage asc, item_group_name asc",
    )
    actual = [row["name"] for row in rows]
    expected = list(PRIMARY_CATEGORY_NAMES)
    if actual != expected:
        failures.append(f"visible primary categories expected {expected}, found {actual}")

    route_by_name = {row["name"]: row.get("route") for row in rows}
    for spec in PRIMARY_CATEGORY_SPECS:
        route = route_by_name.get(spec.name)
        if route != spec.route:
            failures.append(f"primary category {spec.name} route expected {spec.route}, found {route}")

    visible_invalid = [
        row["name"]
        for row in rows
        if row["name"] in INVALID_VISIBLE_CATEGORY_TERMS
    ]
    if visible_invalid:
        failures.append(f"invalid terms still visible as primary categories: {visible_invalid}")


def _check_secondary_categories(failures: list[str]) -> None:
    if not frappe.db.exists("Item Group", OCCASION_ROOT):
        failures.append(f"secondary category root is missing: {OCCASION_ROOT}")
        return

    rows = frappe.get_all(
        "Item Group",
        filters={"parent_item_group": OCCASION_ROOT},
        fields=["name", "route", "show_in_website", "weightage"],
        order_by="weightage asc, item_group_name asc",
    )
    actual = [row["name"] for row in rows]
    expected = list(SECONDARY_CATEGORY_NAMES)
    if actual != expected:
        failures.append(f"secondary categories expected {expected}, found {actual}")

    route_by_name = {row["name"]: row.get("route") for row in rows}
    visible = [row["name"] for row in rows if int(row.get("show_in_website") or 0)]
    if visible:
        failures.append(f"secondary categories must not appear as primary menu categories: {visible}")
    for spec in SECONDARY_CATEGORY_SPECS:
        route = route_by_name.get(spec.name)
        if route != spec.route:
            failures.append(f"secondary category {spec.name} route expected {spec.route}, found {route}")


def _check_legacy_groups_hidden(failures: list[str]) -> None:
    for group in LEGACY_PRIMARY_GROUPS:
        if not frappe.db.exists("Item Group", group):
            continue
        show = int(frappe.db.get_value("Item Group", group, "show_in_website") or 0)
        if show:
            failures.append(f"legacy category must be hidden from the public category menu: {group}")


def _check_published_products(failures: list[str], evidence: dict[str, Any]) -> None:
    rows = frappe.get_all(
        "Website Item",
        filters={"published": 1},
        fields=["name", "item_code", "item_group", "route", "web_item_name"],
        order_by="item_code asc",
    )
    rows_by_item_code = {row["item_code"]: row for row in rows if row.get("item_code")}
    expected_codes = set(PRODUCT_TAXONOMY)
    actual_codes = set(rows_by_item_code)

    missing = sorted(expected_codes - actual_codes)
    extra = sorted(actual_codes - expected_codes)
    if missing:
        failures.append(f"approved product pages missing from published Website Items: {missing}")
    if extra:
        failures.append(f"published Website Items are not in the approved taxonomy map: {extra}")

    for item_code in sorted(expected_codes & actual_codes):
        row = rows_by_item_code[item_code]
        taxonomy = PRODUCT_TAXONOMY[item_code]
        primary = taxonomy["primary"]
        secondary = taxonomy["secondary"]
        evidence["published_products_checked"] += 1

        route = row.get("route") or ""
        expected_route = product_route(item_code)
        if row.get("item_group") != primary:
            failures.append(f"{item_code} Website Item primary expected {primary}, found {row.get('item_group')}")
        if route != expected_route:
            failures.append(f"{item_code} route expected {expected_route}, found {route}")

        item_group = frappe.db.get_value("Item", item_code, "item_group")
        if item_group != primary:
            failures.append(f"{item_code} Item primary expected {primary}, found {item_group}")

        bad_variant_count = frappe.db.count("Item", {"variant_of": item_code, "item_group": ["!=", primary]})
        if bad_variant_count:
            failures.append(f"{item_code} has {bad_variant_count} variants outside primary category {primary}")

        secondary_rows = frappe.get_all(
            "Website Item Group",
            filters={
                "parent": row["name"],
                "parenttype": "Website Item",
                "parentfield": "website_item_groups",
            },
            fields=["item_group"],
            order_by="idx asc",
        )
        actual_secondary = [item["item_group"] for item in secondary_rows]
        if actual_secondary != [secondary]:
            failures.append(f"{item_code} secondary categories expected [{secondary}], found {actual_secondary}")
