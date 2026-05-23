#!/usr/bin/env python3
"""Shared local release guard helpers for Locally Twisted.

These helpers are deliberately offline. They read repo files and local
artifacts; they do not contact Frappe Cloud, DNS, Stripe, Search Console, or
any production service.
"""
from __future__ import annotations

import json
import subprocess
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LOCK_PATH = PROJECT_ROOT / "release_locks" / "locally-twisted-staging-forensic-freeze.json"

REQUIRED_BLOCKED_ACTIONS = {
    "frappe_cloud_deploy",
    "app_mirror_sync",
    "provider_poll",
    "staging_bootstrap",
    "site_migrate",
    "cache_clear",
    "dns",
    "stripe",
    "search_console",
    "live_release",
    "production_indexing",
    "checkout_unpause",
}

REQUIRED_ALLOWED_ACTIONS = {
    "read_only_forensics",
    "local_guard_implementation",
    "docs_update",
    "release_guard_contract_verification",
}

REQUIRED_READ_DOCS = [
    "CODING-HANDOFF.md",
    "ECOMMERCE-SHOP-HANDOFF.md",
    "LT-LAUNCH-RUNBOOK.md",
    "workstreams/frappe-cloud-release-prevention-action-items-2026-05-23.md",
    "workstreams/frappe-cloud-staging-release-failure-forensics-2026-05-23.md",
    "workstreams/frappe-cloud-staging-owner-review-2026-05-22.md",
    "workstreams/release-artifacts/README.md",
    "workstreams/frappe-cloud-release-artifact-chain-binding-2026-05-23.md",
    "workstreams/frappe-cloud-freeze-approval-timestamp-guard-2026-05-23.md",
    "workstreams/frappe-cloud-freeze-reopen-approval-helper-2026-05-23.md",
    "scripts/README.md",
    "capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md",
    "locally-twisted-queue.md",
]

REQUIRED_PROVIDER_SNAPSHOT_FIELDS = {
    "team",
    "site",
    "bench_group",
    "bench",
    "installed_app_hash",
    "target_app_hash",
    "release_id",
    "running_jobs",
    "app_order",
    "site_status",
    "rollback_hash",
    "staging_live_separation",
}

REQUIRED_APP_MIRROR_FRESHNESS_FIELDS = {
    "ok",
    "source_commit",
    "mirror_hash",
    "required_files",
    "provider_mutation_executed",
}

REQUIRED_APP_MIRROR_SOURCE_FILES = {
    "locally_twisted/staging_owner_review_preflight.py",
    "locally_twisted/staging_owner_review_bootstrap.py",
}

REQUIRED_HOSTED_PREFLIGHT_FIELDS = {
    "ok",
    "site",
    "method",
    "expected_app_hash",
    "preflight",
    "provider_mutation_executed",
}

REQUIRED_HOSTED_PREFLIGHT_METHOD = (
    "locally_twisted.staging_owner_review_bootstrap."
    "preflight_staging_owner_review_bootstrap"
)
REQUIRED_HOSTED_PREFLIGHT_SITE = "locallytwisted-staging.frappe.cloud"
REQUIRED_HOSTED_PREFLIGHT_CHECKS = {
    "standard_report",
    "roles",
    "settings",
    "app_hooks",
    "app_order",
    "target_hash",
    "baseline_counts",
    "destructive_seed_evidence",
}

EXPECTED_APP_ORDER = ["frappe", "erpnext", "payments", "webshop", "locally_twisted"]

REOPENABLE_STAGING_ACTIONS = {
    "app_mirror_sync",
    "frappe_cloud_deploy",
    "provider_poll",
    "staging_bootstrap",
    "site_migrate",
    "cache_clear",
}

NEVER_REOPEN_WITH_STAGING_APPROVAL = {
    "dns",
    "stripe",
    "search_console",
    "live_release",
    "production_indexing",
    "checkout_unpause",
}

MAX_REOPEN_APPROVAL_DURATION = timedelta(hours=24)
MAX_REOPEN_APPROVAL_FUTURE_SKEW = timedelta(minutes=10)

REQUIRED_REOPEN_APPROVAL_FIELDS = {
    "ok",
    "approval_type",
    "lock_id",
    "approved_by",
    "approval_evidence",
    "approved_at",
    "expires_at",
    "target_site",
    "source_commit",
    "approved_actions",
    "live_dns_stripe_search_console_blocked",
    "provider_mutation_executed",
}

