#!/usr/bin/env python3
"""Offline contract for staging reopen packet prep-only output."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "release"))

from release_guard_common import REQUIRED_READ_DOCS, REQUIRED_TRIAD_ARTIFACTS, read_json  # noqa: E402


SCRIPT = ROOT / "scripts" / "release" / "staging_reopen_packet_prepare.py"
CONTROLLER = ROOT / "scripts" / "release" / "frappe_cloud_release_controller.py"
ROLLBACK_HASH = "1" * 40
PREP_ALLOWLIST = {
    "README.md",
    "packet-prep-manifest.json",
    "missing-release-artifacts.md",
    "freeze-reopen-approval-preview.json",
}
RESERVED_FINAL_NAMES = {
    "release-identity-proof.json",
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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    failures = run_contract()
    result = {"ok": not failures, "failures": failures}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("[STAGING REOPEN PACKET PREPARE CONTRACT] " + ("PASS" if result["ok"] else "FAIL"))
        for failure in failures:
            print(f"  - {failure}")
    return 0 if result["ok"] else 1


def run_contract() -> list[str]:
    failures: list[str] = []

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        output = tmp_path / "prepared-packet"
        result = run_prepare(
            "--output",
            str(output),
            "--rollback-hash",
            ROLLBACK_HASH,
            "--reviewed-source",
            "--agent",
            "staging-reopen-packet-prepare-contract",
            "--json",
        )
        if result.returncode != 0:
            failures.append("packet prep with reviewed source and rollback context did not pass")
            failures.append(result.stderr or result.stdout)
            return failures

        payload = parse_json_stdout(result, failures)
        assert_negative_flags(payload, "CLI output", failures)

        existing = {path.name for path in output.iterdir()}
        if existing != PREP_ALLOWLIST:
            failures.append(f"prep output file set mismatch: expected {sorted(PREP_ALLOWLIST)}, got {sorted(existing)}")
        reserved = sorted(name for name in RESERVED_FINAL_NAMES if (output / name).exists())
        if reserved:
            failures.append(f"prep output generated reserved final artifact names: {reserved}")

        manifest = read_json(output / "packet-prep-manifest.json")
        assert_negative_flags(manifest, "manifest", failures)
        if "ok" in manifest:
            failures.append("manifest must not use top-level ok as proof language")
        if manifest.get("artifact_type") != "staging_reopen_packet_prep":
            failures.append("manifest artifact_type is wrong")
        if manifest.get("artifact_status") != "prep_only":
            failures.append("manifest artifact_status must be prep_only")
        context = manifest.get("draft_app_mirror_sync_plan_context") or {}
        if context.get("controller_consumable") is not False:
            failures.append("draft app mirror sync plan context must be controller_consumable=false")
        if context.get("provider_mutation_executed") is not False:
            failures.append("draft app mirror sync plan context must prove provider_mutation_executed=false")

        preview = read_json(output / "freeze-reopen-approval-preview.json")
        if preview.get("ok") is not False or preview.get("preview_only") is not True:
            failures.append("approval preview must be ok=false and preview_only=true")
        if preview.get("provider_mutation_executed") is not False:
            failures.append("approval preview must prove provider_mutation_executed=false")

        read_receipt = tmp_path / "read-receipt-for-preview-rejection.json"
        write_temp_read_receipt(read_receipt)
        preview_as_approval = run_controller(
            "--action",
            "app_mirror_sync",
            "--read-receipt",
            str(read_receipt),
            "--reopen-approval",
            str(output / "freeze-reopen-approval-preview.json"),
            "--json",
        )
        if preview_as_approval.returncode == 0:
            failures.append("controller accepted approval preview as real freeze-reopen approval")
        preview_failure = f"{preview_as_approval.stdout}\n{preview_as_approval.stderr}".lower()
        if "freeze reopen approval" not in preview_failure or "ok=true" not in preview_failure:
            failures.append("controller did not reject approval preview as invalid freeze reopen approval")

        no_review = run_prepare("--output", str(tmp_path / "no-review"), "--rollback-hash", ROLLBACK_HASH, "--json")
        if no_review.returncode == 0:
            failures.append("packet prep passed without --reviewed-source")
        if "--reviewed-source" not in f"{no_review.stdout}\n{no_review.stderr}":
            failures.append("missing reviewed-source failure did not name --reviewed-source")

        bad_hash = run_prepare(
            "--output",
            str(tmp_path / "bad-hash"),
            "--rollback-hash",
            "short",
            "--reviewed-source",
            "--json",
        )
        if bad_hash.returncode == 0:
            failures.append("packet prep passed with invalid rollback hash")
        if "rollback hash" not in f"{bad_hash.stdout}\n{bad_hash.stderr}".lower():
            failures.append("bad rollback hash failure did not name rollback hash")

        dirty_output = tmp_path / "dirty-output"
        dirty_output.mkdir()
        (dirty_output / "freeze-reopen-approval.json").write_text("{}", encoding="utf-8")
        dirty_result = run_prepare(
            "--output",
            str(dirty_output),
            "--rollback-hash",
            ROLLBACK_HASH,
            "--reviewed-source",
            "--force",
            "--json",
        )
        if dirty_result.returncode == 0:
            failures.append("packet prep wrote into a directory containing final release artifact names")
        if "final release artifact" not in f"{dirty_result.stdout}\n{dirty_result.stderr}":
            failures.append("dirty output failure did not name final release artifact files")

        non_empty = tmp_path / "non-empty"
        non_empty.mkdir()
        (non_empty / "unrelated.txt").write_text("x", encoding="utf-8")
        non_empty_result = run_prepare(
            "--output",
            str(non_empty),
            "--rollback-hash",
            ROLLBACK_HASH,
            "--reviewed-source",
            "--json",
        )
        if non_empty_result.returncode == 0:
            failures.append("packet prep wrote into a non-empty output directory")
        if "outside the prep allowlist" not in f"{non_empty_result.stdout}\n{non_empty_result.stderr}":
            failures.append("non-empty output failure did not name prep allowlist")

        help_result = run_prepare("--help")
        if help_result.returncode != 0:
            failures.append("packet prep --help failed")
        if "--rollback-hash" not in help_result.stdout:
            failures.append("packet prep help does not expose --rollback-hash")
        if "--reviewed-source" not in help_result.stdout:
            failures.append("packet prep help does not expose --reviewed-source")

    return failures


def assert_negative_flags(payload: dict[str, object], label: str, failures: list[str]) -> None:
    expected_false = [
        "controller_consumable",
        "mutation_capable",
        "provider_mutation_executed",
        "approval_present",
        "provider_snapshot_present",
        "app_mirror_sync_executed",
        "deploy_completion_present",
        "hosted_preflight_present",
        "owner_review_ready",
        "triad_complete",
    ]
    for key in expected_false:
        if payload.get(key) is not False:
            failures.append(f"{label} {key} must be false")
    if payload.get("live_dns_stripe_search_console_blocked") is not True:
        failures.append(f"{label} must keep live/DNS/Stripe/Search Console blocked")


def parse_json_stdout(result: subprocess.CompletedProcess[str], failures: list[str]) -> dict[str, object]:
    try:
        parsed = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        failures.append(f"packet prep did not emit parseable JSON: {exc}")
        return {}
    if not isinstance(parsed, dict):
        failures.append("packet prep JSON output is not an object")
        return {}
    return parsed


def run_prepare(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
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


def write_temp_read_receipt(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "created_at": "2026-05-23T00:00:00+00:00",
                "agent": "staging-reopen-packet-prepare-contract",
                "read_documents": REQUIRED_READ_DOCS,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    sys.exit(main())
