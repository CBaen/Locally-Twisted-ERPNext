"""Shared Locally Twisted website context helpers."""
from __future__ import annotations

import frappe

from locally_twisted.ecommerce_pause import is_ecommerce_paused
from locally_twisted.seo import apply_seo_context


def _assets_json() -> dict:
    get_assets_json = getattr(frappe.utils, "get_assets_json", None)
    if not callable(get_assets_json):
        return {}
    return get_assets_json() or {}


def update_website_context(context):
    """Add shop category data used by category/sidebar templates."""
    apply_seo_context(context)

    try:
        context["lt_assets_json"] = _assets_json()
    except Exception as e:
        frappe.log_error(
            f"website_context._assets_json failed: {e}",
            title="LT website context",
        )
        context["lt_assets_json"] = {}

    try:
        context["lt_ecommerce_paused"] = is_ecommerce_paused()
    except Exception as e:
        frappe.log_error(
            f"website_context.is_ecommerce_paused failed: {e}",
            title="LT website context",
        )
        context["lt_ecommerce_paused"] = True

    try:
        children = frappe.db.get_all(
            "Item Group",
            filters={
                "parent_item_group": "Shop Items",
                "show_in_website": 1,
            },
            fields=["name", "item_group_name", "route", "weightage"],
            order_by="weightage asc, item_group_name asc",
        )
    except Exception as e:
        frappe.log_error(
            f"website_context.update_website_context failed: {e}",
            title="LT website context",
        )
        children = []

    context["shop_categories"] = children
    context["shop_root_route"] = "shop"
    return context
