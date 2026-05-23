#!/usr/bin/env python3
"""Fail-loud Frappe Cloud staging owner-review readiness gate.

This gate intentionally checks the target Frappe Cloud site, not the local
Docker database. A successful GitHub push or Frappe Cloud deploy is not enough:
the owner-review site must contain the catalog and review accounts.
"""
from __future__ import annotations

import argparse
import copy
import http.cookiejar
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_SITE = "locallytwisted-staging.frappe.cloud"
DEFAULT_TEAM = "5b8acl3gba"
DEFAULT_CREDENTIALS = Path(r"C:\Users\baenb\Desktop\vs key\LT Frappe API.txt")
DEFAULT_APP_MIRROR = "https://github.com/CBaen/Locally-Twisted-Frappe-App.git"
PRESS_API = "https://cloud.frappe.io/api/method"
CONFIRMATION = "seed locally twisted staging owner review"
EXPECTED_APP_ORDER = ["frappe", "erpnext", "payments", "webshop", "locally_twisted"]
REQUIRED_USERS = {
    "locallytwisted@gmail.com": {"LT Owner Access", "System Manager"},
    "marketing@exploringnotboring.com": {"LT Marketing Review Access"},
}
MIN_COUNTS = {
    "Website Item": 51,
    "Item": 10685,
    "Item Price": 10666,
    "LT Product Blueprint": 51,
    "Website Slideshow": 47,
    "Website Slideshow Item": 68,
}
OWNER_VISIBLE_ROUTES = (
    "/app",
    "/shop",
    "/shop-items",
    "/shop-items/bouquets/mickey-mouse-bouquet",
    "/shop-items/arches/classic-arch",
    "/shop-items/garlands/large-garland",
    "/shop-items/columns",
)
EXPECTED_GALLERY_THUMBNAILS = {
    "/shop-items/bouquets/mickey-mouse-bouquet": {
        "exact": 3,
        "required_paths": {
            "/files/mickey-mouse-bouquet.png",
            "/files/mickey-mouse-bouquet-large.webp",
        },
    },
    "/shop-items/arches/classic-arch": {
        "minimum": 12,
        "required_paths": {
            "/files/classic-arch.png",
        },
    },
    "/shop-items/garlands/large-garland": {
        "minimum": 2,
        "required_paths": {
            "/files/large-garland.png",
        },
    },
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", default=DEFAULT_SITE)
    parser.add_argument("--team", default=DEFAULT_TEAM)
    parser.add_argument("--credentials", type=Path, default=DEFAULT_CREDENTIALS)
    parser.add_argument("--expected-hash", default=os.environ.get("LT_EXPECTED_APP_HASH"))
    parser.add_argument("--expected-hash-from-mirror", action="store_true")
    parser.add_argument("--mirror-url", default=DEFAULT_APP_MIRROR)
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--release-artifact",
        action="store_true",
        help="Sanitize JSON output for release-packet evidence; requires --json.",
    )
    args = parser.parse_args()
    if args.release_artifact and not args.json:
        parser.error("--release-artifact requires --json")

    try:
        if args.expected_hash_from_mirror:
            args.expected_hash = resolve_mirror_head(args.mirror_url)
        if not args.expected_hash:
            raise RuntimeError(
                "expected app hash is required; pass --expected-hash, set LT_EXPECTED_APP_HASH, "
                "or use --expected-hash-from-mirror"
            )
        args.expected_hash = normalize_expected_hash(args.expected_hash)
        result = run_gate(args)
    except Exception as exc:
        print("[STAGING OWNER REVIEW GATE] FAIL")
        print(f"  - gate crashed: {type(exc).__name__}: {exc}")
        return 1

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("[STAGING OWNER REVIEW GATE] " + ("PASS" if result["ok"] else "FAIL"))
        print(f"  site: {result['site']['name']} status={result['site']['status']}")
        app = result["locally_twisted_app"]
        print(f"  app: {app.get('hash')} {app.get('commit_message')}")
        print(f"  counts: {result['counts']}")
        print(f"  users: {', '.join(sorted(result['accounts']))}")
        print(f"  owner-visible routes: {len(result['owner_visible_routes'])}")
    if result["failures"]:
        if args.json:
            return 1
        print("  failures:")
        for failure in result["failures"]:
            print(f"    - {failure}")
        return 1
    return 0


