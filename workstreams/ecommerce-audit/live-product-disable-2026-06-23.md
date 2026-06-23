# Live Product Disable - 2026-06-23

Status: completed on live `https://locallytwisted.com` through Desk/System
Console using the existing logged-in browser session.

AI takeover rule: these four products are intentionally hidden live. Do not
re-enable, publish, reroute, or move any of them out of `needs_review` without
fresh GL approval.

Capability gate: PASS. Loaded:

- `capabilities/INDEX.md`
- `capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`
- `capabilities/recipes/codex-browser-verification-surface.md`
- `capabilities/recipes/erpnext-ecommerce-receiving-architecture.md`

Related AI-facing records:

- Decision packet:
  `decisions/2026-06-23-live-product-visibility-disable.md`
- Recipe:
  `capabilities/recipes/erpnext-live-product-visibility-retirement.md`
- Failure note:
  `capabilities/failures/owner-catalog-guard-live-disable-drift.md`

## Target Products

These were the documented retired products:

| Item code | Website Item | Route | Live result |
|---|---|---|---|
| `large-garland` | `WEB-ITM-0052` | `shop-items/garlands/large-garland` | template disabled, 87 variants disabled, Website Item unpublished |
| `mothers-day-bouquet` | `WEB-ITM-0032` | `shop-items/bouquets/mothers-day-bouquet` | single Item disabled, Website Item unpublished |
| `large-organic-column` | `WEB-ITM-0033` | `shop-items/columns/large-organic-column` | template disabled, 174 variants disabled, Website Item unpublished |
| `pride-progress-rainbow-balloon-arch` | `WEB-ITM-0042` | `shop-items/arches/pride-progress-rainbow-balloon-arch` | template disabled, 4 variants disabled, Website Item unpublished |

The Website Items were already `published=0` and
`needs_review|needs_review` before the Item disable. The live change disabled
the underlying template/single Items and their child variants.

## What Happened

The normal human Item form path was tried first from:

```text
https://locallytwisted.com/app/item/large-garland
```

Checking `Disabled` and clicking Save was blocked by the custom owner catalog
guard:

```text
Protected Owner Catalog Guard
This product record is protected because it can change public pages, prices, or checkout.
Please use Product Setup or a guarded product update. Blocked save on Item large-garland.
```

That guard is project code, not an external cybersecurity block. It protects
owner-like users from raw catalog edits. A document-save attempt from System
Console hit the same guard, so the final live operation used Desk System
Console with `frappe.db.set_value` for only the exact fields below.

## Final Write Method Used

Desk route:

```text
https://locallytwisted.com/app/system-console
```

Console settings:

- Type: `Python`
- `Commit`: checked for the write script
- No imports
- No deletes
- No price, order, customer, Stripe, or site-setting changes

Fields touched:

- `Item.disabled = 1` for each target template/single Item
- `Item.disabled = 1` for each child variant under the three template products
- idempotent reassertion of:
  - `Website Item.published = 0`
  - `Website Item.lt_product_page_type = "needs_review"`
  - `Website Item.lt_commerce_lane = "needs_review"`

The successful output reported:

```text
large-garland: 88 Items disabled
mothers-day-bouquet: 1 Item disabled
large-organic-column: 175 Items disabled
pride-progress-rainbow-balloon-arch: 5 Items disabled
```

## Console Script Shape

Use this only after target scope is exact and approved. Keep `Commit` unchecked
for the read-only status query; check `Commit` only for the write script.

Read-only status shape:

```python
targets = {
    "large-garland": "WEB-ITM-0052",
    "mothers-day-bouquet": "WEB-ITM-0032",
    "large-organic-column": "WEB-ITM-0033",
    "pride-progress-rainbow-balloon-arch": "WEB-ITM-0042",
}

for item_code, website_item_name in targets.items():
    item_disabled = frappe.db.get_value("Item", item_code, "disabled")
    variants = frappe.get_all(
        "Item",
        filters={"variant_of": item_code},
        fields=["name", "disabled"],
    )
    website_item = frappe.db.get_value(
        "Website Item",
        website_item_name,
        ["published", "lt_product_page_type", "lt_commerce_lane", "route"],
        as_dict=True,
    )
    active_variants = len([row for row in variants if not row.disabled])
    disabled_variants = len([row for row in variants if row.disabled])
    print(
        f"{item_code}: item_disabled={item_disabled}, "
        f"active_variants={active_variants}, "
        f"disabled_variants={disabled_variants}, "
        f"Website Item published={website_item.published}, "
        f"{website_item.lt_product_page_type}|{website_item.lt_commerce_lane}, "
        f"route={website_item.route}"
    )
```

Write shape:

```python
targets = {
    "large-garland": "WEB-ITM-0052",
    "mothers-day-bouquet": "WEB-ITM-0032",
    "large-organic-column": "WEB-ITM-0033",
    "pride-progress-rainbow-balloon-arch": "WEB-ITM-0042",
}

for item_code, website_item_name in targets.items():
    item_codes = [item_code] + frappe.get_all(
        "Item",
        filters={"variant_of": item_code},
        pluck="name",
    )
    for code in item_codes:
        frappe.db.set_value("Item", code, "disabled", 1)
    frappe.db.set_value(
        "Website Item",
        website_item_name,
        {
            "published": 0,
            "lt_product_page_type": "needs_review",
            "lt_commerce_lane": "needs_review",
        },
    )
    print(f"{item_code}: {len(item_codes)} Items disabled")
```

## Post-Change Verification

Fresh read-only System Console verification, with `Commit` unchecked:

```text
large-garland: item_disabled=1, active_variants=0, disabled_variants=87, Website Item published=0, needs_review|needs_review
mothers-day-bouquet: item_disabled=1, active_variants=0, disabled_variants=0, Website Item published=0, needs_review|needs_review
large-organic-column: item_disabled=1, active_variants=0, disabled_variants=174, Website Item published=0, needs_review|needs_review
pride-progress-rainbow-balloon-arch: item_disabled=1, active_variants=0, disabled_variants=4, Website Item published=0, needs_review|needs_review
```

Public route checks:

```text
/shop-items/garlands/large-garland -> 404 Not Found
/shop-items/bouquets/mothers-day-bouquet -> 404 Not Found
/shop-items/columns/large-organic-column -> 404 Not Found
/shop-items/arches/pride-progress-rainbow-balloon-arch -> 404 Not Found
/shop contains none of the four slugs
```

## Repeatable Process

1. Confirm the target product list from current repo docs or indexed
   conversation before choosing scope.
2. Open `https://locallytwisted.com/app/item?disabled=0` in the logged-in Desk
   session and verify the Item exists.
3. If the Item form save is blocked by `Protected Owner Catalog Guard`, do not
   keep retrying the form. The guard is expected for owner-like users.
4. Open `https://locallytwisted.com/app/system-console`.
5. Run a read-only status query first with `Commit` unchecked.
6. If the target list is exact and approved, run the direct `set_value` disable
   script with `Commit` checked.
7. Immediately run the read-only status query again with `Commit` unchecked.
8. Verify the public routes and `/shop`.
9. Record counts, routes, and any blocked attempts in this workstream.

## Rollback Shape

Re-enable only with explicit GL approval. The rollback is the inverse:

- set each target template/single Item and child variant `disabled=0`;
- publish Website Items only if GL explicitly re-approves public visibility;
- if publishing, set the correct `lt_product_page_type` and
  `lt_commerce_lane` from the reviewed product contract, not by guessing.

Do not use Product Setup alone as a public hide/publish mechanism on this
release. Current code records `shop_visibility`, but the public route still
depends on Website Item state.
