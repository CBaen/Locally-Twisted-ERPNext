#!/usr/bin/env python3
"""
Read-only Frappe Cloud cutover preflight for Locally Twisted.

This does not deploy, create a Frappe Cloud site, restore backups, read secrets,
or change DNS. It checks the local and public setup that should be boring before
the owner-present cutover session.

Usage:
    python scripts/verify/frappe_cloud_preflight.py
    python scripts/verify/frappe_cloud_preflight.py --json
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback.
    tomllib = None  # type: ignore[assignment]


PROJECT_ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = PROJECT_ROOT / "apps" / "locally_twisted"
APP_PACKAGE = APP_ROOT / "locally_twisted"
PUBLIC_DOMAIN = "locallytwisted.com"
WWW_DOMAIN = "www.locallytwisted.com"
FRAPPE_CLOUD_VANITY_HOST = "locallytwisted.v.frappe.cloud"
EXPECTED_CLOUDFLARE_NS = {"edward.ns.cloudflare.com", "laura.ns.cloudflare.com"}
APP_SOURCE_REPO = "CBaen/Locally-Twisted-Frappe-App"
APP_SOURCE_URL = f"https://github.com/{APP_SOURCE_REPO}.git"
FRAPPE_CLOUD_PUBLIC_KEY = "id_ed25519.pub"


@dataclass
class Check:
    id: str
    status: str
    summary: str
    details: dict[str, Any] = field(default_factory=dict)


def run(command: list[str], cwd: Path = PROJECT_ROOT) -> tuple[int, str, str]:
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError as exc:
        return 127, "", str(exc)
    return completed.returncode, completed.stdout.strip(), completed.stderr.strip()


def check_git() -> list[Check]:
    checks: list[Check] = []

    code, branch, err = run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    if code == 0 and branch == "main":
        checks.append(Check("git_branch", "pass", "Current branch is main.", {"branch": branch}))
    else:
        checks.append(Check("git_branch", "block", "Cutover must run from main.", {"branch": branch, "error": err}))

    code, remote, err = run(["git", "remote", "get-url", "origin"])
    if code == 0 and remote:
        checks.append(Check("git_remote", "pass", "Origin remote is configured.", {"origin": remote}))
    else:
        checks.append(Check("git_remote", "block", "Origin remote is missing.", {"error": err}))

    code, status, _ = run(["git", "status", "--short"])
    if code != 0:
        checks.append(Check("git_clean", "warn", "Could not inspect git status."))
    elif status:
        changed = [line for line in status.splitlines() if line.strip()]
        checks.append(
            Check(
                "git_clean",
                "warn",
                "Worktree is dirty; owner-present cutover should use a reviewed, pushed commit.",
                {"changed_paths": len(changed)},
            )
        )
    else:
        checks.append(Check("git_clean", "pass", "Worktree is clean."))

    code, pushed, _ = run(["git", "status", "--short", "--branch"])
    if code == 0 and ("ahead" in pushed or "behind" in pushed):
        checks.append(
            Check(
                "git_sync",
                "warn",
                "Local branch is not in a simple synced state with origin.",
                {"status": pushed.splitlines()[0] if pushed else ""},
            )
        )
    elif code == 0:
        checks.append(Check("git_sync", "pass", "Branch header does not report ahead/behind drift."))

    return checks


def check_app_packaging() -> list[Check]:
    checks: list[Check] = []
    app_pyproject = APP_ROOT / "pyproject.toml"
    root_pyproject = PROJECT_ROOT / "pyproject.toml"

    if app_pyproject.exists():
        checks.append(
            Check(
                "app_pyproject",
                "pass",
                "Custom app pyproject.toml exists at the app root.",
                {"path": str(app_pyproject.relative_to(PROJECT_ROOT))},
            )
        )
    else:
        checks.append(Check("app_pyproject", "block", "Custom app pyproject.toml is missing."))
        return checks

    app_source_check = check_app_source_mirror()
    if app_source_check.status == "pass":
        checks.append(app_source_check)
    elif root_pyproject.exists():
        checks.append(
            Check(
                "app_source_shape",
                "warn",
                "Repository root also has a pyproject.toml; confirm Frappe Cloud validates the intended app or use the app-root mirror.",
                {"app_source_repo": APP_SOURCE_URL},
            )
        )
    else:
        checks.append(
            Check(
                "app_source_shape",
                "warn",
                "Repository root is not the Frappe app root; prepare an app-root GitHub source/mirror for Frappe Cloud.",
                {"app_root": str(APP_ROOT.relative_to(PROJECT_ROOT))},
            )
        )

    if tomllib is None:
        checks.append(Check("app_frappe_dependency", "warn", "tomllib unavailable; could not parse pyproject.toml."))
        return checks

    data = tomllib.loads(app_pyproject.read_text(encoding="utf-8"))
    dep = data.get("tool", {}).get("bench", {}).get("frappe-dependencies", {}).get("frappe")
    if dep and "<16" in dep and ">=15" in dep.replace(" ", ""):
        checks.append(Check("app_frappe_dependency", "pass", "App advertises a bounded Frappe v15 dependency.", {"frappe": dep}))
    elif dep:
        checks.append(Check("app_frappe_dependency", "warn", "Review the app's Frappe dependency before Frappe Cloud validation.", {"frappe": dep}))
    else:
        checks.append(Check("app_frappe_dependency", "block", "App does not advertise its Frappe dependency."))

    apt_packages = data.get("deploy", {}).get("dependencies", {}).get("apt", {}).get("packages")
    if isinstance(apt_packages, list):
        checks.append(Check("app_apt_dependencies", "pass", "APT dependency list is explicit.", {"packages": apt_packages}))
    else:
        checks.append(Check("app_apt_dependencies", "warn", "No explicit APT dependency list found."))

    if (APP_PACKAGE / "hooks.py").exists() and (APP_PACKAGE / "patches.txt").exists():
        checks.append(Check("app_hooks_patches", "pass", "hooks.py and patches.txt are present in the custom app."))
    else:
        checks.append(Check("app_hooks_patches", "block", "hooks.py or patches.txt is missing from the custom app."))

    return checks


def check_app_source_mirror() -> Check:
    code, out, err = run(
        [
            "gh",
            "repo",
            "view",
            APP_SOURCE_REPO,
            "--json",
            "defaultBranchRef,visibility,url",
            "--jq",
            ".url + \" \" + .visibility + \" \" + .defaultBranchRef.name",
        ]
    )
    if code != 0 or not out:
        return Check(
            "app_source_shape",
            "warn",
            "App-root GitHub mirror is not confirmed.",
            {"app_source_repo": APP_SOURCE_URL, "error": err},
        )

    code, _, err = run(["gh", "api", f"repos/{APP_SOURCE_REPO}/contents/pyproject.toml", "--jq", ".path"])
    if code != 0:
        return Check(
            "app_source_shape",
            "warn",
            "App-root GitHub mirror exists but pyproject.toml was not confirmed at its root.",
            {"app_source_repo": APP_SOURCE_URL, "error": err},
        )

    return Check(
        "app_source_shape",
        "pass",
        "App-root GitHub mirror is ready for Frappe Cloud custom app validation.",
        {"app_source_repo": APP_SOURCE_URL, "repo": out},
    )


def check_github() -> Check:
    code, login, err = run(["gh", "api", "user", "--jq", ".login"])
    if code == 0 and login:
        return Check("github_auth", "pass", "GitHub CLI can authenticate.", {"login": login})
    return Check("github_auth", "warn", "GitHub CLI auth is not confirmed; Frappe Cloud GitHub app connection still happens in the browser.", {"error": err})


def check_ssh_public_keys() -> list[Check]:
    ssh_dir = Path(os.environ.get("HOME", str(Path.home()))) / ".ssh"
    pub_keys = sorted(ssh_dir.glob("*.pub")) if ssh_dir.exists() else []
    checks: list[Check] = []

    if not pub_keys:
        return [Check("ssh_public_keys", "warn", "No SSH public keys found under the user .ssh directory.")]

    readable: list[dict[str, str]] = []
    unreadable: list[str] = []
    for key_path in pub_keys:
        code, out, _ = run(["ssh-keygen", "-lf", str(key_path)])
        if code == 0 and out:
            readable.append({"name": key_path.name, "fingerprint": out})
        else:
            unreadable.append(key_path.name)

    if readable:
        checks.append(Check("ssh_public_keys", "pass", "At least one SSH public key is readable for Frappe Cloud.", {"keys": readable}))
    if unreadable:
        checks.append(Check("ssh_public_keys_unreadable", "warn", "Some SSH public keys exist but are not readable.", {"keys": unreadable}))

    expected_key = ssh_dir / FRAPPE_CLOUD_PUBLIC_KEY
    expected_private_key = expected_key.with_suffix("")
    code, fingerprint, err = run(["ssh-keygen", "-lf", str(expected_key)])
    if code == 0 and expected_private_key.exists():
        checks.append(
            Check(
                "frappe_cloud_ssh_key",
                "pass",
                "Frappe Cloud SSH public key is readable and the matching private key exists locally.",
                {"public_key": str(expected_key), "fingerprint": fingerprint},
            )
        )
    else:
        checks.append(
            Check(
                "frappe_cloud_ssh_key",
                "warn",
                "Frappe Cloud SSH key is not fully ready.",
                {"public_key": str(expected_key), "private_key_exists": expected_private_key.exists(), "error": err},
            )
        )

    return checks


def resolve_records(name: str, record_type: str) -> list[str]:
    code, out, _ = run(["nslookup", f"-type={record_type}", name])
    if code != 0 or not out:
        return []
    records: list[str] = []
    saw_answer_name = False
    for raw_line in out.splitlines():
        line = raw_line.strip()
        lower = line.lower()
        if not line or lower.startswith(("server:", "non-authoritative")):
            continue
        if lower.startswith("name:"):
            saw_answer_name = True
            continue
        if lower.startswith("address:"):
            value = line.split(":", 1)[1].strip()
            if saw_answer_name and value:
                records.append(value)
            continue
        if "nameserver =" in lower:
            records.append(line.split("=", 1)[1].strip().rstrip(".").lower())
        elif "canonical name =" in lower:
            records.append(line.split("=", 1)[1].strip().rstrip(".").lower())
        elif lower.startswith("addresses:"):
            continue
        elif line and all(part.isdigit() and 0 <= int(part) <= 255 for part in line.split(".") if part):
            records.append(line)
    return sorted(set(records))


def check_dns() -> list[Check]:
    checks: list[Check] = []
    ns_records = set(resolve_records(PUBLIC_DOMAIN, "NS"))
    a_records = resolve_records(PUBLIC_DOMAIN, "A")
    www_cname = resolve_records(WWW_DOMAIN, "CNAME")
    www_a = resolve_records(WWW_DOMAIN, "A")

    if EXPECTED_CLOUDFLARE_NS.issubset(ns_records):
        checks.append(Check("dns_nameservers", "pass", "Domain is already delegated to Cloudflare nameservers.", {"records": sorted(ns_records)}))
    elif ns_records:
        checks.append(Check("dns_nameservers", "warn", "Domain nameservers are not the expected Cloudflare pair.", {"records": sorted(ns_records)}))
    else:
        checks.append(Check("dns_nameservers", "warn", "Could not resolve nameservers for the domain."))

    target_details = {"apex_a": a_records, "www_cname": www_cname, "www_a": www_a}
    if FRAPPE_CLOUD_VANITY_HOST in www_cname:
        checks.append(
            Check(
                "dns_current_target",
                "pass",
                "Public DNS includes the Frappe Cloud vanity host; use the Cloudflare dynamic-route gate for HTTP health.",
                target_details,
            )
        )
    else:
        checks.append(
            Check(
                "dns_current_target",
                "warn",
                "Public DNS target is not confirmed as the Frappe Cloud vanity host; do not change final routing without the launch gate.",
                target_details,
            )
        )
    return checks


def collect_checks() -> list[Check]:
    checks: list[Check] = []
    checks.extend(check_git())
    checks.extend(check_app_packaging())
    checks.append(check_github())
    checks.extend(check_ssh_public_keys())
    checks.extend(check_dns())
    return checks


def render_text(checks: list[Check]) -> None:
    print("Frappe Cloud cutover preflight")
    print("=" * 32)
    for check in checks:
        marker = {"pass": "PASS", "warn": "WARN", "block": "BLOCK"}.get(check.status, check.status.upper())
        print(f"[{marker}] {check.id}: {check.summary}")
        if check.details:
            for key, value in check.details.items():
                print(f"        {key}: {value}")

    blockers = [check for check in checks if check.status == "block"]
    warnings = [check for check in checks if check.status == "warn"]
    print()
    print(f"Summary: {len(blockers)} blocker(s), {len(warnings)} warning(s), {len(checks)} checks.")
    if blockers:
        print("Cutover is not ready. Fix blockers before owner-present work.")
    elif warnings:
        print("No hard blockers found, but clear warnings before calling it demo-ready.")
    else:
        print("No blockers or warnings found.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only Frappe Cloud cutover preflight.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args()

    checks = collect_checks()
    if args.json:
        print(json.dumps([check.__dict__ for check in checks], indent=2, sort_keys=True))
    else:
        render_text(checks)
    return 2 if any(check.status == "block" for check in checks) else 0


if __name__ == "__main__":
    sys.exit(main())
