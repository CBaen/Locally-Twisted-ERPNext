#!/usr/bin/env python3
"""Verify /contact query/session prefill behavior for the shared inquiry form."""
import argparse
import json
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
ITEM_CASE = ("/contact?item=easter-arch", "easter-arch", "Easter Arch")
QUOTE_HANDOFF_KEY = "lt_checkout_quote_handoff_v1"


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

        item_path, item_code, item_name = ITEM_CASE
        item_url = base_url + item_path
        print(f"[PREFILL] {item_url}")
        try:
            page.goto(item_url, wait_until="networkidle", timeout=30000)
        except PlaywrightTimeout:
            print("  FAIL - item prefill page did not load")
            failures += 1
        else:
            decor = page.locator('input[name="x_services"][value="Balloon Decor"]')
            if decor.count() != 1 or not decor.first.is_checked():
                print("  FAIL - Balloon Decor should be checked for product quote links")
                failures += 1
            hidden = page.locator(f'input[name="lt_requested_item_code"][value="{item_code}"]')
            if hidden.count() != 1:
                print("  FAIL - requested item hidden field missing")
                failures += 1
            if page.locator(".lt-book__prefill", has_text=item_name).count() != 1:
                print("  FAIL - requested item prefill banner missing")
                failures += 1
            else:
                print(f"  OK - product quote prefilled for {item_name}")

        print("[PREFILL] checkout delivery quote handoff")
        payload = {
            "source": "checkout",
            "reason": "out_of_area_delivery",
            "customer": {
                "name": "Casey Delivery",
                "phone": "801-555-0144",
                "email": "casey@example.invalid",
            },
            "fulfillment": {
                "method": "delivery",
                "requested_date": "2026-06-15",
                "window_start": "13:00",
                "window_end": "13:30",
                "address_line1": "123 Red Rock Road",
                "address_line2": "Suite 5",
                "city": "St. George",
                "state": "UT",
                "postal_code": "84770",
            },
            "items": [
                {
                    "item_code": "mothers-day-bouquet",
                    "name": "Mother's Day Bouquet",
                    "qty": 2,
                }
            ],
            "notes": "Please call before delivery.",
        }
        page.goto(base_url + "/", wait_until="domcontentloaded", timeout=30000)
        page.evaluate(
            """([key, payload]) => {
                window.sessionStorage.setItem(key, JSON.stringify(payload));
            }""",
            [QUOTE_HANDOFF_KEY, payload],
        )
        try:
            page.goto(base_url + "/contact?intent=quote&source=checkout-delivery", wait_until="networkidle", timeout=30000)
        except PlaywrightTimeout:
            print("  FAIL - checkout quote handoff page did not load")
            failures += 1
        else:
            expected_values = {
                "#book_name": "Casey Delivery",
                "#book_phone": "801-555-0144",
                "#book_email": "casey@example.invalid",
                "#book_date": "2026-06-15",
            }
            for selector, expected in expected_values.items():
                value = page.locator(selector).input_value()
                if value != expected:
                    print(f"  FAIL - {selector} expected {expected!r}, found {value!r}")
                    failures += 1
            location = page.locator("#book_location").input_value()
            if "123 Red Rock Road" not in location or "84770" not in location:
                print(f"  FAIL - location did not include delivery address and ZIP: {location!r}")
                failures += 1
            notes = page.locator("#book_notes").input_value()
            if "Interested item: Mother's Day Bouquet" not in notes or "mothers-day-bouquet" not in notes:
                print(f"  FAIL - notes did not include interested item payload: {notes!r}")
                failures += 1
            if "Please call before delivery." not in notes:
                print(f"  FAIL - notes did not keep checkout note: {notes!r}")
                failures += 1
            delivery = page.locator('input[name="x_services"][value="Delivery"]')
            if delivery.count() != 1 or not delivery.first.is_checked():
                print("  FAIL - Delivery should be checked for checkout delivery quote handoff")
                failures += 1
            delivery_notes = page.locator("#book_delivery_notes")
            if delivery_notes.count() != 1 or not delivery_notes.first.is_enabled():
                print("  FAIL - Delivery notes should be enabled for handoff")
                failures += 1
            elif "out of standard delivery area" not in delivery_notes.first.input_value().lower():
                print(f"  FAIL - delivery notes did not explain delivery quote: {delivery_notes.first.input_value()!r}")
                failures += 1
            if failures == 0:
                print("  OK - checkout delivery quote handoff prefilled contact form")

        browser.close()

    if failures:
        print(f"[PREFILL] {failures} failure(s)")
        return 1
    print("[PREFILL] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
