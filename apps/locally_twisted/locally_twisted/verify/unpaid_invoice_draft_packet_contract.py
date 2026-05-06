"""Fake-data contract for unpaid invoice draft packet rendering.

The live unpaid-invoice verifier proves current ERPNext integration. This module
proves deterministic normal/outlier packet behavior without creating customer
communications or accounting records.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable

from locally_twisted.paperwork import unpaid_invoice_draft_packet


FIXED_GENERATED_AT = "2026-05-06T00:00:00"
GUARD_COUNTS = {
    "Email Queue": 30,
    "Communication": 12,
    "Sales Invoice": 1,
    "Payment Request": 8,
    "Payment Entry": 0,
    "Journal Entry": 0,
}


def run() -> dict[str, object]:
    """Run fake normal/outlier scenarios against the draft packet renderer."""
    scenario_specs: list[tuple[str, Callable[[], dict[str, Any]], Callable[[dict[str, Any]], list[str]]]] = [
        ("normal_unpaid_invoice", _review_normal_unpaid_invoice, _expect_one_clean_packet),
        ("overdue_with_po_reference", _review_overdue_with_po_reference, _expect_one_clean_packet),
        ("multiple_open_invoices", _review_multiple_open_invoices, _expect_multiple_open_invoice_statement),
        ("missing_payment_request", _review_missing_payment_request, _expect_missing_payment_request_copy),
        ("paid_invoice_excluded", _review_paid_invoice_excluded, _expect_no_packets),
        ("malformed_missing_human_approval", _review_missing_human_approval, _expect_malformed_failure),
    ]

    scenarios = []
    failures: list[str] = []
    for scenario_id, review_factory, expectation in scenario_specs:
        result = _render(review_factory())
        scenario_failures = expectation(result)
        scenarios.append(
            {
                "id": scenario_id,
                "passed": not scenario_failures,
                "packet_count": result.get("packet_count"),
                "render_ok": result.get("ok"),
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
        "scenario_count": len(scenarios),
        "scenarios": scenarios,
        "failures": failures,
    }


def _render(review: dict[str, Any]) -> dict[str, Any]:
    return unpaid_invoice_draft_packet.render_from_review(
        review,
        guard_counts_before=deepcopy(GUARD_COUNTS),
        guard_counts_after=deepcopy(GUARD_COUNTS),
        generated_at=FIXED_GENERATED_AT,
    )


def _review_normal_unpaid_invoice() -> dict[str, Any]:
    return _review([_candidate("ACC-SINV-TEST-0001", "Normal Accounting", days_overdue=0)])


def _review_overdue_with_po_reference() -> dict[str, Any]:
    return _review(
        [
            _candidate(
                "ACC-SINV-TEST-0002",
                "Weber State University",
                days_overdue=14,
                po_reference="WSU-PO-4455",
                payment_terms="Net 30",
            )
        ]
    )


def _review_multiple_open_invoices() -> dict[str, Any]:
    return _review(
        [
            _candidate(
                "ACC-SINV-TEST-0003",
                "Intermountain Health",
                days_overdue=4,
                open_invoice_count=3,
                total_open_balance="925.00",
            )
        ]
    )


def _review_missing_payment_request() -> dict[str, Any]:
    return _review(
        [
            _candidate(
                "ACC-SINV-TEST-0004",
                "Dealer Marketing Office",
                days_overdue=0,
                due_date="Due on receipt or per approved terms",
                payment_request=None,
            )
        ]
    )


def _review_paid_invoice_excluded() -> dict[str, Any]:
    return _review([])


def _review_missing_human_approval() -> dict[str, Any]:
    candidate = _candidate("ACC-SINV-TEST-0005", "Malformed Customer", days_overdue=7)
    candidate["draft_documents"][0]["do_not_send_without"] = "correct_recipient | reviewed_invoice_status"
    return _review([candidate])


def _review(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "ok": True,
        "generated_at": FIXED_GENERATED_AT,
        "read_only": True,
        "send_allowed": False,
        "mutation_allowed": False,
        "review_surface": "unpaid_invoice_review",
        "candidate_count": len(candidates),
        "review_candidates": candidates,
    }


def _candidate(
    invoice: str,
    customer_name: str,
    *,
    days_overdue: int,
    due_date: str = "2026-05-20",
    payment_request: str | None = "PAY-REQ-TEST-0001",
    po_reference: str = "PO-REVIEW",
    payment_terms: str = "Review terms on invoice",
    open_invoice_count: int = 1,
    total_open_balance: str = "165.00",
) -> dict[str, Any]:
    priority = "overdue_review" if days_overdue else "unpaid_review"
    key_fields = {
        "invoice_number": invoice,
        "customer": customer_name,
        "customer_name": customer_name,
        "invoice_date": "2026-05-01",
        "due_date": due_date,
        "days_overdue": days_overdue,
        "balance_due": "165.00",
        "invoice_total": "165.00",
        "currency": "USD",
        "po_reference": po_reference,
        "payment_terms": payment_terms,
        "payment_request": payment_request,
        "open_invoice_count_for_customer": open_invoice_count,
        "total_open_balance_for_customer": total_open_balance,
        "review_reason": "Invoice is overdue" if priority == "overdue_review" else "Invoice is unpaid",
    }
    return {
        "invoice": invoice,
        "customer": customer_name,
        "customer_name": customer_name,
        "status": "Overdue" if days_overdue else "Unpaid",
        "priority": priority,
        "days_overdue": days_overdue,
        "balance_due": key_fields["balance_due"],
        "draft_document_ids": ["payment_reminder_draft", "statement_of_account"],
        "draft_documents": [
            _document("payment_reminder_draft", "Payment Reminder Draft", key_fields),
            _document("statement_of_account", "Statement Of Account", key_fields),
        ],
        "human_review": {
            "required": True,
            "send_status": "not_sent",
        },
    }


def _document(document_id: str, title: str, key_fields: dict[str, Any]) -> dict[str, Any]:
    return {
        "document_id": document_id,
        "title": title,
        "audience": "Accounts payable or customer accounting",
        "delivery_channels": ["draft email only"],
        "review_gate": "Human approval of recipient, cadence, and copy",
        "do_not_send_without": "human_approval | correct_recipient | reviewed_invoice_status",
        "automation_ready": "generator_ready_review_required",
        "send_status": "draft_only_not_sent",
        "key_fields_to_review": deepcopy(key_fields),
    }


def _expect_one_clean_packet(result: dict[str, Any]) -> list[str]:
    failures = []
    if result.get("ok") is not True:
        failures.append("expected render_ok true")
    if result.get("packet_count") != 1:
        failures.append(f"expected 1 packet, found {result.get('packet_count')}")
    packets = result.get("packets") or []
    if packets and packets[0].get("send_status") != "draft_only_not_sent":
        failures.append("packet is not draft-only")
    if packets and len(packets[0].get("sections") or []) != 2:
        failures.append("packet does not have two sections")
    return failures


def _expect_multiple_open_invoice_statement(result: dict[str, Any]) -> list[str]:
    failures = _expect_one_clean_packet(result)
    statement = _section(result, "statement_of_account")
    if "3 open invoice(s)" not in (statement.get("answer_first") or ""):
        failures.append("statement answer-first copy did not include multiple open invoices")
    return failures


def _expect_missing_payment_request_copy(result: dict[str, Any]) -> list[str]:
    failures = _expect_one_clean_packet(result)
    reminder = _section(result, "payment_reminder_draft")
    if "not connected yet" not in (reminder.get("answer_first") or ""):
        failures.append("payment reminder did not flag missing payment request")
    return failures


def _expect_no_packets(result: dict[str, Any]) -> list[str]:
    if result.get("ok") is not True:
        return ["empty paid/reconciled input should render ok"]
    if result.get("packet_count") != 0:
        return [f"expected 0 packets, found {result.get('packet_count')}"]
    return []


def _expect_malformed_failure(result: dict[str, Any]) -> list[str]:
    if result.get("ok") is not False:
        return ["malformed missing human approval packet should fail"]
    failures = result.get("failures") or []
    if not any("draft-only" in failure or "human" in failure.lower() for failure in failures):
        return ["malformed result did not explain the human approval/draft-only failure"]
    return []


def _section(result: dict[str, Any], document_id: str) -> dict[str, Any]:
    for packet in result.get("packets") or []:
        for section in packet.get("sections") or []:
            if section.get("document_id") == document_id:
                return section
    return {}
