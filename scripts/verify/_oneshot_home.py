#!/usr/bin/env python3
"""Oneshot: screenshot the new homepage at mobile + desktop, capture console.

Verifies before handoff to GL. Tall viewport so full_page captures the
entire scroll past Frappe's flex-column sticky-footer.
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:8081"
OUT = Path(__file__).resolve().parent / "_screenshots" / "home-2026-04-27"
OUT.mkdir(parents=True, exist_ok=True)


def capture(p, viewport, label):
    ctx = p.chromium.launch(headless=True).new_context(
        viewport=viewport,
        device_scale_factor=2,
    )
    page = ctx.new_page()

    msgs = []
    errs = []
    page.on("console", lambda m: msgs.append((m.type, m.text)))
    page.on("pageerror", lambda e: errs.append(str(e)))

    page.goto(BASE_URL + "/", wait_until="networkidle", timeout=30000)
    out_path = OUT / f"home-{label}.png"
    page.screenshot(path=str(out_path), full_page=True)

    print(f"\n=== {label} ({viewport['width']}x{viewport['height']}) ===")
    print(f"saved: {out_path}")

    title = page.title()
    print(f"title: {title}")

    body_len = len(page.locator("body").inner_text().strip())
    print(f"body text length: {body_len} chars")

    print(f"console messages: {len(msgs)}")
    for kind, text in msgs:
        if kind in ("error", "warning"):
            print(f"  [{kind}] {text}")
    print(f"page errors: {len(errs)}")
    for e in errs:
        print(f"  {e}")

    ctx.browser.close()
    return out_path


with sync_playwright() as p:
    capture(p, {"width": 375, "height": 2400}, "mobile")
    capture(p, {"width": 1280, "height": 2400}, "desktop")
