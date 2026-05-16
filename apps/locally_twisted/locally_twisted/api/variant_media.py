"""Public helpers for variant-aware product media."""
from __future__ import annotations

import json
import re
from typing import Any

import frappe
from frappe import _

from locally_twisted.product_setup_runtime import product_setup_schema_for_website_item


def _variant_options(item_code: str) -> list[dict[str, str]]:
    rows = frappe.get_all(
        "Item Variant Attribute",
        filters={"parent": item_code},
        fields=["attribute", "attribute_value"],
        order_by="idx asc",
    )
    return [
        {
            "attribute": row.get("attribute"),
            "attribute_value": row.get("attribute_value"),
        }
        for row in rows
        if row.get("attribute") and row.get("attribute_value")
    ]


@frappe.whitelist(allow_guest=True)
def get_variant_media(item_code: str, template_item_code: str | None = None, configuration: Any = None) -> dict:
    """Return the storefront image for an Item or variant Item.

    Variant Items are sellable rows, while the Website Item usually lives on
    the template. This method keeps the template image as fallback until a
    source-backed media role marks a variant image as approved for rendering.
    """
    item_code = (item_code or "").strip()
    template_item_code = (template_item_code or "").strip() or None
    if not item_code:
        frappe.throw(_("Please choose a product option first."), frappe.ValidationError)

    item = frappe.db.get_value(
        "Item",
        {"item_code": item_code, "disabled": 0},
        ["item_code", "item_name", "variant_of", "image"],
        as_dict=True,
    )
    if not item:
        frappe.throw(_("Tiny snag: this item is no longer available. Please choose another option."), frappe.ValidationError)

    website_item_code = item.get("variant_of") or item["item_code"]
    if template_item_code and website_item_code != template_item_code:
        frappe.throw(_("Tiny snag: that option does not match this product. Please choose again."), frappe.ValidationError)

    website_item = frappe.db.get_value(
        "Website Item",
        {"item_code": website_item_code, "published": 1},
        ["item_code", "web_item_name", "website_image", "route"],
        as_dict=True,
    )
    if not website_item:
        frappe.throw(_("Tiny snag: this product is not available right now. Please choose another option."), frappe.ValidationError)

    fallback_image = website_item.get("website_image") or None
    variant_image = item.get("image") or None
    setup_media = _approved_product_setup_media(
        template_item_code=website_item["item_code"],
        variant_item_code=item["item_code"],
        configuration=configuration,
    )
    approved_variant_image = setup_media.get("image") if setup_media else None
    image = approved_variant_image or fallback_image
    held_back_variant_image = bool(variant_image and variant_image != fallback_image)
    hold_reason = (
        "Variant image is held until source media classification approves the variant_image role."
        if held_back_variant_image
        else ""
    )

    return {
        "item_code": item["item_code"],
        "template_item_code": website_item["item_code"],
        "image": image,
        "fallback_image": fallback_image,
        "has_variant_image": bool(approved_variant_image and approved_variant_image != fallback_image),
        "held_back_variant_image": held_back_variant_image,
        "held_back_media_role": "ignored_artifact" if held_back_variant_image else "",
        "held_back_render_policy": "hold_back" if held_back_variant_image else "",
        "hold_reason": hold_reason,
        "role_reason": hold_reason,
        "media_role": "product_setup_media_rule" if approved_variant_image else "primary",
        "product_setup_media_rule": setup_media or {},
        "alt": item.get("item_name") or website_item.get("web_item_name") or item["item_code"],
        "route": website_item.get("route"),
        "variant_options": _variant_options(item["item_code"]) if item.get("variant_of") else [],
    }


def _approved_product_setup_media(
    *,
    template_item_code: str,
    variant_item_code: str,
    configuration: Any,
) -> dict[str, Any]:
    schema = product_setup_schema_for_website_item(template_item_code)
    if not schema:
        return {}
    rules = [
        rule
        for rule in schema.get("media_rules") or []
        if rule.get("approved_for_customer") and rule.get("image")
    ]
    if not rules:
        return {}
    for rule in rules:
        if rule.get("rule_type") == "Exact resolved variant" and rule.get("variant_item") == variant_item_code:
            return rule

    selected = _selected_media_values(configuration)
    for rule in rules:
        if rule.get("rule_type") != "Selection group":
            continue
        group_key = str(rule.get("selection_group") or "").strip()
        group_values = selected.get(group_key) or selected.get(_slug(group_key)) or []
        if str(rule.get("selection_value") or "").strip() in group_values:
            return rule
    return {}


def _selected_media_values(configuration: Any) -> dict[str, list[str]]:
    configuration = _configuration_dict(configuration)
    selected: dict[str, list[str]] = {}
    for key, value in (configuration.get("selected_options") or {}).items():
        values = value if isinstance(value, list) else [value]
        clean = [str(item).strip() for item in values if str(item or "").strip()]
        if clean:
            selected[str(key)] = clean
            selected[_slug(key)] = clean
    for row in configuration.get("configuration_groups") or []:
        if not isinstance(row, dict):
            continue
        label = str(row.get("label") or row.get("key") or "").strip()
        key = str(row.get("key") or label).strip()
        values = row.get("values") or []
        if not isinstance(values, list):
            values = [values]
        clean = [str(item).strip() for item in values if str(item or "").strip()]
        if clean:
            selected[key] = clean
            selected[label] = clean
            selected[_slug(key)] = clean
            selected[_slug(label)] = clean
    return selected


def _configuration_dict(configuration: Any) -> dict[str, Any]:
    if configuration in (None, ""):
        return {}
    if isinstance(configuration, str):
        try:
            configuration = json.loads(configuration)
        except (TypeError, ValueError):
            return {}
    return configuration if isinstance(configuration, dict) else {}


def _slug(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(value or "").strip().lower()).strip("-")
