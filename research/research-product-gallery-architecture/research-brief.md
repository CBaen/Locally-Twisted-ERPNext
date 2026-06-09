# Research Brief - Product Gallery Architecture Restoration

Date: 2026-05-22

## Want

Restore product-page additional photos as permanent architecture, not a staging
patch. The accepted chain is: source-approved product gallery media -> `LT
Product Blueprint Gallery Image` -> ERPNext `Website Slideshow` / `Website
Slideshow Item` -> existing Webshop product gallery template.

The target customer behavior is the product-page gallery GL pointed to in the
old legacy_source reference: desktop thumbnails at the left of the main photo, thumbnail
rail capped to the main photo height with internal scroll, and mobile gallery
behavior that keeps thumbnails/indicator state while allowing swipe-like image
changes. Variant selection may update the main image, but must not remove or
rebuild away the product gallery.

## Have

- Local ERPNext/Frappe Webshop route: `http://localhost:8081`.
- Source legacy_source catalog/image witness under `_resources/catalog-source/`.
- Owner-safe product-management layer: `LT Product Blueprint` / Product Setup.
- Existing Product Setup apply path already knows how to create/update native
  ERPNext `Website Slideshow` records.
- Existing product image template override already has thumbnail-rail UI, but
  it can be bypassed if the live template chooses Webshop fallback `slides`
  before LT projected slideshow data.
- The current local DB before repair had source extras and UI surface, but no
  useful live gallery projection: `0` Website Slideshow rows, `0` Website
  Slideshow Item rows, and `0` Website Items with slideshow.

## Won't Accept

- Holding all legacy_source additional images forever under the old "unclassified
  extra" rule.
- Rendering selected variant media as product gallery thumbnails.
- Rendering category/reference media as product gallery thumbnails.
- A DB-only pass where `Website Slideshow` rows exist but product pages render
  no thumbnail rail.
- A one-route proof only. Classic Arch and a representative route that depends
  on projected slideshow data must both render.
- Silent fallback to primary image only when Product Setup gallery rows exist.
- Staging/live claims without local render proof and fail-loud gates.

## Open To

- Dedupe paired legacy_source thumbnail/full-size URLs by semantic source key so a
  single product photo does not become duplicate gallery thumbnails.
- Let source additional product-page images default to role `gallery` when
  they are part of the source-approved product gallery set. Keep separate roles
  for `variant_image`, `reference`, and `ignored_artifact`.
- Keep category browse images and menu/card image approval as separate work.
- Skip source products that are not current live Website Items when proving the
  live product-page projection, while still leaving source-count drift visible
  in the classification packet.

## Questions Resolved

- Authority: Product Setup owns approved gallery rows; raw owner edits to
  Website Slideshow remain blocked.
- Projection: Product Setup apply creates native ERPNext Website Slideshow
  records and links `Website Item.slideshow`.
- Rendering: `get_product_gallery_slides()` is the LT product gallery
  authority. The Webshop `slides` context is fallback only.
- Verification: `product_gallery_projection_contract.py` proves source ->
  Product Setup -> Website Slideshow -> rendered route when ecommerce is open.
  `product_gallery_experience.spec.js` proves desktop rail geometry, dedupe,
  thumbnail click behavior, variant persistence, mobile swipe behavior, and no
  horizontal overflow.

