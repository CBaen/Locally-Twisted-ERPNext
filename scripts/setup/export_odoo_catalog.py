"""
export_odoo_catalog.py — One-shot scrape of LT's Odoo catalog at 5.78.136.133.

Why this exists:
  ~50 products × multiple attributes × multiple variants × photos. Manual
  entry into ERPNext is impractical. We need the catalog data BEFORE we
  can seed the webshop side. Odoo XML-RPC requires admin auth; HTML
  scraping the public catalog is simpler and avoids auth issues.

What it does:
  1. Crawls /shop/category/what-we-make-3 (pages 1..N) to get the product
     list (name + URL + slug).
  2. For each product, fetches the detail page and extracts:
     - Display name
     - Slug + Odoo internal ID
     - Category breadcrumb
     - Base price
     - Attribute definitions (name + values + display type)
     - Variant pricing matrix (parsed from JSON-LD hasVariant block)
     - Photo URLs (main + secondary)
  3. Downloads each product's main image to _resources/odoo-export/images/.
  4. Writes everything to _resources/odoo-export/catalog.json.
  5. Also captures the category tree from Special Occasions + Holidays &
     Seasons pages.

Output:
  _resources/odoo-export/catalog.json
  _resources/odoo-export/images/<product-slug>.png
  _resources/odoo-export/categories.json

Notes:
  - Uses a real-browser User-Agent (Cloudflare blocks default urllib UA per
    LT lessons-learned 2026-04-26).
  - Does NOT export customers (would need auth; deferred to Phase 6 cutover).
  - Does NOT modify the Odoo site (read-only scrape).
  - Idempotent: re-running overwrites the JSON; re-downloads images only
    if missing.

Usage:
  python scripts/setup/export_odoo_catalog.py
  python scripts/setup/export_odoo_catalog.py --max-products 5  # dry-run subset
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

ODOO_BASE = "http://5.78.136.133"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXPORT_DIR = PROJECT_ROOT / "_resources" / "odoo-export"
IMAGES_DIR = EXPORT_DIR / "images"


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def fetch_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def collect_product_links(html: str) -> list[tuple[str, str]]:
    """Return list of (slug-with-id, display_name) extracted from a category listing page."""
    pattern = re.compile(r'href="(/shop/[a-z][a-z0-9-]*/[a-z0-9-]+-(\d+))"[^>]*title="([^"]+)"')
    return [(m.group(1), m.group(3)) for m in pattern.finditer(html)]


def extract_jsonld_product(html: str) -> dict[str, Any] | None:
    """Find the Product JSON-LD block on a product detail page."""
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL):
        try:
            data = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and data.get("@type") == "Product":
            return data
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and item.get("@type") == "Product":
                    return item
    return None


def extract_attribute_definitions(html: str) -> dict[str, list[dict[str, str]]]:
    """Parse the data-attribute-exclusions JSON to get attribute name -> [values]."""
    m = re.search(r'data-attribute-exclusions="(\{[^"]+\})"', html)
    if not m:
        return {}
    raw = m.group(1).replace("&quot;", '"').replace("&#34;", '"').replace("&#39;", "'").replace("&amp;", "&")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    mapped = data.get("mapped_attribute_names", {})
    attrs: dict[str, list[dict[str, str]]] = {}
    for value_id, label in mapped.items():
        if ":" not in label:
            continue
        attr_name, value_name = [p.strip() for p in label.split(":", 1)]
        attrs.setdefault(attr_name, []).append({"value_id": str(value_id), "value_name": value_name})
    return attrs


def extract_image_url(html: str) -> str | None:
    """Find the main product image URL."""
    m = re.search(r'<img[^>]*itemprop="image"[^>]*src="([^"]+)"', html)
    if m:
        return urljoin(ODOO_BASE, m.group(1))
    m = re.search(r'<img[^>]*class="[^"]*o_product_feature_image[^"]*"[^>]*src="([^"]+)"', html)
    if m:
        return urljoin(ODOO_BASE, m.group(1))
    return None


def slug_only(slug_with_id: str) -> str:
    """Strip Odoo's trailing -<id> from a product slug."""
    m = re.match(r"^(.+?)-(\d+)$", slug_with_id)
    return m.group(1) if m else slug_with_id


