"""
scrape_odoo_live.py — Fresh scrape of LT's live Odoo at 5.78.136.133.

Source of truth per GL 2026-04-30: the LIVE Odoo site is the only catalog truth.
Captures EVERY product, EVERY attribute, EVERY value, the full exclusion graph,
and computes EVERY valid attribute combination per product. Variant prices are
resolved through Odoo's dynamic /website_sale/get_combination_info endpoint; the
page's JSON-LD/base price is not trusted as the variant price.

Output:
  _resources/odoo-live/catalog.json
    {
      "scraped_at": "ISO timestamp",
      "source": "http://5.78.136.133",
      "categories": [...],
      "products": [
        {
          "slug": "baby-shower-garland",
          "odoo_id": 71,
          "url": "http://...",
          "name": "Baby Shower Garland",
          "base_price": 150.00,
          "currency": "USD",
          "description": "...",  # HTML-stripped prose from itemprop="description"
          "image_url": "http://5.78.136.133/web/image/product.product/71/...",
          "additional_image_urls": [...],
          "attributes": {
            "Garland Length": {
              "attribute_id": 3,
              "display_type": "pills",
              "values": [
                {"ptav_id": 1293, "name": "6ft"},
                {"ptav_id": 1294, "name": "9ft"},
                {"ptav_id": 1295, "name": "12ft"}
              ]
            },
            "latex colors": {
              "attribute_id": 4,
              "display_type": "color",
              "values": [...]
            }
          },
          "exclusions": {<ptav_id>: [<forbidden_ptav_id>, ...]},
          "valid_variants": [
            {
              "ptav_ids": [1293, 1345],
              "combo": {"Garland Length": "6ft", "latex colors": "White"},
              "price": 150.00,
              "erpnext_variant_price": 150.00
            },
            ...
          ]
        }
      ]
    }
  _resources/odoo-live/images/<slug>.png  (and other formats)
  _resources/odoo-live/images/<slug>--<seq>.png  (additional images)

Run:
  PYTHONIOENCODING=utf-8 PYTHONUTF8=1 python scripts/setup/scrape_odoo_live.py
  PYTHONIOENCODING=utf-8 PYTHONUTF8=1 python scripts/setup/scrape_odoo_live.py --max-products 3 --skip-images   # smoke test
"""
from __future__ import annotations

import argparse
import datetime as dt
import html as html_lib
import itertools
import json
import re
import sys
import time
import urllib.error
import urllib.request
from http.cookiejar import CookieJar
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

ODOO_BASE = "http://5.78.136.133"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "apps" / "locally_twisted"))

from locally_twisted.catalog_variant_rules import (  # noqa: E402
    is_required_variant_attribute,
    project_required_variant_combo,
)

EXPORT_DIR = PROJECT_ROOT / "_resources" / "odoo-live"
IMAGES_DIR = EXPORT_DIR / "images"
TIMEOUT_S = 30
INTER_REQUEST_DELAY_S = 0.15  # be polite
ODOO_COMBINATION_ROUTE = f"{ODOO_BASE}/website_sale/get_combination_info"

CATEGORY_ROOTS = [
    "/shop/category/what-we-make-3",
    "/shop/category/special-occasions-4",
    "/shop/category/holidays-seasons-5",
]


# ── HTTP plumbing ─────────────────────────────────────────────────────

def new_opener() -> urllib.request.OpenerDirector:
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))


def fetch(url: str, opener: urllib.request.OpenerDirector | None = None) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    open_url = opener.open if opener else urllib.request.urlopen
    with open_url(req, timeout=TIMEOUT_S) as resp:
        return resp.read().decode("utf-8", errors="replace")


def fetch_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
        return resp.read()


# ── Category list crawl ───────────────────────────────────────────────

def collect_product_links(category_root_html: str) -> list[tuple[str, str, int]]:
    """From a category listing HTML, return (full_path, name, odoo_id) tuples."""
    rows: list[tuple[str, str, int]] = []
    pattern = re.compile(
        r'href="(/shop/[a-z][a-z0-9-]*/[a-z0-9-]+-(\d+))"[^>]*title="([^"]+)"'
    )
    for m in pattern.finditer(category_root_html):
        # Decode HTML entities in product names: &#39; → ', &#34; → ", etc.
        name = html_lib.unescape(m.group(3))
        rows.append((m.group(1), name, int(m.group(2))))
    return rows


