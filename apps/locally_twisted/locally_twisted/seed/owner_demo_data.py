"""Seed fake owner-action records for local backend access testing.

These records are intentionally synthetic. They make the owner phone page and
assistant DTO contract usable on localhost without real customers, live OAuth,
or customer-facing sends.
"""
from __future__ import annotations

import json
import re

import frappe
from frappe.utils import add_days, today

from locally_twisted.crm_pipeline import PIPELINE_FIELD
from locally_twisted.stage_cascade import LEAD_TASK_FIELD


DEMO_MARKER = "LT-DEMO-OWNER-ACTIONS"
DEMO_DOMAIN = "example.invalid"


def execute(cleanup: bool = False, marker: str = DEMO_MARKER) -> str:
    marker = _clean_marker(marker)
    original_user = frappe.session.user
    frappe.set_user("Administrator")
    try:
        if _truthy(cleanup):
            summary = cleanup_demo_data(marker)
        else:
            summary = sync(marker)
        frappe.db.commit()
        print(json.dumps(summary, indent=2, sort_keys=True, default=str))
        return json.dumps(summary, sort_keys=True, default=str)
    finally:
        frappe.set_user(original_user)


def sync(marker: str = DEMO_MARKER) -> dict[str, object]:
    marker = _clean_marker(marker)
    cleanup_demo_data(marker)
    created: dict[str, list[str]] = {
        "Lead": [],
        "Customer": [],
        "Contact": [],
        "Sales Order": [],
    }

    leads = [
        _create_lead(
            marker=marker,
            slug="avery-new",
            first_name="Avery",
            last_name="Demo",
            phone="801-555-0101",
            stage="New Inquiry",
            occasion="Birthday Party",
            event_in_days=3,
            location="Sandy, Utah",
            preferred="Text",
        ),
        _create_lead(
            marker=marker,
            slug="morgan-quote",
            first_name="Morgan",
            last_name="Sample",
            phone="801-555-0102",
            stage="Quote Sent/Awaiting Approval",
            occasion="School Event",
            event_in_days=8,
            location="Draper, Utah",
            preferred="Phone",
        ),
        _create_lead(
            marker=marker,
            slug="riley-approved",
            first_name="Riley",
            last_name="Practice",
            phone="801-555-0103",
            stage="Approved",
            occasion="Corporate Event",
            event_in_days=12,
            location="Salt Lake City, Utah",
            preferred="Text",
        ),
    ]
    created["Lead"].extend(lead.name for lead in leads)

    customer = _create_customer(marker)
    contact = _create_contact(marker, customer.name)
    order = _create_sales_order(marker, customer.name)
    created["Customer"].append(customer.name)
    created["Contact"].append(contact.name)
    created["Sales Order"].append(order.name)

    return {
        "ok": True,
        "marker": marker,
        "synthetic_only": True,
        "customer_send_allowed": False,
        "created": created,
    }


def cleanup_demo_data(marker: str = DEMO_MARKER) -> dict[str, object]:
    marker = _clean_marker(marker)
    deleted: dict[str, list[str]] = {}

    lead_names = _names_like("Lead", ["lead_name", "email_id"], marker)
    customer_names = _names_like("Customer", ["customer_name"], marker)
    contact_names = set(_contact_names_for(marker, lead_names, customer_names))
    sales_order_names = _sales_orders_for(marker, customer_names)

    for doctype, names in (
        ("Email Queue", _references_to("Email Queue", lead_names, sales_order_names)),
        ("Communication", _references_to("Communication", lead_names, sales_order_names)),
        ("Comment", _references_to("Comment", lead_names, sales_order_names)),
        ("Task", _tasks_for_leads(lead_names)),
        ("Sales Order", sales_order_names),
        ("Contact", sorted(contact_names)),
        ("Customer", customer_names),
        ("Lead", lead_names),
    ):
        deleted[doctype] = _delete_many(doctype, names)

    return {
        "ok": True,
        "marker": marker,
        "cleanup": True,
        "deleted": deleted,
    }


