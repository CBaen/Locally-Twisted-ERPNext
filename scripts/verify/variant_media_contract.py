#!/usr/bin/env python3
"""Verify product-template media contracts on the LT storefront.

This checks the layer-6 media contract: simple checkout variant images render
when the resolved Item has an approved customer image, while complex product
Item images stay held unless Product Setup media rules approve the selection.

Run:
  python scripts/verify/variant_media_contract.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import Any

from _cli import parse_noop_args
from playwright.sync_api import sync_playwright


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
BASE = "http://localhost:8081"

COMPLEX_TEMPLATE_ITEM = "classic-arch"
COMPLEX_VARIANT_ITEM = "classic-arch-20F-BLA-LAY-NOL"
SIMPLE_TEMPLATE_ITEM = "encanto-bouquet"
SIMPLE_PRODUCT_URL = f"{BASE}/shop-items/bouquets/encanto-bouquet"
SIMPLE_VARIANTS = {
    "Small": {
        "item_code": "encanto-bouquet-SMA",
        "image": "/files/encanto-bouquet-small.webp",
    },
    "Medium": {
        "item_code": "encanto-bouquet-MED",
        "image": "/files/encanto-bouquet-medium.webp",
    },
    "Large": {
        "item_code": "encanto-bouquet-LAR",
        "image": "/files/encanto-bouquet-large.webp",
    },
}
DESK_USER = os.environ.get("LT_DESK_TEST_USER") or "Administrator"
DESK_PASSWORD = os.environ.get("LT_DESK_TEST_PASSWORD") or "admin"


class VariantMediaFail(Exception):
    pass


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise VariantMediaFail(message)


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
        cmd.extend(["--kwargs", repr(kwargs)])

    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=60)
    if proc.returncode != 0:
        raise VariantMediaFail(
            f"bench execute failed for {method}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )

    text = proc.stdout.strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise VariantMediaFail(f"{method} returned non-JSON output: {text}") from exc


def check_complex_variant_media_api_holds_raw_item_image() -> dict[str, Any]:
    media = bench_execute(
        "locally_twisted.api.variant_media.get_variant_media",
        kwargs={"item_code": COMPLEX_VARIANT_ITEM, "template_item_code": COMPLEX_TEMPLATE_ITEM},
    )

    assert_true(media.get("item_code") == COMPLEX_VARIANT_ITEM, "variant media API returned the wrong item_code")
    assert_true(
        media.get("fallback_image") == "/files/classic-arch.png",
        f"fallback image should stay on the template, got {media.get('fallback_image')!r}",
    )
    assert_true(
        media.get("image") == media.get("fallback_image"),
        f"complex variant image should stay on fallback until Product Setup approves it, got {media.get('image')!r}",
    )
    assert_true(media.get("has_variant_image") is False, "complex raw variant image should not be marked renderable")
    assert_true(media.get("held_back_variant_image") is True, "source variant image should be reported as held back")
    assert_true(media.get("held_back_media_role") == "ignored_artifact", f"held variant image needs safe role, got {media}")
    assert_true(media.get("held_back_render_policy") == "hold_back", f"held variant image needs render policy, got {media}")
    assert_true(media.get("hold_reason"), "held variant image needs a hold reason")
    assert_true(media.get("media_role") == "primary", f"fallback image should report primary role, got {media}")
    return media


def check_simple_variant_media_api_uses_item_images() -> dict[str, Any]:
    checked = {}
    for label, expected in SIMPLE_VARIANTS.items():
        media = bench_execute(
            "locally_twisted.api.variant_media.get_variant_media",
            kwargs={"item_code": expected["item_code"], "template_item_code": SIMPLE_TEMPLATE_ITEM},
        )

        assert_true(media.get("item_code") == expected["item_code"], f"{label} media API returned the wrong item_code")
        assert_true(
            media.get("fallback_image") == "/files/encanto-bouquet.png",
            f"{label} fallback image should stay on the template, got {media.get('fallback_image')!r}",
        )
        assert_true(media.get("image") == expected["image"], f"{label} variant image did not render: {media}")
        assert_true(media.get("has_variant_image") is True, f"{label} variant image should be marked renderable")
        assert_true(media.get("held_back_variant_image") is False, f"{label} variant image should not be held back")
        assert_true(media.get("held_back_media_role") == "", f"{label} held role should be empty, got {media}")
        assert_true(media.get("held_back_render_policy") == "", f"{label} held policy should be empty, got {media}")
        assert_true(media.get("hold_reason") == "", f"{label} hold reason should be empty, got {media}")
        assert_true(media.get("media_role") == "variant_item_image", f"{label} media role should be variant_item_image")
        rule = media.get("variant_item_media_rule") or {}
        assert_true(rule.get("image") == expected["image"], f"{label} variant item media rule should preserve image")
        checked[label] = media
    return checked


def choose_simple_variant(page, label: str) -> None:
    page.locator(".lt-product__attr[data-attribute-name='Bouquet Size'] .lt-product__chip", has_text=label).click()


def check_simple_product_page_swaps_variant_images(media_by_label: dict[str, Any]) -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1280, "height": 800})
        page = ctx.new_page()
        if _guest_product_route_is_paused(page, SIMPLE_PRODUCT_URL):
            _login_as_operator(page)
            page.goto(SIMPLE_PRODUCT_URL, wait_until="networkidle", timeout=15000)

        image = page.locator(".product-image img.website-image").first
        assert_true(image.count() == 1, "product page main image was not found")
        initial_src = image.get_attribute("src") or ""
        assert_true("encanto-bouquet.png" in initial_src, f"initial simple product image was unexpected: {initial_src!r}")

        for label, media in media_by_label.items():
            expected_image = media["image"]
            choose_simple_variant(page, label)
            page.wait_for_function(
                """(selectedLabel) => {
                    const checked = document.querySelector(
                        ".lt-product__attr[data-attribute-name='Bouquet Size'] .js-lt-attr-input:checked"
                    );
                    return checked && (checked.value || '').includes(selectedLabel);
                }""",
                arg=label,
                timeout=5000,
            )
            page.wait_for_function(
                """(expectedPath) => {
                    const img = document.querySelector('.product-image img.website-image');
                    return img && img.getAttribute('src') && img.getAttribute('src').includes(expectedPath);
                }""",
                arg=expected_image,
                timeout=15000,
            )
        browser.close()


def check_simple_cart_checkout_media_cascade(media_by_label: dict[str, Any]) -> None:
    expected = media_by_label["Medium"]
    cart_line = bench_execute(
        "locally_twisted.api.cart.resolve_cart_item_for_sale",
        kwargs={"item_code": expected["item_code"]},
    )
    assert_true(
        cart_line.get("website_image") == expected["image"],
        f"cart resolver should use the selected variant image, got {cart_line}",
    )
    selected_media = cart_line.get("selected_media") or {}
    assert_true(
        selected_media.get("image") == expected["image"],
        f"cart resolver should preserve selected_media, got {cart_line}",
    )
    assert_true(
        selected_media.get("media_role") == "variant_item_image",
        f"cart selected_media should be a variant_item_image, got {cart_line}",
    )

    line_fields = bench_execute(
        "locally_twisted.product_page_runtime.sales_order_line_configuration_fields",
        kwargs={"resolved_item": cart_line, "client_configuration": None},
    )
    payload = json.loads(line_fields.get("custom_lt_configuration_json") or "{}")
    line_media = payload.get("selected_media") or {}
    assert_true(
        line_media.get("image") == expected["image"],
        f"Sales Order payload should preserve selected variant image, got {payload}",
    )
    receipt_image = bench_execute(
        "locally_twisted.product_page_runtime.customer_facing_line_image",
        kwargs={"item": line_fields},
    )
    assert_true(
        receipt_image == expected["image"],
        f"receipt/customer-facing line image should use selected variant image, got {receipt_image!r}",
    )


def _guest_product_route_is_paused(page, product_url: str) -> bool:
    response = page.goto(product_url, wait_until="domcontentloaded", timeout=15000)
    assert_true(response is not None, "guest product page did not return a response")
    if "/ready-to-order-paused" in page.url:
        return True
    assert_true(
        page.url.rstrip("/") == product_url.rstrip("/"),
        f"guest product page should be open or paused, found {page.url!r}",
    )
    assert_true(
        page.locator(".lt-ecommerce-paused").count() == 0,
        "open guest product page should not render the pause page shell",
    )
    return False


def _login_as_operator(page) -> None:
    response = page.goto(f"{BASE}/login", wait_until="domcontentloaded", timeout=15000)
    assert_true(response is not None, "/login did not return a response")
    login = page.evaluate(
        """async ({ user, password }) => {
            const response = await fetch('/api/method/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ usr: user, pwd: password })
            });
            return { status: response.status, body: await response.text() };
        }""",
        {"user": DESK_USER, "password": DESK_PASSWORD},
    )
    assert_true(login["status"] == 200, f"operator login failed: {login}")


def main() -> int:
    parse_noop_args(__doc__)
    failures = []
    try:
        complex_media = check_complex_variant_media_api_holds_raw_item_image()
        print(f"[PASS] complex variant media API holds raw Item.image at {complex_media['image']}")
    except VariantMediaFail as exc:
        failures.append(str(exc))
        print(f"[FAIL] complex variant media API: {exc}")

    try:
        simple_media = check_simple_variant_media_api_uses_item_images()
        rendered = ", ".join(f"{label}={row['image']}" for label, row in simple_media.items())
        print(f"[PASS] simple variant media API renders selected Item images: {rendered}")
    except VariantMediaFail as exc:
        failures.append(str(exc))
        print(f"[FAIL] simple variant media API: {exc}")
        simple_media = None

    if simple_media:
        try:
            check_simple_product_page_swaps_variant_images(simple_media)
            print("[PASS] Encanto product page swaps the main image for Small, Medium, and Large")
        except VariantMediaFail as exc:
            failures.append(str(exc))
            print(f"[FAIL] simple product page image swap: {exc}")

    if simple_media:
        try:
            check_simple_cart_checkout_media_cascade(simple_media)
            print("[PASS] Encanto selected variant image cascades to cart, Sales Order payload, and receipt helper")
        except VariantMediaFail as exc:
            failures.append(str(exc))
            print(f"[FAIL] simple cart/checkout media cascade: {exc}")

    if failures:
        print("\n[VARIANT MEDIA CONTRACT] FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("\n[VARIANT MEDIA CONTRACT] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
