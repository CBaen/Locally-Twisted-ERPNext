"""Fake-data contract for the no-live customer reminder review report."""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable

from locally_twisted.paperwork import customer_reminder_review_report


FIXED_GENERATED_AT = "2026-05-06T00:00:00"
GUARD_COUNTS = {
    "Email Queue": 30,
    "Communication": 12,
    "Sales Invoice": 1,
    "Payment Request": 8,
    "Payment Entry": 0,
    "Journal Entry": 0,
    "Error Log": 0,
}


def run() -> dict[str, object]:
    """Run fake report-shape scenarios against the reminder review report."""
    scenario_specs: list[tuple[str, Callable[[], dict[str, Any]], Callable[[dict[str, Any]], list[str]]]] = [
        ("mixed_queue_groups_rows", _dry_run_mixed_queue, _expect_grouped_rows),
        ("empty_queue_report_ok", _dry_run_empty_queue, _expect_empty_report),
        ("malformed_send_enabled_rejected", _dry_run_malformed_send_enabled, _expect_malformed_failure),
    ]

    scenarios = []
    failures: list[str] = []
    for scenario_id, dry_run_factory, expectation in scenario_specs:
        result = _render(dry_run_factory())
        scenario_failures = expectation(result)
        scenarios.append(
            {
                "id": scenario_id,
                "passed": not scenario_failures,
                "row_count": result.get("summary", {}).get("row_count"),
                "report_ok": result.get("ok"),
                "failures": scenario_failures,
            }
        )
        failures.extend(f"{scenario_id}: {failure}" for failure in scenario_failures)

    return {
        "ok": not failures,
        "generated_at": FIXED_GENERATED_AT,
        "read_only": True,
        "send_allowed": False,
        "mutation_allowed": False,
        "customer_delivery_enabled": False,
        "scenario_count": len(scenarios),
        "scenarios": scenarios,
        "failures": failures,
    }


def _render(dry_run: dict[str, Any]) -> dict[str, Any]:
    return customer_reminder_review_report.build_from_dry_run(
        dry_run,
        guard_counts_before=deepcopy(GUARD_COUNTS),
        guard_counts_after=deepcopy(GUARD_COUNTS),
        generated_at=FIXED_GENERATED_AT,
    )


def _dry_run_mixed_queue() -> dict[str, Any]:
    return _dry_run(
        [
            _queue_item("ACC-SINV-TEST-0001", "Normal Accounting", 9, "review_now_payment_reminder"),
            _queue_item("ACC-SINV-TEST-0002", "Weber State University", 35, "review_now_statement_and_payment_path"),
            _queue_item("ACC-SINV-TEST-0003", "Fresh Customer", 0, "hold_until_due_or_terms_review"),
        ]
    )


def _dry_run_empty_queue() -> dict[str, Any]:
    return _dry_run([])


def _dry_run_malformed_send_enabled() -> dict[str, Any]:
    item = _queue_item("ACC-SINV-TEST-0004", "Malformed Customer", 5, "review_now_payment_reminder")
    item["send_status"] = "ready_to_send"
    item["customer_delivery_enabled"] = True
    return _dry_run([item])


def _dry_run(queue_items: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "ok": True,
        "generated_at": FIXED_GENERATED_AT,
        "read_only": True,
        "send_allowed": False,
        "mutation_allowed": False,
        "customer_delivery_enabled": False,
        "automatic_delivery_enabled": False,
        "reminder_surface": "customer_reminder_dry_run",
        "operating_mode": "no_live_internal_review",
        "summary": {
            "queue_item_count": len(queue_items),
            "ready_for_internal_review_count": len(queue_items),
            "blocked_customer_send_count": len(queue_items),
        },
        "queue_items": queue_items,
    }


def _queue_item(invoice: str, customer_name: str, days_overdue: int, cadence: str) -> dict[str, Any]:
    return {
        "queue_id": f"customer-reminder-dry-run:{invoice}",
        "invoice": invoice,
        "customer": customer_name,
        "customer_name": customer_name,
        "priority": "overdue_review" if days_overdue else "unpaid_review",
        "days_overdue": days_overdue,
        "balance_due": "165.00",
        "operating_mode": "no_live_internal_review",
        "delivery_mode": "internal_review_only",
        "send_status": "draft_only_not_sent",
        "customer_delivery_enabled": False,
        "automatic_delivery_enabled": False,
        "human_approval_required": True,
        "recommended_cadence": cadence,
        "recommended_document_ids": ["statement_of_account", "payment_reminder_draft"]
        if days_overdue >= 30
        else ["payment_reminder_draft"],
        "blocked_customer_send_until": [
            "human_approval_recorded",
            "correct_recipient_confirmed",
            "invoice_status_rechecked",
            "cadence_approved",
            "copy_approved",
        ],
        "review_checklist": ["Confirm invoice status.", "Confirm recipient.", "Confirm cadence."],
        "draft_sections": [
            {
                "document_id": "payment_reminder_draft",
                "subject": f"Draft only: payment reminder for {invoice}",
                "answer_first": "Payment reminder answer-first copy.",
            }
        ],
    }


def _expect_grouped_rows(result: dict[str, Any]) -> list[str]:
    failures = _expect_report_basics(result)
    summary = result.get("summary", {})
    if summary.get("row_count") != 3:
        failures.append(f"expected 3 rows, found {summary.get('row_count')}")
    if summary.get("review_now_count") != 2:
        failures.append(f"expected 2 review-now rows, found {summary.get('review_now_count')}")
    if summary.get("hold_count") != 1:
        failures.append(f"expected 1 hold row, found {summary.get('hold_count')}")
    groups = result.get("groups") or {}
    if (groups.get("review_now") or {}).get("count") != 2:
        failures.append("review_now group count is wrong")
    if (groups.get("hold") or {}).get("count") != 1:
        failures.append("hold group count is wrong")
    return failures


def _expect_empty_report(result: dict[str, Any]) -> list[str]:
    failures = _expect_report_basics(result)
    if result.get("summary", {}).get("row_count") != 0:
        failures.append("empty queue should produce zero rows")
    return failures


def _expect_malformed_failure(result: dict[str, Any]) -> list[str]:
    if result.get("ok") is not False:
        return ["malformed send-enabled queue item should fail"]
    failures = result.get("failures") or []
    if not any("customer delivery" in failure.lower() or "draft" in failure.lower() for failure in failures):
        return ["malformed result did not explain delivery/draft failure"]
    return []


def _expect_report_basics(result: dict[str, Any]) -> list[str]:
    failures = []
    if result.get("ok") is not True:
        failures.append("expected report ok true")
    if result.get("read_only") is not True:
        failures.append("report is not read-only")
    if result.get("send_allowed") is not False:
        failures.append("report allows sending")
    if result.get("customer_delivery_enabled") is not False:
        failures.append("report enables customer delivery")
    if result.get("report_type") != "customer_reminder_review_report":
        failures.append("wrong report_type")
    columns = result.get("columns") or []
    for fieldname in ("invoice", "customer_name", "recommended_cadence", "send_status", "blocked_customer_send_until"):
        if fieldname not in {column.get("fieldname") for column in columns}:
            failures.append(f"missing report column {fieldname}")
    return failures
