"""Fake-data contract for outbound document send-readiness blockers."""
from __future__ import annotations

import time
from copy import deepcopy
from typing import Any, Callable

import frappe


FIXED_GENERATED_AT = "2026-05-08T00:00:00"


def run() -> dict[str, object]:
    scenario_specs: list[tuple[str, Callable[[], dict[str, Any]], Callable[[dict[str, Any]], list[str]]]] = [
        ("all_documents_block_without_required_fields", _scenario_all_block_missing_fields, _expect_all_blocked),
        ("all_documents_ready_when_complete", _scenario_all_ready_complete, _expect_all_ready),
        ("payment_reminder_missing_payment_path_blocks_send", _scenario_payment_path_missing, _expect_payment_path_blocked),
        ("vendor_w9_missing_secure_attachment_blocks_send", _scenario_vendor_sensitive_missing, _expect_vendor_blocked),
        ("record_level_blocker_writes_evidence", _scenario_record_level_blocker, _expect_record_blocker),
    ]

    scenarios = []
    failures: list[str] = []
    for scenario_id, source_factory, expectation in scenario_specs:
        result = source_factory()
        scenario_failures = expectation(result)
        scenarios.append(
            {
                "id": scenario_id,
                "passed": not scenario_failures,
                "result_ok": result.get("ok"),
                "send_ready_count": result.get("send_ready_count"),
                "blocked_count": result.get("blocked_count"),
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


def _scenario_all_block_missing_fields() -> dict[str, Any]:
    from locally_twisted.outbound_documents.registry import REQUIRED_DOCUMENT_IDS
    from locally_twisted.outbound_documents.send_readiness import evaluate_send_readiness

    results = [
        evaluate_send_readiness(document_id, {}, [])
        for document_id in REQUIRED_DOCUMENT_IDS
    ]
    return _summary(results)


def _scenario_all_ready_complete() -> dict[str, Any]:
    from locally_twisted.outbound_documents.registry import REQUIRED_DOCUMENT_IDS
    from locally_twisted.outbound_documents.send_readiness import (
        complete_fake_approvals,
        complete_fake_fields,
        evaluate_send_readiness,
    )

    results = [
        evaluate_send_readiness(
            document_id,
            complete_fake_fields(document_id),
            complete_fake_approvals(document_id),
        )
        for document_id in REQUIRED_DOCUMENT_IDS
    ]
    return _summary(results)


def _scenario_payment_path_missing() -> dict[str, Any]:
    from locally_twisted.outbound_documents.send_readiness import (
        complete_fake_approvals,
        complete_fake_fields,
        evaluate_send_readiness,
    )

    fields = complete_fake_fields("payment_reminder_draft")
    fields["payment_path"] = ""
    fields["payment_link_if_available"] = "not connected yet"
    result = evaluate_send_readiness(
        "payment_reminder_draft",
        fields,
        complete_fake_approvals("payment_reminder_draft"),
    )
    return _summary([result])


def _scenario_vendor_sensitive_missing() -> dict[str, Any]:
    from locally_twisted.outbound_documents.send_readiness import (
        complete_fake_approvals,
        complete_fake_fields,
        evaluate_send_readiness,
    )

    fields = complete_fake_fields("vendor_setup_w9_packet")
    approvals = complete_fake_approvals("vendor_setup_w9_packet")
    fields["tax_form_attachment"] = None
    approvals = [approval for approval in approvals if approval != "secure_attachment_check"]
    result = evaluate_send_readiness("vendor_setup_w9_packet", fields, approvals)
    return _summary([result])


def _scenario_record_level_blocker() -> dict[str, Any]:
    from locally_twisted.failure_recorder import record_health_failures
    from locally_twisted.outbound_documents.send_readiness import evaluate_send_readiness

    original_commit = frappe.db.commit
    original_log_error = frappe.log_error
    intercepted_commits = []
    log_error_calls = []

    def no_commit(*args, **kwargs):
        intercepted_commits.append(True)

    def fake_log_error(*args, **kwargs):
        log_error_calls.append({"args": args, "kwargs": kwargs})
        return f"ROLLBACK-ERROR-LOG-{len(log_error_calls)}"

    try:
        frappe.db.commit = no_commit
        frappe.log_error = fake_log_error
        token = str(int(time.time()))
        lead = _create_lead(f"LT Send Readiness {token}")
        result = evaluate_send_readiness(
            "quote_estimate",
            {"recipient": "buyer@example.invalid"},
            [],
            primary_doctype="Lead",
            primary_name=lead.name,
            record_blocker=True,
        )
        health = record_health_failures(primary_doctype="Lead", primary_name=lead.name)
        summary = _summary([result])
        summary.update(
            {
                "lead": lead.name,
                "record_health_failures": deepcopy(health),
                "log_error_calls_intercepted": len(log_error_calls),
                "commit_calls_intercepted": len(intercepted_commits),
                "rolled_back": True,
            }
        )
        return summary
    except Exception:
        return {"ok": False, "failures": [frappe.get_traceback()]}
    finally:
        frappe.db.commit = original_commit
        frappe.log_error = original_log_error
        frappe.db.rollback()


def _create_lead(marker: str):
    lead = frappe.get_doc(
        {
            "doctype": "Lead",
            "first_name": marker,
            "lead_name": marker,
            "email_id": f"{marker.lower().replace(' ', '-')}@example.invalid",
            "mobile_no": "801-555-0199",
            "status": "Open",
            "custom_pipeline_stage": "New Inquiry",
        }
    )
    lead.insert(ignore_permissions=True)
    return lead


def _summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    blocked = [result for result in results if result.get("send_ready") is not True]
    ready = [result for result in results if result.get("send_ready") is True]
    failures = [
        f"{result.get('document_id')}: {failure}"
        for result in results
        for failure in result.get("failures") or []
    ]
    return {
        "ok": not failures,
        "document_count": len(results),
        "send_ready_count": len(ready),
        "blocked_count": len(blocked),
        "documents": results,
        "failures": failures,
    }


def _expect_all_blocked(result: dict[str, Any]) -> list[str]:
    failures = _expect_result_ok(result)
    if result.get("blocked_count") != result.get("document_count"):
        failures.append("expected every document to be blocked without required fields")
    for document in result.get("documents") or []:
        blockers = document.get("blocked_send_until") or []
        for expected in (
            "required_field:recipient",
            "required_field:company_branding",
            "required_field:business_copy_recipient",
            "approval_gate:copy_routing_confirmed",
        ):
            if expected not in blockers:
                failures.append(f"{document.get('document_id')} missing blocker {expected}")
        forbidden = "required_field:external_audience_copy_recipient"
        if forbidden in blockers:
            failures.append(f"{document.get('document_id')} should not require standing Cameron copy blocker")
    return failures


def _expect_all_ready(result: dict[str, Any]) -> list[str]:
    failures = _expect_result_ok(result)
    if result.get("send_ready_count") != result.get("document_count"):
        failures.append("expected every complete fake document to be send-ready")
    for document in result.get("documents") or []:
        if document.get("send_allowed") is not True:
            failures.append(f"{document.get('document_id')} did not allow send when complete")
    return failures


def _expect_payment_path_blocked(result: dict[str, Any]) -> list[str]:
    failures = _expect_result_ok(result)
    document = _first_document(result)
    blockers = document.get("blocked_send_until") or []
    for expected in ("required_field:payment_path", "required_field:payment_link_if_available"):
        if expected not in blockers:
            failures.append(f"missing payment blocker {expected}")
    if document.get("send_ready") is not False:
        failures.append("payment reminder should not be send-ready without payment path")
    return failures


def _expect_vendor_blocked(result: dict[str, Any]) -> list[str]:
    failures = _expect_result_ok(result)
    document = _first_document(result)
    blockers = document.get("blocked_send_until") or []
    for expected in ("required_field:tax_form_attachment", "approval_gate:secure_attachment_check"):
        if expected not in blockers:
            failures.append(f"missing vendor blocker {expected}")
    return failures


def _expect_record_blocker(result: dict[str, Any]) -> list[str]:
    failures = _expect_result_ok(result)
    document = _first_document(result)
    evidence = document.get("record_blocker_evidence") or {}
    if document.get("send_ready") is not False:
        failures.append("record-level scenario should stay blocked")
    if evidence.get("ok") is not True:
        failures.append("record-level blocker evidence is not ok")
    if evidence.get("comment") is None:
        failures.append("record-level blocker did not create a Comment")
    health = result.get("record_health_failures") or []
    if not any(row.get("surface") == "outbound_document_send_readiness" for row in health):
        failures.append("record_health_failures did not include outbound document send-readiness")
    if result.get("log_error_calls_intercepted") != 1:
        failures.append("record-level blocker did not call frappe.log_error once")
    return failures


def _expect_result_ok(result: dict[str, Any]) -> list[str]:
    if result.get("ok") is not True:
        return [f"result not ok: {result.get('failures')}"]
    return []


def _first_document(result: dict[str, Any]) -> dict[str, Any]:
    return (result.get("documents") or [{}])[0]
