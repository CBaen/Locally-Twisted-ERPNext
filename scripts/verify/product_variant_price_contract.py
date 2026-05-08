#!/usr/bin/env python3
"""Verify launch-critical product variants keep their intended prices.

Run:
  python scripts/verify/product_variant_price_contract.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from decimal import Decimal
from typing import Any

from _cli import parse_noop_args


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
PRICE_LIST = "Standard Selling"

# Recovered from old Odoo via /website_sale/get_combination_info on 2026-05-08.
BOUQUET_TEMPLATES = (
    "elsa-bouquet",
    "encanto-bouquet",
    "flamingo-bouquet",
    "football-bouquet",
    "holy-cow-bouquet",
    "mickey-mouse-bouquet",
    "minion-bouquet",
    "over-the-hill-bouquet",
    "paw-patrol-bouquet",
    "soccer-bouquet",
    "space-bouquet",
    "stitch-bouquet",
    "unicorn-bouquet",
)
BOUQUET_SIZE_PRICES = {
    "SMA": Decimal("35.00"),
    "MED": Decimal("70.00"),
    "LAR": Decimal("85.00"),
}
EXPECTED_PRICES = {
    f"{template}-{suffix}": price
    for template in BOUQUET_TEMPLATES
    for suffix, price in BOUQUET_SIZE_PRICES.items()
}


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


def mariadb(sql: str) -> list[dict[str, str]]:
    cmd = [
        "docker",
        "exec",
        "-i",
        CONTAINER,
        "bench",
        "--site",
        SITE,
        "mariadb",
        "--batch",
        "--raw",
    ]
    proc = subprocess.run(cmd, input=sql, text=True, capture_output=True, timeout=60)
    if proc.returncode != 0:
        raise ContractFail(f"mariadb query failed\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")
    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    if not lines:
        return []
    headers = lines[0].split("\t")
    return [dict(zip(headers, line.split("\t"))) for line in lines[1:]]


def decimal_from(value: Any) -> Decimal:
    return Decimal(str(value or "0")).quantize(Decimal("0.01"))


def check_item_prices() -> None:
    quoted = ", ".join(f"'{item_code}'" for item_code in EXPECTED_PRICES)
    rows = mariadb(
        f"""
        select i.name as item_code, i.disabled, ip.price_list_rate
        from tabItem i
        left join `tabItem Price` ip
          on ip.item_code = i.name
         and ip.price_list = '{PRICE_LIST}'
         and ip.selling = 1
        where i.name in ({quoted})
        order by i.name;
        """
    )
    by_code = {row["item_code"]: row for row in rows}
    failures = []
    for item_code, expected in EXPECTED_PRICES.items():
        row = by_code.get(item_code)
        if not row:
            failures.append(f"{item_code} is missing")
            continue
        if row.get("disabled") != "0":
            failures.append(f"{item_code} must be active, found disabled={row.get('disabled')}")
        actual = decimal_from(row.get("price_list_rate"))
        if actual != expected:
            failures.append(f"{item_code} expected ${expected}, found ${actual}")

    distinct_prices = {decimal_from(row.get("price_list_rate")) for row in rows}
    if len(distinct_prices) < len(set(EXPECTED_PRICES.values())):
        failures.append("Bouquet variants collapsed to too few price points: " + ", ".join(
            f"${price}" for price in sorted(distinct_prices)
        ))

    if failures:
        raise ContractFail("; ".join(failures))


def check_cart_prices() -> None:
    data = bench_execute(
        "locally_twisted.api.cart.get_cart_items",
        kwargs={"item_codes": sorted(EXPECTED_PRICES)},
    )
    items = {row["item_code"]: row for row in data.get("items") or []}
    failures = []
    for item_code, expected in EXPECTED_PRICES.items():
        row = items.get(item_code)
        if not row:
            failures.append(f"{item_code} did not resolve through cart API")
            continue
        actual = decimal_from(row.get("price_list_rate"))
        if actual != expected:
            failures.append(f"{item_code} cart API expected ${expected}, found ${actual}")
    if failures:
        raise ContractFail("; ".join(failures))


def main() -> int:
    parse_noop_args(__doc__)
    checks = [check_item_prices, check_cart_prices]
    failures = []
    for check in checks:
        try:
            check()
            print(f"[PASS] {check.__name__}")
        except Exception as exc:
            failures.append(f"{check.__name__}: {exc}")
            print(f"[FAIL] {check.__name__}: {exc}")

    if failures:
        print("\n[PRODUCT VARIANT PRICE CONTRACT] FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("\n[PRODUCT VARIANT PRICE CONTRACT] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
