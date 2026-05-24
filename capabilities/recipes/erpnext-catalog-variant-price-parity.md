---
id: erpnext-catalog-variant-price-parity
name: ERPNext Catalog Variant Price Parity
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted ERPNext/Frappe catalog imports from Odoo website_sale
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
  - Odoo
  - catalog
  - variants
  - pricing
  - webshop
---

# ERPNext Catalog Variant Price Parity

Use this recipe when importing, repairing, auditing, or claiming prices for
ERPNext Item variants that came from the old Odoo shop.

## Rule

Product page base price is not variant price.

For Odoo website_sale products, resolve variant prices through
`/website_sale/get_combination_info`. Do not trust JSON-LD, card price, listing
price, or scraped page base price as the price for every ERPNext variant.

## Current LT Contract

- The old Odoo shop at `http://5.78.136.133/shop` is the catalog reference for
  this migration's imported product data.
- Odoo's product-card/base price is not enough. Variant price truth comes from
  `/website_sale/get_combination_info`, including option price modifiers such
  as size, height, length, topper, LED, and approved add-on deltas.
- ERPNext sells Item variants, not parent variant templates.
- Active ERPNext variants intentionally drop optional Odoo axes such as
  `Add Foil Number` when those axes are not required product choices.
- When optional axes are dropped, query Odoo with the required attribute IDs
  only and store that as the ERPNext Item Price.
- Full Odoo combinations with optional add-ons may have higher prices. Those are
  add-on/customizer evidence, not automatically the ERPNext required-variant
  price.
- `scripts/verify/catalog_variant_contract.py` proves variant shape parity, not
  price parity.
- `scripts/verify/product_variant_price_contract.py` proves the historical
  bouquet-size repair. It is not broad enough for the catalog by itself.
- `scripts/verify/product_price_modifier_contract.py` is the broad local source
  price guard for active variant products. It checks the Odoo option-price
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
   docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.seed.repair_variant_prices_from_odoo.execute --kwargs "{'slug_filter':'unicorn-bouquet','dry_run':True}"
   ```

3. Review `old_rate`, `new_rate`, and `would_change`.

4. Apply only bounded, reviewed slices:

   ```powershell
   docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.seed.repair_variant_prices_from_odoo.execute --kwargs "{'slug_filter':'unicorn-bouquet'}"
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
Odoo's resolver returned:

- Small: `$35`
- Medium: `$70`
- Large: `$85`

The same bouquet-size pattern was repaired for 13 bouquet templates on
2026-05-08.

On 2026-05-19, GL found the same failure class on
`easter-balloon-arch-bunny-ear`: both active sizes were `$375` in ERPNext while
Odoo returned `$375` for `20ft` and `$440` for `25ft`. This proved the old
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
- `scripts/verify/product_price_modifier_contract.py` for broad Odoo modifier
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

## Receipt

On 2026-05-08, GL flagged that Unicorn Bouquet variants were still the same
price after active product work. Live ERPNext confirmed all active Unicorn
variants were `$35`. Direct Odoo resolver probes recovered Small `$35`, Medium
`$70`, and Large `$85`. The repair script updated live ERPNext prices for the
bouquet-size family, and `npm run test:product-prices` plus
`cart_checkout_contract.py` passed afterward.

On 2026-05-17, the all-Odoo sellable reimport first exposed that the import
path could still flatten bouquet-size variants to the scraped page base price.
`scripts/setup/stage_seed_data.py` now stages the price enrichment artifact and
`seed_catalog.py` prefers those approved sale-unit prices before page fallback
prices. The second guarded local reimport passed
`product_variant_price_contract.py`; the manifest reports 53 included products,
0 exclusions, and 290 source-ready sale units.

On 2026-05-19, GL caught `easter-balloon-arch-bunny-ear` not changing price on
size selection. Local ERPNext had both active variants at `$375`, while Odoo's
combination endpoint returned `$375` for `20ft` and `$440` for `25ft`. The
local DB was corrected for that item first, then
`repair_variant_price_modifiers_from_odoo` applied Odoo option modifiers across
49 variant products. The apply run corrected 8,405 `Item Price` rows; the
post-apply modifier contract reported 49 products and 10,186 active variants
checked with 0 remaining changes. Browser proof now confirms the reported page
selects `20ft` at `$375` and `25ft` at `$440`.
