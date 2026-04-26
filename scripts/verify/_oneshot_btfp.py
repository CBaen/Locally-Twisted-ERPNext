"""Screenshot /balloon-twisting-and-face-painting at desktop with tall viewport."""
import sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = "http://localhost:8081/balloon-twisting-and-face-painting"
OUT = Path(__file__).resolve().parent / "_screenshots" / time.strftime("%Y%m%d-%H%M%S-btfp")
OUT.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(viewport={"width": 1280, "height": 2400})
    page = ctx.new_page()
    errors = []
    page.on("console", lambda msg: errors.append(f"[{msg.type}] {msg.text}") if msg.type in ("error","warning") else None)
    page.on("pageerror", lambda exc: errors.append(f"[pageerror] {exc}"))
    page.goto(URL, timeout=30000, wait_until="networkidle")
    page.wait_for_timeout(500)
    out = OUT / "desktop-1280.png"
    page.screenshot(path=str(out), full_page=True)
    print(f"saved: {out}")
    print(f"console: {len(errors)} issues")
    for e in errors: print(f"  {e}")
    browser.close()
