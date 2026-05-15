"""Sync website-only external marketing review access.

Run in-process:
  bench --site frontend execute locally_twisted.seed.sync_marketing_review_access.execute
"""
from __future__ import annotations

import json

import frappe

from locally_twisted.marketing_review_access import MARKETING_REVIEW_ROLE, marketing_role_boundary


def execute(commit: bool = True) -> str:
    summary = {
        "ensured_role": False,
        "removed_docperm_rows": [],
        "boundary_ok": False,
        "boundary_failures": [],
        "committed": False,
    }

    _ensure_role(summary)
    _remove_role_docperms(summary)

    boundary = marketing_role_boundary()
    summary["boundary_ok"] = bool(boundary.get("ok"))
    summary["boundary_failures"] = boundary.get("failures") or []

    frappe.clear_cache()
    if commit:
        frappe.db.commit()
        summary["committed"] = True

    print(json.dumps(summary, indent=2, sort_keys=True))
    return json.dumps(summary, sort_keys=True)


def _ensure_role(summary: dict) -> None:
    fields = {
        "role_name": MARKETING_REVIEW_ROLE,
        "desk_access": 0,
        "disabled": 0,
    }
    if frappe.db.exists("Role", MARKETING_REVIEW_ROLE):
        doc = frappe.get_doc("Role", MARKETING_REVIEW_ROLE)
        changed = False
        for fieldname, value in fields.items():
            if doc.get(fieldname) != value:
                doc.set(fieldname, value)
                changed = True
        if changed:
            doc.save(ignore_permissions=True)
            summary["ensured_role"] = True
        return

    frappe.get_doc({"doctype": "Role", **fields}).insert(ignore_permissions=True)
    summary["ensured_role"] = True


def _remove_role_docperms(summary: dict) -> None:
    rows = frappe.get_all(
        "DocPerm",
        filters={"role": MARKETING_REVIEW_ROLE},
        fields=["name", "parent"],
        limit_page_length=500,
    )
    for row in rows:
        frappe.delete_doc("DocPerm", row.name, ignore_permissions=True)
        summary["removed_docperm_rows"].append(row.parent)
