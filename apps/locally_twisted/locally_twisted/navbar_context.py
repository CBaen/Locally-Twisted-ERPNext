"""
navbar_context.py — Inject Shop categories into the website context.

Triggered via update_website_context hook in hooks.py. Runs on every page
render. Reads the 11 Shop Items child Item Groups (Arches, Columns, ...) and
exposes them as `context.shop_categories` for the navbar template to render
as a mega menu (desktop) and accordion (mobile).

Per Agent 4 of plan-deepen research: this is the canonical injection point —
matches webshop's own pattern at webshop/webshop/shopping_cart/utils.py.
"""
from __future__ import annotations

import frappe


def update_website_context(context):
    """Add `shop_categories` and `shop_root_route` to the website context.

    Used by:
      apps/locally_twisted/locally_twisted/templates/includes/navbar/navbar.html

    The query is cheap (one indexed read on a tiny doctype) and runs per request.
    Frappe's website cache covers most page hits so this is not a hot path.
    """
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
        # Defensive: if Item Group table isn't ready (fresh install, partial install),
        # don't break the page. Log and serve an empty list.
        frappe.log_error(
            f"navbar_context.update_website_context failed: {e}",
            title="LT navbar context",
        )
        children = []

    shop_root = frappe.db.get_value("Item Group", "Shop Items", "route") or "shop-items"

    context["shop_categories"] = children
    context["shop_root_route"] = shop_root
    return context
