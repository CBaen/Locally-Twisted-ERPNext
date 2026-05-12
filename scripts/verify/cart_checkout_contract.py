#!/usr/bin/env python3
"""Verify the LT guest cart contract for templates, variants, and single SKUs.

This is intentionally narrower than smoke_shop.py. It checks the launch-critical
purchase contract:

- Retail single-SKU products still resolve normally.
- Ready-to-order variant item codes can be summarized for cart display, using the
  parent Website Item for display route/image and the variant Item Price.
- Quote-first product page variants are rejected from cart before checkout so
  complex decor cannot be sold through the retail lane.
- Variant templates are not added directly from /shop.
- Server checkout rejects direct POST quantities above the browser cart cap
  with customer-safe failure copy.

Run:
  python scripts/verify/cart_checkout_contract.py
"""
from __future__ import annotations

import json
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Any

from _cli import parse_noop_args


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
BASE = "http://localhost:8081"
ROOT = Path(__file__).resolve().parents[2]

QUOTE_VARIANT_TEMPLATE = "6-color-rainbow-arch"
QUOTE_VARIANT_ITEM = "6-color-rainbow-arch-20F"
QUOTE_SINGLE_SKU_ITEM = "easter-arch"
RETAIL_VARIANT_TEMPLATE = "unicorn-bouquet"
RETAIL_VARIANT_ITEM = "unicorn-bouquet-SMA"
SINGLE_SKU_ITEM = "mothers-day-bouquet"
PRICE_LIST = "Standard Selling"
MAX_QTY_PER_LINE = 99
CONFIG_VERSION = "lt-product-config-v1"
FOIL_NUMBER_ADD_ON_ITEM = "ADDON-FOIL-NUMBER"


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


