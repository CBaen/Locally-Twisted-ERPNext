"""Sync Locally Twisted customer/client portal menu boundaries.

Run in-process:
  bench --site frontend execute locally_twisted.seed.sync_customer_portal.execute
"""
from __future__ import annotations

import json
from typing import Any

import frappe


CUSTOMER_MENU = [
    {
        "route": "/account/quotes",
        "title": "Quotes",
        "role": "Customer",
        "reference_doctype": "Quotation",
    },
    {
        "route": "/account/events",
        "title": "Event Details",
        "role": "Customer",
        "reference_doctype": "Sales Order",
    },
    {
        "route": "/account/billing",
        "title": "Invoices & Receipts",
        "role": "Customer",
        "reference_doctype": "Sales Invoice",
    },
    {
        "route": "/account/files",
        "title": "Files & Inspiration",
        "role": "Customer",
        "reference_doctype": "File",
    },
    {
        "route": "/account/checklist",
        "title": "Customer Checklist",
        "role": "Customer",
        "reference_doctype": "LT Customer Checklist Response",
    },
    {
        "route": "/account/repeat",
        "title": "Repeat Client",
        "role": "Customer",
        "reference_doctype": "LT Customer Change Request",
    },
    {
        "route": "/account/follow-up",
        "title": "After-Event Follow-Up",
        "role": "Customer",
        "reference_doctype": "LT Customer Change Request",
    },
    {
        "route": "/organization",
        "title": "Organization Portal",
        "role": "Customer",
        "reference_doctype": "LT Organization Portal Membership",
    },
]

HIDDEN_PORTAL_ROUTES = {
    "/quotations",
    "/orders",
    "/invoices",
    "/addresses",
    "/project",
    "/shipments",
    "/issues",
    "/timesheets",
    "/material-requests",
    "/newsletters",
}

SUPPLIER_PORTAL_ROUTES = {
    "/rfq",
    "/supplier-quotations",
    "/purchase-orders",
    "/purchase-invoices",
}

WEBSITE_SETTINGS = {
    "disable_signup": 1,
    "hide_login": 0,
    "show_footer_on_login": 0,
}

WEBSHOP_GUEST_SETTINGS = {
    "login_required_to_view_products": 0,
    "hide_price_for_guest": 0,
    "enable_checkout": 1,
}


def execute(commit: bool = True) -> str:
    summary: dict[str, Any] = {
        "portal_settings": [],
        "customer_menu": [],
        "hidden_routes": [],
        "supplier_routes": [],
        "website_settings": [],
        "webshop_settings": [],
        "committed": False,
    }

    changed = False
    changed = _ensure_single_values("Website Settings", WEBSITE_SETTINGS, summary["website_settings"]) or changed
    changed = _ensure_single_values("Webshop Settings", WEBSHOP_GUEST_SETTINGS, summary["webshop_settings"]) or changed
    changed = _sync_portal_settings(summary) or changed

    if commit and changed:
        frappe.db.commit()
        summary["committed"] = True

    rendered = json.dumps(summary, sort_keys=True)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return rendered


def _ensure_single_values(doctype: str, fields: dict[str, Any], changes: list[str]) -> bool:
    doc = frappe.get_single(doctype)
    changed = False
    for fieldname, value in fields.items():
        if doc.get(fieldname) != value:
            doc.set(fieldname, value)
            changes.append(fieldname)
            changed = True
    if changed:
        doc.save(ignore_permissions=True)
    return changed


def _sync_portal_settings(summary: dict[str, Any]) -> bool:
    previous_flag = getattr(frappe.flags, "lt_syncing_customer_portal", False)
    frappe.flags.lt_syncing_customer_portal = True
    try:
        portal = frappe.get_single("Portal Settings")
        _set_value(portal, "default_portal_home", "me", summary["portal_settings"])
        _set_value(portal, "default_role", None, summary["portal_settings"])
        portal.sync_menu()
        portal.reload()

        changed = False
        changed = _set_value(portal, "default_portal_home", "me", summary["portal_settings"]) or changed
        changed = _set_value(portal, "default_role", None, summary["portal_settings"]) or changed
        changed = _set_value(portal, "hide_standard_menu", 0, summary["portal_settings"]) or changed

        for spec in CUSTOMER_MENU:
            changed = _ensure_menu_row(portal, spec, enabled=1, change_log=summary["customer_menu"]) or changed

        route_rows = {row.route: row for row in portal.get("menu", []) if row.get("route")}
        for route in sorted(HIDDEN_PORTAL_ROUTES):
            row = route_rows.get(route)
            if row and row.enabled:
                row.enabled = 0
                summary["hidden_routes"].append(route)
                changed = True

        for route in sorted(SUPPLIER_PORTAL_ROUTES):
            row = route_rows.get(route)
            if row and row.role != "Supplier":
                row.role = "Supplier"
                summary["supplier_routes"].append(route)
                changed = True

        if changed:
            portal.save(ignore_permissions=True)
        return changed
    finally:
        frappe.flags.lt_syncing_customer_portal = previous_flag


def _set_value(doc: Any, fieldname: str, value: Any, changes: list[str]) -> bool:
    if doc.get(fieldname) == value:
        return False
    doc.set(fieldname, value)
    changes.append(fieldname)
    return True


def _ensure_menu_row(doc: Any, spec: dict[str, Any], *, enabled: int, change_log: list[str]) -> bool:
    row = next((item for item in doc.get("menu", []) if item.get("route") == spec["route"]), None)
    changed = False
    if row is None:
        doc.append(
            "menu",
            {
                **spec,
                "enabled": enabled,
            },
        )
        change_log.append(f"created:{spec['route']}")
        return True

    for fieldname, value in {**spec, "enabled": enabled}.items():
        if row.get(fieldname) != value:
            row.set(fieldname, value)
            changed = True
    if changed:
        change_log.append(f"updated:{spec['route']}")
    return changed
