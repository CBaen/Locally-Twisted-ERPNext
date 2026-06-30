# Phase 0 Incident Audit - Large head Missionary

Date: 2026-06-30

Status: incident audit with public GET-only evidence, source review, local read-only DB snapshot evidence, and authenticated live read-only API proof. This does not approve repair and does not authorize mutation, cache clearing, deploy, payment/provider action, or customer-message behavior.

## Product

- Public route: `https://locallytwisted.com/shop-items/bouquets/large-head-missionary`
- Template item code in public runtime: `large-head-missionary`
- Public title/H1: `Large head Missionary`
- Public route category: `bouquets`

## Proof Mode

This audit used:

- public GET-only route capture;
- optional public GET-only Product Setup/variant-media API reads;
- local read-only DB snapshot from the LT Docker workshop;
- authenticated live read-only ERPNext API reads through a temporary Frappe Cloud site session;
- local source review of resolver paths.

This audit did not use:

- authenticated Desk access;
- cache clear;
- POST cart/variant selector/checkout calls;
- ERPNext writes;
- payment/provider/DNS/Frappe Cloud changes;
- deployment.

## Public Route Evidence

Read-only helper:

```bash
python scripts/dev/lt_readonly_product_audit.py \
  --output /tmp/lt-large-head-missionary-public-main-v2.json
```

Observed:

| Field | Value |
|---|---|
| HTTP status | `200` |
| Server | `Frappe Cloud` |
| `x-page-name` | `shop-items/bouquets/large-head-missionary` |
| `x-from-cache` | `False` |
| Request id | `79bf0a3c-3575-4259-b989-4663013dd84d` |
| H1 | `Large head Missionary` |
| Extracted price strings | `$15`, `$50`, `$175.00` |
| Embedded Product Setup schema | Present |
| Embedded Product Setup source | `lt_product_setup` |
| Embedded Product Setup status | `Local Preview Ready` |
| Embedded Product Setup base price | `125.0` |
| Runtime commerce lane | `checkout` |
| Runtime checkout allowed | `true` |
| SKU-defining groups | `3` |
| Variant combinations | `30` |

Optional public API GET run:

```bash
LT_READONLY_PRODUCT_AUDIT_ENABLE_API_GETS=1 \
LT_READONLY_PRODUCT_AUDIT_API_BASE_URL=https://locallytwisted.com \
python scripts/dev/lt_readonly_product_audit.py \
  --output /tmp/lt-large-head-missionary-public-api-main-v2.json
```

Observed:

| API | Status | Content Type |
|---|---:|---|
| Product Setup schema | `200` | `application/json` |
| Variant media | `200` | `application/json` |

## Incident Finding

The public page proves split product authority:

- Product Setup runtime exposes `commerce.base_price: 125.0`.
- The same customer-facing route exposes `$175.00` in public HTML.
- The product is rendered as checkout-oriented, with `commerce_lane: "checkout"` and `checkout_allowed: true`.
- The runtime expects three SKU-defining axes and 30 variant combinations.

This means a human-visible Product Setup/base-price value can differ from the sellable customer-facing price path. That matches the owner concern: a backend-visible product value can be saved without becoming the live sellable customer value.

## Local DB Snapshot Finding

Local read-only helper:

```bash
python scripts/dev/lt_readonly_product_db_snapshot.py \
  --output /tmp/lt-large-head-missionary-db-snapshot.json
```

Observed locally:

| Row Group | Local Evidence |
|---|---|
| Website Item | `WEB-ITM-0039`, published, route `shop-items/bouquets/large-head-missionary`, image `/files/large-head-missionary.png` |
| Product Setup | one record named `large-head-missionary`, `publish_status: Local Preview Ready`, `ready_for_live: 0`, `base_price: 175.0` |
| Template Item | `large-head-missionary`, enabled, variant template, sales item, non-stock item |
| Variant Items | 30 enabled variants |
| Item Prices | 30 `Standard Selling` prices, each `175.0` |
| Product Setup price rows | 30 exact checkout price rows, each `175.0` |
| Product Setup options | three SKU-defining selected-option axes: `Missionary`, `skin color`, `Hair color` |

Local interpretation:

- local Product Setup base price, local Product Setup exact price rows, and local Item Prices agree at `175.0`;
- live public embedded Product Setup still reports `commerce.base_price: 125.0`;
- the live customer page and shop listing still expose `$175.00` as the sellable starting price.

