"""Fake-data contract for no-live customer reminder dry runs."""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable

from locally_twisted.paperwork import customer_reminder_dry_run


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
    """Run fake normal/outlier scenarios against the dry-run reminder queue."""
    scenario_specs: list[tuple[str, Callable[[], tuple[dict[str, Any], dict[str, Any]]], Callable[[dict[str, Any]], list[str]]]] = [
        ("overdue_payment_reminder_review_ready", _sources_overdue_payment_reminder, _expect_payment_review_now),
        ("severe_overdue_statement_review", _sources_severe_overdue_statement, _expect_statement_review_now),
        ("current_unpaid_hold_until_due", _sources_current_unpaid, _expect_hold_until_due),
        ("missing_payment_path_blocks_send", _sources_missing_payment_path, _expect_payment_path_blocker),
        ("empty_digest_ok", _sources_empty, _expect_empty_ok),
        ("malformed_delivery_enabled_fails", _sources_malformed_delivery_enabled, _expect_malformed_failure),
    ]

    scenarios = []
    failures: list[str] = []
    for scenario_id, source_factory, expectation in scenario_specs:
        digest, draft_packets = source_factory()
        result = _render(digest, draft_packets)
        scenario_failures = expectation(result)
        scenarios.append(
            {
                "id": scenario_id,
                "passed": not scenario_failures,
                "queue_item_count": result.get("summary", {}).get("queue_item_count"),
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
        "customer_delivery_enabled": False,
        "scenario_count": len(scenarios),
        "scenarios": scenarios,
        "failures": failures,
    }


def _render(digest: dict[str, Any], draft_packets: dict[str, Any]) -> dict[str, Any]:
    return customer_reminder_dry_run.build_from_sources(
        digest,
        draft_packets,
        guard_counts_before=deepcopy(GUARD_COUNTS),
        guard_counts_after=deepcopy(GUARD_COUNTS),
        generated_at=FIXED_GENERATED_AT,
    )


def _sources_overdue_payment_reminder() -> tuple[dict[str, Any], dict[str, Any]]:
    return _sources([_packet("ACC-SINV-TEST-0001", "Normal Accounting", days_overdue=9)])


def _sources_severe_overdue_statement() -> tuple[dict[str, Any], dict[str, Any]]:
    return _sources([_packet("ACC-SINV-TEST-0002", "Weber State University", days_overdue=35)])


def _sources_current_unpaid() -> tuple[dict[str, Any], dict[str, Any]]:
    return _sources([_packet("ACC-SINV-TEST-0003", "Fresh Customer", days_overdue=0)])


def _sources_missing_payment_path() -> tuple[dict[str, Any], dict[str, Any]]:
    return _sources(
        [
            _packet(
                "ACC-SINV-TEST-0004",
                "Dealer Marketing Office",
                days_overdue=14,
                payment_request=None,
            )
        ]
    )


def _sources_empty() -> tuple[dict[str, Any], dict[str, Any]]:
    return _sources([])


def _sources_malformed_delivery_enabled() -> tuple[dict[str, Any], dict[str, Any]]:
    packet = _packet("ACC-SINV-TEST-0005", "Malformed Customer", days_overdue=7)
    packet["send_status"] = "ready_to_send"
    packet["human_approval_required"] = False
    return _sources([packet])


def _sources(packets: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    digest_items = [
        {
            "invoice": packet.get("invoice"),
            "customer": packet.get("customer"),
            "customer_name": packet.get("customer_name"),
            "priority": packet.get("priority"),
            "days_overdue": packet.get("days_overdue"),
            "balance_due": packet.get("balance_due"),
            "send_status": packet.get("send_status"),
            "human_approval_required": packet.get("human_approval_required"),
            "section_ids": [section.get("document_id") for section in packet.get("sections") or []],
        }
        for packet in packets
    ]
    digest = {
        "ok": True,
        "generated_at": FIXED_GENERATED_AT,
        "read_only": True,
        "send_allowed": False,
        "mutation_allowed": False,
        "digest_type": "paperwork_review_digest",
        "sections": {
            "unpaid_invoice_packets": {
                "id": "unpaid_invoice_packets",
                "label": "Unpaid invoice packets",
                "count": len(digest_items),
                "items": digest_items,
            },
            "cutover_deferred_not_blocking": {"id": "cutover_deferred_not_blocking", "label": "Cutover", "count": 0, "items": []},
            "setup_gaps": {"id": "setup_gaps", "label": "Setup gaps", "count": 0, "items": []},
            "partial_connections": {"id": "partial_connections", "label": "Partial", "count": 0, "items": []},
            "next_safe_actions": {"id": "next_safe_actions", "label": "Next safe actions", "count": 1, "items": ["Review internally only."]},
        },
    }
    draft_packets = {
        "ok": True,
        "generated_at": FIXED_GENERATED_AT,
        "read_only": True,
        "send_allowed": False,
        "mutation_allowed": False,
        "packet_type": "unpaid_invoice_draft_packet",
        "packet_count": len(packets),
        "packets": packets,
    }
    return digest, draft_packets


def _packet(
    invoice: str,
    customer_name: str,
    *,
    days_overdue: int,
    payment_request: str | None = "PAY-REQ-TEST-0001",
) -> dict[str, Any]:
    priority = "overdue_review" if days_overdue else "unpaid_review"
    key_fields = {
        "invoice_number": invoice,
        "customer": customer_name,
        "customer_name": customer_name,
        "due_date": "2026-05-01" if days_overdue else "2026-05-20",
        "days_overdue": days_overdue,
        "balance_due": "165.00",
        "currency": "USD",
        "payment_request": payment_request,
        "open_invoice_count_for_customer": 2 if days_overdue >= 30 else 1,
        "total_open_balance_for_customer": "330.00" if days_overdue >= 30 else "165.00",
    }
    return {
        "invoice": invoice,
        "customer": customer_name,
        "customer_name": customer_name,
        "priority": priority,
        "days_overdue": days_overdue,
        "balance_due": key_fields["balance_due"],
        "send_status": "draft_only_not_sent",
        "human_approval_required": True,
        "review_gate": "Human approval of invoice status, recipient, cadence, balance, and copy",
        "sections": [
            _section("payment_reminder_draft", key_fields, payment_request),
            _section("statement_of_account", key_fields, payment_request),
        ],
        "internal_review_checklist": [
            "Confirm invoice status.",
            "Confirm recipient.",
            "Confirm cadence.",
            "Confirm payment path.",
        ],
    }


def _section(document_id: str, key_fields: dict[str, Any], payment_request: str | None) -> dict[str, Any]:
    return {
        "document_id": document_id,
        "title": "Payment Reminder Draft" if document_id == "payment_reminder_draft" else "Statement Of Account",
        "send_status": "draft_only_not_sent",
        "subject": f"Draft only: {document_id} for {key_fields['invoice_number']}",
        "answer_first": f"Payment reference: {payment_request or 'not connected yet'}.",
        "body_preview": "Draft-only customer reminder review copy.",
        "key_fields_to_review": deepcopy(key_fields),
        "do_not_send_without": "human_approval | correct_recipient | reviewed_invoice_status",
    }


def _expect_payment_review_now(result: dict[str, Any]) -> list[str]:
    failures = _expect_one_queue_item(result)
    item = _first_item(result)
    if item.get("recommended_cadence") != "review_now_payment_reminder":
        failures.append("expected review_now_payment_reminder cadence")
    return failures


def _expect_statement_review_now(result: dict[str, Any]) -> list[str]:
    failures = _expect_one_queue_item(result)
    item = _first_item(result)
    if item.get("recommended_cadence") != "review_now_statement_and_payment_path":
        failures.append("expected review_now_statement_and_payment_path cadence")
    if "statement_of_account" not in item.get("recommended_document_ids", []):
        failures.append("expected statement_of_account recommendation")
    return failures


def _expect_hold_until_due(result: dict[str, Any]) -> list[str]:
    failures = _expect_one_queue_item(result)
    if _first_item(result).get("recommended_cadence") != "hold_until_due_or_terms_review":
        failures.append("expected hold_until_due_or_terms_review cadence")
    return failures


def _expect_payment_path_blocker(result: dict[str, Any]) -> list[str]:
    failures = _expect_one_queue_item(result)
    blockers = _first_item(result).get("blocked_customer_send_until") or []
    if "payment_path_confirmed" not in blockers:
        failures.append("missing payment_path_confirmed blocker")
    return failures


def _expect_empty_ok(result: dict[str, Any]) -> list[str]:
    if result.get("ok") is not True:
        return ["empty source should be ok"]
    if result.get("summary", {}).get("queue_item_count") != 0:
        return ["empty source should produce zero queue items"]
    return []


def _expect_malformed_failure(result: dict[str, Any]) -> list[str]:
    if result.get("ok") is not False:
        return ["malformed delivery-enabled source should fail"]
    failures = result.get("failures") or []
    if not any("draft" in failure.lower() or "approval" in failure.lower() for failure in failures):
        return ["malformed result did not explain draft/approval failure"]
    return []


def _expect_one_queue_item(result: dict[str, Any]) -> list[str]:
    failures = []
    if result.get("ok") is not True:
        failures.append("expected ok true")
    if result.get("send_allowed") is not False:
        failures.append("dry run allows sending")
    if result.get("customer_delivery_enabled") is not False:
        failures.append("dry run enables customer delivery")
    if result.get("summary", {}).get("queue_item_count") != 1:
        failures.append(f"expected one queue item, found {result.get('summary', {}).get('queue_item_count')}")
    item = _first_item(result)
    if item and item.get("send_status") != "draft_only_not_sent":
        failures.append("queue item is not draft-only")
    if item and item.get("delivery_mode") != "internal_review_only":
        failures.append("queue item delivery mode is not internal_review_only")
    return failures


def _first_item(result: dict[str, Any]) -> dict[str, Any]:
    return (result.get("queue_items") or [{}])[0]
