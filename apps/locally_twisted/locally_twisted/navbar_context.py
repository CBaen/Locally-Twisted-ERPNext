"""Navigation data for the Locally Twisted public header."""
from __future__ import annotations

import frappe
from frappe.utils import strip_html


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
        "label": "Civic & Community",
        "route": "civic-community",
        "icon": "civic-parade",
        "description": "City, county, chamber, Pride, and public-facing community installs.",
    },
    {
        "label": "Corporate Events",
        "route": "corporate-events",
        "icon": "corporate-entrance",
        "description": "Brand-safe decor for launches, offices, media events, restaurants, and customer activations.",
    },
    {
        "label": "Schools & Campuses",
        "route": "schools-campuses",
        "icon": "school-spirit",
        "description": "Graduations, assemblies, athletics, dances, family nights, and campus moments.",
    },
    {
        "label": "Private Celebrations",
        "route": "private-celebrations",
        "icon": "premium-private-event",
        "description": "Birthdays, weddings, showers, memorials, venues, and family milestones.",
    },
]

SERVICE_LINKS = [
    {"label": "Frequently Asked Questions", "route": "faq"},
    {"label": "Start a Quote", "route": "contact"},
]


def _route(value: str | None, fallback: str) -> str:
    route = (value or fallback).strip("/")
    return route or fallback


def _plain_text(value: str | None) -> str:
    return " ".join(strip_html(str(value or "")).split())


def _product_search_links() -> list[dict[str, str]]:
    items = frappe.db.sql(
        """
        SELECT
            wi.item_code,
            wi.web_item_name,
            wi.route,
            wi.short_description,
            wi.item_group
        FROM `tabWebsite Item` wi
        LEFT JOIN `tabItem` it ON it.item_code = wi.item_code
        WHERE wi.published = 1
          AND (it.variant_of IS NULL OR it.variant_of = '')
        ORDER BY wi.item_group, wi.web_item_name
        """,
        as_dict=True,
    )

    links = []
    for item in items:
        label = _plain_text(item.get("web_item_name") or item.get("item_code"))
        route = _route(item.get("route"), "")
        if not label or not route:
            continue

        item_group = _plain_text(item.get("item_group"))
        description = _plain_text(item.get("short_description"))
        keywords = " ".join(
            part
            for part in (
                "ready order product shop",
                label,
                item.get("item_code"),
                item_group,
                description,
                route.replace("-", " ").replace("/", " "),
            )
            if part
        )
        links.append(
            {
                "label": label,
                "route": route,
                "summary": item_group or "Ready-to-order product",
                "keywords": keywords,
            }
        )
    return links


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

    try:
        search_product_links = _product_search_links()
    except Exception as exc:
        frappe.log_error(
            f"navbar_context product search links failed: {exc}",
            title="LT navbar search context",
        )
        search_product_links = []

    context["lt_nav_product_links"] = product_links
    context["lt_nav_event_links"] = EVENT_LINKS
    context["lt_nav_service_links"] = SERVICE_LINKS
    context["lt_nav_search_product_links"] = search_product_links
    context["lt_nav_quote_route"] = "contact"
    return context
