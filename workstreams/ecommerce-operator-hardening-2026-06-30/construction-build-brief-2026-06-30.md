# Construction Build Brief - Protective Contracts

Date: 2026-06-30

Mode: construction-review

Decision needed: how to convert the triad critique into enforceable LT ecommerce planning contracts before code implementation.

Scope owner: Locally Twisted ecommerce operator hardening lane.

System/project/runtime classification: single project + client/production surface.

Allowed actions: repo documentation edits, non-mutating contract design, build brief, reviewer critique, local text verification.

Forbidden actions: live writes, product writes, provider changes, payment changes, customer-visible promises, deploys, secrets, data-loss operations, cache clears, service restarts.

Evidence bar: repo files, current workstream packet, capability docs, triad critique, and previously captured public-route evidence cited by the workstream. This slice does not refresh live proof.

Stop condition: stop before access, data-loss, money, production, legal/compliance, customer-promise, or live customer-facing risk.

## Goals

- Make the triad's protective requirements concrete enough to govern later implementation.
- Define owner workflow contracts before any Product Setup code or catalog migration work.
- Define safety contracts for price, media, add-ons, listing/cart eligibility, migration, rollback, brand lanes, and live proof.
- Preserve no-downtime posture and fail-loud behavior.

## Non-Goals

- Do not repair `large-head-missionary` in this slice.
- Do not mutate ERPNext records.
- Do not change payment, checkout, provider, DNS, Frappe Cloud, or cache behavior.
- Do not decide final product scope or retire/revive products.

## File Ownership

Primary write scope:

- `workstreams/ecommerce-operator-hardening-2026-06-30/README.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/hardening-milestones.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/significant-change-register.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/protective-contracts.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/construction-review-2026-06-30.md`

Read-only source context:

- `capabilities/INDEX.md`
- `capabilities/recipes/erpnext-ecommerce-receiving-architecture.md`
- `capabilities/recipes/erpnext-product-blueprint-authoring.md`
- `capabilities/recipes/erpnext-catalog-variant-price-parity.md`
- `capabilities/recipes/erpnext-webshop-guest-party-contract.md`
- `capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`
- `capabilities/recipes/three-brand-dba-boundary-contract.md`
- `capabilities/failures/ecommerce-variant-price-source-drift.md`
- `capabilities/failures/product-gallery-projection-regression.md`
- `capabilities/failures/product-primary-media-attachment-drift.md`

## Contracts And Interfaces

The slice must create or update contracts for:

- owner personas and permissions;
- Product Setup states and transitions;
- product authority matrix;
- price identity ledger;
- media role ledger;
- add-on classification;
- listing/cart eligibility invariant;
- active Product Setup uniqueness;
- non-destructive migration;
- pre-mutation release packet;
- document/payment proof modes;
- brand-lane resolution;
- live proof and rollback.

## Risk Areas

- Making the plan look safe without creating enforceable acceptance tests.
- Letting "Approved For Live" read as customer-visible success.
- Letting downstream payment or invoice parity prove the wrong source price.
- Allowing catalog migration language that implies deletion, disabling, or renaming is allowed before dry-run proof.
- Missing brand-lane resolution for route, payment, invoice, files, portal, and automation behavior.

## Verification Gates

- Capability gate passes for this repo and task.
- Restricted-term scan of the workstream returns no hits.
- New contracts are linked from the workstream README.
- Construction-review artifact records independent review and required fixes.
- No code, live data, provider, payment, or deployment changes occur.

## Anti-Overlap Rule

This slice owns planning contracts only. Later code work must open a new build brief with disjoint file ownership and a fresh capability gate.

## Escalation Trigger

Ask Guiding Light before any live mutation, product repair, catalog write, payment exposure, provider action, destructive migration, customer-message behavior, legal/customer-promise change, or decision that changes approved product scope.
