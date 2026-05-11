"""Persisted customer portal fixture for browser-only verification."""
from __future__ import annotations

import time
from typing import Any

import frappe
from frappe.utils.password import update_password


def create(password: str | None = None) -> dict[str, Any]:
    if not password:
        frappe.throw("customer_portal_review_fixture.create requires a password")

    token = str(time.time_ns())
    email = f"lt-portal-visual-{token}@example.invalid"
    original_user = frappe.session.user
    frappe.set_user("Administrator")
    try:
        customer = frappe.get_doc(
            {
                "doctype": "Customer",
                "customer_name": f"LT Portal Visual Customer {token}",
                "customer_type": "Company",
            }
        ).insert(ignore_permissions=True)
        user = frappe.get_doc(
            {
                "doctype": "User",
                "email": email,
                "first_name": "Avery",
                "last_name": "Preview",
                "enabled": 1,
                "user_type": "Website User",
                "send_welcome_email": 0,
                "roles": [{"role": "Customer"}],
            }
        ).insert(ignore_permissions=True)
        update_password(user.name, password)
        contact = frappe.get_doc(
            {
                "doctype": "Contact",
                "first_name": "Avery",
                "last_name": "Preview",
                "user": user.name,
                "email_ids": [{"email_id": email, "is_primary": 1}],
                "links": [{"link_doctype": "Customer", "link_name": customer.name}],
            }
        ).insert(ignore_permissions=True)
        address = frappe.get_doc(
            {
                "doctype": "Address",
                "address_title": f"LT Portal Visual Venue {token}",
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
                "items": [{"item_code": item_code, "qty": 1, "rate": 125}],
            }
        ).insert(ignore_permissions=True)

        quote = _make_ready_quote(customer.name, item_code)
        file_doc = _make_customer_file(user.name, sales_order.name, token)
        portal_file = frappe.get_doc(
            {
                "doctype": "LT Customer Portal File",
                "source_doctype": "Sales Order",
                "source_name": sales_order.name,
                "file": file_doc.name,
                "purpose": "Inspiration",
                "label": "Color palette reference",
                "customer": customer.name,
                "owner_user": user.name,
                "visible_to_customer": 1,
                "uploaded_by_customer": 1,
            }
        ).insert(ignore_permissions=True)
        membership = frappe.get_doc(
            {
                "doctype": "LT Organization Portal Membership",
                "customer": customer.name,
                "contact": contact.name,
                "user": user.name,
                "organization_role": "Org Admin",
                "enabled": 1,
            }
        ).insert(ignore_permissions=True)

        frappe.db.commit()
        return {
            "ok": True,
            "token": token,
            "email": email,
            "customer": customer.name,
            "contact": contact.name,
            "user": user.name,
            "address": address.name,
            "sales_order": sales_order.name,
            "quotation": quote.name if quote else "",
            "file": file_doc.name,
            "portal_file": portal_file.name,
            "membership": membership.name,
        }
    finally:
        frappe.set_user(original_user)


def cleanup(email: str | None = None, token: str | None = None) -> dict[str, Any]:
    if not email and not token:
        frappe.throw("customer_portal_review_fixture.cleanup requires email or token")

    original_user = frappe.session.user
    frappe.set_user("Administrator")
    deleted: list[str] = []
    try:
        if not email and token:
            email = f"lt-portal-visual-{token}@example.invalid"
        token = token or (email or "").replace("lt-portal-visual-", "").replace("@example.invalid", "")
        customer = frappe.db.get_value("Customer", {"customer_name": f"LT Portal Visual Customer {token}"}, "name")

        _delete_many("LT Customer Portal File", {"owner_user": email}, deleted)
        _delete_many("LT Organization Portal Membership", {"user": email}, deleted)
        _delete_many("File", {"owner": email}, deleted)
        if customer:
            _delete_many("Quotation", {"party_name": customer}, deleted)
            _delete_many("Sales Order", {"customer": customer}, deleted)
            _delete_linked_addresses(customer, deleted)
        _delete_many("Contact", {"user": email}, deleted)
        if email and frappe.db.exists("User", email):
            _delete_doc("User", email, deleted)
        if customer and frappe.db.exists("Customer", customer):
            _delete_doc("Customer", customer, deleted)

        frappe.db.commit()
        return {"ok": True, "deleted": deleted}
    finally:
        frappe.set_user(original_user)


def _make_ready_quote(customer: str, item_code: str):
    if not frappe.db.exists("DocType", "Quotation"):
        return None
    quote = frappe.get_doc(
        {
            "doctype": "Quotation",
            "quotation_to": "Customer",
            "party_name": customer,
            "transaction_date": frappe.utils.nowdate(),
            "valid_till": frappe.utils.add_days(frappe.utils.nowdate(), 21),
            "items": [{"item_code": item_code, "qty": 1, "rate": 125}],
        }
    )
    if quote.meta.has_field("custom_lt_product_quote_status"):
        quote.custom_lt_product_quote_status = "Ready For Customer Review"
    return quote.insert(ignore_permissions=True)


def _make_customer_file(owner: str, sales_order: str, token: str):
    original_user = frappe.session.user
    try:
        frappe.set_user(owner)
        return frappe.get_doc(
            {
                "doctype": "File",
                "file_name": f"lt-portal-visual-{token}.txt",
                "is_private": 1,
                "content": f"portal visual fixture {token}".encode("utf-8"),
                "attached_to_doctype": "Sales Order",
                "attached_to_name": sales_order,
            }
        ).insert(ignore_permissions=True)
    finally:
        frappe.set_user(original_user)


def _delete_many(doctype: str, filters: dict[str, Any], deleted: list[str]) -> None:
    if not frappe.db.exists("DocType", doctype):
        return
    for name in frappe.get_all(doctype, filters=filters, pluck="name"):
        _delete_doc(doctype, name, deleted)


def _delete_linked_addresses(customer: str, deleted: list[str]) -> None:
    links = frappe.get_all(
        "Dynamic Link",
        filters={"parenttype": "Address", "link_doctype": "Customer", "link_name": customer},
        pluck="parent",
    )
    for name in links:
        if frappe.db.exists("Address", name):
            _delete_doc("Address", name, deleted)


def _delete_doc(doctype: str, name: str, deleted: list[str]) -> None:
    try:
        frappe.delete_doc(doctype, name, force=True, ignore_permissions=True)
        deleted.append(f"{doctype}:{name}")
    except Exception:
        deleted.append(f"{doctype}:{name}:delete_failed")
        raise


def _first_sales_item() -> str:
    item = frappe.db.get_value("Item", {"disabled": 0, "is_sales_item": 1, "has_variants": 0}, "name")
    if not item:
        frappe.throw("No enabled non-template sales Item exists for customer portal visual fixture")
    return str(item)
