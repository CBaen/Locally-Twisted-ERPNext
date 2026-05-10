#!/usr/bin/env python3
"""Verify that public ecommerce is paused for launch.

This is a temporary launch contract: customer-facing shop, product, cart, and
checkout routes must land on the branded pause page, while public navigation
must not advertise Ready-to-Order or cart entry points.
"""
from __future__ import annotations

import os
import json
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin, urlparse
from urllib.request import Request, urlopen

from _cli import parse_noop_args


ROOT = Path(__file__).resolve().parents[2]
BASE_URL = os.environ.get("LT_BASE_URL", "http://localhost:8081").rstrip("/")
CONTAINER = os.environ.get("LT_FRAPPE_BACKEND_CONTAINER", "locally-twisted-erpnext-v15-backend-1")
SITE = os.environ.get("LT_FRAPPE_SITE", "frontend")
PAUSE_PATH = "/ready-to-order-paused"

NAVBAR = ROOT / "apps/locally_twisted/locally_twisted/templates/includes/navbar/navbar.html"
FOOTER = ROOT / "apps/locally_twisted/locally_twisted/templates/includes/footer/footer.html"
EVENT_BALLOONS = ROOT / "apps/locally_twisted/locally_twisted/www/event_balloons.html"
CHECKOUT_SOURCE = ROOT / "apps/locally_twisted/locally_twisted/www/checkout.py"

BLOCKED_ROUTES = (
    "/shop",
    "/shop?q=arches",
    "/shop-items",
    "/shop-items/arches",
    "/shop-items/bouquets/unicorn-bouquet",
    "/shop-by-category",
    "/all-products",
    "/cart",
    "/checkout",
    "/checkout?item=mothers-day-bouquet&qty=1",
)
CHECKOUT_API_METHODS = (
    "preview_checkout_totals",
    "submit_guest_order",
)
MUTATION_DOCTYPES = (
    "Customer",
    "Contact",
    "Address",
    "Sales Order",
    "Payment Request",
)
OPTIONAL_MUTATION_DOCTYPES = (
    "Stripe Session",
)


def fail(message: str) -> None:
    raise AssertionError(message)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def assert_source_hidden() -> None:
    navbar = read(NAVBAR)
    footer = read(FOOTER)
    event_balloons = read(EVENT_BALLOONS)

    nav_forbidden = (
        "Ready-to-Order",
        'href="/shop"',
        "/shop-items",
        'href="/cart"',
        "Shopping cart",
        "data-lt-search-product-entry",
    )
    for needle in nav_forbidden:
        if needle in navbar:
            fail(f"navbar still exposes ecommerce surface: {needle}")

    footer_forbidden = ("Ready-to-Order", 'href="/shop"', "/shop-items")
    for needle in footer_forbidden:
        if needle in footer:
            fail(f"footer still exposes ecommerce surface: {needle}")

    if 'href="/shop"' in event_balloons:
        fail("event balloons CTA still points customers to /shop")

    if 'action="/shop"' in navbar:
        fail("search form still submits to /shop")


def get_final(route: str) -> tuple[int, str, str]:
    url = urljoin(BASE_URL + "/", route.lstrip("/"))
    request = Request(url, headers={"User-Agent": "LT ecommerce pause verifier"})
    with urlopen(request, timeout=20) as response:
        body = response.read().decode("utf-8", errors="replace")
        return response.status, response.geturl(), body