def run_gate(args: argparse.Namespace) -> dict[str, Any]:
    press = PressClient(args.credentials, args.team)
    site = press.get("press.api.site.get", {"name": args.site})["message"]
    apps = press.get("press.api.site.installed_apps", {"name": args.site})["message"]
    config_rows = press.get("press.api.site.site_config", {"name": args.site})["message"]
    config = {row.get("key"): row.get("value") for row in config_rows}
    session = staging_session(press, args.site)

    counts = {doctype: stage_get_count(args.site, session, doctype) for doctype in MIN_COUNTS}
    accounts = {
        email: stage_get_user(args.site, session, email)
        for email in REQUIRED_USERS
    }
    routes = [fetch_route(args.site, session, path) for path in OWNER_VISIBLE_ROUTES]
    try:
        bootstrap_status = stage_method(
            args.site,
            session,
            "locally_twisted.staging_owner_review_bootstrap.get_staging_owner_review_bootstrap_status",
            {"confirm": CONFIRMATION},
        ).get("message")
    except urllib.error.HTTPError as exc:
        bootstrap_status = {"unavailable": True, "status_code": exc.code}

    lt_app = next((app for app in apps if app.get("app") == "locally_twisted"), {})
    failures: list[str] = []
    if site.get("status") != "Active":
        failures.append(f"staging site is not Active: {site.get('status')}")
    app_order = [app.get("app") for app in apps]
    if app_order != EXPECTED_APP_ORDER:
        failures.append(f"installed app order drifted: {app_order}")
    if lt_app.get("hash") != args.expected_hash:
        failures.append(f"locally_twisted hash {lt_app.get('hash')} != expected {args.expected_hash}")
    if str(config.get("lt_ecommerce_paused")) not in {"1", "true", "True"}:
        failures.append("lt_ecommerce_paused is not enabled on staging")
    if str(config.get("lt_public_indexing_enabled")) not in {"0", "false", "False"}:
        failures.append("lt_public_indexing_enabled is not disabled on staging")
    if (bootstrap_status or {}).get("unavailable"):
        failures.append("staging bootstrap status method is not available on the target app")
    else:
        status_payload = (bootstrap_status or {}).get("status", {})
        if status_payload.get("state") != "success":
            failures.append(
                "bootstrap status is not success: "
                f"{summarize_bootstrap_status_for_failure(bootstrap_status)}"
            )
        if status_payload.get("expected_app_hash") != args.expected_hash:
            failures.append(
                "bootstrap status is not bound to the deployed app hash: "
                f"{status_payload.get('expected_app_hash')} != {args.expected_hash}"
            )
    for doctype, minimum in MIN_COUNTS.items():
        value = counts.get(doctype)
        if not isinstance(value, int) or value < minimum:
            failures.append(f"{doctype} count {value!r} is below required minimum {minimum}")
    for email, required_roles in REQUIRED_USERS.items():
        user = accounts.get(email) or {}
        if not user.get("exists"):
            failures.append(f"required staging user missing: {email}")
            continue
        if not user.get("enabled"):
            failures.append(f"required staging user disabled: {email}")
        missing_roles = sorted(required_roles - set(user.get("roles") or []))
        if missing_roles:
            failures.append(f"{email} missing roles: {missing_roles}")
    for route in routes:
        if route["status"] != 200:
            failures.append(f"{route['path']} returned {route['status']}")
        if route["login_page"]:
            failures.append(f"{route['path']} resolved to a login page for authenticated owner/admin proof")
        if route["path"].startswith("/shop") and "paused" in route["final_url"]:
            failures.append(f"{route['path']} still resolves to paused page for authenticated owner/admin proof")
    product_routes = {route["path"]: route for route in routes}
    for path, contract in EXPECTED_GALLERY_THUMBNAILS.items():
        route = product_routes.get(path) or {}
        if route.get("status") != 200:
            continue
        thumbnail_paths = route.get("thumbnail_paths") or []
        unique_paths = sorted(set(thumbnail_paths))
        if not route.get("has_gallery_shell"):
            failures.append(f"{path} did not render the product gallery thumbnail shell")
        if "exact" in contract and len(unique_paths) != contract["exact"]:
            failures.append(
                f"{path} staging gallery should expose exactly {contract['exact']} unique thumbnails; "
                f"found {len(unique_paths)}: {unique_paths}"
            )
        if "minimum" in contract and len(unique_paths) < contract["minimum"]:
            failures.append(
                f"{path} staging gallery should expose at least {contract['minimum']} unique thumbnails; "
                f"found {len(unique_paths)}: {unique_paths}"
            )
        missing_paths = sorted(set(contract["required_paths"]) - set(unique_paths))
        if missing_paths:
            failures.append(f"{path} staging gallery is missing required thumbnail paths: {missing_paths}")
    category_route = product_routes.get("/shop-items/columns") or {}
    if category_route.get("status") == 200 and not category_route.get("looks_like_category"):
        failures.append("/shop-items/columns did not render like a shop category page")

    result = {
        "ok": not failures,
        "failures": failures,
        "site": {"name": site.get("name"), "status": site.get("status"), "group": site.get("group")},
        "locally_twisted_app": {
            "hash": lt_app.get("hash"),
            "commit_message": lt_app.get("commit_message"),
            "branch": lt_app.get("branch"),
            "repository": lt_app.get("repository"),
        },
        "app_order": app_order,
        "config": {
            "lt_ecommerce_paused": config.get("lt_ecommerce_paused"),
            "lt_public_indexing_enabled": config.get("lt_public_indexing_enabled"),
        },
        "counts": counts,
        "accounts": accounts,
        "owner_visible_routes": routes,
        "bootstrap_status": bootstrap_status,
    }
    if getattr(args, "release_artifact", False):
        return build_release_artifact_result(result)
    return result


