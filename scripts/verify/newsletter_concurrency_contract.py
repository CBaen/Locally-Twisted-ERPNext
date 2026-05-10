#!/usr/bin/env python3
"""Verify simultaneous newsletter signups stay customer-safe.

Run:
  python scripts/verify/newsletter_concurrency_contract.py
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request


def post_signup(base_url: str, email: str, start: threading.Event) -> dict:
    start.wait(timeout=10)
    endpoint = f"{base_url.rstrip('/')}/api/method/locally_twisted.api.newsletter.signup"
    body = urllib.parse.urlencode({"email": email}).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Requested-With": "XMLHttpRequest",
            "X-Frappe-CSRF-Token": "token",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            raw = response.read().decode("utf-8")
            status = response.status
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8") if exc.fp else ""
        status = exc.code
    except urllib.error.URLError as exc:
        return {"status": None, "ok": False, "error": str(exc.reason), "raw": ""}

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = {}

    message = parsed.get("message") if isinstance(parsed, dict) else None
    return {
        "status": status,
        "ok": bool(isinstance(message, dict) and message.get("ok")),
        "message": message.get("message", "") if isinstance(message, dict) else "",
        "raw": raw[:500],
    }


def cleanup_signup(email: str) -> None:
    container = os.environ.get("LT_FRAPPE_BACKEND_CONTAINER", "locally-twisted-erpnext-v15-backend-1")
    site = os.environ.get("LT_FRAPPE_SITE", "frontend")
    kwargs = {
        "doctype": "LT Newsletter Signup",
        "filters": [["email", "=", email]],
        "fields": ["name", "email"],
        "limit_page_length": 20,
    }
    list_command = [
        "docker",
        "exec",
        container,
        "bench",
        "--site",
        site,
        "execute",
        "frappe.client.get_list",
        "--kwargs",
        json.dumps(kwargs),
    ]
    try:
        listed = subprocess.run(list_command, capture_output=True, text=True, timeout=30, check=False)
        if listed.returncode != 0 or not listed.stdout.strip():
            return
        records = json.loads(listed.stdout)
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
        return

    for record in records:
        name = record.get("name")
        if not name:
            continue
        delete_command = [
            "docker",
            "exec",
            container,
            "bench",
            "--site",
            site,
            "execute",
            "frappe.delete_doc",
            "--args",
            json.dumps(["LT Newsletter Signup", name]),
            "--kwargs",
            json.dumps({"force": True, "ignore_permissions": True}),
        ]
        subprocess.run(delete_command, capture_output=True, text=True, timeout=30, check=False)


def run(base_url: str, email: str, skip_cleanup: bool) -> int:
    print("[NEWSLETTER CONCURRENCY CONTRACT]")
    print(f"  endpoint: {base_url.rstrip('/')}/api/method/locally_twisted.api.newsletter.signup")
    print(f"  email: {email}")

    start = threading.Event()
    results: list[dict] = []
    threads = [
        threading.Thread(
            target=lambda: results.append(post_signup(base_url, email, start)),
            daemon=True,
        )
        for _ in range(2)
    ]
    for thread in threads:
        thread.start()
    start.set()
    for thread in threads:
        thread.join(timeout=30)

    if not skip_cleanup:
        cleanup_signup(email)

    print(json.dumps(results, indent=2))
    failures = [
        result
        for result in results
        if result.get("status") != 200 or not result.get("ok")
    ]
    if len(results) != 2 or failures:
        print("[NEWSLETTER CONCURRENCY CONTRACT] FAIL")
        print("  simultaneous duplicate signup must not leak a raw Frappe error to the customer")
        return 1

    print("[NEWSLETTER CONCURRENCY CONTRACT] PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--base-url", default="http://localhost:8081")
    parser.add_argument("--email", default="")
    parser.add_argument("--skip-cleanup", action="store_true")
    args = parser.parse_args()

    email = args.email.strip().lower() or f"concurrent-newsletter-{time.time_ns()}@bbc-test.invalid"
    return run(args.base_url, email, args.skip_cleanup)


if __name__ == "__main__":
    sys.exit(main())