def bench_execute(method: str, *, args: list | None = None, kwargs: dict | None = None) -> object:
    command = [
        "docker",
        "exec",
        CONTAINER,
        "bench",
        "--site",
        SITE,
        "execute",
        method,
    ]
    if args is not None:
        command.extend(["--args", json.dumps(args)])
    if kwargs is not None:
        command.extend(["--kwargs", json.dumps(kwargs)])

    proc = subprocess.run(command, text=True, capture_output=True, timeout=60)
    if proc.returncode != 0:
        fail(
            f"bench execute failed for {method}\n"
            f"STDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    text = proc.stdout.strip()
    return json.loads(text) if text else None


def get_count(doctype: str) -> int:
    return int(bench_execute("frappe.client.get_count", kwargs={"doctype": doctype}) or 0)


def doctype_exists(doctype: str) -> bool:
    return bool(bench_execute("frappe.db.exists", args=["DocType", doctype]))


def mutation_counts() -> dict[str, int]:
    doctypes = list(MUTATION_DOCTYPES)
    doctypes.extend(doctype for doctype in OPTIONAL_MUTATION_DOCTYPES if doctype_exists(doctype))
    return {doctype: get_count(doctype) for doctype in doctypes}


def assert_checkout_api_guard_order() -> None:
    checkout = read(CHECKOUT_SOURCE)
    if "def _assert_checkout_api_open" not in checkout:
        fail("checkout.py is missing the paused ecommerce API guard helper")

    preview_def = checkout.find("def preview_checkout_totals")
    preview_guard = checkout.find('_assert_checkout_api_open("preview_checkout_totals")', preview_def)
    preview_resolver = checkout.find("cart_items = _resolve_cart_items", preview_def)
    if not (preview_def != -1 and preview_def < preview_guard < preview_resolver):
        fail("preview_checkout_totals must check ecommerce pause before resolving cart items")

    submit_def = checkout.find("def submit_guest_order")
    submit_guard = checkout.find('_assert_checkout_api_open("submit_guest_order")', submit_def)
    mutation_markers = (
        'frappe.get_doc({\n            "doctype": "Customer"',
        'frappe.get_doc({\n            "doctype": "Contact"',
        'frappe.get_doc({\n            "doctype": "Address"',
        'frappe.get_doc(so_doc)',
        'frappe.get_doc({\n        "doctype": "Payment Request"',
        "create_session_for_sales_order(",
    )
    mutation_positions = [
        position
        for marker in mutation_markers
        if (position := checkout.find(marker, submit_def)) != -1
    ]
    if not mutation_positions:
        fail("checkout.py source guard verifier could not locate checkout mutation markers")
    if not (submit_def != -1 and submit_def < submit_guard < min(mutation_positions)):
        fail("submit_guest_order must check ecommerce pause before purchase, order, payment, or Stripe work")


def assert_routes_paused() -> None:
    for route in BLOCKED_ROUTES:
        status, final_url, body = get_final(route)
        final_path = urlparse(final_url).path.rstrip("/")
        if status >= 400:
            fail(f"{route} returned HTTP {status}")
        if final_path != PAUSE_PATH:
            fail(f"{route} should land on {PAUSE_PATH}, landed on {final_url}")
        if "Ready-to-order is paused" not in body:
            fail(f"{route} did not render the branded pause message")
        if "Start a custom event quote" not in body:
            fail(f"{route} did not render the contact fallback")


def post_checkout_api(method: str) -> dict[str, object]:
    endpoint = f"{BASE_URL}/api/method/locally_twisted.www.checkout.{method}"
    nonce = int(time.time() * 1000)
    payload = {
        "item_code": f"lt-paused-api-contract-{nonce}",
        "qty": "1",
        "name": "LT Paused Checkout Probe",
        "email": f"lt-paused-checkout-probe-{nonce}@example.invalid",
        "phone": "555-0100",
        "fulfillment_method": "pickup",
        "pickup_location": "Locally Twisted",
        "requested_fulfillment_date": "2099-01-01",
        "requested_window_start": "10:00",
        "requested_window_end": "12:00",
    }
    body = urlencode(payload).encode("utf-8")
    request = Request(
        endpoint,
        data=body,
        method="POST",
        headers={
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "LT ecommerce pause API verifier",
            "X-Frappe-CSRF-Token": "token",
            "X-Requested-With": "XMLHttpRequest",
        },
    )
    try:
        with urlopen(request, timeout=20) as response:
            raw = response.read().decode("utf-8", errors="replace")
            return {"method": method, "status": response.status, "raw": raw}
    except HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        return {"method": method, "status": exc.code, "raw": raw}
    except URLError as exc:
        fail(f"{method} request failed before reaching Frappe: {exc.reason}")


def assert_direct_checkout_apis_blocked() -> None:
    before = mutation_counts()
    results = [post_checkout_api(method) for method in CHECKOUT_API_METHODS]
    after = mutation_counts()

    changed = {
        doctype: {"before": before[doctype], "after": after[doctype]}
        for doctype in MUTATION_DOCTYPES
        if before[doctype] != after[doctype]
    }
    if changed:
        fail(f"paused direct checkout API changed purchase/order record counts: {changed}")

    for result in results:
        method = result["method"]
        status = int(result["status"])
        raw = str(result["raw"])
        if status < 400 or status >= 500:
            fail(f"{method} should return a customer-safe 4xx pause error, returned HTTP {status}")
        if "Ready-to-order is paused" not in raw:
            fail(f"{method} did not return the paused checkout message")
        if "Please start a custom event quote" not in raw:
            fail(f"{method} did not point the customer back to the inquiry path")


def main() -> int:
    parse_noop_args(__doc__)
    assert_source_hidden()
    assert_checkout_api_guard_order()
    assert_routes_paused()
    assert_direct_checkout_apis_blocked()
    print("Ecommerce pause contract passed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"[ECOMMERCE PAUSE] FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
