# Catalog Variant Price Recovery

Active feature handoff for ERPNext Item Price parity against the old Odoo shop.

## Outcome

Every sellable ERPNext product variant should carry the same customer price the
old Odoo shop would have charged for the equivalent required option selection.

This is not the same as variant-count correctness. `catalog_variant_contract.py`
proves active ERPNext variants match the normalized Odoo option combinations.
It does not prove the `Item Price` values are right.

## Current State - 2026-05-08

Resolved:

- Root cause found: the original Odoo scraper trusted product page base price /
  JSON-LD price, then `seed_catalog.py` copied that price to every variant.
- Odoo's source of truth for variant pricing is
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

Fresh sample evidence from Odoo dry-run probes:

| Template | ERPNext | Odoo resolver | Status |
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
- `apps/locally_twisted/locally_twisted/seed/repair_variant_prices_from_odoo.py`
- `scripts/setup/scrape_odoo_live.py`
- `scripts/setup/stage_seed_data.py`
- `scripts/verify/product_variant_price_contract.py`
- `package.json`

Related shop/cart verification:

- `scripts/verify/catalog_variant_contract.py`
- `scripts/verify/cart_checkout_contract.py`
- `scripts/verify/smoke_shop.py`

## Current Verifiers

Passing after the bouquet repair:

```powershell
npm run test:product-prices
python scripts/verify/cart_checkout_contract.py
```

Current broader shop smoke is green again:

```powershell
python scripts/verify/smoke_shop.py
```

The earlier 2026-05-08 category rail/card-rendering failures are closed in the
current open ecommerce website gate. Do not interpret the green shop smoke as
full catalog price parity; it proves the guarded bouquet prices and current
rendered shop flow, while the non-bouquet price recovery remains open.

## How To Continue

1. Stage the Odoo catalog data for in-container repair commands:

   ```powershell
   python scripts/setup/stage_seed_data.py
   ```

2. Run dry-run probes in small batches first:

   ```powershell
   docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.seed.repair_variant_prices_from_odoo.execute --kwargs "{'slug_filter':'6-color-rainbow-arch','dry_run':True}"
   ```

3. Build a full audit report before mass-applying non-bouquet prices. The
   repair command supports `dry_run=True` and `max_products`, but a full
   all-product dry run can be slow because it calls Odoo's resolver for many
   combinations.

4. Apply in bounded batches only after reviewing the dry-run mismatches:

   ```powershell
   docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.seed.repair_variant_prices_from_odoo.execute --kwargs "{'slug_filter':'6-color-rainbow-arch'}"
   ```

5. Extend `scripts/verify/product_variant_price_contract.py` for each repaired
   product family before calling that family closed.

6. Remove ignored staged seed data after repair work if it is no longer needed:

   ```powershell
   Remove-Item -LiteralPath apps\locally_twisted\locally_twisted\seed\_data -Recurse -Force
   ```

## Rules For Future Agents

- Do not claim all product pricing is correct until a full Odoo resolver audit
  has passed or every product family has its own price contract.
- Do not use `_resources/odoo-live/catalog.json` row `price` from the old
  snapshot as proof by itself; older snapshots were generated before dynamic
  price recovery.
- When LT intentionally drops optional Odoo axes from ERPNext variants, query
  Odoo with only the required attribute IDs for the ERPNext variant price.
- Treat full optional combos as add-on/customizer evidence, not necessarily the
  ERPNext Item Price.
- Do not keep `seed/_data/` in git. It is an ignored staging copy only.

## Latest Published Commits

- `c7f9da3 Fix Odoo variant price import` - repaired bouquet-size live prices,
  added dynamic-price repair path, updated scraper/seed behavior, and added the
  bouquet price contract.
- For newer docs/cleanup commits, check `git log --oneline -5` because this
  handoff is intended to stay content-current rather than carry a changelog.
