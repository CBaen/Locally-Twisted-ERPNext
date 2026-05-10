"""Normalize public product-page quote request payloads.

The product page can collect design choices before sending a customer to the
main inquiry form. This module keeps that handoff structured, bounded, and
customer-safe before it becomes Lead / draft Quotation data.
"""
from __future__ import annotations

from typing import Any

import frappe
from frappe import _

from locally_twisted.catalog_contract.color_rules import grouped_colors, is_balloon_color_axis
from locally_twisted.product_page_runtime import CONFIG_VERSION


MAX_QUOTE_TEXT_LENGTH = 240
MAX_QUOTE_ROWS = 24
MAX_QUOTE_SUMMARY_LENGTH = 1800


def normalize_public_product_quote_payload(
    *,
    item: dict[str, Any],
    contract: dict[str, Any],
    incoming: dict[str, Any] | None = None,
) -> dict[str, Any]:
    incoming = incoming or {}
    _assert_runtime_matches_contract(incoming, contract)

    selected_options = _string_dict(
        incoming.get("selected_options"),
        label="product quote options",
    )
    add_ons = _row_list(
        incoming.get("add_ons"),
        label="product quote add-ons",
    )
    customizations = _row_list(
        incoming.get("customizations"),
        label="product quote custom notes",
    )
    color_recipes = _color_recipes(selected_options=selected_options, customizations=customizations)
    summary = _summary(
        item=item,
        selected_options=selected_options,
        add_ons=add_ons,
        customizations=customizations,
        fallback=incoming.get("summary"),
    )

    return {
        "schema_version": CONFIG_VERSION,
        "source": incoming.get("source") or "product-page-contact",
        "website_item_code": item.get("item_code"),
        "web_item_name": item.get("web_item_name"),
        "item_group": item.get("item_group"),
        "route": item.get("route"),
        "product_page_type": contract.get("product_page_type"),
        "commerce_lane": contract.get("commerce_lane"),
        "summary": summary,
        "selected_options": selected_options,
        "add_ons": add_ons,
        "customizations": customizations,
        "color_recipes": color_recipes,
        "needs_operator_review": True,
    }


def _assert_runtime_matches_contract(incoming: dict[str, Any], contract: dict[str, Any]) -> None:
    incoming_page_type = _clean_optional_text(incoming.get("product_page_type"))
    incoming_lane = _clean_optional_text(incoming.get("commerce_lane"))
    actual_page_type = _clean_optional_text(contract.get("product_page_type"))
    actual_lane = _clean_optional_text(contract.get("commerce_lane"))

    if incoming_page_type and actual_page_type and incoming_page_type != actual_page_type:
        frappe.throw(
            _(
                "Tiny snag: this product quote was saved with a different page template. "
                "Please open the product again and send the quote request one more time."
            ),
            frappe.ValidationError,
        )
    if incoming_lane and actual_lane and incoming_lane != actual_lane:
        frappe.throw(
            _(
                "Tiny snag: this product quote was saved with a different buying path. "
                "Please open the product again and send the quote request one more time."
            ),
            frappe.ValidationError,
        )


def _string_dict(value: Any, *, label: str) -> dict[str, str]:
    if value in (None, "", {}):
        return {}
    if not isinstance(value, dict):
        _throw_bad_payload(label)

    normalized: dict[str, str] = {}
    for raw_key, raw_value in value.items():
        key = _clean_required_text(raw_key, label=label)
        text = _clean_required_text(raw_value, label=label)
        normalized[key] = text
    if len(normalized) > MAX_QUOTE_ROWS:
        frappe.throw(
            _("Tiny snag: this product quote has too many option details. Please shorten it and try again."),
            frappe.ValidationError,
        )
    return normalized


def _row_list(value: Any, *, label: str) -> list[dict[str, Any]]:
    if value in (None, "", []):
        return []
    if not isinstance(value, list):
        _throw_bad_payload(label)
    if len(value) > MAX_QUOTE_ROWS:
        frappe.throw(
            _("Tiny snag: this product quote has too many details. Please shorten it and try again."),
            frappe.ValidationError,
        )

    rows: list[dict[str, Any]] = []
    for raw_row in value:
        if not isinstance(raw_row, dict):
            _throw_bad_payload(label)
        row: dict[str, Any] = {}
        for raw_key, raw_value in raw_row.items():
            key = _clean_required_text(raw_key, label=label)
            row[key] = _clean_row_value(raw_value, label=label)
        if row:
            rows.append(row)
    return rows


