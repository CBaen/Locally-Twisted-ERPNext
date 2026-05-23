#!/usr/bin/env python3
"""Prepare a non-mutating LT staging reopen packet brief.

This helper writes a prep-only folder for the next release controller. It does
not create controller-consumable release artifacts and cannot authorize
forensic-freeze reopen, app mirror sync, Frappe Cloud deploy, staging
bootstrap, live release, DNS, Stripe, Search Console, indexing, or checkout.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from release_guard_common import (
    DEFAULT_LOCK_PATH,
    NEVER_REOPEN_WITH_STAGING_APPROVAL,
    PROJECT_ROOT,
    REOPENABLE_STAGING_ACTIONS,
    REQUIRED_APP_MIRROR_SOURCE_FILES,
    REQUIRED_HOSTED_PREFLIGHT_SITE,
    REQUIRED_READ_DOCS,
    REQUIRED_TRIAD_ARTIFACTS,
    ReleaseGuardError,
    current_git_head,
    is_full_hash,
    load_release_lock,
    normalize_hash,
    raise_if_failures,
    validate_release_lock,
)


MIRROR_URL = "https://github.com/CBaen/Locally-Twisted-Frappe-App.git"
MIRROR_REF = "main"
PREP_ALLOWLIST = {
    "README.md",
    "packet-prep-manifest.json",
    "missing-release-artifacts.md",
    "freeze-reopen-approval-preview.json",
}
RESERVED_FINAL_ARTIFACT_NAMES = {
    "freeze-reopen-approval.json",
    "provider-snapshot.json",
    "app-mirror-freshness.json",
    "app-mirror-sync-plan.json",
    "sanitized-payload.json",
    "deploy-completion.json",
    "hosted-bootstrap-preflight.json",
    "read-receipt.json",
    "failure-ledger.json",
    "staging-owner-review-gate.json",
    *REQUIRED_TRIAD_ARTIFACTS.values(),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--lock-file", type=Path, default=DEFAULT_LOCK_PATH)
    parser.add_argument("--output", type=Path, help="Prep directory to create. Defaults to a current-head prep folder.")
    parser.add_argument("--rollback-hash", help="Optional current deployed/staging rollback hash to carry as prep context only.")
    parser.add_argument("--agent", default="Codex", help="Agent/session name for the prep manifest.")
    parser.add_argument("--reviewed-source", action="store_true", help="Required. Confirms the current source HEAD was reviewed for prep context.")
    parser.add_argument("--force", action="store_true", help="Allow overwriting this helper's prep-only allowlist files.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        result = run(args)
    except ReleaseGuardError as exc:
        result = {"artifact_status": "blocked", "failure": str(exc), "provider_mutation_executed": False}
    except Exception as exc:  # pragma: no cover - defensive CLI surface.
        result = {"artifact_status": "blocked", "failure": f"{type(exc).__name__}: {exc}", "provider_mutation_executed": False}

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        passed = result.get("artifact_status") == "prep_only"
        print("[STAGING REOPEN PACKET PREPARE] " + ("PASS" if passed else "BLOCK"))
        if result.get("output"):
            print(f"  output: {result['output']}")
        if result.get("failure"):
            print(f"  failure: {result['failure']}")
    return 0 if result.get("artifact_status") == "prep_only" else 1


def run(args: argparse.Namespace) -> dict[str, Any]:
    if not args.reviewed_source:
        raise ReleaseGuardError("--reviewed-source is required before preparing staging reopen context")

    lock = load_release_lock(args.lock_file)
    raise_if_failures("invalid release lock", validate_release_lock(lock))

    source_commit = current_git_head()
    rollback_hash = normalize_optional_hash(args.rollback_hash)
    output = args.output or default_output_dir(source_commit)
    output = output if output.is_absolute() else PROJECT_ROOT / output
    prepare_output_dir(output, force=args.force)

    manifest = build_manifest(args.agent, lock, source_commit, rollback_hash)
    preview = build_approval_preview(lock, source_commit)

    write_text(output / "README.md", build_readme(source_commit, rollback_hash))
    write_json(output / "packet-prep-manifest.json", manifest)
    write_text(output / "missing-release-artifacts.md", build_missing_artifacts_note())
    write_json(output / "freeze-reopen-approval-preview.json", preview)
    verify_allowlist(output)

    return {
        "artifact_type": "staging_reopen_packet_prep",
        "artifact_status": "prep_only",
        "output": str(output),
        "source_commit": source_commit,
        "controller_consumable": False,
        "mutation_capable": False,
        "provider_mutation_executed": False,
        "approval_present": False,
        "provider_snapshot_present": False,
        "app_mirror_sync_executed": False,
        "deploy_completion_present": False,
        "hosted_preflight_present": False,
        "owner_review_ready": False,
        "triad_complete": False,
        "live_dns_stripe_search_console_blocked": True,
        "generated_files": sorted(PREP_ALLOWLIST),
    }


def normalize_optional_hash(value: str | None) -> str | None:
    if value is None or not str(value).strip():
        return None
    normalized = normalize_hash(value)
    if not is_full_hash(normalized):
        raise ReleaseGuardError("rollback hash must be a full 40-character hex hash when supplied")
    return normalized


def default_output_dir(source_commit: str) -> Path:
    stamp = datetime.now().date().isoformat()
    return PROJECT_ROOT / "workstreams" / "release-artifacts" / f"{stamp}-staging-reopen-{source_commit[:7]}-prep"


def prepare_output_dir(output: Path, *, force: bool) -> None:
    if output.exists() and not output.is_dir():
        raise ReleaseGuardError(f"output exists and is not a directory: {output}")
    if output.exists():
        reserved = sorted(name for name in RESERVED_FINAL_ARTIFACT_NAMES if (output / name).exists())
        if reserved:
            raise ReleaseGuardError("refusing to prepare inside a directory containing final release artifact names: " + ", ".join(reserved))
        existing = {path.name for path in output.iterdir()}
        unexpected = sorted(existing - PREP_ALLOWLIST)
        if unexpected:
            raise ReleaseGuardError("output directory contains files outside the prep allowlist: " + ", ".join(unexpected))
        if existing and not force:
            raise ReleaseGuardError(f"output directory is not empty; rerun with --force only for prep allowlist files: {output}")
    output.mkdir(parents=True, exist_ok=True)


def build_manifest(agent: str, lock: dict[str, Any], source_commit: str, rollback_hash: str | None) -> dict[str, Any]:
    return {
        "artifact_type": "staging_reopen_packet_prep",
        "artifact_status": "prep_only",
        "agent": agent,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_commit": source_commit,
        "target_site": REQUIRED_HOSTED_PREFLIGHT_SITE,
        "lock_id": lock.get("id"),
        "lock_status": lock.get("status"),
        "lock_stage": lock.get("stage"),
        "controller_consumable": False,
        "mutation_capable": False,
        "provider_mutation_executed": False,
        "approval_present": False,
        "provider_snapshot_present": False,
        "app_mirror_sync_executed": False,
        "deploy_completion_present": False,
        "hosted_preflight_present": False,
        "owner_review_ready": False,
        "triad_complete": False,
        "live_dns_stripe_search_console_blocked": True,
        "read_documents_required": list(lock.get("required_read_docs") or REQUIRED_READ_DOCS),
        "reopenable_staging_actions": sorted(REOPENABLE_STAGING_ACTIONS),
        "never_reopen_with_staging_approval": sorted(NEVER_REOPEN_WITH_STAGING_APPROVAL),
        "draft_app_mirror_sync_plan_context": {
            "source_commit": source_commit,
            "mirror_url": MIRROR_URL,
            "mirror_ref": MIRROR_REF,
            "target_site": REQUIRED_HOSTED_PREFLIGHT_SITE,
            "rollback_hash": rollback_hash,
            "reviewed_source": True,
            "required_files": [
                "locally_twisted/staging_owner_review_preflight.py",
                "locally_twisted/staging_owner_review_bootstrap.py",
                *sorted(
                    REQUIRED_APP_MIRROR_SOURCE_FILES
                    - {
                        "locally_twisted/staging_owner_review_preflight.py",
                        "locally_twisted/staging_owner_review_bootstrap.py",
                    }
                ),
            ],
            "post_sync_required": ["app-mirror-freshness.json"],
            "no_provider_deploy_until_post_sync_freshness": True,
            "provider_mutation_executed": False,
            "controller_consumable": False,
        },
        "missing_final_artifacts": sorted(RESERVED_FINAL_ARTIFACT_NAMES),
    }


def build_approval_preview(lock: dict[str, Any], source_commit: str) -> dict[str, Any]:
    approved_at = datetime.now(timezone.utc)
    return {
        "ok": False,
        "preview_only": True,
        "approval_type": "forensic_freeze_reopen",
        "lock_id": lock.get("id"),
        "approved_by": "<explicit approver required>",
        "approval_evidence": "<fresh explicit approval evidence required>",
        "approved_at": approved_at.isoformat(),
        "expires_at": (approved_at + timedelta(hours=12)).isoformat(),
        "target_site": REQUIRED_HOSTED_PREFLIGHT_SITE,
        "source_commit": source_commit,
        "approved_actions": [
            "app_mirror_sync",
            "frappe_cloud_deploy",
            "provider_poll",
            "staging_bootstrap",
            "site_migrate",
            "cache_clear",
        ],
        "live_dns_stripe_search_console_blocked": True,
        "provider_mutation_executed": False,
    }


def verify_allowlist(output: Path) -> None:
    existing = {path.name for path in output.iterdir()}
    missing = sorted(PREP_ALLOWLIST - existing)
    extra = sorted(existing - PREP_ALLOWLIST)
    reserved = sorted(name for name in RESERVED_FINAL_ARTIFACT_NAMES if (output / name).exists())
    failures: list[str] = []
    if missing:
        failures.append(f"prep output missing files: {missing}")
    if extra:
        failures.append(f"prep output contains non-allowlist files: {extra}")
    if reserved:
        failures.append(f"prep output contains reserved final release artifact names: {reserved}")
    raise_if_failures("invalid prep output", failures)


def build_readme(source_commit: str, rollback_hash: str | None) -> str:
    rollback_line = f"Rollback hash context: `{rollback_hash}`" if rollback_hash else "Rollback hash context: not supplied; must come from a fresh provider snapshot before mutation."
    return "\n".join(
        [
            "# LT Staging Reopen Prep",
            "",
            "Status: **prep-only; not controller-consumable; not mutation-capable**.",
            "",
            f"Source commit: `{source_commit}`",
            rollback_line,
            "",
            "This folder reduces post-approval setup ambiguity. It does not",
            "authorize app mirror sync, Frappe Cloud deploy/update, staging",
            "bootstrap/import, migrate, cache clear, live release, DNS, Stripe,",
            "Search Console, indexing, checkout, or provider mutation.",
            "",
            "Only prep files belong here:",
            "",
            "- `README.md`",
            "- `packet-prep-manifest.json`",
            "- `missing-release-artifacts.md`",
            "- `freeze-reopen-approval-preview.json`",
            "",
            "Do not rename prep files into final release artifacts. Generate the real",
            "artifacts only when their source proof exists and the active release",
            "controller requires them.",
            "",
        ]
    )


def build_missing_artifacts_note() -> str:
    lines = [
        "# Missing Final Release Artifacts",
        "",
        "This prep folder is intentionally missing every controller-consumable",
        "artifact required for mutation.",
        "",
    ]
    for name in sorted(RESERVED_FINAL_ARTIFACT_NAMES):
        lines.append(f"- `{name}`")
    lines.extend(
        [
            "",
            "These files must be generated from fresh proof in the real release",
            "packet. This prep folder is not staging proof.",
            "",
        ]
    )
    return "\n".join(lines)


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
