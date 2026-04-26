"""One-shot screenshot of /all-products at desktop after the webshop bundle build.
Captures console errors so we know whether the JS loaded cleanly."""
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = "http://localhost:8081/all-products"
OUT = Path(__file__).resolve().parent / "_screenshots" / time.strftime("%Y%m%d-%H%M%S-allproducts")
OUT.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    page = ctx.new_page()
    console_errors = []
    page.on("console", lambda msg: console_errors.append(f"[{msg.type}] {msg.text}") if msg.type in ("error", "warning") else None)
    page.on("pageerror", lambda exc: console_errors.append(f"[pageerror] {exc}"))
    page.goto(URL, timeout=30000, wait_until="networkidle")
    out = OUT / "desktop-1280.png"
    page.screenshot(path=str(out), full_page=True)
    print(f"saved: {out}")
    print(f"\nConsole messages ({len(console_errors)} errors/warnings):")
    for e in console_errors:
        print(f"  {e}")
    browser.close()

print(f"\nDir: {OUT}")