RAW_BOOTSTRAP_DETAIL_KEYS = {
    "_server_messages",
    "body",
    "body_excerpt",
    "exc",
    "exc_info",
    "raw_body",
    "response_body",
    "server_messages",
    "traceback",
    "traceback_tail",
    "traceback_text",
}


def build_release_artifact_result(result: dict[str, Any]) -> dict[str, Any]:
    """Return release-packet-safe owner-review gate evidence.

    The normal gate result can contain historical bootstrap diagnostics from
    the target site. Release packets need the state/count/hash/user/route
    evidence without raw traceback or HTTP body text.
    """
    safe = copy.deepcopy(result)
    bootstrap_status, omitted_count = sanitize_bootstrap_status(
        safe.get("bootstrap_status")
    )
    safe["bootstrap_status"] = bootstrap_status
    safe["release_artifact"] = {
        "kind": "staging_owner_review_gate",
        "sanitized": True,
        "raw_diagnostic_details_omitted": bool(omitted_count),
        "raw_diagnostic_detail_count": omitted_count,
    }
    safe["failures"] = [
        compact_release_text(failure, limit=900)
        for failure in safe.get("failures", [])
    ]
    return safe


def sanitize_bootstrap_status(value: Any) -> tuple[Any, int]:
    omitted_count = 0

    def walk(node: Any) -> Any:
        nonlocal omitted_count
        if isinstance(node, dict):
            safe_node: dict[str, Any] = {}
            for key, child in node.items():
                if is_raw_bootstrap_detail_key(str(key)):
                    omitted_count += 1
                    continue
                safe_node[key] = walk(child)
            return safe_node
        if isinstance(node, list):
            return [walk(child) for child in node]
        if isinstance(node, str):
            return compact_release_text(node)
        return node

    safe_value = walk(value)
    if omitted_count and isinstance(safe_value, dict):
        safe_value["raw_diagnostic_details_omitted"] = True
        safe_value["raw_diagnostic_detail_count"] = omitted_count
    return safe_value, omitted_count


