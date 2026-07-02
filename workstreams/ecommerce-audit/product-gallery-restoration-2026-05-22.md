# Product Gallery Restoration - 2026-05-22

Status: local architecture restored and guarded. This is not staging/live
release approval.

2026-05-24 staging follow-up: hosted staging now has the customer-facing
follow-up for removed gallery label copy and base-photo availability after
configured product selection. See
`workstreams/ecommerce-audit/product-gallery-staging-followup-2026-05-24.md`.
Fresh hosted staging proof passed `npm run test:product-gallery-experience`
`4/4` against `https://locallytwisted-staging.frappe.cloud`.

## Scope

Guiding Light reported that product pages no longer showed additional product
photos as the expected left thumbnail gallery. Some images still existed in
source data and/or variant media paths, but the live Frappe projection was
empty or bypassed. This lane restores product-page galleries as architecture,
not as a visual staging patch.

## Kept Architecture

The permanent chain is:

```text
legacy_source/source-approved product gallery media
-> LT Product Blueprint Gallery Image
-> ERPNext Website Slideshow / Website Slideshow Item
-> Website Item.slideshow
-> Webshop product gallery template
```

Media roles are now explicit:

- `gallery`: approved product-page gallery photo; renders in the product
  gallery after Product Setup projection.
- `variant_image`: selected-option media; may update the main image, but does
  not populate the gallery rail.
- `reference`: retained evidence, not rendered in the product gallery.
- `ignored_artifact`: held back and never rendered.

## What Changed

- Added `catalog_contract/gallery_media.py` so legacy_source paired thumbnail/full-size
  URLs dedupe by semantic source key and prefer the best local file.
- Updated the source Product Setup sync to create/update Product Setup gallery
  child rows from source-approved gallery media.
- Added `--apply-gallery` to `scripts/setup/sync_product_blueprints_from_catalog.py`
  so local source files are staged into Docker, copied into Frappe public
  files, attached to the target Item, projected into `Website Slideshow`, and
  linked through `Website Item.slideshow`.
- Updated `product_blueprint_local_apply.py` so the existing guarded Product
  Setup apply path can project gallery rows without granting owner users direct
  raw slideshow mutation.
- Updated media classification/visibility contracts from "all extras held" to
  role-based media: approved source product-gallery images render; variant,
  category, reference, and ignored artifacts stay separate.
- Updated the product image template so LT's projected gallery helper is the
  authority. Webshop `slides` is fallback only, preventing the single-extra
  route class from silently rendering no rail.
- Tightened the product gallery UI: desktop left rail, main image right,
  rail height capped to the main image, internal rail scroll, mobile horizontal
  rail/swipe behavior, compact indicator, and variant selection persistence.

## Current Local Data

After the local write/apply pass:

- `51` Website Items are covered by Product Setup.
- `68` Product Setup approved gallery rows exist for the live Website Item set.
- `47` Website Items have native `Website Slideshow` links.
- `68` Website Slideshow Item rows exist.
- Source classification still sees `53` source products and `70` deduped
  source gallery images because two source slugs, `easter-arch` and
  `pride-arch`, are not current live Website Items in the local catalog.

## Verification

Fresh local proof:

```bash
python scripts/verify/product_page_media_classification_packet.py
python scripts/verify/product_page_media_visibility_contract.py
python scripts/verify/product_setup_catalog_coverage.py
python scripts/verify/product_gallery_projection_contract.py
npm run test:product-gallery-experience
npm run test:owner-product-safety
npm run test:ecommerce-full
```

Observed results:

- Classification packet passed with `70` deduped source gallery images and
  `0` unsafe unclassified images.
- Media visibility passed with `68` approved live gallery images, `47`
  Website Items with slideshows, and `68` Website Slideshow Item rows.
- Product Setup coverage passed with `68` checked gallery rows.
- Product gallery projection passed source -> Product Setup -> slideshow ->
  rendered route checks.
- Browser gallery experience passed `3/3`, including Classic Arch and
  Large Garland as representative product routes.
- Owner product safety and ecommerce full gates passed after gallery gates were
  inserted.

## Boundaries

- This does not approve ERPNext Item Group/category images.
- This does not approve image-rich mega-menu media.
- This does not change live/staging/Frappe Cloud/DNS/Stripe.
- This does not make every product checkout-ready; checkout lanes still belong
  to the product runtime and payment gates.
- Do not delete the role split. Product gallery, selected variant media, and
  category/reference media are different contracts.

## Staging Handoff Note

The local `--apply-gallery` wrapper stages `_resources/catalog-source` into the
Docker container before running the in-app sync. A staging/Frappe Cloud packet
must provide the same source files to the app/site execution environment before
running Product Setup gallery projection. Do not treat the local Docker staging
path as proof that Frappe Cloud already has those files. The staging packet
should rerun `product_gallery_projection_contract.py` against the staging URL
after projection.

## Backlinks

- `research/research-product-gallery-architecture/research-brief.md`
- `ECOMMERCE-SHOP-HANDOFF.md`
- `CODING-HANDOFF.md`
- `locally-twisted-decisions.md`
- `lessons-learned.md`
- `capabilities/failures/product-gallery-projection-regression.md`
- `capabilities/failures/variant-media-overgating-regression.md`
- `workstreams/ecommerce-audit/variant-item-media-restore-2026-05-17.md`
