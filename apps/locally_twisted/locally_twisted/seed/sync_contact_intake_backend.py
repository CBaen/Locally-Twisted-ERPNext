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

PERMISSION_FIELDS = (
    "read",
    "write",
    "create",
    "delete",
    "submit",
    "cancel",
    "amend",
    "report",
    "export",
    "import",
    "share",
    "print",
    "email",
)


def _permission_row(role: str, **enabled: int) -> dict[str, int | str]:
    row: dict[str, int | str] = {"role": role}
    for fieldname in PERMISSION_FIELDS:
        row[fieldname] = 1 if enabled.get(fieldname) else 0
    return row


SERVICE_TYPE_PERMISSIONS = [
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
    _permission_row("LT Owner Access", read=1),
    _permission_row("LT Manager Access", read=1),
    _permission_row("Sales Manager", read=1),
    _permission_row("Sales User", read=1),
]

REQUIRED_PERMISSION_ROLES = {
    "LT Owner Access": 1,
    "LT Manager Access": 1,
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
    "custom_preferred_contact_method": {
        "label": "Preferred Contact Method",
        "fieldtype": "Select",
        "options": "\nEmail\nPhone\nText",
        "depends_on": None,
    },
    "lt_section_decor": {
        "label": "Balloon Decor Details",
        "depends_on": _selected(["Balloon Decor"]),
        "insert_after": "custom_preferred_contact_method",
    },
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
    "custom_lt_product_quote_items": {
        "label": "Product Quote Items",
        "fieldtype": "Table",
        "options": "LT Product Quote Item",
        "insert_after": "custom_lt_product_quote_payload",
    },
}

