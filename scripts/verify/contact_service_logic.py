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

        phone = page.locator("#book_phone")
        if phone.count() != 1:
            failures.append("phone field should exist once")
        else:
            if phone.get_attribute("required") is None:
                failures.append("phone field should be required")
            if phone.get_attribute("autocomplete") != "tel":
                failures.append("phone field should preserve autocomplete=tel")
            if "book_phone_helper" not in (phone.get_attribute("aria-describedby") or ""):
                failures.append("phone field should point to approved helper copy")
            phone_helper = page.locator("#book_phone_helper")
            if phone_helper.count() != 1 or "Used solely in regards to your inquiry." not in (phone_helper.text_content() or ""):
                failures.append("phone helper should use approved copy")

        email = page.locator("#book_email")
        if email.count() != 1:
            failures.append("email field should exist once")
        else:
            if email.get_attribute("required") is None:
                failures.append("email field should be required")
            if email.get_attribute("autocomplete") != "email":
                failures.append("email field should preserve autocomplete=email")
            described_by = email.get_attribute("aria-describedby") or ""
            for expected_id in ("book_email_helper", "book_email_hint"):
                if expected_id not in described_by:
                    failures.append(f"email field should point to {expected_id}")
            helper = page.locator("#book_email_helper")
            if helper.count() != 1 or "Used solely in regards to your inquiry." not in (helper.text_content() or ""):
                failures.append("email helper should use approved copy")
            email.fill("casey@gamil.com")
            email.blur()
            hint = page.locator("#book_email_hint")
            if hint.count() != 1 or "casey@gmail.com" not in (hint.text_content() or ""):
                failures.append("email typo hint should suggest casey@gmail.com for gamil.com")

        preferred = page.locator("#book_preferred_contact_method")
        if preferred.count() != 1:
            failures.append("preferred contact method field should exist once")
        else:
            if preferred.get_attribute("required") is None:
                failures.append("preferred contact method should be required")
            if preferred.get_attribute("aria-describedby") and "book_preferred_contact_method_helper" in preferred.get_attribute("aria-describedby"):
                failures.append("preferred contact method should not point to removed helper copy")
            if page.locator("#book_preferred_contact_method_helper").count() != 0:
                failures.append("preferred contact method helper copy should not exist")
            options = preferred.locator("option").evaluate_all("(nodes) => nodes.map((node) => node.value)")
            if options != ["", "Email", "Phone", "Text"]:
                failures.append(f"preferred contact options should be Email/Phone/Text, found {options!r}")

        spam_token = page.locator("#book_spam_token")
        if spam_token.count() != 1:
            failures.append("inquiry form should render one signed spam token")
        elif spam_token.get_attribute("name") != "lt_form_token" or "." not in (spam_token.input_value() or ""):
            failures.append("inquiry spam token should be signed and posted as lt_form_token")
        honeypot = page.locator("#book_website")
        if honeypot.count() != 1:
            failures.append("inquiry form should render one invisible website honeypot")
        elif honeypot.get_attribute("name") != "website" or honeypot.get_attribute("tabindex") != "-1":
            failures.append("inquiry honeypot should be named website and removed from tab order")

        time_fields = [
            ("#book_time", "x_event_time", "#book_time_hour", "#book_time_minute", "#book_time_period"),
            ("#book_end_time", "x_event_end_time", "#book_end_time_hour", "#book_end_time_minute", "#book_end_time_period"),
        ]
        for hidden_selector, field_name, hour_selector, minute_selector, period_selector in time_fields:
            hidden = page.locator(hidden_selector)
            if hidden.count() != 1 or hidden.get_attribute("name") != field_name:
                failures.append(f"{field_name} hidden time target should preserve backend mapping")
                continue
            for selector in (hour_selector, minute_selector, period_selector):
                if page.locator(selector).count() != 1:
                    failures.append(f"{field_name} should expose structured 12-hour control {selector}")
            helper = page.locator(f"{hidden_selector}_helper")
            if helper.count() != 1:
                failures.append(f"{field_name} estimate helper copy should exist once")
            elif helper.inner_text().strip() != "Even Estimates Help":
                failures.append(f"{field_name} estimate helper copy should be 'Even Estimates Help'")

        optional_fields = [
            ("#book_occasion", "event type"),
        ]
        for selector, label in optional_fields:
            field = page.locator(selector)
            if field.count() != 1:
                failures.append(f"{label} field should exist once")
            elif field.get_attribute("required") is not None:
                failures.append(f"{label} field should not be required")

        required_fields = [
            ("#book_date", "event date"),
            ("#book_location", "event city/location"),
        ]
        for selector, label in required_fields:
            field = page.locator(selector)
            if field.count() != 1:
                failures.append(f"{label} field should exist once")
            elif field.get_attribute("required") is None:
                failures.append(f"{label} field should be required")
        failures.extend(check_service(
            page,
            "Balloon Decor",
            {"Balloon Decor"},
            {"Balloon Twisting", "Face Painting", "Delivery", "Events Inquiry", "Event Environment"},
        ))
        failures.extend(check_service(
            page,
            "Delivery",
            {"Delivery"},
            {"Balloon Decor", "Balloon Twisting", "Face Painting", "Pickup", "Events Inquiry", "Event Environment"},
        ))
        failures.extend(check_service(
            page,
            "Pickup",
            {"Pickup"},
            {"Balloon Decor", "Balloon Twisting", "Face Painting", "Delivery", "Events Inquiry", "Event Environment"},
        ))
        failures.extend(check_service(
            page,
            "Events Inquiry",
            {"Events Inquiry"},
            {"Balloon Decor", "Balloon Twisting", "Face Painting", "Delivery", "Pickup", "Event Environment"},
        ))
        events_panel = panel(page, "Events Inquiry")
        if events_panel.count() == 1 and events_panel.first.is_visible():
            heading = events_panel.locator(".lt-book__conditional-title").first.text_content() or ""
            normalized_heading = heading.strip().replace("\u2019", "'")
            if normalized_heading != "Multiple services or larger event":
                failures.append("Events Inquiry heading should be \"Multiple services or larger event\"")
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
            {"Balloon Decor", "Face Painting", "Delivery", "Pickup", "Events Inquiry"},
        ))
        failures.extend(check_service(
            page,
            "Face Painting",
            {"Face Painting", "Event Environment"},
            {"Balloon Decor", "Balloon Twisting", "Delivery", "Pickup", "Events Inquiry"},
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
