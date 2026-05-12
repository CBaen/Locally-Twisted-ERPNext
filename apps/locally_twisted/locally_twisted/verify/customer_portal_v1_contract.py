"""Verify the LT-owned customer portal V1 contract."""
from __future__ import annotations

import json
import time
from typing import Any

import frappe


class ContractFail(Exception):
    pass


REQUIRED_MODULE_KEYS = {
    "events",
    "quotes",
    "billing",
    "files",
    "checklist",
    "repeat",
    "follow_up",
    "organization",
}

INDIVIDUAL_ROUTES = {
    "me": "data-lt-account-dashboard",
    "account/events": "data-lt-account-events",
    "account/quotes": "data-lt-account-quotes",
    "account/billing": "data-lt-account-billing",
    "account/files": "data-lt-account-files",
    "account/checklist": "data-lt-account-checklist",
    "account/repeat": "data-lt-account-repeat",
    "account/follow_up": "data-lt-account-follow-up",
}

ORGANIZATION_ROUTES = {
    "organization": "data-lt-organization-dashboard",
    "organization/events": "data-lt-organization-events",
    "organization/billing": "data-lt-organization-billing",
    "organization/files": "data-lt-organization-files",
    "organization/people": "data-lt-organization-people",
}

FORBIDDEN_MARKERS = {
    "Manage third party apps",
    "Opportunity",
    "SHORT NOTICE",
    "Stay in the loop",
    "Timesheets",
    "Material Request",
    "Supplier Quotation",
    "Gross Profit",
    "Buying",
}

REQUIRED_SHELL_MARKERS = {
    "lt-customer-portal.css",
    "lt-portal__metric",
}


def run() -> dict[str, Any]:
    original_user = frappe.session.user
    try:
        return {"ok": True, **_run_contract()}
    except ContractFail as exc:
        return {"ok": False, "failures": [str(exc)]}
    except Exception:
        return {"ok": False, "failures": [frappe.get_traceback()]}
    finally:
        frappe.set_user(original_user)
        frappe.db.rollback()


def _run_contract() -> dict[str, Any]:
    from locally_twisted.customer_portal import (
        get_customer_portal_summary,
        register_customer_portal_file,
        request_repeat_event,
        set_customer_checklist_response,
        submit_customer_change_request,
    )

    fixture = _make_customer_fixture()
    frappe.set_user(fixture["user"])
    frappe.cache.hdel("portal_menu_items", fixture["user"])

    summary = get_customer_portal_summary()
    _assert_module_summary(summary)

    sales_order = frappe.get_doc("Sales Order", fixture["sales_order"])
    original_delivery_date = sales_order.get("delivery_date")
    change = submit_customer_change_request(
        "Sales Order",
        sales_order.name,
        "event_timing",
        {"requested_start": "15:00", "reason": "Venue access changed."},
    )
    if not change.get("change_request"):
        raise ContractFail(f"customer change request did not return a request id: {change}")
    sales_order.reload()
    if sales_order.get("delivery_date") != original_delivery_date:
        raise ContractFail("customer change request directly mutated Sales Order delivery_date")

    checklist = set_customer_checklist_response("Sales Order", sales_order.name, "venue_access", True)
    if checklist.get("completed") is not True:
        raise ContractFail(f"checklist response did not save completed=True: {checklist}")

    repeat = request_repeat_event("Sales Order", sales_order.name, "Same basic setup next year.")
    if not repeat.get("change_request"):
        raise ContractFail(f"repeat request did not create a review request: {repeat}")
    if frappe.db.exists("Sales Order", {"customer": fixture["customer"], "po_no": "Same basic setup next year."}):
        raise ContractFail("repeat request created or mutated an order instead of a review request")

    portal_file = _assert_customer_portal_file_registration_guard(
        fixture,
        sales_order.name,
        register_customer_portal_file,
    )

    rendered = _render_required_routes()
    _assert_portal_menu()

    return {
        "customer_user": fixture["user"],
        "modules": sorted(summary["modules"].keys()),
        "rendered_routes": sorted(rendered),
        "change_request": change["change_request"],
        "repeat_request": repeat["change_request"],
        "portal_file": portal_file,
        "rolled_back": True,
    }


