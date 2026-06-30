# Triad Critique - Ecommerce Operator Hardening Plan

Date: 2026-06-30

Review type: real multi-agent triad synthesis.

Status: plan critique complete. This is not implementation approval, not a live fix, not a product write, and not a release approval.

## Decision

Adjust before implementation.

The tightened plan is directionally right: Product Setup should become the owner operating surface, ERPNext records should become protected projections, SKU-defining axes should remain true variants, and high-cardinality choices should move into structured configuration where they do not need separate product records.

The triad does not recommend proceeding straight to build yet. The plan needs stricter owner workflow, migration, rollback, brand-lane, price/media identity, and public proof contracts before implementation starts.

## Evidence Used

The triad was briefed with:

- [triad-critique-plan-brief.md](triad-critique-plan-brief.md)
- [README.md](README.md)
- [lane-charter.md](lane-charter.md)
- [operating-brief.md](operating-brief.md)
- [plan-deepen-notes.md](plan-deepen-notes.md)
- [significant-change-register.md](significant-change-register.md)
- [research-map.md](research-map.md)
- [owner-workflow-map.md](owner-workflow-map.md)
- [public-runtime-flow-map.md](public-runtime-flow-map.md)
- [broken-connections-register.md](broken-connections-register.md)
- [hardening-milestones.md](hardening-milestones.md)

Local source and capability evidence sampled by reviewers included Product Setup schema/runtime/apply logic, shop listing, cart, checkout, Stripe session construction, payment success reconciliation, pricing/media failure notes, guest checkout contract, launch gate, and brand-boundary contract.

No reviewer edited files, started services, read secrets, ran logged-in live verifiers, or mutated data.

## Lane Findings

### Reviewer 1: Owner and Business Workflow Lens

The owner outcome is correct, but Product Setup still reads too much like a technical control panel. The plan must define who can change what, which state transitions exist, what proof is required for each transition, and what the owner sees when a change is blocked.

Required changes from this lens:

- Add owner personas and permissions: owner, trained employee, manager/approver, developer/admin.
- Replace vague status language with a transition table: state, actor, proof required, public behavior, failure message, and rollback behavior.
- Make Product Setup a guided business workflow, not just a DocType with technical fields.
- Define proof by change type: copy, price, media, option, add-on, visibility, and route.
- Move owner acceptance tests into the Product Setup design phase and repeat them per phase.
- Add an owner dashboard/report showing blocked products, reason, affected URL, required decision, last proof time, and whether developer help is required.

### Reviewer 2: Technical and Data Architecture Lens

The SKU-only variant plus structured configuration architecture is technically sound for LT, and the current runtime already has many primitives needed to preserve selected configuration into cart, Sales Order, payment labels/images, invoices, and receipts.

The plan still needs stricter migration semantics and source-of-truth contracts.

Required changes from this lens:

- Add a non-mutating authority matrix before migration design, while still using the incident product for evidence.
- Add a no-destructive-migration invariant: no variant, Item Price, Website Item, Item, Sales Order reference, invoice, or payment-linked record is deleted, renamed, disabled, or collapsed until dry-run proof says it is safe.
- Enforce one active Product Setup per target item, slug, and brand lane before runtime reliance on Product Setup.
- Add a price identity ledger: source intent to Product Setup price rule to exact Item Price rows to public display to cart to Sales Order to payment to invoice/receipt.
- Add a media role spec separating primary image, gallery, selected-option media, cart/payment/receipt image, and merchandising references.
- Add a listing/cart eligibility invariant: any checkout-looking product shown in `/shop` must resolve through cart with enabled Item, checkout lane, and Standard Selling Item Price.
- Split the first proof if needed: incident product for authority proof, high-cardinality product for variant/configuration proof.

### Reviewer 3: Adversarial Release and Safety Lens

The plan has the right safety posture but under-defines rollback, production proof, payment isolation, brand-lane proof, and listing/cart parity.

Required changes from this lens:

- Add a pre-mutation release packet before any local apply beyond rollback-safe proof, staging write, or live write. It must include environment, branch/hash, target products, row-level diff, backup/snapshot, rollback command, cache plan, verifiers, and stop condition.
- Make the first proof slice fail unless `/shop` listing eligibility and cart eligibility match.
- Split payment/document dry-runs into pure no-write payload proof, local test proof, staging proof, and live proof. No real payment session, customer email, Payment Request, submitted invoice, or receipt send belongs in this lane without separate payment approval.
- Require brand-lane resolution in the product authority matrix and proof packet.
- Treat "Approved For Live" as not live. Live requires target-site update evidence, cache evidence where applicable, public route/API proof, owner Desk proof, and rollback proof.

