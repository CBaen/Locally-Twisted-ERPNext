"""Inject Locally Twisted navigation context into Frappe website pages."""
from __future__ import annotations

import frappe


def update_website_context(context):
    """Add product and occasion menu data to the website context.

    Product links are backed by real ERPNext Item Group and Website Item
    routes. Occasion links should keep customers in product discovery; the
    top utility Contact Us button remains the inquiry path.
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
        {"label": "Birthdays", "route": "shop-items/deliveries/birthday-deliveries", "column": "personal"},
        {"label": "Baby Showers & Reveals", "route": "shop-items/garlands/baby-shower-garland", "column": "personal"},
        {"label": "Graduations", "route": "shop-items/grab-go/graduation-grab-n-go", "column": "personal"},
        {"label": "Get Well", "route": "shop-items/get-well-bouquets", "column": "personal"},
        {"label": "Missionary Farewells & Homecomings", "route": "shop-items/bouquets/large-head-missionary", "column": "faith"},
        {"label": "Church Events", "route": "shop-items/garlands", "column": "faith"},
        {"label": "Religious Celebrations", "route": "shop-items/arches/easter-arch", "column": "faith"},
        {"label": "Corporate Events", "route": "shop-items/bouquets/logo-3-layered-bouquet", "column": "hosted"},
        {"label": "Schools & Community", "route": "shop-items/arches/basketball-arch", "column": "hosted"},
        {"label": "Weddings", "route": "shop-items/garlands", "column": "hosted"},
        {"label": "Holidays & Seasons", "route": "shop-items/seasonal-specialty", "column": "hosted"},
    ]

    context["shop_categories"] = children
    context["shop_root_route"] = "shop-by-category"
    return context
