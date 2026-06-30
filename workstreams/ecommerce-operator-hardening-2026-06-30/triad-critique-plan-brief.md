# Ecommerce Operator Hardening Triad Critique Plan Brief

Date: 2026-06-30

## Outcome

Critique the tightened LT ecommerce owner-operated hardening plan before implementation. The critique should improve the plan, identify gaps, call out unsafe assumptions, and recommend adjustments that make the work implementable without production downtime or customer-facing false success.

The plan being critiqued is not a code patch. It is the feature-lane strategy that says:

- Product Setup becomes the owner operating surface.
- ERPNext remains the accounting/catalog substrate.
- Raw ERPNext records become protected projections.
- Existing excessive variant shape is migration debt.
- Future model uses SKU-defining variants plus structured configuration.
- Live product changes require validated projection and public proof.

## Current Verified State

Primary lane docs:

- `workstreams/ecommerce-operator-hardening-2026-06-30/README.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/lane-charter.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/operating-brief.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/plan-deepen-notes.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/significant-change-register.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/research-map.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/owner-workflow-map.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/public-runtime-flow-map.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/broken-connections-register.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/hardening-milestones.md`

Local source/capability evidence:

- Product Setup / Product Blueprint is the intended owner product-authoring surface.
- Owner-like direct edits to raw `Item`, `Website Item`, `Item Price`, option/category/gallery/settings records are guarded because they can desync public ecommerce behavior.
- Local Product Setup apply can create/update local records but does not publish/hide/reroute existing public Website Items.
- Product pages, shop cards, cart, checkout, Sales Orders, payment lines, invoices, and receipts each resolve product data through separate paths.
- Server-side Item Price is checkout authority, but source-price correctness still needs proof.
- Product media is multi-authority: Website Item image, Item image, Product Setup primary image/media rules, File attachments, Website Slideshow, variant media, shop card, cart/payment/receipt images.
- Current docs indicate the excessive variant shape is a historical/scaffold artifact and not the desired future model.

Capability gate for this briefing pass: PASS.

Loaded resources:

- `capabilities/INDEX.md`
- `capabilities/recipes/erpnext-ecommerce-receiving-architecture.md`
- `capabilities/recipes/erpnext-product-blueprint-authoring.md`
- `capabilities/recipes/erpnext-catalog-variant-price-parity.md`
- `capabilities/recipes/erpnext-webshop-guest-party-contract.md`
- `capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`
- `capabilities/failures/ecommerce-variant-price-source-drift.md`
- `capabilities/failures/product-gallery-projection-regression.md`
- `capabilities/failures/product-primary-media-attachment-drift.md`

## Scope And Ownership

Scope owner: Locally Twisted ecommerce feature lane.

System/project/runtime classification:

- single project;
- client/production surface;
- external research;
- no live mutation in this critique.

In scope for critique:

- product creation and maintenance workflow;
- owner-facing Product Setup;
- SKU-defining variants vs configuration-only selections;
- price projection and proof;
- media/main image/gallery/selected variant image behavior;
- add-ons and modifiers;
- public projection to shop/product/cart/checkout/doc/payment surfaces;
- migration from excessive variants;
- verifiers, release gates, and owner acceptance tests;
- research translation from prior ERP and open-source ecommerce systems.

Out of scope for critique:

- implementing code;
- live product writes;
- provider/dashboard changes;
- deploys;
- payment exposure;
- DNS/Frappe Cloud actions;
- secrets, auth files, session state, or raw customer data.

## Constraints And Hard Stops

Hard constraints:

- The public site cannot go down.
- Do not use the restricted platform name in docs, paths, branches, comments, or normal conversation.
- Treat prior ERP research as architecture evidence only. Do not copy implementation, code, names, paths, or platform-specific vocabulary into LT.
- No customer-visible success without downstream proof.
- Raw ERPNext table editing should not become the normal owner path.

Stop before recommending:

- live production mutation;
- data-loss or destructive migration;
- payment/money changes;
- legal/compliance/customer-promise decisions;
- customer-facing launch/checkout exposure;
- external account writes;
- work that requires unavailable credentials or secrets.

## Implementation Shape To Critique

Adjusted implementation order:

1. Incident proof: authenticated read-only audit of `large-head-missionary` and exact edited row/field.
2. Product authority matrix: define source/projection for title, description, price, media, options, add-ons, visibility, route, and lane.
3. Product Setup UX/state model: owner-ready statuses, blockers, preview, publish/apply semantics.
4. One-product proof: price + copy + main image + selected media projection across public page/shop/cart/checkout/document/payment dry-run.
5. Variant taxonomy proof: model one high-cardinality product with SKU-only variants plus structured configuration.
6. Catalog-wide dry-run: classify all products and produce repair packets with no writes.
7. Staging proof: route/shop/product/cart/checkout/document proof for selected families.
8. Live rollout: one product/family at a time through release gate; no payment exposure unless separately approved.

Default decisions:

- Future target is SKU-only variants plus structured configuration.
- Product Setup is owner source of truth.
- Raw ERPNext catalog edits remain guarded.
- Immediate live change means validated projection plus public proof.
- Existing excessive variant shape is migration debt.

## Interfaces Or Artifacts

Artifacts the final plan should produce or update:

- product authority matrix;
- variant/option taxonomy;
- owner Product Setup UX/state spec;
- price identity spec;
- media projection spec;
- add-on/modifier spec;
- public projection verifier list;
- one-product proof packet;
- catalog-wide dry-run repair packet;
- owner acceptance test script.

Existing workstream docs are in:

- `workstreams/ecommerce-operator-hardening-2026-06-30/`

## Verification And Acceptance

The triad critique is accepted when it produces:

- a clearly labeled real multi-agent triad result;
- lens-specific findings with file/evidence references;
- convergence and dissent;
- required plan changes before implementation;
- risks that must become hard stops;
- suggested first proof slice;
- missing research or access gaps;
- a concise recommendation: proceed, adjust, or escalate.

Implementation acceptance for the later build is not part of this critique, but the critique should check whether these later acceptance tests are sufficient:

- owner can change product price and public price reflects after validated projection;
- owner can change description and public product page reflects the approved public copy;
- owner can set main image and selected-option/variant image;
- owner can create a product through Product Setup without raw Website Item permissions;
- SKU-only variant model preserves configuration in cart, checkout, Sales Order, invoice, and receipt;
- unsupported add-ons/options fail loudly and route to quote/review;
- no product reaches Live state without public route proof.

## Open Questions Or Assumptions

Assumptions:

- Existing docs are claims until checked against repo, DB, and public route behavior.
- The first proof product should include `large-head-missionary` because it triggered the incident, but another high-cardinality product may be safer for the variant-taxonomy proof.
- Complete prior ERP external-drive docs are not yet mapped on this machine.
- Payment exposure remains out of scope unless a separate payment/launch gate reopens it.

Open questions for reviewers:

- Is the adjusted implementation order correct, or should the authority matrix precede the incident proof?
- Where does the plan still hide developer-only work behind owner-friendly language?
- What migration/data-loss risks are understated?
- What verifier or acceptance gap would let another false-success incident slip through?
- What is the smallest safe proof slice that meaningfully tests the whole architecture?

## Next Safe Step

Run three independent critique lenses:

1. Owner/business workflow lens: can an employee truly run this?
2. Technical/data architecture lens: will the model avoid variant explosion while preserving price/media/order meaning?
3. Adversarial release/safety lens: what could break the live site, payments, data, or customer trust?

Then synthesize convergence, dissent, and plan adjustments into a saved triad critique artifact in this same workstream folder.
