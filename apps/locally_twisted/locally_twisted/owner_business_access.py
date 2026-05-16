"""Owner-safe business access DTOs for phone and assistant clients.

This module is the provider-neutral boundary. ChatGPT, future MCP adapters,
mobile pages, and other tools should consume these small DTOs instead of raw
ERPNext records.
"""
from __future__ import annotations

import re
from urllib.parse import quote

import frappe
from frappe import _
from frappe.utils import add_days, getdate, now_datetime, today

from locally_twisted.crm_pipeline import ARCHIVE_STAGE, PIPELINE_FIELD
from locally_twisted.stage_cascade import LEAD_TASK_FIELD


OWNER_ACCESS_ROLES = {"LT Owner Access", "System Manager"}
READ_SCOPES = {"lt.owner.read", "lt.contacts.read", "lt.leads.read", "lt.calendar.read"}
WRITE_SCOPES = {"lt.contact-log.write"}
ALLOWED_WRITE_DOCTYPES = {"Lead", "Contact", "Customer", "Sales Order"}
DEFAULT_LIMIT = 12


def has_owner_access(user: str | None = None) -> bool:
    """Return true for explicit owner/support users only."""
    user = user or frappe.session.user
    if not user or user == "Guest":
        return False
    roles = set(frappe.get_roles(user))
    return bool(OWNER_ACCESS_ROLES & roles)


def require_owner_access() -> None:
    if has_owner_access():
        return
    frappe.throw(
        _("This owner view is only available to Locally Twisted owner/support accounts."),
        frappe.PermissionError,
    )


def action_center_context(limit: int = DEFAULT_LIMIT) -> dict[str, object]:
    require_owner_access()
    urgent = urgent_contacts(limit=limit)
    bookings = upcoming_bookings(limit=6)
    return {
        "ok": True,
        "generated_at": now_datetime().isoformat(),
        "identity": {
            "user": frappe.session.user,
            "access": "owner",
            "read_scopes": sorted(READ_SCOPES),
            "write_scopes": sorted(WRITE_SCOPES),
        },
        "summary": today_summary(urgent=urgent, bookings=bookings),
        "urgent_contacts": urgent,
        "upcoming_bookings": bookings,
        "boundaries": {
            "provider_neutral": True,
            "raw_erpnext_records": False,
            "customer_send_allowed": False,
            "assistant_write_allowed": ["log_contact_attempt"],
            "human_tap_required_for_call_or_text": True,
        },
    }


def today_summary(
    urgent: list[dict[str, object]] | None = None,
    bookings: list[dict[str, object]] | None = None,
) -> dict[str, int]:
    require_owner_access()
    urgent = urgent if urgent is not None else urgent_contacts(limit=DEFAULT_LIMIT)
    bookings = bookings if bookings is not None else upcoming_bookings(limit=6)
    return {
        "urgent_contact_count": len(urgent),
        "new_inquiry_count": _count(
            "Lead",
            {
                PIPELINE_FIELD: "New Inquiry",
            },
        ),
        "upcoming_booking_count": len(bookings),
        "open_followup_count": _count(
            "Task",
            {
                "status": ["not in", ["Completed", "Cancelled"]],
            },
        ),
    }


def urgent_contacts(limit: int = DEFAULT_LIMIT) -> list[dict[str, object]]:
    require_owner_access()
    limit = _limit(limit)
    cards: list[dict[str, object]] = []
    cards.extend(_lead_cards(limit=limit))
    cards.extend(_task_lead_cards(limit=limit))
    cards = _dedupe_cards(cards)
    cards.sort(key=_card_sort_key)
    return cards[:limit]


def upcoming_bookings(limit: int = 6) -> list[dict[str, object]]:
    require_owner_access()
    limit = _limit(limit, maximum=20)
    if not frappe.has_permission("Sales Order", ptype="read"):
        return []
    fields = _existing_fields(
        "Sales Order",
        [
            "name",
            "customer",
            "customer_name",
            "delivery_date",
            "transaction_date",
            "status",
            "contact_person",
            "contact_mobile",
            "contact_phone",
        ],
    )
    rows = frappe.get_all(
        "Sales Order",
        filters={
            "docstatus": ["<", 2],
            "delivery_date": ["between", [today(), add_days(today(), 21)]],
        },
        fields=fields,
        order_by="delivery_date asc, modified desc",
        limit_page_length=limit,
    )
    return [_booking_card(row) for row in rows]