LEAD_INTAKE_CUSTOM_FIELDS = {
    "lt_booking_tab": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "lt_booking_tab",
        "label": "LT Booking Details",
        "fieldtype": "Tab Break",
        "insert_after": "qualification_tab",
    },
    "lt_section_basics": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "lt_section_basics",
        "label": "Event Basics",
        "fieldtype": "Section Break",
        "insert_after": "lt_booking_tab",
    },
    "custom_event_type": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_event_type",
        "label": "Services Requested",
        "fieldtype": "Table MultiSelect",
        "options": "LT Lead Service Type",
        "insert_after": "lt_section_basics",
        "description": "Pick one or more services. The booking detail sub-sections appear automatically based on which services are selected.",
    },
    "custom_occasion_type": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_occasion_type",
        "label": "What are they celebrating?",
        "fieldtype": "Select",
        "options": "\nBirthday Party\nSchool Event\nCorporate Event\nFestival / Fair\nChurch Event\nFamily Reunion\nHoliday Party\nOther\nWedding\nBaby Shower\nGrand Opening\nGraduation\nGet Well\nMissionary Farewell / Homecoming\nReligious Celebration",
        "insert_after": "custom_event_type",
    },
    "custom_event_date": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_event_date",
        "label": "Event Date",
        "fieldtype": "Date",
        "insert_after": "custom_occasion_type",
    },
    "custom_event_time": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_event_time",
        "label": "Event Start Time",
        "fieldtype": "Data",
        "insert_after": "custom_event_date",
        "description": TIME_TEXT_DESCRIPTION,
    },
    "custom_event_end_time": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_event_end_time",
        "label": "Event End Time",
        "fieldtype": "Data",
        "insert_after": "custom_event_time",
        "description": TIME_TEXT_DESCRIPTION,
    },
    "custom_event_location": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_event_location",
        "label": "City / Location",
        "fieldtype": "Data",
        "insert_after": "custom_event_end_time",
        "description": "Address, venue name, or city",
    },
    "custom_guest_count": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_guest_count",
        "label": "Estimated Guests",
        "fieldtype": "Int",
        "insert_after": "custom_event_location",
    },
    "custom_preferred_contact_method": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_preferred_contact_method",
        "label": "Preferred Contact Method",
        "fieldtype": "Select",
        "options": "\nEmail\nPhone\nText",
        "insert_after": "custom_guest_count",
        "description": "Customer's requested follow-up channel for this inquiry.",
    },
    "lt_section_decor": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "lt_section_decor",
        "label": "Balloon Decor Details",
        "fieldtype": "Section Break",
        "insert_after": "custom_preferred_contact_method",
        "depends_on": _selected(["Balloon Decor"]),
    },
    "custom_decor_types": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_decor_types",
        "label": "Decor Types",
        "fieldtype": "Data",
        "insert_after": "lt_section_decor",
        "description": "Entrance decor, table decor, backdrop, columns...",
    },
    "custom_setup_time_arrival": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_setup_time_arrival",
        "label": "Setup Arrival Time",
        "fieldtype": "Data",
        "insert_after": "custom_decor_types",
        "description": TIME_TEXT_DESCRIPTION,
    },
    "custom_decor_notes": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_decor_notes",
        "label": "Decor Notes",
        "fieldtype": "Long Text",
        "insert_after": "custom_setup_time_arrival",
        "depends_on": _selected(["Balloon Decor"]),
        "description": "Size, style, any special requirements...",
    },
    "lt_section_twisting": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "lt_section_twisting",
        "label": "Balloon Twisting Details",
        "fieldtype": "Section Break",
        "insert_after": "custom_decor_notes",
        "depends_on": _selected(["Balloon Twisting"]),
    },
    "custom_num_twisters": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_num_twisters",
        "label": "Number of Twisters",
        "fieldtype": "Int",
        "insert_after": "lt_section_twisting",
    },
    "custom_artist_start": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_artist_start",
        "label": "Twister Start Time",
        "fieldtype": "Data",
        "insert_after": "custom_num_twisters",
        "description": TIME_TEXT_DESCRIPTION,
    },
    "custom_artist_end": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_artist_end",
        "label": "Twister End Time",
        "fieldtype": "Data",
        "insert_after": "custom_artist_start",
        "description": TIME_TEXT_DESCRIPTION,
    },
    "custom_twisting_notes": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_twisting_notes",
        "label": "Twisting Notes",
        "fieldtype": "Long Text",
        "insert_after": "custom_artist_end",
        "depends_on": _selected(["Balloon Twisting"]),
        "description": "Special requests, character themes...",
    },
    "lt_section_painting": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "lt_section_painting",
        "label": "Face Painting Details",
        "fieldtype": "Section Break",
        "insert_after": "custom_twisting_notes",
        "depends_on": _selected(["Face Painting"]),
    },
    "custom_num_painters": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_num_painters",
        "label": "Number of Face Painters",
        "fieldtype": "Int",
        "insert_after": "lt_section_painting",
    },
    "custom_painter_start": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_painter_start",
        "label": "Painter Start Time",
        "fieldtype": "Data",
        "insert_after": "custom_num_painters",
        "description": TIME_TEXT_DESCRIPTION,
    },
    "custom_painter_end": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_painter_end",
        "label": "Painter End Time",
        "fieldtype": "Data",
        "insert_after": "custom_painter_start",
        "description": TIME_TEXT_DESCRIPTION,
    },
    "custom_painting_notes": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_painting_notes",
        "label": "Face Painting Notes",
        "fieldtype": "Long Text",
        "insert_after": "custom_painter_end",
        "depends_on": _selected(["Face Painting"]),
        "description": "Design preferences, age range of kids...",
    },
    "lt_section_delivery": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "lt_section_delivery",
        "label": "Delivery Details",
        "fieldtype": "Section Break",
        "insert_after": "custom_painting_notes",
        "depends_on": _selected(["Delivery"]),
    },
    "custom_delivery_window_start": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_delivery_window_start",
        "label": "Delivery Window Start",
        "fieldtype": "Data",
        "insert_after": "lt_section_delivery",
        "description": TIME_TEXT_DESCRIPTION,
    },
    "custom_delivery_window_end": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_delivery_window_end",
        "label": "Delivery Window End",
        "fieldtype": "Data",
        "insert_after": "custom_delivery_window_start",
        "description": TIME_TEXT_DESCRIPTION,
    },
    "custom_delivery_notes": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_delivery_notes",
        "label": "Delivery Notes",
        "fieldtype": "Long Text",
        "insert_after": "custom_delivery_window_end",
        "depends_on": _selected(["Delivery"]),
        "description": "When do you need delivery? Morning, afternoon, specific time...",
    },
    "lt_section_package": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "lt_section_package",
        "label": "Events Inquiry Details",
        "fieldtype": "Section Break",
        "insert_after": "custom_delivery_notes",
        "depends_on": _selected(["Events Inquiry"]),
    },
    "custom_package_notes": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_package_notes",
        "label": "Events Inquiry Notes",
        "fieldtype": "Long Text",
        "insert_after": "lt_section_package",
        "depends_on": _selected(["Events Inquiry"]),
        "description": "Describe your ideal event package...",
    },
    "lt_section_other": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "lt_section_other",
        "label": "Something Else Details",
        "fieldtype": "Section Break",
        "insert_after": "custom_package_notes",
        "depends_on": _selected(["Something Else"]),
    },
    "custom_other_notes": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_other_notes",
        "label": "Something Else Notes",
        "fieldtype": "Long Text",
        "insert_after": "lt_section_other",
        "depends_on": _selected(["Something Else"]),
        "description": "Tell us about your idea...",
    },
    "lt_section_environment": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "lt_section_environment",
        "label": "Event Environment",
        "fieldtype": "Section Break",
        "insert_after": "custom_other_notes",
        "depends_on": _selected(["Balloon Twisting", "Face Painting"]),
    },
    "custom_indoor_outdoor": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_indoor_outdoor",
        "label": "Indoor / Outdoor",
        "fieldtype": "Select",
        "options": "\nIndoor\nOutdoor\nBoth",
        "insert_after": "lt_section_environment",
    },
    "custom_shade_required": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_shade_required",
        "label": "Shade Required",
        "fieldtype": "Check",
        "insert_after": "custom_indoor_outdoor",
        "depends_on": _selected(["Balloon Twisting", "Face Painting"]),
        "description": "Automatically required for outdoor events",
    },
    "custom_colors": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_colors",
        "label": "Color Preferences",
        "fieldtype": "Data",
        "insert_after": "custom_shade_required",
        "description": "Specific colors, brand colors, theme colors...",
    },
    "lt_section_photos": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "lt_section_photos",
        "label": "Inspiration Photos",
        "fieldtype": "Section Break",
        "insert_after": "custom_colors",
        "description": "Up to 5 photos, 25 MB each.",
    },
    "lt_section_anything_else": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "lt_section_anything_else",
        "label": "Anything Else",
        "fieldtype": "Section Break",
        "insert_after": "lt_section_photos",
    },
    "custom_anything_else": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_anything_else",
        "label": "Anything else we should know?",
        "fieldtype": "Long Text",
        "insert_after": "lt_section_anything_else",
        "description": "Form posts to `description`. Map at form-handler layer.",
    },
    "lt_section_internal": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "lt_section_internal",
        "label": "Internal - Relationship & Workflow",
        "fieldtype": "Section Break",
        "insert_after": "custom_anything_else",
    },
    "custom_referred_by": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_referred_by",
        "label": "Referred By (Contact)",
        "fieldtype": "Link",
        "options": "Contact",
        "insert_after": "lt_section_internal",
    },
    "custom_source_channel": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_source_channel",
        "label": "Source Channel",
        "fieldtype": "Select",
        "options": "\nPhone Call\nEmail\nText Message\nIn Person\nWebsite Form",
        "insert_after": "custom_referred_by",
        "description": "How did this lead come in?",
    },
    "custom_taken_by": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_taken_by",
        "label": "Taken By",
        "fieldtype": "Link",
        "options": "User",
        "insert_after": "custom_source_channel",
        "description": "Who received this inquiry (Jeff, Julie, etc.)",
    },
    "custom_internal_notes": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_internal_notes",
        "label": "Internal Only Notes",
        "fieldtype": "Long Text",
        "insert_after": "custom_taken_by",
        "description": "Visible to staff only - never shown to the customer.",
    },
    "custom_client_type": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_client_type",
        "label": "Client Type",
        "fieldtype": "Select",
        "options": "\nPersonal / Private Party\nCorporate / Business",
        "insert_after": "custom_internal_notes",
        "description": "Determines payment terms: personal = 72hr prepay, corporate = Net 30",
    },
    "custom_booking_confirmed": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_booking_confirmed",
        "label": "Booking Confirmed",
        "fieldtype": "Check",
        "insert_after": "custom_client_type",
        "description": "Set True after booking confirmation email is sent. Prevents resending when a lead transitions to Won more than once.",
    },
}

