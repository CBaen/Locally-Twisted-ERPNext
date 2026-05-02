"""Sync Task fields required by LT CRM stage cascades.

Run in-process:
  bench --site frontend execute locally_twisted.seed.sync_stage_cascade.execute
"""
from __future__ import annotations

import json

import frappe

from locally_twisted.crm_pipeline import PIPELINE_OPTIONS
from locally_twisted.stage_cascade import LEAD_TASK_FIELD, TASK_KEY_FIELD, TASK_STAGE_FIELD


TASK_CUSTOM_FIELDS = {
    LEAD_TASK_FIELD: {
        "doctype": "Custom Field",
        "dt": "Task",
        "fieldname": LEAD_TASK_FIELD,
        "label": "Inquiry",
        "fieldtype": "Link",
        "options": "Lead",
        "insert_after": "subject",
        "in_standard_filter": 1,
        "in_list_view": 1,
    },
    TASK_STAGE_FIELD: {
        "doctype": "Custom Field",
        "dt": "Task",
        "fieldname": TASK_STAGE_FIELD,
        "label": "Inquiry Stage",
        "fieldtype": "Select",
        "options": "\n".join(PIPELINE_OPTIONS),
        "insert_after": LEAD_TASK_FIELD,
        "in_standard_filter": 1,
        "in_list_view": 1,
    },
    TASK_KEY_FIELD: {
        "doctype": "Custom Field",
        "dt": "Task",
        "fieldname": TASK_KEY_FIELD,
        "label": "LT Cascade Key",
        "fieldtype": "Data",
        "insert_after": TASK_STAGE_FIELD,
        "hidden": 1,
        "read_only": 1,
        "no_copy": 1,
    },
}


def execute() -> str:
    summary = sync()
    frappe.clear_cache(doctype="Task")
    frappe.db.commit()
    print(json.dumps(summary, indent=2, sort_keys=True))
    return json.dumps(summary, sort_keys=True)


def sync() -> dict:
    summary = {
        "ensured_custom_fields": [],
        "updated_custom_fields": [],
    }
    for fieldname, spec in TASK_CUSTOM_FIELDS.items():
        _ensure_custom_field(fieldname, spec, summary)
    return summary


def _ensure_custom_field(fieldname: str, spec: dict, summary: dict) -> None:
    name = frappe.db.get_value(
        "Custom Field",
        {"dt": spec["dt"], "fieldname": fieldname},
        "name",
    )
    if not name:
        frappe.get_doc(spec).insert(ignore_permissions=True)
        summary["ensured_custom_fields"].append(fieldname)
        return

    doc = frappe.get_doc("Custom Field", name)
    changed = False
    for key, value in spec.items():
        if key == "doctype":
            continue
        if getattr(doc, key, None) != value:
            setattr(doc, key, value)
            changed = True
    if changed:
        doc.save(ignore_permissions=True)
        summary["updated_custom_fields"].append(fieldname)
