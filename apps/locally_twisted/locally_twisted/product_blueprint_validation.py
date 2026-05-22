"""Validation helpers for employee-authored product blueprints.

This module is deliberately read-only: it classifies a proposed product setup
and names blockers, but it does not create Items, Website Items, prices, files,
or public routes.
"""

from __future__ import annotations

import re
from typing import Any

from locally_twisted.product_setup_runtime import BEHAVIOR_TO_PAYLOAD_TARGET, ROLE_TO_BEHAVIOR


SCHEMA_VERSION = "lt-product-blueprint-v1"

READY_FOR_LOCAL_PREVIEW = "Ready For Local Preview"
BLOCKED = "Blocked"
NOT_CHECKED = "Not checked"

PAGE_TEMPLATE_TO_CONTRACT = {
    "Ready-to-order page": "simple_product",
    "Configurable product page": "complex_custom_product",
    # Legacy value kept readable so old local Product Setup drafts fail safe
    # through the same contract instead of becoming invalid on load.
    "Custom quote page": "complex_custom_product",
}

BUYING_PATH_TO_CONTRACT = {
    "Direct checkout": "checkout",
    "Quote first": "quote_first",
    "Needs review": "needs_review",
}

OPTION_ROLE_TO_PAYLOAD_TARGET = {
    "Sale unit option": "selected_options",
    "Color recipe": "color_recipes",
    "Add-on": "add_ons",
    "Review only": "quote_context",
}

PREVIEW_STATUSES = {"Local Preview Ready", "Staging Ready"}
LIVE_STATUSES = {"Approved For Live"}
STATUS_OPTIONS = {
    "Draft",
    "Needs Product Review",
    "Needs Price Review",
    "Needs Media Review",
    *PREVIEW_STATUSES,
    *LIVE_STATUSES,
}
SHOP_VISIBILITY_OPTIONS = {"Keep current", "Visible in shop", "Hidden from shop"}

SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def validate_blueprint_doc(doc: Any) -> dict[str, Any]:
    """Validate a Frappe Document-like product blueprint."""
    return validate_blueprint(blueprint_doc_to_dict(doc))


def blueprint_doc_to_dict(doc: Any) -> dict[str, Any]:
    """Convert a Frappe Document-like object into the pure validation shape."""
    return {
        "product_name": _text(getattr(doc, "product_name", "")),
        "product_slug": _text(getattr(doc, "product_slug", "")),
        "item_group": _text(getattr(doc, "item_group", "")),
        "page_template": _text(getattr(doc, "page_template", "")),
        "buying_path": _text(getattr(doc, "buying_path", "")),
        "publish_status": _text(getattr(doc, "publish_status", "")) or "Draft",
        "shop_visibility": _text(getattr(doc, "shop_visibility", "")) or "Keep current",
        "target_item_code": _text(getattr(doc, "target_item_code", "")),
        "base_price": getattr(doc, "base_price", None),
        "price_rows": [_row_to_dict(row) for row in getattr(doc, "price_rows", [])],
        "product_summary": _text(getattr(doc, "product_summary", "")),
        "product_story": _text(getattr(doc, "product_story", "")),
        "product_details": _text(getattr(doc, "product_details", "")),
        "primary_image": _text(getattr(doc, "primary_image", "")),
        "gallery_image_rows": [_row_to_dict(row) for row in getattr(doc, "gallery_image_rows", [])],
        "option_rows": [_row_to_dict(row) for row in getattr(doc, "option_rows", [])],
        "color_recipe_rows": [_row_to_dict(row) for row in getattr(doc, "color_recipe_rows", [])],
        "add_on_rows": [_row_to_dict(row) for row in getattr(doc, "add_on_rows", [])],
        "conditional_price_rows": [
            _row_to_dict(row) for row in getattr(doc, "conditional_price_rows", [])
        ],
        "media_rule_rows": [_row_to_dict(row) for row in getattr(doc, "media_rule_rows", [])],
        "content_rule_rows": [_row_to_dict(row) for row in getattr(doc, "content_rule_rows", [])],
    }


