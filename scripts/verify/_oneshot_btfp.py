#!/usr/bin/env python3
"""Oneshot: screenshot /balloon-twisting-and-face-painting at mobile + desktop.

Verifies the new Common Questions accordion section (Slice 6b BTFP propagation)
before handoff to GL.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:8081"
OUT = Path(__file__).resolve().parent / "_screenshots" / "btfp-2026-04-27"
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

    page.goto(BASE_URL + "/balloon-twisting-and-face-painting",
              wait_until="networkidle", timeout=30000)
    # Let carousel settle so first image is at full opacity (3% of 36s = 1.08s).
    page.wait_for_timeout(1500)
    out_path = OUT / f"btfp-{label}.png"
    page.screenshot(path=str(out_path), full_page=True)

    print(f"\n=== {label} ({viewport['width']}x{viewport['height']}) ===")
    print(f"saved: {out_path}")
    print(f"title: {page.title()}")

    banner_visible = page.locator(".lt-btfp__banner-copy").count() > 0
    carousel_imgs = page.locator(".lt-btfp__carousel-img").count()
    fp_carousels = page.locator(".lt-btfp__carousel").count()
    print(f"banner present: {banner_visible}")
    print(f"carousels: {fp_carousels}, total images: {carousel_imgs}")

    faq_heading = page.locator("#lt-btfp__faq-heading")
    faq_visible = faq_heading.count() > 0 and faq_heading.is_visible()
    summary_count = page.locator(".lt-btfp__faq-item summary").count()
    print(f"BTFP FAQ section visible: {faq_visible}")
    print(f"BTFP FAQ summaries: {summary_count}")

    cancel_text = page.locator("text=Cancel 72+ hours").count()
    print(f"new cancellation copy present: {cancel_text > 0}")

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
    capture(p, {"width": 375, "height": 3600}, "mobile")
    capture(p, {"width": 1280, "height": 3200}, "desktop")
