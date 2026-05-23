#!/usr/bin/env python3
"""Local Frappe Cloud release controller gate for Locally Twisted.

This script is a preflight/controller gate, not a deployment client. It checks
the active release lock, required read receipt, payload shape, failure circuit
breaker, provider snapshot, and artifact-owned triad inputs before any future
release script is allowed to mutate provider state.

Examples:
  python scripts/release/frappe_cloud_release_controller.py --action frappe_cloud_deploy
  python scripts/release/frappe_cloud_release_controller.py --action read_only_forensics --read-receipt path/to/read-receipt.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from release_guard_common import (
    DEFAULT_LOCK_PATH,
    PROJECT_ROOT,
    ReleaseGuardError,
    action_is_mutating,
    ensure_action_allowed,
    load_release_lock,
    raise_if_failures,
    validate_failure_ledger,
    validate_app_mirror_freshness,
    validate_hosted_bootstrap_preflight,
    validate_provider_snapshot,
    validate_read_receipt,
    validate_release_lock,
    validate_triad_artifacts,
)

sys.path.insert(0, str(PROJECT_ROOT))
from scripts.verify.frappe_cloud_payload_contract import (  # noqa: E402
    load_payload_file,
    validate_frappe_cloud_payload,
)


READ_RECEIPT_ACTIONS = {
    "read_only_forensics",
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

PAYLOAD_REQUIRED_ACTIONS = {
    "frappe_cloud_deploy",
}

HOSTED_PREFLIGHT_REQUIRED_ACTIONS = {
    "staging_bootstrap",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--action", required=True, help="Release action to gate.")
    parser.add_argument("--lock-file", type=Path, default=DEFAULT_LOCK_PATH)
    parser.add_argument("--read-receipt", type=Path, help="JSON proof that required release docs were read.")
    parser.add_argument("--payload-file", type=Path, help="Sanitized Frappe Cloud JSON payload artifact to validate.")
    parser.add_argument("--app-mirror-freshness", type=Path, help="Read-only app mirror freshness artifact JSON.")
    parser.add_argument("--hosted-bootstrap-preflight", type=Path, help="Read-only hosted staging bootstrap preflight artifact JSON.")
    parser.add_argument("--provider-snapshot", type=Path, help="Read-only provider-state snapshot JSON.")
    parser.add_argument("--triad-artifact-dir", type=Path, help="Directory containing controller/provider-witness/gate-fixer/recorder artifacts.")
    parser.add_argument("--failure-ledger", type=Path, help="JSON failure-class ledger for circuit-breaker checks.")
    parser.add_argument("--emergency-handoff-dir", type=Path, help="Directory where a failed release command writes an emergency handoff artifact.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable result.")
    args = parser.parse_args()

    try:
        result = run_controller(args)
    except ReleaseGuardError as exc:
        result = {"ok": False, "action": args.action, "failure": str(exc)}
    except Exception as exc:  # pragma: no cover - defensive crash surface.
        result = {"ok": False, "action": args.action, "failure": f"{type(exc).__name__}: {exc}"}

    if not result["ok"] and args.emergency_handoff_dir:
        result["emergency_handoff"] = str(write_emergency_handoff(args, result))

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        marker = "PASS" if result["ok"] else "BLOCK"
        print(f"[FRAPPE CLOUD RELEASE CONTROLLER] {marker}")
        print(f"  action: {result['action']}")
        if result["ok"]:
            print("  result: preflight gates passed; no provider mutation was executed")
        else:
            print(f"  failure: {result['failure']}")
    return 0 if result["ok"] else 1


def write_emergency_handoff(args: argparse.Namespace, result: dict[str, object]) -> Path:
    args.emergency_handoff_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = args.emergency_handoff_dir / f"emergency-handoff-{stamp}-{args.action}.md"
    lock_id = "unknown"
    lock_stage = "unknown"
    try:
        lock = load_release_lock(args.lock_file)
        lock_id = str(lock.get("id") or "unknown")
        lock_stage = str(lock.get("stage") or "unknown")
    except Exception:
        pass
    path.write_text(
        "\n".join(
            [
                "# Emergency Release Handoff",
                "",
                f"Action: `{args.action}`",
                f"Result: BLOCK",
                f"Failure: {result.get('failure')}",
                f"Active lock: `{lock_id}`",
                f"Lock stage: `{lock_stage}`",
                "",
                "## Current State",
                "",
                "Release controller blocked before provider mutation. This artifact is local evidence only.",
                "",
                "## Last Mutation",
                "",
                "None performed by this controller run.",
                "",
                "## Known Blockers",
                "",
                f"- {result.get('failure')}",
                "",
                "## What Not To Touch",
                "",
                "- Frappe Cloud deploy/update/bootstrap/migrate/cache",
                "- live release",
                "- DNS",
                "- Stripe",
                "- Search Console",
                "- production indexing",
                "- checkout unpause",
                "",
                "## Next Safe Action",
                "",
                "Stay in forensic/read-only mode, update the blocker evidence, and reopen release execution only with a fresh artifact-backed plan.",
                "",
                "## Failure-Class Circuit Breaker",
                "",
                f"Failure ledger provided: `{bool(args.failure_ledger)}`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def run_controller(args: argparse.Namespace) -> dict[str, object]:
    lock = load_release_lock(args.lock_file)
    raise_if_failures("invalid release lock", validate_release_lock(lock))

    if args.action in PAYLOAD_REQUIRED_ACTIONS and not args.payload_file:
        raise ReleaseGuardError("sanitized Frappe Cloud payload artifact is required before deploy/update actions")

    if args.payload_file:
        payload = load_payload_file(args.payload_file)
        raise_if_failures("invalid Frappe Cloud payload", validate_frappe_cloud_payload(payload))

    if args.action in READ_RECEIPT_ACTIONS:
        if not args.read_receipt:
            raise ReleaseGuardError("required-doc read receipt is missing")
        raise_if_failures("invalid read receipt", validate_read_receipt(args.read_receipt, lock.get("required_read_docs")))

    if action_is_mutating(args.action):
        if not args.app_mirror_freshness:
            raise ReleaseGuardError("app mirror freshness artifact is required before mutation")
        raise_if_failures("invalid app mirror freshness artifact", validate_app_mirror_freshness(args.app_mirror_freshness))

        if not args.provider_snapshot:
            raise ReleaseGuardError("provider snapshot is required before mutation")
        raise_if_failures("invalid provider snapshot", validate_provider_snapshot(args.provider_snapshot))

        if args.action in HOSTED_PREFLIGHT_REQUIRED_ACTIONS:
            if not args.hosted_bootstrap_preflight:
                raise ReleaseGuardError("hosted bootstrap preflight artifact is required before staging bootstrap")
            raise_if_failures(
                "invalid hosted bootstrap preflight artifact",
                validate_hosted_bootstrap_preflight(
                    args.hosted_bootstrap_preflight,
                    provider_snapshot_path=args.provider_snapshot,
                    app_mirror_freshness_path=args.app_mirror_freshness,
                ),
            )

        if not args.triad_artifact_dir:
            raise ReleaseGuardError("artifact-owned triad directory is required before mutation")
        raise_if_failures("invalid triad artifacts", validate_triad_artifacts(args.triad_artifact_dir))

        if not args.failure_ledger:
            raise ReleaseGuardError("failure-class ledger is required before mutation")
        raise_if_failures("failure circuit breaker blocked mutation", validate_failure_ledger(args.failure_ledger))

    ensure_action_allowed(args.action, lock)

    return {
        "ok": True,
        "action": args.action,
        "lock": lock.get("id"),
        "stage": lock.get("stage"),
        "provider_mutation_executed": False,
    }


if __name__ == "__main__":
    sys.exit(main())
