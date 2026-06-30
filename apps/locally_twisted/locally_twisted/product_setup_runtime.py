"""Generic Product Setup runtime for LT ecommerce.

This module is product-agnostic on purpose. Existing catalog records can be
used as evidence, but Product Setup owns the reusable ecommerce meaning:
selection groups, SKU-defining variant axes, configuration-only choices,
add-ons, pricing/media behavior, and the resolved customer payload.
"""
from __future__ import annotations

import hashlib
import json
import re
from itertools import product
from typing import Any


SCHEMA_VERSION = "lt-product-setup-runtime-v1"
CONFIG_VERSION = "lt-product-config-v1"

OPERATING_BRAND_OPTIONS = {
    "locally_twisted",
    "commercial_balloon_decor",
    "memorial_balloons",
}

BEHAVIOR_SKU = "SKU-defining variant"
BEHAVIOR_CONFIGURATION = "Configuration only"
BEHAVIOR_ADD_ON = "Add-on"
BEHAVIOR_MEASUREMENT = "Measurement/Text"
BEHAVIOR_UPLOAD = "Upload/Reference"
BEHAVIOR_REVIEW = "Review only"

CONTROL_SINGLE = "Single select"
CONTROL_MULTI = "Multi select"
CONTROL_TEXT = "Text"
CONTROL_NUMBER = "Number"
CONTROL_FILE = "File upload"
CONTROL_CHECKBOX = "Checkbox"

DOCUMENT_CUSTOMER_OPERATOR = "Customer and operator"
DOCUMENT_OPERATOR_ONLY = "Operator only"
DOCUMENT_INTERNAL_ONLY = "Internal only"

BEHAVIOR_OPTIONS = {
    BEHAVIOR_SKU,
    BEHAVIOR_CONFIGURATION,
    BEHAVIOR_ADD_ON,
    BEHAVIOR_MEASUREMENT,
    BEHAVIOR_UPLOAD,
    BEHAVIOR_REVIEW,
}

CONTROL_OPTIONS = {
    CONTROL_SINGLE,
    CONTROL_MULTI,
    CONTROL_TEXT,
    CONTROL_NUMBER,
    CONTROL_FILE,
    CONTROL_CHECKBOX,
}

ROLE_TO_BEHAVIOR = {
    "Sale unit option": BEHAVIOR_SKU,
    "Color recipe": BEHAVIOR_CONFIGURATION,
    "Add-on": BEHAVIOR_ADD_ON,
    "Review only": BEHAVIOR_REVIEW,
}

BEHAVIOR_TO_PAYLOAD_TARGET = {
    BEHAVIOR_SKU: "selected_options",
    BEHAVIOR_CONFIGURATION: "configuration_groups",
    BEHAVIOR_ADD_ON: "add_ons",
    BEHAVIOR_MEASUREMENT: "configuration_groups",
    BEHAVIOR_UPLOAD: "configuration_groups",
    BEHAVIOR_REVIEW: "quote_context",
}

COMMERCE_OUTCOME_BY_PATH = {
    "Direct checkout": "checkout",
    "Quote first": "request",
    "Needs review": "review",
}

ACTIVE_SETUP_STATUSES = {
    "Local Preview Ready",
    "Staging Ready",
    "Approved For Live",
}


def build_product_setup_schema_doc(doc: Any) -> dict[str, Any]:
    """Build the generic Product Setup schema from a Frappe document."""
    from locally_twisted.product_blueprint_validation import blueprint_doc_to_dict

    return build_product_setup_schema(blueprint_doc_to_dict(doc))


def product_setup_schema_for_website_item(website_item_code: str | None) -> dict[str, Any] | None:
    """Return the Product Setup schema linked to a Website Item/Item code, if any."""
    website_item_code = _text(website_item_code)
    if not website_item_code:
        return None

    import frappe

    if not frappe.db.exists("DocType", "LT Product Blueprint"):
        return None
    name = _active_product_setup_name(frappe, "target_item_code", website_item_code)
    if not name:
        name = _active_product_setup_name(frappe, "product_slug", website_item_code)
    if not name:
        return None
    return build_product_setup_schema_doc(frappe.get_doc("LT Product Blueprint", name))


