# Shop Primary And Secondary Taxonomy Map - 2026-05-24

## Status

Implemented locally/source and deployed to Frappe Cloud staging on 2026-05-24
after GL approval.

This packet changed source-owned taxonomy records and the staging ERPNext
catalog projection. It did not change product names, prices, checkout behavior,
payment settings, live, DNS, Search Console, live Stripe, or production data.

Verified local result after implementation:

- Local ERPNext published `Website Item` count: `51`.
- Visible primary `Item Group` children of `Shop Items`: `8`.
- Secondary `Website Item Group` rows: `51`.
- Secondary categories live under hidden parent group `Shop Occasions`.
- Product names remain unchanged.

Staging release result:

- Full repo source: `8913160 Document shop taxonomy implementation`.
- Frappe app mirror: `bb19a4b Sync shop taxonomy staging app`.
- Frappe Cloud bench deploy: `2ve3dgt97a`, `Success`.
- Frappe Cloud site migration job: `22jih1qaln`, `Success`.
- Staging cache was cleared through the Frappe Cloud site action.
- Hosted route probe confirmed active category routes and target product routes
  return `200`; duplicate product routes `/shop-items/arches/easter-arch` and
  `/shop-items/arches/pride-arch` return `404`.
- Hosted staging proof passed `npm run test:search-contract` `4/4`,
  `npm run test:product-gallery-experience` `4/4`,
  `npm run test:checkout-experience` `3/3`,
  `shop_category_hero_images.spec.js` `25/25`, and
  `public_asset_integrity.py --base-url https://locallytwisted-staging.frappe.cloud`
  for `31` routes and `315` local asset URLs.

## Taxonomy Contract

Primary category answers: **what physical product type is this?**

Secondary category answers: **what broad occasion or use case is this for?**

Product names are frozen for this taxonomy pass. Do not rename products as part
of the category cleanup.

Do not use any of these as primary or secondary categories:

- Delivery
- Pickup
- Latex-free
- Color
- Size
- Add-ons
- Foil numbers
- Grab & Go
- Specific holiday names such as Easter, Halloween, Mother's Day, or Pride
- Character/theme names
- Product option values

Specific terms such as Easter, Halloween, Mother's Day, Pride, latex-free,
delivery-eligible, and pickup-eligible belong in product names, product copy,
search keywords, product options, checkout fulfillment, or future tags. They do
not belong in the two-level category model.

## Approved Secondary Categories

- Any Occasion
- Birthday
- Holiday
- Graduation
- Baby Shower
- Sports
- Get Well
- Religious
- Corporate

## Approved Mapping

| Item code | Product name | Current primary | Approved primary | Approved secondary |
|---|---|---|---|---|
| `6-color-rainbow-arch` | 6 color rainbow arch | Arches | Arches | Any Occasion |
| `6-graduation-stands` | 6' Graduation stands | Stands & Easels | Stands & Easels | Graduation |
| `7-butterfly-column` | 7' Butterfly Column | Columns | Columns | Any Occasion |
| `7-epic-column` | 7' Epic Column | Columns | Columns | Any Occasion |
| `baby-shower-combination-photo-opt` | Baby Shower Combination Photo opt | Table Decor | Photo Ops & Backdrops | Baby Shower |
| `baby-shower-garland` | Baby Shower Garland | Garlands | Garlands | Baby Shower |
| `baby-table-decor` | Baby Table decor | Table Decor | Table Decor | Baby Shower |
| `balloon-drop` | Balloon Drop | Drops | Balloon Drops | Any Occasion |
| `bandage-get-well-bouquet-latex-free` | Bandage "GET WELL" Bouquet (Latex free) | Get-Well Bouquets | Bouquets | Get Well |
| `basketball-arch` | Basketball Arch | Arches | Arches | Sports |
| `birthday-deliveries` | Birthday Deliveries | Deliveries | Bouquets | Birthday |
| `butterfly-get-well-bouquet-latex-free` | Butterfly "GET WELL" Bouquet (Latex free) | Get-Well Bouquets | Bouquets | Get Well |
| `classic-arch` | Classic Arch | Arches | Arches | Any Occasion |
| `classic-column` | Classic Column | Columns | Columns | Any Occasion |
| `classic-organic-arch` | Classic Organic Arch | Arches | Arches | Any Occasion |
| `classic-organic-balloon-garland` | Classic Organic Balloon Garland | Garlands | Garlands | Any Occasion |
| `classic-organic-columns` | Classic Organic columns | Columns | Columns | Any Occasion |
| `classic-organic-for-easel` | classic organic for easel | Stands & Easels | Stands & Easels | Any Occasion |
| `easter-balloon-arch-bunny-ear` | Easter Balloon Arch - Bunny Ear | Arches | Arches | Holiday |
| `easter-balloon-cups` | Easter Balloon Cups | Seasonal & Specialty | Table Decor | Holiday |
| `elsa-bouquet` | Elsa Bouquet | Bouquets | Bouquets | Birthday |
| `encanto-bouquet` | Encanto Bouquet | Bouquets | Bouquets | Birthday |
| `flamingo-bouquet` | Flamingo Bouquet | Bouquets | Bouquets | Birthday |
| `football-bouquet` | Football Bouquet | Bouquets | Bouquets | Sports |
| `graduation-grab-n-go` | Graduation Grab n Go | Grab & Go | Garlands | Graduation |
| `halloween-arch` | Halloween arch | Arches | Arches | Holiday |
| `holy-cow-bouquet` | Holy COW!! Bouquet | Bouquets | Bouquets | Birthday |
| `large-garland` | Large Garland | Garlands | Garlands | Any Occasion |
| `large-head-missionary` | Large head Missionary | Bouquets | Bouquets | Religious |
| `large-organic-column` | Large Organic Column | Columns | Columns | Any Occasion |
| `logo-3-layered-bouquet` | Logo 3 layered bouquet | Bouquets | Bouquets | Corporate |
| `marble-table-decor` | Marble table decor | Table Decor | Table Decor | Any Occasion |
| `mickey-mouse-bouquet` | Mickey Mouse Bouquet | Bouquets | Bouquets | Birthday |
| `minion-bouquet` | Minion Bouquet | Bouquets | Bouquets | Birthday |
| `mothers-day-bouquet` | Mother's Day Bouquet | Bouquets | Bouquets | Holiday |
| `mothers-day-front-yard-7-column` | Mother's day front yard 7' Column | Columns | Columns | Holiday |
| `number-balloon-columns` | Number Balloon Columns | Columns | Columns | Birthday |
| `organic-grab-n-go` | Organic Grab n' Go | Grab & Go | Garlands | Any Occasion |
| `over-the-hill-bouquet` | Over the Hill Bouquet | Bouquets | Bouquets | Birthday |
| `paw-patrol-bouquet` | Paw Patrol Bouquet | Bouquets | Bouquets | Birthday |
| `pemium-organic-column` | Pemium Organic Column | Columns | Columns | Any Occasion |
| `premium-organic-arch` | Premium Organic Arch | Arches | Arches | Any Occasion |
| `premium-organic-garland` | Premium Organic Garland | Garlands | Garlands | Any Occasion |
| `pride-progress-rainbow-balloon-arch` | Pride progress Rainbow Balloon Arch | Arches | Arches | Holiday |
| `shooting-star-get-well-bouquet-latex-free` | Shooting star "GET WELL" Bouquet (Latex free) | Get-Well Bouquets | Bouquets | Get Well |
| `sleepy-baby-column` | Sleepy Baby Column | Columns | Columns | Baby Shower |
| `soccer-bouquet` | Soccer Bouquet | Bouquets | Bouquets | Sports |
| `space-bouquet` | Space Bouquet | Bouquets | Bouquets | Birthday |
| `star-column` | Star Column | Columns | Columns | Any Occasion |
| `stitch-bouquet` | Stitch Bouquet | Bouquets | Bouquets | Birthday |
| `unicorn-bouquet` | Unicorn Bouquet | Bouquets | Bouquets | Birthday |

