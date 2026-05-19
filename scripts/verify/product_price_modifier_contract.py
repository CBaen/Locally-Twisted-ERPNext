#!/usr/bin/env python3
"""Verify ERPNext variant prices match Odoo option price modifiers.

Run:
  python scripts/verify/product_price_modifier_contract.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from typing import Any

from _cli import parse_noop_args


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
METHOD = "locally_twisted.seed.repair_variant_price_modifiers_from_odoo.execute"


class ContractFail(Exception):
    pass


def bench_execute(method: str, *, kwargs: dict[str, Any] | None = None, timeout: int = 900) -> Any:
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
        cmd.extend(["--kwargs", repr(kwargs)])

    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
    if proc.returncode != 0:
        raise ContractFail(
            f"bench execute failed for {method}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    text = proc.stdout.strip()
    if not text:
        return None
    try:
        parsed = json.loads(text)
        if isinstance(parsed, str):
            parsed = json.loads(parsed)
        return parsed
    except json.JSONDecodeError as exc:
        raise ContractFail(f"{method} returned non-JSON output: {text}") from exc


def check_no_odoo_price_modifier_drift() -> None:
    data = bench_execute(METHOD, kwargs={"dry_run": True, "strict": False})
    errors = data.get("errors") or []
    if errors:
        details = "; ".join(f"{row.get('template')}: {row.get('error')}" for row in errors)
        raise ContractFail(f"Odoo price modifier probe had errors: {details}")

    products_checked = int(data.get("products_checked") or 0)
    variants_checked = int(data.get("variants_checked") or 0)
    variants_that_would_change = int(data.get("variants_that_would_change") or 0)

    if products_checked < 45:
        raise ContractFail(f"expected broad variant catalog coverage, checked only {products_checked} products")
    if variants_checked < 10000:
        raise ContractFail(f"expected 10k+ active variants checked, got {variants_checked}")
    if variants_that_would_change:
        raise ContractFail(f"{variants_that_would_change} variant prices still differ from Odoo modifiers")

    print(
        "[PASS] Odoo price modifiers match ERPNext Item Prices "
        f"for {products_checked} products / {variants_checked} active variants"
    )


def main() -> int:
    parse_noop_args(__doc__)
    try:
        check_no_odoo_price_modifier_drift()
    except Exception as exc:
        print(f"[FAIL] check_no_odoo_price_modifier_drift: {exc}")
        print("\n[PRODUCT PRICE MODIFIER CONTRACT] FAIL")
        return 1

    print("\n[PRODUCT PRICE MODIFIER CONTRACT] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
