#!/usr/bin/env python3
"""Verify customer/operator email policy and attachment boundaries."""
from __future__ import annotations

import json
import subprocess
import sys
from typing import Any

from _cli import parse_noop_args

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.verify.customer_email_policy_contract.run"


class CustomerEmailPolicyContractFail(Exception):
    pass


def bench_execute() -> dict[str, Any]:
    proc = subprocess.run(
        ["docker", "exec", CONTAINER, "bench", "--site", SITE, "execute", METHOD],
        text=True,
        capture_output=True,
        timeout=90,
    )
    if proc.returncode != 0:
        raise CustomerEmailPolicyContractFail(
            f"bench execute failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    text = proc.stdout.strip()
    if not text:
        raise CustomerEmailPolicyContractFail("customer email policy contract returned no output")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise CustomerEmailPolicyContractFail(f"customer email policy contract returned non-JSON output: {text}") from exc
    if not isinstance(parsed, dict):
        raise CustomerEmailPolicyContractFail(
            f"customer email policy contract returned {type(parsed).__name__}, expected object"
        )
    return parsed


def main() -> int:
    parse_noop_args(__doc__)
    try:
        result = bench_execute()
    except CustomerEmailPolicyContractFail as exc:
        print(f"[CUSTOMER EMAIL POLICY CONTRACT] FAIL\n  - {exc}")
        return 1

    failures = _contract_failures(result)
    print("[CUSTOMER EMAIL POLICY CONTRACT] " + ("PASS" if result.get("ok") and not failures else "FAIL"))
    print(f"  checked_surfaces: {len(result.get('checked_surfaces') or [])}")
    for surface in result.get("checked_surfaces") or []:
        print(f"    - {surface.get('id')}: {'PASS' if surface.get('passed') else 'FAIL'}")
    all_failures = list(result.get("failures") or []) + failures
    if all_failures:
        print("  failures:")
        for failure in all_failures:
            print(f"    - {failure}")
    return 0 if result.get("ok") and not failures else 1


def _contract_failures(result: dict[str, Any]) -> list[str]:
    failures = []
    if result.get("read_only") is not True:
        failures.append("contract is not read-only")
    if result.get("send_allowed") is not False:
        failures.append("contract allows sending")
    if result.get("mutation_allowed") is not False:
        failures.append("contract allows mutations")
    if result.get("customer_delivery_enabled") is not False:
        failures.append("contract enables customer delivery")
    expected = {
        "lead_auto_ack",
        "lead_business_notification",
        "paid_order_receipt",
        "paid_order_operator_notification",
        "first_order_welcome",
        "paid_order_dynamic_contract",
    }
    found = {surface.get("id") for surface in result.get("checked_surfaces") or []}
    missing = sorted(expected - found)
    if missing:
        failures.append("missing checked surfaces: " + ", ".join(missing))
    for surface in result.get("checked_surfaces") or []:
        if surface.get("passed") is not True:
            failures.append(f"{surface.get('id')} failed")
    return failures


if __name__ == "__main__":
    sys.exit(main())
