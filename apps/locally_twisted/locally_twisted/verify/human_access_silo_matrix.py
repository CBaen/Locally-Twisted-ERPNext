"""Live human-access matrix for LT Desk, portal, and reviewer roles."""
from __future__ import annotations

import json
from typing import Any

import frappe

from locally_twisted.maintenance.heartbeat import boundary_report as maintenance_boundary_report
from locally_twisted.maintenance.heartbeat import MAINTENANCE_WORKSPACE
from locally_twisted.marketing_review_access import (
    MARKETING_REVIEW_ROLE,
    MARKETING_REVIEW_ROUTE,
    marketing_role_boundary,
)
from locally_twisted.verify.persona_workspace_permissions import run as persona_workspace_permissions


ADMIN_USERS = {
    "Administrator": {"special_admin": True},
    "cameron@builtbycameron.com": {"required_roles": {"System Manager"}},
}

OWNER_USERS = {
    "locallytwisted@gmail.com": {
        "default_workspace": "LT Owner Home",
        "required_roles": {"System Manager", "LT Owner Access", "Item Manager"},
    }
}

PERSONA_USERS = {
    "lt-owner-temp@example.com": {
        "group": "owner-test",
        "default_workspace": "LT Owner Home",
        "required_roles": {
            "Accounts Manager",
            "Accounts User",
            "Item Manager",
            "LT Owner Access",
            "Newsletter Manager",
            "System Manager",
            "Website Manager",
        },
        "forbidden_roles": {"LT Marketing Review Access"},
    },
    "lt-manager-temp@example.com": {
        "group": "manager",
        "default_workspace": "LT Manager Home",
        "forbidden_roles": {
            "System Manager",
            "Website Manager",
            "Accounts Manager",
            "Item Manager",
            "Sales Master Manager",
            "LT Owner Access",
            "LT Accountant Access",
            "LT Marketing Review Access",
        },
        "forbidden_doctype_permissions": {
            "Item Price": {"read", "create", "write", "delete"},
            "Website Item": {"read", "create", "write", "delete"},
            "Web Page": {"read", "create", "write", "delete"},
        },
    },
    "lt-employee-temp@example.com": {
        "group": "employee",
        "default_workspace": "LT Employee Home",
        "forbidden_roles": {
            "System Manager",
            "Website Manager",
            "Accounts Manager",
            "Sales Manager",
            "Item Manager",
            "LT Owner Access",
            "LT Accountant Access",
            "LT Marketing Review Access",
        },
        "forbidden_doctype_permissions": {
            "Lead": {"read", "create", "write", "delete"},
            "Customer": {"read", "create", "write", "delete"},
            "Contact": {"read", "create", "write", "delete"},
            "Address": {"read", "create", "write", "delete"},
            "Sales Order": {"read", "create", "write", "delete"},
            "Sales Invoice": {"read", "create", "write", "delete"},
            "Item Price": {"read", "create", "write", "delete"},
            "Website Item": {"read", "create", "write", "delete"},
            "Web Page": {"read", "create", "write", "delete"},
        },
    },
    "lt-accountant-temp@example.com": {
        "group": "accounting",
        "default_workspace": "LT Accountant Home",
        "required_roles": {"LT Accountant Access"},
        "forbidden_roles": {
            "System Manager",
            "Website Manager",
            "Item Manager",
            "LT Owner Access",
            "LT Marketing Review Access",
        },
        "forbidden_doctype_permissions": {
            "Lead": {"read", "create", "write", "delete"},
            "Project": {"read", "create", "write", "delete"},
            "Task": {"read", "create", "write", "delete"},
            "Item Price": {"read", "create", "write", "delete"},
            "Website Item": {"read", "create", "write", "delete"},
            "Web Page": {"read", "create", "write", "delete"},
        },
    },
}

WORKSPACES = {
    "LT Owner Home": {
        "title": "Owner Home",
        "landing_for": ["owner", "admin/owner fallback"],
        "required_roles": {"LT Owner Access"},
    },
    "LT Manager Home": {
        "title": "Manager Home",
        "landing_for": ["manager"],
        "required_roles": {"LT Manager Access"},
    },
    "LT Employee Home": {
        "title": "My Jobs",
        "landing_for": ["employee"],
        "required_roles": {"LT Employee Access"},
    },
    "LT Accountant Home": {
        "title": "Accounting Home",
        "landing_for": ["accounting"],
        "required_roles": {"LT Accountant Access"},
    },
    "LT Marketing Home": {
        "title": "Marketing Home",
        "landing_for": ["internal marketing/admin only"],
        "required_roles": {"LT Owner Access", "Website Manager", "Newsletter Manager", "System Manager"},
        "forbidden_roles": {MARKETING_REVIEW_ROLE},
    },
    MAINTENANCE_WORKSPACE: {
        "title": "Maintenance Home",
        "landing_for": ["maintenance"],
        "required_roles": {"LT Maintenance Admin Access"},
    },
}

