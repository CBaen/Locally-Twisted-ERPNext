"""
navbar_context.py — Inject Shop categories and mega-menu panel data into the
website context.

Triggered via update_website_context hook in hooks.py. Runs on every page
render. Reads the 11 Shop Items child Item Groups (Arches, Columns, ...) and
exposes them as `context.shop_categories` for backward compatibility, plus
three new mega-menu panel context keys added 2026-04-30:

  context["mega_special_occasions"]  — life-event leaf links
  context["mega_holidays_seasons"]   — holiday/seasonal leaf links (3 columns)
  context["mega_what_we_make"]       — product-type leaf links (3 columns, from
                                        live Item Group routes)

Per Agent 4 of plan-deepen research: this is the canonical injection point —
matches webshop's own pattern at webshop/webshop/shopping_cart/utils.py.
"""
from __future__ import annotations

import frappe


def update_website_context(context):
    """Add shop category context keys to the website context.

    Existing exports (preserved — do not remove):
      context["shop_categories"]  — list of {name, item_group_name, route, weightage}
      context["shop_root_route"]  — route of the "Shop Items" root group

    New exports added 2026-04-30 (mega menu panels):
      context["mega_special_occasions"]  — list of {label, route}
      context["mega_holidays_seasons"]   — list of {label, route, column}
                                            column: "winter_spring" | "spring_summer" |
                                                    "fall_winter"
      context["mega_what_we_make"]       — list of {label, route, column}
                                            column: "arrangements" | "installations" |
                                                    "accents"

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

    # Build a quick lookup: item_group_name -> route, for mega panel construction.
    route_by_name = {c["item_group_name"]: c["route"] for c in children}

    # ---- mega_special_occasions ------------------------------------------------
    # Life-event categories. Route targets: real Item Group routes where a
    # matching group exists; "seasonal-specialty" content-only for others.
    # Hetzner source: Special Occasions mega panel (single column, "Life Events").
    # Note: "Baby Reveal & Showers" and "Missionary Farewell" have no dedicated
    # ERPNext Item Group — they map to Seasonal & Specialty as content-only routes
    # (will 404 until a dedicated group or redirect is added in Phase 2).
    context["mega_special_occasions"] = [
        {
            "label": "Birthday Parties",
            "route": route_by_name.get("Seasonal & Specialty", "shop-items/seasonal-specialty"),
        },
        {
            "label": "Baby Reveal & Showers",
            "route": route_by_name.get("Seasonal & Specialty", "shop-items/seasonal-specialty"),
            "content_only": True,  # no dedicated ERPNext Item Group yet
        },
        {
            "label": "Graduations",
            "route": route_by_name.get("Seasonal & Specialty", "shop-items/seasonal-specialty"),
        },
        {
            "label": "Missionary Farewell",
            "route": route_by_name.get("Seasonal & Specialty", "shop-items/seasonal-specialty"),
            "content_only": True,
        },
        {
            "label": "Get-Well Bouquets",
            "route": route_by_name.get("Get-Well Bouquets", "shop-items/get-well-bouquets"),
        },
    ]

    # ---- mega_holidays_seasons -------------------------------------------------
    # Three-column grouping matching Hetzner's Winter & Spring / Spring & Summer /
    # Fall & Winter layout. All route targets are Seasonal & Specialty (the
    # single holiday-themed ERPNext group). Phase 2 can add dedicated groups and
    # update these routes — the column/label structure stays stable.
    seasonal_route = route_by_name.get("Seasonal & Specialty", "shop-items/seasonal-specialty")
    context["mega_holidays_seasons"] = [
        # column: winter_spring
        {"label": "New Year's Eve",    "route": seasonal_route, "column": "winter_spring"},
        {"label": "Valentine's Day",   "route": seasonal_route, "column": "winter_spring"},
        {"label": "St. Patrick's Day", "route": seasonal_route, "column": "winter_spring"},
        {"label": "Easter",            "route": seasonal_route, "column": "winter_spring"},
        # column: spring_summer
        {"label": "Mother's Day",      "route": route_by_name.get("Bouquets", "shop-items/bouquets"), "column": "spring_summer"},
        {"label": "Father's Day",      "route": route_by_name.get("Bouquets", "shop-items/bouquets"), "column": "spring_summer"},
        {"label": "Pride",             "route": seasonal_route, "column": "spring_summer"},
        {"label": "4th of July",       "route": seasonal_route, "column": "spring_summer"},
        # column: fall_winter
        {"label": "Fall",              "route": seasonal_route, "column": "fall_winter"},
        {"label": "Halloween",         "route": seasonal_route, "column": "fall_winter"},
        {"label": "Christmas",         "route": seasonal_route, "column": "fall_winter"},
    ]

    # ---- mega_what_we_make -----------------------------------------------------
    # Three-column grouping matching Hetzner's Arrangements / Installations /
    # Accents layout. Routes are LIVE Item Group routes from the running DB.
    # "Photo Frames" has no matching ERPNext Item Group — mapped to Table Decor
    # as the nearest category (content-only, flagged for Phase 2).
    context["mega_what_we_make"] = [
        # column: arrangements
        {"label": "Balloon Arches",   "route": route_by_name.get("Arches", "shop-items/arches"),           "column": "arrangements"},
        {"label": "Columns",          "route": route_by_name.get("Columns", "shop-items/columns"),          "column": "arrangements"},
        {"label": "Centerpieces",     "route": route_by_name.get("Table Decor", "shop-items/table-decor"),  "column": "arrangements"},
        {"label": "Helium Bouquets",  "route": route_by_name.get("Bouquets", "shop-items/bouquets"),        "column": "arrangements"},
        # column: installations
        {"label": "Organic Garlands", "route": route_by_name.get("Garlands", "shop-items/garlands"),        "column": "installations"},
        {"label": "Backdrops",        "route": route_by_name.get("Seasonal & Specialty", "shop-items/seasonal-specialty"), "column": "installations", "content_only": True},
        {"label": "Balloon Drops",    "route": route_by_name.get("Drops", "shop-items/drops"),              "column": "installations"},
        {"label": "Grab N Go",        "route": route_by_name.get("Grab & Go", "shop-items/grab-go"),        "column": "installations"},
        # column: accents
        {"label": "Stands & Easels",  "route": route_by_name.get("Stands & Easels", "shop-items/stands-easels"), "column": "accents"},
        {"label": "Table Decor",      "route": route_by_name.get("Table Decor", "shop-items/table-decor"),  "column": "accents"},
        {"label": "Deliveries",       "route": route_by_name.get("Deliveries", "shop-items/deliveries"),    "column": "accents"},
    ]

    context["shop_categories"] = children
    context["shop_root_route"] = shop_root
    return context