def check_cart_api_routes_ready_to_order_and_blocks_quote_first() -> None:
    data = bench_execute(
        "locally_twisted.api.cart.get_cart_items",
        kwargs={"item_codes": [RETAIL_VARIANT_ITEM, QUOTE_VARIANT_ITEM, SINGLE_SKU_ITEM, QUOTE_VARIANT_TEMPLATE]},
    )

    items = by_item_code(data.get("items") or [])
    missing = {row["item_code"]: row.get("reason") for row in data.get("missing") or []}

    assert_true(SINGLE_SKU_ITEM in items, f"{SINGLE_SKU_ITEM} should still resolve as a cart item")
    assert_true(RETAIL_VARIANT_ITEM in items, f"{RETAIL_VARIANT_ITEM} should resolve as a retail variant cart item")
    assert_true(
        QUOTE_VARIANT_TEMPLATE in missing,
        f"{QUOTE_VARIANT_TEMPLATE} should not resolve as a directly purchasable template",
    )
    assert_true(
        missing.get(QUOTE_VARIANT_ITEM) == "quote_required",
        f"{QUOTE_VARIANT_ITEM} should be rejected from cart as quote_required, found {missing.get(QUOTE_VARIANT_ITEM)!r}",
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


def check_checkout_resolver_accepts_retail_variant() -> None:
    line = bench_execute(
        "locally_twisted.api.cart.resolve_cart_item_for_sale",
        kwargs={"item_code": RETAIL_VARIANT_ITEM},
    )
    assert_true(line.get("item_code") == RETAIL_VARIANT_ITEM, "checkout resolver should preserve retail variant item code")
    assert_true(float(line.get("price_list_rate") or 0) == 35.0, "checkout resolver should use retail variant price")
    assert_true(line.get("website_item_code") == RETAIL_VARIANT_TEMPLATE, "checkout resolver should point at parent Website Item")
    assert_true(line.get("checkout_lane") == "retail_checkout", "checkout resolver should expose retail lane")


def _foil_number_configuration(value: str) -> dict[str, Any]:
    line = bench_execute(
        "locally_twisted.api.cart.resolve_cart_item_for_sale",
        kwargs={"item_code": RETAIL_VARIANT_ITEM},
    )
    selected_options = {
        str(row.get("attribute")): str(row.get("attribute_value"))
        for row in line.get("variant_options") or []
        if row.get("attribute") and row.get("attribute_value")
    }
    return {
        "schema_version": CONFIG_VERSION,
        "item_code": RETAIL_VARIANT_ITEM,
        "website_item_code": RETAIL_VARIANT_TEMPLATE,
        "selected_options": selected_options,
        "add_ons": [
            {
                "key": "foil_number",
                "label": "Foil number",
                "value": value,
                "quantity": len(value),
            }
        ],
        "customizations": [],
    }


def _ineligible_foil_number_configuration(value: str) -> dict[str, Any]:
    return {
        "schema_version": CONFIG_VERSION,
        "item_code": SINGLE_SKU_ITEM,
        "website_item_code": SINGLE_SKU_ITEM,
        "selected_options": {},
        "add_ons": [
            {
                "key": "foil_number",
                "label": "Foil number",
                "value": value,
                "quantity": len(value),
            }
        ],
        "customizations": [],
    }


def _review_only_add_on_configuration() -> dict[str, Any]:
    line = bench_execute(
        "locally_twisted.api.cart.resolve_cart_item_for_sale",
        kwargs={"item_code": RETAIL_VARIANT_ITEM},
    )
    selected_options = {
        str(row.get("attribute")): str(row.get("attribute_value"))
        for row in line.get("variant_options") or []
        if row.get("attribute") and row.get("attribute_value")
    }
    return {
        "schema_version": CONFIG_VERSION,
        "item_code": RETAIL_VARIANT_ITEM,
        "website_item_code": RETAIL_VARIANT_TEMPLATE,
        "selected_options": selected_options,
        "add_ons": [
            {
                "key": "plush_add_ons",
                "label": "Plush add ons",
                "value": "Teddy bear",
                "quantity": 1,
            }
        ],
        "customizations": [],
    }


def check_configured_same_sku_cart_lines_stay_separate_and_visible() -> None:
    cart_entries = [
        {"item_code": RETAIL_VARIANT_ITEM, "qty": 1, "configuration": _foil_number_configuration("5")},
        {"item_code": RETAIL_VARIANT_ITEM, "qty": 1, "configuration": _foil_number_configuration("8")},
    ]
    data = bench_execute(
        "locally_twisted.api.cart.get_cart_items",
        kwargs={"item_codes": cart_entries},
    )
    items = data.get("items") or []
    assert_true(len(items) == 2, f"same SKU with different configurations should return 2 cart rows, found {len(items)}")

    line_keys = [row.get("cart_line_key") for row in items]
    assert_true(len(set(line_keys)) == 2, f"configured cart rows should have distinct line keys, found {line_keys}")
    for row in items:
        display_lines = row.get("display_lines") or []
        add_on_rows = [line for line in display_lines if line.get("is_add_on")]
        assert_true(len(display_lines) == 2, f"configured cart row should show base + add-on display lines, found {display_lines}")
        assert_true(len(add_on_rows) == 1, f"configured cart row should show one add-on row, found {display_lines}")
        assert_true(
            add_on_rows[0].get("item_code") == FOIL_NUMBER_ADD_ON_ITEM,
            f"add-on display row should use {FOIL_NUMBER_ADD_ON_ITEM}, found {add_on_rows[0]}",
        )
        assert_true(
            float(add_on_rows[0].get("price_list_rate") or 0) == 12.0,
            f"foil-number add-on display row should show $12, found {add_on_rows[0]}",
        )
        assert_true(
            int(add_on_rows[0].get("qty") or 0) == 1,
            f"single foil-number add-on display row should expose qty 1, found {add_on_rows[0]}",
        )
        assert_true(
            float(add_on_rows[0].get("line_total") or 0) == 12.0,
            f"single foil-number add-on display row should expose line_total $12, found {add_on_rows[0]}",
        )
        assert_true(
            float(row.get("line_total") or 0) == 47.0,
            f"configured cart row line_total should include $35 base + $12 add-on, found {row.get('line_total')}",
        )

    resolved = bench_execute(
        "locally_twisted.www.checkout._resolve_cart_items",
        kwargs={"item_code": "", "qty": 1, "items_json": json.dumps(cart_entries)},
    )
    assert_true(
        len(resolved) == 2,
        f"checkout cart resolver should not collapse same SKU with different configurations, found {resolved}",
    )


def check_multi_digit_add_on_quantity_and_total_are_visible() -> None:
    cart_entries = [
        {"item_code": RETAIL_VARIANT_ITEM, "qty": 1, "configuration": _foil_number_configuration("12")},
    ]
    data = bench_execute(
        "locally_twisted.api.cart.get_cart_items",
        kwargs={"item_codes": cart_entries},
    )
    items = data.get("items") or []
    assert_true(len(items) == 1, f"configured multi-digit add-on cart row should return 1 row, found {items}")
    add_on_rows = [
        line
        for line in (items[0].get("display_lines") or [])
        if line.get("is_add_on")
    ]
    assert_true(len(add_on_rows) == 1, f"multi-digit add-on should show one add-on display row, found {items}")
    add_on = add_on_rows[0]
    assert_true(add_on.get("display_label") == "Foil number: 12", f"add-on label should preserve selected value, found {add_on}")
    assert_true(int(add_on.get("qty") or 0) == 2, f"foil number 12 should display add-on qty 2, found {add_on}")
    assert_true(float(add_on.get("line_total") or 0) == 24.0, f"foil number 12 should display add-on total $24, found {add_on}")
    assert_true(float(items[0].get("line_total") or 0) == 59.0, f"line total should include $35 + $24, found {items[0]}")


def check_cart_line_key_matches_browser_unicode_serialization() -> None:
    configuration = _foil_number_configuration("5")
    configuration["selected_options"]["Bouquet Size"] = "Small \u2014 launch proof label"
    line_key = bench_execute(
        "locally_twisted.product_page_runtime.cart_line_key",
        kwargs={"item_code": RETAIL_VARIANT_ITEM, "client_configuration": configuration},
    )
    assert_true(
        "\\u2014" not in line_key,
        f"server cart_line_key should match browser JSON.stringify Unicode output, found {line_key!r}",
    )


def check_cart_and_checkout_templates_fail_loud_on_line_key_mismatch() -> None:
    cart_template = (ROOT / "apps/locally_twisted/locally_twisted/www/lt_cart.html").read_text(encoding="utf-8")
    checkout_template = (ROOT / "apps/locally_twisted/locally_twisted/www/checkout.html").read_text(encoding="utf-8")

    for label, source in (("/cart", cart_template), ("/checkout", checkout_template)):
        assert_true(
            "|| byCode[line.item_code]" not in source,
            f"{label} must not fall back from configured line_key to item_code; that can render the wrong configured line",
        )
        assert_true(
            "configured cart line did not match the server" in source,
            f"{label} must show a loud customer-safe line-key mismatch state",
        )
        assert_true(
            "formatDisplayLine" in source,
            f"{label} must use the shared display-line formatter for add-on qty and totals",
        )
        assert_true(
            ".line_total" in source and ".qty" in source,
            f"{label} add-on formatter must expose add-on qty and line total, not only unit price",
        )


def check_product_page_color_selector_uses_recipe_schema() -> None:
    item_configure = (
        ROOT / "apps/locally_twisted/locally_twisted/templates/generators/item/item_configure.html"
    ).read_text(encoding="utf-8")

    assert_true(
        'type="checkbox"' in item_configure and "selectedColorRecipeRows" in item_configure,
        "color selector must allow multi-color recipe selection, not only a single radio choice",
    )
    assert_true(
        "color_recipes: selectedColorRecipeRows()" in item_configure,
        "configured cart payload must include color_recipes",
    )
    assert_true(
        "selected_options: selectedSaleUnitAttrs()" in item_configure,
        "configured cart payload must exclude color axes from selected_options",
    )
    assert_true(
        "selected_options: selectedAttrs()" not in item_configure,
        "single-select color selected_options payload must not pass checkout readiness",
    )


def check_add_on_eligibility_rejects_unapproved_product() -> None:
    expected = "this add-on is not available for this product"
    bench_execute_expect_error(
        "locally_twisted.www.checkout._resolve_sale_lines",
        kwargs={
            "cart_items": [
                {
                    "item_code": SINGLE_SKU_ITEM,
                    "qty": 1,
                    "configuration": _ineligible_foil_number_configuration("7"),
                }
            ]
        },
        expected=expected,
    )


def check_review_only_source_add_ons_route_to_quote_not_checkout() -> None:
    expected = "this add-on needs a quote before checkout"
    bench_execute_expect_error(
        "locally_twisted.www.checkout._resolve_sale_lines",
        kwargs={
            "cart_items": [
                {
                    "item_code": RETAIL_VARIANT_ITEM,
                    "qty": 1,
                    "configuration": _review_only_add_on_configuration(),
                }
            ]
        },
        expected=expected,
    )


def check_checkout_rejects_over_limit_quantities() -> None:
    expected = f"Tiny snag: one cart line has more than {MAX_QTY_PER_LINE} items."
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
    if "Ready-to-order is paused" in html:
        assert_true(
            "data-item-code=" not in html,
            "/shop pause page must not expose add-to-cart buttons while ecommerce is blocked",
        )
        return
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
    parse_noop_args(__doc__)
    checks = [
        check_cart_api_routes_ready_to_order_and_blocks_quote_first,
        check_checkout_resolver_accepts_retail_variant,
        check_configured_same_sku_cart_lines_stay_separate_and_visible,
        check_multi_digit_add_on_quantity_and_total_are_visible,
        check_cart_line_key_matches_browser_unicode_serialization,
        check_cart_and_checkout_templates_fail_loud_on_line_key_mismatch,
        check_product_page_color_selector_uses_recipe_schema,
        check_add_on_eligibility_rejects_unapproved_product,
        check_review_only_source_add_ons_route_to_quote_not_checkout,
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