def _assert_module_summary(summary: dict[str, Any]) -> None:
    modules = summary.get("modules") or {}
    missing = sorted(REQUIRED_MODULE_KEYS - set(modules))
    if missing:
        raise ContractFail(f"customer portal summary missing modules: {', '.join(missing)}")
    if not summary.get("identity", {}).get("customers"):
        raise ContractFail("customer portal summary did not resolve linked Customer identity")
    if "docstatus" in json.dumps(summary).lower():
        raise ContractFail("customer portal summary leaked raw ERPNext docstatus language")


def _render_required_routes() -> set[str]:
    from frappe.website.serve import get_response_content

    rendered: set[str] = set()
    for route, marker in {**INDIVIDUAL_ROUTES, **ORGANIZATION_ROUTES}.items():
        html = get_response_content(route)
        if marker not in html:
            raise ContractFail(f"{route} did not render required marker {marker}")
        expected_view_marker = "Organization view" if route in ORGANIZATION_ROUTES else "Private account view"
        missing_shell = sorted(term for term in REQUIRED_SHELL_MARKERS | {expected_view_marker} if term not in html)
        if missing_shell:
            raise ContractFail(f"{route} did not render branded account shell markers: {', '.join(missing_shell)}")
        forbidden = sorted(term for term in FORBIDDEN_MARKERS if term in html)
        if forbidden:
            raise ContractFail(f"{route} exposed forbidden portal markers: {', '.join(forbidden)}")
        rendered.add(route)
    return rendered


def _assert_portal_menu() -> None:
    from frappe.website.utils import get_portal_sidebar_items

    routes = {
        str(row.get("route"))
        for row in get_portal_sidebar_items()
        if row.get("enabled") and row.get("role") == "Customer"
    }
    expected = {
        "/account/quotes",
        "/account/events",
        "/account/billing",
        "/account/files",
        "/account/checklist",
        "/account/repeat",
        "/account/follow-up",
        "/organization",
    }
    if routes != expected:
        raise ContractFail(f"customer portal sidebar routes drifted: {sorted(routes)}")


def _assert_customer_portal_file_registration_guard(
    fixture: dict[str, str],
    sales_order: str,
    register_file: Any,
) -> str:
    valid_file = _insert_file(
        fixture["user"],
        "lt-portal-valid",
        "Sales Order",
        sales_order,
    )
    result = register_file(
        "Sales Order",
        sales_order,
        valid_file.name,
        "Reference",
        "Customer-owned reference",
    )
    portal_file = result.get("portal_file")
    if not portal_file:
        raise ContractFail(f"valid customer-owned source file did not register: {result}")
    portal_doc = frappe.get_doc("LT Customer Portal File", portal_file)
    if portal_doc.file != valid_file.name or not portal_doc.uploaded_by_customer:
        raise ContractFail("valid customer portal file did not preserve file/uploaded_by_customer fields")

    staff_file = _insert_file(
        "Administrator",
        "lt-portal-staff-owned",
        "Sales Order",
        sales_order,
    )
    _expect_file_registration_blocked(
        register_file,
        "Sales Order",
        sales_order,
        staff_file.name,
        "staff-owned file attached to the same source",
    )

    wrong_source_file = _insert_file(
        fixture["user"],
        "lt-portal-wrong-source",
        "Customer",
        fixture["customer"],
    )
    _expect_file_registration_blocked(
        register_file,
        "Sales Order",
        sales_order,
        wrong_source_file.name,
        "customer-owned file attached to a different source",
    )

    for blocked_file in (staff_file.name, wrong_source_file.name):
        if frappe.db.exists("LT Customer Portal File", {"file": blocked_file}):
            raise ContractFail(f"blocked file was still registered in LT Customer Portal File: {blocked_file}")

    return str(portal_file)


