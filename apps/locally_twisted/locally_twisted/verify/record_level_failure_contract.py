"""Record-level failure contract for LT fail-loud backend hardening.

This verifier proves that partial backend failures leave durable evidence on
the affected business record. It uses fake records, intercepts commits, and
rolls the transaction back.
"""
from __future__ import annotations

import time

import frappe


class ContractFail(Exception):
    pass


def run() -> dict[str, object]:
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
        result = _run_contract(log_error_calls)
        result["commit_calls_intercepted"] = len(intercepted_commits)
        result["log_error_calls_intercepted"] = len(log_error_calls)
        result["rolled_back"] = True
        return result
    except ContractFail as exc:
        return {"ok": False, "failures": [str(exc)]}
    except Exception:
        return {"ok": False, "failures": [frappe.get_traceback()]}
    finally:
        frappe.db.commit = original_commit
        frappe.log_error = original_log_error
        frappe.db.rollback()


def _run_contract(log_error_calls: list[dict[str, object]]) -> dict[str, object]:
    from locally_twisted.failure_recorder import (
        FAILURE_COMMENT_PREFIX,
        record_backend_failure,
        record_backend_failure_resolution,
        record_health_failures,
    )

    token = str(int(time.time()))
    marker = f"LT Failure Recorder {token}"
    lead = _create_lead(marker)
    grouping_key = f"record_level_failure_contract:lead_contact_dedup:{lead.name}"

    before = _counts()
    evidence = record_backend_failure(
        surface="record_level_failure_contract",
        step="lead_contact_dedup",
        severity="error",
        primary_doctype="Lead",
        primary_name=lead.name,
        customer_visible_impact="Customer inquiry was received, but Contact linking failed.",
        internal_next_action="Review the Lead and link/create the Contact before follow-up.",
        exception=ValueError("synthetic contact dedup failure"),
        grouping_key=grouping_key,
    )
    after = _counts()

    failures = []
    if not evidence.get("ok"):
        failures.append(f"record_backend_failure returned not-ok: {evidence!r}")
    if evidence.get("primary") != f"Lead:{lead.name}":
        failures.append("recorder evidence did not identify the primary Lead")
    if after["Comment"] - before["Comment"] != 1:
        failures.append("recorder did not create exactly one record-level Comment")
    if len(log_error_calls) != 1:
        failures.append(f"recorder should call frappe.log_error exactly once, found {len(log_error_calls)}")

    comment = _latest_comment("Lead", lead.name)
    if not comment:
        failures.append("Lead has no failure Comment")
    else:
        content = comment.get("content") or ""
        for expected in (
            FAILURE_COMMENT_PREFIX,
            "record_level_failure_contract",
            "lead_contact_dedup",
            "Review the Lead and link/create the Contact before follow-up.",
        ):
            if expected not in content:
                failures.append(f"Lead failure Comment missing {expected!r}")

    health = record_health_failures()
    matching = [
        row
        for row in health
        if row.get("primary_doctype") == "Lead"
        and row.get("primary_name") == lead.name
        and row.get("step") == "lead_contact_dedup"
    ]
    if not matching:
        failures.append("record_health_failures did not report the synthetic Lead blocker")

    if failures:
        raise ContractFail("; ".join(failures))

    resolution = record_backend_failure_resolution(
        primary_doctype="Lead",
        primary_name=lead.name,
        surface="record_level_failure_contract",
        step="lead_contact_dedup",
        grouping_key=grouping_key,
        resolution_note="Synthetic failure reviewed during rollback contract.",
    )
    if not resolution.get("ok"):
        raise ContractFail(f"failure resolution returned not-ok: {resolution!r}")

    resolved_health = record_health_failures(primary_doctype="Lead", primary_name=lead.name)
    still_open = [row for row in resolved_health if row.get("grouping_key") == grouping_key]
    if still_open:
        raise ContractFail("record_health_failures still reported a resolved synthetic blocker")

    _assert_limited_health_keeps_older_unresolved_failure()

    return {
        "ok": True,
        "lead": lead.name,
        "comment": comment.get("name") if comment else None,
        "resolution_comment": resolution.get("comment"),
        "record_health_failures": len(health),
        "record_health_failures_after_resolution": len(resolved_health),
    }


def _assert_limited_health_keeps_older_unresolved_failure() -> None:
    from locally_twisted.failure_recorder import (
        record_backend_failure,
        record_backend_failure_resolution,
        record_health_failures,
    )

    token = str(int(time.time() * 1000))
    lead = _create_lead(f"LT Failure Limit {token}")
    older_key = f"record_level_failure_contract:older_unresolved:{lead.name}"
    newer_key = f"record_level_failure_contract:newer_resolved:{lead.name}"

    record_backend_failure(
        surface="record_level_failure_contract",
        step="older_unresolved",
        severity="error",
        primary_doctype="Lead",
        primary_name=lead.name,
        customer_visible_impact="Customer inquiry is waiting on a backend follow-up.",
        internal_next_action="This older synthetic blocker should stay visible in limited health reports.",
        exception=ValueError("synthetic older unresolved failure"),
        grouping_key=older_key,
    )
    time.sleep(0.01)
    record_backend_failure(
        surface="record_level_failure_contract",
        step="newer_resolved",
        severity="error",
        primary_doctype="Lead",
        primary_name=lead.name,
        customer_visible_impact="Customer inquiry briefly hit a backend follow-up issue.",
        internal_next_action="This newer synthetic blocker is resolved and should not hide older failures.",
        exception=ValueError("synthetic newer resolved failure"),
        grouping_key=newer_key,
    )
    record_backend_failure_resolution(
        primary_doctype="Lead",
        primary_name=lead.name,
        surface="record_level_failure_contract",
        step="newer_resolved",
        grouping_key=newer_key,
        resolution_note="Synthetic newer failure resolved during rollback contract.",
    )

    limited_health = record_health_failures(primary_doctype="Lead", primary_name=lead.name, limit=1)
    grouping_keys = [row.get("grouping_key") for row in limited_health]
    if older_key not in grouping_keys:
        raise ContractFail(
            "record_health_failures(limit=1) hid an older unresolved blocker after filtering "
            f"a newer resolved blocker; got {grouping_keys}"
        )


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


def _counts() -> dict[str, int]:
    return {
        doctype: int(frappe.db.count(doctype))
        for doctype in ("Comment", "Error Log")
        if frappe.db.exists("DocType", doctype)
    }


def _latest_comment(reference_doctype: str, reference_name: str):
    rows = frappe.get_all(
        "Comment",
        filters={
            "reference_doctype": reference_doctype,
            "reference_name": reference_name,
        },
        fields=["name", "content", "creation"],
        order_by="creation desc",
        limit=1,
    )
    return rows[0] if rows else None