def validate_blueprint(data: dict[str, Any]) -> dict[str, Any]:
    """Return a fail-loud readiness report for a product blueprint."""
    blockers: list[str] = []
    warnings: list[str] = []
    save_blockers: list[str] = []

    product_name = _text(data.get("product_name"))
    slug = _text(data.get("product_slug"))
    item_group = _text(data.get("item_group"))
    page_template = _text(data.get("page_template"))
    buying_path = _text(data.get("buying_path"))
    publish_status = _text(data.get("publish_status")) or "Draft"
    shop_visibility = _text(data.get("shop_visibility")) or "Keep current"
    target_item_code = _text(data.get("target_item_code"))
    base_price = _float(data.get("base_price"))

    if not product_name:
        blockers.append("Product name is required.")
    if not slug:
        blockers.append("Product slug is required.")
    elif not SLUG_PATTERN.match(slug):
        blockers.append("Product slug must use lowercase letters, numbers, and single hyphens only.")
    if not item_group:
        blockers.append("Item Group is required so ERPNext knows where the product belongs.")
    if page_template not in PAGE_TEMPLATE_TO_CONTRACT:
        blockers.append("Page Template must be Ready-to-order page or Configurable product page.")
    if buying_path not in BUYING_PATH_TO_CONTRACT:
        blockers.append("Buying Path must be Direct checkout, Quote first, or Needs review.")
    if publish_status not in STATUS_OPTIONS:
        blockers.append(f"Unknown product setup status: {publish_status}.")
    if shop_visibility not in SHOP_VISIBILITY_OPTIONS:
        blockers.append("Shop Visibility must be Keep current, Visible in shop, or Hidden from shop.")

    product_page_type = PAGE_TEMPLATE_TO_CONTRACT.get(page_template)
    commerce_lane = BUYING_PATH_TO_CONTRACT.get(buying_path)

    option_rows = [_normalize_option(row) for row in data.get("option_rows") or []]
    color_rows = [_normalize_color_recipe(row) for row in data.get("color_recipe_rows") or []]
    add_on_rows = [_normalize_add_on(row) for row in data.get("add_on_rows") or []]
    conditional_price_rows = [_normalize_conditional_price(row) for row in data.get("conditional_price_rows") or []]
    exact_price_rows = [_normalize_price_row(row) for row in data.get("price_rows") or []]
    gallery_image_rows = [_normalize_gallery_image(row) for row in data.get("gallery_image_rows") or []]
    media_rule_rows = [_normalize_media_rule(row) for row in data.get("media_rule_rows") or []]
    content_rule_rows = [_normalize_content_rule(row) for row in data.get("content_rule_rows") or []]

    if buying_path == "Direct checkout" and base_price <= 0 and not _has_positive_checkout_price_rows(exact_price_rows):
        blockers.append("Direct checkout products need a base checkout price or exact checkout price rows.")
    if shop_visibility == "Visible in shop" and not _has_customer_facing_product_image(
        primary_image=_text(data.get("primary_image")),
        gallery_image_rows=gallery_image_rows,
    ):
        blockers.append(
            "Visible shop products need a fallback/main product photo or at least one approved gallery photo."
        )

    _validate_options(option_rows, blockers, warnings)
    _validate_color_recipes(color_rows, blockers)
    _validate_add_ons(add_on_rows, buying_path, blockers, warnings)
    _validate_conditional_prices(conditional_price_rows, buying_path, blockers, warnings)
    _validate_exact_prices(exact_price_rows, buying_path, slug, target_item_code, blockers, warnings)
    _validate_gallery_images(gallery_image_rows, blockers, warnings)
    _validate_media_rules(media_rule_rows, blockers, warnings)
    _validate_content_rules(content_rule_rows, blockers, warnings)

    if buying_path == "Direct checkout" and not option_rows and not color_rows and not add_on_rows:
        warnings.append("Direct checkout product has no options/add-ons; confirm it is truly a simple fixed product.")

    if publish_status in LIVE_STATUSES:
        save_blockers.append("Live approval is not available from local product blueprints.")
    unsafe_price_blockers = [
        blocker for blocker in blockers if "exact checkout price rows must belong to this Product Setup" in blocker
    ]
    if unsafe_price_blockers:
        save_blockers.append("Product setup cannot save cross-product checkout price rows: " + "; ".join(unsafe_price_blockers))
    if publish_status in PREVIEW_STATUSES and blockers:
        save_blockers.append("Product setup cannot move to preview/staging while validation blockers remain.")
    if shop_visibility == "Visible in shop" and blockers:
        save_blockers.append(
            "Product setup cannot request shop visibility while validation blockers remain: "
            + "; ".join(blockers)
        )

    validation_status = READY_FOR_LOCAL_PREVIEW if not blockers else BLOCKED
    summary = _summary(validation_status, blockers, warnings)

    return {
        "schema_version": SCHEMA_VERSION,
        "ok": not blockers,
        "validation_status": validation_status,
        "summary": summary,
        "blockers": blockers,
        "warnings": warnings,
        "save_blockers": save_blockers,
        "ready_for_live": False,
        "contract": {
            "product_page_type": product_page_type,
            "commerce_lane": commerce_lane,
            "base_price": base_price,
            "shop_visibility": shop_visibility,
            "price_rows": exact_price_rows,
            "payload_target_counts": _payload_target_counts(option_rows, add_on_rows),
            "option_rows": option_rows,
            "color_recipe_rows": color_rows,
            "add_on_rows": add_on_rows,
            "conditional_price_rows": conditional_price_rows,
            "media_rule_rows": media_rule_rows,
            "gallery_image_rows": gallery_image_rows,
            "content_rule_rows": content_rule_rows,
            "product_generation_enabled": False,
            "live_publish_enabled": False,
        },
    }


