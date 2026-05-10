"""Verify public inquiry form accepts repeat email submissions with 5 photos.

This is a launch contract for Locally Twisted: one customer may send multiple
separate event inquiries from the same email address, and the form advertises
up to five inspiration photos.
"""

from __future__ import annotations

import argparse
import base64
import time

import requests

PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
)


def submit(base_url: str, email: str, label: str) -> dict:
    files = [
        ("ufile", (f"inspiration-{idx}.png", PNG_1X1, "image/png"))
        for idx in range(1, 6)
    ]
    data = {
        "contact_name": "Repeat Email Photo Test",
        "email_from": email,
        "phone": "(801) 555-0100",
        "partner_name": "Test",
        "x_event_time": "4:00 PM",
        "x_event_end_time": "5:00 PM",
        "x_event_location": "Test City",
        "x_guest_count": "33",
        "x_services": "Balloon Twisting,Face Painting",
        "description": label,
    }
    response = requests.post(
        f"{base_url.rstrip('/')}/api/method/locally_twisted.www.book.submit_book_inquiry",
        data=data,
        files=files,
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()["message"]
    assert payload["ok"] is True, payload
    assert payload["photo_uploads"]["submitted"] == 5, payload
    assert payload["photo_uploads"]["attached"] == 5, payload
    assert not payload["photo_uploads"].get("rejected"), payload
    assert not payload["photo_uploads"].get("failed"), payload
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8081")
    args = parser.parse_args()

    token = int(time.time())
    email = f"lt-repeat-email-photo-{token}@example.invalid"
    first = submit(args.base_url, email, f"repeat-email-photo contract first {token}")
    second = submit(args.base_url, email, f"repeat-email-photo contract second {token}")
    if first["lead"] == second["lead"]:
        raise AssertionError(f"Expected two separate Lead records, got {first['lead']}")
    print("BOOK FORM REPEAT EMAIL + 5 PHOTO CHECK PASSED")
    print({"email": email, "leads": [first["lead"], second["lead"]]})


if __name__ == "__main__":
    main()
