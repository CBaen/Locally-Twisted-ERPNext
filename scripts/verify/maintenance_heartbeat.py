#!/usr/bin/env python3
"""Verify the sanitized client operations heartbeat contract."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.maintenance.heartbeat.run"

REQUIRED_EVENTS = {
    "public_boot_asset_map",
    "maintenance_scheduler",
    "client_notification_preferences",
    "maintenance_role_boundary",
}
REQUIRED_TOPICS = {
    "System Health",
    "New Leads",
    "Stale Leads",
    "Appointments",
    "Payments Paid",
    "Payments Late",
    "Documents Due",
    "Failed Automations",
    "Website Errors",
    "Security Events",
}


class MaintenanceHeartbeatFail(Exception):
    pass


def bench_execute(include_heavy: bool) -> dict[str, Any]:
    proc = subprocess.run(
        [
            "docker",
            "exec",
            CONTAINER,
            "bench",
            "--site",
            SITE,
            "execute",
            METHOD,
            "--kwargs",
            repr({"include_heavy": include_heavy, "write": False}),
        ],
        text=True,
        capture_output=True,
        timeout=120,
    )
    if proc.returncode != 0:
        raise MaintenanceHeartbeatFail(
            f"bench execute failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    return _parse_json_stdout(proc.stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--heavy", action="store_true", help="Include slower business digest checks")
    parser.add_argument("--json", action="store_true", help="Print the full heartbeat payload")
    args = parser.parse_args()

    try:
        result = bench_execute(include_heavy=args.heavy)
        failures = _contract_failures(result)
    except MaintenanceHeartbeatFail as exc:
        print(f"[MAINTENANCE HEARTBEAT] FAIL\n  - {exc}")
        return 1

    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print("[MAINTENANCE HEARTBEAT] " + ("PASS" if not failures else "FAIL"))
        print(f"  generated_at: {result.get('generated_at')}")
        print(f"  events: {len(result.get('events') or [])}")
        for event in result.get("events") or []:
            print(
                "    - "
                f"{event.get('component')}: {event.get('status')} "
                f"({event.get('safe_summary')})"
            )

    if failures:
        print("  failures:")
        for failure in failures:
            print(f"    - {failure}")
        return 1
    return 0


def _contract_failures(result: dict[str, Any]) -> list[str]:
    failures = []
    if result.get("digest_type") != "client_operations_heartbeat":
        failures.append("digest_type is not client_operations_heartbeat")
    for key, expected in {
        "read_only": True,
        "send_allowed": False,
        "mutation_allowed": False,
        "customer_delivery_enabled": False,
        "automatic_delivery_enabled": False,
        "sanitized": True,
        "raw_log_access": False,
        "customer_data_included": False,
    }.items():
        if result.get(key) is not expected:
            failures.append(f"{key} expected {expected}, found {result.get(key)}")

    topics = set(result.get("notification_topics_available") or [])
    missing_topics = sorted(REQUIRED_TOPICS - topics)
    if missing_topics:
        failures.append("missing notification topics: " + ", ".join(missing_topics))

    tier_by_number = {
        tier.get("tier"): tier for tier in result.get("permission_tiers") or []
    }
    for tier in range(5):
        if tier not in tier_by_number:
            failures.append(f"missing permission tier {tier}")
    if tier_by_number.get(4, {}).get("requires_approval") is not True:
        failures.append("permission tier 4 must require approval")
    if tier_by_number.get(4, {}).get("customer_delivery_allowed") is not True:
        failures.append("permission tier 4 must be the only live customer/data lane")

    events = result.get("events") or []
    event_ids = {event.get("component") for event in events}
    missing_events = sorted(REQUIRED_EVENTS - event_ids)
    if missing_events:
        failures.append("missing heartbeat events: " + ", ".join(missing_events))
    for event in events:
        if event.get("sanitized") is not True:
            failures.append(f"{event.get('component')} is not marked sanitized")
        if event.get("raw_log_access") is not False:
            failures.append(f"{event.get('component')} exposes raw log access")
        if event.get("customer_data_included") is not False:
            failures.append(f"{event.get('component')} includes customer data")

    summary = result.get("summary") or {}
    if summary.get("red_count", 0):
        failures.append(f"heartbeat has red event count {summary.get('red_count')}")
    if result.get("ok") is not True:
        failures.append("heartbeat returned ok=false")
    return failures


def _parse_json_stdout(stdout: str) -> dict[str, Any]:
    text = stdout.strip()
    if not text:
        raise MaintenanceHeartbeatFail("heartbeat returned no output")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise MaintenanceHeartbeatFail(f"heartbeat returned non-JSON output: {text}") from None
        try:
            parsed = json.loads(text[start : end + 1])
        except json.JSONDecodeError as exc:
            raise MaintenanceHeartbeatFail(f"heartbeat returned non-JSON output: {text}") from exc
    if not isinstance(parsed, dict):
        raise MaintenanceHeartbeatFail(f"heartbeat returned {type(parsed).__name__}, expected object")
    return parsed


if __name__ == "__main__":
    sys.exit(main())
