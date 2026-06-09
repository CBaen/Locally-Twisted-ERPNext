# Product Page Contract Source Audit

This is a read-only dry run from legacy_source/source catalog data into the new product-page contract shape.
It is not an ERPNext import and does not mutate the database.

## Counts

- Source products: 53
- Products with gallery/alternate images: 49
- Products with confirmed add-on contracts: 14
- Products with source-backed dependency matrices: 36
- Required-axis valid combinations preserved: 273
- Variant products with resolver-backed prices: 0
- Products with warnings/review notes: 53

## Product-page template classification

- Configurable product page (`complex_custom_product`): 38
- Ready-to-order page (`simple_product`): 15

## Commerce lane classification

- Online checkout (`checkout`): 53

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

## Sample contracts with review notes

| Slug | Template | Lane | Category hint | Variant rows | Required axes | Add-ons | Warnings |
|---|---|---|---|---:|---|---|---|
| baby-shower-combination-photo-opt | Configurable product page | Online checkout | Table Decor | 53 |  |  | Color axis removed from required ERPNext variants and needs customization/import handling: latex colors<br>Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| classic-organic-balloon-garland | Configurable product page | Online checkout | Garlands | 159 | Garland Length |  | Color axis removed from required ERPNext variants and needs customization/import handling: latex colors<br>Variant product lacks resolver-backed erpnext_variant_price rows. |
| basketball-arch | Configurable product page | Online checkout | Arches | 2 | Arch Size |  | Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| number-balloon-columns | Configurable product page | Online checkout | Columns | 371 |  |  | Color axis removed from required ERPNext variants and needs customization/import handling: Number colors<br>Color axis removed from required ERPNext variants and needs customization/import handling: latex colors<br>Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| easter-balloon-arch-bunny-ear | Configurable product page | Online checkout | Arches | 2 | Arch Size |  | Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| graduation-grab-n-go | Configurable product page | Online checkout | Grab & Go | 53 |  |  | Color axis removed from required ERPNext variants and needs customization/import handling: latex colors<br>Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| halloween-arch | Configurable product page | Online checkout | Arches | 212 | Arch Size |  | Color axis removed from required ERPNext variants and needs customization/import handling: latex colors<br>Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| large-head-missionary | Configurable product page | Online checkout | Bouquets | 30 | Missionary, skin color, Hair color |  | Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| premium-organic-garland | Configurable product page | Online checkout | Garlands | 159 | Garland Length |  | Color axis removed from required ERPNext variants and needs customization/import handling: latex colors<br>Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| premium-organic-arch | Configurable product page | Online checkout | Arches | 424 | Arch Size |  | Color axis removed from required ERPNext variants and needs customization/import handling: latex colors<br>Axis needs review before import: Add ons - Potential optional add-ons; needs product-family mapping.<br>Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| pemium-organic-column | Configurable product page | Online checkout | Columns | 636 | Column Height |  | Color axis removed from required ERPNext variants and needs customization/import handling: latex colors<br>Axis needs review before import: Add ons - Potential optional add-ons; needs product-family mapping.<br>Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| pride-progress-rainbow-balloon-arch | Configurable product page | Online checkout | Arches | 4 | Arch Size |  | Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| classic-arch | Configurable product page | Online checkout | Arches | 848 | Arch Size, Design, LED Lights |  | Color axis removed from required ERPNext variants and needs customization/import handling: latex colors<br>Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| classic-column | Configurable product page | Online checkout | Columns | 1908 | Column Height, topper |  | Color axis removed from required ERPNext variants and needs customization/import handling: latex colors<br>Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| classic-organic-columns | Configurable product page | Online checkout | Columns | 318 | Column Height |  | Color axis removed from required ERPNext variants and needs customization/import handling: latex colors<br>Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| baby-shower-garland | Configurable product page | Online checkout | Garlands | 159 | Garland Length |  | Color axis removed from required ERPNext variants and needs customization/import handling: latex colors<br>Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| balloon-drop | Configurable product page | Online checkout | Drops | 159 | Drop Size |  | Color axis removed from required ERPNext variants and needs customization/import handling: latex colors<br>Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| classic-organic-arch | Configurable product page | Online checkout | Arches | 636 | Arch Size |  | Color axis removed from required ERPNext variants and needs customization/import handling: latex colors<br>Axis needs review before import: Add ons - Potential optional add-ons; needs product-family mapping.<br>Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| unicorn-bouquet | Ready-to-order page | Online checkout | Bouquets | 30 | Bouquet Size | foil_number | Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| mickey-mouse-bouquet | Ready-to-order page | Online checkout | Bouquets | 30 | Bouquet Size | foil_number | Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| minion-bouquet | Ready-to-order page | Online checkout | Bouquets | 30 | Bouquet Size | foil_number | Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| encanto-bouquet | Ready-to-order page | Online checkout | Bouquets | 30 | Bouquet Size | foil_number | Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| stitch-bouquet | Ready-to-order page | Online checkout | Bouquets | 30 | Bouquet Size | foil_number | Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| flamingo-bouquet | Ready-to-order page | Online checkout | Bouquets | 30 | Bouquet Size | foil_number | Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |
| football-bouquet | Ready-to-order page | Online checkout | Bouquets | 30 | Bouquet Size | foil_number | Variant product lacks resolver-backed erpnext_variant_price rows.<br>One or more alternate images are held back until gallery/variant/reference classification. |

## Interpretation

The contract builder separates confirmed foil-number add-ons from required axes and keeps unmapped add-on families out of checkout add-on controls.
Every source product is now classified into one of the two reusable product-page template types and all 53 legacy_source-imported products target checkout.
Resolver-backed price notes remain audit signals: variant rows may lack `erpnext_variant_price`, but the import path can still use source row price/base price and the separate price gates verify Item Price coverage.
`product_page_price_readiness_contract.py` checks the separate live-ERPNext Item Price gate for the current database.
`product_page_price_enrichment_contract.py` builds the separate candidate price map for purge/reimport rehearsal without mutating the source scrape.
Gallery images are present but intentionally marked review-needed until classified as parent gallery vs variant image vs other source media.
`product_page_media_visibility_contract.py` checks the separate live-ERPNext media evidence and source-media classification gate.

## Gate result

**PASS with review notes.** All legacy_source products resolve to sellable checkout targets; add-on/media/price notes remain separate gates.