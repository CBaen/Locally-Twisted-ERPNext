---
id: erpnext-catalog-variant-price-parity
name: ERPNext Catalog Variant Price Parity
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted ERPNext/Frappe catalog imports from legacy_source website_sale
currently_true: local_only
verification_level: 2
last_verified: 2026-05-19
evidence_quality: direct
successful_uses: 2
failed_uses: 2
regressions: 1
depends_on:
  - erpnext-checkout-commerce-rules
  - fail-loud-operating-law
used_by:
  - catalog-variant-price-recovery
  - ecommerce-price-identity-incident-review-2026-05-19
tags:
  - Locally Twisted
  - ERPNext
  - Frappe
  - legacy_source
  - catalog
  - variants
  - pricing
  - webshop
---

# ERPNext Catalog Variant Price Parity

Use this recipe when importing, repairing, auditing, or claiming prices for
ERPNext Item variants that came from the old legacy_source shop.

## Rule

Product page base price is not variant price.

Product Setup saved price is also not public sellable price until it reaches
the Item Price authority or the runtime contract explicitly reads Product Setup
as authority.

For legacy_source website_sale products, resolve variant prices through
`/website_sale/get_combination_info`. Do not trust JSON-LD, card price, listing
price, or scraped page base price as the price for every ERPNext variant.

## Current LT Contract

- The old legacy_source shop at `http://5.78.136.133/shop` is the catalog reference for
  this migration's imported product data.
- legacy_source's product-card/base price is not enough. Variant price truth comes from
  `/website_sale/get_combination_info`, including option price modifiers such
  as size, height, length, topper, LED, and approved add-on deltas.
- ERPNext sells Item variants, not parent variant templates.
- Active ERPNext variants intentionally drop optional legacy_source axes such as
  `Add Foil Number` when those axes are not required product choices.
- When optional axes are dropped, query legacy_source with the required attribute IDs
  only and store that as the ERPNext Item Price.
- Full legacy_source combinations with optional add-ons may have higher prices. Those are
  add-on/customizer evidence, not automatically the ERPNext required-variant
  price.
- `scripts/verify/catalog_variant_contract.py` proves variant shape parity, not
  price parity.
- `scripts/verify/product_variant_price_contract.py` proves the historical
  bouquet-size repair. It is not broad enough for the catalog by itself.
- `scripts/verify/product_price_modifier_contract.py` is the broad local source
  price guard for active variant products. It checks the legacy_source option-price
  modifiers against ERPNext `Item Price` rows and fails if any active variant
  would change.
- `scripts/verify/product_price_display.spec.js` proves at least one real
  product page updates visible price and selected variant item code for a
  non-first priced option.
- Launch/import proof must check source-price truth before downstream
  ERPNext/Stripe agreement. If ERPNext is wrong, Stripe can be perfectly wrong
  with it.

## Implementation Pattern

1. Stage source data for in-container commands when needed:

   ```powershell
   python scripts/setup/stage_seed_data.py
   ```

2. Use the dynamic resolver path:

   ```powershell
   docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.seed.repair_variant_prices_from_legacy_source.execute --kwargs "{'slug_filter':'unicorn-bouquet','dry_run':True}"
   ```

3. Review `old_rate`, `new_rate`, and `would_change`.

4. Apply only bounded, reviewed slices:

   ```powershell
   docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.seed.repair_variant_prices_from_legacy_source.execute --kwargs "{'slug_filter':'unicorn-bouquet'}"
   ```

5. Add or extend a product-family verifier before calling that family complete.

6. Run cart/checkout verification after price changes:

   ```powershell
   npm run test:product-prices
   npm run test:product-price-display
   python scripts/verify/cart_checkout_contract.py
   ```

7. Remove ignored staging copies when done if they are no longer needed:

   ```powershell
   Remove-Item -LiteralPath apps\locally_twisted\locally_twisted\seed\_data -Recurse -Force
   ```

## Known Failure

The original catalog import flattened variant prices because the scraper copied
the product page `base_price` into every `valid_variants` row and
`seed_catalog.py` upserted every Item Price from that base price.

For Unicorn Bouquet, live ERPNext had Small, Medium, and Large all at `$35`.
legacy_source's resolver returned:

- Small: `$35`
- Medium: `$70`
- Large: `$85`

The same bouquet-size pattern was repaired for 13 bouquet templates on
2026-05-08.

On 2026-05-19, GL found the same failure class on
`easter-balloon-arch-bunny-ear`: both active sizes were `$375` in ERPNext while
legacy_source returned `$375` for `20ft` and `$440` for `25ft`. This proved the old
guard was too narrow. The wider incident is tracked in
`workstreams/ecommerce-price-identity-incident-review-2026-05-19.md` and the
failure recipe
`capabilities/failures/ecommerce-variant-price-source-drift.md`.

## Verification

Current focused guard:

```powershell
npm run test:product-prices
```

This now runs both:

- `scripts/verify/product_variant_price_contract.py` for the historical bouquet
  size repair.
