#!/usr/bin/env python3
"""Verify simplified ERPNext Desk workspaces use current LT backend labels."""
from __future__ import annotations

import json
import subprocess
import sys
from typing import Any


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"

EXPECTED_WORKSPACE_SHORTCUTS = {
    "LT Owner Home": {
        "Booking Calendar": ("Sales Order", "Calendar"),
        "Customers": ("Customer", "List"),
        "People to Contact": ("Contact", "List"),
        "Add Product": ("Item", "New"),
    },
    "LT Manager Home": {
        "Booking Calendar": ("Sales Order", "Calendar"),
        "Customers": ("Customer", "List"),
        "People to Contact": ("Contact", "List"),
    },
    "LT Employee Home": {
        "Booking Calendar": ("Sales Order", "Calendar"),
        "People to Contact": ("Contact", "List"),
    },
}

STALE_LABELS = {"Event Calendar", "Clients & Customers", "Contacts"}

OWNER_HOME_NUMBER_CARDS = {
    "New Inquiries": {
        "label": "New Inquiries",
        "document_type": "Lead",
        "function": "Count",
        "filters_json": [["Lead", "status", "=", "Open"]],
    },
    "Bookings": {
        "label": "Bookings",
        "document_type": "Sales Order",
        "function": "Count",
        "filters_json": [],
    },
    "Customers": {
        "label": "Customers",
        "document_type": "Customer",
        "function": "Count",
        "filters_json": [["Customer", "disabled", "=", 0]],
    },
    "Overdue Follow-ups": {
        "label": "Overdue Follow-ups",
        "document_type": "Task",
        "function": "Count",
        "filters_json": [["Task", "status", "=", "Overdue"]],
    },
}

OWNER_HOME_CHART = {
    "name": "LT Incoming Inquiries",
    "chart_name": "LT Incoming Inquiries",
    "document_type": "Lead",
    "chart_type": "Count",
    "based_on": "creation",
    "time_interval": "Weekly",
    "timespan": "Last Quarter",
    "timeseries": 1,
    "type": "Bar",
}

OWNER_HOME_TEXT = {
    "Today at Locally Twisted",
    "What Jeff does next",
    "Answer new inquiries",
    "Check upcoming bookings",
    "Finish follow-ups",
    "Update products only when needed",
}