def _validate_options(rows: list[dict[str, Any]], blockers: list[str], warnings: list[str]) -> None:
    seen: set[str] = set()
    for idx, row in enumerate(rows, start=1):
        label = row.get("axis_name") or f"option row {idx}"
        if not row.get("axis_name"):
            blockers.append(f"Option row {idx} needs an axis name.")
        if row.get("axis_name") in seen:
            blockers.append(f"Option axis is duplicated: {row['axis_name']}.")
        seen.add(row.get("axis_name"))
        if row.get("role") not in OPTION_ROLE_TO_PAYLOAD_TARGET:
            blockers.append(f"{label}: option role is not recognized.")
        if row.get("min_selections") < 0:
            blockers.append(f"{label}: minimum selections cannot be negative.")
        if row.get("max_selections") < 0:
            blockers.append(f"{label}: maximum selections cannot be negative.")
        if row.get("max_selections") and row.get("min_selections") > row.get("max_selections"):
            blockers.append(f"{label}: minimum selections cannot exceed maximum selections.")
        for default in row.get("default_values") or []:
            if default not in (row.get("values") or []):
                blockers.append(f"{label}: default value {default} is not in the allowed values.")
        if not row.get("values"):
            blockers.append(f"{label}: at least one value is required.")
        if row.get("pricing_behavior") == "Needs review":
            warnings.append(f"{label}: pricing needs review before this selection can be checkout-ready.")
        if row.get("role") == "Review only":
            warnings.append(f"{label}: review-only options will route through quote context, not checkout.")


def _validate_color_recipes(rows: list[dict[str, Any]], blockers: list[str]) -> None:
    for idx, row in enumerate(rows, start=1):
        label = row.get("recipe_name") or f"color recipe row {idx}"
        if not row.get("recipe_name"):
            blockers.append(f"Color recipe row {idx} needs a name.")
        if row["min_colors"] < 0:
            blockers.append(f"{label}: minimum colors cannot be negative.")
        if row["max_colors"] <= 0:
            blockers.append(f"{label}: maximum colors must be greater than zero.")
        if row["min_colors"] > row["max_colors"]:
            blockers.append(f"{label}: minimum colors cannot exceed maximum colors.")


def _validate_add_ons(
    rows: list[dict[str, Any]],
    buying_path: str,
    blockers: list[str],
    warnings: list[str],
) -> None:
    for idx, row in enumerate(rows, start=1):
        label = row.get("add_on_name") or f"add-on row {idx}"
        if not row.get("add_on_name"):
            blockers.append(f"Add-on row {idx} needs a name.")
        if row["quantity_min"] < 0 or row["quantity_max"] < 0:
            blockers.append(f"{label}: add-on quantities cannot be negative.")
        if row["quantity_max"] and row["quantity_min"] > row["quantity_max"]:
            blockers.append(f"{label}: minimum quantity cannot exceed maximum quantity.")
        if buying_path == "Direct checkout":
            if not row["checkout_approved"]:
                blockers.append(f"{label}: direct checkout add-ons require checkout approval.")
            if row["price_source"] == "Needs review":
                blockers.append(f"{label}: direct checkout add-ons need a resolved price source.")
            if row["price_source"] == "Fixed Item Price" and not row.get("add_on_item"):
                blockers.append(f"{label}: fixed-price add-ons need an ERPNext Item.")
        elif row["checkout_approved"]:
            warnings.append(f"{label}: checkout approval is ignored while the product is quote-first/review.")


