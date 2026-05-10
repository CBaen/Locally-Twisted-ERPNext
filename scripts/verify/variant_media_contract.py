#!/usr/bin/env python3
"""Verify variant-aware product media on the LT storefront.

This checks the customer-facing bug GL named: selecting a product variant should
move the product photo to the matching variant image when ERPNext has one.

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

TEMPLATE_ITEM = "classic-arch"
VARIANT_ITEM = "classic-arch-20F-BLA-LAY-NOL"
PRODUCT_URL = f"{BASE}/shop-items/arches/classic-arch"
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
        cmd.extend(["--kwargs", json.dumps(kwargs)])

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


def check_variant_media_api() -> dict[str, Any]:
    media = bench_execute(
        "locally_twisted.api.variant_media.get_variant_media",
        kwargs={"item_code": VARIANT_ITEM, "template_item_code": TEMPLATE_ITEM},
    )

    assert_true(media.get("item_code") == VARIANT_ITEM, "variant media API returned the wrong item_code")
    assert_true(
        media.get("fallback_image") == "/files/classic-arch.png",
        f"fallback image should stay on the template, got {media.get('fallback_image')!r}",
    )
    assert_true(
        media.get("image") and media["image"].startswith("/files/classic-arch--extra-"),
        f"{VARIANT_ITEM} should have a mapped extra image, got {media.get('image')!r}",
    )
    assert_true(media.get("has_variant_image") is True, "variant should be marked as having its own image")
    return media


def choose_classic_arch_variant(page) -> None:
    page.locator(".lt-product__attr[data-attribute-name='Arch Size'] .lt-product__chip", has_text="20ft").click()
    page.locator("select.js-lt-attr-input[data-attribute-name='latex colors']").select_option(label="black")
    page.locator(".lt-product__attr[data-attribute-name='Design'] .lt-product__chip", has_text="Layered").click()
    page.locator(".lt-product__attr[data-attribute-name='LED Lights'] .lt-product__chip", has_text="No Lights").click()


def check_product_page_swaps_image(media: dict[str, Any]) -> None:
    expected_image = media["image"]
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1280, "height": 800})
        page = ctx.new_page()
        _assert_guest_product_route_is_paused(page)
        _login_as_operator(page)
        page.goto(PRODUCT_URL, wait_until="networkidle", timeout=15000)

        image = page.locator(".product-image img.website-image").first
        assert_true(image.count() == 1, "product page main image was not found")
        initial_src = image.get_attribute("src") or ""
        assert_true("classic-arch.png" in initial_src, f"initial product image was unexpected: {initial_src!r}")

        choose_classic_arch_variant(page)
        page.wait_for_function(
            """(variantCode) => {
                const btn = document.querySelector('#lt-add-to-cart-variant');
                return btn && btn.getAttribute('data-item-code') === variantCode && !btn.disabled;
            }""",
            arg=VARIANT_ITEM,
            timeout=15000,
        )
        page.wait_for_function(
            """(expectedPath) => {
                const img = document.querySelector('.product-image img.website-image');
                return img && img.getAttribute('src') && img.getAttribute('src').includes(expectedPath);
            }""",
            arg=expected_image,
            timeout=15000,
        )

        final_src = image.get_attribute("src") or ""
        assert_true(final_src != initial_src, "variant selection did not change the main product image")
        browser.close()


def _assert_guest_product_route_is_paused(page) -> None:
    response = page.goto(PRODUCT_URL, wait_until="domcontentloaded", timeout=15000)
    assert_true(response is not None, "guest product page did not return a response")
    assert_true(
        "/ready-to-order-paused" in page.url,
        f"guest product page should be paused while ecommerce is hidden, found {page.url!r}",
    )


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
        media = check_variant_media_api()
        print(f"[PASS] variant media API returns {media['image']} for {VARIANT_ITEM}")
    except VariantMediaFail as exc:
        failures.append(str(exc))
        print(f"[FAIL] variant media API: {exc}")
        media = None

    if media:
        try:
            check_product_page_swaps_image(media)
            print(f"[PASS] product page swaps to {media['image']} after option selection")
        except VariantMediaFail as exc:
            failures.append(str(exc))
            print(f"[FAIL] product page image swap: {exc}")

    if failures:
        print("\n[VARIANT MEDIA CONTRACT] FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("\n[VARIANT MEDIA CONTRACT] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
