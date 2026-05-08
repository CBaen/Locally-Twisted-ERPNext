"""Desk report adapter for the sanitized LT maintenance heartbeat."""
from __future__ import annotations

from locally_twisted.maintenance import heartbeat


COLUMNS = [
    {
        "label": "Component",
        "fieldname": "component",
        "fieldtype": "Data",
        "width": 220,
    },
    {
        "label": "Status",
        "fieldname": "status",
        "fieldtype": "Data",
        "width": 90,
    },
    {
        "label": "Severity",
        "fieldname": "severity",
        "fieldtype": "Data",
        "width": 100,
    },
    {
        "label": "Safe Summary",
        "fieldname": "safe_summary",
        "fieldtype": "Small Text",
        "width": 320,
    },
    {
        "label": "Action Needed",
        "fieldname": "action_needed",
        "fieldtype": "Small Text",
        "width": 360,
    },
    {
        "label": "Source",
        "fieldname": "source",
        "fieldtype": "Data",
        "width": 180,
    },
]


def execute(filters=None):
    """Return sanitized heartbeat rows for Frappe's Script Report runner."""
    result = heartbeat.run(include_heavy=False, write=False)
    rows = []
    for event in result.get("events") or []:
        rows.append(
            {
                "component": event.get("component"),
                "status": str(event.get("status") or "").title(),
                "severity": str(event.get("severity") or "").title(),
                "safe_summary": event.get("safe_summary"),
                "action_needed": event.get("action_needed"),
                "source": event.get("source"),
            }
        )
    return COLUMNS, rows
