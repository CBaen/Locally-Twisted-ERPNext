# Plan-Deepen Notes - Owner-Operated Ecommerce Hardening

Date: 2026-06-30

Outcome: adjust.

The approach is directionally correct, but it must be tightened before implementation. The right plan is to build an LT ecommerce operating layer around Product Setup, with ERPNext as the accounting/catalog substrate and raw records as protected projections.

Update after triad critique: [protective-contracts.md](protective-contracts.md) is now the controlling contract for future implementation. Any later code or migration work must satisfy it or record a blocker.

## Route Record

```markdown
Mode: plan-deepen
Decision needed: whether the owner-operated ecommerce hardening approach is complete enough to implement
Scope owner: Locally Twisted ecommerce feature lane
System/project/runtime classification: single project + client/production surface + external research
Allowed actions: research, mapping, docs, dry-run plans, local-only proof
Forbidden actions: live writes, provider changes, payment changes, customer-visible promises, deploys, secrets, data-loss operations
Evidence bar: repo files, capability docs, current workstream packet, official external docs, public route proof where available
Stop condition: stop at access, data-loss, money, production, legal/compliance, or customer-promise risk
```

## Structure

Evidence checked:

- Current feature lane packet.
- Product Setup authoring and ecommerce receiving capability docs.
- Variant-price parity and media failure notes.
- Official docs for Saleor, Medusa, Vendure, Spree, and BigCommerce ecommerce modeling patterns.

Risks found:

- The current ask is broad enough to become a rewrite without containment.
- Existing 10k+ variants are both data debt and possible current runtime dependency.
- "Immediate live" can mean unsafe raw save unless it is defined as validated projection plus proof.

Plan adjustment:

- Use the Significant Change Register as the controlling backlog.
- Build one proof product first before catalog-wide migration.
- Treat "save live immediately" as a product state transition with validation, projection, cache clear, and public proof.
- Treat `Approved For Live` as not live until target-site proof, cache proof where applicable, public route/API proof, owner Desk proof, and rollback proof are attached.

Open question or escalation:

- Need authenticated prior-backend access and complete external-drive research path before using that system as detailed workflow evidence.

## Data Model

Evidence checked:

- Product Setup distinguishes SKU-defining selections, configuration-only groups, add-ons, measurements/uploads, and review-only payloads.
- Current ERPNext sellable path still uses Item Variants and Item Prices.
- External systems converge on variants as purchasable units, not every decoration/configuration choice.

Risks found:

- Migrating existing products too early could break prices, cart, quote workflows, media, or historical orders.
- Some current variants may encode real sellable prices that must not be lost.

Plan adjustment:

- Classify every option axis before changing data:
  - SKU-defining variant,
  - configuration-only,
  - color recipe,
  - paid add-on,
  - measurement/upload,
  - quote context,
  - unsupported/drop.
- Produce dry-run migration packets before any data mutation.
- Preserve historical order/invoice references; do not delete live records casually.
- Enforce one active Product Setup per target item, slug/route, and brand lane before runtime reliance on Product Setup.
- Make the first catalog-wide output a non-mutating report, not a write.

Open question or escalation:

- Which existing published products are safest for the first SKU-only migration proof after `large-head-missionary` incident audit?

## Integration

Evidence checked:

- Product page, shop, cart, checkout, Sales Order, payment, and invoice each resolve product data through separate paths.
- Existing local apply does not publish/hide/reroute public Website Items.
- Payment and checkout paths must remain separately gated.

Risks found:

- Fixing only Product Setup will not fix live ecommerce unless projection reaches every public/runtime surface.
- Fixing only public product pages will not fix cart, checkout, Sales Order, payment, and invoice meaning.

Plan adjustment:

- Define projection targets per product datum:
  - title/copy,
  - route/category,
  - visibility/lane,
  - price,
  - main image,
  - gallery,
  - selected-option media,
  - add-ons,
  - configuration payload,
  - document/payment labels.
- Require proof across all affected targets before a product can show `Live`.
- Require `/shop` listing eligibility and cart eligibility to match for every checkout-looking product.
- Require price identity and media role ledgers before downstream cart/payment/document parity can count.

Open question or escalation:

- Any live publish mechanism requires a separate release gate and explicit approval.

## Owner UX

