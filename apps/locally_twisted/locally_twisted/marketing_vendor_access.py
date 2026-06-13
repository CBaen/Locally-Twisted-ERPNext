"""Fail-loud sync for the known external marketing vendor user."""
from __future__ import annotations

import contextlib
import io
import json
from typing import Any

import frappe
from frappe.utils import cstr

from locally_twisted.external_marketing_builder_access import (
    EXTERNAL_MARKETING_BUILDER_ROLE,
    FORBIDDEN_BUILDER_ROLES,
    builder_role_boundary,
)
from locally_twisted.marketing_review_access import MARKETING_REVIEW_ROLE, marketing_role_boundary
from locally_twisted.seed.sync_external_marketing_builder_access import execute as sync_builder_access
from locally_twisted.seed.sync_marketing_review_access import execute as sync_review_access


DEFAULT_VENDOR_EMAIL = "marketing@exploringnotboring.com"
MODE_ROLE = {
    "review": MARKETING_REVIEW_ROLE,
    "builder": EXTERNAL_MARKETING_BUILDER_ROLE,
}
MODE_USER_TYPE = {
    "review": "Website User",
    "builder": "System User",
}


class MarketingVendorAccessFailure(Exception):
    """Raised when vendor access cannot be synced safely."""


@frappe.whitelist()
def execute(
    email: str = DEFAULT_VENDOR_EMAIL,
    mode: str = "builder",
    first_name: str = "Marketing",
    last_name: str = "Builder",
    commit: bool | str | int = True,
) -> str:
    """Ensure the known marketing vendor user has the requested controlled lane.

    `builder` means the controlled LT External Marketing Builder lane: Desk
    access for approved landing Web Pages, product-page marketing edits, and LT
    Marketing Tracking Settings. It is not System Manager or Website Manager.
    """
    _require_operator_if_http_request()
    email = cstr(email or "").strip().lower()
    mode = cstr(mode or "builder").strip().lower()
    commit_bool = _as_bool(commit)
    report: dict[str, Any] = {
        "ok": False,
        "email": email,
        "mode": mode,
        "expected_role": MODE_ROLE.get(mode),
        "expected_user_type": MODE_USER_TYPE.get(mode),
        "created_user": False,
        "updated_user": False,
        "removed_roles": [],
        "added_roles": [],
        "failures": [],
        "committed": False,
    }

    try:
        _validate(email=email, mode=mode)
        _sync_role_infrastructure(mode=mode, report=report)
        user_doc = _ensure_user(email=email, mode=mode, first_name=first_name, last_name=last_name, report=report)
        _sync_roles(user_doc=user_doc, mode=mode, report=report)
        user_doc.save(ignore_permissions=True)
        report["updated_user"] = True
        frappe.clear_cache(user=email)
        _verify_user(email=email, mode=mode, report=report)
        if commit_bool:
            frappe.db.commit()
            report["committed"] = True
        report["ok"] = True
    except Exception as exc:
        frappe.db.rollback()
        report["failures"].append(cstr(exc))
        _log_loud_failure(report)
    print(json.dumps(report, sort_keys=True))
    return json.dumps(report, sort_keys=True)


def _require_operator_if_http_request() -> None:
    """Require a trusted operator for HTTP/API calls, while keeping bench execute usable."""
    if not getattr(getattr(frappe, "local", None), "request", None):
        return
    user = cstr(getattr(frappe.session, "user", "") or "")
    if not user or user == "Guest":
        frappe.throw("System Manager login required for marketing vendor access operations", frappe.PermissionError)
    roles = set(frappe.get_roles(user) or [])
    if user != "Administrator" and "System Manager" not in roles:
        frappe.throw("System Manager role required for marketing vendor access operations", frappe.PermissionError)


def _validate(email: str, mode: str) -> None:
    if not email or "@" not in email:
        raise MarketingVendorAccessFailure("a concrete vendor email is required")
    if mode not in MODE_ROLE:
        raise MarketingVendorAccessFailure(f"unsupported mode {mode!r}; expected one of {sorted(MODE_ROLE)}")


