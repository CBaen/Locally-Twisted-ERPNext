"""Shared Locally Twisted website context helpers."""
from __future__ import annotations

import frappe


def update_website_context(context):
    """Add shop category data used by category/sidebar templates."""
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
