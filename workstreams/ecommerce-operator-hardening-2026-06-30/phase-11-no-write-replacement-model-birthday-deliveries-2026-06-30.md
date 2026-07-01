# Phase 11 - No-Write Replacement Model For Birthday Deliveries

Date: 2026-06-30

Status: source-only/offline no-write replacement model exists. This is design
evidence only. No deploy, cache clear, ERPNext/live mutation, provider/payment
action, DNS change, customer message, secret read, variant collapse, record
disablement, record deletion, route change, or product-scope approval occurred.

## Purpose

Phase 9 classified Birthday Deliveries axes. Phase 10 captured saved-artifact
rollback targets and blockers. Phase 11 combines those two packets into a
no-write replacement model so the next agent can see the candidate shape without
mistaking it for mutation approval.

## Output

Tooling:

- `scripts/dev/lt_product_setup_replacement_model_report.py`
- `scripts/verify/product_setup_replacement_model_contract.py`

Saved Birthday Deliveries run:

```bash
python scripts/dev/lt_product_setup_replacement_model_report.py --classification /tmp/lt-birthday-deliveries-variant-axis-classification.json --rollback /tmp/lt-birthday-deliveries-dependency-rollback-report.json --source-artifact /tmp/lt-catalog-authority-full-20260630/044-birthday-deliveries.json --output /tmp/lt-birthday-deliveries-replacement-model-report.json --pretty --fail-on-blocker
```

Result: expected exit `1`.

Model result:

- Current preserved shape: `2,430` variant Items and `2,430` Item Prices.
- Candidate SKU axis: `Delivery Size`.
- Candidate SKU rows: `3` design-only rows for `Small`, `Medium`, and `Large`.
- Configuration payload axis: `Delivery themes`.
- Paid add-on candidates: `Add Foil Number` and `Add Bouquet`.
- Blocker count: `27`.

The replacement report includes current saved-artifact rollback row counts,
candidate SKU price hints from current exact price rows, configuration payload
contracts, paid add-on contracts, proposed record actions, and blockers.

## Important Limits

This phase does not approve:

- the 3-SKU model;
- disabling, deleting, renaming, repurposing, or collapsing current variants;
- exact replacement Item Prices;
- paid add-on runtime behavior;
- cart payload preservation;
- Sales Order, invoice, payment, receipt, or customer-label behavior;
- live brand-lane proof;
- public route proof;
- File/slideshow reference proof;
- owner-scope approval;
- deployment, cache clear, or live write paths.

`Add Bouquet` affects current saved price, so the replacement model still
blocks exact price trust until add-on/runtime pricing and document labels exist.

## Triad / Witness Note

Phase 11 inherits Phase 9 and Phase 10 real witness findings. A fresh
post-Phase-10 subagent spawn for an additional review lane hit the platform
usage limit and errored before work began, so no new Phase 11 subagent review is
claimed. To stay inside the user's no-live/no-deploy constraints, this slice
keeps all output no-write and blocked.

## Verification

Capability gate: PASS.

Loaded resources:

- `capabilities/INDEX.md`
- `capabilities/failures/product-setup-projection-authority-drift.md`
- `capabilities/recipes/erpnext-catalog-variant-price-parity.md`
- `capabilities/recipes/erpnext-product-blueprint-authoring.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/protective-contracts.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/phase-9-variant-axis-classification-birthday-deliveries-2026-06-30.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/phase-10-dependency-rollback-capture-birthday-deliveries-2026-06-30.md`

Checks:

```bash
python -m py_compile scripts/dev/lt_product_setup_replacement_model_report.py scripts/verify/product_setup_replacement_model_contract.py
python scripts/verify/product_setup_replacement_model_contract.py
python scripts/dev/lt_product_setup_replacement_model_report.py --classification /tmp/lt-birthday-deliveries-variant-axis-classification.json --rollback /tmp/lt-birthday-deliveries-dependency-rollback-report.json --source-artifact /tmp/lt-catalog-authority-full-20260630/044-birthday-deliveries.json --output /tmp/lt-birthday-deliveries-replacement-model-report.json --pretty --fail-on-blocker
```

Results:

- `py_compile`: pass.
- `product_setup_replacement_model_contract.py`: pass, 3 tests.
- Saved Birthday Deliveries report: expected exit `1`, 3 design-only candidate
  SKUs, 27 blockers.

No runtime, browser, ERPNext, provider, payment, DNS, cache, deploy, or customer
checks were run because this slice is source-only/offline.

## Next Safe Work

The next safe slice is source-only owner-visible publish/apply contract design
for Product Setup changes:

- define the exact no-write preview packet that must exist before an owner can
  request product publication or repair;
- define add-on/runtime pricing proof for paid add-on candidates;
- define payload-preservation proof for configuration axes;
- define public/cart/order/document verification requirements;
- keep all writes blocked until the pre-mutation release packet exists.
