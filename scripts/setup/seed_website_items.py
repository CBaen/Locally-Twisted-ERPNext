#!/usr/bin/env python3
"""
Seed Locally Twisted's small-shop catalog into ERPNext.

Reads `_resources/odoo-export/catalog.json` (the LT Odoo product export from
2026-04-26) and creates Item + Website Item + Item Price records on the
local LT install at http://localhost:8081 for each product priced under
$200 with a downloaded image. Attaches the product image to each Item.

Filter rationale (see locally-twisted-decisions.md): the $200 line in this
catalog correlates with the boundary between "fixed-spec product, customer
buys without consulting" and "balloon decor with install variables, customer
inquires before buying." The 33 items under $200 are bouquets, columns ≤
$180, kits, and small decor — the small-shop sidebar.

Idempotent: API "already exists" responses are caught and the loop continues.
Safe to re-run if the script aborts partway. Re-running will skip existing
records and only act on missing pieces.

Usage:
    python scripts/setup/seed_website_items.py

Reads:  _resources/odoo-export/catalog.json
        _resources/odoo-export/images/<slug>.png
Writes: 1 Item Group ("Shop Items"), 33 Item records, 33 Website Item
        records, 33 Item Price records, 33 File attachments to Item.image.

Stdlib only — no `pip install` required. Pattern follows
scripts/translate/translate_crm_lead.py.
"""

import html
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from http.cookiejar import CookieJar
from pathlib import Path

BASE = "http://localhost:8081"
USER = "Administrator"
PWD = "admin"

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CATALOG_PATH = PROJECT_ROOT / "_resources" / "odoo-export" / "catalog.json"
IMAGES_DIR = PROJECT_ROOT / "_resources" / "odoo-export" / "images"

PRICE_CEILING = 200.0
ITEM_GROUP = "Shop Items"
PARENT_ITEM_GROUP = "All Item Groups"
PRICE_LIST = "Standard Selling"
COMPANY = "Locally Twisted"
STOCK_UOM = "Nos"


# ──────────────────────────────────────────────────────────────────────
# HTTP plumbing — same shape as scripts/translate/translate_crm_lead.py
# ──────────────────────────────────────────────────────────────────────


def make_opener():
    cj = CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))


def login(opener):
    data = urllib.parse.urlencode({"usr": USER, "pwd": PWD}).encode()
    req = urllib.request.Request(f"{BASE}/api/method/login", data=data)
    with opener.open(req, timeout=10) as r:
        if r.status != 200:
            raise SystemExit(f"login failed: HTTP {r.status}")
    print(f"[login] OK as {USER}")


def quote_path(path):
    return urllib.parse.quote(path, safe="/?=&[]\"")


def api_get(opener, path):
    req = urllib.request.Request(
        f"{BASE}{quote_path(path)}",
        headers={"X-Requested-With": "XMLHttpRequest"},
    )
    with opener.open(req, timeout=15) as r:
        return json.loads(r.read().decode())


def insert_doc(opener, doc, label):
    """POST to frappe.client.insert. Returns (name, was_dup)."""
    payload = json.dumps({"doc": doc}).encode()
    req = urllib.request.Request(
        f"{BASE}/api/method/frappe.client.insert",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
        },
    )
    try:
        with opener.open(req, timeout=30) as r:
            parsed = json.loads(r.read().decode())
            return parsed.get("message", {}).get("name", "?"), False
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        if "already exists" in body or "DuplicateEntryError" in body:
            return None, True
        raise SystemExit(f"[{label}] insert failed: HTTP {e.code} body={body[:400]}")


def upload_file_to_item(opener, item_name, image_path):
    """Upload an image file and attach it to Item.image. Returns file_url."""
    boundary = f"----LT-{uuid.uuid4().hex}"
    crlf = b"\r\n"
    body = []

    def field(name, value):
        body.append(f"--{boundary}".encode())
        body.append(
            f'Content-Disposition: form-data; name="{name}"'.encode()
        )
        body.append(b"")
        body.append(str(value).encode())

    field("doctype", "Item")
    field("docname", item_name)
    field("fieldname", "image")
    field("is_private", "0")

    # File part
    body.append(f"--{boundary}".encode())
    filename = image_path.name
    mime = mimetypes.guess_type(str(image_path))[0] or "application/octet-stream"
    body.append(
        f'Content-Disposition: form-data; name="file"; filename="{filename}"'.encode()
    )
    body.append(f"Content-Type: {mime}".encode())
    body.append(b"")
    body.append(image_path.read_bytes())

    body.append(f"--{boundary}--".encode())
    body.append(b"")
    payload = crlf.join(body)

    req = urllib.request.Request(
        f"{BASE}/api/method/upload_file",
        data=payload,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "X-Requested-With": "XMLHttpRequest",
        },
    )
    try:
        with opener.open(req, timeout=60) as r:
            parsed = json.loads(r.read().decode())
            return parsed.get("message", {}).get("file_url")
    except urllib.error.HTTPError as e:
        raise SystemExit(
            f"[{item_name}] image upload failed: HTTP {e.code} body={e.read().decode()[:400]}"
        )


def set_field(opener, doctype, name, fieldname, value):
    """Use frappe.client.set_value to update one field on an existing doc."""
    payload = json.dumps(
        {
            "doctype": doctype,
            "name": name,
            "fieldname": fieldname,
            "value": value,
        }
    ).encode()
    req = urllib.request.Request(
        f"{BASE}/api/method/frappe.client.set_value",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
        },
    )
    with opener.open(req, timeout=20) as r:
        return json.loads(r.read().decode())


