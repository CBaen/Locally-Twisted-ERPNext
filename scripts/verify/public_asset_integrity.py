#!/usr/bin/env python3
"""Verify public pages do not reference missing or wrong-MIME static assets."""
from __future__ import annotations

import re
import sys
import argparse
import os
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urljoin, urlparse, urlunparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[2]
LAYOUT_HELPERS = ROOT / "scripts" / "verify" / "layout_helpers.js"
BASE_URL = "http://localhost:8081"
EXTRA_ROUTES = (
    "/shop-items",
    "/shop-items/arches",
    "/shop-items/bouquets",
    "/shop-items/garlands",
    "/shop-items/columns",
    "/shop-items/seasonal-specialty",
    "/shop-items/arches/easter-balloon-arch-bunny-ear",
    "/shop-items/bouquets/unicorn-bouquet",
)
ROUTE_PATH_RE = re.compile(r"path:\s*\"([^\"]+)\"")
LINK_HEADER_RE = re.compile(r"<([^>]+)>")
CSS_URL_RE = re.compile(
    r"url\(\s*(?P<quote>['\"]?)(?P<url>.*?)(?P=quote)\s*\)",
    re.IGNORECASE,
)
CSS_IMPORT_RE = re.compile(
    r"@import\s+(?:url\(\s*)?(?P<quote>['\"])(?P<url>.*?)(?P=quote)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class AssetRef:
    route: str
    url: str
    expected_type: str | None
    source: str


class AssetParser(HTMLParser):
    def __init__(self, route: str) -> None:
        super().__init__()
        self.route = route
        self.assets: list[AssetRef] = []
        self.raw_space_refs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = dict(attrs)
        if tag == "link" and data.get("href"):
            rel = (data.get("rel") or "").lower()
            as_value = (data.get("as") or "").lower()
            if "stylesheet" in rel or as_value in {"style", "font"}:
                self._add(data["href"] or "", expected_type_for(data["href"] or "", as_value or rel), "html link")
        elif tag == "script" and data.get("src"):
            self._add(data["src"] or "", "javascript", "html script")
        elif tag == "img" and data.get("src"):
            self._add(data["src"] or "", "image", "html image")

    def _add(self, url: str, expected_type: str | None, source: str) -> None:
        if " " in url:
            self.raw_space_refs.append(url)
        self.assets.append(AssetRef(self.route, url, expected_type, source))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(__doc__ or "").strip(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("LT_BASE_URL", BASE_URL),
        help="Public site base URL. Defaults to LT_BASE_URL or http://localhost:8081.",
    )
    return parser.parse_args()


def public_routes() -> list[str]:
    routes: list[str] = []
    if LAYOUT_HELPERS.exists():
        text = LAYOUT_HELPERS.read_text(encoding="utf-8")
        routes.extend(match.group(1) for match in ROUTE_PATH_RE.finditer(text))
    routes.extend(EXTRA_ROUTES)
    return sorted(set(routes), key=lambda route: (route.count("/"), route))


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    return urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            quote(parsed.path, safe="/%"),
            parsed.params,
            quote(parsed.query, safe="=&?/%"),
            parsed.fragment,
        )
    )


def request(url: str) -> tuple[int, dict[str, str], str]:
    try:
        with urlopen(
            Request(normalize_url(url), headers={"User-Agent": "LT public asset integrity verifier"}),
            timeout=20,
        ) as response:
            body = response.read(700_000).decode("utf-8", "replace")
            return response.status, dict(response.headers), body
    except HTTPError as error:
        body = error.read(2_000).decode("utf-8", "replace")
        return error.code, dict(error.headers), body
    except (OSError, URLError, ValueError) as error:
        return 0, {}, str(error)


