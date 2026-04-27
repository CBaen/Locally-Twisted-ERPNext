#!/usr/bin/env python3
"""Capture BTFP after orientation + aspect-ratio fixes.

- Full-page desktop and mobile
- Tight crop around the services band (sized to actual band height)
- Individual photo captures by toggling opacity to force-show each one
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:8081"
OUT = Path(__file__).resolve().parent / "_screenshots" / "btfp-after-2026-04-27"
OUT.mkdir(parents=True, exist_ok=True)


def capture(p, viewport, label):
    ctx = p.chromium.launch(headless=True).new_context(
        viewport=viewport, device_scale_factor=2,
    )
    page = ctx.new_page()
    page.goto(BASE_URL + "/balloon-twisting-and-face-painting", wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(800)

    # Full page
    page.screenshot(path=str(OUT / f"{label}-full.png"), full_page=True)

    # Services band — measure live, don't assume
    services = page.locator(".lt-btfp__services")
    sb = services.bounding_box()
    if sb:
        page.screenshot(path=str(OUT / f"{label}-services.png"),
                        clip={"x": 0, "y": sb["y"] - 8,
                              "width": viewport["width"],
                              "height": sb["height"] + 16})

    # Force show each carousel image individually
    if label == "desktop":
        # Pause animation, set all carousel imgs opacity to 0
        page.evaluate("""() => {
            const sheet = document.styleSheets;
            document.querySelectorAll('.lt-btfp__carousel-img').forEach(el => {
                el.style.animation = 'none';
                el.style.opacity = '0';
            });
        }""")
        carousels = page.locator(".lt-btfp__carousel").all()
        for ci, carousel in enumerate(carousels, 1):
            label_name = "twisting" if ci == 2 else "facepainting"  # order in DOM
            imgs = carousel.locator(".lt-btfp__carousel-img").all()
            for pi, img in enumerate(imgs, 1):
                page.evaluate("""(els) => {
                    els.forEach(e => e.style.opacity = '0');
                }""", carousel.locator(".lt-btfp__carousel-img").all())
                # Show just this one
                page.evaluate("""(el) => { el.style.opacity = '1'; }""", img)
                page.wait_for_timeout(120)
                src = img.get_attribute("src") or ""
                fn = src.rsplit("/", 1)[-1]
                box = carousel.bounding_box()
                if box and box["width"] > 0:
                    img.scroll_into_view_if_needed()
                    page.wait_for_timeout(80)
                    box = carousel.bounding_box()
                    page.screenshot(path=str(OUT / f"{label_name}-{pi}-{fn}.png"),
                                    clip={"x": box["x"], "y": box["y"],
                                          "width": box["width"], "height": box["height"]})


def main():
    with sync_playwright() as p:
        capture(p, {"width": 1280, "height": 900}, "desktop")
        capture(p, {"width": 390, "height": 844}, "mobile")
    print(f"\nSaved to: {OUT}")


if __name__ == "__main__":
    main()
