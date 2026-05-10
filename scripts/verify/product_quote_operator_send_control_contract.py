#!/usr/bin/env python3
"""Verify the operator-owned product quote send control.

Run:
  python scripts/verify/product_quote_operator_send_control_contract.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from typing import Any

from _cli import parse_noop_args


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.verify.product_quote_operator_send_control_contract.run"


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

    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=120)
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
        result = bench_execute(METHOD)
    except ContractFail as exc:
        print(f"[PRODUCT QUOTE OPERATOR SEND CONTROL CONTRACT] FAIL\n  - {exc}")
        return 1

    if not result or not result.get("ok"):
        print("[PRODUCT QUOTE OPERATOR SEND CONTROL CONTRACT] FAIL")
        for failure in (result or {}).get("failures") or ["missing result"]:
            print(f"  - {failure}")
        return 1

    print("[PRODUCT QUOTE OPERATOR SEND CONTROL CONTRACT] PASS")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
