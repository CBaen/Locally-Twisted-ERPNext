#!/usr/bin/env python3
"""Print the current local release status in plain English and JSON.

This is a non-mutating dashboard command. It reads local artifacts and tells a
future agent whether the next step is READY_FOR_CONTROLLER, NO-GO, or BLOCKED.
It never contacts Frappe Cloud and never performs provider mutation.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from release_guard_common import (
    DEFAULT_LOCK_PATH,
    PROJECT_ROOT,
    ReleaseGuardError,
    current_git_head,
    load_release_lock,
    raise_if_failures,
    validate_read_receipt,
    validate_release_lock,
    validate_reopen_approval,
)
from release_identity_artifact import validate_identity_artifact


DEFAULT_TARGET_SITE = "locallytwisted-staging.frappe.cloud"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lock-file", type=Path, default=DEFAULT_LOCK_PATH)
    parser.add_argument("--identity-proof", type=Path, help="Fresh release-identity-proof.json.")
    parser.add_argument("--reopen-approval", type=Path, help="Fresh freeze-reopen-approval.json.")
    parser.add_argument("--read-receipt", type=Path, help="Fresh required-doc read receipt JSON.")
    parser.add_argument("--packet-dir", type=Path, help="Fresh release artifact packet directory, if prepared.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        result = build_report(args)
    except ReleaseGuardError as exc:
        result = {
            "ok": False,
            "status": "BLOCKED",
            "blockers": [str(exc)],
            "provider_mutation_executed": False,
        }
    except Exception as exc:  # pragma: no cover - defensive CLI surface.
        result = {
            "ok": False,
            "status": "BLOCKED",
            "blockers": [f"{type(exc).__name__}: {exc}"],
            "provider_mutation_executed": False,
        }

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"[LT RELEASE STATUS] {result['status']}")
        print(f"  source: {result.get('source_commit', 'unknown')}")
        print(f"  target: {result.get('target_site', DEFAULT_TARGET_SITE)}")
        print(f"  provider_mutation_executed: {str(result.get('provider_mutation_executed')).lower()}")
        blockers = result.get("blockers") or []
        if blockers:
            print("  blockers:")
            for blocker in blockers:
                print(f"    - {blocker}")
        print(f"  next_safe_step: {result.get('next_safe_step')}")
    return 0 if result.get("ok") else 1


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    lock = load_release_lock(args.lock_file)
    lock_failures = validate_release_lock(lock)
    if lock_failures:
        return status_result(
            status="BLOCKED",
            lock=lock,
            blockers=[f"invalid active release lock: {'; '.join(lock_failures)}"],
            checks=[],
        )

    blockers: list[str] = []
    checks: list[dict[str, Any]] = []
    source_commit = current_git_head()

    record_check(checks, "release_lock", True, f"{lock.get('id')} is active at stage {lock.get('stage')}")

    if lock.get("status") == "active" and lock.get("stage") == "forensic-freeze":
        record_check(checks, "forensic_freeze", True, "release mutation is blocked until fresh approval artifacts exist")

    if args.identity_proof:
        identity_failures = validate_identity_artifact(args.identity_proof, lock=lock)
        if identity_failures:
            blockers.append("identity proof is invalid: " + "; ".join(identity_failures))
            record_check(checks, "identity_proof", False, str(args.identity_proof))
        else:
            record_check(checks, "identity_proof", True, str(args.identity_proof))
    else:
        blockers.append("fresh release identity proof artifact is missing")
        record_check(checks, "identity_proof", False, "not provided")

    if args.reopen_approval:
        approval_failures = validate_reopen_approval(args.reopen_approval, lock)
        if approval_failures:
            blockers.append("freeze reopen approval is invalid: " + "; ".join(approval_failures))
            record_check(checks, "freeze_reopen_approval", False, str(args.reopen_approval))
        else:
            record_check(checks, "freeze_reopen_approval", True, str(args.reopen_approval))
    else:
        blockers.append("fresh freeze-reopen approval artifact is missing")
        record_check(checks, "freeze_reopen_approval", False, "not provided")

    if args.read_receipt:
        receipt_failures = validate_read_receipt(args.read_receipt, lock.get("required_read_docs"))
        if receipt_failures:
            blockers.append("required-doc read receipt is invalid: " + "; ".join(receipt_failures))
            record_check(checks, "read_receipt", False, str(args.read_receipt))
        else:
            record_check(checks, "read_receipt", True, str(args.read_receipt))
    else:
        blockers.append("fresh required-doc read receipt is missing")
        record_check(checks, "read_receipt", False, "not provided")

    if args.packet_dir:
        packet_failures = validate_packet_dir(args.packet_dir)
        if packet_failures:
            blockers.append("release packet is incomplete: " + "; ".join(packet_failures))
            record_check(checks, "release_packet", False, str(args.packet_dir))
        else:
            record_check(checks, "release_packet", True, str(args.packet_dir))
    else:
        blockers.append("fresh release artifact packet directory is missing")
        record_check(checks, "release_packet", False, "not provided")

    status = "NO-GO" if blockers else "READY_FOR_CONTROLLER"
    return status_result(
        status=status,
        lock=lock,
        source_commit=source_commit,
        blockers=blockers,
        checks=checks,
    )


def validate_packet_dir(packet_dir: Path) -> list[str]:
    failures: list[str] = []
    if not packet_dir.exists() or not packet_dir.is_dir():
        return [f"packet directory does not exist: {packet_dir}"]
    required_names = {
        "controller.md",
        "provider-witness.md",
        "gate-fixer.md",
        "recorder.md",
        "failure-ledger.json",
        "read-receipt.json",
    }
    found = {path.name for path in packet_dir.iterdir()}
    missing = sorted(required_names - found)
    if missing:
        failures.append(f"packet directory is missing required artifacts: {missing}")
    readme = packet_dir / "README.md"
    if readme.exists():
        text = readme.read_text(encoding="utf-8", errors="replace").lower()
        if "no-go" in text or "read-only evidence only" in text:
            failures.append("packet README is explicitly no-go/read-only; create a fresh mutation-capable packet")
    else:
        failures.append("packet directory is missing README.md")
    return failures


def record_check(checks: list[dict[str, Any]], name: str, ok: bool, detail: str) -> None:
    checks.append({"name": name, "ok": ok, "detail": detail})


def status_result(
    *,
    status: str,
    lock: dict[str, Any],
    blockers: list[str],
    checks: list[dict[str, Any]],
    source_commit: str | None = None,
) -> dict[str, Any]:
    if source_commit is None:
        try:
            source_commit = current_git_head()
        except ReleaseGuardError:
            source_commit = "unknown"
    return {
        "ok": status == "READY_FOR_CONTROLLER",
        "status": status,
        "source_commit": source_commit,
        "lock_id": lock.get("id"),
        "lock_stage": lock.get("stage"),
        "target_site": DEFAULT_TARGET_SITE,
        "blockers": blockers,
        "checks": checks,
        "provider_mutation_executed": False,
        "next_safe_step": next_safe_step(status, blockers),
    }


def next_safe_step(status: str, blockers: list[str]) -> str:
    if status == "READY_FOR_CONTROLLER":
        return "Run the release controller with the fresh packet artifacts; do not bypass controller gates."
    if any("identity proof" in blocker for blocker in blockers):
        return "Create a fresh release identity proof artifact before requesting any release mutation."
    if any("approval" in blocker for blocker in blockers):
        return "Get explicit bounded approval and generate a fresh freeze-reopen approval artifact."
    return "Stay in forensic/local guard mode and close the listed blockers."


if __name__ == "__main__":
    sys.exit(main())
