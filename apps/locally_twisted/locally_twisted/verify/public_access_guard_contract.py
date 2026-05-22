"""Verify public access settings and marketing review boundaries fail loudly."""
from __future__ import annotations

import time
from typing import Any, Callable

import frappe

from locally_twisted.marketing_review_access import MARKETING_REVIEW_ROLE


class ContractFail(Exception):
    pass


def run() -> dict[str, Any]:
    probes = [
        _expect_blocked("website_public_signup", _open_public_signup),
        _expect_blocked("portal_default_customer_role", _set_default_customer_role),
        _expect_blocked("supplier_route_as_customer", _set_supplier_route_customer),
        _expect_allowed("migration_portal_repair", _repair_portal_settings_during_migrate),
        _expect_blocked("marketing_lead_docperm", _insert_marketing_lead_docperm),
        _expect_blocked("marketing_role_desk_access", _enable_marketing_desk_access),
        _expect_blocked("marketing_user_customer_role", _give_marketing_user_customer_role),
    ]
    failures = [row["detail"] for row in probes if not row["ok"]]
    return {"ok": not failures, "probes": probes, "failures": failures}


def execute() -> dict[str, Any]:
    report = run()
    print(report)
    return report


def _expect_blocked(label: str, fn: Callable[[], None]) -> dict[str, Any]:
    try:
        fn()
    except Exception as exc:
        frappe.db.rollback()
        frappe.clear_cache()
        text = str(exc)
        if "Protected Public Access Boundary" in text or _expected_text(text):
            return {"probe": label, "ok": True, "blocked": True, "detail": text}
        return {"probe": label, "ok": False, "blocked": True, "detail": f"wrong error: {text}"}
    finally:
        frappe.set_user("Administrator")
    frappe.db.rollback()
    frappe.clear_cache()
    return {"probe": label, "ok": False, "blocked": False, "detail": "mutation was not blocked"}


def _expect_allowed(label: str, fn: Callable[[], None]) -> dict[str, Any]:
    try:
        fn()
    except Exception as exc:
        frappe.db.rollback()
        frappe.clear_cache()
        return {"probe": label, "ok": False, "blocked": True, "detail": str(exc)}
    finally:
        frappe.flags.in_migrate = False
        frappe.set_user("Administrator")
    frappe.db.rollback()
    frappe.clear_cache()
    return {"probe": label, "ok": True, "blocked": False, "detail": "mutation allowed"}


def _expected_text(text: str) -> bool:
    lowered = text.lower()
    return any(
        marker in lowered
        for marker in (
            "public signup",
            "default_role",
            "supplier-only",
            "direct docperm",
            "desk access",
            "cannot also have",
        )
    )


def _open_public_signup() -> None:
    doc = frappe.get_single("Website Settings")
    doc.disable_signup = 0
    doc.save(ignore_permissions=True)


def _set_default_customer_role() -> None:
    doc = frappe.get_single("Portal Settings")
    doc.default_role = "Customer"
    doc.save(ignore_permissions=True)


def _set_supplier_route_customer() -> None:
    doc = frappe.get_single("Portal Settings")
    for row in doc.get("menu") or []:
        if row.route == "/rfq":
            row.role = "Customer"
            row.enabled = 1
            break
    doc.save(ignore_permissions=True)


def _repair_portal_settings_during_migrate() -> None:
    doc = frappe.get_single("Portal Settings")
    doc.default_role = "Customer"
    doc.default_portal_home = "login"
    for row in doc.get("menu") or []:
        if row.route == "/rfq":
            row.role = "Customer"
            row.enabled = 1
        if row.route == "/orders":
            row.enabled = 1
    frappe.flags.in_migrate = True
    doc.save(ignore_permissions=True)

    if doc.default_role:
        raise ContractFail("migration repair did not clear Portal Settings.default_role")
    if doc.default_portal_home != "me":
        raise ContractFail("migration repair did not restore Portal Settings.default_portal_home")
    for row in doc.get("menu") or []:
        if row.route == "/rfq" and row.role != "Supplier":
            raise ContractFail("migration repair did not keep /rfq Supplier-only")
        if row.route == "/orders" and int(row.enabled or 0):
            raise ContractFail("migration repair did not hide /orders")


def _insert_marketing_lead_docperm() -> None:
    frappe.get_doc(
        {
            "doctype": "DocPerm",
            "parent": "Lead",
            "parenttype": "DocType",
            "parentfield": "permissions",
            "role": MARKETING_REVIEW_ROLE,
            "permlevel": 0,
            "read": 1,
        }
    ).insert(ignore_permissions=True)


def _enable_marketing_desk_access() -> None:
    doc = frappe.get_doc("Role", MARKETING_REVIEW_ROLE)
    doc.desk_access = 1
    doc.save(ignore_permissions=True)


def _give_marketing_user_customer_role() -> None:
    email = f"lt-public-access-guard-{int(time.time() * 1000)}@example.invalid"
    user = frappe.get_doc(
        {
            "doctype": "User",
            "email": email,
            "first_name": "Public",
            "last_name": "Access Guard",
            "enabled": 1,
            "user_type": "Website User",
            "send_welcome_email": 0,
            "roles": [{"role": MARKETING_REVIEW_ROLE}],
        }
    )
    user.insert(ignore_permissions=True)
    user.append("roles", {"role": "Customer"})
    user.save(ignore_permissions=True)
