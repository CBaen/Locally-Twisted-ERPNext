#!/usr/bin/env python3
"""Capture the actual render from GL's locally-twisted-app design page as ground truth."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "_render" / "physics-reference"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

URL = "http://localhost:3000/design"
VIEWPORTS = {
    "mobile": {"width": 375, "height": 1200},
    "desktop": {"width": 1280, "height": 1100},
}


def capture():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for name, vp in VIEWPORTS.items():
            ctx = browser.new_context(viewport=vp, device_scale_factor=2)
            page = ctx.new_page()
            print(f"[{name}] navigating to {URL}")
            page.goto(URL, timeout=60000, wait_until="networkidle")
            # Three.js takes a moment to initialize + first frame to paint
            page.wait_for_timeout(3500)
            out = OUTPUT_DIR / f"GL-actual-{name}.png"
            page.screenshot(path=str(out), full_page=True)
            print(f"[{name}] saved {out}")
            ctx.close()
        browser.close()


if __name__ == "__main__":
    capture()