def search_contacts(query: str, limit: int = 8) -> dict[str, object]:
    require_owner_access()
    query = (query or "").strip()
    if len(query) < 2:
        return {"ok": True, "results": []}
    limit = _limit(limit, maximum=20)
    results: list[dict[str, object]] = []
    results.extend(_search_leads(query, limit))
    results.extend(_search_contacts(query, limit))
    return {"ok": True, "results": _dedupe_cards(results)[:limit]}


def log_contact_attempt(
    source_doctype: str,
    source_name: str,
    channel: str,
    note: str | None = None,
) -> dict[str, object]:
    """Record a human contact attempt. This is the only initial write DTO."""
    require_owner_access()
    source_doctype = (source_doctype or "").strip()
    source_name = (source_name or "").strip()
    channel = (channel or "").strip().lower()
    if source_doctype not in ALLOWED_WRITE_DOCTYPES:
        frappe.throw(_("This record type is not available for owner contact logging."), frappe.PermissionError)
    if channel not in {"call", "text", "email", "other"}:
        frappe.throw(_("Choose call, text, email, or other for the contact log."), frappe.ValidationError)
    if not frappe.db.exists(source_doctype, source_name):
        frappe.throw(_("That business record was not found."), frappe.DoesNotExistError)
    if not frappe.has_permission(source_doctype, ptype="read"):
        frappe.throw(_("This account cannot read that business record."), frappe.PermissionError)

    safe_note = (note or "").strip()
    content = f"Owner contact attempt: {channel}"
    if safe_note:
        content = f"{content}\n\n{safe_note[:500]}"
    comment = frappe.get_doc(
        {
            "doctype": "Comment",
            "comment_type": "Comment",
            "reference_doctype": source_doctype,
            "reference_name": source_name,
            "content": content,
        }
    )
    comment.insert(ignore_permissions=True)
    frappe.db.commit()
    return {
        "ok": True,
        "comment": comment.name,
        "source_doctype": source_doctype,
        "source_name": source_name,
        "channel": channel,
    }


def _lead_cards(limit: int) -> list[dict[str, object]]:
    if not frappe.has_permission("Lead", ptype="read"):
        return []
    fields = _existing_fields(
        "Lead",
        [
            "name",
            "lead_name",
            "first_name",
            "last_name",
            "company_name",
            "email_id",
            "phone",
            "mobile_no",
            "status",
            PIPELINE_FIELD,
            "custom_event_date",
            "custom_event_time",
            "custom_event_location",
            "custom_preferred_contact_method",
            "custom_occasion_type",
            "modified",
            "creation",
        ],
    )
    rows = frappe.get_all(
        "Lead",
        filters={PIPELINE_FIELD: ["!=", ARCHIVE_STAGE]},
        fields=fields,
        order_by=f"{PIPELINE_FIELD} asc, custom_event_date asc, modified desc",
        limit_page_length=max(limit * 2, 12),
    )
    return [_lead_card(row, reason=_lead_reason(row)) for row in rows if _phone_for(row)]


def _task_lead_cards(limit: int) -> list[dict[str, object]]:
    if not frappe.has_permission("Task", ptype="read") or not frappe.has_permission("Lead", ptype="read"):
        return []
    if not frappe.get_meta("Task").has_field(LEAD_TASK_FIELD):
        return []
    rows = frappe.get_all(
        "Task",
        filters={
            "status": ["not in", ["Completed", "Cancelled"]],
            LEAD_TASK_FIELD: ["is", "set"],
        },
        fields=["name", "subject", "priority", "exp_end_date", LEAD_TASK_FIELD],
        order_by="priority desc, exp_end_date asc, modified desc",
        limit_page_length=max(limit * 2, 12),
    )
    cards = []
    for task in rows:
        lead_name = task.get(LEAD_TASK_FIELD)
        if not lead_name or not frappe.db.exists("Lead", lead_name):
            continue
        lead = frappe.db.get_value(
            "Lead",
            lead_name,
            _existing_fields(
                "Lead",
                [
                    "name",
                    "lead_name",
                    "first_name",
                    "last_name",
                    "company_name",
                    "email_id",
                    "phone",
                    "mobile_no",
                    "status",
                    PIPELINE_FIELD,
                    "custom_event_date",
                    "custom_event_time",
                    "custom_event_location",
                    "custom_preferred_contact_method",
                    "custom_occasion_type",
                    "modified",
                    "creation",
                ],
            ),
            as_dict=True,
        )
        if lead and _phone_for(lead):
            cards.append(_lead_card(lead, reason=task.get("subject") or "Follow up"))
    return cards


