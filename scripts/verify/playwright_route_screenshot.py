"""Capture any LT route at desktop + mobile via Playwright.

Saves to C:/Users/baenb/.claude/lt-{slug}-{viewport}.png so the file is
trivially Read-able from a future Claude session.

Run:
    PYTHONIOENCODING=utf-8 PYTHONUTF8=1 \\
        python scripts/verify/playwright_route_screenshot.py /contact
"""
from __future__ import annotations

import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT_DIR = Path("C:/Users/baenb/.claude")
OUT_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_BASE = "http://localhost:8081"


def slugify(route: str) -> str:
    return route.strip("/").replace("/", "-") or "home"


def capture(p, url: str, viewport: dict, output_path: Path, *, is_mobile: bool = False) -> None:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport=viewport,
        is_mobile=is_mobile,
        user_agent=(
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) "
            "AppleWebKit/605.1.15 Version/16.0 Mobile/15E148 Safari/604.1"
        ) if is_mobile else None,
    )
    page = context.new_page()
    page.goto(url, wait_until="networkidle", timeout=20000)
    page.evaluate("""async () => {
        const distance = 240;
        const delay = 80;
        const h = document.body.scrollHeight;
        for (let y = 0; y < h; y += distance) {
            window.scrollTo(0, y);
            await new Promise(r => setTimeout(r, delay));
        }
        window.scrollTo(0, 0);
    }""")
    page.wait_for_load_state("networkidle", timeout=15000)
    page.wait_for_timeout(1200)
    page.screenshot(path=str(output_path), full_page=True)
    browser.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("route", help="Route path to capture, for example /contact")
    parser.add_argument("base_url", nargs="?", default=DEFAULT_BASE, help=f"Base URL. Default: {DEFAULT_BASE}")
    args = parser.parse_args()

    route = args.route
    base = args.base_url
    url = f"{base.rstrip('/')}/{route.lstrip('/')}"
    slug = slugify(route)

    desktop_path = OUT_DIR / f"lt-{slug}-desktop.png"
    mobile_path = OUT_DIR / f"lt-{slug}-mobile.png"

    with sync_playwright() as p:
        print(f"-> Desktop {url}")
        capture(p, url, {"width": 1366, "height": 900}, desktop_path)
        print(f"   saved: {desktop_path}")
        print(f"-> Mobile  {url}")
        capture(p, url, {"width": 375, "height": 812}, mobile_path, is_mobile=True)
        print(f"   saved: {mobile_path}")


if __name__ == "__main__":
    main()
