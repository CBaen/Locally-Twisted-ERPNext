#!/usr/bin/env python3
"""Verify LT CRM stage changes create safe operational follow-up tasks."""
from __future__ import annotations

import json
import subprocess
import sys
import time
from typing import Any


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"

TASK_FIELDS = {
    "custom_lt_lead": {"label": "Inquiry", "fieldtype": "Link", "options": "Lead"},
    "custom_pipeline_stage": {"label": "Inquiry Stage", "fieldtype": "Select"},
    "custom_lt_cascade_key": {"label": "LT Cascade Key", "fieldtype": "Data"},
}
PIPELINE_STAGES = [
    "New Inquiry",
    "Quote Sent/Awaiting Approval",
    "Approved",
    "In Production",
    "Event/Post Event",
    "Archive",
]
EXPECTED_STAGE_TASKS = {
    "New Inquiry": "Reply to new inquiry",
    "Quote Sent/Awaiting Approval": "Follow up on quote",
    "Approved": "Confirm booking details",
    "In Production": "Prepare event production plan",
    "Event/Post Event": "Send post-event follow-up",
}
FINANCIAL_DOCTYPES = ("Sales Order", "Sales Invoice", "Payment Request")


def bench_execute(
    method: str,
    *,
    args: list[Any] | None = None,
    kwargs: dict[str, Any] | None = None,
) -> Any:
    cmd = [
        "docker",
        "exec",
        CONTAINER,
        "bench",
        "--site",
        SITE,
        "execute",
        method,
    ]
    if args is not None:
        cmd.extend(["--args", json.dumps(args)])
    if kwargs is not None:
        cmd.extend(["--kwargs", json.dumps(kwargs)])

    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=60)
    if proc.returncode != 0:
        raise RuntimeError(
            f"bench execute failed for {method}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    text = proc.stdout.strip()
    if not text:
        return None
    return json.loads(text)


def get_all(doctype: str, **kwargs: Any) -> list[dict[str, Any]]:
    return bench_execute("frappe.get_all", args=[doctype], kwargs=kwargs) or []


def insert_doc(doc: dict[str, Any]) -> dict[str, Any]:
    return bench_execute("frappe.client.insert", kwargs={"doc": doc})


def set_value(doctype: str, name: str, fieldname: str, value: Any) -> dict[str, Any]:
    return bench_execute(
        "frappe.client.set_value",
        kwargs={"doctype": doctype, "name": name, "fieldname": fieldname, "value": value},
    )


def delete_doc(doctype: str, name: str) -> None:
    bench_execute(
        "frappe.delete_doc",
        args=[doctype, name],
        kwargs={"ignore_permissions": 1, "force": 1},
    )


def check_task_custom_fields() -> list[str]:
    failures = []
    rows = get_all(
        "Custom Field",
        filters={"dt": "Task", "fieldname": ["in", list(TASK_FIELDS)]},
        fields=["fieldname", "label", "fieldtype", "options"],
        limit_page_length=20,
    )
    by_fieldname = {row["fieldname"]: row for row in rows}
    for fieldname, expected in TASK_FIELDS.items():
        row = by_fieldname.get(fieldname)
        if not row:
            failures.append(f"Task Custom Field missing: {fieldname}")
            continue
        for key, value in expected.items():
            if row.get(key) != value:
                failures.append(f"Task.{fieldname}.{key} expected {value!r}, found {row.get(key)!r}")

    stage_row = by_fieldname.get("custom_pipeline_stage")
    if stage_row and (stage_row.get("options") or "").splitlines() != PIPELINE_STAGES:
        failures.append(
            "Task.custom_pipeline_stage options do not match CRM stages: "
            f"{stage_row.get('options')!r}"
        )
    return failures


def check_hook_source() -> list[str]:
    source = open("apps/locally_twisted/locally_twisted/hooks.py", encoding="utf-8").read()
    lead_source = open("apps/locally_twisted/locally_twisted/lead_cascade.py", encoding="utf-8").read()
    failures = []
    if '"on_update": "locally_twisted.stage_cascade.on_update"' not in source:
        failures.append("hooks.py does not wire Lead.on_update to stage_cascade.on_update")
    if "stage_cascade.after_insert(doc)" not in lead_source:
        failures.append("lead_cascade.after_insert does not call stage_cascade.after_insert")
    return failures


def count_docs() -> dict[str, int]:
    counts = {}
    for doctype in FINANCIAL_DOCTYPES:
        rows = get_all(doctype, fields=["name"], limit_page_length=100000)
        counts[doctype] = len(rows)
    return counts


def tasks_for_lead(lead_name: str) -> list[dict[str, Any]]:
    return get_all(
        "Task",
        filters={"custom_lt_lead": lead_name},
        fields=["name", "subject", "status", "custom_pipeline_stage", "custom_lt_cascade_key"],
        order_by="creation asc",
        limit_page_length=100,
    )


def check_live_stage_cascade() -> list[str]:
    failures = []
    marker = f"CASCADE-TEST-{int(time.time())}"
    lead_name = None
    financial_before = count_docs()

    try:
        lead = insert_doc(
            {
                "doctype": "Lead",
                "first_name": marker,
                "lead_name": marker,
                "email_id": f"{marker.lower()}@example.invalid",
                "status": "Open",
                "custom_pipeline_stage": "New Inquiry",
            }
        )
        lead_name = lead["name"]

        failures.extend(_expect_stage_task(lead_name, "New Inquiry", should_be_open=True))

        set_value("Lead", lead_name, "custom_pipeline_stage", "Quote Sent/Awaiting Approval")
        failures.extend(_expect_stage_task(lead_name, "New Inquiry", should_be_open=False))
        failures.extend(_expect_stage_task(lead_name, "Quote Sent/Awaiting Approval", should_be_open=True))

        set_value("Lead", lead_name, "custom_pipeline_stage", "Approved")
        set_value("Lead", lead_name, "custom_pipeline_stage", "In Production")
        failures.extend(_expect_stage_task(lead_name, "Quote Sent/Awaiting Approval", should_be_open=False))
        failures.extend(_expect_stage_task(lead_name, "Approved", should_be_open=False))
        failures.extend(_expect_stage_task(lead_name, "In Production", should_be_open=True))

        set_value("Lead", lead_name, "custom_pipeline_stage", "Archive")
        open_tasks = [task for task in tasks_for_lead(lead_name) if task.get("status") not in {"Completed", "Cancelled"}]
        if open_tasks:
            failures.append(
                f"Archive should close open cascade tasks, found open tasks: "
                f"{[(task['subject'], task['status']) for task in open_tasks]!r}"
            )

        financial_after = count_docs()
        if financial_after != financial_before:
            failures.append(
                f"Stage cascade changed financial document counts; before {financial_before!r}, "
                f"after {financial_after!r}"
            )
    finally:
        cleanup_test_records(lead_name, marker)

    return failures


def _expect_stage_task(lead_name: str, stage: str, *, should_be_open: bool) -> list[str]:
    failures = []
    expected_subject = EXPECTED_STAGE_TASKS[stage]
    matching = [
        task for task in tasks_for_lead(lead_name)
        if task.get("custom_pipeline_stage") == stage
    ]
    if not matching:
        return [f"Missing cascade Task for {lead_name} stage {stage!r}"]

    task = matching[0]
    if not (task.get("subject") or "").startswith(expected_subject):
        failures.append(
            f"{stage!r} task subject expected to start {expected_subject!r}, found {task.get('subject')!r}"
        )
    is_open = task.get("status") not in {"Completed", "Cancelled"}
    if should_be_open and not is_open:
        failures.append(f"{stage!r} cascade Task should be open, found status {task.get('status')!r}")
    if not should_be_open and is_open:
        failures.append(f"{stage!r} cascade Task should be completed/closed, found {task.get('status')!r}")
    return failures


def cleanup_test_records(lead_name: str | None, marker: str) -> None:
    if lead_name:
        for task in tasks_for_lead(lead_name):
            _safe_delete("Task", task["name"])
        for link in get_all(
            "Dynamic Link",
            filters={"link_doctype": "Lead", "link_name": lead_name},
            fields=["parent"],
            limit_page_length=100,
        ):
            _safe_delete("Contact", link["parent"])
        for communication in get_all(
            "Communication",
            filters={"reference_doctype": "Lead", "reference_name": lead_name},
            fields=["name"],
            limit_page_length=100,
        ):
            _safe_delete("Communication", communication["name"])
        _safe_delete("Lead", lead_name)

    for lead in get_all(
        "Lead",
        filters={"first_name": marker},
        fields=["name"],
        limit_page_length=20,
    ):
        _safe_delete("Lead", lead["name"])


def _safe_delete(doctype: str, name: str) -> None:
    try:
        delete_doc(doctype, name)
    except Exception:
        pass


def main() -> int:
    failures = []
    failures.extend(check_task_custom_fields())
    failures.extend(check_hook_source())
    if not failures:
        failures.extend(check_live_stage_cascade())

    if failures:
        print("[CRM STAGE CASCADE] FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("[CRM STAGE CASCADE] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
