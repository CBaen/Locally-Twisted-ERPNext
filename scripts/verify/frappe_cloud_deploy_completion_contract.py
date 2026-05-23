#!/usr/bin/env python3
"""Offline contract for post-deploy/update Frappe Cloud completion artifacts.

This validator is intentionally local-only. It does not call Frappe Cloud or
perform any provider mutation. It validates the sanitized artifact that must
exist after a controlled deploy/update and before hosted bootstrap preflight.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "release"))

from release_guard_common import EXPECTED_APP_ORDER  # noqa: E402


DEFAULT_SITE = "locallytwisted-staging.frappe.cloud"
ALLOWED_ACTIONS = {
    "frappe_cloud_deploy",
    "frappe_cloud_update",
    "site_update",
    "deploy_update",
}
SUCCESS_STATUSES = {"success", "succeeded", "completed"}
REQUIRED_FIELDS = {
    "ok",
    "site",
    "action",
    "expected_app_hash",
    "target_app_hash",
    "installed_app_hash",
    "provider_job",
    "running_jobs",
    "app_order",
    "site_status",
    "site_config",
    "provider_mutation_executed",
}
UNSAFE_KEYS = {
    "api_key",
    "api_secret",
    "authorization",
    "body_excerpt",
    "cookie",
    "cookies",
    "exc",
    "exception",
    "password",
    "raw_body",
    "response_body",
    "secret",
    "session_id",
    "sid",
    "token",
    "traceback",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-file", type=Path, help="Sanitized deploy-completion artifact JSON.")
    parser.add_argument("--provider-snapshot", type=Path, help="Required pre-deploy/update provider snapshot for artifact-file mode.")
    parser.add_argument("--app-mirror-freshness", type=Path, help="Required app mirror freshness artifact for artifact-file mode.")
    parser.add_argument("--expected-site", default=os.environ.get("LT_STAGING_SITE", DEFAULT_SITE))
    parser.add_argument("--expected-hash", default=os.environ.get("LT_EXPECTED_APP_HASH"))
    parser.add_argument("--self-test", action="store_true", help="Run offline contract self-tests.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable result.")
    args = parser.parse_args()

    try:
        if args.self_test:
            result = run_self_test()
        elif args.artifact_file:
            if not args.provider_snapshot or not args.app_mirror_freshness:
                result = {
                    "ok": False,
                    "failures": [
                        "artifact-file mode requires --provider-snapshot and --app-mirror-freshness"
                    ],
                }
            else:
                result = validate_from_files(args)
        else:
            result = {"ok": False, "failures": ["pass --artifact-file or --self-test"]}
    except Exception as exc:
        result = {"ok": False, "failures": [f"{type(exc).__name__}: {exc}"]}

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("[FRAPPE CLOUD DEPLOY COMPLETION CONTRACT] " + ("PASS" if result["ok"] else "FAIL"))
        for failure in result["failures"]:
            print(f"  - {failure}")
    return 0 if result["ok"] else 1


def validate_from_files(args: argparse.Namespace) -> dict[str, Any]:
    artifact = load_json(args.artifact_file)
    provider_snapshot = load_json(args.provider_snapshot) if args.provider_snapshot else None
    app_mirror_freshness = load_json(args.app_mirror_freshness) if args.app_mirror_freshness else None
    failures = validate_deploy_completion_artifact(
        artifact,
        expected_site=args.expected_site,
        expected_hash=args.expected_hash,
        provider_snapshot=provider_snapshot,
        app_mirror_freshness=app_mirror_freshness,
        require_provider_snapshot=True,
        require_app_mirror_freshness=True,
    )
    return {"ok": not failures, "failures": failures}


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"artifact is missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"artifact is not valid JSON: {path}: {exc}") from exc


def validate_deploy_completion_artifact(
    artifact: Any,
    *,
    expected_site: str = DEFAULT_SITE,
    expected_hash: str | None = None,
    provider_snapshot: Any | None = None,
    app_mirror_freshness: Any | None = None,
    require_provider_snapshot: bool = False,
    require_app_mirror_freshness: bool = False,
) -> list[str]:
    if not isinstance(artifact, dict):
        return ["deploy completion artifact must be a JSON object"]

    failures: list[str] = []
    missing = sorted(field for field in REQUIRED_FIELDS if field not in artifact)
    if missing:
        failures.append(f"deploy completion artifact is missing required fields: {missing}")

    failures.extend(find_unsanitized_content(artifact))

    if artifact.get("ok") is not True:
        failures.append("deploy completion artifact must have ok=true")
    if artifact.get("provider_mutation_executed") is not True:
        failures.append("deploy completion artifact must prove provider_mutation_executed=true")

    action = artifact.get("action")
    if action not in ALLOWED_ACTIONS:
        failures.append(f"deploy completion action must be one of {sorted(ALLOWED_ACTIONS)}")

    if artifact.get("site") != expected_site:
        failures.append(f"deploy completion site must be {expected_site}")
    if artifact.get("site_status") != "Active":
        failures.append("deploy completion site_status must be Active")
    if artifact.get("running_jobs") not in ([], ()):
        failures.append("deploy completion running_jobs must be empty")
    if artifact.get("app_order") != EXPECTED_APP_ORDER:
        failures.append(f"deploy completion app_order must be {EXPECTED_APP_ORDER}")

    provider_job = artifact.get("provider_job")
    if not isinstance(provider_job, dict):
        failures.append("deploy completion provider_job must be an object")
    else:
        job_status = str(provider_job.get("status") or "").strip().lower()
        if job_status not in SUCCESS_STATUSES:
            failures.append("deploy completion provider_job.status must prove success")
        if not (provider_job.get("name") or provider_job.get("id")):
            failures.append("deploy completion provider_job must include name or id")

    site_config = artifact.get("site_config")
    if not isinstance(site_config, dict):
        failures.append("deploy completion site_config must be an object")
    else:
        if not flag_is_true(site_config.get("lt_ecommerce_paused")):
            failures.append("deploy completion must prove lt_ecommerce_paused=1 on staging")
        if not flag_is_false(site_config.get("lt_public_indexing_enabled")):
            failures.append("deploy completion must prove lt_public_indexing_enabled=0 on staging")

    expected_hash_value = normalize_hash(expected_hash) if expected_hash else normalize_hash(artifact.get("expected_app_hash"))
    target_hash = normalize_hash(artifact.get("target_app_hash"))
    installed_hash = normalize_hash(artifact.get("installed_app_hash"))
    artifact_expected_hash = normalize_hash(artifact.get("expected_app_hash"))
    for label, value in (
        ("expected_app_hash", artifact_expected_hash),
        ("target_app_hash", target_hash),
        ("installed_app_hash", installed_hash),
    ):
        if not is_full_hash(value):
            failures.append(f"deploy completion {label} must be a full 40-character hex hash")

    if expected_hash and artifact_expected_hash != expected_hash_value:
        failures.append("deploy completion expected_app_hash must match the expected hash argument")
    if is_full_hash(target_hash) and is_full_hash(expected_hash_value) and target_hash != expected_hash_value:
        failures.append("deploy completion target_app_hash must match expected_app_hash")
    if is_full_hash(installed_hash) and is_full_hash(expected_hash_value) and installed_hash != expected_hash_value:
        failures.append("deploy completion installed_app_hash must match expected_app_hash")

    if require_provider_snapshot and provider_snapshot is None:
        failures.append("deploy completion provider snapshot binding artifact is required")
    else:
        failures.extend(validate_provider_binding(provider_snapshot, expected_site, expected_hash_value))

    if require_app_mirror_freshness and app_mirror_freshness is None:
        failures.append("deploy completion app mirror freshness binding artifact is required")
    else:
        failures.extend(validate_app_mirror_binding(app_mirror_freshness, expected_hash_value))
    return failures


def validate_provider_binding(
    provider_snapshot: Any | None,
    expected_site: str,
    expected_hash: str,
) -> list[str]:
    if provider_snapshot is None:
        return []
    if not isinstance(provider_snapshot, dict):
        return ["provider snapshot binding artifact must be a JSON object"]
    failures: list[str] = []
    if provider_snapshot.get("site") != expected_site:
        failures.append("deploy completion site must match provider snapshot site")
    provider_target_hash = normalize_hash(provider_snapshot.get("target_app_hash"))
    if is_full_hash(expected_hash) and provider_target_hash != expected_hash:
        failures.append("deploy completion expected_app_hash must match provider snapshot target_app_hash")
    return failures


def validate_app_mirror_binding(app_mirror_freshness: Any | None, expected_hash: str) -> list[str]:
    if app_mirror_freshness is None:
        return []
    if not isinstance(app_mirror_freshness, dict):
        return ["app mirror freshness binding artifact must be a JSON object"]
    failures: list[str] = []
    if app_mirror_freshness.get("ok") is not True:
        failures.append("app mirror freshness binding artifact must have ok=true")
    mirror_hash = normalize_hash(app_mirror_freshness.get("mirror_hash"))
    if is_full_hash(expected_hash) and mirror_hash != expected_hash:
        failures.append("deploy completion expected_app_hash must match app mirror freshness mirror_hash")
    return failures


def normalize_hash(value: Any) -> str:
    return str(value or "").strip().lower()


def is_full_hash(value: str) -> bool:
    return len(value) == 40 and all(char in "0123456789abcdef" for char in value)


def flag_is_true(value: Any) -> bool:
    if value is True or value == 1:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return False


def flag_is_false(value: Any) -> bool:
    if value is False or value == 0:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"0", "false", "no", "off"}
    return False


def find_unsanitized_content(value: Any, path: str = "$") -> list[str]:
    failures: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            normalized_key = str(key).strip().lower().replace("-", "_")
            child_path = f"{path}.{key}"
            if normalized_key in UNSAFE_KEYS:
                failures.append(f"deploy completion artifact contains unsafe key: {child_path}")
            failures.extend(find_unsanitized_content(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            failures.extend(find_unsanitized_content(child, f"{path}[{index}]"))
    elif isinstance(value, str):
        lowered = value.lower()
        if "traceback (most recent call last)" in lowered:
            failures.append(f"deploy completion artifact contains traceback text: {path}")
    return failures


def run_self_test() -> dict[str, Any]:
    cases = [
        ContractCase("valid_fixture", expect_ok=True),
        ContractCase(
            "missing_installed_hash",
            expect_ok=False,
            mutate=lambda artifact, _provider, _mirror: artifact.pop("installed_app_hash"),
            expected_failure="missing required fields",
        ),
        ContractCase(
            "no_go",
            expect_ok=False,
            mutate=lambda artifact, _provider, _mirror: artifact.update({"ok": False}),
            expected_failure="must have ok=true",
        ),
        ContractCase(
            "wrong_site",
            expect_ok=False,
            mutate=lambda artifact, _provider, _mirror: artifact.update({"site": "wrong-staging.frappe.cloud"}),
            expected_failure="site must be",
        ),
        ContractCase(
            "wrong_hash",
            expect_ok=False,
            mutate=lambda artifact, _provider, _mirror: artifact.update({"installed_app_hash": "b" * 40}),
            expected_failure="installed_app_hash must match expected_app_hash",
        ),
        ContractCase(
            "running_jobs",
            expect_ok=False,
            mutate=lambda artifact, _provider, _mirror: artifact.update({"running_jobs": [{"name": "job-1"}]}),
            expected_failure="running_jobs must be empty",
        ),
        ContractCase(
            "bad_app_order",
            expect_ok=False,
            mutate=lambda artifact, _provider, _mirror: artifact.update(
                {"app_order": ["frappe", "erpnext", "webshop", "payments", "locally_twisted"]}
            ),
            expected_failure="app_order must be",
        ),
        ContractCase(
            "unsafe_flags",
            expect_ok=False,
            mutate=unsafe_flags,
            expected_failure="lt_ecommerce_paused=1",
        ),
        ContractCase(
            "failed_provider_job",
            expect_ok=False,
            mutate=lambda artifact, _provider, _mirror: artifact["provider_job"].update({"status": "Failed"}),
            expected_failure="provider_job.status must prove success",
        ),
        ContractCase(
            "wrong_provider_binding",
            expect_ok=False,
            mutate=lambda _artifact, provider, _mirror: provider.update({"target_app_hash": "b" * 40}),
            expected_failure="provider snapshot target_app_hash",
        ),
        ContractCase(
            "missing_provider_binding",
            expect_ok=False,
            provider_present=False,
            expected_failure="provider snapshot binding artifact is required",
        ),
        ContractCase(
            "wrong_mirror_binding",
            expect_ok=False,
            mutate=lambda _artifact, _provider, mirror: mirror.update({"mirror_hash": "b" * 40}),
            expected_failure="app mirror freshness mirror_hash",
        ),
        ContractCase(
            "missing_mirror_binding",
            expect_ok=False,
            mirror_present=False,
            expected_failure="app mirror freshness binding artifact is required",
        ),
        ContractCase(
            "unsanitized_body",
            expect_ok=False,
            mutate=lambda artifact, _provider, _mirror: artifact.update({"body_excerpt": "raw failure body"}),
            expected_failure="unsafe key",
        ),
    ]

    failures: list[str] = []
    case_results: list[dict[str, Any]] = []
    for case in cases:
        artifact = valid_artifact()
        provider = valid_provider_snapshot()
        mirror = valid_app_mirror_freshness()
        if case.mutate:
            case.mutate(artifact, provider, mirror)
        case_failures = validate_deploy_completion_artifact(
            artifact,
            expected_site=DEFAULT_SITE,
            provider_snapshot=provider if case.provider_present else None,
            app_mirror_freshness=mirror if case.mirror_present else None,
            require_provider_snapshot=True,
            require_app_mirror_freshness=True,
        )
        case_ok = not case_failures
        contract_failures: list[str] = []
        if case_ok != case.expect_ok:
            contract_failures.append(f"{case.name}: expected ok={case.expect_ok}, found ok={case_ok}")
        if case.expected_failure and not any(case.expected_failure in failure for failure in case_failures):
            contract_failures.append(
                f"{case.name}: expected failure containing {case.expected_failure!r}; found {case_failures}"
            )
        failures.extend(contract_failures)
        case_results.append(
            {
                "name": case.name,
                "status": "PASS" if not contract_failures else "FAIL",
                "ok": case_ok,
                "failures": case_failures,
                "contract_failures": contract_failures,
            }
        )

    return {"ok": not failures, "failures": failures, "cases": case_results}


class ContractCase:
    def __init__(
        self,
        name: str,
        *,
        expect_ok: bool,
        mutate: Any | None = None,
        expected_failure: str | None = None,
        provider_present: bool = True,
        mirror_present: bool = True,
    ) -> None:
        self.name = name
        self.expect_ok = expect_ok
        self.mutate = mutate
        self.expected_failure = expected_failure
        self.provider_present = provider_present
        self.mirror_present = mirror_present


def valid_artifact() -> dict[str, Any]:
    app_hash = "a" * 40
    return {
        "ok": True,
        "site": DEFAULT_SITE,
        "action": "frappe_cloud_deploy",
        "expected_app_hash": app_hash,
        "target_app_hash": app_hash,
        "installed_app_hash": app_hash,
        "provider_job": {
            "name": "deploy-job-1",
            "status": "Success",
            "method": "press.api.site.update",
        },
        "running_jobs": [],
        "app_order": EXPECTED_APP_ORDER,
        "site_status": "Active",
        "site_config": {
            "lt_ecommerce_paused": "1",
            "lt_public_indexing_enabled": "0",
        },
        "provider_mutation_executed": True,
    }


def valid_provider_snapshot() -> dict[str, Any]:
    return {
        "site": DEFAULT_SITE,
        "target_app_hash": "a" * 40,
    }


def valid_app_mirror_freshness() -> dict[str, Any]:
    return {
        "ok": True,
        "mirror_hash": "a" * 40,
    }


def unsafe_flags(artifact: dict[str, Any], _provider: dict[str, Any], _mirror: dict[str, Any]) -> None:
    artifact["site_config"]["lt_ecommerce_paused"] = "0"
    artifact["site_config"]["lt_public_indexing_enabled"] = "1"


if __name__ == "__main__":
    sys.exit(main())
