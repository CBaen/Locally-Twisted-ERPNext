"""Verify public inquiry form accepts repeat email submissions with 5 photos.

This is a launch contract for Locally Twisted: one customer may send multiple
separate event inquiries from the same email address, and the form advertises
up to five inspiration photos.

By default the localhost run deletes old and current verifier-owned fake
records. Use --keep-records only when intentionally debugging a failed run.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import time
import urllib.parse

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


def cleanup_records(
    base_url: str,
    *,
    email: str | None = None,
    include_existing: bool = False,
) -> dict | None:
    if not _is_local_base_url(base_url):
        return None
    return _bench_execute_json(
        "locally_twisted.verify.book_form_repeat_email_photos_cleanup.cleanup",
        {"email": email, "include_existing": include_existing},
    )


def fail_if_cleanup_incomplete(label: str, cleanup: dict | None) -> None:
    if cleanup is None:
        raise AssertionError(
            f"{label} cleanup unavailable. Use a localhost Frappe target or pass --keep-records explicitly."
        )
    if cleanup.get("failures"):
        raise AssertionError(f"{label} cleanup failed: {cleanup['failures']}")
    if not cleanup.get("ok"):
        raise AssertionError(f"{label} cleanup left verifier-owned records: {cleanup.get('remaining')}")


def _bench_execute_json(method: str, kwargs: dict) -> dict | None:
    container = os.environ.get("LT_FRAPPE_BACKEND_CONTAINER", "locally-twisted-erpnext-v15-backend-1")
    site = os.environ.get("LT_FRAPPE_SITE", "frontend")
    command = [
        "docker",
        "exec",
        container,
        "bench",
        "--site",
        site,
        "execute",
        method,
        "--kwargs",
        repr(kwargs),
    ]
    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        print(f"local bench unavailable for cleanup: {exc}")
        return None
    if result.returncode != 0:
        print(f"local bench cleanup command failed: {result.stderr.strip()[:500]}")
        return None
    try:
        return json.loads(result.stdout.strip() or "{}")
    except json.JSONDecodeError as exc:
        print(f"local bench cleanup returned non-JSON: {exc}: {result.stdout.strip()[:500]}")
        return None


def _is_local_base_url(base_url: str) -> bool:
    host = urllib.parse.urlparse(base_url).hostname
    return host in {"localhost", "127.0.0.1", "::1"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8081")
    parser.add_argument(
        "--keep-records",
        action="store_true",
        help="Leave generated Leads/files/emails in place for manual debugging.",
    )
    parser.add_argument(
        "--skip-existing-cleanup",
        action="store_true",
        help="Do not remove older verifier-owned repeat-email/photo records before running.",
    )
    args = parser.parse_args()

    existing_cleanup = None
    if not args.keep_records and not args.skip_existing_cleanup:
        existing_cleanup = cleanup_records(args.base_url, include_existing=True)
        fail_if_cleanup_incomplete("pre-run existing verifier-record", existing_cleanup)

    token = int(time.time())
    email = f"lt-repeat-email-photo-{token}@example.invalid"
    first = None
    second = None
    cleanup = None
    try:
        first = submit(args.base_url, email, f"repeat-email-photo contract first {token}")
        second = submit(args.base_url, email, f"repeat-email-photo contract second {token}")
        if first["lead"] == second["lead"]:
            raise AssertionError(f"Expected two separate Lead records, got {first['lead']}")
    finally:
        if not args.keep_records:
            cleanup = cleanup_records(args.base_url, email=email)

    if not args.keep_records:
        fail_if_cleanup_incomplete("current verifier-record", cleanup)

    print("BOOK FORM REPEAT EMAIL + 5 PHOTO CHECK PASSED")
    print(
        {
            "email": email,
            "leads": [first["lead"], second["lead"]] if first and second else [],
            "pre_run_cleanup_deleted": len((existing_cleanup or {}).get("deleted", [])),
            "current_cleanup_deleted": len((cleanup or {}).get("deleted", [])),
            "records_kept": bool(args.keep_records),
        }
    )


if __name__ == "__main__":
    main()