def _create_lead(
    *,
    marker: str,
    slug: str,
    first_name: str,
    last_name: str,
    phone: str,
    stage: str,
    occasion: str,
    event_in_days: int,
    location: str,
    preferred: str,
):
    email = f"{slug}.{_email_marker(marker)}@{DEMO_DOMAIN}"
    fields = {
        "doctype": "Lead",
        "lead_name": f"{first_name} {last_name} - {marker}",
        "first_name": first_name,
        "last_name": last_name,
        "email_id": email,
        "mobile_no": phone,
        "status": "Lead",
        PIPELINE_FIELD: stage,
    }
    for fieldname, value in {
        "custom_event_date": add_days(today(), event_in_days),
        "custom_event_time": "10:00 AM",
        "custom_event_location": location,
        "custom_preferred_contact_method": preferred,
        "custom_occasion_type": occasion,
    }.items():
        if frappe.get_meta("Lead").has_field(fieldname):
            fields[fieldname] = value

    lead = frappe.get_doc(fields)
    lead.flags.lt_defer_customer_ack = True
    lead.insert(ignore_permissions=True)
    return lead


def _create_customer(marker: str):
    customer = frappe.get_doc(
        {
            "doctype": "Customer",
            "customer_name": f"{marker} Calendar Client",
            "customer_type": "Individual",
            "customer_group": _default_customer_group(),
            "territory": _default_territory(),
        }
    )
    customer.insert(ignore_permissions=True)
    return customer


def _create_contact(marker: str, customer_name: str):
    contact = frappe.get_doc(
        {
            "doctype": "Contact",
            "first_name": "Jordan",
            "last_name": "Calendar Demo",
            "email_ids": [
                {
                    "email_id": f"jordan.calendar.{_email_marker(marker)}@{DEMO_DOMAIN}",
                    "is_primary": 1,
                }
            ],
            "phone_nos": [
                {
                    "phone": "801-555-0104",
                    "is_primary_mobile_no": 1,
                    "is_primary_phone": 1,
                }
            ],
            "links": [{"link_doctype": "Customer", "link_name": customer_name}],
        }
    )
    contact.insert(ignore_permissions=True)
    return contact


def _create_sales_order(marker: str, customer_name: str):
    item = _demo_sales_item()
    order = frappe.get_doc(
        {
            "doctype": "Sales Order",
            "customer": customer_name,
            "transaction_date": today(),
            "delivery_date": add_days(today(), 6),
            "company": _default_company(),
            "items": [
                {
                    "item_code": item["item_code"],
                    "item_name": item.get("item_name"),
                    "description": f"{marker} synthetic booking line",
                    "qty": 1,
                    "rate": 125,
                    "delivery_date": add_days(today(), 6),
                    "uom": item.get("stock_uom") or "Nos",
                }
            ],
        }
    )
    order.insert(ignore_permissions=True)
    return order


def _demo_sales_item() -> dict[str, str]:
    for filters in (
        {"disabled": 0, "is_sales_item": 1, "is_stock_item": 0, "has_variants": 0},
        {"disabled": 0, "is_sales_item": 1, "has_variants": 0},
        {"disabled": 0, "is_sales_item": 1},
    ):
        rows = frappe.get_all(
            "Item",
            filters=filters,
            fields=["item_code", "item_name", "stock_uom"],
            order_by="modified desc",
            limit_page_length=1,
        )
        if rows:
            return rows[0]
    frappe.throw("No enabled sales Item is available for owner demo Sales Order seeding")


def _default_company() -> str:
    company = frappe.defaults.get_global_default("company")
    if company:
        return company
    return frappe.get_all("Company", pluck="name", limit_page_length=1)[0]


