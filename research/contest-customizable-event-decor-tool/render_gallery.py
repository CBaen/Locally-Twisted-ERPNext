#!/usr/bin/env python3
"""
Render gallery for the Customizable Event Decor Design Tool contest.

Captures static-HTML mockups via file:// URLs at mobile + desktop viewports.
4 contestants × 6 screens × 2 viewports = 48 screenshots.

Output:
    _render/contestant-{N}/{screen}-{viewport}.png

Run from the contest directory:
    python render_gallery.py
"""
import sys
import time
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("FAIL — playwright not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)

CONTEST_DIR = Path(__file__).resolve().parent
RENDER_DIR = CONTEST_DIR / "_render"

CONTESTANTS = [1, 2, 3, 4]
SCREENS = [
    "01-entry",
    "02-color-one",
    "03-picker",
    "04-composition",
    "05-done",
    "06-upsell",
    "index",
]
VIEWPORTS = {
    "mobile": {"width": 375, "height": 812},
    "desktop": {"width": 1280, "height": 900},
}


def capture_all() -> int:
    fails: list[str] = []
    successes = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for viewport_name, viewport in VIEWPORTS.items():
            ctx = browser.new_context(viewport=viewport, device_scale_factor=2)
            page = ctx.new_page()
            for n in CONTESTANTS:
                for screen in SCREENS:
                    html_path = CONTEST_DIR / f"contestant-{n}" / "mockup" / f"{screen}.html"
                    if not html_path.exists():
                        fails.append(f"contestant-{n}/{screen}.html — missing")
                        continue
                    url = html_path.as_uri()
                    output_path = RENDER_DIR / f"contestant-{n}" / f"{screen}-{viewport_name}.png"
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    print(f"[{viewport_name:7s}] c{n} {screen:14s} -> {output_path.relative_to(CONTEST_DIR)}")
                    try:
                        page.goto(url, timeout=15000, wait_until="domcontentloaded")
                        # Static HTML; no network. Just let inline assets settle.
                        page.wait_for_timeout(400)
                        body_text = page.locator("body").inner_text().strip()
                        if not body_text:
                            fails.append(f"c{n}/{screen} {viewport_name} — empty body")
                            continue
                        page.screenshot(path=str(output_path), full_page=True)
                        successes += 1
                    except PlaywrightTimeout:
                        fails.append(f"c{n}/{screen} {viewport_name} — timeout")
                    except Exception as e:
                        fails.append(f"c{n}/{screen} {viewport_name} — {e}")
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