# ──────────────────────────────────────────────────────────────────────
# Catalog handling
# ──────────────────────────────────────────────────────────────────────


def parse_price(p):
    v = p.get("base_price")
    if v is None:
        return None
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def load_eligible_products():
    """Return products with price < $200 and a real image file on disk."""
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    products = catalog.get("products", [])
    eligible = []
    for p in products:
        price = parse_price(p)
        if price is None or price >= PRICE_CEILING:
            continue
        slug = p.get("slug")
        if not slug:
            continue
        image_path = IMAGES_DIR / f"{slug}.png"
        if not image_path.exists():
            continue
        eligible.append(
            {
                "slug": slug,
                "name": html.unescape(p.get("name", "")).strip(),
                "description": html.unescape(p.get("description", "")).strip(),
                "price": price,
                "image_path": image_path,
                "url": p.get("url", ""),
            }
        )
    return eligible


# ──────────────────────────────────────────────────────────────────────
# Seed flow
# ──────────────────────────────────────────────────────────────────────


def ensure_item_group(opener):
    """Create Shop Items group under All Item Groups if it doesn't exist."""
    name, was_dup = insert_doc(
        opener,
        {
            "doctype": "Item Group",
            "item_group_name": ITEM_GROUP,
            "parent_item_group": PARENT_ITEM_GROUP,
            "is_group": 0,
            "show_in_website": 1,
        },
        ITEM_GROUP,
    )
    if was_dup:
        print(f"[item-group] {ITEM_GROUP} already exists")
    else:
        print(f"[item-group] created {name}")


def seed_one(opener, prod):
    """Create Item, attach image, create Website Item, create Item Price."""
    slug = prod["slug"]
    label = slug

    # 1. Item
    item_doc = {
        "doctype": "Item",
        "item_code": slug,
        "item_name": prod["name"][:140],
        "item_group": ITEM_GROUP,
        "stock_uom": STOCK_UOM,
        "is_stock_item": 0,
        "is_sales_item": 1,
        "is_purchase_item": 0,
        "include_item_in_manufacturing": 0,
        "description": prod["description"] or prod["name"],
        "standard_rate": prod["price"],
    }
    item_name, was_dup = insert_doc(opener, item_doc, f"Item:{label}")
    if was_dup:
        item_name = slug
        print(f"  [item]      {slug:40s} (exists)")
    else:
        print(f"  [item]      {slug:40s} -> {item_name}")

    # 2. Image upload + attach
    # Skip if Item already has image set (idempotent re-runs)
    existing = api_get(opener, f"/api/resource/Item/{slug}").get("data", {})
    if not existing.get("image"):
        file_url = upload_file_to_item(opener, item_name, prod["image_path"])
        if file_url:
            # upload_file already attaches via doctype/docname/fieldname
            print(f"  [image]     {prod['image_path'].name:40s} -> {file_url}")
    else:
        print(f"  [image]     {prod['image_path'].name:40s} (already attached: {existing['image']})")

    # 3. Item Price (Standard Selling)
    # Skip-via-try since duplicates are common on re-run
    price_doc = {
        "doctype": "Item Price",
        "item_code": slug,
        "price_list": PRICE_LIST,
        "price_list_rate": prod["price"],
        "currency": "USD",
        "selling": 1,
    }
    _, was_dup = insert_doc(opener, price_doc, f"Price:{label}")
    if was_dup:
        print(f"  [price]     ${prod['price']:>7.2f}  (Standard Selling)  (exists)")
    else:
        print(f"  [price]     ${prod['price']:>7.2f}  (Standard Selling)")

    # 4. Website Item
    wi_doc = {
        "doctype": "Website Item",
        "item_code": slug,
        "web_item_name": prod["name"][:140],
        "item_group": ITEM_GROUP,
        "route": f"shop/{slug}",
        "published": 1,
        "short_description": prod["description"][:140] if prod["description"] else prod["name"],
        "web_long_description": prod["description"] or prod["name"],
    }
    _, was_dup = insert_doc(opener, wi_doc, f"WebsiteItem:{label}")
    if was_dup:
        print(f"  [web-item]  published=1  route=shop/{slug}  (exists)")
    else:
        print(f"  [web-item]  published=1  route=shop/{slug}")


def update_webshop_settings(opener):
    """Bump products_per_page to 12 (default 6 is small for browsing)."""
    set_field(opener, "Webshop Settings", "Webshop Settings", "products_per_page", 12)
    print("[webshop-settings] products_per_page = 12")


def main():
    opener = make_opener()
    login(opener)

    products = load_eligible_products()
    print(f"[catalog] {len(products)} eligible products (price < ${PRICE_CEILING}, image on disk)")
    print()

    ensure_item_group(opener)
    print()

    for i, prod in enumerate(products, 1):
        print(f"[{i:2}/{len(products)}] ${prod['price']:>7.2f}  {prod['name']}")
        seed_one(opener, prod)
        print()

    update_webshop_settings(opener)
    print()
    print(f"[summary] Seeded {len(products)} products into Item + Website Item + Item Price.")
    print(f"OK -> {BASE}/all-products")
    print(f"OK -> {BASE}/app/website-item")
    return 0


if __name__ == "__main__":
    sys.exit(main())
