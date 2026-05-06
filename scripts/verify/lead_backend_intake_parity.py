#!/usr/bin/env python3
"""Verify ERPNext Lead/CRM metadata matches the public /contact intake form."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"

EXPECTED_SERVICES = {
    "Balloon Decor",
    "Balloon Twisting",
    "Face Painting",
    "Delivery",
    "Pickup",
    "Events Inquiry",
    "Something Else",
}
STALE_SERVICES = {"Delivery Only", "Event Package"}
STALE_INTERNAL_COPY = {"even an estimate is helpful"}
TIME_TEXT_DESCRIPTION = "Plain text time entry. Examples: 3 PM, 3:30 PM, afternoon, TBD."
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
MACHINE_TIME_RE = re.compile(r"^\d{1,2}:\d{2}:\d{2}(?:\.\d+)?$")


def selected(values: list[str]) -> str:
    quoted = ",".join(f"'{value}'" for value in values)
    return (
        "eval:doc.custom_event_type && doc.custom_event_type.some(function(r){"
        f"return [{quoted}].indexOf(r.service_type) !== -1;"
        "})"
    )


EXPECTED_CUSTOM_FIELDS = {
    "custom_event_type": {"label": "Services Requested"},
    "lt_section_delivery": {
        "label": "Delivery Details",
        "depends_on": selected(["Delivery"]),
    },
    "lt_section_package": {
        "label": "Events Inquiry Details",
        "depends_on": selected(["Events Inquiry"]),
    },
    "custom_package_notes": {
        "label": "Events Inquiry Notes",
        "depends_on": selected(["Events Inquiry"]),
    },
    "lt_section_environment": {
        "label": "Event Environment",
        "depends_on": selected(["Balloon Twisting", "Face Painting"]),
    },
    "custom_shade_required": {
        "label": "Shade Required",
        "depends_on": selected(["Balloon Twisting", "Face Painting"]),
    },
    "custom_decor_notes": {
        "label": "Decor Notes",
        "depends_on": selected(["Balloon Decor"]),
    },
    "custom_other_notes": {
        "label": "Something Else Notes",
        "depends_on": selected(["Something Else"]),
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
    "lt_section_photos": {
        "label": "Inspiration Photos",
    },
    "custom_inspiration_photos": {
        "label": "Inspiration Photos",
        "fieldtype": "Table",
        "options": "LT Lead Photo",
    },
    "custom_lt_payment_timing": {
        "label": "Payment Timing",
        "fieldtype": "Select",
        "options": "\nFull payment before prep\nDeposit then balance\nNet 30\nPaid in full at checkout",
    },
    "custom_lt_deposit_due": {
        "label": "Deposit Due",
        "fieldtype": "Currency",
    },
    "custom_lt_balance_timing": {
        "label": "Balance Timing",
        "fieldtype": "Data",
    },
    "custom_lt_payment_notes": {
        "label": "Payment Notes",
        "fieldtype": "Small Text",
    },
}


def bench_execute(method: str, *, args: list[Any] | None = None, kwargs: dict[str, Any] | None = None) -> Any:
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
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def get_list(doctype: str, **kwargs: Any) -> list[dict[str, Any]]:
    payload = {"doctype": doctype, **kwargs}
    return bench_execute("frappe.client.get_list", kwargs=payload) or []


def check_service_types() -> list[str]:
    failures = []
    rows = get_list(
        "LT Service Type",
        fields=["name", "service_type"],
        limit_page_length=200,
        order_by="name asc",
    )
    names = {row["name"] for row in rows}
    service_types = {row.get("service_type") for row in rows}
    found = names | service_types

    missing = sorted(EXPECTED_SERVICES - found)
    stale = sorted(STALE_SERVICES & found)
    if missing:
        failures.append(f"LT Service Type missing current values: {', '.join(missing)}")
    if stale:
        failures.append(f"LT Service Type still has stale values: {', '.join(stale)}")
    return failures


def check_lead_custom_fields() -> list[str]:
    failures = []
    rows = get_list(
        "Custom Field",
        filters={"dt": "Lead"},
        fields=["fieldname", "label", "fieldtype", "description", "depends_on", "options"],
        limit_page_length=250,
        order_by="idx asc",
    )
    by_name = {row["fieldname"]: row for row in rows}

    for fieldname, expected in EXPECTED_CUSTOM_FIELDS.items():
        row = by_name.get(fieldname)
        if not row:
            failures.append(f"Lead Custom Field missing: {fieldname}")
            continue
        for key, expected_value in expected.items():
            actual = row.get(key)
            if actual != expected_value:
                failures.append(
                    f"{fieldname}.{key} expected {expected_value!r}, found {actual!r}"
                )

    for row in rows:
        haystack = "\n".join(
            str(row.get(key) or "")
            for key in ("label", "description", "depends_on", "options")
        )
        for stale in sorted(STALE_SERVICES):
            if stale in haystack:
                failures.append(f"{row['fieldname']} still references stale service {stale!r}")
        for stale in sorted(STALE_INTERNAL_COPY):
            if stale.lower() in haystack.lower():
                failures.append(f"{row['fieldname']} still has customer-only copy in backend metadata")
    return failures


def check_lead_photo_doctype() -> list[str]:
    failures = []
    rows = get_list(
        "DocType",
        filters={"name": "LT Lead Photo"},
        fields=["name", "istable"],
        limit_page_length=1,
    )
    if not rows:
        return ["LT Lead Photo child DocType is missing"]
    if rows[0].get("istable") != 1:
        failures.append("LT Lead Photo exists but is not a child table")

    meta = bench_execute("frappe.client.get", kwargs={"doctype": "DocType", "name": "LT Lead Photo"})
    fieldnames = {field.get("fieldname") for field in meta.get("fields", [])}
    for fieldname in ("photo", "caption"):
        if fieldname not in fieldnames:
            failures.append(f"LT Lead Photo missing child field: {fieldname}")
    return failures


def check_existing_time_text_values() -> list[str]:
    failures = []
    rows = get_list(
        "Lead",
        fields=["name", *TIME_TEXT_FIELDS],
        limit_page_length=10000,
        order_by="name asc",
    )
    for row in rows:
        for fieldname in TIME_TEXT_FIELDS:
            value = row.get(fieldname)
            if value and MACHINE_TIME_RE.match(str(value).strip()):
                failures.append(
                    f"{row['name']}.{fieldname} still has machine-style time text: {value!r}"
                )
    return failures


def check_submit_mapping_helper() -> list[str]:
    failures = []
    try:
        rows = bench_execute(
            "locally_twisted.www.book._service_child_rows",
            args=[["Delivery", "Pickup", "Events Inquiry"]],
        )
    except RuntimeError as exc:
        return [f"submit helper _service_child_rows missing or failed: {exc}"]

    expected = [
        {"service_type": "Delivery"},
        {"service_type": "Pickup"},
        {"service_type": "Events Inquiry"},
    ]
    if rows != expected:
        failures.append(f"_service_child_rows expected {expected!r}, found {rows!r}")
    source = Path("apps/locally_twisted/locally_twisted/www/book.py").read_text(encoding="utf-8")
    if '"custom_event_type": _service_child_rows(services)' not in source:
        failures.append("submit_book_inquiry does not populate Lead.custom_event_type from services")

    try:
        artist_rule = bench_execute(
            "locally_twisted.www.book._payment_rule_for_inquiry",
            kwargs={
                "services": ["Balloon Twisting", "Face Painting"],
                "num_twisters": 1,
                "num_painters": 1,
            },
        )
        decor_rule = bench_execute(
            "locally_twisted.www.book._payment_rule_for_inquiry",
            kwargs={"services": ["Balloon Decor"]},
        )
        other_rule = bench_execute(
            "locally_twisted.www.book._payment_rule_for_inquiry",
            kwargs={"services": ["Something Else"]},
        )
        mixed_rule = bench_execute(
            "locally_twisted.www.book._payment_rule_for_inquiry",
            kwargs={
                "services": ["Balloon Decor", "Balloon Twisting"],
                "num_twisters": 2,
            },
        )
    except RuntimeError as exc:
        return [*failures, f"payment rule helper missing or failed: {exc}"]
    if artist_rule.get("deposit_due") != 100.0:
        failures.append(f"twisting + painting should require $100 deposit, found {artist_rule!r}")
    if artist_rule.get("payment_timing") != "Deposit then balance":
        failures.append(f"artist services should use deposit timing, found {artist_rule!r}")
    if decor_rule.get("payment_timing") != "Full payment before prep":
        failures.append(f"decor quote should use full-before-prep timing, found {decor_rule!r}")
    if other_rule.get("payment_timing") != "Full payment before prep":
        failures.append(f"miscellaneous inquiries should stay quote-aware, found {other_rule!r}")
    if mixed_rule.get("deposit_due") != 100.0:
        failures.append(f"two-artist mixed decor inquiry should require $100 deposit, found {mixed_rule!r}")
    if "prep" not in (mixed_rule.get("payment_notes") or "").lower():
        failures.append(f"mixed decor + artist inquiry should mention prep payment timing, found {mixed_rule!r}")
    return failures


def check_public_form_time_copy() -> list[str]:
    failures = []
    source = Path("apps/locally_twisted/locally_twisted/templates/includes/book_form.html").read_text(
        encoding="utf-8"
    )
    required_snippets = [
        "Event Start Time",
        "Event End Time",
        "(even an estimate is helpful!)",
        'type="text" id="book_time" name="x_event_time"',
        'type="text" id="book_end_time" name="x_event_end_time"',
    ]
    for snippet in required_snippets:
        if snippet not in source:
            failures.append(f"public inquiry form missing time-field snippet: {snippet}")
    return failures


def main() -> int:
    failures = []
    failures.extend(check_service_types())
    failures.extend(check_lead_custom_fields())
    failures.extend(check_lead_photo_doctype())
    failures.extend(check_existing_time_text_values())
    failures.extend(check_submit_mapping_helper())
    failures.extend(check_public_form_time_copy())

    if failures:
        print("[LEAD BACKEND INTAKE PARITY] FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("[LEAD BACKEND INTAKE PARITY] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
