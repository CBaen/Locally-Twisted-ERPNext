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
from locally_twisted.product_setup_runtime import build_product_setup_schema


SCHEMA_VERSION = "lt-product-blueprint-apply-plan-v1"
MAX_DIRECT_CHECKOUT_VARIANTS = 50


def build_apply_plan_doc(doc: Any) -> dict[str, Any]:
    """Build a dry-run apply plan for a Frappe Document-like blueprint."""
    return build_apply_plan(blueprint_doc_to_dict(doc))


def build_apply_plan(data: dict[str, Any]) -> dict[str, Any]:
    """Return a dry-run product-generation plan without mutating ERPNext."""
    validation = validate_blueprint(data)
    setup_schema = build_product_setup_schema(data)
    contract = validation.get("contract") or {}
    product_page_type = contract.get("product_page_type")
    commerce_lane = contract.get("commerce_lane")
    operating_brand = _text(contract.get("operating_brand"))
    operating_brand_authority_state = _text(contract.get("operating_brand_authority_state")) or "missing"
    slug = _text(data.get("product_slug"))
    product_name = _text(data.get("product_name"))
    item_group = _text(data.get("item_group"))
    base_price = float(contract.get("base_price") or 0)
    shop_visibility = _text(contract.get("shop_visibility")) or "Keep current"
    exact_price_rows = list(contract.get("price_rows") or [])
    sale_axes = [
        {
            "axis_name": row.get("label"),
            "values": row.get("values") or [],
        }
        for row in setup_schema.get("selection_groups") or []
        if row.get("sku_defining")
    ]
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
        operating_brand=operating_brand,
        operating_brand_authority_state=operating_brand_authority_state,
        base_price=base_price,
        shop_visibility=shop_visibility,
        exact_price_rows=exact_price_rows,
        sale_axes=sale_axes,
        variant_combos=variant_combos if not blockers else [],
        contract=contract,
        setup_schema=setup_schema,
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
    operating_brand: str,
    operating_brand_authority_state: str,
    base_price: float,
    shop_visibility: str,
    exact_price_rows: list[dict[str, Any]],
    sale_axes: list[dict[str, Any]],
    variant_combos: list[dict[str, str]],
    contract: dict[str, Any],
    setup_schema: dict[str, Any],
) -> dict[str, Any]:
    has_variants = bool(variant_combos)
    base_item = {
        "doctype": "Item",
        "action": "would_upsert",
        "item_code": slug,
        "item_name": product_name,
        "item_group": item_group,
        "operating_brand": operating_brand,
        "operating_brand_authority_state": operating_brand_authority_state,
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
        "requested_shop_visibility": shop_visibility,
        "shop_visibility": "local_preview_unpublished",
        "operating_brand": operating_brand,
        "operating_brand_authority_state": operating_brand_authority_state,
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
    item_prices = _planned_item_prices(
        slug=slug,
        commerce_lane=commerce_lane,
        base_price=base_price,
        item_variants=item_variants,
        exact_price_rows=exact_price_rows,
    )
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
        "product_setup_schema": setup_schema,
        "gallery": {
            "action": "would_apply_approved_gallery_images"
            if setup_schema.get("gallery_images")
            else "held_until_gallery_images_exist",
            "images": setup_schema.get("gallery_images") or [],
            "reason": "Approved Product Setup gallery images become the product's Website Slideshow.",
        },
        "media": {
            "action": "would_apply_approved_rules" if setup_schema.get("media_rules") else "held_until_media_rules_exist",
            "rules": setup_schema.get("media_rules") or [],
            "reason": "Only approved Product Setup media rules can change customer-facing images.",
        },
        "content_rules": {
            "action": "would_apply_approved_rules"
            if setup_schema.get("content_rules")
            else "held_until_content_rules_exist",
            "rules": setup_schema.get("content_rules") or [],
            "reason": "Only approved Product Setup copy rules can change customer-facing page content.",
        },
    }


def _planned_item_prices(
    *,
    slug: str,
    commerce_lane: str | None,
    base_price: float,
    item_variants: list[dict[str, Any]],
    exact_price_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if commerce_lane != "checkout":
        return []
    rows = [
        {
            "doctype": "Item Price",
            "action": "would_upsert",
            "item_code": row["item_code"],
            "price_list": "Standard Selling",
            "price_list_rate": row["price"],
            "option_summary": row.get("option_summary"),
        }
        for row in exact_price_rows
        if row.get("enabled_for_checkout")
    ]
    if rows:
        return rows
    price_target_codes = [row["item_code"] for row in item_variants] or [slug]
    return [
        {
            "doctype": "Item Price",
            "action": "would_upsert",
            "item_code": item_code,
            "price_list": "Standard Selling",
            "price_list_rate": base_price,
        }
        for item_code in price_target_codes
    ]


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
