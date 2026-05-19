"""Customer-safe portal data and actions for Locally Twisted accounts."""
from __future__ import annotations

import json
from typing import Any

import frappe
from frappe import _


READY_QUOTE_STATUS = "Ready For Customer Review"
CHANGE_REQUEST_STATUS = "Submitted"


MODULE_DEFINITIONS = {
    "events": {
        "label": "Event Details",
        "description": "Dates, locations, services, and current booking status.",
    },
    "quotes": {
        "label": "Quotes",
        "description": "Quotes that are ready for customer review.",
    },
    "billing": {
        "label": "Invoices & Receipts",
        "description": "Customer-safe invoices, receipts, and payment next steps.",
    },
    "files": {
        "label": "Files & Inspiration",
        "description": "Reference files and customer-visible event files.",
    },
    "checklist": {
        "label": "Checklist",
        "description": "Prep items that help the event go smoothly.",
    },
    "repeat": {
        "label": "Repeat Client",
        "description": "Request a similar event without starting from scratch.",
    },
    "follow_up": {
        "label": "After-Event Follow-Up",
        "description": "Receipts, review links, photos, and rebook prompts.",
    },
    "organization": {
        "label": "Organization Portal",
        "description": "Company, school, civic, and AP account tools.",
    },
}


def get_customer_portal_summary(user: str | None = None) -> dict[str, Any]:
    identity = resolve_customer_identity(user)
    customers = identity["customers"]
    contact_names = identity["contacts"]
    lead_names = _lead_names_for_contacts(contact_names)

    events = _event_summaries(customers, lead_names)
    quotes = _quote_summaries(customers, lead_names)
    invoices = _invoice_summaries(customers)
    payments = _payment_summaries(customers, events, invoices)
    files = _portal_file_summaries(customers, identity["user"])
    checklist = _checklist_summary(customers, identity["user"], events)
    organizations = _organization_memberships(identity["user"], contact_names, customers)
    follow_up = _follow_up_summary(events, invoices, files)

    modules = {
        "events": {"count": len(events), **MODULE_DEFINITIONS["events"]},
        "quotes": {"count": len(quotes), **MODULE_DEFINITIONS["quotes"]},
        "billing": {"count": len(invoices) + len(payments), **MODULE_DEFINITIONS["billing"]},
        "files": {"count": len(files), **MODULE_DEFINITIONS["files"]},
        "checklist": {"count": len(checklist["items"]), **MODULE_DEFINITIONS["checklist"]},
        "repeat": {"count": len(events), **MODULE_DEFINITIONS["repeat"]},
        "follow_up": {"count": len(follow_up["items"]), **MODULE_DEFINITIONS["follow_up"]},
        "organization": {"count": len(organizations), **MODULE_DEFINITIONS["organization"]},
    }

    return _json_safe({
        "identity": identity,
        "next_action": _next_action(events, quotes, invoices, payments),
        "modules": modules,
        "events": events,
        "quotes": quotes,
        "billing": {"invoices": invoices, "payment_requests": payments},
        "files": files,
        "checklist": checklist,
        "repeat": _repeat_summary(events),
        "follow_up": follow_up,
        "organizations": organizations,
    })


def get_organization_portal_summary(user: str | None = None) -> dict[str, Any]:
    summary = get_customer_portal_summary(user)
    org_customers = [row["customer"] for row in summary["organizations"] if row.get("enabled")]
    org_identity = dict(summary["identity"])
    org_identity["customers"] = org_customers
    return _json_safe({
        "identity": org_identity,
        "memberships": summary["organizations"],
        "events": [row for row in summary["events"] if row.get("customer") in org_customers],
        "billing": {
            "invoices": [row for row in summary["billing"]["invoices"] if row.get("customer") in org_customers],
            "payment_requests": [
                row for row in summary["billing"]["payment_requests"] if row.get("customer") in org_customers
            ],
        },
        "files": [row for row in summary["files"] if row.get("customer") in org_customers],
        "people": _organization_people(org_customers),
        "next_action": summary["next_action"],
    })


