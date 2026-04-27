#!/usr/bin/env python3
"""Oneshot: capture the desktop nav in default + hover state.

Verifies the hover-double-underline fix on .lt-header__nav-link.
Crops to the header band so we can see line/color details clearly.
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:8081"
OUT = Path(__file__).resolve().parent / "_screenshots" / "nav-hover-2026-04-27"
OUT.mkdir(parents=True, exist_ok=True)


def capture(p):
    ctx = p.chromium.launch(headless=True).new_context(
        viewport={"width": 1280, "height": 800},
        device_scale_factor=2,
    )
    page = ctx.new_page()

    msgs = []
    errs = []
    page.on("console", lambda m: msgs.append((m.type, m.text)))
    page.on("pageerror", lambda e: errs.append(str(e)))

    page.goto(BASE_URL + "/", wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(400)

    # Default state — full header band
    header = page.locator("header.lt-header")
    box = header.bounding_box()
    if box:
        clip = {"x": 0, "y": 0, "width": 1280, "height": int(box["height"]) + 8}
        page.screenshot(path=str(OUT / "01-default.png"), clip=clip)

    # Hover state — Twisting & Face Painting (the first nav link)
    link = page.locator(".lt-header__nav-link").first
    link.hover()
    page.wait_for_timeout(350)  # let transition complete
    if box:
        page.screenshot(path=str(OUT / "02-hover-twisting.png"), clip=clip)

    # Hover state — Event Decor (a middle link, double-check consistency)
    page.locator(".lt-header__nav-link").nth(1).hover()
    page.wait_for_timeout(350)
    if box:
        page.screenshot(path=str(OUT / "03-hover-event-decor.png"), clip=clip)

    # Capture the computed text-decoration on the hovered link to prove the fix
    page.locator(".lt-header__nav-link").nth(1).hover()
    page.wait_for_timeout(200)
    decoration = page.evaluate(
        """() => {
            const el = document.querySelectorAll('.lt-header__nav-link')[1];
            const cs = getComputedStyle(el);
            return {
                'text-decoration-line': cs.textDecorationLine,
                'border-bottom-width': cs.borderBottomWidth,
                'border-bottom-color': cs.borderBottomColor,
                'color': cs.color,
            };
        }"""
    )
    print("Computed style of hovered nav link:")
    for k, v in decoration.items():
        print(f"  {k}: {v}")

    print(f"\nConsole msgs: {len(msgs)}  pageerrors: {len(errs)}")
    for kind, text in msgs[:5]:
        print(f"  [{kind}] {text}")
    for e in errs[:5]:
        print(f"  ERR {e}")


def main():
    with sync_playwright() as p:
        capture(p)
    print(f"\nSaved to: {OUT}")


if __name__ == "__main__":
    main()
