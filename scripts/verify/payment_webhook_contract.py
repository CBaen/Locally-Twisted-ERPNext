#!/usr/bin/env python3
"""Verify LT Stripe webhook event handling.

Run:
  python scripts/verify/payment_webhook_contract.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from typing import Any

from _cli import parse_noop_args


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"


class ContractFail(Exception):
    pass


def bench_execute(method: str, *, kwargs: dict[str, Any] | None = None) -> Any:
    cmd = [
        "docker",
        "exec",
        CONTAINER,
        "bench",
        "--site",
        SITE,
        "execute",
        method,
    ]
    if kwargs is not None:
        cmd.extend(["--kwargs", json.dumps(kwargs)])

    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=60)
    if proc.returncode != 0:
        raise ContractFail(
            f"bench execute failed for {method}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )

    text = proc.stdout.strip()
    if not text:
        return None

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ContractFail(f"{method} returned non-JSON output: {text}") from exc


def main() -> int:
    parse_noop_args(__doc__)
    try:
        result = bench_execute("locally_twisted.verify.payment_webhook_contract.run")
    except ContractFail as exc:
        print(f"[PAYMENT WEBHOOK CONTRACT] FAIL\n  - {exc}")
        return 1

    if not result or not result.get("ok"):
        print("[PAYMENT WEBHOOK CONTRACT] FAIL")
        for failure in (result or {}).get("failures") or ["Verifier returned no result"]:
            print(f"  - {failure}")
        return 1

    print("[PAYMENT WEBHOOK CONTRACT] PASS")
    print(f"  unpaid_completed: {result.get('unpaid_completed')}")
    print(f"  async_payment_succeeded_calls: {result.get('async_payment_succeeded_calls')}")
    print(f"  ignored_event: {result.get('ignored_event')}")
    print(f"  non_lt_checkout: {result.get('non_lt_checkout')}")
    print(f"  missing_payment_request_status_code: {result.get('missing_payment_request_status_code')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
