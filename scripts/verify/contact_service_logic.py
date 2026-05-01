#!/usr/bin/env python3
"""Verify service-specific conditional fields on the /contact inquiry form."""
import argparse
import sys

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("FAIL - playwright not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)


BASE_PATH = "/contact"
PACKAGE_ITEMS = [
    "Balloon Arches",
    "Columns",
    "Garlands",
    "Picture Perfect Backdrops",
    "Balloon Drops",
    "Balloon Bouquets",
    "Centerpieces",
    "Custom Sculptures",
]


def expect_checkbox(page, value: str, *, present: bool = True) -> list[str]:
    errors = []
    locator = page.locator(f'input[name="x_services"][value="{value}"]')
    count = locator.count()
    if present and count != 1:
        errors.append(f"checkbox {value!r} expected once, found {count}")
    if not present and count != 0:
        errors.append(f"checkbox {value!r} should not be present")
    return errors


def panel(page, condition: str):
    return page.locator(f'[data-visibility-condition="{condition}"]')


def expect_panel(page, condition: str, *, visible: bool) -> list[str]:
    errors = []
    locator = panel(page, condition)
    count = locator.count()
    if count != 1:
        errors.append(f"panel {condition!r} expected once, found {count}")
        return errors
    is_visible = locator.first.is_visible()
    if visible and not is_visible:
        errors.append(f"panel {condition!r} should be visible")
    if not visible and is_visible:
        errors.append(f"panel {condition!r} should be hidden")
    return errors


def expect_absent_panel(page, condition: str) -> list[str]:
    locator = panel(page, condition)
    if locator.count() != 0:
        return [f"panel {condition!r} should not exist"]
    return []


def check_service(page, value: str, expected_visible: set[str], expected_hidden: set[str]) -> list[str]:
    errors = []
    page.locator('input[name="x_services"]').evaluate_all(
        "(nodes) => nodes.forEach((node) => { node.checked = false; node.dispatchEvent(new Event('change', { bubbles: true })); })"
    )
    checkbox = page.locator(f'input[name="x_services"][value="{value}"]')
    if checkbox.count() != 1:
        return [f"cannot check service {value!r}; checkbox not found"]
    checkbox.check()

    for condition in sorted(expected_visible):
        errors.extend(expect_panel(page, condition, visible=True))
    for condition in sorted(expected_hidden):
        errors.extend(expect_panel(page, condition, visible=False))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True, help="Example: http://localhost:8081")
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")

    failures = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 390, "height": 900})
        try:
            page.goto(base_url + BASE_PATH, wait_until="networkidle", timeout=30000)
        except PlaywrightTimeout:
            print("FAIL - /contact did not load")
            browser.close()
            return 1

        failures.extend(expect_checkbox(page, "Events Inquiry"))
        failures.extend(expect_checkbox(page, "Event Package", present=False))
        failures.extend(expect_absent_panel(page, "Something Else"))

        failures.extend(check_service(
            page,
            "Balloon Decor",
            {"Balloon Decor"},
            {"Balloon Twisting", "Face Painting", "Delivery Only", "Events Inquiry", "Event Environment"},
        ))
        failures.extend(check_service(
            page,
            "Delivery Only",
            {"Delivery Only"},
            {"Balloon Decor", "Balloon Twisting", "Face Painting", "Pickup Only", "Events Inquiry", "Event Environment"},
        ))
        failures.extend(check_service(
            page,
            "Pickup Only",
            {"Pickup Only"},
            {"Balloon Decor", "Balloon Twisting", "Face Painting", "Delivery Only", "Events Inquiry", "Event Environment"},
        ))
        failures.extend(check_service(
            page,
            "Events Inquiry",
            {"Events Inquiry"},
            {"Balloon Decor", "Balloon Twisting", "Face Painting", "Delivery Only", "Pickup Only", "Event Environment"},
        ))
        events_panel = panel(page, "Events Inquiry")
        if events_panel.count() == 1 and events_panel.first.is_visible():
            heading = events_panel.locator(".lt-book__conditional-title").first.text_content() or ""
            if heading.strip() != "Let's build a memory":
                failures.append("Events Inquiry heading should be \"Let's build a memory\"")
            for item in PACKAGE_ITEMS:
                item_checkbox = events_panel.locator(f'input[name="x_package_items"][value="{item}"]')
                if item_checkbox.count() != 1:
                    failures.append(f"Events Inquiry package item {item!r} should be a checkbox")
            if events_panel.locator("#book_package_colors").count() != 1:
                failures.append("Events Inquiry should ask for package colors")
            if events_panel.locator("#book_package_notes").count() != 1:
                failures.append("Events Inquiry should keep one memory/vibe notes box")
            if events_panel.locator("#book_decor_types").count() != 0:
                failures.append("Events Inquiry should not use the freeform decor types field")
        failures.extend(check_service(
            page,
            "Balloon Twisting",
            {"Balloon Twisting", "Event Environment"},
            {"Balloon Decor", "Face Painting", "Delivery Only", "Pickup Only", "Events Inquiry"},
        ))
        failures.extend(check_service(
            page,
            "Face Painting",
            {"Face Painting", "Event Environment"},
            {"Balloon Decor", "Balloon Twisting", "Delivery Only", "Pickup Only", "Events Inquiry"},
        ))

        shade = page.locator("#book_shade_required")
        if shade.count() != 1:
            failures.append("shade checkbox should exist once inside Event Environment")
        if page.get_by_text("Northern Utah Location (Residential Address)").count() < 1:
            failures.append("Riverdale location should be labeled as Northern Utah Location (Residential Address)")

        browser.close()

    if failures:
        print("[SERVICE LOGIC] FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("[SERVICE LOGIC] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
