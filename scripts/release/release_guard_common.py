#!/usr/bin/env python3
"""Shared local release guard helpers for Locally Twisted.

These helpers are deliberately offline. They read repo files and local
artifacts; they do not contact Frappe Cloud, DNS, Stripe, Search Console, or
any production service.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LOCK_PATH = PROJECT_ROOT / "release_locks" / "locally-twisted-staging-forensic-freeze.json"

REQUIRED_BLOCKED_ACTIONS = {
    "frappe_cloud_deploy",
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
    "workstreams/frappe-cloud-release-prevention-action-items-2026-05-23.md",
    "workstreams/frappe-cloud-staging-release-failure-forensics-2026-05-23.md",
    "workstreams/frappe-cloud-staging-owner-review-2026-05-22.md",
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

EXPECTED_APP_ORDER = ["frappe", "erpnext", "payments", "webshop", "locally_twisted"]

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


def load_release_lock(path: Path = DEFAULT_LOCK_PATH) -> dict[str, Any]:
    data = read_json(path)
    if not isinstance(data, dict):
        raise ReleaseGuardError(f"release lock must be a JSON object: {path}")
    return data


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


def ensure_action_allowed(action: str, lock: dict[str, Any]) -> None:
    if lock.get("status") != "active":
        return

    blocked = set(lock.get("blocked_actions") or [])
    allowed = set(lock.get("allowed_actions") or [])
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
