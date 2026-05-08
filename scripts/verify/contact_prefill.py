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
BTFP_PAGE = "/balloon-twisting-and-face-painting"
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

        btfp_url = base_url + BTFP_PAGE
        print(f"[PREFILL] {btfp_url}")
        try:
            page.goto(btfp_url, wait_until="networkidle", timeout=30000)
        except PlaywrightTimeout:
            print("  FAIL - BTFP page did not load")
            failures += 1
        else:
            body_text = page.locator("body").inner_text(timeout=10000)
            if "THE PROCESS" in body_text or "Booking is straightforward" in body_text:
                print("  FAIL - BTFP page still contains the unapproved process section")
                failures += 1
            if page.locator("#lt-book-form").count() != 1:
                print("  FAIL - BTFP page should reuse the shared intake form")
                failures += 1

            service_values = page.locator('input[name="x_services"]').evaluate_all(
                "(nodes) => nodes.map((node) => node.value)"
            )
            expected_values = ["Balloon Twisting", "Face Painting"]
            if service_values != expected_values:
                print(f"  FAIL - BTFP page should expose only live-service choices, found {service_values!r}")
                failures += 1
            else:
                print("  OK - BTFP page shows only live-service choices")

            for service in expected_values:
                locator = page.locator(f'input[name="x_services"][value="{service}"]')
                if locator.count() != 1 or not locator.first.is_checked():
                    print(f"  FAIL - BTFP page should preselect {service!r}")
                    failures += 1
            for hidden_service in ["Balloon Decor", "Delivery", "Pickup", "Events Inquiry", "Something Else"]:
                if page.locator(f'input[name="x_services"][value="{hidden_service}"]').count() != 0:
                    print(f"  FAIL - BTFP page should not expose {hidden_service!r}")
                    failures += 1

            support_banner = page.locator(".lt-btfp__banner")
            if support_banner.count() != 1:
                print("  FAIL - BTFP page should include the last-minute support banner")
                failures += 1
            else:
                support_background = support_banner.first.evaluate("node => getComputedStyle(node).backgroundColor")
                if support_background != "rgb(14, 34, 64)":
                    print(f"  FAIL - BTFP support banner should use brand blue, found {support_background}")
                    failures += 1
                support_color = support_banner.first.evaluate("node => getComputedStyle(node).color")
                if support_color not in {"rgb(250, 247, 242)", "rgb(255, 255, 255)"}:
                    print(f"  FAIL - BTFP support banner text should be light on brand blue, found {support_color}")
                    failures += 1

            crawl = page.locator(".lt-btfp__event-crawl")
            if crawl.count() != 1:
                print("  FAIL - BTFP page should include the event-type crawl")
                failures += 1
            else:
                background = crawl.first.evaluate("node => getComputedStyle(node).backgroundColor")
                if background != "rgb(14, 34, 64)":
                    print(f"  FAIL - BTFP crawl banner should use brand blue, found {background}")
                    failures += 1
                color = crawl.first.evaluate("node => getComputedStyle(node).color")
                if color != "rgb(250, 247, 242)" and color != "rgb(255, 255, 255)":
                    print(f"  FAIL - BTFP crawl text should be light on brand blue, found {color}")
                    failures += 1
                before = page.evaluate(
                    """() => {
                        const track = document.querySelector('.lt-btfp__event-crawl-track');
                        if (!track) return null;
                        const style = getComputedStyle(track);
                        const matrix = new DOMMatrixReadOnly(style.transform);
                        return { x: matrix.m41, animationName: style.animationName };
                    }"""
                )
                page.wait_for_timeout(650)
                after = page.evaluate(
                    """() => {
                        const track = document.querySelector('.lt-btfp__event-crawl-track');
                        if (!track) return null;
                        const matrix = new DOMMatrixReadOnly(getComputedStyle(track).transform);
                        return { x: matrix.m41 };
                    }"""
                )
                if not before or not after or before.get("animationName") != "lt-btfp-event-crawl-scroll":
                    print(f"  FAIL - BTFP event crawl should animate, found {before!r}")
                    failures += 1
                elif after.get("x") <= before.get("x"):
                    print(f"  FAIL - BTFP event crawl should move left-to-right, before={before!r} after={after!r}")
                    failures += 1
            if page.locator('a[href="/shop/event-booking-deposit-32"]').count() != 0:
                print("  FAIL - BTFP page should not restore the old public deposit checkout CTA")
                failures += 1

            calculator = page.locator(".lt-btfp__calculator")
            if calculator.count() != 1:
                print("  FAIL - BTFP page should include the customer pricing calculator")
                failures += 1
            else:
                page.locator("#btfp_calc_hours").fill("1.5")
                page.locator("#btfp_calc_service_both").check()
                calc_state = page.evaluate(
                    """() => ({
                        total: document.querySelector('[data-btfp-calc-total]')?.textContent?.trim(),
                        deposit: document.querySelector('[data-btfp-calc-deposit]')?.textContent?.trim(),
                        balance: document.querySelector('[data-btfp-calc-balance]')?.textContent?.trim(),
                        formula: document.querySelector('[data-btfp-calc-formula]')?.textContent?.trim(),
                    })"""
                )
                if calc_state.get("total") != "$375":
                    print(f"  FAIL - 1.5 hours for both services should total $375, found {calc_state!r}")
                    failures += 1
                if calc_state.get("deposit") != "$100":
                    print(f"  FAIL - both services should show $100 deposit, found {calc_state!r}")
                    failures += 1
                if calc_state.get("balance") != "$275":
                    print(f"  FAIL - both services at 1.5 hours should show $275 balance, found {calc_state!r}")
                    failures += 1
                if "No discounts" not in (calc_state.get("formula") or ""):
                    print(f"  FAIL - calculator formula should state no discounts, found {calc_state!r}")
                    failures += 1
                page.locator("#btfp_calc_hours").fill("0.5")
                min_state = page.evaluate(
                    """() => ({
                        hours: document.querySelector('#btfp_calc_hours')?.value,
                        total: document.querySelector('[data-btfp-calc-total]')?.textContent?.trim(),
                    })"""
                )
                if min_state.get("hours") != "1" or min_state.get("total") != "$260":
                    print(f"  FAIL - BTFP calculator should not allow less than 1 hour, found {min_state!r}")
                    failures += 1

            if page.locator('.lt-book[data-form-contract="inquiry-v1"] #lt-book-form[data-form-contract="inquiry-v1"]').count() != 1:
                print("  FAIL - shared inquiry form should declare the form design contract")
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
