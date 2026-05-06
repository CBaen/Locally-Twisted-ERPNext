#!/usr/bin/env python3
"""Verify the LT guest cart contract for templates, variants, and single SKUs.

This is intentionally narrower than smoke_shop.py. It checks the launch-critical
purchase contract:

- Retail single-SKU products still resolve normally.
- Retail variant item codes can be summarized for cart display, using the
  parent Website Item for display route/image and the variant Item Price.
- Product groups do not create a quote-only cart failure. Delivery ZIP/city is
  the checkout quote gate, not the product group by itself.
- Variant templates are not added directly from /shop.
- Server checkout rejects direct POST quantities above the browser cart cap.

Run:
  python scripts/verify/cart_checkout_contract.py
"""
from __future__ import annotations

import json
import subprocess
import sys
import urllib.request
from typing import Any


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
BASE = "http://localhost:8081"

QUOTE_VARIANT_TEMPLATE = "6-color-rainbow-arch"
QUOTE_VARIANT_ITEM = "6-color-rainbow-arch-20F"
QUOTE_SINGLE_SKU_ITEM = "easter-arch"
RETAIL_VARIANT_TEMPLATE = "unicorn-bouquet"
RETAIL_VARIANT_ITEM = "unicorn-bouquet-SMA-12"
SINGLE_SKU_ITEM = "mothers-day-bouquet"
PRICE_LIST = "Standard Selling"
MAX_QTY_PER_LINE = 99


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


