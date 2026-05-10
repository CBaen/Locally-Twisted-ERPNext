"""Create synthetic clients/events/meetings and verify LT automation behavior."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta
import time
from typing import Any

import frappe

from locally_twisted.customer_email_theme import AUTO_ACK_SUBJECT
from locally_twisted.crm_pipeline import ARCHIVE_STAGE, PIPELINE_FIELD


CLIENT_SCENARIOS = [
    {
        "id": "private_birthday_household",
        "client_type": "Individual household",
        "first_name": "QA Parent Riley",
        "company_name": "",
        "email_prefix": "qa-private-birthday",
        "phone": "801-555-0101",
        "occasion": "Birthday Party",
        "event_location": "Backyard, West Jordan UT",
        "guest_count": 28,
        "services": ["Balloon Decor", "Delivery"],
        "source_channel": "Website Form",
        "event_category": "Event",
        "meeting_category": "Meeting",
        "pipeline_path": ["Quote Sent/Awaiting Approval", "Approved", "In Production", "Event/Post Event", "Archive"],
        "notes": "Backyard birthday with delivery, colors, shade, and event logistics.",
    },
    {
        "id": "corporate_grand_opening",
        "client_type": "Corporate company",
        "first_name": "QA Corporate Buyer",
        "company_name": "BBC QA Corporate Events Team",
        "email_prefix": "qa-corporate-opening",
        "phone": "801-555-0102",
        "occasion": "Grand Opening",
        "event_location": "Showroom lobby, Salt Lake City UT",
        "guest_count": 175,
        "services": ["Balloon Decor", "Events Inquiry"],
        "source_channel": "Email",
        "event_category": "Event",
        "meeting_category": "Call",
        "pipeline_path": ["Quote Sent/Awaiting Approval", "Approved"],
        "notes": "Corporate procurement-style buyer with company, install location, and decision follow-up.",
    },
    {
        "id": "school_artist_service",
        "client_type": "School campus",
        "first_name": "QA School Coordinator",
        "company_name": "BBC QA Elementary School",
        "email_prefix": "qa-school-campus",
        "phone": "801-555-0103",
        "occasion": "School Event",
        "event_location": "School gym, Sandy UT",
        "guest_count": 420,
        "services": ["Balloon Twisting", "Face Painting"],
        "source_channel": "Phone Call",
        "event_category": "Event",
        "meeting_category": "Meeting",
        "pipeline_path": ["Approved", "In Production", "Event/Post Event"],
        "num_twisters": 2,
        "num_painters": 2,
        "notes": "School event with artist staffing, timing, and post-event follow-up.",
    },
    {
        "id": "nonprofit_community_festival",
        "client_type": "Nonprofit or civic event",
        "first_name": "QA Community Organizer",
        "company_name": "BBC QA Community Foundation",
        "email_prefix": "qa-community-festival",
        "phone": "801-555-0104",
        "occasion": "Festival / Fair",
        "event_location": "City park pavilion, Provo UT",
        "guest_count": 900,
        "services": ["Balloon Decor", "Balloon Twisting", "Events Inquiry"],
        "source_channel": "In Person",
        "event_category": "Event",
        "meeting_category": "Meeting",
        "pipeline_path": ["Quote Sent/Awaiting Approval", "Archive"],
        "notes": "Community festival lead with mixed service request and archive path.",
    },
]


class Matrix:
    def __init__(self, marker: str):
        self.marker = marker
        self.failures: list[str] = []
        self.warnings: list[str] = []
        self.scenarios: list[dict[str, Any]] = []
        self.created: dict[str, set[str]] = {}
        self.created_order: list[tuple[str, str]] = []

    def remember(self, doc) -> None:
        self.created.setdefault(doc.doctype, set()).add(doc.name)
        self.created_order.append((doc.doctype, doc.name))

    def add_failure(self, scenario_id: str, message: str) -> None:
        self.failures.append(f"{scenario_id}: {message}")

    def add_warning(self, scenario_id: str, message: str) -> None:
        self.warnings.append(f"{scenario_id}: {message}")


def run() -> dict[str, Any]:
    marker = f"CLIENT-MATRIX-{time.time_ns()}"
    matrix = Matrix(marker)
    started_at = datetime.utcnow().isoformat()

    try:
        for index, spec in enumerate(CLIENT_SCENARIOS, start=1):
            _run_client_scenario(matrix, spec, index)
        _check_no_open_record_failures(matrix)
    finally:
        cleanup = _cleanup(matrix)

    return {
        "ok": not matrix.failures,
        "generated_at": started_at,
        "marker": marker,
        "scenario_count": len(CLIENT_SCENARIOS),
        "scenarios": matrix.scenarios,
        "failures": matrix.failures,
        "warnings": matrix.warnings,
        "created_counts": {doctype: len(names) for doctype, names in sorted(matrix.created.items())},
        "cleanup": cleanup,
    }


def _run_client_scenario(matrix: Matrix, spec: dict[str, Any], index: int) -> None:
    scenario_id = spec["id"]
    event_date = (datetime.utcnow() + timedelta(days=14 + index)).date().isoformat()
    email = f"{spec['email_prefix']}-{matrix.marker.lower()}@bbc-test.invalid"
    lead = _create_lead(matrix, spec, event_date, email)
    contact_name = _linked_contact_for_lead(lead.name)
    customer = _create_customer(matrix, spec, index)
    contact = _create_customer_contact(matrix, customer.name, spec, email)
    address = _create_customer_address(matrix, customer.name, spec, index)
    event = _create_event(matrix, spec, lead.name, contact_name or contact.name, event_date, category=spec["event_category"])
    meeting = _create_event(matrix, spec, lead.name, contact_name or contact.name, event_date, category=spec["meeting_category"])
    todo = _create_todo(matrix, lead.name, spec)

    checks: dict[str, Any] = {
        "id": scenario_id,
        "lead": lead.name,
        "customer": customer.name,
        "customer_contact": contact.name,
        "customer_address": address.name,
        "event": event.name,
        "meeting": meeting.name,
        "todo": todo.name,
        "client_type": spec["client_type"],
        "services": spec["services"],
        "pipeline_path": spec["pipeline_path"],
    }

    _check_lead_cascade(matrix, scenario_id, lead, spec)
    _check_customer_links(matrix, scenario_id, customer.name, contact.name, address.name)
    _check_event_links(matrix, scenario_id, event.name, lead.name, contact_name or contact.name)
    _check_event_links(matrix, scenario_id, meeting.name, lead.name, contact_name or contact.name)
    _check_todo_link(matrix, scenario_id, todo.name, lead.name)
    _walk_pipeline(matrix, scenario_id, lead.name, spec["pipeline_path"])
    _check_no_finance_from_crm_stage(matrix, scenario_id, lead.name)

    event_task_count = _count_event_generated_tasks(event.name) + _count_event_generated_tasks(meeting.name)
    if event_task_count == 0:
        matrix.add_warning(
            scenario_id,
            "Event/meeting records save and link, but no event-created follow-up Task automation exists today.",
        )

    checks["final_open_tasks"] = _open_tasks_for_lead(lead.name)
    checks["contact_linked_to_lead"] = bool(contact_name)
    checks["event_generated_tasks"] = event_task_count
    matrix.scenarios.append(checks)


def _create_lead(matrix: Matrix, spec: dict[str, Any], event_date: str, email: str):
    lead_doc = {
        "doctype": "Lead",
        "first_name": f"{spec['first_name']} {matrix.marker}",
        "lead_name": "Booking Request",
        "email_id": email,
        "mobile_no": spec["phone"],
        "company_name": spec["company_name"] or None,
        "source": "Website",
        "status": "Open",
        PIPELINE_FIELD: "New Inquiry",
        "custom_occasion_type": spec["occasion"],
        "custom_event_date": event_date,
        "custom_event_time": "10:00:00",
        "custom_event_end_time": "12:00:00",
        "custom_event_location": spec["event_location"],
        "custom_guest_count": spec["guest_count"],
        "custom_event_type": [{"service_type": service} for service in spec["services"]],
        "custom_indoor_outdoor": "Both",
        "custom_shade_required": 1,
        "custom_colors": "navy, brass, white",
        "custom_anything_else": f"{matrix.marker}: {spec['notes']}",
        "custom_source_channel": spec["source_channel"],
    }
    for optional_field, value in {
        "custom_num_twisters": spec.get("num_twisters"),
        "custom_num_painters": spec.get("num_painters"),
        "custom_twisting_notes": "Two-hour artist block; line management needed." if spec.get("num_twisters") else None,
        "custom_painting_notes": "Use school-safe designs and short queue options." if spec.get("num_painters") else None,
    }.items():
        if value is not None:
            lead_doc[optional_field] = value

    lead = frappe.get_doc(lead_doc)
    lead.insert(ignore_permissions=True)
    matrix.remember(lead)
    return lead


def _create_customer(matrix: Matrix, spec: dict[str, Any], index: int):
    customer_type = "Individual" if not spec["company_name"] else "Company"
    customer = frappe.get_doc(
        {
            "doctype": "Customer",
            "customer_name": f"{spec['client_type']} {matrix.marker}",
            "customer_type": customer_type,
            "customer_group": _first_leaf("Customer Group", ["Commercial", "Individual"]),
            "territory": _first_leaf("Territory", ["Utah", "United States"]),
        }
    )
    customer.insert(ignore_permissions=True)
    matrix.remember(customer)
    return customer


def _create_customer_contact(matrix: Matrix, customer_name: str, spec: dict[str, Any], email: str):
    contact = frappe.get_doc(
        {
            "doctype": "Contact",
            "first_name": spec["first_name"],
            "last_name": matrix.marker,
            "company_name": spec["company_name"] or customer_name,
            "email_ids": [{"email_id": email.replace("@", "+customer@"), "is_primary": 1}],
            "phone_nos": [{"phone": spec["phone"], "is_primary_mobile_no": 1}],
            "links": [{"link_doctype": "Customer", "link_name": customer_name}],
        }
    )
    contact.insert(ignore_permissions=True)
    matrix.remember(contact)
    return contact


def _create_customer_address(matrix: Matrix, customer_name: str, spec: dict[str, Any], index: int):
    address = frappe.get_doc(
        {
            "doctype": "Address",
            "address_title": f"{spec['client_type']} {matrix.marker}",
            "address_type": "Shipping",
            "address_line1": f"{100 + index} QA Automation Lane",
            "city": "West Jordan",
            "state": "UT",
            "pincode": "84088",
            "country": "United States",
            "links": [{"link_doctype": "Customer", "link_name": customer_name}],
        }
    )
    address.insert(ignore_permissions=True)
    matrix.remember(address)
    return address


def _create_event(matrix: Matrix, spec: dict[str, Any], lead_name: str, contact_name: str, event_date: str, *, category: str):
    subject = f"{matrix.marker} {spec['client_type']} {category}"
    event_doc = {
        "doctype": "Event",
        "subject": subject,
        "event_category": category,
        "event_type": "Private",
        "starts_on": f"{event_date} 10:00:00",
        "ends_on": f"{event_date} 12:00:00",
        "status": "Open",
        "location": spec["event_location"],
        "description": f"{matrix.marker}: {spec['notes']}",
        "reference_doctype": "Lead",
        "reference_docname": lead_name,
    }
    if frappe.get_meta("Event").has_field("links"):
        event_doc["links"] = [{"link_doctype": "Lead", "link_name": lead_name}]
    if frappe.get_meta("Event").has_field("event_participants") and contact_name:
        event_doc["event_participants"] = _event_participant_rows(contact_name)

    event = frappe.get_doc(event_doc)
    event.insert(ignore_permissions=True)
    matrix.remember(event)
    return event


def _event_participant_rows(contact_name: str) -> list[dict[str, Any]]:
    fields = {df.fieldname for df in frappe.get_meta("Event Participants").fields}
    row: dict[str, Any] = {}
    if "reference_doctype" in fields:
        row["reference_doctype"] = "Contact"
    if "reference_docname" in fields:
        row["reference_docname"] = contact_name
    if "email" in fields:
        row["email"] = frappe.db.get_value("Contact Email", {"parent": contact_name, "is_primary": 1}, "email_id")
    return [row] if row else []


def _create_todo(matrix: Matrix, lead_name: str, spec: dict[str, Any]):
    todo = frappe.get_doc(
        {
            "doctype": "ToDo",
            "description": f"{matrix.marker}: Review synthetic {spec['client_type']} client",
            "reference_type": "Lead",
            "reference_name": lead_name,
            "status": "Open",
            "priority": "Medium",
            "date": (datetime.utcnow() + timedelta(days=1)).date().isoformat(),
        }
    )
    todo.insert(ignore_permissions=True)
    matrix.remember(todo)
    return todo


def _check_lead_cascade(matrix: Matrix, scenario_id: str, lead, spec: dict[str, Any]) -> None:
    lead.reload()
    if spec["first_name"] not in (lead.lead_name or ""):
        matrix.add_failure(scenario_id, f"Lead title did not include customer name: {lead.lead_name!r}")
    expected_service_label = _expected_service_title_fragment(spec["services"])
    if expected_service_label and expected_service_label not in (lead.lead_name or ""):
        matrix.add_failure(
            scenario_id,
            f"Lead title did not include service summary {expected_service_label!r}: {lead.lead_name!r}",
        )

    if not _linked_contact_for_lead(lead.name):
        matrix.add_failure(scenario_id, "Lead insert did not create/link a Contact")

    if not _email_queue_for("Lead", lead.name, AUTO_ACK_SUBJECT):
        matrix.add_failure(scenario_id, "Website Lead did not queue the customer acknowledgment email")

    if not _stage_task(lead.name, "New Inquiry"):
        matrix.add_failure(scenario_id, "Lead insert did not create the New Inquiry follow-up Task")


def _expected_service_title_fragment(services: list[str]) -> str:
    labels = [{"Events Inquiry": "Event Inquiry"}.get(service, service) for service in services]
    if not labels:
        return ""
    if len(labels) == 1:
        return labels[0]
    if len(labels) == 2:
        return f"{labels[0]} + {labels[1]}"
    return f"{labels[0]} + {len(labels) - 1} more"


def _check_customer_links(matrix: Matrix, scenario_id: str, customer_name: str, contact_name: str, address_name: str) -> None:
    if not frappe.db.exists("Contact", contact_name):
        matrix.add_failure(scenario_id, "Customer Contact was not created")
    if not frappe.db.exists("Address", address_name):
        matrix.add_failure(scenario_id, "Customer Address was not created")
    if not frappe.db.exists("Dynamic Link", {"parenttype": "Contact", "parent": contact_name, "link_doctype": "Customer", "link_name": customer_name}):
        matrix.add_failure(scenario_id, "Contact is not linked to Customer")
    if not frappe.db.exists("Dynamic Link", {"parenttype": "Address", "parent": address_name, "link_doctype": "Customer", "link_name": customer_name}):
        matrix.add_failure(scenario_id, "Address is not linked to Customer")


def _check_event_links(matrix: Matrix, scenario_id: str, event_name: str, lead_name: str, contact_name: str) -> None:
    event = frappe.get_doc("Event", event_name)
    if event.reference_doctype != "Lead" or event.reference_docname != lead_name:
        matrix.add_failure(scenario_id, f"Event {event_name} did not preserve Lead reference")
    if frappe.get_meta("Event").has_field("event_participants") and contact_name:
        if not event.get("event_participants"):
            matrix.add_failure(scenario_id, f"Event {event_name} did not retain Contact participant")


def _check_todo_link(matrix: Matrix, scenario_id: str, todo_name: str, lead_name: str) -> None:
    todo = frappe.get_doc("ToDo", todo_name)
    if todo.reference_type != "Lead" or todo.reference_name != lead_name:
        matrix.add_failure(scenario_id, "ToDo did not preserve Lead reference")


def _walk_pipeline(matrix: Matrix, scenario_id: str, lead_name: str, path: list[str]) -> None:
    for stage in path:
        frappe.db.set_value("Lead", lead_name, PIPELINE_FIELD, stage, update_modified=True)
        lead = frappe.get_doc("Lead", lead_name)
        lead.run_method("on_update")

        if stage == ARCHIVE_STAGE:
            open_tasks = _open_tasks_for_lead(lead_name)
            if open_tasks:
                matrix.add_failure(scenario_id, f"Archive stage left open cascade Tasks: {open_tasks!r}")
            continue

        task = _stage_task(lead_name, stage)
        if not task:
            matrix.add_failure(scenario_id, f"Stage {stage!r} did not create/open its follow-up Task")


def _check_no_finance_from_crm_stage(matrix: Matrix, scenario_id: str, lead_name: str) -> None:
    # Current LT CRM stage automation is intentionally Task-only. There is no
    # direct Lead foreign key on the finance doctypes, so this is a marker-based
    # smoke check rather than a full accounting audit.
    for doctype in ("Sales Order", "Sales Invoice", "Payment Request", "Payment Entry"):
        meta = frappe.get_meta(doctype)
        marker_fields = [field for field in ("remarks", "title") if meta.has_field(field)]
        for fieldname in marker_fields:
            if frappe.db.exists(doctype, {fieldname: ["like", f"%{lead_name}%"]}):
                matrix.add_failure(scenario_id, f"CRM/event automation unexpectedly created {doctype}")


def _check_no_open_record_failures(matrix: Matrix) -> None:
    from locally_twisted.failure_recorder import record_health_failures

    open_failures = record_health_failures(limit=20)
    related = [
        row for row in open_failures
        if str(row.get("primary_name") or "") in {name for names in matrix.created.values() for name in names}
    ]
    if related:
        matrix.failures.append(f"record health blockers appeared for synthetic records: {related!r}")


def _stage_task(lead_name: str, stage: str) -> dict[str, Any] | None:
    rows = frappe.get_all(
        "Task",
        filters={"custom_lt_lead": lead_name, "custom_pipeline_stage": stage},
        fields=["name", "subject", "status", "custom_pipeline_stage"],
        order_by="creation desc",
        limit_page_length=1,
    )
    if not rows:
        return None
    row = rows[0]
    if row.get("status") in {"Completed", "Cancelled"}:
        return None
    return row


def _open_tasks_for_lead(lead_name: str) -> list[dict[str, Any]]:
    return frappe.get_all(
        "Task",
        filters={"custom_lt_lead": lead_name, "status": ["not in", ["Completed", "Cancelled"]]},
        fields=["name", "subject", "status", "custom_pipeline_stage"],
        order_by="creation asc",
        limit_page_length=20,
    )


def _count_event_generated_tasks(event_name: str) -> int:
    meta = frappe.get_meta("Task")
    if not (meta.has_field("reference_type") and meta.has_field("reference_name")):
        return 0
    return frappe.db.count("Task", {"reference_type": "Event", "reference_name": event_name})


def _linked_contact_for_lead(lead_name: str) -> str | None:
    return frappe.db.get_value(
        "Dynamic Link",
        {"parenttype": "Contact", "link_doctype": "Lead", "link_name": lead_name},
        "parent",
    )


def _email_queue_for(reference_doctype: str, reference_name: str, subject_fragment: str) -> str | None:
    communication_name = frappe.db.get_value(
        "Communication",
        {
            "reference_doctype": reference_doctype,
            "reference_name": reference_name,
            "subject": ["like", f"%{subject_fragment}%"],
        },
        "name",
    )
    if communication_name:
        return communication_name

    email_queue_meta = frappe.get_meta("Email Queue")
    filters: dict[str, Any] = {}
    if email_queue_meta.has_field("reference_doctype") and email_queue_meta.has_field("reference_name"):
        filters = {"reference_doctype": reference_doctype, "reference_name": reference_name}
    if filters and email_queue_meta.has_field("subject"):
        filters["subject"] = ["like", f"%{subject_fragment}%"]
    if filters:
        return frappe.db.get_value("Email Queue", filters, "name")
    return None


def _first_leaf(doctype: str, preferred_names: list[str]) -> str:
    for name in preferred_names:
        if frappe.db.exists(doctype, {"name": name, "is_group": 0}):
            return name
    row = frappe.get_all(doctype, filters={"is_group": 0}, fields=["name"], limit_page_length=1)
    if row:
        return row[0].name
    return _first_existing(doctype, preferred_names)


def _first_existing(doctype: str, names: list[str]) -> str:
    for name in names:
        if frappe.db.exists(doctype, name):
            return name
    row = frappe.get_all(doctype, fields=["name"], limit_page_length=1)
    if not row:
        raise RuntimeError(f"No {doctype} records available")
    return row[0].name


def _cleanup(matrix: Matrix) -> dict[str, Any]:
    attempts = []
    failures = []
    for doctype, name in _cleanup_targets(matrix):
        try:
            if frappe.db.exists(doctype, name):
                frappe.delete_doc(doctype, name, force=True, ignore_permissions=True)
                attempts.append({"doctype": doctype, "name": name, "deleted": True})
        except Exception as exc:
            failures.append({"doctype": doctype, "name": name, "error": f"{type(exc).__name__}: {exc}"})
    frappe.db.commit()
    return {"deleted": attempts, "failures": failures}


def _cleanup_targets(matrix: Matrix) -> list[tuple[str, str]]:
    names_by_type = {doctype: set(names) for doctype, names in matrix.created.items()}
    for lead_name in names_by_type.get("Lead", set()):
        for doctype in ("Email Queue", "Communication", "Comment", "ToDo", "Event"):
            filters = _reference_filters(doctype, "Lead", lead_name)
            if not filters:
                continue
            for name in frappe.get_all(doctype, filters=filters, pluck="name", limit_page_length=200):
                names_by_type.setdefault(doctype, set()).add(name)
        if frappe.get_meta("Task").has_field("custom_lt_lead"):
            for name in frappe.get_all(
                "Task",
                filters={"custom_lt_lead": lead_name},
                pluck="name",
                limit_page_length=200,
            ):
                names_by_type.setdefault("Task", set()).add(name)
        for contact_name in frappe.get_all(
            "Dynamic Link",
            filters={"parenttype": "Contact", "link_doctype": "Lead", "link_name": lead_name},
            pluck="parent",
            limit_page_length=50,
        ):
            names_by_type.setdefault("Contact", set()).add(contact_name)

    for customer_name in names_by_type.get("Customer", set()):
        for doctype in ("Contact", "Address"):
            for name in frappe.get_all(
                "Dynamic Link",
                filters={"parenttype": doctype, "link_doctype": "Customer", "link_name": customer_name},
                pluck="parent",
                limit_page_length=50,
            ):
                names_by_type.setdefault(doctype, set()).add(name)

    order = [
        "Email Queue",
        "Communication",
        "Comment",
        "ToDo",
        "Task",
        "Event",
        "Address",
        "Contact",
        "Lead",
        "Customer",
    ]
    targets = []
    for doctype in order:
        targets.extend((doctype, name) for name in sorted(names_by_type.get(doctype, set())))
    return targets


def _reference_filters(doctype: str, reference_doctype: str, reference_name: str) -> dict[str, Any] | None:
    if doctype == "ToDo":
        meta = frappe.get_meta(doctype)
        if meta.has_field("reference_type") and meta.has_field("reference_name"):
            return {"reference_type": reference_doctype, "reference_name": reference_name}
        return None
    meta = frappe.get_meta(doctype)
    if meta.has_field("reference_doctype") and meta.has_field("reference_name"):
        return {"reference_doctype": reference_doctype, "reference_name": reference_name}
    return None
