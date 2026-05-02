#!/usr/bin/env python3
"""Verify the LT guest cart contract for templates, variants, and single SKUs.

This is intentionally narrower than smoke_shop.py. It checks the launch-critical
purchase contract:

- Variant item codes resolve as purchasable cart lines, using the parent Website
  Item for display route/image and the variant Item Price for checkout price.
- Variant templates are not added directly from /shop cards.
- Single-SKU products still resolve normally.

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

VARIANT_TEMPLATE = "6-color-rainbow-arch"
VARIANT_ITEM = "6-color-rainbow-arch-20F"
SINGLE_SKU_ITEM = "easter-arch"
PRICE_LIST = "Standard Selling"


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


def check_cart_api_resolves_variant_and_single_sku() -> None:
    data = bench_execute(
        "locally_twisted.api.cart.get_cart_items",
        kwargs={"item_codes": [VARIANT_ITEM, SINGLE_SKU_ITEM, VARIANT_TEMPLATE]},
    )
    variant_media = bench_execute(
        "locally_twisted.api.variant_media.get_variant_media",
        kwargs={"item_code": VARIANT_ITEM, "template_item_code": VARIANT_TEMPLATE},
    )

    items = by_item_code(data.get("items") or [])
    missing = {row["item_code"]: row.get("reason") for row in data.get("missing") or []}

    assert_true(SINGLE_SKU_ITEM in items, f"{SINGLE_SKU_ITEM} should still resolve as a cart item")
    assert_true(VARIANT_ITEM in items, f"{VARIANT_ITEM} should resolve as a purchasable variant cart item")
    assert_true(
        VARIANT_TEMPLATE in missing,
        f"{VARIANT_TEMPLATE} should not resolve as a directly purchasable template",
    )

    variant = items[VARIANT_ITEM]
    assert_true(
        variant.get("route") == "shop-items/arches/6-color-rainbow-arch",
        f"{VARIANT_ITEM} should use parent Website Item route, found {variant.get('route')!r}",
    )
    assert_true(
        variant.get("website_image") == variant_media.get("image"),
        f"{VARIANT_ITEM} should use selected variant image when present, found {variant.get('website_image')!r}",
    )
    assert_true(
        float(variant.get("price_list_rate") or 0) == 340.0,
        f"{VARIANT_ITEM} should use its variant price 340.0, found {variant.get('price_list_rate')!r}",
    )


def check_checkout_resolver_accepts_variant() -> None:
    line = bench_execute(
        "locally_twisted.api.cart.resolve_cart_item_for_sale",
        kwargs={"item_code": VARIANT_ITEM},
    )
    assert_true(line.get("item_code") == VARIANT_ITEM, "checkout resolver should preserve variant item code")
    assert_true(float(line.get("price_list_rate") or 0) == 340.0, "checkout resolver should use variant price")
    assert_true(line.get("website_item_code") == VARIANT_TEMPLATE, "checkout resolver should point at parent Website Item")


def check_shop_cards_do_not_add_templates() -> None:
    html = get_url("/shop")
    assert_true(
        f'data-item-code="{VARIANT_TEMPLATE}"' not in html,
        f"/shop must not expose an add-to-cart button for template {VARIANT_TEMPLATE}",
    )
    assert_true(
        f'data-item-code="{SINGLE_SKU_ITEM}"' in html,
        f"/shop should keep add-to-cart available for single SKU {SINGLE_SKU_ITEM}",
    )
    assert_true("Choose options" in html, "/shop should link variant templates to option selection")


def main() -> int:
    checks = [
        check_cart_api_resolves_variant_and_single_sku,
        check_checkout_resolver_accepts_variant,
        check_shop_cards_do_not_add_templates,
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
