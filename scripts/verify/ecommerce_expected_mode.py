#!/usr/bin/env python3
"""Fail if the local ecommerce exposure mode is not the expected one.

Examples:
  python scripts/verify/ecommerce_expected_mode.py --expect open
  python scripts/verify/ecommerce_expected_mode.py --expect paused
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


BASE_URL = os.environ.get("LT_BASE_URL", "http://localhost:8081").rstrip("/")
CONTAINER = os.environ.get("LT_FRAPPE_BACKEND_CONTAINER", "locally-twisted-erpnext-v15-backend-1")
SITE = os.environ.get("LT_FRAPPE_SITE", "frontend")
PAUSE_PATH = "/ready-to-order-paused"
OPEN_ROUTES = ("/shop", "/cart", "/checkout")


class ModeFail(Exception):
    pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expect", choices=("open", "paused"), required=True)
    args = parser.parse_args()

    try:
        paused = is_configured_paused()
        assert_expected_config(args.expect, paused)
        assert_routes_match_expectation(args.expect)
    except ModeFail as exc:
        print(f"[ECOMMERCE EXPECTED MODE] FAIL: {exc}", file=sys.stderr)
        return 1

    print(f"[ECOMMERCE EXPECTED MODE] PASS expect={args.expect} paused={paused}")
    return 0


def is_configured_paused() -> bool:
    proc = subprocess.run(
        [
            "docker",
            "exec",
            CONTAINER,
            "bench",
            "--site",
            SITE,
            "execute",
            "locally_twisted.ecommerce_pause.is_ecommerce_paused",
        ],
        text=True,
        capture_output=True,
        timeout=60,
    )
    if proc.returncode != 0:
        raise ModeFail(
            "bench execute failed while reading lt_ecommerce_paused\n"
            f"STDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )

    text = proc.stdout.strip()
    if not text:
        return False
    try:
        return bool(json.loads(text))
    except json.JSONDecodeError:
        return text.lower() not in {"0", "false", "no", "off", "open"}


def assert_expected_config(expect: str, paused: bool) -> None:
    if expect == "open" and paused:
        raise ModeFail("expected local ecommerce open, but lt_ecommerce_paused is active")
    if expect == "paused" and not paused:
        raise ModeFail("expected ecommerce paused, but lt_ecommerce_paused is open")


def assert_routes_match_expectation(expect: str) -> None:
    for route in OPEN_ROUTES:
        status, final_url, body = get_final(route)
        if status >= 400:
            raise ModeFail(f"{route} returned HTTP {status}")

        final_path = urlparse(final_url).path.rstrip("/") or "/"
        if expect == "open":
            if final_path == PAUSE_PATH:
                raise ModeFail(f"{route} should be open, but landed on {final_url}")
            if "lt-ecommerce-paused" in body:
                raise ModeFail(f"{route} should be open, but rendered the pause shell")
        else:
            if final_path != PAUSE_PATH:
                raise ModeFail(f"{route} should be paused, but landed on {final_url}")
            if "Ready-to-order is paused" not in body:
                raise ModeFail(f"{route} paused route did not render the branded pause message")


def get_final(route: str) -> tuple[int, str, str]:
    url = urljoin(BASE_URL + "/", route.lstrip("/"))
    request = Request(url, headers={"User-Agent": "LT expected ecommerce mode verifier"})
    with urlopen(request, timeout=20) as response:
        return response.status, response.geturl(), response.read().decode("utf-8", errors="replace")


if __name__ == "__main__":
    sys.exit(main())
