"""Verify sales pitches are filtered without blocking real event inquiries."""

from __future__ import annotations

import argparse
import re
import time
from html import unescape

from smoke_forms import cleanup_record_in_backend_frappe


ENDPOINT = "/api/method/locally_twisted.www.book.submit_book_inquiry"
TOKEN_RE = re.compile(
    r'<input[^>]+name=["\']lt_form_token["\'][^>]+value=["\']([^"\']+)["\']',
    re.IGNORECASE,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:8081")
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")

    failures: list[str] = []
    sales_marker = f"SALES-FILTER-TEST-{time.time_ns()}"
    customer_marker = f"EVENT-CUSTOMER-TEST-{time.time_ns()}"

    try:
        sales_payload = submit(
            base_url,
            marker=sales_marker,
            email="sales-filter-test@example.invalid",
            description=(
                "Good Morning, I tried emailing you, but it seems it didn't go through. "
                "We offer Virtual Assistants using our custom built AI tool to handle "
                "marketing, administrative tasks, graphic design, accounting, and prospecting. "
                "Are you looking for help?"
            ),
            location="Sales Vendor",
            service="Events Inquiry",
            company="Sales Vendor",
        )
        if sales_payload.get("business_notification", {}).get("queued") is True:
            failures.append("sales solicitation should not queue the owner inquiry email")
        if sales_payload.get("business_notification", {}).get("suppressed") is not True:
            failures.append(f"sales solicitation should be explicitly suppressed: {sales_payload!r}")
        if not sales_payload.get("lead"):
            failures.append("sales solicitation should still save a Lead for review/audit")
        if sales_payload.get("customer_confirmation", {}).get("queued") is not True:
            failures.append("sales solicitation should still follow the normal customer-safe response path")

        customer_payload = submit(
            base_url,
            marker=customer_marker,
            email="event-customer-test@example.invalid",
            description=(
                "We are planning a corporate marketing event and need balloon decor "
                "for an entrance, branded photo backdrop, and maybe face painting for families."
            ),
            location="Ogden, UT",
            service="Balloon Decor",
            company="Customer Event Co",
        )
        if customer_payload.get("business_notification", {}).get("queued") is not True:
            failures.append(f"real event inquiry should still queue owner email: {customer_payload!r}")
        if customer_payload.get("business_notification", {}).get("suppressed"):
            failures.append("real event inquiry should not be marked as suppressed")
    finally:
        for marker in (sales_marker, customer_marker):
            cleanup = cleanup_record_in_backend_frappe(marker, base_url)
            if cleanup is not True:
                failures.append(f"cleanup did not confirm success for {marker}: {cleanup!r}")

    if failures:
        print("[INQUIRY SALES SOLICITATION FILTER] FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("[INQUIRY SALES SOLICITATION FILTER] PASS")
    return 0


def submit(
    base_url: str,
    *,
    marker: str,
    email: str,
    description: str,
    location: str,
    service: str,
    company: str,
) -> dict:
    import requests

    token = fetch_form_token(base_url)
    time.sleep(2.1)
    response = requests.post(
        f"{base_url}{ENDPOINT}",
        data={
            "contact_name": marker,
            "email_from": email,
            "phone": "801-555-0197",
            "preferred_contact_method": "Email",
            "partner_name": company,
            "x_event_date": "2026-06-20",
            "x_event_location": location,
            "x_services": service,
            "description": description,
            "lt_form_token": token,
        },
        headers={"X-Requested-With": "XMLHttpRequest"},
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()["message"]
    if payload.get("ok") is not True:
        raise AssertionError(f"inquiry submit returned not-ok: {payload!r}")
    return payload


def fetch_form_token(base_url: str) -> str:
    import requests

    response = requests.get(f"{base_url}/contact", timeout=30)
    response.raise_for_status()
    match = TOKEN_RE.search(response.text)
    if not match:
        raise AssertionError("public inquiry form did not render lt_form_token")
    return unescape(match.group(1)).strip()


if __name__ == "__main__":
    raise SystemExit(main())
