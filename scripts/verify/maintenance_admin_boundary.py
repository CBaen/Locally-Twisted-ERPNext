#!/usr/bin/env python3
"""Verify Maintenance Admin sees only sanitized maintenance surfaces."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.maintenance.heartbeat.boundary_report"


class MaintenanceBoundaryFail(Exception):
    pass


def bench_execute() -> dict[str, Any]:
    proc = subprocess.run(
        ["docker", "exec", CONTAINER, "bench", "--site", SITE, "execute", METHOD],
        text=True,
        capture_output=True,
        timeout=90,
    )
    if proc.returncode != 0:
        raise MaintenanceBoundaryFail(
            f"bench execute failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    return _parse_json_stdout(proc.stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true", help="Print the full boundary payload")
    args = parser.parse_args()

    try:
        result = bench_execute()
        failures = _contract_failures(result)
    except MaintenanceBoundaryFail as exc:
        print(f"[MAINTENANCE ADMIN BOUNDARY] FAIL\n  - {exc}")
        return 1

    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print("[MAINTENANCE ADMIN BOUNDARY] " + ("PASS" if not failures else "FAIL"))
        print(f"  role: {result.get('role')}")
        print(f"  allowed_doctypes: {len(result.get('allowed_doctypes') or [])}")
        print(f"  forbidden_doctypes: {len(result.get('forbidden_doctypes') or [])}")
        print(f"  workspace_shortcuts: {len(result.get('workspace_shortcuts') or [])}")

    if failures:
        print("  failures:")
        for failure in failures:
            print(f"    - {failure}")
        return 1
    return 0


def _contract_failures(result: dict[str, Any]) -> list[str]:
    failures = list(result.get("failures") or [])
    for key, expected in {
        "sanitized": True,
        "raw_log_access": False,
        "customer_data_included": False,
    }.items():
        if result.get(key) is not expected:
            failures.append(f"{key} expected {expected}, found {result.get(key)}")
    if result.get("role_exists") is not True:
        failures.append("maintenance role is missing")
    for row in result.get("allowed_doctypes") or []:
        if row.get("exists") is not True:
            failures.append(f"allowed DocType missing: {row.get('doctype')}")
        if row.get("can_read") is not True:
            failures.append(f"maintenance role cannot read {row.get('doctype')}")
    for row in result.get("forbidden_doctypes") or []:
        if row.get("can_read") is True:
            failures.append(f"maintenance role can read forbidden DocType {row.get('doctype')}")
    if result.get("ok") is not True:
        failures.append("boundary_report returned ok=false")
    return sorted(set(failures))


def _parse_json_stdout(stdout: str) -> dict[str, Any]:
    text = stdout.strip()
    if not text:
        raise MaintenanceBoundaryFail("boundary report returned no output")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise MaintenanceBoundaryFail(f"boundary report returned non-JSON output: {text}") from None
        try:
            parsed = json.loads(text[start : end + 1])
        except json.JSONDecodeError as exc:
            raise MaintenanceBoundaryFail(f"boundary report returned non-JSON output: {text}") from exc
    if not isinstance(parsed, dict):
        raise MaintenanceBoundaryFail(f"boundary report returned {type(parsed).__name__}, expected object")
    return parsed


if __name__ == "__main__":
    sys.exit(main())
