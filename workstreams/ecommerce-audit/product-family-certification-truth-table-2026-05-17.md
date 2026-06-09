# Product Family Certification Truth Table - 2026-05-17

## Superseded Current State

This tranche table is historical as of the later 2026-05-17 all-legacy_source sellable
reimport. Do not use the older tranche counts below as the current product
queue.

Current control artifact:
`workstreams/ecommerce-audit/legacy_source-sellable-product-reimport-2026-05-17.md`.
Current verified state: 53 legacy_source-imported products included, 0 excluded, 290
priced sale units, 53 checkout-allowed product pages, and all 53 live Website
Item routes browser-proved in two batches before restoring
`lt_ecommerce_paused=1`. The remaining work is optional-surface follow-through:
95 extra images held until classified and 9 review-only add-on controls hidden
until mapped.

## Purpose

Historical backend-first certification map for existing Locally Twisted
ecommerce product families. This was the control artifact for the earlier
tranche goal. The active control artifact is now
`legacy_source-sellable-product-reimport-2026-05-17.md`.

This is not a live-release approval. `lt_ecommerce_paused=1` remains the
customer exposure lock.

## Business-Lane Correction

GL corrected the product model on 2026-05-17: there are no business
"quote-first" products. That label came from agent-side safety modeling, not
from Locally Twisted's intended catalog. If it is a product, the target state is
purchasable. Pricing and product details should come from the legacy_source product
export list; if a product cannot be mapped cleanly, repull or repair the import
source instead of treating "quote-first" as a final business lane.

The ERPNext field value `quote_first` still exists in current verifiers and
records as an internal legacy/safety state. In this handoff, read it as
"not safely purchasable yet because import data, pricing, media, or checkout
proof is incomplete." Products in that state should be blocked, hidden, or
kept out of customer checkout until they are proven from source export data and
runtime tests.

## Scope Cleanup Before This Report

The previous local Product Setup release proof left generated Website Item
`WEB-ITM-0055` / `release-proof-complex-product-1779036020` published in the
local `frontend` ERPNext site. That proof item is not an existing catalog
product. It was unpublished locally, not deleted, so current product-family
reports measure the 53 real product families again.

## Fresh Evidence

All commands below were run locally on 2026-05-17 after the generated proof
Website Item was unpublished.

