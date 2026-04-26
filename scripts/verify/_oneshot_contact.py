"""Screenshot /contact at mobile + desktop with tall viewport to capture full page."""
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = "http://localhost:8081/contact"
OUT = Path(__file__).resolve().parent / "_screenshots" / time.strftime("%Y%m%d-%H%M%S-contact")
OUT.mkdir(parents=True, exist_ok=True)

VIEWPORTS = [
    ("mobile-375", 375, 2200),
    ("desktop-1280", 1280, 2200),
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    for label, w, h in VIEWPORTS:
        ctx = browser.new_context(viewport={"width": w, "height": h})
        page = ctx.new_page()
        errors = []
        page.on("console", lambda msg: errors.append(f"[{msg.type}] {msg.text}") if msg.type in ("error", "warning") else None)
        page.on("pageerror", lambda exc: errors.append(f"[pageerror] {exc}"))
        page.goto(URL, timeout=30000, wait_until="networkidle")
        page.wait_for_timeout(500)
        out = OUT / f"{label}.png"
        page.screenshot(path=str(out), full_page=True)
        print(f"{label}: {out}")
        if errors:
            print(f"  console issues ({len(errors)}):")
            for e in errors:
                print(f"    {e}")
        ctx.close()
    browser.close()

print(f"\nDir: {OUT}")
