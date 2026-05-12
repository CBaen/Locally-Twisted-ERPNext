"""Cleanup helpers for the public repeat-email/photo form verifier."""
from __future__ import annotations

from typing import Any

import frappe

from locally_twisted.verify.book_form_repeat_email_photos_email_contract import (
    verify_email_delivery as _verify_email_delivery,
)


EMAIL_PREFIX = "lt-repeat-email-photo-"
EMAIL_SUFFIX = "@example.invalid"


@frappe.whitelist()
def preview(email: str | None = None, include_existing: bool = False) -> dict[str, Any]:
    """Return remaining verifier-owned records without mutating the database."""
    _require_authenticated_user()
    lead_names = _lead_names(email=email, include_existing=include_existing)
    targets = _cleanup_targets(lead_names, email=email, include_existing=include_existing)
    return {
        "ok": True,
        "email": email,
        "include_existing": bool(include_existing),
        "lead_count": len(targets.get("Lead", set())),
        "file_count": len(targets.get("File", set())),
        "email_queue_count": len(targets.get("Email Queue", set())),
        "communication_count": len(targets.get("Communication", set())),
        "contact_count": len(targets.get("Contact", set())),
        "task_count": len(targets.get("Task", set())),
        "todo_count": len(targets.get("ToDo", set())),
        "event_count": len(targets.get("Event", set())),
        "comment_count": len(targets.get("Comment", set())),
    }


@frappe.whitelist()
def cleanup(email: str | None = None, include_existing: bool = False) -> dict[str, Any]:
    """Delete records created by scripts/verify/book_form_repeat_email_photos.py.

    The guard only permits the verifier-owned invalid email namespace so this
    helper cannot become a general Lead cleanup tool by accident.
    """
    _require_authenticated_user()
    _validate_scope(email=email, include_existing=include_existing)
    lead_names = _lead_names(email=email, include_existing=include_existing)
    targets = _cleanup_targets(lead_names, email=email, include_existing=include_existing)
    deleted = []
    failures = []

    for doctype in _delete_order():
        for name in sorted(targets.get(doctype, set())):
            try:
                if frappe.db.exists(doctype, name):
                    frappe.delete_doc(doctype, name, ignore_permissions=True, force=True)
                    deleted.append({"doctype": doctype, "name": name})
            except Exception as exc:
                failures.append(
                    {
                        "doctype": doctype,
                        "name": name,
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                )

    frappe.db.commit()
    remaining = preview(email=email, include_existing=include_existing)
    return {
        "ok": not failures and not _has_remaining_records(remaining),
        "email": email,
        "include_existing": bool(include_existing),
        "deleted": deleted,
        "failures": failures,
        "remaining": remaining,
    }


@frappe.whitelist()
def verify_email_delivery(email: str, expected_labels: str | list[str] | None = None) -> dict[str, Any]:
    _require_authenticated_user()
    return _verify_email_delivery(email=email, expected_labels=expected_labels)


def _require_authenticated_user() -> None:
    if getattr(getattr(frappe, "session", None), "user", None) == "Guest":
        frappe.throw("Authentication required for verifier-owned record inspection")


def _validate_scope(email: str | None, include_existing: bool) -> None:
    if email:
        if not _is_verifier_email(email):
            frappe.throw("Refusing repeat-email/photo cleanup outside verifier email namespace")
        return
    if include_existing:
        return
    frappe.throw("Repeat-email/photo cleanup needs an exact verifier email or include_existing=True")


def _is_verifier_email(email: str) -> bool:
    return str(email or "").startswith(EMAIL_PREFIX) and str(email or "").endswith(EMAIL_SUFFIX)


def _lead_names(email: str | None, include_existing: bool) -> list[str]:
    filters: dict[str, Any] = {}
    names: set[str] = set()
    if email:
        filters["email_id"] = email
        names.update(frappe.get_all("Lead", filters=filters, pluck="name", limit_page_length=1000))
        names.update(
            frappe.get_all(
                "Lead",
                filters={"custom_anything_else": ["like", f"%Customer email: {email}%"]},
                pluck="name",
                limit_page_length=1000,
            )
        )
    elif include_existing:
        filters["email_id"] = ["like", f"{EMAIL_PREFIX}%{EMAIL_SUFFIX}"]
        names.update(frappe.get_all("Lead", filters=filters, pluck="name", limit_page_length=1000))
        names.update(
            frappe.get_all(
                "Lead",
                filters={
                    "custom_anything_else": [
                        "like",
                        f"%Customer email: {EMAIL_PREFIX}%{EMAIL_SUFFIX}%",
                    ]
                },
                pluck="name",
                limit_page_length=1000,
            )
        )
    else:
        return []
    return sorted(names)


def _cleanup_targets(
    lead_names: list[str],
    *,
    email: str | None,
    include_existing: bool,
) -> dict[str, set[str]]:
    targets: dict[str, set[str]] = {"Lead": set(lead_names)}

    for lead_name in lead_names:
        for doctype in ("File", "Email Queue", "Communication", "Comment", "ToDo", "Event"):
            filters = _reference_filters(doctype, "Lead", lead_name)
            if not filters:
                continue
            targets.setdefault(doctype, set()).update(
                frappe.get_all(doctype, filters=filters, pluck="name", limit_page_length=1000)
            )

        if frappe.get_meta("Task").has_field("custom_lt_lead"):
            targets.setdefault("Task", set()).update(
                frappe.get_all(
                    "Task",
                    filters={"custom_lt_lead": lead_name},
                    pluck="name",
                    limit_page_length=1000,
                )
            )

        targets.setdefault("Contact", set()).update(
            frappe.get_all(
                "Dynamic Link",
                filters={"parenttype": "Contact", "link_doctype": "Lead", "link_name": lead_name},
                pluck="parent",
                limit_page_length=1000,
            )
        )

    contact_filters = _contact_email_filters(email=email, include_existing=include_existing)
    if contact_filters:
        targets.setdefault("Contact", set()).update(
            frappe.get_all("Contact Email", filters=contact_filters, pluck="parent", limit_page_length=1000)
        )

    return targets


def _reference_filters(doctype: str, reference_doctype: str, reference_name: str) -> dict[str, Any] | None:
    meta = frappe.get_meta(doctype)
    if doctype == "File":
        if meta.has_field("attached_to_doctype") and meta.has_field("attached_to_name"):
            return {"attached_to_doctype": reference_doctype, "attached_to_name": reference_name}
        return None
    if doctype == "ToDo":
        if meta.has_field("reference_type") and meta.has_field("reference_name"):
            return {"reference_type": reference_doctype, "reference_name": reference_name}
        return None
    if meta.has_field("reference_doctype") and meta.has_field("reference_name"):
        return {"reference_doctype": reference_doctype, "reference_name": reference_name}
    return None


def _contact_email_filters(email: str | None, include_existing: bool) -> dict[str, Any] | None:
    if email:
        return {"email_id": email}
    if include_existing:
        return {"email_id": ["like", f"{EMAIL_PREFIX}%{EMAIL_SUFFIX}"]}
    return None


def _delete_order() -> list[str]:
    return [
        "Email Queue",
        "Communication",
        "Comment",
        "ToDo",
        "Task",
        "Event",
        "File",
        "Contact",
        "Lead",
    ]


def _has_remaining_records(remaining: dict[str, Any]) -> bool:
    return any(
        int(remaining.get(key, 0) or 0)
        for key in (
            "lead_count",
            "file_count",
            "email_queue_count",
            "communication_count",
            "contact_count",
            "task_count",
            "todo_count",
            "event_count",
            "comment_count",
        )
    )
