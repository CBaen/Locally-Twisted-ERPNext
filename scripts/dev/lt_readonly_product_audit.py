#!/usr/bin/env python3
"""Collect read-only public evidence for an LT product route.

Default use:
  python scripts/dev/lt_readonly_product_audit.py --output /tmp/lt-product-audit.json

Optional public API GET reads:
  LT_READONLY_PRODUCT_AUDIT_ENABLE_API_GETS=1 \
  LT_READONLY_PRODUCT_AUDIT_API_BASE_URL=http://localhost:8081 \
  python scripts/dev/lt_readonly_product_audit.py --output /tmp/lt-product-audit.json

This helper never writes ERPNext data, never clears cache, and never performs
non-GET requests. It has no credential or token arguments.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_BASE_URL = "https://locallytwisted.com"
DEFAULT_ROUTE = "/shop-items/bouquets/large-head-missionary"
DEFAULT_ITEM_CODE = "large-head-missionary"
ENABLE_API_ENV = "LT_READONLY_PRODUCT_AUDIT_ENABLE_API_GETS"
API_BASE_ENV = "LT_READONLY_PRODUCT_AUDIT_API_BASE_URL"
USER_AGENT = "lt-readonly-product-audit/1.0"
MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


class AuditBlocked(RuntimeError):
    """Raised when a requested behavior is outside the read-only contract."""


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        enforce_readonly_contract(args)
        report = build_report(args)
        write_report(args.output, report)
    except AuditBlocked as exc:
        print(f"[LT READ-ONLY PRODUCT AUDIT] BLOCKED: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"[LT READ-ONLY PRODUCT AUDIT] FAIL: {exc}", file=sys.stderr)
        return 1

    status = "PASS" if not report["failures"] else "FAIL"
    print(f"[LT READ-ONLY PRODUCT AUDIT] {status}")
    if report.get("status") == "dry_run":
        print("  output: not written in dry-run mode")
    else:
        print(f"  output: {Path(args.output).resolve()}")
    print("  method: GET only")
    print("  mutation: none")
    for failure in report["failures"]:
        print(f"  failure: {failure}")
    return 0 if not report["failures"] else 1


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help=f"Public site base URL. Default: {DEFAULT_BASE_URL}")
    parser.add_argument("--route", default=DEFAULT_ROUTE, help=f"Product route. Default: {DEFAULT_ROUTE}")
    parser.add_argument("--item-code", default=DEFAULT_ITEM_CODE, help=f"Template item code. Default: {DEFAULT_ITEM_CODE}")
    parser.add_argument("--output", required=True, help="Caller-provided local JSON output path.")
    parser.add_argument("--timeout", type=float, default=20.0, help="HTTP timeout in seconds.")
    parser.add_argument("--http-method", default="GET", help="Must be GET. Any other method is blocked.")
    parser.add_argument("--clear-cache", action="store_true", help="Unsupported; included so accidental use fails loudly.")
    parser.add_argument("--write-erpnext", action="store_true", help="Unsupported; included so accidental use fails loudly.")
    parser.add_argument("--allow-mutating-api", action="store_true", help="Unsupported; included so accidental use fails loudly.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned GETs without fetching or writing output.")
    return parser.parse_args(argv)


def enforce_readonly_contract(args: argparse.Namespace) -> None:
    method = str(args.http_method or "").strip().upper()
    if method != "GET":
        if method in MUTATING_METHODS:
            raise AuditBlocked(f"{method} is outside this helper's read-only contract")
        raise AuditBlocked(f"unsupported HTTP method {method!r}; only GET is allowed")
    if args.clear_cache:
        raise AuditBlocked("cache clearing is outside this helper's contract")
    if args.write_erpnext:
        raise AuditBlocked("ERPNext writes are outside this helper's contract")
    if args.allow_mutating_api:
        raise AuditBlocked("mutating API access is outside this helper's contract")
    validate_http_base(args.base_url, "--base-url")
    validate_local_output(args.output)
    api_enabled = env_truthy(os.environ.get(ENABLE_API_ENV, ""))
    api_base = os.environ.get(API_BASE_ENV, "").strip()
    if api_enabled and not api_base:
        raise AuditBlocked(f"{ENABLE_API_ENV}=1 requires non-secret {API_BASE_ENV}")
    if api_base:
        validate_http_base(api_base, API_BASE_ENV)


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    product_url = join_url(args.base_url, args.route)
    api_enabled = env_truthy(os.environ.get(ENABLE_API_ENV, ""))
    api_base = os.environ.get(API_BASE_ENV, "").strip()
    api_urls = public_api_urls(api_base, args.item_code) if api_enabled else {}
    planned_gets = [product_url, *api_urls.values()]
    if args.dry_run:
        print("[LT READ-ONLY PRODUCT AUDIT] DRY RUN")
        for url in planned_gets:
            print(f"  GET {url}")
        return {
            "status": "dry_run",
            "generated_at": utc_now(),
            "product": {"item_code": args.item_code, "route": args.route, "base_url": args.base_url},
            "readonly_contract": readonly_contract(),
            "planned_gets": planned_gets,
            "public_route": None,
            "optional_api_gets": {"enabled": api_enabled, "base_url": api_base or None, "results": {}},
            "can_prove": can_prove(api_enabled),
            "cannot_prove": cannot_prove(),
            "failures": [],
        }

    failures: list[str] = []
    route_result = fetch_get(product_url, timeout=args.timeout)
    if route_result.get("error"):
        failures.append(f"public route GET failed: {route_result['error']}")
    elif int(route_result.get("status") or 0) >= 400:
        failures.append(f"public route returned HTTP {route_result.get('status')}")

    route_body = route_result.pop("_body_text", "")
    route_evidence = extract_route_evidence(route_body, expected_title="Large head Missionary")
    route_result["evidence"] = route_evidence
    if not route_evidence["expected_title_present"]:
        failures.append("public route did not include expected product title text")

    api_results: dict[str, Any] = {}
    if api_enabled:
        for name, url in api_urls.items():
            result = fetch_get(url, timeout=args.timeout)
            if result.get("error"):
                failures.append(f"{name} GET failed: {result['error']}")
            elif int(result.get("status") or 0) >= 400:
                failures.append(f"{name} returned HTTP {result.get('status')}")
            body = result.pop("_body_text", "")
            result["json"] = parse_json_or_note(body)
            api_results[name] = result

    return {
        "status": "fail" if failures else "pass",
        "generated_at": utc_now(),
        "product": {"item_code": args.item_code, "route": args.route, "base_url": args.base_url},
        "readonly_contract": readonly_contract(),
        "planned_gets": planned_gets,
        "public_route": route_result,
        "optional_api_gets": {"enabled": api_enabled, "base_url": api_base or None, "results": api_results},
        "can_prove": can_prove(api_enabled),
        "cannot_prove": cannot_prove(),
        "blocked_mutating_paths": [
            "variant selector price API uses POST and is intentionally not called",
            "cart and checkout APIs require POST and are intentionally not called",
            "Desk/database record reads requiring authentication are intentionally not attempted",
            "cache clearing and ERPNext writes are intentionally blocked",
        ],
        "failures": failures,
    }


def fetch_get(url: str, *, timeout: float) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={"Accept": "text/html,application/json", "User-Agent": USER_AGENT},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read()
            final_url = response.geturl()
            headers = dict(response.headers.items())
            status = response.status
    except urllib.error.HTTPError as exc:
        body = exc.read()
        final_url = exc.geturl()
        headers = dict(exc.headers.items())
        status = exc.code
    except urllib.error.URLError as exc:
        return {"url": url, "method": "GET", "error": str(exc.reason)}

    text = body.decode("utf-8", errors="replace")
    return {
        "url": url,
        "final_url": final_url,
        "method": "GET",
        "status": status,
        "headers": safe_headers(headers),
        "body_sha256": hashlib.sha256(body).hexdigest(),
        "body_bytes": len(body),
        "_body_text": text,
    }


def extract_route_evidence(body: str, *, expected_title: str) -> dict[str, Any]:
    setup_schema = extract_json_script(body, "js-lt-product-setup-schema")
    architecture = extract_json_script(body, "js-lt-product-page-architecture")
    return {
        "title": first_match_text(body, r"<title[^>]*>(.*?)</title>"),
        "h1": first_match_text(body, r"<h1[^>]*>(.*?)</h1>"),
        "expected_title_present": expected_title.lower() in html.unescape(body).lower(),
        "price_strings": extract_price_strings(body),
        "has_product_setup_schema": isinstance(setup_schema, dict),
        "embedded_product_setup_schema": setup_schema,
        "has_product_page_architecture": isinstance(architecture, dict),
        "embedded_product_page_architecture": architecture,
        "story_container_present": "js-lt-product-story" in body,
        "details_container_present": "js-lt-product-details" in body,
    }


def extract_json_script(body: str, class_name: str) -> Any:
    script_pattern = re.compile(r"<script\b(?P<attrs>[^>]*)>(?P<body>.*?)</script>", re.IGNORECASE | re.DOTALL)
    for match in script_pattern.finditer(body):
        attrs = match.group("attrs")
        if class_name not in attrs:
            continue
        raw = html.unescape(match.group("body")).strip()
        return parse_json_or_note(raw)
    return None


def parse_json_or_note(text: str) -> Any:
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        return {"parse_error": str(exc), "raw_excerpt": text[:500]}


def first_match_text(body: str, pattern: str) -> str | None:
    match = re.search(pattern, body, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    text = re.sub(r"<[^>]+>", " ", match.group(1))
    text = re.sub(r"\s+", " ", html.unescape(text)).strip()
    return text or None


def extract_price_strings(body: str) -> list[str]:
    prices = set()
    for raw in re.findall(r"\$\s*[0-9][0-9,]*(?:\.[0-9]{2})?", html.unescape(body)):
        prices.add(re.sub(r"\$\s*", "$", raw))
    return sorted(prices)


def public_api_urls(api_base: str, item_code: str) -> dict[str, str]:
    params = urllib.parse.urlencode({"item_code": item_code})
    return {
        "product_setup_schema": join_url(
            api_base,
            f"/api/method/locally_twisted.api.product_setup.get_product_setup_schema?{params}",
        ),
        "variant_media": join_url(
            api_base,
            f"/api/method/locally_twisted.api.variant_media.get_variant_media?{params}",
        ),
    }


def readonly_contract() -> dict[str, Any]:
    return {
        "http_methods_allowed": ["GET"],
        "mutating_methods_blocked": sorted(MUTATING_METHODS),
        "erpnext_writes": "blocked",
        "cache_clear": "blocked",
        "credentials_in_args": "not_supported",
        "output": "caller_provided_local_json_path_only",
    }


def can_prove(api_enabled: bool) -> list[str]:
    proof = [
        "public route HTTP response status, selected response headers, and body hash",
        "whether the rendered HTML contains the expected product title text",
        "public HTML title, first H1, visible dollar strings, and LT product script blocks when present",
        "embedded Product Setup schema as rendered into the public page, when present",
    ]
    if api_enabled:
        proof.append("public GET responses from the Product Setup schema and variant media APIs")
    return proof


def cannot_prove() -> list[str]:
    return [
        "authenticated Desk row values or who changed them",
        "complete Website Item, Item, Item Price, Product Setup, File, or slideshow database truth",
        "variant selector price behavior because that public endpoint is POST-only",
        "cart, checkout, Sales Order, payment, invoice, or receipt behavior because those paths are outside GET-only proof",
        "cache health beyond response headers visible on the GET response",
        "release readiness or live data correctness",
    ]


def safe_headers(headers: dict[str, str]) -> dict[str, str]:
    allowed = {
        "cache-control",
        "content-type",
        "date",
        "etag",
        "last-modified",
        "server",
        "x-cache",
        "x-from-cache",
        "x-cache-status",
        "x-frappe-request-id",
        "x-frame-options",
        "x-page-name",
        "x-request-id",
    }
    return {key.lower(): value for key, value in headers.items() if key.lower() in allowed}


def join_url(base: str, path: str) -> str:
    if path.startswith(("http://", "https://")):
        validate_http_base(path, "URL")
        return path
    return urllib.parse.urljoin(base.rstrip("/") + "/", path.lstrip("/"))


def validate_http_base(value: str, label: str) -> None:
    parsed = urllib.parse.urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise AuditBlocked(f"{label} must be an http or https URL")


def validate_local_output(value: str) -> None:
    parsed = urllib.parse.urlparse(value)
    if parsed.scheme:
        raise AuditBlocked("--output must be a local file path, not a URL")
    path = Path(value)
    if path.exists() and path.is_dir():
        raise AuditBlocked("--output must name a JSON file, not a directory")
    if path.suffix.lower() != ".json":
        raise AuditBlocked("--output must end in .json")


def write_report(output: str, report: dict[str, Any]) -> None:
    if report.get("status") == "dry_run":
        return
    output_path = Path(output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def env_truthy(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


if __name__ == "__main__":
    sys.exit(main())
