"""One-time Frappe Cloud staging bootstrap for owner ecommerce review.

This module is intentionally staging-locked. It exists because a Frappe Cloud
custom-app deploy updates code and schema, but it does not populate a fresh
site's catalog, owner accounts, Product Setup rows, or gallery projection.
"""
from __future__ import annotations

import json
import traceback
from pathlib import Path
from typing import Any

import frappe


JOB_NAME = "lt-staging-owner-review-bootstrap"
STATUS_KEY = "lt_staging_owner_review_bootstrap_status"
CONFIRMATION = "seed locally twisted staging owner review"
OWNER_EMAIL = "locallytwisted@gmail.com"
MARKETING_EMAIL = "marketing@exploringnotboring.com"
DEVELOPER_EMAIL = "cameron@builtbycameron.com"
OWNER_ROLES = (
    "Desk User",
    "LT Owner Access",
    "Sales Manager",
    "Sales User",
    "Projects Manager",
    "Projects User",
    "Prepared Report User",
    "Sales Master Manager",
    "Item Manager",
    "Accounts Manager",
    "Accounts User",
    "Newsletter Manager",
    "System Manager",
    "Website Manager",
    "Customer",
)


@frappe.whitelist()
def enqueue_staging_owner_review_bootstrap(confirm: str) -> dict[str, Any]:
    """Queue the staging data bootstrap.

    The long catalog import must run in a worker. Do not call the seed
    synchronously through an HTTP request; the request can time out while the
    database is still in a partial state.
    """
    _assert_staging(confirm)
    frappe.only_for("System Manager")
    _set_status("queued", {"message": "queued staging owner-review bootstrap"})
    job = frappe.enqueue(
        "locally_twisted.staging_owner_review_bootstrap.run_staging_owner_review_bootstrap",
        queue="long",
        timeout=7200,
        job_name=JOB_NAME,
        job_id=JOB_NAME,
        enqueue_after_commit=False,
        deduplicate=True,
    )
    return {"ok": True, "job_name": JOB_NAME, "job_id": getattr(job, "id", None)}


@frappe.whitelist()
def get_staging_owner_review_bootstrap_status(confirm: str) -> dict[str, Any]:
    _assert_staging(confirm)
    frappe.only_for("System Manager")
    status = frappe.cache().get_value(STATUS_KEY) or {}
    return {
        "ok": True,
        "status": status,
        "counts": _counts(),
        "accounts": {
            email: {
                "exists": bool(frappe.db.exists("User", email)),
                "enabled": int(frappe.db.get_value("User", email, "enabled") or 0),
                "user_type": frappe.db.get_value("User", email, "user_type"),
                "roles": frappe.get_roles(email) if frappe.db.exists("User", email) else [],
            }
            for email in (OWNER_EMAIL, MARKETING_EMAIL, DEVELOPER_EMAIL)
        },
    }


def run_staging_owner_review_bootstrap() -> dict[str, Any]:
    _assert_staging(CONFIRMATION)
    _set_status("running", {"message": "starting staging owner-review bootstrap", "counts": _counts()})
    summary: dict[str, Any] = {"steps": [], "pre_counts": _counts()}
    try:
        _ensure_owner_user(summary)
        _run_seed_syncs(summary, before_catalog=True)
        if _counts()["Website Item"] == 0 or _counts()["Item"] == 0:
            _seed_catalog(summary)
        else:
            summary["steps"].append({"name": "seed_catalog", "action": "skipped_existing_catalog"})
        _run_seed_syncs(summary, before_catalog=False)
        _sync_product_setup_and_galleries(summary)
        frappe.clear_cache()
        frappe.db.commit()
        summary["post_counts"] = _counts()
        _set_status("success", summary)
        return summary
    except Exception as exc:
        frappe.db.rollback()
        summary["error"] = f"{type(exc).__name__}: {exc}"
        summary["traceback_tail"] = traceback.format_exc().splitlines()[-20:]
        summary["post_counts"] = _counts()
        _set_status("failure", summary)
        raise


def _assert_staging(confirm: str) -> None:
    if confirm != CONFIRMATION:
        frappe.throw("Wrong confirmation for staging owner-review bootstrap.", frappe.PermissionError)
    site = str(frappe.local.site or "")
    host = str(getattr(getattr(frappe.local, "request", None), "host", "") or "")
    allowed_by_site = "staging" in site.lower() or "staging" in host.lower()
    allowed_by_config = bool(frappe.conf.get("lt_allow_staging_bootstrap"))
    forbidden = "locallytwisted.v.frappe.cloud" in site or "locallytwisted.com" in host
    if forbidden or not (allowed_by_site or allowed_by_config):
        frappe.throw(
            f"Staging owner-review bootstrap is blocked on site={site!r} host={host!r}.",
            frappe.PermissionError,
        )