def _active_product_setup_name(frappe_module: Any, fieldname: str, value: str) -> str | None:
    rows = frappe_module.get_all(
        "LT Product Blueprint",
        filters={fieldname: value, "publish_status": ["in", sorted(ACTIVE_SETUP_STATUSES)]},
        pluck="name",
        order_by="modified desc",
        limit_page_length=1,
    )
    return rows[0] if rows else None


def build_product_setup_schema(data: dict[str, Any]) -> dict[str, Any]:
    """Return a backend-owned, product-agnostic setup schema."""
    product_slug = _text(data.get("product_slug"))
    product_name = _text(data.get("product_name"))
    operating_brand = _text(data.get("operating_brand"))
    buying_path = _text(data.get("buying_path")) or "Needs review"
    page_template = _text(data.get("page_template")) or "Configurable product page"
    publish_status = _text(data.get("publish_status")) or "Draft"
    groups = [_selection_group(row, index) for index, row in enumerate(data.get("option_rows") or [], start=1)]
    add_ons = [_add_on_group(row, index) for index, row in enumerate(data.get("add_on_rows") or [], start=1)]
    pricing_rules = [_pricing_rule(row, index) for index, row in enumerate(data.get("conditional_price_rows") or [], start=1)]
    media_rules = [_media_rule(row, index) for index, row in enumerate(data.get("media_rule_rows") or [], start=1)]
    gallery_images = [_gallery_image(row, index) for index, row in enumerate(data.get("gallery_image_rows") or [], start=1)]
    content_rules = [_content_rule(row, index) for index, row in enumerate(data.get("content_rule_rows") or [], start=1)]
    sku_groups = [group for group in groups if group["sku_defining"]]
    variant_count = _variant_combination_count(sku_groups)

    return {
        "schema_version": SCHEMA_VERSION,
        "config_version": CONFIG_VERSION,
        "product": {
            "product_slug": product_slug,
            "product_name": product_name,
            "operating_brand": operating_brand,
            "operating_brand_authority_state": operating_brand_authority_state(operating_brand),
            "item_group": _text(data.get("item_group")),
            "page_template": page_template,
            "buying_path": buying_path,
            "setup_status": publish_status,
            "shop_visibility": _text(data.get("shop_visibility")) or "Keep current",
            "primary_image": _text(data.get("primary_image")),
        },
        "commerce": {
            "requested_outcome": COMMERCE_OUTCOME_BY_PATH.get(buying_path, "review"),
            "base_price": _float(data.get("base_price")),
            "pricing_authority": "server",
        },
        "selection_groups": groups,
        "add_on_groups": add_ons,
        "pricing_rules": pricing_rules,
        "gallery_images": gallery_images,
        "media_rules": media_rules,
        "content_rules": content_rules,
        "generation": {
            "sku_defining_group_count": len(sku_groups),
            "variant_combination_count": variant_count,
            "configuration_only_group_count": len([group for group in groups if group["payload_target"] == "configuration_groups"]),
        },
        "source": "lt_product_setup",
    }


def operating_brand_authority_state(operating_brand: str) -> str:
    operating_brand = _text(operating_brand)
    if not operating_brand:
        return "missing"
    if operating_brand not in OPERATING_BRAND_OPTIONS:
        return "invalid"
    return "source_declared"