def bench_execute_expect_error(method: str, *, kwargs: dict[str, Any], expected: str) -> None:
    cmd = [
        "docker",
        "exec",
        CONTAINER,
        "bench",
        "--site",
        SITE,
        "execute",
        method,
        "--kwargs",
        json.dumps(kwargs),
    ]
    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=60)
    if proc.returncode == 0:
        raise ContractFail(f"{method} should have failed for {kwargs}, returned {proc.stdout.strip()!r}")
    combined = f"{proc.stdout}\n{proc.stderr}"
    if expected not in combined:
        raise ContractFail(
            f"{method} failed, but did not include {expected!r}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )


def get_url(path: str) -> str:
    req = urllib.request.Request(
        f"{BASE}{path}",
        headers={"User-Agent": "LT cart contract verifier"},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        if resp.status != 200:
            raise ContractFail(f"{path} returned HTTP {resp.status}")
        return resp.read().decode("utf-8", errors="replace")


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise ContractFail(message)


def by_item_code(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {item["item_code"]: item for item in items}


def check_cart_api_resolves_priced_items_without_product_quote_gate() -> None:
    data = bench_execute(
        "locally_twisted.api.cart.get_cart_items",
        kwargs={"item_codes": [RETAIL_VARIANT_ITEM, QUOTE_VARIANT_ITEM, SINGLE_SKU_ITEM, QUOTE_VARIANT_TEMPLATE]},
    )

    items = by_item_code(data.get("items") or [])
    missing = {row["item_code"]: row.get("reason") for row in data.get("missing") or []}

    assert_true(SINGLE_SKU_ITEM in items, f"{SINGLE_SKU_ITEM} should still resolve as a cart item")
    assert_true(RETAIL_VARIANT_ITEM in items, f"{RETAIL_VARIANT_ITEM} should resolve as a retail variant cart item")
    assert_true(
        QUOTE_VARIANT_ITEM in items,
        f"{QUOTE_VARIANT_ITEM} is priced and should not be rejected by product group as quote_required",
    )
    assert_true(
        QUOTE_VARIANT_TEMPLATE in missing,
        f"{QUOTE_VARIANT_TEMPLATE} should not resolve as a directly purchasable template",
    )

    single = items[SINGLE_SKU_ITEM]
    assert_true(
        single.get("checkout_lane") == "retail_checkout",
        f"{SINGLE_SKU_ITEM} should stay in retail checkout lane, found {single.get('checkout_lane')!r}",
    )

    variant = items[RETAIL_VARIANT_ITEM]
    assert_true(
        variant.get("route") == "shop-items/bouquets/unicorn-bouquet",
        f"{RETAIL_VARIANT_ITEM} should use parent Website Item route, found {variant.get('route')!r}",
    )
    assert_true(
        float(variant.get("price_list_rate") or 0) == 35.0,
        f"{RETAIL_VARIANT_ITEM} should use its variant price 35.0, found {variant.get('price_list_rate')!r}",
    )
    assert_true(
        variant.get("checkout_lane") == "retail_checkout",
        f"{RETAIL_VARIANT_ITEM} should be marked retail_checkout, found {variant.get('checkout_lane')!r}",
    )

    quoted_before = items[QUOTE_VARIANT_ITEM]
    assert_true(
        quoted_before.get("checkout_lane") == "retail_checkout",
        f"{QUOTE_VARIANT_ITEM} should be retail_checkout unless fulfillment details require a quote, found {quoted_before.get('checkout_lane')!r}",
    )


def check_checkout_resolver_accepts_retail_variant() -> None:
    line = bench_execute(
        "locally_twisted.api.cart.resolve_cart_item_for_sale",
        kwargs={"item_code": RETAIL_VARIANT_ITEM},
    )
    assert_true(line.get("item_code") == RETAIL_VARIANT_ITEM, "checkout resolver should preserve retail variant item code")
    assert_true(float(line.get("price_list_rate") or 0) == 35.0, "checkout resolver should use retail variant price")
    assert_true(line.get("website_item_code") == RETAIL_VARIANT_TEMPLATE, "checkout resolver should point at parent Website Item")
    assert_true(line.get("checkout_lane") == "retail_checkout", "checkout resolver should expose retail lane")


def check_checkout_rejects_over_limit_quantities() -> None:
    expected = f"Cart line quantity cannot exceed {MAX_QTY_PER_LINE}"
    bench_execute_expect_error(
        "locally_twisted.www.checkout._resolve_cart_items",
        kwargs={"item_code": SINGLE_SKU_ITEM, "qty": MAX_QTY_PER_LINE + 1, "items_json": ""},
        expected=expected,
    )
    bench_execute_expect_error(
        "locally_twisted.www.checkout._resolve_cart_items",
        kwargs={
            "item_code": "",
            "qty": 1,
            "items_json": json.dumps([{"item_code": SINGLE_SKU_ITEM, "qty": MAX_QTY_PER_LINE + 1}]),
        },
        expected=expected,
    )


def check_shop_cards_keep_priced_products_cartable_and_do_not_add_templates() -> None:
    html = get_url("/shop")
    assert_true(
        f'data-item-code="{QUOTE_VARIANT_TEMPLATE}"' not in html,
        f"/shop must not expose an add-to-cart button for template {QUOTE_VARIANT_TEMPLATE}",
    )
    assert_true(
        f'data-item-code="{QUOTE_SINGLE_SKU_ITEM}"' in html,
        f"/shop should keep priced single-SKU product {QUOTE_SINGLE_SKU_ITEM} cartable",
    )
    assert_true(
        f'data-item-code="{SINGLE_SKU_ITEM}"' in html,
        f"/shop should keep add-to-cart available for single SKU {SINGLE_SKU_ITEM}",
    )


def main() -> int:
    checks = [
        check_cart_api_resolves_priced_items_without_product_quote_gate,
        check_checkout_resolver_accepts_retail_variant,
        check_checkout_rejects_over_limit_quantities,
        check_shop_cards_keep_priced_products_cartable_and_do_not_add_templates,
    ]

    failures = []
    for check in checks:
        try:
            check()
            print(f"[PASS] {check.__name__}")
        except ContractFail as exc:
            failures.append(str(exc))
            print(f"[FAIL] {check.__name__}: {exc}")

    if failures:
        print("\n[CART CHECKOUT CONTRACT] FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("\n[CART CHECKOUT CONTRACT] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
