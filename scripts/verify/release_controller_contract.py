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
from datetime import datetime, timedelta, timezone
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
    source_commit = current_source_commit()

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
        write_payload(payload, "b" * 40)

        deploy_missing_reopen = run_controller(
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
        if deploy_missing_reopen.returncode == 0:
            failures.append("frappe_cloud_deploy passed without freeze reopen approval")
        if "freeze reopen approval" not in f"{deploy_missing_reopen.stdout}\n{deploy_missing_reopen.stderr}".lower():
            failures.append("deploy missing-reopen output did not mention freeze reopen approval")
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

        approval = tmp_path / "freeze-reopen-approval.json"
        mirror = tmp_path / "app-mirror-freshness.json"
        sync_plan = tmp_path / "app-mirror-sync-plan.json"
        provider = tmp_path / "provider-snapshot.json"
        hosted_valid = tmp_path / "hosted-bootstrap-preflight-valid.json"
        hosted_no_go = tmp_path / "hosted-bootstrap-preflight-no-go.json"
        hosted_wrong_site = tmp_path / "hosted-bootstrap-preflight-wrong-site.json"
        hosted_wrong_hash = tmp_path / "hosted-bootstrap-preflight-wrong-hash.json"
        deploy_completion = tmp_path / "deploy-completion.json"
        triad_dir = tmp_path / "triad"
        ledger = tmp_path / "failure-ledger.json"
        write_reopen_approval(approval, source_commit)
        write_valid_mirror(mirror, source_commit, "b" * 40)
        write_valid_sync_plan(sync_plan, source_commit)
        write_valid_provider(provider, "locallytwisted-staging.frappe.cloud", "b" * 40)
        write_valid_deploy_completion(deploy_completion, "locallytwisted-staging.frappe.cloud", "b" * 40)
        write_hosted_preflight(hosted_valid, "locallytwisted-staging.frappe.cloud", "b" * 40, ok=True)
        write_hosted_preflight(hosted_no_go, "locallytwisted-staging.frappe.cloud", "b" * 40, ok=False)
        write_hosted_preflight(hosted_wrong_site, "wrong-staging.frappe.cloud", "b" * 40, ok=True)
        write_hosted_preflight(hosted_wrong_hash, "locallytwisted-staging.frappe.cloud", "d" * 40, ok=True)
        write_valid_triad(triad_dir)
        ledger.write_text(json.dumps({"fresh_release_plan_approved": True, "failures": []}), encoding="utf-8")

        deploy_missing_mirror = run_controller(
            "--action",
            "frappe_cloud_deploy",
            "--payload-file",
            str(payload),
            "--read-receipt",
            str(receipt),
            "--reopen-approval",
            str(approval),
            "--json",
        )
        if deploy_missing_mirror.returncode == 0:
            failures.append("frappe_cloud_deploy passed without app mirror freshness proof")
        if "app mirror freshness" not in f"{deploy_missing_mirror.stdout}\n{deploy_missing_mirror.stderr}".lower():
            failures.append("deploy missing-mirror output did not mention app mirror freshness")

        missing_bootstrap_reopen = run_controller(
            "--action",
            "staging_bootstrap",
            "--read-receipt",
            str(receipt),
            "--json",
        )
        if missing_bootstrap_reopen.returncode == 0:
            failures.append("staging_bootstrap passed without freeze reopen approval")
        if "freeze reopen approval" not in f"{missing_bootstrap_reopen.stdout}\n{missing_bootstrap_reopen.stderr}".lower():
            failures.append("missing staging_bootstrap reopen output did not mention freeze reopen approval")

        missing_mirror = run_controller(
            "--action",
            "staging_bootstrap",
            "--read-receipt",
            str(receipt),
            "--reopen-approval",
            str(approval),
            "--json",
        )
        if missing_mirror.returncode == 0:
            failures.append("staging_bootstrap passed without app mirror freshness artifact")
        if "app mirror freshness" not in f"{missing_mirror.stdout}\n{missing_mirror.stderr}".lower():
            failures.append("missing staging_bootstrap mirror output did not mention app mirror freshness")

        sync_missing_plan = run_controller(
            "--action",
            "app_mirror_sync",
            "--read-receipt",
            str(receipt),
            "--reopen-approval",
            str(approval),
            "--json",
        )
        if sync_missing_plan.returncode == 0:
            failures.append("app_mirror_sync passed without app mirror sync plan")
        if "sync plan" not in f"{sync_missing_plan.stdout}\n{sync_missing_plan.stderr}".lower():
            failures.append("app_mirror_sync missing-plan output did not mention sync plan")

        sync_with_plan_without_freshness = run_controller(
            "--action",
            "app_mirror_sync",
            "--read-receipt",
            str(receipt),
            "--reopen-approval",
            str(approval),
            "--app-mirror-sync-plan",
            str(sync_plan),
            "--provider-snapshot",
            str(provider),
            "--triad-artifact-dir",
            str(triad_dir),
            "--failure-ledger",
            str(ledger),
            "--json",
        )
        if sync_with_plan_without_freshness.returncode != 0:
            failures.append("app_mirror_sync with valid pre-sync plan was still deadlocked on freshness")

        stale_sync_plan = tmp_path / "stale-app-mirror-sync-plan.json"
        write_valid_sync_plan(stale_sync_plan, "d" * 40)
        sync_with_stale_plan = run_controller(
            "--action",
            "app_mirror_sync",
            "--read-receipt",
            str(receipt),
            "--reopen-approval",
            str(approval),
            "--app-mirror-sync-plan",
            str(stale_sync_plan),
            "--provider-snapshot",
            str(provider),
            "--triad-artifact-dir",
            str(triad_dir),
            "--failure-ledger",
            str(ledger),
            "--json",
        )
        if sync_with_stale_plan.returncode == 0:
            failures.append("app_mirror_sync passed with a stale source_commit in the sync plan")
        if "artifact chain" not in f"{sync_with_stale_plan.stdout}\n{sync_with_stale_plan.stderr}".lower():
            failures.append("stale sync-plan failure did not mention artifact chain consistency")

        mismatched_payload = tmp_path / "mismatched-sanitized-payload.json"
        write_payload(mismatched_payload, "d" * 40)
        deploy_with_mismatched_payload = run_controller(
            "--action",
            "frappe_cloud_deploy",
            "--payload-file",
            str(mismatched_payload),
            "--read-receipt",
            str(receipt),
            "--reopen-approval",
            str(approval),
            "--app-mirror-freshness",
            str(mirror),
            "--provider-snapshot",
            str(provider),
            "--triad-artifact-dir",
            str(triad_dir),
            "--failure-ledger",
            str(ledger),
            "--json",
        )
        if deploy_with_mismatched_payload.returncode == 0:
            failures.append("frappe_cloud_deploy passed with a payload hash that did not match mirror/provider artifacts")
        if "payload locally_twisted app hash" not in f"{deploy_with_mismatched_payload.stdout}\n{deploy_with_mismatched_payload.stderr}".lower():
            failures.append("mismatched deploy payload failure did not mention payload hash binding")

        deploy_with_valid_chain = run_controller(
            "--action",
            "frappe_cloud_deploy",
            "--payload-file",
            str(payload),
            "--read-receipt",
            str(receipt),
            "--reopen-approval",
            str(approval),
            "--app-mirror-freshness",
            str(mirror),
            "--provider-snapshot",
            str(provider),
            "--triad-artifact-dir",
            str(triad_dir),
            "--failure-ledger",
            str(ledger),
            "--json",
        )
        if deploy_with_valid_chain.returncode != 0:
            failures.append("frappe_cloud_deploy with a valid payload/provider/mirror chain did not pass the local controller gate")

        missing_deploy_completion = run_controller(
            "--action",
            "staging_bootstrap",
            "--read-receipt",
            str(receipt),
            "--reopen-approval",
            str(approval),
            "--app-mirror-freshness",
            str(mirror),
            "--provider-snapshot",
            str(provider),
            "--json",
        )
        if missing_deploy_completion.returncode == 0:
            failures.append("staging_bootstrap passed without deploy completion artifact")
        if "deploy" not in f"{missing_deploy_completion.stdout}\n{missing_deploy_completion.stderr}".lower():
            failures.append("missing deploy completion output did not mention deploy completion")

        missing_hosted = run_controller(
            "--action",
            "staging_bootstrap",
            "--read-receipt",
            str(receipt),
            "--reopen-approval",
            str(approval),
            "--app-mirror-freshness",
            str(mirror),
            "--provider-snapshot",
            str(provider),
            "--deploy-completion",
            str(deploy_completion),
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
                "--reopen-approval",
                str(approval),
                "--app-mirror-freshness",
                str(mirror),
                "--provider-snapshot",
                str(provider),
                "--deploy-completion",
                str(deploy_completion),
                "--hosted-bootstrap-preflight",
                str(artifact),
                "--json",
            )
            if invalid_hosted.returncode == 0:
                failures.append(f"staging_bootstrap passed with {label} hosted preflight artifact")
            combined = f"{invalid_hosted.stdout}\n{invalid_hosted.stderr}".lower()
            if "hosted bootstrap preflight" not in combined:
                failures.append(f"{label} hosted preflight failure did not mention hosted bootstrap preflight")

        valid_artifacts_without_reopen = run_controller(
            "--action",
            "staging_bootstrap",
            "--read-receipt",
            str(receipt),
            "--app-mirror-freshness",
            str(mirror),
            "--provider-snapshot",
            str(provider),
            "--deploy-completion",
            str(deploy_completion),
            "--hosted-bootstrap-preflight",
            str(hosted_valid),
            "--triad-artifact-dir",
            str(triad_dir),
            "--failure-ledger",
            str(ledger),
            "--json",
        )
        if valid_artifacts_without_reopen.returncode == 0:
            failures.append("staging_bootstrap passed without freeze reopen approval")
        if "freeze reopen approval" not in f"{valid_artifacts_without_reopen.stdout}\n{valid_artifacts_without_reopen.stderr}".lower():
            failures.append("valid staging_bootstrap artifacts without approval did not fail on freeze reopen approval")

        valid_artifacts_with_reopen = run_controller(
            "--action",
            "staging_bootstrap",
            "--read-receipt",
            str(receipt),
            "--reopen-approval",
            str(approval),
            "--app-mirror-freshness",
            str(mirror),
            "--provider-snapshot",
            str(provider),
            "--deploy-completion",
            str(deploy_completion),
            "--hosted-bootstrap-preflight",
            str(hosted_valid),
            "--triad-artifact-dir",
            str(triad_dir),
            "--failure-ledger",
            str(ledger),
            "--json",
        )
        if valid_artifacts_with_reopen.returncode != 0:
            failures.append("staging_bootstrap with valid reopen approval and artifacts did not pass the local controller gate")

        help_result = run_controller("--help")
        if help_result.returncode != 0:
            failures.append("release controller --help failed")
        if "--app-mirror-freshness" not in help_result.stdout:
            failures.append("release controller help does not expose --app-mirror-freshness")
        if "--hosted-bootstrap-preflight" not in help_result.stdout:
            failures.append("release controller help does not expose --hosted-bootstrap-preflight")
        if "--deploy-completion" not in help_result.stdout:
            failures.append("release controller help does not expose --deploy-completion")
        if "--reopen-approval" not in help_result.stdout:
            failures.append("release controller help does not expose --reopen-approval")
        if "--app-mirror-sync-plan" not in help_result.stdout:
            failures.append("release controller help does not expose --app-mirror-sync-plan")

    return failures


def current_source_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=10,
        check=True,
    )
    return result.stdout.strip().lower()


