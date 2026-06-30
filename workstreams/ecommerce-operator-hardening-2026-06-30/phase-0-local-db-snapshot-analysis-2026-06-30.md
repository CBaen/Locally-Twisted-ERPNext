# Phase 0 Local DB Snapshot Analysis - Large head Missionary

Date: 2026-06-30

Status: local-only read-only DB analysis. This is not live proof, not repair approval, and not deployment approval.

Input:

- `/tmp/lt-large-head-missionary-db-snapshot.json`

Snapshot contract:

- `read_only: true`
- failures: none
- source: local LT Docker workshop, site `frontend`
- no ERPNext writes, no cache clear, no deploy, no payment/provider action

## Local Snapshot Summary

| Row Group | Count |
|---|---:|
| Website Item | 1 |
| Template Item | 1 |
| Variant Items | 30 |
| Item Prices | 30 |
| Item Variant Attribute rows | 93 |
| Product Setup records | 1 |
| Product Setup option rows | 3 |
| Product Setup price rows | 30 |
| Product Setup media rules | 15 |
| Product Setup gallery rows | 1 |
| File rows by URL | 31 |
| File rows by attachment | 48 |

## Local Row Findings

| Area | Local Read-Only Evidence |
|---|---|
| Website Item | `WEB-ITM-0039`, item code `large-head-missionary`, published `1`, route `shop-items/bouquets/large-head-missionary`, image `/files/large-head-missionary.png`, slideshow `LT Product Gallery - large-head-missionary`, modified `2026-05-24 16:42:45.556169` by `Administrator` |
| Template Item | `large-head-missionary`, enabled, has variants, sales item, non-stock item, image `/files/large-head-missionary.png`, modified `2026-05-17 16:09:50.270338` by `Administrator` |
| Variant Items | 30 enabled variants, all under `large-head-missionary` |
| Item Prices | 30 `Standard Selling` prices, all `USD`, UOM `Nos`, selling `1`, each `175.0` |
| Product Setup | one record named `large-head-missionary`, `publish_status: Local Preview Ready`, `validation_status: Ready For Local Preview`, `ready_for_live: 0`, `base_price: 175.0`, target item `large-head-missionary`, target Website Item `WEB-ITM-0039`, modified `2026-05-22 13:54:26.463965` by `Administrator` |
| Product Setup options | three SKU-defining selected-option axes: `Missionary`, `skin color`, `Hair color` |
| Product Setup price rows | 30 exact checkout price rows, each `175.0`, mapped to the 30 variant item codes |
| Product Setup add-ons | none captured |
| Product Setup media rules | 15 exact-variant selected-photo rules, all `approved_for_customer: 0` |
| Product Setup gallery | one approved customer gallery image `/files/large-head-missionary--extra-01.png` |

## Important Interpretation

Local DB proof narrows the product model:

- local Product Setup base price is `175.0`;
- local Product Setup exact price rows are all `175.0`;
- local Standard Selling Item Prices are all `175.0`;
- local public/customer price authority is internally consistent for price.

But live public proof still shows embedded Product Setup `commerce.base_price: 125.0` on `https://locallytwisted.com/shop-items/bouquets/large-head-missionary`.

Therefore the current strongest finding is not "local Product Setup and Item Prices disagree." It is:

**local authority and live public embedded Product Setup authority disagree.**

That can mean live data drift, stale live Product Setup row, a live-only owner edit, a deployment/app-mirror mismatch, or another hosted resolver difference. Local proof cannot choose among those.

## Blockers Closed Locally

Closed for local-only evidence:

- Website Item row identity.
- Template Item row identity.
- 30 enabled variant Items.
- 30 Standard Selling Item Prices at `175.0`.
- one local Product Setup record.
- local Product Setup exact price rows at `175.0`.
- local Product Setup active uniqueness by target item/slug, pending brand-lane field availability.
- local row-level rollback inventory for captured rows.

## Blockers Still Open For Live

Still open:

- exact hosted/live Product Setup row values;
- exact hosted/live Item Price rows;
- exact backend row and field changed by the owner;
- hosted/live `modified` and `modified_by`;
- hosted/live Product Setup active uniqueness;
- hosted/live file/gallery/media rows;
- hosted/live historical order/document/payment dependencies;
- whether live public `125.0` is a current live DB value, stale published artifact, or release/app-mirror drift.

## Next Safe Step

Authenticated live read-only DB/Desk proof is now required. It should compare the same row groups captured locally:

- Website Item;
- Product Setup and child rows;
- template Item;
- variant Items;
- Item Variant Attribute rows;
- Item Prices;
- File/media/gallery rows;
- `modified`/`modified_by`.

Stop before repair, cache clear, deploy, migration, or payment/provider action.
