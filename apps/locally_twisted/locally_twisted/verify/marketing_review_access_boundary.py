"""Verify external marketing review access is website-only."""
from __future__ import annotations

import time

import frappe
from frappe.utils.password import update_password

from locally_twisted.marketing_review_access import (
    FORBIDDEN_MARKETING_DOCTYPES,
    FORBIDDEN_MARKETING_ROLES,
    MARKETING_REVIEW_ROLE,
    MARKETING_REVIEW_ROUTE,
    apply_marketing_review_context,
    marketing_role_boundary,
)


class ContractFail(Exception):
    pass


def create_fixture(password: str | None = None) -> dict:
    """Create a committed marketing reviewer fixture for browser/HTTP proof."""
    if not password:
        frappe.throw("marketing_review_access_boundary.create_fixture requires a password")
    boundary = marketing_role_boundary()
    if not boundary.get("ok"):
        frappe.throw("; ".join(boundary.get("failures") or ["marketing boundary failed"]))

    original_user = frappe.session.user
    frappe.set_user("Administrator")
    try:
        email = _make_user("marketing-browser", roles=[MARKETING_REVIEW_ROLE])
        update_password(email, password)
        frappe.db.commit()
        return {"ok": True, "email": email}
    finally:
        frappe.set_user(original_user)


def cleanup_fixture(email: str | None = None) -> dict:
    """Remove a committed marketing reviewer fixture."""
    email = (email or "").strip()
    if not email:
        frappe.throw("marketing_review_access_boundary.cleanup_fixture requires email")

    original_user = frappe.session.user
    frappe.set_user("Administrator")
    try:
        deleted = []
        if frappe.db.exists("User", email):
            frappe.delete_doc("User", email, force=True, ignore_permissions=True)
            deleted.append(f"User:{email}")
        frappe.db.commit()
        return {"ok": True, "deleted": deleted}
    finally:
        frappe.set_user(original_user)


def run() -> dict:
    try:
        result = _run_contract()
        return {"ok": True, **result}
    except ContractFail as exc:
        return {"ok": False, "failures": [str(exc)]}
    except Exception:
        return {"ok": False, "failures": [frappe.get_traceback()]}
    finally:
        frappe.db.rollback()


def _run_contract() -> dict:
    boundary = marketing_role_boundary()
    if not boundary.get("ok"):
        raise ContractFail("; ".join(boundary.get("failures") or ["marketing boundary failed"]))

    marketing_user = _make_marketing_user()
    customer_user = _make_user("customer")

    _assert_user_boundary(marketing_user)
    _assert_forbidden_record_access(marketing_user)
    _assert_contact_creation_blocked(marketing_user)
    _assert_review_context_allowed(marketing_user)
    _assert_me_redirects_to_review(marketing_user)
    _assert_review_context_blocked(customer_user)

    return {
        "role": MARKETING_REVIEW_ROLE,
        "marketing_user_type": "Website User",
        "forbidden_doctypes_checked": [
            doctype for doctype in FORBIDDEN_MARKETING_DOCTYPES if frappe.db.exists("DocType", doctype)
        ],
        "forbidden_roles_checked": sorted(FORBIDDEN_MARKETING_ROLES),
        "review_route_context": "allowed_for_marketing_role_only",
        "me_route": f"redirects_to_{MARKETING_REVIEW_ROUTE}",
        "rolled_back": True,
    }


def _make_marketing_user() -> str:
    return _make_user("marketing", roles=[MARKETING_REVIEW_ROLE])


def _make_user(slug: str, roles: list[str] | None = None) -> str:
    stamp = int(time.time() * 1000)
    email = f"lt-{slug}-review-access-{stamp}@example.invalid"
    frappe.get_doc(
        {
            "doctype": "User",
            "email": email,
            "first_name": "Access",
            "last_name": slug.title(),
            "enabled": 1,
            "user_type": "Website User",
            "send_welcome_email": 0,
            "roles": [{"role": role} for role in (roles or [])],
        }
    ).insert(ignore_permissions=True)
    return email


def _assert_user_boundary(user: str) -> None:
    user_doc = frappe.get_doc("User", user)
    if user_doc.user_type != "Website User":
        raise ContractFail(f"{user} should be Website User, found {user_doc.user_type}")

    roles = {row.role for row in user_doc.roles}
    if MARKETING_REVIEW_ROLE not in roles:
        raise ContractFail(f"{user} missing {MARKETING_REVIEW_ROLE}")
    forbidden_roles = sorted(roles & FORBIDDEN_MARKETING_ROLES)
    if forbidden_roles:
        raise ContractFail(f"{user} has forbidden roles: {', '.join(forbidden_roles)}")

def _assert_forbidden_record_access(user: str) -> None:
    original_user = frappe.session.user
    try:
        for doctype in FORBIDDEN_MARKETING_DOCTYPES:
            if not frappe.db.exists("DocType", doctype):
                continue
            names = frappe.get_all(doctype, pluck="name", limit_page_length=1, ignore_permissions=True)
            frappe.set_user(user)
            try:
                rows = frappe.get_list(doctype, pluck="name", limit_page_length=1)
            except frappe.PermissionError:
                rows = []
            if rows:
                raise ContractFail(f"{user} can list forbidden DocType {doctype}")
            if names:
                doc = frappe.get_doc(doctype, names[0])
                for ptype in ("read", "write", "delete"):
                    if doc.has_permission(ptype, user=user):
                        raise ContractFail(f"{user} can {ptype} forbidden {doctype} record {names[0]}")
            frappe.set_user(original_user)
    finally:
        frappe.set_user(original_user)


def _assert_contact_creation_blocked(user: str) -> None:
    original_user = frappe.session.user
    try:
        frappe.set_user(user)
        try:
            frappe.get_doc(
                {
                    "doctype": "Contact",
                    "first_name": "Marketing",
                    "last_name": "Blocked",
                }
            ).insert()
        except frappe.PermissionError:
            return
        raise ContractFail(f"{user} can create Contact records")
    finally:
        frappe.set_user(original_user)


def _assert_review_context_allowed(user: str) -> None:
    original_user = frappe.session.user
    try:
        frappe.set_user(user)
        context = frappe._dict()
        apply_marketing_review_context(context)
        if not context.get("marketing_review_links"):
            raise ContractFail("marketing review context did not expose review links")
    finally:
        frappe.set_user(original_user)


def _assert_review_context_blocked(user: str) -> None:
    original_user = frappe.session.user
    try:
        frappe.set_user(user)
        try:
            apply_marketing_review_context(frappe._dict())
        except frappe.PermissionError:
            return
        raise ContractFail("non-marketing Website User should not reach marketing review context")
    finally:
        frappe.set_user(original_user)


def _assert_me_redirects_to_review(user: str) -> None:
    from locally_twisted.www import me as me_page

    original_user = frappe.session.user
    try:
        frappe.set_user(user)
        try:
            me_page.get_context(frappe._dict())
        except frappe.Redirect:
            location = getattr(frappe.local.flags, "redirect_location", "")
            if location != MARKETING_REVIEW_ROUTE:
                raise ContractFail(f"/me redirected marketing user to {location!r}")
            return
        raise ContractFail("/me did not redirect marketing user to marketing review")
    finally:
        frappe.local.flags.redirect_location = None
        frappe.set_user(original_user)