def _lead_card(row, *, reason: str) -> dict[str, object]:
    phone = _phone_for(row)
    name = _person_name(row)
    event_date = row.get("custom_event_date")
    location = row.get("custom_event_location") or ""
    stage = row.get(PIPELINE_FIELD) or row.get("status") or ""
    draft = _message_draft(name=name, date=event_date, location=location)
    return {
        "id": f"Lead:{row.get('name')}",
        "source_doctype": "Lead",
        "source_name": row.get("name"),
        "type": "lead",
        "title": name,
        "subtitle": row.get("custom_occasion_type") or row.get("company_name") or "Inquiry",
        "reason": reason,
        "stage": stage,
        "when": _date_text(event_date, row.get("custom_event_time")),
        "location": location,
        "preferred_contact_method": row.get("custom_preferred_contact_method") or "",
        "email": row.get("email_id") or "",
        **_phone_actions(phone, draft),
        "message_draft": draft,
        "record_url": _desk_url("Lead", row.get("name")),
    }


def _booking_card(row) -> dict[str, object]:
    customer = row.get("customer")
    contact = _contact_for_customer(customer) if customer else {}
    phone = row.get("contact_mobile") or row.get("contact_phone") or _phone_for(contact)
    title = row.get("customer_name") or customer or row.get("name")
    draft = _message_draft(name=title, date=row.get("delivery_date"), location="")
    return {
        "id": f"Sales Order:{row.get('name')}",
        "source_doctype": "Sales Order",
        "source_name": row.get("name"),
        "type": "booking",
        "title": title,
        "subtitle": "Upcoming booking",
        "reason": "Confirm upcoming booking",
        "stage": row.get("status") or "",
        "when": _date_text(row.get("delivery_date"), None),
        "location": "",
        "preferred_contact_method": "",
        "email": contact.get("email_id") or "",
        **_phone_actions(phone, draft),
        "message_draft": draft,
        "record_url": _desk_url("Sales Order", row.get("name")),
    }


def _search_leads(query: str, limit: int) -> list[dict[str, object]]:
    fields = _existing_fields(
        "Lead",
        ["name", "lead_name", "first_name", "last_name", "company_name", "email_id", "phone", "mobile_no", PIPELINE_FIELD],
    )
    filters = [
        ["Lead", "lead_name", "like", f"%{query}%"],
    ]
    rows = frappe.get_all("Lead", filters=filters, fields=fields, limit_page_length=limit)
    return [_lead_card(row, reason="Contact lookup") for row in rows if _phone_for(row)]


def _search_contacts(query: str, limit: int) -> list[dict[str, object]]:
    if not frappe.has_permission("Contact", ptype="read"):
        return []
    fields = _existing_fields("Contact", ["name", "first_name", "last_name", "email_id", "phone", "mobile_no"])
    rows = frappe.get_all(
        "Contact",
        filters={"first_name": ["like", f"%{query}%"]},
        fields=fields,
        limit_page_length=limit,
    )
    cards = []
    for row in rows:
        _hydrate_contact_points(row)
        phone = _phone_for(row)
        if not phone:
            continue
        name = _person_name(row)
        draft = _message_draft(name=name, date=None, location="")
        cards.append(
            {
                "id": f"Contact:{row.get('name')}",
                "source_doctype": "Contact",
                "source_name": row.get("name"),
                "type": "contact",
                "title": name,
                "subtitle": "Contact",
                "reason": "Contact lookup",
                "stage": "",
                "when": "",
                "location": "",
                "preferred_contact_method": "",
                "email": row.get("email_id") or "",
                **_phone_actions(phone, draft),
                "message_draft": draft,
                "record_url": _desk_url("Contact", row.get("name")),
            }
        )
    return cards


def _contact_for_customer(customer: str | None) -> dict:
    if not customer:
        return {}
    links = frappe.get_all(
        "Dynamic Link",
        filters={"parenttype": "Contact", "link_doctype": "Customer", "link_name": customer},
        fields=["parent"],
        limit_page_length=1,
    )
    if not links:
        return {}
    contact = frappe.db.get_value(
        "Contact",
        links[0].parent,
        _existing_fields("Contact", ["name", "first_name", "last_name", "email_id", "phone", "mobile_no"]),
        as_dict=True,
    ) or {}
    _hydrate_contact_points(contact)
    return contact


def _phone_actions(phone: str | None, message: str) -> dict[str, str | None]:
    phone_display = _phone_display(phone)
    phone_href = _phone_href(phone)
    sms_href = f"sms:{phone_href[4:]}?&body={quote(message)}" if phone_href else None
    return {
        "phone": phone_display,
        "phone_href": phone_href,
        "sms_href": sms_href,
    }


def _hydrate_contact_points(row) -> None:
    contact_name = row.get("name")
    if not contact_name:
        return
    if not _phone_for(row):
        row["mobile_no"] = _contact_phone(contact_name)
    if not row.get("email_id"):
        row["email_id"] = _contact_email(contact_name)


