#!/usr/bin/env python3
"""Render the Stripe Checkout URL and document what payment options appear.

Reads the URL from /tmp/lt_stripe_url.txt (curl-emitted) and uses Playwright
to load it. Captures:
- Full-page screenshot
- All text mentioning "Link"
- Visible payment-option labels
- Whether a "Pay without Link" button is present
"""
import sys
import time
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("FAIL — playwright not installed")
    sys.exit(1)

URL_FILE = Path("/tmp/lt_stripe_url.txt")
if not URL_FILE.exists():
    print(f"FAIL — {URL_FILE} not found")
    sys.exit(1)

url = URL_FILE.read_text().strip()
print(f"URL: {url[:120]}...")

out_dir = Path(__file__).parent / "_screenshots" / time.strftime("stripe-link-%Y%m%d-%H%M%S")
out_dir.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(viewport={"width": 1280, "height": 1200})
    page = ctx.new_page()

    print("\nLoading Stripe page...")
    page.goto(url, timeout=45000, wait_until="networkidle")
    time.sleep(3)  # let any deferred Link UI render

    page.screenshot(path=str(out_dir / "stripe-checkout.png"), full_page=True)

    body_text = page.locator("body").inner_text()
    link_mentions = [line for line in body_text.split("\n") if "link" in line.lower()]
    print(f"\nLines mentioning 'Link' ({len(link_mentions)}):")
    for ln in link_mentions[:20]:
        print(f"  {ln}")

    # Check for "Pay without Link" button
    pay_without_link = page.locator("text=/pay\\s+without\\s+link/i").count()
    print(f"\n'Pay without Link' element count: {pay_without_link}")

    # Look for Link logo / Link branding
    link_logos = page.locator("[alt*='Link' i], [aria-label*='Link' i]").count()
    print(f"Link-labeled elements: {link_logos}")

    # Save screenshot path
    print(f"\nScreenshot: {out_dir / 'stripe-checkout.png'}")
    browser.close()