def crawl_categories(max_pages: int = 6) -> dict[int, dict]:
    """Crawl all listed category roots and dedup products by Odoo id.
    Returns {odoo_id: {"path", "name"}}."""
    seen: dict[int, dict] = {}
    for root in CATEGORY_ROOTS:
        for page in range(1, max_pages + 1):
            url = f"{ODOO_BASE}{root}" + (f"/page/{page}" if page > 1 else "")
            try:
                html = fetch(url)
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    break
                raise
            new_count = 0
            for path, name, odoo_id in collect_product_links(html):
                if odoo_id in seen:
                    continue
                seen[odoo_id] = {"path": path, "name": name}
                new_count += 1
            if new_count == 0:
                break
            time.sleep(INTER_REQUEST_DELAY_S)
    return seen


# ── Per-product extraction ────────────────────────────────────────────

PRICE_RE = re.compile(r'<span[^>]*class="[^"]*oe_currency_value[^"]*"[^>]*>([\d.,]+)</span>', re.IGNORECASE)
JSONLD_RE = re.compile(r'<script type="application/ld\+json">\s*(\{.+?\})\s*</script>', re.DOTALL)
DESC_RE = re.compile(r'<div[^>]*itemprop="description"[^>]*>(.*?)</div>', re.DOTALL)
EXCL_RE = re.compile(r'data-attribute-exclusions="([^"]+)"', re.DOTALL)
CSRF_RE = re.compile(r'csrf_token:\s*"([^"]+)"')
ATTR_BLOCK_RE = re.compile(
    r'<li\s+name="variant_attribute"\s+data-attribute-id="(\d+)"\s+data-attribute-name="([^"]+)"\s+data-attribute-display-type="([^"]+)"[^>]*>(.*?)</li>\s*</li>?',
    re.DOTALL,
)
# Looser block: closing </li> for outer element matched by depth — use forward-search instead
VARIANT_INPUT_RE = re.compile(
    r'<input[^>]+data-value-id="(\d+)"[^>]+data-value-name="([^"]+)"',
    re.IGNORECASE,
)
IMG_RE = re.compile(r'(?:src|data-src|href)="(/web/image/product[^"]+)"', re.IGNORECASE)


def html_unescape(s: str) -> str:
    return (s.replace('&quot;', '"')
             .replace('&#34;', '"')
             .replace('&amp;', '&')
             .replace('&#39;', "'")
             .replace('&lt;', '<')
             .replace('&gt;', '>'))


def extract_jsonld_product(html: str) -> dict[str, Any]:
    for m in JSONLD_RE.finditer(html):
        try:
            data = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and data.get("@type") == "Product":
            return data
    return {}


def extract_base_price(html: str, jsonld: dict) -> float | None:
    """Prefer JSON-LD offer price. Fall back to first oe_currency_value."""
    offer = jsonld.get("offers")
    if isinstance(offer, dict):
        v = offer.get("price")
        if v is not None:
            try:
                return float(v)
            except (TypeError, ValueError):
                pass
    m = PRICE_RE.search(html)
    if m:
        try:
            return float(m.group(1).replace(",", ""))
        except ValueError:
            return None
    return None


def extract_description(html: str, jsonld: dict) -> str:
    """Pull HTML-stripped description prose. Prefer DOM (richer) over JSON-LD."""
    m = DESC_RE.search(html)
    if m:
        prose = re.sub(r'<[^>]+>', ' ', m.group(1))
        prose = re.sub(r'\s+', ' ', prose).strip()
        if prose:
            return prose
    return jsonld.get("description") or ""


def extract_exclusions(html: str) -> dict:
    """Return the parsed data-attribute-exclusions JSON."""
    m = EXCL_RE.search(html)
    if not m:
        return {}
    raw = html_unescape(m.group(1))
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def extract_attribute_blocks(html: str) -> dict[str, dict]:
    """Find each <li name="variant_attribute"> outer element and parse it.
    Use a stack-based scan since nested </li> tags break naive regex."""
    out: dict[str, dict] = {}
    cursor = 0
    while True:
        # Find next variant_attribute opening
        opener = re.search(
            r'<li\s+name="variant_attribute"\s+data-attribute-id="(\d+)"\s+data-attribute-name="([^"]+)"\s+data-attribute-display-type="([^"]+)"[^>]*>',
            html[cursor:],
        )
        if not opener:
            break
        attr_id = int(opener.group(1))
        attr_name = opener.group(2)
        display_type = opener.group(3)
        block_start = cursor + opener.end()
        # find the matching closing </li> at depth 0 (counting <li> opens/closes)
        depth = 1
        i = block_start
        while i < len(html) and depth > 0:
            next_open = html.find("<li", i)
            next_close = html.find("</li>", i)
            if next_close == -1:
                break
            if next_open != -1 and next_open < next_close:
                depth += 1
                i = next_open + 3
            else:
                depth -= 1
                i = next_close + 5
        block_end = i
        block_html = html[block_start:block_end]
        # Parse value rows; HTML-decode value names just in case
        values = []
        for m in VARIANT_INPUT_RE.finditer(block_html):
            ptav_id = int(m.group(1))
            value_name = html_lib.unescape(m.group(2))
            values.append({"ptav_id": ptav_id, "name": value_name})
        if values:
            out[attr_name] = {
                "attribute_id": attr_id,
                "display_type": display_type,
                "values": values,
            }
        cursor = block_end
    return out