def is_raw_bootstrap_detail_key(key: str) -> bool:
    lower = key.strip().lower()
    return (
        lower in RAW_BOOTSTRAP_DETAIL_KEYS
        or "traceback" in lower
        or lower.endswith("_body")
    )


def summarize_bootstrap_status_for_failure(bootstrap_status: Any) -> str:
    if not isinstance(bootstrap_status, dict):
        return "missing bootstrap status payload"
    status_payload = bootstrap_status.get("status")
    if not isinstance(status_payload, dict):
        return "missing bootstrap status.status payload"
    summary: dict[str, Any] = {}
    for key in ("state", "error", "expected_app_hash", "target_site", "site", "updated_at"):
        if key in status_payload:
            value = status_payload.get(key)
            summary[key] = compact_release_text(value) if isinstance(value, str) else value
    for key in ("counts", "pre_counts", "post_counts"):
        value = status_payload.get(key)
        if isinstance(value, dict):
            summary[key] = value
    if not summary:
        return "bootstrap status.status did not include state or summary fields"
    return json.dumps(summary, sort_keys=True)


def compact_release_text(value: Any, *, limit: int = 700) -> str:
    text = " ".join(str(value).replace("\r", "\n").split())
    lower = text.lower()
    if (
        "traceback (most recent call last)" in lower
        or "/home/frappe/frappe-bench/apps/" in lower
        or "\\apps\\frappe\\" in lower
    ):
        return "raw diagnostic text omitted from release artifact"
    redacted = re.sub(
        r"(?i)\b(api[_-]?key|api[_-]?secret|authorization|cookie|password|secret|session[_-]?id|sid|token)\b"
        r"\s*[:=]\s*['\"]?[^'\"\s,;}]+",
        lambda match: f"{match.group(1)}=[REDACTED]",
        text,
    )
    if len(redacted) > limit:
        return redacted[: limit - 3].rstrip() + "..."
    return redacted


