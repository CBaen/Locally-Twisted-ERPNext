"""Capture the full footer area on /accessibility at desktop + mobile.
Uses a tall viewport (2000px) so the entire scroll height is visible
in full_page=True regardless of the body's flex sticky-footer behavior."""
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = "http://localhost:8081/accessibility"
OUT = Path(__file__).resolve().parent / "_screenshots" / time.strftime("%Y%m%d-%H%M%S-footer")
OUT.mkdir(parents=True, exist_ok=True)

VIEWPORTS = [
    ("mobile-375", 375, 2000),
    ("desktop-1280", 1280, 2000),
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    for label, w, h in VIEWPORTS:
        ctx = browser.new_context(viewport={"width": w, "height": h})
        page = ctx.new_page()
        page.goto(URL, timeout=30000, wait_until="networkidle")
        page.wait_for_timeout(500)
        out = OUT / f"{label}.png"
        page.screenshot(path=str(out), full_page=True)
        print(f"{label}: {out}")
        ctx.close()
    browser.close()

print(f"\nDir: {OUT}")
