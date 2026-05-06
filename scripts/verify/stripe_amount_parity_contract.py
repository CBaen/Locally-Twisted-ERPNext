#!/usr/bin/env python3
"""Verify Stripe Checkout Session line items match ERPNext order totals."""
from __future__ import annotations

import json
import subprocess
import sys
from typing import Any


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.verify.stripe_amount_parity_contract.run"


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
        print(f"[STRIPE AMOUNT PARITY CONTRACT] FAIL\n  - {exc}")
        return 1

    if not result or not result.get("ok"):
        print("[STRIPE AMOUNT PARITY CONTRACT] FAIL")
        for failure in (result or {}).get("failures") or ["Verifier returned no result"]:
            print(f"  - {failure}")
        return 1

    evidence = result.get("evidence") or {}
    print("[STRIPE AMOUNT PARITY CONTRACT] PASS")
    print(f"  taxable_order_cents: {evidence.get('taxable_order_cents')}")
    print(f"  taxable_stripe_cents: {evidence.get('taxable_stripe_cents')}")
    print(f"  nontaxable_order_cents: {evidence.get('nontaxable_order_cents')}")
    print(f"  negative_adjustment_rejected: {evidence.get('negative_adjustment_rejected')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
