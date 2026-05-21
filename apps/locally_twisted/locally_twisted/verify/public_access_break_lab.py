"""Local-only helpers for public-write and access-boundary break probes.

These helpers intentionally mutate the local ERPNext site. They are not release
checks and must never be run against staging or live.
"""
from __future__ import annotations

from typing import Any

import frappe


MARKETING_REVIEW_ROLE = "LT Marketing Review Access"
SUPPLIER_ROUTES = {
    "/rfq",
    "/supplier-quotations",
    "/purchase-orders",
    "/purchase-invoices",
}


def state() -> dict[str, Any]:
    """Return the narrow state this break lab mutates and restores."""
    website = frappe.get_single("Website Settings")
    portal = frappe.get_single("Portal Settings")
    return {
        "website_settings": {
            "disable_signup": website.get("disable_signup"),
            "hide_login": website.get("hide_login"),
        },
        "portal_settings": {
            "default_role": portal.get("default_role"),
            "default_portal_home": portal.get("default_portal_home"),
            "supplier_routes": [
                {
                    "title": row.title,
                    "route": row.route,
                    "role": row.role,
                    "enabled": row.enabled,
                }
                for row in portal.get("menu") or []
                if row.route in SUPPLIER_ROUTES
            ],
        },
        "marketing_docperm_rows": frappe.db.get_all(
            "DocPerm",
            filters={"role": MARKETING_REVIEW_ROLE},
            fields=["name", "parent", "role", "read", "write", "create", "delete"],
            order_by="parent asc, name asc",
        ),
    }


def break_public_signup_default_customer() -> dict[str, Any]:
    """Open public signup and auto-assign Customer to new portal users."""
    before = state()
    website = frappe.get_single("Website Settings")
    website.disable_signup = 0
    website.save(ignore_permissions=True)

    portal = frappe.get_single("Portal Settings")
    portal.default_role = "Customer"
    portal.save(ignore_permissions=True)

    frappe.db.commit()
    frappe.clear_cache()
    return {
        "trigger": "public_signup_default_customer_enabled",
        "before": before,
        "after": state(),
    }


def restore_invite_only_portal() -> dict[str, Any]:
    """Restore invite-only customer portal settings."""
    before = state()
    website = frappe.get_single("Website Settings")
    website.disable_signup = 1
    website.hide_login = 0
    website.save(ignore_permissions=True)

    portal = frappe.get_single("Portal Settings")
    portal.default_role = None
    portal.default_portal_home = "me"
    portal.save(ignore_permissions=True)

    frappe.db.commit()
    frappe.clear_cache()
    return {
        "trigger": "restore_invite_only_portal",
        "before": before,
        "after": state(),
    }


def break_supplier_routes_as_customer() -> dict[str, Any]:
    """Expose supplier portal routes to Customer by changing Portal Settings rows."""
    before = state()
    portal = frappe.get_single("Portal Settings")
    for row in portal.get("menu") or []:
        if row.route in SUPPLIER_ROUTES:
            row.role = "Customer"
            row.enabled = 1
    portal.save(ignore_permissions=True)
    frappe.db.commit()
    frappe.clear_cache()
    return {
        "trigger": "supplier_routes_changed_to_customer",
        "before": before,
        "after": state(),
    }


def restore_supplier_routes() -> dict[str, Any]:
    """Restore supplier portal routes to Supplier-only menu rows."""
    before = state()
    portal = frappe.get_single("Portal Settings")
    for row in portal.get("menu") or []:
        if row.route in SUPPLIER_ROUTES:
            row.role = "Supplier"
            row.enabled = 1
    portal.save(ignore_permissions=True)
    frappe.db.commit()
    frappe.clear_cache()
    return {
        "trigger": "restore_supplier_routes",
        "before": before,
        "after": state(),
    }


def break_marketing_docperm_lead_read() -> dict[str, Any]:
    """Grant the external marketing review role a direct Lead DocPerm row."""
    before = state()
    if not frappe.db.exists(
        "DocPerm",
        {"parent": "Lead", "role": MARKETING_REVIEW_ROLE, "permlevel": 0},
    ):
        frappe.get_doc(
            {
                "doctype": "DocPerm",
                "parent": "Lead",
                "parenttype": "DocType",
                "parentfield": "permissions",
                "role": MARKETING_REVIEW_ROLE,
                "permlevel": 0,
                "read": 1,
            }
        ).insert(ignore_permissions=True)
    frappe.db.commit()
    frappe.clear_cache(doctype="Lead")
    return {
        "trigger": "marketing_review_role_direct_lead_docperm",
        "before": before,
        "after": state(),
    }


def restore_marketing_docperms() -> dict[str, Any]:
    """Remove direct DocPerm rows for the external marketing review role."""
    before = state()
    for name in frappe.db.get_all(
        "DocPerm",
        filters={"role": MARKETING_REVIEW_ROLE},
        pluck="name",
    ):
        frappe.delete_doc("DocPerm", name, ignore_permissions=True, force=True)
    frappe.db.commit()
    frappe.clear_cache()
    return {
        "trigger": "restore_marketing_review_docperms",
        "before": before,
        "after": state(),
    }
