#!/usr/bin/env python3
"""Read-only Meta operations inventory for Locally Twisted.

This verifier answers: "What can the current Meta token see?"

It performs only Graph API GET requests. It does not create, edit, pause,
publish, send messages, fetch lead records, touch billing, change partner
access, or change ENB access.

Usage from the project root:

    python scripts/verify/meta_operations_inventory.py

Optional JSON output:

    python scripts/verify/meta_operations_inventory.py --json
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
from pathlib import Path
from typing import Any


GRAPH_HOST = "https://graph.facebook.com"
DEFAULT_VERSION = "v25.0"
DEFAULT_ENV_FILE = ".env"
DEFAULT_TOKEN_ENV = "META_ACCESS_TOKEN"
DEFAULT_BUSINESS_ID = "1327185764080942"
DEFAULT_AD_ACCOUNT_ID = "act_27813262"


@dataclass(frozen=True)
class Check:
    key: str
    path: str
    fields: str
    limit: int = 100
    required: bool = False
    notes: str = ""


class GraphReadError(RuntimeError):
    def __init__(self, status: int | None, payload: dict[str, Any] | str):
        self.status = status
        self.payload = payload
        super().__init__(self._format())

    def _format(self) -> str:
        if isinstance(self.payload, dict):
            error = self.payload.get("error") if isinstance(self.payload.get("error"), dict) else {}
            message = error.get("message") or self.payload
            code = error.get("code")
            error_type = error.get("type")
            parts = []
            if self.status:
                parts.append(f"HTTP {self.status}")
            if error_type:
                parts.append(str(error_type))
            if code:
                parts.append(f"code={code}")
            parts.append(str(message))
            return ": ".join(parts)
        prefix = f"HTTP {self.status}: " if self.status else ""
        return prefix + str(self.payload)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", default=DEFAULT_ENV_FILE)
    parser.add_argument("--token-env", default=DEFAULT_TOKEN_ENV)
    parser.add_argument("--api-version", default=DEFAULT_VERSION)
    parser.add_argument("--business-id", default=DEFAULT_BUSINESS_ID)
    parser.add_argument("--ad-account-id", default=DEFAULT_AD_ACCOUNT_ID)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args(argv)

    token = os.environ.get(args.token_env, "").strip() or read_env_value(Path(args.env_file), args.token_env)
    if not token:
        print("[META OPERATIONS INVENTORY] BLOCKED")
        print(f"  - {args.token_env} was not found in the shell or {args.env_file}.")
        print("  - No Meta request was made.")
        return 2

    inventory = run_inventory(
        token=token,
        version=args.api_version,
        business_id=args.business_id,
        ad_account_id=args.ad_account_id,
        timeout=args.timeout,
    )

    if args.json:
        print(json.dumps(inventory, indent=2, sort_keys=True))
    else:
        print_text_summary(inventory)

    return 1 if inventory["failures"] else 0


def run_inventory(*, token: str, version: str, business_id: str, ad_account_id: str, timeout: float) -> dict[str, Any]:
    checks = [
        Check("business", business_id, "id,name,verification_status,primary_page", required=True),
        Check("owned_ad_accounts", f"{business_id}/owned_ad_accounts", "id,account_id,name,account_status,currency,timezone_name,business,disable_reason"),
        Check("client_ad_accounts", f"{business_id}/client_ad_accounts", "id,account_id,name,account_status,currency,timezone_name,business,disable_reason"),
        Check("owned_pages", f"{business_id}/owned_pages", "id,name,verification_status,link"),
        Check("system_users", f"{business_id}/system_users", "id,name,role"),
        Check("ad_account", ad_account_id, "id,account_id,name,account_status,currency,timezone_name,business,disable_reason"),
        Check("campaigns", f"{ad_account_id}/campaigns", "id,name,status,effective_status,objective,buying_type,created_time,updated_time"),
        Check("adsets", f"{ad_account_id}/adsets", "id,name,status,effective_status,campaign_id"),
        Check("ads", f"{ad_account_id}/ads", "id,name,status,effective_status,adset_id,campaign_id"),
        Check("insights_last_7d", f"{ad_account_id}/insights", "account_id,spend,impressions,clicks", limit=1),
        Check("pixels", f"{ad_account_id}/adspixels", "id,name,creation_time,last_fired_time,owner_business"),
        Check("custom_conversions", f"{ad_account_id}/customconversions", "id,name,custom_event_type,event_source_type,is_archived"),
    ]

    results: dict[str, Any] = {}
    failures: dict[str, str] = {}
    warnings: dict[str, str] = {}
    owned_pages: list[dict[str, Any]] = []

    for check in checks:
        params = {"fields": check.fields, "limit": str(check.limit)}
        if check.key == "insights_last_7d":
            params["date_preset"] = "last_7d"
        try:
            payload = graph_get(
                token=token,
                version=version,
                path=check.path,
                params=params,
                timeout=timeout,
            )
        except GraphReadError as exc:
            if check.required:
                failures[check.key] = str(exc)
            else:
                warnings[check.key] = str(exc)
            results[check.key] = {"ok": False, "error": str(exc), "required": check.required}
            continue

        summary = summarize_payload(payload)
        results[check.key] = {"ok": True, **summary}
        if check.key == "owned_pages":
            owned_pages = payload.get("data", []) if isinstance(payload.get("data"), list) else []

    page_checks = []
    lane_blockers: list[str] = []
    for page in owned_pages:
        page_id = str(page.get("id") or "")
        if not page_id:
            continue
        page_summary = {"page": page.get("name"), "page_id": page_id, "checks": {}}
        page_check_specs = [
            ("page_metadata", page_id, "id,name,instagram_business_account,connected_instagram_account"),
            ("page_posts_public_metadata", f"{page_id}/posts", "id,created_time,permalink_url"),
            ("lead_forms_metadata", f"{page_id}/leadgen_forms", "id,name,status,created_time"),
        ]
        for key, path, fields in page_check_specs:
            try:
                payload = graph_get(
                    token=token,
                    version=version,
                    path=path,
                    params={"fields": fields, "limit": "100"},
                    timeout=timeout,
                )
            except GraphReadError as exc:
                page_summary["checks"][key] = {"ok": False, "error": str(exc)}
                if key in {"page_posts_public_metadata", "lead_forms_metadata"}:
                    lane_blockers.append(f"{page.get('name') or page_id} {key}: {exc}")
                continue
            page_summary["checks"][key] = {"ok": True, **summarize_payload(payload)}
        page_checks.append(page_summary)

    debug = debug_token(token=token, version=version, timeout=timeout)
    return {
        "status": "fail" if failures else "pass",
        "method": "GET only",
        "mutation": "none",
        "token_printed": False,
        "lead_records_exported": False,
        "customer_messages_read": False,
        "enb_access": "untouched",
        "api_version": version,
        "business_id": business_id,
        "ad_account_id": ad_account_id,
        "token": debug,
        "results": results,
        "page_checks": page_checks,
        "lane_blockers": lane_blockers,
        "warnings": warnings,
        "failures": failures,
    }


def read_env_value(path: Path, key: str) -> str:
    if not path.exists():
        return ""
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].lstrip()
        if not line.startswith(key + "="):
            continue
        value = line.split("=", 1)[1].strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        return value
    return ""


def graph_get(
    *,
    token: str,
    version: str,
    path: str,
    params: dict[str, str],
    timeout: float,
) -> dict[str, Any]:
    encoded = dict(params)
    encoded["access_token"] = token
    url = f"{GRAPH_HOST}/{version.strip('/')}/{path.lstrip('/')}?{urllib.parse.urlencode(encoded)}"
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "lt-meta-ops-inventory/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise GraphReadError(exc.code, parse_json_or_text(body)) from None
    except urllib.error.URLError as exc:
        raise GraphReadError(None, str(exc.reason)) from None
    except json.JSONDecodeError as exc:
        raise GraphReadError(None, f"non-JSON response: {exc}") from None

    if not isinstance(payload, dict):
        raise GraphReadError(None, f"expected JSON object, got {type(payload).__name__}")
    if "error" in payload:
        raise GraphReadError(None, payload)
    return payload


def debug_token(*, token: str, version: str, timeout: float) -> dict[str, Any]:
    try:
        payload = graph_get(
            token=token,
            version=version,
            path="debug_token",
            params={"input_token": token},
            timeout=timeout,
        )
    except GraphReadError as exc:
        return {"ok": False, "error": str(exc)}
    data = payload.get("data", {}) if isinstance(payload.get("data"), dict) else {}
    return {
        "ok": bool(data.get("is_valid")),
        "app_id": data.get("app_id"),
        "application": data.get("application"),
        "type": data.get("type"),
        "expires_at": data.get("expires_at"),
        "data_access_expires_at": data.get("data_access_expires_at"),
        "scopes": sorted(str(scope) for scope in data.get("scopes", []) if scope),
        "granular_scopes_count": len(data.get("granular_scopes", []) or []),
    }


def summarize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if isinstance(payload.get("data"), list):
        items = payload["data"]
        return {
            "count": len(items),
            "names": item_labels(items),
        }
    keys = sorted(key for key in payload.keys() if key not in {"access_token"})
    summary: dict[str, Any] = {"count": None, "keys": keys}
    for key in ("id", "name", "account_id", "account_status", "currency", "timezone_name", "verification_status"):
        if key in payload:
            summary[key] = payload[key]
    return summary


def item_labels(items: list[Any], max_items: int = 8) -> list[str]:
    labels = []
    for item in items[:max_items]:
        if not isinstance(item, dict):
            continue
        label = item.get("name") or item.get("username") or item.get("account_id") or item.get("id")
        if label:
            labels.append(str(label))
    return labels


def parse_json_or_text(text: str) -> dict[str, Any] | str:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return text.strip()
    return payload if isinstance(payload, dict) else text.strip()


def print_text_summary(inventory: dict[str, Any]) -> None:
    print("[META OPERATIONS INVENTORY] " + inventory["status"].upper())
    print("  method: GET only")
    print("  mutation: none")
    print("  token_printed: false")
    print("  lead_records_exported: false")
    print("  customer_messages_read: false")
    print("  enb_access: untouched")
    token = inventory.get("token", {})
    print(f"  token_valid: {token.get('ok')}")
    print(f"  token_type: {token.get('type')}")
    print(f"  app: {token.get('application')} ({token.get('app_id')})")
    print(f"  scopes: {', '.join(token.get('scopes', []))}")
    print("  resources:")
    for key, value in inventory.get("results", {}).items():
        ok = value.get("ok")
        count = value.get("count")
        detail = f"count={count}" if count is not None else "object"
        print(f"  - {key}: {'ok' if ok else 'blocked'} ({detail})")
    if inventory.get("warnings"):
        print("  warnings:")
        for key, value in inventory["warnings"].items():
            print(f"  - {key}: {value}")
    if inventory.get("lane_blockers"):
        print("  lane_blockers:")
        for value in inventory["lane_blockers"]:
            print(f"  - {value}")


if __name__ == "__main__":
    sys.exit(main())