| Gate | Result | Evidence |
|---|---|---|
| Product pattern contract | PASS with terminology caveat | `python scripts/verify/product_pattern_contract.py` via `complex_checkout_scaffold.py`; 53 products, 18 backend checkout, 30 legacy internal `quote_first` holds, 5 needs-review, no checkout blockers |
| Complex checkout scaffold | PASS with terminology caveat | `python scripts/verify/complex_checkout_scaffold.py`; 18 direct checkout guards, 4 simple purchasable proof candidates, 6 multi-color UI products, 20 add-on/conditional blocked, 5 needs-review |
| Price readiness | PASS | `python scripts/verify/product_page_price_readiness_contract.py`; backend-first gate now reports 18 backend checkout products and 51/51 checkout sale units priced; source-template classification still shows 15 checkout products and 8 source/backend lane differences for audit context |
| Media visibility | PASS with caveat | `python scripts/verify/product_page_media_visibility_contract.py`; 53 live primary images, 1,751 active variant images, 95 source extras held back, 0 unsafe unclassified images |
| Checkout family cascade | PASS | `python scripts/verify/checkout_product_family_contract.py`; 18 direct checkout families, 151 sale SKUs, 39 add-on rows, 102 color-recipe rows, and 190 SO/SI rows rolled back |
| Variant media safety | PASS | `python scripts/verify/variant_media_contract.py`; unclassified media held and product pages keep approved primary image |
| Product-page runtime | PASS | `python scripts/verify/product_page_runtime_contract.py`; selected config preserved through SO/SI/Quotation paths in rollback |
| Cart/checkout runtime | PASS | `python scripts/verify/cart_checkout_contract.py`; blocked-product guards, cart line keys, add-ons, over-limit quantities, stale payload failures, and color-recipe/variant mismatch failures guarded |
| Open-mode product UX | PASS / local only | Temporarily set local `lt_ecommerce_paused=0`, ran `node scripts/verify/post_import_checkout_proof.js`, restored `lt_ecommerce_paused=1`, and cleared website cache; product page, cart, and checkout preview passed for all 18 current checkout families at desktop and mobile widths |
| Product source repair map | PASS | `python scripts/verify/product_source_repair_map.py`; 53/53 legacy_source export rows found, 18 certified checkout products, 35 blocked-until-certified products, 0 contract failures |
| Simple purchasable rehearsal | PASS / backend only | `python scripts/verify/simple_purchasable_rehearsal_contract.py`; 4 simple repair-lane products, 33 sale SKUs, source-backed prices, SO/SI line preservation, and rollback cleanup passed |
| Simple purchasable browser proof | PASS / local only | `python scripts/verify/simple_purchasable_browser_proof.py`; temporary local opening proved the same 4 products through desktop/mobile product pages, cart, checkout preview, and verified restoration |
| Simple purchasable payment cascade | PASS / rollback only | `python scripts/verify/simple_purchasable_payment_cascade_contract.py`; all 33 sale lines passed Payment Request, Payment Entry, Sales Invoice, receipt, operator email, welcome email, idempotency, and rollback cleanup |
| Multi-color purchasable rehearsal | PASS / backend only | `python scripts/verify/multi_color_purchasable_rehearsal_contract.py --report workstreams/ecommerce-audit/multi-color-purchasable-rehearsal-2026-05-17.json`; 6 multi-color repair-lane products, 563 enabled color SKUs, source-backed prices, color-recipes payloads, SO/SI line preservation, and rollback cleanup passed |
| Multi-color purchasable browser proof | PASS / local only | `python scripts/verify/multi_color_purchasable_browser_proof.py`; temporary local opening proved the same 6 products through desktop/mobile product pages, 14 visible color drawer selections, cart, checkout preview, and verified restoration |
| Stripe amount parity | PASS | `python scripts/verify/stripe_amount_parity_contract.py`; hosted checkout cents match ERPNext totals |
| Payment cascade | PASS | `python scripts/verify/payment_cascade_contract.py`; SO -> PR -> Payment Entry -> SI -> receipt/operator/welcome email rolled back |

## Source / Backend Lane Difference

The price-readiness verifier now reports both source-template classification and
current backend Website Item lane. Backend lane remains authoritative for
current checkout admission, but `quote_first` is a legacy/internal hold label,
not the desired catalog model.

- Source-template classification: 15 checkout products, 38 legacy internal
  hold products.
- Current backend classification: 18 checkout products, 30 legacy internal
  hold products, 5 needs-review products.
- Backend checkout price gate: 18/18 backend checkout products and 51/51 sale
  units have live ERPNext price coverage.

The three products promoted to backend checkout relative to source-template
classification are:

- `6-graduation-stands`
- `7-butterfly-column`
- `graduation-grab-n-go`

The updated checkout-family cascade now covers these three, and the open-mode
browser proof covers all 18 current checkout families at desktop and mobile
widths.

The five backend needs-review products relative to source-template legacy hold
classification are:

- `bandage-get-well-bouquet-latex-free`
- `birthday-deliveries`
- `butterfly-get-well-bouquet-latex-free`
- `marble-table-decor`
- `shooting-star-get-well-bouquet-latex-free`

## Certification Status Counts

| Status | Count | Meaning |
|---|---:|---|
| Direct checkout regression guard | 18 | Current backend says checkout-ready; keep these green while proving UX/cascade family by family |
| Simple purchasable payment cascade passed | 4 | Source/export price, SO/SI line preservation, desktop/mobile product-page UX, cart, checkout preview, Payment Request, Payment Entry, Sales Invoice, receipt, operator email, and welcome email are proven; final owner/product approval remains before customer checkout |
| Multi-color browser proof passed | 6 | Source/export price, server-side color recipe controls, checkout line resolution, SO/SI line preservation, desktop/mobile product-page UX, visible color drawer selection, cart, checkout preview, and rollback/restoration are proven; payment/customer-message cascade, media update behavior, and final owner/product approval remain before customer checkout |
| Add-on or conditional pricing blocked | 20 | Needs explicit add-on and/or conditional pricing contracts before checkout |
| Needs review or missing | 5 | Keep blocked or hidden until product-page type, buying path, source export meaning, pricing, and media are reviewed |

