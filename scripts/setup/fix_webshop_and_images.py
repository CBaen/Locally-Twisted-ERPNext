#!/usr/bin/env python3
"""
Fix webshop visibility + attach uploaded images to Item.image and
Website Item.website_image.

After scripts/setup/seed_website_items.py runs, three things still need
explicit attention:

1. **Webshop Settings.enabled = 0 by default.** The 4-page product listing
   (`/all-products`) DOES render, but the listing engine's
   `add_display_details` hides items behind the "shop is off" gate when
   `enabled=0`. Symptom: only the 2 items whose state happened to bypass
   the filter render. Fix: set `enabled=1`.

2. **`upload_file` does not write the file_url back to the parent doc's
   field.** It creates a File record with `attached_to_field=image` but
   `Item.image` stays null. Frappe gotcha — separate from the file
   attachment record. Fix: explicit `set_value` per item.

3. **Webshop reads `Website Item.website_image` for storefront display, NOT
   `Item.image`.** The two fields are independent in v15. Fix: set both.

Idempotent. Safe to re-run. Only writes when the target value is actually
missing/wrong.

Usage:
    python scripts/setup/fix_webshop_and_images.py

Reads:  Existing Item + Website Item + File records on http://localhost:8081
Writes: Item.image, Website Item.website_image (33 rows each), Webshop
        Settings (enabled, show_price, allow_items_not_in_stock,
        products_per_page).
"""

import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from http.cookiejar import CookieJar

BASE = "http://localhost:8081"
USER = "Administrator"
PWD = "admin"

WEBSHOP_TARGETS = {
    "enabled": 1,
    "show_price": 1,
    "allow_items_not_in_stock": 1,
    "products_per_page": 12,
    "enable_field_filters": 1,
    "show_attachments": 0,
    "enable_checkout": 1,
    "price_list": "Standard Selling",
    "default_customer_group": "Individual",
    "company": "Locally Twisted",
}


def make_opener():
    cj = CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))


def login(opener):
    data = urllib.parse.urlencode({"usr": USER, "pwd": PWD}).encode()
    with opener.open(urllib.request.Request(f"{BASE}/api/method/login", data=data), timeout=10):
        pass
    print(f"[login] OK as {USER}")


def quote(p):
    return urllib.parse.quote(p, safe="/?=&[]\"")


def api_get(opener, path):
    req = urllib.request.Request(
        f"{BASE}{quote(path)}", headers={"X-Requested-With": "XMLHttpRequest"}
    )
    with opener.open(req, timeout=15) as r:
        return json.loads(r.read().decode())


def set_value(opener, doctype, name, fieldname, value):
    payload = json.dumps(
        {"doctype": doctype, "name": name, "fieldname": fieldname, "value": value}
    ).encode()
    req = urllib.request.Request(
        f"{BASE}/api/method/frappe.client.set_value",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
        },
    )
    try:
        with opener.open(req, timeout=20) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise SystemExit(f"set_value failed for {doctype}/{name}.{fieldname}: HTTP {e.code} body={body[:300]}")


def fix_webshop_settings(opener):
    cur = api_get(opener, "/api/resource/Webshop Settings/Webshop Settings").get("data", {})
    print("[webshop] current:", {k: cur.get(k) for k in WEBSHOP_TARGETS})
    for field, want in WEBSHOP_TARGETS.items():
        have = cur.get(field)
        if have != want:
            set_value(opener, "Webshop Settings", "Webshop Settings", field, want)
            print(f"  [set] {field} {have!r} -> {want!r}")
        else:
            print(f"  [skip] {field} = {have!r}")


def fix_images(opener):
    items = api_get(
        opener,
        '/api/resource/Item?limit_page_length=100&filters=[["item_group","=","Shop Items"]]&fields=["name","image"]',
    ).get("data", [])
    print(f"\n[images] {len(items)} Items in Shop Items group")

    fixed_item, fixed_wi, skipped = 0, 0, 0
    for it in items:
        slug = it["name"]
        # Find the File record attached to this Item with attached_to_field=image
        files = api_get(
            opener,
            f'/api/resource/File?filters=[["attached_to_doctype","=","Item"],["attached_to_name","=","{slug}"],["attached_to_field","=","image"]]&fields=["file_url"]',
        ).get("data", [])
        if not files:
            print(f"  [warn] {slug}: no File record with attached_to_field=image — skipping")
            skipped += 1
            continue
        file_url = files[0]["file_url"]

        # 1) Item.image
        if it.get("image") != file_url:
            set_value(opener, "Item", slug, "image", file_url)
            fixed_item += 1
            print(f"  [item.image]         {slug:42s} -> {file_url}")

        # 2) Website Item.website_image  (look up Website Item by item_code)
        wi = api_get(
            opener,
            f'/api/resource/Website Item?filters=[["item_code","=","{slug}"]]&fields=["name","website_image"]',
        ).get("data", [])
        if wi:
            wi_name = wi[0]["name"]
            if wi[0].get("website_image") != file_url:
                set_value(opener, "Website Item", wi_name, "website_image", file_url)
                fixed_wi += 1
                print(f"  [website_image]      {slug:42s} -> {file_url}")

    print(
        f"\n[summary] Item.image fixed: {fixed_item} / Website Item.website_image fixed: {fixed_wi} / skipped: {skipped}"
    )


def main():
    opener = make_opener()
    login(opener)
    fix_webshop_settings(opener)
    fix_images(opener)
    print()
    print(f"OK -> {BASE}/all-products")
    return 0


if __name__ == "__main__":
    sys.exit(main())
