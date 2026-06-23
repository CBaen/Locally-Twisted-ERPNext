---
id: erpnext-live-product-visibility-retirement
name: ERPNext Live Product Visibility Retirement
schema_version: 2.1
profile: foundation
level: recipe
maturity: candidate
scope: Locally Twisted live ERPNext product visibility retirement
currently_true: true
last_verified: 2026-06-23
tags:
  - locally-twisted
  - erpnext
  - frappe
  - ecommerce
  - catalog
  - live
  - product-visibility
  - fail-loud
---

# ERPNext Live Product Visibility Retirement

## What It Does

Retires approved LT products from live public visibility without changing
prices, orders, customers, payment settings, DNS, Frappe Cloud release
settings, or unrelated catalog records.

Use this for narrow live product hide/disable work when GL has already approved
the exact product list.

## Current Contract

The durable hidden state for an approved retired product is:

- target template/single `Item.disabled = 1`;
- child variant `Item.disabled = 1` when the product has variants;
- target `Website Item.published = 0`;
- `Website Item.lt_product_page_type = "needs_review"`;
- `Website Item.lt_commerce_lane = "needs_review"`;
- public product route returns `404`;
- `/shop` does not contain the retired slug.

Do not publish, re-enable, reroute, or relabel retired products without fresh
GL approval.

## Workflow

1. Run the capability context gate from the LT repo root with this recipe plus
   the relevant live/provider recipe.
2. Confirm the target list from current GL instruction, current repo docs, or
   indexed conversation evidence. Do not choose product scope from stale
   counts or old manifests.
3. Open the logged-in live Desk list:
   `https://locallytwisted.com/app/item?disabled=0`.
4. Try the normal human Item form only as the first path. If `Protected Owner
   Catalog Guard` blocks the save, treat that as expected LT project behavior,
   not an external cybersecurity issue.
5. Do not disable or weaken the owner catalog guard.
6. Use Desk System Console only for the exact approved fields and exact target
   records. Run a read-only status query first with `Commit` unchecked.
7. If the target list and read-only state are correct, run the scoped
   `frappe.db.set_value` write with `Commit` checked.
8. Immediately rerun the read-only status query with `Commit` unchecked.
9. Verify the public product routes and `/shop`.
10. Record the target list, counts, blocked path, final write shape, and route
    proof in a feature handoff.

## 2026-06-23 Verified Use

Live handoff:
`../../workstreams/ecommerce-audit/live-product-disable-2026-06-23.md`.

The successful live write disabled:

- `large-garland`: template plus 87 variants.
- `mothers-day-bouquet`: single Item, no variants.
- `large-organic-column`: template plus 174 variants.
- `pride-progress-rainbow-balloon-arch`: template plus 4 variants.

All four Website Items remained unpublished and held at
`needs_review|needs_review`. Their public product routes returned `404`, and
`/shop` did not contain the four slugs.

## Failure Modes

- Treating `Protected Owner Catalog Guard` as an external cybersecurity issue.
- Retrying the same blocked Item form instead of moving to the approved admin
  maintenance path.
- Disabling the guard to make a one-time change easier.
- Using Product Setup alone and assuming the public route will hide.
- Publishing or re-enabling a retired product from old product-count pressure.
- Touching price, Stripe, order, customer, site setting, route, or DNS records
  during a product visibility retirement.

## Verification

Minimum proof:

- read-only live Desk/System Console status before and after;
- target root Item disabled;
- target variants disabled and `active_variants=0`;
- Website Item unpublished and `needs_review|needs_review`;
- product routes return `404`;
- `/shop` returns `200` and does not contain the target slugs.

Use browser proof when rendered state matters. For direct route availability,
HTTP and HTML checks are acceptable if they hit `https://locallytwisted.com`
after the live write.
