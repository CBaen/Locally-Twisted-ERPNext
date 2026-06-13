#!/usr/bin/env python3
"""Sync LT marketing vendor user to review or builder access, with loud failure."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any

CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.marketing_vendor_access.execute"
DEFAULT_EMAIL = "marketing@exploringnotboring.com"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--email", default=DEFAULT_EMAIL)
    parser.add_argument("--mode", choices=("review", "builder"), default="builder")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    kwargs = {"email": args.email, "mode": args.mode, "commit": True}
    try:
        result = _bench_execute(kwargs)
    except Exception as exc:
        print("[MARKETING VENDOR ACCESS SYNC] FAIL")
        print(f"  - {exc}")
        return 1

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, default=str))
    else:
        print("[MARKETING VENDOR ACCESS SYNC] " + ("PASS" if result.get("ok") else "FAIL"))
        print(f"  email: {result.get('email')}")
        print(f"  mode: {result.get('mode')}")
        print(f"  expected_role: {result.get('expected_role')}")
        print(f"  expected_user_type: {result.get('expected_user_type')}")
        user = result.get("user") or {}
        if user:
            print(f"  current_user_type: {user.get('user_type')}")
            print(f"  current_roles: {', '.join(user.get('roles') or [])}")
        if result.get("removed_roles"):
            print(f"  removed_roles: {', '.join(result.get('removed_roles'))}")
        if result.get("added_roles"):
            print(f"  added_roles: {', '.join(result.get('added_roles'))}")
        failures = result.get("failures") or []
        if failures:
            print("  failures:")
            for failure in failures:
                print(f"    - {failure}")
    return 0 if result.get("ok") else 1


def _bench_execute(kwargs: dict[str, Any]) -> dict[str, Any]:
    proc = subprocess.run(
        ["docker", "exec", CONTAINER, "bench", "--site", SITE, "execute", METHOD, "--kwargs", repr(kwargs)],
        text=True,
        capture_output=True,
        timeout=180,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"bench execute failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
    return _parse_json_stdout(proc.stdout)


def _parse_json_stdout(stdout: str) -> dict[str, Any]:
    text = stdout.strip()
    if not text:
        raise RuntimeError("sync helper returned no output")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        if start == -1:
            raise RuntimeError(f"sync helper returned non-JSON output: {text}") from None
        parsed, _ = json.JSONDecoder().raw_decode(text[start:])
    if not isinstance(parsed, dict):
        raise RuntimeError(f"sync helper returned {type(parsed).__name__}, expected object")
    return parsed


if __name__ == "__main__":
    sys.exit(main())
