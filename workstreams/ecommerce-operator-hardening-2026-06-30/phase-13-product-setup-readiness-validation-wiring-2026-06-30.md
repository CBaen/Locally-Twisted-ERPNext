# Phase 13 - Product Setup Readiness Validation Wiring

Date: 2026-06-30

Status: source-only validation wiring complete. No deploy, cache clear,
ERPNext/live mutation, provider/payment action, DNS change, customer message,
secret read, variant collapse, record disablement, record deletion, route
change, or product-scope approval occurred.

## Purpose

Phase 12 defined owner-visible readiness language as an offline report. Phase
13 wires the same contract into Product Setup validation JSON so Desk and future
UI work have a source-level state to read without implying that Save means live
publication.

## Source Changes

- `apps/locally_twisted/locally_twisted/product_blueprint_validation.py`
  - Adds `owner_publish_readiness` to validation output.
  - Adds `publish_apply_approval` with local/staging/live apply, mutation, cache
    clear, and deploy approvals all false.
  - Maps Product Setup states to owner-visible states:
    - `Draft`
    - `Needs Review`
    - `Local Proof Ready`
    - `Staging Ready`
    - `Blocked - Proof Needed`
  - Keeps `public_success_claim_allowed` and `publish_apply_allowed` false.
- `scripts/verify/product_blueprint_contract.py`
  - Adds contract tests proving Product Setup readiness states do not claim live
    success and live approval remains blocked.

## Verification

Capability gate: PASS.

Loaded resources:

- `capabilities/INDEX.md`
- `capabilities/failures/product-setup-projection-authority-drift.md`
- `capabilities/recipes/erpnext-product-blueprint-authoring.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/protective-contracts.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/phase-12-owner-visible-publish-readiness-birthday-deliveries-2026-06-30.md`

Checks:

```bash
python -m py_compile apps/locally_twisted/locally_twisted/product_blueprint_validation.py scripts/verify/product_blueprint_contract.py
python scripts/verify/product_blueprint_contract.py
```

Results:

- `py_compile`: pass.
- `product_blueprint_contract.py`: pass, 28 tests.

No runtime, browser, ERPNext, provider, payment, DNS, cache, deploy, or customer
checks were run because this slice is source-only.

## Remaining Safe Work

This phase adds validation JSON only. Future UI work should show the readiness
state and next owner step in Desk, but must still avoid adding live publish
buttons or any apply path until a release packet and owner approval exist.
