#!/usr/bin/env python3
"""Verify owner phone/action API is scoped, local-safe, and provider-neutral."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.verify.owner_business_access_contract.run"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print the full verifier payload")
    args = parser.parse_args()

    try:
        result = bench_execute()
    except Exception as exc:
        print("[OWNER BUSINESS ACCESS CONTRACT] FAIL")
        print(f"  - {exc}")
        return 1

    failures = result.get("failures") or []
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, default=str))
    else:
        print("[OWNER BUSINESS ACCESS CONTRACT] " + ("PASS" if not failures and result.get("ok") else "FAIL"))
        print(f"  owner_user: {result.get('owner_user')}")
        print(f"  provider_neutral: {result.get('provider_neutral')}")
        print(f"  customer_send_allowed: {result.get('customer_send_allowed')}")
        print(f"  write_surfaces: {', '.join(result.get('write_surfaces') or [])}")
        print("  rollback: verifier cleaned up temporary owner-action records")
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
