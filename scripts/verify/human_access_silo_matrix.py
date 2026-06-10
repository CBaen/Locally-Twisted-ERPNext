#!/usr/bin/env python3
"""Verify LT human access groups, landing pages, and data silos."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.verify.human_access_silo_matrix.run"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print the full access matrix payload")
    args = parser.parse_args()

    try:
        result = bench_execute()
    except Exception as exc:
        print("[HUMAN ACCESS SILO MATRIX] FAIL")
        print(f"  - {exc}")
        return 1

    failures = result.get("failures") or []
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, default=str))
    else:
        matrix = result.get("matrix") or {}
        print("[HUMAN ACCESS SILO MATRIX] " + ("PASS" if result.get("ok") and not failures else "FAIL"))
        print(f"  admin_users: {len((matrix.get('admin') or {}).get('users') or {})}")
        print(f"  owner_users: {len((matrix.get('owner') or {}).get('users') or {})}")
        print(f"  desk_personas: {len((matrix.get('desk_personas') or {}).get('users') or {})}")
        print(f"  workspaces_checked: {len(matrix.get('workspaces') or {})}")
        external = matrix.get("external_marketing") or {}
        print(f"  external_marketing: {external.get('role')} desk_access={external.get('desk_access')}")
        external_builder = matrix.get("external_marketing_builder") or {}
        print(
            "  external_marketing_builder: "
            f"{external_builder.get('role')} desk_access={external_builder.get('desk_access')}"
        )
        indexing = matrix.get("indexing") or {}
        print(f"  indexing: {indexing.get('status')}")

    if failures:
        print("  failures:")
        for failure in failures:
            print(f"    - {failure}")
        return 1
    return 0


def bench_execute() -> dict[str, Any]:
    proc = subprocess.run(
        ["docker", "exec", CONTAINER, "bench", "--site", SITE, "execute", METHOD],
        text=True,
        capture_output=True,
        timeout=180,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"bench execute failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    text = proc.stdout.strip()
    if not text:
        raise RuntimeError("verifier returned no output")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        if start == -1:
            raise RuntimeError(f"verifier returned non-JSON output: {text}") from None
        parsed, _ = json.JSONDecoder().raw_decode(text[start:])
    if not isinstance(parsed, dict):
        raise RuntimeError(f"verifier returned {type(parsed).__name__}, expected object")
    return parsed


if __name__ == "__main__":
    sys.exit(main())
