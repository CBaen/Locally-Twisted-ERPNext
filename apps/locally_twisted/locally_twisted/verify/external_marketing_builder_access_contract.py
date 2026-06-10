"""Contract for controlled external marketing builder access."""
from __future__ import annotations

from typing import Any

import frappe

from locally_twisted.external_marketing_builder_access import (
    EXTERNAL_MARKETING_BUILDER_ROLE,
    EXTERNAL_MARKETING_WORKSPACE,
    FORBIDDEN_BUILDER_DOCTYPES,
    TRACKING_SETTINGS_DOCTYPE,
    builder_role_boundary,
    has_web_page_permission,
)
from locally_twisted.locally_twisted.doctype.lt_marketing_tracking_settings.lt_marketing_tracking_settings import (
    public_tracking_config,
)


def run() -> dict[str, Any]:
    failures: list[str] = []
    boundary = builder_role_boundary()
    failures.extend(boundary.get("failures") or [])

    _check_workspace(failures)
    _check_tracking_config(failures)
    _check_forbidden_permission_edges(failures)
    _check_temp_user_permissions(failures)

    return {
        "ok": not failures,
        "role": EXTERNAL_MARKETING_BUILDER_ROLE,
        "workspace": EXTERNAL_MARKETING_WORKSPACE,
        "tracking_settings_doctype": TRACKING_SETTINGS_DOCTYPE,
        "boundary": boundary,
        "failures": sorted(set(failures)),
    }


def _check_workspace(failures: list[str]) -> None:
    if not frappe.db.exists("Workspace", EXTERNAL_MARKETING_WORKSPACE):
        failures.append(f"missing workspace {EXTERNAL_MARKETING_WORKSPACE}")
        return
    doc = frappe.get_doc("Workspace", EXTERNAL_MARKETING_WORKSPACE)
    roles = {row.role for row in doc.roles}
    if roles != {EXTERNAL_MARKETING_BUILDER_ROLE}:
        failures.append(f"{EXTERNAL_MARKETING_WORKSPACE} roles should only be {EXTERNAL_MARKETING_BUILDER_ROLE}")
    shortcut_targets = {row.link_to or row.url for row in doc.shortcuts}
    for expected in {"Web Page", "Website Item", TRACKING_SETTINGS_DOCTYPE, "/marketing-review", "/shop", "/contact"}:
        if expected not in shortcut_targets:
            failures.append(f"{EXTERNAL_MARKETING_WORKSPACE} missing shortcut {expected}")


def _check_tracking_config(failures: list[str]) -> None:
    if not frappe.db.exists("DocType", TRACKING_SETTINGS_DOCTYPE):
        failures.append(f"missing DocType {TRACKING_SETTINGS_DOCTYPE}")
        return
    config = public_tracking_config()
    if config.get("ga4_measurement_id") != "G-0Z0WY5XQRB":
        failures.append("public tracking config should default to verified GA4 ID G-0Z0WY5XQRB")
    forbidden_keys = {"api_key", "secret", "token", "password"}
    if forbidden_keys & set(config):
        failures.append("public tracking config must not expose secret-like keys")


def _check_forbidden_permission_edges(failures: list[str]) -> None:
    for doctype in ("Website Settings", "Item", "Item Price", "Lead", "Sales Order", "File"):
        if not frappe.db.exists("DocType", doctype):
            continue
        if frappe.db.exists("DocPerm", {"parent": doctype, "role": EXTERNAL_MARKETING_BUILDER_ROLE}):
            failures.append(f"{EXTERNAL_MARKETING_BUILDER_ROLE} must not have DocPerm on {doctype}")


