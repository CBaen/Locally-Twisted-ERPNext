#!/usr/bin/env python3
"""Verify LT external marketing review access is website-only."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.verify.marketing_review_access_boundary.run"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true", help="Print the full verifier payload")
    args = parser.parse_args()

    try:
        result = bench_execute()
    except Exception as exc:
        print("[MARKETING REVIEW ACCESS BOUNDARY] FAIL")
        print(f"  - {exc}")
        return 1

    failures = result.get("failures") or []
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, default=str))
    else:
        print("[MARKETING REVIEW ACCESS BOUNDARY] " + ("PASS" if not failures else "FAIL"))
        print(f"  role: {result.get('role')}")
        print(f"  review_route_context: {result.get('review_route_context')}")
        print(f"  forbidden_doctypes_checked: {len(result.get('forbidden_doctypes_checked') or [])}")
        print("  rollback: verifier rolled back the temporary marketing user")
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
        timeout=120,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"bench execute failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    return _parse_json_stdout(proc.stdout)


def _parse_json_stdout(stdout: str) -> dict[str, Any]:
    text = stdout.strip()
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
