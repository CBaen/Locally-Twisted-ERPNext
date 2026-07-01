# Phase 12 - Owner-Visible Publish Readiness For Birthday Deliveries

Date: 2026-06-30

Status: source-only/offline owner-visible publish readiness report exists. This
is not a live publish path and not a live repair. No deploy, cache clear,
ERPNext/live mutation, provider/payment action, DNS change, customer message,
secret read, variant collapse, record disablement, record deletion, route
change, or product-scope approval occurred.

## Purpose

Phase 12 turns the Phase 11 no-write replacement model into a plain product
readiness state. The business problem is that a human can press Save and see a
success toast while the customer-facing site is unchanged. This report makes
that impossible to describe as success: if blockers remain, the product is
owner-visible `Blocked - Proof Needed`.

## Output

Tooling:

- `scripts/dev/lt_product_setup_publish_readiness_report.py`
- `scripts/verify/product_setup_publish_readiness_contract.py`

Saved Birthday Deliveries run:

```bash
python scripts/dev/lt_product_setup_publish_readiness_report.py --replacement /tmp/lt-birthday-deliveries-replacement-model-report.json --output /tmp/lt-birthday-deliveries-publish-readiness-report.json --pretty --fail-on-blocker
```

Result: expected exit `1`.

Readiness result:

- Owner state: `Blocked - Proof Needed`.
- Blocker count: `27`.
- Blocker groups:
  - `approval_and_release`
  - `brand_and_public_route`
  - `history_and_rollback`
  - `media_files`
  - `options_addons_payload`
  - `price_and_sku_model`
- Live apply approved: `False`.
- Mutation approved: `False`.
- Cache clear approved: `False`.
- Deploy approved: `False`.

The report includes owner-allowed actions:

- Save draft edits: allowed.
- Request technical review: allowed.
- Preview no-write packet: allowed.
- Publish/apply to live: blocked.

## State Contract

The report defines the source-only owner state machine language:

- `Draft`: safe to edit, nothing public promised.
- `Needs Review`: review requested, no public change promised.
- `Local Proof Ready`: local proof only, not live.
- `Staging Ready`: staging proof, not live.
- `Approved For Live`: controlled live apply packet may proceed later, not
  automatically live.
- `Live Applied`: live route, cart, documents, rollback, and cache proof passed
  after apply.

This is still report-level infrastructure. It does not change the actual
Product Setup UI or state machine yet.

## Verification

Capability gate: PASS.

Loaded resources:

- `capabilities/INDEX.md`
- `capabilities/failures/product-setup-projection-authority-drift.md`
- `capabilities/recipes/erpnext-catalog-variant-price-parity.md`
- `capabilities/recipes/erpnext-product-blueprint-authoring.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/protective-contracts.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/phase-11-no-write-replacement-model-birthday-deliveries-2026-06-30.md`

Checks:

```bash
python -m py_compile scripts/dev/lt_product_setup_publish_readiness_report.py scripts/verify/product_setup_publish_readiness_contract.py
python scripts/verify/product_setup_publish_readiness_contract.py
python scripts/dev/lt_product_setup_publish_readiness_report.py --replacement /tmp/lt-birthday-deliveries-replacement-model-report.json --output /tmp/lt-birthday-deliveries-publish-readiness-report.json --pretty --fail-on-blocker
```

Results:

- `py_compile`: pass.
- `product_setup_publish_readiness_contract.py`: pass, 3 tests.
- Saved Birthday Deliveries readiness report: expected exit `1`,
  `Blocked - Proof Needed`, 27 blockers.

No runtime, browser, ERPNext, provider, payment, DNS, cache, deploy, or customer
checks were run because this slice is source-only/offline.

## Next Safe Work

The next safe implementation slice is to wire this readiness contract into
Product Setup validation/UI without enabling live writes:

- add owner-visible blocker categories to Product Setup preview/status output;
- keep Save as draft success only, not live/public success;
- expose Request Review / Proof Needed language;
- block publish/apply controls until the no-write readiness packet passes and a
  separate release packet exists.
