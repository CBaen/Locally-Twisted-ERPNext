# Multi-Color Purchasable Rehearsal - 2026-05-17

## Purpose

Rollback-safe backend proof for the first multi-color product repair tranche.
This follows GL's correction that these are purchasable product targets, not
business quote-first products.

This is not live approval. `lt_ecommerce_paused=1` remains the customer
exposure lock.

## Products Proved

| Product | Slug | Enabled color SKUs | Source canonical combos | Price |
|---|---|---:|---:|---:|
| 7' Epic Column | `7-epic-column` | 51 | 51 | $100 |
| Baby Shower Combination Photo opt | `baby-shower-combination-photo-opt` | 51 | 51 | $650 |
| Baby Table decor | `baby-table-decor` | 2 | 2 | $30 |
| classic organic for easel | `classic-organic-for-easel` | 51 | 51 | $100 |
| Number Balloon Columns | `number-balloon-columns` | 357 | 357 | $55 |
| Sleepy Baby Column | `sleepy-baby-column` | 51 | 51 | $220 |

Total: 563 enabled color SKUs.

## What Passed

Command:

```bash
python scripts/verify/multi_color_purchasable_rehearsal_contract.py --report workstreams/ecommerce-audit/multi-color-purchasable-rehearsal-2026-05-17.json
```

Result:

- PASS.
- Temporarily applied `simple_product|checkout` to the six Website Items inside
  one ERPNext transaction.
- Proved legacy_source source rows exist for all six products.
- Proved source color axes are recognized as balloon color axes.
- Proved server-side product options target `color_recipes` with
  `multi_color_recipe_builder`.
- Proved all 563 enabled live color SKUs resolve through checkout with
  `color_recipes` and no color leakage into `selected_options`.
- Proved all 563 Sales Order lines and matching Sales Invoice lines preserve
  the LT configuration fields.
- Intercepted commits and rolled back all generated records.
- Survivor counts after rollback: Customer 0, Sales Order 0, Sales Invoice 0.

## Source Normalization Fix

The first run failed because legacy_source's export contains duplicate color labels that
differ only by casing: `Blue Slate` / `Blue slate` and `Smoke Grey` /
`Smoke grey`. ERPNext Item Attribute import already treats those as the same
source color and stores the first-seen canonical casing.

The shared color canonicalizer now maps those lowercase variants to the same
canonical names used by the legacy_source value-normalize map:

- `Blue slate` -> `Blue Slate`
- `Smoke grey` -> `Smoke Grey`

`product_page_runtime_contract.py` now guards this in the multi-color recipe
cleanup path.

## Not Proved Yet

- Browser product-page interaction for these six products.
- Browser cart and checkout preview for these six products.
- Payment Request, Payment Entry, receipt, operator email, and welcome email
  cascade for these six products.
- Variant or combination image updates for these six products beyond existing
  media guard behavior.
- Owner/product-scope approval for customer exposure.
- Staging or live release.

## Next Gate

Run a local open-mode browser proof for the same six products, then run a
payment/customer-message cascade proof. Keep them blocked from customer
checkout until those pass and owner/product approval is explicit.

## Backlinks

- `workstreams/ecommerce-audit/product-family-certification-truth-table-2026-05-17.md`
- `workstreams/ecommerce-audit/product-source-repair-map-2026-05-17.md`
- `workstreams/ecommerce-audit/README.md`
- `CODING-HANDOFF.md`
- `scripts/verify/multi_color_purchasable_rehearsal_contract.py`
- `apps/locally_twisted/locally_twisted/verify/multi_color_purchasable_rehearsal_contract.py`