def bench_execute(method: str, *, kwargs: dict[str, Any] | None = None) -> Any:
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
    if kwargs is not None:
        cmd.extend(["--kwargs", json.dumps(kwargs)])

    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=60)
    if proc.returncode != 0:
        raise RuntimeError(
            f"bench execute failed for {method}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    text = proc.stdout.strip()
    return json.loads(text) if text else None


def get_doc(doctype: str, name: str) -> dict[str, Any]:
    return bench_execute("frappe.client.get", kwargs={"doctype": doctype, "name": name})


def try_get_doc(doctype: str, name: str) -> dict[str, Any] | None:
    try:
        return get_doc(doctype, name)
    except RuntimeError as exc:
        if "DoesNotExistError" in str(exc):
            return None
        raise


def decode_filters(value: str | None) -> Any:
    if not value:
        return []
    return json.loads(value)


def check_calendar_view() -> list[str]:
    failures = []
    calendar = get_doc("Calendar View", "Sales Order")
    expected = {
        "reference_doctype": "Sales Order",
        "subject_field": "customer_name",
        "start_date_field": "delivery_date",
        "end_date_field": "delivery_date",
    }
    for key, value in expected.items():
        if calendar.get(key) != value:
            failures.append(f"Calendar View/Sales Order {key} expected {value!r}, found {calendar.get(key)!r}")
    return failures


def check_workspace(name: str, expected: dict[str, tuple[str, str]]) -> list[str]:
    failures = []
    workspace = get_doc("Workspace", name)
    shortcuts = {row["label"]: row for row in workspace.get("shortcuts", [])}
    content = json.loads(workspace.get("content") or "[]")
    content_labels = {
        (block.get("data") or {}).get("shortcut_name")
        for block in content
        if block.get("type") == "shortcut"
    }

    stale_found = sorted((set(shortcuts) | content_labels) & STALE_LABELS)
    if stale_found:
        failures.append(f"{name} still shows stale labels: {', '.join(stale_found)}")

    for label, (doctype, view) in expected.items():
        shortcut = shortcuts.get(label)
        if not shortcut:
            failures.append(f"{name} missing shortcut {label!r}")
            continue
        if label not in content_labels:
            failures.append(f"{name} content missing shortcut block {label!r}")
        if shortcut.get("link_to") != doctype or shortcut.get("doc_view") != view:
            failures.append(
                f"{name} {label!r} expected {doctype}/{view}, found "
                f"{shortcut.get('link_to')}/{shortcut.get('doc_view')}"
            )
    return failures


def check_owner_command_center() -> list[str]:
    failures = []
    workspace = get_doc("Workspace", "LT Owner Home")
    content = json.loads(workspace.get("content") or "[]")
    content_text = json.dumps(content)

    for text in OWNER_HOME_TEXT:
        if text not in content_text:
            failures.append(f"LT Owner Home content missing text {text!r}")

    number_card_blocks = {
        (block.get("data") or {}).get("number_card_name")
        for block in content
        if block.get("type") == "number_card"
    }
    workspace_number_cards = {
        row["number_card_name"]: row.get("label")
        for row in workspace.get("number_cards", [])
    }

    for name, expected in OWNER_HOME_NUMBER_CARDS.items():
        card = try_get_doc("Number Card", name)
        if not card:
            failures.append(f"Missing Number Card {name!r}")
            continue
        for key in ("label", "document_type", "function"):
            if card.get(key) != expected[key]:
                failures.append(
                    f"Number Card {name!r} {key} expected {expected[key]!r}, found {card.get(key)!r}"
                )
        if decode_filters(card.get("filters_json")) != expected["filters_json"]:
            failures.append(
                f"Number Card {name!r} filters expected {expected['filters_json']!r}, "
                f"found {decode_filters(card.get('filters_json'))!r}"
            )
        if name not in workspace_number_cards:
            failures.append(f"LT Owner Home missing number card child row {name!r}")
        if name not in number_card_blocks:
            failures.append(f"LT Owner Home content missing number card block {name!r}")

    chart = try_get_doc("Dashboard Chart", OWNER_HOME_CHART["name"])
    if not chart:
        failures.append(f"Missing Dashboard Chart {OWNER_HOME_CHART['name']!r}")
    else:
        for key, value in OWNER_HOME_CHART.items():
            if key == "name":
                continue
            if chart.get(key) != value:
                failures.append(
                    f"Dashboard Chart {OWNER_HOME_CHART['name']!r} {key} expected {value!r}, "
                    f"found {chart.get(key)!r}"
                )

    workspace_charts = {row["chart_name"]: row.get("label") for row in workspace.get("charts", [])}
    chart_blocks = {
        (block.get("data") or {}).get("chart_name")
        for block in content
        if block.get("type") == "chart"
    }
    if OWNER_HOME_CHART["name"] not in workspace_charts:
        failures.append(f"LT Owner Home missing chart child row {OWNER_HOME_CHART['name']!r}")
    if OWNER_HOME_CHART["name"] not in chart_blocks:
        failures.append(f"LT Owner Home content missing chart block {OWNER_HOME_CHART['name']!r}")

    return failures


def main() -> int:
    failures = []
    failures.extend(check_calendar_view())
    for name, expected in EXPECTED_WORKSPACE_SHORTCUTS.items():
        failures.extend(check_workspace(name, expected))
    failures.extend(check_owner_command_center())

    if failures:
        print("[BACKEND WORKSPACE PARITY] FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("[BACKEND WORKSPACE PARITY] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
