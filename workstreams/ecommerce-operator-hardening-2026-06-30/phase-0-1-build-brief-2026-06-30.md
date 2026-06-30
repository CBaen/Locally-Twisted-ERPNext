# Phase 0/1 Product Authority Build Brief

Date: 2026-06-30

Status: implementation-ready build brief for a non-mutating Phase 0/1 slice. This is not code approval, not data repair approval, not cache approval, not deployment approval, and not payment/provider approval.

Capability gate: PASS in the parent task for this exact slice.

Loaded context:

- `workstreams/ecommerce-operator-hardening-2026-06-30/protective-contracts.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/hardening-milestones.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/construction-review-2026-06-30.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/README.md`

## Route Record

Mode: Phase 0/1 implementation brief.
Decision needed: prove the `large-head-missionary` incident path and define the non-mutating product authority packet shape before any repair work.
Scope owner: Locally Twisted ecommerce operator-hardening lane.
System/project/runtime classification: single project plus authenticated read-only client/runtime surface.
Allowed actions: repo reads, authenticated read-only ERPNext inspection, public route reads, no-write scripts/verifiers, and documentation artifacts.
Forbidden actions: deploys, cache clears, ERPNext record writes, product repair, migrations, provider/payment/DNS/Frappe Cloud changes, secret reads, customer messages, and destructive cleanup.
Evidence bar: direct repo proof, authenticated read-only row proof, public route proof, and explicit uncertainty labels where access is missing.
Stop condition: stop before mutation, repair, cache action, release action, or any claim that cannot be proved with read-only evidence.
Lane owner: Phase 0/1 implementation agents.
Artifact path: this workstream directory, with exact output files assigned before work begins.
Coordination path: the active ecommerce operator-hardening workstream files.
File/system ownership: docs and no-write audit artifacts only; ERPNext data is read-only.
Dependencies: authenticated read-only access if row-level `modified`, `modified_by`, Product Setup, Website Item, Item, Item Price, and gallery/slideshow proof is required.
Anti-overlap rule: one agent owns one output artifact at a time; no agent edits another worker's file or broadens into code/data changes.
Escalation trigger: missing credentials/access, conflicting product authority evidence, duplicate active authority, payment/provider evidence required, or any proposed mutation.

## Outcome

Phase 0 must produce a read-only incident audit for `large-head-missionary` that names the exact saved backend field, the exact public resolver or downstream row that ignored it, and the likely cause category without changing data.

Phase 1 must produce a non-mutating product authority matrix packet that defines which source owns each product datum and which surfaces are projections, starting with `large-head-missionary` and reusable as a template for later catalog-wide dry-run work.

## Goals

- Prove the incident path for `large-head-missionary` from owner save evidence to public output.
- Compare Website Item, Item template, variant Items, Item Price rows, Product Setup rows, gallery/slideshow rows, and rendered public page.
- Capture `modified`, `modified_by`, status, route, price, copy, image, gallery, and active-authority evidence.
- Classify the cause as wrong field, wrong doctype, wrong price row, inactive Product Setup, duplicate Product Setup, stale seed copy, cache evidence gap, deployment drift, or unresolved.
- Draft a product authority matrix packet covering brand lane, route, Product Setup, Website Item, Item, price, media, options/add-ons, historical references, rollback target, and proof gaps.
- Make every blocker owner-readable and developer-actionable.

## Non-Goals

- Do not repair `large-head-missionary`.
- Do not clear cache or use cache clearing as proof.
- Do not mutate local, staging, or live ERPNext data.
- Do not change code, fixtures, hooks, seed data, migrations, scripts, provider settings, DNS, or Frappe Cloud settings.
- Do not expose checkout, payment, document sending, or customer-message paths.
- Do not decide catalog-wide product scope or retire/revive any product.

## Current Verified State

The accepted planning contracts require Phase 0 to be read-only and require Phase 1 to create an authority packet before migration or repair design. The workstream README records public-route evidence for `large-head-missionary`: public output can show Product Setup/base-price data that differs from sellable variant pricing, proving split authority but not complete row-level cause.

Authenticated live/database row proof has not been performed in this slice. Treat all row-level cause theories as unproved until the read-only audit captures row evidence.

## File And System Ownership

Implementation agents may read:

- this workstream directory;
- relevant LT source files listed in the README primary evidence section;
- public route output for `https://locallytwisted.com/shop-items/bouquets/large-head-missionary`;
- authenticated ERPNext rows through read-only Desk/report/API access when credentials are provided through approved channels.

Implementation agents may write only assigned Phase 0/1 documentation or no-write verifier output files in this workstream directory. Recommended outputs are:

- `phase-0-incident-audit-large-head-missionary-2026-06-30.md`
- `phase-1-product-authority-matrix-template-2026-06-30.md`
- `phase-1-large-head-missionary-authority-packet-2026-06-30.md`

No implementation agent owns ERPNext data, cache, deployment state, provider settings, customer messages, or release paths in this slice.

## Contracts And Interfaces

Use `protective-contracts.md` as controlling law. The Phase 0/1 packet must satisfy these interfaces:

