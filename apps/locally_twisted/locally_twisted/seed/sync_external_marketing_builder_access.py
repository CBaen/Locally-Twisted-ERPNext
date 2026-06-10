"""Sync controlled external marketing builder access.

Run in-process:
  bench --site frontend execute locally_twisted.seed.sync_external_marketing_builder_access.execute
"""
from __future__ import annotations

import json

import frappe

from locally_twisted.external_marketing_builder_access import (
    EXTERNAL_MARKETING_BUILDER_ROLE,
    EXTERNAL_MARKETING_WORKSPACE,
    TRACKING_SETTINGS_DOCTYPE,
    builder_role_boundary,
)


DOC_PERMS = {
    "Web Page": {"read": 1, "write": 1, "create": 1, "delete": 0, "export": 1, "report": 1},
    "Website Item": {"read": 1, "write": 1, "create": 0, "delete": 0, "export": 1, "report": 1},
    "Web Template": {"read": 1, "write": 0, "create": 0, "delete": 0, "export": 0, "report": 0},
    "Website Theme": {"read": 1, "write": 0, "create": 0, "delete": 0, "export": 0, "report": 0},
    TRACKING_SETTINGS_DOCTYPE: {"read": 1, "write": 1, "create": 0, "delete": 0, "export": 1, "report": 1},
}

WORKSPACE_SHORTCUTS = [
    {"label": "Landing Pages", "type": "DocType", "link_to": "Web Page", "doc_view": "List", "color": "Blue"},
    {"label": "Product Pages", "type": "DocType", "link_to": "Website Item", "doc_view": "List", "color": "Green"},
    {
        "label": "Tracking Settings",
        "type": "DocType",
        "link_to": TRACKING_SETTINGS_DOCTYPE,
        "doc_view": "List",
        "color": "Purple",
    },
    {"label": "Marketing Review", "type": "URL", "url": "/marketing-review", "color": "Purple"},
    {"label": "Live Site", "type": "URL", "url": "/", "color": "Blue"},
    {"label": "Shop", "type": "URL", "url": "/shop", "color": "Green"},
    {"label": "Contact", "type": "URL", "url": "/contact", "color": "Green"},
    {"label": "Sitemap", "type": "URL", "url": "/sitemap.xml", "color": "Grey"},
]


def execute(commit: bool = True) -> str:
    summary = {
        "ensured_role": False,
        "ensured_docperms": [],
        "removed_forbidden_docperms": [],
        "updated_workspace": False,
        "boundary_ok": False,
        "boundary_failures": [],
        "committed": False,
    }

    _ensure_role(summary)
    _ensure_docperms(summary)
    _remove_forbidden_docperms(summary)
    _ensure_workspace(summary)

    boundary = builder_role_boundary()
    summary["boundary_ok"] = bool(boundary.get("ok"))
    summary["boundary_failures"] = boundary.get("failures") or []

    frappe.clear_cache()
    if commit:
        frappe.db.commit()
        summary["committed"] = True

    print(json.dumps(summary, indent=2, sort_keys=True))
    return json.dumps(summary, sort_keys=True)


def _ensure_role(summary: dict) -> None:
    fields = {"role_name": EXTERNAL_MARKETING_BUILDER_ROLE, "desk_access": 1, "disabled": 0}
    if frappe.db.exists("Role", EXTERNAL_MARKETING_BUILDER_ROLE):
        doc = frappe.get_doc("Role", EXTERNAL_MARKETING_BUILDER_ROLE)
        changed = _set_fields(doc, fields)
        if changed:
            doc.save(ignore_permissions=True)
            summary["ensured_role"] = True
        return

    frappe.get_doc({"doctype": "Role", **fields}).insert(ignore_permissions=True)
    summary["ensured_role"] = True


def _ensure_docperms(summary: dict) -> None:
    for doctype, perms in DOC_PERMS.items():
        if not frappe.db.exists("DocType", doctype):
            continue
        row_name = frappe.db.exists(
            "DocPerm",
            {
                "parent": doctype,
                "parenttype": "DocType",
                "role": EXTERNAL_MARKETING_BUILDER_ROLE,
                "permlevel": 0,
            },
        )
        fields = {
            "parent": doctype,
            "parentfield": "permissions",
            "parenttype": "DocType",
            "role": EXTERNAL_MARKETING_BUILDER_ROLE,
            "permlevel": 0,
            "read": perms["read"],
            "write": perms["write"],
            "create": perms["create"],
            "delete": perms["delete"],
            "export": perms["export"],
            "report": perms["report"],
            "print": 1 if perms["read"] else 0,
            "email": 0,
            "share": 0,
            "submit": 0,
            "cancel": 0,
            "amend": 0,
            "if_owner": 0,
        }
        if row_name:
            doc = frappe.get_doc("DocPerm", row_name)
            if _set_fields(doc, fields):
                doc.save(ignore_permissions=True)
                summary["ensured_docperms"].append(doctype)
            continue

        frappe.get_doc({"doctype": "DocPerm", **fields}).insert(ignore_permissions=True)
        summary["ensured_docperms"].append(doctype)


