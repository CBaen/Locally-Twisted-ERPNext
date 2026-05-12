# V1 Odoo-to-ERPNext Import Manifest

- Generated: `2026-05-12T02:53:07Z`
- Mode: read-only manifest; no purge, import, delete, or ERPNext mutation.
- V1 scope: products that fit the current ERPNext backend/schema contract.
- Variants, cups, and high-variant products are not blanket exclusions.
- Owner-explicit excluded structures are held out: Classic Column, Classic Arch, Classic Organic Arch, Classic Organic Columns, Classic Garland.

## Summary

- Included products: 48
- Excluded products: 5 (owner_explicit_exclusion=5)
- V1 sale units: 225
- V1 price units needing source fix or checkout hold: 0
- V1 price resolution statuses: source_price_ready=225
- V1 extra images held out of import: 66
- V1 confirmed add-on products: 14
- V1 review-only add-on products: 8
- V1 product statuses: fix_needed=8, ready=40
- Validation: PASS

## Blocker Reduction

- `source_contract`: Corrected V1 includes products that fit backend schema, including variants and quote-first products. Warning counts inside V1: {'axis_needs_review': 8, 'color_axis_customization': 19, 'missing_resolver_prices': 44, 'unclassified_gallery_images': 45}.
- `price_review`: Corrected V1 prices are derived from source artifacts where possible. Resolution counts: {'source_price_ready': 225}. Excluded live-snapshot review units: 65.
- `media`: 66 global extra image rows apply to corrected V1; 29 belong to explicitly excluded products. Primary images are source-backed and extras are held unless approved.
- `add_ons`: 8 corrected V1 products have review-only add-on axes and must stay quote-first for those add-ons until mapped. Confirmed foil_number add-on remains available where eligible.

## Owner Decisions Still Needed

- `v1_source_price_resolution` (0): Resolve source price conflicts, or keep source-missing sale units on checkout hold/quote-first fallback. Safe default: `source_price_missing_checkout_hold`.
- `v1_extra_images` (66): Only needed if extras should publish in V1; otherwise the manifest holds them and imports primary images only. Safe default: `hold_until_classified`.
- `v1_review_only_add_ons` (8): Approve each review-only add-on family for checkout, or keep those products/add-ons quote-first until mapped. Safe default: `quote_only_until_approved`.

## ERPNext Field Mapping

- Template Item / Website Item code: source slug.
- Item Group: source `slug_to_group` mapping.
- Website Item `lt_product_page_type`: source product-page contract.
- Website Item `lt_commerce_lane`: source commerce-lane contract.
- Line configuration version: `lt-product-config-v1`.
- Line fields: `{"json": "custom_lt_configuration_json", "page_type": "custom_lt_product_page_type", "summary": "custom_lt_configuration_summary", "template_item": "custom_lt_product_template_item", "version": "custom_lt_configuration_version"}`.
- Confirmed foil-number add-on: `ADDON-FOIL-NUMBER` runtime contract for eligible bouquet products.
- Quote-first products may be imported with `lt_commerce_lane=quote_first`; they must not be presented as Ready-to-Order checkout until backend support is complete.

## Included Products

