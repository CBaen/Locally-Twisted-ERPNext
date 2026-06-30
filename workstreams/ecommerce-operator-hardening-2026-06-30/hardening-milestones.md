# Ecommerce Operator Hardening Milestones

Date: 2026-06-30

Status: project plan draft. This is intentionally larger than a patch.

Controlling contract: [protective-contracts.md](protective-contracts.md). Later implementation must load that file before code, migration, verifier, or release work in this lane.

## Goal

Make ecommerce owner-operable without weakening safety:

- Product Setup is the normal human product-management surface.
- Raw ERPNext product/page/price/gallery/settings tables stay protected.
- Every product change has a proof packet.
- Customer-facing product data is consistent across shop, product page, cart, checkout, documents, payment, and owner/operator views.
- Unsupported states fail loudly before customers see false success.
- `Approved For Live` is not live. Live requires target-site proof, cache proof where applicable, public route/API proof, owner Desk proof, cart proof where relevant, and rollback proof.

## Non-Goals

- Do not patch the one product by hand and call the system fixed.
- Do not let owner raw edits bypass the catalog guard.
- Do not expose checkout or payments unless the separate launch/payment gates pass.
- Do not import implementation ideas from prior ERP research; only architecture-neutral workflow lessons are allowed.
- Do not delete, rename, disable, collapse, repurpose, or overwrite existing catalog/history records until a catalog-wide dry-run proves dependencies, replacements, historical references, rollback, and owner approval where product scope changes.

## Cross-Phase Protective Contracts

These contracts apply to every phase:

- Owner/persona permissions must be explicit before an action can be exposed.
- Product Setup states must be real state transitions with actor, proof, public behavior, failure message, and rollback behavior.
- Product authority packets must resolve brand lane, route, Product Setup, Website Item, Item, price authority, media authority, add-ons/options, and rollback target before mutation.
- Runtime code must not rely on "newest active Product Setup by modified time"; one active Product Setup per target item, slug/route, and brand lane is a blocker.
- Price proof must follow the ordered price identity ledger from business intent through Product Setup, Item Price, public display, cart, checkout, Sales Order, payment payload where in scope, and invoice/receipt where in scope.
- Media proof must separate Product Setup primary image, Website Item image, Item image, File attachment, slideshow/gallery, selected-option media, shop card, metadata, cart, payment, receipt, and merchandising references.
- Every option/add-on must be classified as SKU-defining variant, configuration-only, color recipe/customization, measurement/upload, review-only quote context, paid checkout add-on, or unsupported.
- Any product that appears checkout-ready in `/shop` must also be cart-ready with enabled Item, checkout lane, sellable Item/variant, Standard Selling Item Price, Product Setup authority, public route proof, and cart API proof.
- Document/payment proof must name its mode: no-write payload proof, local test proof, staging proof, or live proof. Live payment/document behavior requires a separate payment/release approval.
- Every write path beyond no-write proof requires a pre-mutation release packet with environment, branch/hash, target products, row-level diff, backup/snapshot, rollback command, cache plan, verifiers, brand-lane proof, proof mode, no-downtime/customer-impact section, stop condition, and approvals.

## Phase 0 - Stabilize And Prove The Incident

Outcome: know exactly what live row was edited and why it did not affect public output.

2026-06-30 status: live read-only API proof is complete for
`large-head-missionary`. The owner save succeeded into Product Setup, but did
not project to live `Standard Selling` Item Price rows or Website Item public
copy fields. See
`live-readonly-api-audit-large-head-missionary-2026-06-30.md`.

Tasks:

- Authenticated live read-only audit for `large-head-missionary`.
- Compare Website Item, Item template, variant Items, Item Price rows, Product Setup rows, gallery/slideshow rows, and rendered public page.
- Capture modified timestamps and modified_by for the owner's save.
- Confirm whether issue is wrong field, wrong doctype, wrong price row, inactive Product Setup, duplicate Product Setup, stale seed copy, cache, or deployment drift.
- Do not clear cache in this read-only phase. If a later approved release/cache action clears cache, run public route proof after that action, but do not call cache the root cause unless DB rows prove it.

Exit criteria:

- One incident report names the exact saved field and the exact public resolver that ignored it.
- One product-specific repair path exists, but broad fixes are not skipped.
- No mutation occurs in this phase.

Exit status: met for incident proof, not for repair. Move next to no-write
preview and projection design; do not repair live rows from Phase 0 alone.

2026-06-30 continuation: no-write projection preview and parity tooling now
exist and fail on the known drift artifact as expected. See
`phase-2-projection-preview-parity-2026-06-30.md`.

## Phase 1 - Canonical Product Authority Map

Outcome: every product datum has one owner authority and named projections.

Tasks:

