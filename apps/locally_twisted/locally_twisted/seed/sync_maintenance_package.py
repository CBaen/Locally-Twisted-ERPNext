"""Sync sanitized Maintenance Admin role, report, and workspace.

Run in-process:
  bench --site frontend execute locally_twisted.seed.sync_maintenance_package.execute
"""
from __future__ import annotations

import json

import frappe

from locally_twisted.maintenance import heartbeat
from locally_twisted.seed.standard_report_import import standard_report_import_context


MAINTENANCE_ROLE = heartbeat.MAINTENANCE_ROLE
WORKSPACE_NAME = heartbeat.MAINTENANCE_WORKSPACE
REPORT_NAME = heartbeat.HEARTBEAT_REPORT
REPORT_REF_DOCTYPE = heartbeat.RUN_DOCTYPE

READ_ONLY_PERMS = {
    "read": 1,
    "report": 1,
    "export": 1,
    "print": 1,
}
CREATE_LOG_PERMS = {
    "create": 1,
    "read": 1,
    "report": 1,
    "export": 1,
    "print": 1,
}
REQUEST_PERMS = {
    "create": 1,
    "read": 1,
    "write": 1,
    "report": 1,
    "export": 1,
    "print": 1,
}

PERMISSION_PLAN = {
    heartbeat.RUN_DOCTYPE: READ_ONLY_PERMS,
    heartbeat.EVENT_DOCTYPE: READ_ONLY_PERMS,
    heartbeat.ACTION_REQUEST_DOCTYPE: REQUEST_PERMS,
    heartbeat.ACTION_LOG_DOCTYPE: CREATE_LOG_PERMS,
}

SHORTCUTS = [
    {
        "label": "Maintenance Heartbeat",
        "type": "Report",
        "link_to": REPORT_NAME,
        "report_ref_doctype": REPORT_REF_DOCTYPE,
        "color": "Blue",
    },
    {
        "label": "Maintenance Runs",
        "type": "DocType",
        "link_to": heartbeat.RUN_DOCTYPE,
        "doc_view": "List",
        "color": "Blue",
    },
    {
        "label": "Maintenance Events",
        "type": "DocType",
        "link_to": heartbeat.EVENT_DOCTYPE,
        "doc_view": "List",
        "color": "Orange",
    },
    {
        "label": "Action Requests",
        "type": "DocType",
        "link_to": heartbeat.ACTION_REQUEST_DOCTYPE,
        "doc_view": "List",
        "color": "Green",
    },
    {
        "label": "Action Logs",
        "type": "DocType",
        "link_to": heartbeat.ACTION_LOG_DOCTYPE,
        "doc_view": "List",
        "color": "Grey",
    },
]


def execute() -> str:
    summary = {
        "ensured_role": False,
        "updated_doctype_permissions": [],
        "updated_reports": [],
        "updated_workspace": False,
        "boundary_ok": False,
        "boundary_failures": [],
    }
    _ensure_role(summary)
    for doctype, permissions in PERMISSION_PLAN.items():
        _ensure_doctype_permission(doctype, permissions, summary)
    _ensure_report(summary)
    _ensure_workspace(summary)
    boundary = heartbeat.boundary_report()
    summary["boundary_ok"] = bool(boundary.get("ok"))
    summary["boundary_failures"] = boundary.get("failures") or []
    frappe.clear_cache()
    frappe.db.commit()
    print(json.dumps(summary, indent=2, sort_keys=True))
    return json.dumps(summary, sort_keys=True)


def _ensure_role(summary: dict) -> None:
    if frappe.db.exists("Role", MAINTENANCE_ROLE):
        doc = frappe.get_doc("Role", MAINTENANCE_ROLE)
        changed = _set_fields(doc, {"desk_access": 1, "disabled": 0})
        if changed:
            doc.save(ignore_permissions=True)
            summary["ensured_role"] = True
        return

    frappe.get_doc(
        {
            "doctype": "Role",
            "role_name": MAINTENANCE_ROLE,
            "desk_access": 1,
            "disabled": 0,
        }
    ).insert(ignore_permissions=True)
    summary["ensured_role"] = True