def extract_image_urls(html: str, jsonld: dict) -> tuple[str | None, list[str]]:
    """Main image (from JSON-LD), plus additional unique image URLs from the page.

    If JSON-LD has no `image` field (5 LT products are like this), promote the
    first DOM-discovered /web/image/product URL to be main. Prefer the
    `product.product/<id>/image_1920` shape (highest-res, customer-facing) over
    the smaller template variants.
    """
    main = jsonld.get("image")
    if main and not main.startswith("http"):
        main = urljoin(ODOO_BASE, main)

    found: list[str] = []
    for m in IMG_RE.finditer(html):
        u = urljoin(ODOO_BASE, m.group(1))
        if u not in found:
            found.append(u)

    if not main and found:
        # Pick the best fallback: prefer product.product/.../image_1920
        def priority(u: str) -> tuple[int, int, int]:
            return (
                0 if "/product.product/" in u else 1,
                0 if "image_1920" in u else (1 if "image_1024" in u else 2),
                found.index(u),  # stable tie-break
            )
        sorted_found = sorted(found, key=priority)
        main = sorted_found[0]

    extras = [u for u in found if u != main]
    return main, extras


def compute_valid_variants(
    attributes: dict[str, dict],
    exclusions_data: dict,
    base_price: float | None,
) -> list[dict]:
    """Cartesian product of all attribute values, filtered by exclusions.
    Returns: [{ptav_ids: [...], combo: {attr_name: value_name}, price: <base>}]"""
    if not attributes:
        return []
    excl_map = exclusions_data.get("exclusions", {}) or {}
    # ensure keys are int (they're str from JSON)
    excl_int = {int(k): set(int(x) for x in v) for k, v in excl_map.items()}

    # Stable order of attributes
    attr_names = sorted(attributes.keys())
    value_lists = [
        [(v["ptav_id"], v["name"]) for v in attributes[an]["values"]]
        for an in attr_names
    ]

    valid = []
    for combo in itertools.product(*value_lists):
        ptav_ids = [pv[0] for pv in combo]
        # Check exclusions: a combination is invalid if ANY ptav in it
        # excludes ANY OTHER ptav also in it
        invalid = False
        for i, ptav_i in enumerate(ptav_ids):
            forbidden = excl_int.get(ptav_i, set())
            for j, ptav_j in enumerate(ptav_ids):
                if i == j:
                    continue
                if ptav_j in forbidden:
                    invalid = True
                    break
            if invalid:
                break
        if invalid:
            continue
        valid.append({
            "ptav_ids": ptav_ids,
            "combo": {attr_names[k]: combo[k][1] for k in range(len(attr_names))},
            "price": base_price,
        })
    return valid


def extract_csrf_token(html: str) -> str | None:
    match = CSRF_RE.search(html)
    return match.group(1) if match else None


def ptav_attribute_lookup(attributes: dict[str, dict]) -> dict[int, str]:
    lookup: dict[int, str] = {}
    for attr_name, attr_data in attributes.items():
        for value in attr_data.get("values") or []:
            lookup[int(value["ptav_id"])] = attr_name
    return lookup


def required_ptav_ids_for_seed(row: dict, attributes: dict[str, dict]) -> list[int]:
    """Return the Odoo ptav ids that match the ERPNext required variant combo."""
    full_ptav_ids = [int(value) for value in row.get("ptav_ids") or []]
    combo = row.get("combo") or {}
    projected_combo = project_required_variant_combo(combo)
    if len(projected_combo) == len(combo):
        return full_ptav_ids

    lookup = ptav_attribute_lookup(attributes)
    required_names = set(projected_combo)
    required_ids = [
        ptav_id
        for ptav_id in full_ptav_ids
        if lookup.get(ptav_id) in required_names and is_required_variant_attribute(lookup.get(ptav_id))
    ]
    if not required_ids:
        raise RuntimeError(f"Could not project ERPNext ptav ids from row: {row}")
    return required_ids


