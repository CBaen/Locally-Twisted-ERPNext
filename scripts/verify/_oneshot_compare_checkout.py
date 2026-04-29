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

            # Drill to a real product page (not a category). Look for links
            # that match the Odoo product detail pattern /shop/<slug>-<id>.
            try:
                product_hrefs = page.evaluate("""
                    () => Array.from(document.querySelectorAll("a[href^='/shop/']"))
                        .map(a => a.getAttribute('href'))
                        .filter(h => /^\\/shop\\/[a-z0-9-]+-\\d+(\\?|$)/.test(h))
                """)
                print(f"[ODOO] candidate product hrefs: {product_hrefs[:5]}")
                target = product_hrefs[0] if product_hrefs else None
                if target:
                    print(f"[ODOO] navigating to product: {target}")
                    page.goto(f"{ODOO_BASE}{target}", timeout=20000, wait_until="domcontentloaded")
                    time.sleep(1)
                    shot(page, "02-odoo-product")

                    # Force-click the add-to-cart button — sticky header
                    # intercepts normal clicks. force=True bypasses the
                    # actionability check, then we wait for navigation.
                    try:
                        page.locator("#add_to_cart").first.click(force=True, timeout=8000)
                        time.sleep(3)
                        print(f"[ODOO] after add-to-cart, on: {page.url}")
                    except Exception as e:
                        # Fallback — submit the product form directly via JS.
                        print(f"[ODOO] click failed ({e}); trying JS form submit")
                        try:
                            page.evaluate("""
                                () => {
                                    const f = document.querySelector("form.js_add_cart_json")
                                          || document.querySelector("form[action*='cart/update_json']")
                                          || document.querySelector("form#product_details");
                                    if (f) f.submit();
                                }
                            """)
                            time.sleep(3)
                            print(f"[ODOO] after JS submit, on: {page.url}")
                        except Exception as e2:
                            print(f"[ODOO] JS submit also failed: {e2}")
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
