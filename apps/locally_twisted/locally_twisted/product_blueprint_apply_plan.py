"""Dry-run planner for employee-authored product blueprints.

The planner names the ERPNext records that would be needed for a product setup,
but it does not write any of them.
"""

from __future__ import annotations

from itertools import product
from typing import Any

from locally_twisted.product_blueprint_validation import (
    READY_FOR_LOCAL_PREVIEW,
    blueprint_doc_to_dict,
    validate_blueprint,
)


SCHEMA_VERSION = "lt-product-blueprint-apply-plan-v1"
MAX_DIRECT_CHECKOUT_VARIANTS = 50


def build_apply_plan_doc(doc: Any) -> dict[str, Any]:
    """Build a dry-run apply plan for a Frappe Document-like blueprint."""
    return build_apply_plan(blueprint_doc_to_dict(doc))


def build_apply_plan(data: dict[str, Any]) -> dict[str, Any]:
    """Return a dry-run product-generation plan without mutating ERPNext."""
    validation = validate_blueprint(data)
    contract = validation.get("contract") or {}
    product_page_type = contract.get("product_page_type")
    commerce_lane = contract.get("commerce_lane")
    slug = _text(data.get("product_slug"))
    product_name = _text(data.get("product_name"))
    item_group = _text(data.get("item_group"))
    base_price = float(contract.get("base_price") or 0)
    sale_axes = [row for row in contract.get("option_rows") or [] if row.get("payload_target") == "selected_options"]
    variant_combos = _variant_combinations(sale_axes)

    blockers = list(validation.get("blockers") or [])
    if commerce_lane == "checkout" and len(variant_combos) > MAX_DIRECT_CHECKOUT_VARIANTS:
        blockers.append(
            f"Direct checkout blueprint would create {len(variant_combos)} variants; "
            f"limit is {MAX_DIRECT_CHECKOUT_VARIANTS}. Use quote-first or split the product."
        )

    plan_status = "blocked" if blockers else "dry_run_ready"
    planned_records = _planned_records(
        slug=slug,
        product_name=product_name,
        item_group=item_group,
        product_page_type=product_page_type,
        commerce_lane=commerce_lane,
        base_price=base_price,
        sale_axes=sale_axes,
        variant_combos=variant_combos if not blockers else [],
        contract=contract,
    )

    return {
        "schema_version": SCHEMA_VERSION,
        "ok": not blockers,
        "dry_run": True,
        "writes_enabled": False,
        "live_publish_enabled": False,
        "plan_status": plan_status,
        "validation_status": validation.get("validation_status"),
        "summary": _summary(plan_status, planned_records, blockers),
        "blockers": blockers,
        "warnings": list(validation.get("warnings") or []),
        "validation": validation,
        "planned_records": planned_records,
        "next_required_gate": "guarded_local_apply",
    }


def _planned_records(
    *,
    slug: str,
    product_name: str,
    item_group: str,
    product_page_type: str | None,
    commerce_lane: str | None,
    base_price: float,
    sale_axes: list[dict[str, Any]],
    variant_combos: list[dict[str, str]],
    contract: dict[str, Any],
) -> dict[str, Any]:
    has_variants = bool(variant_combos)
    base_item = {
        "doctype": "Item",
        "action": "would_upsert",
        "item_code": slug,
        "item_name": product_name,
        "item_group": item_group,
        "has_variants": 1 if has_variants else 0,
        "published": 0,
    }
    website_item = {
        "doctype": "Website Item",
        "action": "would_upsert",
        "item_code": slug,
        "web_item_name": product_name,
        "route": f"shop-items/{slug}",
        "published": 0,
        "lt_product_page_type": product_page_type,
        "lt_commerce_lane": commerce_lane,
    }
    item_attributes = [
        {
            "doctype": "Item Attribute",
            "action": "would_ensure",
            "attribute_name": row.get("axis_name"),
            "values": row.get("values") or [],
        }
        for row in sale_axes
    ]
    item_variants = [
        {
            "doctype": "Item",
            "action": "would_upsert_variant",
            "template_item_code": slug,
            "item_code": _variant_item_code(slug, combo),
            "attributes": combo,
        }
        for combo in variant_combos
    ]
    price_target_codes = [row["item_code"] for row in item_variants] or ([slug] if commerce_lane == "checkout" else [])
    item_prices = [
        {
            "doctype": "Item Price",
            "action": "would_upsert",
            "item_code": item_code,
            "price_list": "Standard Selling",
            "price_list_rate": base_price,
        }
        for item_code in price_target_codes
        if commerce_lane == "checkout"
    ]
    add_ons = [
        {
            "source_name": row.get("add_on_name"),
            "payload_target": row.get("payload_target"),
            "add_on_item": row.get("add_on_item"),
            "price_source": row.get("price_source"),
            "checkout_approved": row.get("checkout_approved"),
            "action": "would_reference_existing_item" if row.get("add_on_item") else "held_for_review",
        }
        for row in contract.get("add_on_rows") or []
    ]
    return {
        "base_item": base_item,
        "website_item": website_item,
        "item_attributes": item_attributes,
        "item_variants": item_variants,
        "item_prices": item_prices,
        "add_ons": add_ons,
        "color_recipes": contract.get("color_recipe_rows") or [],
        "conditional_prices": contract.get("conditional_price_rows") or [],
        "media": {
            "action": "held_for_later_slice",
            "reason": "Product Blueprint does not yet include media assignment fields.",
        },
    }


def _variant_combinations(sale_axes: list[dict[str, Any]]) -> list[dict[str, str]]:
    if not sale_axes:
        return []
    axis_names = [str(row.get("axis_name") or "") for row in sale_axes]
    values = [list(row.get("values") or []) for row in sale_axes]
    if any(not axis or not row_values for axis, row_values in zip(axis_names, values)):
        return []
    return [dict(zip(axis_names, combo)) for combo in product(*values)]


def _variant_item_code(slug: str, combo: dict[str, str]) -> str:
    suffix = "-".join(_code_part(value) for value in combo.values())
    return f"{slug}-{suffix}" if suffix else slug


def _code_part(value: str) -> str:
    cleaned = "".join(ch for ch in value.upper() if ch.isalnum())
    return (cleaned[:6] or "VAR").strip()


def _summary(plan_status: str, planned_records: dict[str, Any], blockers: list[str]) -> str:
    if plan_status != "dry_run_ready":
        return f"Apply plan blocked: {len(blockers)} issue(s) must be fixed before any local apply action."
    variant_count = len(planned_records.get("item_variants") or [])
    price_count = len(planned_records.get("item_prices") or [])
    return (
        "Dry-run ready only: would plan "
        f"{variant_count} variant(s), {price_count} price row(s), and one unpublished Website Item."
    )


def _text(value: Any) -> str:
    return str(value or "").strip()
