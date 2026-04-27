#!/usr/bin/env python3
"""Capture the header at desktop + mobile after the truck/cart SVG swap.

Crops to the header band so the icon details are visible.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:8081"
OUT = Path(__file__).resolve().parent / "_screenshots" / "header-icons-2026-04-27"
OUT.mkdir(parents=True, exist_ok=True)


def capture_at(p, viewport, label):
    ctx = p.chromium.launch(headless=True).new_context(
        viewport=viewport, device_scale_factor=2,
    )
    page = ctx.new_page()
    msgs, errs = [], []
    page.on("console", lambda m: msgs.append((m.type, m.text)))
    page.on("pageerror", lambda e: errs.append(str(e)))
    page.goto(BASE_URL + "/", wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(400)
    header = page.locator("header.lt-header")
    box = header.bounding_box()
    if box:
        clip_h = int(box["height"]) + 10
        page.screenshot(path=str(OUT / f"{label}-default.png"),
                        clip={"x": 0, "y": 0, "width": viewport["width"], "height": clip_h})
        # Hover the truck on desktop only
        if label == "desktop":
            link = page.locator(".lt-header__nav-link").nth(3)  # Portfolio
            link.hover()
            page.wait_for_timeout(300)
            page.screenshot(path=str(OUT / f"{label}-hover.png"),
                            clip={"x": 0, "y": 0, "width": viewport["width"], "height": clip_h})
    print(f"\n=== {label} ===  console:{len(msgs)} errors:{len(errs)}")
    for kind, text in msgs[:3]:
        print(f"  [{kind}] {text}")


def main():
    with sync_playwright() as p:
        capture_at(p, {"width": 1280, "height": 800}, "desktop")
        capture_at(p, {"width": 390, "height": 844}, "mobile")
    print(f"\nSaved to: {OUT}")


if __name__ == "__main__":
    main()
