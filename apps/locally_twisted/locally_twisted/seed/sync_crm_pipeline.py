"""Sync the LT business-stage CRM board without repurposing Lead.status.

Run in-process:
  bench --site frontend execute locally_twisted.seed.sync_crm_pipeline.execute
"""
from __future__ import annotations

import json

import frappe


PIPELINE_FIELD = "custom_pipeline_stage"
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
PIPELINE_FIELD_SPEC = {
    "doctype": "Custom Field",
    "dt": "Lead",
    "fieldname": PIPELINE_FIELD,
    "label": "Where We Are",
    "fieldtype": "Select",
    "options": "\n".join(PIPELINE_OPTIONS),
    "default": "New Inquiry",
    "insert_after": "status",
    "in_standard_filter": 1,
    "in_list_view": 1,
}
STATUS_TO_PIPELINE = {
    "Lead": "New Inquiry",
    "Open": "New Inquiry",
    "Replied": "New Inquiry",
    "Interested": "New Inquiry",
    "Opportunity": "Quote Sent/Awaiting Approval",
    "Quotation": "Quote Sent/Awaiting Approval",
    "Lost Quotation": "Archive",
    "Converted": "Approved",
    "Do Not Contact": "Archive",
}


def execute() -> str:
    summary = sync()
    frappe.clear_cache(doctype="Lead")
    frappe.db.commit()
    print(json.dumps(summary, indent=2, sort_keys=True))
    return json.dumps(summary, sort_keys=True)


def sync() -> dict:
    summary = {
        "ensured_custom_fields": [],
        "updated_custom_fields": [],
        "removed_status_property_setters": [],
        "updated_leads": 0,
        "ensured_kanban_boards": [],
    }
    _remove_lt_status_property_setters(summary)
    _ensure_pipeline_custom_field(summary)
    frappe.clear_cache(doctype="Lead")
    summary["updated_leads"] = _normalize_existing_leads()
    _ensure_inquiry_kanban_board(summary)
    return summary


def _remove_lt_status_property_setters(summary: dict) -> None:
    setters = frappe.get_all(
        "Property Setter",
        filters={"doc_type": "Lead", "field_name": "status", "property": "options"},
        fields=["name", "value"],
        limit_page_length=100,
    )
    desired = "\n".join(PIPELINE_OPTIONS)
    for setter in setters:
        if (setter.value or "") != desired:
            continue
        frappe.delete_doc("Property Setter", setter.name, ignore_permissions=True)
        summary["removed_status_property_setters"].append(setter.name)


def _ensure_pipeline_custom_field(summary: dict) -> None:
    name = frappe.db.get_value(
        "Custom Field",
        {"dt": "Lead", "fieldname": PIPELINE_FIELD},
        "name",
    )
    if not name:
        frappe.get_doc(PIPELINE_FIELD_SPEC).insert(ignore_permissions=True)
        summary["ensured_custom_fields"].append(PIPELINE_FIELD)
        return

    doc = frappe.get_doc("Custom Field", name)
    changed = _set_fields(doc, {k: v for k, v in PIPELINE_FIELD_SPEC.items() if k != "doctype"})
    if changed:
        doc.save(ignore_permissions=True)
        summary["updated_custom_fields"].append(PIPELINE_FIELD)


def _normalize_existing_leads() -> int:
    updated = 0
    allowed = set(PIPELINE_OPTIONS)
    for lead in frappe.get_all(
        "Lead",
        fields=["name", "status", PIPELINE_FIELD],
        limit_page_length=10000,
    ):
        current = lead.get(PIPELINE_FIELD)
        if current in allowed:
            continue
        desired = STATUS_TO_PIPELINE.get(lead.status, "New Inquiry")
        frappe.db.set_value(
            "Lead",
            lead.name,
            PIPELINE_FIELD,
            desired,
            update_modified=False,
        )
        updated += 1
    return updated


def _ensure_inquiry_kanban_board(summary: dict) -> None:
    prior_orders = {}
    if frappe.db.exists("Kanban Board", "LT Inquiry Board"):
        doc = frappe.get_doc("Kanban Board", "LT Inquiry Board")
        prior_orders = {
            row.column_name: row.order
            for row in doc.columns
            if row.order
        }
        is_new = False
    else:
        doc = frappe.get_doc({
            "doctype": "Kanban Board",
            "name": "LT Inquiry Board",
            "kanban_board_name": "LT Inquiry Board",
        })
        is_new = True

    changed = False
    fields = {
        "kanban_board_name": "LT Inquiry Board",
        "reference_doctype": "Lead",
        "field_name": PIPELINE_FIELD,
        "private": 0,
        "show_labels": 1,
        "filters": None,
        "fields": None,
    }
    changed = _set_fields(doc, fields) or changed

    desired_rows = []
    for column_name, indicator, status in PIPELINE_COLUMNS:
        order = prior_orders.get(column_name)
        if column_name == "New Inquiry":
            order = order or prior_orders.get("Open")
        desired_rows.append({
            "column_name": column_name,
            "indicator": indicator,
            "status": status,
            "order": order or "[]",
        })

    current_rows = [
        {
            "column_name": row.column_name,
            "indicator": row.indicator,
            "status": row.status,
            "order": row.order,
        }
        for row in doc.columns
    ]
    if current_rows != desired_rows:
        doc.set("columns", [])
        for row in desired_rows:
            doc.append("columns", row)
        changed = True

    if is_new:
        doc.insert(ignore_permissions=True)
        summary["ensured_kanban_boards"].append("LT Inquiry Board")
    elif changed:
        doc.save(ignore_permissions=True)
        summary["ensured_kanban_boards"].append("LT Inquiry Board")


def _set_fields(doc, fields: dict) -> bool:
    changed = False
    for key, value in fields.items():
        if getattr(doc, key, None) != value:
            setattr(doc, key, value)
            changed = True
    return changed
