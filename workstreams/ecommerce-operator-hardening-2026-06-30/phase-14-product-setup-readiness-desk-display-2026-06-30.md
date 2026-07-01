# Phase 14 - Product Setup Readiness Desk Display

Date: 2026-06-30

Status: source-only Desk display wiring complete. No deploy, cache clear,
ERPNext/live mutation, provider/payment action, DNS change, customer message,
secret read, variant collapse, record disablement, record deletion, route
change, or product-scope approval occurred.

## Purpose

Phase 13 put owner readiness state into validation JSON. Phase 14 gives Desk a
read-only `Show Readiness` button that displays that state, the next owner step,
whether public success is allowed, whether live publish/apply is allowed, and up
to ten blockers.

This makes the backend clearer without creating a publish button.

## Source Changes

- `apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_product_blueprint/lt_product_blueprint.js`
  - Adds `Show Readiness` under `Product Setup`.
  - Reads `validation_json.owner_publish_readiness`.
  - Shows blocked/readiness state and next step.
  - Falls back to `Blocked - Proof Needed` if validation JSON cannot be parsed.
  - Does not call any write, publish, live, cache, deploy, provider, or customer
    method.
- `scripts/verify/product_blueprint_contract.py`
  - Adds static proof that the Desk client includes `Show Readiness`, reads
    readiness state, and does not leak the local apply confirmation token.

## Verification

Capability gate: PASS.

Loaded resources:

- `capabilities/INDEX.md`
- `capabilities/failures/product-setup-projection-authority-drift.md`
- `capabilities/recipes/erpnext-product-blueprint-authoring.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/protective-contracts.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/phase-13-product-setup-readiness-validation-wiring-2026-06-30.md`

Checks:

```bash
python -m py_compile scripts/verify/product_blueprint_contract.py
python scripts/verify/product_blueprint_contract.py
```

Results:

- `py_compile`: pass.
- `product_blueprint_contract.py`: pass, 28 tests.

No runtime, browser, ERPNext, provider, payment, DNS, cache, deploy, or customer
checks were run because this slice is source-only.

## Remaining Safe Work

This button displays saved validation state only. Future work can make the
readiness panel richer, but it must not add live publish/apply controls until a
release packet and owner approval exist.
