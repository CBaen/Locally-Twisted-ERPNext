#!/usr/bin/env python3
"""Verify LT payment backend configuration.

Run:
  python scripts/verify/payment_backend_config_contract.py
"""
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
    try:
        result = bench_execute("locally_twisted.verify.payment_backend_config_contract.run")
    except ContractFail as exc:
        print(f"[PAYMENT BACKEND CONFIG CONTRACT] FAIL\n  - {exc}")
        return 1

    if not result or not result.get("ok"):
        print("[PAYMENT BACKEND CONFIG CONTRACT] FAIL")
        for failure in (result or {}).get("failures") or ["Verifier returned no result"]:
            print(f"  - {failure}")
        for warning in (result or {}).get("warnings") or []:
            print(f"  warning: {warning}")
        return 1

    print("[PAYMENT BACKEND CONFIG CONTRACT] PASS")
    for key in [
        "stripe_settings_name",
        "payment_gateway_account",
        "stripe_payment_method_configuration",
        "operator_email",
        "webhook_secret_configured",
    ]:
        print(f"  {key}: {result.get(key)}")
    for warning in result.get("warnings") or []:
        print(f"  warning: {warning}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
