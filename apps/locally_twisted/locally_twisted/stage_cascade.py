"""Safe operational cascades for LT CRM stage changes.

This module deliberately creates only Task records. It does not create
quotes, orders, invoices, payment requests, customers, or accounting state.
"""
from __future__ import annotations

import frappe
from frappe.utils import add_days, getdate, today

from locally_twisted.crm_pipeline import ARCHIVE_STAGE, PIPELINE_FIELD, PIPELINE_OPTIONS


LEAD_TASK_FIELD = "custom_lt_lead"
TASK_STAGE_FIELD = "custom_pipeline_stage"
TASK_KEY_FIELD = "custom_lt_cascade_key"

STAGE_TASKS = {
    "New Inquiry": {
        "subject": "Reply to new inquiry",
        "description": "Call or text the customer, then record what happened on the Lead.",
        "priority": "High",
        "due_in_days": 0,
    },
    "Quote Sent/Awaiting Approval": {
        "subject": "Follow up on quote",
        "description": "Follow up on the quote and note whether the customer approved, needs changes, or went quiet.",
        "priority": "High",
        "due_in_days": 2,
    },
    "Approved": {
        "subject": "Confirm booking details",
        "description": "Confirm date, location, timing, colors, delivery or pickup notes, and payment/deposit status before production work starts.",
        "priority": "High",
        "due_in_days": 0,
    },
    "In Production": {
        "subject": "Prepare event production plan",
        "description": "Prepare materials, staffing, delivery/setup notes, and any contractor communication needed for this event.",
        "priority": "Medium",
        "due_in_days": 3,
        "prefer_event_date": True,
    },
    "Event/Post Event": {
        "subject": "Send post-event follow-up",
        "description": "After the event, follow up with the customer, confirm everything went well, and ask for review/photo permission if appropriate.",
        "priority": "Medium",
        "due_in_days": 1,
        "event_offset_days": 1,
    },
}


def after_insert(doc, method=None) -> None:
    _safe_run(doc)


def on_update(doc, method=None) -> None:
    _safe_run(doc)


def _safe_run(doc) -> None:
    try:
        if not _task_fields_ready():
            return
        _sync_stage_tasks(doc)
    except Exception as exc:
        frappe.log_error(
            title=f"Lead stage cascade failed for {doc.name}",
            message=f"{type(exc).__name__}: {exc}\nLead: {doc.name}",
        )


def _task_fields_ready() -> bool:
    meta = frappe.get_meta("Task")
    return all(
        meta.has_field(fieldname)
        for fieldname in (LEAD_TASK_FIELD, TASK_STAGE_FIELD, TASK_KEY_FIELD)
    )


def _sync_stage_tasks(doc) -> None:
    stage = doc.get(PIPELINE_FIELD) or "New Inquiry"
    if stage not in PIPELINE_OPTIONS:
        return

    if stage == ARCHIVE_STAGE:
        _complete_open_cascade_tasks(doc.name)
        return

    _complete_other_stage_tasks(doc.name, stage)
    _ensure_current_stage_task(doc, stage)


def _complete_other_stage_tasks(lead_name: str, current_stage: str) -> None:
    for task_name in frappe.get_all(
        "Task",
        filters={
            LEAD_TASK_FIELD: lead_name,
            TASK_STAGE_FIELD: ["!=", current_stage],
            "status": ["not in", ["Completed", "Cancelled"]],
        },
        pluck="name",
        limit_page_length=100,
    ):
        _complete_task(task_name)


def _complete_open_cascade_tasks(lead_name: str) -> None:
    for task_name in frappe.get_all(
        "Task",
        filters={
            LEAD_TASK_FIELD: lead_name,
            "status": ["not in", ["Completed", "Cancelled"]],
        },
        pluck="name",
        limit_page_length=100,
    ):
        _complete_task(task_name)


def _ensure_current_stage_task(doc, stage: str) -> None:
    spec = STAGE_TASKS.get(stage)
    if not spec:
        return

    key = _cascade_key(doc.name, stage)
    existing = frappe.get_all(
        "Task",
        filters={TASK_KEY_FIELD: key},
        fields=["name", "status"],
        limit_page_length=1,
    )
    if existing:
        task = frappe.get_doc("Task", existing[0].name)
        changed = False
        fields = _task_fields(doc, stage, spec)
        for fieldname, value in fields.items():
            if getattr(task, fieldname, None) != value:
                setattr(task, fieldname, value)
                changed = True
        if task.status in {"Completed", "Cancelled"}:
            task.status = "Open"
            task.progress = 0
            task.completed_on = None
            task.completed_by = None
            changed = True
        if changed:
            task.save(ignore_permissions=True)
        return

    frappe.get_doc({"doctype": "Task", **_task_fields(doc, stage, spec)}).insert(
        ignore_permissions=True
    )


def _task_fields(doc, stage: str, spec: dict) -> dict:
    due_date = _due_date(doc, spec)
    return {
        "subject": f"{spec['subject']}: {_lead_label(doc)}",
        "status": "Open",
        "priority": spec["priority"],
        "exp_start_date": today(),
        "exp_end_date": due_date,
        "description": _description(doc, spec["description"]),
        LEAD_TASK_FIELD: doc.name,
        TASK_STAGE_FIELD: stage,
        TASK_KEY_FIELD: _cascade_key(doc.name, stage),
    }


def _complete_task(task_name: str) -> None:
    task = frappe.get_doc("Task", task_name)
    task.status = "Completed"
    task.progress = 100
    task.completed_on = today()
    if frappe.session.user and frappe.db.exists("User", frappe.session.user):
        task.completed_by = frappe.session.user
    task.save(ignore_permissions=True)


def _due_date(doc, spec: dict) -> str:
    event_date = doc.get("custom_event_date")
    if event_date and spec.get("prefer_event_date"):
        return str(getdate(event_date))
    if event_date and "event_offset_days" in spec:
        return str(add_days(getdate(event_date), spec["event_offset_days"]))
    return str(add_days(today(), spec.get("due_in_days", 0)))


def _description(doc, action_text: str) -> str:
    pieces = [
        action_text,
        "",
        f"Lead: {doc.name}",
    ]
    if doc.get("custom_event_date"):
        pieces.append(f"Event date: {doc.get('custom_event_date')}")
    if doc.get("custom_event_location"):
        pieces.append(f"Location: {doc.get('custom_event_location')}")
    pieces.append("")
    pieces.append("This task is operational only. It does not create revenue, invoices, payments, or win/loss reporting.")
    return "\n".join(pieces)


def _lead_label(doc) -> str:
    return (doc.get("lead_name") or doc.get("first_name") or doc.name or "Inquiry").split(" - ")[0]


def _cascade_key(lead_name: str, stage: str) -> str:
    return f"{lead_name}::{stage}"
