"""No-live report data source for customer reminder review.

This module turns the dry-run reminder queue into a table-style internal report.
It is meant for Desk/report/scheduled-internal-display work, not customer
delivery.
"""
from __future__ import annotations

from typing import Any

import frappe
from frappe.utils import now_datetime

from locally_twisted.paperwork import customer_reminder_dry_run


REPORT_TYPE = "customer_reminder_review_report"
SOURCE_SURFACE = "customer_reminder_dry_run"
COLUMNS = (
    {"label": "Invoice", "fieldname": "invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 180},
    {"label": "Customer", "fieldname": "customer_name", "fieldtype": "Data", "width": 220},
    {"label": "Days Overdue", "fieldname": "days_overdue", "fieldtype": "Int", "width": 110},
    {"label": "Balance Due", "fieldname": "balance_due", "fieldtype": "Currency", "width": 120},
    {"label": "Cadence", "fieldname": "recommended_cadence", "fieldtype": "Data", "width": 220},
    {"label": "Drafts", "fieldname": "recommended_document_ids", "fieldtype": "Data", "width": 220},
    {"label": "Send Status", "fieldname": "send_status", "fieldtype": "Data", "width": 160},
    {"label": "Blocked Until", "fieldname": "blocked_customer_send_until", "fieldtype": "Data", "width": 360},
)


def run() -> dict[str, object]:
    """Return the no-live customer reminder review report without mutations."""
    before = _guard_counts()
    dry_run = customer_reminder_dry_run.run()
    return build_from_dry_run(dry_run, guard_counts_before=before)


def build_from_dry_run(
    dry_run: dict[str, Any],
    *,
    guard_counts_before: dict[str, int] | None = None,
    guard_counts_after: dict[str, int] | None = None,
    generated_at: str | None = None,
) -> dict[str, object]:
    """Build report rows from a customer reminder dry-run payload."""
    before = guard_counts_before if guard_counts_before is not None else {}
    failures: list[str] = []

    failures.extend(_source_failures(dry_run))
    queue_items = list(dry_run.get("queue_items") or [])
    rows = [_row(item) for item in queue_items]
    failures.extend(_row_failures(rows, queue_items))

    if guard_counts_after is not None:
        after = guard_counts_after
    elif guard_counts_before is not None:
        after = _guard_counts()
    else:
        after = before

    if before != after:
        failures.append("mutation guard changed while building customer reminder review report")

    groups = {
        "review_now": _group(
            "review_now",
            "Review now",
            [row for row in rows if str(row["recommended_cadence"]).startswith("review_now")],
        ),
        "hold": _group(
            "hold",
            "Hold / terms review",
            [row for row in rows if not str(row["recommended_cadence"]).startswith("review_now")],
        ),
        "blocked_send": _group(
            "blocked_send",
            "Blocked from customer send",
            [row for row in rows if row.get("blocked_customer_send_until")],
        ),
    }

    return {
        "ok": not failures,
        "generated_at": generated_at or now_datetime().isoformat(),
        "read_only": True,
        "send_allowed": False,
        "mutation_allowed": False,
        "customer_delivery_enabled": False,
        "automatic_delivery_enabled": False,
        "report_type": REPORT_TYPE,
        "source_surface": SOURCE_SURFACE,
        "operating_mode": "no_live_internal_review",
        "columns": list(COLUMNS),
        "rows": rows,
        "groups": groups,
        "summary": {
            "row_count": len(rows),
            "review_now_count": groups["review_now"]["count"],
            "hold_count": groups["hold"]["count"],
            "blocked_send_count": groups["blocked_send"]["count"],
        },
        "mutation_guard": {
            "guarded_doctypes": list(customer_reminder_dry_run.MUTATION_GUARD_DOCTYPES),
            "before": before,
            "after": after,
            "changed": before != after,
        },
        "boundaries": {
            "internal_report_only": True,
            "no_email_queue": True,
            "no_communication": True,
            "no_payment_request": True,
            "no_payment_entry": True,
            "no_journal_entry": True,
            "no_invoice_submit_cancel": True,
            "no_error_log": True,
            "no_customer_send": True,
        },
        "next_safe_action": "Attach these rows to a Desk page or scheduled internal-only report; do not enable customer sending.",
        "failures": failures,
    }


def _row(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "queue_id": item.get("queue_id"),
        "invoice": item.get("invoice"),
        "customer": item.get("customer"),
        "customer_name": item.get("customer_name"),
        "days_overdue": int(item.get("days_overdue") or 0),
        "balance_due": item.get("balance_due"),
        "recommended_cadence": item.get("recommended_cadence"),
        "recommended_document_ids": ", ".join(item.get("recommended_document_ids") or []),
        "send_status": item.get("send_status"),
        "delivery_mode": item.get("delivery_mode"),
        "customer_delivery_enabled": bool(item.get("customer_delivery_enabled")),
        "automatic_delivery_enabled": bool(item.get("automatic_delivery_enabled")),
        "blocked_customer_send_until": ", ".join(item.get("blocked_customer_send_until") or []),
        "review_checklist": " | ".join(item.get("review_checklist") or []),
        "draft_section_count": len(item.get("draft_sections") or []),
    }


def _group(group_id: str, label: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "id": group_id,
        "label": label,
        "count": len(rows),
        "invoice_names": [row.get("invoice") for row in rows],
    }


def _source_failures(dry_run: dict[str, Any]) -> list[str]:
    failures = []
    if dry_run.get("ok") is not True:
        failures.extend(f"customer_reminder_dry_run: {failure}" for failure in dry_run.get("failures") or ["not ok"])
    if dry_run.get("read_only") is not True:
        failures.append("customer_reminder_dry_run is not marked read_only")
    if dry_run.get("send_allowed") is not False:
        failures.append("customer_reminder_dry_run allows sending")
    if dry_run.get("mutation_allowed") is not False:
        failures.append("customer_reminder_dry_run allows mutation")
    if dry_run.get("customer_delivery_enabled") is not False:
        failures.append("customer_reminder_dry_run enables customer delivery")
    if dry_run.get("automatic_delivery_enabled") is not False:
        failures.append("customer_reminder_dry_run enables automatic delivery")
    if dry_run.get("reminder_surface") != SOURCE_SURFACE:
        failures.append("customer_reminder_dry_run returned wrong reminder_surface")
    if dry_run.get("mutation_guard", {}).get("changed"):
        failures.append("customer_reminder_dry_run mutation guard changed")
    return failures


def _row_failures(rows: list[dict[str, Any]], queue_items: list[dict[str, Any]]) -> list[str]:
    failures = []
    for item in queue_items:
        invoice = item.get("invoice") or "<missing invoice>"
        if item.get("delivery_mode") != "internal_review_only":
            failures.append(f"{invoice} source queue item is not internal-review-only")
        if item.get("send_status") != "draft_only_not_sent":
            failures.append(f"{invoice} source queue item is not draft-only")
        if item.get("customer_delivery_enabled") is not False:
            failures.append(f"{invoice} source queue item enables customer delivery")
        if item.get("automatic_delivery_enabled") is not False:
            failures.append(f"{invoice} source queue item enables automatic delivery")

    for row in rows:
        invoice = row.get("invoice") or "<missing invoice>"
        if row.get("delivery_mode") != "internal_review_only":
            failures.append(f"{invoice} report row is not internal-review-only")
        if row.get("send_status") != "draft_only_not_sent":
            failures.append(f"{invoice} report row is not draft-only")
        if row.get("customer_delivery_enabled") is not False:
            failures.append(f"{invoice} report row enables customer delivery")
        if row.get("automatic_delivery_enabled") is not False:
            failures.append(f"{invoice} report row enables automatic delivery")
    return failures


def _guard_counts() -> dict[str, int]:
    return {
        doctype: int(frappe.db.count(doctype))
        for doctype in customer_reminder_dry_run.MUTATION_GUARD_DOCTYPES
        if frappe.db.exists("DocType", doctype)
    }
