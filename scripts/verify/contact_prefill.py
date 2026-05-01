#!/usr/bin/env python3
"""Verify /contact service query parameters preselect the shared inquiry form."""
import argparse
import sys

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("FAIL - playwright not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)


CASES = [
    ("/contact?service=btfp", ["Balloon Twisting", "Face Painting"]),
    ("/contact?service=twisting", ["Balloon Twisting"]),
    ("/contact?service=face-painting", ["Face Painting"]),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True, help="Example: http://localhost:8081")
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")

    failures = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 390, "height": 900})
        for path, expected_services in CASES:
            url = base_url + path
            print(f"[PREFILL] {url}")
            try:
                page.goto(url, wait_until="networkidle", timeout=30000)
            except PlaywrightTimeout:
                print("  FAIL - page did not load")
                failures += 1
                continue

            for service in expected_services:
                locator = page.locator(f'input[name="x_services"][value="{service}"]')
                if locator.count() != 1:
                    print(f"  FAIL - checkbox for {service!r} not found")
                    failures += 1
                    continue
                if not locator.first.is_checked():
                    print(f"  FAIL - checkbox for {service!r} is not checked")
                    failures += 1
                else:
                    print(f"  OK - {service} checked")

            if "Balloon Twisting" in expected_services:
                twisting_panel = page.locator('[data-visibility-condition="Balloon Twisting"]')
                if twisting_panel.count() != 1 or not twisting_panel.first.is_visible():
                    print("  FAIL - Balloon Twisting details panel is not visible")
                    failures += 1
            if "Face Painting" in expected_services:
                painting_panel = page.locator('[data-visibility-condition="Face Painting"]')
                if painting_panel.count() != 1 or not painting_panel.first.is_visible():
                    print("  FAIL - Face Painting details panel is not visible")
                    failures += 1

        browser.close()

    if failures:
        print(f"[PREFILL] {failures} failure(s)")
        return 1
    print("[PREFILL] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
