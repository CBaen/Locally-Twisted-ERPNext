"""Guarded local ERPNext apply path for employee product blueprints.

This module converts a validated blueprint plan into local ERPNext product
records. The employee Desk button is only a caller; this helper remains the
final write boundary and requires an explicit local-write flag plus confirmation
token.
"""

from __future__ import annotations

import json
from typing import Any

from locally_twisted.product_blueprint_apply_plan import build_apply_plan, build_apply_plan_doc
from locally_twisted.product_blueprint_validation import blueprint_doc_to_dict


SCHEMA_VERSION = "lt-product-blueprint-local-apply-v1"
LOCAL_APPLY_CONFIRMATION = "LOCAL_ONLY_BLUEPRINT_APPLY"
PRICE_LIST = "Standard Selling"


class ProductBlueprintApplyError(Exception):
    """Raised when a blueprint cannot be applied to local ERPNext records."""


def build_local_apply_preview(data: dict[str, Any]) -> dict[str, Any]:
    """Return a no-write local apply preview for pure tests and Desk evidence."""
    plan = build_apply_plan(data)
    blockers = _plan_blockers(plan)
    planned = plan.get("planned_records") or {}
    return {
        "schema_version": SCHEMA_VERSION,
        "ok": not blockers,
        "mode": "local_apply_preview",
        "dry_run": True,
        "writes_enabled": False,
        "live_publish_enabled": False,
        "website_item_published": 0,
        "can_apply_locally": not blockers,
        "blockers": blockers,
        "summary": _result_summary(planned),
        "planned_counts": _planned_counts(planned),
        "plan": plan,
    }


def validate_local_apply_request(
    plan: dict[str, Any],
    *,
    allow_writes: bool = False,
    confirmation: str | None = None,
) -> dict[str, Any]:
    """Validate the explicit write gate for local-only blueprint apply."""
    blockers = _plan_blockers(plan)
    if not allow_writes:
        blockers.append("Local apply requires allow_writes=True.")
    if confirmation != LOCAL_APPLY_CONFIRMATION:
        blockers.append(f"Local apply requires confirmation token {LOCAL_APPLY_CONFIRMATION}.")
    return {
        "schema_version": SCHEMA_VERSION,
        "ok": not blockers,
        "writes_enabled": allow_writes and not blockers,
        "live_publish_enabled": False,
        "website_item_published": 0,
        "blockers": blockers,
    }


def apply_blueprint_locally(
    doc: Any,
    *,
    allow_writes: bool = False,
    confirmation: str | None = None,
) -> dict[str, Any]:
    """Apply a validated blueprint to local ERPNext records without committing."""
    plan = build_apply_plan_doc(doc)
    gate = validate_local_apply_request(plan, allow_writes=allow_writes, confirmation=confirmation)
    if not gate["ok"]:
        raise ProductBlueprintApplyError("Local blueprint apply blocked: " + "; ".join(gate["blockers"]))

    import frappe
    from locally_twisted.owner_catalog_guard import catalog_guard_context

    data = blueprint_doc_to_dict(doc)
    planned = plan["planned_records"]
    _guard_existing_targets(frappe, doc, planned)

    with catalog_guard_context("blueprint_local_apply"):
        attributes = [
            _ensure_item_attribute(frappe, row["attribute_name"], row.get("values") or [])
            for row in planned.get("item_attributes") or []
        ]
        template_item = _upsert_template_item(frappe, planned["base_item"], planned, data)
        variants = [_upsert_variant(frappe, template_item, row) for row in planned.get("item_variants") or []]
        prices = [_upsert_item_price(frappe, row) for row in planned.get("item_prices") or []]
        website_item = _upsert_website_item(frappe, template_item, planned["website_item"], data)
        _write_blueprint_targets(frappe, doc, template_item, website_item)
        cache_result = _rebuild_variant_cache(frappe, template_item) if variants else {"attempted": False}
        frappe.clear_cache()

    return {
        "schema_version": SCHEMA_VERSION,
        "ok": True,
        "mode": "local_apply",
        "writes_enabled": True,
        "live_publish_enabled": False,
        "website_item_published": 0,
        "blueprint": getattr(doc, "name", None),
        "item_code": template_item,
        "website_item": website_item,
        "item_attributes": attributes,
        "variants": variants,
        "item_prices": prices,
        "cache": cache_result,
        "summary": (
            f"Applied local records for {template_item}: "
            f"{len(variants)} variant(s), {len(prices)} price row(s), one unpublished Website Item."
        ),
    }


