#!/usr/bin/env python3
"""
Render the physics reference prototype(s) at mobile + desktop.

Output: _render/physics-reference/{shape}-{viewport}.png
"""
import sys
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("FAIL - playwright not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)

REF_DIR = Path(__file__).resolve().parent
CONTEST_DIR = REF_DIR.parent
RENDER_DIR = CONTEST_DIR / "_render" / "physics-reference"

SHAPES = ["swirl-arch"]
VIEWPORTS = {
    "mobile": {"width": 375, "height": 900},
    "desktop": {"width": 1280, "height": 1100},
}


def capture_all() -> int:
    fails: list[str] = []
    successes = 0
    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for viewport_name, viewport in VIEWPORTS.items():
            ctx = browser.new_context(viewport=viewport, device_scale_factor=2)
            page = ctx.new_page()
            for shape in SHAPES:
                html_path = REF_DIR / f"{shape}.html"
                if not html_path.exists():
                    fails.append(f"{shape}.html - missing")
                    continue
                url = html_path.as_uri()
                output_path = RENDER_DIR / f"{shape}-{viewport_name}.png"
                print(f"[{viewport_name:7s}] {shape:14s} -> {output_path.relative_to(CONTEST_DIR)}")
                try:
                    page.goto(url, timeout=15000, wait_until="domcontentloaded")
                    page.wait_for_timeout(600)
                    body_text = page.locator("body").inner_text().strip()
                    if not body_text:
                        fails.append(f"{shape} {viewport_name} - empty body")
                        continue
                    page.screenshot(path=str(output_path), full_page=True)
                    successes += 1
                except PlaywrightTimeout:
                    fails.append(f"{shape} {viewport_name} - timeout")
                except Exception as e:
                    fails.append(f"{shape} {viewport_name} - {e}")
            ctx.close()
        browser.close()

    print()
    print(f"Captured {successes} screenshots to {RENDER_DIR.relative_to(CONTEST_DIR)}/")
    if fails:
        print(f"FAILURES ({len(fails)}):")
        for f in fails:
            print(f"  - {f}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(capture_all())
