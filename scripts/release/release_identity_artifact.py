#!/usr/bin/env python3
"""Build or validate a local release identity proof artifact.

This helper is deliberately local/offline. It does not read Codex auth files,
does not read secrets, and does not contact Frappe Cloud. The point is to make
account/session identity an explicit release artifact before any future staging
mutation can leave forensic-freeze.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from release_guard_common import (
    DEFAULT_LOCK_PATH,
    MAX_REOPEN_APPROVAL_DURATION,
    REQUIRED_HOSTED_PREFLIGHT_SITE,
    ReleaseGuardError,
    current_git_head,
    is_full_hash,
    load_release_lock,
    normalize_hash,
    raise_if_failures,
    validate_release_lock,
)


ARTIFACT_TYPE = "release_identity_proof"
DEFAULT_APP_MIRROR_REPO = "https://github.com/CBaen/Locally-Twisted-Frappe-App.git"
REQUIRED_SURFACES = {
    "codex_account",
    "github_cli",
    "frappe_cloud_team",
    "frappe_cloud_site",
    "app_mirror_repo",
    "release_operator",
}
PASSING_STATUSES = {"verified", "manual_confirmed"}
DISALLOWED_KEY_PARTS = {
    "api_key",
    "api_secret",
    "auth",
    "authorization",
    "cookie",
    "password",
    "secret",
    "session",
    "sid",
    "token",
}
DISALLOWED_VALUE_MARKERS = ("sk-", "ghp_", "github_pat_", "xoxb-", "sid=")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--lock-file", type=Path, default=DEFAULT_LOCK_PATH)
    parser.add_argument("--output", type=Path, help="Where to write release-identity-proof.json with --write.")
    parser.add_argument("--write", action="store_true", help="Write a passing identity proof after validation.")
    parser.add_argument("--force", action="store_true", help="Allow overwriting --output.")
    parser.add_argument("--validate-only", type=Path, help="Validate an existing release identity artifact.")
    parser.add_argument("--codex-account-label", help="Human-visible Codex/ChatGPT account context, no secrets.")
    parser.add_argument("--github-account", help="Expected GitHub login. If omitted with --detect-github-cli, gh is queried read-only.")
    parser.add_argument("--detect-github-cli", action="store_true", help="Read the local gh login with gh api user --jq .login.")
    parser.add_argument("--frappe-cloud-team", help="Expected Frappe Cloud team id or human-safe label.")
    parser.add_argument("--frappe-cloud-site", default=REQUIRED_HOSTED_PREFLIGHT_SITE)
    parser.add_argument("--app-mirror-repo", default=DEFAULT_APP_MIRROR_REPO)
    parser.add_argument("--operator", help="Human/agent release operator name.")
    parser.add_argument("--evidence", help="Short evidence note for this identity proof.")
    parser.add_argument("--duration-hours", type=float, default=12.0)
    parser.add_argument("--json", action="store_true")
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
        marker = "PASS" if result.get("ok") else "BLOCK"
        print(f"[RELEASE IDENTITY ARTIFACT] {marker}")
        if result.get("output"):
            print(f"  output: {result['output']}")
        if result.get("failure"):
            print(f"  failure: {result['failure']}")
    return 0 if result.get("ok") else 1


def run(args: argparse.Namespace) -> dict[str, Any]:
    lock = load_release_lock(args.lock_file)
    raise_if_failures("invalid release lock", validate_release_lock(lock))

    if args.validate_only:
        failures = validate_identity_artifact(args.validate_only, lock=lock)
        return {
            "ok": not failures,
            "path": str(args.validate_only),
            "failures": failures,
            "failure": "; ".join(failures) if failures else None,
            "provider_mutation_executed": False,
        }

    if args.duration_hours <= 0 or timedelta(hours=args.duration_hours) > MAX_REOPEN_APPROVAL_DURATION:
        raise ReleaseGuardError("identity proof duration must be greater than 0 and no longer than 24 hours")

    github_account = args.github_account
    github_evidence = "manual confirmation"
    if args.detect_github_cli and not github_account:
        github_account, github_evidence = detect_github_login()

    missing_for_write = []
    for field_name, value in (
        ("--codex-account-label", args.codex_account_label),
        ("--github-account or --detect-github-cli", github_account),
        ("--frappe-cloud-team", args.frappe_cloud_team),
        ("--operator", args.operator),
        ("--evidence", args.evidence),
    ):
        if args.write and not str(value or "").strip():
            missing_for_write.append(field_name)
    if missing_for_write:
        raise ReleaseGuardError("identity proof write is missing required fields: " + ", ".join(missing_for_write))

    artifact = build_artifact(
        lock=lock,
        ok=bool(args.write),
        codex_account_label=args.codex_account_label,
        github_account=github_account,
        github_evidence=github_evidence,
        frappe_cloud_team=args.frappe_cloud_team,
        frappe_cloud_site=args.frappe_cloud_site,
        app_mirror_repo=args.app_mirror_repo,
        operator=args.operator,
        evidence=args.evidence,
        duration_hours=args.duration_hours,
    )

    if args.write:
        if not args.output:
            raise ReleaseGuardError("--write requires --output")
        if args.output.exists() and not args.force:
            raise ReleaseGuardError(f"refusing to overwrite existing identity artifact without --force: {args.output}")
        failures = validate_identity_payload(artifact, lock=lock)
        raise_if_failures("generated identity proof is invalid", failures)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return {
            "ok": True,
            "output": str(args.output),
            "source_commit": artifact["source_commit"],
            "provider_mutation_executed": False,
        }

    artifact["preview_only"] = True
    return {
        "ok": False,
        "failure": "preview only; rerun with --write and explicit account/session fields before release mutation",
        "preview": artifact,
        "provider_mutation_executed": False,
    }


def detect_github_login() -> tuple[str | None, str]:
    try:
        result = subprocess.run(
            ["gh", "api", "user", "--jq", ".login"],
            text=True,
            capture_output=True,
            timeout=15,
            check=True,
        )
    except Exception:
        return None, "gh api user read-only check failed or is unavailable"
    login = result.stdout.strip()
    if not login:
        return None, "gh api user returned no login"
    return login, "gh api user --jq .login"


def build_artifact(
    *,
    lock: dict[str, Any],
    ok: bool,
    codex_account_label: str | None,
    github_account: str | None,
    github_evidence: str,
    frappe_cloud_team: str | None,
    frappe_cloud_site: str,
    app_mirror_repo: str,
    operator: str | None,
    evidence: str | None,
    duration_hours: float,
) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(hours=duration_hours)
    return {
        "ok": ok,
        "artifact_type": ARTIFACT_TYPE,
        "lock_id": lock.get("id"),
        "target_site": REQUIRED_HOSTED_PREFLIGHT_SITE,
        "source_commit": current_git_head(),
        "created_at": now.isoformat(),
        "expires_at": expires_at.isoformat(),
        "secret_free": True,
        "provider_mutation_executed": False,
        "account_checks": [
            check_row(
                "codex_account",
                "Codex/ChatGPT account selected intentionally for LT release work",
                codex_account_label,
                "manual confirmation; Codex auth files are not read",
                evidence,
                ok,
            ),
            check_row(
                "github_cli",
                "GitHub CLI account allowed to read/write LT source and app mirror as needed",
                github_account,
                github_evidence,
                evidence,
                ok,
            ),
            check_row(
                "frappe_cloud_team",
                "Frappe Cloud team/account owns the LT staging site",
                frappe_cloud_team,
                "manual confirmation or provider snapshot evidence",
                evidence,
                ok,
            ),
            check_row(
                "frappe_cloud_site",
                REQUIRED_HOSTED_PREFLIGHT_SITE,
                frappe_cloud_site,
                "manual confirmation or provider snapshot evidence",
                evidence,
                ok,
            ),
            check_row(
                "app_mirror_repo",
                DEFAULT_APP_MIRROR_REPO,
                app_mirror_repo,
                "manual confirmation plus app mirror freshness proof",
                evidence,
                ok,
            ),
            check_row(
                "release_operator",
                "named operator responsible for this release packet",
                operator,
                "manual confirmation",
                evidence,
                ok,
            ),
        ],
    }


def check_row(
    surface: str,
    expected: str,
    actual: str | None,
    method: str,
    evidence: str | None,
    ok: bool,
) -> dict[str, Any]:
    actual_value = str(actual or "").strip()
    evidence_value = str(evidence or method or "").strip()
    return {
        "surface": surface,
        "status": "manual_confirmed" if ok and actual_value else "needs_confirmation",
        "expected": expected,
        "actual": actual_value,
        "method": method,
        "evidence": evidence_value,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


def validate_identity_artifact(path: Path, *, lock: dict[str, Any] | None = None) -> list[str]:
    try:
        artifact = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return [f"identity proof artifact is missing: {path}"]
    except json.JSONDecodeError as exc:
        return [f"identity proof artifact is not valid JSON: {exc}"]
    if not isinstance(artifact, dict):
        return [f"identity proof artifact must be a JSON object: {path}"]
    if lock is None:
        lock = load_release_lock()
    return validate_identity_payload(artifact, lock=lock)


def validate_identity_payload(artifact: dict[str, Any], *, lock: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if artifact.get("ok") is not True:
        failures.append("identity proof must have ok=true before release mutation")
    if artifact.get("artifact_type") != ARTIFACT_TYPE:
        failures.append(f"identity proof artifact_type must be {ARTIFACT_TYPE}")
    if artifact.get("lock_id") != lock.get("id"):
        failures.append("identity proof lock_id must match active release lock")
    if artifact.get("target_site") != REQUIRED_HOSTED_PREFLIGHT_SITE:
        failures.append(f"identity proof target_site must be {REQUIRED_HOSTED_PREFLIGHT_SITE}")
    if artifact.get("provider_mutation_executed") is not False:
        failures.append("identity proof must prove provider_mutation_executed=false")
    if artifact.get("secret_free") is not True:
        failures.append("identity proof must declare secret_free=true")

    source_commit = normalize_hash(artifact.get("source_commit"))
    if not is_full_hash(source_commit):
        failures.append("identity proof source_commit must be a full 40-character hex hash")
    else:
        try:
            current_head = current_git_head()
        except ReleaseGuardError as exc:
            failures.append(str(exc))
        else:
            if source_commit != current_head:
                failures.append(f"identity proof source_commit must match current repository HEAD: {source_commit} != {current_head}")

    created_at = parse_identity_timestamp(artifact.get("created_at"), "created_at", failures)
    expires_at = parse_identity_timestamp(artifact.get("expires_at"), "expires_at", failures)
    if created_at and expires_at:
        now = datetime.now(timezone.utc)
        if expires_at <= now:
            failures.append("identity proof is expired")
        if expires_at <= created_at:
            failures.append("identity proof expires_at must be after created_at")
        if expires_at - created_at > MAX_REOPEN_APPROVAL_DURATION:
            failures.append("identity proof duration must be 24 hours or less")

    failures.extend(validate_secret_free(artifact))
    failures.extend(validate_account_checks(artifact.get("account_checks")))
    return failures


def parse_identity_timestamp(value: Any, field_name: str, failures: list[str]) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        failures.append(f"identity proof {field_name} must be a non-empty timestamp string")
        return None
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        failures.append(f"identity proof {field_name} must be ISO-8601 parseable")
        return None
    if parsed.tzinfo is None:
        failures.append(f"identity proof {field_name} must include a timezone offset")
        return None
    return parsed.astimezone(timezone.utc)


def validate_secret_free(value: Any) -> list[str]:
    failures: list[str] = []
    for key in collect_keys(value):
        lowered = key.lower()
        if lowered == "secret_free":
            continue
        if any(part in lowered for part in DISALLOWED_KEY_PARTS):
            failures.append(f"identity proof contains disallowed secret-bearing key: {key}")
    for text_value in collect_strings(value):
        lowered = text_value.lower()
        if any(marker.lower() in lowered for marker in DISALLOWED_VALUE_MARKERS):
            failures.append("identity proof contains a value that looks like a raw secret/token")
            break
    return failures


def validate_account_checks(checks: Any) -> list[str]:
    if not isinstance(checks, list):
        return ["identity proof account_checks must be a list"]
    failures: list[str] = []
    by_surface: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(checks):
        if not isinstance(row, dict):
            failures.append(f"identity proof account_checks[{index}] must be an object")
            continue
        surface = str(row.get("surface") or "").strip()
        if not surface:
            failures.append(f"identity proof account_checks[{index}] is missing surface")
            continue
        if surface in by_surface:
            failures.append(f"identity proof has duplicate account check surface: {surface}")
        by_surface[surface] = row
        if row.get("status") not in PASSING_STATUSES:
            failures.append(f"identity proof {surface} status must be verified or manual_confirmed")
        for field in ("expected", "actual", "method", "evidence", "checked_at"):
            if not str(row.get(field) or "").strip():
                failures.append(f"identity proof {surface} is missing {field}")
        row_failures: list[str] = []
        parse_identity_timestamp(row.get("checked_at"), f"account_checks.{surface}.checked_at", row_failures)
        failures.extend(row_failures)

    missing_surfaces = sorted(REQUIRED_SURFACES - set(by_surface))
    if missing_surfaces:
        failures.append(f"identity proof is missing required account surfaces: {missing_surfaces}")

    site_row = by_surface.get("frappe_cloud_site")
    if site_row and str(site_row.get("actual") or "") != REQUIRED_HOSTED_PREFLIGHT_SITE:
        failures.append(f"identity proof frappe_cloud_site actual must be {REQUIRED_HOSTED_PREFLIGHT_SITE}")
    mirror_row = by_surface.get("app_mirror_repo")
    if mirror_row and "Locally-Twisted-Frappe-App" not in str(mirror_row.get("actual") or ""):
        failures.append("identity proof app_mirror_repo actual must reference Locally-Twisted-Frappe-App")
    return failures


def collect_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            keys.add(str(key))
            keys.update(collect_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(collect_keys(child))
    return keys


def collect_strings(value: Any) -> list[str]:
    strings: list[str] = []
    if isinstance(value, str):
        strings.append(value)
    elif isinstance(value, dict):
        for child in value.values():
            strings.extend(collect_strings(child))
    elif isinstance(value, list):
        for child in value:
            strings.extend(collect_strings(child))
    return strings


if __name__ == "__main__":
    sys.exit(main())