REQUIRED_APP_MIRROR_SYNC_PLAN_FIELDS = {
    "ok",
    "source_commit",
    "mirror_url",
    "mirror_ref",
    "target_site",
    "rollback_hash",
    "required_files",
    "post_sync_required",
    "no_provider_deploy_until_post_sync_freshness",
    "reviewed_source",
    "provider_mutation_executed",
}

REQUIRED_TRIAD_ARTIFACTS = {
    "controller": "controller.md",
    "provider_witness": "provider-witness.md",
    "gate_fixer": "gate-fixer.md",
    "recorder": "recorder.md",
}


class ReleaseGuardError(RuntimeError):
    """Raised when a local release guard blocks the requested action."""


def repo_path(rel_path: str) -> Path:
    return PROJECT_ROOT.joinpath(*str(rel_path).replace("\\", "/").split("/"))


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ReleaseGuardError(f"required artifact is missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ReleaseGuardError(f"{path} is not valid JSON: {exc}") from exc


def current_git_head() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=PROJECT_ROOT,
            text=True,
            capture_output=True,
            timeout=10,
            check=True,
        )
    except Exception as exc:
        raise ReleaseGuardError(f"could not resolve current repository HEAD: {exc}") from exc
    head = normalize_hash(result.stdout)
    if not is_full_hash(head):
        raise ReleaseGuardError(f"current repository HEAD is not a full commit hash: {head!r}")
    return head


def load_release_lock(path: Path = DEFAULT_LOCK_PATH) -> dict[str, Any]:
    data = read_json(path)
    if not isinstance(data, dict):
        raise ReleaseGuardError(f"release lock must be a JSON object: {path}")
    return data


def normalize_hash(value: Any) -> str:
    return str(value or "").strip().lower()


def is_full_hash(value: str) -> bool:
    return len(value) == 40 and all(char in "0123456789abcdef" for char in value)


