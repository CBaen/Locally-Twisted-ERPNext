#!/usr/bin/env python3
"""Verify fake no-live customer reminder dry-run scenarios.

Run:
  python scripts/verify/customer_reminder_dry_run_contract.py
  python scripts/verify/customer_reminder_dry_run_contract.py --json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.verify.customer_reminder_dry_run_contract.run"


class CustomerReminderDryRunContractFail(Exception):
    pass


def bench_execute() -> dict[str, Any]:
    proc = subprocess.run(
        ["docker", "exec", CONTAINER, "bench", "--site", SITE, "execute", METHOD],
        text=True,
        capture_output=True,
        timeout=90,
    )
    if proc.returncode != 0:
        raise CustomerReminderDryRunContractFail(
            f"bench execute failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    text = proc.stdout.strip()
    if not text:
        raise CustomerReminderDryRunContractFail("customer reminder dry-run contract returned no output")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise CustomerReminderDryRunContractFail(
            f"customer reminder dry-run contract returned non-JSON output: {text}"
        ) from exc
    if not isinstance(parsed, dict):
        raise CustomerReminderDryRunContractFail(
            f"customer reminder dry-run contract returned {type(parsed).__name__}, expected object"
        )
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true", help="Print full JSON report")
    args = parser.parse_args()

    try:
        result = bench_execute()
        failures = _contract_failures(result)
    except CustomerReminderDryRunContractFail as exc:
        print(f"[CUSTOMER REMINDER DRY RUN CONTRACT] FAIL\n  - {exc}")
        return 1

    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        _print_summary(result, failures)

    return 0 if result.get("ok") and not failures else 1


def _contract_failures(result: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    if result.get("read_only") is not True:
        failures.append("contract is not marked read_only")
    if result.get("send_allowed") is not False:
        failures.append("contract allows customer sending")
    if result.get("mutation_allowed") is not False:
        failures.append("contract allows accounting mutations")
    if result.get("customer_delivery_enabled") is not False:
        failures.append("contract enables customer delivery")
    expected = {
        "overdue_payment_reminder_review_ready",
        "severe_overdue_statement_review",
        "current_unpaid_hold_until_due",
        "missing_payment_path_blocks_send",
        "empty_digest_ok",
        "malformed_delivery_enabled_fails",
    }
    scenario_ids = {scenario.get("id") for scenario in result.get("scenarios") or []}
    missing = sorted(expected - scenario_ids)
    if missing:
        failures.append("missing scenarios: " + ", ".join(missing))
    for scenario in result.get("scenarios") or []:
        if scenario.get("passed") is not True:
            failures.append(f"{scenario.get('id')} did not pass")
    return failures


def _print_summary(result: dict[str, Any], contract_failures: list[str]) -> None:
    print(
        "[CUSTOMER REMINDER DRY RUN CONTRACT] "
        + ("PASS" if result.get("ok") and not contract_failures else "FAIL")
    )
    print(f"  scenario_count: {result.get('scenario_count')}")
    for scenario in result.get("scenarios") or []:
        print(f"    - {scenario.get('id')}: {'PASS' if scenario.get('passed') else 'FAIL'}")
    failures = list(result.get("failures") or []) + contract_failures
    if failures:
        print("  failures:")
        for failure in failures:
            print(f"    - {failure}")


if __name__ == "__main__":
    sys.exit(main())
