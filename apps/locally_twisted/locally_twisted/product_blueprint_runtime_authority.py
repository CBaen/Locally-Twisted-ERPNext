"""Runtime authority blockers for employee-authored Product Setup records."""
from __future__ import annotations

from typing import Any

from locally_twisted.product_setup_runtime import ACTIVE_SETUP_STATUSES


def runtime_authority_save_blockers(doc: Any, frappe_module: Any | None = None) -> list[str]:
    """Return owner-visible blockers when runtime cannot safely resolve authority."""
    if _text(getattr(doc, "publish_status", "")) not in ACTIVE_SETUP_STATUSES:
        return []
    operating_brand = _text(getattr(doc, "operating_brand", ""))
    if not operating_brand:
        return []

    if frappe_module is None:
        import frappe as frappe_module

    row = _target_website_item_runtime_row(doc, frappe_module)
    if not row:
        return []

    label = row.get("name") or row.get("item_code") or "the linked Website Item"
    if row.get("missing_runtime_brand_fields"):
        detail = ""
        if row.get("runtime_meta_error"):
            detail = f" Metadata lookup failed: {row.get('runtime_meta_error')}."
        return [
            "Product Setup runtime authority is blocked for "
            f"{label}: Website Item operating-brand runtime fields are not installed. "
            "Run the Product Setup brand runtime field migration before preview, staging, live approval, or local apply."
            f"{detail}"
        ]

    expected_item_code = _text(getattr(doc, "target_item_code", "")) or _text(getattr(doc, "product_slug", ""))
    website_item_code = _text(row.get("item_code"))
    if expected_item_code and website_item_code and expected_item_code != website_item_code:
        return [
            "Product Setup runtime authority is blocked for "
            f"{label}: linked Website Item item code is {website_item_code}, but this Product Setup targets {expected_item_code}. "
            "Fix the target Item/Website Item link before preview, staging, live approval, or local apply."
        ]

    website_brand = _text(row.get("operating_brand"))
    website_brand_state = _text(row.get("operating_brand_authority_state"))
    if website_brand != operating_brand or website_brand_state != "source_declared":
        return [
            "Product Setup runtime authority is blocked for "
            f"{label}: Website Item Operating Brand must be source-declared as {operating_brand} before this setup can become active. "
            f"Current Website Item brand/state: {website_brand or 'missing'} / {website_brand_state or 'missing'}."
        ]
    return []


def _target_website_item_runtime_row(doc: Any, frappe_module: Any) -> dict | None:
    try:
        meta = frappe_module.get_meta("Website Item")
    except Exception as exc:
        return {
            "name": "Website Item",
            "item_code": "",
            "missing_runtime_brand_fields": True,
            "runtime_meta_error": str(exc),
        }

    fields = ["name", "item_code"]
    has_brand_fields = meta.has_field("operating_brand") and meta.has_field("operating_brand_authority_state")
    if has_brand_fields:
        fields.extend(["operating_brand", "operating_brand_authority_state"])

    for item_filter in _target_website_item_filters(doc):
        row = frappe_module.db.get_value("Website Item", item_filter, fields, as_dict=True)
        if not row:
            continue
        result = dict(row)
        if not has_brand_fields:
            result["missing_runtime_brand_fields"] = True
        return result
    return None


def _target_website_item_filters(doc: Any) -> list[dict[str, str]]:
    filters: list[dict[str, str]] = []
    target_website_item = _text(getattr(doc, "target_website_item", ""))
    target_item_code = _text(getattr(doc, "target_item_code", ""))
    product_slug = _text(getattr(doc, "product_slug", ""))
    if target_website_item:
        filters.append({"name": target_website_item})
    if target_item_code:
        filters.append({"item_code": target_item_code})
    if product_slug and product_slug != target_item_code:
        filters.append({"item_code": product_slug})
    return filters


def _text(value: Any) -> str:
    return str(value or "").strip()
