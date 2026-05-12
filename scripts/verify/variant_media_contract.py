#!/usr/bin/env python3
"""Verify product-template media contracts on the LT storefront.

This checks the layer-6 media contract: unclassified variant images must stay
held back, and selecting a ready-to-order variant must not imply a photo changed
unless the backend returns an approved `variant_image` role. Quote-first product
templates are verified as quote-first surfaces instead of forcing their old
direct-checkout selector contract.

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

QUOTE_FIRST_TEMPLATE_ITEM = "classic-arch"
QUOTE_FIRST_VARIANT_ITEM = "classic-arch-20F-BLA-LAY-NOL"
QUOTE_FIRST_PRODUCT_URL = f"{BASE}/shop-items/arches/classic-arch"
READY_TEMPLATE_ITEM = "unicorn-bouquet"
READY_VARIANT_ITEM = "unicorn-bouquet-MED"
READY_PRODUCT_URL = f"{BASE}/shop-items/bouquets/unicorn-bouquet"
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


def check_quote_first_variant_media_api() -> dict[str, Any]:
    media = bench_execute(
        "locally_twisted.api.variant_media.get_variant_media",
        kwargs={"item_code": QUOTE_FIRST_VARIANT_ITEM, "template_item_code": QUOTE_FIRST_TEMPLATE_ITEM},
    )

    assert_true(media.get("item_code") == QUOTE_FIRST_VARIANT_ITEM, "variant media API returned the wrong item_code")
    assert_true(
        media.get("fallback_image") == "/files/classic-arch.png",
        f"fallback image should stay on the template, got {media.get('fallback_image')!r}",
    )
    assert_true(
        media.get("image") == media.get("fallback_image"),
        f"unclassified quote-first variant image should stay on fallback, got {media.get('image')!r}",
    )
    assert_true(media.get("has_variant_image") is False, "unclassified variant image should not be marked renderable")
    assert_true(media.get("held_back_variant_image") is True, "source variant image should be reported as held back")
    assert_true(media.get("held_back_media_role") == "ignored_artifact", f"held variant image needs safe role, got {media}")
    assert_true(media.get("held_back_render_policy") == "hold_back", f"held variant image needs render policy, got {media}")
    assert_true(media.get("hold_reason"), "held variant image needs a hold reason")
    assert_true(media.get("media_role") == "primary", f"fallback image should report primary role, got {media}")
    return media


def check_ready_variant_media_api() -> dict[str, Any]:
    media = bench_execute(
        "locally_twisted.api.variant_media.get_variant_media",
        kwargs={"item_code": READY_VARIANT_ITEM, "template_item_code": READY_TEMPLATE_ITEM},
    )

    assert_true(media.get("item_code") == READY_VARIANT_ITEM, "ready variant media API returned the wrong item_code")
    assert_true(
        media.get("fallback_image") == "/files/unicorn-bouquet.png",
        f"ready fallback image should stay on the template, got {media.get('fallback_image')!r}",
    )
    assert_true(
        media.get("image") == media.get("fallback_image"),
        f"unclassified ready variant image should stay on fallback, got {media.get('image')!r}",
    )
    assert_true(media.get("has_variant_image") is False, "unclassified ready variant should not be marked renderable")
    assert_true(media.get("held_back_variant_image") is True, "source variant image should be reported as held back")
    assert_true(media.get("held_back_media_role") == "ignored_artifact", f"held ready image needs safe role, got {media}")
    assert_true(media.get("held_back_render_policy") == "hold_back", f"held ready image needs render policy, got {media}")
    assert_true(media.get("hold_reason"), "held ready image needs a hold reason")
    assert_true(media.get("media_role") == "primary", f"fallback image should report primary role, got {media}")
    return media


def choose_ready_variant(page) -> None:
    page.locator(".lt-product__attr[data-attribute-name='Bouquet Size'] .lt-product__chip", has_text="Medium").click()


def check_ready_product_page_holds_unclassified_variant_image(media: dict[str, Any]) -> None:
    expected_image = media["image"]
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1280, "height": 800})
        page = ctx.new_page()
        if _guest_product_route_is_paused(page, READY_PRODUCT_URL):
            _login_as_operator(page)
            page.goto(READY_PRODUCT_URL, wait_until="networkidle", timeout=15000)

        image = page.locator(".product-image img.website-image").first
        assert_true(image.count() == 1, "product page main image was not found")
        initial_src = image.get_attribute("src") or ""
        assert_true("unicorn-bouquet.png" in initial_src, f"initial ready product image was unexpected: {initial_src!r}")

        choose_ready_variant(page)
        page.wait_for_function(
            """() => {
                const checked = document.querySelector(
                    ".lt-product__attr[data-attribute-name='Bouquet Size'] .js-lt-attr-input:checked"
                );
                return checked && /Medium/.test(checked.value || '');
            }""",
            timeout=5000,
        )
        page.wait_for_timeout(1500)
        page.wait_for_function(
            """(expectedPath) => {
                const img = document.querySelector('.product-image img.website-image');
                return img && img.getAttribute('src') && img.getAttribute('src').includes(expectedPath);
            }""",
            arg=expected_image,
            timeout=15000,
        )

        final_src = image.get_attribute("src") or ""
        assert_true(final_src == initial_src, "unclassified variant selection should not change the main product image")
        browser.close()


def check_quote_first_product_surface() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1280, "height": 800})
        page = ctx.new_page()
        if _guest_product_route_is_paused(page, QUOTE_FIRST_PRODUCT_URL):
            _login_as_operator(page)
            page.goto(QUOTE_FIRST_PRODUCT_URL, wait_until="networkidle", timeout=15000)

        assert_true(
            page.locator(".lt-product__cart--quote-first").count() == 1,
            "Classic Arch should render the quote-first product-template surface",
        )
        assert_true(
            page.locator(".lt-product__configure").count() == 0,
            "Classic Arch quote-first page should not expose direct-checkout variant controls",
        )
        assert_true(
            page.locator(".lt-product__quote-attr .js-lt-quote-option").count() > 0,
            "Classic Arch quote-first page should expose quote option controls",
        )
        image = page.locator(".product-image img.website-image").first
        assert_true(image.count() == 1, "quote-first product page main image was not found")
        initial_src = image.get_attribute("src") or ""
        assert_true("classic-arch.png" in initial_src, f"initial quote-first product image was unexpected: {initial_src!r}")
        browser.close()


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
        quote_first_media = check_quote_first_variant_media_api()
        print(f"[PASS] quote-first variant media API holds unclassified media at {quote_first_media['image']}")
    except VariantMediaFail as exc:
        failures.append(str(exc))
        print(f"[FAIL] quote-first variant media API: {exc}")

    try:
        check_quote_first_product_surface()
        print("[PASS] Classic Arch renders quote-first controls instead of stale direct-checkout variant controls")
    except VariantMediaFail as exc:
        failures.append(str(exc))
        print(f"[FAIL] quote-first product surface: {exc}")

    try:
        ready_media = check_ready_variant_media_api()
        print(f"[PASS] ready-to-order variant media API holds unclassified media at {ready_media['image']}")
    except VariantMediaFail as exc:
        failures.append(str(exc))
        print(f"[FAIL] ready-to-order variant media API: {exc}")
        ready_media = None

    if ready_media:
        try:
            check_ready_product_page_holds_unclassified_variant_image(ready_media)
            print("[PASS] ready-to-order product page keeps primary image until variant media is classified")
        except VariantMediaFail as exc:
            failures.append(str(exc))
            print(f"[FAIL] ready-to-order product page image swap: {exc}")

    if failures:
        print("\n[VARIANT MEDIA CONTRACT] FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("\n[VARIANT MEDIA CONTRACT] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