## Tranche 1 - Preserve Current Direct Checkout Products

These are not blanket live-approved. They are the first certification tranche:
preserve current checkout behavior, then prove page UX and cascade family by
family.

| Product | Slug | Current next step |
|---|---|---|
| 6' Graduation stands | `6-graduation-stands` | Backend cascade proved 2 variants through SO/SI; open-mode product UX proof passed representative selection |
| 7' Butterfly Column | `7-butterfly-column` | Backend cascade proved 51 color variants through SO/SI; open-mode product UX proof passed color recipe selection |
| Easter Balloon Cups | `easter-balloon-cups` | Backend cascade proved 7 variants through SO/SI; open-mode product UX proof passed representative selection |
| Elsa Bouquet | `elsa-bouquet` | Bouquet-size checkout regression guard |
| Encanto Bouquet | `encanto-bouquet` | Bouquet-size checkout regression guard |
| Flamingo Bouquet | `flamingo-bouquet` | Bouquet-size checkout regression guard |
| Football Bouquet | `football-bouquet` | Bouquet-size checkout regression guard |
| Graduation Grab n Go | `graduation-grab-n-go` | Backend cascade proved 51 color variants through SO/SI; open-mode product UX proof passed color recipe selection |
| Holy COW!! Bouquet | `holy-cow-bouquet` | Bouquet-size checkout regression guard |
| Mickey Mouse Bouquet | `mickey-mouse-bouquet` | Bouquet-size checkout regression guard |
| Minion Bouquet | `minion-bouquet` | Bouquet-size checkout regression guard |
| Mother's Day Bouquet | `mothers-day-bouquet` | Single-SKU checkout regression guard |
| Over the Hill Bouquet | `over-the-hill-bouquet` | Bouquet-size checkout regression guard |
| Paw Patrol Bouquet | `paw-patrol-bouquet` | Bouquet-size checkout regression guard |
| Soccer Bouquet | `soccer-bouquet` | Bouquet-size checkout regression guard |
| Space Bouquet | `space-bouquet` | Bouquet-size checkout regression guard |
| Stitch Bouquet | `stitch-bouquet` | Bouquet-size checkout regression guard |
| Unicorn Bouquet | `unicorn-bouquet` | Bouquet-size checkout regression guard |

## Tranche 2 - Simple Purchasable Proof Candidates

These stay out of customer checkout until final owner/product approval. Backend
SO/SI rehearsal passed on 2026-05-17 with 33 sale SKU lines and zero surviving
generated records. Desktop/mobile product page, cart, and checkout preview
proof passed with local restoration verified. Payment cascade also passed for
Payment Request, Payment Entry, Sales Invoice, customer receipt, operator email,
welcome email, idempotency, and rollback cleanup.

| Product | Slug | Required before checkout |
|---|---|---|
| Easter Arch | `easter-arch` | Backend SO/SI, browser, and payment cascade proof passed; still needs final owner/product approval |
| Large head Missionary | `large-head-missionary` | Backend SO/SI passed for 30 variants; browser and payment cascade proof passed; still needs final owner/product approval |
| Mother's day front yard 7' Column | `mothers-day-front-yard-7-column` | Backend SO/SI, browser, and payment cascade proof passed; still needs final owner/product approval |
| Pride Arch | `pride-arch` | Backend SO/SI, browser, and payment cascade proof passed; still needs final owner/product approval |

## Tranche 3 - Multi-Color Browser Proof Passed

These stay out of customer checkout until payment/customer-message cascade,
media update behavior where approved, and final owner/product approval pass.
Backend rehearsal passed on 2026-05-17 with 563 enabled color SKU lines,
source-backed prices, `color_recipes` payloads, SO/SI preservation, and zero
surviving generated records. Local open-mode browser proof also passed at
desktop and mobile widths with 12 product-route checks and 14 visible color
drawer proofs.

