"""One-shot: screenshot the Odoo checkout flow and our local Stripe page.

Why: GL is on /stripe_checkout (Frappe payments' built-in card form) and
finds it unprofessional vs. the Odoo site's old checkout flow. This script
captures both side-by-side so we can compare what each looks like before
deciding the fix.

Cleanup: delete this file after use (it's a one-shot, not a standing tool).
"""
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


ODOO_BASE = "http://5.78.136.133"
LT_BASE = "http://localhost:8081"

OUT = Path(__file__).resolve().parent / "_screenshots" / time.strftime("compare-%Y%m%d-%H%M%S")
OUT.mkdir(parents=True, exist_ok=True)


def shot(page, name):
    path = OUT / f"{name}.png"
    page.screenshot(path=str(path), full_page=True)
    print(f"  saved {path.name}  ({page.url})")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()

        # ── Odoo flow ─────────────────────────────────────────────────
        print("[ODOO] loading /shop")
        try:
            page.goto(f"{ODOO_BASE}/shop", timeout=20000, wait_until="domcontentloaded")
        except PlaywrightTimeout:
            print("       FAIL — /shop did not load")
        else:
            shot(page, "01-odoo-shop")

            # Click the first product card to drill into a product page.
            try:
                first_link = page.locator("a[href^='/shop/']").nth(2)
                href = first_link.get_attribute("href")
                if href and "/shop/" in href and href != "/shop/cart":
                    print(f"[ODOO] clicking product: {href}")
                    page.goto(f"{ODOO_BASE}{href}", timeout=20000, wait_until="domcontentloaded")
                    shot(page, "02-odoo-product")

                    # Add to cart — Odoo's standard button is named #add_to_cart
                    try:
                        page.click("#add_to_cart, a:has-text('Add to Cart'), button:has-text('Add to Cart')",
                                   timeout=5000)
                        time.sleep(2)
                        print("[ODOO] added to cart")
                    except Exception as e:
                        print(f"[ODOO] could not click add-to-cart: {e}")
            except Exception as e:
                print(f"[ODOO] could not find product link: {e}")

        # The four URLs GL named — visit each and snap.
        for slug, name in [
            ("/shop/cart", "03-odoo-cart"),
            ("/shop/address", "04-odoo-address"),
            ("/shop/checkout?try_skip_step=true", "05-odoo-delivery"),
            ("/shop/payment", "06-odoo-payment"),
        ]:
            print(f"[ODOO] loading {slug}")
            try:
                page.goto(f"{ODOO_BASE}{slug}", timeout=20000, wait_until="domcontentloaded")
                time.sleep(1)
                shot(page, name)
            except PlaywrightTimeout:
                print(f"       FAIL — {slug} did not load")

        # ── Our local /stripe_checkout (the page GL was on) ───────────
        # Use the exact query params from GL's URL. The PR doesn't need to
        # exist for the form to render — the publishable key fetch will fail
        # gracefully but the form layout will still show.
        local_url = (
            f"{LT_BASE}/stripe_checkout"
            "?amount=35.0&title=Locally+Twisted"
            "&description=Payment+for+order+SAL-ORD-2026-00010+%E2%80%94+Locally+Twisted"
            "&reference_doctype=Payment+Request"
            "&reference_docname=ACC-PRQ-2026-00009"
            "&payer_email=cameronbpaul%40gmail.com"
            "&payer_name=Cameron+Paul"
            "&order_id=ACC-PRQ-2026-00009"
            "&currency=USD&payment_gateway=Stripe-Test"
        )
        print(f"[LT] loading /stripe_checkout")
        try:
            page.goto(local_url, timeout=20000, wait_until="domcontentloaded")
            time.sleep(2)
            shot(page, "07-lt-stripe-checkout")
        except PlaywrightTimeout:
            print("     FAIL — /stripe_checkout did not load")

        browser.close()

    print(f"\nAll screenshots in: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