def execute(
    blueprint_name: str,
    allow_writes: bool = False,
    confirmation: str | None = None,
) -> str:
    """Bench entrypoint for guarded local-only blueprint apply."""
    import frappe

    doc = frappe.get_doc("LT Product Blueprint", blueprint_name)
    result = apply_blueprint_locally(doc, allow_writes=allow_writes, confirmation=confirmation)
    rendered = json.dumps(result, indent=2, sort_keys=True)
    print(rendered)
    return rendered


def _plan_blockers(plan: dict[str, Any]) -> list[str]:
    blockers = list(plan.get("blockers") or [])
    if not plan.get("ok"):
        blockers.extend(row for row in plan.get("blockers") or [] if row not in blockers)
    if plan.get("live_publish_enabled"):
        blockers.append("Apply plan attempted to enable live publishing.")
    planned = plan.get("planned_records") or {}
    website = planned.get("website_item") or {}
    if int(website.get("published") or 0) != 0:
        blockers.append("Local apply only supports unpublished Website Items.")
    duplicate_codes = _duplicate_variant_codes(planned.get("item_variants") or [])
    if duplicate_codes:
        blockers.append(f"Variant item codes must be unique before local apply: {', '.join(duplicate_codes)}.")
    return blockers


def _duplicate_variant_codes(item_variants: list[dict[str, Any]]) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for row in item_variants:
        code = str(row.get("item_code") or "").strip()
        if not code:
            continue
        if code in seen:
            duplicates.add(code)
        seen.add(code)
    return sorted(duplicates)


def _planned_counts(planned: dict[str, Any]) -> dict[str, int]:
    return {
        "item_attributes": len(planned.get("item_attributes") or []),
        "item_variants": len(planned.get("item_variants") or []),
        "item_prices": len(planned.get("item_prices") or []),
        "website_items": 1 if planned.get("website_item") else 0,
    }


def _result_summary(planned: dict[str, Any]) -> str:
    counts = _planned_counts(planned)
    return (
        "Local apply preview only: would write "
        f"{counts['item_variants']} variant(s), {counts['item_prices']} price row(s), "
        "and one unpublished Website Item."
    )


def _guard_existing_targets(frappe, doc: Any, planned: dict[str, Any]) -> None:
    base_code = planned["base_item"]["item_code"]
    existing_item = frappe.db.exists("Item", base_code)
    if existing_item and _text(getattr(doc, "target_item_code", "")) != base_code:
        raise ProductBlueprintApplyError(
            f"Local apply found existing Item {base_code}. Link the blueprint target first or choose a new slug."
        )

    existing_website_item = frappe.db.exists("Website Item", {"item_code": base_code})
    if existing_website_item and _text(getattr(doc, "target_website_item", "")) != existing_website_item:
        raise ProductBlueprintApplyError(
            "Local apply found an existing Website Item for "
            f"{base_code}. Link the blueprint target first or choose a new slug."
        )

    item_group = planned["base_item"]["item_group"]
    if not frappe.db.exists("Item Group", item_group):
        raise ProductBlueprintApplyError(f"Item Group does not exist: {item_group}")


