#!/usr/bin/env python3
"""Verify checkout conversion keeps Lead, Customer, order, and tasks aligned."""
from __future__ import annotations

import json
import subprocess
import sys
from typing import Any


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
    try:
        result = bench_execute("locally_twisted.verify.checkout_lead_conversion_contract.run")
    except ContractFail as exc:
        print(f"[CHECKOUT LEAD CONVERSION CONTRACT] FAIL\n  - {exc}")
        return 1

    if not result or not result.get("ok"):
        print("[CHECKOUT LEAD CONVERSION CONTRACT] FAIL")
        for failure in (result or {}).get("failures") or ["Verifier returned no result"]:
            print(f"  - {failure}")
        return 1

    print("[CHECKOUT LEAD CONVERSION CONTRACT] PASS")
    for key in [
        "lead",
        "contact",
        "customer",
        "sales_order",
        "payment_request",
        "lead_status",
        "pipeline_stage",
        "active_task_stage",
    ]:
        print(f"  {key}: {result.get(key)}")
    print("  rollback: verifier rolled back all generated records")
    return 0


if __name__ == "__main__":
    sys.exit(main())
