"""Inject Locally Twisted navigation context into Frappe website pages."""
from __future__ import annotations

import frappe


def update_website_context(context):
    """Add product and occasion menu data to the website context.

    Product links are backed by real ERPNext Item Group routes.
    Occasion links are planning contexts that route to /contact with a backend
    occasion value, rather than pretending occasions are product categories.
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
        frappe.log_error(
            f"navbar_context.update_website_context failed: {e}",
            title="LT navbar context",
        )
        children = []

    route_by_name = {c["item_group_name"]: c["route"] for c in children}

    context["mega_shop_balloon_decor"] = [
        {"label": "Arches", "route": route_by_name.get("Arches", "shop-items/arches"), "column": "installations"},
        {"label": "Garlands", "route": route_by_name.get("Garlands", "shop-items/garlands"), "column": "installations"},
        {"label": "Columns", "route": route_by_name.get("Columns", "shop-items/columns"), "column": "installations"},
        {"label": "Balloon Drops", "route": route_by_name.get("Drops", "shop-items/drops"), "column": "installations"},
        {"label": "Bouquets", "route": route_by_name.get("Bouquets", "shop-items/bouquets"), "column": "grab_go"},
        {"label": "Get-Well Bouquets", "route": route_by_name.get("Get-Well Bouquets", "shop-items/get-well-bouquets"), "column": "grab_go"},
        {"label": "Grab & Go", "route": route_by_name.get("Grab & Go", "shop-items/grab-go"), "column": "grab_go"},
        {"label": "Deliveries", "route": route_by_name.get("Deliveries", "shop-items/deliveries"), "column": "grab_go"},
        {"label": "Table Decor", "route": route_by_name.get("Table Decor", "shop-items/table-decor"), "column": "details"},
        {"label": "Stands & Easels", "route": route_by_name.get("Stands & Easels", "shop-items/stands-easels"), "column": "details"},
        {"label": "Seasonal & Specialty", "route": route_by_name.get("Seasonal & Specialty", "shop-items/seasonal-specialty"), "column": "details"},
    ]

    context["mega_plan_by_occasion"] = [
        {"label": "Birthdays", "route": "contact?occasion=birthday", "column": "personal"},
        {"label": "Baby Showers & Reveals", "route": "contact?occasion=baby_shower", "column": "personal"},
        {"label": "Graduations", "route": "contact?occasion=graduation", "column": "personal"},
        {"label": "Get Well", "route": "contact?occasion=get_well", "column": "personal"},
        {"label": "Missionary Farewells & Homecomings", "route": "contact?occasion=missionary", "column": "faith"},
        {"label": "Church Events", "route": "contact?occasion=church", "column": "faith"},
        {"label": "Religious Celebrations", "route": "contact?occasion=religious", "column": "faith"},
        {"label": "Corporate Events", "route": "contact?occasion=corporate", "column": "hosted"},
        {"label": "Schools & Community", "route": "contact?occasion=school", "column": "hosted"},
        {"label": "Weddings", "route": "contact?occasion=wedding", "column": "hosted"},
        {"label": "Holidays & Seasons", "route": "contact?occasion=holiday", "column": "hosted"},
    ]

    context["shop_categories"] = children
    context["shop_root_route"] = "shop-by-category"
    return context