SERVICE_TYPE_DOCTYPE = {
    "doctype": "DocType",
    "name": "LT Service Type",
    "module": "Custom",
    "custom": 1,
    "editable_grid": 1,
    "autoname": "field:service_type",
    "naming_rule": "By fieldname",
    "title_field": "service_type",
    "allow_rename": 1,
    "fields": [
        {
            "fieldname": "service_type",
            "label": "Service Type",
            "fieldtype": "Data",
            "reqd": 1,
            "unique": 1,
            "in_list_view": 1,
        },
    ],
    "permissions": [
        dict(row) for row in SERVICE_TYPE_PERMISSIONS
    ],
}

LEAD_SERVICE_TYPE_DOCTYPE = {
    "doctype": "DocType",
    "name": "LT Lead Service Type",
    "module": "Custom",
    "custom": 1,
    "istable": 1,
    "editable_grid": 1,
    "allow_rename": 1,
    "fields": [
        {
            "fieldname": "service_type",
            "label": "Service Type",
            "fieldtype": "Link",
            "options": "LT Service Type",
            "reqd": 1,
            "in_list_view": 1,
        },
    ],
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

PRODUCT_QUOTE_ITEM_DOCTYPE = {
    "doctype": "DocType",
    "name": "LT Product Quote Item",
    "module": "Custom",
    "custom": 1,
    "istable": 1,
    "editable_grid": 1,
    "fields": [
        {
            "fieldname": "product_page",
            "label": "Product Page",
            "fieldtype": "Link",
            "options": "Item",
            "in_list_view": 1,
        },
        {
            "fieldname": "product_page_type",
            "label": "Page Type",
            "fieldtype": "Data",
            "in_list_view": 1,
        },
        {
            "fieldname": "commerce_lane",
            "label": "Commerce Lane",
            "fieldtype": "Data",
        },
        {
            "fieldname": "summary",
            "label": "Summary",
            "fieldtype": "Small Text",
            "in_list_view": 1,
        },
        {
            "fieldname": "payload_json",
            "label": "Payload JSON",
            "fieldtype": "JSON",
        },
        {
            "fieldname": "status",
            "label": "Status",
            "fieldtype": "Data",
            "default": "Needs Operator Review",
        },
    ],
}

ENSURED_LEAD_CUSTOM_FIELDS = {
    **LEAD_INTAKE_CUSTOM_FIELDS,
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
    "custom_lt_product_template_item": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_lt_product_template_item",
        "label": "Requested Product Page",
        "fieldtype": "Link",
        "options": "Item",
        "insert_after": "custom_anything_else",
    },
    "custom_lt_product_page_type": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_lt_product_page_type",
        "label": "LT Product Page Type",
        "fieldtype": "Data",
        "insert_after": "custom_lt_product_template_item",
    },
    "custom_lt_product_quote_summary": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_lt_product_quote_summary",
        "label": "Product Quote Summary",
        "fieldtype": "Small Text",
        "insert_after": "custom_lt_product_page_type",
    },
    "custom_lt_product_quote_payload": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_lt_product_quote_payload",
        "label": "Product Quote Payload",
        "fieldtype": "JSON",
        "insert_after": "custom_lt_product_quote_summary",
    },
    "custom_lt_product_quote_items": {
        "doctype": "Custom Field",
        "dt": "Lead",
        "fieldname": "custom_lt_product_quote_items",
        "label": "Product Quote Items",
        "fieldtype": "Table",
        "options": "LT Product Quote Item",
        "insert_after": "custom_lt_product_quote_payload",
    },
}


