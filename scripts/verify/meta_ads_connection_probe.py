#!/usr/bin/env python3
"""Read-only Meta ads API connection probe.

Use from the project root after a Meta access token exists:

    META_ACCESS_TOKEN="..." python scripts/verify/meta_ads_connection_probe.py

Optional business-asset check:

    META_ACCESS_TOKEN="..." python scripts/verify/meta_ads_connection_probe.py --include-businesses

This script validates whether the token can read the current user and visible
Meta ad accounts. It performs only Graph API GET requests. It does not create,
edit, pause, publish, export customer data, touch billing, or change partner
access.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


GRAPH_HOST = "https://graph.facebook.com"
DEFAULT_VERSION = "v25.0"
DEFAULT_TOKEN_ENV = "META_ACCESS_TOKEN"


@dataclass(frozen=True)
class Probe:
    name: str
    path: str
    fields: str
    required: bool = True


BASE_PROBES = (
    Probe("current_user", "me", "id,name"),
    Probe(
        "ad_accounts",
        "me/adaccounts",
        "id,account_id,name,account_status,currency,timezone_name,business,disable_reason",
    ),
)

BUSINESS_PROBES = (
    Probe("businesses", "me/businesses", "id,name,verification_status,primary_page", required=False),
)


class GraphProbeError(RuntimeError):
    """Raised when a read-only Graph API probe fails."""

    def __init__(self, name: str, status: int | None, payload: dict[str, Any] | str):
        self.name = name
        self.status = status
        self.payload = payload
        super().__init__(self._format())

    def _format(self) -> str:
        if isinstance(self.payload, dict):
            error = self.payload.get("error") if isinstance(self.payload.get("error"), dict) else {}
            message = error.get("message") or self.payload
            code = error.get("code")
            error_type = error.get("type")
            pieces = [f"{self.name} failed"]
            if self.status:
                pieces.append(f"HTTP {self.status}")
            if error_type:
                pieces.append(str(error_type))
            if code:
                pieces.append(f"code {code}")
            pieces.append(str(message))
            return ": ".join(pieces)
        suffix = f"HTTP {self.status}: " if self.status else ""
        return f"{self.name} failed: {suffix}{self.payload}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--token-env",
        default=DEFAULT_TOKEN_ENV,
        help=f"Environment variable containing the Meta access token. Default: {DEFAULT_TOKEN_ENV}",
    )
    parser.add_argument(
        "--api-version",
        default=DEFAULT_VERSION,
        help=f"Meta Graph API version to call. Default: {DEFAULT_VERSION}",
    )
    parser.add_argument(
        "--include-businesses",
        action="store_true",
        help="Also try the read-only /me/businesses business-asset probe.",
    )
    parser.add_argument("--json", action="store_true", help="Print raw sanitized JSON probe results.")
    parser.add_argument("--dry-run", action="store_true", help="Print the GET endpoints that would be called.")
    parser.add_argument("--timeout", type=float, default=20.0, help="HTTP timeout in seconds.")
    args = parser.parse_args(argv)

    probes = list(BASE_PROBES)
    if args.include_businesses:
        probes.extend(BUSINESS_PROBES)

    if args.dry_run:
        print("[META ADS CONNECTION PROBE] DRY RUN")
        print("  method: GET only")
        print("  mutation: none")
        for probe in probes:
            print(f"  - {probe.name}: /{args.api_version}/{probe.path}?fields={probe.fields}")
        return 0

    token = os.environ.get(args.token_env, "").strip()
    if not token:
        print("[META ADS CONNECTION PROBE] BLOCKED")
        print(f"  - Set {args.token_env} in the environment for this shell only.")
        print("  - Do not commit tokens, paste tokens into docs, or store them in this repo.")
        print("  - No Meta request was made.")
        return 2

    results: dict[str, Any] = {}
    failures: list[str] = []
    warnings: list[str] = []
    for probe in probes:
        try:
            results[probe.name] = graph_get(
                version=args.api_version,
                path=probe.path,
                params={"fields": probe.fields, "limit": "100"},
                token=token,
                timeout=args.timeout,
            )
        except GraphProbeError as exc:
            message = str(exc)
            if probe.required:
                failures.append(message)
            else:
                warnings.append(message)

    sanitized = sanitize_results(results)
    if args.json:
        print(
            json.dumps(
                {
                    "status": "fail" if failures else "pass",
                    "api_version": args.api_version,
                    "method": "GET",
                    "mutation": "none",
                    "results": sanitized,
                    "warnings": warnings,
                    "failures": failures,
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        print("[META ADS CONNECTION PROBE] " + ("FAIL" if failures else "PASS"))
        print("  method: GET only")
        print("  mutation: none")
        print("  enb_access: untouched")
        print_summary(sanitized, warnings, failures)

    return 1 if failures else 0


def graph_get(
    *,
    version: str,
    path: str,
    params: dict[str, str],
    token: str,
    timeout: float,
) -> dict[str, Any]:
    encoded_params = dict(params)
    encoded_params["access_token"] = token
    url = f"{GRAPH_HOST}/{version.strip('/')}/{path.lstrip('/')}?{urllib.parse.urlencode(encoded_params)}"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "lt-meta-ads-connection-probe/1.0",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise GraphProbeError(path, exc.code, parse_json_or_text(body)) from None
    except urllib.error.URLError as exc:
        raise GraphProbeError(path, None, str(exc.reason)) from None
    except json.JSONDecodeError as exc:
        raise GraphProbeError(path, None, f"non-JSON response: {exc}") from None

    if not isinstance(payload, dict):
        raise GraphProbeError(path, None, f"expected JSON object, got {type(payload).__name__}")
    if "error" in payload:
        raise GraphProbeError(path, None, payload)
    return payload


def parse_json_or_text(text: str) -> dict[str, Any] | str:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return text.strip()
    return payload if isinstance(payload, dict) else text.strip()


def sanitize_results(results: dict[str, Any]) -> dict[str, Any]:
    sanitized: dict[str, Any] = {}
    for key, value in results.items():
        if key == "current_user":
            sanitized[key] = {
                "id_present": bool(value.get("id")),
                "name_present": bool(value.get("name")),
            }
        elif key in {"ad_accounts", "businesses"}:
            rows = value.get("data") if isinstance(value.get("data"), list) else []
            sanitized[key] = {
                "count": len(rows),
                "items": [sanitize_item(row) for row in rows],
            }
        else:
            sanitized[key] = value
    return sanitized


def sanitize_item(item: Any) -> dict[str, Any]:
    if not isinstance(item, dict):
        return {"raw_type": type(item).__name__}
    allowed = {
        "id",
        "account_id",
        "name",
        "account_status",
        "currency",
        "timezone_name",
        "business",
        "disable_reason",
        "verification_status",
        "primary_page",
    }
    return {key: item[key] for key in sorted(allowed) if key in item}


def print_summary(sanitized: dict[str, Any], warnings: list[str], failures: list[str]) -> None:
    current_user = sanitized.get("current_user") or {}
    print(f"  current_user_visible: {bool(current_user.get('id_present'))}")
    if "ad_accounts" in sanitized:
        print(f"  ad_accounts_visible: {sanitized['ad_accounts'].get('count', 0)}")
    if "businesses" in sanitized:
        print(f"  businesses_visible: {sanitized['businesses'].get('count', 0)}")
    if warnings:
        print("  warnings:")
        for warning in warnings:
            print(f"    - {warning}")
    if failures:
        print("  failures:")
        for failure in failures:
            print(f"    - {failure}")


if __name__ == "__main__":
    sys.exit(main())
