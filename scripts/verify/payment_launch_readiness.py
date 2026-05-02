#!/usr/bin/env python3
"""Verify LT payment launch-readiness without running a real checkout.

This is a structural/configuration check. It does not create orders, call
Stripe, submit a card, or print secret values.

Run:
  python scripts/verify/payment_launch_readiness.py
  python scripts/verify/payment_launch_readiness.py --mode live
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.request
from typing import Any


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
BASE_URL = "http://localhost:8081"


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


def route_status(path: str) -> int:
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        headers={"User-Agent": "LT payment launch readiness verifier"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return int(resp.status)
    except Exception as exc:
        raise ContractFail(f"{path} could not be reached at {BASE_URL}: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["local", "live"],
        default="local",
        help="local checks current dev readiness; live additionally requires explicit live-mode config keys",
    )
    args = parser.parse_args()

    try:
        result = bench_execute(
            "locally_twisted.verify.payment_launch_readiness.run",
            kwargs={"mode": args.mode},
        )
        route_results = {
            "/privacy": route_status("/privacy"),
            "/terms-of-service": route_status("/terms-of-service"),
        }
    except ContractFail as exc:
        print(f"[PAYMENT LAUNCH READINESS] FAIL\n  - {exc}")
        return 1

    failures = list((result or {}).get("failures") or [])
    warnings = list((result or {}).get("warnings") or [])
    for path, status in route_results.items():
        if status != 200:
            failures.append(f"{path} returned HTTP {status}, expected 200")

    if failures:
        print("[PAYMENT LAUNCH READINESS] FAIL")
        for failure in failures:
            print(f"  - {failure}")
        for warning in warnings:
            print(f"  warning: {warning}")
        return 1

    print("[PAYMENT LAUNCH READINESS] PASS")
    print(f"  mode: {args.mode}")
    for key in [
        "stripe_mode",
        "stripe_settings_name",
        "payment_gateway_account",
        "payment_gateway_currency",
        "webshop_checkout_enabled",
        "operator_email",
        "webhook_secret_configured",
        "outgoing_email_account",
    ]:
        print(f"  {key}: {result.get(key)}")
    for path, status in route_results.items():
        print(f"  route {path}: HTTP {status}")
    for warning in warnings:
        print(f"  warning: {warning}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
