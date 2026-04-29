"""Capture: new /checkout layout (mobile + desktop) + Stripe-hosted page."""
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright


OUT = Path(__file__).resolve().parent / "_screenshots" / time.strftime("after-%Y%m%d-%H%M%S")
OUT.mkdir(parents=True, exist_ok=True)

LT_CHECKOUT = "http://localhost:8081/checkout?item=number-balloon-columns&qty=1"
STRIPE_URL = sys.argv[1] if len(sys.argv) > 1 else None


def shot(page, name):
    p = OUT / f"{name}.png"
    page.screenshot(path=str(p), full_page=True)
    print(f"  saved {p.name} ({page.url[:80]}...)")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # Desktop /checkout
        ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()
        page.goto(LT_CHECKOUT, timeout=20000, wait_until="networkidle")
        shot(page, "01-lt-checkout-desktop")
        ctx.close()

        # Mobile /checkout
        ctx = browser.new_context(viewport={"width": 375, "height": 812})
        page = ctx.new_page()
        page.goto(LT_CHECKOUT, timeout=20000, wait_until="networkidle")
        shot(page, "02-lt-checkout-mobile")
        ctx.close()

        # Stripe-hosted checkout (if URL given)
        if STRIPE_URL:
            ctx = browser.new_context(viewport={"width": 1280, "height": 900})
            page = ctx.new_page()
            page.goto(STRIPE_URL, timeout=30000, wait_until="networkidle")
            time.sleep(2)
            shot(page, "03-stripe-hosted")
            ctx.close()

        browser.close()
    print(f"\nIn: {OUT}")


if __name__ == "__main__":
    main()
