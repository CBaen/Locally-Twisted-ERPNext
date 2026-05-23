#!/usr/bin/env python3
"""Offline contract for the freeze reopen approval artifact helper."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / "scripts" / "release" / "freeze_reopen_approval_artifact.py"


def main() -> int:
    failures = run_checks()
    if failures:
        print("[FREEZE REOPEN APPROVAL ARTIFACT CONTRACT] FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("[FREEZE REOPEN APPROVAL ARTIFACT CONTRACT] PASS")
    return 0


def run_checks() -> list[str]:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        valid_path = tmp_path / "freeze-reopen-approval.json"

        preview = run_helper("--json")
        if preview.returncode == 0:
            failures.append("preview mode returned success without --write")
        preview_payload = json.loads(preview.stdout)
        if preview_payload.get("preview", {}).get("ok") is not False:
            failures.append("preview payload must not be mutation-capable ok=true")
        if preview_payload.get("preview", {}).get("preview_only") is not True:
            failures.append("preview payload did not mark preview_only=true")

        write_valid = run_helper(
            "--write",
            "--output",
            str(valid_path),
            "--approved-by",
            "Guiding Light",
            "--approval-evidence",
            "contract test explicit approval placeholder",
            "--json",
        )
        if write_valid.returncode != 0:
            failures.append(f"valid approval write failed: {write_valid.stdout} {write_valid.stderr}")
        elif not valid_path.exists():
            failures.append("valid approval write did not create output file")

        validate_valid = run_helper("--validate-only", str(valid_path), "--json")
        if validate_valid.returncode != 0:
            failures.append(f"valid approval did not validate: {validate_valid.stdout} {validate_valid.stderr}")

        missing_write_evidence = run_helper(
            "--write",
            "--output",
            str(tmp_path / "missing-write-evidence.json"),
            "--approved-by",
            "Guiding Light",
            "--json",
        )
        if missing_write_evidence.returncode == 0 or "approval-evidence" not in missing_write_evidence.stdout.lower():
            failures.append("write without --approval-evidence was not blocked")

        overwrite = run_helper(
            "--write",
            "--output",
            str(valid_path),
            "--approved-by",
            "Guiding Light",
            "--approval-evidence",
            "contract test explicit approval placeholder",
            "--json",
        )
        if overwrite.returncode == 0 or "overwrite" not in overwrite.stdout.lower():
            failures.append("existing approval artifact overwrite was not blocked")

        live_action = run_helper(
            "--write",
            "--output",
            str(tmp_path / "bad-live.json"),
            "--approved-by",
            "Guiding Light",
            "--approval-evidence",
            "contract test explicit approval placeholder",
            "--action",
            "live_release",
            "--json",
        )
        if live_action.returncode == 0 or "non-staging" not in live_action.stdout.lower():
            failures.append("live_release action was not rejected")

        inactive_lock = tmp_path / "inactive-lock.json"
        lock_payload = json.loads((ROOT / "release_locks" / "locally-twisted-staging-forensic-freeze.json").read_text(encoding="utf-8"))
        lock_payload["status"] = "closed"
        inactive_lock.write_text(json.dumps(lock_payload), encoding="utf-8")
        inactive_result = run_helper(
            "--lock-file",
            str(inactive_lock),
            "--write",
            "--output",
            str(tmp_path / "inactive-lock-approval.json"),
            "--approved-by",
            "Guiding Light",
            "--approval-evidence",
            "contract test explicit approval placeholder",
            "--json",
        )
        if inactive_result.returncode == 0 or "release lock status" not in inactive_result.stdout.lower():
            failures.append("helper write did not reject an inactive release lock")

        stale_path = tmp_path / "stale-source.json"
        stale_payload = json.loads(valid_path.read_text(encoding="utf-8"))
        stale_payload["source_commit"] = "a" * 40
        stale_path.write_text(json.dumps(stale_payload), encoding="utf-8")
        stale_result = run_helper("--validate-only", str(stale_path), "--json")
        if stale_result.returncode == 0 or "current repository head" not in stale_result.stdout.lower():
            failures.append("stale-source approval did not fail current-HEAD validation")

        missing_evidence_path = tmp_path / "missing-approval-evidence.json"
        missing_evidence_payload = json.loads(valid_path.read_text(encoding="utf-8"))
        missing_evidence_payload.pop("approval_evidence", None)
        missing_evidence_path.write_text(json.dumps(missing_evidence_payload), encoding="utf-8")
        missing_evidence_result = run_helper("--validate-only", str(missing_evidence_path), "--json")
        if missing_evidence_result.returncode == 0 or "approval_evidence" not in missing_evidence_result.stdout.lower():
            failures.append("approval without approval_evidence did not fail validation")

        expired_path = tmp_path / "expired.json"
        expired_payload = dict(stale_payload)
        expired_payload["source_commit"] = json.loads(valid_path.read_text(encoding="utf-8"))["source_commit"]
        expired_payload["approved_at"] = (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat()
        expired_payload["expires_at"] = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        expired_path.write_text(json.dumps(expired_payload), encoding="utf-8")
        expired_result = run_helper("--validate-only", str(expired_path), "--json")
        if expired_result.returncode == 0 or "expired" not in expired_result.stdout.lower():
            failures.append("expired approval did not fail validation")

        timezone_less_path = tmp_path / "timezone-less.json"
        timezone_less_payload = json.loads(valid_path.read_text(encoding="utf-8"))
        timezone_less_payload["approved_at"] = "2026-05-23T12:00:00"
        timezone_less_payload["expires_at"] = "2026-05-23T13:00:00"
        timezone_less_path.write_text(json.dumps(timezone_less_payload), encoding="utf-8")
        timezone_less_result = run_helper("--validate-only", str(timezone_less_path), "--json")
        if timezone_less_result.returncode == 0 or "timezone" not in timezone_less_result.stdout.lower():
            failures.append("timezone-less approval did not fail validation")

        overlong = run_helper(
            "--write",
            "--output",
            str(tmp_path / "overlong.json"),
            "--approved-by",
            "Guiding Light",
            "--approval-evidence",
            "contract test explicit approval placeholder",
            "--duration-hours",
            "25",
            "--json",
        )
        if overlong.returncode == 0 or "24 hours" not in overlong.stdout.lower():
            failures.append("overlong generated approval was not blocked")

    return failures


def run_helper(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(HELPER), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


if __name__ == "__main__":
    sys.exit(main())