## Convergence

All three reviewers agree:

- Product Setup as owner authority is the right direction, but it must become an owner workflow with clear states and proof, not a developer-only record editor.
- Variant reduction is essential, but destructive cleanup is unsafe until a catalog-wide dry-run maps current records, dependencies, replacements, and rollback.
- Price changes must be traced from source intent through every downstream surface. Downstream parity alone can preserve the wrong source value.
- Media must be treated as multiple roles, not one generic image field.
- `/shop` listing eligibility and cart eligibility must match. A product that looks buyable but cannot enter cart is a fail-loud violation.
- Live publishing requires environment-specific proof and rollback proof. Source push, app mirror update, and "approved" state are not live proof.
- Payment and customer-message behavior must stay isolated unless the payment/release gate is separately reopened and passed.

## Dissent or Tension

There is no material disagreement on direction.

The main tension is sequencing:

- The incident product should still be audited first because it is the concrete failure that triggered the lane.
- The authority matrix must follow immediately and become the control surface for what any later repair is allowed to touch.
- Variant/configuration proof may need a different product than the incident product if the incident product is not the safest high-cardinality test case.

## Required Plan Changes Before Build

1. Add an owner persona and permission model.
2. Add a Product Setup state-transition table with actor, proof, public behavior, failure message, and rollback behavior.
3. Add an owner-facing blocked-products dashboard/report requirement.
4. Add a non-mutating authority matrix before migration design.
5. Add a no-delete/no-rename/no-disable migration invariant for catalog and historical records until dry-run and rollback proof pass.
6. Add active Product Setup uniqueness as a blocker.
7. Add price identity ledger requirements across source, Product Setup, Item Price, public display, cart, Sales Order, payment, invoice, and receipt.
8. Add media role identity requirements across Website Item, Item, Product Setup, File, slideshow/gallery, HTML metadata, shop card, cart, payment, and receipt.
9. Add add-on classification: paid checkout add-on, configuration-only choice, quote/review context, or unsupported.
10. Add `/shop` listing and cart eligibility as one invariant.
11. Add a pre-mutation release packet for any write path.
12. Split document/payment proof into no-write, local test, staging, and live modes.
13. Add brand-lane resolution to every product authority/proof packet.
14. Treat "Approved For Live" as not live until target-site, cache, public route/API, owner Desk, and rollback proof are attached.

## Revised Safe Sequence

1. Read-only incident proof for `large-head-missionary`.
2. Non-mutating product authority matrix.
3. Owner persona, permission, and state-transition design.
4. Product Setup guided workflow design.
5. Price identity, media role, add-on classification, and listing/cart invariants.
6. Pre-mutation release packet template and rollback contract.
7. One-product no-write/local proof for copy, price, primary image, selected media, and cart eligibility.
8. High-cardinality variant/configuration proof, using the safest representative product.
9. Catalog-wide dry-run with no destructive writes.
10. Staging proof.
11. Live rollout one product or one product family at a time, only through the release gate.

## Hard Stops

Stop before:

- production mutation;
- product writes on live;
- payment exposure;
- customer email/message/receipt sending;
- destructive catalog cleanup;
- legal or customer-promise change;
- brand-lane ambiguity;
- any change that cannot be rolled back and publicly re-proved.

## Capability Gate

Capability gate: PASS.

Loaded resources for the parent planning/editing session:

- `capabilities/INDEX.md`
- `capabilities/recipes/erpnext-ecommerce-receiving-architecture.md`
- `capabilities/recipes/erpnext-product-blueprint-authoring.md`
- `capabilities/recipes/erpnext-catalog-variant-price-parity.md`
- `capabilities/recipes/erpnext-webshop-guest-party-contract.md`
- `capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`
- `capabilities/failures/ecommerce-variant-price-source-drift.md`
- `capabilities/failures/product-gallery-projection-regression.md`
- `capabilities/failures/product-primary-media-attachment-drift.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/README.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/operating-brief.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/plan-deepen-notes.md`

## Next Safe Action

Patch the plan documents to include the required changes above, then run a focused plan-deepen pass on the revised build sequence before any implementation.
