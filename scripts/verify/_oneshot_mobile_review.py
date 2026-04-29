#!/usr/bin/env python3
"""Oneshot — capture mobile (375px) + desktop (1280px) screenshots of priority pages
for a responsive-design review session.
"""
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

BASE = "http://localhost:8081"
PAGES = [
    "/",
    "/contact",
    "/lookbook",
    "/all-products",
    "/balloon-twisting-and-face-painting",
    "/faq",
    "/accessibility",
    "/refund-policy",
]
VIEWPORTS = [
    ("mobile", 375, 812),
    ("desktop", 1280, 800),
]

def main():
    ts = time.strftime("%Y%m%d-%H%M%S")
    out = Path(__file__).resolve().parent / "_screenshots" / f"{ts}-mobile-review"
    out.mkdir(parents=True, exist_ok=True)

    fails = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for label, w, h in VIEWPORTS:
            ctx = browser.new_context(viewport={"width": w, "height": h})
            page = ctx.new_page()
            for path in PAGES:
                url = f"{BASE}{path}"
                safe = path.strip("/").replace("/", "_") or "home"
                target = out / f"{safe}__{label}.png"
                try:
                    page.goto(url, timeout=30000, wait_until="networkidle")
                    page.screenshot(path=str(target), full_page=True)
                    print(f"  [{label:7}] {path:45} -> {target.name}")
                except PlaywrightTimeout:
                    print(f"  [{label:7}] {path:45} TIMEOUT")
                    fails += 1
                except Exception as e:
                    print(f"  [{label:7}] {path:45} ERROR {e}")
                    fails += 1
            ctx.close()
        browser.close()

    print(f"\nSaved to: {out}")
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
