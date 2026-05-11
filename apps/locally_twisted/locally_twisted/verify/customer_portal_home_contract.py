"""Verify the Locally Twisted customer account home is customer-safe."""
from __future__ import annotations

import time

import frappe


class ContractFail(Exception):
    pass


REQUIRED_MARKERS = {
    "data-lt-account-dashboard",
    "lt-customer-portal.css",
    "Private account view",
    "lt-portal__metric",
    "Event Details",
    "Invoices & Receipts",
    "Files & Inspiration",
    "Organization Portal",
}

FORBIDDEN_MARKERS = {
    "Manage third party apps",
    "Manage your apps",
    "third_party_apps",
    "Timesheets",
    "Material Requests",
    "Supplier Quotation",
    "Opportunity",
}


def run() -> dict:
    original_user = frappe.session.user
    try:
        result = _run_contract()
        return {"ok": True, **result}
    except ContractFail as exc:
        return {"ok": False, "failures": [str(exc)]}
    except Exception:
        return {"ok": False, "failures": [frappe.get_traceback()]}
    finally:
        frappe.set_user(original_user)
        frappe.db.rollback()


def _run_contract() -> dict:
    user = _make_rollback_customer_user()
    frappe.set_user(user)
    frappe.cache.hdel("portal_menu_items", user)

    html = _render_me()
    missing = sorted(marker for marker in REQUIRED_MARKERS if marker not in html)
    if missing:
        raise ContractFail("account home is missing LT markers: " + ", ".join(missing))

    forbidden = sorted(marker for marker in FORBIDDEN_MARKERS if marker in html)
    if forbidden:
        raise ContractFail("account home exposes native/internal markers: " + ", ".join(forbidden))

    sidebar_routes = _portal_sidebar_routes()
    expected_routes = {
        "/account/quotes",
        "/account/events",
        "/account/billing",
        "/account/files",
        "/account/checklist",
        "/account/repeat",
        "/account/follow-up",
        "/organization",
    }
    if set(sidebar_routes) != expected_routes:
        raise ContractFail(f"customer portal sidebar routes drifted: {sidebar_routes}")

    return {
        "customer_user": user,
        "rendered_route": "/me",
        "required_markers": sorted(REQUIRED_MARKERS),
        "sidebar_routes": sidebar_routes,
        "rolled_back": True,
    }


def _make_rollback_customer_user() -> str:
    email = f"lt-portal-contract-{int(time.time())}@example.invalid"
    customer = frappe.get_doc(
        {
            "doctype": "Customer",
            "customer_name": "LT Portal Contract Customer",
            "customer_type": "Individual",
        }
    ).insert(ignore_permissions=True)

    user = frappe.get_doc(
        {
            "doctype": "User",
            "email": email,
            "first_name": "Portal",
            "last_name": "Contract",
            "enabled": 1,
            "user_type": "Website User",
            "send_welcome_email": 0,
            "roles": [{"role": "Customer"}],
        }
    )
    user.insert(ignore_permissions=True)

    frappe.get_doc(
        {
            "doctype": "Contact",
            "first_name": "Portal",
            "last_name": "Contract",
            "user": user.name,
            "email_ids": [{"email_id": email, "is_primary": 1}],
            "links": [{"link_doctype": "Customer", "link_name": customer.name}],
        }
    ).insert(ignore_permissions=True)
    return user.name


def _render_me() -> str:
    from frappe.website.serve import get_response_content

    return get_response_content("me")


def _portal_sidebar_routes() -> list[str]:
    from frappe.website.utils import get_portal_sidebar_items

    return [
        str(row.get("route"))
        for row in get_portal_sidebar_items()
        if row.get("enabled") and row.get("role") == "Customer"
    ]