FULL_ACCESS_DOCTYPES = [
    "Lead",
    "Customer",
    "Contact",
    "Sales Order",
    "Sales Invoice",
    "Payment Request",
    "Payment Entry",
    "Item",
    "Item Price",
    "Website Item",
    "Web Page",
    "Project",
    "Task",
    "File",
    "LT Product Blueprint",
]


def run() -> dict[str, Any]:
    failures: list[str] = []
    matrix = {
        "admin": _admin_report(failures),
        "owner": _owner_report(failures),
        "desk_personas": _persona_report(failures),
        "workspaces": _workspace_report(failures),
        "external_marketing": _external_marketing_report(failures),
        "maintenance": _maintenance_report(failures),
        "customer_portal": _customer_portal_report(failures),
        "indexing": _indexing_report(),
    }

    permission_failures = persona_workspace_permissions().get("failures") or []
    failures.extend(permission_failures)
    matrix["desk_persona_shortcut_permissions"] = {
        "ok": not permission_failures,
        "failures": permission_failures,
    }

    return {
        "ok": not failures,
        "failures": sorted(set(failures)),
        "matrix": matrix,
    }


def _admin_report(failures: list[str]) -> dict[str, Any]:
    users = {}
    for user, spec in ADMIN_USERS.items():
        users[user] = _user_report(user)
        if users[user].get("missing"):
            failures.append(f"admin user {user} is missing")
            continue
        if not spec.get("special_admin"):
            _require_roles(user, users[user]["roles"], spec.get("required_roles") or set(), failures)
        _require_full_access(user, failures)
    return {"users": users, "full_access_doctypes": _existing_full_access_doctypes()}


def _owner_report(failures: list[str]) -> dict[str, Any]:
    users = {}
    for user, spec in OWNER_USERS.items():
        users[user] = _user_report(user)
        if users[user].get("missing"):
            failures.append(f"owner user {user} is missing")
            continue
        if users[user].get("default_workspace") != spec["default_workspace"]:
            failures.append(
                f"owner user {user} default_workspace expected {spec['default_workspace']!r}, "
                f"found {users[user].get('default_workspace')!r}"
            )
        _require_roles(user, users[user]["roles"], spec["required_roles"], failures)
        _require_full_access(user, failures)
    return {"users": users, "full_access_doctypes": _existing_full_access_doctypes()}


def _persona_report(failures: list[str]) -> dict[str, Any]:
    users = {}
    for user, spec in PERSONA_USERS.items():
        users[user] = _user_report(user)
        if users[user].get("missing"):
            continue
        if users[user].get("user_type") != "System User":
            failures.append(f"{user} should be a System User for Desk landing checks")
        if users[user].get("default_workspace") != spec["default_workspace"]:
            failures.append(
                f"{user} default_workspace expected {spec['default_workspace']!r}, "
                f"found {users[user].get('default_workspace')!r}"
            )
        _require_roles(user, users[user]["roles"], spec.get("required_roles") or set(), failures)
        _forbid_roles(user, users[user]["roles"], spec.get("forbidden_roles") or set(), failures)
        _forbid_doctype_permissions(
            user,
            spec.get("forbidden_doctype_permissions") or {},
            failures,
        )
    return {"users": users}


def _workspace_report(failures: list[str]) -> dict[str, Any]:
    workspaces = {}
    for name, spec in WORKSPACES.items():
        if not frappe.db.exists("Workspace", name):
            failures.append(f"missing workspace {name}")
            workspaces[name] = {"missing": True}
            continue

        doc = frappe.get_doc("Workspace", name)
        roles = {row.role for row in doc.roles}
        workspaces[name] = {
            "title": doc.title,
            "module": doc.module,
            "roles": sorted(roles),
            "landing_for": spec["landing_for"],
        }
        if doc.title != spec["title"]:
            failures.append(f"{name} title expected {spec['title']!r}, found {doc.title!r}")
        _require_roles(f"workspace {name}", roles, spec.get("required_roles") or set(), failures)
        _forbid_roles(f"workspace {name}", roles, spec.get("forbidden_roles") or set(), failures)
    return workspaces