## Primary Category Cleanup

These prior primary groups were hidden/demoted by the implementation:

- `Deliveries` is fulfillment, not a product category.
- `Get-Well Bouquets` is an occasion/use-case grouping; approved primary is
  `Bouquets`, approved secondary is `Get Well`.
- `Grab & Go` is not a product category. It can be a marketing/menu concept,
  but the approved primary for those current products is `Garlands`.
- `Seasonal & Specialty` is not a product type. The current product maps to
  `Table Decor` with secondary `Holiday`.
- `Drops` became `Balloon Drops`; route aliases preserve old inbound URLs.

New or confirmed primary categories needed by the approved mapping:

- Arches
- Balloon Drops
- Bouquets
- Columns
- Garlands
- Photo Ops & Backdrops
- Stands & Easels
- Table Decor

## Implementation Receipts

Source-owned contract:

- `apps/locally_twisted/locally_twisted/shop_taxonomy.py`
- `apps/locally_twisted/locally_twisted/seed/sync_shop_taxonomy.py`
- `apps/locally_twisted/locally_twisted/patches/sync_shop_taxonomy_20260524.py`
- `apps/locally_twisted/locally_twisted/fixtures/item_group.json`

Runtime projection:

- `51` Website Items retagged to approved primary groups.
- `9` template Items retagged.
- `2,852` variant Items retagged.
- `51` secondary Website Item Group rows created.
- Prior visible primary groups were hidden, with compatibility routes retained
  through `website_route_rules`.

Verifier receipts:

- `python scripts\verify\shop_taxonomy_contract.py`
- `python scripts\verify\catalog_public_sellability_contract.py`
- `docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.verify.commerce_rules_contract.run`
- `python scripts\verify\nav_ia.py`
- `python scripts\verify\category_media_candidates.py --json output\category-media-candidates-taxonomy-smoke.json --markdown output\category-media-candidates-taxonomy-smoke.md --max-per-category 2`
- `scripts\verify\run_playwright.cmd test scripts/verify/shop_category_hero_images.spec.js --reporter=line`
- `python scripts\verify\public_asset_integrity.py`
- `python scripts\verify\smoke_shop.py`

Related copy hardening:

- Bouquet size labels were normalized away from supplier shorthand through
  `normalize_bouquet_size_labels_20260524.py`.
- Product Setup gallery/customer copy was normalized through
  `normalize_product_setup_bouquet_copy_20260524.py`.

No staging/live/provider mutation is approved by this packet. Promotion must
use the normal Frappe Cloud staging release gate and protect production data,
payment settings, DNS, Search Console, and live Stripe.
