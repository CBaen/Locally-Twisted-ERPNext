# Phase 8 - Owner-Visible Runtime Authority Blockers

Date: 2026-06-30

Status: source-only Desk/Product Setup blocker hardening complete locally.
No deploy, cache clear, live ERPNext mutation, provider/payment/DNS/Frappe
Cloud change, customer message, or product-scope decision occurred.

## Purpose

Phase 7 made runtime lookup fail closed when Product Setup authority is
ambiguous or brand-unsafe. Phase 8 makes the same class of problem visible in
Product Setup validation before a record can imply preview, staging, live
approval, or local apply readiness.

## What Changed

- `apps/locally_twisted/locally_twisted/product_blueprint_runtime_authority.py`
  - Added read-only runtime authority save blockers for active Product Setup
    statuses.
  - Blocks active Product Setup when a linked Website Item exists but
    operating-brand runtime fields are not installed.
  - Blocks active Product Setup when linked Website Item brand/state is not
    `operating_brand` plus `source_declared`.
  - Blocks active Product Setup when linked Website Item item code disagrees
    with the Product Setup target Item or product slug.
  - Does not block drafts or new preview plans when no existing Website Item is
    found.
- `apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_product_blueprint/lt_product_blueprint.py`
  - Calls runtime authority blockers during Desk validation beside the existing
    same-brand active uniqueness guard.
  - Appends blockers to both `blockers` and `save_blockers`, sets
    `validation_status = Blocked`, and throws through the existing save path.
- `scripts/verify/product_blueprint_contract.py`
  - Added fake-Frappe coverage for valid Website Item brand metadata, missing
    runtime fields, mismatched brand, missing authority state, no existing
    Website Item, and target item mismatch.

## Witness Review

Review type: real multi-agent witness/triad support.

- Intent/risk witness required the owner-visible meaning to be: Product Setup
  cannot be treated as ready because the site cannot safely tell which
  brand/product setup controls the public product.
- Technical witness recommended controller-level DB checks, not pure validation
  only, because the checks need Website Item metadata and existing target
  records.

## Verification

Passed:

```bash
python -m py_compile apps/locally_twisted/locally_twisted/product_blueprint_runtime_authority.py apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_product_blueprint/lt_product_blueprint.py scripts/verify/product_blueprint_contract.py
python scripts/verify/product_blueprint_contract.py
```

`product_blueprint_contract.py` result: 27 tests passed.

Capability gate: PASS.

Loaded resources:

- `capabilities/INDEX.md`
- `capabilities/failures/product-setup-projection-authority-drift.md`
- `capabilities/recipes/erpnext-product-blueprint-authoring.md`
- `capabilities/recipes/erpnext-catalog-variant-price-parity.md`
- `capabilities/recipes/erpnext-ecommerce-receiving-architecture.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/protective-contracts.md`

## Still Not Claimed

- No live Product Setup records were migrated or repaired.
- No public product route, cart, checkout, payment, document, media, or
  customer-message authority was proved or repaired.
- This does not add database-level unique indexes.
- This does not make Product Setup saves project to customer-facing price,
  copy, or media.
- This does not prove live/public brand lane.

## Next Safe Work

1. Start variant-axis classification/collapse planning with Birthday
   Deliveries as the first high-cardinality proof target.
2. Capture row-level rollback targets before any catalog mutation.
3. Design owner-visible publish/apply or direct runtime-authority workflow
   before repairing live product rows.
