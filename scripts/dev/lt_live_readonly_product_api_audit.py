#!/usr/bin/env python3
"""Live read-only LT product authority audit through Frappe Cloud site login.

This helper uses Frappe Cloud API credentials only to obtain a temporary site
session, then performs GET requests against the live ERPNext site API.

It never writes ERPNext data, never clears cache, never deploys, and never
prints or stores API secrets or the returned session id. The only write is the
caller-provided local JSON evidence file.

Required environment, usually loaded from `.env`:

  FRAPPE_CLOUD_BASE_URL
  FRAPPE_CLOUD_API_KEY
  FRAPPE_CLOUD_API_SECRET
  FRAPPE_CLOUD_SITE_NAME
"""
from __future__ import annotations

import argparse
import hashlib
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


DEFAULT_HOST = "https://locallytwisted.com"
DEFAULT_ITEM_CODE = "large-head-missionary"
DEFAULT_BLUEPRINT = "large-head-missionary"
DEFAULT_WEBSITE_ITEM = "WEB-ITM-0039"
DEFAULT_ROUTE = "/shop-items/bouquets/large-head-missionary"
DEFAULT_FC_BASE = "https://cloud.frappe.io"
USER_AGENT = "lt-live-readonly-product-api-audit/1.0"


class LiveAuditBlocked(RuntimeError):
    """Raised when a requested behavior is outside the read-only contract."""


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        enforce_contract(args)
        if args.env_file:
            load_env_file(Path(args.env_file))
        if args.dry_run:
            print("[LT LIVE READ-ONLY PRODUCT API AUDIT] DRY RUN")
            print(f"  host: {args.host}")
            print(f"  site env: {env_present('FRAPPE_CLOUD_SITE_NAME')}")
            print(f"  item_code: {args.item_code}")
            print(f"  blueprint: {args.blueprint}")
            print(f"  website_item: {args.website_item}")
            print("  operation: Frappe Cloud site login + live ERPNext GET requests only")
            return 0
        report = build_report(args)
        write_report(args.output, report)
    except LiveAuditBlocked as exc:
        print(f"[LT LIVE READ-ONLY PRODUCT API AUDIT] BLOCKED: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"[LT LIVE READ-ONLY PRODUCT API AUDIT] FAIL: {exc}", file=sys.stderr)
        return 1

    status = "PASS" if not report["failures"] else "FAIL"
    print(f"[LT LIVE READ-ONLY PRODUCT API AUDIT] {status}")
    print(f"  output: {Path(args.output).resolve()}")
    print("  mutation: none")
    for failure in report["failures"]:
        print(f"  failure: {failure}")
    return 0 if not report["failures"] else 1


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--env-file", default=".env", help="Local dotenv file to load without printing values.")
    parser.add_argument("--host", default=DEFAULT_HOST, help=f"Live ERPNext host. Default: {DEFAULT_HOST}")
    parser.add_argument("--item-code", default=DEFAULT_ITEM_CODE, help=f"Template item code. Default: {DEFAULT_ITEM_CODE}")
    parser.add_argument("--blueprint", default=DEFAULT_BLUEPRINT, help=f"LT Product Blueprint name. Default: {DEFAULT_BLUEPRINT}")
    parser.add_argument("--website-item", default=DEFAULT_WEBSITE_ITEM, help=f"Website Item name. Default: {DEFAULT_WEBSITE_ITEM}")
    parser.add_argument("--route", default=DEFAULT_ROUTE, help=f"Public product route. Default: {DEFAULT_ROUTE}")
    parser.add_argument("--output", help="Caller-provided local JSON output path.")
    parser.add_argument("--timeout", type=float, default=30.0, help="HTTP timeout seconds.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned read-only scope.")
    parser.add_argument("--clear-cache", action="store_true", help="Unsupported; included so accidental use fails loudly.")
    parser.add_argument("--write-erpnext", action="store_true", help="Unsupported; included so accidental use fails loudly.")
    parser.add_argument("--deploy", action="store_true", help="Unsupported; included so accidental use fails loudly.")
    return parser.parse_args(argv)


def enforce_contract(args: argparse.Namespace) -> None:
    if args.clear_cache:
        raise LiveAuditBlocked("cache clearing is outside this helper's contract")
    if args.write_erpnext:
        raise LiveAuditBlocked("ERPNext writes are outside this helper's contract")
    if args.deploy:
        raise LiveAuditBlocked("deploy/release action is outside this helper's contract")
    validate_http_base(args.host)
    if not args.dry_run:
        if not args.output:
            raise LiveAuditBlocked("--output is required unless --dry-run is used")
        validate_local_output(args.output)


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    sid = frappe_cloud_site_session(
        reason=f"LT live read-only product authority audit {datetime.now(timezone.utc).date().isoformat()}",
        timeout=args.timeout,
    )
    failures: list[str] = []
    client = SiteClient(args.host, sid, timeout=args.timeout)

    blueprint = data_or_failure(
        client.get_json(f"/api/resource/{quote_path('LT Product Blueprint')}/{quote_path(args.blueprint)}"),
        "blueprint",
        failures,
    ) or {}
    website_item = data_or_failure(
        client.get_json(f"/api/resource/{quote_path('Website Item')}/{quote_path(args.website_item)}"),
        "website_item",
        failures,
    ) or {}
    template_item = data_or_failure(
        client.get_json(f"/api/resource/{quote_path('Item')}/{quote_path(args.item_code)}"),
        "template_item",
        failures,
    ) or {}

    variants = api_list(
        client,
        "Item",
        filters=[["variant_of", "=", args.item_code]],
        fields=["name", "item_code", "variant_of", "disabled", "is_sales_item", "image", "modified", "modified_by"],
    )
    item_codes = [args.item_code, *[row["item_code"] for row in variants if row.get("item_code")]]
    item_prices = api_list(
        client,
        "Item Price",
        filters=[["item_code", "in", item_codes], ["selling", "=", 1]],
        fields=[
            "name",
            "item_code",
            "price_list",
            "price_list_rate",
            "currency",
            "uom",
            "selling",
            "valid_from",
            "valid_upto",
            "modified",
            "modified_by",
        ],
    )

    public_result = client.get_text(args.route)
    html = public_result.pop("_body_text", "")
    price_strings = sorted(set(re.findall(r"\$\s?\d+(?:\.\d{2})?", html)))

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scope": "live authenticated read-only site API plus public GET; no writes/cache/deploy",
        "host": args.host,
        "site_name": env_required("FRAPPE_CLOUD_SITE_NAME"),
        "user_context": "site session obtained from Frappe Cloud API; sid redacted and not stored",
        "readonly_contract": {
            "frappe_cloud": "GET site login only",
            "erpnext_site": "GET /api/resource and public GET only",
            "erpnext_writes": "blocked",
            "cache_clear": "blocked",
            "deploy": "blocked",
            "payment_provider": "blocked",
        },
        "blueprint_summary": pick(
            blueprint,
            [
                "name",
                "product_name",
                "product_slug",
                "operating_brand",
                "base_price",
                "publish_status",
                "shop_visibility",
                "validation_status",
                "ready_for_live",
                "target_item_code",
                "target_website_item",
                "modified",
                "modified_by",
                "owner",
            ],
        ),
        "website_item_summary": pick(
            website_item,
            [
                "name",
                "item_code",
                "web_item_name",
                "published",
                "route",
                "item_group",
                "website_image",
                "slideshow",
                "modified",
                "modified_by",
                "owner",
            ],
        ),
        "template_item_summary": pick(
            template_item,
            [
                "name",
                "item_code",
                "item_name",
                "item_group",
                "has_variants",
                "disabled",
                "is_sales_item",
                "is_stock_item",
                "image",
                "modified",
                "modified_by",
                "owner",
            ],
        ),
        "counts": {
            "variants": len(variants),
            "item_prices": len(item_prices),
            "blueprint_price_rows": len(blueprint.get("price_rows") or []),
            "blueprint_option_rows": len(blueprint.get("option_rows") or []),
            "blueprint_content_rule_rows": len(blueprint.get("content_rule_rows") or []),
        },
        "price_summary": {
            "blueprint_base_price": blueprint.get("base_price"),
            "blueprint_price_row_values": sorted(float_values(blueprint.get("price_rows") or [], "price")),
            "item_price_values": sorted(float_values(item_prices, "price_list_rate")),
            "item_price_modified_summary": sorted(
                {
                    f"{row.get('modified')} by {row.get('modified_by')}"
                    for row in item_prices
                    if row.get("modified") or row.get("modified_by")
                }
            ),
        },
        "content_summary": {
            "blueprint_content_fields": content_fields(blueprint),
            "website_item_content_fields": content_fields(website_item),
            "blueprint_content_rule_rows": blueprint.get("content_rule_rows") or [],
        },
        "public_summary": {
            **public_result,
            "price_strings": price_strings,
            "contains_125": "$125" in html or "125.00" in html,
            "contains_175": "$175" in html or "175.00" in html,
        },
        "rows": {
            "blueprint_price_rows": blueprint.get("price_rows") or [],
            "blueprint_option_rows": blueprint.get("option_rows") or [],
            "variants": variants,
            "item_prices": item_prices,
        },
        "failures": failures,
    }
    return report


