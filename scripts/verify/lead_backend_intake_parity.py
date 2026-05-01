#!/usr/bin/env python3
"""Verify ERPNext Lead/CRM metadata matches the public /contact intake form."""
from __future__ import annotations

import json
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
    "custom_event_time": {"depends_on": None},
    "custom_event_end_time": {"depends_on": None},
    "custom_guest_count": {"depends_on": None},
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
        fields=["fieldname", "label", "depends_on", "options"],
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
        haystack = "\n".join(str(row.get(key) or "") for key in ("label", "depends_on", "options"))
        for stale in sorted(STALE_SERVICES):
            if stale in haystack:
                failures.append(f"{row['fieldname']} still references stale service {stale!r}")
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
    return failures


def main() -> int:
    failures = []
    failures.extend(check_service_types())
    failures.extend(check_lead_custom_fields())
    failures.extend(check_submit_mapping_helper())

    if failures:
        print("[LEAD BACKEND INTAKE PARITY] FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("[LEAD BACKEND INTAKE PARITY] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
