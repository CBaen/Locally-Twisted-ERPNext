# Product Family Certification Truth Table - 2026-05-17

## Purpose

Backend-first certification map for existing Locally Twisted ecommerce product
families. This is the control artifact for the active goal: certify products in
tranches, proving pricing, variant logic, media, product-page UX, checkout,
payment, invoice, receipt, and owner/operator cascades before any public
ecommerce release claim.

This is not a live-release approval. `lt_ecommerce_paused=1` remains the
customer exposure lock.

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
| Product pattern contract | PASS | `python scripts/verify/product_pattern_contract.py` via `complex_checkout_scaffold.py`; 53 products, 18 checkout, 30 quote-first, 5 needs-review, no checkout blockers |
| Complex checkout scaffold | PASS | `python scripts/verify/complex_checkout_scaffold.py`; 18 direct checkout guards, 4 simple lane-flip candidates, 6 multi-color UI products, 20 add-on/conditional blocked, 5 needs-review |
| Price readiness | PASS | `python scripts/verify/product_page_price_readiness_contract.py`; backend-first gate now reports 18 backend checkout products and 51/51 checkout sale units priced; source-template classification still shows 15 checkout products and 8 source/backend lane differences for audit context |
| Media visibility | PASS with caveat | `python scripts/verify/product_page_media_visibility_contract.py`; 53 live primary images, 1,751 active variant images, 95 source extras held back, 0 unsafe unclassified images |
| Checkout family cascade | PASS | `python scripts/verify/checkout_product_family_contract.py`; 47 sale SKUs and 86 SO/SI rows rolled back |
| Variant media safety | PASS | `python scripts/verify/variant_media_contract.py`; unclassified media held and product pages keep approved primary image |
| Product-page runtime | PASS | `python scripts/verify/product_page_runtime_contract.py`; selected config preserved through SO/SI/Quotation paths in rollback |
| Cart/checkout runtime | PASS | `python scripts/verify/cart_checkout_contract.py`; quote-first blocks, cart line keys, add-ons, over-limit quantities, and stale payload failures guarded |
| Stripe amount parity | PASS | `python scripts/verify/stripe_amount_parity_contract.py`; hosted checkout cents match ERPNext totals |
| Payment cascade | PASS | `python scripts/verify/payment_cascade_contract.py`; SO -> PR -> Payment Entry -> SI -> receipt/operator/welcome email rolled back |

## Source / Backend Lane Difference

The price-readiness verifier now reports both source-template classification and
current backend Website Item lane. Backend lane remains authoritative for
checkout readiness.

- Source-template classification: 15 checkout products, 38 quote-first products.
- Current backend classification: 18 checkout products, 30 quote-first products,
  5 needs-review products.
- Backend checkout price gate: 18/18 backend checkout products and 51/51 sale
  units have live ERPNext price coverage.

The three products promoted to backend checkout relative to source-template
classification are:

- `6-graduation-stands`
- `7-butterfly-column`
- `graduation-grab-n-go`

They still need product-family UX/cascade proof like every other Tranche 1
product, but the live ERPNext price gate now covers them.

The five backend needs-review products relative to source-template quote-first
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
| Simple lane-flip candidate | 4 | Quote-first now; can be considered for checkout only after focused local rehearsal |
| Multi-color recipe UI required | 6 | Needs customer-facing multi-color UI plus backend validation before checkout |
| Add-on or conditional pricing blocked | 20 | Needs explicit add-on and/or conditional pricing contracts before checkout |
| Needs review or missing | 5 | Keep blocked/quote-first/hidden until product-page type, lane, and source meaning are reviewed |

## Tranche 1 - Preserve Current Direct Checkout Products

These are not blanket live-approved. They are the first certification tranche:
preserve current checkout behavior, then prove page UX and cascade family by
family.

| Product | Slug | Current next step |
|---|---|---|
| 6' Graduation stands | `6-graduation-stands` | Price gate covers 2/2 sale units; run product-family UX/cascade proof |
| 7' Butterfly Column | `7-butterfly-column` | Price gate covers 1/1 sale unit; run product-family UX/cascade proof |
| Easter Balloon Cups | `easter-balloon-cups` | Preserve direct checkout and prove selected option receipt parity |
| Elsa Bouquet | `elsa-bouquet` | Bouquet-size checkout regression guard |
| Encanto Bouquet | `encanto-bouquet` | Bouquet-size checkout regression guard |
| Flamingo Bouquet | `flamingo-bouquet` | Bouquet-size checkout regression guard |
| Football Bouquet | `football-bouquet` | Bouquet-size checkout regression guard |
| Graduation Grab n Go | `graduation-grab-n-go` | Price gate covers 1/1 sale unit; run product-family UX/cascade proof |
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

## Tranche 2 - Simple Lane-Flip Candidates

These stay quote-first until a focused local lane-flip rehearsal proves product
page, cart, checkout, payment, invoice, receipt, and owner/operator payload
parity.

| Product | Slug | Required before checkout |
|---|---|---|
| Easter Arch | `easter-arch` | Focused local lane-flip rehearsal proof |
| Large head Missionary | `large-head-missionary` | Focused local lane-flip rehearsal proof |
| Mother's day front yard 7' Column | `mothers-day-front-yard-7-column` | Focused local lane-flip rehearsal proof |
| Pride Arch | `pride-arch` | Focused local lane-flip rehearsal proof |

## Tranche 3 - Multi-Color Recipe UI Required

These require customer-facing multi-color recipe UI, backend validation, image
update behavior where approved, and receipt summary parity before checkout.

| Product | Slug |
|---|---|
| 7' Epic Column | `7-epic-column` |
| Baby Shower Combination Photo opt | `baby-shower-combination-photo-opt` |
| Baby Table decor | `baby-table-decor` |
| classic organic for easel | `classic-organic-for-easel` |
| Number Balloon Columns | `number-balloon-columns` |
| Sleepy Baby Column | `sleepy-baby-column` |

## Tranche 4 - Add-On Or Conditional Pricing Blocked

These remain quote-first until explicit add-on mapping, conditional price
matrices, quantity/value limits, total provenance, and SO/SI/receipt
preservation are implemented and proved.

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

1. Build a focused Tranche 1 certification runner/report that proves the 18
   current direct-checkout products by family, not only as a grouped contract.
2. Add browser screenshots or Playwright checks for the Tranche 1 product-page
   UX at desktop and mobile widths before any design claim.
3. Keep all other product families quote-first, needs-review, or hidden until
   their tranche gate passes.