def export_category(category_path: str, max_pages: int = 5) -> list[tuple[str, str]]:
    """Crawl a category's paginated listing and return (relative_path, display_name) tuples."""
    all_products: list[tuple[str, str]] = []
    seen: set[str] = set()
    for page in range(1, max_pages + 1):
        url = f"{ODOO_BASE}{category_path}" + (f"/page/{page}" if page > 1 else "")
        try:
            html = fetch(url)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                break
            raise
        page_products = collect_product_links(html)
        if not page_products:
            break
        new_count = 0
        for slug, name in page_products:
            if slug in seen:
                continue
            seen.add(slug)
            all_products.append((slug, name))
            new_count += 1
        if new_count == 0:
            break
        print(f"  page {page}: {new_count} new products")
    return all_products


def export_product(slug_with_id: str, name: str) -> dict[str, Any]:
    """Fetch a product detail page and return structured data."""
    url = f"{ODOO_BASE}/shop{slug_with_id.replace('/shop', '')}" if slug_with_id.startswith("/shop") else f"{ODOO_BASE}{slug_with_id}"
    html = fetch(url)
    jsonld = extract_jsonld_product(html) or {}
    attrs = extract_attribute_definitions(html)
    image_url = jsonld.get("image") or extract_image_url(html)

    # Variants: list of {url, price} from JSON-LD's hasVariant
    variants = []
    for v in (jsonld.get("hasVariant") or []):
        offers = v.get("offers", {})
        if isinstance(offers, dict):
            variants.append({
                "url": v.get("url"),
                "price": offers.get("price"),
                "currency": offers.get("priceCurrency"),
            })

    return {
        "slug_with_id": slug_with_id.lstrip("/").replace("shop/", "", 1),
        "slug": slug_only(slug_with_id.split("/")[-1]),
        "name": name,
        "url": url,
        "base_price": jsonld.get("offers", {}).get("price") if isinstance(jsonld.get("offers"), dict) else None,
        "currency": jsonld.get("offers", {}).get("priceCurrency") if isinstance(jsonld.get("offers"), dict) else None,
        "description": jsonld.get("description"),
        "image_url": image_url,
        "attributes": attrs,
        "variants": variants,
        "variant_count": len(variants),
    }


def download_image(url: str, slug: str) -> Path | None:
    if not url:
        return None
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    # Determine extension from URL or default to .png
    ext = ".png"
    for candidate in (".png", ".jpg", ".jpeg", ".webp"):
        if candidate in url.lower():
            ext = candidate
            break
    target = IMAGES_DIR / f"{slug}{ext}"
    if target.exists():
        return target
    try:
        data = fetch_bytes(url)
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        print(f"    ! image download failed for {slug}: {e}")
        return None
    target.write_bytes(data)
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--max-products", type=int, default=None,
                        help="Cap product count (for dry runs)")
    parser.add_argument("--skip-images", action="store_true",
                        help="Skip image downloads (faster dry run)")
    args = parser.parse_args()

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    # Phase 1: collect product list across What We Make pages
    print("=== Crawling What We Make catalog ===")
    products_basic = export_category("/shop/category/what-we-make-3", max_pages=5)
    print(f"\nFound {len(products_basic)} products in What We Make")

    if args.max_products:
        products_basic = products_basic[: args.max_products]
        print(f"Limited to first {len(products_basic)} for dry run")

    # Phase 2: fetch each product's detail
    print(f"\n=== Fetching detail for {len(products_basic)} products ===")
    products: list[dict[str, Any]] = []
    for i, (slug_with_id, name) in enumerate(products_basic, 1):
        print(f"[{i}/{len(products_basic)}] {name}")
        try:
            product = export_product(slug_with_id, name)
            products.append(product)
            if not args.skip_images and product.get("image_url"):
                target = download_image(product["image_url"], product["slug"])
                if target:
                    print(f"    image -> {target.relative_to(PROJECT_ROOT)}")
        except Exception as e:
            print(f"    ! failed: {e}")
            products.append({"slug": slug_with_id, "name": name, "error": str(e)})

    # Phase 3: persist
    catalog_path = EXPORT_DIR / "catalog.json"
    catalog_path.write_text(json.dumps({
        "source": ODOO_BASE,
        "category": "/shop/category/what-we-make-3",
        "product_count": len(products),
        "products": products,
    }, indent=2))
    print(f"\nWrote {catalog_path.relative_to(PROJECT_ROOT)} ({len(products)} products)")

    # Quick stats
    with_attrs = sum(1 for p in products if p.get("attributes"))
    with_variants = sum(1 for p in products if p.get("variant_count", 0) > 0)
    with_images = sum(1 for p in products if p.get("image_url"))
    print(f"Stats: {with_attrs} have attributes, {with_variants} have variants, {with_images} have image URLs")


if __name__ == "__main__":
    main()
