# Phase 9 - Variant Axis Classification For Birthday Deliveries

Date: 2026-06-30

Status: source-only offline classification tooling complete locally. No
deploy, cache clear, live ERPNext mutation, catalog record mutation,
provider/payment/DNS/Frappe Cloud change, customer message, or product-scope
decision occurred.

## Purpose

Phase 9 starts the variant-explosion repair path without touching catalog data.
The goal is to classify which owner-entered axes truly need ERPNext SKU
variants and which axes should become configuration payload, paid add-ons,
review context, media logic, or unsupported states.

Birthday Deliveries is the first proof target because the saved catalog
authority artifact shows 2,430 active variants and 2,430 Item Prices from four
Product Setup axes.

## What Changed

- `scripts/dev/lt_product_setup_variant_axis_classification_report.py`
  - Added an offline saved-artifact report. It does not call the network, read
    credentials, inspect Docker, clear cache, deploy, or write ERPNext data.
  - Reads saved Product Setup option rows, exact price rows, variants, and Item
    Prices.
  - Detects whether an axis changes exact price while other axes stay constant.
  - Emits product identity, match summary, current shape, axis evidence, payload
    target, collapse summary, price strategy, blockers, and next safe actions.
  - Keeps mutation approval false.
- `scripts/verify/product_setup_variant_axis_classification_contract.py`
  - Added synthetic coverage proving the report keeps variant-collapse work
    blocked while identifying a smaller candidate SKU set.
  - Uses the saved Birthday Deliveries artifact when present.

## Birthday Deliveries Result

Input artifact:

- `/tmp/lt-catalog-authority-full-20260630/044-birthday-deliveries.json`

Current saved evidence:

- Current variants: `2,430`
- Current Item Prices: `2,430`
- Current Product Setup option axes: `4`
- Current axes:
  - `Delivery Size`: 3 values
  - `Delivery themes`: 27 values
  - `Add Foil Number`: 10 values
  - `Add Bouquet`: 3 values

Offline candidate classification:

- Candidate SKU-defining axis: `Delivery Size`
- Candidate bounded SKU count: `3`
- Configuration payload candidate: `Delivery themes`
- Paid add-on candidates: `Add Foil Number`, `Add Bouquet`

Price strategy finding:

- `Delivery Size` and `Add Bouquet` affect exact saved price.
- `Add Bouquet` is held as a paid add-on candidate because it reads as a
  modifier/add-on axis. Exact prices cannot be trusted after variant collapse
  until non-SKU price-affecting axes have add-on/runtime pricing proof and
  cart/order/document labels.

The report intentionally exits nonzero with blockers:

- `current_sku_axes_need_reclassification`
- `variant_explosion_requires_no_write_plan`

This is the correct result. It proves a safer candidate model, not permission
to mutate the catalog.

## Witness Review

Review type: real multi-agent witness/triad support.

Intent/risk witness acceptance:

- Phase 9 must stay source-only.
- Birthday Deliveries must remain planning evidence only.
- Axis rows need current behavior, value count, multiplier, price-signal
  summary, proposed classification, blockers, and proof needed before writes.
- Classification must match the protective contract categories.
- Any collapse plan must stay dry-run and preserve cart/order/document/payment
  identity before mutation.

Technical witness acceptance:

- Reuse existing authority packet and Product Setup runtime/apply-plan
  contracts.
- Include input artifacts, product identity, match summary, current counts,
  axis price evidence, candidate payload targets, collapse summary, price
  strategy, blockers, and next safe actions.
- State that variant mapping is inferred from Product Setup price-row
  `option_summary` until a later artifact includes Item Variant Attribute rows.
- Do not imply deletion, disablement, rename, repurpose, or collapse readiness.

## Verification

Passed:

```bash
python -m py_compile scripts/dev/lt_product_setup_variant_axis_classification_report.py scripts/verify/product_setup_variant_axis_classification_contract.py
python scripts/verify/product_setup_variant_axis_classification_contract.py
```

Intentional blocker run:

```bash
python scripts/dev/lt_product_setup_variant_axis_classification_report.py --input /tmp/lt-catalog-authority-full-20260630/044-birthday-deliveries.json --output /tmp/lt-birthday-deliveries-variant-axis-classification.json --pretty --fail-on-blocker
```

That command intentionally exited `1` because Birthday Deliveries remains
blocked for mutation. It wrote the offline report to:

- `/tmp/lt-birthday-deliveries-variant-axis-classification.json`

Capability gate: PASS.

Loaded resources:

- `capabilities/INDEX.md`
- `capabilities/failures/product-setup-projection-authority-drift.md`
- `capabilities/recipes/erpnext-catalog-variant-price-parity.md`
- `capabilities/recipes/erpnext-product-blueprint-authoring.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/protective-contracts.md`

## Still Not Claimed

- No variant, Item, Item Price, Website Item, Product Setup, order, invoice,
  payment, document, file, or customer-message record was changed.
- No live/public route proof was refreshed.
- No owner approval for actual collapse/migration was inferred.
- No add-on Items, add-on prices, cart expansion, invoice labels, payment
  labels, or receipt behavior were implemented.
- No historical dependency or rollback snapshot packet exists yet.
- Birthday Deliveries is not fixed; it is better mapped.

## Next Safe Work

1. Add dependency/rollback target capture for Birthday Deliveries current
   variants, Item Prices, historical references, media rules, and route/cart
   identity.
2. Design the no-write replacement model: 3 SKU variants plus payload fields
   for theme and add-on choices, with cart-line identity and document labels.
3. Only after that, produce a pre-mutation packet for review. Do not disable,
   delete, rename, repurpose, or collapse current variant records from Phase 9.
