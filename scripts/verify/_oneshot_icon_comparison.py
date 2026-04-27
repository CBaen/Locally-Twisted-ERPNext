#!/usr/bin/env python3
"""Render the icon-pack comparison HTML and screenshot it for GL review."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent.parent
HTML = ROOT / "_resources" / "icon-comparison-2026-04-27" / "compare.html"
OUT = Path(__file__).resolve().parent / "_screenshots" / "icon-comparison-2026-04-27"
OUT.mkdir(parents=True, exist_ok=True)


def main():
    if not HTML.exists():
        print(f"missing: {HTML}")
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport={"width": 1280, "height": 1600},
            device_scale_factor=2,
        )
        page = ctx.new_page()
        page.goto(HTML.as_uri(), wait_until="networkidle", timeout=15000)
        page.wait_for_timeout(800)  # let JS load + inject
        out = OUT / "comparison.png"
        page.screenshot(path=str(out), full_page=True)
        print(f"saved: {out}")
        browser.close()


if __name__ == "__main__":
    main()
