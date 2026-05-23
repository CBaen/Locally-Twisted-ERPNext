#!/usr/bin/env python3
"""Verify the LT forensic-freeze release lock blocks release mutation locally.

This gate is offline. It proves the repo has a machine-readable active lock,
the lock blocks provider/live/search/payment actions, required docs exist,
missing read receipts fail, the failure circuit breaker works, and triad
artifacts are required.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "release"))

from release_guard_common import (  # noqa: E402
    DEFAULT_LOCK_PATH,
    REQUIRED_ALLOWED_ACTIONS,
    REQUIRED_BLOCKED_ACTIONS,
    REQUIRED_READ_DOCS,
    ReleaseGuardError,
    ensure_action_allowed,
    load_release_lock,
    validate_failure_ledger,
    validate_read_receipt,
    validate_release_lock,
    validate_triad_artifacts,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lock-file", type=Path, default=DEFAULT_LOCK_PATH)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    failures = run_checks(args.lock_file)
    result = {"ok": not failures, "failures": failures}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("[RELEASE LOCK CONTRACT] " + ("PASS" if result["ok"] else "FAIL"))
        for failure in failures:
            print(f"  - {failure}")
    return 0 if result["ok"] else 1


def run_checks(lock_file: Path) -> list[str]:
    failures: list[str] = []
    try:
        lock = load_release_lock(lock_file)
    except ReleaseGuardError as exc:
        return [str(exc)]

    failures.extend(validate_release_lock(lock))

    for action in sorted(REQUIRED_BLOCKED_ACTIONS):
        try:
            ensure_action_allowed(action, lock)
        except ReleaseGuardError:
            continue
        failures.append(f"blocked action was allowed during forensic-freeze: {action}")

    for action in sorted(REQUIRED_ALLOWED_ACTIONS):
        try:
            ensure_action_allowed(action, lock)
        except ReleaseGuardError as exc:
            failures.append(f"allowed forensic action was blocked: {action}: {exc}")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        missing_receipt = tmp_path / "missing-read-receipt.json"
        try:
            validate_read_receipt(missing_receipt)
            failures.append("missing read receipt did not fail")
        except ReleaseGuardError:
            pass

        valid_receipt = tmp_path / "valid-read-receipt.json"
        valid_receipt.write_text(
            json.dumps(
                {
                    "agent": "release-lock-contract",
                    "created_at": "2026-05-23T00:00:00-06:00",
                    "read_documents": REQUIRED_READ_DOCS,
                }
            ),
            encoding="utf-8",
        )
        failures.extend(validate_read_receipt(valid_receipt))

        triad_dir = tmp_path / "triad"
        triad_dir.mkdir()
        missing_triad_failures = validate_triad_artifacts(triad_dir)
        if not missing_triad_failures:
            failures.append("empty triad artifact directory did not fail")
        for filename in ("controller.md", "provider-witness.md", "gate-fixer.md", "recorder.md"):
            (triad_dir / filename).write_text(
                f"target: locallytwisted-staging.frappe.cloud\nstate: PASS\nevidence: {filename} proof\n",
                encoding="utf-8",
            )
        failures.extend(validate_triad_artifacts(triad_dir))

        repeated_ledger = tmp_path / "repeated-failures.json"
        repeated_ledger.write_text(
            json.dumps(
                {
                    "fresh_release_plan_approved": False,
                    "failures": [
                        {"class": "payload_shape", "guard_written": True},
                        {"class": "payload_shape", "guard_written": True},
                    ],
                }
            ),
            encoding="utf-8",
        )
        if not validate_failure_ledger(repeated_ledger):
            failures.append("repeated failure class without fresh plan did not fail")

        guarded_ledger = tmp_path / "guarded-failures.json"
        guarded_ledger.write_text(
            json.dumps(
                {
                    "fresh_release_plan_approved": True,
                    "failures": [
                        {"class": "payload_shape", "guard_written": True},
                        {"class": "payload_shape", "guard_written": True},
                    ],
                }
            ),
            encoding="utf-8",
        )
        failures.extend(validate_failure_ledger(guarded_ledger))

    return failures


if __name__ == "__main__":
    sys.exit(main())