def fetch_combination_price(
    opener: urllib.request.OpenerDirector,
    csrf_token: str,
    product_template_id: int,
    ptav_ids: list[int],
) -> dict:
    payload = json.dumps(
        {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "product_template_id": product_template_id,
                "product_id": 0,
                "combination": ptav_ids,
                "add_qty": 1,
                "parent_combination": [],
            },
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        ODOO_COMBINATION_ROUTE,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
            "X-CSRFToken": csrf_token,
        },
    )
    with opener.open(req, timeout=TIMEOUT_S) as resp:
        body = resp.read().decode("utf-8", errors="replace")
    data = json.loads(body)
    if data.get("error"):
        raise RuntimeError(f"Odoo combination price error for {ptav_ids}: {data['error']}")
    result = data.get("result") or {}
    if not result.get("is_combination_possible"):
        raise RuntimeError(f"Odoo says combination is not possible: {ptav_ids}")
    if result.get("price") is None:
        raise RuntimeError(f"Odoo returned no price for combination: {ptav_ids}")
    return result


def enrich_variant_prices_from_odoo(
    *,
    opener: urllib.request.OpenerDirector,
    csrf_token: str | None,
    product_template_id: int | None,
    attributes: dict[str, dict],
    valid_variants: list[dict],
) -> None:
    if not product_template_id or not valid_variants:
        return
    if not csrf_token:
        raise RuntimeError(f"Odoo page did not expose csrf_token for product {product_template_id}")

    full_price_cache: dict[tuple[int, ...], dict] = {}
    erpnext_price_cache: dict[tuple[int, ...], dict] = {}

    for row in valid_variants:
        full_key = tuple(int(value) for value in row.get("ptav_ids") or [])
        erpnext_key = tuple(required_ptav_ids_for_seed(row, attributes))
        if full_key not in full_price_cache:
            full_price_cache[full_key] = fetch_combination_price(
                opener,
                csrf_token,
                int(product_template_id),
                list(full_key),
            )
            time.sleep(INTER_REQUEST_DELAY_S)
        if erpnext_key not in erpnext_price_cache:
            erpnext_price_cache[erpnext_key] = fetch_combination_price(
                opener,
                csrf_token,
                int(product_template_id),
                list(erpnext_key),
            )
            time.sleep(INTER_REQUEST_DELAY_S)

        full_result = full_price_cache[full_key]
        erpnext_result = erpnext_price_cache[erpnext_key]
        row["price"] = float(full_result["price"])
        row["odoo_product_id"] = full_result.get("product_id")
        row["erpnext_variant_price"] = float(erpnext_result["price"])
        row["erpnext_odoo_product_id"] = erpnext_result.get("product_id")


def slug_from_path(product_path: str) -> tuple[str, int | None]:
    """`/shop/what-we-make-3/baby-shower-garland-71` → ('baby-shower-garland', 71)."""
    last = product_path.rsplit("/", 1)[-1]
    m = re.match(r"^(.+?)-(\d+)$", last)
    if m:
        return m.group(1), int(m.group(2))
    return last, None


def export_product(product_path: str, name: str, odoo_id: int) -> dict[str, Any]:
    url = f"{ODOO_BASE}{product_path}"
    opener = new_opener()
    html = fetch(url, opener=opener)
    jsonld = extract_jsonld_product(html)
    base_price = extract_base_price(html, jsonld)
    description = extract_description(html, jsonld)
    exclusions_data = extract_exclusions(html)
    attributes = extract_attribute_blocks(html)
    main_img, extra_imgs = extract_image_urls(html, jsonld)
    valid_variants = compute_valid_variants(attributes, exclusions_data, base_price)
    slug, parsed_id = slug_from_path(product_path)
    product_template_id = odoo_id or parsed_id
    enrich_variant_prices_from_odoo(
        opener=opener,
        csrf_token=extract_csrf_token(html),
        product_template_id=product_template_id,
        attributes=attributes,
        valid_variants=valid_variants,
    )

    return {
        "slug": slug,
        "odoo_id": product_template_id,
        "url": url,
        "name": name,
        "base_price": base_price,
        "currency": (jsonld.get("offers") or {}).get("priceCurrency") or "USD",
        "description": description,
        "image_url": main_img,
        "additional_image_urls": extra_imgs,
        "attributes": attributes,
        "exclusions": {int(k): [int(x) for x in v] for k, v in (exclusions_data.get("exclusions") or {}).items()},
        "mapped_attribute_names": exclusions_data.get("mapped_attribute_names") or {},
        "valid_variants": valid_variants,
        "variant_count": len(valid_variants),
    }


