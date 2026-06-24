---
name: Product primary media attachment drift
type: failure
failure_kind: recurring_pattern
schema_version: 0.1
date_discovered: 2026-06-24
last_updated: 2026-06-24
status: guarded
scope: project
owner_context: Locally Twisted ERPNext product pages and homepage merchandising
related_capabilities:
  - ../recipes/frappe-product-page-company-first.md
  - ../recipes/homepage-launch-proof-contract.md
related_failures:
  - product-gallery-projection-regression.md
  - owner-catalog-guard-live-disable-drift.md
tags:
  - locally-twisted
  - erpnext
  - webshop
  - media
  - product-page
  - homepage
  - file-attachment
  - owner-catalog-guard
---

# Failure Recipe: Product Primary Media Attachment Drift

## Symptom

A product's gallery or Product Setup media looks corrected in Desk, but the
public product page, SEO image, or homepage merchandising card still renders
an old main image.

## Trigger Conditions

- A user deletes or changes a visible gallery photo in Desk and expects the
  product main image to change.
- `Website Item.website_image`, underlying `Item.image`, and
  `LT Product Blueprint.primary_image` are not checked together.
- A public file URL exists, but the image has no `File` row attached to the
  target `Website Item`.
- Direct owner/API saves are blocked by LT's protected owner catalog guard.
- Public homepage cards are cached/rendered from the Website Item image while
  Product Setup gallery rows already look clean.

## Known Instances

| Date | Project | Surface | Bad outcome | Evidence | Guard state | Status |
|---|---|---|---|---|---|---|
| 2026-06-24 | Locally Twisted | Birthday Deliveries product page and homepage Customer Favorites | Backend gallery rows omitted `/files/birthday-deliveries.png`, but live product metadata/main image and homepage card still used the old PNG because primary image fields and File attachment were stale | `workstreams/live-homepage-birthday-media-repair-2026-06-24.md`; decision `decisions/2026-06-24-live-homepage-birthday-media-repair.md` | primary media/File attachment guard documented | guarded |

## Root Pattern

ERPNext product media has separate meanings:

- gallery/slideshow media;
- Website Item primary image;
- underlying Item image;
- Product Blueprint primary image;
- File attachment validation;
- public product-page metadata/runtime JSON;
- homepage or other merchandising references.

Cleaning one layer can make Desk look fixed while the public main image remains
wrong.

## Required Guard

For product primary-media changes, prove all relevant layers:

1. `Website Item.website_image` points to the approved image.
2. underlying `Item.image` points to the approved image.
3. `LT Product Blueprint.primary_image` points to the approved image when the
   product has a blueprint.
4. A `File` row exists for the approved image and is attached to the Website
   Item when Website Item validation expects it.
5. Old image rows are absent from gallery/slideshow tables when they should no
   longer be page-rendered.
6. Fresh public product HTML references the approved image in metadata, Open
   Graph/Twitter image metadata, main image markup, and runtime JSON.
7. Fresh public homepage/card HTML references the approved image if the product
   is merchandised outside its product page.

## Recovery Recipe

1. Read the current live public HTML first; count old and new image references.
2. Inspect Website Item, Item, Product Blueprint, Website Slideshow, and File
   rows before writing.
3. If direct saves are blocked by the owner catalog guard, do not disable the
   guard.
4. Prefer a source-owned idempotent patch/release when the Frappe Cloud path is
   healthy.
5. If GL approved an urgent live repair and release is blocked, use a scoped
   admin maintenance/System Console path that writes only the named fields and
   records.
6. Re-verify public product page and homepage HTML after cache clears or route
   refresh.

## What Not To Do

- Do not treat Product Setup gallery rows as proof of the public main image.
- Do not treat a public file URL as proof the File row/attachment exists.
- Do not globally delete uploaded files when the user only requested removal
  from a page.
- Do not weaken the owner catalog guard to make raw saves easier.
- Do not claim source patch or app mirror push is live proof without public
  route evidence.

## Cross-links

- `../../workstreams/live-homepage-birthday-media-repair-2026-06-24.md`
- `../../decisions/2026-06-24-live-homepage-birthday-media-repair.md`
- `../recipes/frappe-product-page-company-first.md`
- `../recipes/homepage-launch-proof-contract.md`
- `product-gallery-projection-regression.md`
- `owner-catalog-guard-live-disable-drift.md`

## Evidence Quality

Verified live on 2026-06-24 through public `locallytwisted.com` route checks,
live product-page HTML, live homepage HTML, backend record inspection, and
hash match between GL's supplied local WebP and the live uploaded WebP.
