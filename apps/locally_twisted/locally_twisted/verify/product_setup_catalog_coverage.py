"""Verify every storefront product has an owner-editable Product Setup record."""
from __future__ import annotations

from typing import Any

import frappe
from frappe.utils import flt

from locally_twisted.product_setup_runtime import ACTIVE_SETUP_STATUSES, get_product_setup_schema_json


UNSAFE_CUSTOMER_SCHEMA_TERMS = (
    "super shape",
)


def run() -> dict[str, Any]:
    website_items = frappe.get_all(
        "Website Item",
        filters={"item_code": ["!=", ""]},
        fields=[
            "name",
            "item_code",
            "published",
            "website_image",
            "slideshow",
            "lt_product_page_type",
            "lt_commerce_lane",
        ],
        order_by="item_code asc",
    )
    blueprints = {
        row["product_slug"]: row
        for row in frappe.get_all(
            "LT Product Blueprint",
            fields=[
                "name",
                "product_slug",
                "target_item_code",
                "target_website_item",
                "buying_path",
                "publish_status",
                "shop_visibility",
                "operator_notes",
            ],
        )
    }

    failures: list[str] = []
    evidence = {
        "website_items": len(website_items),
        "blueprints": len(blueprints),
        "checkout_products": 0,
        "checked_price_rows": 0,
        "checked_variant_media_rows": 0,
        "checked_gallery_rows": 0,
        "checked_customer_safe_setup_schemas": 0,
        "draft_backfilled_blueprints": 0,
        "active_preview_blueprints": 0,
    }

    for row in website_items:
        item_code = row["item_code"]
        blueprint = blueprints.get(item_code)
        if not blueprint:
            failures.append(f"{item_code} has no LT Product Blueprint owner-edit record")
            continue
        if blueprint.get("target_item_code") != item_code:
            failures.append(f"{item_code} Product Setup target_item_code is {blueprint.get('target_item_code')!r}")
        if blueprint.get("target_website_item") != row["name"]:
            failures.append(f"{item_code} Product Setup target_website_item is {blueprint.get('target_website_item')!r}")
        if _published_checkout(row):
            if blueprint.get("publish_status") not in ACTIVE_SETUP_STATUSES:
                failures.append(f"{item_code} published checkout Product Setup must be active for preview/runtime media")
            else:
                evidence["active_preview_blueprints"] += 1
                _check_customer_safe_setup_schema(item_code, failures, evidence)
        elif "current storefront catalog for guarded owner editing" in (blueprint.get("operator_notes") or ""):
            if blueprint.get("publish_status") != "Draft":
                failures.append(f"{item_code} non-checkout backfilled Product Setup must stay Draft until reviewed")
            else:
                evidence["draft_backfilled_blueprints"] += 1
        if row.get("lt_commerce_lane") == "checkout":
            evidence["checkout_products"] += 1
            _check_checkout_price_rows(item_code, blueprint["name"], failures, evidence)
        _check_variant_media_rows(row, blueprint["name"], failures, evidence)
        _check_gallery_rows(row, blueprint["name"], failures, evidence)

    return {
        "ok": not failures,
        "evidence": evidence,
        "failures": failures,
    }


def execute() -> dict[str, Any]:
    return run()


def _check_checkout_price_rows(
    item_code: str,
    blueprint_name: str,
    failures: list[str],
    evidence: dict[str, int],
) -> None:
    expected_codes = _sellable_codes(item_code)
    rows = frappe.get_all(
        "LT Product Blueprint Price",
        filters={"parent": blueprint_name, "enabled_for_checkout": 1},
        fields=["item_code", "price"],
    )
    prices = {row["item_code"]: flt(row.get("price")) for row in rows}
    for code in expected_codes:
        evidence["checked_price_rows"] += 1
        if prices.get(code, 0) <= 0:
            failures.append(f"{item_code} Product Setup missing positive checkout price row for {code}")


def _sellable_codes(item_code: str) -> list[str]:
    item = frappe.get_doc("Item", item_code)
    if int(item.get("has_variants") or 0):
        return frappe.get_all(
            "Item",
            filters={"variant_of": item_code, "disabled": 0},
            pluck="name",
            order_by="name asc",
        )
    return [item_code]


def _published_checkout(website_item: dict[str, Any]) -> bool:
    return int(website_item.get("published") or 0) and website_item.get("lt_commerce_lane") == "checkout"


def _check_variant_media_rows(
    website_item: dict[str, Any],
    blueprint_name: str,
    failures: list[str],
    evidence: dict[str, int],
) -> None:
    item_code = website_item["item_code"]
    fallback_image = website_item.get("website_image") or ""
    variants = frappe.get_all(
        "Item",
        filters={"variant_of": item_code, "disabled": 0, "image": ["!=", ""]},
        fields=["name", "image"],
    )
    if not variants:
        return
    rows = frappe.get_all(
        "LT Product Blueprint Media Rule",
        filters={"parent": blueprint_name},
        fields=["variant_item", "image", "approved_for_customer"],
    )
    media_by_variant = {row["variant_item"]: row for row in rows if row.get("variant_item")}
    simple_checkout = (
        website_item.get("lt_product_page_type") == "simple_product"
        and website_item.get("lt_commerce_lane") == "checkout"
    )
    for variant in variants:
        image = variant.get("image")
        if not image or image == fallback_image:
            continue
        evidence["checked_variant_media_rows"] += 1
        rule = media_by_variant.get(variant["name"])
        if not rule:
            failures.append(f"{item_code} Product Setup missing variant media row for {variant['name']}")
            continue
        if rule.get("image") != image:
            failures.append(f"{item_code} Product Setup variant media for {variant['name']} points at {rule.get('image')!r}")
        if simple_checkout and not int(rule.get("approved_for_customer") or 0):
            failures.append(f"{item_code} simple checkout variant media for {variant['name']} must be approved")


def _check_gallery_rows(
    website_item: dict[str, Any],
    blueprint_name: str,
    failures: list[str],
    evidence: dict[str, int],
) -> None:
    slideshow = website_item.get("slideshow")
    if not slideshow:
        return
    expected = frappe.get_all(
        "Website Slideshow Item",
        filters={"parent": slideshow},
        fields=["image"],
        order_by="idx asc",
    )
    if not expected:
        return
    actual = frappe.get_all(
        "LT Product Blueprint Gallery Image",
        filters={"parent": blueprint_name},
        fields=["image", "approved_for_customer"],
        order_by="idx asc",
    )
    actual_by_image = {row["image"]: row for row in actual if row.get("image")}
    for row in expected:
        evidence["checked_gallery_rows"] += 1
        match = actual_by_image.get(row.get("image"))
        if not match:
            failures.append(f"{website_item['item_code']} Product Setup missing gallery image {row.get('image')!r}")
        elif not int(match.get("approved_for_customer") or 0):
            failures.append(f"{website_item['item_code']} Product Setup gallery image {row.get('image')!r} must be approved")


def _check_customer_safe_setup_schema(
    item_code: str,
    failures: list[str],
    evidence: dict[str, int],
) -> None:
    evidence["checked_customer_safe_setup_schemas"] += 1
    schema_text = get_product_setup_schema_json(item_code).casefold()
    for term in UNSAFE_CUSTOMER_SCHEMA_TERMS:
        if term.casefold() in schema_text:
            failures.append(f"{item_code} Product Setup customer schema still exposes {term!r}")
