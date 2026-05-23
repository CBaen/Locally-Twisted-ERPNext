#!/usr/bin/env python3
"""Draft, write, or validate a local forensic-freeze reopen approval artifact.

This helper does not contact Frappe Cloud and does not mutate staging. It only
builds or validates the `freeze-reopen-approval.json` file that the release
controller already requires before any future staging mutation.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from release_guard_common import (
    DEFAULT_LOCK_PATH,
    MAX_REOPEN_APPROVAL_DURATION,
    REQUIRED_HOSTED_PREFLIGHT_SITE,
    REOPENABLE_STAGING_ACTIONS,
    ReleaseGuardError,
    current_git_head,
    load_release_lock,
    raise_if_failures,
    validate_release_artifact_chain,
    validate_release_lock,
    validate_reopen_approval,
)

DEFAULT_ACTIONS = [
    "app_mirror_sync",
    "frappe_cloud_deploy",
    "provider_poll",
    "staging_bootstrap",
    "site_migrate",
    "cache_clear",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--lock-file", type=Path, default=DEFAULT_LOCK_PATH)
    parser.add_argument("--output", type=Path, help="Where to write freeze-reopen-approval.json when --write is used.")
    parser.add_argument("--write", action="store_true", help="Write a mutation-capable approval artifact after validation.")
    parser.add_argument("--force", action="store_true", help="Allow overwriting --output.")
    parser.add_argument("--approved-by", help="Required with --write. Human/business approver name.")
    parser.add_argument("--approval-evidence", help="Required with --write. Short source of the explicit approval.")
    parser.add_argument("--duration-hours", type=float, default=12.0, help="Approval window, max 24 hours.")
    parser.add_argument(
        "--action",
        dest="actions",
        action="append",
        help="Approved staging action. Can be repeated. Defaults to all staging-only reopen actions.",
    )
    parser.add_argument("--validate-only", type=Path, help="Validate an existing freeze-reopen-approval.json and exit.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable result.")
    args = parser.parse_args()

    try:
        result = run(args)
    except ReleaseGuardError as exc:
        result = {"ok": False, "failure": str(exc), "provider_mutation_executed": False}
    except Exception as exc:  # pragma: no cover - defensive CLI surface.
        result = {"ok": False, "failure": f"{type(exc).__name__}: {exc}", "provider_mutation_executed": False}

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        if result.get("ok"):
            print("[FREEZE REOPEN APPROVAL ARTIFACT] PASS")
            if result.get("output"):
                print(f"  output: {result['output']}")
        else:
            print("[FREEZE REOPEN APPROVAL ARTIFACT] BLOCK")
            print(f"  failure: {result.get('failure')}")
            if result.get("preview"):
                print(json.dumps(result["preview"], indent=2, sort_keys=True))
    return 0 if result.get("ok") else 1


def run(args: argparse.Namespace) -> dict[str, Any]:
    lock = load_release_lock(args.lock_file)
    raise_if_failures("invalid release lock", validate_release_lock(lock))
    actions = requested_actions(args.actions)

    if args.validate_only:
        return validate_existing(args.validate_only, lock, actions)

    if args.duration_hours <= 0 or timedelta(hours=args.duration_hours) > MAX_REOPEN_APPROVAL_DURATION:
        raise ReleaseGuardError("approval duration must be greater than 0 and no longer than 24 hours")

    if args.write:
        if not args.output:
            raise ReleaseGuardError("--write requires --output")
        if not args.approved_by or not args.approved_by.strip():
            raise ReleaseGuardError("--write requires --approved-by")
        if not args.approval_evidence or not args.approval_evidence.strip():
            raise ReleaseGuardError("--write requires --approval-evidence")
        if args.output.exists() and not args.force:
            raise ReleaseGuardError(f"refusing to overwrite existing approval artifact without --force: {args.output}")

        artifact = build_artifact(
            lock=lock,
            ok=True,
            approved_by=args.approved_by.strip(),
            approval_evidence=args.approval_evidence.strip(),
            actions=actions,
            duration_hours=args.duration_hours,
        )
        failures = validate_artifact_payload(artifact, lock, actions)
        raise_if_failures("generated freeze reopen approval is invalid", failures)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return {
            "ok": True,
            "output": str(args.output),
            "source_commit": artifact["source_commit"],
            "approved_actions": artifact["approved_actions"],
            "provider_mutation_executed": False,
        }

    preview = build_artifact(
        lock=lock,
        ok=False,
        approved_by=args.approved_by or "<explicit approver required>",
        approval_evidence=args.approval_evidence or "<explicit approval evidence required>",
        actions=actions,
        duration_hours=args.duration_hours,
    )
    preview["preview_only"] = True
    return {
        "ok": False,
        "failure": "preview only; rerun with --write, --output, --approved-by, and --approval-evidence after explicit approval",
        "preview": preview,
        "provider_mutation_executed": False,
    }


def requested_actions(raw_actions: list[str] | None) -> list[str]:
    actions = raw_actions or DEFAULT_ACTIONS
    normalized = []
    seen: set[str] = set()
    for action in actions:
        action = str(action).strip()
        if not action:
            continue
        if action in seen:
            continue
        if action not in REOPENABLE_STAGING_ACTIONS:
            raise ReleaseGuardError(f"unsupported or non-staging reopen action: {action}")
        normalized.append(action)
        seen.add(action)
    if not normalized:
        raise ReleaseGuardError("at least one staging action is required")
    return normalized


def build_artifact(
    *,
    lock: dict[str, Any],
    ok: bool,
    approved_by: str,
    approval_evidence: str,
    actions: list[str],
    duration_hours: float,
) -> dict[str, Any]:
    approved_at = datetime.now(timezone.utc)
    expires_at = approved_at + timedelta(hours=duration_hours)
    return {
        "ok": ok,
        "approval_type": "forensic_freeze_reopen",
        "lock_id": lock.get("id"),
        "approved_by": approved_by,
        "approval_evidence": approval_evidence,
        "approved_at": approved_at.isoformat(),
        "expires_at": expires_at.isoformat(),
        "target_site": REQUIRED_HOSTED_PREFLIGHT_SITE,
        "source_commit": current_git_head(),
        "approved_actions": actions,
        "live_dns_stripe_search_console_blocked": True,
        "provider_mutation_executed": False,
    }


def validate_existing(path: Path, lock: dict[str, Any], actions: list[str]) -> dict[str, Any]:
    failures = validate_approval_path(path, lock, actions)
    if failures:
        return {
            "ok": False,
            "path": str(path),
            "failures": failures,
            "failure": "; ".join(failures),
            "provider_mutation_executed": False,
        }
    return {"ok": True, "path": str(path), "provider_mutation_executed": False}


def validate_artifact_payload(artifact: dict[str, Any], lock: dict[str, Any], actions: list[str]) -> list[str]:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "freeze-reopen-approval.json"
        path.write_text(json.dumps(artifact), encoding="utf-8")
        return validate_approval_path(path, lock, actions)


def validate_approval_path(path: Path, lock: dict[str, Any], actions: list[str]) -> list[str]:
    failures: list[str] = []
    for action in actions:
        failures.extend(validate_reopen_approval(path, lock, action=action))
    failures.extend(validate_release_artifact_chain(action=actions[0], reopen_approval_path=path))
    return sorted(set(failures))


if __name__ == "__main__":
    sys.exit(main())
