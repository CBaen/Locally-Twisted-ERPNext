#!/usr/bin/env python3
"""Oneshot: screenshot /faq at mobile + desktop, capture console.

Verifies Slice 6b FAQ page before handoff to GL.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:8081"
OUT = Path(__file__).resolve().parent / "_screenshots" / "faq-2026-04-27"
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

    page.goto(BASE_URL + "/faq", wait_until="networkidle", timeout=30000)
    out_path = OUT / f"faq-{label}.png"
    page.screenshot(path=str(out_path), full_page=True)

    print(f"\n=== {label} ({viewport['width']}x{viewport['height']}) ===")
    print(f"saved: {out_path}")
    print(f"title: {page.title()}")

    body_len = len(page.locator("body").inner_text().strip())
    print(f"body text length: {body_len} chars")

    h1 = page.locator("h1").first.inner_text() if page.locator("h1").count() else "(none)"
    h2_count = page.locator("h2.lt-faq__group-title").count()
    h3_count = page.locator("h3.lt-faq__question").count()
    print(f"h1: {h1}")
    print(f"h2 groups: {h2_count}")
    print(f"h3 questions: {h3_count}")

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
    capture(p, {"width": 375, "height": 3200}, "mobile")
    capture(p, {"width": 1280, "height": 3200}, "desktop")
