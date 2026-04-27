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

    # Force show each carousel image individually (desktop only)
    if label == "desktop":
        page.evaluate("""() => {
            document.querySelectorAll('.lt-btfp__carousel-img').forEach(el => {
                el.style.animation = 'none';
                el.style.opacity = '0';
            });
        }""")
        # Get a flat list of (carousel-index, img-index, src) to iterate over from JS
        descriptor = page.evaluate("""() => {
            const out = [];
            document.querySelectorAll('.lt-btfp__carousel').forEach((c, ci) => {
                c.querySelectorAll('.lt-btfp__carousel-img').forEach((img, pi) => {
                    out.push({ ci, pi, src: img.getAttribute('src') });
                });
            });
            return out;
        }""")
        for item in descriptor:
            ci, pi, src = item["ci"], item["pi"], item["src"]
            label_name = "facepainting" if ci == 0 else "twisting"
            fn = src.rsplit("/", 1)[-1]
            page.evaluate(
                """({ci, pi}) => {
                    document.querySelectorAll('.lt-btfp__carousel-img').forEach(el => el.style.opacity = '0');
                    const c = document.querySelectorAll('.lt-btfp__carousel')[ci];
                    const img = c.querySelectorAll('.lt-btfp__carousel-img')[pi];
                    img.style.opacity = '1';
                    c.scrollIntoView({block:'center'});
                }""",
                {"ci": ci, "pi": pi},
            )
            page.wait_for_timeout(180)
            box = page.evaluate(
                """(ci) => {
                    const c = document.querySelectorAll('.lt-btfp__carousel')[ci];
                    const r = c.getBoundingClientRect();
                    return { x: r.x, y: r.y, w: r.width, h: r.height };
                }""", ci,
            )
            if box and box["w"] > 0:
                page.screenshot(path=str(OUT / f"{label_name}-{pi+1}-{fn}.png"),
                                clip={"x": box["x"], "y": box["y"],
                                      "width": box["w"], "height": box["h"]})


def main():
    with sync_playwright() as p:
        capture(p, {"width": 1280, "height": 900}, "desktop")
        capture(p, {"width": 390, "height": 844}, "mobile")
    print(f"\nSaved to: {OUT}")


if __name__ == "__main__":
    main()