def _ensure_doctype_permission(doctype: str, desired: dict[str, int], summary: dict) -> None:
    if not frappe.db.exists("DocType", doctype):
        summary.setdefault("boundary_failures", []).append(f"Missing DocType {doctype}")
        return

    all_permission_fields = (
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
        "print",
        "email",
        "share",
    )
    fields = {
        field: 1 if desired.get(field) else 0
        for field in all_permission_fields
    }
    fields.update({"role": MAINTENANCE_ROLE, "permlevel": 0})

    row_name = frappe.db.exists(
        "DocPerm",
        {"parent": doctype, "parenttype": "DocType", "role": MAINTENANCE_ROLE, "permlevel": 0},
    )
    if row_name:
        current = frappe.get_doc("DocPerm", row_name)
        changed = False
        for field, value in fields.items():
            if getattr(current, field, 0) != value:
                changed = True
                break
        if changed:
            frappe.db.set_value("DocPerm", row_name, fields, update_modified=False)
            frappe.clear_cache(doctype=doctype)
            summary["updated_doctype_permissions"].append(doctype)
        return

    idx = (
        frappe.db.sql(
            "select coalesce(max(idx), 0) from `tabDocPerm` where parent = %s",
            doctype,
        )[0][0]
        + 1
    )
    name = frappe.generate_hash(length=10)
    frappe.db.sql(
        """
        insert into `tabDocPerm`
            (`name`, `creation`, `modified`, `modified_by`, `owner`, `docstatus`, `idx`,
             `parent`, `parentfield`, `parenttype`, `role`, `permlevel`,
             `read`, `write`, `create`, `delete`, `submit`, `cancel`, `amend`,
             `report`, `export`, `import`, `print`, `email`, `share`)
        values
            (%(name)s, now(), now(), %(user)s, %(user)s, 0, %(idx)s,
             %(parent)s, 'permissions', 'DocType', %(role)s, 0,
             %(read)s, %(write)s, %(create)s, %(delete)s, %(submit)s, %(cancel)s, %(amend)s,
             %(report)s, %(export)s, %(import)s, %(print)s, %(email)s, %(share)s)
        """,
        {
            "name": name,
            "user": frappe.session.user or "Administrator",
            "idx": idx,
            "parent": doctype,
            **fields,
        },
    )
    frappe.clear_cache(doctype=doctype)
    summary["updated_doctype_permissions"].append(doctype)


def _ensure_report(summary: dict) -> None:
    if frappe.db.exists("Report", REPORT_NAME):
        doc = frappe.get_doc("Report", REPORT_NAME)
        is_new = False
        changed = False
    else:
        doc = frappe.get_doc({"doctype": "Report", "name": REPORT_NAME})
        is_new = True
        changed = True

    fields = {
        "report_name": REPORT_NAME,
        "ref_doctype": REPORT_REF_DOCTYPE,
        "is_standard": "Yes",
        "module": "Locally Twisted",
        "report_type": "Script Report",
        "disabled": 0,
        "prepared_report": 0,
        "add_total_row": 0,
    }
    changed = _set_fields(doc, fields) or changed

    desired_roles = [{"role": MAINTENANCE_ROLE}, {"role": "System Manager"}]
    if _child_table_rows(doc.roles, ["role"]) != desired_roles:
        doc.set("roles", [])
        for row in desired_roles:
            doc.append("roles", row)
        changed = True

    if is_new:
        with standard_report_import_context():
            doc.insert(ignore_permissions=True)
        summary["updated_reports"].append(REPORT_NAME)
    elif changed:
        with standard_report_import_context():
            doc.save(ignore_permissions=True)
        summary["updated_reports"].append(REPORT_NAME)


