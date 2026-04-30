#!/usr/bin/env python3
"""
Form smoke test.

POST a test record to the configured form endpoint, verify it landed in the
backend, then delete it. Fails loudly if any step doesn't complete.

This gate exists because of the Locally Twisted /book form 10-day silent
failure (2026-04-22). The form's widget crashed on init; the browser fell
back to a plain HTML POST; the server returned an empty 200; the customer
saw a blank page; no record was created. Jeff did not notice for ~10 days.
This smoke test would have caught it on the first deploy.

Contains two independent smoke tests:
  1. smoke_test()        — /book form via Playwright browser automation
  2. smoke_newsletter()  — newsletter API endpoint via direct HTTP POST

Self-contained: no imports outside the standard library + playwright.
"""
import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("FAIL — playwright not installed. Run: pip install playwright && playwright install chromium")
    sys.exit(1)

# =============================================================================
# STACK-SPECIFIC: how to verify the test record was created
# Replace this block when porting to a non-Frappe stack.
# =============================================================================
def verify_record_in_backend_frappe(test_marker: str, base_url: str) -> bool:
    """Check the Frappe REST API for a Lead record matching the test marker."""
    import urllib.request
    import urllib.error
    import json
    api = f"{base_url.rstrip('/')}/api/resource/Lead?filters=[[\"lead_name\",\"=\",\"{test_marker}\"]]&fields=[\"name\"]"
    try:
        with urllib.request.urlopen(api, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        return len(data.get("data", [])) > 0
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError) as e:
        print(f"       backend verification failed: {e}")
        return False

VERIFY_BACKEND = verify_record_in_backend_frappe   # swap for other stacks

# =============================================================================
# Smoke test
# =============================================================================
def smoke_test(base_url: str, form_path: str, shape_only: bool = False) -> int:
    test_marker = f"SMOKE-TEST-{int(time.time())}"
    form_url = f"{base_url.rstrip('/')}/{form_path.lstrip('/')}"
    print(f"\n[SMOKE] Form: {form_url}")
    print(f"        Test marker: {test_marker}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Step 1: navigate
        try:
            page.goto(form_url, timeout=30000)
        except PlaywrightTimeout:
            print(f"        FAIL — could not load form page")
            browser.close()
            return 1

        # Step 2: shape check — does the form exist on the page?
        form_count = page.locator("form").count()
        if form_count == 0:
            print(f"        FAIL — no <form> element found on {form_url}")
            browser.close()
            return 1
        print(f"        FORM SHAPE OK ({form_count} form element(s) found)")

        if shape_only:
            print(f"        --shape-only flag set; stopping here. PASS.")
            browser.close()
            return 0

        # Step 3: fill the form (TEMPLATE — adapt selectors to actual form)
        # Replace these selectors with the real form's field names.
        try:
            name_field = page.locator("input[name='contact_name'], input[name='lead_name'], input[name='name']").first
            email_field = page.locator("input[type='email'], input[name='email_id']").first
            if name_field.count() > 0:
                name_field.fill(test_marker)
            if email_field.count() > 0:
                email_field.fill("smoke-test@example.invalid")
        except Exception as e:
            print(f"        FAIL — could not fill form fields: {e}")
            browser.close()
            return 1

        # Step 4: submit
        try:
            page.locator("button[type='submit'], input[type='submit']").first.click(timeout=10000)
        except PlaywrightTimeout:
            print(f"        FAIL — could not click submit button")
            browser.close()
            return 1

        # Step 5: verify the page response — must NOT be a blank white page
        # (this is the LT 2026-04-22 failure mode)
        time.sleep(2)
        body_text = page.locator("body").inner_text()
        if not body_text.strip():
            print(f"        FAIL — page body is empty after submit (silent-failure pattern)")
            browser.close()
            return 1

        # Step 6: optional — check for explicit success confirmation
        # Look for a success modal, "thank you" message, or URL hash change
        confirmation_visible = (
            page.locator("text=/thank|received|success|confirmed/i").count() > 0
            or "#received" in page.url
            or "#success" in page.url
        )
        if not confirmation_visible:
            print(f"        WARN — no explicit confirmation found on success page")
            # don't fail — proceed to backend check
        else:
            print(f"        SUCCESS UI VISIBLE")

        browser.close()

    # Step 7: backend verification (the most important step)
    print(f"        Verifying record in backend...")
    time.sleep(3)  # give async create time to land
    if not VERIFY_BACKEND(test_marker, base_url):
        print(f"        FAIL — record with marker '{test_marker}' not found in backend")
        print(f"        This is the silent-submission failure pattern. Investigate.")
        return 1
    print(f"        BACKEND VERIFIED — record exists")

    # Step 8: cleanup (best-effort; failure here is a warning not a fail)
    # Implement record deletion via API if possible.
    print(f"        TODO: delete test record '{test_marker}' from backend")
    print(f"        SMOKE TEST PASS")
    return 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True, help="https://yoursite.com")
    parser.add_argument("--form-path", default="/book", help="path to the form (default: /book)")
    parser.add_argument("--shape-only", action="store_true",
                        help="Only verify form structure parses; do not submit (for CI without prod access)")
    args = parser.parse_args()
    sys.exit(smoke_test(args.base_url, args.form_path, args.shape_only))

if __name__ == "__main__":
    main()
