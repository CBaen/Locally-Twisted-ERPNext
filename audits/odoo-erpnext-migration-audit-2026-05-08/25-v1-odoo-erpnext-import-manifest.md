# V1 Odoo-to-ERPNext Import Manifest

- Generated: `2026-05-17T23:10:00Z`
- Mode: read-only manifest; no purge, import, delete, or ERPNext mutation.
- V1 scope: Odoo-imported products that fit the current ERPNext backend/schema contract.
- Variants, cups, and high-variant products are not blanket exclusions.
- No owner exclusion list is active for Odoo-imported products.

## Summary

- Included products: 53
- Excluded products: 0 (none)
- V1 sale units: 290
- V1 price units needing source fix or checkout hold: 0
- V1 price resolution statuses: source_price_ready=290
- V1 extra images held out of import: 95
- V1 confirmed add-on products: 14
- V1 review-only add-on products: 9
- V1 product statuses: ready=53
- Validation: PASS

## Blocker Reduction

- `source_contract`: Corrected V1 includes Odoo-imported products as sellable product targets when source trace and backend schema are present. Warning counts inside V1: {'axis_needs_review': 9, 'color_axis_customization': 24, 'missing_resolver_prices': 49, 'unclassified_gallery_images': 49}.
- `price_review`: Corrected V1 prices are derived from source artifacts where possible. Resolution counts: {'source_price_ready': 290}. Excluded live-snapshot review units: 0.
- `media`: 95 global extra image rows apply to corrected V1; 0 belong to products outside this generated subset. Primary images are source-backed and extras are held unless approved.
- `add_ons`: 9 corrected V1 products have review-only add-on axes. Those add-on controls stay hidden until mapped; the products themselves remain sellable targets. Confirmed foil_number add-on remains available where eligible.

## Owner Decisions Still Needed

- `v1_source_price_resolution` (0): Resolve source price conflicts, or keep source-missing sale units blocked from checkout until priced. Safe default: `source_price_missing_checkout_hold`.
- `v1_extra_images` (95): Only needed if extras should publish in V1; otherwise the manifest holds them and imports primary images only. Safe default: `hold_until_classified`.
- `v1_review_only_add_ons` (9): Approve each review-only add-on family for checkout add-on controls, or keep those add-on controls hidden until mapped. Safe default: `hide_add_on_until_mapped`.

## ERPNext Field Mapping

- Template Item / Website Item code: source slug.
- Item Group: source `slug_to_group` mapping.
- Website Item `lt_product_page_type`: source product-page contract.
- Website Item `lt_commerce_lane`: source commerce-lane contract.
- Line configuration version: `lt-product-config-v1`.
- Line fields: `{"json": "custom_lt_configuration_json", "page_type": "custom_lt_product_page_type", "summary": "custom_lt_configuration_summary", "template_item": "custom_lt_product_template_item", "version": "custom_lt_configuration_version"}`.
- Confirmed foil-number add-on: `ADDON-FOIL-NUMBER` runtime contract for eligible bouquet products.
- Odoo-imported products should import as sellable checkout targets; review-only add-on controls stay hidden until mapped.

## Included Products

