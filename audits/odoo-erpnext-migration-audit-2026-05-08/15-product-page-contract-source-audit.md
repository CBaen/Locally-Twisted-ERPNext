# Product Page Contract Source Audit

This is a read-only dry run from Odoo/source catalog data into the new product-page contract shape.
It is not an ERPNext import and does not mutate the database.

## Counts

- Source products: 53
- Products with gallery/alternate images: 49
- Products with confirmed add-on contracts: 14
- Products with source-backed dependency matrices: 36
- Required-axis valid combinations preserved: 273
- Variant products with resolver-backed prices: 0
- Products with warnings/blockers: 53

## Product-page template classification

- Custom quote page (`complex_custom_product`): 38
- Ready-to-order page (`simple_product`): 15

## Commerce lane classification

- Online checkout (`checkout`): 15
- Quote request first (`quote_first`): 38

## Warning buckets

- axis_needs_review: 9
- color_axis_customization: 25
- missing_resolver_prices: 49
- unclassified_gallery_images: 49

## Review-only source add-on families

- Add Bouquet: 1 product(s) need mapping before checkout
- Add ons: 3 product(s) need mapping before checkout
- Orbz toppers: 2 product(s) need mapping before checkout
- Plush add ons: 3 product(s) need mapping before checkout

## Sample contracts needing review

| Slug | Template | Lane | Category hint | Variant rows | Required axes | Add-ons | Warnings |
|---|---|---|---|---:|---|---|---|
| baby-shower-combination-photo-opt | Custom quote page | Quote request first | Table Decor | 53 |  |  | Color axis removed from required ERPNext variants and needs customization/import handling: latex colors<br>Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| classic-organic-balloon-garland | Custom quote page | Quote request first | Garlands | 159 | Garland Length |  | Color axis removed from required ERPNext variants and needs customization/import handling: latex colors<br>Variant product lacks resolver-backed erpnext_variant_price rows. |
| basketball-arch | Custom quote page | Quote request first | Arches | 2 | Arch Size |  | Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| number-balloon-columns | Custom quote page | Quote request first | Columns | 371 |  |  | Color axis removed from required ERPNext variants and needs customization/import handling: Number colors<br>Color axis removed from required ERPNext variants and needs customization/import handling: latex colors<br>Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| easter-balloon-arch-bunny-ear | Custom quote page | Quote request first | Arches | 2 | Arch Size |  | Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| graduation-grab-n-go | Custom quote page | Quote request first | Grab & Go | 53 |  |  | Color axis removed from required ERPNext variants and needs customization/import handling: latex colors<br>Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| halloween-arch | Custom quote page | Quote request first | Arches | 212 | Arch Size |  | Color axis removed from required ERPNext variants and needs customization/import handling: latex colors<br>Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| large-head-missionary | Custom quote page | Quote request first | Bouquets | 30 | Missionary, skin color, Hair color |  | Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| premium-organic-garland | Custom quote page | Quote request first | Garlands | 159 | Garland Length |  | Color axis removed from required ERPNext variants and needs customization/import handling: latex colors<br>Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| premium-organic-arch | Custom quote page | Quote request first | Arches | 424 | Arch Size |  | Color axis removed from required ERPNext variants and needs customization/import handling: latex colors<br>Axis needs review before import: Add ons - Potential optional add-ons; needs product-family mapping.<br>Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| pemium-organic-column | Custom quote page | Quote request first | Columns | 636 | Column Height |  | Color axis removed from required ERPNext variants and needs customization/import handling: latex colors<br>Axis needs review before import: Add ons - Potential optional add-ons; needs product-family mapping.<br>Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| pride-progress-rainbow-balloon-arch | Custom quote page | Quote request first | Arches | 4 | Arch Size |  | Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| classic-arch | Custom quote page | Quote request first | Arches | 848 | Arch Size, Design, LED Lights |  | Color axis removed from required ERPNext variants and needs customization/import handling: latex colors<br>Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| classic-column | Custom quote page | Quote request first | Columns | 1908 | Column Height, topper |  | Color axis removed from required ERPNext variants and needs customization/import handling: latex colors<br>Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| classic-organic-columns | Custom quote page | Quote request first | Columns | 318 | Column Height |  | Color axis removed from required ERPNext variants and needs customization/import handling: latex colors<br>Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| baby-shower-garland | Custom quote page | Quote request first | Garlands | 159 | Garland Length |  | Color axis removed from required ERPNext variants and needs customization/import handling: latex colors<br>Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| balloon-drop | Custom quote page | Quote request first | Drops | 159 | Drop Size |  | Color axis removed from required ERPNext variants and needs customization/import handling: latex colors<br>Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| classic-organic-arch | Custom quote page | Quote request first | Arches | 636 | Arch Size |  | Color axis removed from required ERPNext variants and needs customization/import handling: latex colors<br>Axis needs review before import: Add ons - Potential optional add-ons; needs product-family mapping.<br>Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| unicorn-bouquet | Ready-to-order page | Online checkout | Bouquets | 30 | Bouquet Size | foil_number | Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| mickey-mouse-bouquet | Ready-to-order page | Online checkout | Bouquets | 30 | Bouquet Size | foil_number | Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| minion-bouquet | Ready-to-order page | Online checkout | Bouquets | 30 | Bouquet Size | foil_number | Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| encanto-bouquet | Ready-to-order page | Online checkout | Bouquets | 30 | Bouquet Size | foil_number | Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| stitch-bouquet | Ready-to-order page | Online checkout | Bouquets | 30 | Bouquet Size | foil_number | Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| flamingo-bouquet | Ready-to-order page | Online checkout | Bouquets | 30 | Bouquet Size | foil_number | Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| football-bouquet | Ready-to-order page | Online checkout | Bouquets | 30 | Bouquet Size | foil_number | Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |

## Interpretation

The contract builder can separate confirmed foil-number add-ons from required axes, but the source artifact is not import-ready.
Every source product is now classified into one of the two reusable product-page template types so import review is about architecture, not fake product content.
The largest source-artifact blocker remains resolver-backed pricing: variant rows currently lack `erpnext_variant_price` for a destructive purge/import.
`product_page_price_readiness_contract.py` checks the separate live-ERPNext Item Price gate for the current database.
`product_page_price_enrichment_contract.py` builds the separate candidate price map for purge/reimport rehearsal without mutating the source scrape.
Gallery images are present but intentionally marked review-needed until classified as parent gallery vs variant image vs other source media.
`product_page_media_visibility_contract.py` checks the separate live-ERPNext media evidence and source-media classification gate.

## Gate result

**BLOCKED for destructive purge/import.** Contract dry-run is useful, but source enrichment/classification is still required.