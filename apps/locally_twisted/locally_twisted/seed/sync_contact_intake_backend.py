"""Sync Lead/CRM backend metadata to the current public contact intake.

Run in-process:
  bench --site frontend execute locally_twisted.seed.sync_contact_intake_backend.execute
"""
from __future__ import annotations

import json
import re

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

TIME_TEXT_DESCRIPTION = "Plain text time entry. Examples: 3 PM, 3:30 PM, afternoon, TBD."
SAFE_FIELDTYPE_CONVERSIONS = {("Time", "Data")}
TIME_TEXT_FIELDS = (
    "custom_event_time",
    "custom_event_end_time",
    "custom_setup_time_arrival",
    "custom_artist_start",
    "custom_artist_end",
    "custom_painter_start",
    "custom_painter_end",
    "custom_delivery_window_start",
    "custom_delivery_window_end",
)
TIME_TEXT_RE = re.compile(r"^(\d{1,2}):(\d{2})(?::(\d{2})(?:\.(\d+))?)?$")


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
    "custom_event_time": {
        "label": "Event Start Time",
        "fieldtype": "Data",
        "description": TIME_TEXT_DESCRIPTION,
        "depends_on": None,
    },
    "custom_event_end_time": {
        "label": "Event End Time",
        "fieldtype": "Data",
        "description": TIME_TEXT_DESCRIPTION,
        "depends_on": None,
    },
    "custom_guest_count": {"depends_on": None},
    "custom_setup_time_arrival": {
        "fieldtype": "Data",
        "description": TIME_TEXT_DESCRIPTION,
    },
    "custom_artist_start": {
        "fieldtype": "Data",
        "description": TIME_TEXT_DESCRIPTION,
    },
    "custom_artist_end": {
        "fieldtype": "Data",
        "description": TIME_TEXT_DESCRIPTION,
    },
    "custom_painter_start": {
        "fieldtype": "Data",
        "description": TIME_TEXT_DESCRIPTION,
    },
    "custom_painter_end": {
        "fieldtype": "Data",
        "description": TIME_TEXT_DESCRIPTION,
    },
    "custom_delivery_window_start": {
        "fieldtype": "Data",
        "description": TIME_TEXT_DESCRIPTION,
    },
    "custom_delivery_window_end": {
        "fieldtype": "Data",
        "description": TIME_TEXT_DESCRIPTION,
    },
    "custom_inspiration_photos": {
        "label": "Inspiration Photos",
        "fieldtype": "Table",
        "options": "LT Lead Photo",
        "insert_after": "lt_section_photos",
    },
    "custom_lt_payment_timing": {
        "label": "Payment Timing",
        "fieldtype": "Select",
        "options": "\nFull payment before prep\nDeposit then balance\nNet 30\nPaid in full at checkout",
        "insert_after": "custom_internal_notes",
    },
    "custom_lt_deposit_due": {
        "label": "Deposit Due",
        "fieldtype": "Currency",
        "insert_after": "custom_lt_payment_timing",
    },
    "custom_lt_balance_timing": {
        "label": "Balance Timing",
        "fieldtype": "Data",
        "insert_after": "custom_lt_deposit_due",
    },
    "custom_lt_payment_notes": {
        "label": "Payment Notes",
        "fieldtype": "Small Text",
        "insert_after": "custom_lt_balance_timing",
    },
}

LEAD_PHOTO_DOCTYPE = {
    "doctype": "DocType",
    "name": "LT Lead Photo",
    "module": "Custom",
    "custom": 1,
    "istable": 1,
    "editable_grid": 1,
    "fields": [
        {
            "fieldname": "photo",
            "label": "Photo",
            "fieldtype": "Attach Image",
            "reqd": 1,
        },
        {
            "fieldname": "caption",
            "label": "Caption",
            "fieldtype": "Data",
            "in_list_view": 1,
        },
    ],
}