def _remove_forbidden_docperms(summary: dict) -> None:
    allowed = set(DOC_PERMS)
    rows = frappe.db.get_all(
        "DocPerm",
        filters={"role": EXTERNAL_MARKETING_BUILDER_ROLE},
        fields=["name", "parent"],
        limit_page_length=500,
    )
    for row in rows:
        if row.parent in allowed:
            continue
        frappe.delete_doc("DocPerm", row.name, ignore_permissions=True)
        summary["removed_forbidden_docperms"].append(row.parent)


def _ensure_workspace(summary: dict) -> None:
    if frappe.db.exists("Workspace", EXTERNAL_MARKETING_WORKSPACE):
        doc = frappe.get_doc("Workspace", EXTERNAL_MARKETING_WORKSPACE)
        changed = False
    else:
        doc = frappe.get_doc(
            {
                "doctype": "Workspace",
                "name": EXTERNAL_MARKETING_WORKSPACE,
                "label": EXTERNAL_MARKETING_WORKSPACE,
                "title": "External Marketing Builder",
                "module": "Website",
                "icon": "website",
                "indicator_color": "purple",
                "public": 1,
                "is_hidden": 0,
                "hide_custom": 1,
            }
        )
        doc.insert(ignore_permissions=True)
        changed = True

    fields = {
        "label": EXTERNAL_MARKETING_WORKSPACE,
        "title": "External Marketing Builder",
        "module": "Website",
        "icon": "website",
        "indicator_color": "purple",
        "public": 1,
        "is_hidden": 0,
        "hide_custom": 1,
    }
    changed = _set_fields(doc, fields) or changed
    if _child_table_rows(doc.roles, ["role"]) != [{"role": EXTERNAL_MARKETING_BUILDER_ROLE}]:
        doc.set("roles", [])
        doc.append("roles", {"role": EXTERNAL_MARKETING_BUILDER_ROLE})
        changed = True

    if _ensure_shortcuts(doc):
        changed = True

    desired_content = _workspace_content()
    if _load_content(doc.content) != desired_content:
        doc.content = json.dumps(desired_content)
        changed = True

    if changed:
        doc.save(ignore_permissions=True)
        summary["updated_workspace"] = True


def _ensure_shortcuts(doc) -> bool:
    fields = ["label", "type", "link_to", "url", "doc_view", "color"]
    desired_rows = [{field: row.get(field) for field in fields} for row in WORKSPACE_SHORTCUTS]
    current_rows = [{field: getattr(row, field, None) for field in fields} for row in doc.shortcuts]
    if current_rows == desired_rows:
        return False
    doc.set("shortcuts", [])
    for row in desired_rows:
        doc.append("shortcuts", row)
    return True


def _workspace_content() -> list[dict]:
    return [
        _header("lt-external-marketing-title", '<span class="h4"><b>External Marketing Builder</b></span>', 12),
        _header(
            "lt-external-marketing-note",
            '<span class="text-muted">Create campaign landing pages and update approved tracking IDs. Core shop, products, checkout, customers, orders, payments, and files are not part of this access.</span>',
            12,
        ),
        _shortcut("lt-external-marketing-web-pages", "Landing Pages", 3),
        _shortcut("lt-external-marketing-product-pages", "Product Pages", 3),
        _shortcut("lt-external-marketing-tracking", "Tracking Settings", 3),
        _shortcut("lt-external-marketing-review", "Marketing Review", 3),
        _shortcut("lt-external-marketing-site", "Live Site", 4),
        _shortcut("lt-external-marketing-shop", "Shop", 4),
        _shortcut("lt-external-marketing-contact", "Contact", 4),
    ]


def _set_fields(doc, fields: dict) -> bool:
    changed = False
    for key, value in fields.items():
        if getattr(doc, key, None) != value:
            setattr(doc, key, value)
            changed = True
    return changed


def _child_table_rows(rows, fields: list[str]) -> list[dict]:
    return [{field: getattr(row, field, None) for field in fields} for row in rows]


def _load_content(raw: str | None):
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def _header(block_id: str, text: str, col: int) -> dict:
    return {"id": block_id, "type": "header", "data": {"text": text, "col": col}}


def _shortcut(block_id: str, shortcut_name: str, col: int) -> dict:
    return {"id": block_id, "type": "shortcut", "data": {"shortcut_name": shortcut_name, "col": col}}