def resolve_customer_identity(user: str | None = None) -> dict[str, Any]:
    user = user or frappe.session.user
    if not user or user == "Guest":
        frappe.throw(_("Please log in to view your Locally Twisted account."), frappe.PermissionError)

    user_doc = frappe.get_doc("User", user)
    roles = {row.role for row in user_doc.get("roles", [])}
    if user_doc.user_type != "Website User" or "Customer" not in roles:
        frappe.throw(_("This account is not set up for the Locally Twisted customer portal."), frappe.PermissionError)

    contacts = frappe.get_all(
        "Contact",
        filters={"user": user},
        fields=["name", "first_name", "last_name"],
        order_by="modified desc",
    )
    contact_names = [row.name for row in contacts]
    customers = _customers_for_contacts(contact_names)
    return {
        "user": user,
        "display_name": user_doc.full_name or user_doc.first_name or user_doc.name,
        "contacts": contact_names,
        "customers": customers,
        "roles": sorted(roles),
    }


@frappe.whitelist()
def submit_customer_change_request(
    source_doctype: str | None = None,
    source_name: str | None = None,
    request_type: str | None = None,
    payload: str | dict[str, Any] | None = None,
) -> dict[str, Any]:
    source_doctype = _clean(source_doctype)
    source_name = _clean(source_name)
    request_type = _clean(request_type) or "general"
    payload_dict = _payload_dict(payload)
    identity = resolve_customer_identity()
    _assert_source_access(identity, source_doctype, source_name)

    request = frappe.get_doc(
        {
            "doctype": "LT Customer Change Request",
            "source_doctype": source_doctype,
            "source_name": source_name,
            "request_type": request_type,
            "status": CHANGE_REQUEST_STATUS,
            "requester_user": identity["user"],
            "requester_contact": (identity["contacts"] or [""])[0],
            "customer": _source_customer(identity, source_doctype, source_name),
            "summary": _change_request_summary(request_type, payload_dict),
            "payload_json": json.dumps(payload_dict, sort_keys=True),
        }
    )
    # Permission bypass is guarded by resolve_customer_identity and _assert_source_access above.
    request.insert(ignore_permissions=True)
    return {
        "ok": True,
        "change_request": request.name,
        "status": request.status,
        "source_doctype": source_doctype,
        "source_name": source_name,
    }


@frappe.whitelist()
def set_customer_checklist_response(
    source_doctype: str | None = None,
    source_name: str | None = None,
    item_key: str | None = None,
    completed: bool | int | str = False,
) -> dict[str, Any]:
    source_doctype = _clean(source_doctype)
    source_name = _clean(source_name)
    item_key = _clean(item_key)
    identity = resolve_customer_identity()
    _assert_source_access(identity, source_doctype, source_name)
    if not item_key:
        frappe.throw(_("Please choose a checklist item."), frappe.ValidationError)

    existing = frappe.db.exists(
        "LT Customer Checklist Response",
        {
            "source_doctype": source_doctype,
            "source_name": source_name,
            "item_key": item_key,
            "user": identity["user"],
        },
    )
    doc = frappe.get_doc("LT Customer Checklist Response", existing) if existing else frappe.new_doc("LT Customer Checklist Response")
    doc.update(
        {
            "source_doctype": source_doctype,
            "source_name": source_name,
            "item_key": item_key,
            "completed": 1 if _as_bool(completed) else 0,
            "user": identity["user"],
            "customer": _source_customer(identity, source_doctype, source_name),
        }
    )
    doc.save(ignore_permissions=True)
    return {"ok": True, "response": doc.name, "item_key": item_key, "completed": bool(doc.completed)}


