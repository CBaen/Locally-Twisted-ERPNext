#!/usr/bin/env python3
"""Fail-loud Frappe Cloud staging owner-review readiness gate.

This gate intentionally checks the target Frappe Cloud site, not the local
Docker database. A successful GitHub push or Frappe Cloud deploy is not enough:
the owner-review site must contain the catalog and review accounts.
"""
from __future__ import annotations

import argparse
import http.cookiejar
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_SITE = "locallytwisted-staging.frappe.cloud"
DEFAULT_TEAM = "5b8acl3gba"
DEFAULT_CREDENTIALS = Path(r"C:\Users\baenb\Desktop\vs key\LT Frappe API.txt")
PRESS_API = "https://cloud.frappe.io/api/method"
CONFIRMATION = "seed locally twisted staging owner review"
EXPECTED_APP_ORDER = ["frappe", "erpnext", "payments", "webshop", "locally_twisted"]
REQUIRED_USERS = {
    "locallytwisted@gmail.com": {"LT Owner Access", "System Manager"},
    "marketing@exploringnotboring.com": {"LT Marketing Review Access"},
}
MIN_COUNTS = {
    "Website Item": 50,
    "Item": 10000,
    "Item Price": 10000,
    "LT Product Blueprint": 50,
    "Website Slideshow": 1,
    "Website Slideshow Item": 1,
}
OWNER_VISIBLE_ROUTES = (
    "/app",
    "/shop",
    "/shop-items",
    "/shop-items/bouquets/mickey-mouse-bouquet",
    "/shop-items/columns",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", default=DEFAULT_SITE)
    parser.add_argument("--team", default=DEFAULT_TEAM)
    parser.add_argument("--credentials", type=Path, default=DEFAULT_CREDENTIALS)
    parser.add_argument("--expected-hash", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
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
    elif (bootstrap_status or {}).get("status", {}).get("state") not in {"success", None}:
        failures.append(f"bootstrap status is not success: {bootstrap_status}")
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

    return {
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
    return {
        "path": path,
        "status": status,
        "final_url": final_url,
        "title": extract_title(body),
        "login_page": "login_email" in body or "redirect-to" in final_url or "<title>Sign In" in body,
    }


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
