"""Verify public catalog records still resolve to coherent storefront state."""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

import frappe


PRICE_LIST = "Standard Selling"
ROOT_ITEM_GROUP = "Shop Items"
VALID_PAGE_TYPES = {"simple_product", "complex_custom_product"}
VALID_COMMERCE_LANES = {"checkout", "quote_first"}
PROTECTED_ROUTES = {
    "",
    "about",
    "accessibility",
    "all-products",
    "book",
    "cart",
    "checkout",
    "contact",
    "faq",
    "login",
    "portfolio",
    "privacy",
    "ready-to-order-paused",
    "refund-policy",
    "shop",
    "shop-by-category",
    "shop-items",
    "terms",
    "thank-you",
}


def run() -> dict[str, Any]:
    rows = _published_website_items()
    item_codes = [row["item_code"] for row in rows if row.get("item_code")]
    items = _items(item_codes)
    item_groups = _item_group_ancestry()
    price_map = _selling_price_map()
    variants_by_template = _active_variants_by_template()
    variant_attributes = _variant_attributes(variants_by_template)
    route_counts = Counter(_clean_route(row.get("route")) for row in rows)

    failures: list[str] = []
    warnings: list[str] = []
    evidence: dict[str, Any] = {
        "published_website_items": len(rows),
        "checkout_website_items": 0,
        "quote_first_website_items": 0,
        "checked_sellable_item_codes": 0,
        "checked_variant_templates": 0,
        "checked_active_variants": 0,
        "duplicate_route_count": 0,
        "protected_route_count": 0,
    }

    for row in rows:
        _check_website_item(
            row=row,
            items=items,
            item_groups=item_groups,
            price_map=price_map,
            variants_by_template=variants_by_template,
            variant_attributes=variant_attributes,
            route_counts=route_counts,
            failures=failures,
            warnings=warnings,
            evidence=evidence,
        )

    _check_orphan_prices_for_public_templates(
        rows=rows,
        items=items,
        price_map=price_map,
        variants_by_template=variants_by_template,
        warnings=warnings,
    )

    return {
        "ok": not failures,
        "price_list": PRICE_LIST,
        "evidence": evidence,
        "failures": failures,
        "warnings": warnings,
    }


def execute() -> dict[str, Any]:
    return run()


def _published_website_items() -> list[dict[str, Any]]:
    return frappe.get_all(
        "Website Item",
        filters={"published": 1},
        fields=[
            "name",
            "item_code",
            "web_item_name",
            "route",
            "item_group",
            "lt_product_page_type",
            "lt_commerce_lane",
        ],
        order_by="name asc",
    )


def _items(item_codes: list[str]) -> dict[str, dict[str, Any]]:
    if not item_codes:
        return {}
    rows = frappe.get_all(
        "Item",
        filters={"name": ["in", item_codes]},
        fields=["name", "item_code", "item_name", "disabled", "has_variants", "variant_of", "item_group"],
    )
    return {row["name"]: row for row in rows}


def _selling_price_map() -> dict[str, list[float]]:
    rows = frappe.get_all(
        "Item Price",
        filters={"price_list": PRICE_LIST, "selling": 1},
        fields=["item_code", "price_list_rate"],
    )
    by_code: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        item_code = row.get("item_code")
        if item_code:
            by_code[item_code].append(float(row.get("price_list_rate") or 0))
    return dict(by_code)


def _active_variants_by_template() -> dict[str, list[dict[str, Any]]]:
    rows = frappe.get_all(
        "Item",
        filters={"variant_of": ["!=", ""], "disabled": 0},
        fields=["name", "item_code", "item_name", "variant_of"],
        order_by="variant_of asc, name asc",
    )
    by_template: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        template = row.get("variant_of")
        if template:
            by_template[template].append(row)
    return dict(by_template)


def _variant_attributes(variants_by_template: dict[str, list[dict[str, Any]]]) -> dict[str, tuple[tuple[str, str], ...]]:
    variant_names = [row["name"] for rows in variants_by_template.values() for row in rows]
    if not variant_names:
        return {}
    rows = frappe.get_all(
        "Item Variant Attribute",
        filters={"parent": ["in", variant_names]},
        fields=["parent", "attribute", "attribute_value"],
        order_by="parent asc, idx asc",
    )
    by_variant: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for row in rows:
        parent = row.get("parent")
        attribute = row.get("attribute")
        value = row.get("attribute_value")
        if parent and attribute and value:
            by_variant[parent].append((str(attribute), str(value)))
    return {variant: tuple(sorted(attrs)) for variant, attrs in by_variant.items()}


def _item_group_ancestry() -> dict[str, set[str]]:
    groups = frappe.get_all("Item Group", fields=["name", "parent_item_group"])
    parents = {row["name"]: row.get("parent_item_group") for row in groups}
    ancestry: dict[str, set[str]] = {}
    for group in parents:
        seen: set[str] = set()
        current = group
        while current and current not in seen:
            seen.add(current)
            current = parents.get(current)
        ancestry[group] = seen
    return ancestry