| Product | Slug | Status | Lane | Required Axis | Sale Units | Price Review | Extra Images Held | Add-ons |
|---|---|---|---|---|---:|---:|---:|---|
| Baby Shower Combination Photo opt | `baby-shower-combination-photo-opt` | ready | quote_first | single SKU | 1 | 0 | 1 | none |
| Basketball Arch | `basketball-arch` | ready | quote_first | Arch Size | 2 | 0 | 1 | none |
| Number Balloon Columns | `number-balloon-columns` | ready | quote_first | single SKU | 1 | 0 | 1 | none |
| Easter Balloon Arch - Bunny Ear | `easter-balloon-arch-bunny-ear` | ready | quote_first | Arch Size | 2 | 0 | 1 | none |
| Graduation Grab n Go | `graduation-grab-n-go` | ready | quote_first | single SKU | 1 | 0 | 1 | none |
| Halloween arch | `halloween-arch` | ready | quote_first | Arch Size | 4 | 0 | 1 | none |
| Large head Missionary | `large-head-missionary` | ready | quote_first | Missionary, skin color, Hair color | 30 | 0 | 1 | none |
| Premium Organic Garland | `premium-organic-garland` | ready | quote_first | Garland Length | 3 | 0 | 1 | none |
| Premium Organic Arch | `premium-organic-arch` | fix_needed | quote_first | Arch Size | 4 | 0 | 1 | none |
| Pemium Organic Column | `pemium-organic-column` | fix_needed | quote_first | Column Height | 6 | 0 | 1 | none |
| Pride progress Rainbow Balloon Arch | `pride-progress-rainbow-balloon-arch` | ready | quote_first | Arch Size | 4 | 0 | 1 | none |
| Baby Shower Garland | `baby-shower-garland` | ready | quote_first | Garland Length | 3 | 0 | 1 | none |
| Balloon Drop | `balloon-drop` | ready | quote_first | Drop Size | 3 | 0 | 1 | none |
| Unicorn Bouquet | `unicorn-bouquet` | ready | checkout | Bouquet Size | 3 | 0 | 1 | foil_number |
| Mickey Mouse Bouquet | `mickey-mouse-bouquet` | ready | checkout | Bouquet Size | 3 | 0 | 1 | foil_number |
| Minion Bouquet | `minion-bouquet` | ready | checkout | Bouquet Size | 3 | 0 | 6 | foil_number |
| Encanto Bouquet | `encanto-bouquet` | ready | checkout | Bouquet Size | 3 | 0 | 1 | foil_number |
| Stitch Bouquet | `stitch-bouquet` | ready | checkout | Bouquet Size | 3 | 0 | 1 | foil_number |
| Flamingo Bouquet | `flamingo-bouquet` | ready | checkout | Bouquet Size | 3 | 0 | 1 | foil_number |
| Football Bouquet | `football-bouquet` | ready | checkout | Bouquet Size | 3 | 0 | 1 | foil_number |
| Soccer Bouquet | `soccer-bouquet` | ready | checkout | Bouquet Size | 3 | 0 | 1 | foil_number |
| Space Bouquet | `space-bouquet` | ready | checkout | Bouquet Size | 3 | 0 | 1 | foil_number |
| Over the Hill Bouquet | `over-the-hill-bouquet` | ready | checkout | Bouquet Size | 3 | 0 | 1 | foil_number |
| 7' Butterfly Column | `7-butterfly-column` | ready | quote_first | single SKU | 1 | 0 | 0 | none |
| 7' Epic Column | `7-epic-column` | ready | quote_first | single SKU | 1 | 0 | 0 | none |
| Organic Grab n' Go | `organic-grab-n-go` | ready | quote_first | Garland Length | 3 | 0 | 1 | none |
| Birthday Deliveries | `birthday-deliveries` | fix_needed | quote_first | Delivery Size, Delivery themes | 81 | 0 | 14 | foil_number |
| Easter Balloon Cups | `easter-balloon-cups` | ready | checkout | Easter Designs | 7 | 0 | 4 | none |
| Star Column | `star-column` | fix_needed | quote_first | Column Height | 4 | 0 | 0 | none |
| Sleepy Baby Column | `sleepy-baby-column` | ready | quote_first | single SKU | 1 | 0 | 1 | none |
| Baby Table decor | `baby-table-decor` | ready | quote_first | single SKU | 1 | 0 | 1 | none |
| Logo 3 layered bouquet | `logo-3-layered-bouquet` | ready | quote_first | single SKU | 1 | 0 | 1 | none |
| 6 color rainbow arch | `6-color-rainbow-arch` | ready | quote_first | Arch Size | 2 | 0 | 1 | none |
| Mother's day front yard 7' Column | `mothers-day-front-yard-7-column` | ready | quote_first | single SKU | 1 | 0 | 1 | none |
| Marble table decor | `marble-table-decor` | fix_needed | quote_first | single SKU | 1 | 0 | 1 | none |
| Paw Patrol Bouquet | `paw-patrol-bouquet` | ready | checkout | Bouquet Size | 3 | 0 | 1 | foil_number |
| Elsa Bouquet | `elsa-bouquet` | ready | checkout | Bouquet Size | 3 | 0 | 1 | foil_number |
| Holy COW!! Bouquet | `holy-cow-bouquet` | ready | checkout | Bouquet Size | 3 | 0 | 1 | foil_number |
| Butterfly "GET WELL" Bouquet (Latex free) | `butterfly-get-well-bouquet-latex-free` | fix_needed | quote_first | single SKU | 1 | 0 | 1 | none |
| Bandage "GET WELL" Bouquet (Latex free) | `bandage-get-well-bouquet-latex-free` | fix_needed | quote_first | single SKU | 1 | 0 | 1 | none |
| Shooting star "GET WELL" Bouquet (Latex free) | `shooting-star-get-well-bouquet-latex-free` | fix_needed | quote_first | single SKU | 1 | 0 | 1 | none |
| 6' Graduation stands | `6-graduation-stands` | ready | quote_first | Graduation stands | 2 | 0 | 1 | none |
| classic organic for easel | `classic-organic-for-easel` | ready | quote_first | single SKU | 1 | 0 | 1 | none |
| Easter Arch | `easter-arch` | ready | quote_first | single SKU | 1 | 0 | 1 | none |
| Mother's Day Bouquet | `mothers-day-bouquet` | ready | checkout | single SKU | 1 | 0 | 1 | none |
| Large Garland | `large-garland` | ready | quote_first | Garland Length | 3 | 0 | 1 | none |
| Large Organic Column | `large-organic-column` | ready | quote_first | Column Height | 6 | 0 | 1 | none |
| Pride Arch | `pride-arch` | ready | quote_first | single SKU | 1 | 0 | 1 | none |

## Next Command Sequence

- `python scripts/verify/v1_odoo_erpnext_import_manifest.py`
- `python scripts/verify/catalog_purge_scope_dry_run.py`
- `python scripts/verify/product_import_readiness_gate.py --report output/product-import-readiness-gate.json`
- `python scripts/setup/stage_seed_data.py`
- `bench --site frontend backup --with-files`
- `bench --site frontend execute locally_twisted.seed.seed_catalog.execute --kwargs "{'dry_run': True}"`
