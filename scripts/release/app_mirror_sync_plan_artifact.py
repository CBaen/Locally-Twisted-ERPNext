#!/usr/bin/env python3
"""Draft, write, or validate the LT app-mirror pre-sync plan artifact.

This helper is local/offline only. It does not push to the app-root mirror,
call Frappe Cloud, deploy, bootstrap, migrate, cache clear, or touch
live/DNS/Stripe/Search Console. It only builds or validates the
`app-mirror-sync-plan.json` file that the release controller requires before a
future approved `app_mirror_sync`.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from release_guard_common import (
    DEFAULT_LOCK_PATH,
    PROJECT_ROOT,
    REQUIRED_APP_MIRROR_SOURCE_FILES,
    REQUIRED_HOSTED_PREFLIGHT_SITE,
    ReleaseGuardError,
    current_git_head,
    is_full_hash,
    load_release_lock,
    normalize_hash,
    raise_if_failures,
    validate_app_mirror_sync_plan,
    validate_release_artifact_chain,
    validate_release_lock,
)


DEFAULT_APP_MIRROR = "https://github.com/CBaen/Locally-Twisted-Frappe-App.git"
DEFAULT_MIRROR_REF = "main"
POST_SYNC_REQUIRED = ["app-mirror-freshness.json"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--lock-file", type=Path, default=DEFAULT_LOCK_PATH)
    parser.add_argument("--output", type=Path, help="Where to write app-mirror-sync-plan.json when --write is used.")
    parser.add_argument("--write", action="store_true", help="Write a controller-consumable pre-sync plan after validation.")
    parser.add_argument("--force", action="store_true", help="Allow overwriting --output.")
    parser.add_argument("--rollback-hash", help="Required with --write. Current deployed/staging rollback hash.")
    parser.add_argument("--mirror-url", default=DEFAULT_APP_MIRROR)
    parser.add_argument("--mirror-ref", default=DEFAULT_MIRROR_REF)
    parser.add_argument("--agent", default="Codex", help="Agent/session name for the generated artifact.")
    parser.add_argument("--reviewed-source", action="store_true", help="Required with --write. Confirms current source was reviewed.")
    parser.add_argument("--validate-only", type=Path, help="Validate an existing app-mirror-sync-plan.json and exit.")
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
        print("[APP MIRROR SYNC PLAN ARTIFACT] " + ("PASS" if result.get("ok") else "BLOCK"))
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

    rollback_hash = normalize_rollback_hash(args.rollback_hash)
    source_commit = current_git_head()
    mirror_url = canonical_mirror_url(args.mirror_url)
    mirror_ref = canonical_mirror_ref(args.mirror_ref)

    if args.write:
        if not args.output:
            raise ReleaseGuardError("--write requires --output")
        if args.output.name != "app-mirror-sync-plan.json":
            raise ReleaseGuardError("--output filename must be app-mirror-sync-plan.json")
        output = normalize_release_artifact_output(args.output)
        if not args.reviewed_source:
            raise ReleaseGuardError("--write requires --reviewed-source")
        if output.exists() and not args.force:
            raise ReleaseGuardError(f"refusing to overwrite existing app mirror sync plan without --force: {output}")
        assert_release_files_clean()

        artifact = build_artifact(
            ok=True,
            source_commit=source_commit,
            rollback_hash=rollback_hash,
            mirror_url=mirror_url,
            mirror_ref=mirror_ref,
            agent=args.agent,
        )
        failures = validate_payload(artifact)
        raise_if_failures("generated app mirror sync plan is invalid", failures)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return {
            "ok": True,
            "output": str(output),
            "source_commit": source_commit,
            "rollback_hash": rollback_hash,
            "provider_mutation_executed": False,
            "app_mirror_sync_executed": False,
        }

    preview = build_artifact(
        ok=False,
        source_commit=source_commit,
        rollback_hash=rollback_hash,
        mirror_url=mirror_url,
        mirror_ref=mirror_ref,
        agent=args.agent,
    )
    preview["preview_only"] = True
    return {
        "ok": False,
        "failure": "preview only; rerun with --write, --output, --rollback-hash, and --reviewed-source after explicit approval",
        "preview": preview,
        "provider_mutation_executed": False,
        "app_mirror_sync_executed": False,
    }


def normalize_rollback_hash(value: str | None) -> str:
    rollback_hash = normalize_hash(value)
    if not is_full_hash(rollback_hash):
        raise ReleaseGuardError("rollback hash must be a full 40-character hex hash")
    return rollback_hash


def canonical_mirror_url(value: str) -> str:
    mirror_url = str(value or "").strip()
    if mirror_url != DEFAULT_APP_MIRROR:
        raise ReleaseGuardError(f"mirror URL must be exactly {DEFAULT_APP_MIRROR}")
    return mirror_url


def canonical_mirror_ref(value: str) -> str:
    mirror_ref = str(value or "").strip()
    if mirror_ref != DEFAULT_MIRROR_REF:
        raise ReleaseGuardError(f"mirror ref must be exactly {DEFAULT_MIRROR_REF}")
    return mirror_ref


def normalize_release_artifact_output(output: Path) -> Path:
    resolved = output if output.is_absolute() else PROJECT_ROOT / output
    resolved = resolved.resolve()
    release_root = (PROJECT_ROOT / "workstreams" / "release-artifacts").resolve()
    try:
        resolved.relative_to(release_root)
    except ValueError as exc:
        raise ReleaseGuardError(f"output must be inside {release_root}") from exc
    return resolved


def build_artifact(
    *,
    ok: bool,
    source_commit: str,
    rollback_hash: str,
    mirror_url: str,
    mirror_ref: str,
    agent: str,
) -> dict[str, Any]:
    return {
        "ok": ok,
        "artifact_type": "app_mirror_sync_plan",
        "agent": agent,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_commit": source_commit,
        "mirror_url": mirror_url,
        "mirror_ref": mirror_ref,
        "target_site": REQUIRED_HOSTED_PREFLIGHT_SITE,
        "rollback_hash": rollback_hash,
        "required_files": sorted(REQUIRED_APP_MIRROR_SOURCE_FILES),
        "post_sync_required": POST_SYNC_REQUIRED,
        "no_provider_deploy_until_post_sync_freshness": True,
        "reviewed_source": True,
        "provider_mutation_executed": False,
        "app_mirror_sync_executed": False,
    }


def validate_existing(path: Path) -> dict[str, Any]:
    failures = validate_plan_path(path)
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
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "app-mirror-sync-plan.json"
        path.write_text(json.dumps(artifact), encoding="utf-8")
        return validate_plan_path(path)


def validate_plan_path(path: Path) -> list[str]:
    failures: list[str] = []
    failures.extend(validate_app_mirror_sync_plan(path))
    failures.extend(validate_release_artifact_chain(action="app_mirror_sync", app_mirror_sync_plan_path=path))
    return sorted(set(failures))


def assert_release_files_clean() -> None:
    app_paths = [f"apps/locally_twisted/{path}" for path in sorted(REQUIRED_APP_MIRROR_SOURCE_FILES)]
    guard_paths = [
        "scripts/release/app_mirror_sync_plan_artifact.py",
        "scripts/verify/app_mirror_sync_plan_artifact_contract.py",
        "scripts/release/frappe_cloud_release_controller.py",
        "scripts/release/release_guard_common.py",
        "scripts/verify/release_controller_contract.py",
        "scripts/verify/release_lock_contract.py",
        "release_locks/locally-twisted-staging-forensic-freeze.json",
        "package.json",
    ]
    tracked_paths = sorted(set(app_paths + guard_paths))
    for rel in app_paths:
        if not (PROJECT_ROOT / rel).exists():
            raise ReleaseGuardError(f"required source file is missing: {rel}")
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "--", *tracked_paths],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        timeout=10,
    )
    if result.returncode != 0:
        raise ReleaseGuardError(result.stderr.strip() or "could not check release file cleanliness")
    if result.stdout.strip():
        raise ReleaseGuardError(
            "release source and guard files must be clean before writing app mirror sync plan; git status: "
            + result.stdout.strip().replace("\n", "; ")
        )


if __name__ == "__main__":
    sys.exit(main())
