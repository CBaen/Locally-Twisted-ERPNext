#!/usr/bin/env python3
"""Focused capture of the BTFP services band at native resolution.

Scrolls, measures the band live, then clips precisely so the saved PNG
shows the carousels at their true rendered size with no downscale.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:8081"
OUT = Path(__file__).resolve().parent / "_screenshots" / "btfp-band-2026-04-27"
OUT.mkdir(parents=True, exist_ok=True)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1280, "height": 1200}, device_scale_factor=2)
        page = ctx.new_page()
        page.goto(BASE_URL + "/balloon-twisting-and-face-painting", wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(800)

        # Pause carousel animations so we capture stable images, then show the
        # second image in each carousel for variety
        page.evaluate("""() => {
            document.querySelectorAll('.lt-btfp__carousel-img').forEach(el => {
                el.style.animation = 'none';
                el.style.opacity = '0';
            });
            document.querySelectorAll('.lt-btfp__carousel').forEach(c => {
                const imgs = c.querySelectorAll('.lt-btfp__carousel-img');
                if (imgs[0]) imgs[0].style.opacity = '1';
            });
        }""")

        page.wait_for_timeout(200)

        # Scroll the services band into view and measure
        info = page.evaluate("""() => {
            const el = document.querySelector('.lt-btfp__services');
            el.scrollIntoView({block:'start'});
            const r = el.getBoundingClientRect();
            return { x: r.x, y: r.y, w: r.width, h: r.height, scrollY: window.scrollY };
        }""")
        page.wait_for_timeout(200)

        info2 = page.evaluate("""() => {
            const el = document.querySelector('.lt-btfp__services');
            const r = el.getBoundingClientRect();
            return { x: r.x, y: r.y, w: r.width, h: r.height };
        }""")

        # Capture at the band's actual rendered size
        page.screenshot(
            path=str(OUT / "services-band-desktop.png"),
            clip={"x": 0, "y": max(0, info2["y"]),
                  "width": 1280, "height": min(info2["h"] + 24, 1200 - max(0, int(info2["y"])))},
        )

        # Also capture each carousel individually (just the carousel, not the card chrome)
        carousels = page.evaluate("""() => {
            const out = [];
            document.querySelectorAll('.lt-btfp__carousel').forEach((c, i) => {
                const r = c.getBoundingClientRect();
                out.push({i, x: r.x, y: r.y, w: r.width, h: r.height});
            });
            return out;
        }""")
        for c in carousels:
            label = "facepainting" if c["i"] == 0 else "twisting"
            page.screenshot(
                path=str(OUT / f"carousel-{label}.png"),
                clip={"x": c["x"], "y": c["y"], "width": c["w"], "height": c["h"]},
            )
            print(f"carousel {label}: {c['w']:.0f}x{c['h']:.0f}")

        browser.close()
    print(f"\nSaved to: {OUT}")


if __name__ == "__main__":
    main()
