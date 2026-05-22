"""Sync website-only external marketing review access.

Run in-process:
  bench --site frontend execute locally_twisted.seed.sync_marketing_review_access.execute
"""
from __future__ import annotations

import json

import frappe

from locally_twisted.marketing_review_access import MARKETING_REVIEW_ROLE, marketing_role_boundary


APPROVED_REVIEWER_EMAILS = frozenset({"marketing@exploringnotboring.com"})
PROTECTED_USER_EMAILS = frozenset(
    {
        "administrator",
        "guest",
        "cameron@builtbycameron.com",
        "locallytwisted@gmail.com",
    }
)
REVIEWER_CLEAR_FIELDS = ("default_workspace", "module_profile", "role_profile_name")


def execute(commit: bool = True, reviewer_email: str | None = None, send_welcome_email: bool = False) -> str:
    approved_reviewer_email = _approved_reviewer_email(reviewer_email) if reviewer_email else None
    summary = {
        "ensured_role": False,
        "reviewer_user": {},
        "removed_docperm_rows": [],
        "boundary_ok": False,
        "boundary_failures": [],
        "committed": False,
    }

    _ensure_role(summary)
    if approved_reviewer_email:
        _ensure_reviewer_user(summary, approved_reviewer_email, send_welcome_email=send_welcome_email)
    _remove_role_docperms(summary)

    boundary = marketing_role_boundary()
    summary["boundary_ok"] = bool(boundary.get("ok"))
    summary["boundary_failures"] = boundary.get("failures") or []

    frappe.clear_cache()
    if commit:
        frappe.db.commit()
        summary["committed"] = True

    print(json.dumps(summary, indent=2, sort_keys=True))
    return json.dumps(summary, sort_keys=True)


def _ensure_role(summary: dict) -> None:
    fields = {
        "role_name": MARKETING_REVIEW_ROLE,
        "desk_access": 0,
        "disabled": 0,
    }
    if frappe.db.exists("Role", MARKETING_REVIEW_ROLE):
        doc = frappe.get_doc("Role", MARKETING_REVIEW_ROLE)
        changed = False
        for fieldname, value in fields.items():
            if doc.get(fieldname) != value:
                doc.set(fieldname, value)
                changed = True
        if changed:
            doc.save(ignore_permissions=True)
            summary["ensured_role"] = True
        return

    frappe.get_doc({"doctype": "Role", **fields}).insert(ignore_permissions=True)
    summary["ensured_role"] = True


def _ensure_reviewer_user(summary: dict, email: str, *, send_welcome_email: bool) -> None:
    email = _approved_reviewer_email(email)

    fields = {
        "email": email,
        "first_name": "Marketing",
        "last_name": "Reviewer",
        "enabled": 1,
        "user_type": "Website User",
        "send_welcome_email": 1 if send_welcome_email else 0,
    }
    if frappe.db.exists("User", email):
        doc = frappe.get_doc("User", email)
        before_roles = {row.role for row in doc.roles}
        changed = before_roles != {MARKETING_REVIEW_ROLE}
        action = "unchanged"
        for fieldname, value in fields.items():
            if doc.get(fieldname) != value:
                doc.set(fieldname, value)
                changed = True
        for fieldname in REVIEWER_CLEAR_FIELDS:
            if doc.meta.has_field(fieldname) and doc.get(fieldname):
                doc.set(fieldname, None)
                changed = True
    else:
        doc = frappe.get_doc({"doctype": "User", **fields})
        changed = True
        action = "created"

    if changed or doc.is_new():
        doc.roles = []
        doc.append("roles", {"role": MARKETING_REVIEW_ROLE})
    if doc.is_new():
        doc.insert(ignore_permissions=True)
    else:
        if changed:
            action = "repaired"
            doc.save(ignore_permissions=True)
    summary["reviewer_user"] = {
        "email": email,
        "action": action,
        "approved_reviewer_allowlist": sorted(APPROVED_REVIEWER_EMAILS),
        "user_type": "Website User",
        "roles": [MARKETING_REVIEW_ROLE],
        "send_welcome_email": bool(send_welcome_email),
    }


def _approved_reviewer_email(email: str) -> str:
    normalized = (email or "").strip().lower()
    if not normalized:
        frappe.throw("reviewer_email is required to provision a marketing reviewer", frappe.ValidationError)
    if normalized in PROTECTED_USER_EMAILS or normalized not in APPROVED_REVIEWER_EMAILS:
        approved = ", ".join(sorted(APPROVED_REVIEWER_EMAILS))
        frappe.throw(
            f"Refusing to provision marketing review access for {normalized!r}; approved reviewer email: {approved}",
            frappe.ValidationError,
        )
    return normalized


def _remove_role_docperms(summary: dict) -> None:
    rows = frappe.get_all(
        "DocPerm",
        filters={"role": MARKETING_REVIEW_ROLE},
        fields=["name", "parent"],
        limit_page_length=500,
    )
    for row in rows:
        frappe.delete_doc("DocPerm", row.name, ignore_permissions=True)
        summary["removed_docperm_rows"].append(row.parent)