def _validate_conditional_prices(
    rows: list[dict[str, Any]],
    buying_path: str,
    blockers: list[str],
    warnings: list[str],
) -> None:
    for idx, row in enumerate(rows, start=1):
        label = row.get("condition_label") or f"conditional price row {idx}"
        if not row.get("condition_label"):
            blockers.append(f"Conditional price row {idx} needs a label.")
        if not row.get("applies_when"):
            blockers.append(f"{label}: condition details are required.")
        if buying_path == "Direct checkout":
            if not row["approved_for_checkout"]:
                blockers.append(f"{label}: conditional pricing must be approved before direct checkout.")
            if row["price_behavior"] in {"Quote only", "Needs review"}:
                blockers.append(f"{label}: quote-only or review pricing cannot enter direct checkout.")
        elif row["approved_for_checkout"]:
            warnings.append(f"{label}: checkout pricing approval is ignored while the product is quote-first/review.")


def _validate_exact_prices(
    rows: list[dict[str, Any]],
    buying_path: str,
    product_slug: str,
    target_item_code: str,
    blockers: list[str],
    warnings: list[str],
) -> None:
    seen: set[str] = set()
    allowed_roots = _allowed_price_roots(product_slug, target_item_code)
    for idx, row in enumerate(rows, start=1):
        label = row.get("item_code") or f"price row {idx}"
        if not row.get("item_code"):
            blockers.append(f"Price row {idx} needs a sellable Item.")
        elif not _belongs_to_current_product(row["item_code"], allowed_roots):
            blockers.append(f"{label}: exact checkout price rows must belong to this Product Setup's Item or variants.")
        if row.get("item_code") in seen:
            blockers.append(f"Exact checkout price is duplicated for {row['item_code']}.")
        seen.add(row.get("item_code"))
        if row["enabled_for_checkout"] and row["price"] <= 0:
            blockers.append(f"{label}: checkout price must be greater than zero.")
        if buying_path != "Direct checkout" and row["enabled_for_checkout"]:
            warnings.append(f"{label}: checkout price is ignored while the product is quote-first/review.")


def _validate_gallery_images(
    rows: list[dict[str, Any]],
    blockers: list[str],
    warnings: list[str],
) -> None:
    seen: set[str] = set()
    for idx, row in enumerate(rows, start=1):
        label = row.get("heading") or f"gallery photo {idx}"
        image = row.get("image")
        if not image:
            blockers.append(f"{label}: gallery photo needs an image.")
        if image in seen:
            warnings.append(f"{label}: gallery photo image is duplicated.")
        seen.add(image)
        if image and not row.get("approved_for_customer"):
            warnings.append(f"{label}: gallery photo is saved but not approved for customer display.")


def _validate_media_rules(
    rows: list[dict[str, Any]],
    blockers: list[str],
    warnings: list[str],
) -> None:
    valid_types = {"Selection group", "Selection combination", "Exact resolved variant"}
    for idx, row in enumerate(rows, start=1):
        label = row.get("rule_name") or f"image rule {idx}"
        if not row.get("rule_name"):
            blockers.append(f"Image rule {idx} needs a rule name.")
        if row.get("rule_type") not in valid_types:
            blockers.append(f"{label}: image rule type is not recognized.")
        if row.get("rule_type") == "Selection group" and not (
            row.get("selection_group") and row.get("selection_value")
        ):
            blockers.append(f"{label}: selection-group image rules need a selection group and value.")
        if row.get("rule_type") == "Selection combination" and not row.get("selection_conditions"):
            blockers.append(f"{label}: combination image rules need selection conditions.")
        if row.get("rule_type") == "Exact resolved variant" and not row.get("variant_item"):
            blockers.append(f"{label}: exact-variant image rules need a variant item.")
        if row.get("approved_for_customer") and not row.get("image"):
            blockers.append(f"{label}: approved image rule must include an image.")
        if row.get("image") and not row.get("approved_for_customer"):
            warnings.append(f"{label}: image rule is saved but not approved for customer display.")


