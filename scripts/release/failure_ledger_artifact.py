#!/usr/bin/env python3
"""Draft, write, or validate the LT release failure-ledger artifact.

This helper is local/offline only. It does not approve release execution,
contact Frappe Cloud, sync the app mirror, deploy, bootstrap, migrate, cache
clear, index staging, unpause checkout, or touch live/DNS/Stripe/Search
Console. It only builds or validates `failure-ledger.json` for a future
artifact-bound staging packet.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from release_guard_common import (
    DEFAULT_LOCK_PATH,
    PROJECT_ROOT,
    REQUIRED_HOSTED_PREFLIGHT_SITE,
    ReleaseGuardError,
    current_git_head,
    load_release_lock,
    raise_if_failures,
    validate_failure_ledger,
    validate_release_lock,
)


DEFAULT_FAILURES = [
    {
        "failure_class": "typed_provider_payload_shape",
        "summary": "Frappe Cloud deploy/update request used stringified nested apps/sites JSON before typed payload validation existed.",
        "source_evidence": "workstreams/frappe-cloud-staging-release-failure-forensics-2026-05-23.md",
        "guard_written": True,
        "guard_path": "scripts/verify/frappe_cloud_payload_contract.py",
        "guard_command": "npm run test:frappe-cloud-payload",
    },
    {
        "failure_class": "portal_settings_migration_drift",
        "summary": "Hosted site update/migrate encountered Portal Settings default home drift that local state had not exposed.",
        "source_evidence": "workstreams/frappe-cloud-staging-release-failure-forensics-2026-05-23.md",
        "guard_written": True,
        "guard_path": "scripts/verify/staging_owner_review_bootstrap_contract.py",
        "guard_command": "npm run test:staging-owner-review-bootstrap-contract",
    },
    {
        "failure_class": "role_fixture_order_drift",
        "summary": "Permission sync referenced owner/manager roles before the roles were guaranteed on hosted staging.",
        "source_evidence": "capabilities/failures/frappe-cloud-permission-role-fixture-order-drift.md",
        "guard_written": True,
        "guard_path": "scripts/verify/staging_owner_review_bootstrap_contract.py",
        "guard_command": "npm run test:staging-owner-review-bootstrap-contract",
    },
    {
        "failure_class": "staging_bootstrap_report_developer_mode",
        "summary": "Hosted bootstrap hit standard Report developer-mode constraints before catalog mutation.",
        "source_evidence": "workstreams/frappe-cloud-staging-release-failure-forensics-2026-05-23.md",
        "guard_written": True,
        "guard_path": "scripts/verify/staging_owner_review_bootstrap_contract.py",
        "guard_command": "npm run test:staging-owner-review-bootstrap-contract",
    },
    {
        "failure_class": "stale_app_mirror_missing_hosted_preflight",
        "summary": "Frappe Cloud staging/app-root mirror lacked the hosted preflight source required before owner-review bootstrap.",
        "source_evidence": "workstreams/release-artifacts/2026-05-23-app-mirror-freshness-readonly/README.md",
        "guard_written": True,
        "guard_path": "scripts/verify/frappe_cloud_app_mirror_freshness.py",
        "guard_command": "npm run test:frappe-cloud-app-mirror-freshness",
    },
    {
        "failure_class": "artifact_json_bom_friction",
        "summary": "A PowerShell-written UTF-8 BOM read receipt blocked the controller before the intended missing-approval gate.",
        "source_evidence": "workstreams/frappe-cloud-release-json-artifact-bom-guard-2026-05-23.md",
        "guard_written": True,
        "guard_path": "scripts/verify/release_controller_contract.py",
        "guard_command": "npm run test:release-controller",
    },
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--lock-file", type=Path, default=DEFAULT_LOCK_PATH)
    parser.add_argument("--output", type=Path, help="Where to write failure-ledger.json when --write is used.")
    parser.add_argument("--write", action="store_true", help="Write a controller-consumable failure ledger after validation.")
    parser.add_argument("--force", action="store_true", help="Allow overwriting --output.")
    parser.add_argument("--agent", default="Codex", help="Agent/session name for the generated artifact.")
    parser.add_argument("--reviewed-source", action="store_true", help="Required with --write. Confirms current source and failure classes were reviewed.")
    parser.add_argument("--fresh-release-plan-approved", action="store_true", help="Only for real fresh release-plan approval evidence, not helper preview.")
    parser.add_argument("--fresh-release-plan-evidence", help="Required if --fresh-release-plan-approved is used.")
    parser.add_argument("--validate-only", type=Path, help="Validate an existing failure-ledger.json and exit.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable result.")
    args = parser.parse_args()

    try:
        result = run(args)
    except ReleaseGuardError as exc:
        result = {"ok": False, "failure": str(exc), "provider_mutation_executed": False}
    except Exception as exc:  # pragma: no cover - defensive CLI surface.
        result = {"ok": False, "failure": f"{type(exc).__name__}: {exc}", "provider_mutation_executed": False}

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("[FAILURE LEDGER ARTIFACT] " + ("PASS" if result.get("ok") else "BLOCK"))
        if result.get("output"):
            print(f"  output: {result['output']}")
        if result.get("failure"):
            print(f"  failure: {result['failure']}")
        if result.get("preview"):
            print(json.dumps(result["preview"], indent=2, sort_keys=True))
    return 0 if result.get("ok") else 1


def run(args: argparse.Namespace) -> dict[str, Any]:
    lock = load_release_lock(args.lock_file)
    raise_if_failures("invalid release lock", validate_release_lock(lock))

    if args.validate_only:
        return validate_existing(args.validate_only)

    source_commit = current_git_head()
    artifact = build_artifact(
        ok=args.write,
        agent=args.agent,
        lock=lock,
        source_commit=source_commit,
        fresh_release_plan_approved=args.fresh_release_plan_approved,
        fresh_release_plan_evidence=args.fresh_release_plan_evidence,
    )

    if args.write:
        if not args.output:
            raise ReleaseGuardError("--write requires --output")
        if args.output.name != "failure-ledger.json":
            raise ReleaseGuardError("--output filename must be failure-ledger.json")
        if not args.reviewed_source:
            raise ReleaseGuardError("--write requires --reviewed-source")
        output = normalize_release_artifact_output(args.output)
        if output.exists() and not args.force:
            raise ReleaseGuardError(f"refusing to overwrite existing failure ledger without --force: {output}")
        failures = validate_payload(artifact)
        raise_if_failures("generated failure ledger is invalid", failures)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return {
            "ok": True,
            "output": str(output),
            "source_commit": source_commit,
            "provider_mutation_executed": False,
        }

    artifact["preview_only"] = True
    artifact["controller_consumable"] = False
    return {
        "ok": False,
        "failure": "preview only; rerun with --write, --output, and --reviewed-source for a packet artifact",
        "preview": artifact,
        "provider_mutation_executed": False,
    }


def build_artifact(
    *,
    ok: bool,
    agent: str,
    lock: dict[str, Any],
    source_commit: str,
    fresh_release_plan_approved: bool,
    fresh_release_plan_evidence: str | None,
) -> dict[str, Any]:
    artifact: dict[str, Any] = {
        "ok": ok,
        "artifact_type": "failure_ledger",
        "agent": agent,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "lock_id": lock.get("id"),
        "source_commit": source_commit,
        "target_site": REQUIRED_HOSTED_PREFLIGHT_SITE,
        "provider_mutation_executed": False,
        "fresh_release_plan_approved": fresh_release_plan_approved,
        "failures": DEFAULT_FAILURES,
    }
    if fresh_release_plan_evidence:
        artifact["fresh_release_plan_evidence"] = fresh_release_plan_evidence
    return artifact


def normalize_release_artifact_output(output: Path) -> Path:
    resolved = output if output.is_absolute() else PROJECT_ROOT / output
    resolved = resolved.resolve()
    release_root = (PROJECT_ROOT / "workstreams" / "release-artifacts").resolve()
    try:
        resolved.relative_to(release_root)
    except ValueError as exc:
        raise ReleaseGuardError(f"output must be inside {release_root}") from exc
    return resolved


def validate_existing(path: Path) -> dict[str, Any]:
    failures = validate_failure_ledger(path)
    if failures:
        return {
            "ok": False,
            "path": str(path),
            "failures": failures,
            "failure": "; ".join(failures),
            "provider_mutation_executed": False,
        }
    return {"ok": True, "path": str(path), "provider_mutation_executed": False}


def validate_payload(artifact: dict[str, Any]) -> list[str]:
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "failure-ledger.json"
        path.write_text(json.dumps(artifact), encoding="utf-8")
        return validate_failure_ledger(path)


if __name__ == "__main__":
    sys.exit(main())
