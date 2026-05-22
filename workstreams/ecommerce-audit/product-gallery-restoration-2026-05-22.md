# Product Gallery Restoration - 2026-05-22

Status: local architecture restored and guarded. This is not staging/live
release approval.

## Scope

Guiding Light reported that product pages no longer showed additional product
photos as the expected left thumbnail gallery. Some images still existed in
source data and/or variant media paths, but the live Frappe projection was
empty or bypassed. This lane restores product-page galleries as architecture,
not as a visual staging patch.

## Kept Architecture

The permanent chain is:

```text
Odoo/source-approved product gallery media
-> LT Product Blueprint Gallery Image
-> ERPNext Website Slideshow / Website Slideshow Item
-> Website Item.slideshow
-> Webshop product gallery template
```

Media roles are now explicit:

- `gallery`: approved product-page gallery photo; renders in the product
  gallery after Product Setup projection.
- `variant_image`: selected-option media; may update the main image, but does
  not populate the gallery rail by default. The narrow exception is simple
  `simple_product|checkout` exact-variant media that is approved for the
  customer and read through active Product Setup schema; that media can join
  the standard product thumbnail set so a product like Mickey Mouse Bouquet has
  its full customer-visible photo set without requiring a size click first.
- `reference`: retained evidence, not rendered in the product gallery.
- `ignored_artifact`: held back and never rendered.

## What Changed

- Added `catalog_contract/gallery_media.py` so Odoo paired thumbnail/full-size
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
- Tightened `get_product_gallery_slides()` after triad review so approved
  simple checkout media is read through active Product Setup schema, not raw
  child-row access. The helper now rejects non-customer, non-exact,
  unpublished-status, and non-simple-checkout media for the gallery rail.
- Promoted published checkout Product Setups to `Local Preview Ready` through
  the catalog sync path. Non-checkout backfills remain Draft until reviewed.

## Current Local Data

After the local write/apply pass:

- `51` Website Items are covered by Product Setup.
- `68` Product Setup approved gallery rows exist for the live Website Item set.
- `47` Website Items have native `Website Slideshow` links.
- `68` Website Slideshow Item rows exist.
- `30` published checkout Product Setups are `Local Preview Ready`.
- `21` non-checkout backfilled Product Setups remain Draft.
- Source classification still sees `53` source products and `70` deduped
  source gallery images because two source slugs, `easter-arch` and
  `pride-arch`, are not current live Website Items in the local catalog.

## Verification

Fresh local proof:

```powershell
python scripts\verify\product_page_media_classification_packet.py
python scripts\verify\product_page_media_visibility_contract.py
python scripts\verify\product_setup_catalog_coverage.py
python scripts\verify\product_gallery_projection_contract.py
npm run test:product-gallery-experience
npm run test:owner-product-safety
npm run test:ecommerce-full
python scripts\verify\ignore_permissions_justification_lint.py
npm run test:interactive-layout -- --grep "contact expanded conditionals fit"
```

Observed results:

- Classification packet passed with `70` deduped source gallery images and
  `0` unsafe unclassified images.
- Media visibility passed with `68` approved live gallery images, `47`
  Website Items with slideshows, and `68` Website Slideshow Item rows.
- Product Setup coverage passed with `68` checked gallery rows.
- Product gallery projection passed source -> Product Setup -> slideshow ->
  rendered route checks.
- Browser gallery experience passed `4/4`, including Classic Arch, Large
  Garland, Mickey Mouse Bouquet's three-photo regression, and mobile swipe.
- Owner product safety and ecommerce full gates passed after gallery gates were
  inserted.
- Permission-bypass lint passes with Product Setup slideshow projection
  explicitly justified at the guarded local-apply boundary.
- The contact expanded-layout gate passes after the layout helper learned to
  ignore descendants of `aria-hidden`/opacity-zero honeypot containers.

## Boundaries

- This does not approve ERPNext Item Group/category images.
- This does not approve image-rich mega-menu media.
- This does not change live/staging/Frappe Cloud/DNS/Stripe.
- This does not make every product checkout-ready; checkout lanes still belong
  to the product runtime and payment gates.
- Do not delete the role split. Product gallery, selected variant media, and
  category/reference media are different contracts.

## Staging Handoff Note

The local `--apply-gallery` wrapper stages `_resources/odoo-live` into the
Docker container before running the in-app sync. A staging/Frappe Cloud packet
must provide the same source files to the app/site execution environment before
running Product Setup gallery projection. Do not treat the local Docker staging
path as proof that Frappe Cloud already has those files.

`product_gallery_projection_contract.py` is not staging proof just because
`LT_BASE_URL` points at staging. The verifier shells into the local Docker
`frontend` site for Product Setup, Website Item, and slideshow rows; the env
var only changes the rendered HTML fetch target. A staging packet must prove
the staging app mirror, site update/migration, cache clear, pause state, source
file availability, and staging route rendering. Any database-side gallery proof
must run in the staging environment or stay explicitly unverified.

Staging-safe gate list:

1. Triad review the release scope, doc truth, and gate evidence.
2. Confirm source commit, app-mirror commit, staging host, rollback path, and
   `lt_ecommerce_paused=1`.
3. Run local gallery/Product Setup/owner/ecommerce hard gates first.
4. Deploy/update/migrate staging and clear cache.
5. Run staging HTTP/browser checks against the staging URL.
6. Run staging-side DB/gallery proof if tooling exists; otherwise do not claim
   Product Setup/slideshow staging parity.

## Backlinks

- `research/research-product-gallery-architecture/research-brief.md`
- `ECOMMERCE-SHOP-HANDOFF.md`
- `CODING-HANDOFF.md`
- `locally-twisted-decisions.md`
- `lessons-learned.md`
- `capabilities/failures/product-gallery-projection-regression.md`
- `capabilities/failures/variant-media-overgating-regression.md`
- `workstreams/ecommerce-audit/variant-item-media-restore-2026-05-17.md`
