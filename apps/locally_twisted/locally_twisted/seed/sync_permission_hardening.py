"""Harden LT-owned custom DocType permissions.

Run in-process:
  bench --site frontend execute locally_twisted.seed.sync_permission_hardening.execute
"""
from __future__ import annotations

import json

import frappe

from locally_twisted.seed.sync_contact_intake_backend import (
    PERMISSION_FIELDS,
    SERVICE_TYPE_PERMISSIONS,
    _normalized_permission_row,
    _permission_row,
)


DASHBOARD_REVIEWED_ITEM_PERMISSIONS = [
    _permission_row(
        "System Manager",
        read=1,
        write=1,
        create=1,
        delete=1,
        report=1,
        export=1,
        share=1,
        print=1,
        email=1,
    ),
]

HARDENED_DOCTYPE_PERMISSIONS = {
    "LT Service Type": SERVICE_TYPE_PERMISSIONS,
    "Dashboard Reviewed Item": DASHBOARD_REVIEWED_ITEM_PERMISSIONS,
}


def execute(commit: bool = True) -> str:
    summary = {
        "hardened_doctype_permissions": [],
        "missing_optional_doctypes": [],
    }
    for doctype_name, permission_rows in HARDENED_DOCTYPE_PERMISSIONS.items():
        if not frappe.db.exists("DocType", doctype_name):
            summary["missing_optional_doctypes"].append(doctype_name)
            continue
        _sync_doctype_permissions(doctype_name, permission_rows, summary)

    if commit:
        frappe.db.commit()
    print(json.dumps(summary, indent=2, sort_keys=True))
    return json.dumps(summary, sort_keys=True)


def _sync_doctype_permissions(
    doctype_name: str,
    permission_rows: list[dict[str, int | str]],
    summary: dict,
) -> None:
    doc = frappe.get_doc("DocType", doctype_name)
    current = [_normalized_permission_row(row.as_dict()) for row in doc.permissions]
    desired = [_normalized_permission_row(row) for row in permission_rows]
    if current == desired:
        return

    doc.set("permissions", [])
    for row in permission_rows:
        clean = {key: value for key, value in row.items() if key == "role" or key in PERMISSION_FIELDS}
        doc.append("permissions", clean)
    doc.save(ignore_permissions=True)
    frappe.clear_cache(doctype=doctype_name)
    summary["hardened_doctype_permissions"].append(doctype_name)