This narrows the unresolved issue. The local workshop is internally price-consistent, while the hosted public page exposes a different Product Setup base price. That makes hosted/live row drift, a live-only owner edit, a stale live Product Setup row, or release/app-mirror mismatch stronger candidates than a local Product Setup-vs-Item Price split.

## Current Cause Classification

| Cause Category | Status | Evidence |
|---|---|---|
| Wrong field edited | Closed mechanically | The owner edited Product Setup fields; live Product Setup base price and 30 Product Setup price rows are `125.0`. |
| Wrong doctype edited | Confirmed as Product Setup vs public authority split | Owner edited `LT Product Blueprint`; public price/copy currently resolve from `Item Price` and Website Item fields. |
| Wrong price row | Confirmed | Live Product Setup price rows are `125.0`; live sellable `Item Price` rows are still `175.0`. |
| Inactive Product Setup | Contributing design issue, not save failure | Live Product Setup status is `Local Preview Ready`, `ready_for_live: 0`, but it is still embedded into the public Product Setup schema. |
| Duplicate Product Setup | Not primary current cause | Live exact record `large-head-missionary` saved correctly; brand-lane uniqueness can still be proven before broad repair. |
| Stale seed copy | Unresolved | Need row timestamps and source/fixture comparison |
| Cache | Not supported as root cause from current evidence | Public route returned `x-from-cache: False`; no cache clear was run |
| Deployment/live data drift | Not primary for this owner save | Live Product Setup reflects the owner edit; live Item Price and Website Item public-copy fields did not change because they are separate authorities. |

Current best classification: **owner save succeeded into Product Setup, but Product Setup is not the current write-through authority for public/sellable price or server-rendered public copy**.

## Source Resolver Evidence

Local source review supports why the split can happen:

- `/shop` reads published Website Items and joins Item Price for listing price, then applies variant starting price logic.
- Cart resolution requires an enabled Item, published Website Item, checkout commerce lane, and Standard Selling Item Price.
- Product Setup schema can be embedded into the product page and expose base price/configuration data without itself proving sellable Item Price authority.
- Variant selector/cart/checkout proof requires POST paths or authenticated/local test proof and was intentionally not run in this GET-only Phase 0 public audit.

## Authority Packet

The first non-mutating authority packet is:

- [authority-packet-large-head-missionary.md](authority-packet-large-head-missionary.md)

The reusable template is:

- [authority-matrix-template.md](authority-matrix-template.md)

Those files classify public/source facts separately from DB/Desk unknowns.

## Blockers

| Blocker | Category | Blocks | Required Next Proof |
|---|---|---|---|
| Owner-saved Product Setup row is confirmed, but public price authority did not update. | Not safe to sell yet | Claiming Product Setup edits reliably control live customer price | Build owner publish/apply contract or direct Product Setup runtime authority |
| Product Setup status is `Local Preview Ready` while public schema still embeds it. | Waiting for design decision | Claiming backend save should publish live | Define save vs publish semantics and make them visible/fail-loud |
| Live sellable Item Prices stayed at `175.0`. | Waiting for repair design | Cart/listing/checkout price parity | Build no-write preview, rollback target, and Product Setup-to-Item Price parity verifier before mutation |
| Public copy renders Website Item fields, not Product Setup top-level copy. | Waiting for decision | Owner copy-edit confidence | Decide Website Item vs Product Setup copy authority and projection path |
| Cart/checkout proof was not run. | Waiting for proof | Checkout-ready closeout | Non-mutating cart API proof or approved local/test proof in a later slice |
| Rollback target is absent. | Developer help required | Any repair mutation | Row-level pre-change snapshot before mutation |

## Next Safe Step

Next safe steps are design and no-write repair planning, not immediate live mutation:

- capture a rollback target for live Product Setup, Website Item, Item, Item Price, media, and copy rows;
- decide whether Product Setup becomes direct runtime authority or explicit publish/apply authority;
- build a no-write preview that shows exactly which customer-facing rows would change;
- build a fail-loud parity verifier for Product Setup price/copy vs public/sellable authority;
- only then design the approved repair path.

Local read-only helper prepared for an approved local/authenticated site:

```bash
python scripts/dev/lt_readonly_product_db_snapshot.py \
  --output /tmp/lt-large-head-missionary-db-snapshot.json
```

This helper is SELECT/read-only through local `bench execute frappe.get_all`. It fails if the local LT backend container is unavailable and does not connect to Frappe Cloud live.

Stop before any write, cache clear, repair, deploy, or payment/provider action.
