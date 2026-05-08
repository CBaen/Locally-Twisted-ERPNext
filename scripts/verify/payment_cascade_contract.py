#!/usr/bin/env python3
"""Verify the LT paid-order cascade without leaving test records behind.

Run:
  python scripts/verify/payment_cascade_contract.py
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

    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=90)
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
        result = bench_execute("locally_twisted.verify.payment_cascade_contract.run")
    except ContractFail as exc:
        print(f"[PAYMENT CASCADE CONTRACT] FAIL\n  - {exc}")
        return 1

    if not result or not result.get("ok"):
        print("[PAYMENT CASCADE CONTRACT] FAIL")
        for failure in (result or {}).get("failures") or ["Verifier returned no result"]:
            print(f"  - {failure}")
        return 1

    print("[PAYMENT CASCADE CONTRACT] PASS")
    for key in [
        "sales_order",
        "payment_request",
        "payment_entry",
        "sales_invoice",
        "receipt_email_queue",
        "operator_email_queue",
        "welcome_email_queue",
        "checkout_notes",
    ]:
        print(f"  {key}: {result.get(key)}")
    print("  rollback: verifier rolled back all generated records")
    return 0


if __name__ == "__main__":
    sys.exit(main())
