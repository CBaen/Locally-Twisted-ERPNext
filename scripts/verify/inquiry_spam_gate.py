"""Verify the public inquiry form rejects bot-style submissions.

The contract is intentionally low-friction for real customers:

- the rendered form includes a signed spam token and an invisible honeypot;
- direct endpoint posts without the token are rejected before Lead creation;
- filled honeypot posts are rejected before Lead creation.
"""

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

    marker = f"SPAM-GATE-TEST-{time.time_ns()}"
    token = fetch_form_token(base_url, failures)

    missing_token_response = submit(base_url, marker, {})
    if missing_token_response.status_code < 400:
        failures.append(
            f"missing-token post should be rejected, got {missing_token_response.status_code}"
        )

    if token:
        too_fast_response = submit(base_url, marker, {"lt_form_token": token})
        if too_fast_response.status_code < 400:
            failures.append(
                f"too-fast token post should be rejected, got {too_fast_response.status_code}"
            )

        honeypot_response = submit(
            base_url,
            marker,
            {"lt_form_token": token, "website": "https://spam.example"},
        )
        if honeypot_response.status_code < 400:
            failures.append(
                f"filled honeypot post should be rejected, got {honeypot_response.status_code}"
            )

    cleanup = cleanup_record_in_backend_frappe(marker, base_url)
    if cleanup is not True:
        failures.append(f"spam-gate cleanup did not confirm success: {cleanup!r}")

    if failures:
        print("[INQUIRY SPAM GATE] FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("[INQUIRY SPAM GATE] PASS")
    return 0


def fetch_form_token(base_url: str, failures: list[str]) -> str:
    import requests

    response = requests.get(f"{base_url}/contact", timeout=30)
    response.raise_for_status()
    body = response.text
    match = TOKEN_RE.search(body)
    if not match:
        failures.append("public form missing signed lt_form_token field")
        return ""
    token = unescape(match.group(1)).strip()
    if "." not in token:
        failures.append("public form spam token is not signed")
    if 'name="website"' not in body and "name='website'" not in body:
        failures.append("public form missing invisible honeypot field")
    return token


def submit(base_url: str, marker: str, extra: dict[str, str]):
    import requests

    data = {
        "contact_name": marker,
        "email_from": "spam-gate-test@example.invalid",
        "phone": "801-555-0188",
        "preferred_contact_method": "Email",
        "x_event_date": "2026-06-20",
        "x_event_location": "Ogden, UT",
        "x_services": "Balloon Decor",
        "description": "Verifier-owned spam-gate probe.",
    }
    data.update(extra)
    return requests.post(
        f"{base_url}{ENDPOINT}",
        data=data,
        headers={"X-Requested-With": "XMLHttpRequest"},
        timeout=30,
    )


if __name__ == "__main__":
    raise SystemExit(main())
