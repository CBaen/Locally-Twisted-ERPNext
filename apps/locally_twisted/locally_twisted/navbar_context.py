"""Navigation data for the Locally Twisted public header."""
from __future__ import annotations

import frappe
from frappe.utils import strip_html

from locally_twisted.ecommerce_pause import is_ecommerce_paused

PRODUCT_GROUP_ICONS = {
    "Arches": "balloon-arch",
    "Garlands": "organic-garland",
    "Columns": "balloon-column",
    "Drops": "event-stage",
    "Balloon Drops": "event-stage",
    "Bouquets": "balloon-bouquet",
    "Get-Well Bouquets": "balloon-bouquet",
    "Grab & Go": "balloon-cluster",
    "Table Decor": "balloon-cluster",
    "Stands & Easels": "event-stage",
    "Deliveries": "delivery-install",
    "Seasonal & Specialty": "balloon-pair",
}

READY_TO_ORDER_CATEGORY_SUMMARIES = {
    "Arches": "Entry moments, photo frames, and room-defining balloon statements.",
    "Columns": "Freestanding color and height for doors, stages, and focal points.",
    "Bouquets": "Themed balloon bundles for birthdays, characters, teams, and quick gifts.",
    "Get-Well Bouquets": "Cheerful balloon bundles for recovery, hospitals, and thoughtful deliveries.",
    "Garlands": "Organic balloon runs for backdrops, mantels, entrances, and install moments.",
    "Drops": "Ceiling drops and reveal moments for dances, parties, and big announcements.",
    "Grab & Go": "Fast pickup pieces when you need party color without a custom install.",
    "Table Decor": "Centerpieces and smaller pieces for tables, counters, and welcome areas.",
    "Stands & Easels": "Freestanding display pieces for signs, graduations, entrances, and school moments.",
    "Deliveries": "Delivery-ready balloon options and logistics support.",
    "Seasonal & Specialty": "Holiday, school-year, and limited-season pieces.",
}

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


def _group_icon(item_group: str | None) -> str:
    return PRODUCT_GROUP_ICONS.get(_plain_text(item_group), "balloon-pair")


def _category_summary(label: str) -> str:
    return READY_TO_ORDER_CATEGORY_SUMMARIES.get(
        label,
        "Browse ready-to-order balloon decor by category.",
    )


def _ready_to_order_category_links() -> list[dict[str, str]]:
    if is_ecommerce_paused():
        return []

    categories = frappe.db.get_all(
        "Item Group",
        filters={"parent_item_group": "Shop Items", "show_in_website": 1},
        fields=["name", "item_group_name", "route", "weightage"],
        order_by="weightage asc, item_group_name asc",
    )

    links = []
    for category in categories:
        label = _plain_text(category.get("item_group_name") or category.get("name"))
        route = _route(category.get("route"), "")
        if not label or not route:
            continue

        keywords = " ".join(
            part
            for part in (
                "ready order shop category balloon decor",
                label,
                category.get("name"),
                route.replace("-", " ").replace("/", " "),
            )
            if part
        )
        links.append(
            {
                "label": label,
                "route": route,
                "summary": _category_summary(label),
                "keywords": keywords,
                "icon": _group_icon(label),
                "item_group": _plain_text(category.get("name")),
            }
        )
    return links


def update_website_context(context):
    """Add mega-menu data backed by ready-to-order Item Group categories."""
    try:
        ready_to_order_links = _ready_to_order_category_links()
    except Exception as exc:
        frappe.log_error(
            title="LT navbar context",
            message=f"navbar_context ready-to-order category links failed: {exc}",
        )
        ready_to_order_links = []

    context["lt_nav_ready_to_order_links"] = ready_to_order_links
    context["lt_nav_event_links"] = EVENT_LINKS
    context["lt_nav_service_links"] = SERVICE_LINKS
    context["lt_nav_search_ready_to_order_links"] = ready_to_order_links
    context["lt_nav_quote_route"] = "contact"
    return context
