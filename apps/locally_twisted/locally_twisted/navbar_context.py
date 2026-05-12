"""Navigation data for the Locally Twisted public header."""
from __future__ import annotations

import frappe
from frappe.utils import strip_html

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


def _has_checkout_price(website_item_code: str) -> bool:
    return bool(
        frappe.db.sql(
            """
            SELECT ip.name
            FROM `tabItem` it
            JOIN `tabItem Price` ip
              ON ip.item_code = it.item_code
             AND ip.price_list = 'Standard Selling'
             AND ip.selling = 1
            WHERE it.disabled = 0
              AND (it.item_code = %(item_code)s OR it.variant_of = %(item_code)s)
            LIMIT 1
            """,
            {"item_code": website_item_code},
        )
    )


def _is_backend_checkout_enabled(item: dict) -> bool:
    return item.get("lt_product_page_type") == "simple_product" and item.get("lt_commerce_lane") == "checkout"


def _ready_to_order_exclusion_reason(item: dict) -> str:
    item_code = item.get("item_code") or ""
    if not _is_backend_checkout_enabled(item):
        return "not_checkout_enabled"
    if not _has_checkout_price(item_code):
        return "missing_checkout_price"
    return ""


def _ready_to_order_product_links() -> list[dict[str, str]]:
    items = frappe.db.sql(
        """
        SELECT
            wi.item_code,
            wi.web_item_name,
            wi.route,
            wi.short_description,
            wi.item_group,
            wi.lt_product_page_type,
            wi.lt_commerce_lane
        FROM `tabWebsite Item` wi
        LEFT JOIN `tabItem` it ON it.item_code = wi.item_code
        WHERE wi.published = 1
          AND it.disabled = 0
          AND (it.variant_of IS NULL OR it.variant_of = '')
        ORDER BY wi.item_group, wi.web_item_name
        """,
        as_dict=True,
    )

    links = []
    for item in items:
        if _ready_to_order_exclusion_reason(item):
            continue

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
                "icon": _group_icon(item_group),
                "item_code": item.get("item_code") or "",
                "item_group": item_group,
            }
        )
    return links


def update_website_context(context):
    """Add mega-menu data backed by explicit ERPNext Website Item checkout lanes."""
    try:
        product_links = _ready_to_order_product_links()
    except Exception as exc:
        frappe.log_error(
            f"navbar_context ready-to-order links failed: {exc}",
            title="LT navbar context",
        )
        product_links = []

    context["lt_nav_product_links"] = product_links
    context["lt_nav_event_links"] = EVENT_LINKS
    context["lt_nav_service_links"] = SERVICE_LINKS
    context["lt_nav_search_product_links"] = product_links
    context["lt_nav_quote_route"] = "contact"
    return context
