#!/usr/bin/env python3
"""Render swirl-arch.html at all 4 sizes (20/25/30/40 ft) at desktop viewport.
Verifies the size selector now produces visibly different scales (after the
camera-fixing physics correction)."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

REF_DIR = Path(__file__).resolve().parent
RENDER_DIR = REF_DIR.parent / "_render" / "physics-reference"
RENDER_DIR.mkdir(parents=True, exist_ok=True)

URL = (REF_DIR / "swirl-arch.html").as_uri()
SIZES = [20, 25, 30, 40]
VIEWPORT = {"width": 1280, "height": 1100}


def capture():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport=VIEWPORT, device_scale_factor=2)
        page = ctx.new_page()
        page.goto(URL, timeout=30000, wait_until="networkidle")
        page.wait_for_timeout(2500)
        for size in SIZES:
            print(f"[size={size}ft] toggling and capturing")
            page.evaluate(f"""
                document.querySelector('input[name="size"][value="{size}"]').click();
            """)
            page.wait_for_timeout(1200)
            # Crop to just the canvas area for clearer side-by-side comparison
            canvas = page.locator(".scene")
            box = canvas.bounding_box()
            if box:
                out = RENDER_DIR / f"swirl-arch-{size}ft-canvas.png"
                page.screenshot(
                    path=str(out),
                    clip={
                        "x": box["x"],
                        "y": box["y"],
                        "width": box["width"],
                        "height": box["height"],
                    },
                )
                print(f"[size={size}ft] canvas-only -> {out.name}")
            full = RENDER_DIR / f"swirl-arch-{size}ft-fullpage.png"
            page.screenshot(path=str(full), full_page=True)
            print(f"[size={size}ft] full-page    -> {full.name}")
        ctx.close()
        browser.close()


if __name__ == "__main__":
    capture()
