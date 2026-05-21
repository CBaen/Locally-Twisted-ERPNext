"""Verify persona workspace shortcuts match each user's real permissions."""
from __future__ import annotations

import json

import frappe


PERSONA_WORKSPACES = {
    "lt-owner-temp@example.com": "LT Owner Home",
    "lt-manager-temp@example.com": "LT Manager Home",
    "lt-employee-temp@example.com": "LT Employee Home",
}

READ_VIEWS = {"Calendar", "Gantt", "Kanban", "List", "Report", "Tree"}
CREATE_VIEWS = {"New"}


def run() -> dict[str, object]:
    failures = []
    checked = []
    skipped = []

    for user, workspace_name in PERSONA_WORKSPACES.items():
        if not frappe.db.exists("User", user):
            skipped.append(
                {
                    "user": user,
                    "workspace": workspace_name,
                    "reason": "temp persona user is not provisioned",
                }
            )
            continue
        if not frappe.db.exists("Workspace", workspace_name):
            failures.append(f"{workspace_name} does not exist")
            continue

        workspace = frappe.get_doc("Workspace", workspace_name)
        shortcuts = {row.label: row for row in workspace.shortcuts}
        for label in _visible_shortcut_labels(workspace):
            shortcut = shortcuts.get(label)
            if not shortcut:
                failures.append(f"{workspace_name} content shows {label!r} but no shortcut row exists")
                continue

            checks = _permission_checks(shortcut)
            for target_type, target_name, ptype in checks:
                checked.append(
                    {
                        "user": user,
                        "workspace": workspace_name,
                        "shortcut": label,
                        "target_type": target_type,
                        "target_name": target_name,
                        "permission": ptype,
                    }
                )
                if not _has_permission(user, target_type, target_name, ptype):
                    failures.append(
                        f"{workspace_name} shows {label!r} to {user}, but {user} lacks "
                        f"{ptype} permission on {target_type} {target_name!r}"
                    )

    return {"ok": not failures, "checked": checked, "skipped": skipped, "failures": failures}


def _visible_shortcut_labels(workspace) -> list[str]:
    labels = []
    for block in _load_content(workspace.content):
        if block.get("type") != "shortcut":
            continue
        label = (block.get("data") or {}).get("shortcut_name")
        if label and label not in labels:
            labels.append(label)
    return labels


def _permission_checks(shortcut) -> list[tuple[str, str, str]]:
    if shortcut.type == "DocType" and shortcut.link_to:
        if shortcut.doc_view in CREATE_VIEWS:
            return [("DocType", shortcut.link_to, "create")]
        if not shortcut.doc_view or shortcut.doc_view in READ_VIEWS:
            return [("DocType", shortcut.link_to, "read")]
    if shortcut.type == "Report" and shortcut.link_to:
        checks = [("Report", shortcut.link_to, "read")]
        if shortcut.report_ref_doctype:
            checks.append(("DocType", shortcut.report_ref_doctype, "read"))
        return checks
    if shortcut.type == "Page" and shortcut.link_to:
        return [("Page", shortcut.link_to, "read")]
    return []


def _has_permission(user: str, target_type: str, target_name: str, ptype: str) -> bool:
    if target_type == "DocType":
        return bool(frappe.has_permission(target_name, ptype=ptype, user=user))
    if not frappe.db.exists(target_type, target_name):
        return False
    doc = frappe.get_doc(target_type, target_name)
    return bool(frappe.has_permission(target_type, doc=doc, ptype=ptype, user=user))


def _load_content(value: str | None) -> list[dict]:
    if not value:
        return []
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return []
    return parsed if isinstance(parsed, list) else []
