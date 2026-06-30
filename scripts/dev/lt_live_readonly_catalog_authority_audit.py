#!/usr/bin/env python3
"""Collect read-only LT catalog authority artifacts through Frappe site login.

This scales the single-product live audit helper to the published Website Item
catalog. It uses Frappe Cloud API credentials only to obtain a temporary site
session, then performs GET requests against the ERPNext site API. It never
writes ERPNext data, clears cache, deploys, or stores the returned session id.

Required environment for non-dry-run use, usually loaded from `.env`:

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
DEFAULT_FC_BASE = "https://cloud.frappe.io"
DEFAULT_OUTPUT_DIR = "output/lt-live-readonly-catalog-authority"
USER_AGENT = "lt-live-readonly-catalog-authority-audit/1.0"
ACTIVE_BLUEPRINT_STATUSES = {
    "Needs Product Review",
    "Needs Price Review",
    "Needs Media Review",
    "Local Preview Ready",
    "Staging Ready",
    "Approved For Live",
    "Live",
    "Hidden",
    "Quote Only",
    "Paused",
}


class CatalogAuditBlocked(RuntimeError):
    """Raised when a requested behavior is outside the read-only contract."""


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        enforce_contract(args)
        if args.env_file and not args.dry_run:
            load_env_file(Path(args.env_file))
        if args.dry_run:
            print("[LT LIVE READ-ONLY CATALOG AUTHORITY AUDIT] DRY RUN")
            print(f"  host: {args.host}")
            print(f"  output_dir: {args.output_dir}")
            print(f"  include_unpublished: {args.include_unpublished}")
            print(f"  public_get: {args.public_get}")
            print(f"  limit: {args.limit if args.limit is not None else 'all'}")
            print("  operation: Frappe Cloud site login + live ERPNext GET requests only")
            print("  mutation: none")
            return 0
        index = collect_catalog(args)
    except CatalogAuditBlocked as exc:
        print(f"[LT LIVE READ-ONLY CATALOG AUTHORITY AUDIT] BLOCKED: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"[LT LIVE READ-ONLY CATALOG AUTHORITY AUDIT] FAIL: {exc}", file=sys.stderr)
        return 1

    status = "PASS" if not index["failures"] else "FAIL"
    print(f"[LT LIVE READ-ONLY CATALOG AUTHORITY AUDIT] {status}")
    print(f"  output_dir: {Path(args.output_dir).resolve()}")
    print(f"  index: {index['index_path']}")
    print(f"  products_written: {index['counts']['products_written']}")
    print("  mutation: none")
    for failure in index["failures"][:12]:
        print(f"  failure: {failure}")
    if len(index["failures"]) > 12:
        print(f"  failure: ... {len(index['failures']) - 12} more")
    return 0 if not index["failures"] else 1


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--env-file", default=".env", help="Local dotenv file to load without printing values.")
    parser.add_argument("--host", default=DEFAULT_HOST, help=f"Live ERPNext host. Default: {DEFAULT_HOST}")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="Directory for per-product artifacts and index JSON.")
    parser.add_argument("--limit", type=positive_int, help="Limit number of Website Items processed after filtering.")
    parser.add_argument("--include-unpublished", action="store_true", help="Include unpublished Website Items.")
    parser.add_argument("--public-get", action="store_true", help="Also GET each public route and store hashes/price strings.")
    parser.add_argument("--timeout", type=float, default=30.0, help="HTTP timeout seconds.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned read-only scope without env, login, network, or writes.")
    parser.add_argument("--clear-cache", action="store_true", help="Unsupported; included so accidental use fails loudly.")
    parser.add_argument("--write-erpnext", action="store_true", help="Unsupported; included so accidental use fails loudly.")
    parser.add_argument("--deploy", action="store_true", help="Unsupported; included so accidental use fails loudly.")
    return parser.parse_args(argv)


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("--limit must be greater than zero")
    return parsed


def enforce_contract(args: argparse.Namespace) -> None:
    if args.clear_cache:
        raise CatalogAuditBlocked("cache clearing is outside this helper's contract")
    if args.write_erpnext:
        raise CatalogAuditBlocked("ERPNext writes are outside this helper's contract")
    if args.deploy:
        raise CatalogAuditBlocked("deploy/release action is outside this helper's contract")
    validate_http_base(args.host)
    if args.timeout <= 0:
        raise CatalogAuditBlocked("--timeout must be greater than zero")
    if not args.dry_run:
        validate_local_output_dir(args.output_dir)


def collect_catalog(args: argparse.Namespace) -> dict[str, Any]:
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    output_dir = Path(args.output_dir).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    sid = frappe_cloud_site_session(
        reason=f"LT live read-only catalog authority audit {datetime.now(timezone.utc).date().isoformat()}",
        timeout=args.timeout,
    )
    client = SiteClient(args.host, sid, timeout=args.timeout)
    failures: list[str] = []

    website_items = list_website_items(client, include_unpublished=args.include_unpublished)
    if args.limit is not None:
        website_items = website_items[: args.limit]
    blueprints = list_blueprints(client)
    blueprint_index = build_blueprint_index(blueprints)

    artifacts: list[dict[str, Any]] = []
    for position, website_row in enumerate(website_items, start=1):
        artifact = build_product_artifact(
            client,
            website_row,
            blueprint_index=blueprint_index,
            host=args.host,
            generated_at=generated_at,
            include_public_get=args.public_get,
            failures=failures,
        )
        filename = artifact_filename(position, artifact)
        artifact_path = output_dir / filename
        write_json(artifact_path, artifact)
        artifacts.append(
            {
                "artifact": filename,
                "product_identifier": artifact["product_identifier"],
                "match_summary": artifact["match_summary"],
                "counts": artifact["counts"],
                "failures": artifact["failures"],
            }
        )

    index_path = output_dir / "index.json"
    index = {
        "generated_at": generated_at,
        "scope": "live authenticated read-only site API; optional public GET; no writes/cache/deploy",
        "host": args.host,
        "site_name": env_required("FRAPPE_CLOUD_SITE_NAME"),
        "user_context": "site session obtained from Frappe Cloud API; sid redacted and not stored",
        "readonly_contract": readonly_contract(public_get=args.public_get),
        "inputs": {
            "include_unpublished": args.include_unpublished,
            "public_get": args.public_get,
            "limit": args.limit,
        },
        "counts": {
            "website_items_seen": len(website_items),
            "blueprints_seen": len(blueprints),
            "products_written": len(artifacts),
            "products_with_failures": sum(1 for item in artifacts if item["failures"]),
            "blueprint_matched": sum(1 for item in artifacts if item["match_summary"]["blueprint_match_status"] == "matched"),
            "blueprint_missing": sum(1 for item in artifacts if item["match_summary"]["blueprint_match_status"] == "missing"),
            "blueprint_ambiguous": sum(1 for item in artifacts if item["match_summary"]["blueprint_match_status"] == "ambiguous"),
        },
        "artifacts": artifacts,
        "failures": failures,
        "index_path": str(index_path.resolve()),
    }
    write_json(index_path, index)
    return index


def list_website_items(client: "SiteClient", *, include_unpublished: bool) -> list[dict[str, Any]]:
    filters: list[Any] = []
    if not include_unpublished:
        filters.append(["published", "=", 1])
    return api_list(
        client,
        "Website Item",
        filters=filters,
        fields=[
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
    )


def list_blueprints(client: "SiteClient") -> list[dict[str, Any]]:
    return api_list(
        client,
        "LT Product Blueprint",
        filters=[],
        fields=[
            "name",
            "product_name",
            "product_slug",
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
    )


def build_product_artifact(
    client: "SiteClient",
    website_row: dict[str, Any],
    *,
    blueprint_index: dict[str, dict[str, list[dict[str, Any]]]],
    host: str,
    generated_at: str,
    include_public_get: bool,
    failures: list[str],
) -> dict[str, Any]:
    product_failures: list[str] = []
    website_name = str(website_row.get("name") or "")
    item_code = str(website_row.get("item_code") or "")
    route = normalize_route(website_row.get("route"))
    route_slug = route.rsplit("/", 1)[-1] if route else ""

    website_item = fetch_doc(client, "Website Item", website_name, "website_item", product_failures) if website_name else {}
    if website_item:
        item_code = str(website_item.get("item_code") or item_code)
        route = normalize_route(website_item.get("route")) or route
        route_slug = route.rsplit("/", 1)[-1] if route else route_slug

    blueprint_match = match_blueprint(
        blueprint_index,
        website_item_name=website_name,
        item_code=item_code,
        route_slug=route_slug,
    )
    product_failures.extend(blueprint_match["failures"])
    blueprint = {}
    if blueprint_match["status"] == "matched":
        blueprint = fetch_doc(
            client,
            "LT Product Blueprint",
            blueprint_match["name"],
            "blueprint",
            product_failures,
        )

    template_item = fetch_doc(client, "Item", item_code, "template_item", product_failures) if item_code else {}
    variants = (
        safe_api_list(
            client,
            "Item",
            filters=[["variant_of", "=", item_code]],
            fields=[
                "name",
                "item_code",
                "item_name",
                "variant_of",
                "disabled",
                "is_sales_item",
                "is_stock_item",
                "image",
                "modified",
                "modified_by",
                "owner",
            ],
            label=f"variant list for {item_code}",
            failures=product_failures,
        )
        if item_code
        else []
    )
    item_codes = [code for code in [item_code, *[str(row.get("item_code") or "") for row in variants]] if code]
    item_prices = item_price_rows_for_codes(client, item_codes, failures=product_failures) if item_codes else []

    public_summary: dict[str, Any]
    if include_public_get and route:
        public_summary = public_get_summary(client, route)
    else:
        public_summary = {"skipped": True, "reason": "not requested" if route else "missing route"}

    if not website_name:
        product_failures.append("Website Item row did not include name")
    if not item_code:
        product_failures.append(f"{website_name or '<unknown>'} has no linked item_code")
    if not route:
        product_failures.append(f"{website_name or item_code or '<unknown>'} has no public route")
    product_failures.append(
        "brand lane is not proved by current Website Item/Product Setup fields; mutation must stay blocked"
    )
    failures.extend(f"{website_name or item_code or '<unknown>'}: {failure}" for failure in product_failures)

    return {
        "generated_at": generated_at,
        "scope": "live authenticated read-only site API plus optional public GET; no writes/cache/deploy",
        "host": host,
        "site_name": env_required("FRAPPE_CLOUD_SITE_NAME"),
        "user_context": "site session obtained from Frappe Cloud API; sid redacted and not stored",
        "readonly_contract": readonly_contract(public_get=include_public_get),
        "product_identifier": {
            "website_item": website_name or None,
            "item_code": item_code or None,
            "route": route,
            "route_slug": route_slug or None,
            "brand_lane": None,
            "brand_lane_status": "not_proved",
            "product_setup": blueprint.get("name") or blueprint_match.get("name"),
            "product_name": first_present(
                blueprint,
                ("product_name", "item_name", "title"),
            )
            or first_present(website_item, ("web_item_name", "item_name", "title")),
        },
        "match_summary": {
            "blueprint_match_status": blueprint_match["status"],
            "blueprint_match_basis": blueprint_match["basis"],
            "candidate_blueprints": blueprint_match["candidates"],
        },
        "blueprint_summary": pick(
            blueprint,
            [
                "name",
                "product_name",
                "product_slug",
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
            "blueprint_add_on_rows": len(blueprint.get("add_on_rows") or []),
            "blueprint_conditional_price_rows": len(blueprint.get("conditional_price_rows") or []),
            "blueprint_content_rule_rows": len(blueprint.get("content_rule_rows") or []),
            "blueprint_media_rule_rows": len(blueprint.get("media_rule_rows") or []),
            "blueprint_color_recipe_rows": len(blueprint.get("color_recipe_rows") or []),
            "blueprint_gallery_rows": len(blueprint.get("gallery_image_rows") or []),
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
        "public_summary": public_summary,
        "rows": {
            "website_item": website_item,
            "blueprint": blueprint,
            "template_item": template_item,
            "blueprint_price_rows": blueprint.get("price_rows") or [],
            "blueprint_option_rows": blueprint.get("option_rows") or [],
            "blueprint_add_on_rows": blueprint.get("add_on_rows") or [],
            "blueprint_color_recipe_rows": blueprint.get("color_recipe_rows") or [],
            "blueprint_conditional_price_rows": blueprint.get("conditional_price_rows") or [],
            "blueprint_content_rule_rows": blueprint.get("content_rule_rows") or [],
            "blueprint_media_rule_rows": blueprint.get("media_rule_rows") or [],
            "blueprint_gallery_rows": blueprint.get("gallery_image_rows") or [],
            "variants": variants,
            "item_prices": item_prices,
        },
        "failures": product_failures,
    }


def build_blueprint_index(blueprints: list[dict[str, Any]]) -> dict[str, dict[str, list[dict[str, Any]]]]:
    index = {
        "target_website_item": {},
        "target_item_code": {},
        "product_slug": {},
        "name": {},
    }
    for row in blueprints:
        for key in index:
            value = normalize_key(row.get(key))
            if value:
                index[key].setdefault(value, []).append(row)
    return index


def match_blueprint(
    index: dict[str, dict[str, list[dict[str, Any]]]],
    *,
    website_item_name: str,
    item_code: str,
    route_slug: str,
) -> dict[str, Any]:
    attempts = [
        ("target_website_item", normalize_key(website_item_name)),
        ("target_item_code", normalize_key(item_code)),
        ("product_slug", normalize_key(route_slug)),
        ("product_slug", normalize_key(item_code)),
        ("name", normalize_key(item_code)),
        ("name", normalize_key(route_slug)),
    ]
    seen_attempts: set[tuple[str, str]] = set()
    all_candidates: dict[str, dict[str, Any]] = {}
    matched_basis: list[str] = []
    for basis, key in attempts:
        if not key or (basis, key) in seen_attempts:
            continue
        seen_attempts.add((basis, key))
        candidates = index.get(basis, {}).get(key, [])
        if candidates:
            matched_basis.append(f"{basis}={key}")
        for candidate in candidates:
            name = str(candidate.get("name") or "")
            if name:
                all_candidates[name] = candidate

    active_candidates = {
        name: candidate for name, candidate in all_candidates.items() if active_blueprint(candidate)
    }
    candidate_pool = active_candidates or all_candidates
    if len(candidate_pool) == 1:
        name, candidate = next(iter(candidate_pool.items()))
        return {
            "status": "matched",
            "basis": ", ".join(matched_basis) if matched_basis else None,
            "name": name,
            "candidates": summarize_candidates([candidate]),
            "failures": [] if active_candidates else [f"matched Product Setup {name} is not in an active authority status"],
        }
    if len(candidate_pool) > 1:
        return {
            "status": "ambiguous",
            "basis": ", ".join(matched_basis) if matched_basis else None,
            "name": None,
            "candidates": summarize_candidates(list(candidate_pool.values())),
            "failures": [
                "ambiguous LT Product Blueprint authority; more than one active or plausible Product Setup matched target website item, item code, slug, or name"
            ],
        }
    return {
        "status": "missing",
        "basis": None,
        "name": None,
        "candidates": [],
        "failures": ["no LT Product Blueprint matched Website Item by target_website_item, item_code, product_slug, or name"],
    }


def active_blueprint(row: dict[str, Any]) -> bool:
    return str(row.get("publish_status") or "").strip() in ACTIVE_BLUEPRINT_STATUSES


def summarize_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        pick(
            candidate,
            [
                "name",
                "product_slug",
                "target_item_code",
                "target_website_item",
                "publish_status",
                "shop_visibility",
                "modified",
                "modified_by",
            ],
        )
        for candidate in candidates
    ]


class SiteClient:
    def __init__(self, host: str, sid: str, *, timeout: float) -> None:
        self.host = host.rstrip("/")
        self.sid = sid
        self.timeout = timeout

    def get_json(self, path: str) -> dict[str, Any]:
        result = self._get(path, accept="application/json")
        if "json" not in result:
            raise CatalogAuditBlocked(
                f"{summarize_path(path)} did not return JSON "
                f"(status={result.get('status')}, content_type={result.get('content_type')})"
            )
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
        raise CatalogAuditBlocked(f"{doctype} list did not return a list")
    return data


def safe_api_list(
    client: SiteClient,
    doctype: str,
    *,
    filters: list[Any],
    fields: list[str],
    label: str,
    failures: list[str],
) -> list[dict[str, Any]]:
    try:
        return api_list(client, doctype, filters=filters, fields=fields)
    except CatalogAuditBlocked as exc:
        failures.append(f"{label} fetch failed: {exc}")
        return []


def item_price_rows_for_codes(client: SiteClient, item_codes: list[str], *, failures: list[str]) -> list[dict[str, Any]]:
    fields = [
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
        "owner",
    ]
    rows: list[dict[str, Any]] = []
    for chunk in chunks(item_codes, 20):
        rows.extend(
            safe_api_list(
                client,
                "Item Price",
                filters=[["item_code", "in", chunk], ["selling", "=", 1]],
                fields=fields,
                label=f"Item Price list for {len(chunk)} item code(s)",
                failures=failures,
            )
        )
    return rows


def chunks(values: list[str], size: int) -> list[list[str]]:
    return [values[index : index + size] for index in range(0, len(values), size)]


def fetch_doc(client: SiteClient, doctype: str, name: str, label: str, failures: list[str]) -> dict[str, Any]:
    try:
        payload = client.get_json(f"/api/resource/{quote_path(doctype)}/{quote_path(name)}")
    except CatalogAuditBlocked as exc:
        failures.append(f"{label} fetch failed for {doctype} {name}: {exc}")
        return {}
    data = payload.get("data")
    if isinstance(data, dict):
        return data
    message = payload.get("message")
    if isinstance(message, dict):
        return message
    failures.append(f"{label} fetch returned no document data for {doctype} {name}")
    return {}


def public_get_summary(client: SiteClient, route: str) -> dict[str, Any]:
    result = client.get_text(route)
    html = result.pop("_body_text", "")
    return {
        **result,
        "route": route,
        "price_strings": sorted(set(re.findall(r"\$\s?\d+(?:\.\d{2})?", html))),
        "contains_add_to_cart": "add-to-cart" in html.lower() or "add to cart" in html.lower(),
        "contains_quote": "quote" in html.lower(),
    }


def frappe_cloud_site_session(*, reason: str, timeout: float) -> str:
    params = {"name": env_required("FRAPPE_CLOUD_SITE_NAME"), "reason": reason}
    payload = frappe_cloud_get("/api/method/press.api.site.login", params, timeout=timeout)
    sid = (payload.get("message") or {}).get("sid") if isinstance(payload.get("message"), dict) else payload.get("sid")
    if not sid:
        raise CatalogAuditBlocked("Frappe Cloud site login did not return a site session")
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
        raise CatalogAuditBlocked(f"Frappe Cloud GET {endpoint} failed with HTTP {exc.code}: {body[:300]}") from exc


def readonly_contract(*, public_get: bool) -> dict[str, str]:
    return {
        "frappe_cloud": "GET site login only",
        "erpnext_site": "GET /api/resource only",
        "public_route_get": "enabled" if public_get else "skipped",
        "erpnext_writes": "blocked",
        "cache_clear": "blocked",
        "deploy": "blocked",
        "payment_provider": "blocked",
    }


def content_fields(doc: dict[str, Any]) -> dict[str, Any]:
    markers = ("about", "description", "story", "detail", "copy", "content", "subtitle", "intro", "seo")
    return {
        key: value
        for key, value in doc.items()
        if any(marker in key.lower() for marker in markers) and not isinstance(value, (list, dict))
    }


def pick(doc: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    return {field: doc.get(field) for field in fields if field in doc}


def first_present(doc: dict[str, Any], fields: tuple[str, ...]) -> Any:
    for field in fields:
        value = doc.get(field)
        if value not in (None, ""):
            return value
    return None


def float_values(rows: list[dict[str, Any]], key: str) -> set[float]:
    values: set[float] = set()
    for row in rows:
        value = row.get(key)
        if value in (None, ""):
            continue
        try:
            values.add(float(value))
        except (TypeError, ValueError):
            continue
    return values


def normalize_route(value: Any) -> str | None:
    if value in (None, ""):
        return None
    route = str(value).strip()
    if not route:
        return None
    return route if route.startswith("/") else f"/{route}"


def normalize_key(value: Any) -> str:
    if value in (None, ""):
        return ""
    return str(value).strip().strip("/").lower()


def quote_path(value: str) -> str:
    return urllib.parse.quote(value, safe="")


def summarize_path(path: str) -> str:
    parsed = urllib.parse.urlparse(path)
    query_length = len(parsed.query or "")
    return f"{parsed.path or path} query_bytes={query_length}"


def artifact_filename(position: int, artifact: dict[str, Any]) -> str:
    identifier = artifact.get("product_identifier") or {}
    stem = (
        identifier.get("item_code")
        or identifier.get("route_slug")
        or identifier.get("website_item")
        or f"product-{position:03d}"
    )
    return f"{position:03d}-{slugify(str(stem))}.json"


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip()).strip("-._").lower()
    return slug or "product"


def env_required(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise CatalogAuditBlocked(f"missing required environment variable: {name}")
    return value


def load_env_file(path: Path) -> None:
    if not path.exists():
        raise CatalogAuditBlocked(f"env file does not exist: {path}")
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
        raise CatalogAuditBlocked(f"invalid HTTP base URL: {value!r}")


def validate_local_output_dir(path: str) -> None:
    output = Path(path).expanduser()
    if output.exists() and not output.is_dir():
        raise CatalogAuditBlocked(f"output dir path exists and is not a directory: {output}")
    parent = output.resolve().parent
    if not parent.exists():
        raise CatalogAuditBlocked(f"output dir parent does not exist: {parent}")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
