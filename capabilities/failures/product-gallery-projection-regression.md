---
name: Product gallery projection regression
type: failure
failure_kind: recurring_pattern
schema_version: 0.1
date_discovered: 2026-05-22
last_updated: 2026-05-22
status: guarded
scope: project
owner_context: Locally Twisted ERPNext ecommerce
related_capabilities:
  - erpnext-ecommerce-receiving-architecture
related_failures:
  - variant-media-overgating-regression
tags:
  - ecommerce
  - media
  - gallery
  - webshop
  - product-setup
---

# Failure Recipe: Product Gallery Projection Regression

## Symptom

Product pages have source-approved additional photos or native `Website
Slideshow` rows, but the customer-facing product route renders only the primary
image or only selected-variant image behavior.

## Trigger Conditions

- Source extra media is globally held instead of role-classified.
- Product Setup gallery rows are not projected into native ERPNext Website
  Slideshow rows.
- `Website Item.slideshow` is empty after Product Setup sync/apply.
- The product image template chooses a generic Webshop `slides` fallback before
  the LT slideshow helper, so one-extra or projected-gallery routes render no
  thumbnail rail.
- Published checkout Product Setups stay `Draft`, so active Product Setup
  runtime media is unavailable and approved simple product photos disappear
  from the gallery rail.

## Known Instances

| Date | Project | Surface | Bad outcome | Evidence | Guard state | Status |
|---|---|---|---|---|---|---|
| 2026-05-22 | Locally Twisted | Product pages | DB/source gallery media existed in parts of the system, but product pages did not consistently render additional-photo thumbnails | `workstreams/ecommerce-audit/product-gallery-restoration-2026-05-22.md`; `scripts/verify/product_gallery_projection_contract.py`; `scripts/verify/product_gallery_experience.spec.js` | source/Product Setup/slideshow/render guards added | guarded |

## Root Pattern

The system had three separate media meanings but treated them as one vague
"extra images" bucket. That made it easy to either hold everything or prove
only the DB projection while missing rendered route behavior.

## Required Guard

Gallery work must prove all four layers:

1. Source-approved `gallery` media exists after dedupe.
2. Product Setup owns approved gallery rows.
3. Native ERPNext Website Slideshow records are linked to Website Items.
4. Product pages render the thumbnail rail in the browser.

Current guards:

- `python scripts/verify/product_gallery_projection_contract.py`
- `npm run test:product-gallery-experience`
- `python scripts/verify/product_page_media_visibility_contract.py`
- `python scripts/verify/product_setup_catalog_coverage.py`

## What Not To Do

- Do not restore galleries by hardcoding product-page images.
- Do not render arbitrary selected variant images as gallery thumbnails.
- Only approved simple checkout exact-variant media may join the standard
  thumbnail set, and only when read through active Product Setup schema.
- Do not render category/reference media as product-gallery media.
- Do not call DB slideshow rows sufficient without route render proof.
- Do not make Webshop fallback `slides` outrank LT Product Setup projection.
- Do not let published checkout Product Setups remain inactive if their media
  or price rules are needed by the public runtime.

## Cross-Links

- Related handoff: `workstreams/ecommerce-audit/product-gallery-restoration-2026-05-22.md`
- Related capability: `capabilities/recipes/erpnext-ecommerce-receiving-architecture.md`
- Related failure: `capabilities/failures/variant-media-overgating-regression.md`
- Related decision: `locally-twisted-decisions.md`
- Related lesson: `lessons-learned.md`

## Evidence Quality

Verified locally against source Odoo export, local ERPNext Product Setup rows,
native Website Slideshow rows, rendered product routes, desktop browser
geometry, mobile gallery behavior, variant media persistence, owner-product
safety, and ecommerce full gates. Live remains unmodified.