def _sync_role_infrastructure(mode: str, report: dict[str, Any]) -> None:
    # The seed helpers print their own JSON. Suppress that here so this operator
    # method emits exactly one final machine-readable report.
    with contextlib.redirect_stdout(io.StringIO()):
        if mode == "builder":
            sync_payload = json.loads(sync_builder_access(commit=False))
        else:
            sync_payload = json.loads(sync_review_access(commit=False))
    report["role_infrastructure_sync"] = sync_payload
    boundary = builder_role_boundary() if mode == "builder" else marketing_role_boundary()
    report["boundary"] = boundary
    if not boundary.get("ok"):
        raise MarketingVendorAccessFailure("; ".join(boundary.get("failures") or ["marketing access boundary failed"]))


def _ensure_user(email: str, mode: str, first_name: str, last_name: str, report: dict[str, Any]):
    expected_user_type = MODE_USER_TYPE[mode]
    if frappe.db.exists("User", email):
        user_doc = frappe.get_doc("User", email)
    else:
        user_doc = frappe.get_doc(
            {
                "doctype": "User",
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "enabled": 1,
                "user_type": expected_user_type,
                "send_welcome_email": 0,
            }
        )
        user_doc.insert(ignore_permissions=True)
        report["created_user"] = True

    for field, value in {
        "enabled": 1,
        "user_type": expected_user_type,
        "send_welcome_email": 0,
    }.items():
        if user_doc.get(field) != value:
            user_doc.set(field, value)
    if first_name and not user_doc.first_name:
        user_doc.first_name = first_name
    if last_name and not user_doc.last_name:
        user_doc.last_name = last_name
    return user_doc


def _sync_roles(user_doc, mode: str, report: dict[str, Any]) -> None:
    expected_role = MODE_ROLE[mode]
    opposite_role = MODE_ROLE["review" if mode == "builder" else "builder"]
    forbidden = set()
    if mode == "builder":
        forbidden.update(FORBIDDEN_BUILDER_ROLES)
    forbidden.add(opposite_role)
    forbidden.discard(expected_role)

    current_roles = [row.role for row in user_doc.get("roles") or []]
    kept_roles = []
    removed = []
    for role in current_roles:
        if role in forbidden:
            removed.append(role)
        else:
            kept_roles.append(role)
    if expected_role not in kept_roles:
        kept_roles.append(expected_role)
        report["added_roles"].append(expected_role)
    report["removed_roles"] = sorted(set(removed))

    user_doc.set("roles", [])
    for role in sorted(set(kept_roles)):
        user_doc.append("roles", {"role": role})


def _verify_user(email: str, mode: str, report: dict[str, Any]) -> None:
    user_doc = frappe.get_doc("User", email)
    roles = sorted(row.role for row in user_doc.get("roles") or [])
    expected_role = MODE_ROLE[mode]
    expected_user_type = MODE_USER_TYPE[mode]
    report["user"] = {
        "name": user_doc.name,
        "enabled": int(user_doc.enabled or 0),
        "user_type": user_doc.user_type,
        "roles": roles,
    }
    if not int(user_doc.enabled or 0):
        raise MarketingVendorAccessFailure(f"User {email} is disabled after sync")
    if user_doc.user_type != expected_user_type:
        raise MarketingVendorAccessFailure(
            f"User {email} has user_type {user_doc.user_type!r}; expected {expected_user_type!r}"
        )
    if expected_role not in roles:
        raise MarketingVendorAccessFailure(f"User {email} missing expected role {expected_role}")
    if mode == "builder":
        forbidden_roles = sorted((set(roles) & set(FORBIDDEN_BUILDER_ROLES)) - {expected_role})
        if forbidden_roles:
            raise MarketingVendorAccessFailure(f"User {email} has forbidden builder roles: {', '.join(forbidden_roles)}")


def _log_loud_failure(report: dict[str, Any]) -> None:
    try:
        frappe.log_error(
            title="Marketing vendor access sync failed loudly",
            message=json.dumps(report, indent=2, sort_keys=True, default=str),
        )
        frappe.db.commit()
    except Exception:
        frappe.db.rollback()


def _as_bool(value: bool | str | int) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return bool(value)
    return cstr(value).strip().lower() in {"1", "true", "yes", "y", "commit"}