def _default_customer_group() -> str:
    group = frappe.db.get_value("Customer Group", {"is_group": 0}, "name")
    if group:
        return group
    return frappe.get_all("Customer Group", pluck="name", limit_page_length=1)[0]


def _default_territory() -> str:
    territory = frappe.db.get_value("Territory", {"is_group": 0}, "name")
    if territory:
        return territory
    return frappe.get_all("Territory", pluck="name", limit_page_length=1)[0]


def _contact_names_for(marker: str, lead_names: list[str], customer_names: list[str]) -> list[str]:
    names = set(_names_like("Contact", ["first_name", "last_name"], marker))
    linked_names = [*lead_names, *customer_names]
    if linked_names:
        for row in frappe.get_all(
            "Dynamic Link",
            filters={"link_name": ["in", linked_names], "parenttype": "Contact"},
            fields=["parent"],
            limit_page_length=500,
        ):
            names.add(row.parent)
    email_filter = f"%{_email_marker(marker)}@{DEMO_DOMAIN}"
    for row in frappe.get_all(
        "Contact Email",
        filters={"email_id": ["like", email_filter]},
        fields=["parent"],
        limit_page_length=500,
    ):
        names.add(row.parent)
    return sorted(names)


def _sales_orders_for(marker: str, customer_names: list[str]) -> list[str]:
    names = set()
    if customer_names:
        names.update(
            frappe.get_all(
                "Sales Order",
                filters={"customer": ["in", customer_names]},
                pluck="name",
                limit_page_length=500,
            )
        )
    for row in frappe.get_all(
        "Sales Order Item",
        filters={"description": ["like", f"%{marker}%"]},
        fields=["parent"],
        limit_page_length=500,
    ):
        names.add(row.parent)
    return sorted(names)


def _references_to(doctype: str, lead_names: list[str], sales_order_names: list[str]) -> list[str]:
    if not frappe.db.exists("DocType", doctype):
        return []
    names = set()
    for reference_doctype, reference_names in (
        ("Lead", lead_names),
        ("Sales Order", sales_order_names),
    ):
        if not reference_names:
            continue
        names.update(
            frappe.get_all(
                doctype,
                filters={
                    "reference_doctype": reference_doctype,
                    "reference_name": ["in", reference_names],
                },
                pluck="name",
                limit_page_length=500,
            )
        )
    return sorted(names)


def _tasks_for_leads(lead_names: list[str]) -> list[str]:
    if not lead_names or not frappe.get_meta("Task").has_field(LEAD_TASK_FIELD):
        return []
    return frappe.get_all(
        "Task",
        filters={LEAD_TASK_FIELD: ["in", lead_names]},
        pluck="name",
        limit_page_length=500,
    )


def _names_like(doctype: str, fields: list[str], marker: str) -> list[str]:
    names = set()
    meta = frappe.get_meta(doctype)
    for field in fields:
        if field != "name" and not meta.has_field(field):
            continue
        names.update(
            frappe.get_all(
                doctype,
                filters={field: ["like", f"%{marker}%"]},
                pluck="name",
                limit_page_length=500,
            )
        )
    return sorted(names)


def _delete_many(doctype: str, names: list[str]) -> list[str]:
    deleted = []
    for name in names:
        if not frappe.db.exists(doctype, name):
            continue
        doc = frappe.get_doc(doctype, name)
        if getattr(doc, "docstatus", 0) == 1:
            doc.cancel()
        frappe.delete_doc(doctype, name, force=True, ignore_permissions=True)
        deleted.append(name)
    return deleted


def _clean_marker(marker: str) -> str:
    marker = (marker or DEMO_MARKER).strip()
    if not re.fullmatch(r"[A-Z0-9][A-Z0-9_-]{4,80}", marker):
        frappe.throw("Owner demo marker must be uppercase letters, numbers, dashes, or underscores.")
    return marker


def _email_marker(marker: str) -> str:
    return marker.lower().replace("_", "-")


def _truthy(value) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    return bool(value)
