---
id: erpnext-catalog-variant-price-parity
name: ERPNext Catalog Variant Price Parity
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted ERPNext/Frappe catalog imports from Odoo website_sale
currently_true: unknown
verification_level: 2
last_verified: 2026-05-17
evidence_quality: direct
successful_uses: 1
failed_uses: 1
regressions: 0
depends_on:
  - erpnext-checkout-commerce-rules
  - fail-loud-operating-law
used_by:
  - catalog-variant-price-recovery
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
- `scripts/verify/product_variant_price_contract.py` proves the currently
  guarded price families used by the all-Odoo sellable reimport proof. Pair it
  with `v1_odoo_erpnext_import_manifest.py` and the all-product browser proof
  before claiming catalog-wide checkout readiness.

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
2026-05-08. The remaining non-bouquet catalog is not fully certified.

## Verification

Current focused guard:

```powershell
npm run test:product-prices
```

Current supporting checkout guard:

```powershell
python scripts/verify/cart_checkout_contract.py
```

Current shape guard:

```powershell
python scripts/verify/catalog_variant_contract.py
```

Do not claim live/public pricing approval from these commands. They prove the
local import/runtime contract; GL still needs to test locally before any live
release packet.

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
