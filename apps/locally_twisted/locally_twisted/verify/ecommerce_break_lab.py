"""Local-only helpers for controlled ecommerce break-lab probes.

These helpers intentionally mutate the local ERPNext site. They are not release
checks and must never be run against staging or live.
"""
from __future__ import annotations

from typing import Any

import frappe


EXPECTED_WEBSHOP_SETTINGS = {
    "enabled": 1,
    "show_price": 1,
    "login_required_to_view_products": 0,
    "hide_price_for_guest": 0,
    "enable_checkout": 1,
    "price_list": "Standard Selling",
    "default_customer_group": "Individual",
}


def state() -> dict[str, Any]:
    """Return the narrow state this break lab mutates and restores."""
    settings = frappe.get_single("Webshop Settings")
    return {
        "guest_portal_users": frappe.db.get_all(
            "Portal User",
            filters={"parent": "Guest", "parenttype": "Customer", "user": "Guest"},
            fields=["name", "parent", "parentfield", "parenttype", "user", "idx"],
            order_by="idx asc",
        ),
        "webshop_settings": {
            fieldname: settings.get(fieldname)
            for fieldname in EXPECTED_WEBSHOP_SETTINGS
        },
        "lt_ecommerce_paused": frappe.conf.get("lt_ecommerce_paused"),
    }


def break_guest_portal_link() -> dict[str, Any]:
    """Bypass Frappe document hooks and remove the Guest Portal User child row."""
    before = state()
    frappe.db.sql(
        """
        delete from `tabPortal User`
        where parent = %s
          and parenttype = %s
          and user = %s
        """,
        ("Guest", "Customer", "Guest"),
    )
    frappe.db.commit()
    _clear_guest_cache()
    return {
        "trigger": "direct_sql_delete_guest_portal_user",
        "before": before,
        "after": state(),
    }


def restore_guest_portal_link() -> dict[str, Any]:
    """Restore the required Customer:Guest -> User:Guest Portal User row."""
    before = state()
    customer = frappe.get_doc("Customer", "Guest")
    existing = [
        row
        for row in customer.get("portal_users") or []
        if row.user == "Guest"
    ]
    if not existing:
        customer.append("portal_users", {"user": "Guest"})
    customer.save(ignore_permissions=True)
    frappe.db.commit()
    _clear_guest_cache()
    return {
        "trigger": "restore_guest_portal_user",
        "before": before,
        "after": state(),
    }


def break_guest_price_visibility() -> dict[str, Any]:
    """Hide prices for Guest visitors by mutating Webshop Settings."""
    before = state()
    settings = frappe.get_single("Webshop Settings")
    settings.hide_price_for_guest = 1
    settings.save(ignore_permissions=True)
    frappe.db.commit()
    frappe.clear_cache()
    return {
        "trigger": "webshop_hide_price_for_guest_enabled",
        "before": before,
        "after": state(),
    }


def restore_webshop_settings() -> dict[str, Any]:
    """Restore the current LT Webshop Settings contract for public testing."""
    before = state()
    settings = frappe.get_single("Webshop Settings")
    for fieldname, value in EXPECTED_WEBSHOP_SETTINGS.items():
        settings.set(fieldname, value)
    settings.save(ignore_permissions=True)
    frappe.db.commit()
    frappe.clear_cache()
    return {
        "trigger": "restore_webshop_settings_contract",
        "before": before,
        "after": state(),
    }


def _clear_guest_cache() -> None:
    for doctype, name in (("Customer", "Guest"), ("User", "Guest"), ("Contact", "Guest-Guest")):
        frappe.clear_document_cache(doctype, name)
