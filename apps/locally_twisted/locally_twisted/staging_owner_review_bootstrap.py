"""One-time Frappe Cloud staging bootstrap for owner ecommerce review.

This module is intentionally staging-locked. It exists because a Frappe Cloud
custom-app deploy updates code and schema, but it does not populate a fresh
site's catalog, owner accounts, Product Setup rows, or gallery projection.
"""
from __future__ import annotations

import json
import importlib
import traceback
from pathlib import Path
from typing import Any

import frappe


JOB_NAME = "lt-staging-owner-review-bootstrap"
STATUS_KEY = "lt_staging_owner_review_bootstrap_status"
STATUS_FILE = "lt-staging-owner-review-bootstrap-status.json"
CONFIRMATION = "seed locally twisted staging owner review"
STAGING_SITE = "locallytwisted-staging.frappe.cloud"
OWNER_EMAIL = "locallytwisted@gmail.com"
MARKETING_EMAIL = "marketing@exploringnotboring.com"
DEVELOPER_EMAIL = "cameron@builtbycameron.com"
CATALOG_MIN_COUNTS = {
    "Item": 10685,
    "Item Price": 10666,
    "Website Item": 51,
}
OWNER_REVIEW_MIN_COUNTS = {
    **CATALOG_MIN_COUNTS,
    "LT Product Blueprint": 51,
    "Website Slideshow": 47,
    "Website Slideshow Item": 68,
}
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
def enqueue_staging_owner_review_bootstrap(
    confirm: str,
    expected_app_hash: str | None = None,
) -> dict[str, Any]:
    """Queue the staging data bootstrap.

    The long catalog import must run in a worker. Do not call the seed
    synchronously through an HTTP request; the request can time out while the
    database is still in a partial state.
    """
    _assert_staging(confirm)
    frappe.only_for("System Manager")
    expected_app_hash = _normalize_expected_app_hash(expected_app_hash)
    _set_status(
        "queued",
        {"message": "queued staging owner-review bootstrap"},
        expected_app_hash=expected_app_hash,
    )
    job = frappe.enqueue(
        "locally_twisted.staging_owner_review_bootstrap.run_staging_owner_review_bootstrap",
        queue="long",
        timeout=7200,
        expected_app_hash=expected_app_hash,
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
    status = _get_status()
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


def run_staging_owner_review_bootstrap(expected_app_hash: str | None = None) -> dict[str, Any]:
    _assert_staging(CONFIRMATION)
    expected_app_hash = _normalize_expected_app_hash(expected_app_hash)
    _set_status(
        "running",
        {"message": "starting staging owner-review bootstrap"},
        expected_app_hash=expected_app_hash,
    )
    summary: dict[str, Any] = {
        "steps": [],
        "expected_app_hash": expected_app_hash,
        "pre_counts": _counts(),
    }
    try:
        _run_seed_syncs(summary, before_catalog=True)
        _ensure_owner_user(summary)
        catalog_gaps = _count_gaps(_counts(), CATALOG_MIN_COUNTS)
        if catalog_gaps:
            _seed_catalog(summary, catalog_gaps)
        else:
            summary["steps"].append({"name": "seed_catalog", "action": "skipped_existing_catalog"})
        _assert_count_baseline("catalog", CATALOG_MIN_COUNTS)
        _run_seed_syncs(summary, before_catalog=False)
        _sync_product_setup_and_galleries(summary)
        _assert_count_baseline("owner_review", OWNER_REVIEW_MIN_COUNTS)
        frappe.clear_cache()
        frappe.db.commit()
        summary["post_counts"] = _counts()
        _set_status("success", summary, expected_app_hash=expected_app_hash)
        return summary
    except Exception as exc:
        frappe.db.rollback()
        summary["error"] = f"{type(exc).__name__}: {exc}"
        summary["traceback_tail"] = traceback.format_exc().splitlines()[-20:]
        summary["post_counts"] = _counts()
        _set_status("failure", summary, expected_app_hash=expected_app_hash)
        raise


def _assert_staging(confirm: str) -> None:
    if confirm != CONFIRMATION:
        frappe.throw("Wrong confirmation for staging owner-review bootstrap.", frappe.PermissionError)
    site = str(frappe.local.site or "")
    host = str(getattr(getattr(frappe.local, "request", None), "host", "") or "")
    site_name = site.lower().strip()
    host_name = host.lower().split(":", 1)[0].strip()
    forbidden = "locallytwisted.v.frappe.cloud" in site_name or "locallytwisted.com" in host_name
    allowed = site_name == STAGING_SITE or host_name == STAGING_SITE
    if forbidden or not allowed:
        frappe.throw(
            f"Staging owner-review bootstrap is blocked on site={site!r} host={host!r}.",
            frappe.PermissionError,
        )


def _set_status(
    state: str,
    payload: dict[str, Any],
    *,
    expected_app_hash: str | None = None,
) -> None:
    status = {
        "state": state,
        "site": frappe.local.site,
        "target_site": STAGING_SITE,
        "expected_app_hash": expected_app_hash,
        "updated_at": frappe.utils.now_datetime().isoformat(),
        "counts": _counts(),
        **payload,
    }
    frappe.cache().set_value(STATUS_KEY, status, expires_in_sec=86400)
    status_path = _status_path()
    status_path.parent.mkdir(parents=True, exist_ok=True)
    status_path.write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")


def _get_status() -> dict[str, Any]:
    cached = frappe.cache().get_value(STATUS_KEY)
    if isinstance(cached, dict) and cached:
        return cached
    status_path = _status_path()
    if not status_path.exists():
        return {}
    try:
        return json.loads(status_path.read_text(encoding="utf-8"))
    except ValueError as exc:
        return {
            "state": "failure",
            "message": f"durable bootstrap status could not be parsed: {exc}",
            "site": frappe.local.site,
        }


def _status_path() -> Path:
    return Path(frappe.get_site_path("private", "files", STATUS_FILE))


def _normalize_expected_app_hash(expected_app_hash: str | None) -> str | None:
    if not expected_app_hash:
        return None
    expected_app_hash = str(expected_app_hash).strip()
    if len(expected_app_hash) != 40 or any(char not in "0123456789abcdef" for char in expected_app_hash.lower()):
        frappe.throw("Expected app hash must be a full 40-character hex commit hash.", frappe.ValidationError)
    return expected_app_hash.lower()


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
        module = importlib.import_module(module_path)
        module = importlib.reload(module)
        execute = getattr(module, "execute")
        if module_path.endswith("sync_marketing_review_access"):
            result = execute(reviewer_email=MARKETING_EMAIL, send_welcome_email=False)
        else:
            result = execute()
        summary["steps"].append({"name": module_path.rsplit(".", 1)[-1], "result": _compact_result(result)})


def _seed_catalog(summary: dict[str, Any], catalog_gaps: dict[str, dict[str, int]]) -> None:
    from locally_twisted.seed.seed_catalog import execute

    guard_dir = Path(frappe.get_app_path("locally_twisted", "seed", "_guard"))
    result = execute(
        dry_run=False,
        destructive=True,
        backup_path="Frappe Cloud staging empty-site owner-review bootstrap; no customer data existed.",
        snapshot_path=str(guard_dir / "current-state-snapshot-2026-05-19-2314"),
        purge_scope_report=str(guard_dir / "16-catalog-purge-scope-dry-run.json"),
    )
    summary["steps"].append(
        {
            "name": "seed_catalog",
            "reason": "missing_or_partial_catalog_baseline",
            "gaps": catalog_gaps,
            "result": _compact_result(result),
        }
    )


def _sync_product_setup_and_galleries(summary: dict[str, Any]) -> None:
    from locally_twisted.seed.sync_product_blueprints_from_catalog import execute

    data_dir = frappe.get_app_path("locally_twisted", "seed", "_data")
    result = execute(write=True, apply_gallery=True, data_dir=data_dir)
    summary["steps"].append({"name": "sync_product_blueprints_from_catalog", "result": _compact_result(result)})


def _count_gaps(counts: dict[str, int], minimums: dict[str, int]) -> dict[str, dict[str, int]]:
    return {
        doctype: {"actual": int(counts.get(doctype) or 0), "minimum": minimum}
        for doctype, minimum in minimums.items()
        if int(counts.get(doctype) or 0) < minimum
    }


def _assert_count_baseline(label: str, minimums: dict[str, int]) -> None:
    gaps = _count_gaps(_counts(), minimums)
    if gaps:
        frappe.throw(
            f"Staging owner-review bootstrap did not reach the {label} baseline: {gaps}",
            frappe.ValidationError,
        )


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