class PressClient:
    def __init__(self, credentials: Path, team: str) -> None:
        lines = [line.strip() for line in credentials.read_text(encoding="utf-8").splitlines() if line.strip()]
        if len(lines) < 4:
            raise RuntimeError(f"credential file shape is not recognized: {credentials}")
        token = f"Token {lines[1]}:{lines[3]}"
        self.headers = {"Authorization": token, "X-Press-Team": team, "Accept": "application/json"}

    def get(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        url = f"{PRESS_API}/{method}?{urllib.parse.urlencode(params)}"
        return request_json(url, headers=self.headers)

    def post_json(self, method: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        headers = {**self.headers, "Content-Type": "application/json"}
        return request_json(f"{PRESS_API}/{method}", data=body, headers=headers)


def staging_session(press: PressClient, site: str) -> urllib.request.OpenerDirector:
    login = press.post_json("press.api.site.login", {"name": site, "reason": "Codex staging owner-review gate"})
    sid = (login.get("message") or {}).get("sid")
    if not sid:
        raise RuntimeError("Frappe Cloud did not return a staging SID")
    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
    opener.open(f"https://{site}/app?sid={urllib.parse.quote(str(sid))}", timeout=60).read()
    return opener


def stage_get_count(site: str, opener: urllib.request.OpenerDirector, doctype: str) -> int | str:
    try:
        return stage_method(site, opener, "frappe.client.get_count", {"doctype": doctype}).get("message")
    except Exception as exc:
        return f"ERROR: {type(exc).__name__}: {exc}"


def stage_get_user(site: str, opener: urllib.request.OpenerDirector, email: str) -> dict[str, Any]:
    try:
        doc = stage_method(site, opener, "frappe.client.get", {"doctype": "User", "name": email}).get("message")
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return {"exists": False, "enabled": 0, "roles": []}
        raise
    roles = [row.get("role") for row in (doc or {}).get("roles", []) if row.get("role")]
    return {
        "exists": True,
        "enabled": int((doc or {}).get("enabled") or 0),
        "user_type": (doc or {}).get("user_type"),
        "roles": roles,
    }


def stage_method(
    site: str,
    opener: urllib.request.OpenerDirector,
    method: str,
    params: dict[str, Any],
) -> dict[str, Any]:
    url = f"https://{site}/api/method/{method}?{urllib.parse.urlencode(params)}"
    return request_json(url, opener=opener, headers={"Accept": "application/json"})


def fetch_route(site: str, opener: urllib.request.OpenerDirector, path: str) -> dict[str, Any]:
    url = f"https://{site}{path}"
    try:
        with opener.open(url, timeout=60) as response:
            body = response.read().decode("utf-8", errors="replace")
            final_url = response.geturl()
            status = response.status
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        final_url = exc.geturl()
        status = exc.code
    thumbnail_paths = extract_gallery_thumbnail_paths(body)
    return {
        "path": path,
        "status": status,
        "final_url": final_url,
        "title": extract_title(body),
        "login_page": "login_email" in body or "redirect-to" in final_url or "<title>Sign In" in body,
        "has_gallery_shell": "lt-product__media-shell has-thumbnails" in body
        or "lt-product__media-shell  has-thumbnails" in body,
        "thumbnail_count": len(set(thumbnail_paths)),
        "thumbnail_paths": thumbnail_paths,
        "looks_like_category": "product-card" in body or "lt-shop" in body or "item-card" in body,
    }


def resolve_mirror_head(mirror_url: str) -> str:
    result = subprocess.run(
        ["git", "ls-remote", mirror_url, "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    head = result.stdout.strip().split()[0] if result.stdout.strip() else ""
    if len(head) != 40:
        raise RuntimeError(f"could not resolve app mirror HEAD from {mirror_url!r}")
    return head


def normalize_expected_hash(value: str) -> str:
    expected_hash = str(value).strip().lower()
    if len(expected_hash) != 40 or any(char not in "0123456789abcdef" for char in expected_hash):
        raise RuntimeError(f"expected app hash must be a full 40-character hex commit hash: {value!r}")
    return expected_hash


def extract_gallery_thumbnail_paths(body: str) -> list[str]:
    button_pattern = re.compile(
        r"<button\b(?=[^>]*\bclass=[\"'][^\"']*\blt-product__thumbnail-button\b)[^>]*>(.*?)</button>",
        re.IGNORECASE | re.DOTALL,
    )
    img_pattern = re.compile(r"<img\b[^>]*\bsrc=[\"']([^\"']+)[\"']", re.IGNORECASE)
    paths: list[str] = []
    for button_html in button_pattern.findall(body):
        match = img_pattern.search(button_html)
        if not match:
            continue
        paths.append(normalize_asset_path(match.group(1)))
    return paths


def normalize_asset_path(src: str) -> str:
    parsed = urllib.parse.urlsplit(src)
    return parsed.path or src


def extract_title(body: str) -> str:
    lower = body.lower()
    start = lower.find("<title>")
    end = lower.find("</title>")
    if start == -1 or end == -1 or end <= start:
        return ""
    return " ".join(body[start + 7 : end].split())


def request_json(
    url: str,
    *,
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
    opener: urllib.request.OpenerDirector | None = None,
) -> dict[str, Any]:
    req = urllib.request.Request(url, data=data, headers=headers or {})
    open_fn = opener.open if opener else urllib.request.urlopen
    with open_fn(req, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


if __name__ == "__main__":
    sys.exit(main())
