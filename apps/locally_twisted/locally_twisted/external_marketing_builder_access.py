"""Controlled external marketing builder access.

This role is intentionally separate from the review-only marketing role.
It grants a marketing vendor a Desk surface for landing-page drafts,
product-page marketing edits, and tracking IDs without handing over pricing,
variants, checkout, customers, orders, payments, or raw website settings.
"""
from __future__ import annotations

from typing import Any

import frappe
from frappe import _


EXTERNAL_MARKETING_BUILDER_ROLE = "LT External Marketing Builder"
EXTERNAL_MARKETING_WORKSPACE = "LT External Marketing Builder Home"
TRACKING_SETTINGS_DOCTYPE = "LT Marketing Tracking Settings"

LANDING_ROUTE_PREFIXES = ("campaigns/", "landing/", "marketing/")

FORBIDDEN_BUILDER_ROLES = {
    "System Manager",
    "Website Manager",
    "Item Manager",
    "Accounts User",
    "Accounts Manager",
    "Sales User",
    "Sales Manager",
    "LT Owner Access",
    "LT Accountant Access",
    "LT Maintenance Admin Access",
    "LT Marketing Review Access",
}

FORBIDDEN_BUILDER_DOCTYPES = (
    "Lead",
    "Customer",
    "Contact",
    "Address",
    "Quotation",
    "Sales Order",
    "Sales Invoice",
    "Payment Request",
    "Payment Entry",
    "Communication",
    "Email Queue",
    "File",
    "Item",
    "Item Price",
    "Website Settings",
    "Webshop Settings",
    "Project",
    "Task",
    "Error Log",
    "Access Log",
    "Activity Log",
    "Version",
)


def is_external_marketing_builder(user: str | None = None) -> bool:
    user = user or frappe.session.user
    if not user or user in {"Guest", "Administrator"}:
        return False
    return bool(
        frappe.db.exists(
            "Has Role",
            {
                "parenttype": "User",
                "parent": user,
                "role": EXTERNAL_MARKETING_BUILDER_ROLE,
            },
        )
    )


def web_page_permission_query_condition(user: str | None = None) -> str | None:
    """Limit external builders to campaign/landing/marketing Web Page records."""
    if not is_external_marketing_builder(user):
        return None

    return " or ".join(
        f"`tabWeb Page`.`route` like {frappe.db.escape(prefix + '%')}"
        for prefix in LANDING_ROUTE_PREFIXES
    )


def has_web_page_permission(doc=None, ptype: str | None = None, user: str | None = None) -> bool | None:
    """Allow external builders to work only inside approved landing routes."""
    if not is_external_marketing_builder(user):
        return None
    if ptype == "create":
        return True
    if doc is None:
        return None
    return _web_page_route_is_allowed(getattr(doc, "route", None))


def validate_builder_web_page_mutation(doc, method: str | None = None) -> None:
    """Fail loudly if an external builder tries to save a core public route."""
    if not is_external_marketing_builder():
        return
    if _web_page_route_is_allowed(doc.get("route")):
        return

    frappe.throw(
        _(
            "External marketing builders can only create or edit landing pages under "
            "/campaigns/, /landing/, or /marketing/. Core website, shop, product, "
            "checkout, and policy pages stay in the controlled site build."
        ),
        frappe.PermissionError,
    )


def builder_no_records_condition(user: str | None = None) -> str | None:
    if is_external_marketing_builder(user):
        return "1=0"
    return None


def has_builder_sensitive_doc_permission(doc=None, ptype: str | None = None, user: str | None = None) -> bool | None:
    if is_external_marketing_builder(user):
        return False
    return None


def block_builder_sensitive_doc_mutation(doc, method: str | None = None) -> None:
    if is_external_marketing_builder():
        frappe.throw(
            _("External marketing builder access cannot change ERPNext business records."),
            frappe.PermissionError,
        )


def marketing_or_builder_no_records_condition(user: str | None = None) -> str | None:
    if is_external_marketing_builder(user):
        return "1=0"
    from locally_twisted.marketing_review_access import marketing_no_records_condition

    return marketing_no_records_condition(user)


