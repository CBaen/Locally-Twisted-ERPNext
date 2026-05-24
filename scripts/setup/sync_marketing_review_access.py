#!/usr/bin/env python3
"""Sync LT website-only external marketing review access."""
from __future__ import annotations

import json
import subprocess
import sys
from typing import Any


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.seed.sync_marketing_review_access.execute"


def main() -> int:
    try:
        result = bench_execute()
    except Exception as exc:
        print("[MARKETING REVIEW ACCESS SYNC] FAIL")
        print(f"  - {exc}")
        return 1

    failures = result.get("boundary_failures") or []
    print("[MARKETING REVIEW ACCESS SYNC] " + ("PASS" if not failures else "FAIL"))
    print(f"  ensured_role: {result.get('ensured_role')}")
    print(f"  removed_docperm_rows: {len(result.get('removed_docperm_rows') or [])}")
    print(f"  boundary_ok: {result.get('boundary_ok')}")
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
        timeout=90,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"bench execute failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    return _parse_json_stdout(proc.stdout)


def _parse_json_stdout(stdout: str) -> dict[str, Any]:
    text = stdout.strip()
    if not text:
        raise RuntimeError("sync returned no output")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        if start == -1:
            raise RuntimeError(f"sync returned non-JSON output: {text}") from None
        parsed, _ = json.JSONDecoder().raw_decode(text[start:])
        if not isinstance(parsed, dict):
            raise RuntimeError(f"sync returned {type(parsed).__name__}, expected object")
        return parsed


if __name__ == "__main__":
    sys.exit(main())
