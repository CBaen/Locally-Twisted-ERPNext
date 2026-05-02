#!/usr/bin/env python3
"""Verify LT's CRM board uses a custom business-stage field.

The Odoo-approved stage names are allowed to drive Jeff's Kanban board.
ERPNext's native Lead.status must remain available for ERPNext internals.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"

PIPELINE_FIELD = "custom_pipeline_stage"
PIPELINE_LABEL = "Where We Are"
PIPELINE_OPTIONS = [
    "New Inquiry",
    "Quote Sent/Awaiting Approval",
    "Approved",
    "In Production",
    "Event/Post Event",
    "Archive",
]
PIPELINE_COLUMNS = [
    ("New Inquiry", "Blue", "Active"),
    ("Quote Sent/Awaiting Approval", "Cyan", "Active"),
    ("Approved", "Green", "Active"),
    ("In Production", "Orange", "Active"),
    ("Event/Post Event", "Purple", "Active"),
    ("Archive", "Gray", "Archived"),
]
STALE_BOARD_COLUMNS = {
    "Lead",
    "Open",
    "Replied",
    "Interested",
    "Converted",
    "Do Not Contact",
}
STANDARD_STATUS_REQUIRED = {"Lead", "Open", "Converted", "Do Not Contact"}


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


def get_list(doctype: str, **kwargs: Any) -> list[dict[str, Any]]:
    return bench_execute("frappe.client.get_list", kwargs={"doctype": doctype, **kwargs}) or []


def get_all(doctype: str, **kwargs: Any) -> list[dict[str, Any]]:
    return bench_execute("frappe.get_all", args=[doctype], kwargs=kwargs) or []


def get_doc(doctype: str, name: str) -> dict[str, Any]:
    return bench_execute("frappe.client.get", kwargs={"doctype": doctype, "name": name})


def try_get_doc(doctype: str, name: str) -> dict[str, Any] | None:
    try:
        return get_doc(doctype, name)
    except RuntimeError as exc:
        if "DoesNotExistError" in str(exc):
            return None
        raise


def check_pipeline_custom_field() -> list[str]:
    failures = []
    rows = get_list(
        "Custom Field",
        filters={"dt": "Lead", "fieldname": PIPELINE_FIELD},
        fields=[
            "fieldname",
            "label",
            "fieldtype",
            "options",
            "default",
            "insert_after",
            "in_standard_filter",
            "in_list_view",
        ],
        limit_page_length=5,
    )
    if not rows:
        return [f"Lead Custom Field missing: {PIPELINE_FIELD}"]

    row = rows[0]
    expected = {
        "label": PIPELINE_LABEL,
        "fieldtype": "Select",
        "options": "\n".join(PIPELINE_OPTIONS),
        "default": "New Inquiry",
        "in_standard_filter": 1,
        "in_list_view": 1,
    }
    for key, value in expected.items():
        if row.get(key) != value:
            failures.append(f"{PIPELINE_FIELD}.{key} expected {value!r}, found {row.get(key)!r}")
    return failures


def check_standard_status_is_preserved() -> list[str]:
    failures = []
    rows = get_all(
        "DocField",
        filters={"parent": "Lead", "fieldname": "status"},
        fields=["options"],
        limit_page_length=1,
    )
    if not rows:
        return ["Lead.status DocField missing"]
    options = set((rows[0].get("options") or "").splitlines())
    missing = sorted(STANDARD_STATUS_REQUIRED - options)
    if missing:
        failures.append(f"Lead.status missing standard ERPNext options: {', '.join(missing)}")

    property_setters = get_all(
        "Property Setter",
        filters={
            "doc_type": "Lead",
            "field_name": "status",
            "property": "options",
        },
        fields=["name", "value"],
        limit_page_length=20,
    )
    for setter in property_setters:
        value = setter.get("value") or ""
        overlap = sorted(set(PIPELINE_OPTIONS) & set(value.splitlines()))
        if overlap:
            failures.append(
                f"Lead.status Property Setter {setter['name']} contains LT pipeline values: "
                f"{', '.join(overlap)}"
            )
    return failures


def check_inquiry_board() -> list[str]:
    failures = []
    board = try_get_doc("Kanban Board", "LT Inquiry Board")
    if not board:
        return ["Kanban Board missing: LT Inquiry Board"]

    if board.get("reference_doctype") != "Lead":
        failures.append(
            f"LT Inquiry Board reference_doctype expected 'Lead', found {board.get('reference_doctype')!r}"
        )
    if board.get("field_name") != PIPELINE_FIELD:
        failures.append(
            f"LT Inquiry Board field_name expected {PIPELINE_FIELD!r}, found {board.get('field_name')!r}"
        )

    columns = [
        (row.get("column_name"), row.get("indicator"), row.get("status"))
        for row in board.get("columns", [])
    ]
    if columns != PIPELINE_COLUMNS:
        failures.append(f"LT Inquiry Board columns expected {PIPELINE_COLUMNS!r}, found {columns!r}")

    stale = sorted(STALE_BOARD_COLUMNS & {name for name, _indicator, _status in columns})
    if stale:
        failures.append(f"LT Inquiry Board still has stale ERPNext status columns: {', '.join(stale)}")
    return failures


def check_existing_lead_values() -> list[str]:
    failures = []
    if get_list(
        "Custom Field",
        filters={"dt": "Lead", "fieldname": PIPELINE_FIELD},
        fields=["name"],
        limit_page_length=1,
    ) == []:
        return failures

    rows = get_list(
        "Lead",
        fields=["name", PIPELINE_FIELD],
        limit_page_length=10000,
        order_by="name asc",
    )
    allowed = set(PIPELINE_OPTIONS)
    blank = [row["name"] for row in rows if not row.get(PIPELINE_FIELD)]
    invalid = [
        f"{row['name']}={row.get(PIPELINE_FIELD)!r}"
        for row in rows
        if row.get(PIPELINE_FIELD) and row.get(PIPELINE_FIELD) not in allowed
    ]
    if blank:
        failures.append(f"Leads missing {PIPELINE_FIELD}: {', '.join(blank[:10])}")
    if invalid:
        failures.append(f"Leads with invalid {PIPELINE_FIELD}: {', '.join(invalid[:10])}")
    return failures


def check_public_intake_mapping() -> list[str]:
    source = Path("apps/locally_twisted/locally_twisted/www/book.py").read_text(encoding="utf-8")
    if '"custom_pipeline_stage": "New Inquiry"' not in source:
        return ["submit_book_inquiry does not set Lead.custom_pipeline_stage to New Inquiry"]
    return []


def main() -> int:
    failures = []
    failures.extend(check_pipeline_custom_field())
    failures.extend(check_standard_status_is_preserved())
    failures.extend(check_inquiry_board())
    failures.extend(check_existing_lead_values())
    failures.extend(check_public_intake_mapping())

    if failures:
        print("[CRM PIPELINE PARITY] FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("[CRM PIPELINE PARITY] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