- Product Authority Matrix: resolve brand lane, public route, Website Item, Item template, sellable Item/variant rows, active Product Setup, copy, category, visibility, fulfillment lane, quote/checkout lane, media roles, price roles, options/add-ons, historical references, and rollback target.
- Active Product Setup Uniqueness: report whether active authority is unique by target item, public slug/route, and brand lane.
- Price Identity Ledger: trace business/source intent, Product Setup price, Item Price rows, public display, selector display, cart API if no-write/read-only proof is available, and proof gaps for checkout/documents/payment.
- Media Role Ledger: distinguish Product Setup primary image, Website Item image, Item image, File attachment, gallery/slideshow, metadata/social image, shop card, product gallery, selected-option media, cart image, and downstream proof gaps.
- Listing And Cart Eligibility Invariant: if the product appears checkout-ready, identify whether the read-only evidence proves enabled Item, checkout lane, sellable Item/variant, Standard Selling Item Price, Product Setup authority, public route proof, and cart API proof.
- Document And Payment Proof Modes: this slice allows no-write payload proof only. Anything beyond that is blocked.
- Brand-Lane Resolution: resolve only among `locally_twisted`, `commercial_balloon_decor`, and `memorial_balloons`; ambiguous lane fails closed.

## Implementation Shape

1. Confirm local repo context and read the controlling workstream files.
2. Gather public route evidence without logging in or mutating state.
3. With approved authenticated read-only access, inspect rows for `large-head-missionary` across Website Item, Product Setup, Item template, variant Items, Item Price, gallery/slideshow, File/media, and relevant audit fields.
4. Record exact values, timestamps, `modified_by`, and resolver/source path evidence. Do not infer cause from timestamps alone.
5. Build the incident audit with one named cause or an explicit unresolved blocker.
6. Build the authority matrix template, then instantiate it for `large-head-missionary`.
7. List proof gaps and the next safe non-mutating verifier needed before any repair plan.

## Risk Areas

- False success from treating Product Setup save as public proof.
- Price drift between Product Setup/base price and variant Item Price rows.
- Duplicate or inactive Product Setup records being mistaken for authority.
- Copy/media drift between Product Setup, Website Item, Item, File, slideshow/gallery, shop card, cart, and metadata.
- Cache or deployment drift being named as root cause without row evidence.
- Checkout-looking public behavior without cart/API eligibility proof.
- Hidden mutation through Desk actions, report exports that update state, cache clear helpers, or scripts with side effects.
- Worker overlap in a dirty shared workstream.

## Verification Gates

Gate 1: file-scope proof. Before writing, each worker confirms its assigned output file and does not edit other files.

Gate 2: read-only proof. All ERPNext interactions must be read-only. If the access path cannot be proven read-only, stop.

Gate 3: incident evidence. The audit must name the saved field, saved record, public resolver/surface, visible public output, and row-level evidence for why the save did or did not project.

Gate 4: authority packet completeness. The matrix packet must either resolve every Contract 3 minimum field or mark it as a blocker with the missing evidence and next read-only step.

Gate 5: no mutation proof. The closeout must state that no data, cache, provider, payment, DNS, Frappe Cloud, customer-message, migration, deployment, or code changes were made.

## Allowed Actions

- Read repo files and workstream docs.
- Read public product/shop route output.
- Use authenticated read-only ERPNext/Desk/API/report access when credentials are already available through approved channels.
- Run no-write scripts or queries that only inspect state.
- Produce markdown reports and no-write evidence artifacts in assigned files.
- Mark unresolved evidence as blockers.

## Forbidden Actions

- Any ERPNext insert, update, delete, submit, cancel, patch, migration, fixture apply, or import.
- Cache clear, bench clear-cache, website cache clear, restart, rebuild, deploy, or site update.
- Payment/provider/DNS/Frappe Cloud configuration or proof that creates external records.
- Reading secrets, credentials, raw session files, browser profiles, `.env` files, or token stores.
- Customer emails, payment sessions, invoices, receipts, Sales Order submission, or provider dashboard changes.
- Changing product scope, visibility, prices, routes, media, Product Setup records, Item rows, Item Prices, Website Items, or files.
- Editing any file not explicitly assigned to the worker.

## Escalation Triggers

Escalate before continuing if:

- authenticated read-only access is missing or not clearly read-only;
- the needed row evidence is unavailable without mutation;
- evidence conflicts on brand lane, route, active Product Setup, Item/variant authority, price authority, or media authority;
- duplicate active Product Setup records are found;
- checkout/cart/payment/document proof is required to answer the incident;
- cache clear, deploy, data repair, migration, provider action, or owner approval appears necessary;
- another worker owns or has modified the same output file;
- a proposed next step would affect customers or external systems.

## Exact Stop Conditions

Stop immediately if a command, UI path, script, or API action can write data, clear cache, restart services, deploy code, send a customer message, create payment/document records, or change provider/DNS/Frappe Cloud state.

Stop immediately if credentials are absent, invalid, or would require reading secret files.

Stop immediately if the incident cannot be classified from read-only evidence. Record `unresolved - missing evidence`, name the missing evidence, and do not guess.

Stop immediately after the incident audit and authority packet are complete. Do not proceed into repair design, code implementation, migration planning, release packet creation, or product-family rollout in this slice.

## Acceptance Criteria

- The incident audit identifies the exact backend save evidence and the exact customer-facing/public resolver mismatch, or explicitly records the missing read-only evidence.
- The authority matrix packet exists and covers all Contract 3 minimum fields for `large-head-missionary`, with blockers for unresolved fields.
- The briefed outputs distinguish Product Setup authority, raw ERPNext records, public projections, cart/checkout eligibility, media roles, and price identity.
- All outputs state proof mode and confirm no mutation occurred.
- No Guiding Light question remains unless credentials/access are missing or a business/product-scope decision is required.

## Next Safe Step

Assign separate workers to the Phase 0 incident audit and Phase 1 authority packet artifacts, with one output file per worker. Begin with public route capture and authenticated read-only row inspection for `large-head-missionary`; stop before any repair or cache action.