| Product | Slug | Status | Lane | Required Axis | Sale Units | Price Review | Extra Images Held | Add-ons |
|---|---|---|---|---|---:|---:|---:|---|
| Baby Shower Combination Photo opt | `baby-shower-combination-photo-opt` | ready | checkout | single SKU | 1 | 0 | 1 | none |
| Classic Organic Balloon Garland | `classic-organic-balloon-garland` | ready | checkout | Garland Length | 3 | 0 | 0 | none |
| Basketball Arch | `basketball-arch` | ready | checkout | Arch Size | 2 | 0 | 1 | none |
| Number Balloon Columns | `number-balloon-columns` | ready | checkout | single SKU | 1 | 0 | 1 | none |
| Easter Balloon Arch - Bunny Ear | `easter-balloon-arch-bunny-ear` | ready | checkout | Arch Size | 2 | 0 | 1 | none |
| Graduation Grab n Go | `graduation-grab-n-go` | ready | checkout | single SKU | 1 | 0 | 1 | none |
| Halloween arch | `halloween-arch` | ready | checkout | Arch Size | 4 | 0 | 1 | none |
| Large head Missionary | `large-head-missionary` | ready | checkout | Missionary, skin color, Hair color | 30 | 0 | 1 | none |
| Premium Organic Garland | `premium-organic-garland` | ready | checkout | Garland Length | 3 | 0 | 1 | none |
| Premium Organic Arch | `premium-organic-arch` | ready | checkout | Arch Size | 4 | 0 | 1 | none |
| Pemium Organic Column | `pemium-organic-column` | ready | checkout | Column Height | 6 | 0 | 1 | none |
| Pride progress Rainbow Balloon Arch | `pride-progress-rainbow-balloon-arch` | ready | checkout | Arch Size | 4 | 0 | 1 | none |
| Classic Arch | `classic-arch` | ready | checkout | Arch Size, Design, LED Lights | 16 | 0 | 22 | none |
| Classic Column | `classic-column` | ready | checkout | Column Height, topper | 36 | 0 | 5 | none |
| Classic Organic columns | `classic-organic-columns` | ready | checkout | Column Height | 6 | 0 | 1 | none |
| Baby Shower Garland | `baby-shower-garland` | ready | checkout | Garland Length | 3 | 0 | 1 | none |
| Balloon Drop | `balloon-drop` | ready | checkout | Drop Size | 3 | 0 | 1 | none |
| Classic Organic Arch | `classic-organic-arch` | ready | checkout | Arch Size | 4 | 0 | 1 | none |
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
| 7' Butterfly Column | `7-butterfly-column` | ready | checkout | single SKU | 1 | 0 | 0 | none |
| 7' Epic Column | `7-epic-column` | ready | checkout | single SKU | 1 | 0 | 0 | none |
| Organic Grab n' Go | `organic-grab-n-go` | ready | checkout | Garland Length | 3 | 0 | 1 | none |
| Birthday Deliveries | `birthday-deliveries` | ready | checkout | Delivery Size, Delivery themes | 81 | 0 | 14 | foil_number |
| Easter Balloon Cups | `easter-balloon-cups` | ready | checkout | Easter Designs | 7 | 0 | 4 | none |
| Star Column | `star-column` | ready | checkout | Column Height | 4 | 0 | 0 | none |
| Sleepy Baby Column | `sleepy-baby-column` | ready | checkout | single SKU | 1 | 0 | 1 | none |
| Baby Table decor | `baby-table-decor` | ready | checkout | single SKU | 1 | 0 | 1 | none |
| Logo 3 layered bouquet | `logo-3-layered-bouquet` | ready | checkout | single SKU | 1 | 0 | 1 | none |
| 6 color rainbow arch | `6-color-rainbow-arch` | ready | checkout | Arch Size | 2 | 0 | 1 | none |
| Mother's day front yard 7' Column | `mothers-day-front-yard-7-column` | ready | checkout | single SKU | 1 | 0 | 1 | none |
| Marble table decor | `marble-table-decor` | ready | checkout | single SKU | 1 | 0 | 1 | none |
| Paw Patrol Bouquet | `paw-patrol-bouquet` | ready | checkout | Bouquet Size | 3 | 0 | 1 | foil_number |
| Elsa Bouquet | `elsa-bouquet` | ready | checkout | Bouquet Size | 3 | 0 | 1 | foil_number |
| Holy COW!! Bouquet | `holy-cow-bouquet` | ready | checkout | Bouquet Size | 3 | 0 | 1 | foil_number |
| Butterfly "GET WELL" Bouquet (Latex free) | `butterfly-get-well-bouquet-latex-free` | ready | checkout | single SKU | 1 | 0 | 1 | none |
| Bandage "GET WELL" Bouquet (Latex free) | `bandage-get-well-bouquet-latex-free` | ready | checkout | single SKU | 1 | 0 | 1 | none |
| Shooting star "GET WELL" Bouquet (Latex free) | `shooting-star-get-well-bouquet-latex-free` | ready | checkout | single SKU | 1 | 0 | 1 | none |
| 6' Graduation stands | `6-graduation-stands` | ready | checkout | Graduation stands | 2 | 0 | 1 | none |
| classic organic for easel | `classic-organic-for-easel` | ready | checkout | single SKU | 1 | 0 | 1 | none |
| Easter Arch | `easter-arch` | ready | checkout | single SKU | 1 | 0 | 1 | none |
| Mother's Day Bouquet | `mothers-day-bouquet` | ready | checkout | single SKU | 1 | 0 | 1 | none |
| Large Garland | `large-garland` | ready | checkout | Garland Length | 3 | 0 | 1 | none |
| Large Organic Column | `large-organic-column` | ready | checkout | Column Height | 6 | 0 | 1 | none |
| Pride Arch | `pride-arch` | ready | checkout | single SKU | 1 | 0 | 1 | none |

## Next Command Sequence

- `python scripts/verify/v1_odoo_erpnext_import_manifest.py`
- `python scripts/verify/catalog_purge_scope_dry_run.py`
- `python scripts/verify/product_import_readiness_gate.py --report output/product-import-readiness-gate.json`
- `python scripts/setup/stage_seed_data.py`
- `bench --site frontend backup --with-files`
- `bench --site frontend execute locally_twisted.seed.seed_catalog.execute --kwargs "{'dry_run': True}"`