- `scripts/verify/product_price_modifier_contract.py` for broad legacy_source modifier
  parity across active variant products.

Visible-page guard for the reported Easter Bunny Ear Arch failure:

```powershell
npm run test:product-price-display
```

Launch gate integration:

```powershell
python scripts/verify/website_launch_verify.py
```

This now runs the broad source-price modifier contract and the visible
price-display contract in addition to the older bouquet price contract.

Current supporting checkout guard:

```powershell
python scripts/verify/cart_checkout_contract.py
```

Current shape guard:

```powershell
python scripts/verify/catalog_variant_contract.py
```

Do not claim live/public pricing approval from these commands. They prove the
local import/runtime contract. Staging/live still require target-site source
price proof after deploy/import, GL local acceptance, and separate payment
cutover approval.

Homepage/product merchandising note: if a public card uses a `From $XX.XX`
claim, it must derive from the same product-page/source-backed starting-price
path or record an explicit GL exception. The 2026-06-24 Customer Favorites
homepage row uses `get_variant_starting_price` for the four approved Website
Item routes instead of hand-typed prices, and Classic Arch was replaced because
it was quote-first and lacked the required visible/source-backed starting
price.

## Receipt

On 2026-05-08, GL flagged that Unicorn Bouquet variants were still the same
price after active product work. Live ERPNext confirmed all active Unicorn
variants were `$35`. Direct legacy_source resolver probes recovered Small `$35`, Medium
`$70`, and Large `$85`. The repair script updated live ERPNext prices for the
bouquet-size family, and `npm run test:product-prices` plus
`cart_checkout_contract.py` passed afterward.

On 2026-05-17, the all-legacy_source sellable reimport first exposed that the import
path could still flatten bouquet-size variants to the scraped page base price.
`scripts/setup/stage_seed_data.py` now stages the price enrichment artifact and
`seed_catalog.py` prefers those approved sale-unit prices before page fallback
prices. The second guarded local reimport passed
`product_variant_price_contract.py`; the manifest reports 53 included products,
0 exclusions, and 290 source-ready sale units.

On 2026-05-19, GL caught `easter-balloon-arch-bunny-ear` not changing price on
size selection. Local ERPNext had both active variants at `$375`, while legacy_source's
combination endpoint returned `$375` for `20ft` and `$440` for `25ft`. The
local DB was corrected for that item first, then
`repair_variant_price_modifiers_from_legacy_source` applied legacy_source option modifiers across
49 variant products. The apply run corrected 8,405 `Item Price` rows; the
post-apply modifier contract reported 49 products and 10,186 active variants
checked with 0 remaining changes. Browser proof now confirms the reported page
selects `20ft` at `$375` and `25ft` at `$440`.

On 2026-06-30, live read-only API proof for `large-head-missionary` showed a
different price authority split: Product Setup saved base/exact prices at
`125.0`, but the live `Standard Selling` Item Price rows and public price
remained `175.0`. That incident is tracked by
`capabilities/failures/product-setup-projection-authority-drift.md`. For owner
save incidents, load that failure recipe in addition to this price parity
recipe.

On 2026-06-30, Phase 9 added
`scripts/dev/lt_product_setup_variant_axis_classification_report.py` for
offline saved-artifact variant-axis classification. Against the saved Birthday
Deliveries artifact, the report showed the current 2,430-variant shape could
be planned as a blocked 3-SKU candidate model: `Delivery Size` as the only
candidate SKU-defining axis, `Delivery themes` as configuration payload, and
`Add Foil Number` plus `Add Bouquet` as paid add-on candidates. `Add Bouquet`
affects saved price, so a collapse design still needs add-on/runtime pricing
proof and cart/order/document labels. This is classification evidence only. It
does not approve mutation, add-on behavior, historical reference migration,
live repair, or public checkout changes.

On 2026-06-30, Phase 10 added
`scripts/dev/lt_product_setup_dependency_rollback_report.py` and
`scripts/verify/product_setup_dependency_rollback_contract.py` for offline
dependency/rollback target capture from saved catalog authority artifacts.
Against Birthday Deliveries, it captures row-level saved-artifact rollback rows
for 2,430 variant Items, 2,430 Item Prices, four Product Setup option rows, and
nine media/gallery/pointer rows. It intentionally exits blocked while live
route proof, brand-lane proof, historical references, File/slideshow reference
proof, add-on/runtime behavior, and owner mutation approval are missing. This
is a planning and safety artifact, not release approval.

On 2026-06-30, Phase 11 added
`scripts/dev/lt_product_setup_replacement_model_report.py` and
`scripts/verify/product_setup_replacement_model_contract.py` for no-write
replacement model design. Against Birthday Deliveries, it produces three
design-only candidate SKU rows from `Delivery Size`, models `Delivery themes`
as configuration payload, and holds `Add Foil Number` plus `Add Bouquet` as
paid add-on candidates. It intentionally exits blocked because the model still
needs add-on/runtime pricing, payload preservation, live/public proof,
historical references, owner approval, and a release packet before any catalog
write.
