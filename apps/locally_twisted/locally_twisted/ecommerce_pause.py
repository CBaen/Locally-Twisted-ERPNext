"""Temporary public ecommerce pause for launch."""
from __future__ import annotations

from urllib.parse import quote, urlparse

import frappe
from werkzeug.exceptions import HTTPException
from werkzeug.utils import redirect


ECOMMERCE_PAUSED_DEFAULT = True
ECOMMERCE_PAUSED = ECOMMERCE_PAUSED_DEFAULT
SHOP_DISCOVERY_OPEN_DEFAULT = False
CHECKOUT_PAUSED_DEFAULT = True
PAUSE_ROUTE = "/ready-to-order-paused"
LIVE_SHOP_DISCOVERY_HOSTS = {"locallytwisted.com", "www.locallytwisted.com"}

SHOP_DISCOVERY_PUBLIC_PATHS = (
    "/shop",
    "/shop-items",
    "/shop-by-category",
    "/all-products",
    "/products",
)

CHECKOUT_PUBLIC_PATHS = (
    "/cart",
    "/checkout",
)

ECOMMERCE_DISCOVERY_PATHS = SHOP_DISCOVERY_PUBLIC_PATHS + CHECKOUT_PUBLIC_PATHS + (PAUSE_ROUTE,)


def _as_bool(value: object) -> bool:
    if isinstance(value, str):
        return value.strip().lower() not in {"0", "false", "no", "off", "open"}
    return bool(value)


def _request_host() -> str:
    request = getattr(getattr(frappe, "local", None), "request", None)
    if not request:
        return ""

    host = str(getattr(request, "host", "") or "").strip().lower()
    if not host and getattr(request, "host_url", None):
        host = urlparse(str(request.host_url)).netloc.lower()
    if ":" in host:
        host = host.split(":", 1)[0]
    return host


def is_ecommerce_paused() -> bool:
    """Return the current public commerce gate.

    The safe default is paused. Local launch testing can open the lanes with
    `bench --site frontend set-config lt_ecommerce_paused 0`.
    """
    return _as_bool(frappe.conf.get("lt_ecommerce_paused", ECOMMERCE_PAUSED_DEFAULT))


def is_shop_discovery_open() -> bool:
    """Allow shop/category/product browsing without opening checkout."""
    if not is_ecommerce_paused():
        return True
    configured = frappe.conf.get("lt_shop_discovery_open", None)
    if configured is not None:
        return _as_bool(configured)
    # Live-only fallback for release mode when Frappe Cloud has not exposed the new config key yet.
    if _request_host() in LIVE_SHOP_DISCOVERY_HOSTS:
        return True
    return SHOP_DISCOVERY_OPEN_DEFAULT


def is_checkout_paused() -> bool:
    """Return whether cart, checkout pages, and checkout APIs are blocked."""
    if is_ecommerce_paused():
        return True
    configured = frappe.conf.get("lt_checkout_paused", None)
    if configured is not None:
        return _as_bool(configured)
    return False


def normalize_path(path: str | None) -> str:
    normalized = "/" + str(path or "").strip("/")
    return "/" if normalized == "/" else normalized.rstrip("/")


def _matches_path(path: str | None, roots: tuple[str, ...]) -> bool:
    normalized = normalize_path(path)
    return any(
        normalized == root or normalized.startswith(f"{root}/")
        for root in roots
    )


def is_shop_discovery_path(path: str | None) -> bool:
    return _matches_path(path, SHOP_DISCOVERY_PUBLIC_PATHS)


def is_checkout_path(path: str | None) -> bool:
    return _matches_path(path, CHECKOUT_PUBLIC_PATHS)


def is_blocked_public_path(path: str | None) -> bool:
    if is_checkout_path(path):
        return is_checkout_paused()
    if is_shop_discovery_path(path):
        return not is_shop_discovery_open()
    return False


def is_ecommerce_discovery_path(path: str | None) -> bool:
    return _matches_path(path, ECOMMERCE_DISCOVERY_PATHS)


def before_request() -> None:
    """Send public ecommerce traffic to the branded pause page.

    Logged-in operators can still open direct ecommerce URLs for repair work.
    Guests get a clear launch-safe message instead of unstable product, cart,
    or checkout surfaces.
    """
    if not is_ecommerce_paused() and not is_checkout_paused():
        return
    if frappe.session.user != "Guest":
        return

    request = getattr(frappe.local, "request", None)
    if not request:
        return

    path = normalize_path(getattr(request, "path", ""))
    if path == PAUSE_ROUTE or not is_blocked_public_path(path):
        return

    query_string = getattr(request, "query_string", b"") or b""
    if isinstance(query_string, bytes):
        query_string = query_string.decode("utf-8", errors="ignore")
    source = f"{path}?{query_string}" if query_string else path
    raise HTTPException(response=redirect(f"{PAUSE_ROUTE}?from={quote(source, safe='')}", code=302))
