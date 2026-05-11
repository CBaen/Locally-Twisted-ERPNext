#!/usr/bin/env python3
"""Verify Cloudflare is launch-safe for Frappe dynamic routes.

This is a public HTTP probe for the staged or production domain after
Cloudflare is in front of Frappe Cloud. It does not use Cloudflare API keys and
does not read secrets.

Run:
  python scripts/verify/cloudflare_launch_readiness.py --base-url https://example.com
  python scripts/verify/cloudflare_launch_readiness.py --base-url http://localhost:8081 --allow-http
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


WEBHOOK_PATH = "/api/method/locally_twisted.payments.stripe_webhook.stripe_webhook"
DYNAMIC_GET_PATHS = (
    ("login", "/login"),
    ("account_home", "/me"),
    ("contact", "/contact"),
    ("cart", "/cart"),
    ("checkout", "/checkout"),
    ("payment_success", "/payment-success?payment_request=LT-CF-PROBE"),
    ("thank_you", "/thank-you?order=LT-CF-PROBE"),
    ("api_ping", "/api/method/frappe.ping"),
)
ALLOWED_DYNAMIC_CACHE_STATUSES = {"BYPASS", "DYNAMIC"}
CHALLENGE_BODY_MARKERS = (
    "cf-chl",
    "checking your browser",
    "just a moment",
    "attention required",
    "cloudflare ray id",
)


@dataclass
class Check:
    id: str
    status: str
    summary: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class HttpResult:
    status: int
    final_url: str
    headers: dict[str, str]
    body_sample: str


def fetch(base_url: str, path: str, *, method: str = "GET", data: bytes | None = None) -> HttpResult:
    headers = {
        "Accept": "application/json, text/html;q=0.9, */*;q=0.8",
        "User-Agent": "LT Cloudflare launch readiness verifier",
    }
    if method == "POST":
        headers.update(
            {
                "Content-Type": "application/json",
                "Stripe-Signature": "t=1,v1=probe",
            }
        )

    request = Request(
        urljoin(base_url.rstrip("/") + "/", path.lstrip("/")),
        data=data,
        method=method,
        headers=headers,
    )
    try:
        with urlopen(request, timeout=20) as response:
            body = response.read(4096).decode("utf-8", errors="replace")
            return HttpResult(
                status=int(response.status),
                final_url=response.geturl(),
                headers={key.lower(): value for key, value in response.headers.items()},
                body_sample=body,
            )
    except HTTPError as error:
        body = error.read(4096).decode("utf-8", errors="replace") if error.fp else ""
        return HttpResult(
            status=int(error.code),
            final_url=error.geturl(),
            headers={key.lower(): value for key, value in error.headers.items()},
            body_sample=body,
        )
    except URLError as exc:
        raise RuntimeError(f"{path} could not be reached: {exc.reason}") from exc


def check_base_url(base_url: str, *, allow_http: bool) -> Check:
    parsed = urlparse(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return Check("base_url", "block", "Base URL must include scheme and host.", {"base_url": base_url})
    if parsed.scheme != "https" and not allow_http:
        return Check(
            "base_url",
            "block",
            "Cloudflare launch checks require HTTPS; use --allow-http only for local smoke testing.",
            {"base_url": base_url},
        )
    return Check("base_url", "pass", "Base URL shape is valid.", {"base_url": base_url})


def dynamic_route_check(route_id: str, path: str, result: HttpResult) -> Check:
    shared_failure = cloudflare_failure(route_id, result)
    if shared_failure:
        return shared_failure
    if result.status == 404:
        return Check(
            route_id,
            "block",
            f"{path} returned HTTP 404; the required dynamic route is not reaching the Frappe app.",
            route_details(result),
        )
    if result.status >= 500:
        return Check(
            route_id,
            "block",
            f"{path} returned HTTP {result.status}; dynamic route must reach Frappe cleanly.",
            route_details(result),
        )
    return Check(
        route_id,
        "pass",
        f"{path} reached origin without Cloudflare challenge or dynamic-cache hit.",
        route_details(result),
    )


def webhook_check(result: HttpResult) -> Check:
    shared_failure = cloudflare_failure("stripe_webhook", result)
    if shared_failure:
        return shared_failure
    if result.status not in {400, 503}:
        return Check(
            "stripe_webhook",
            "block",
            "Unsigned Stripe webhook probe should reach Frappe and fail as invalid signature or missing secret.",
            route_details(result),
        )
    return Check(
        "stripe_webhook",
        "pass",
        "Stripe webhook path reached Frappe without Cloudflare challenge or cache.",
        route_details(result),
    )


def cloudflare_failure(route_id: str, result: HttpResult) -> Check | None:
    cf_mitigated = result.headers.get("cf-mitigated", "").lower()
    body_lower = result.body_sample.lower()
    if cf_mitigated == "challenge" or any(marker in body_lower for marker in CHALLENGE_BODY_MARKERS):
        return Check(
            route_id,
            "block",
            "Cloudflare challenge/WAF interstitial is visible on a dynamic route.",
            route_details(result),
        )

    cache_status = result.headers.get("cf-cache-status", "").upper().strip()
    if cache_status and cache_status not in ALLOWED_DYNAMIC_CACHE_STATUSES:
        return Check(
            route_id,
            "block",
            f"Cloudflare considered a dynamic route cacheable or served it from cache: {cache_status}.",
            route_details(result),
        )
    return None


def route_details(result: HttpResult) -> dict[str, Any]:
    return {
        "status": result.status,
        "final_url": result.final_url,
        "cf_cache_status": result.headers.get("cf-cache-status"),
        "cf_mitigated": result.headers.get("cf-mitigated"),
        "server": result.headers.get("server"),
    }


def collect_checks(base_url: str, *, allow_http: bool) -> list[Check]:
    checks = [check_base_url(base_url, allow_http=allow_http)]
    if checks[0].status == "block":
        return checks

    for route_id, path in DYNAMIC_GET_PATHS:
        try:
            checks.append(dynamic_route_check(route_id, path, fetch(base_url, path)))
        except RuntimeError as exc:
            checks.append(Check(route_id, "block", str(exc), {"path": path}))

    try:
        checks.append(webhook_check(fetch(base_url, WEBHOOK_PATH, method="POST", data=b"{}")))
    except RuntimeError as exc:
        checks.append(Check("stripe_webhook", "block", str(exc), {"path": WEBHOOK_PATH}))

    return checks


def render_text(checks: list[Check]) -> None:
    print("Cloudflare launch readiness")
    print("===========================")
    for check in checks:
        marker = {"pass": "PASS", "warn": "WARN", "block": "BLOCK"}.get(check.status, check.status.upper())
        print(f"[{marker}] {check.id}: {check.summary}")
        for key, value in check.details.items():
            print(f"        {key}: {value}")

    blockers = [check for check in checks if check.status == "block"]
    warnings = [check for check in checks if check.status == "warn"]
    print()
    print(f"Summary: {len(blockers)} blocker(s), {len(warnings)} warning(s), {len(checks)} checks.")
    if blockers:
        print("Cloudflare cutover gate is blocked.")
    else:
        print("Cloudflare dynamic-route gate passed for the checked URL.")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--base-url", required=True, help="HTTPS staging or production base URL to verify.")
    parser.add_argument("--allow-http", action="store_true", help="Allow http:// base URLs for local smoke testing only.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    checks = collect_checks(args.base_url, allow_http=args.allow_http)
    if args.json:
        print(json.dumps([asdict(check) for check in checks], indent=2, sort_keys=True))
    else:
        render_text(checks)
    return 1 if any(check.status == "block" for check in checks) else 0


if __name__ == "__main__":
    sys.exit(main())