def _check_website_item(
    *,
    row: dict[str, Any],
    items: dict[str, dict[str, Any]],
    item_groups: dict[str, set[str]],
    price_map: dict[str, list[float]],
    variants_by_template: dict[str, list[dict[str, Any]]],
    variant_attributes: dict[str, tuple[tuple[str, str], ...]],
    route_counts: Counter,
    failures: list[str],
    warnings: list[str],
    evidence: dict[str, Any],
) -> None:
    item_code = row.get("item_code")
    label = f"{row.get('name')}:{item_code}"
    route = _clean_route(row.get("route"))
    page_type = row.get("lt_product_page_type")
    commerce_lane = row.get("lt_commerce_lane")

    if route_counts[route] > 1:
        evidence["duplicate_route_count"] += 1
        failures.append(f"{label} route '{route}' is duplicated across published Website Items")
    if route in PROTECTED_ROUTES:
        evidence["protected_route_count"] += 1
        failures.append(f"{label} route '{route}' collides with a protected public route")

    item = items.get(item_code)
    if not item:
        failures.append(f"{label} is published but linked Item does not exist")
        return
    if int(item.get("disabled") or 0):
        failures.append(f"{label} is published but linked Item is disabled")
    if item.get("variant_of"):
        failures.append(f"{label} is a published Website Item for a variant; publish the template page instead")

    group = row.get("item_group") or item.get("item_group")
    if group not in item_groups:
        failures.append(f"{label} uses missing Item Group '{group}'")
    elif ROOT_ITEM_GROUP not in item_groups[group]:
        failures.append(f"{label} uses non-shop Item Group '{group}'")

    if page_type not in VALID_PAGE_TYPES:
        failures.append(f"{label} has invalid product page type '{page_type}'")
    if commerce_lane not in VALID_COMMERCE_LANES:
        failures.append(f"{label} has invalid commerce lane '{commerce_lane}'")

    if commerce_lane == "checkout":
        evidence["checkout_website_items"] += 1
        _check_checkout_sellability(
            label=label,
            item=item,
            price_map=price_map,
            variants_by_template=variants_by_template,
            variant_attributes=variant_attributes,
            failures=failures,
            evidence=evidence,
        )
    elif commerce_lane == "quote_first":
        evidence["quote_first_website_items"] += 1


def _check_checkout_sellability(
    *,
    label: str,
    item: dict[str, Any],
    price_map: dict[str, list[float]],
    variants_by_template: dict[str, list[dict[str, Any]]],
    variant_attributes: dict[str, tuple[tuple[str, str], ...]],
    failures: list[str],
    evidence: dict[str, Any],
) -> None:
    item_code = item["name"]
    if int(item.get("has_variants") or 0):
        variants = variants_by_template.get(item_code) or []
        evidence["checked_variant_templates"] += 1
        if not variants:
            failures.append(f"{label} is checkout with variants, but has no active variants")
            return
        seen: dict[tuple[tuple[str, str], ...], str] = {}
        for variant in variants:
            variant_code = variant["name"]
            evidence["checked_active_variants"] += 1
            _check_price(label=f"{label} variant {variant_code}", item_code=variant_code, price_map=price_map, failures=failures)
            combo = variant_attributes.get(variant_code) or ()
            if not combo:
                failures.append(f"{label} variant {variant_code} has no variant attributes")
                continue
            if combo in seen:
                failures.append(
                    f"{label} has duplicate active variant option tuple: {seen[combo]} and {variant_code}"
                )
            else:
                seen[combo] = variant_code
        return

    evidence["checked_sellable_item_codes"] += 1
    _check_price(label=label, item_code=item_code, price_map=price_map, failures=failures)


def _check_price(*, label: str, item_code: str, price_map: dict[str, list[float]], failures: list[str]) -> None:
    prices = price_map.get(item_code) or []
    positive_prices = [price for price in prices if price > 0]
    if not positive_prices:
        failures.append(f"{label} has no positive {PRICE_LIST} selling Item Price")
    if len(positive_prices) > 1:
        failures.append(f"{label} has multiple positive {PRICE_LIST} selling Item Prices")


def _check_orphan_prices_for_public_templates(
    *,
    rows: list[dict[str, Any]],
    items: dict[str, dict[str, Any]],
    price_map: dict[str, list[float]],
    variants_by_template: dict[str, list[dict[str, Any]]],
    warnings: list[str],
) -> None:
    public_codes = {row.get("item_code") for row in rows if row.get("item_code")}
    public_variant_codes = {
        variant["name"]
        for template in public_codes
        for variant in variants_by_template.get(template, [])
    }
    expected_public_price_codes = set(public_codes) | public_variant_codes
    for item_code in sorted(price_map):
        if item_code in expected_public_price_codes:
            continue
        item = items.get(item_code)
        if item:
            warnings.append(f"{item_code} has public-price-list price but is not expected as a public sellable code")


def _clean_route(route: Any) -> str:
    return str(route or "").strip().strip("/")