def _ensure_workspace(summary: dict) -> None:
    if frappe.db.exists("Workspace", WORKSPACE_NAME):
        doc = frappe.get_doc("Workspace", WORKSPACE_NAME)
        changed = False
    else:
        doc = frappe.get_doc(
            {
                "doctype": "Workspace",
                "name": WORKSPACE_NAME,
                "label": WORKSPACE_NAME,
                "title": "Maintenance Home",
                "module": "Locally Twisted",
                "icon": "tool",
                "indicator_color": "blue",
                "public": 1,
                "is_hidden": 0,
                "hide_custom": 1,
            }
        )
        doc.insert(ignore_permissions=True)
        changed = True

    fields = {
        "label": WORKSPACE_NAME,
        "title": "Maintenance Home",
        "module": "Locally Twisted",
        "icon": "tool",
        "indicator_color": "blue",
        "public": 1,
        "is_hidden": 0,
        "hide_custom": 1,
    }
    changed = _set_fields(doc, fields) or changed
    changed = _ensure_workspace_role(doc) or changed
    changed = _ensure_shortcuts(doc, SHORTCUTS) or changed

    desired_content = _workspace_content()
    if _load_content(doc.content) != desired_content:
        doc.content = json.dumps(desired_content)
        changed = True

    if changed:
        doc.save(ignore_permissions=True)
        summary["updated_workspace"] = True


def _ensure_workspace_role(doc) -> bool:
    if MAINTENANCE_ROLE in {row.role for row in doc.roles}:
        return False
    doc.append("roles", {"role": MAINTENANCE_ROLE})
    return True


def _ensure_shortcuts(doc, desired_shortcuts: list[dict]) -> bool:
    changed = False
    existing_by_label = {row.label: row for row in doc.shortcuts}

    for spec in desired_shortcuts:
        row = existing_by_label.get(spec["label"])
        if row is None:
            row = doc.append("shortcuts", {})
            changed = True
        for key in (
            "label",
            "type",
            "link_to",
            "url",
            "doc_view",
            "kanban_board",
            "color",
            "format",
            "report_ref_doctype",
        ):
            value = spec.get(key)
            if _normalize_blank(getattr(row, key, None)) != _normalize_blank(value):
                setattr(row, key, value)
                changed = True
    return changed


def _workspace_content() -> list[dict]:
    blocks = [
        _header(
            "lt-maintenance-title",
            '<span class="h4"><b>Maintenance Home</b></span>',
            12,
        ),
        _header(
            "lt-maintenance-subtitle",
            '<span class="text-muted">Sanitized heartbeat, action requests, and explanation logs only. Raw logs and customer records stay outside this role.</span>',
            12,
        ),
    ]
    for idx, shortcut in enumerate(SHORTCUTS, start=1):
        blocks.append(_shortcut(f"lt-maintenance-shortcut-{idx}", shortcut["label"], 3))
    return blocks


def _set_fields(doc, fields: dict) -> bool:
    changed = False
    for key, value in fields.items():
        if _normalize_blank(getattr(doc, key, None)) != _normalize_blank(value):
            setattr(doc, key, value)
            changed = True
    return changed


def _child_table_rows(rows, fields: list[str]) -> list[dict]:
    return [{field: getattr(row, field, None) for field in fields} for row in rows]


def _normalize_blank(value):
    return None if value in ("", None) else value


def _header(block_id: str, text: str, col: int) -> dict:
    return {"id": block_id, "type": "header", "data": {"text": text, "col": col}}


def _shortcut(block_id: str, shortcut_name: str, col: int) -> dict:
    return {
        "id": block_id,
        "type": "shortcut",
        "data": {"shortcut_name": shortcut_name, "col": col},
    }


def _load_content(value: str | None) -> list[dict]:
    if not value:
        return []
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return []
    return parsed if isinstance(parsed, list) else []