def _validate_content_rules(
    rows: list[dict[str, Any]],
    blockers: list[str],
    warnings: list[str],
) -> None:
    valid_types = {"Selection group", "Selection combination", "Exact resolved variant"}
    for idx, row in enumerate(rows, start=1):
        label = row.get("rule_name") or f"copy rule {idx}"
        if not row.get("rule_name"):
            blockers.append(f"Copy rule {idx} needs a rule name.")
        if row.get("rule_type") not in valid_types:
            blockers.append(f"{label}: copy rule type is not recognized.")
        if row.get("rule_type") == "Selection group" and not (
            row.get("selection_group") and row.get("selection_value")
        ):
            blockers.append(f"{label}: selection-group copy rules need a selection group and value.")
        if row.get("rule_type") == "Selection combination" and not row.get("selection_conditions"):
            blockers.append(f"{label}: combination copy rules need selection conditions.")
        if row.get("rule_type") == "Exact resolved variant" and not row.get("variant_item"):
            blockers.append(f"{label}: exact-variant copy rules need a variant item.")
        has_copy = row.get("display_title") or row.get("product_story") or row.get("product_details")
        if row.get("approved_for_customer") and not has_copy:
            blockers.append(f"{label}: approved copy rule must change a title, About This Design, or What's Included.")
        if has_copy and not row.get("approved_for_customer"):
            warnings.append(f"{label}: copy rule is saved but not approved for customer display.")


def _normalize_option(row: dict[str, Any]) -> dict[str, Any]:
    role = _text(row.get("role")) or "Sale unit option"
    selection_behavior = _text(row.get("selection_behavior")) or ROLE_TO_BEHAVIOR.get(role, "SKU-defining variant")
    payload_target = BEHAVIOR_TO_PAYLOAD_TARGET.get(selection_behavior) or OPTION_ROLE_TO_PAYLOAD_TARGET.get(role)
    values = _split_values(row.get("values"))
    return {
        "axis_name": _text(row.get("axis_name")),
        "role": role,
        "selection_behavior": selection_behavior,
        "control_type": _text(row.get("control_type")) or ("Multi select" if _int(row.get("max_selections")) > 1 else "Single select"),
        "required": _as_bool(row.get("required")),
        "min_selections": _int(row.get("min_selections")),
        "max_selections": _int(row.get("max_selections")),
        "values": values,
        "default_values": _split_values(row.get("default_values")),
        "payload_target": payload_target,
        "pricing_behavior": _text(row.get("pricing_behavior")) or "Included in base price",
        "media_behavior": _text(row.get("media_behavior")) or "No image change",
        "document_output": _text(row.get("document_output")) or "Customer and operator",
        "operator_note": _text(row.get("operator_note")),
    }


def _normalize_color_recipe(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "recipe_name": _text(row.get("recipe_name")),
        "min_colors": _int(row.get("min_colors")),
        "max_colors": _int(row.get("max_colors")),
        "palette_source": _text(row.get("palette_source")),
        "operator_note": _text(row.get("operator_note")),
    }


def _normalize_add_on(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "add_on_name": _text(row.get("add_on_name")),
        "add_on_item": _text(row.get("add_on_item")),
        "price_source": _text(row.get("price_source")) or "Needs review",
        "requires_value": _as_bool(row.get("requires_value")),
        "quantity_min": _int(row.get("quantity_min")),
        "quantity_max": _int(row.get("quantity_max")),
        "checkout_approved": _as_bool(row.get("checkout_approved")),
        "payload_target": "add_ons" if _as_bool(row.get("checkout_approved")) else "quote_context",
    }


def _normalize_conditional_price(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "condition_label": _text(row.get("condition_label")),
        "applies_when": _text(row.get("applies_when")),
        "price_behavior": _text(row.get("price_behavior")) or "Needs review",
        "amount": _text(row.get("amount")),
        "approved_for_checkout": _as_bool(row.get("approved_for_checkout")),
    }


def _normalize_price_row(row: dict[str, Any]) -> dict[str, Any]:
    enabled = row.get("enabled_for_checkout")
    return {
        "item_code": _text(row.get("item_code")),
        "option_summary": _text(row.get("option_summary")),
        "price": _float(row.get("price")),
        "enabled_for_checkout": True if enabled is None else _as_bool(enabled),
        "operator_note": _text(row.get("operator_note")),
    }


def _normalize_gallery_image(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "image": _text(row.get("image")),
        "heading": _text(row.get("heading")),
        "description": _text(row.get("description")),
        "approved_for_customer": _as_bool(row.get("approved_for_customer")),
        "operator_note": _text(row.get("operator_note")),
    }