class SiteClient:
    def __init__(self, host: str, sid: str, *, timeout: float) -> None:
        self.host = host.rstrip("/")
        self.sid = sid
        self.timeout = timeout

    def get_json(self, path: str) -> dict[str, Any]:
        result = self._get(path, accept="application/json")
        if "json" not in result:
            raise LiveAuditBlocked(f"{path} did not return JSON")
        return result["json"]

    def get_text(self, path: str) -> dict[str, Any]:
        return self._get(path, accept="text/html")

    def _get(self, path: str, *, accept: str) -> dict[str, Any]:
        request = urllib.request.Request(
            self.host + path,
            headers={
                "Accept": accept,
                "Cookie": f"sid={self.sid}",
                "X-Requested-With": "XMLHttpRequest",
                "User-Agent": USER_AGENT,
            },
            method="GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = response.read()
                status = response.status
                headers = dict(response.headers.items())
        except urllib.error.HTTPError as exc:
            body = exc.read()
            status = exc.code
            headers = dict(exc.headers.items())
        text = body.decode("utf-8", errors="replace")
        result: dict[str, Any] = {
            "status": status,
            "content_type": headers.get("Content-Type") or headers.get("content-type"),
            "body_sha256": hashlib.sha256(body).hexdigest(),
            "body_bytes": len(body),
        }
        if "json" in str(result["content_type"]).lower():
            result["json"] = json.loads(text)
        else:
            result["_body_text"] = text
        return result


def api_list(client: SiteClient, doctype: str, *, filters: list[Any], fields: list[str]) -> list[dict[str, Any]]:
    query = urllib.parse.urlencode(
        {
            "filters": json.dumps(filters),
            "fields": json.dumps(fields),
            "limit_page_length": "5000",
        }
    )
    payload = client.get_json(f"/api/resource/{quote_path(doctype)}?{query}")
    data = payload.get("data") or []
    if not isinstance(data, list):
        raise LiveAuditBlocked(f"{doctype} list did not return a list")
    return data


def frappe_cloud_site_session(*, reason: str, timeout: float) -> str:
    params = {"name": env_required("FRAPPE_CLOUD_SITE_NAME"), "reason": reason}
    payload = frappe_cloud_get("/api/method/press.api.site.login", params, timeout=timeout)
    sid = (payload.get("message") or {}).get("sid") if isinstance(payload.get("message"), dict) else payload.get("sid")
    if not sid:
        raise LiveAuditBlocked("Frappe Cloud site login did not return a site session")
    return str(sid)


def frappe_cloud_get(endpoint: str, params: dict[str, Any], *, timeout: float) -> dict[str, Any]:
    base = os.environ.get("FRAPPE_CLOUD_BASE_URL", DEFAULT_FC_BASE).rstrip("/")
    url = f"{base}{endpoint}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "Authorization": f"token {env_required('FRAPPE_CLOUD_API_KEY')}:{env_required('FRAPPE_CLOUD_API_SECRET')}",
            "User-Agent": USER_AGENT,
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise LiveAuditBlocked(f"Frappe Cloud GET {endpoint} failed with HTTP {exc.code}: {body[:300]}") from exc


def data_or_failure(payload: dict[str, Any], label: str, failures: list[str]) -> dict[str, Any] | None:
    data = payload.get("data")
    if isinstance(data, dict):
        return data
    message = payload.get("message")
    if isinstance(message, dict):
        return message
    failures.append(f"{label} returned no document data")
    return None


def content_fields(doc: dict[str, Any]) -> dict[str, Any]:
    markers = ("about", "description", "story", "detail", "copy", "content", "subtitle", "intro", "seo")
    return {
        key: value
        for key, value in doc.items()
        if any(marker in key.lower() for marker in markers) and not isinstance(value, (list, dict))
    }


def pick(doc: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    return {field: doc.get(field) for field in fields if field in doc}


def float_values(rows: list[dict[str, Any]], key: str) -> set[float]:
    values: set[float] = set()
    for row in rows:
        value = row.get(key)
        if value in (None, ""):
            continue
        values.add(float(value))
    return values


def quote_path(value: str) -> str:
    return urllib.parse.quote(value, safe="")


def env_present(name: str) -> str:
    return "present" if os.environ.get(name) else "missing"


def env_required(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise LiveAuditBlocked(f"missing required environment variable: {name}")
    return value


def load_env_file(path: Path) -> None:
    if not path.exists():
        raise LiveAuditBlocked(f"env file does not exist: {path}")
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key and key not in os.environ:
            os.environ[key] = value


def validate_http_base(value: str) -> None:
    parsed = urllib.parse.urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise LiveAuditBlocked(f"invalid HTTP base URL: {value!r}")


def validate_local_output(path: str) -> None:
    output = Path(path)
    if output.exists() and output.is_dir():
        raise LiveAuditBlocked(f"output path is a directory: {output}")
    parent = output.expanduser().resolve().parent
    if not parent.exists():
        raise LiveAuditBlocked(f"output parent does not exist: {parent}")


def write_report(path: str, report: dict[str, Any]) -> None:
    Path(path).write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
