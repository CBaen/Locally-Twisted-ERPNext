#!/usr/bin/env python3
"""Verify approved product gallery media projects into Frappe-native slideshows.

Run:
  python scripts/verify/product_gallery_projection_contract.py
"""
from __future__ import annotations

import json
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from _cli import parse_noop_args


CONTAINER = "locally-twisted-erpnext-v15-backend-1"
SITE = "frontend"
ROOT = Path(__file__).resolve().parents[2]
BASE_URL = os.environ.get("LT_BASE_URL", "http://localhost:8081").rstrip("/")


class ContractFail(Exception):
    pass


def main() -> int:
    parse_noop_args(__doc__)
    failures = _contract_failures()
    print("[PRODUCT GALLERY PROJECTION CONTRACT] " + ("PASS" if not failures else "FAIL"))
    if failures:
        print("  failures:")
        for failure in failures:
            print(f"    - {failure}")
    return 0 if not failures else 1


def _contract_failures() -> list[str]:
    sys.path.insert(0, str(ROOT / "apps" / "locally_twisted"))

    from locally_twisted.catalog_contract.gallery_media import canonical_gallery_sources
    from locally_twisted.catalog_contract.source_builder import build_product_page_contract

    products = _products()
    images_dir = ROOT / "_resources/catalog-source/images"
    contracts = [build_product_page_contract(product) for product in products]
    expected_by_slug = {
        str(product.get("slug") or ""): [
            source.file_url for source in canonical_gallery_sources(product, images_dir) if source.file_url
        ]
        for product, contract in zip(products, contracts)
        if any(image.role == "gallery" for image in contract.gallery)
    }
    expected_by_slug = {slug: rows for slug, rows in expected_by_slug.items() if rows}

    failures: list[str] = []
    approved_gallery_count = sum(len(rows) for rows in expected_by_slug.values())
    if approved_gallery_count <= 0:
        failures.append("source contract approved zero product gallery images")
        return failures

    website_items = {
        row["item_code"]: row
        for row in get_all(
            "Website Item",
            fields=["name", "item_code", "route", "slideshow", "website_image"],
            limit_page_length=0,
        )
        if row.get("item_code")
    }
    blueprints = {
        row["product_slug"]: row
        for row in get_all(
            "LT Product Blueprint",
            fields=["name", "product_slug", "target_item_code", "target_website_item"],
            limit_page_length=0,
        )
        if row.get("product_slug")
    }
    linked_slideshows = {row.get("slideshow") for row in website_items.values() if row.get("slideshow")}

    slideshow_rows = get_all(
        "Website Slideshow Item",
        fields=["parent", "image"],
        order_by="idx asc",
        limit_page_length=0,
    )
    slideshow_images: dict[str, list[str]] = {}
    for row in slideshow_rows:
        slideshow_images.setdefault(str(row.get("parent") or ""), []).append(str(row.get("image") or ""))

    orphan_slideshows = [
        row["name"]
        for row in get_all("Website Slideshow", fields=["name"], limit_page_length=0)
        if str(row.get("name") or "").startswith("LT Product Gallery -")
        and row.get("name") not in linked_slideshows
    ]
    if orphan_slideshows:
        failures.append("orphan LT Product Gallery slideshow(s): " + ", ".join(orphan_slideshows[:10]))

    ecommerce_paused = bool(bench_execute("locally_twisted.ecommerce_pause.is_ecommerce_paused"))

    for slug, expected in expected_by_slug.items():
        website_item = website_items.get(slug)
        if not website_item:
            continue

        blueprint = blueprints.get(slug)
        if not blueprint:
            failures.append(f"{slug}: missing Product Setup blueprint for approved gallery media")
            continue

        gallery_rows = get_all(
            "LT Product Blueprint Gallery Image",
            filters={"parent": blueprint["name"]},
            fields=["image", "approved_for_customer"],
            order_by="idx asc",
            limit_page_length=0,
        )
        approved_rows = [row for row in gallery_rows if row.get("image") and int(row.get("approved_for_customer") or 0)]
        if len(approved_rows) < len(expected):
            failures.append(
                f"{slug}: Product Setup has {len(approved_rows)} approved gallery row(s), expected at least {len(expected)}"
            )

        images = [str(row.get("image") or "") for row in approved_rows]
        missing_setup = [image for image in expected if image not in images]
        if missing_setup:
            failures.append(f"{slug}: Product Setup missing gallery image(s): {', '.join(missing_setup[:5])}")
        duplicates = _duplicates(images)
        if duplicates:
            failures.append(f"{slug}: duplicate Product Setup gallery image(s): {', '.join(duplicates[:5])}")

        slideshow = website_item.get("slideshow")
        if not slideshow:
            failures.append(f"{slug}: Website Item has approved gallery media but no slideshow")
            continue

        slide_images = [image for image in slideshow_images.get(slideshow, []) if image]
        if len(slide_images) < len(expected):
            failures.append(f"{slug}: slideshow has {len(slide_images)} image(s), expected at least {len(expected)}")
        missing_slides = [image for image in expected if image not in slide_images]
        if missing_slides:
            failures.append(f"{slug}: Website Slideshow missing image(s): {', '.join(missing_slides[:5])}")
        slide_duplicates = _duplicates(slide_images)
        if slide_duplicates:
            failures.append(f"{slug}: duplicate Website Slideshow image(s): {', '.join(slide_duplicates[:5])}")
        if any(not image for image in slide_images):
            failures.append(f"{slug}: Website Slideshow includes an empty image row")
        if not ecommerce_paused:
            render_failure = _render_failure(slug, website_item, slide_images)
            if render_failure:
                failures.append(render_failure)

    if not ecommerce_paused:
        failures.extend(_all_product_gallery_render_failures(website_items, slideshow_images))

    return failures