def resolve_product_setup_configuration(
    schema: dict[str, Any],
    configuration: dict[str, Any] | None,
    *,
    trusted_variant_attributes: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Validate customer selections against a Product Setup schema."""
    configuration = configuration or {}
    selections = _selection_input(configuration)
    trusted_selections = _trusted_selection_input(trusted_variant_attributes)
    blockers: list[str] = []
    resolved_variant_attributes: dict[str, str] = {}
    configuration_groups: list[dict[str, Any]] = []
    add_ons: list[dict[str, Any]] = []

    for group in schema.get("selection_groups") or []:
        values = _selected_values(selections, group)
        label = group["label"]
        trusted_value = _trusted_group_value(trusted_selections, group) if group.get("sku_defining") else ""
        if trusted_value:
            if values and values != [trusted_value]:
                blockers.append(f"{label}: saved selection does not match the priced item.")
            values = [trusted_value]
        min_count = int(group.get("min_selections") or 0)
        max_count = int(group.get("max_selections") or 0)
        allowed = {str(value) for value in group.get("values") or []}

        if len(values) < min_count:
            blockers.append(f"{label}: choose at least {min_count}.")
        if max_count and len(values) > max_count:
            blockers.append(f"{label}: choose at most {max_count}.")
        for value in values:
            if allowed and value not in allowed and value != trusted_value:
                blockers.append(f"{label}: {value} is not an allowed choice.")

        if group.get("sku_defining"):
            if len(values) == 1:
                resolved_variant_attributes[label] = values[0]
            elif not values and min_count == 0:
                continue
            else:
                blockers.append(f"{label}: SKU-defining groups need exactly one selected value.")
        elif group.get("payload_target") == "add_ons":
            if values:
                add_ons.append(
                    {
                        "key": group["key"],
                        "label": label,
                        "values": values,
                        "document_output": group["document_output"],
                    }
                )
        elif values:
            configuration_groups.append(
                {
                    "key": group["key"],
                    "label": label,
                    "values": values,
                    "document_output": group["document_output"],
                }
            )

    unresolved = _unresolved_checkout_states(schema)
    blockers.extend(unresolved)
    requested_outcome = (schema.get("commerce") or {}).get("requested_outcome") or "review"
    outcome = "blocked" if blockers else requested_outcome
    payload = {
        "schema_version": CONFIG_VERSION,
        "source": "lt_product_setup",
        "product_setup_schema_version": schema.get("schema_version"),
        "website_item_code": (schema.get("product") or {}).get("product_slug"),
        "selected_options": resolved_variant_attributes,
        "configuration_groups": configuration_groups,
        "add_ons": add_ons,
        "customizations": [],
    }
    selected_media = resolve_product_setup_media(
        schema,
        variant_item_code=_text(configuration.get("item_code")),
        configuration=configuration,
    )
    selected_content = resolve_product_setup_content(
        schema,
        variant_item_code=_text(configuration.get("item_code")),
        configuration=configuration,
    )
    if selected_media:
        payload["selected_media"] = selected_media
    if selected_content:
        payload["selected_content"] = selected_content

    return {
        "schema_version": "lt-product-setup-resolution-v1",
        "ok": not blockers,
        "commerce_outcome": outcome,
        "customer_message": _customer_message(blockers, requested_outcome),
        "blockers": blockers,
        "resolved_variant_attributes": resolved_variant_attributes,
        "configuration_groups": configuration_groups,
        "add_ons": add_ons,
        "selected_media": selected_media,
        "selected_content": selected_content,
        "configuration_payload": payload,
        "validation_hash": _validation_hash(payload),
    }


def resolve_product_setup_media(
    schema: dict[str, Any] | None,
    *,
    variant_item_code: str | None = None,
    configuration: Any = None,
) -> dict[str, Any]:
    """Return the best approved Product Setup media rule for a selection."""
    if not schema:
        return {}
    rules = [
        rule
        for rule in schema.get("media_rules") or []
        if rule.get("approved_for_customer") and rule.get("image")
    ]
    if not rules:
        return {}

    selected = _selected_media_values(configuration)
    variant_item_code = _text(variant_item_code)
    candidates: list[tuple[int, dict[str, Any]]] = []

    for rule in rules:
        if not _media_rule_matches(rule, selected=selected, variant_item_code=variant_item_code):
            continue
        candidates.append((_media_rule_score(rule), rule))

    if not candidates:
        return {}
    candidates.sort(key=lambda row: row[0], reverse=True)
    return candidates[0][1]


def resolve_product_setup_content(
    schema: dict[str, Any] | None,
    *,
    variant_item_code: str | None = None,
    configuration: Any = None,
) -> dict[str, Any]:
    """Return the best approved Product Setup content rule for a selection."""
    if not schema:
        return {}
    rules = [
        rule
        for rule in schema.get("content_rules") or []
        if rule.get("approved_for_customer") and _content_rule_has_copy(rule)
    ]
    if not rules:
        return {}

    selected = _selected_media_values(configuration)
    variant_item_code = _text(variant_item_code)
    candidates: list[tuple[int, dict[str, Any]]] = []

    for rule in rules:
        if not _media_rule_matches(rule, selected=selected, variant_item_code=variant_item_code):
            continue
        candidates.append((_media_rule_score(rule), rule))

    if not candidates:
        return {}
    candidates.sort(key=lambda row: row[0], reverse=True)
    return candidates[0][1]


def get_product_setup_schema_json(item_code: str | None) -> str:
    """Return HTML-safe Product Setup schema JSON for product templates."""
    schema = product_setup_schema_for_website_item(item_code) or {
        "schema_version": SCHEMA_VERSION,
        "config_version": CONFIG_VERSION,
        "product": {"product_slug": _text(item_code)},
        "commerce": {"requested_outcome": "legacy_runtime"},
        "selection_groups": [],
        "add_on_groups": [],
        "pricing_rules": [],
        "gallery_images": [],
        "media_rules": [],
        "content_rules": [],
        "generation": {"sku_defining_group_count": 0, "variant_combination_count": 0},
        "source": "legacy_product_runtime",
    }
    return _safe_json(schema)


def _selection_group(row: dict[str, Any], index: int) -> dict[str, Any]:
    label = _text(row.get("axis_name")) or f"Selection Group {index}"
    values = _split_values(row.get("values"))
    behavior = _behavior(row)
    control_type = _control_type(row, behavior)
    required = _as_bool(row.get("required"))
    min_selections = _int(row.get("min_selections"))
    if min_selections == 0 and required:
        min_selections = 1
    max_selections = _int(row.get("max_selections"))
    if max_selections <= 0:
        max_selections = 1 if control_type in {CONTROL_SINGLE, CONTROL_TEXT, CONTROL_NUMBER, CONTROL_FILE, CONTROL_CHECKBOX} else len(values)
    default_values = _split_values(row.get("default_values"))
    payload_target = BEHAVIOR_TO_PAYLOAD_TARGET.get(behavior, "configuration_groups")

    return {
        "key": _slug(label),
        "label": label,
        "selection_behavior": behavior,
        "sku_defining": behavior == BEHAVIOR_SKU,
        "payload_target": payload_target,
        "control_type": control_type,
        "required": required,
        "min_selections": min_selections,
        "max_selections": max_selections,
        "values": values,
        "default_values": default_values,
        "pricing_behavior": _text(row.get("pricing_behavior")) or "Included in base price",
        "media_behavior": _text(row.get("media_behavior")) or "No image change",
        "document_output": _text(row.get("document_output")) or DOCUMENT_CUSTOMER_OPERATOR,
        "operator_note": _text(row.get("operator_note")),
    }


def _add_on_group(row: dict[str, Any], index: int) -> dict[str, Any]:
    label = _text(row.get("add_on_name")) or f"Add-on {index}"
    return {
        "key": _slug(label),
        "label": label,
        "item_code": _text(row.get("add_on_item")),
        "pricing_behavior": _text(row.get("price_source")) or "Needs review",
        "requires_value": _as_bool(row.get("requires_value")),
        "quantity_min": _int(row.get("quantity_min")),
        "quantity_max": _int(row.get("quantity_max")),
        "checkout_approved": _as_bool(row.get("checkout_approved")),
        "payload_target": "add_ons" if _as_bool(row.get("checkout_approved")) else "configuration_groups",
    }


def _pricing_rule(row: dict[str, Any], index: int) -> dict[str, Any]:
    label = _text(row.get("condition_label")) or f"Pricing Rule {index}"
    return {
        "key": _slug(label),
        "label": label,
        "applies_when": _text(row.get("applies_when")),
        "pricing_behavior": _text(row.get("price_behavior")) or "Needs review",
        "amount": _text(row.get("amount")),
        "approved_for_checkout": _as_bool(row.get("approved_for_checkout")),
    }


def _media_rule(row: dict[str, Any], index: int) -> dict[str, Any]:
    label = _text(row.get("rule_name")) or f"Media Rule {index}"
    conditions = _media_rule_conditions(row)
    return {
        "key": _slug(label),
        "label": label,
        "rule_type": _text(row.get("rule_type")) or "Selection group",
        "selection_group": _text(row.get("selection_group")),
        "selection_value": _text(row.get("selection_value")),
        "selection_conditions": _text(row.get("selection_conditions")),
        "conditions": conditions,
        "variant_item": _text(row.get("variant_item")),
        "image": _text(row.get("image")),
        "approved_for_customer": _as_bool(row.get("approved_for_customer")),
        "document_output": _text(row.get("document_output")) or DOCUMENT_CUSTOMER_OPERATOR,
        "operator_note": _text(row.get("operator_note")),
    }


def _gallery_image(row: dict[str, Any], index: int) -> dict[str, Any]:
    label = _text(row.get("heading")) or f"Gallery Photo {index}"
    return {
        "key": _slug(label),
        "label": label,
        "image": _text(row.get("image")),
        "heading": label,
        "description": _text(row.get("description")),
        "approved_for_customer": _as_bool(row.get("approved_for_customer")),
        "operator_note": _text(row.get("operator_note")),
    }


def _content_rule(row: dict[str, Any], index: int) -> dict[str, Any]:
    label = _text(row.get("rule_name")) or f"Copy Rule {index}"
    conditions = _media_rule_conditions(row)
    return {
        "key": _slug(label),
        "label": label,
        "rule_type": _text(row.get("rule_type")) or "Selection group",
        "selection_group": _text(row.get("selection_group")),
        "selection_value": _text(row.get("selection_value")),
        "selection_conditions": _text(row.get("selection_conditions")),
        "conditions": conditions,
        "variant_item": _text(row.get("variant_item")),
        "display_title": _text(row.get("display_title")),
        "product_story": _text(row.get("product_story")),
        "product_details": _text(row.get("product_details")),
        "approved_for_customer": _as_bool(row.get("approved_for_customer")),
        "operator_note": _text(row.get("operator_note")),
    }


def _content_rule_has_copy(rule: dict[str, Any]) -> bool:
    return bool(
        _text(rule.get("display_title"))
        or _text(rule.get("product_story"))
        or _text(rule.get("product_details"))
    )


def _behavior(row: dict[str, Any]) -> str:
    behavior = _text(row.get("selection_behavior"))
    if behavior in BEHAVIOR_OPTIONS:
        return behavior
    return ROLE_TO_BEHAVIOR.get(_text(row.get("role")), BEHAVIOR_SKU)


def _control_type(row: dict[str, Any], behavior: str) -> str:
    control_type = _text(row.get("control_type"))
    if control_type in CONTROL_OPTIONS:
        return control_type
    if behavior == BEHAVIOR_UPLOAD:
        return CONTROL_FILE
    if behavior == BEHAVIOR_MEASUREMENT:
        return CONTROL_TEXT
    if behavior == BEHAVIOR_ADD_ON:
        return CONTROL_CHECKBOX
    return CONTROL_MULTI if _int(row.get("max_selections")) > 1 else CONTROL_SINGLE


def _selection_input(configuration: dict[str, Any]) -> dict[str, Any]:
    selections = configuration.get("selections")
    if isinstance(selections, dict):
        return selections
    merged: dict[str, Any] = {}
    for key in ("selected_options", "configuration_groups"):
        raw = configuration.get(key)
        if isinstance(raw, dict):
            merged.update(raw)
        elif isinstance(raw, list):
            for row in raw:
                if not isinstance(row, dict):
                    continue
                row_key = _text(row.get("key") or row.get("label") or row.get("axis"))
                if row_key:
                    merged[_slug(row_key)] = row.get("values") or row.get("value")
    return merged


def _trusted_selection_input(values: dict[str, str] | None) -> dict[str, str]:
    trusted: dict[str, str] = {}
    if not isinstance(values, dict):
        return trusted
    for key, value in values.items():
        clean_key = _text(key)
        clean_value = _text(value)
        if not clean_key or not clean_value:
            continue
        trusted[clean_key] = clean_value
        trusted[_slug(clean_key)] = clean_value
    return trusted


def _trusted_group_value(trusted: dict[str, str], group: dict[str, Any]) -> str:
    label = _text(group.get("label"))
    key = _text(group.get("key"))
    return trusted.get(label) or trusted.get(_slug(label)) or trusted.get(key) or trusted.get(_slug(key)) or ""


def _media_rule_matches(
    rule: dict[str, Any],
    *,
    selected: dict[str, list[str]],
    variant_item_code: str,
) -> bool:
    rule_type = _text(rule.get("rule_type")) or "Selection group"
    conditions = rule.get("conditions") or []

    if rule_type == "Exact resolved variant":
        if _text(rule.get("variant_item")) != variant_item_code:
            return False
        return _conditions_match(conditions, selected)

    if rule_type == "Selection combination":
        return bool(conditions) and _conditions_match(conditions, selected)

    if rule_type == "Selection group":
        group = _text(rule.get("selection_group"))
        value = _text(rule.get("selection_value"))
        if not group or not value:
            return False
        group_values = selected.get(group) or selected.get(_slug(group)) or []
        return value in group_values

    return False


def _media_rule_score(rule: dict[str, Any]) -> int:
    rule_type = _text(rule.get("rule_type")) or "Selection group"
    conditions = rule.get("conditions") or []
    if rule_type == "Exact resolved variant" and conditions:
        return 200 + len(conditions)
    if rule_type == "Selection combination":
        return 100 + len(conditions)
    if rule_type == "Exact resolved variant":
        return 80
    if rule_type == "Selection group":
        return 10
    return 0


def _conditions_match(conditions: list[dict[str, str]], selected: dict[str, list[str]]) -> bool:
    for condition in conditions:
        group = _text(condition.get("group") or condition.get("selection_group"))
        value = _text(condition.get("value") or condition.get("selection_value"))
        if not group or not value:
            return False
        group_values = selected.get(group) or selected.get(_slug(group)) or []
        if value not in group_values:
            return False
    return True


def _selected_media_values(configuration: Any) -> dict[str, list[str]]:
    configuration = _configuration_dict(configuration)
    selected: dict[str, list[str]] = {}
    for key, value in (configuration.get("selected_options") or {}).items():
        _set_selected_media_values(selected, key, value)
    for row in configuration.get("configuration_groups") or []:
        if not isinstance(row, dict):
            continue
        label = _text(row.get("label") or row.get("key"))
        key = _text(row.get("key") or label)
        values = row.get("values") or []
        _set_selected_media_values(selected, key, values)
        _set_selected_media_values(selected, label, values)
    return selected


def _set_selected_media_values(target: dict[str, list[str]], key: Any, raw_values: Any) -> None:
    clean_key = _text(key)
    if not clean_key:
        return
    values = raw_values if isinstance(raw_values, list) else [raw_values]
    clean = [_text(item) for item in values if _text(item)]
    if not clean:
        return
    target[clean_key] = clean
    target[_slug(clean_key)] = clean


def _configuration_dict(configuration: Any) -> dict[str, Any]:
    if configuration in (None, ""):
        return {}
    if isinstance(configuration, str):
        try:
            configuration = json.loads(configuration)
        except (TypeError, ValueError):
            return {}
    return configuration if isinstance(configuration, dict) else {}


def _media_rule_conditions(row: dict[str, Any]) -> list[dict[str, str]]:
    raw_conditions = row.get("conditions")
    if isinstance(raw_conditions, list):
        return _condition_list_from_mappings(raw_conditions)

    parsed = _parse_condition_text(row.get("selection_conditions") or row.get("conditions_json"))
    if parsed:
        return parsed

    group = _text(row.get("selection_group"))
    value = _text(row.get("selection_value"))
    if group and value:
        return [{"group": group, "value": value}]
    return []


def _parse_condition_text(value: Any) -> list[dict[str, str]]:
    text = _text(value)
    if not text:
        return []
    if text.startswith("["):
        try:
            rows = json.loads(text)
        except (TypeError, ValueError):
            rows = []
        if isinstance(rows, list):
            return _condition_list_from_mappings(rows)
    conditions: list[dict[str, str]] = []
    for line in text.splitlines():
        clean = line.strip()
        if not clean:
            continue
        separator = "=" if "=" in clean else ":"
        if separator not in clean:
            continue
        group, selected_value = clean.split(separator, 1)
        group = group.strip()
        selected_value = selected_value.strip()
        if group and selected_value:
            conditions.append({"group": group, "value": selected_value})
    return conditions


def _condition_list_from_mappings(rows: list[Any]) -> list[dict[str, str]]:
    conditions: list[dict[str, str]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        group = _text(row.get("group") or row.get("selection_group"))
        value = _text(row.get("value") or row.get("selection_value"))
        if group and value:
            conditions.append({"group": group, "value": value})
    return conditions


def _selected_values(selections: dict[str, Any], group: dict[str, Any]) -> list[str]:
    raw = selections.get(group["key"])
    if raw is None:
        raw = selections.get(group["label"])
    if raw is None:
        return []
    if isinstance(raw, list):
        return [_text(value) for value in raw if _text(value)]
    if isinstance(raw, tuple):
        return [_text(value) for value in raw if _text(value)]
    return [_text(raw)] if _text(raw) else []


def _unresolved_checkout_states(schema: dict[str, Any]) -> list[str]:
    requested = (schema.get("commerce") or {}).get("requested_outcome")
    if requested != "checkout":
        return []
    blockers: list[str] = []
    if float((schema.get("commerce") or {}).get("base_price") or 0) <= 0:
        blockers.append("Checkout needs a server-owned base price.")
    for group in schema.get("selection_groups") or []:
        if group.get("pricing_behavior") == "Needs review":
            blockers.append(f"{group['label']}: pricing needs review before checkout.")
    for rule in schema.get("pricing_rules") or []:
        if not rule.get("approved_for_checkout"):
            blockers.append(f"{rule['label']}: pricing rule is not approved for checkout.")
    return blockers


def _variant_combination_count(groups: list[dict[str, Any]]) -> int:
    if not groups:
        return 0
    counts = [len(group.get("values") or []) for group in groups]
    if any(count == 0 for count in counts):
        return 0
    total = 1
    for count in counts:
        total *= count
    return total


def _customer_message(blockers: list[str], requested_outcome: str) -> str:
    if blockers:
        return "Tiny snag: this product setup needs review before checkout. Please adjust the selections or ask the team for help."
    if requested_outcome == "checkout":
        return ""
    if requested_outcome == "request":
        return "This setup is ready to send as a request with the selected details preserved."
    return "This setup needs team review before it can continue."


def _validation_hash(payload: dict[str, Any]) -> str:
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    # A short deterministic fingerprint is enough for cart/document parity.
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _split_values(value: Any) -> list[str]:
    if isinstance(value, list):
        return [_text(item) for item in value if _text(item)]
    text = _text(value)
    if not text:
        return []
    return [part.strip() for part in re.split(r"[\n,]+", text) if part.strip()]


def _safe_json(value: dict[str, Any]) -> str:
    text = json.dumps(value, sort_keys=True, default=str, ensure_ascii=False)
    return (
        text.replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", str(value or "").strip().lower()).strip("-")
    return slug or "selection"


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
