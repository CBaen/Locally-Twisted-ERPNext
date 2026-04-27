#!/usr/bin/env python3
"""Tight crop on the truck icon so we can SEE which way the cab faces.
Also reports the computed transform on the SVG element.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:8081"
OUT = Path(__file__).resolve().parent / "_screenshots" / "truck-zoom-2026-04-27"
OUT.mkdir(parents=True, exist_ok=True)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1280, "height": 800}, device_scale_factor=4)
        page = ctx.new_page()
        page.goto(BASE_URL + "/", wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(400)

        truck = page.locator(".lt-header__icon--truck").first
        box = truck.bounding_box()
        if box:
            # Zoom in on the truck — pad 30 px around it
            pad = 30
            clip = {
                "x": max(0, box["x"] - pad),
                "y": max(0, box["y"] - pad),
                "width": box["width"] + pad * 2,
                "height": box["height"] + pad * 2,
            }
            page.screenshot(path=str(OUT / "desktop-truck-tight.png"), clip=clip)
            print(f"truck bounding box: {box}")

        info = page.evaluate(
            """() => {
                const svg = document.querySelector('.lt-header__icon--truck');
                if (!svg) return null;
                const cs = getComputedStyle(svg);
                return {
                    transform: cs.transform,
                    width: cs.width,
                    height: cs.height,
                    color: cs.color,
                    stroke: cs.stroke,
                };
            }"""
        )
        print(f"truck computed style: {info}")

        # Also a wider crop showing the truck + delivery text
        utility = page.locator(".lt-header__utility-left")
        ub = utility.bounding_box()
        if ub:
            page.screenshot(
                path=str(OUT / "desktop-utility-strip.png"),
                clip={"x": max(0, ub["x"] - 10), "y": max(0, ub["y"] - 6),
                      "width": ub["width"] + 20, "height": ub["height"] + 12},
            )

        browser.close()
    print(f"\nSaved to: {OUT}")


if __name__ == "__main__":
    main()