# ── Image download ────────────────────────────────────────────────────

def determine_image_extension(url: str) -> str:
    for ext in (".png", ".jpg", ".jpeg", ".webp", ".gif"):
        if ext in url.lower():
            return ext
    return ".png"  # Odoo's default


def download_image(url: str, target: Path) -> bool:
    if target.exists():
        return True
    try:
        data = fetch_bytes(url)
    except (urllib.error.HTTPError, urllib.error.URLError) as e:
        print(f"    ! image download failed for {target.name}: {e}")
        return False
    target.write_bytes(data)
    return True


# ── Main ──────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--max-products", type=int, default=None,
                        help="Cap product count (for dry runs)")
    parser.add_argument("--skip-images", action="store_true",
                        help="Skip image downloads")
    parser.add_argument("--out-dir", default=str(EXPORT_DIR),
                        help=f"Output directory (default: {EXPORT_DIR})")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    img_dir = out_dir / "images"
    out_dir.mkdir(parents=True, exist_ok=True)
    img_dir.mkdir(parents=True, exist_ok=True)

    print("=== Crawling category roots ===")
    products_by_id = crawl_categories()
    print(f"Found {len(products_by_id)} unique products across "
          f"{len(CATEGORY_ROOTS)} category roots")

    if args.max_products:
        items = list(products_by_id.items())[: args.max_products]
        products_by_id = dict(items)
        print(f"Limited to first {len(products_by_id)} for dry run")

    print(f"\n=== Fetching detail for {len(products_by_id)} products ===")
    products: list[dict[str, Any]] = []
    failures: list[dict] = []
    for i, (odoo_id, meta) in enumerate(sorted(products_by_id.items()), 1):
        print(f"[{i:2}/{len(products_by_id)}] {meta['name']} (id={odoo_id})")
        try:
            prod = export_product(meta["path"], meta["name"], odoo_id)
            print(f"    base=${prod['base_price']} attrs={list(prod['attributes'].keys())} "
                  f"variants={prod['variant_count']} img={'Y' if prod['image_url'] else 'N'}")
            products.append(prod)
            if not args.skip_images and prod.get("image_url"):
                # Main image
                ext = determine_image_extension(prod["image_url"])
                target = img_dir / f"{prod['slug']}{ext}"
                if download_image(prod["image_url"], target):
                    print(f"    [main img] {target.name}")
                # Additional images
                for j, extra_url in enumerate(prod.get("additional_image_urls", []), 1):
                    ext = determine_image_extension(extra_url)
                    extra_target = img_dir / f"{prod['slug']}--extra-{j:02d}{ext}"
                    if download_image(extra_url, extra_target):
                        print(f"    [extra img {j}] {extra_target.name}")
            time.sleep(INTER_REQUEST_DELAY_S)
        except Exception as e:
            print(f"    ! FAILED: {type(e).__name__}: {e}")
            failures.append({
                "odoo_id": odoo_id,
                "path": meta["path"],
                "name": meta["name"],
                "error": str(e),
            })

    catalog_path = out_dir / "catalog.json"
    catalog_path.write_text(json.dumps({
        "scraped_at": dt.datetime.now().isoformat(),
        "source": ODOO_BASE,
        "category_roots": CATEGORY_ROOTS,
        "product_count": len(products),
        "failure_count": len(failures),
        "products": products,
        "failures": failures,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {catalog_path.relative_to(PROJECT_ROOT)} ({len(products)} products, {len(failures)} failures)")

    # Summary stats — loud failure on any failure
    with_attrs = sum(1 for p in products if p.get("attributes"))
    with_variants = sum(1 for p in products if p.get("variant_count", 0) > 0)
    with_images = sum(1 for p in products if p.get("image_url"))
    with_desc = sum(1 for p in products if p.get("description"))
    print("\n=== Summary ===")
    print(f"  Products: {len(products)}")
    print(f"  With attributes: {with_attrs}")
    print(f"  With computed variants: {with_variants}")
    print(f"  With image URL: {with_images}")
    print(f"  With description: {with_desc}")
    print(f"  Failures: {len(failures)}")

    if failures:
        print("\n=== FAILURES (loud) ===")
        for f in failures:
            print(f"  - {f['name']} (id={f['odoo_id']}): {f['error']}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