- Define authority for title, summary, story, details, category, route, visibility, primary image, gallery, variant image, base price, variant price, add-on price, option taxonomy, fulfillment policy, tax behavior, and brand lane.
- Decide which fields are owner-editable in Product Setup, which are system projections, and which are raw protected records.
- Add validation that rejects duplicate active Product Setup records per target item/slug/brand lane.
- Add validation that Product Setup active status cannot coexist with conflicting live Website Item copy/price/media without a projection plan.
- Add historical-reference capture for Sales Orders, invoices, payment records, customer communications, verifiers, and public links.
- Add brand-lane resolution for route, payment/document identity, files/media, portals, and automation behavior.

Exit criteria:

- Product Setup has a documented authority matrix.
- Owner cannot save a misleading active product setup when required public projections are missing.
- Authority packet exists before any migration or repair design.

Current blocker: the preview artifact explicitly records that brand-lane proof
and active Product Setup uniqueness are not yet proven by the saved audit input.

2026-06-30 catalog continuation: live read-only collection now has saved
artifacts for all 47 published Website Items. Every published Website Item
matched a Product Setup record, but every product still has at least one
blocker. Brand lane is unproved for all 47, and 19 matched Product Setups are
in Draft/inactive authority status. The next Phase 1 implementation slice is
therefore a catalog authority resolver/packet layer, not a live repair.

2026-06-30 Phase 5 source progress: Product Setup now requires
`operating_brand` and carries it through validation, dry-run apply-plan output,
and runtime Product Setup schema as `source_declared`. This reduces one source
ambiguity but does not prove live brand lane. Source validation also blocks
active same-brand Product Setup duplicates for the same slug, target Item, or
target Website Item, and runtime active lookup fails closed on duplicate
matches instead of selecting by modified time. Saved-artifact packet logic now
keeps `source_declared` and
same-brand source uniqueness separate from live proof through the
`source_authority` packet section and packet-aware parity verifier.

2026-06-30 Phase 7 source progress: runtime Product Setup lookup is now
brand-aware before cross-brand same-slug active setups are allowed. Product
schema/API/gallery resolution requires explicit or source-declared
`operating_brand`, checks target Item, target Website Item, and slug within
that brand, and fails closed on missing/invalid brand or active ambiguity. The
next Phase 1 build slice is owner-visible blocker reporting for these
conflicts.

## Phase 2 - Owner Product Setup UX

Outcome: owner sees a real business process, not technical fields.

Tasks:

- Review labels and field grouping for product name, sellable status, price, photos, options, add-ons, and live readiness.
- Add owner-visible blockers with plain next steps.
- Add preview that shows:
  - public route,
  - shop card data,
  - product page copy,
  - starting price,
  - exact variant/add-on price effects,
  - gallery/media changes,
  - cart/checkout eligibility,
  - document/payment impact.
- Add "request review" or equivalent transition instead of implying save equals public change.
- Add actor-based permissions for owner, trained employee, manager/approver, and developer/admin.
- Add an owner-readable state-transition table in the UI/workflow model.
- Add a blocked-products report showing product, route, state, blocker, last proof time, next step, and whether developer/admin help is required.
- Add canonical blocker categories and owner-facing message templates for common failures.
- Run owner acceptance scripts during this phase and again after later phases, not only at the end.

Exit criteria:

- Owner can understand whether a product is draft, blocked, ready for review, staged, or live.
- Product Setup does not imply public success until proof exists.
- Non-developer owner-profile test can understand every blocker without a developer command.

## Phase 3 - Price Identity Rebuild

Outcome: one price change updates every required sellable row or fails before save.

Tasks:

- Classify price types:
  - simple fixed product price,
  - variant exact price,
  - base price used only for generated variants,
  - add-on price,
  - fulfillment fee,
  - quote-only estimate,
  - unsupported dynamic rule.
- Build mutation plan from Product Setup to Item Price rows.
- Add diff preview for all affected Item Price rows.
- Add verifier for listing, product page, variant selector, cart, checkout, Sales Order, payment line items, invoice, and receipt.
- Add loud blocker when Product Setup price and live Item Price disagree for active products.
- Add ordered price identity ledger and require source/Product Setup price truth before downstream parity can count.
- Require Item Price proof to name `item_code`, variant/option key, Price List, currency, UOM if relevant, validity dates/scope, and source resolver or approval evidence.
- Split payment/document price proof into no-write payload proof, local test proof, staging proof, or live proof.

Exit criteria:

- Owner changing a price changes the public sellable price chain after approval.
- A product cannot be approved live with conflicting Product Setup and Item Price authority.
- Payment/invoice parity cannot be used to prove a price unless source authority passed first.

## Phase 4 - Copy And Media Projection

Outcome: description/photo edits project to every public surface.

Tasks:

- Make Product Setup public copy the source for Website Item LT custom fields.
- Add projection for short description, story, details, and content rules.
- Make primary image/gallery changes produce Website Item image, Website Slideshow rows, approved media rules, and cart/payment image proof.
- Add browser proof for desktop/mobile product page gallery and shop card.
- Add media role ledger for Product Setup primary image, Website Item image, Item image, File attachment, slideshow/gallery, metadata, shop card, product gallery, selected-option media, cart image, payment image, receipt image, and merchandising references.
- Preserve the media guard: simple checkout variant `Item.image` can be approved selected-option media only when Product Setup media rules accept it; complex/custom raw variant images remain held unless Product Setup approves the role.

