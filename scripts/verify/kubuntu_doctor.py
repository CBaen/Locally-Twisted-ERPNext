#!/usr/bin/env python3
"""Read-only local health check for the Wardenclyffe Kubuntu LT stack."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROJECT = "locally-twisted-erpnext-v15"
BACKEND = "locally-twisted-erpnext-v15-backend-1"
BASE_URL = "http://127.0.0.1:8081"
EXPECTED_APPS = {"frappe", "erpnext", "payments", "webshop", "locally_twisted"}


failures: list[str] = []
warnings: list[str] = []


def run(args: list[str], *, cwd: Path = ROOT) -> tuple[int, str]:
    proc = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def check(condition: bool, message: str) -> None:
    if condition:
        print(f"PASS {message}")
    else:
        print(f"FAIL {message}")
        failures.append(message)


def warn(condition: bool, message: str) -> None:
    if condition:
        print(f"PASS {message}")
    else:
        print(f"WARN {message}")
        warnings.append(message)


def http_status(url: str) -> int | None:
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return response.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except OSError:
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()

    print("[LT KUBUNTU DOCTOR] read-only")

    code, branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    check(code == 0 and branch == "main", "git branch is main")

    code, status = run(["git", "status", "--short"])
    if code == 0 and not status:
        print("PASS no uncommitted git changes")
    else:
        print("WARN repo has uncommitted changes")
        warnings.append("repo has uncommitted changes")

    check(shutil.which("docker") is not None, "docker CLI is available")
    check(shutil.which("node") is not None, "node is available")
    check(shutil.which("npm") is not None, "npm is available")

    warn((ROOT / "node_modules" / "@playwright" / "test").exists(), "repo-local Playwright dependency is installed")

    code, containers = run(["docker", "ps", "--format", "{{.Names}}"])
    check(code == 0 and BACKEND in containers.splitlines(), f"{BACKEND} is running")
    check(code == 0 and any(name.startswith(PROJECT) for name in containers.splitlines()), f"{PROJECT} containers are visible")

    check(http_status(BASE_URL) == 200, f"{BASE_URL}/ returns HTTP 200")

    code, version = run(["docker", "exec", BACKEND, "bench", "--site", "frontend", "version"])
    check(code == 0 and "erpnext 15.105.0" in version and "frappe 15.106.0" in version, "bench reports expected ERPNext/Frappe versions")

    code, apps = run(["docker", "exec", BACKEND, "bench", "--site", "frontend", "list-apps"])
    found_apps = {line.split()[0] for line in apps.splitlines() if line.strip()}
    check(code == 0 and EXPECTED_APPS.issubset(found_apps), "expected apps are installed")

    if warnings:
        print("[LT KUBUNTU DOCTOR] warnings: " + "; ".join(warnings))
    if failures:
        print("[LT KUBUNTU DOCTOR] failed: " + "; ".join(failures))
        return 1
    print("[LT KUBUNTU DOCTOR] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
