#!/usr/bin/env python3
"""Oneshot: screenshot /faq accordion at mobile + desktop, both states.

Verifies Slice 6b FAQ accordion before handoff to GL.
Captures: all-collapsed (default), and one-expanded (verifies open state).
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:8081"
OUT = Path(__file__).resolve().parent / "_screenshots" / "faq-2026-04-27"
OUT.mkdir(parents=True, exist_ok=True)


def capture(p, viewport, label, expand_first=False):
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

    if expand_first:
        page.locator(".lt-faq__item summary").first.click()
        page.wait_for_timeout(200)

    out_path = OUT / f"faq-{label}.png"
    page.screenshot(path=str(out_path), full_page=True)

    print(f"\n=== {label} ({viewport['width']}x{viewport['height']}) ===")
    print(f"saved: {out_path}")
    print(f"title: {page.title()}")

    body_len = len(page.locator("body").inner_text().strip())
    print(f"body text length: {body_len} chars")

    h1 = page.locator("h1").first.inner_text() if page.locator("h1").count() else "(none)"
    h2_count = page.locator("h2.lt-faq__group-title").count()
    summary_count = page.locator(".lt-faq__item summary").count()
    open_count = page.locator(".lt-faq__item[open]").count()
    print(f"h1: {h1}")
    print(f"h2 groups: {h2_count}")
    print(f"summaries: {summary_count}")
    print(f"open accordions: {open_count}")

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
    capture(p, {"width": 375, "height": 2400}, "mobile-collapsed")
    capture(p, {"width": 1280, "height": 2400}, "desktop-collapsed")
    capture(p, {"width": 1280, "height": 2400}, "desktop-one-open", expand_first=True)
