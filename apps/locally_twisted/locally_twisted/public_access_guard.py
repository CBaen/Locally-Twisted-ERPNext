"""Architectural guard for public access and external-review boundaries."""
from __future__ import annotations

from typing import Any

import frappe
from frappe import _

from locally_twisted.marketing_review_access import (
    FORBIDDEN_MARKETING_ROLES,
    MARKETING_REVIEW_ROLE,
)


TITLE = "Protected Public Access Boundary"

SUPPLIER_ROUTES = {
    "/rfq",
    "/supplier-quotations",
    "/purchase-orders",
    "/purchase-invoices",
}

STOCK_CUSTOMER_ROUTES_TO_HIDE = {
    "/addresses",
    "/invoices",
    "/issues",
    "/material-requests",
    "/newsletters",
    "/orders",
    "/project",
    "/quotations",
    "/shipments",
    "/timesheets",
}


def validate_public_access_boundary(doc, method: str | None = None, *args, **kwargs) -> None:
    """Block settings/permission drift that would expose public or reviewer access."""
    doctype = getattr(doc, "doctype", None)
    if doctype == "Website Settings":
        _validate_website_settings(doc)
    elif doctype == "Portal Settings":
        _validate_portal_settings(doc)
    elif doctype == "DocPerm":
        _validate_docperm(doc)
    elif doctype == "Role":
        _validate_role(doc)
    elif doctype == "User":
        _validate_user_roles(doc)
    elif doctype == "Has Role":
        _validate_has_role_row(doc)


def _validate_website_settings(doc) -> None:
    if int(doc.get("disable_signup") or 0) != 1:
        _block(
            "Public signup must stay disabled. Customer portal access is invite-only.",
            doc,
        )
    if int(doc.get("hide_login") or 0) != 0:
        _block(
            "Login must stay visible while customer/account routes exist.",
            doc,
        )


def _validate_portal_settings(doc) -> None:
    if getattr(frappe.flags, "in_migrate", False):
        _normalize_portal_settings_for_migrate(doc)

    if doc.get("default_role"):
        _block(
            "Portal Settings.default_role must stay empty so public signup cannot auto-grant roles.",
            doc,
        )
    if doc.get("default_portal_home") != "me":
        _block(
            "Portal Settings.default_portal_home must stay 'me' for the LT account home.",
            doc,
        )

    for row in doc.get("menu") or []:
        route = row.get("route")
        if not route or not int(row.get("enabled") or 0):
            continue
        if route in SUPPLIER_ROUTES and row.get("role") != "Supplier":
            _block(f"{route} must remain Supplier-only.", doc)
        if route in STOCK_CUSTOMER_ROUTES_TO_HIDE:
            _block(f"{route} must stay hidden from the customer portal menu.", doc)


def _normalize_portal_settings_for_migrate(doc) -> None:
    """Let Frappe's migrate-time portal sync repair safe values before saving."""
    doc.set("default_role", None)
    doc.set("default_portal_home", "me")

    for row in doc.get("menu") or []:
        route = row.get("route")
        if route in SUPPLIER_ROUTES:
            row.set("role", "Supplier")
        if route in STOCK_CUSTOMER_ROUTES_TO_HIDE:
            row.set("enabled", 0)


def _validate_docperm(doc) -> None:
    if doc.get("role") == MARKETING_REVIEW_ROLE:
        _block(
            f"{MARKETING_REVIEW_ROLE} must not have direct DocPerm rows.",
            doc,
        )


def _validate_role(doc) -> None:
    if doc.get("name") == MARKETING_REVIEW_ROLE and int(doc.get("desk_access") or 0):
        _block(
            f"{MARKETING_REVIEW_ROLE} must remain website-only and cannot grant Desk access.",
            doc,
        )


def _validate_user_roles(doc) -> None:
    roles = _role_set(doc)
    if MARKETING_REVIEW_ROLE not in roles:
        return
    forbidden = sorted(roles & FORBIDDEN_MARKETING_ROLES)
    if forbidden:
        _block(
            f"{MARKETING_REVIEW_ROLE} users cannot also have: {', '.join(forbidden)}.",
            doc,
        )
    if doc.get("user_type") != "Website User":
        _block(
            f"{MARKETING_REVIEW_ROLE} users must stay Website User accounts.",
            doc,
        )


def _validate_has_role_row(doc) -> None:
    role = doc.get("role")
    parent = doc.get("parent")
    parenttype = doc.get("parenttype")
    if parenttype != "User" or not parent:
        return

    if role == MARKETING_REVIEW_ROLE and _user_has_any_role(parent, FORBIDDEN_MARKETING_ROLES):
        _block(
            f"{MARKETING_REVIEW_ROLE} cannot be added to a user with internal business roles.",
            doc,
        )
    if role in FORBIDDEN_MARKETING_ROLES and _user_has_role(parent, MARKETING_REVIEW_ROLE):
        _block(
            f"Users with {MARKETING_REVIEW_ROLE} cannot receive internal business role {role}.",
            doc,
        )


def _role_set(doc) -> set[str]:
    return {row.role for row in doc.get("roles") or [] if row.role}


def _user_has_role(user: str, role: str) -> bool:
    return bool(
        frappe.db.exists(
            "Has Role",
            {"parenttype": "User", "parent": user, "role": role},
        )
    )


def _user_has_any_role(user: str, roles: set[str]) -> bool:
    return bool(
        frappe.db.exists(
            "Has Role",
            {"parenttype": "User", "parent": user, "role": ["in", sorted(roles)]},
        )
    )


def _block(message: str, doc: Any) -> None:
    try:
        frappe.log_error(
            title=TITLE,
            message="\n".join(
                [
                    message,
                    f"doctype={getattr(doc, 'doctype', '')}",
                    f"name={getattr(doc, 'name', '')}",
                    f"user={frappe.session.user}",
                ]
            ),
        )
    except Exception:
        pass
    frappe.throw(_(message), frappe.PermissionError, title=TITLE)
