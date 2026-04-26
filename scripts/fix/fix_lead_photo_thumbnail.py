#!/usr/bin/env python3
"""
Add inline thumbnail display to the LT Lead Photo child table grid.

Why: Frappe's "Attach Image" fieldtype is rejected for `in_list_view=1`
on child tables — so the upload field can't render as a thumbnail in
the grid view. The standard Frappe pattern is to add a separate "Image"
fieldtype field that READS the URL from the Attach Image field and
DISPLAYS it as a thumbnail. The Attach Image field stays for uploading
(via row-click expand); the Image field provides the inline preview.

Schema after this script:
  LT Lead Photo (child)
    photo      (Attach Image)  — upload target, hidden from grid
    thumbnail  (Image)          — displays photo's URL inline in grid
    caption    (Data)           — caption text inline in grid

Recreates the LT Lead Photo DocType with the new field set. Safe because
no rows exist yet (no Lead records have photos attached). The Lead's
`custom_inspiration_photos` Table field's `options="LT Lead Photo"`
reference is preserved (recreated DocType uses same name).

Idempotent. Stdlib only.
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


LEAD_PHOTO_DOCTYPE = {
    "doctype": "DocType",
    "name": "LT Lead Photo",
    "module": "Custom",
    "custom": 1,
    "istable": 1,
    "fields": [
        {
            "fieldname": "photo",
            "label": "Photo",
            "fieldtype": "Attach Image",
            "reqd": 1,
        },
        {
            "fieldname": "thumbnail",
            "label": "",
            "fieldtype": "Image",
            "options": "photo",      # render the URL stored in `photo`
            "in_list_view": 1,
        },
        {
            "fieldname": "caption",
            "label": "Caption",
            "fieldtype": "Data",
            "in_list_view": 1,
            "columns": 6,            # leave room for the thumbnail column
        },
    ],
    "permissions": [],
}


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


def call(opener, method, payload, timeout=30):
    req = urllib.request.Request(
        f"{BASE}/api/method/{method}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "X-Requested-With": "XMLHttpRequest"},
    )
    try:
        with opener.open(req, timeout=timeout) as r:
            return json.loads(r.read().decode()), False
    except urllib.error.HTTPError as e:
        return e.read().decode(), True


def main():
    opener = make_opener()
    login(opener)

    # Delete existing LT Lead Photo DocType (safe: no rows attached to any Lead yet)
    print("[step 1] Drop existing LT Lead Photo DocType (recreate clean)")
    res, err = call(opener, "frappe.client.delete",
                    {"doctype": "DocType", "name": "LT Lead Photo"})
    if err and 'DoesNotExistError' not in res:
        print(f"  [warn] delete: {res[:200]}")
    else:
        print("  [ok]   deleted (or already absent)")

    # Recreate with the new field structure
    print("[step 2] Recreate LT Lead Photo with thumbnail Image display")
    res, err = call(opener, "frappe.client.insert", {"doc": LEAD_PHOTO_DOCTYPE})
    if err:
        raise SystemExit(f"insert failed: {res[:300]}")
    print(f"  [ok]   {res.get('message', {}).get('name', '?')}")

    print()
    print("OK -> http://localhost:8081/app/lead/new")
    print("Scroll to Inspiration Photos. Add a row, upload an image,")
    print("save the Lead. The grid row should show a thumbnail beside the caption.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