def write_payload(path: Path, app_hash: str) -> None:
    path.write_text(
        json.dumps(
            {
                "content_type": "application/json",
                "body": {
                    "apps": [
                        {
                            "app": "locally_twisted",
                            "repository": "https://github.com/CBaen/Locally-Twisted-Frappe-App.git",
                            "hash": app_hash,
                        }
                    ],
                    "sites": [{"name": "locallytwisted-staging.frappe.cloud"}],
                },
            }
        ),
        encoding="utf-8",
    )


def write_reopen_approval(path: Path, source_commit: str) -> None:
    approved_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    expires_at = approved_at + timedelta(hours=12)
    path.write_text(
        json.dumps(
            {
                "ok": True,
                "approval_type": "forensic_freeze_reopen",
                "lock_id": "lt-staging-forensic-freeze-2026-05-23",
                "approved_by": "Guiding Light",
                "approval_evidence": "release-controller-contract explicit approval placeholder",
                "approved_at": approved_at.isoformat(),
                "expires_at": expires_at.isoformat(),
                "target_site": "locallytwisted-staging.frappe.cloud",
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
        ),
        encoding="utf-8",
    )


def write_valid_mirror(path: Path, source_commit: str, app_hash: str) -> None:
    path.write_text(
        json.dumps(
            {
                "ok": True,
                "source_commit": source_commit,
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


def write_valid_sync_plan(path: Path, source_commit: str) -> None:
    path.write_text(
        json.dumps(
            {
                "ok": True,
                "source_commit": source_commit,
                "mirror_url": "https://github.com/CBaen/Locally-Twisted-Frappe-App.git",
                "mirror_ref": "main",
                "target_site": "locallytwisted-staging.frappe.cloud",
                "rollback_hash": "c" * 40,
                "reviewed_source": True,
                "required_files": [
                    "locally_twisted/staging_owner_review_preflight.py",
                    "locally_twisted/staging_owner_review_bootstrap.py",
                ],
                "post_sync_required": ["app-mirror-freshness.json"],
                "no_provider_deploy_until_post_sync_freshness": True,
                "provider_mutation_executed": False,
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


def write_valid_deploy_completion(path: Path, site: str, app_hash: str) -> None:
    path.write_text(
        json.dumps(
            {
                "ok": True,
                "site": site,
                "action": "frappe_cloud_deploy",
                "expected_app_hash": app_hash,
                "target_app_hash": app_hash,
                "installed_app_hash": app_hash,
                "provider_job": {"name": "deploy-job-1", "status": "Success"},
                "running_jobs": [],
                "app_order": ["frappe", "erpnext", "payments", "webshop", "locally_twisted"],
                "site_status": "Active",
                "site_config": {
                    "lt_ecommerce_paused": "1",
                    "lt_public_indexing_enabled": "0",
                },
                "provider_mutation_executed": True,
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