def _external_marketing_report(failures: list[str]) -> dict[str, Any]:
    boundary = marketing_role_boundary()
    if not boundary.get("ok"):
        failures.extend(boundary.get("failures") or [])
    if boundary.get("desk_access") != 0:
        failures.append(f"{MARKETING_REVIEW_ROLE} must not grant Desk access")
    if frappe.db.count("DocPerm", {"role": MARKETING_REVIEW_ROLE}):
        failures.append(f"{MARKETING_REVIEW_ROLE} must not have DocPerm rows")

    role_home = _role_home_page_hook()
    if _hook_value(role_home.get(MARKETING_REVIEW_ROLE)) != MARKETING_REVIEW_ROUTE.lstrip("/"):
        failures.append(f"{MARKETING_REVIEW_ROLE} should land on {MARKETING_REVIEW_ROUTE}")

    return {
        "role": MARKETING_REVIEW_ROLE,
        "desk_access": boundary.get("desk_access"),
        "review_route": MARKETING_REVIEW_ROUTE,
        "docperm_rows": frappe.db.count("DocPerm", {"role": MARKETING_REVIEW_ROLE}),
        "forbidden_doctypes_checked": boundary.get("forbidden_doctypes"),
        "indexing_authority": "none; no Desk, no Website Manager, no Website records, no Search Console path",
    }


def _maintenance_report(failures: list[str]) -> dict[str, Any]:
    report = maintenance_boundary_report()
    if not report.get("ok"):
        failures.extend(report.get("failures") or [])
    for key, expected in {
        "sanitized": True,
        "raw_log_access": False,
        "customer_data_included": False,
    }.items():
        if report.get(key) is not expected:
            failures.append(f"maintenance {key} expected {expected}, found {report.get(key)}")
    return {
        "role": report.get("role"),
        "workspace": report.get("workspace"),
        "sanitized": report.get("sanitized"),
        "raw_log_access": report.get("raw_log_access"),
        "customer_data_included": report.get("customer_data_included"),
    }


def _customer_portal_report(failures: list[str]) -> dict[str, Any]:
    website = frappe.get_single("Website Settings")
    portal = frappe.get_single("Portal Settings")
    report = {
        "signup_disabled": int(website.disable_signup or 0) == 1,
        "default_portal_home": portal.default_portal_home,
        "default_role": portal.default_role,
    }
    if not report["signup_disabled"]:
        failures.append("Website Settings.disable_signup must stay enabled for invite-only customer access")
    if portal.default_role:
        failures.append("Portal Settings.default_role should stay empty; do not auto-grant customer roles")
    if portal.default_portal_home != "me":
        failures.append("Portal Settings.default_portal_home should be 'me'")
    return report


def _indexing_report() -> dict[str, str]:
    return {
        "status": "parked",
        "rule": "No Search Console submission, sitemap submission, reindex request, or external marketing indexing work until shop is on staging and owner approves products to go live.",
        "marketing_company": "review-only public doorway; no ERPNext Desk or indexing authority",
    }


def _user_report(user: str) -> dict[str, Any]:
    if not frappe.db.exists("User", user):
        return {"missing": True}
    doc = frappe.get_doc("User", user)
    return {
        "enabled": int(doc.enabled or 0),
        "user_type": doc.user_type,
        "role_profile_name": doc.role_profile_name,
        "default_workspace": doc.default_workspace,
        "roles": sorted(row.role for row in doc.roles),
    }


def _require_roles(subject: str, actual: set[str] | list[str], expected: set[str], failures: list[str]) -> None:
    actual_set = set(actual)
    for role in sorted(role for role in expected if frappe.db.exists("Role", role)):
        if role not in actual_set:
            failures.append(f"{subject} missing required role {role}")


def _forbid_roles(subject: str, actual: set[str] | list[str], forbidden: set[str], failures: list[str]) -> None:
    actual_set = set(actual)
    for role in sorted(actual_set & forbidden):
        failures.append(f"{subject} must not have role {role}")


def _forbid_doctype_permissions(
    user: str,
    spec: dict[str, set[str]],
    failures: list[str],
) -> None:
    for doctype, ptypes in spec.items():
        if not frappe.db.exists("DocType", doctype):
            continue
        for ptype in sorted(ptypes):
            if frappe.has_permission(doctype, ptype=ptype, user=user):
                failures.append(f"{user} must not have {ptype} permission on {doctype}")


def _require_full_access(user: str, failures: list[str]) -> None:
    for doctype in _existing_full_access_doctypes():
        for ptype in ("read", "create", "write"):
            if not frappe.has_permission(doctype, ptype=ptype, user=user):
                failures.append(f"{user} lacks {ptype} permission on {doctype}")


def _existing_full_access_doctypes() -> list[str]:
    return [doctype for doctype in FULL_ACCESS_DOCTYPES if frappe.db.exists("DocType", doctype)]


def _role_home_page_hook() -> dict[str, str]:
    hooks = frappe.get_hooks("role_home_page") or {}
    if isinstance(hooks, dict):
        return hooks
    return {}


def _hook_value(value: Any) -> Any:
    if isinstance(value, list):
        return value[0] if value else None
    return value


def to_json() -> str:
    return json.dumps(run(), indent=2, sort_keys=True, default=str)
