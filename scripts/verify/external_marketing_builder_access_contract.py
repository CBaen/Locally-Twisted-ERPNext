#!/usr/bin/env python3
"""Verify LT controlled external marketing builder access."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
SYNC_METHOD = "locally_twisted.seed.sync_external_marketing_builder_access.execute"
VERIFY_METHOD = "locally_twisted.verify.external_marketing_builder_access_contract.run"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print full verifier payload")
    args = parser.parse_args()

    try:
        sync = _bench_execute(SYNC_METHOD)
        result = _bench_execute(VERIFY_METHOD)
    except Exception as exc:
        print("[EXTERNAL MARKETING BUILDER ACCESS] FAIL")
        print(f"  - {exc}")
        return 1

    failures = result.get("failures") or []
    if args.json:
        print(json.dumps({"sync": sync, "result": result}, indent=2, sort_keys=True, default=str))
    else:
        print("[EXTERNAL MARKETING BUILDER ACCESS] " + ("PASS" if not failures else "FAIL"))
        print(f"  role: {result.get('role')}")
        print(f"  workspace: {result.get('workspace')}")
        print(f"  tracking_settings: {result.get('tracking_settings_doctype')}")
    if failures:
        print("  failures:")
        for failure in failures:
            print(f"    - {failure}")
        return 1
    return 0


def _bench_execute(method: str) -> dict[str, Any]:
    proc = subprocess.run(
        ["docker", "exec", CONTAINER, "bench", "--site", SITE, "execute", method],
        text=True,
        capture_output=True,
        timeout=120,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"bench execute {method} failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
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