def has_marketing_or_builder_sensitive_doc_permission(
    doc=None,
    ptype: str | None = None,
    user: str | None = None,
) -> bool | None:
    if is_external_marketing_builder(user):
        return False
    from locally_twisted.marketing_review_access import has_marketing_sensitive_doc_permission

    return has_marketing_sensitive_doc_permission(doc=doc, ptype=ptype, user=user)


def builder_role_boundary() -> dict[str, Any]:
    failures: list[str] = []
    role_exists = bool(frappe.db.exists("Role", EXTERNAL_MARKETING_BUILDER_ROLE))
    role = frappe.get_doc("Role", EXTERNAL_MARKETING_BUILDER_ROLE) if role_exists else None

    if not role_exists:
        failures.append(f"Missing Role {EXTERNAL_MARKETING_BUILDER_ROLE}")
    elif not int(role.get("desk_access") or 0):
        failures.append(f"{EXTERNAL_MARKETING_BUILDER_ROLE} must grant Desk access")

    expected_permissions = {
        "Web Page": {"read": 1, "write": 1, "create": 1, "delete": 0},
        "Website Item": {"read": 1, "write": 1, "create": 0, "delete": 0},
        "Web Template": {"read": 1, "write": 0, "create": 0, "delete": 0},
        "Website Theme": {"read": 1, "write": 0, "create": 0, "delete": 0},
        TRACKING_SETTINGS_DOCTYPE: {"read": 1, "write": 1, "create": 0, "delete": 0},
    }
    actual_permissions = _docperm_report(EXTERNAL_MARKETING_BUILDER_ROLE)
    for doctype, expected in expected_permissions.items():
        row = actual_permissions.get(doctype)
        if not row:
            failures.append(f"{EXTERNAL_MARKETING_BUILDER_ROLE} missing DocPerm for {doctype}")
            continue
        for fieldname, expected_value in expected.items():
            if int(row.get(fieldname) or 0) != expected_value:
                failures.append(
                    f"{EXTERNAL_MARKETING_BUILDER_ROLE} {doctype}.{fieldname} "
                    f"expected {expected_value}, found {row.get(fieldname)}"
                )

    for doctype in FORBIDDEN_BUILDER_DOCTYPES:
        if not frappe.db.exists("DocType", doctype):
            continue
        if _role_has_any_permission(doctype, EXTERNAL_MARKETING_BUILDER_ROLE):
            failures.append(f"{EXTERNAL_MARKETING_BUILDER_ROLE} has forbidden DocPerm on {doctype}")

    return {
        "ok": not failures,
        "role": EXTERNAL_MARKETING_BUILDER_ROLE,
        "workspace": EXTERNAL_MARKETING_WORKSPACE,
        "tracking_settings_doctype": TRACKING_SETTINGS_DOCTYPE,
        "landing_route_prefixes": list(LANDING_ROUTE_PREFIXES),
        "role_exists": role_exists,
        "desk_access": int(role.get("desk_access") or 0) if role else None,
        "docperm": actual_permissions,
        "forbidden_doctypes": list(FORBIDDEN_BUILDER_DOCTYPES),
        "forbidden_roles": sorted(FORBIDDEN_BUILDER_ROLES),
        "failures": failures,
    }


def _web_page_route_is_allowed(route: str | None) -> bool:
    route = str(route or "").lstrip("/")
    return any(route.startswith(prefix) for prefix in LANDING_ROUTE_PREFIXES)


def _role_has_any_permission(doctype: str, role: str) -> bool:
    return bool(
        frappe.db.exists(
            "DocPerm",
            {
                "parent": doctype,
                "parenttype": "DocType",
                "role": role,
            },
        )
    )


def _docperm_report(role: str) -> dict[str, dict[str, int]]:
    rows = frappe.db.get_all(
        "DocPerm",
        filters={"role": role},
        fields=["parent", "read", "write", "create", "delete", "export", "report", "permlevel"],
        limit_page_length=500,
    )
    return {row["parent"]: row for row in rows}
