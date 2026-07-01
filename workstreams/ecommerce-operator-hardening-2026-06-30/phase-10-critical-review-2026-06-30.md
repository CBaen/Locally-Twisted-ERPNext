# Phase 10 Critical Review - Birthday Deliveries Dependency/Rollback Direction

Date: 2026-06-30

Status: critical review artifact only. No code edit, deploy, cache clear, live
ERPNext mutation, provider/payment/DNS/Frappe Cloud action, customer message,
secret read, or product-scope decision occurred.

## Scope

This review covers the intended Phase 10 direction after Phase 9:
dependency/rollback target capture for Birthday Deliveries before any no-write
replacement model or catalog mutation.

Allowed output for this pass:

- name what would make Phase 10 dangerously overclaim readiness;
- name minimum blockers that must remain blockers;
- set verification expectations for any dependency/rollback report.

This pass does not approve disabling, deleting, renaming, repurposing, merging,
or collapsing current Birthday Deliveries variants.

## Inputs Reviewed

- `workstreams/ecommerce-operator-hardening-2026-06-30/phase-9-variant-axis-classification-birthday-deliveries-2026-06-30.md`
- `CODING-HANDOFF.md`
- `locally-twisted-queue.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/phase-10-dependency-rollback-capture-birthday-deliveries-2026-06-30.md`
- `/tmp/lt-catalog-authority-full-20260630/044-birthday-deliveries.json`
- `/tmp/lt-birthday-deliveries-variant-axis-classification.json`
- `capabilities/failures/product-setup-projection-authority-drift.md`
- `capabilities/failures/product-primary-media-attachment-drift.md`
- `capabilities/failures/ecommerce-variant-price-source-drift.md`
- `capabilities/recipes/erpnext-product-blueprint-authoring.md`
- `capabilities/recipes/erpnext-ecommerce-receiving-architecture.md`

Capability gate: PASS.

Loaded resources:

- `capabilities/INDEX.md`
- `capabilities/failures/product-setup-projection-authority-drift.md`
- `capabilities/failures/product-primary-media-attachment-drift.md`
- `capabilities/failures/ecommerce-variant-price-source-drift.md`
- `capabilities/recipes/erpnext-product-blueprint-authoring.md`
- `capabilities/recipes/erpnext-ecommerce-receiving-architecture.md`

## Review Of Phase 10 Draft Direction

The Phase 10 dependency/rollback draft is acceptable only as a source-only
receipt/plan. It correctly says Birthday Deliveries remains blocked and that
no dependency capture has been accepted as proof yet.

The draft would become unsafe if a later closeout treats it as the actual
capture packet. It lists the right categories, but it does not yet provide
row-level captures, direct dependency queries, historical-reference results,
restore sequences, public route proof, add-on/runtime proof, or owner approval.

The minimum required interpretation is:

- Phase 10 draft direction: usable as a checklist.
- Phase 10 proof status: not started or not accepted.
- Mutation readiness: blocked.
- Replacement model readiness: blocked.
- Owner-facing claim: "Birthday Deliveries has a safer review path mapped,"
  not "Birthday Deliveries is ready to simplify."

## Current Verified Shape From Saved Artifacts

Birthday Deliveries remains blocked.

- Product: `birthday-deliveries`
- Website Item: `WEB-ITM-0047`
- Public route in saved artifact: `/shop-items/bouquets/birthday-deliveries`
- Brand lane: `null`, `not_proved`
- Product Setup status: `Local Preview Ready`
- Product Setup validation status: `Ready For Local Preview`
- Current variants: `2,430`
- Current Item Prices: `2,430`
- Product Setup price rows: `2,430`
- Unique saved price values: `9`
- Current Product Setup option axes: `4`
- Public GET in saved catalog artifact: skipped
- Saved readonly contract: no writes, no cache clear, no deploy, no payment provider action

Phase 9 candidate model:

