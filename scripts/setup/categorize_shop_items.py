#!/usr/bin/env python3
"""
Re-categorize the 33 seeded Items into 4 Item Groups.

Three groups for the Shop (filter pills on /shop):
- Bouquets   — themed/branded bouquets (Unicorn, Mickey, Get Well, etc.)
- Columns    — themed-or-event-specific columns (Number, 7' Butterfly,
               Mother's Day Front Yard)
- Ready-Made — small kits & decor (Easter Cups, Baby Table, Marble Table,
               6' Graduation Stands, Graduation Grab n Go)

One group OFF the shop (consultative — invoiced, not e-commerce):
- Event Decor — Classic Organic Columns, Premium Organic, Large Organic,
                Easel Organic, Baby Shower Garland, Logo Bouquet,
                Organic Grab n' Go, 7' Epic Column

Event Decor items keep their Item records (Jeff still uses them in
Quotations / Invoices) but their Website Item records are unpublished
so they don't appear on the storefront.

Idempotent. Re-runs are safe — only writes when the target value differs
from the current one.
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

PARENT_ITEM_GROUP = "All Item Groups"

# Item slug -> target Item Group. The 33 seeded items, assigned per the
# Shop vs Event Decor distinction.
ASSIGNMENTS = {
    # ── Bouquets (17 themed bouquets) ─────────────────────────────────
    "unicorn-bouquet": "Bouquets",
    "mickey-mouse-bouquet": "Bouquets",
    "minion-bouquet": "Bouquets",
    "encanto-bouquet": "Bouquets",
    "stitch-bouquet": "Bouquets",
    "flamingo-bouquet": "Bouquets",
    "football-bouquet": "Bouquets",
    "soccer-bouquet": "Bouquets",
    "over-the-hill-bouquet": "Bouquets",
    "space-bouquet": "Bouquets",
    "paw-patrol-bouquet": "Bouquets",
    "elsa-bouquet": "Bouquets",
    "holy-cow-bouquet": "Bouquets",
    "butterfly-get-well-bouquet-latex-free": "Bouquets",
    "bandage-get-well-bouquet-latex-free": "Bouquets",
    "shooting-star-get-well-bouquet-latex-free": "Bouquets",

    # ── Columns (themed or event-specific) ────────────────────────────
    "number-balloon-columns": "Columns",
    "7-butterfly-column": "Columns",
    "mothers-day-front-yard-7-column": "Columns",

    # ── Ready-Made (small kits, decor, stands) ────────────────────────
    "easter-balloon-cups": "Ready-Made",
    "baby-table-decor": "Ready-Made",
    "marble-table-decor": "Ready-Made",
    "6-graduation-stands": "Ready-Made",
    "graduation-grab-n-go": "Ready-Made",

    # ── Event Decor (consultative — unpublished from shop) ────────────
    "classic-organic-columns": "Event Decor",
    "pemium-organic-column": "Event Decor",
    "classic-organic-for-easel": "Event Decor",
    "baby-shower-garland": "Event Decor",
    "logo-3-layered-bouquet": "Event Decor",
    "organic-grab-n-go": "Event Decor",
    "7-epic-column": "Event Decor",
}

SHOP_GROUPS = {"Bouquets", "Columns", "Ready-Made"}
EVENT_DECOR_GROUP = "Event Decor"

ITEM_GROUPS_TO_ENSURE = ["Bouquets", "Columns", "Ready-Made", "Event Decor"]


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


def insert_doc(opener, doc, label):
    payload = json.dumps({"doc": doc}).encode()
    req = urllib.request.Request(
        f"{BASE}/api/method/frappe.client.insert",
        data=payload,
        headers={"Content-Type": "application/json", "X-Requested-With": "XMLHttpRequest"},
    )
    try:
        with opener.open(req, timeout=30) as r:
            return json.loads(r.read().decode()).get("message", {}).get("name"), False
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        if "already exists" in body or "DuplicateEntryError" in body:
            return None, True
        raise SystemExit(f"[{label}] insert failed: HTTP {e.code} body={body[:300]}")


def set_value(opener, doctype, name, fieldname, value):
    payload = json.dumps(
        {"doctype": doctype, "name": name, "fieldname": fieldname, "value": value}
    ).encode()
    req = urllib.request.Request(
        f"{BASE}/api/method/frappe.client.set_value",
        data=payload,
        headers={"Content-Type": "application/json", "X-Requested-With": "XMLHttpRequest"},
    )
    with opener.open(req, timeout=20) as r:
        return json.loads(r.read().decode())


def ensure_item_groups(opener):
    print("\n[item-groups] ensuring 4 groups exist")
    for group in ITEM_GROUPS_TO_ENSURE:
        _, was_dup = insert_doc(
            opener,
            {
                "doctype": "Item Group",
                "item_group_name": group,
                "parent_item_group": PARENT_ITEM_GROUP,
                "is_group": 0,
                "show_in_website": 1,
            },
            group,
        )
        print(f"  [{'skip' if was_dup else 'new '}] {group}")


def reassign_items(opener):
    print("\n[items] reassigning Item.item_group + Website Item.item_group")
    moved_s, moved_e, skipped = 0, 0, 0
    unpublished = 0

    for slug, target_group in ASSIGNMENTS.items():
        # Item.item_group
        item = api_get(opener, f"/api/resource/Item/{slug}").get("data", {})
        current_group = item.get("item_group")
        if current_group != target_group:
            set_value(opener, "Item", slug, "item_group", target_group)
            print(f"  [item]      {slug:42s}  {current_group} -> {target_group}")
            if target_group in SHOP_GROUPS:
                moved_s += 1
            else:
                moved_e += 1
        else:
            skipped += 1

        # Website Item.item_group + published flag
        wi_list = api_get(
            opener,
            f'/api/resource/Website Item?filters=[["item_code","=","{slug}"]]&fields=["name","item_group","published"]',
        ).get("data", [])
        if not wi_list:
            print(f"  [warn]      {slug:42s}  no Website Item — skipping")
            continue
        wi = wi_list[0]
        wi_name = wi["name"]

        if wi.get("item_group") != target_group:
            set_value(opener, "Website Item", wi_name, "item_group", target_group)

        # Event Decor items get unpublished from the storefront
        target_published = 0 if target_group == EVENT_DECOR_GROUP else 1
        if wi.get("published") != target_published:
            set_value(opener, "Website Item", wi_name, "published", target_published)
            if target_published == 0:
                unpublished += 1
                print(f"  [unpub]     {slug:42s}  Event Decor — removed from shop")

    print(
        f"\n[summary] Moved to Shop: {moved_s} / Moved to Event Decor: {moved_e} / "
        f"Already correct: {skipped} / Unpublished from shop: {unpublished}"
    )


def main():
    opener = make_opener()
    login(opener)
    ensure_item_groups(opener)
    reassign_items(opener)
    print()
    print(f"OK -> {BASE}/shop")
    print(f"OK -> {BASE}/all-products (still works; now shows only Shop items)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