ENSURED_LEAD_CUSTOM_FIELDS = {
    "custom_inspiration_photos": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_inspiration_photos",
        "label": "Inspiration Photos",
        "fieldtype": "Table",
        "options": "LT Lead Photo",
        "insert_after": "lt_section_photos",
    },
    "custom_lt_payment_timing": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_lt_payment_timing",
        "label": "Payment Timing",
        "fieldtype": "Select",
        "options": "\nFull payment before prep\nDeposit then balance\nNet 30\nPaid in full at checkout",
        "insert_after": "custom_internal_notes",
    },
    "custom_lt_deposit_due": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_lt_deposit_due",
        "label": "Deposit Due",
        "fieldtype": "Currency",
        "insert_after": "custom_lt_payment_timing",
    },
    "custom_lt_balance_timing": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_lt_balance_timing",
        "label": "Balance Timing",
        "fieldtype": "Data",
        "insert_after": "custom_lt_deposit_due",
    },
    "custom_lt_payment_notes": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_lt_payment_notes",
        "label": "Payment Notes",
        "fieldtype": "Small Text",
        "insert_after": "custom_lt_balance_timing",
    },
}


def execute(commit: bool = True) -> str:
    summary = {
        "ensured_doctypes": [],
        "renamed_services": [],
        "ensured_services": [],
        "ensured_custom_fields": [],
        "updated_custom_fields": [],
        "normalized_time_values": 0,
        "updated_leads": 0,
    }
    _sync_service_types(summary)
    _ensure_lead_photo_doctype(summary)
    _ensure_lead_custom_fields(summary)
    _sync_lead_custom_fields(summary)
    summary["normalized_time_values"] = _normalize_existing_lead_time_text()
    summary["updated_leads"] = _rewrite_existing_lead_service_csv()
    frappe.clear_cache(doctype="Lead")
    if commit:
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


def _ensure_lead_photo_doctype(summary: dict) -> None:
    if frappe.db.exists("DocType", "LT Lead Photo"):
        return
    frappe.get_doc(LEAD_PHOTO_DOCTYPE).insert(ignore_permissions=True)
    summary["ensured_doctypes"].append("LT Lead Photo")


def _ensure_lead_custom_fields(summary: dict) -> None:
    for fieldname, field in ENSURED_LEAD_CUSTOM_FIELDS.items():
        if frappe.db.exists("Custom Field", {"dt": "Lead", "fieldname": fieldname}):
            continue
        frappe.get_doc(field).insert(ignore_permissions=True)
        summary["ensured_custom_fields"].append(fieldname)


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
        safe_fieldtype_conversion = False
        for key, value in updates.items():
            current = getattr(doc, key)
            if current != value:
                if key == "fieldtype":
                    conversion = (current, value)
                    if conversion not in SAFE_FIELDTYPE_CONVERSIONS:
                        raise RuntimeError(
                            f"Refusing unsafe fieldtype conversion for Lead.{fieldname}: "
                            f"{current!r} to {value!r}"
                        )
                    safe_fieldtype_conversion = True
                setattr(doc, key, value)
                changed = True
        if changed:
            if safe_fieldtype_conversion:
                doc.flags.ignore_validate = True
            doc.save(ignore_permissions=True)
            summary["updated_custom_fields"].append(fieldname)


def _normalize_existing_lead_time_text() -> int:
    updated = 0
    fields = ["name", *TIME_TEXT_FIELDS]
    for lead in frappe.get_all(
        "Lead",
        fields=fields,
        limit_page_length=10000,
    ):
        for fieldname in TIME_TEXT_FIELDS:
            current = lead.get(fieldname)
            normalized = _friendly_time_text(current)
            if normalized != current:
                frappe.db.set_value(
                    "Lead",
                    lead.name,
                    fieldname,
                    normalized,
                    update_modified=False,
                )
                updated += 1
    return updated


def _friendly_time_text(value: object) -> str | None:
    if value is None or value == "":
        return None
    text = str(value).strip()
    match = TIME_TEXT_RE.match(text)
    if not match:
        return text

    hour = int(match.group(1))
    minute = match.group(2)
    seconds = match.group(3)
    microseconds = match.group(4)

    # Values with real seconds/microseconds came from the old Time-field widget,
    # not from a human choosing an estimated event time.
    if (seconds and seconds != "00") or (microseconds and int(microseconds) != 0):
        return None

    suffix = "AM" if hour < 12 else "PM"
    display_hour = hour % 12 or 12
    return f"{display_hour}:{minute} {suffix}"


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
