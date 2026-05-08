#!/usr/bin/env python3
"""Verify the LT outbound document registry and source templates."""
from __future__ import annotations

import json
import subprocess
import sys
from typing import Any

from _cli import parse_noop_args


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.verify.outbound_documents_contract.run"


class ContractFail(Exception):
    pass


def bench_execute(method: str) -> Any:
    proc = subprocess.run(
        ["docker", "exec", CONTAINER, "bench", "--site", SITE, "execute", method],
        text=True,
        capture_output=True,
        timeout=60,
    )
    if proc.returncode != 0:
        raise ContractFail(
            f"bench execute failed for {method}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )

    text = proc.stdout.strip()
    if not text:
        raise ContractFail(f"{method} returned no output")

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ContractFail(f"{method} returned non-JSON output: {text}") from exc


def main() -> int:
    parse_noop_args(__doc__)
    try:
        result = bench_execute(METHOD)
    except ContractFail as exc:
        print(f"[OUTBOUND DOCUMENTS CONTRACT] FAIL\n  - {exc}")
        return 1

    if not result or not result.get("ok"):
        print("[OUTBOUND DOCUMENTS CONTRACT] FAIL")
        for failure in (result or {}).get("failures") or ["Verifier returned no result"]:
            print(f"  - {failure}")
        return 1

    evidence = result.get("evidence") or {}
    print("[OUTBOUND DOCUMENTS CONTRACT] PASS")
    print(f"  document_count: {evidence.get('document_count')}")
    print(f"  template_dir: {evidence.get('template_dir')}")
    print(f"  documents: {', '.join(evidence.get('document_ids') or [])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