Exit criteria:

- Owner copy/media edits have one preview and one projection path.
- Product page, shop card, cart, checkout, and payment images cannot silently diverge.
- Gallery proof alone is not accepted as primary-image or cart/payment/receipt image proof.

## Phase 5 - Option And Add-On Taxonomy

Outcome: each owner-entered option becomes either a sellable SKU selector, configuration field, review-only prompt, or add-on line.

Tasks:

- Define option categories:
  - SKU-defining variant attribute,
  - configuration-only selection,
  - color recipe/customization,
  - measurement/upload,
  - review-only quote context,
  - paid add-on.
- Add Product Setup validation for each category.
- Add add-on approval packets requiring enabled Item and Standard Selling Item Price.
- Add cart, checkout, Sales Order, invoice, and payment proof for paid add-ons.
- Add unsupported/add-on-visible blocker when an option appears in UI without runtime/document/payment behavior.

Exit criteria:

- Owner cannot create a visible option that lacks runtime/document/payment behavior.
- Unsupported add-ons stay quote/review-only with plain owner/customer messaging.

## Phase 6 - Existing Catalog Repair

Outcome: current live products are reconciled into the new owner authority model.

Tasks:

- Reconcile every published Website Item to Product Setup.
- Detect duplicate active Product Setup rows.
- Detect Product Setup price vs Item Price mismatches.
- Detect description authority mismatches.
- Detect media/gallery projection gaps.
- Detect products shown in `/shop` but rejected by cart.
- Detect quote-first products with checkout-looking UI.
- Produce repair reports first, then repair scripts with dry-run, diff, apply, and rollback notes after approval.
- Prohibit destructive cleanup until dependency map, replacement plan, historical-reference handling, route/cart behavior, rollback/restore method, and owner approval pass.

Exit criteria:

- Every published product has a clean authority packet or an explicit blocked status.
- Retired/unpublished products remain hidden unless explicitly reapproved.
- First catalog-wide output is a report, not a write.

## Phase 7 - Staging And Live Release Gates

Outcome: no product change reaches customers without proof.

Tasks:

- Add staging product-change packet:
  - source Product Setup,
  - generated raw record diffs,
  - verifier outputs,
  - browser screenshots,
  - cart/checkout proof where relevant,
  - document/payment proof where relevant.
- Add live product-change packet:
  - old live app hash and target app-mirror branch/commit for Frappe Cloud app releases,
  - old-live-to-target diff and dirty-overlap audit for release-scope files,
  - deploy pipeline status and site update result,
  - migrate result where schema/patch/data migration is involved,
  - exact Frappe Cloud/site update evidence,
  - cache clear evidence if applicable,
  - public route proof,
  - public API proof,
  - owner Desk proof,
  - rollback path.
- Add no-downtime/customer-impact section:
  - release containment,
  - fallback or pause posture,
  - expected customer impact,
  - proof content/product changes do not accidentally expose checkout/payment.
- Add minimum rollback contract:
  - pre-change row snapshot,
  - exact fields touched,
  - reversible patch, maintenance command, or documented manual procedure,
  - cache rollback plan,
  - public proof after rollback,
  - owner-visible status after rollback.
- Keep ecommerce pause/payment gates separate from product content gates.

Exit criteria:

- Product publish/change is a reviewed release artifact.
- A live public product change can be explained and reproduced without developer memory.
- If rollback cannot be defined, live mutation is blocked.

## Phase 8 - Owner Acceptance And Readiness

Outcome: the owner can run the workflow.

Tasks:

- Script test cases:
  - add a draft product,
  - change description,
  - change price,
  - add photo,
  - add option,
  - add add-on,
  - hide product,
  - attempt unsafe raw edit,
  - attempt unsupported conditional pricing.
- Run with non-developer operator account.
- Record where wording, permissions, or workflow blocks are confusing.
- Add owner-facing dashboard for red-alarm product blockers.
- Confirm owner/staff can distinguish Draft, Needs Review, Local Proof Ready, Staging Ready, Approved For Live, Live, Hidden, Retired, Quote Only, and Paused. Checkout readiness is proved by the listing/cart invariant, not a separate state.

Exit criteria:

- Owner can complete approved product maintenance without calling a developer.
- Unsupported work fails loudly with next steps.

## First Concrete Build Slice

Start with the smallest slice that proves the architecture:

1. One existing checkout product: `large-head-missionary`.
2. One description change.
3. One variant price change.
4. One primary image/gallery change.
5. One add-on proof only if already approved.

This slice must produce:

- Product Setup diff.
- Raw record diff.
- Public render diff.
- Cart/checkout proof.
- Sales Order/payment/invoice dry-run or controlled test proof.
- Owner-visible status and blocker output.

Only after this works should the repair broaden to all products.
