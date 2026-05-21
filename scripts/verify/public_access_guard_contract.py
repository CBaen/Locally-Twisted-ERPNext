#!/usr/bin/env python3
"""Verify LT public access settings and marketing review boundaries are guarded."""
from __future__ import annotations

import json
import subprocess
import sys
from typing import Any

from _cli import parse_noop_args


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.verify.public_access_guard_contract.run"


class ContractFail(Exception):
    pass


def main() -> int:
    parse_noop_args(__doc__)
    try:
        result = bench_execute()
    except ContractFail as exc:
        print("[PUBLIC ACCESS GUARD CONTRACT] FAIL")
        print(f"  - {exc}")
        return 1

    failures = result.get("failures") or []
    probes = result.get("probes") or []
    print("[PUBLIC ACCESS GUARD CONTRACT] " + ("PASS" if not failures else "FAIL"))
    print(f"  probes: {len([row for row in probes if row.get('ok')])}/{len(probes)} passed")
    for row in probes:
        status = "ok" if row.get("ok") else "fail"
        blocked = "blocked" if row.get("blocked") else "allowed"
        print(f"  - {row.get('probe')}: {status}, {blocked}")

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
        raise ContractFail(
            f"bench execute failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    text = proc.stdout.strip()
    if not text:
        raise ContractFail("verifier returned no output")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        if start == -1:
            raise ContractFail(f"verifier returned non-JSON output: {text}") from None
        parsed, _ = json.JSONDecoder().raw_decode(text[start:])
        if not isinstance(parsed, dict):
            raise ContractFail(f"verifier returned {type(parsed).__name__}, expected object")
        return parsed


if __name__ == "__main__":
    sys.exit(main())