def _set_status(state: str, payload: dict[str, Any]) -> None:
    frappe.cache().set_value(
        STATUS_KEY,
        {
            "state": state,
            "site": frappe.local.site,
            "updated_at": frappe.utils.now_datetime().isoformat(),
            **payload,
        },
        expires_in_sec=86400,
    )


def _counts() -> dict[str, int]:
    return {
        doctype: frappe.db.count(doctype)
        for doctype in (
            "Item",
            "Item Price",
            "Website Item",
            "Website Slideshow",
            "Website Slideshow Item",
            "LT Product Blueprint",
            "User",
        )
        if frappe.db.table_exists(doctype)
    }


def _ensure_owner_user(summary: dict[str, Any]) -> None:
    _ensure_roles(OWNER_ROLES)
    fields = {
        "email": OWNER_EMAIL,
        "first_name": "Jeff",
        "last_name": "Kimber",
        "enabled": 1,
        "user_type": "System User",
        "send_welcome_email": 0,
        "default_workspace": "LT Owner Home",
        "time_zone": "America/Denver",
    }
    action = "unchanged"
    if frappe.db.exists("User", OWNER_EMAIL):
        doc = frappe.get_doc("User", OWNER_EMAIL)
    else:
        doc = frappe.get_doc({"doctype": "User", **fields})
        action = "created"

    changed = doc.is_new()
    for fieldname, value in fields.items():
        if doc.meta.has_field(fieldname) and doc.get(fieldname) != value:
            doc.set(fieldname, value)
            changed = True
    existing_roles = {row.role for row in doc.roles}
    for role in OWNER_ROLES:
        if role not in existing_roles:
            doc.append("roles", {"role": role})
            changed = True
    if doc.is_new():
        doc.insert(ignore_permissions=True)
    elif changed:
        action = "repaired"
        doc.save(ignore_permissions=True)
    summary["steps"].append({"name": "ensure_owner_user", "action": action, "roles": list(OWNER_ROLES)})


def _ensure_roles(roles: tuple[str, ...]) -> None:
    for role in roles:
        if not frappe.db.exists("Role", role):
            frappe.get_doc({"doctype": "Role", "role_name": role, "desk_access": 1}).insert(
                ignore_permissions=True
            )


def _run_seed_syncs(summary: dict[str, Any], *, before_catalog: bool) -> None:
    modules = (
        (
            "locally_twisted.seed.sync_contact_intake_backend",
            "locally_twisted.seed.sync_crm_pipeline",
            "locally_twisted.seed.sync_stage_cascade",
            "locally_twisted.seed.sync_backend_workspaces",
            "locally_twisted.seed.sync_marketing_workspace",
            "locally_twisted.seed.sync_customer_portal",
            "locally_twisted.seed.sync_finance_workspace",
            "locally_twisted.seed.sync_site_branding",
            "locally_twisted.seed.sync_permission_hardening",
        )
        if before_catalog
        else (
            "locally_twisted.seed.sync_marketing_review_access",
            "locally_twisted.seed.sync_maintenance_package",
        )
    )
    for module_path in modules:
        module = frappe.get_attr(f"{module_path}.execute")
        if module_path.endswith("sync_marketing_review_access"):
            result = module(reviewer_email=MARKETING_EMAIL, send_welcome_email=False)
        else:
            result = module()
        summary["steps"].append({"name": module_path.rsplit(".", 1)[-1], "result": _compact_result(result)})


def _seed_catalog(summary: dict[str, Any]) -> None:
    from locally_twisted.seed.seed_catalog import execute

    guard_dir = Path(frappe.get_app_path("locally_twisted", "seed", "_guard"))
    result = execute(
        dry_run=False,
        destructive=True,
        backup_path="Frappe Cloud staging empty-site owner-review bootstrap; no customer data existed.",
        snapshot_path=str(guard_dir / "current-state-snapshot-2026-05-19-2314"),
        purge_scope_report=str(guard_dir / "16-catalog-purge-scope-dry-run.json"),
    )
    summary["steps"].append({"name": "seed_catalog", "result": _compact_result(result)})


def _sync_product_setup_and_galleries(summary: dict[str, Any]) -> None:
    from locally_twisted.seed.sync_product_blueprints_from_catalog import execute

    data_dir = frappe.get_app_path("locally_twisted", "seed", "_data")
    result = execute(write=True, apply_gallery=True, data_dir=data_dir)
    summary["steps"].append({"name": "sync_product_blueprints_from_catalog", "result": _compact_result(result)})


def _compact_result(result: Any) -> Any:
    if isinstance(result, str):
        try:
            parsed = json.loads(result)
        except ValueError:
            return result[:1000]
    else:
        parsed = result
    if isinstance(parsed, dict):
        keys = ("ok", "dry_run", "summary", "committed", "boundary_ok", "products_seeded", "variants_created")
        return {key: parsed.get(key) for key in keys if key in parsed}
    return parsed
