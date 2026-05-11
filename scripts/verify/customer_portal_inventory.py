#!/usr/bin/env python3
"""Inventory LT login, guest checkout, and portal-menu boundaries.

This is a read-only pre-build check. It fails on hard account/commerce boundary
drift and reports default ERPNext portal routes that still need LT translation.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"

CURRENT_CUSTOMER_ROUTE_KEEPERS = {
    "/account/quotes",
    "/account/events",
    "/account/billing",
    "/account/files",
    "/account/checklist",
    "/account/repeat",
    "/account/follow-up",
    "/organization",
}
CURRENT_CUSTOMER_ROUTE_RENAME_OR_HIDE = {
    "/quotations",
    "/orders",
    "/invoices",
    "/addresses",
    "/project",
    "/shipments",
    "/issues",
    "/timesheets",
    "/material-requests",
}
SUPPLIER_ROUTE_CANDIDATES = {
    "/rfq",
    "/supplier-quotations",
    "/purchase-orders",
    "/purchase-invoices",
}
EXPECTED_CUSTOMER_MENU = {
    "/account/quotes": {
        "title": "Quotes",
        "reference_doctype": "Quotation",
    },
    "/account/events": {
        "title": "Event Details",
        "reference_doctype": "Sales Order",
    },
    "/account/billing": {
        "title": "Invoices & Receipts",
        "reference_doctype": "Sales Invoice",
    },
    "/account/files": {
        "title": "Files & Inspiration",
        "reference_doctype": "File",
    },
    "/account/checklist": {
        "title": "Customer Checklist",
        "reference_doctype": "LT Customer Checklist Response",
    },
    "/account/repeat": {
        "title": "Repeat Client",
        "reference_doctype": "LT Customer Change Request",
    },
    "/account/follow-up": {
        "title": "After-Event Follow-Up",
        "reference_doctype": "LT Customer Change Request",
    },
    "/organization": {
        "title": "Organization Portal",
        "reference_doctype": "LT Organization Portal Membership",
    },
}
PUBLIC_OR_STOCK_ROUTES_TO_HIDE = {
    "/newsletters",
    *CURRENT_CUSTOMER_ROUTE_RENAME_OR_HIDE,
}


def bench_execute(method: str, *, kwargs: dict[str, Any] | None = None) -> Any:
    cmd = [
        "docker",
        "exec",
        CONTAINER,
        "bench",
        "--site",
        SITE,
        "execute",
        method,
    ]
    if kwargs is not None:
        cmd.extend(["--kwargs", json.dumps(kwargs)])

    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=60)
    if proc.returncode != 0:
        raise RuntimeError(
            f"bench execute failed for {method}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    text = proc.stdout.strip()
    return json.loads(text) if text else None


def get_doc(doctype: str) -> dict[str, Any]:
    return bench_execute(
        "frappe.client.get",
        kwargs={"doctype": doctype, "name": doctype},
    )


def get_count(doctype: str, filters: dict[str, Any]) -> int:
    value = bench_execute(
        "frappe.client.get_count",
        kwargs={"doctype": doctype, "filters": filters},
    )
    return int(value or 0)


def http_status(base_url: str, path: str) -> int:
    req = urllib.request.Request(
        base_url.rstrip("/") + path,
        headers={"User-Agent": "LT customer portal inventory"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return int(response.status)
    except urllib.error.HTTPError as exc:
        return int(exc.code)


def menu_rows(portal: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in portal.get("menu") or []:
        rows.append(
            {
                "idx": row.get("idx"),
                "title": row.get("title"),
                "route": row.get("route"),
                "role": row.get("role"),
                "enabled": row.get("enabled"),
                "reference_doctype": row.get("reference_doctype"),
            }
        )
    return rows


def classify_customer_routes(menu: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    customer = [
        row
        for row in menu
        if row.get("enabled") and row.get("role") == "Customer" and row.get("route")
    ]
    keepers = [row for row in customer if row["route"] in CURRENT_CUSTOMER_ROUTE_KEEPERS]
    needs_translation = [
        row for row in customer if row["route"] in CURRENT_CUSTOMER_ROUTE_RENAME_OR_HIDE
    ]
    unknown = [
        row
        for row in customer
        if row["route"] not in CURRENT_CUSTOMER_ROUTE_KEEPERS
        and row["route"] not in CURRENT_CUSTOMER_ROUTE_RENAME_OR_HIDE
    ]
    return {
        "customer_candidate_routes": keepers,
        "customer_routes_needing_translation": needs_translation,
        "customer_unknown_routes": unknown,
    }


def strict_menu_failures(portal: dict[str, Any], menu: list[dict[str, Any]]) -> list[str]:
    failures = []
    active_by_route = {
        row.get("route"): row
        for row in menu
        if row.get("enabled") and row.get("route")
    }

    if portal.get("default_portal_home") != "me":
        failures.append("Portal Settings.default_portal_home should be 'me' for the LT account home")
    if portal.get("default_role"):
        failures.append("Portal Settings.default_role should stay empty; public signup remains disabled")

    for route, expected in EXPECTED_CUSTOMER_MENU.items():
        row = active_by_route.get(route)
        if not row:
            failures.append(f"Missing enabled customer portal route {route}")
            continue
        if row.get("role") != "Customer":
            failures.append(f"{route} should be Customer-only, found role {row.get('role')!r}")
        for key, value in expected.items():
            if row.get(key) != value:
                failures.append(f"{route} {key} expected {value!r}, found {row.get(key)!r}")

    for route in sorted(PUBLIC_OR_STOCK_ROUTES_TO_HIDE):
        row = active_by_route.get(route)
        if row:
            failures.append(f"{route} should be hidden from the portal menu, found enabled as {row.get('title')!r}")

    for route in sorted(SUPPLIER_ROUTE_CANDIDATES):
        row = active_by_route.get(route)
        if row and row.get("role") != "Supplier":
            failures.append(f"{route} should remain Supplier-only, found role {row.get('role')!r}")

    return failures


def run(base_url: str, *, strict_menu: bool = False) -> dict[str, Any]:
    website = get_doc("Website Settings")
    webshop = get_doc("Webshop Settings")
    portal = get_doc("Portal Settings")
    system = get_doc("System Settings")

    menu = menu_rows(portal)
    classified = classify_customer_routes(menu)
    supplier_candidates = [
        row
        for row in menu
        if row.get("enabled")
        and row.get("role") == "Supplier"
        and row.get("route") in SUPPLIER_ROUTE_CANDIDATES
    ]

    failures: list[str] = []
    warnings: list[str] = []

    login_status = http_status(base_url, "/login")
    me_status = http_status(base_url, "/me")
    if login_status != 200:
        failures.append(f"/login expected HTTP 200, found {login_status}")
    if me_status not in {401, 403, 302}:
        failures.append(f"/me should not be readable as a guest, found HTTP {me_status}")

    if int(website.get("disable_signup") or 0) != 1:
        failures.append("Website Settings.disable_signup must stay enabled for invite-only customer access")
    if int(website.get("hide_login") or 0) != 0:
        failures.append("Website Settings.hide_login must stay off while account links remain visible")

    if int(webshop.get("login_required_to_view_products") or 0) != 0:
        failures.append("Webshop Settings.login_required_to_view_products must stay off for guest shopping")
    if int(webshop.get("hide_price_for_guest") or 0) != 0:
        failures.append("Webshop Settings.hide_price_for_guest must stay off for public pricing")
    if int(webshop.get("enable_checkout") or 0) != 1:
        failures.append("Webshop Settings.enable_checkout must stay on for current ecommerce testing")

    if classified["customer_routes_needing_translation"]:
        warnings.append("Customer portal still exposes stock ERPNext routes that need LT translation or hiding")
    if supplier_candidates:
        warnings.append("Supplier portal routes exist and should stay separate from the customer/client portal")
    if not portal.get("default_portal_home"):
        warnings.append("Portal Settings.default_portal_home is not set; portal home is still native/default")
    if strict_menu:
        failures.extend(strict_menu_failures(portal, menu))

    return {
        "status": "fail" if failures else "pass",
        "hard_failures": failures,
        "warnings": warnings,
        "http": {
            "login": login_status,
            "me_guest": me_status,
        },
        "settings": {
            "website": {
                "disable_signup": website.get("disable_signup"),
                "hide_login": website.get("hide_login"),
                "show_footer_on_login": website.get("show_footer_on_login"),
            },
            "system": {
                "disable_user_pass_login": system.get("disable_user_pass_login"),
                "login_with_email_link": system.get("login_with_email_link"),
                "allow_login_using_mobile_number": system.get("allow_login_using_mobile_number"),
                "enable_two_factor_auth": system.get("enable_two_factor_auth"),
            },
            "webshop": {
                "enabled": webshop.get("enabled"),
                "enable_checkout": webshop.get("enable_checkout"),
                "login_required_to_view_products": webshop.get("login_required_to_view_products"),
                "hide_price_for_guest": webshop.get("hide_price_for_guest"),
                "enable_wishlist": webshop.get("enable_wishlist"),
                "enable_reviews": webshop.get("enable_reviews"),
            },
            "portal": {
                "default_role": portal.get("default_role"),
                "default_portal_home": portal.get("default_portal_home"),
                "hide_standard_menu": portal.get("hide_standard_menu"),
            },
        },
        "portal_menu": menu,
        "route_classification": {
            **classified,
            "supplier_portal_candidates": supplier_candidates,
        },
        "role_counts": {
            "Customer": get_count("Has Role", {"role": "Customer"}),
            "Supplier": get_count("Has Role", {"role": "Supplier"}),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:8081")
    parser.add_argument("--report", type=Path)
    parser.add_argument(
        "--strict-menu",
        action="store_true",
        help="Fail unless the LT customer/client portal menu has been translated.",
    )
    args = parser.parse_args()

    result = run(args.base_url, strict_menu=args.strict_menu)
    rendered = json.dumps(result, indent=2, sort_keys=True)
    print(rendered)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered + "\n", encoding="utf-8")
    return 1 if result["hard_failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