def execute(commit: bool = True) -> str:
    summary = {
        "ensured_doctypes": [],
        "ensured_roles": [],
        "hardened_doctype_permissions": [],
        "renamed_services": [],
        "ensured_services": [],
        "ensured_custom_fields": [],
        "updated_custom_fields": [],
        "normalized_time_values": 0,
        "updated_leads": 0,
    }
    _ensure_permission_roles(summary)
    _ensure_contact_child_doctypes(summary)
    _sync_service_types(summary)
    _ensure_lead_custom_fields(summary)
    _sync_lead_custom_fields(summary)
    summary["normalized_time_values"] = _normalize_existing_lead_time_text()
    summary["updated_leads"] = _rewrite_existing_lead_service_csv()
    frappe.clear_cache(doctype="Lead")
    if commit:
        frappe.db.commit()
    print(json.dumps(summary, indent=2, sort_keys=True))
    return json.dumps(summary, sort_keys=True)


def _ensure_permission_roles(summary: dict) -> None:
    for role_name, desk_access in REQUIRED_PERMISSION_ROLES.items():
        if frappe.db.exists("Role", role_name):
            continue
        frappe.get_doc(
            {
                "doctype": "Role",
                "role_name": role_name,
                "desk_access": desk_access,
                "disabled": 0,
            }
        ).insert(ignore_permissions=True)
        summary["ensured_roles"].append(role_name)


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


def _ensure_contact_child_doctypes(summary: dict) -> None:
    for spec in (SERVICE_TYPE_DOCTYPE, LEAD_SERVICE_TYPE_DOCTYPE, LEAD_PHOTO_DOCTYPE, PRODUCT_QUOTE_ITEM_DOCTYPE):
        if frappe.db.exists("DocType", spec["name"]):
            if spec["name"] == "LT Service Type":
                _sync_doctype_permissions(spec["name"], SERVICE_TYPE_PERMISSIONS, summary)
            continue
        frappe.get_doc(spec).insert(ignore_permissions=True)
        summary["ensured_doctypes"].append(spec["name"])
        if spec["name"] == "LT Service Type":
            summary["hardened_doctype_permissions"].append(spec["name"])


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
        doc.append("permissions", dict(row))
    doc.save(ignore_permissions=True)
    frappe.clear_cache(doctype=doctype_name)
    summary["hardened_doctype_permissions"].append(doctype_name)


def _normalized_permission_row(row: dict) -> dict[str, int | str]:
    normalized: dict[str, int | str] = {"role": row.get("role") or ""}
    for fieldname in PERMISSION_FIELDS:
        normalized[fieldname] = 1 if row.get(fieldname) else 0
    return normalized


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
    if not frappe.get_meta("Lead").has_field("custom_services"):
        return 0

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
