#!/usr/bin/env python3
"""Fast contract for Cloudflare launch-readiness cache-status handling.

This does not call the network. It proves dynamic routes fail loudly when
Cloudflare reports cache eligibility, including first-request MISS responses.

Run:
  python scripts/verify/cloudflare_launch_readiness_contract.py
"""
from __future__ import annotations

import argparse
import sys

from cloudflare_launch_readiness import HttpResult, cloudflare_failure


FORBIDDEN_DYNAMIC_CACHE_STATUSES = (
    "MISS",
    "HIT",
    "STALE",
    "UPDATING",
    "EXPIRED",
    "REVALIDATED",
)
ALLOWED_DYNAMIC_CACHE_STATUSES = (
    None,
    "",
    "BYPASS",
    "DYNAMIC",
    "dynamic",
)


def _result(cache_status: str | None) -> HttpResult:
    headers = {}
    if cache_status is not None:
        headers["cf-cache-status"] = cache_status
    return HttpResult(
        status=200,
        final_url="https://example.test/login",
        headers=headers,
        body_sample="Login",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.parse_args()

    failures = []
    for status in FORBIDDEN_DYNAMIC_CACHE_STATUSES:
        check = cloudflare_failure("login", _result(status))
        if not check or check.status != "block":
            failures.append(f"cf-cache-status {status} should block dynamic routes")

    for status in ALLOWED_DYNAMIC_CACHE_STATUSES:
        check = cloudflare_failure("login", _result(status))
        if check:
            failures.append(f"cf-cache-status {status!r} should pass dynamic routes, got {check.summary}")

    if failures:
        print("[CLOUDFLARE LAUNCH READINESS CONTRACT] FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("[CLOUDFLARE LAUNCH READINESS CONTRACT] PASS")
    print("  forbidden dynamic cache statuses: " + ", ".join(FORBIDDEN_DYNAMIC_CACHE_STATUSES))
    print("  allowed dynamic cache statuses: absent, empty, BYPASS, DYNAMIC")
    return 0


if __name__ == "__main__":
    sys.exit(main())
