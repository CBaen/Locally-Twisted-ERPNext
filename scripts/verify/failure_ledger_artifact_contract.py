#!/usr/bin/env python3
"""Offline contract for the LT failure-ledger artifact helper."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / "scripts" / "release" / "failure_ledger_artifact.py"
CONTROLLER = ROOT / "scripts" / "release" / "frappe_cloud_release_controller.py"

sys.path.insert(0, str(ROOT / "scripts" / "release"))
from release_guard_common import REQUIRED_READ_DOCS  # noqa: E402

ROLLBACK_HASH = "1" * 40
TARGET_HASH = "2" * 40


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    failures = run_contract()
    result = {"ok": not failures, "failures": failures}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("[FAILURE LEDGER ARTIFACT CONTRACT] " + ("PASS" if result["ok"] else "FAIL"))
        for failure in failures:
            print(f"  - {failure}")
    return 0 if result["ok"] else 1


def run_contract() -> list[str]:
    failures: list[str] = []
    cleanup_release_outputs()
    try:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            release_output = ROOT / "workstreams" / "release-artifacts" / "tmp-contract-failure-ledger" / "failure-ledger.json"
            valid_copy = tmp_path / "failure-ledger.json"

            preview = run_helper("--json")
            if preview.returncode == 0:
                failures.append("preview mode returned success without --write")
            preview_payload = parse_json_stdout(preview, failures)
            if preview_payload.get("preview", {}).get("ok") is not False:
                failures.append("preview payload must not be controller-consumable ok=true")
            if preview_payload.get("preview", {}).get("controller_consumable") is not False:
                failures.append("preview payload must mark controller_consumable=false")
            if preview_payload.get("provider_mutation_executed") is not False:
                failures.append("preview result must prove provider_mutation_executed=false")

            write_valid = run_helper(
                "--write",
                "--output",
                str(release_output),
                "--reviewed-source",
                "--agent",
                "failure-ledger-artifact-contract",
                "--json",
            )
            if write_valid.returncode != 0:
                failures.append(f"valid failure ledger write failed: {write_valid.stdout} {write_valid.stderr}")
            elif not release_output.exists():
                failures.append("valid failure ledger write did not create output file")
            else:
                artifact = json.loads(release_output.read_text(encoding="utf-8"))
                if artifact.get("ok") is not True:
                    failures.append("written failure ledger must be ok=true")
                if artifact.get("provider_mutation_executed") is not False:
                    failures.append("written failure ledger must prove provider_mutation_executed=false")
                if not artifact.get("failures"):
                    failures.append("written failure ledger must include failures")
                valid_copy.write_text(json.dumps(artifact), encoding="utf-8")

            validate_valid = run_helper("--validate-only", str(valid_copy), "--json")
            if validate_valid.returncode != 0:
                failures.append(f"valid failure ledger did not validate: {validate_valid.stdout} {validate_valid.stderr}")

            missing_review = run_helper(
                "--write",
                "--output",
                str(ROOT / "workstreams" / "release-artifacts" / "tmp-contract-failure-ledger-missing-review" / "failure-ledger.json"),
                "--json",
            )
            if missing_review.returncode == 0 or "--reviewed-source" not in missing_review.stdout:
                failures.append("write without --reviewed-source was not blocked")

            bad_output_name = run_helper(
                "--write",
                "--output",
                str(ROOT / "workstreams" / "release-artifacts" / "tmp-contract-failure-ledger-bad-name" / "bad-name.json"),
                "--reviewed-source",
                "--json",
            )
            if bad_output_name.returncode == 0 or "failure-ledger.json" not in bad_output_name.stdout:
                failures.append("bad output filename was not blocked")

            bad_output_location = run_helper(
                "--write",
                "--output",
                str(tmp_path / "outside-release-artifacts" / "failure-ledger.json"),
                "--reviewed-source",
                "--json",
            )
            if bad_output_location.returncode == 0 or "release-artifacts" not in bad_output_location.stdout:
                failures.append("output outside workstreams/release-artifacts was not blocked")

            overwrite = run_helper(
                "--write",
                "--output",
                str(release_output),
                "--reviewed-source",
                "--json",
            )
            if overwrite.returncode == 0 or "overwrite" not in overwrite.stdout.lower():
                failures.append("existing failure ledger overwrite was not blocked")

            empty_ledger = tmp_path / "empty-failure-ledger.json"
            write_mutated_ledger(valid_copy, empty_ledger, lambda payload: payload.update({"failures": []}))
            empty_result = run_helper("--validate-only", str(empty_ledger), "--json")
            if empty_result.returncode == 0 or "non-empty" not in empty_result.stdout:
                failures.append("empty failure ledger did not fail validation")

            fake_guard = tmp_path / "fake-guard-failure-ledger.json"
            write_mutated_ledger(fake_guard_source(valid_copy), fake_guard, set_fake_guard)
            fake_guard_result = run_helper("--validate-only", str(fake_guard), "--json")
            if fake_guard_result.returncode == 0 or "guard_path" not in fake_guard_result.stdout:
                failures.append("failure ledger with fake guard path did not fail validation")

            missing_summary = tmp_path / "missing-summary-failure-ledger.json"
            write_mutated_ledger(valid_copy, missing_summary, lambda payload: payload["failures"][0].pop("summary", None))
            missing_summary_result = run_helper("--validate-only", str(missing_summary), "--json")
            if missing_summary_result.returncode == 0 or "summary" not in missing_summary_result.stdout:
                failures.append("failure ledger missing summary did not fail validation")

            raw_secret = tmp_path / "raw-secret-failure-ledger.json"
            write_mutated_ledger(valid_copy, raw_secret, lambda payload: payload.update({"raw_provider_log": "token=abc"}))
            raw_secret_result = run_helper("--validate-only", str(raw_secret), "--json")
            if raw_secret_result.returncode == 0 or "disallowed" not in raw_secret_result.stdout:
                failures.append("failure ledger with raw/secret diagnostic key did not fail validation")

            stale = tmp_path / "stale-failure-ledger.json"
            write_mutated_ledger(valid_copy, stale, lambda payload: payload.update({"source_commit": "a" * 40}))
            stale_result = run_helper("--validate-only", str(stale), "--json")
            if stale_result.returncode == 0 or "current repository head" not in stale_result.stdout.lower():
                failures.append("stale-source failure ledger did not fail current-HEAD validation")

            repeated_no_plan = tmp_path / "repeated-no-plan-failure-ledger.json"
            write_mutated_ledger(valid_copy, repeated_no_plan, duplicate_first_failure)
            repeated_no_plan_result = run_helper("--validate-only", str(repeated_no_plan), "--json")
            if repeated_no_plan_result.returncode == 0 or "fresh_release_plan_approved" not in repeated_no_plan_result.stdout:
                failures.append("repeated failure class without fresh plan approval did not fail")

            repeated_with_plan = tmp_path / "repeated-with-plan-failure-ledger.json"
            write_mutated_ledger(valid_copy, repeated_with_plan, approve_repeated_failure)
            repeated_with_plan_result = run_helper("--validate-only", str(repeated_with_plan), "--json")
            if repeated_with_plan_result.returncode != 0:
                failures.append(f"repeated failure class with evidence did not validate: {repeated_with_plan_result.stdout}")

            controller_artifacts = write_controller_artifacts(tmp_path, valid_copy)
            missing_ledger = run_controller(
                "--action",
                "app_mirror_sync",
                *controller_artifacts["common_args"],
                "--json",
            )
            if missing_ledger.returncode == 0 or "failure-class ledger" not in missing_ledger.stdout.lower():
                failures.append("controller did not block app_mirror_sync when failure ledger was missing")

            invalid_ledger = run_controller(
                "--action",
                "app_mirror_sync",
                *controller_artifacts["common_args"],
                "--failure-ledger",
                str(empty_ledger),
                "--json",
            )
            if invalid_ledger.returncode == 0 or "failure ledger" not in invalid_ledger.stdout.lower():
                failures.append("controller did not block app_mirror_sync with invalid failure ledger")

            valid_ledger = run_controller(
                "--action",
                "app_mirror_sync",
                *controller_artifacts["common_args"],
                "--failure-ledger",
                str(valid_copy),
                "--json",
            )
            if valid_ledger.returncode != 0:
                failures.append(f"controller did not accept app_mirror_sync with valid failure ledger and artifacts: {valid_ledger.stdout}")

            help_result = run_helper("--help")
            if help_result.returncode != 0:
                failures.append("failure ledger helper --help failed")
            for flag in ("--write", "--reviewed-source", "--validate-only", "--fresh-release-plan-approved"):
                if flag not in help_result.stdout:
                    failures.append(f"failure ledger helper help does not expose {flag}")
    finally:
        cleanup_release_outputs()
    return failures


def write_controller_artifacts(tmp_path: Path, valid_ledger: Path) -> dict[str, list[str]]:
    approval = tmp_path / "freeze-reopen-approval.json"
    identity = tmp_path / "release-identity-proof.json"
    sync_plan = tmp_path / "app-mirror-sync-plan.json"
    provider = tmp_path / "provider-snapshot.json"
    receipt = tmp_path / "read-receipt.json"
    triad = tmp_path / "triad"
    write_reopen_approval(approval)
    write_identity(identity)
    write_sync_plan(sync_plan)
    write_provider(provider)
    write_read_receipt(receipt)
    write_triad(triad)
    return {
        "common_args": [
            "--read-receipt",
            str(receipt),
            "--reopen-approval",
            str(approval),
            "--identity-proof",
            str(identity),
            "--app-mirror-sync-plan",
            str(sync_plan),
            "--provider-snapshot",
            str(provider),
            "--triad-artifact-dir",
            str(triad),
        ]
    }


def write_identity(path: Path) -> None:
    checked_at = datetime.now(timezone.utc).isoformat()
    checks = []
    for surface, expected, actual in (
        ("codex_account", "Codex/ChatGPT account selected intentionally for LT release work", "work-account-contract"),
        ("github_cli", "GitHub CLI account allowed to read/write LT source and app mirror as needed", "CBaen"),
        ("frappe_cloud_team", "Frappe Cloud team/account owns the LT staging site", "lt-team-contract"),
        ("frappe_cloud_site", "locallytwisted-staging.frappe.cloud", "locallytwisted-staging.frappe.cloud"),
        ("app_mirror_repo", "https://github.com/CBaen/Locally-Twisted-Frappe-App.git", "https://github.com/CBaen/Locally-Twisted-Frappe-App.git"),
        ("release_operator", "named operator responsible for this release packet", "failure-ledger-contract"),
    ):
        checks.append(
            {
                "surface": surface,
                "status": "manual_confirmed",
                "expected": expected,
                "actual": actual,
                "method": "offline failure-ledger contract fixture",
                "evidence": "synthetic release identity proof for local contract only",
                "checked_at": checked_at,
            }
        )
    created_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    path.write_text(
        json.dumps(
            {
                "ok": True,
                "artifact_type": "release_identity_proof",
                "lock_id": "lt-staging-forensic-freeze-2026-05-23",
                "target_site": "locallytwisted-staging.frappe.cloud",
                "source_commit": git_head(),
                "created_at": created_at.isoformat(),
                "expires_at": (created_at + timedelta(hours=12)).isoformat(),
                "secret_free": True,
                "provider_mutation_executed": False,
                "account_checks": checks,
            }
        ),
        encoding="utf-8",
    )


def write_reopen_approval(path: Path) -> None:
    approved_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    path.write_text(
        json.dumps(
            {
                "ok": True,
                "approval_type": "forensic_freeze_reopen",
                "lock_id": "lt-staging-forensic-freeze-2026-05-23",
                "approved_by": "Guiding Light",
                "approval_evidence": "failure-ledger-artifact-contract synthetic approval",
                "approved_at": approved_at.isoformat(),
                "expires_at": (approved_at + timedelta(hours=12)).isoformat(),
                "target_site": "locallytwisted-staging.frappe.cloud",
                "source_commit": git_head(),
                "approved_actions": ["app_mirror_sync"],
                "live_dns_stripe_search_console_blocked": True,
                "provider_mutation_executed": False,
            }
        ),
        encoding="utf-8",
    )


def write_sync_plan(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "ok": True,
                "artifact_type": "app_mirror_sync_plan",
                "agent": "failure-ledger-artifact-contract",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "source_commit": git_head(),
                "mirror_url": "https://github.com/CBaen/Locally-Twisted-Frappe-App.git",
                "mirror_ref": "main",
                "target_site": "locallytwisted-staging.frappe.cloud",
                "rollback_hash": ROLLBACK_HASH,
                "required_files": [
                    "locally_twisted/staging_owner_review_bootstrap.py",
                    "locally_twisted/staging_owner_review_preflight.py",
                ],
                "post_sync_required": ["app-mirror-freshness.json"],
                "no_provider_deploy_until_post_sync_freshness": True,
                "reviewed_source": True,
                "provider_mutation_executed": False,
                "app_mirror_sync_executed": False,
            }
        ),
        encoding="utf-8",
    )


def write_provider(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "team": "Built by Cameron",
                "site": "locallytwisted-staging.frappe.cloud",
                "bench_group": "bench-40102",
                "bench": "bench-40102-000003-f4v",
                "installed_app_hash": ROLLBACK_HASH,
                "target_app_hash": ROLLBACK_HASH,
                "release_id": "contract",
                "running_jobs": [],
                "app_order": ["frappe", "erpnext", "payments", "webshop", "locally_twisted"],
                "site_status": "Active",
                "rollback_hash": ROLLBACK_HASH,
                "staging_live_separation": True,
            }
        ),
        encoding="utf-8",
    )


def write_read_receipt(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "agent": "failure-ledger-artifact-contract",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "read_documents": REQUIRED_READ_DOCS,
            }
        ),
        encoding="utf-8",
    )


def write_triad(directory: Path) -> None:
    directory.mkdir()
    for filename in ("controller.md", "provider-witness.md", "gate-fixer.md", "recorder.md"):
        (directory / filename).write_text(
            f"target: locallytwisted-staging.frappe.cloud\nstate: PASS\nevidence: {filename} synthetic proof\n",
            encoding="utf-8",
        )


def write_mutated_ledger(source: Path, target: Path, mutate) -> None:
    payload = json.loads(source.read_text(encoding="utf-8"))
    mutate(payload)
    target.write_text(json.dumps(payload), encoding="utf-8")


def fake_guard_source(path: Path) -> Path:
    return path


def set_fake_guard(payload: dict[str, object]) -> None:
    failures = payload.get("failures")
    if isinstance(failures, list) and failures and isinstance(failures[0], dict):
        failures[0]["guard_path"] = "scripts/verify/not-a-real-guard.py"


def duplicate_first_failure(payload: dict[str, object]) -> None:
    failures = payload.get("failures")
    if isinstance(failures, list) and failures:
        failures.append(dict(failures[0]))
    payload["fresh_release_plan_approved"] = False
    payload.pop("fresh_release_plan_evidence", None)


def approve_repeated_failure(payload: dict[str, object]) -> None:
    duplicate_first_failure(payload)
    payload["fresh_release_plan_approved"] = True
    payload["fresh_release_plan_evidence"] = "failure-ledger-artifact-contract synthetic plan evidence"


def parse_json_stdout(result: subprocess.CompletedProcess[str], failures: list[str]) -> dict[str, object]:
    try:
        parsed = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        failures.append(f"helper did not emit parseable JSON: {exc}")
        return {}
    if not isinstance(parsed, dict):
        failures.append("helper JSON output is not an object")
        return {}
    return parsed


def run_helper(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(HELPER), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )


def run_controller(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CONTROLLER), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=60,
    )


def cleanup_release_outputs() -> None:
    release_root = ROOT / "workstreams" / "release-artifacts"
    for name in (
        "tmp-contract-failure-ledger",
        "tmp-contract-failure-ledger-missing-review",
        "tmp-contract-failure-ledger-bad-name",
    ):
        target = release_root / name
        if target.exists():
            for path in sorted(target.glob("*")):
                path.unlink()
            target.rmdir()


def git_head() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.strip().lower()


if __name__ == "__main__":
    sys.exit(main())
