"""Canonical sitemap for the public Locally Twisted site."""

from urllib.parse import quote

from frappe.utils import nowdate
from frappe.website.router import get_pages
from frappe.www.sitemap import get_public_pages_from_doctypes

from locally_twisted.ecommerce_pause import is_ecommerce_discovery_path, is_ecommerce_paused
from locally_twisted.seo import absolute_url, canonical_path, normalize_path


no_cache = 1
base_template_path = "www/sitemap.xml"

PUBLIC_ECOMMERCE_ALIAS_PATHS = (
    "/shop-items/seasonal-specialty",
)


def _sitemap_url(path: str) -> str:
    canonical = normalize_path(path)
    if canonical == "/":
        return absolute_url("/")
    return absolute_url(quote(canonical.lstrip("/").encode("utf-8")))


def _add_link(links: list[dict[str, str]], seen: set[str], path: str, lastmod: str) -> None:
    canonical = canonical_path(path)
    if is_ecommerce_paused() and is_ecommerce_discovery_path(canonical):
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

    for path in PUBLIC_ECOMMERCE_ALIAS_PATHS:
        _add_link(links, seen, path, nowdate())

    return {"links": links}