def _ensure_item_attribute(frappe, attribute_name: str, values: list[str]) -> str:
    clean_name = _text(attribute_name)
    if not clean_name:
        raise ProductBlueprintApplyError("Item Attribute name cannot be blank.")
    existing = frappe.db.exists("Item Attribute", clean_name) or frappe.db.get_value(
        "Item Attribute", {"attribute_name": clean_name}, "name"
    )
    if existing:
        doc = frappe.get_doc("Item Attribute", existing)
    else:
        doc = frappe.get_doc(
            {
                "doctype": "Item Attribute",
                "attribute_name": clean_name,
                "numeric_values": 0,
                "item_attribute_values": [],
            }
        )

    existing_values = {_text(row.attribute_value) for row in doc.item_attribute_values or []}
    used_abbrs = {_text(row.abbr) for row in doc.item_attribute_values or []}
    changed = False
    for value in values:
        clean_value = _text(value)
        if not clean_value or clean_value in existing_values:
            continue
        abbr = _make_abbr(clean_value, used_abbrs)
        doc.append("item_attribute_values", {"attribute_value": clean_value, "abbr": abbr})
        existing_values.add(clean_value)
        used_abbrs.add(abbr)
        changed = True

    if existing:
        if changed:
            # Permission bypass is guarded by the local-only blueprint apply gate.
            doc.save(ignore_permissions=True)
    else:
        # Permission bypass is guarded by the local-only blueprint apply gate.
        doc.insert(ignore_permissions=True)
    return doc.name


def _upsert_template_item(frappe, base_item: dict[str, Any], planned: dict[str, Any], data: dict[str, Any]) -> str:
    item_code = base_item["item_code"]
    has_variants = 1 if planned.get("item_variants") else 0
    attr_names = [row["attribute_name"] for row in planned.get("item_attributes") or []]
    description = _text(data.get("product_summary")) or base_item["item_name"]
    payload = {
        "item_name": base_item["item_name"][:140],
        "item_group": base_item["item_group"],
        "stock_uom": "Nos",
        "is_stock_item": 0,
        "is_sales_item": 1,
        "is_purchase_item": 0,
        "include_item_in_manufacturing": 0,
        "description": description,
        "has_variants": has_variants,
        "variant_based_on": "Item Attribute" if has_variants else None,
    }
    if frappe.db.exists("Item", item_code):
        item = frappe.get_doc("Item", item_code)
        if bool(item.has_variants) != bool(has_variants):
            raise ProductBlueprintApplyError(f"Existing Item {item_code} has a different variant structure.")
        for fieldname, value in payload.items():
            setattr(item, fieldname, value)
        item.attributes = []
        for attr_name in attr_names:
            item.append("attributes", {"attribute": attr_name})
        # Permission bypass is guarded by blueprint target collision checks and local apply confirmation.
        item.save(ignore_permissions=True)
        return item.name

    item = frappe.get_doc({"doctype": "Item", "item_code": item_code, **payload})
    for attr_name in attr_names:
        item.append("attributes", {"attribute": attr_name})
    # Permission bypass is guarded by blueprint target collision checks and local apply confirmation.
    item.insert(ignore_permissions=True)
    return item.name


def _upsert_variant(frappe, template_item: str, variant_plan: dict[str, Any]) -> str:
    from erpnext.controllers.item_variant import ItemVariantExistsError, create_variant, get_variant

    args = dict(variant_plan.get("attributes") or {})
    try:
        existing = get_variant(template_item, args=args)
    except Exception:
        existing = None
    if existing:
        return existing

    item_code = variant_plan["item_code"]
    if frappe.db.exists("Item", item_code):
        item = frappe.get_doc("Item", item_code)
        if item.variant_of != template_item:
            raise ProductBlueprintApplyError(f"Variant item code already exists outside this template: {item_code}")
        return item.name

    try:
        variant = create_variant(template_item, args=args)
        variant.item_code = item_code
        variant.item_name = _variant_item_name(frappe, template_item, args)
        # Permission bypass is guarded by variant-template checks and local apply confirmation.
        variant.insert(ignore_permissions=True)
        return variant.name
    except ItemVariantExistsError:
        existing = get_variant(template_item, args=args)
        if existing:
            return existing
        raise