def _clean_row_value(value: Any, *, label: str) -> Any:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return value
    if isinstance(value, list):
        return [_clean_required_text(entry, label=label) for entry in value if str(entry or "").strip()]
    if isinstance(value, dict):
        _throw_bad_payload(label)
    return _clean_required_text(value, label=label)


def _clean_optional_text(value: Any) -> str:
    if value in (None, ""):
        return ""
    return " ".join(str(value).split())[:MAX_QUOTE_TEXT_LENGTH]


def _clean_required_text(value: Any, *, label: str) -> str:
    if isinstance(value, (dict, list, tuple, set)):
        _throw_bad_payload(label)
    text = _clean_optional_text(value)
    if not text:
        _throw_bad_payload(label)
    return text


def _summary(
    *,
    item: dict[str, Any],
    selected_options: dict[str, str],
    add_ons: list[dict[str, Any]],
    customizations: list[dict[str, Any]],
    fallback: Any,
) -> str:
    item_name = _clean_optional_text(item.get("web_item_name")) or _clean_optional_text(item.get("item_code")) or "Product"
    item_code = _clean_optional_text(item.get("item_code"))
    pieces = [f"Requested product page quote: {item_name}" + (f" ({item_code})" if item_code else "")]

    for key, value in selected_options.items():
        pieces.append(f"{key}: {value}")
    for row in add_ons:
        line = _row_summary(row)
        if line:
            pieces.append(line)
    for row in customizations:
        line = _row_summary(row)
        if line:
            pieces.append(line)

    fallback_text = _clean_optional_text(fallback)
    if fallback_text and len(pieces) == 1 and fallback_text not in pieces[0]:
        pieces.append(fallback_text)
    return "; ".join(pieces)[:MAX_QUOTE_SUMMARY_LENGTH]


def _row_summary(row: dict[str, Any]) -> str:
    label = (
        _clean_optional_text(row.get("label"))
        or _clean_optional_text(row.get("axis"))
        or _clean_optional_text(row.get("key"))
    )
    value = row.get("value")
    if value in (None, ""):
        value = row.get("values")
    if value in (None, ""):
        value = row.get("quantity")
    display_value = _display_value(value)
    if label and display_value:
        return f"{label}: {display_value}"
    if label:
        return label
    return display_value


def _display_value(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(_clean_optional_text(entry) for entry in value if _clean_optional_text(entry))
    if value in (None, ""):
        return ""
    return _clean_optional_text(value)


def _color_recipes(
    *,
    selected_options: dict[str, str],
    customizations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    recipes: dict[str, list[str]] = {}

    for axis, text in selected_options.items():
        if is_balloon_color_axis(axis):
            recipes[axis] = _split_color_values(text)

    for row in customizations:
        axis = _clean_optional_text(row.get("axis")) or _clean_optional_text(row.get("key"))
        if not is_balloon_color_axis(axis):
            continue
        values = row.get("values")
        if values in (None, ""):
            values = row.get("value")
        recipes[axis] = _split_color_values(values)

    result = []
    for axis, values in recipes.items():
        clean_values = [value for value in values if value]
        if not clean_values:
            continue
        result.append(
            {
                "axis": axis,
                "label": "Balloon color recipe",
                "values": clean_values,
                "color_groups": grouped_colors(clean_values),
                "status": "needs_operator_review",
                "source": "product_quote_request",
            }
        )
    return result


def _split_color_values(value: Any) -> list[str]:
    if isinstance(value, list):
        return [_clean_optional_text(entry) for entry in value if _clean_optional_text(entry)]
    if value in (None, ""):
        return []
    if isinstance(value, dict):
        _throw_bad_payload("product quote color recipe")
    parts = [
        _clean_optional_text(part)
        for part in str(value).replace("|", ",").replace(";", ",").split(",")
    ]
    return [part for part in parts if part]


def _throw_bad_payload(label: str) -> None:
    frappe.throw(
        _(
            "Tiny snag: the {0} did not come through cleanly. "
            "Please open the product again and send the quote request one more time."
        ).format(label),
        frappe.ValidationError,
    )