Evidence checked:

- Owner path exists but is incomplete for live public release.
- External ecommerce systems emphasize searchable variants, bulk price/media editing, product statuses, and owner-friendly product creation.

Risks found:

- A technically correct schema can still fail if Jeff or an employee cannot operate it.
- Raw ERPNext forms may remain tempting unless Product Setup clearly explains blocked states and next steps.

Plan adjustment:

- Product Setup must become business-language UI, not a technical schema editor.
- Product Setup states must name actor, proof, public behavior, failure message, and rollback behavior.
- Add an owner-visible readiness dashboard:
  - live status,
  - price blockers,
  - media blockers,
  - add-on blockers,
  - route/shop/cart/checkout proof,
  - last successful public projection.
- Owner acceptance tests become required exit criteria.
- Owner acceptance starts in the Product Setup UX/state phase and repeats after later phases.

Open question or escalation:

- Need at least one owner/staff workflow session before final UI polish claims.

## Safety / Release

Evidence checked:

- Launch gate requires Frappe Cloud/site update proof and public route proof.
- Payment/checkout exposure has its own paused-state and provider gates.
- User hard constraint: public site cannot go down.

Risks found:

- A broad catalog migration can break public product routes or checkout.
- Cache clears and route changes can be production-affecting.
- Payment/provider changes are out of scope for normal product workflow hardening.

Plan adjustment:

- Use no-downtime strategy:
  - docs and local proof first,
  - read-only live audit,
  - dry-run migration packet,
  - staging proof,
  - one-product live proof only after approval,
  - then product-family rollout.
- Keep ecommerce/payment exposure gates separate from product-management gates.
- Require a pre-mutation release packet before any write beyond no-write proof.
- Split document/payment proof into no-write payload proof, local test proof, staging proof, and live proof. Live payment/document behavior requires separate approval.
- Block live mutation if rollback cannot be defined and publicly re-proved.

Open question or escalation:

- Stop before any live mutation, payment, deploy, DNS, provider, or customer communication action.

## Research

Evidence checked:

- Local prior-research roots exist but complete external-drive source tree is not yet mapped.
- Official external docs support the same key split: true variants, non-SKU configuration/modifiers, product/variant media, explicit publishing status, channel/price contracts.

Risks found:

- Research can become generic if not converted into LT acceptance tests.
- Restricted platform naming must not leak into docs, branches, paths, comments, or normal conversation.

Plan adjustment:

- Every research lesson must become one of:
  - Significant Change Register entry,
  - Product Setup UX requirement,
  - migration rule,
  - verifier,
  - owner acceptance test.
- Use source links for non-restricted systems; store restricted-source evidence as sanitized local pointers only.

Open question or escalation:

- Need exact external-drive mount/path or user-guided access for the prior backend docs.

## Adjusted Implementation Order

1. Incident proof: authenticated read-only audit of `large-head-missionary` and exact edited row/field.
2. Non-mutating authority matrix: define source/projection for title, description, price, media, options, add-ons, visibility, route, lane, and rollback target.
3. Owner workflow contract: personas, permissions, state transitions, blockers, preview, dashboard/report, and owner acceptance scripts.
4. Identity contracts: price identity ledger, media role ledger, add-on classification, listing/cart eligibility invariant, and Product Setup uniqueness.
5. Pre-mutation release packet and rollback contract: environment, target products/routes, row-level diff, snapshot, rollback, cache plan, verifier list, brand-lane proof, proof mode, stop condition, and approvals.
6. One-product no-write/local proof: copy, price, primary image, selected media, and cart eligibility for the incident product where safe.
7. Variant taxonomy proof: model one high-cardinality product with SKU-only variants plus structured configuration.
8. Catalog-wide dry-run: classify all products and produce non-mutating repair packets.
9. Staging proof: route/shop/product/cart/checkout/document proof for selected families under staging release rules.
10. Live rollout: one product/family at a time through release gate; no payment exposure unless separately approved.

## Bottom Line

Proceed with lane research, mapping, dry-run planning, and local proof. Adjust before implementation by making Product Setup the controlling owner surface, defining immediate live projection as verified state transition, and treating existing variant explosion as migration debt with staged repair. Escalate before any live mutation, data-loss, money, legal/compliance, or customer-visible action.
