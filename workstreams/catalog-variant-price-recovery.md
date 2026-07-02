# Catalog Variant Price Recovery

Active feature handoff for ERPNext Item Price parity against the catalog_data shop.

## Outcome

Every sellable ERPNext product variant should carry the same customer price the
catalog_data shop would have charged for the equivalent required option selection.

This is not the same as variant-count correctness. `catalog_variant_contract.py`
proves active ERPNext variants match the normalized catalog_data option combinations.
It does not prove the `Item Price` values are right.

## Current State - 2026-05-19

Resolved in the local ERPNext database:

- GL caught the Easter Bunny Ear Arch product page still showing the same
  price when the customer selected different arch sizes.
- Root cause confirmed: non-bouquet variant families still had flattened
  ERPNext `Item Price` rows from the original base-price import. The product
  page was mostly displaying the backend value it was given.
- Source of truth confirmed again: the catalog_data shop at
  `shop` and its `/website_sale/get_combination_info`
  endpoint. For `easter-balloon-arch-bunny-ear`, catalog_data returns:
  - `20ft`: `$375`
  - `25ft`: `$440`
- Local ERPNext now matches those prices:
  - `easter-balloon-arch-bunny-ear-20F`: `$375`
  - `easter-balloon-arch-bunny-ear-25F`: `$440`
- Added `locally_twisted.seed.repair_variant_price_modifiers_from_catalog_data` to
  recover catalog_data option price modifiers and apply them across active ERPNext
  variants without stopping on large color/customizer families.
- Applied the modifier repair locally across 49 variant products:
  - 10,186 active variants inspected.
  - 8,405 `Item Price` rows corrected during the apply run.
  - Post-apply dry-run reported 0 remaining variant prices that would change.
- Added `scripts/verify/product_price_modifier_contract.py` and included it in
  `npm run test:product-prices`, so bouquet-specific price checks are now paired
  with the broad catalog_data modifier parity gate.
- Added `scripts/verify/product_price_display.spec.js` and
  `npm run test:product-price-display` to prove the actual product page updates
  the visible price and selected variant item code for the reported arch.
- Opened the wider incident review at
  `workstreams/ecommerce-price-identity-incident-review-2026-05-19.md` and the
  failure recipe at
  `capabilities/failures/ecommerce-variant-price-source-drift.md`.
- Wired the broad source-price modifier and visible price-display gates into
  `scripts/verify/website_launch_verify.py`; added the same class of checks to
  the product import readiness command list.

Passing proof after repair:

```bash
python scripts/verify/catalog_variant_contract.py
npm run test:product-prices
npm run test:product-price-display
```

Focused cascade proof:

- `locally_twisted.api.cart.get_cart_items` now returns:
  - `easter-balloon-arch-bunny-ear-20F`: `price_list_rate=375.0`
  - `easter-balloon-arch-bunny-ear-25F`: `price_list_rate=440.0`

Known separate drift:

- `python scripts/verify/cart_checkout_contract.py` still fails two color-recipe
  assertions because the current backend routes that tested color-recipe item to
  quote-required instead of checkout. That is separate from the size/price
  repair and should be handled in the checkout/color-recipe lane, not mixed into
  this pricing correction.

## Prior State - 2026-05-08

Resolved:

- Root cause found: the original catalog_data scraper trusted product page base price /
  JSON-LD price, then `seed_catalog.py` copied that price to every variant.
- catalog_data's source of truth for variant pricing is
  `/website_sale/get_combination_info`.
- The bouquet-size family is repaired in live ERPNext:
  - Small: `$35`
  - Medium: `$70`
  - Large: `$85`
- Repaired bouquet templates: `unicorn-bouquet`, `mickey-mouse-bouquet`,
  `minion-bouquet`, `encanto-bouquet`, `stitch-bouquet`,
  `flamingo-bouquet`, `football-bouquet`, `soccer-bouquet`,
  `over-the-hill-bouquet`, `space-bouquet`, `paw-patrol-bouquet`,
  `elsa-bouquet`, and `holy-cow-bouquet`.
- Guard added: `npm run test:product-prices`, included in
  `npm run test:website-verify`.

Not resolved:

- Full catalog pricing is not certified.
- Live ERPNext has 49 active variant templates. Only the 13 bouquet-size
  templates have been fully repaired and guarded so far.
- 36 non-bouquet variant templates still show one live active price point each.
  Some are legitimately flat; others are already proven wrong.