- Candidate SKU axis: `Delivery Size`
- Candidate SKU count: `3`
- Configuration payload candidate: `Delivery themes`
- Paid add-on candidates: `Add Foil Number`, `Add Bouquet`

Critical price detail:

- `Delivery Size` affects saved exact price.
- `Add Bouquet` also affects saved exact price.
- `Delivery themes` and `Add Foil Number` did not affect saved exact price in
  Phase 9 evidence.
- Exact prices cannot be trusted after collapse until non-SKU price-affecting
  axes have add-on/runtime pricing proof and cart/order/document labels.

Media context:

- The current primary image repair is `/files/birthday-deliveries--extra-12.webp`
  on Website Item, Item, Product Blueprint, product page, and homepage evidence
  from the earlier live media repair lane.
- That media repair does not prove variant-collapse readiness, add-on media
  behavior, cart images, receipt images, or dependency rollback safety.

## Dangerous Phase 10 Overclaims

Phase 10 would dangerously overclaim readiness if it says or implies any of the
following:

- The `3` candidate SKU count is an approved replacement model.
- `Delivery Size` alone can carry pricing after collapse.
- `Add Bouquet` can move to an add-on path before add-on Items, prices,
  runtime expansion, cart labels, order labels, invoice labels, payment labels,
  and receipt labels are proven.
- `source_declared` or defaulted operating-brand data is live brand-lane proof.
- The saved artifact proves the public route, because public GET was skipped.
- Product Setup `Local Preview Ready` means live/public mutation readiness.
- The 2026-06-24 primary-image repair proves Phase 10 media dependencies.
- A list of current counts is a rollback plan.
- A rollback plan is complete without named records, field values, relationship
  edges, timestamps, and owner/source identity for every affected surface.
- Item Price parity proves source price truth.
- Stripe/checkout parity, if later present, proves source price truth by itself.
- Disabling variants is safer than deletion without proving historical
  references and public/cart behavior.
- A `/tmp` artifact is durable project evidence unless copied into a stable
  report location or regenerated with command evidence.
- Phase 10 can choose product scope or product business behavior without GL or
  approved source evidence.

## Minimum Blockers

Any Phase 10 dependency/rollback report must keep these blockers explicit until
resolved:

1. Brand lane is not live-proved for Birthday Deliveries in the saved artifact.
2. Public route proof is missing from the saved artifact.
3. No historical dependency map exists for the 2,430 current variant Item codes.
4. No rollback packet exists for current Item, Item Variant Attribute, Item
   Price, Product Setup price row, Website Item, slideshow/gallery, File, cart,
   order, invoice, payment, receipt, and customer-facing route surfaces.
5. `Add Bouquet` is price-affecting but has no approved add-on/runtime pricing
   implementation proof.
6. `Add Foil Number` is classified as a paid add-on candidate but has no
   add-on item, zero/nonzero price rule, cart identity, or document-label proof.
7. `Delivery themes` is classified as configuration payload but has no
   end-to-end payload preservation proof after SKU collapse.
8. Variant mapping in Phase 9 is inferred from Product Setup price-row
   `option_summary` text unless a later artifact includes direct Item Variant
   Attribute rows.
9. The Product Setup apply plan is already blocked by the 2,430-variant shape;
   Phase 10 must not route around that guard.
10. No owner approval exists for destructive or semi-destructive catalog
    actions.

## Required Dependency Coverage

A useful dependency report must identify every current Birthday Deliveries
record that could still be referenced after a collapse. At minimum:

- template Item `birthday-deliveries`;
- all 2,430 variant Items;
- all 2,430 Standard Selling Item Prices;
- Item Variant Attribute rows for the template and variants;
- Website Item `WEB-ITM-0047`;
- Product Setup `birthday-deliveries`;
- all Product Setup option and price rows;
- Website Slideshow/gallery rows and Product Setup gallery/media-rule rows;
- File rows and attachments for primary, gallery, Open Graph, runtime JSON, and
  homepage/card media;
