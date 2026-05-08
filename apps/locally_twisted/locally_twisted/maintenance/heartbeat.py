"""Sanitized client operations heartbeat.

This module intentionally summarizes health state without exposing customer
records, payment references, raw tracebacks, IP addresses, or message bodies.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import frappe
from frappe.utils import now_datetime


DIGEST_TYPE = "client_operations_heartbeat"
BOOT_INCLUDE = "templates/includes/frappe_public_boot.html"
MAINTENANCE_ROLE = "LT Maintenance Admin Access"
RUN_DOCTYPE = "LT Maintenance Run"
EVENT_DOCTYPE = "LT Maintenance Health Event"
ACTION_REQUEST_DOCTYPE = "LT Maintenance Action Request"
ACTION_LOG_DOCTYPE = "LT Maintenance Action Log"
PREFERENCE_DOCTYPE = "LT Client Notification Preference"
HEARTBEAT_REPORT = "LT Maintenance Heartbeat"
MAINTENANCE_WORKSPACE = "LT Maintenance Home"

MAINTENANCE_READ_DOCTYPES = (
    RUN_DOCTYPE,
    EVENT_DOCTYPE,
    ACTION_REQUEST_DOCTYPE,
    ACTION_LOG_DOCTYPE,
)

FORBIDDEN_MAINTENANCE_DOCTYPES = (
    "Error Log",
    "Activity Log",
    "Access Log",
    "Version",
    "Communication",
    "Comment",
    "Email Queue",
    "Lead",
    "Customer",
    "Contact",
    "Address",
    "Sales Order",
    "Sales Invoice",
    "Payment Request",
    "Payment Entry",
    "File",
    PREFERENCE_DOCTYPE,
)

NOTIFICATION_TOPICS = (
    "System Health",
    "New Leads",
    "Stale Leads",
    "Appointments",
    "Payments Paid",
    "Payments Late",
    "Documents Due",
    "Failed Automations",
    "Website Errors",
    "Security Events",
)

PERMISSION_TIERS = (
    {
        "tier": 0,
        "label": "Observe / report only",
        "requires_approval": False,
        "customer_delivery_allowed": False,
        "money_or_accounting_mutation_allowed": False,
    },
    {
        "tier": 1,
        "label": "Draft / internal review only",
        "requires_approval": False,
        "customer_delivery_allowed": False,
        "money_or_accounting_mutation_allowed": False,
    },
    {
        "tier": 2,
        "label": "Safe metadata/blocker repair",
        "requires_approval": True,
        "customer_delivery_allowed": False,
        "money_or_accounting_mutation_allowed": False,
    },
    {
        "tier": 3,
        "label": "Idempotent app-owned setup repair",
        "requires_approval": True,
        "customer_delivery_allowed": False,
        "money_or_accounting_mutation_allowed": False,
    },
    {
        "tier": 4,
        "label": "Live customer/money/data action",
        "requires_approval": True,
        "customer_delivery_allowed": True,
        "money_or_accounting_mutation_allowed": True,
    },
)


def run(include_heavy: bool = True, write: bool = False) -> dict[str, Any]:
    """Return a JSON-safe heartbeat payload and optionally persist sanitized rows."""
    started = now_datetime()
    events = [
        _public_boot_event(),
        _scheduler_event(),
        _notification_preferences_event(),
        _maintenance_role_event(),
    ]
    if include_heavy:
        events.extend(
            [
                _business_automation_event(),
                _paperwork_digest_event(),
            ]
        )

    result = {
        "ok": not any(event["status"] == "red" for event in events),
        "generated_at": started.isoformat(),
        "digest_type": DIGEST_TYPE,
        "read_only": True,
        "send_allowed": False,
        "mutation_allowed": False,
        "customer_delivery_enabled": False,
        "automatic_delivery_enabled": False,
        "sanitized": True,
        "raw_log_access": False,
        "customer_data_included": False,
        "include_heavy": include_heavy,
        "notification_topics_available": list(NOTIFICATION_TOPICS),
        "permission_tiers": list(PERMISSION_TIERS),
        "summary": _summary(events),
        "events": events,
        "next_safe_actions": _next_safe_actions(events),
        "failures": [event["safe_summary"] for event in events if event["status"] == "red"],
    }
    if write:
        _write_result(result)
    return result


def scheduled_light_checkup() -> None:
    """Hourly-safe scheduled checkup: no heavy fake-data/synthetic surfaces."""
    run(include_heavy=False, write=True)


def scheduled_full_checkup() -> None:
    """Daily scheduled checkup with sanitized persistence and compact Error Log evidence."""
    result = run(include_heavy=True, write=True)
    if not result.get("ok"):
        frappe.log_error(
            title="LT maintenance heartbeat needs attention",
            message=json.dumps(_log_payload(result), indent=2, default=str),
        )


def scheduled_checkup() -> None:
    """Compatibility alias for scheduler/manual calls."""
    scheduled_full_checkup()


def boundary_report() -> dict[str, Any]:
    """Return the sanitized Maintenance Admin access boundary state."""
    allowed = []
    forbidden = []
    failures = []

    role_exists = bool(frappe.db.exists("Role", MAINTENANCE_ROLE))
    if not role_exists:
        failures.append(f"Missing Role {MAINTENANCE_ROLE}")

    for doctype in MAINTENANCE_READ_DOCTYPES:
        doctype_exists = bool(frappe.db.exists("DocType", doctype))
        can_read = _role_can_read(doctype, MAINTENANCE_ROLE)
        allowed.append({"doctype": doctype, "exists": doctype_exists, "can_read": can_read})
        if not doctype_exists:
            failures.append(f"Missing DocType {doctype}")
        elif not can_read:
            failures.append(f"{MAINTENANCE_ROLE} cannot read {doctype}")

    for doctype in FORBIDDEN_MAINTENANCE_DOCTYPES:
        doctype_exists = bool(frappe.db.exists("DocType", doctype))
        can_read = _role_can_read(doctype, MAINTENANCE_ROLE)
        forbidden.append({"doctype": doctype, "exists": doctype_exists, "can_read": can_read})
        if can_read:
            failures.append(f"{MAINTENANCE_ROLE} can read forbidden DocType {doctype}")

    report_roles = []
    if frappe.db.exists("Report", HEARTBEAT_REPORT):
        report = frappe.get_doc("Report", HEARTBEAT_REPORT)
        report_roles = [row.role for row in report.roles]
        if MAINTENANCE_ROLE not in report_roles:
            failures.append(f"{HEARTBEAT_REPORT} missing {MAINTENANCE_ROLE} role")
    else:
        failures.append(f"Missing Report {HEARTBEAT_REPORT}")

    workspace_roles = []
    workspace_shortcuts = []
    if frappe.db.exists("Workspace", MAINTENANCE_WORKSPACE):
        workspace = frappe.get_doc("Workspace", MAINTENANCE_WORKSPACE)
        workspace_roles = [row.role for row in workspace.roles]
        workspace_shortcuts = [
            {
                "label": row.label,
                "type": row.type,
                "link_to": row.link_to,
                "url": row.url,
                "doc_view": row.doc_view,
            }
            for row in workspace.shortcuts
        ]
        if MAINTENANCE_ROLE not in workspace_roles:
            failures.append(f"{MAINTENANCE_WORKSPACE} missing {MAINTENANCE_ROLE} role")
        forbidden_shortcuts = [
            row
            for row in workspace_shortcuts
            if row.get("link_to") in FORBIDDEN_MAINTENANCE_DOCTYPES or row.get("url")
        ]
        if forbidden_shortcuts:
            failures.append(f"{MAINTENANCE_WORKSPACE} contains forbidden shortcut(s)")
    else:
        failures.append(f"Missing Workspace {MAINTENANCE_WORKSPACE}")

    if frappe.db.exists("Role Profile", "LT Maintenance Admin"):
        failures.append("LT Maintenance Admin must be a role, not a Role Profile")

    return {
        "ok": not failures,
        "generated_at": now_datetime().isoformat(),
        "role": MAINTENANCE_ROLE,
        "role_exists": role_exists,
        "sanitized": True,
        "customer_data_included": False,
        "raw_log_access": False,
        "allowed_doctypes": allowed,
        "forbidden_doctypes": forbidden,
        "report_roles": report_roles,
        "workspace_roles": workspace_roles,
        "workspace_shortcuts": workspace_shortcuts,
        "failures": failures,
    }


def _public_boot_event() -> dict[str, Any]:
    failures: list[str] = []
    templates = Path(frappe.get_app_path("locally_twisted")) / "templates"
    include_path = templates / "includes" / "frappe_public_boot.html"
    if not include_path.exists():
        failures.append("shared public boot include is missing")
    else:
        text = include_path.read_text(encoding="utf-8")
        for marker in ("frappe.boot =", "frappe.boot.assets_json", "frappe.sys_defaults"):
            if marker not in text:
                failures.append(f"shared public boot include missing {marker}")

    block_re = re.compile(r"{%\s*block\s+base_scripts\s*%}(?P<body>.*?){%\s*endblock\s*%}", re.DOTALL)
    for path in templates.rglob("*.html"):
        text = path.read_text(encoding="utf-8")
        for match in block_re.finditer(text):
            body = match.group("body")
            if "frappe-web.bundle.js" in body and BOOT_INCLUDE not in body:
                failures.append(f"{path.relative_to(templates)} bypasses shared boot include")

    return _event(
        "public_boot_asset_map",
        "Public Frappe boot asset map",
        failures,
        "public_route_runtime",
        "Use the shared public boot include before loading Frappe bundles.",
    )


def _scheduler_event() -> dict[str, Any]:
    failures: list[str] = []
    hooks = frappe.get_hooks("scheduler_events")
    text = json.dumps(hooks, default=str)
    for marker in (
        "locally_twisted.maintenance.heartbeat.scheduled_light_checkup",
        "locally_twisted.maintenance.heartbeat.scheduled_full_checkup",
    ):
        if marker not in text:
            failures.append(f"scheduler missing {marker.rsplit('.', 1)[-1]}")
    return _event(
        "maintenance_scheduler",
        "Maintenance heartbeat scheduler",
        failures,
        "scheduled_operations",
        "Keep light hourly and full daily heartbeat hooks registered.",
    )


def _notification_preferences_event() -> dict[str, Any]:
    failures: list[str] = []
    active_count = 0
    cadence_count = 0
    if not frappe.db.exists("DocType", PREFERENCE_DOCTYPE):
        failures.append("notification preference doctype missing")
    else:
        active_count = frappe.db.count(PREFERENCE_DOCTYPE, {"enabled": 1})
        rows = frappe.get_all(
            PREFERENCE_DOCTYPE,
            filters={"enabled": 1},
            fields=["cadence"],
            limit_page_length=100,
        )
        cadence_count = len({row.get("cadence") for row in rows if row.get("cadence")})
    event = _event(
        "client_notification_preferences",
        "Client notification preferences",
        failures,
        "client_digest_preferences",
        "Configure owner-selected topics, channels, and cadence before enabling delivery.",
        status_override="yellow" if not failures and active_count == 0 else None,
    )
    event["safe_metrics"] = {
        "active_preference_count": active_count,
        "active_cadence_count": cadence_count,
    }
    return event


def _maintenance_role_event() -> dict[str, Any]:
    report = boundary_report()
    failures = list(report.get("failures") or [])
    return _event(
        "maintenance_role_boundary",
        "Maintenance Admin sanitized access boundary",
        failures,
        "permissions",
        "Expose only sanitized maintenance records; raw Frappe logs stay owner/admin-only.",
    )


def _business_automation_event() -> dict[str, Any]:
    try:
        from locally_twisted.verify import business_automation_index

        result = business_automation_index.run(
            include_digest=False,
            include_synthetic=False,
            include_customer_reminders=False,
            include_customer_reminder_report=False,
        )
    except Exception as exc:  # pragma: no cover - surfaced in heartbeat
        return _event(
            "business_automation_index",
            "Business automation index",
            [f"{type(exc).__name__}: {exc}"],
            "business_operations",
            "Repair the automation index runner before trusting business digest status.",
        )

    failures = []
    if result.get("read_only") is not True:
        failures.append("business automation index is not marked read-only")
    if result.get("ok") is not True:
        failures.append("business automation index reports required failures")

    event = _event(
        "business_automation_index",
        "Business automation index",
        failures,
        "business_operations",
        "Review launch-required failures through owner/admin access.",
        status_override="yellow" if result.get("exists_but_not_connected") else None,
    )
    summary = result.get("summary") or {}
    event["safe_metrics"] = {
        "surface_count": summary.get("surface_count", 0),
        "connected_count": summary.get("connected_count", 0),
        "partial_connection_count": len(result.get("exists_but_not_connected") or []),
        "missing_required_count": len(result.get("missing_needs_connection") or []),
        "record_level_failure_count": len(result.get("record_level_failures") or []),
    }
    return event


def _paperwork_digest_event() -> dict[str, Any]:
    try:
        from locally_twisted.paperwork import paperwork_review_digest

        result = paperwork_review_digest.run()
    except Exception as exc:  # pragma: no cover - surfaced in heartbeat
        return _event(
            "paperwork_review_digest",
            "Paperwork review digest",
            [f"{type(exc).__name__}: {exc}"],
            "business_digest",
            "Repair the paperwork digest runner before enabling owner digest delivery.",
        )

    failures = []
    if result.get("read_only") is not True:
        failures.append("paperwork digest is not read-only")
    if result.get("send_allowed") is not False:
        failures.append("paperwork digest allows customer sending")
    if result.get("mutation_allowed") is not False:
        failures.append("paperwork digest allows mutations")
    if result.get("ok") is not True:
        failures.append("paperwork digest returned not ok")

    event = _event(
        "paperwork_review_digest",
        "Paperwork review digest",
        failures,
        "business_digest",
        "Keep digest internal until recipient, cadence, and copy approvals exist.",
    )
    sections = result.get("sections") or {}
    event["safe_metrics"] = {
        key: (sections.get(key) or {}).get("count", 0)
        for key in (
            "unpaid_invoice_packets",
            "cutover_deferred_not_blocking",
            "setup_gaps",
            "partial_connections",
            "next_safe_actions",
        )
    }
    return event


def _event(
    component: str,
    label: str,
    failures: list[str],
    source: str,
    action_needed: str,
    *,
    status_override: str | None = None,
) -> dict[str, Any]:
    if failures:
        status = "red"
        severity = "critical"
        summary = f"{label} needs attention"
    else:
        status = status_override or "green"
        severity = "warning" if status == "yellow" else "info"
        summary = f"{label} is configured" if status == "green" else f"{label} needs owner setup"
    return {
        "component": component,
        "status": status,
        "severity": severity,
        "safe_summary": summary,
        "action_needed": action_needed,
        "source": source,
        "check_id": component,
        "detail_count": len(failures),
        "safe_details": failures[:5],
        "sanitized": True,
        "customer_data_included": False,
        "raw_log_access": False,
        "approval_required": status != "green",
    }


def _summary(events: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "event_count": len(events),
        "green_count": sum(1 for event in events if event["status"] == "green"),
        "yellow_count": sum(1 for event in events if event["status"] == "yellow"),
        "red_count": sum(1 for event in events if event["status"] == "red"),
    }


def _next_safe_actions(events: list[dict[str, Any]]) -> list[str]:
    actions = [event["action_needed"] for event in events if event["status"] != "green"]
    return actions or ["No operator action needed from the sanitized heartbeat."]


def _write_result(result: dict[str, Any]) -> None:
    if not frappe.db.exists("DocType", RUN_DOCTYPE) or not frappe.db.exists("DocType", EVENT_DOCTYPE):
        return
    run_id = frappe.generate_hash(length=12)
    run_doc = frappe.get_doc(
        {
            "doctype": RUN_DOCTYPE,
            "run_id": run_id,
            "generated_at": result["generated_at"],
            "status": "Pass" if result.get("ok") else "Needs Attention",
            "severity": "Info" if result.get("ok") else "Critical",
            "event_count": result["summary"]["event_count"],
            "failure_count": result["summary"]["red_count"],
            "sanitized": 1,
            "customer_data_included": 0,
            "raw_log_access": 0,
            "digest_type": result["digest_type"],
            "digest_json": json.dumps(_storage_payload(result), indent=2, default=str),
        }
    )
    run_doc.insert(ignore_permissions=True)
    for event in result["events"]:
        frappe.get_doc(
            {
                "doctype": EVENT_DOCTYPE,
                "run_id": run_id,
                "generated_at": result["generated_at"],
                "component": event["component"],
                "status": event["status"].title(),
                "severity": event["severity"].title(),
                "safe_summary": event["safe_summary"],
                "action_needed": event["action_needed"],
                "source": event["source"],
                "check_id": event["check_id"],
                "detail_count": event["detail_count"],
                "sanitized": 1,
                "customer_data_included": 0,
                "raw_log_access": 0,
                "approval_required": 1 if event["approval_required"] else 0,
            }
        ).insert(ignore_permissions=True)
    frappe.db.commit()


def _storage_payload(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "generated_at": result.get("generated_at"),
        "digest_type": result.get("digest_type"),
        "summary": result.get("summary"),
        "events": [
            {
                "component": event.get("component"),
                "status": event.get("status"),
                "severity": event.get("severity"),
                "safe_summary": event.get("safe_summary"),
                "action_needed": event.get("action_needed"),
                "source": event.get("source"),
            }
            for event in result.get("events", [])
        ],
    }


def _log_payload(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "generated_at": result.get("generated_at"),
        "digest_type": result.get("digest_type"),
        "summary": result.get("summary"),
        "failures": result.get("failures"),
        "next_safe_actions": result.get("next_safe_actions"),
        "sanitized": True,
        "raw_log_access": False,
        "customer_data_included": False,
    }


def _role_can_read(doctype: str, role: str) -> bool:
    if not frappe.db.exists("DocType", doctype) or not frappe.db.exists("Role", role):
        return False
    return bool(
        frappe.get_all(
            "DocPerm",
            filters={"parent": doctype, "role": role, "read": 1},
            limit_page_length=1,
        )
    )