Fresh sample evidence from catalog_data dry-run probes:

| Template | ERPNext | catalog_data resolver | Status |
|---|---:|---:|---|
| `6-color-rainbow-arch-20F` | `$340` | `$340` | ok |
| `6-color-rainbow-arch-25F` | `$340` | `$425` | wrong |
| `basketball-arch-25F` | `$340` | `$425` | wrong |
| `easter-balloon-arch-bunny-ear-25F` | `$375` | `$440` | wrong |
| `pride-progress-rainbow-balloon-arch-25F` | `$260` | `$325` | wrong |
| `pride-progress-rainbow-balloon-arch-30F` | `$260` | `$390` | wrong |
| `pride-progress-rainbow-balloon-arch-35F` | `$260` | `$455` | wrong |
| `6-graduation-stands` variants | `$45` | `$45` | flat-ok sample |
| `baby-table-decor` variants | `$30` | `$30` | flat-ok sample |

## Files

Production and repair path:

- `apps/locally_twisted/locally_twisted/seed/seed_catalog.py`
- `apps/locally_twisted/locally_twisted/seed/repair_variant_prices_from_catalog_source.py`
- `scripts/setup/scrape_catalog_data_live.py`
- `scripts/setup/stage_seed_data.py`
- `scripts/verify/product_variant_price_contract.py`
- `package.json`

Related shop/cart verification:

- `scripts/verify/catalog_variant_contract.py`
- `scripts/verify/cart_checkout_contract.py`
- `scripts/verify/smoke_shop.py`

## Current Verifiers - 2026-05-19

Passing after the broad local modifier repair:

```bash
npm run test:product-prices
npm run test:product-price-display
python scripts/verify/catalog_variant_contract.py
```

Supporting checkout/cart proof for the reported Easter arch variants:

```bash
locally_twisted.api.cart.get_cart_items
```

`python scripts/verify/cart_checkout_contract.py` currently has separate
color-recipe drift because the tested color-recipe item is routed to quote. Do
not treat that as part of the size-price repair; handle it in the
checkout/color-recipe lane.

## How To Continue

For this lane, the next work is not another narrow product patch. Treat any
price issue as source-price identity work:

1. Stage the catalog_data catalog data for in-container repair commands when source data
   needs refreshing:

   ```bash
   python scripts/setup/stage_seed_data.py
   ```

2. Run the broad dry-run source-price guard before and after any catalog import,
   repair, seed, selector, or checkout-price change:

   ```bash
   python scripts/verify/product_price_modifier_contract.py
   ```

3. Prove visible customer behavior for non-first priced options:

   ```bash
   npm run test:product-price-display
   ```

4. If the broad guard fails, use the repair script in dry-run mode first:

   ```bash
   docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.seed.repair_variant_price_modifiers_from_catalog_data.execute --kwargs "{'dry_run': True, 'strict': False}"
   ```

5. Apply only after reviewing mismatches and confirming the target is local or a
   GL-approved staging/live maintenance window:

   ```bash
   docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.seed.repair_variant_price_modifiers_from_catalog_data.execute --kwargs "{'strict': False}"
   ```

6. Remove ignored staged seed data after repair work if it is no longer needed:

   ```bash
   Remove-Item -LiteralPath apps/locally_twisted/locally_twisted/seed/_data -Recurse -Force
   ```

## Rules For Future Agents

- Do not claim product pricing is correct unless the broad source-price modifier
  gate passes on the target DB and representative visible/cart/checkout proof
  covers non-first priced options.
- Do not use `_resources/catalog-source/catalog.json` row `price` from the old
  snapshot as proof by itself; older snapshots were generated before dynamic
  price recovery.
- When LT intentionally drops optional catalog_data axes from ERPNext variants, query
  catalog_data with only the required attribute IDs for the ERPNext variant price.
- Treat full optional combos as add-on/customizer evidence, not necessarily the
  ERPNext Item Price.
- Do not keep `seed/_data/` in git. It is an ignored staging copy only.

## Latest Published Commits

- `c7f9da3 Fix catalog_data variant price import` - repaired bouquet-size live prices,
  added dynamic-price repair path, updated scraper/seed behavior, and added the
  bouquet price contract.
- For newer docs/cleanup commits, check `git log --oneline -5` because this
  handoff is intended to stay content-current rather than carry a changelog.
