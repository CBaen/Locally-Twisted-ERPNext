#!/usr/bin/env python3
"""Create or self-test the sanitized Frappe Cloud provider snapshot artifact.

The real snapshot mode calls only read-only Frappe Cloud/Press API methods and
writes the `provider-snapshot.json` artifact required before future mutation.
Self-test mode is offline and safe for normal release-prevention checks.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "release"))
sys.path.insert(0, str(ROOT / "scripts" / "verify"))

from release_guard_common import EXPECTED_APP_ORDER, validate_provider_snapshot  # noqa: E402
from staging_owner_review_gate import (  # noqa: E402
    DEFAULT_APP_MIRROR,
    DEFAULT_CREDENTIALS,
    DEFAULT_SITE,
    DEFAULT_TEAM,
    PressClient,
    normalize_expected_hash,
)


READ_ONLY_METHODS = (
    "press.api.site.get",
    "press.api.site.installed_apps",
    "press.api.site.site_config",
    "press.api.site.running_jobs",
    "press.api.site.jobs",
    "press.api.bench.deploy_information",
    "press.api.bench.deploy_status",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", default=os.environ.get("LT_STAGING_SITE", DEFAULT_SITE))
    parser.add_argument("--team", default=os.environ.get("LT_FC_TEAM", DEFAULT_TEAM))
    parser.add_argument(
        "--credentials",
        type=Path,
        default=Path(os.environ.get("LT_FC_CREDENTIALS", str(DEFAULT_CREDENTIALS))),
    )
    parser.add_argument("--target-app-hash", default=os.environ.get("LT_TARGET_APP_HASH"))
    parser.add_argument("--target-app-hash-from-mirror", action="store_true")
    parser.add_argument("--mirror-url", default=DEFAULT_APP_MIRROR)
    parser.add_argument("--rollback-hash", default=os.environ.get("LT_ROLLBACK_HASH"))
    parser.add_argument("--output", type=Path, help="Write provider-snapshot.json to this path.")
    parser.add_argument("--self-test", action="store_true", help="Run offline validation checks.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable result.")
    args = parser.parse_args()

    try:
        if args.self_test:
            result = run_self_test()
        else:
            if args.target_app_hash_from_mirror:
                args.target_app_hash = resolve_mirror_head(args.mirror_url)
            snapshot = build_snapshot(args)
            output = write_snapshot(args.output, snapshot) if args.output else None
            failures = validate_snapshot_object(snapshot)
            result = {"ok": not failures, "failures": failures, "snapshot": snapshot, "output": str(output) if output else None}
    except Exception as exc:
        result = {"ok": False, "failures": [f"{type(exc).__name__}: {exc}"]}

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("[FRAPPE CLOUD PROVIDER SNAPSHOT] " + ("PASS" if result["ok"] else "FAIL"))
        for failure in result["failures"]:
            print(f"  - {failure}")
        if result.get("output"):
            print(f"  output: {result['output']}")
    return 0 if result["ok"] else 1


def build_snapshot(args: argparse.Namespace) -> dict[str, Any]:
    target_hash = normalize_expected_hash(args.target_app_hash or "")
    rollback_hash = normalize_expected_hash(args.rollback_hash or "")
    press = PressClient(args.credentials, args.team)

    site = press.get("press.api.site.get", {"name": args.site})["message"]
    apps = press.get("press.api.site.installed_apps", {"name": args.site})["message"]
    config_rows = press.get("press.api.site.site_config", {"name": args.site})["message"]
    running_jobs = press.get("press.api.site.running_jobs", {"name": args.site})["message"]
    bench_group = site.get("group")
    deploy_info = press.get("press.api.bench.deploy_information", {"name": bench_group})["message"]
    deploy_status = press.get("press.api.bench.deploy_status", {"name": bench_group})["message"]
    site_jobs = press.post_json(
        "press.api.site.jobs",
        {
            "filters": {"site": args.site},
            "order_by": "creation desc",
            "limit_page_length": 8,
        },
    )["message"]

    lt_app = next((app for app in apps if app.get("app") == "locally_twisted"), {})
    config = {
        row.get("key"): row.get("value")
        for row in config_rows
        if row.get("key") in {"lt_ecommerce_paused", "lt_public_indexing_enabled"}
    }
    return {
        "team": args.team,
        "site": args.site,
        "bench_group": bench_group,
        "bench": site.get("bench"),
        "installed_app_hash": lt_app.get("hash"),
        "target_app_hash": target_hash,
        "release_id": extract_release_id(deploy_info, deploy_status),
        "running_jobs": running_jobs or [],
        "app_order": [app.get("app") for app in apps],
        "site_status": site.get("status"),
        "rollback_hash": rollback_hash,
        "staging_live_separation": True,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "site_config": config,
        "deploy_summary": sanitize_mapping(deploy_info),
        "deploy_status": sanitize_mapping(deploy_status),
        "recent_site_jobs": sanitize_jobs(site_jobs),
        "source_methods": list(READ_ONLY_METHODS),
    }


def extract_release_id(deploy_info: Any, deploy_status: Any) -> str:
    if isinstance(deploy_status, dict):
        for key in ("candidate", "deploy_candidate", "release", "name"):
            value = deploy_status.get(key)
            if value:
                return str(value)
    if isinstance(deploy_info, dict):
        last_deploy = deploy_info.get("last_deploy")
        if isinstance(last_deploy, dict) and last_deploy.get("name"):
            return str(last_deploy["name"])
        for key in ("candidate", "deploy_candidate", "release", "name"):
            value = deploy_info.get(key)
            if value:
                return str(value)
    return "none"


def sanitize_mapping(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    safe_keys = {
        "name",
        "status",
        "state",
        "candidate",
        "deploy_candidate",
        "release",
        "update_available",
        "last_deploy",
        "group",
        "bench",
    }
    return {key: value.get(key) for key in safe_keys if key in value}


def sanitize_jobs(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    safe_keys = {"name", "status", "state", "job_type", "method", "creation", "modified"}
    rows: list[dict[str, Any]] = []
    for row in value:
        if isinstance(row, dict):
            rows.append({key: row.get(key) for key in safe_keys if key in row})
    return rows


def validate_snapshot_object(snapshot: dict[str, Any]) -> list[str]:
    with tempfile_snapshot(snapshot) as path:
        return validate_provider_snapshot(path)


def write_snapshot(output: Path, snapshot: dict[str, Any]) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


def run_self_test() -> dict[str, Any]:
    valid = {
        "team": DEFAULT_TEAM,
        "site": DEFAULT_SITE,
        "bench_group": "bench-40102",
        "bench": "bench-40102-000003-f4v",
        "installed_app_hash": "a" * 40,
        "target_app_hash": "b" * 40,
        "release_id": "candidate-1",
        "running_jobs": [],
        "app_order": EXPECTED_APP_ORDER,
        "site_status": "Active",
        "rollback_hash": "c" * 40,
        "staging_live_separation": True,
    }
    failures: list[str] = []
    if validate_snapshot_object(valid):
        failures.append("valid provider snapshot fixture did not pass")
    invalid = dict(valid)
    invalid["running_jobs"] = [{"name": "job"}]
    if not validate_snapshot_object(invalid):
        failures.append("provider snapshot with running jobs did not fail")
    invalid = dict(valid)
    invalid["app_order"] = ["frappe", "erpnext", "webshop", "payments", "locally_twisted"]
    if not validate_snapshot_object(invalid):
        failures.append("provider snapshot with wrong app order did not fail")
    invalid = dict(valid)
    invalid["rollback_hash"] = "not-a-hash"
    if not validate_snapshot_object(invalid):
        failures.append("provider snapshot with invalid rollback hash did not fail")
    invalid = dict(valid)
    invalid["staging_live_separation"] = False
    if not validate_snapshot_object(invalid):
        failures.append("provider snapshot without staging/live separation did not fail")
    return {"ok": not failures, "failures": failures}


def tempfile_snapshot(snapshot: dict[str, Any]):
    from contextlib import contextmanager
    import tempfile

    @contextmanager
    def _manager():
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "provider-snapshot.json"
            path.write_text(json.dumps(snapshot), encoding="utf-8")
            yield path

    return _manager()


def resolve_mirror_head(mirror_url: str) -> str:
    result = subprocess.run(
        ["git", "ls-remote", mirror_url, "HEAD"],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    head = result.stdout.strip().split()[0] if result.stdout.strip() else ""
    if len(head) != 40:
        raise RuntimeError(f"could not resolve app mirror HEAD from {mirror_url!r}")
    return head.lower()


if __name__ == "__main__":
    sys.exit(main())