def _expect_file_registration_blocked(
    register_file: Any,
    source_doctype: str,
    source_name: str,
    file_name: str,
    case_label: str,
) -> None:
    try:
        register_file(source_doctype, source_name, file_name, "Reference", case_label)
    except (frappe.PermissionError, frappe.ValidationError):
        return
    except Exception as exc:
        raise ContractFail(f"{case_label} failed with the wrong exception type: {type(exc).__name__}: {exc}") from exc
    raise ContractFail(f"{case_label} was allowed to register as a customer-uploaded portal file")


def _make_customer_fixture() -> dict[str, str]:
    token = str(time.time_ns())
    email = f"lt-portal-v1-{token}@example.invalid"
    customer = frappe.get_doc(
        {
            "doctype": "Customer",
            "customer_name": f"LT Portal V1 Customer {token}",
            "customer_type": "Company",
        }
    ).insert(ignore_permissions=True)
    user = frappe.get_doc(
        {
            "doctype": "User",
            "email": email,
            "first_name": "Portal",
            "last_name": "V1",
            "enabled": 1,
            "user_type": "Website User",
            "send_welcome_email": 0,
            "roles": [{"role": "Customer"}],
        }
    ).insert(ignore_permissions=True)
    contact = frappe.get_doc(
        {
            "doctype": "Contact",
            "first_name": "Portal",
            "last_name": "V1",
            "user": user.name,
            "email_ids": [{"email_id": email, "is_primary": 1}],
            "links": [{"link_doctype": "Customer", "link_name": customer.name}],
        }
    ).insert(ignore_permissions=True)
    address = frappe.get_doc(
        {
            "doctype": "Address",
            "address_title": f"LT Portal V1 Venue {token}",
            "address_type": "Shipping",
            "address_line1": "123 Portal Way",
            "city": "Ogden",
            "state": "UT",
            "pincode": "84401",
            "country": "United States",
            "links": [{"link_doctype": "Customer", "link_name": customer.name}],
        }
    ).insert(ignore_permissions=True)
    item_code = _first_sales_item()
    sales_order = frappe.get_doc(
        {
            "doctype": "Sales Order",
            "customer": customer.name,
            "customer_address": address.name,
            "delivery_date": frappe.utils.add_days(frappe.utils.nowdate(), 14),
            "order_type": "Sales",
            "items": [{"item_code": item_code, "qty": 1, "rate": 25}],
        }
    ).insert(ignore_permissions=True)

    frappe.get_doc(
        {
            "doctype": "LT Organization Portal Membership",
            "customer": customer.name,
            "contact": contact.name,
            "user": user.name,
            "organization_role": "Org Admin",
            "enabled": 1,
        }
    ).insert(ignore_permissions=True)

    return {
        "customer": customer.name,
        "user": user.name,
        "contact": contact.name,
        "address": address.name,
        "sales_order": sales_order.name,
    }


def _insert_file(owner: str, label: str, attached_to_doctype: str, attached_to_name: str):
    original_user = frappe.session.user
    token = str(time.time_ns())
    try:
        frappe.set_user(owner)
        return frappe.get_doc(
            {
                "doctype": "File",
                "file_name": f"{label}-{token}.txt",
                "is_private": 1,
                "content": f"portal fixture {label} {token}".encode("utf-8"),
                "attached_to_doctype": attached_to_doctype,
                "attached_to_name": attached_to_name,
            }
        ).insert(ignore_permissions=True)
    finally:
        frappe.set_user(original_user)


def _first_sales_item() -> str:
    item = frappe.db.get_value("Item", {"disabled": 0, "is_sales_item": 1, "has_variants": 0}, "name")
    if not item:
        raise ContractFail("No enabled non-template sales Item exists for customer portal contract")
    return str(item)
