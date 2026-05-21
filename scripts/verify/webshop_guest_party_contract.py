#!/usr/bin/env python3
"""Verify LT's Webshop Guest party cleanup guard.

Run:
  python scripts/verify/webshop_guest_party_contract.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from typing import Any

from _cli import parse_noop_args


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.verify.webshop_guest_party_contract.run"


class ContractFail(Exception):
    pass


def bench_execute() -> dict[str, Any]:
    proc = subprocess.run(
        ["docker", "exec", CONTAINER, "bench", "--site", SITE, "execute", METHOD],
        text=True,
        capture_output=True,
        timeout=120,
    )
    if proc.returncode != 0:
        raise ContractFail(
            f"bench execute failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )

    text = proc.stdout.strip()
    if not text:
        raise ContractFail("verifier returned no output")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        if start == -1:
            raise ContractFail(f"verifier returned non-JSON output: {text}") from None
        parsed, _ = json.JSONDecoder().raw_decode(text[start:])
        if not isinstance(parsed, dict):
            raise ContractFail(f"verifier returned {type(parsed).__name__}, expected object")
        return parsed


def main() -> int:
    parse_noop_args(__doc__)
    try:
        result = bench_execute()
    except ContractFail as exc:
        print("[WEBSHOP GUEST PARTY CONTRACT] FAIL")
        print(f"  - {exc}")
        return 1

    failures = result.get("failures") or []
    warnings = result.get("warnings") or []
    evidence = result.get("evidence") or {}

    print("[WEBSHOP GUEST PARTY CONTRACT] " + ("PASS" if not failures else "FAIL"))
    print(f"  guest_user: {evidence.get('guest_user')}")
    print(f"  guest_roles: {evidence.get('guest_roles')}")
    print(f"  guest_customer: {evidence.get('guest_customer')}")
    print(f"  guest_portal_users: {len(evidence.get('guest_portal_users') or [])}")
    print(f"  guest_dynamic_links: {len(evidence.get('guest_dynamic_links') or [])}")
    print(f"  webshop_settings: {evidence.get('webshop_settings')}")
    probe = evidence.get("guest_variant_selector_probe") or {}
    print(
        "  variant_probe: "
        f"{probe.get('template_item_code')} exact_match={probe.get('exact_match')} "
        f"product_info={probe.get('has_product_info')}"
    )
    guard_probes = evidence.get("runtime_guard_probes") or []
    print(f"  runtime_guard_probes: {len([row for row in guard_probes if row.get('blocked')])}/{len(guard_probes)} blocked")

    for warning in warnings:
        print(f"  warning: {warning}")
    if failures:
        print("  failures:")
        for failure in failures:
            print(f"    - {failure}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
