"""Sync Lead/CRM backend metadata to the current public contact intake.

Run in-process:
  bench --site frontend execute locally_twisted.seed.sync_contact_intake_backend.execute
"""
from __future__ import annotations

import json

import frappe


EXPECTED_SERVICES = [
    "Balloon Decor",
    "Balloon Twisting",
    "Face Painting",
    "Delivery",
    "Pickup",
    "Events Inquiry",
    "Something Else",
]

SERVICE_RENAMES = {
    "Delivery Only": "Delivery",
    "Event Package": "Events Inquiry",
}


def _selected(values: list[str]) -> str:
    quoted = ",".join(f"'{value}'" for value in values)
    return (
        "eval:doc.custom_event_type && doc.custom_event_type.some(function(r){"
        f"return [{quoted}].indexOf(r.service_type) !== -1;"
        "})"
    )


CUSTOM_FIELD_UPDATES = {
    "custom_event_type": {"label": "Services Requested"},
    "lt_section_delivery": {
        "label": "Delivery Details",
        "depends_on": _selected(["Delivery"]),
    },
    "lt_section_package": {
        "label": "Events Inquiry Details",
        "depends_on": _selected(["Events Inquiry"]),
    },
    "custom_package_notes": {
        "label": "Events Inquiry Notes",
        "depends_on": _selected(["Events Inquiry"]),
    },
    "lt_section_environment": {
        "label": "Event Environment",
        "depends_on": _selected(["Balloon Twisting", "Face Painting"]),
    },
    "custom_shade_required": {
        "label": "Shade Required",
        "depends_on": _selected(["Balloon Twisting", "Face Painting"]),
    },
    "custom_decor_notes": {
        "label": "Decor Notes",
        "depends_on": _selected(["Balloon Decor"]),
    },
    "custom_other_notes": {
        "label": "Something Else Notes",
        "depends_on": _selected(["Something Else"]),
    },
    "custom_event_time": {"depends_on": None},
    "custom_event_end_time": {"depends_on": None},
    "custom_guest_count": {"depends_on": None},
}


def execute() -> str:
    summary = {
        "renamed_services": [],
        "ensured_services": [],
        "updated_custom_fields": [],
        "updated_leads": 0,
    }
    _sync_service_types(summary)
    _sync_lead_custom_fields(summary)
    summary["updated_leads"] = _rewrite_existing_lead_service_csv()
    frappe.clear_cache(doctype="Lead")
    frappe.db.commit()
    print(json.dumps(summary, indent=2, sort_keys=True))
    return json.dumps(summary, sort_keys=True)


def _sync_service_types(summary: dict) -> None:
    for old, new in SERVICE_RENAMES.items():
        if not frappe.db.exists("LT Service Type", old):
            continue
        if frappe.db.exists("LT Service Type", new):
            frappe.rename_doc(
                "LT Service Type",
                old,
                new,
                force=True,
                merge=True,
                show_alert=False,
            )
        else:
            frappe.rename_doc(
                "LT Service Type",
                old,
                new,
                force=True,
                show_alert=False,
            )
        summary["renamed_services"].append({"from": old, "to": new})

    for service in EXPECTED_SERVICES:
        if frappe.db.exists("LT Service Type", service):
            doc = frappe.get_doc("LT Service Type", service)
            if doc.service_type != service:
                doc.service_type = service
                doc.save(ignore_permissions=True)
            continue
        doc = frappe.get_doc({
            "doctype": "LT Service Type",
            "service_type": service,
        })
        doc.name = service
        doc.insert(ignore_permissions=True)
        summary["ensured_services"].append(service)


def _sync_lead_custom_fields(summary: dict) -> None:
    for fieldname, updates in CUSTOM_FIELD_UPDATES.items():
        name = frappe.db.get_value(
            "Custom Field",
            {"dt": "Lead", "fieldname": fieldname},
            "name",
        )
        if not name:
            raise RuntimeError(f"Lead Custom Field missing: {fieldname}")
        doc = frappe.get_doc("Custom Field", name)
        changed = False
        for key, value in updates.items():
            if getattr(doc, key) != value:
                setattr(doc, key, value)
                changed = True
        if changed:
            doc.save(ignore_permissions=True)
            summary["updated_custom_fields"].append(fieldname)


def _rewrite_existing_lead_service_csv() -> int:
    updated = 0
    for lead in frappe.get_all(
        "Lead",
        filters={"custom_services": ["is", "set"]},
        fields=["name", "custom_services"],
        limit_page_length=10000,
    ):
        current = lead.custom_services or ""
        revised = current
        for old, new in SERVICE_RENAMES.items():
            revised = revised.replace(old, new)
        if revised != current:
            frappe.db.set_value("Lead", lead.name, "custom_services", revised)
            updated += 1
    return updated