- Website Item route and any redirect/canonical behavior;
- carts or Guest cart rows if present;
- Lead, Quotation, Sales Order, Sales Invoice, Payment Request, Payment Entry,
  Email Queue, Communication, and customer document rows that reference current
  variant Item codes;
- any local verifier, import manifest, source map, or report that keys by the
  current variant Item codes.

The report should distinguish "not found" from "not checked." Unchecked
surfaces are blockers.

## Required Rollback Coverage

A rollback packet must be field-level, not narrative-only. It must include:

- exact record identifiers;
- doctype and parent/child relationship;
- current values for every field proposed for change;
- current modified timestamp and modified_by;
- old and new route/image/price/copy values when applicable;
- whether the row is live/customer-facing, backend-only, or source-only;
- whether rollback can be done through source-owned patch/apply tooling or
  would require a controlled maintenance path;
- a restore sequence that does not weaken the owner catalog guard;
- a post-rollback verification list.

For variants, "rollback" must cover more than recreating count `2,430`. It
must prove the exact Item codes, attributes, prices, disabled state, and
references that existed before any change.

## Verification Expectations

Minimum acceptable Phase 10 report verification:

- The report runs in no-write mode by default.
- It exits nonzero while any blocker above remains unresolved.
- It names the exact saved artifact path or fresh live read-only command used.
- If it uses `/tmp` artifacts, it states that evidence is local and ephemeral.
- It proves direct Item Variant Attribute mapping instead of relying only on
  Product Setup `option_summary`, or it keeps the inference limitation as a
  blocker.
- It performs reference checks across catalog, cart, checkout, documents,
  payment records, communications, media, and public routes.
- It separates source authority, live runtime authority, public route proof,
  payment/document proof, and owner approval.
- It blocks mutation approval unless rollback targets are complete and
  verifiable.
- It includes a machine-readable JSON artifact and a human-readable summary.
- It is explicit that passing dependency capture is not the same as passing
  replacement model approval.

Expected blocker posture:

- A dependency/rollback report may pass collection quality.
- It must still block mutation readiness until brand lane proof, public route
  proof, add-on/runtime pricing proof, payload preservation proof, document
  labels, historical dependency safety, rollback restore proof, and owner
  approval exist.

## Phase 10 Go/No-Go Standard

Phase 10 is allowed to answer:

- "What would break if we collapse Birthday Deliveries variants?"
- "What exact records must be preserved or restorable?"
- "Which proofs are missing before a replacement model is safe?"

Phase 10 is not allowed to answer:

- "Birthday Deliveries is ready to collapse."
- "The 3-SKU model is approved."
- "The public shop is fixed."
- "Checkout/payment/document identity is safe."
- "Live mutation is ready."

Closeout classification for this artifact: review-only blocker standard.

## Follow-Up Implementation Review

After this review, Phase 10 implementation added
`scripts/dev/lt_product_setup_dependency_rollback_report.py` and
`scripts/verify/product_setup_dependency_rollback_contract.py`.

The implementation satisfies the minimum no-write direction for saved-artifact
rollback target capture because it:

- consumes saved catalog authority JSON only;
- defaults to Birthday Deliveries without reading live ERPNext;
- emits deterministic JSON;
- includes row-level saved-artifact rollback rows for the captured variants,
  Item Prices, Product Setup option rows, and media/gallery/pointer rows;
- keeps mutation, collapse, cache, deploy, and owner-scope approvals false;
- exits nonzero with `--fail-on-blocker` while blocker proof is missing.

It still must not be treated as mutation readiness. The tool does not prove
live public route state, live brand-lane authority, direct Item Variant
Attribute rows, order/invoice/payment/customer-message references, File
attachment rows, Website Slideshow child rows, add-on runtime pricing, cart
payload preservation, or owner approval.

Accepted closeout language: "Phase 10 captured saved-artifact rollback targets
and named blockers." Rejected closeout language: "Birthday Deliveries is ready
to simplify," "the 3-SKU model is approved," or "rollback is complete."
