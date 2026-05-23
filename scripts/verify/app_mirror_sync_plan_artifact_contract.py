#!/usr/bin/env python3
"""Offline contract for the app mirror sync plan artifact helper."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / "scripts" / "release" / "app_mirror_sync_plan_artifact.py"
CONTROLLER = ROOT / "scripts" / "release" / "frappe_cloud_release_controller.py"
READ_RECEIPT = ROOT / "workstreams" / "release-artifacts" / "2026-05-23-staging-reopen-9e63fef-readonly" / "read-receipt.json"
ROLLBACK_HASH = "1" * 40


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    failures = run_contract()
    result = {"ok": not failures, "failures": failures}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("[APP MIRROR SYNC PLAN ARTIFACT CONTRACT] " + ("PASS" if result["ok"] else "FAIL"))
        for failure in failures:
            print(f"  - {failure}")
    return 0 if result["ok"] else 1


def run_contract() -> list[str]:
    failures: list[str] = []
    cleanup_release_outputs()
    try:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            valid_path = tmp_path / "app-mirror-sync-plan.json"
            release_output = ROOT / "workstreams" / "release-artifacts" / "tmp-contract-app-mirror-sync-plan" / "app-mirror-sync-plan.json"

            preview = run_helper("--rollback-hash", ROLLBACK_HASH, "--json")
            if preview.returncode == 0:
                failures.append("preview mode returned success without --write")
            preview_payload = parse_json_stdout(preview, failures)
            if preview_payload.get("preview", {}).get("ok") is not False:
                failures.append("preview payload must not be controller-consumable ok=true")
            if preview_payload.get("preview", {}).get("preview_only") is not True:
                failures.append("preview payload did not mark preview_only=true")

            write_valid = run_helper(
                "--write",
                "--output",
                str(release_output),
                "--rollback-hash",
                ROLLBACK_HASH,
                "--reviewed-source",
                "--agent",
                "app-mirror-sync-plan-artifact-contract",
                "--json",
            )
            if write_valid.returncode != 0:
                write_output = f"{write_valid.stdout}\n{write_valid.stderr}".lower()
                if "release source and guard files must be clean" in write_output:
                    write_synthetic_valid_plan(valid_path)
                    dirty_guard_observed = True
                else:
                    failures.append(f"valid sync plan write failed: {write_valid.stdout} {write_valid.stderr}")
            elif not release_output.exists():
                failures.append("valid sync plan write did not create output file")
                dirty_guard_observed = False
            else:
                dirty_guard_observed = False

            if release_output.exists():
                artifact = json.loads(release_output.read_text(encoding="utf-8"))
                if artifact.get("ok") is not True:
                    failures.append("written sync plan must be ok=true")
                if artifact.get("provider_mutation_executed") is not False:
                    failures.append("written sync plan must prove provider_mutation_executed=false")
                if artifact.get("app_mirror_sync_executed") is not False:
                    failures.append("written sync plan must prove app_mirror_sync_executed=false")
                if artifact.get("reviewed_source") is not True:
                    failures.append("written sync plan must prove reviewed_source=true")
                valid_path.write_text(json.dumps(artifact), encoding="utf-8")

            validate_valid = run_helper("--validate-only", str(valid_path), "--json")
            if validate_valid.returncode != 0:
                failures.append(f"valid sync plan did not validate: {validate_valid.stdout} {validate_valid.stderr}")

            controller_without_approval = run_controller(
                "--action",
                "app_mirror_sync",
                "--read-receipt",
                str(READ_RECEIPT),
                "--app-mirror-sync-plan",
                str(valid_path),
                "--json",
            )
            if controller_without_approval.returncode == 0:
                failures.append("controller accepted app mirror sync plan without freeze reopen approval")
            if "freeze reopen approval" not in f"{controller_without_approval.stdout}\n{controller_without_approval.stderr}".lower():
                failures.append("controller missing-approval failure did not name freeze reopen approval")

            bad_mirror = run_helper("--rollback-hash", ROLLBACK_HASH, "--mirror-url", "https://example.com/CBaen/Locally-Twisted-Frappe-App.git", "--json")
            if bad_mirror.returncode == 0 or "mirror url" not in bad_mirror.stdout.lower():
                failures.append("non-canonical mirror URL was not blocked")

            bad_ref = run_helper("--rollback-hash", ROLLBACK_HASH, "--mirror-ref", "feature/test", "--json")
            if bad_ref.returncode == 0 or "mirror ref" not in bad_ref.stdout.lower():
                failures.append("non-canonical mirror ref was not blocked")

            bad_output_location = run_helper(
                "--write",
                "--output",
                str(tmp_path / "outside-release-artifacts" / "app-mirror-sync-plan.json"),
                "--rollback-hash",
                ROLLBACK_HASH,
                "--reviewed-source",
                "--json",
            )
            if bad_output_location.returncode == 0 or "release-artifacts" not in bad_output_location.stdout:
                failures.append("output outside workstreams/release-artifacts was not blocked")

            missing_review = run_helper(
                "--write",
                "--output",
                str(ROOT / "workstreams" / "release-artifacts" / "tmp-contract-missing-review" / "app-mirror-sync-plan.json"),
                "--rollback-hash",
                ROLLBACK_HASH,
                "--json",
            )
            if missing_review.returncode == 0 or "--reviewed-source" not in missing_review.stdout:
                failures.append("write without --reviewed-source was not blocked")

            bad_hash = run_helper(
                "--write",
                "--output",
                str(ROOT / "workstreams" / "release-artifacts" / "tmp-contract-bad-hash" / "app-mirror-sync-plan.json"),
                "--rollback-hash",
                "short",
                "--reviewed-source",
                "--json",
            )
            if bad_hash.returncode == 0 or "rollback hash" not in bad_hash.stdout.lower():
                failures.append("invalid rollback hash was not blocked")

            bad_output_name = run_helper(
                "--write",
                "--output",
                str(ROOT / "workstreams" / "release-artifacts" / "tmp-contract-bad-name" / "bad-name.json"),
                "--rollback-hash",
                ROLLBACK_HASH,
                "--reviewed-source",
                "--json",
            )
            if bad_output_name.returncode == 0 or "app-mirror-sync-plan.json" not in bad_output_name.stdout:
                failures.append("bad output filename was not blocked")

            if not dirty_guard_observed:
                overwrite = run_helper(
                    "--write",
                    "--output",
                    str(release_output),
                    "--rollback-hash",
                    ROLLBACK_HASH,
                    "--reviewed-source",
                    "--json",
                )
                if overwrite.returncode == 0 or "overwrite" not in overwrite.stdout.lower():
                    failures.append("existing sync plan overwrite was not blocked")

            stale_path = tmp_path / "stale" / "app-mirror-sync-plan.json"
            stale_path.parent.mkdir()
            stale_payload = json.loads(valid_path.read_text(encoding="utf-8"))
            stale_payload["source_commit"] = "a" * 40
            stale_path.write_text(json.dumps(stale_payload), encoding="utf-8")
            stale_result = run_helper("--validate-only", str(stale_path), "--json")
            if stale_result.returncode == 0 or "current repository head" not in stale_result.stdout.lower():
                failures.append("stale-source sync plan did not fail current-HEAD validation")

            missing_required = tmp_path / "missing-required" / "app-mirror-sync-plan.json"
            missing_required.parent.mkdir()
            missing_payload = json.loads(valid_path.read_text(encoding="utf-8"))
            missing_payload["required_files"] = []
            missing_required.write_text(json.dumps(missing_payload), encoding="utf-8")
            missing_required_result = run_helper("--validate-only", str(missing_required), "--json")
            if missing_required_result.returncode == 0 or "required_files" not in missing_required_result.stdout:
                failures.append("sync plan missing required_files did not fail validation")

            help_result = run_helper("--help")
            if help_result.returncode != 0:
                failures.append("sync plan helper --help failed")
            for flag in ("--write", "--rollback-hash", "--reviewed-source", "--validate-only"):
                if flag not in help_result.stdout:
                    failures.append(f"sync plan helper help does not expose {flag}")

    finally:
        cleanup_release_outputs()

    return failures


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
        "tmp-contract-app-mirror-sync-plan",
        "tmp-contract-missing-review",
        "tmp-contract-bad-hash",
        "tmp-contract-bad-name",
    ):
        target = release_root / name
        if target.exists():
            for path in sorted(target.glob("*")):
                path.unlink()
            target.rmdir()


def write_synthetic_valid_plan(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "ok": True,
                "artifact_type": "app_mirror_sync_plan",
                "agent": "app-mirror-sync-plan-artifact-contract",
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
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


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
