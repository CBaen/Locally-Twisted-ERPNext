#!/usr/bin/env python3
"""Verify guests cannot reach the Event Playground internal preview bridge."""
from __future__ import annotations

from http.client import HTTPConnection
from urllib.parse import urlparse

from _cli import parse_noop_args


BASE_URL = "http://localhost:8081"
ROUTE = "/event-playground?port=12345"
PREVIEW_MARKER = "127.0.0.1:12345/event-playground.html"


def _request(path: str):
    parsed = urlparse(BASE_URL)
    conn = HTTPConnection(parsed.hostname, parsed.port or 80, timeout=10)
    conn.request("GET", path)
    response = conn.getresponse()
    body = response.read().decode("utf-8", errors="replace")
    headers = {key.lower(): value for key, value in response.getheaders()}
    conn.close()
    return response.status, headers, body


def main() -> int:
    parse_noop_args(__doc__)
    status, headers, body = _request(ROUTE)
    failures = []

    if status == 200 and PREVIEW_MARKER in body:
        failures.append("guest response exposed the local preview iframe URL")
    if status not in {301, 302, 403}:
        failures.append(f"guest response should redirect to login or deny access, found HTTP {status}")
    if status in {301, 302} and "/login" not in headers.get("location", ""):
        failures.append(f"guest redirect should point at /login, found {headers.get('location')!r}")

    if failures:
        print("[EVENT PLAYGROUND GATE] FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("[EVENT PLAYGROUND GATE] PASS")
    print(f"  status: {status}")
    print(f"  location: {headers.get('location', '')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
