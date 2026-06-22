#!/usr/bin/env python3
"""Verify the public root renders the Locally Twisted homepage, not login."""
from __future__ import annotations

import argparse
import os
import re
import sys
from html import unescape
from typing import Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "http://localhost:8081"
EXPECTED_TITLE = "Locally Twisted - Utah Balloon Event Decor & Installations"
REQUIRED_MARKERS = (
    "FREE EVENT QUOTE",
    "FOURTH OF JULY EVENTS",
    "Balloon moments for public events",
)
FORBIDDEN_MARKERS = (
    "PRIVATE CUSTOMER ACCOUNT",
    "Welcome back",
    "Invite-only access",
)


def fetch_home(base_url: str) -> tuple[int, str, str, str]:
    url = urljoin(base_url.rstrip("/") + "/", "/")
    request = Request(url, headers={"User-Agent": "LT public home identity verifier"})
    with urlopen(request, timeout=30) as response:
        body = response.read().decode("utf-8", errors="replace")
        return response.status, response.geturl(), response.headers.get("content-type", ""), body


def page_title(body: str) -> str:
    match = re.search(r"<title[^>]*>(.*?)</title>", body, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    return unescape(re.sub(r"\s+", " ", match.group(1))).strip()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-url",
        default=os.environ.get("LT_BASE_URL", DEFAULT_BASE_URL),
        help="Base URL to verify. Defaults to LT_BASE_URL or localhost.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    failures: list[str] = []
    try:
        status, final_url, content_type, body = fetch_home(args.base_url)
    except HTTPError as error:
        failures.append(f"/ returned HTTP {error.code}")
        status = error.code
        final_url = error.geturl()
        content_type = error.headers.get("content-type", "")
        body = error.read().decode("utf-8", errors="replace")
    except (OSError, URLError) as error:
        print(f"[PUBLIC HOME IDENTITY] FAIL: could not fetch /: {error}", file=sys.stderr)
        return 1

    title = page_title(body)
    body_key = unescape(re.sub(r"\s+", " ", body)).casefold()
    if status >= 400:
        failures.append(f"/ expected HTTP < 400, found {status}")
    if "text/html" not in content_type.casefold():
        failures.append(f"/ expected HTML content, found {content_type!r}")
    if "#login" in final_url or final_url.rstrip("/").endswith("/login"):
        failures.append(f"/ resolved to login surface: {final_url}")
    if title != EXPECTED_TITLE:
        failures.append(f"/ expected title {EXPECTED_TITLE!r}, found {title!r}")
    for marker in REQUIRED_MARKERS:
        if marker.casefold() not in body_key:
            failures.append(f"/ missing homepage marker {marker!r}")
    for marker in FORBIDDEN_MARKERS:
        if marker.casefold() in body_key:
            failures.append(f"/ rendered login/account marker {marker!r}")

    if failures:
        print("[PUBLIC HOME IDENTITY] FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("[PUBLIC HOME IDENTITY] PASS")
    print(f"status={status}")
    print(f"final_url={final_url}")
    print(f"title={title}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