def _normalize_media_rule(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "rule_name": _text(row.get("rule_name")),
        "rule_type": _text(row.get("rule_type")) or "Selection group",
        "selection_group": _text(row.get("selection_group")),
        "selection_value": _text(row.get("selection_value")),
        "selection_conditions": _text(row.get("selection_conditions")),
        "variant_item": _text(row.get("variant_item")),
        "image": _text(row.get("image")),
        "approved_for_customer": _as_bool(row.get("approved_for_customer")),
        "operator_note": _text(row.get("operator_note")),
    }


def _normalize_content_rule(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "rule_name": _text(row.get("rule_name")),
        "rule_type": _text(row.get("rule_type")) or "Selection group",
        "selection_group": _text(row.get("selection_group")),
        "selection_value": _text(row.get("selection_value")),
        "selection_conditions": _text(row.get("selection_conditions")),
        "variant_item": _text(row.get("variant_item")),
        "display_title": _text(row.get("display_title")),
        "product_story": _text(row.get("product_story")),
        "product_details": _text(row.get("product_details")),
        "approved_for_customer": _as_bool(row.get("approved_for_customer")),
        "operator_note": _text(row.get("operator_note")),
    }


def _has_positive_checkout_price_rows(rows: list[dict[str, Any]]) -> bool:
    return any(row.get("enabled_for_checkout") and row.get("price", 0) > 0 for row in rows)


def _has_customer_facing_product_image(
    *,
    primary_image: str,
    gallery_image_rows: list[dict[str, Any]],
) -> bool:
    if _text(primary_image):
        return True
    return any(row.get("approved_for_customer") and _text(row.get("image")) for row in gallery_image_rows)


def _allowed_price_roots(product_slug: str, target_item_code: str) -> set[str]:
    return {root for root in {_text(product_slug), _text(target_item_code)} if root}


def _belongs_to_current_product(item_code: str, allowed_roots: set[str]) -> bool:
    code = _text(item_code)
    return any(code == root or code.startswith(f"{root}-") for root in allowed_roots)


def _row_to_dict(row: Any) -> dict[str, Any]:
    if isinstance(row, dict):
        return dict(row)
    keys = (
        "axis_name",
        "role",
        "selection_behavior",
        "control_type",
        "required",
        "min_selections",
        "max_selections",
        "values",
        "default_values",
        "payload_target",
        "pricing_behavior",
        "media_behavior",
        "document_output",
        "operator_note",
        "recipe_name",
        "min_colors",
        "max_colors",
        "palette_source",
        "add_on_name",
        "add_on_item",
        "price_source",
        "requires_value",
        "quantity_min",
        "quantity_max",
        "checkout_approved",
        "condition_label",
        "applies_when",
        "price_behavior",
        "amount",
        "approved_for_checkout",
        "rule_name",
        "rule_type",
        "selection_group",
        "selection_value",
        "selection_conditions",
        "variant_item",
        "image",
        "heading",
        "description",
        "approved_for_customer",
        "display_title",
        "product_story",
        "product_details",
        "item_code",
        "option_summary",
        "price",
        "enabled_for_checkout",
    )
    return {key: getattr(row, key, None) for key in keys if hasattr(row, key)}


def _payload_target_counts(option_rows: list[dict[str, Any]], add_on_rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in option_rows:
        target = row.get("payload_target")
        if target:
            counts[target] = counts.get(target, 0) + 1
    for row in add_on_rows:
        target = row.get("payload_target")
        if target:
            counts[target] = counts.get(target, 0) + 1
    return counts


def _split_values(value: Any) -> list[str]:
    if isinstance(value, list):
        return [_text(item) for item in value if _text(item)]
    text = _text(value)
    if not text:
        return []
    return [part.strip() for part in re.split(r"[\n,]+", text) if part.strip()]


def _summary(status: str, blockers: list[str], warnings: list[str]) -> str:
    if status == READY_FOR_LOCAL_PREVIEW:
        if warnings:
            return f"Ready for local preview only, with {len(warnings)} warning(s). No live publishing action exists."
        return "Ready for local preview only. No live publishing action exists."
    return f"Blocked: {len(blockers)} issue(s) must be fixed before preview or staging."


def _text(value: Any) -> str:
    return str(value or "").strip()


def _int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _float(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}
