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
from datetime import datetime, timedelta, timezone
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
    validate_app_mirror_sync_plan,
    validate_app_mirror_freshness,
    validate_hosted_bootstrap_preflight,
    validate_read_receipt,
    validate_reopen_approval,
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
        approved_at, expires_at = approval_window()
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

        valid_reopen = tmp_path / "freeze-reopen-approval.json"
        valid_reopen.write_text(
            json.dumps(
                {
                    "ok": True,
                    "approval_type": "forensic_freeze_reopen",
                    "lock_id": lock.get("id"),
                    "approved_by": "Guiding Light",
                    "approved_at": approved_at,
                    "expires_at": expires_at,
                    "target_site": "locallytwisted-staging.frappe.cloud",
                    "source_commit": "a" * 40,
                    "approved_actions": ["app_mirror_sync", "frappe_cloud_deploy", "staging_bootstrap"],
                    "live_dns_stripe_search_console_blocked": True,
                    "provider_mutation_executed": False,
                }
            ),
            encoding="utf-8",
        )
        failures.extend(validate_reopen_approval(valid_reopen, lock, action="app_mirror_sync"))

        live_reopen = tmp_path / "bad-live-reopen-approval.json"
        live_reopen.write_text(
            json.dumps(
                {
                    "ok": True,
                    "approval_type": "forensic_freeze_reopen",
                    "lock_id": lock.get("id"),
                    "approved_by": "Guiding Light",
                    "approved_at": approved_at,
                    "expires_at": expires_at,
                    "target_site": "locallytwisted-staging.frappe.cloud",
                    "source_commit": "a" * 40,
                    "approved_actions": ["app_mirror_sync", "live_release"],
                    "live_dns_stripe_search_console_blocked": True,
                    "provider_mutation_executed": False,
                }
            ),
            encoding="utf-8",
        )
        if not validate_reopen_approval(live_reopen, lock, action="live_release"):
            failures.append("freeze reopen approval that included live_release did not fail")

        expired_reopen = tmp_path / "expired-freeze-reopen-approval.json"
        expired_reopen.write_text(
            json.dumps(
                {
                    "ok": True,
                    "approval_type": "forensic_freeze_reopen",
                    "lock_id": lock.get("id"),
                    "approved_by": "Guiding Light",
                    "approved_at": (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat(),
                    "expires_at": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                    "target_site": "locallytwisted-staging.frappe.cloud",
                    "source_commit": "a" * 40,
                    "approved_actions": ["app_mirror_sync"],
                    "live_dns_stripe_search_console_blocked": True,
                    "provider_mutation_executed": False,
                }
            ),
            encoding="utf-8",
        )
        if not validate_reopen_approval(expired_reopen, lock, action="app_mirror_sync"):
            failures.append("expired freeze reopen approval did not fail")

        malformed_reopen = tmp_path / "malformed-freeze-reopen-approval.json"
        malformed_reopen.write_text(
            json.dumps(
                {
                    "ok": True,
                    "approval_type": "forensic_freeze_reopen",
                    "lock_id": lock.get("id"),
                    "approved_by": "Guiding Light",
                    "approved_at": "not-a-date",
                    "expires_at": expires_at,
                    "target_site": "locallytwisted-staging.frappe.cloud",
                    "source_commit": "a" * 40,
                    "approved_actions": ["app_mirror_sync"],
                    "live_dns_stripe_search_console_blocked": True,
                    "provider_mutation_executed": False,
                }
            ),
            encoding="utf-8",
        )
        if not validate_reopen_approval(malformed_reopen, lock, action="app_mirror_sync"):
            failures.append("malformed freeze reopen approval timestamp did not fail")

        timezone_less_reopen = tmp_path / "timezone-less-freeze-reopen-approval.json"
        timezone_less_reopen.write_text(
            json.dumps(
                {
                    "ok": True,
                    "approval_type": "forensic_freeze_reopen",
                    "lock_id": lock.get("id"),
                    "approved_by": "Guiding Light",
                    "approved_at": "2026-05-23T12:00:00",
                    "expires_at": "2026-05-23T13:00:00",
                    "target_site": "locallytwisted-staging.frappe.cloud",
                    "source_commit": "a" * 40,
                    "approved_actions": ["app_mirror_sync"],
                    "live_dns_stripe_search_console_blocked": True,
                    "provider_mutation_executed": False,
                }
            ),
            encoding="utf-8",
        )
        if not validate_reopen_approval(timezone_less_reopen, lock, action="app_mirror_sync"):
            failures.append("timezone-less freeze reopen approval timestamp did not fail")

        future_reopen = tmp_path / "future-freeze-reopen-approval.json"
        future_reopen.write_text(
            json.dumps(
                {
                    "ok": True,
                    "approval_type": "forensic_freeze_reopen",
                    "lock_id": lock.get("id"),
                    "approved_by": "Guiding Light",
                    "approved_at": (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat(),
                    "expires_at": (datetime.now(timezone.utc) + timedelta(hours=3)).isoformat(),
                    "target_site": "locallytwisted-staging.frappe.cloud",
                    "source_commit": "a" * 40,
                    "approved_actions": ["app_mirror_sync"],
                    "live_dns_stripe_search_console_blocked": True,
                    "provider_mutation_executed": False,
                }
            ),
            encoding="utf-8",
        )
        if not validate_reopen_approval(future_reopen, lock, action="app_mirror_sync"):
            failures.append("future-dated freeze reopen approval did not fail")

        long_reopen = tmp_path / "long-freeze-reopen-approval.json"
        long_reopen.write_text(
            json.dumps(
                {
                    "ok": True,
                    "approval_type": "forensic_freeze_reopen",
                    "lock_id": lock.get("id"),
                    "approved_by": "Guiding Light",
                    "approved_at": approved_at,
                    "expires_at": (datetime.now(timezone.utc) + timedelta(days=3)).isoformat(),
                    "target_site": "locallytwisted-staging.frappe.cloud",
                    "source_commit": "a" * 40,
                    "approved_actions": ["app_mirror_sync"],
                    "live_dns_stripe_search_console_blocked": True,
                    "provider_mutation_executed": False,
                }
            ),
            encoding="utf-8",
        )
        if not validate_reopen_approval(long_reopen, lock, action="app_mirror_sync"):
            failures.append("overlong freeze reopen approval did not fail")

        valid_sync_plan = tmp_path / "app-mirror-sync-plan.json"
        valid_sync_plan.write_text(
            json.dumps(
                {
                    "ok": True,
                    "source_commit": "a" * 40,
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
        failures.extend(validate_app_mirror_sync_plan(valid_sync_plan))

        bad_sync_plan = tmp_path / "bad-app-mirror-sync-plan.json"
        bad_sync_plan.write_text(
            json.dumps(
                {
                    "ok": True,
                    "source_commit": "a" * 40,
                    "mirror_url": "https://github.com/CBaen/Locally-Twisted-Frappe-App.git",
                    "mirror_ref": "main",
                    "target_site": "locallytwisted-staging.frappe.cloud",
                    "rollback_hash": "c" * 40,
                    "reviewed_source": True,
                    "required_files": ["locally_twisted/staging_owner_review_preflight.py"],
                    "post_sync_required": [],
                    "no_provider_deploy_until_post_sync_freshness": False,
                    "provider_mutation_executed": False,
                }
            ),
            encoding="utf-8",
        )
        if not validate_app_mirror_sync_plan(bad_sync_plan):
            failures.append("incomplete app mirror sync plan did not fail")

        valid_mirror = tmp_path / "app-mirror-freshness.json"
        valid_mirror.write_text(
            json.dumps(
                {
                    "ok": True,
                    "source_commit": "a" * 40,
                    "mirror_hash": "b" * 40,
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
        failures.extend(validate_app_mirror_freshness(valid_mirror))

        partial_mirror = tmp_path / "partial-app-mirror-freshness.json"
        partial_mirror.write_text(
            json.dumps(
                {
                    "ok": True,
                    "source_commit": "a" * 40,
                    "mirror_hash": "b" * 40,
                    "provider_mutation_executed": False,
                    "required_files": [
                        {
                            "path": "locally_twisted/staging_owner_review_preflight.py",
                            "source_exists": True,
                            "mirror_exists": True,
                            "matches": True,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        if not validate_app_mirror_freshness(partial_mirror):
            failures.append("partial app mirror freshness artifact missing bootstrap did not fail")

        stale_mirror = tmp_path / "stale-app-mirror-freshness.json"
        stale_mirror.write_text(
            json.dumps(
                {
                    "ok": False,
                    "source_commit": "a" * 40,
                    "mirror_hash": "b" * 40,
                    "provider_mutation_executed": False,
                    "required_files": [
                        {
                            "path": "locally_twisted/staging_owner_review_preflight.py",
                            "source_exists": True,
                            "mirror_exists": False,
                            "matches": False,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        if not validate_app_mirror_freshness(stale_mirror):
            failures.append("stale app mirror freshness artifact did not fail")

        valid_provider_snapshot = tmp_path / "provider-snapshot.json"
        valid_provider_snapshot.write_text(
            json.dumps(
                {
                    "team": "team",
                    "site": "locallytwisted-staging.frappe.cloud",
                    "bench_group": "bench-group",
                    "bench": "bench",
                    "installed_app_hash": "b" * 40,
                    "target_app_hash": "b" * 40,
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

        valid_hosted_preflight = tmp_path / "hosted-bootstrap-preflight.json"
        valid_hosted_preflight.write_text(
            json.dumps(
                {
                    "ok": True,
                    "site": "locallytwisted-staging.frappe.cloud",
                    "method": (
                        "locally_twisted.staging_owner_review_bootstrap."
                        "preflight_staging_owner_review_bootstrap"
                    ),
                    "expected_app_hash": "b" * 40,
                    "provider_mutation_executed": False,
                    "preflight": valid_hosted_preflight_payload(
                        "locallytwisted-staging.frappe.cloud",
                        "b" * 40,
                    ),
                }
            ),
            encoding="utf-8",
        )
        failures.extend(
            validate_hosted_bootstrap_preflight(
                valid_hosted_preflight,
                provider_snapshot_path=valid_provider_snapshot,
                app_mirror_freshness_path=valid_mirror,
            )
        )

        wrong_site_hosted_preflight = tmp_path / "wrong-site-hosted-bootstrap-preflight.json"
        wrong_site_hosted_preflight.write_text(
            json.dumps(
                {
                    "ok": True,
                    "site": "wrong-staging.frappe.cloud",
                    "method": (
                        "locally_twisted.staging_owner_review_bootstrap."
                        "preflight_staging_owner_review_bootstrap"
                    ),
                    "expected_app_hash": "b" * 40,
                    "provider_mutation_executed": False,
                    "preflight": valid_hosted_preflight_payload(
                        "wrong-staging.frappe.cloud",
                        "b" * 40,
                    ),
                }
            ),
            encoding="utf-8",
        )
        if not validate_hosted_bootstrap_preflight(
            wrong_site_hosted_preflight,
            provider_snapshot_path=valid_provider_snapshot,
            app_mirror_freshness_path=valid_mirror,
        ):
            failures.append("wrong-site hosted bootstrap preflight artifact did not fail chain validation")

        wrong_hash_hosted_preflight = tmp_path / "wrong-hash-hosted-bootstrap-preflight.json"
        wrong_hash_hosted_preflight.write_text(
            json.dumps(
                {
                    "ok": True,
                    "site": "locallytwisted-staging.frappe.cloud",
                    "method": (
                        "locally_twisted.staging_owner_review_bootstrap."
                        "preflight_staging_owner_review_bootstrap"
                    ),
                    "expected_app_hash": "d" * 40,
                    "provider_mutation_executed": False,
                    "preflight": valid_hosted_preflight_payload(
                        "locallytwisted-staging.frappe.cloud",
                        "d" * 40,
                    ),
                }
            ),
            encoding="utf-8",
        )
        if not validate_hosted_bootstrap_preflight(
            wrong_hash_hosted_preflight,
            provider_snapshot_path=valid_provider_snapshot,
            app_mirror_freshness_path=valid_mirror,
        ):
            failures.append("wrong-hash hosted bootstrap preflight artifact did not fail chain validation")

        stale_hosted_preflight = tmp_path / "stale-hosted-bootstrap-preflight.json"
        stale_hosted_preflight.write_text(
            json.dumps(
                {
                    "ok": False,
                    "site": "locallytwisted-staging.frappe.cloud",
                    "method": (
                        "locally_twisted.staging_owner_review_bootstrap."
                        "preflight_staging_owner_review_bootstrap"
                    ),
                    "expected_app_hash": "a" * 40,
                    "provider_mutation_executed": False,
                    "preflight": {"ok": False, "failures": ["target_hash: mismatch"]},
                }
            ),
            encoding="utf-8",
        )
        if not validate_hosted_bootstrap_preflight(stale_hosted_preflight):
            failures.append("stale hosted bootstrap preflight artifact did not fail")

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


def approval_window() -> tuple[str, str]:
    approved_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    expires_at = approved_at + timedelta(hours=12)
    return approved_at.isoformat(), expires_at.isoformat()


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


if __name__ == "__main__":
    sys.exit(main())