def _all_product_gallery_render_failures(
    website_items: dict[str, dict[str, Any]],
    slideshow_images: dict[str, list[str]],
) -> list[str]:
    failures: list[str] = []
    for item_code, website_item in sorted(website_items.items()):
        route = str(website_item.get("route") or "").strip()
        if not route or not route.lstrip("/").startswith("shop-items/"):
            continue
        slide_images = [image for image in slideshow_images.get(str(website_item.get("slideshow") or ""), []) if image]
        failure = _render_architecture_failure(item_code, website_item, slide_images)
        if failure:
            failures.append(failure)
    return failures


def _render_architecture_failure(item_code: str, website_item: dict[str, Any], slide_images: list[str]) -> str | None:
    route = str(website_item.get("route") or "").strip()
    html = _get_route_html(route)
    expected_count = _unique_renderable_image_count([str(website_item.get("website_image") or ""), *slide_images])
    rail_count = _rendered_thumbnail_button_count(html)

    if expected_count < 2 and rail_count:
        return f"{item_code}: rendered a gallery rail for {expected_count} distinct product image(s)"
    if expected_count >= 2 and rail_count != expected_count:
        return f"{item_code}: rendered {rail_count} gallery thumbnail(s), expected {expected_count} distinct product image(s)"

    rendered_paths = _rendered_gallery_paths(html)
    duplicate_groups = _duplicate_content_groups(rendered_paths)
    if duplicate_groups:
        details = "; ".join(", ".join(group) for group in duplicate_groups[:5])
        return f"{item_code}: rendered duplicate image content under different URLs: {details}"
    return None


def _render_failure(slug: str, website_item: dict[str, Any], slide_images: list[str]) -> str | None:
    route = str(website_item.get("route") or "").strip()
    if not route:
        return f"{slug}: Website Item has slideshow but no route for rendered gallery proof"

    html = _get_route_html(route)
    rail_count = _rendered_thumbnail_button_count(html)
    expected_rendered = _unique_renderable_image_count([str(website_item.get("website_image") or ""), *slide_images])
    if expected_rendered < 2:
        return None
    if rail_count < expected_rendered:
        return (
            f"{slug}: product route renders {rail_count} thumbnail button(s), "
            f"expected at least {expected_rendered}"
        )
    if 'data-lt-gallery-role="standard-product-thumbnails"' not in html:
        return f"{slug}: product route rendered thumbnails without the LT gallery rail role"
    return None


def _rendered_gallery_paths(html: str) -> list[str]:
    paths = re.findall(r'<img[^>]+class="[^"]*\b(?:website-image|item-slideshow-image)\b[^"]*"[^>]+src="([^"]+)"', html)
    return _unique(paths)


def _rendered_thumbnail_button_count(html: str) -> int:
    return len(re.findall(r'<button[^>]+class="[^"]*\blt-product__thumbnail-button\b', html))


def _duplicate_content_groups(images: list[str]) -> list[list[str]]:
    by_key: dict[str, list[str]] = {}
    for image in _unique(images):
        key = _image_content_key(image)
        by_key.setdefault(key, []).append(image)
    return [paths for paths in by_key.values() if len(paths) > 1]


def _unique_renderable_image_count(images: list[str]) -> int:
    keys: set[str] = set()
    for image in _unique(images):
        keys.add(_image_content_key(image))
    return len(keys)


def _image_content_key(image: str) -> str:
    image = str(image or "").strip()
    if not image:
        return ""
    url = urljoin(BASE_URL + "/", image.lstrip("/"))
    request = Request(url, headers={"User-Agent": "LT product gallery projection verifier"})
    try:
        with urlopen(request, timeout=20) as response:
            digest = hashlib.sha256(response.read()).hexdigest()
            return f"sha256:{digest}"
    except (HTTPError, URLError):
        return f"url:{image}"


def _get_route_html(route: str) -> str:
    url = urljoin(BASE_URL + "/", route.lstrip("/"))
    request = Request(url, headers={"User-Agent": "LT product gallery projection verifier"})
    try:
        with urlopen(request, timeout=20) as response:
            return response.read().decode("utf-8", errors="replace")
    except HTTPError as exc:
        raise ContractFail(f"{route} returned HTTP {exc.code} during product gallery render proof") from exc
    except URLError as exc:
        raise ContractFail(f"{route} could not be fetched during product gallery render proof: {exc.reason}") from exc


def get_all(doctype: str, **kwargs: Any) -> list[dict[str, Any]]:
    return bench_execute("frappe.get_all", args=[doctype], kwargs=kwargs) or []


def bench_execute(
    method: str,
    *,
    args: list[Any] | None = None,
    kwargs: dict[str, Any] | None = None,
    timeout: int = 90,
) -> Any:
    cmd = ["docker", "exec", CONTAINER, "bench", "--site", SITE, "execute", method]
    if args is not None:
        cmd.extend(["--args", json.dumps(args)])
    if kwargs is not None:
        cmd.extend(["--kwargs", json.dumps(kwargs)])

    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
    if proc.returncode != 0:
        raise ContractFail(
            f"bench execute failed for {method}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    text = proc.stdout.strip()
    return json.loads(text) if text else None


def _products() -> list[dict[str, Any]]:
    data = json.loads((ROOT / "_resources/catalog-source/catalog.json").read_text(encoding="utf-8"))
    return list(data.get("products") if isinstance(data, dict) else data)


def _duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return duplicates


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        value = str(value or "").strip()
        if not value or value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


if __name__ == "__main__":
    sys.exit(main())