def _check_temp_user_permissions(failures: list[str]) -> None:
    user = f"lt-external-marketing-verifier-{frappe.generate_hash(length=8)}@example.invalid"
    original_user = frappe.session.user
    try:
        doc = frappe.get_doc(
            {
                "doctype": "User",
                "email": user,
                "first_name": "LT",
                "last_name": "External Marketing Verifier",
                "enabled": 1,
                "user_type": "System User",
                "send_welcome_email": 0,
                "roles": [{"role": EXTERNAL_MARKETING_BUILDER_ROLE}],
            }
        )
        doc.insert(ignore_permissions=True)

        if not frappe.has_permission(TRACKING_SETTINGS_DOCTYPE, ptype="write", user=user):
            failures.append(f"temporary {EXTERNAL_MARKETING_BUILDER_ROLE} user cannot write tracking settings")
        if not frappe.has_permission("Web Page", ptype="create", user=user):
            failures.append(f"temporary {EXTERNAL_MARKETING_BUILDER_ROLE} user cannot create Web Pages")
        _check_product_page_permissions(failures, user)
        if frappe.db.exists("DocType", "Website Settings") and frappe.has_permission(
            "Website Settings", ptype="write", user=user
        ):
            failures.append(f"temporary {EXTERNAL_MARKETING_BUILDER_ROLE} user can write Website Settings")

        allowed_page = frappe._dict({"doctype": "Web Page", "route": "campaigns/verifier-page", "owner": user})
        denied_page = frappe._dict({"doctype": "Web Page", "route": "shop", "owner": user})
        if not has_web_page_permission(allowed_page, ptype="write", user=user):
            failures.append("external builder route guard should allow /campaigns/ Web Pages")
        if has_web_page_permission(denied_page, ptype="write", user=user):
            failures.append("external builder route guard must block core Web Page routes")

        for doctype in FORBIDDEN_BUILDER_DOCTYPES:
            if not frappe.db.exists("DocType", doctype):
                continue
            if doctype == "File":
                _check_file_access(failures, user)
                continue
            if _user_can_list_records(doctype, user):
                failures.append(f"temporary {EXTERNAL_MARKETING_BUILDER_ROLE} user can list forbidden {doctype}")
            if _user_can_read_existing_record(doctype, user):
                failures.append(f"temporary {EXTERNAL_MARKETING_BUILDER_ROLE} user can open forbidden {doctype}")
    finally:
        frappe.set_user(original_user)
        frappe.db.rollback()


def _check_product_page_permissions(failures: list[str], user: str) -> None:
    if not frappe.db.exists("DocType", "Website Item"):
        failures.append("missing Website Item DocType")
        return
    if not frappe.has_permission("Website Item", ptype="read", user=user):
        failures.append(f"temporary {EXTERNAL_MARKETING_BUILDER_ROLE} user cannot read product pages")
    if not frappe.has_permission("Website Item", ptype="write", user=user):
        failures.append(f"temporary {EXTERNAL_MARKETING_BUILDER_ROLE} user cannot write product pages")
    for ptype in ("create", "delete"):
        if frappe.has_permission("Website Item", ptype=ptype, user=user):
            failures.append(f"temporary {EXTERNAL_MARKETING_BUILDER_ROLE} user can {ptype} product pages")


def _user_can_list_records(doctype: str, user: str) -> bool:
    original_user = frappe.session.user
    try:
        frappe.set_user(user)
        if frappe.get_meta(doctype).issingle:
            return False
        return bool(frappe.get_list(doctype, fields=["name"], limit_page_length=1, ignore_permissions=False))
    except frappe.PermissionError:
        return False
    finally:
        frappe.set_user(original_user)


def _user_can_read_existing_record(doctype: str, user: str) -> bool:
    sample_name = _sample_record_name(doctype)
    if not sample_name:
        return False
    try:
        doc = frappe.get_doc(doctype, sample_name)
    except Exception:
        return False
    return bool(frappe.has_permission(doc=doc, ptype="read", user=user))


def _sample_record_name(doctype: str) -> str | None:
    meta = frappe.get_meta(doctype)
    if meta.issingle:
        return doctype
    return frappe.db.get_value(doctype, {}, "name", order_by="modified desc")


def _check_file_access(failures: list[str], user: str) -> None:
    """Frappe exposes public files through its File query; enforce the sensitive parts."""
    original_user = frappe.session.user
    try:
        frappe.set_user(user)
        private_rows = frappe.get_list(
            "File",
            filters={"is_private": 1},
            fields=["name"],
            limit_page_length=1,
            ignore_permissions=False,
        )
        if private_rows:
            failures.append(f"temporary {EXTERNAL_MARKETING_BUILDER_ROLE} user can list private File records")
    except frappe.PermissionError:
        pass
    finally:
        frappe.set_user(original_user)

    sample_name = frappe.db.get_value("File", {"is_private": 0}, "name", order_by="modified desc")
    if sample_name:
        sample = frappe.get_doc("File", sample_name)
        if frappe.has_permission(doc=sample, ptype="read", user=user):
            failures.append(f"temporary {EXTERNAL_MARKETING_BUILDER_ROLE} user can open File records")
        for ptype in ("create", "write", "delete"):
            if frappe.has_permission(doc=sample, ptype=ptype, user=user):
                failures.append(f"temporary {EXTERNAL_MARKETING_BUILDER_ROLE} user can {ptype} File records")
