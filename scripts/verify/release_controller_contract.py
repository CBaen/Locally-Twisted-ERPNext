#!/usr/bin/env python3
"""Offline CLI contract for the LT Frappe Cloud release controller.

This proves the controller itself, not only helper functions:

- active forensic-freeze lock blocks mutation actions;
- missing read receipt blocks read-only release forensics;
- the controller exposes the app mirror freshness artifact gate;
- the controller exposes the hosted bootstrap preflight artifact gate;
- the staging bootstrap path fails missing, no-go, wrong-site, and wrong-hash
  hosted preflight artifacts before it can reach the final freeze block;
- a valid read receipt allows a read-only forensic action without provider
  mutation.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "release"))

from release_guard_common import REQUIRED_READ_DOCS  # noqa: E402


CONTROLLER = ROOT / "scripts" / "release" / "frappe_cloud_release_controller.py"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    failures = run_contract()
    result = {"ok": not failures, "failures": failures}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("[RELEASE CONTROLLER CONTRACT] " + ("PASS" if result["ok"] else "FAIL"))
        for failure in failures:
            print(f"  - {failure}")
    return 0 if result["ok"] else 1


def run_contract() -> list[str]:
    failures: list[str] = []

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        emergency_dir = tmp_path / "emergency"
        receipt = tmp_path / "read-receipt.json"
        receipt.write_text(
            json.dumps(
                {
                    "agent": "release-controller-contract",
                    "created_at": "2026-05-23T00:00:00-06:00",
                    "read_documents": REQUIRED_READ_DOCS,
                }
            ),
            encoding="utf-8",
        )

        missing_payload = run_controller("--action", "frappe_cloud_deploy", "--json")
        if missing_payload.returncode == 0:
            failures.append("frappe_cloud_deploy passed without a sanitized payload artifact")
        if "payload" not in f"{missing_payload.stdout}\n{missing_payload.stderr}".lower():
            failures.append("missing deploy payload output did not mention payload")

        payload = tmp_path / "sanitized-payload.json"
        payload.write_text(
            json.dumps(
                {
                    "content_type": "application/json",
                    "body": {
                        "apps": [
                            {
                                "app": "locally_twisted",
                                "repository": "https://github.com/CBaen/Locally-Twisted-Frappe-App.git",
                                "hash": "a" * 40,
                            }
                        ],
                        "sites": [{"name": "locallytwisted-staging.frappe.cloud"}],
                    },
                }
            ),
            encoding="utf-8",
        )

        deploy_missing_mirror = run_controller(
            "--action",
            "frappe_cloud_deploy",
            "--payload-file",
            str(payload),
            "--read-receipt",
            str(receipt),
            "--emergency-handoff-dir",
            str(emergency_dir),
            "--json",
        )
        if deploy_missing_mirror.returncode == 0:
            failures.append("frappe_cloud_deploy passed without app mirror freshness proof")
        if "app mirror freshness" not in f"{deploy_missing_mirror.stdout}\n{deploy_missing_mirror.stderr}".lower():
            failures.append("deploy missing-mirror output did not mention app mirror freshness")
        handoffs = list(emergency_dir.glob("emergency-handoff-*.md"))
        if not handoffs:
            failures.append("blocked deploy did not write an emergency handoff artifact")
        elif "What Not To Touch" not in handoffs[0].read_text(encoding="utf-8"):
            failures.append("emergency handoff is missing What Not To Touch section")

        missing_receipt = run_controller("--action", "read_only_forensics", "--json")
        if missing_receipt.returncode == 0:
            failures.append("read_only_forensics passed without a required-doc read receipt")
        if "read receipt" not in f"{missing_receipt.stdout}\n{missing_receipt.stderr}".lower():
            failures.append("missing receipt output did not mention read receipt")

        allowed = run_controller("--action", "read_only_forensics", "--read-receipt", str(receipt), "--json")
        if allowed.returncode != 0:
            failures.append("read_only_forensics with valid read receipt did not pass")
        if "provider_mutation_executed" not in allowed.stdout:
            failures.append("allowed read-only output did not report provider_mutation_executed=false")

        missing_mirror = run_controller("--action", "staging_bootstrap", "--read-receipt", str(receipt), "--json")
        if missing_mirror.returncode == 0:
            failures.append("staging_bootstrap passed without app mirror freshness artifact")
        if "app mirror freshness" not in f"{missing_mirror.stdout}\n{missing_mirror.stderr}".lower():
            failures.append("missing staging_bootstrap mirror output did not mention app mirror freshness")

        mirror = tmp_path / "app-mirror-freshness.json"
        provider = tmp_path / "provider-snapshot.json"
        hosted_valid = tmp_path / "hosted-bootstrap-preflight-valid.json"
        hosted_no_go = tmp_path / "hosted-bootstrap-preflight-no-go.json"
        hosted_wrong_site = tmp_path / "hosted-bootstrap-preflight-wrong-site.json"
        hosted_wrong_hash = tmp_path / "hosted-bootstrap-preflight-wrong-hash.json"
        triad_dir = tmp_path / "triad"
        ledger = tmp_path / "failure-ledger.json"
        write_valid_mirror(mirror, "b" * 40)
        write_valid_provider(provider, "locallytwisted-staging.frappe.cloud", "b" * 40)
        write_hosted_preflight(hosted_valid, "locallytwisted-staging.frappe.cloud", "b" * 40, ok=True)
        write_hosted_preflight(hosted_no_go, "locallytwisted-staging.frappe.cloud", "b" * 40, ok=False)
        write_hosted_preflight(hosted_wrong_site, "wrong-staging.frappe.cloud", "b" * 40, ok=True)
        write_hosted_preflight(hosted_wrong_hash, "locallytwisted-staging.frappe.cloud", "d" * 40, ok=True)
        write_valid_triad(triad_dir)
        ledger.write_text(json.dumps({"fresh_release_plan_approved": True, "failures": []}), encoding="utf-8")

        missing_hosted = run_controller(
            "--action",
            "staging_bootstrap",
            "--read-receipt",
            str(receipt),
            "--app-mirror-freshness",
            str(mirror),
            "--provider-snapshot",
            str(provider),
            "--json",
        )
        if missing_hosted.returncode == 0:
            failures.append("staging_bootstrap passed without hosted preflight artifact")
        if "hosted bootstrap preflight" not in f"{missing_hosted.stdout}\n{missing_hosted.stderr}".lower():
            failures.append("missing hosted preflight output did not mention hosted bootstrap preflight")

        for label, artifact in (
            ("no-go", hosted_no_go),
            ("wrong-site", hosted_wrong_site),
            ("wrong-hash", hosted_wrong_hash),
        ):
            invalid_hosted = run_controller(
                "--action",
                "staging_bootstrap",
                "--read-receipt",
                str(receipt),
                "--app-mirror-freshness",
                str(mirror),
                "--provider-snapshot",
                str(provider),
                "--hosted-bootstrap-preflight",
                str(artifact),
                "--json",
            )
            if invalid_hosted.returncode == 0:
                failures.append(f"staging_bootstrap passed with {label} hosted preflight artifact")
            combined = f"{invalid_hosted.stdout}\n{invalid_hosted.stderr}".lower()
            if "hosted bootstrap preflight" not in combined:
                failures.append(f"{label} hosted preflight failure did not mention hosted bootstrap preflight")

        freeze_after_valid_artifacts = run_controller(
            "--action",
            "staging_bootstrap",
            "--read-receipt",
            str(receipt),
            "--app-mirror-freshness",
            str(mirror),
            "--provider-snapshot",
            str(provider),
            "--hosted-bootstrap-preflight",
            str(hosted_valid),
            "--triad-artifact-dir",
            str(triad_dir),
            "--failure-ledger",
            str(ledger),
            "--json",
        )
        if freeze_after_valid_artifacts.returncode == 0:
            failures.append("staging_bootstrap passed even though forensic-freeze is active")
        if "forensic-freeze" not in f"{freeze_after_valid_artifacts.stdout}\n{freeze_after_valid_artifacts.stderr}":
            failures.append("valid staging_bootstrap artifacts did not reach the final forensic-freeze block")

        help_result = run_controller("--help")
        if help_result.returncode != 0:
            failures.append("release controller --help failed")
        if "--app-mirror-freshness" not in help_result.stdout:
            failures.append("release controller help does not expose --app-mirror-freshness")
        if "--hosted-bootstrap-preflight" not in help_result.stdout:
            failures.append("release controller help does not expose --hosted-bootstrap-preflight")

    return failures


def write_valid_mirror(path: Path, app_hash: str) -> None:
    path.write_text(
        json.dumps(
            {
                "ok": True,
                "source_commit": "a" * 40,
                "mirror_hash": app_hash,
                "provider_mutation_executed": False,
                "required_files": [
                    {
                        "path": "locally_twisted/staging_owner_review_preflight.py",
                        "source_exists": True,
                        "mirror_exists": True,
                        "matches": True,
                    },
                    {
                        "path": "locally_twisted/staging_owner_review_bootstrap.py",
                        "source_exists": True,
                        "mirror_exists": True,
                        "matches": True,
                    },
                ],
            }
        ),
        encoding="utf-8",
    )


def write_valid_provider(path: Path, site: str, app_hash: str) -> None:
    path.write_text(
        json.dumps(
            {
                "team": "team",
                "site": site,
                "bench_group": "bench-group",
                "bench": "bench",
                "installed_app_hash": app_hash,
                "target_app_hash": app_hash,
                "release_id": "none",
                "running_jobs": [],
                "app_order": ["frappe", "erpnext", "payments", "webshop", "locally_twisted"],
                "site_status": "Active",
                "rollback_hash": "c" * 40,
                "staging_live_separation": True,
            }
        ),
        encoding="utf-8",
    )


def write_hosted_preflight(path: Path, site: str, app_hash: str, *, ok: bool) -> None:
    failures = [] if ok else ["target_hash: mismatch"]
    preflight = valid_hosted_preflight_payload(site, app_hash)
    if not ok:
        preflight["ok"] = False
        preflight["failures"] = failures
        preflight["checks"]["target_hash"]["ok"] = False
        preflight["checks"]["target_hash"]["failures"] = failures
    path.write_text(
        json.dumps(
            {
                "ok": ok,
                "site": site,
                "method": (
                    "locally_twisted.staging_owner_review_bootstrap."
                    "preflight_staging_owner_review_bootstrap"
                ),
                "expected_app_hash": app_hash,
                "provider_mutation_executed": False,
                "preflight": preflight,
                "failures": failures,
            }
        ),
        encoding="utf-8",
    )


def valid_hosted_preflight_payload(site: str, app_hash: str) -> dict[str, object]:
    required_checks = [
        "standard_report",
        "roles",
        "settings",
        "app_hooks",
        "app_order",
        "target_hash",
        "baseline_counts",
        "destructive_seed_evidence",
    ]
    checks = {name: {"ok": True, "failures": []} for name in required_checks}
    checks["target_hash"] = {
        "ok": True,
        "expected_app_hash": app_hash,
        "current_app_hash": app_hash,
        "failures": [],
    }
    return {
        "ok": True,
        "target_site": site,
        "expected_app_hash": app_hash,
        "required_checks": required_checks,
        "checks": checks,
        "failures": [],
    }


def write_valid_triad(path: Path) -> None:
    path.mkdir()
    for filename in ("controller.md", "provider-witness.md", "gate-fixer.md", "recorder.md"):
        (path / filename).write_text(
            f"target: locallytwisted-staging.frappe.cloud\nstate: PASS\nevidence: {filename} proof\n",
            encoding="utf-8",
        )


def run_controller(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CONTROLLER), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=10,
    )


if __name__ == "__main__":
    sys.exit(main())
