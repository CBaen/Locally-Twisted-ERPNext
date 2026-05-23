"""Non-mutating preflight checks for staging owner-review bootstrap."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import frappe


STAGING_SITE = "locallytwisted-staging.frappe.cloud"
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
MARKETING_REVIEW_ROLE = "LT Marketing Review Access"
REQUIRED_BOOTSTRAP_ROLES = tuple(sorted(set(OWNER_ROLES + (MARKETING_REVIEW_ROLE,))))
EXPECTED_APP_ORDER = ["frappe", "erpnext", "payments", "webshop", "locally_twisted"]
PREFLIGHT_REQUIRED_CHECKS = (
    "standard_report",
    "roles",
    "settings",
    "app_hooks",
    "app_order",
    "target_hash",
    "baseline_counts",
    "destructive_seed_evidence",
)
REQUIRED_SINGLE_SETTINGS = {
    "Website Settings": {
        "disable_signup": 1,
        "hide_login": 0,
        "home_page": "home",
    },
    "Portal Settings": {
        "default_portal_home": "me",
        "default_role": None,
        "hide_standard_menu": 0,
    },
    "Webshop Settings": {
        "enabled": 1,
        "login_required_to_view_products": 0,
        "hide_price_for_guest": 0,
        "show_price": 1,
    },
}
ZERO_DATA_DOCTYPES = (
    "Lead",
    "Opportunity",
    "Quotation",
    "Sales Order",
    "Sales Invoice",
    "Payment Entry",
    "Communication",
    "Email Queue",
)


def build_bootstrap_preflight(
    *,
    expected_app_hash: str | None,
    backup_artifact: Any = None,
    zero_data_proof: Any = None,
) -> dict[str, Any]:
    counts = _counts()
    zero_data_counts = _zero_data_counts()
    catalog_gaps = count_gaps(counts, CATALOG_MIN_COUNTS)
    checks = {
        "standard_report": _check_standard_report_save_contract(),
        "roles": _check_required_roles(),
        "settings": _check_required_settings(),
        "app_hooks": _check_app_hooks(),
        "app_order": _check_app_order(),
        "target_hash": _check_target_hash(expected_app_hash),
        "baseline_counts": {
            "ok": True,
            "counts": counts,
            "catalog_minimums": CATALOG_MIN_COUNTS,
            "owner_review_minimums": OWNER_REVIEW_MIN_COUNTS,
            "catalog_gaps": catalog_gaps,
            "owner_review_gaps": count_gaps(counts, OWNER_REVIEW_MIN_COUNTS),
            "catalog_seed_required": bool(catalog_gaps),
        },
        "destructive_seed_evidence": _validate_destructive_seed_evidence(
            catalog_gaps=catalog_gaps,
            backup_artifact=backup_artifact,
            zero_data_proof=zero_data_proof,
            zero_data_counts=zero_data_counts,
        ),
    }
    failures = _preflight_failures(checks)
    return {
        "ok": not failures,
        "target_site": STAGING_SITE,
        "expected_app_hash": expected_app_hash,
        "required_checks": list(PREFLIGHT_REQUIRED_CHECKS),
        "checks": checks,
        "failures": failures,
        "zero_data_counts": zero_data_counts,
    }


def assert_preflight_allows_catalog_mutation(preflight: dict[str, Any]) -> None:
    if preflight.get("ok"):
        return
    frappe.throw(
        "Staging owner-review bootstrap preflight blocked catalog mutation: "
        + "; ".join(str(failure) for failure in preflight.get("failures") or []),
        frappe.ValidationError,
    )


def seed_catalog_backup_path(preflight: dict[str, Any]) -> str:
    evidence = ((preflight.get("checks") or {}).get("destructive_seed_evidence") or {})
    if evidence.get("ok") is not True:
        frappe.throw("Destructive catalog seed is blocked without preflight backup evidence.", frappe.ValidationError)
    backup_path = str(evidence.get("backup_path") or "").strip()
    if not backup_path or _looks_like_descriptive_backup_string(backup_path):
        frappe.throw("Destructive catalog seed backup evidence is not an artifact or zero-data proof.", frappe.ValidationError)
    return backup_path


def count_gaps(counts: dict[str, int], minimums: dict[str, int]) -> dict[str, dict[str, int]]:
    return {
        doctype: {"actual": int(counts.get(doctype) or 0), "minimum": minimum}
        for doctype, minimum in minimums.items()
        if int(counts.get(doctype) or 0) < minimum
    }


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


def _preflight_failures(checks: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for check_name in PREFLIGHT_REQUIRED_CHECKS:
        check = checks.get(check_name)
        if not isinstance(check, dict):
            failures.append(f"{check_name}: missing check")
            continue
        if check.get("ok") is True:
            continue
        check_failures = check.get("failures") or ["check did not pass"]
        for failure in check_failures:
            failures.append(f"{check_name}: {failure}")
    return failures


def _check_standard_report_save_contract() -> dict[str, Any]:
    failures: list[str] = []
    try:
        from locally_twisted.seed.standard_report_import import standard_report_import_context
    except Exception as exc:
        return {"ok": False, "failures": [f"standard report import context unavailable: {exc}"]}
    if not callable(standard_report_import_context):
        failures.append("standard_report_import_context is not callable")
    return {
        "ok": not failures,
        "context": "locally_twisted.seed.standard_report_import.standard_report_import_context",
        "doctype": "Report",
        "required_flags": ["in_import", "in_patch", "in_install"],
        "mutates": False,
        "failures": failures,
    }


def _check_required_roles() -> dict[str, Any]:
    roles: dict[str, dict[str, Any]] = {}
    failures: list[str] = []
    for role in REQUIRED_BOOTSTRAP_ROLES:
        exists = bool(frappe.db.exists("Role", role))
        disabled = frappe.db.get_value("Role", role, "disabled") if exists else None
        roles[role] = {"exists": exists, "disabled": int(disabled or 0) if exists else None}
        if not exists:
            failures.append(f"missing Role {role!r}")
        elif int(disabled or 0):
            failures.append(f"disabled Role {role!r}")
    return {"ok": not failures, "roles": roles, "failures": failures}


def _check_required_settings() -> dict[str, Any]:
    settings: dict[str, Any] = {}
    failures: list[str] = []
    for doctype, expected_fields in REQUIRED_SINGLE_SETTINGS.items():
        try:
            doc = frappe.get_single(doctype)
        except Exception as exc:
            settings[doctype] = {"exists": False, "error": f"{type(exc).__name__}: {exc}"}
            failures.append(f"{doctype} could not be loaded")
            continue
        values: dict[str, Any] = {}
        for fieldname, expected in expected_fields.items():
            actual = doc.get(fieldname)
            values[fieldname] = {"actual": actual, "expected": expected, "ok": actual == expected}
            if actual != expected:
                failures.append(f"{doctype}.{fieldname}={actual!r}, expected {expected!r}")
        settings[doctype] = {"exists": True, "fields": values}
    return {"ok": not failures, "settings": settings, "failures": failures}


def _check_app_hooks() -> dict[str, Any]:
    failures: list[str] = []
    hooks = frappe.get_hooks("doc_events") or {}
    required = {
        "Website Settings": "locally_twisted.public_access_guard.validate_public_access_boundary",
        "Portal Settings": "locally_twisted.public_access_guard.validate_public_access_boundary",
    }
    present: dict[str, bool] = {}
    for doctype, dotted_path in required.items():
        hook_values = json.dumps(hooks.get(doctype) or {})
        present[doctype] = dotted_path in hook_values
        if not present[doctype]:
            failures.append(f"{doctype} is missing public access guard hook")
    return {"ok": not failures, "required_hooks": required, "present": present, "failures": failures}


def _check_app_order() -> dict[str, Any]:
    installed_apps = list(frappe.get_installed_apps() or [])
    failures: list[str] = []
    if installed_apps != EXPECTED_APP_ORDER:
        failures.append(f"installed app order is {installed_apps}, expected {EXPECTED_APP_ORDER}")
    return {"ok": not failures, "installed_apps": installed_apps, "expected_app_order": EXPECTED_APP_ORDER, "failures": failures}


def _check_target_hash(expected_app_hash: str | None) -> dict[str, Any]:
    current_hash = _current_locally_twisted_app_hash()
    failures: list[str] = []
    if not expected_app_hash:
        failures.append("expected_app_hash is required before hosted bootstrap mutation")
    if not current_hash:
        failures.append("current locally_twisted app hash could not be read from the hosted app checkout")
    elif expected_app_hash and current_hash != expected_app_hash:
        failures.append(f"current app hash {current_hash} != expected target hash {expected_app_hash}")
    return {
        "ok": not failures,
        "expected_app_hash": expected_app_hash,
        "current_app_hash": current_hash,
        "failures": failures,
    }


def _current_locally_twisted_app_hash() -> str | None:
    try:
        app_root = Path(frappe.get_app_path("locally_twisted")).parent
        result = subprocess.run(
            ["git", "-C", str(app_root), "rev-parse", "HEAD"],
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except Exception:
        return None
    app_hash = result.stdout.strip().lower()
    if result.returncode != 0 or len(app_hash) != 40 or any(char not in "0123456789abcdef" for char in app_hash):
        return None
    return app_hash


def _validate_destructive_seed_evidence(
    *,
    catalog_gaps: dict[str, dict[str, int]],
    backup_artifact: Any,
    zero_data_proof: Any,
    zero_data_counts: dict[str, int],
) -> dict[str, Any]:
    if not catalog_gaps:
        return {"ok": True, "required": False, "mode": "not_required_existing_catalog", "failures": []}

    backup_check = _validate_backup_artifact_evidence(backup_artifact)
    if backup_check.get("ok"):
        backup_check.update({"required": True, "mode": "backup_artifact"})
        return backup_check

    zero_data_check = _validate_zero_data_proof(zero_data_proof, zero_data_counts)
    if zero_data_check.get("ok"):
        zero_data_check.update({"required": True, "mode": "explicit_zero_data"})
        return zero_data_check

    return {
        "ok": False,
        "required": True,
        "catalog_gaps": catalog_gaps,
        "backup_artifact_failures": backup_check.get("failures") or [],
        "zero_data_proof_failures": zero_data_check.get("failures") or [],
        "failures": [
            "destructive catalog seed requires a real backup_artifact or explicit zero_data_proof"
        ],
    }


def _validate_backup_artifact_evidence(raw_artifact: Any) -> dict[str, Any]:
    artifact, parse_failure = _coerce_mapping(raw_artifact, "backup_artifact")
    failures: list[str] = [parse_failure] if parse_failure else []
    if not artifact:
        failures.append("backup_artifact is missing")
        return {"ok": False, "failures": failures}

    reference = (
        artifact.get("backup_path")
        or artifact.get("artifact_path")
        or artifact.get("path")
        or artifact.get("backup_id")
        or artifact.get("name")
    )
    site = artifact.get("site") or artifact.get("target_site")
    if not reference or not str(reference).strip():
        failures.append("backup_artifact must include backup_path/artifact_path/path/backup_id/name")
    elif _looks_like_descriptive_backup_string(str(reference)):
        failures.append("backup_artifact reference is descriptive text, not an artifact reference")
    if site != STAGING_SITE:
        failures.append(f"backup_artifact site {site!r} does not match {STAGING_SITE!r}")
    if not artifact.get("created_at"):
        failures.append("backup_artifact must include created_at")
    if artifact.get("with_files") is not True:
        failures.append("backup_artifact must prove with_files=true")
    return {
        "ok": not failures,
        "backup_path": str(reference) if reference else None,
        "backup_artifact": artifact,
        "failures": failures,
    }


def _validate_zero_data_proof(raw_proof: Any, zero_data_counts: dict[str, int]) -> dict[str, Any]:
    proof, parse_failure = _coerce_mapping(raw_proof, "zero_data_proof")
    failures: list[str] = [parse_failure] if parse_failure else []
    if not proof:
        failures.append("zero_data_proof is missing")
        return {"ok": False, "failures": failures}

    proof_counts = proof.get("counts")
    if proof.get("explicit_zero_data") is not True and proof.get("mode") != "explicit_zero_data":
        failures.append("zero_data_proof must set explicit_zero_data=true or mode='explicit_zero_data'")
    if proof.get("site") != STAGING_SITE:
        failures.append(f"zero_data_proof site {proof.get('site')!r} does not match {STAGING_SITE!r}")
    if not isinstance(proof_counts, dict):
        failures.append("zero_data_proof counts must be an object")
        proof_counts = {}
    for doctype in ZERO_DATA_DOCTYPES:
        if _as_count(proof_counts.get(doctype), default=-1) != 0:
            failures.append(f"zero_data_proof {doctype} count is not zero")
        if _as_count(zero_data_counts.get(doctype), default=-1) != 0:
            failures.append(f"current hosted {doctype} count is not zero")
    proof_hash = hashlib.sha256(json.dumps(proof, sort_keys=True).encode("utf-8")).hexdigest()[:16]
    return {
        "ok": not failures,
        "backup_path": f"zero-data-proof:{proof_hash}",
        "zero_data_proof": proof,
        "failures": failures,
    }


def _coerce_mapping(value: Any, label: str) -> tuple[dict[str, Any], str | None]:
    if value is None or value == "":
        return {}, None
    if isinstance(value, dict):
        return value, None
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except ValueError as exc:
            return {}, f"{label} must be a JSON object when passed as a string: {exc}"
        if isinstance(parsed, dict):
            return parsed, None
    return {}, f"{label} must be an object"


def _looks_like_descriptive_backup_string(value: str) -> bool:
    lowered = " ".join(value.lower().split())
    descriptive_fragments = (
        "no customer data",
        "empty-site",
        "empty site",
        "owner-review bootstrap",
        "frappe cloud staging",
    )
    return any(fragment in lowered for fragment in descriptive_fragments)


def _as_count(value: Any, *, default: int) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _zero_data_counts() -> dict[str, int]:
    return {
        doctype: frappe.db.count(doctype)
        for doctype in ZERO_DATA_DOCTYPES
        if frappe.db.table_exists(doctype)
    }
