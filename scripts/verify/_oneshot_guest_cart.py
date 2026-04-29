#!/usr/bin/env python3
"""Guest cart end-to-end verification.

Verifies the localStorage-backed guest cart flow:
1. /shop loads, lt-guest-cart.js is loaded, LT_CART is exposed
2. Programmatically add two distinct items via LT_CART.add()
3. /cart renders both lines with names + prices, subtotal correct
4. Navbar cart count badge reflects total qty
5. /checkout (cart mode) hydrates summary from localStorage with both lines
6. Clearing the cart via LT_CART.clear() returns /cart to empty state

Stops short of actually submitting the order (would create a real Stripe
Session). The submission path is exercised separately with the 4242 test
card by GL in a real browser.

Saves screenshots to scripts/verify/_screenshots/<timestamp>/.
"""
import sys
import time
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("FAIL — playwright not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)

BASE = "http://localhost:8081"
ITEM_A = "number-balloon-columns"
ITEM_B = "graduation-grab-n-go"


def main() -> int:
    out_dir = Path(__file__).parent / "_screenshots" / time.strftime("guest-cart-%Y%m%d-%H%M%S")
    out_dir.mkdir(parents=True, exist_ok=True)

    fails = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()
        console_errors = []
        page.on("pageerror", lambda exc: console_errors.append(f"PAGE ERROR: {exc}"))
        page.on("console", lambda msg: console_errors.append(f"CONSOLE {msg.type}: {msg.text}") if msg.type in ("error",) else None)

        # ── Step 1: load /shop and confirm LT_CART exposed ──
        print(f"\n[1] GET {BASE}/shop")
        page.goto(f"{BASE}/shop", timeout=30000, wait_until="networkidle")
        page.screenshot(path=str(out_dir / "01-shop.png"), full_page=True)
        has_lt_cart = page.evaluate("typeof window.LT_CART !== 'undefined'")
        if not has_lt_cart:
            fails.append("LT_CART global not exposed on /shop")
        else:
            print("    ✓ LT_CART global present")

        # ── Step 2: programmatically add two items ──
        print(f"\n[2] LT_CART.add({ITEM_A!r}, 2) + LT_CART.add({ITEM_B!r}, 1)")
        page.evaluate(f"window.LT_CART.clear()")  # ensure clean baseline
        page.evaluate(f"window.LT_CART.add({ITEM_A!r}, 2)")
        page.evaluate(f"window.LT_CART.add({ITEM_B!r}, 1)")
        cart = page.evaluate("window.LT_CART.getCart()")
        count = page.evaluate("window.LT_CART.getCount()")
        print(f"    cart: {cart}")
        print(f"    count: {count}")
        if count != 3:
            fails.append(f"Expected count=3, got {count}")

        # ── Step 3: navigate to /cart and verify lines render ──
        print(f"\n[3] GET {BASE}/cart")
        page.goto(f"{BASE}/cart", timeout=30000, wait_until="networkidle")
        # Wait for client-side hydration to finish
        page.wait_for_selector("#lt-cart-populated:not([hidden])", timeout=10000)
        page.screenshot(path=str(out_dir / "02-cart-populated.png"), full_page=True)

        line_count = page.locator(".lt-cart__line").count()
        print(f"    rendered lines: {line_count}")
        if line_count != 2:
            fails.append(f"Expected 2 cart lines, got {line_count}")

        subtotal_text = page.locator("#lt-cart-subtotal").text_content() or ""
        print(f"    subtotal: {subtotal_text}")
        # Number Balloon Columns is $55 and we added 2 → $110
        # Graduation Grab n Go is $85 and we added 1 → $85
        # Total subtotal = $195
        if "195" not in subtotal_text:
            fails.append(f"Expected subtotal containing 195, got {subtotal_text!r}")

        # ── Step 4: cart count badge in navbar ──
        badge_text = page.locator("#lt-cart-count").text_content() or ""
        print(f"    navbar badge: {badge_text!r}")
        if badge_text.strip() != "3":
            fails.append(f"Expected navbar badge=3, got {badge_text!r}")

        # ── Step 5: navigate to /checkout in cart mode ──
        print(f"\n[5] GET {BASE}/checkout")
        page.goto(f"{BASE}/checkout", timeout=30000, wait_until="networkidle")
        # Wait for cart-mode hydration
        page.wait_for_selector("#lt-checkout-summary-subtotal-row:not([hidden])", timeout=10000)
        page.screenshot(path=str(out_dir / "03-checkout-cart-mode.png"), full_page=True)

        co_lines = page.locator("#lt-checkout-summary-lines .lt-checkout__line").count()
        co_subtotal = page.locator("#lt-checkout-summary-subtotal").text_content() or ""
        co_items_json = page.locator("#lt-checkout-items-json").input_value() or ""
        co_mode = page.locator("#lt-checkout-form").get_attribute("data-mode")
        print(f"    mode: {co_mode}")
        print(f"    lines: {co_lines}")
        print(f"    subtotal: {co_subtotal}")
        print(f"    items_json: {co_items_json}")

        if co_mode != "cart":
            fails.append(f"Expected data-mode=cart, got {co_mode!r}")
        if co_lines != 2:
            fails.append(f"Expected 2 checkout summary lines, got {co_lines}")
        if "195" not in co_subtotal:
            fails.append(f"Expected checkout subtotal containing 195, got {co_subtotal!r}")
        if not co_items_json or "[]" == co_items_json:
            fails.append(f"items_json input not populated, got {co_items_json!r}")

        # ── Step 6: clear + verify empty state ──
        print(f"\n[6] LT_CART.clear() + reload /cart")
        page.evaluate("window.LT_CART.clear()")
        page.goto(f"{BASE}/cart", timeout=30000, wait_until="networkidle")
        page.wait_for_selector("#lt-cart-empty:not([hidden])", timeout=5000)
        page.screenshot(path=str(out_dir / "04-cart-empty.png"), full_page=True)
        print("    ✓ empty state visible")

        # Console error check
        if console_errors:
            print("\n[!] Console errors observed:")
            for err in console_errors:
                print(f"    {err}")
            fails.append(f"{len(console_errors)} console error(s) observed")

        browser.close()

    print(f"\nScreenshots saved to {out_dir}")
    if fails:
        print(f"\n{len(fails)} FAILURE(S):")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("\nALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
