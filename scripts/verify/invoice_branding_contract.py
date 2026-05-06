#!/usr/bin/env python3
"""Verify the LT branded Sales Invoice print format and rendered output."""
from __future__ import annotations

import json
import subprocess
import sys
from typing import Any


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.verify.invoice_branding_contract.run"


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
    try:
        result = bench_execute(METHOD)
    except ContractFail as exc:
        print(f"[INVOICE BRANDING CONTRACT] FAIL\n  - {exc}")
        return 1

    if not result or not result.get("ok"):
        print("[INVOICE BRANDING CONTRACT] FAIL")
        for failure in (result or {}).get("failures") or ["Verifier returned no result"]:
            print(f"  - {failure}")
        return 1

    evidence = result.get("evidence") or {}
    print("[INVOICE BRANDING CONTRACT] PASS")
    print(f"  print_format: {evidence.get('print_format_name')}")
    print(f"  letter_head: {evidence.get('letter_head_name')}")
    print(f"  default_print_format: {evidence.get('meta_default_print_format')}")
    print(f"  sample_invoice: {evidence.get('sample_invoice')}")
    print(f"  rendered_length: {evidence.get('rendered_length')}")
    print(f"  default_rendered_length: {evidence.get('default_rendered_length')}")
    print(f"  logo_asset_exists: {evidence.get('logo_asset_exists')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
