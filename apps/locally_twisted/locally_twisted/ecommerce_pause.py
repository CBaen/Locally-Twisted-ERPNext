"""Temporary public ecommerce pause for launch."""
from __future__ import annotations

from urllib.parse import quote

import frappe
from werkzeug.exceptions import HTTPException
from werkzeug.utils import redirect


ECOMMERCE_PAUSED = True
PAUSE_ROUTE = "/ready-to-order-paused"

BLOCKED_PUBLIC_PATHS = (
    "/shop",
    "/shop-items",
    "/shop-by-category",
    "/all-products",
    "/cart",
    "/checkout",
)


def is_ecommerce_paused() -> bool:
    return ECOMMERCE_PAUSED


def normalize_path(path: str | None) -> str:
    normalized = "/" + str(path or "").strip("/")
    return "/" if normalized == "/" else normalized.rstrip("/")


def is_blocked_public_path(path: str | None) -> bool:
    normalized = normalize_path(path)
    return any(
        normalized == blocked or normalized.startswith(f"{blocked}/")
        for blocked in BLOCKED_PUBLIC_PATHS
    )


def before_request() -> None:
    """Send public ecommerce traffic to the branded pause page.

    Logged-in operators can still open direct ecommerce URLs for repair work.
    Guests get a clear launch-safe message instead of unstable product, cart,
    or checkout surfaces.
    """
    if not is_ecommerce_paused():
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
