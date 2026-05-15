"""Verify LT custom DocTypes do not expose broad All mutation rights."""
from __future__ import annotations

import frappe


GOVERNED_DOCTYPES = {
    "LT Service Type": {
        "required": True,
        "admin_only": False,
    },
    "Dashboard Reviewed Item": {
        "required": False,
        "admin_only": True,
    },
}
MUTATION_PERMISSIONS = ("write", "create", "delete", "submit", "cancel", "amend", "export", "import", "share")
WEBSITE_USER_FORBIDDEN = ("write", "create", "delete", "export", "share")


def run() -> dict[str, object]:
    failures: list[str] = []
    checked: list[dict[str, object]] = []
    governed = _governed_doctypes()

    for doctype_name, policy in governed.items():
        if not frappe.db.exists("DocType", doctype_name):
            if policy["required"]:
                failures.append(f"{doctype_name} DocType is missing")
            checked.append({"doctype": doctype_name, "exists": False})
            continue

        doc = frappe.get_doc("DocType", doctype_name)
        checked.append(
            {
                "doctype": doctype_name,
                "exists": True,
                "roles": [row.role for row in doc.permissions],
            }
        )
        failures.extend(_all_mutation_failures(doctype_name, doc.permissions))
        if policy["admin_only"]:
            failures.extend(_admin_only_failures(doctype_name, doc.permissions))

    failures.extend(_website_user_mutation_failures("LT Service Type"))

    return {
        "ok": not failures,
        "checked": checked,
        "website_users": _enabled_website_users(),
        "forbidden_website_permissions": list(WEBSITE_USER_FORBIDDEN),
        "failures": sorted(set(failures)),
    }


def _governed_doctypes() -> dict[str, dict[str, bool]]:
    governed = dict(GOVERNED_DOCTYPES)
    for row in frappe.get_all(
        "DocType",
        filters=[["name", "like", "LT %"]],
        fields=["name", "istable"],
        limit_page_length=500,
    ):
        if row.get("istable"):
            continue
        governed.setdefault(row["name"], {"required": False, "admin_only": False})
    return dict(sorted(governed.items()))


def _all_mutation_failures(doctype_name: str, permission_rows) -> list[str]:
    failures = []
    for row in permission_rows:
        if row.role != "All":
            continue
        enabled = [fieldname for fieldname in MUTATION_PERMISSIONS if int(row.get(fieldname) or 0)]
        if enabled:
            failures.append(
                f"{doctype_name} grants role All mutation permissions: {', '.join(sorted(enabled))}"
            )
    return failures


def _admin_only_failures(doctype_name: str, permission_rows) -> list[str]:
    failures = []
    roles = {row.role for row in permission_rows}
    if roles != {"System Manager"}:
        failures.append(
            f"{doctype_name} is retained but is not restricted to System Manager only: {', '.join(sorted(roles))}"
        )
    system_row = next((row for row in permission_rows if row.role == "System Manager"), None)
    if not system_row or not int(system_row.get("read") or 0):
        failures.append(f"{doctype_name} retained admin permission is missing System Manager read access")
    return failures


def _website_user_mutation_failures(doctype_name: str) -> list[str]:
    failures = []
    if not frappe.db.exists("DocType", doctype_name):
        return [f"{doctype_name} DocType is missing"]

    for user in _enabled_website_users():
        for ptype in WEBSITE_USER_FORBIDDEN:
            if frappe.has_permission(doctype_name, ptype=ptype, user=user):
                failures.append(f"{user} has {ptype} permission on {doctype_name}")
    return failures


def _enabled_website_users() -> list[str]:
    users = frappe.get_all(
        "User",
        filters={"enabled": 1, "user_type": "Website User"},
        pluck="name",
        order_by="name asc",
    )
    if frappe.db.exists("User", "Guest") and "Guest" not in users:
        users.append("Guest")
    return sorted(set(users))