def _contact_phone(contact_name: str) -> str | None:
    row = frappe.get_all(
        "Contact Phone",
        filters={"parent": contact_name},
        fields=["phone", "is_primary_mobile_no", "is_primary_phone"],
        order_by="is_primary_mobile_no desc, is_primary_phone desc, idx asc",
        limit_page_length=1,
    )
    return row[0].get("phone") if row else None


def _contact_email(contact_name: str) -> str | None:
    row = frappe.get_all(
        "Contact Email",
        filters={"parent": contact_name},
        fields=["email_id", "is_primary"],
        order_by="is_primary desc, idx asc",
        limit_page_length=1,
    )
    return row[0].get("email_id") if row else None


def _message_draft(name: str, date, location: str) -> str:
    first = (name or "there").split()[0]
    pieces = [f"Hi {first}, this is Jeff with Locally Twisted."]
    if date:
        pieces.append(f"I am following up about your event on {_date_text(date, None)}.")
    elif location:
        pieces.append(f"I am following up about your event in {location}.")
    else:
        pieces.append("I am following up about your Locally Twisted request.")
    pieces.append("Is now a good time?")
    return " ".join(pieces)


def _phone_for(row) -> str | None:
    return row.get("mobile_no") or row.get("phone")


def _phone_display(phone: str | None) -> str | None:
    if not phone:
        return None
    digits = re.sub(r"\D", "", str(phone))
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) == 10:
        return f"({digits[0:3]}) {digits[3:6]}-{digits[6:10]}"
    return str(phone).strip()


def _phone_href(phone: str | None) -> str | None:
    if not phone:
        return None
    phone_text = str(phone).strip()
    digits = re.sub(r"\D", "", phone_text)
    if not digits:
        return None
    if phone_text.startswith("+"):
        return f"tel:+{digits}"
    if len(digits) == 10:
        return f"tel:+1{digits}"
    return f"tel:+{digits}" if len(digits) == 11 and digits.startswith("1") else f"tel:{digits}"


def _person_name(row) -> str:
    lead_name = (row.get("lead_name") or "").strip()
    if lead_name:
        return lead_name.split(" - ")[0]
    first = (row.get("first_name") or "").strip()
    last = (row.get("last_name") or "").strip()
    full = " ".join(part for part in [first, last] if part).strip()
    return full or row.get("company_name") or row.get("customer_name") or row.get("name") or "Customer"


def _lead_reason(row) -> str:
    stage = row.get(PIPELINE_FIELD)
    if stage == "New Inquiry":
        return "New inquiry needs a reply"
    if stage == "Quote Sent/Awaiting Approval":
        return "Quote follow-up"
    if stage == "Approved":
        return "Confirm booking details"
    return "Follow up"


def _date_text(date_value, time_value) -> str:
    if not date_value:
        return ""
    try:
        text = getdate(date_value).strftime("%b %-d, %Y")
    except ValueError:
        text = getdate(date_value).strftime("%b %#d, %Y")
    if time_value:
        return f"{text} at {time_value}"
    return text


def _desk_url(doctype: str, name: str | None) -> str:
    if not name:
        return "/app/Workspaces"
    return f"/app/{frappe.scrub(doctype).replace('_', '-')}/{quote(str(name))}"


def _existing_fields(doctype: str, fields: list[str]) -> list[str]:
    meta = frappe.get_meta(doctype)
    return [field for field in fields if field == "name" or meta.has_field(field)]


def _count(doctype: str, filters: dict) -> int:
    if not frappe.db.exists("DocType", doctype) or not frappe.has_permission(doctype, ptype="read"):
        return 0
    return int(frappe.db.count(doctype, filters))


def _limit(value, *, maximum: int = 50) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = DEFAULT_LIMIT
    return max(1, min(parsed, maximum))


def _dedupe_cards(cards: list[dict[str, object]]) -> list[dict[str, object]]:
    seen = set()
    deduped = []
    for card in cards:
        card_id = card.get("id")
        if card_id in seen:
            continue
        seen.add(card_id)
        deduped.append(card)
    return deduped


def _card_sort_key(card: dict[str, object]) -> tuple[int, str, str]:
    stage_weight = {
        "New Inquiry": 0,
        "Quote Sent/Awaiting Approval": 1,
        "Approved": 2,
        "In Production": 3,
        "Event/Post Event": 4,
    }.get(str(card.get("stage") or ""), 5)
    return (stage_weight, str(card.get("when") or "zzzz"), str(card.get("title") or ""))
