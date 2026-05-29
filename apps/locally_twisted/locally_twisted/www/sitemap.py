"""Canonical sitemap for the public Locally Twisted site."""

from urllib.parse import quote

from frappe.utils import nowdate
from frappe.website.router import get_pages
from frappe.www.sitemap import get_public_pages_from_doctypes

from locally_twisted.ecommerce_pause import (
    PAUSE_ROUTE,
    is_checkout_path,
    is_shop_discovery_open,
    is_shop_discovery_path,
)
from locally_twisted.seo import absolute_url, canonical_path, normalize_path


no_cache = 1
base_template_path = "www/sitemap.xml"


def _sitemap_url(path: str) -> str:
    canonical = normalize_path(path)
    if canonical == "/":
        return absolute_url("/")
    return absolute_url(quote(canonical.lstrip("/").encode("utf-8")))


def _add_link(links: list[dict[str, str]], seen: set[str], path: str, lastmod: str) -> None:
    canonical = canonical_path(path)
    if canonical == PAUSE_ROUTE:
        return
    if is_checkout_path(canonical):
        return
    if is_shop_discovery_path(canonical) and not is_shop_discovery_open():
        return
    loc = _sitemap_url(canonical)
    if loc in seen:
        return
    seen.add(loc)
    links.append({"loc": loc, "lastmod": lastmod})


def get_context(context):
    links = []
    seen = set()

    for _route, page in get_pages().items():
        if not page.sitemap:
            continue
        _add_link(links, seen, page.name, nowdate())

    for route, data in get_public_pages_from_doctypes().items():
        _add_link(links, seen, route or "", f"{data['modified']:%Y-%m-%d}")

    return {"links": links}