def _upsert_item_price(frappe, price_plan: dict[str, Any]) -> str:
    item_code = price_plan["item_code"]
    price = float(price_plan["price_list_rate"])
    existing = frappe.db.exists(
        "Item Price",
        {
            "item_code": item_code,
            "price_list": PRICE_LIST,
            "selling": 1,
        },
    )
    if existing:
        doc = frappe.get_doc("Item Price", existing)
        doc.price_list_rate = price
        doc.currency = "USD"
        doc.selling = 1
        # Permission bypass is guarded by local apply confirmation and exact Item Price lookup.
        doc.save(ignore_permissions=True)
        return doc.name
    doc = frappe.get_doc(
        {
            "doctype": "Item Price",
            "item_code": item_code,
            "price_list": PRICE_LIST,
            "price_list_rate": price,
            "currency": "USD",
            "selling": 1,
        }
    )
    # Permission bypass is guarded by local apply confirmation and exact Item Price plan rows.
    doc.insert(ignore_permissions=True)
    return doc.name


def _upsert_website_item(frappe, template_item: str, website_plan: dict[str, Any], data: dict[str, Any]) -> str:
    existing = frappe.db.exists("Website Item", {"item_code": template_item})
    route = _route_for(frappe, website_plan["item_code"], _text(data.get("item_group")))
    route_owner = frappe.db.get_value("Website Item", {"route": route}, "name")
    if route_owner and route_owner != existing:
        raise ProductBlueprintApplyError(f"Website Item route is already in use: {route}")

    if existing:
        doc = frappe.get_doc("Website Item", existing)
    else:
        from webshop.webshop.doctype.website_item.website_item import make_website_item

        doc = make_website_item(frappe.get_doc("Item", template_item), save=False)
        # Permission bypass is guarded by route collision checks and local apply confirmation.
        doc.insert(ignore_permissions=True)

    doc.web_item_name = website_plan["web_item_name"][:140]
    doc.item_group = _text(data.get("item_group"))
    doc.published = 0
    doc.route = route
    summary = _text(data.get("product_summary"))
    doc.short_description = summary[:140] if summary else doc.web_item_name
    doc.web_long_description = summary
    meta = frappe.get_meta("Website Item")
    if meta.has_field("lt_product_page_type"):
        doc.lt_product_page_type = website_plan.get("lt_product_page_type")
    if meta.has_field("lt_commerce_lane"):
        doc.lt_commerce_lane = website_plan.get("lt_commerce_lane")
    # Permission bypass is guarded by route collision checks and local apply confirmation.
    doc.save(ignore_permissions=True)
    return doc.name


def _write_blueprint_targets(frappe, doc: Any, item_code: str, website_item: str) -> None:
    if not getattr(doc, "doctype", None) or not getattr(doc, "name", None):
        return
    frappe.db.set_value(
        doc.doctype,
        doc.name,
        {
            "target_item_code": item_code,
            "target_website_item": website_item,
        },
        update_modified=True,
    )
    doc.target_item_code = item_code
    doc.target_website_item = website_item


def _rebuild_variant_cache(frappe, template_item: str) -> dict[str, Any]:
    try:
        from webshop.webshop.variant_selector.utils import ItemVariantsCacheManager

        ItemVariantsCacheManager(template_item).rebuild_cache()
        return {"attempted": True, "ok": True}
    except Exception as exc:
        frappe.log_error(
            f"Product blueprint local apply variant cache rebuild failed for {template_item}: {exc}",
            title="LT Product Blueprint local apply",
        )
        return {"attempted": True, "ok": False, "error": str(exc)}


def _route_for(frappe, slug: str, item_group: str) -> str:
    group_route = frappe.db.get_value("Item Group", item_group, "route") or "shop-items"
    return f"{group_route}/{slug}".strip("/")


def _variant_item_name(frappe, template_item: str, args: dict[str, str]) -> str:
    template_name = frappe.db.get_value("Item", template_item, "item_name") or template_item
    suffix = " / ".join(str(value) for value in args.values())
    return f"{template_name} - {suffix}"[:140]


def _make_abbr(value: str, used: set[str]) -> str:
    base = "".join(ch for ch in value.upper() if ch.isalnum())[:3] or "VAR"
    candidate = base
    counter = 1
    while candidate in used:
        suffix = str(counter)
        candidate = f"{base[: max(1, 3 - len(suffix))]}{suffix}"[:3]
        counter += 1
    return candidate


def _text(value: Any) -> str:
    return str(value or "").strip()
