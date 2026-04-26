"""One-shot screenshot of /accessibility at mobile + desktop. Disposable."""
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = "http://localhost:8081/accessibility"
OUT = Path(__file__).resolve().parent / "_screenshots" / time.strftime("%Y%m%d-%H%M%S-accessibility")
OUT.mkdir(parents=True, exist_ok=True)

VIEWPORTS = [
    ("mobile-375", 375, 800),
    ("desktop-1280", 1280, 900),
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    for label, w, h in VIEWPORTS:
        ctx = browser.new_context(viewport={"width": w, "height": h})
        page = ctx.new_page()
        page.goto(URL, timeout=30000, wait_until="networkidle")
        body_text = page.locator("body").inner_text().strip()
        if not body_text:
            print(f"{label}: FAIL — body empty")
            sys.exit(1)
        out = OUT / f"{label}.png"
        page.screenshot(path=str(out), full_page=True)
        print(f"{label}: {out}")
        ctx.close()
    browser.close()

print(f"\nDir: {OUT}")
