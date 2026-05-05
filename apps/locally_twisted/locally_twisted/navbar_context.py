"""Navigation data for the Locally Twisted public header."""
from __future__ import annotations

import frappe


FALLBACK_PRODUCT_LINKS = [
    {"label": "Arches", "route": "shop-items/arches", "icon": "balloon-arch"},
    {"label": "Garlands", "route": "shop-items/garlands", "icon": "organic-garland"},
    {"label": "Columns", "route": "shop-items/columns", "icon": "balloon-column"},
    {"label": "Balloon Drops", "route": "shop-items/drops", "icon": "event-stage"},
    {"label": "Bouquets", "route": "shop-items/bouquets", "icon": "balloon-bouquet"},
    {"label": "Grab & Go", "route": "shop-items/grab-go", "icon": "balloon-cluster"},
]

EVENT_LINKS = [
    {
        "label": "Civic and Community",
        "route": "event-balloons",
        "icon": "civic-parade",
        "description": "Parades, city events, school entrances, and public-facing installs.",
    },
    {
        "label": "Corporate Entrances",
        "route": "portfolio",
        "icon": "corporate-entrance",
        "description": "Brand-safe decor for offices, launches, open houses, and venues.",
    },
    {
        "label": "Schools and Campuses",
        "route": "event-balloons",
        "icon": "school-spirit",
        "description": "Assemblies, graduations, games, spirit weeks, and campus moments.",
    },
    {
        "label": "Private Celebrations",
        "route": "event-balloons",
        "icon": "premium-private-event",
        "description": "Polished birthdays, showers, weddings, and hosted home events.",
    },
]

SERVICE_LINKS = [
    {"label": "How the Process Works", "route": "process"},
    {"label": "Balloon Twisting and Face Painting", "route": "balloon-twisting-and-face-painting"},
    {"label": "Frequently Asked Questions", "route": "faq"},
    {"label": "Start a Quote", "route": "contact"},
]


def _route(value: str | None, fallback: str) -> str:
    route = (value or fallback).strip("/")
    return route or fallback


def update_website_context(context):
    """Add mega-menu data backed by ERPNext Item Group routes when available."""
    product_links = [dict(item) for item in FALLBACK_PRODUCT_LINKS]

    try:
        children = frappe.db.get_all(
            "Item Group",
            filters={"parent_item_group": "Shop Items", "show_in_website": 1},
            fields=["item_group_name", "route", "weightage"],
            order_by="weightage asc, item_group_name asc",
        )
    except Exception as exc:
        frappe.log_error(
            f"navbar_context.update_website_context failed: {exc}",
            title="LT navbar context",
        )
        children = []

    if children:
        route_by_label = {
            child["item_group_name"]: _route(child.get("route"), "")
            for child in children
            if child.get("item_group_name")
        }
        for item in product_links:
            matched_route = route_by_label.get(item["label"])
            if matched_route:
                item["route"] = matched_route

    context["lt_nav_product_links"] = product_links
    context["lt_nav_event_links"] = EVENT_LINKS
    context["lt_nav_service_links"] = SERVICE_LINKS
    context["lt_nav_quote_route"] = "contact"
    return context