def validate_release_lock(lock: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if lock.get("status") != "active":
        failures.append("release lock status must be active")
    if lock.get("stage") != "forensic-freeze":
        failures.append("release lock stage must be forensic-freeze")

    blocked = set(lock.get("blocked_actions") or [])
    missing_blocked = sorted(REQUIRED_BLOCKED_ACTIONS - blocked)
    if missing_blocked:
        failures.append(f"release lock is missing blocked actions: {missing_blocked}")

    allowed = set(lock.get("allowed_actions") or [])
    missing_allowed = sorted(REQUIRED_ALLOWED_ACTIONS - allowed)
    if missing_allowed:
        failures.append(f"release lock is missing allowed forensic actions: {missing_allowed}")

    required_docs = list(lock.get("required_read_docs") or [])
    missing_docs = sorted(set(REQUIRED_READ_DOCS) - set(required_docs))
    if missing_docs:
        failures.append(f"release lock required_read_docs is missing: {missing_docs}")

    for field in ("source_incident", "action_list"):
        rel_path = lock.get(field)
        if not isinstance(rel_path, str) or not rel_path:
            failures.append(f"release lock is missing {field}")
        elif not repo_path(rel_path).exists():
            failures.append(f"release lock {field} does not exist: {rel_path}")

    for rel_path in required_docs:
        if not isinstance(rel_path, str):
            failures.append(f"release lock required_read_docs contains non-string value: {rel_path!r}")
        elif not repo_path(rel_path).exists():
            failures.append(f"required read doc does not exist: {rel_path}")

    roles = set(lock.get("required_artifact_roles") or [])
    missing_roles = sorted(set(REQUIRED_TRIAD_ARTIFACTS) - roles)
    if missing_roles:
        failures.append(f"release lock required_artifact_roles is missing: {missing_roles}")
    return failures


def ensure_action_allowed(
    action: str,
    lock: dict[str, Any],
    *,
    reopen_approved_actions: set[str] | None = None,
) -> None:
    if lock.get("status") != "active":
        return

    blocked = set(lock.get("blocked_actions") or [])
    allowed = set(lock.get("allowed_actions") or [])
    if reopen_approved_actions and action in reopen_approved_actions:
        return
    if action in blocked:
        raise ReleaseGuardError(
            f"release lock {lock.get('id')} is active; action {action!r} is blocked during forensic-freeze"
        )
    if action not in allowed:
        raise ReleaseGuardError(
            f"release lock {lock.get('id')} is active; action {action!r} is not listed as allowed"
        )


def action_is_mutating(action: str) -> bool:
    return action in REQUIRED_BLOCKED_ACTIONS


def validate_read_receipt(path: Path, required_docs: list[str] | None = None) -> list[str]:
    receipt = read_json(path)
    if not isinstance(receipt, dict):
        return [f"read receipt must be a JSON object: {path}"]

    docs = receipt.get("read_documents") or receipt.get("documents_read")
    if not isinstance(docs, list):
        return ["read receipt must include read_documents as a list"]

    normalized_docs = {str(doc).replace("\\", "/") for doc in docs}
    required = {doc.replace("\\", "/") for doc in (required_docs or REQUIRED_READ_DOCS)}
    missing = sorted(required - normalized_docs)
    failures: list[str] = []
    if missing:
        failures.append(f"read receipt is missing required docs: {missing}")
    if not receipt.get("created_at"):
        failures.append("read receipt is missing created_at")
    if not receipt.get("agent"):
        failures.append("read receipt is missing agent")
    return failures


def validate_provider_snapshot(path: Path) -> list[str]:
    snapshot = read_json(path)
    if not isinstance(snapshot, dict):
        return [f"provider snapshot must be a JSON object: {path}"]

    missing = sorted(field for field in REQUIRED_PROVIDER_SNAPSHOT_FIELDS if field not in snapshot)
    failures = [f"provider snapshot is missing required fields: {missing}"] if missing else []
    if snapshot.get("staging_live_separation") is not True:
        failures.append("provider snapshot must explicitly prove staging_live_separation=true")
    if snapshot.get("site_status") != "Active":
        failures.append("provider snapshot site_status must be Active before mutation")
    if snapshot.get("running_jobs") not in ([], ()):
        failures.append("provider snapshot running_jobs must be empty before mutation")
    if snapshot.get("app_order") != EXPECTED_APP_ORDER:
        failures.append(f"provider snapshot app_order must be {EXPECTED_APP_ORDER}")
    for hash_field in ("installed_app_hash", "target_app_hash", "rollback_hash"):
        value = str(snapshot.get(hash_field) or "")
        if len(value) != 40 or any(char not in "0123456789abcdef" for char in value.lower()):
            failures.append(f"provider snapshot {hash_field} must be a full 40-character hex hash")
    return failures


def validate_app_mirror_freshness(path: Path) -> list[str]:
    artifact = read_json(path)
    if not isinstance(artifact, dict):
        return [f"app mirror freshness artifact must be a JSON object: {path}"]

    missing = sorted(field for field in REQUIRED_APP_MIRROR_FRESHNESS_FIELDS if field not in artifact)
    failures = [f"app mirror freshness artifact is missing required fields: {missing}"] if missing else []
    if artifact.get("ok") is not True:
        failures.append("app mirror freshness artifact must have ok=true before mutation")
    if artifact.get("provider_mutation_executed") is not False:
        failures.append("app mirror freshness artifact must prove provider_mutation_executed=false")
    for hash_field in ("source_commit", "mirror_hash"):
        value = str(artifact.get(hash_field) or "")
        if len(value) != 40 or any(char not in "0123456789abcdef" for char in value.lower()):
            failures.append(f"app mirror freshness {hash_field} must be a full 40-character hex hash")

    rows = artifact.get("required_files")
    if not isinstance(rows, list) or not rows:
        failures.append("app mirror freshness required_files must be a non-empty list")
        return failures
    seen_paths: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            failures.append(f"app mirror freshness required_files[{index}] is not an object")
            continue
        path_value = row.get("path")
        if not isinstance(path_value, str) or not path_value:
            failures.append(f"app mirror freshness required_files[{index}] is missing path")
        else:
            normalized_path = path_value.replace("\\", "/")
            if normalized_path in seen_paths:
                failures.append(f"app mirror freshness has duplicate required file row: {normalized_path}")
            seen_paths.add(normalized_path)
        if row.get("source_exists") is not True:
            failures.append(f"app mirror freshness source file is missing: {path_value}")
        if row.get("mirror_exists") is not True:
            failures.append(f"app mirror freshness mirror file is missing: {path_value}")
        if row.get("matches") is not True:
            failures.append(f"app mirror freshness file does not match source: {path_value}")
    missing_source_files = sorted(REQUIRED_APP_MIRROR_SOURCE_FILES - seen_paths)
    if missing_source_files:
        failures.append(f"app mirror freshness is missing required source files: {missing_source_files}")
    return failures


def validate_reopen_approval(path: Path, lock: dict[str, Any], action: str | None = None) -> list[str]:
    approval = read_json(path)
    if not isinstance(approval, dict):
        return [f"freeze reopen approval must be a JSON object: {path}"]

    missing = sorted(field for field in REQUIRED_REOPEN_APPROVAL_FIELDS if field not in approval)
    failures = [f"freeze reopen approval is missing required fields: {missing}"] if missing else []
    if approval.get("ok") is not True:
        failures.append("freeze reopen approval must have ok=true")
    if approval.get("approval_type") != "forensic_freeze_reopen":
        failures.append("freeze reopen approval approval_type must be forensic_freeze_reopen")
    if approval.get("lock_id") != lock.get("id"):
        failures.append("freeze reopen approval lock_id must match active release lock")
    if approval.get("target_site") != REQUIRED_HOSTED_PREFLIGHT_SITE:
        failures.append(f"freeze reopen approval target_site must be {REQUIRED_HOSTED_PREFLIGHT_SITE}")
    if approval.get("provider_mutation_executed") is not False:
        failures.append("freeze reopen approval must prove provider_mutation_executed=false")
    if approval.get("live_dns_stripe_search_console_blocked") is not True:
        failures.append("freeze reopen approval must keep live/DNS/Stripe/Search Console blocked")

    source_commit = str(approval.get("source_commit") or "")
    if len(source_commit) != 40 or any(char not in "0123456789abcdef" for char in source_commit.lower()):
        failures.append("freeze reopen approval source_commit must be a full 40-character hex hash")

    approved_at = parse_release_timestamp(approval.get("approved_at"), "approved_at", failures)
    expires_at = parse_release_timestamp(approval.get("expires_at"), "expires_at", failures)
    if approved_at and expires_at:
        now = datetime.now(timezone.utc)
        if approved_at > now + MAX_REOPEN_APPROVAL_FUTURE_SKEW:
            failures.append("freeze reopen approval approved_at cannot be in the future")
        if expires_at <= now:
            failures.append("freeze reopen approval is expired")
        if expires_at <= approved_at:
            failures.append("freeze reopen approval expires_at must be after approved_at")
        if expires_at - approved_at > MAX_REOPEN_APPROVAL_DURATION:
            failures.append("freeze reopen approval duration must be 24 hours or less")

    approved_by = str(approval.get("approved_by") or "").strip()
    if not approved_by:
        failures.append("freeze reopen approval approved_by must be non-empty")

    approval_evidence = str(approval.get("approval_evidence") or "").strip()
    if not approval_evidence:
        failures.append("freeze reopen approval approval_evidence must be non-empty")

    approved_actions_raw = approval.get("approved_actions")
    if not isinstance(approved_actions_raw, list) or not approved_actions_raw:
        failures.append("freeze reopen approval approved_actions must be a non-empty list")
        approved_actions: set[str] = set()
    else:
        approved_actions = {str(item) for item in approved_actions_raw}
        forbidden = sorted(approved_actions & NEVER_REOPEN_WITH_STAGING_APPROVAL)
        if forbidden:
            failures.append(f"freeze reopen approval may not include live/search/payment actions: {forbidden}")
        unknown = sorted(approved_actions - REOPENABLE_STAGING_ACTIONS)
        if unknown:
            failures.append(f"freeze reopen approval contains unsupported actions: {unknown}")
    if action and action not in approved_actions:
        failures.append(f"freeze reopen approval does not approve requested action: {action}")
    return failures


def parse_release_timestamp(value: Any, field_name: str, failures: list[str]) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        failures.append(f"freeze reopen approval {field_name} must be a non-empty timestamp string")
        return None
    raw = value.strip()
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        failures.append(f"freeze reopen approval {field_name} must be ISO-8601 parseable")
        return None
    if parsed.tzinfo is None:
        failures.append(f"freeze reopen approval {field_name} must include a timezone offset")
        return None
    return parsed.astimezone(timezone.utc)


def validate_release_artifact_chain(
    *,
    action: str,
    payload_file: Path | None = None,
    reopen_approval_path: Path | None = None,
    app_mirror_sync_plan_path: Path | None = None,
    app_mirror_freshness_path: Path | None = None,
    provider_snapshot_path: Path | None = None,
    deploy_completion_path: Path | None = None,
    hosted_bootstrap_preflight_path: Path | None = None,
    source_commit: str | None = None,
) -> list[str]:
    """Validate cross-artifact binding for a mutation-capable release packet.

    Shape validators prove each artifact can stand alone. This chain validator
    proves the packet is one coherent release attempt, so stale approval,
    payload, mirror, provider, and deploy/preflight evidence cannot be mixed.
    """
    failures: list[str] = []
    current_source_commit = normalize_hash(source_commit) if source_commit else current_git_head()

    approval = read_json(reopen_approval_path) if reopen_approval_path else None
    sync_plan = read_json(app_mirror_sync_plan_path) if app_mirror_sync_plan_path else None
    mirror = read_json(app_mirror_freshness_path) if app_mirror_freshness_path else None
    provider = read_json(provider_snapshot_path) if provider_snapshot_path else None
    deploy_completion = read_json(deploy_completion_path) if deploy_completion_path else None
    hosted_preflight = read_json(hosted_bootstrap_preflight_path) if hosted_bootstrap_preflight_path else None
    payload = read_json(payload_file) if payload_file else None

    if approval:
        failures.extend(
            require_hash_match(
                "freeze reopen approval source_commit",
                approval.get("source_commit"),
                "current repository HEAD",
                current_source_commit,
            )
        )

    if sync_plan:
        failures.extend(
            require_hash_match(
                "app mirror sync plan source_commit",
                sync_plan.get("source_commit"),
                "current repository HEAD",
                current_source_commit,
            )
        )
        if approval:
            failures.extend(
                require_hash_match(
                    "app mirror sync plan source_commit",
                    sync_plan.get("source_commit"),
                    "freeze reopen approval source_commit",
                    approval.get("source_commit"),
                )
            )
        if provider:
            failures.extend(
                require_hash_match(
                    "app mirror sync plan rollback_hash",
                    sync_plan.get("rollback_hash"),
                    "provider snapshot rollback_hash",
                    provider.get("rollback_hash"),
                )
            )

    if mirror:
        failures.extend(
            require_hash_match(
                "app mirror freshness source_commit",
                mirror.get("source_commit"),
                "current repository HEAD",
                current_source_commit,
            )
        )
        if approval:
            failures.extend(
                require_hash_match(
                    "app mirror freshness source_commit",
                    mirror.get("source_commit"),
                    "freeze reopen approval source_commit",
                    approval.get("source_commit"),
                )
            )
        if sync_plan:
            failures.extend(
                require_hash_match(
                    "app mirror freshness source_commit",
                    mirror.get("source_commit"),
                    "app mirror sync plan source_commit",
                    sync_plan.get("source_commit"),
                )
            )
        if provider and action != "app_mirror_sync":
            failures.extend(
                require_hash_match(
                    "provider snapshot target_app_hash",
                    provider.get("target_app_hash"),
                    "app mirror freshness mirror_hash",
                    mirror.get("mirror_hash"),
                )
            )

    if payload:
        body = release_payload_body(payload)
        app_hash = release_payload_app_hash(body, "locally_twisted")
        if not app_hash:
            failures.append("sanitized payload must include locally_twisted app hash for release chain binding")
        elif mirror:
            failures.extend(
                require_hash_match(
                    "payload locally_twisted app hash",
                    app_hash,
                    "app mirror freshness mirror_hash",
                    mirror.get("mirror_hash"),
                )
            )
        if provider and app_hash:
            failures.extend(
                require_hash_match(
                    "payload locally_twisted app hash",
                    app_hash,
                    "provider snapshot target_app_hash",
                    provider.get("target_app_hash"),
                )
            )
        payload_sites = release_payload_sites(body)
        if provider and provider.get("site") not in payload_sites:
            failures.append(
                "sanitized payload sites must include provider snapshot site "
                f"{provider.get('site')!r}; found {sorted(payload_sites)}"
            )

    if deploy_completion and provider:
        failures.extend(
            require_hash_match(
                "deploy completion expected_app_hash",
                deploy_completion.get("expected_app_hash"),
                "provider snapshot target_app_hash",
                provider.get("target_app_hash"),
            )
        )
    if deploy_completion and mirror:
        failures.extend(
            require_hash_match(
                "deploy completion expected_app_hash",
                deploy_completion.get("expected_app_hash"),
                "app mirror freshness mirror_hash",
                mirror.get("mirror_hash"),
            )
        )
    if hosted_preflight and deploy_completion:
        failures.extend(
            require_hash_match(
                "hosted bootstrap preflight expected_app_hash",
                hosted_preflight.get("expected_app_hash"),
                "deploy completion expected_app_hash",
                deploy_completion.get("expected_app_hash"),
            )
        )
    return failures


def require_hash_match(label: str, value: Any, expected_label: str, expected: Any) -> list[str]:
    actual_hash = normalize_hash(value)
    expected_hash = normalize_hash(expected)
    if not is_full_hash(actual_hash) or not is_full_hash(expected_hash):
        return []
    if actual_hash != expected_hash:
        return [f"{label} must match {expected_label}: {actual_hash} != {expected_hash}"]
    return []


def release_payload_body(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return payload
    for wrapper_key in ("payload", "body", "data"):
        wrapped = payload.get(wrapper_key)
        if isinstance(wrapped, dict) and ("apps" in wrapped or "sites" in wrapped):
            return wrapped
    return payload


def release_payload_app_hash(body: Any, app_name: str) -> str:
    if not isinstance(body, dict):
        return ""
    apps = body.get("apps")
    if not isinstance(apps, list):
        return ""
    for row in apps:
        if isinstance(row, dict) and row.get("app") == app_name:
            return normalize_hash(row.get("hash"))
    return ""


def release_payload_sites(body: Any) -> set[str]:
    if not isinstance(body, dict):
        return set()
    sites = body.get("sites")
    if not isinstance(sites, list):
        return set()
    names: set[str] = set()
    for row in sites:
        if isinstance(row, dict) and row.get("name"):
            names.add(str(row["name"]))
    return names


def approved_actions_from_reopen_approval(path: Path) -> set[str]:
    approval = read_json(path)
    if not isinstance(approval, dict):
        return set()
    return {str(item) for item in approval.get("approved_actions") or []}


def validate_app_mirror_sync_plan(path: Path) -> list[str]:
    plan = read_json(path)
    if not isinstance(plan, dict):
        return [f"app mirror sync plan must be a JSON object: {path}"]

    missing = sorted(field for field in REQUIRED_APP_MIRROR_SYNC_PLAN_FIELDS if field not in plan)
    failures = [f"app mirror sync plan is missing required fields: {missing}"] if missing else []
    if plan.get("ok") is not True:
        failures.append("app mirror sync plan must have ok=true")
    if plan.get("provider_mutation_executed") is not False:
        failures.append("app mirror sync plan must prove provider_mutation_executed=false")
    if plan.get("reviewed_source") is not True:
        failures.append("app mirror sync plan must prove reviewed_source=true")
    if plan.get("target_site") != REQUIRED_HOSTED_PREFLIGHT_SITE:
        failures.append(f"app mirror sync plan target_site must be {REQUIRED_HOSTED_PREFLIGHT_SITE}")

    for hash_field in ("source_commit", "rollback_hash"):
        value = str(plan.get(hash_field) or "")
        if len(value) != 40 or any(char not in "0123456789abcdef" for char in value.lower()):
            failures.append(f"app mirror sync plan {hash_field} must be a full 40-character hex hash")

    if not isinstance(plan.get("mirror_url"), str) or "Locally-Twisted-Frappe-App" not in plan.get("mirror_url", ""):
        failures.append("app mirror sync plan mirror_url must point at the LT Frappe app mirror")
    if not isinstance(plan.get("mirror_ref"), str) or not plan.get("mirror_ref"):
        failures.append("app mirror sync plan mirror_ref must be non-empty")

    required_files_raw = plan.get("required_files")
    if not isinstance(required_files_raw, list) or not required_files_raw:
        failures.append("app mirror sync plan required_files must be a non-empty list")
        required_files: set[str] = set()
    else:
        required_files = {str(item).replace("\\", "/") for item in required_files_raw}
        missing_source_files = sorted(REQUIRED_APP_MIRROR_SOURCE_FILES - required_files)
        if missing_source_files:
            failures.append(f"app mirror sync plan is missing required source files: {missing_source_files}")

    post_sync_required = plan.get("post_sync_required")
    if not isinstance(post_sync_required, list):
        failures.append("app mirror sync plan post_sync_required must be a list")
    elif "app-mirror-freshness.json" not in {str(item) for item in post_sync_required}:
        failures.append("app mirror sync plan must require post-sync app-mirror-freshness.json")
    if plan.get("no_provider_deploy_until_post_sync_freshness") is not True:
        failures.append("app mirror sync plan must block provider deploy until post-sync freshness passes")
    return failures


def validate_hosted_bootstrap_preflight(
    path: Path,
    provider_snapshot_path: Path | None = None,
    app_mirror_freshness_path: Path | None = None,
) -> list[str]:
    artifact = read_json(path)
    if not isinstance(artifact, dict):
        return [f"hosted bootstrap preflight artifact must be a JSON object: {path}"]

    missing = sorted(field for field in REQUIRED_HOSTED_PREFLIGHT_FIELDS if field not in artifact)
    failures = [f"hosted bootstrap preflight artifact is missing required fields: {missing}"] if missing else []
    if artifact.get("ok") is not True:
        failures.append("hosted bootstrap preflight artifact must have ok=true before staging bootstrap")
    if artifact.get("provider_mutation_executed") is not False:
        failures.append("hosted bootstrap preflight artifact must prove provider_mutation_executed=false")
    if artifact.get("method") != REQUIRED_HOSTED_PREFLIGHT_METHOD:
        failures.append(f"hosted bootstrap preflight method must be {REQUIRED_HOSTED_PREFLIGHT_METHOD}")
    if artifact.get("site") != REQUIRED_HOSTED_PREFLIGHT_SITE:
        failures.append(f"hosted bootstrap preflight site must be {REQUIRED_HOSTED_PREFLIGHT_SITE}")
    if "body_excerpt" in artifact:
        failures.append("hosted bootstrap preflight artifact must not contain raw body_excerpt")
    expected_hash = str(artifact.get("expected_app_hash") or "")
    if len(expected_hash) != 40 or any(char not in "0123456789abcdef" for char in expected_hash.lower()):
        failures.append("hosted bootstrap preflight expected_app_hash must be a full 40-character hex hash")

    if provider_snapshot_path:
        snapshot = read_json(provider_snapshot_path)
        if not isinstance(snapshot, dict):
            failures.append(f"provider snapshot must be a JSON object: {provider_snapshot_path}")
        else:
            if artifact.get("site") != snapshot.get("site"):
                failures.append(
                    "hosted bootstrap preflight site must match provider snapshot site "
                    f"({artifact.get('site')!r} != {snapshot.get('site')!r})"
                )
            for snapshot_hash_field in ("target_app_hash", "installed_app_hash"):
                if expected_hash and expected_hash.lower() != str(snapshot.get(snapshot_hash_field) or "").lower():
                    failures.append(
                        "hosted bootstrap preflight expected_app_hash must match provider snapshot "
                        f"{snapshot_hash_field}"
                    )

    if app_mirror_freshness_path:
        mirror = read_json(app_mirror_freshness_path)
        if not isinstance(mirror, dict):
            failures.append(f"app mirror freshness artifact must be a JSON object: {app_mirror_freshness_path}")
        elif expected_hash and expected_hash.lower() != str(mirror.get("mirror_hash") or "").lower():
            failures.append("hosted bootstrap preflight expected_app_hash must match app mirror freshness mirror_hash")

    preflight = artifact.get("preflight")
    if not isinstance(preflight, dict):
        failures.append("hosted bootstrap preflight preflight must be an object")
        return failures
    if preflight.get("ok") is not True:
        failures.append("hosted bootstrap preflight payload must have preflight.ok=true")
    if preflight.get("failures") not in ([], ()):
        failures.append(f"hosted bootstrap preflight payload has failures: {preflight.get('failures')}")
    if preflight.get("target_site") != artifact.get("site"):
        failures.append("hosted bootstrap preflight payload target_site must match artifact site")
    if str(preflight.get("expected_app_hash") or "").lower() != expected_hash.lower():
        failures.append("hosted bootstrap preflight payload expected_app_hash must match artifact expected_app_hash")
    required_checks = preflight.get("required_checks")
    if not isinstance(required_checks, list):
        failures.append("hosted bootstrap preflight payload must include required_checks list")
    else:
        missing_checks = sorted(REQUIRED_HOSTED_PREFLIGHT_CHECKS - {str(item) for item in required_checks})
        if missing_checks:
            failures.append(f"hosted bootstrap preflight payload is missing required_checks: {missing_checks}")
    checks = preflight.get("checks")
    if not isinstance(checks, dict):
        failures.append("hosted bootstrap preflight payload must include checks object")
    else:
        for check_name in sorted(REQUIRED_HOSTED_PREFLIGHT_CHECKS):
            check = checks.get(check_name)
            if not isinstance(check, dict):
                failures.append(f"hosted bootstrap preflight checks.{check_name} must be an object")
                continue
            if check.get("ok") is not True:
                failures.append(f"hosted bootstrap preflight checks.{check_name}.ok must be true")
        target_hash_check = checks.get("target_hash") if isinstance(checks.get("target_hash"), dict) else {}
        if str(target_hash_check.get("expected_app_hash") or "").lower() != expected_hash.lower():
            failures.append("hosted bootstrap preflight target_hash.expected_app_hash must match artifact expected_app_hash")
        if str(target_hash_check.get("current_app_hash") or "").lower() != expected_hash.lower():
            failures.append("hosted bootstrap preflight target_hash.current_app_hash must match artifact expected_app_hash")
    return failures


def validate_triad_artifacts(directory: Path) -> list[str]:
    failures: list[str] = []
    if not directory.exists() or not directory.is_dir():
        return [f"triad artifact directory is missing: {directory}"]

    for role, filename in REQUIRED_TRIAD_ARTIFACTS.items():
        artifact = directory / filename
        if not artifact.exists():
            failures.append(f"triad role {role} is missing artifact {filename}")
            continue
        content = artifact.read_text(encoding="utf-8").strip()
        lower = content.lower()
        if not content:
            failures.append(f"triad role {role} artifact is empty: {filename}")
            continue
        if "target:" not in lower:
            failures.append(f"triad role {role} artifact must include target: {filename}")
        if "evidence:" not in lower:
            failures.append(f"triad role {role} artifact must include evidence: {filename}")
        if not any(marker in lower for marker in ("pass", "block", "no-go", "no go")):
            failures.append(f"triad role {role} artifact must include pass/block/no-go state: {filename}")
    return failures


def validate_failure_ledger(path: Path) -> list[str]:
    ledger = read_json(path)
    if isinstance(ledger, list):
        failures_data = ledger
        fresh_plan_approved = False
    elif isinstance(ledger, dict):
        failures_data = ledger.get("failures") or []
        fresh_plan_approved = bool(ledger.get("fresh_release_plan_approved"))
    else:
        return [f"failure ledger must be a JSON object or list: {path}"]

    if not isinstance(failures_data, list):
        return ["failure ledger failures must be a list"]

    classes: list[str] = []
    failures: list[str] = []
    for index, entry in enumerate(failures_data):
        if not isinstance(entry, dict):
            failures.append(f"failure ledger entry {index} is not an object")
            continue
        failure_class = entry.get("class") or entry.get("failure_class")
        if not failure_class:
            failures.append(f"failure ledger entry {index} is missing class")
            continue
        classes.append(str(failure_class))
        if not entry.get("guard_written"):
            failures.append(f"failure class {failure_class!r} has no guard_written=true")

    repeated = sorted(name for name, count in Counter(classes).items() if count >= 2)
    if repeated and not fresh_plan_approved:
        failures.append(
            "repeated provider/bootstrap failure classes require fresh_release_plan_approved=true: "
            + ", ".join(repeated)
        )
    return failures


def raise_if_failures(prefix: str, failures: list[str]) -> None:
    if failures:
        raise ReleaseGuardError(prefix + ": " + "; ".join(failures))
