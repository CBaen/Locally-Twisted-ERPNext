"""
Capture the LT home page using a real Chromium browser via Playwright.

Replaces the prior `chrome --headless --screenshot` approach, which was
producing screenshots that did not match what GL actually saw in their
browser. Playwright's chromium gives us proper networkidle-wait, full-page
captures, and rendering closer to real-browser behavior.

Outputs:
  C:/Users/baenb/.claude/lt-playwright-desktop.png  (1366x900 viewport, full page)
  C:/Users/baenb/.claude/lt-playwright-mobile.png   (375x812 viewport, full page)

Run:
  PYTHONIOENCODING=utf-8 PYTHONUTF8=1 python scripts/verify/playwright_home_screenshot.py
"""
from __future__ import annotations

from pathlib import Path

from _cli import parse_noop_args

from playwright.sync_api import sync_playwright

URL = "http://localhost:8081/"
OUT_DIR = Path("C:/Users/baenb/.claude")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def capture(p, viewport, output_path, *, is_mobile=False):
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
    page.goto(URL, wait_until="networkidle", timeout=15000)
    # Page Builder uses intersection-observer lazy-load on images; scroll
    # the full page so all data-src images get swapped in before capture.
    page.evaluate("""async () => {
      const distance = 200;
      const delay = 80;
      const height = document.body.scrollHeight;
      for (let y = 0; y < height; y += distance) {
        window.scrollTo(0, y);
        await new Promise(r => setTimeout(r, delay));
      }
      window.scrollTo(0, 0);
    }""")
    page.wait_for_load_state("networkidle", timeout=15000)
    page.wait_for_timeout(1500)
    page.screenshot(path=str(output_path), full_page=True)

    # While we're here, capture a few facts about what's actually in the DOM
    facts = {
        "title": page.title(),
        "navbar_count": page.locator("nav.navbar").count(),
        "navbar_brand_text": page.locator(".navbar-brand").first.inner_text() if page.locator(".navbar-brand").count() else None,
        "nav_link_texts": [a.inner_text() for a in page.locator(".navbar-nav .nav-link").all()],
        "footer_count": page.locator("footer.web-footer").count(),
        "footer_bg_color": page.locator("footer.web-footer").first.evaluate("el => getComputedStyle(el).backgroundColor") if page.locator("footer.web-footer").count() else None,
        "footer_column_titles": [el.inner_text() for el in page.locator(".web-footer .footer-group-label").all()],
        "footer_brand_visible": page.locator(".lt-footer-brand").count(),
        "lt_theme_link_count": page.locator("link[href*='lt-theme.css']").count(),
        "h1_text": page.locator("h1").first.inner_text() if page.locator("h1").count() else None,
        "viewport_width": page.evaluate("() => window.innerWidth"),
    }

    browser.close()
    return facts


def main():
    parse_noop_args(__doc__)
    with sync_playwright() as p:
        print("→ Capturing desktop view (1366x900)...")
        d = capture(p, {"width": 1366, "height": 900}, OUT_DIR / "lt-playwright-desktop.png")
        print(f"  saved: {OUT_DIR / 'lt-playwright-desktop.png'}")
        print(f"  facts: {d}")
        print()
        print("→ Capturing mobile view (375x812)...")
        m = capture(p, {"width": 375, "height": 812}, OUT_DIR / "lt-playwright-mobile.png", is_mobile=True)
        print(f"  saved: {OUT_DIR / 'lt-playwright-mobile.png'}")
        print(f"  facts: {m}")


if __name__ == "__main__":
    main()
