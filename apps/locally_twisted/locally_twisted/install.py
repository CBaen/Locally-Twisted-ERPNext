"""Install and migration hooks for LT-owned ERPNext schema."""
from __future__ import annotations

import frappe

from locally_twisted.seed.sync_contact_intake_backend import execute as sync_contact_intake_backend
from locally_twisted.seed.sync_customer_portal import execute as sync_customer_portal

REQUIRED_INSTALL_ROLES = (
    "LT Owner Access",
    "LT Manager Access",
)


def after_install() -> None:
    """Ensure fresh Frappe Cloud sites receive the contact intake schema."""
    ensure_required_roles()
    sync_contact_intake_backend(commit=False)
    sync_customer_portal(commit=False)


def after_migrate() -> None:
    """Repair or refresh contact intake schema during bench/site updates."""
    ensure_required_roles()
    sync_contact_intake_backend(commit=False)
    sync_customer_portal(commit=False)


def ensure_required_roles() -> None:
    for role_name in REQUIRED_INSTALL_ROLES:
        if frappe.db.exists("Role", role_name):
            continue
        frappe.get_doc(
            {
                "doctype": "Role",
                "role_name": role_name,
                "desk_access": 1,
                "disabled": 0,
            }
        ).insert(ignore_permissions=True)