| Product | Slug | Required before checkout |
|---|---|---|
| 7' Epic Column | `7-epic-column` | Backend SO/SI and browser proof passed; still needs payment/customer-message cascade, media behavior, and final owner/product approval |
| Baby Shower Combination Photo opt | `baby-shower-combination-photo-opt` | Backend SO/SI and browser proof passed; still needs payment/customer-message cascade, media behavior, and final owner/product approval |
| Baby Table decor | `baby-table-decor` | Backend SO/SI and browser proof passed; still needs payment/customer-message cascade, media behavior, and final owner/product approval |
| classic organic for easel | `classic-organic-for-easel` | Backend SO/SI and browser proof passed; still needs payment/customer-message cascade, media behavior, and final owner/product approval |
| Number Balloon Columns | `number-balloon-columns` | Backend SO/SI and browser proof passed for both color axes; still needs payment/customer-message cascade, media behavior, and final owner/product approval |
| Sleepy Baby Column | `sleepy-baby-column` | Backend SO/SI and browser proof passed; still needs payment/customer-message cascade, media behavior, and final owner/product approval |

## Tranche 4 - Add-On Or Conditional Pricing Blocked

These remain blocked from customer checkout until explicit add-on mapping,
conditional price matrices, quantity/value limits, total provenance, and
SO/SI/receipt preservation are implemented and proved from product source data.

| Product | Slug | Primary blocker |
|---|---|---|
| 6 color rainbow arch | `6-color-rainbow-arch` | Conditional pricing |
| Baby Shower Garland | `baby-shower-garland` | Multi-color, conditional pricing, freeform text |
| Balloon Drop | `balloon-drop` | Multi-color, conditional pricing |
| Basketball Arch | `basketball-arch` | Conditional pricing |
| Classic Arch | `classic-arch` | Multi-color and conditional pricing; final stress case |
| Classic Column | `classic-column` | Multi-color, conditional pricing, freeform text |
| Classic Organic Arch | `classic-organic-arch` | Multi-color, add-ons, conditional pricing, freeform text |
| Classic Organic Balloon Garland | `classic-organic-balloon-garland` | Multi-color, conditional pricing |
| Classic Organic columns | `classic-organic-columns` | Multi-color, conditional pricing |
| Easter Balloon Arch - Bunny Ear | `easter-balloon-arch-bunny-ear` | Conditional pricing |
| Halloween arch | `halloween-arch` | Multi-color, conditional pricing |
| Large Garland | `large-garland` | Multi-color, conditional pricing |
| Large Organic Column | `large-organic-column` | Multi-color, conditional pricing |
| Logo 3 layered bouquet | `logo-3-layered-bouquet` | Multi-color and freeform text |
| Organic Grab n' Go | `organic-grab-n-go` | Multi-color, conditional pricing |
| Pemium Organic Column | `pemium-organic-column` | Multi-color, add-ons, conditional pricing, freeform text |
| Premium Organic Arch | `premium-organic-arch` | Multi-color, add-ons, conditional pricing, freeform text |
| Premium Organic Garland | `premium-organic-garland` | Multi-color, conditional pricing |
| Pride progress Rainbow Balloon Arch | `pride-progress-rainbow-balloon-arch` | Conditional pricing |
| Star Column | `star-column` | Multi-color, add-ons, conditional pricing |

## Tranche 5 - Needs Review Or Missing

These do not enter checkout planning until product-page type, buying path,
source meaning, add-ons, and media/pricing presentation are reviewed.

| Product | Slug |
|---|---|
| Bandage "GET WELL" Bouquet (Latex free) | `bandage-get-well-bouquet-latex-free` |
| Birthday Deliveries | `birthday-deliveries` |
| Butterfly "GET WELL" Bouquet (Latex free) | `butterfly-get-well-bouquet-latex-free` |
| Marble table decor | `marble-table-decor` |
| Shooting star "GET WELL" Bouquet (Latex free) | `shooting-star-get-well-bouquet-latex-free` |

## Next Concrete Work

1. Run payment/customer-message cascade proof for the six multi-color
   repair-lane products.
2. Get final owner/product-scope approval before exposing the simple
   repair-lane products or the multi-color repair-lane products to customers.
3. Use `product-source-repair-map-2026-05-17.md` to repair the remaining
   product-family holds into purchasable products; repull the legacy_source export if
   current source data is incomplete or unclear.
4. Keep all other product families blocked, needs-review, or hidden until their
   tranche gate passes; do not present `quote_first` as the business model.
5. Replace remaining verifier/report wording that says quote-first with
   blocked/import-repair language where the field name itself is not required.