def expected_type_for(url: str, hint: str = "") -> str | None:
    path = urlparse(url).path.lower()
    if hint == "script" or path.endswith(".js"):
        return "javascript"
    if hint in {"style", "stylesheet"} or path.endswith(".css"):
        return "css"
    if hint == "font" or path.endswith((".woff", ".woff2", ".ttf", ".otf")):
        return "font"
    if path.endswith((".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".ico")):
        return "image"
    return None


def content_type_matches(content_type: str, expected_type: str | None) -> bool:
    if expected_type is None:
        return True
    content_type = content_type.lower()
    if expected_type == "css":
        return "text/css" in content_type
    if expected_type == "javascript":
        return "javascript" in content_type or "ecmascript" in content_type
    if expected_type == "image":
        return content_type.startswith("image/")
    if expected_type == "font":
        return (
            content_type.startswith("font/")
            or "application/font" in content_type
            or "application/octet-stream" in content_type
        )
    return True


def link_header_assets(route: str, header: str) -> list[AssetRef]:
    refs: list[AssetRef] = []
    for match in LINK_HEADER_RE.finditer(header or ""):
        url = match.group(1)
        expected_type = expected_type_for(url)
        if "/assets/" in url or url.startswith("/website_script.js"):
            refs.append(AssetRef(route, url, expected_type, "link preload header"))
    return refs


def css_dependency_assets(route: str, css_url: str, css_body: str) -> list[AssetRef]:
    refs: list[AssetRef] = []
    for pattern in (CSS_URL_RE, CSS_IMPORT_RE):
        for match in pattern.finditer(css_body):
            url = (match.group("url") or "").strip()
            if not url or url.startswith(("#", "data:", "about:")):
                continue
            refs.append(
                AssetRef(
                    route,
                    urljoin(css_url, url),
                    expected_type_for(url),
                    f"css dependency in {urlparse(css_url).path}",
                )
            )
    return refs


def is_local_url(base_url: str, url: str) -> bool:
    base = urlparse(base_url)
    parsed = urlparse(urljoin(base_url.rstrip("/") + "/", url))
    return parsed.netloc == base.netloc


def main() -> int:
    args = parse_args()

    base_url = args.base_url.rstrip("/")
    failures: list[str] = []
    raw_space_refs: list[str] = []
    seen_assets: dict[str, tuple[int, str, str | None, str]] = {}
    scanned_css_assets: set[str] = set()
    routes = public_routes()

    for route in routes:
        page_url = urljoin(base_url.rstrip("/") + "/", route.lstrip("/"))
        status, headers, body = request(page_url)
        if status >= 400 or status == 0:
            failures.append(f"{route}: page returned HTTP {status}")
            continue

        parser = AssetParser(route)
        parser.feed(body)
        raw_space_refs.extend(f"{route}: {ref}" for ref in parser.raw_space_refs)

        refs: list[AssetRef] = [
            *link_header_assets(route, headers.get("Link", "")),
            *parser.assets,
        ]

        while refs:
            ref = refs.pop(0)
            if " " in ref.url:
                raw_space_refs.append(f"{route}: {ref.url}")
            absolute_url = urljoin(base_url.rstrip("/") + "/", ref.url.lstrip("/"))
            if not is_local_url(base_url, absolute_url):
                continue
            if absolute_url not in seen_assets:
                asset_status, asset_headers, _asset_body = request(absolute_url)
                content_type = asset_headers.get("Content-Type", "")
                seen_assets[absolute_url] = (asset_status, content_type, ref.expected_type, _asset_body)
            else:
                asset_status, content_type, _expected, _asset_body = seen_assets[absolute_url]
            if asset_status >= 400 or asset_status == 0:
                failures.append(f"{route}: {ref.source} {ref.url} returned HTTP {asset_status}")
            elif not content_type_matches(content_type, ref.expected_type):
                failures.append(
                    f"{route}: {ref.source} {ref.url} returned {content_type!r}, "
                    f"expected {ref.expected_type or 'any'}"
                )
            elif ref.expected_type == "css" and absolute_url not in scanned_css_assets:
                scanned_css_assets.add(absolute_url)
                refs.extend(css_dependency_assets(route, absolute_url, _asset_body))

    if raw_space_refs:
        print("[PUBLIC ASSET INTEGRITY] FAIL raw spaces in asset URLs")
        for ref in raw_space_refs[:40]:
            print(f"  - {ref}")
        if len(raw_space_refs) > 40:
            print(f"  - ... {len(raw_space_refs) - 40} more")
        failures.append(f"{len(raw_space_refs)} asset URL(s) contain raw spaces")

    if failures:
        print("[PUBLIC ASSET INTEGRITY] FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print(
        "[PUBLIC ASSET INTEGRITY] PASS "
        f"({len(routes)} routes, {len(seen_assets)} unique local asset URLs)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
