#!/usr/bin/env python3
"""Capture /shop full page at desktop + mobile."""
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:8081"
OUT = Path(__file__).resolve().parent / "_screenshots" / "shop-2026-04-27"
OUT.mkdir(parents=True, exist_ok=True)


def capture(p, viewport, label):
    ctx = p.chromium.launch(headless=True).new_context(
        viewport=viewport, device_scale_factor=2,
    )
    page = ctx.new_page()
    msgs, errs = [], []
    page.on("console", lambda m: msgs.append((m.type, m.text)))
    page.on("pageerror", lambda e: errs.append(str(e)))
    page.goto(BASE_URL + "/shop", wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(800)
    page.screenshot(path=str(OUT / f"{label}.png"), full_page=True)
    print(f"[{label}] console:{len(msgs)} errors:{len(errs)}")
    for kind, text in msgs[:5]:
        print(f"  [{kind}] {text}")
    for e in errs[:3]:
        print(f"  ERR {e}")


def main():
    with sync_playwright() as p:
        capture(p, {"width": 1280, "height": 900}, "desktop")
        capture(p, {"width": 390, "height": 844}, "mobile")
    print(f"\nSaved to: {OUT}")


if __name__ == "__main__":
    main()