@frappe.whitelist()
def request_repeat_event(
    source_doctype: str | None = None,
    source_name: str | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    return submit_customer_change_request(
        source_doctype,
        source_name,
        "repeat_event",
        {"notes": _clean(notes), "intent": "Book a similar event"},
    )


@frappe.whitelist()
def register_customer_portal_file(
    source_doctype: str | None = None,
    source_name: str | None = None,
    file_name: str | None = None,
    purpose: str | None = None,
    label: str | None = None,
) -> dict[str, Any]:
    source_doctype = _clean(source_doctype)
    source_name = _clean(source_name)
    file_name = _clean(file_name)
    purpose = _clean(purpose) or "Reference"
    identity = resolve_customer_identity()
    _assert_source_access(identity, source_doctype, source_name)
    _assert_customer_uploaded_file_belongs_to_source(identity, source_doctype, source_name, file_name)

    doc = frappe.get_doc(
        {
            "doctype": "LT Customer Portal File",
            "source_doctype": source_doctype,
            "source_name": source_name,
            "file": file_name,
            "purpose": purpose,
            "label": _clean(label) or purpose,
            "customer": _source_customer(identity, source_doctype, source_name),
            "owner_user": identity["user"],
            "visible_to_customer": 1,
            "uploaded_by_customer": 1,
        }
    )
    # Permission bypass is guarded by source access and customer-owned File checks above.
    doc.insert(ignore_permissions=True)
    return {"ok": True, "portal_file": doc.name, "file": file_name, "purpose": purpose}


def _assert_customer_uploaded_file_belongs_to_source(
    identity: dict[str, Any],
    source_doctype: str,
    source_name: str,
    file_name: str,
) -> None:
    if not file_name:
        frappe.throw(_("Please attach a valid file before adding it to the portal."), frappe.ValidationError)

    file_row = frappe.db.get_value(
        "File",
        file_name,
        ["name", "owner", "attached_to_doctype", "attached_to_name"],
        as_dict=True,
    )
    if not file_row:
        frappe.throw(_("Please attach a valid file before adding it to the portal."), frappe.ValidationError)
    if file_row.get("owner") != identity["user"]:
        frappe.throw(_("That file was not uploaded by this customer account."), frappe.PermissionError)
    if file_row.get("attached_to_doctype") != source_doctype or file_row.get("attached_to_name") != source_name:
        frappe.throw(_("That file is not attached to the selected customer record."), frappe.PermissionError)


def _customers_for_contacts(contact_names: list[str]) -> list[str]:
    if not contact_names:
        return []
    links = frappe.get_all(
        "Dynamic Link",
        filters={"parenttype": "Contact", "parent": ["in", contact_names], "link_doctype": "Customer"},
        pluck="link_name",
    )
    return sorted({str(name) for name in links if name})


def _lead_names_for_contacts(contact_names: list[str]) -> list[str]:
    if not contact_names:
        return []
    links = frappe.get_all(
        "Dynamic Link",
        filters={"parenttype": "Contact", "parent": ["in", contact_names], "link_doctype": "Lead"},
        pluck="link_name",
    )
    return sorted({str(name) for name in links if name})


def _event_summaries(customers: list[str], lead_names: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if customers:
        fields = _safe_fields(
            "Sales Order",
            [
                "name",
                "customer",
                "transaction_date",
                "delivery_date",
                "status",
                "grand_total",
                "custom_lt_fulfillment_method",
                "custom_lt_delivery_zone",
                "custom_lt_requested_fulfillment_date",
                "custom_lt_requested_window_start",
                "custom_lt_requested_window_end",
                "custom_lt_fulfillment_status",
            ],
        )
        for row in frappe.get_all(
            "Sales Order",
            filters={"customer": ["in", customers]},
            fields=fields,
            order_by="modified desc",
            limit=20,
        ):
            rows.append(
                {
                    "source_doctype": "Sales Order",
                    "source_name": row.name,
                    "customer": row.get("customer"),
                    "title": f"Booking {row.name}",
                    "status_label": _friendly_order_status(row.get("status")),
                    "event_date": _first(row.get("custom_lt_requested_fulfillment_date"), row.get("delivery_date")),
                    "window": _time_window(row.get("custom_lt_requested_window_start"), row.get("custom_lt_requested_window_end")),
                    "fulfillment": _first(row.get("custom_lt_fulfillment_method"), row.get("custom_lt_fulfillment_status")),
                    "amount": row.get("grand_total"),
                }
            )
    if lead_names:
        fields = _safe_fields(
            "Lead",
            [
                "name",
                "lead_name",
                "status",
                "custom_pipeline_stage",
                "custom_event_date",
                "custom_event_time",
                "custom_event_end_time",
                "custom_event_location",
                "custom_guest_count",
            ],
        )
        for row in frappe.get_all("Lead", filters={"name": ["in", lead_names]}, fields=fields, order_by="modified desc"):
            rows.append(
                {
                    "source_doctype": "Lead",
                    "source_name": row.name,
                    "customer": "",
                    "title": row.get("lead_name") or f"Inquiry {row.name}",
                    "status_label": _friendly_pipeline_status(row.get("custom_pipeline_stage") or row.get("status")),
                    "event_date": row.get("custom_event_date"),
                    "window": _time_window(row.get("custom_event_time"), row.get("custom_event_end_time")),
                    "location": row.get("custom_event_location"),
                    "guest_count": row.get("custom_guest_count"),
                }
            )
    return rows


def _quote_summaries(customers: list[str], lead_names: list[str]) -> list[dict[str, Any]]:
    if not (customers or lead_names):
        return []
    meta = frappe.get_meta("Quotation")
    fields = _safe_fields(
        "Quotation",
        [
            "name",
            "quotation_to",
            "party_name",
            "transaction_date",
            "valid_till",
            "status",
            "grand_total",
            "rounded_total",
            "custom_lt_product_quote_status",
            "custom_event_date",
            "custom_event_location",
        ],
    )
    filters: list[list[Any]] = []
    if customers:
        filters.append(["party_name", "in", customers])
    if lead_names:
        filters.append(["party_name", "in", lead_names])
    rows: list[dict[str, Any]] = []
    for filter_row in filters:
        query_filters: dict[str, Any] | list[list[Any]] = [filter_row]
        if meta.has_field("custom_lt_product_quote_status"):
            query_filters = [filter_row, ["custom_lt_product_quote_status", "=", READY_QUOTE_STATUS]]
        for row in frappe.get_all("Quotation", filters=query_filters, fields=fields, order_by="modified desc", limit=20):
            rows.append(
                {
                    "source_doctype": "Quotation",
                    "source_name": row.name,
                    "customer": row.get("party_name") if row.get("party_name") in customers else "",
                    "title": f"Quote {row.name}",
                    "status_label": _friendly_quote_status(row.get("custom_lt_product_quote_status") or row.get("status")),
                    "event_date": row.get("custom_event_date"),
                    "location": row.get("custom_event_location"),
                    "amount": _first(row.get("rounded_total"), row.get("grand_total")),
                    "valid_till": row.get("valid_till"),
                }
            )
    return _dedupe_by_source(rows)


def _invoice_summaries(customers: list[str]) -> list[dict[str, Any]]:
    if not customers:
        return []
    fields = _safe_fields("Sales Invoice", ["name", "customer", "posting_date", "due_date", "status", "grand_total", "outstanding_amount"])
    rows = []
    for row in frappe.get_all("Sales Invoice", filters={"customer": ["in", customers]}, fields=fields, order_by="modified desc", limit=20):
        rows.append(
            {
                "source_doctype": "Sales Invoice",
                "source_name": row.name,
                "customer": row.get("customer"),
                "title": f"Invoice {row.name}",
                "status_label": _friendly_invoice_status(row.get("status"), row.get("outstanding_amount")),
                "amount": row.get("grand_total"),
                "outstanding_amount": row.get("outstanding_amount"),
                "due_date": row.get("due_date"),
                "posting_date": row.get("posting_date"),
            }
        )
    return rows


def _payment_summaries(customers: list[str], events: list[dict[str, Any]], invoices: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not customers:
        return []
    fields = _safe_fields("Payment Request", ["name", "party", "status", "grand_total", "reference_doctype", "reference_name"])
    rows = []
    for row in frappe.get_all(
        "Payment Request",
        filters={"party_type": "Customer", "party": ["in", customers]},
        fields=fields,
        order_by="modified desc",
        limit=20,
    ):
        rows.append(
            {
                "source_doctype": "Payment Request",
                "source_name": row.name,
                "customer": row.get("party"),
                "title": f"Payment link {row.name}",
                "status_label": _friendly_payment_status(row.get("status")),
                "amount": row.get("grand_total"),
                "reference_doctype": row.get("reference_doctype"),
                "reference_name": row.get("reference_name"),
            }
        )
    return rows


def _portal_file_summaries(customers: list[str], user: str) -> list[dict[str, Any]]:
    if not customers or not _doctype_exists("LT Customer Portal File"):
        return []
    fields = _safe_fields(
        "LT Customer Portal File",
        ["name", "customer", "source_doctype", "source_name", "file", "purpose", "label", "uploaded_by_customer"],
    )
    rows = []
    for row in frappe.get_all(
        "LT Customer Portal File",
        filters={"customer": ["in", customers], "visible_to_customer": 1},
        fields=fields,
        order_by="modified desc",
        limit=30,
    ):
        rows.append(
            {
                "source_doctype": row.get("source_doctype"),
                "source_name": row.get("source_name"),
                "customer": row.get("customer"),
                "title": row.get("label") or row.get("purpose") or "Customer file",
                "purpose": row.get("purpose"),
                "file": row.get("file"),
                "uploaded_by_customer": bool(row.get("uploaded_by_customer")),
            }
        )
    return rows


def _checklist_summary(customers: list[str], user: str, events: list[dict[str, Any]]) -> dict[str, Any]:
    source = events[0] if events else {}
    source_doctype = source.get("source_doctype") or ""
    source_name = source.get("source_name") or ""
    completed = _completed_checklist_items(user, source_doctype, source_name) if source_doctype and source_name else set()
    items = [
        {"key": "event_details", "label": "Review event details", "completed": "event_details" in completed},
        {"key": "venue_access", "label": "Confirm venue access, parking, or gate notes", "completed": "venue_access" in completed},
        {"key": "reference_files", "label": "Upload or confirm inspiration files", "completed": "reference_files" in completed},
        {"key": "billing_contact", "label": "Confirm billing contact if needed", "completed": "billing_contact" in completed},
    ]
    return {"source": source, "items": items}


def _completed_checklist_items(user: str, source_doctype: str, source_name: str) -> set[str]:
    if not _doctype_exists("LT Customer Checklist Response"):
        return set()
    return set(
        frappe.get_all(
            "LT Customer Checklist Response",
            filters={
                "user": user,
                "source_doctype": source_doctype,
                "source_name": source_name,
                "completed": 1,
            },
            pluck="item_key",
        )
    )


def _repeat_summary(events: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "eligible": bool(events),
        "source": events[0] if events else {},
        "message": "Ask us to rebuild something similar, then we will review details before quoting.",
    }


def _follow_up_summary(events: list[dict[str, Any]], invoices: list[dict[str, Any]], files: list[dict[str, Any]]) -> dict[str, Any]:
    items = []
    if invoices:
        items.append({"label": "Receipt and invoice history", "status_label": "Available"})
    if files:
        items.append({"label": "Customer-visible event files", "status_label": "Available"})
    if events:
        items.append({"label": "Review or rebook prompt", "status_label": "Ready when the event wraps"})
    return {"items": items, "review_link": "/contact?intent=review"}


def _organization_memberships(user: str, contact_names: list[str], customers: list[str]) -> list[dict[str, Any]]:
    if not _doctype_exists("LT Organization Portal Membership"):
        return []
    filters = {"enabled": 1, "user": user}
    fields = _safe_fields("LT Organization Portal Membership", ["name", "customer", "contact", "user", "organization_role", "enabled"])
    memberships = frappe.get_all("LT Organization Portal Membership", filters=filters, fields=fields, order_by="modified desc")
    allowed_customers = set(customers)
    return [
        {
            "membership": row.name,
            "customer": row.get("customer"),
            "contact": row.get("contact"),
            "organization_role": row.get("organization_role"),
            "enabled": bool(row.get("enabled")),
        }
        for row in memberships
        if row.get("customer") in allowed_customers
    ]


def _organization_people(customers: list[str]) -> list[dict[str, Any]]:
    if not customers:
        return []
    links = frappe.get_all(
        "Dynamic Link",
        filters={"parenttype": "Contact", "link_doctype": "Customer", "link_name": ["in", customers]},
        fields=["parent", "link_name"],
        limit=50,
    )
    contact_names = sorted({row.parent for row in links})
    people = []
    for contact in frappe.get_all("Contact", filters={"name": ["in", contact_names]}, fields=["name", "first_name", "last_name", "user"]):
        people.append(
            {
                "contact": contact.name,
                "name": " ".join(part for part in [contact.get("first_name"), contact.get("last_name")] if part) or contact.name,
                "user": contact.get("user"),
            }
        )
    return people


def _next_action(events: list[dict[str, Any]], quotes: list[dict[str, Any]], invoices: list[dict[str, Any]], payments: list[dict[str, Any]]) -> dict[str, str]:
    if quotes:
        return {"label": "Review your quote", "href": "/account/quotes", "tone": "attention"}
    unpaid = [row for row in invoices if row.get("outstanding_amount")]
    if unpaid or payments:
        return {"label": "Review billing", "href": "/account/billing", "tone": "attention"}
    if events:
        return {"label": "Check event details", "href": "/account/events", "tone": "calm"}
    return {"label": "Start a new request", "href": "/contact", "tone": "calm"}


def _assert_source_access(identity: dict[str, Any], source_doctype: str, source_name: str) -> None:
    if not source_doctype or not source_name:
        frappe.throw(_("Please choose the record this request belongs to."), frappe.ValidationError)
    if not frappe.db.exists(source_doctype, source_name):
        frappe.throw(_("We could not find that customer record."), frappe.PermissionError)
    if _source_customer(identity, source_doctype, source_name):
        return
    if source_doctype == "Lead" and source_name in _lead_names_for_contacts(identity["contacts"]):
        return
    frappe.throw(_("That record is not available in this customer account."), frappe.PermissionError)


def _source_customer(identity: dict[str, Any], source_doctype: str, source_name: str) -> str:
    customers = set(identity["customers"])
    if source_doctype in {"Sales Order", "Sales Invoice"}:
        customer = frappe.db.get_value(source_doctype, source_name, "customer")
        return str(customer) if customer in customers else ""
    if source_doctype == "Payment Request":
        party = frappe.db.get_value("Payment Request", source_name, "party")
        return str(party) if party in customers else ""
    if source_doctype == "Address":
        links = frappe.get_all(
            "Dynamic Link",
            filters={"parenttype": "Address", "parent": source_name, "link_doctype": "Customer", "link_name": ["in", list(customers)]},
            pluck="link_name",
        )
        return str(links[0]) if links else ""
    if source_doctype == "Quotation":
        party = frappe.db.get_value("Quotation", source_name, "party_name")
        return str(party) if party in customers else ""
    if source_doctype == "LT Customer Portal File":
        customer = frappe.db.get_value("LT Customer Portal File", source_name, "customer")
        return str(customer) if customer in customers else ""
    return ""


def _change_request_summary(request_type: str, payload: dict[str, Any]) -> str:
    clean_type = request_type.replace("_", " ").strip().title()
    detail = payload.get("reason") or payload.get("notes") or payload.get("intent") or ""
    return f"{clean_type}: {detail}"[:500] if detail else clean_type[:500]


def _safe_fields(doctype: str, fields: list[str]) -> list[str]:
    meta = frappe.get_meta(doctype)
    available = {"name", *(df.fieldname for df in meta.fields if df.fieldname)}
    return [field for field in fields if field in available]


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def _doctype_exists(doctype: str) -> bool:
    return bool(frappe.db.exists("DocType", doctype))


def _payload_dict(payload: str | dict[str, Any] | None) -> dict[str, Any]:
    if isinstance(payload, dict):
        return payload
    if isinstance(payload, str) and payload.strip():
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError:
            return {"message": payload.strip()}
        return parsed if isinstance(parsed, dict) else {"value": parsed}
    return {}


def _as_bool(value: bool | int | str) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _first(*values: Any) -> Any:
    return next((value for value in values if value not in (None, "")), "")


def _time_window(start: Any, end: Any) -> str:
    if start and end:
        return f"{start} - {end}"
    return str(start or end or "")


def _dedupe_by_source(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    deduped = []
    for row in rows:
        key = (row.get("source_doctype"), row.get("source_name"))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped


def _friendly_order_status(status: Any) -> str:
    mapping = {
        "Draft": "Being prepared",
        "To Deliver and Bill": "Confirmed, waiting on delivery and billing",
        "To Deliver": "Confirmed, waiting on delivery",
        "To Bill": "Delivered, waiting on billing",
        "Completed": "Completed",
        "Closed": "Closed",
    }
    return mapping.get(str(status or ""), str(status or "In review"))


def _friendly_quote_status(status: Any) -> str:
    if str(status or "") == READY_QUOTE_STATUS:
        return "Ready for your review"
    return "In review"


def _friendly_invoice_status(status: Any, outstanding_amount: Any) -> str:
    try:
        if float(outstanding_amount or 0) > 0:
            return "Payment may be needed"
    except (TypeError, ValueError):
        pass
    mapping = {"Paid": "Paid", "Overdue": "Overdue", "Unpaid": "Payment may be needed"}
    return mapping.get(str(status or ""), str(status or "Available"))


def _friendly_payment_status(status: Any) -> str:
    mapping = {"Paid": "Paid", "Initiated": "Payment link ready", "Requested": "Payment link ready"}
    return mapping.get(str(status or ""), str(status or "Payment link ready"))


def _friendly_pipeline_status(status: Any) -> str:
    mapping = {
        "New Inquiry": "Received",
        "Quote Sent/Awaiting Approval": "Quote in review",
        "Approved": "Approved",
        "In Production": "In production",
        "Event/Post Event": "Event/post-event",
        "Archive": "Wrapped up",
    }
    return mapping.get(str(status or ""), str(status or "Received"))
