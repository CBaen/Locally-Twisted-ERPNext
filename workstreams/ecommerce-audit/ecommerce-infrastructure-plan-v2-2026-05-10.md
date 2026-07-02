D:2026-05-10 | Check:memory recall + local infrastructure docs readback 2026-05-10 | Confidence:[LOCAL-PROOF]

# Ecommerce Infrastructure Plan v2 - Receiving System First

## One-sentence plan

Build and prove a Locally Twisted owned ecommerce receiving system around ERPNext/Webshop before using product rows for import, public checkout, or launch decisions.

## Perspective reset

The launch-critical question is not:

> Are the products ready?

The launch-critical question is:

> Can ERPNext/Frappe safely receive catalog_data-derived ecommerce meaning from page -> cart/quote -> checkout -> Sales Order -> invoice/operator workflow, while preserving customer intent or failing loudly?

Products are downstream test cases. Infrastructure is the main work.

## Non-negotiables

1. **catalog_data is a witness, not a blueprint.** Preserve business meaning; do not copy catalog_data code or accidental architecture.
2. **ERPNext is the accounting/catalog spine, not the whole ecommerce brain.** Native Item, Website Item, Item Price, Quotation, Sales Order, and Sales Invoice are necessary but not sufficient.
3. **LT owns the receiving layer.** Product-page contracts, configuration payloads, quote-first bridge, add-ons, dependency logic, media classification, and fail-loud verifiers are LT infrastructure.
4. **Quote-first / hold / blocked are valid success states.** Fake checkout is not success.
5. **No artifact = no evidence.** Completion text, routed subagent output, or product tables without witness paths do not count.
6. **No public launch/import/purge until gates pass.** Existing proof slices are useful; they are not full-catalog launch approval.

## Target infrastructure model

### Layer 1 - Source authority

Purpose: decide what source evidence controls the rebuild.

Inputs:

- catalog_data local source/module evidence.
- User-provided catalog_data surfaces.
- Any safe public catalog_data page captures.
- Existing source maps and audit packets.
- Official catalog_data docs where relevant.

Required output:

- Source authority decision note naming version/context conflicts.
- Labels for each finding: business meaning, implementation artifact, stale/unclear, source bug/regression, unknown.

Current blocker:

- catalog_data local module evidence is `19.0.2.15.0`; prior notes warn production DB may still be `19.0.2.14.0`.

### Layer 2 - Receiving contract register

Purpose: one infrastructure-facing staging register that says how each kind of ecommerce meaning is received.

This is not primarily a product matrix. It is a contract map:

| Meaning type | Source witness | ERPNext/native destination | LT custom destination | Runtime owner | Verifier | Failure mode |
|---|---|---|---|---|---|---|
| Required variant axis | catalog_data/source/page | Item Variant / Website Item configure | Contract model / dependency matrix | `product_page_runtime.py` | architecture/cart verifier | block/quote-first |
| Custom color/design recipe | catalog_data/source/page | none sufficient alone | payload JSON / quote child row | quote runtime | quote verifier | quote-first |
| Paid checkout add-on | source + business approval | add-on Item + Item Price | add-on payload + linked SO/SI lines | cart/runtime service | backend record proof | reject if unapproved |
| Media/gallery meaning | source images/pages | Website Item image / Item image / slideshow if approved | classification packet | media/register verifier | browser proof | hold until classified |

Required output:

- `ecommerce-infrastructure-readiness-packet-2026-05-10.md` or equivalent.
- It should be the operational dashboard, replacing product-row-first status.

### Layer 3 - Page class and buying path

Purpose: every public ecommerce page must have a safe machine lane and customer/operator label.

Core lanes:

- `simple_product` / checkout-capable only when all runtime gates pass.
- `complex_custom_product` / quote-first.
- `needs_review` / safe block or inquiry path.
- `hybrid` / disabled unless separately proven.

Required output:

- Evidence that machine values do not leak as customer copy.
- Evidence that unknown/missing classification cannot become paid checkout.

### Layer 4 - Runtime configuration payload

Purpose: every customer selection becomes a versioned, server-validated payload before cart/quote/order.

Minimum contract:

- `schema_version: lt-product-config-v1`
- website item / template context
- sellable item/variant when checkout-capable
- selected options with customer-facing labels
- approved add-ons only
- customizations/color/design details when quote-first
- quote/review flags when paid checkout is unsafe

Required output:

- Positive proof for supported payloads.
- Negative proof for stale, malformed, oversized, unsupported, or route-manipulated payloads.

### Layer 5 - Cart and checkout preservation

Purpose: prove the cart and checkout are not silently flattening customer intent.

Required proof families:

1. Same-SKU configured lines remain separate when selections differ.
2. Required options cannot be bypassed.
3. Approved add-ons become priced/add-on-linked lines.
4. Review-only add-ons cannot sneak into checkout as free/hidden notes.
5. Quote-first items cannot be forced into checkout by route/item-code manipulation.
6. Backend Sales Order Item rows preserve the same meaning the customer saw.

No allowed shortcut:

- Browser checkout display alone does not prove backend preservation.

### Layer 6 - Quote-first bridge

Purpose: complex products must preserve customer intent without pretending payment checkout is safe.

Path:

Product page -> Contact/Lead structured payload -> draft Quotation packet -> operator review -> reviewed quote delivery -> accepted quote draft Sales Order only when approved.

Required proof:

- Lead/Quotation fields/child rows preserve product/page/selected details.
- Draft quote language does not imply paid order success.
- No invoice/payment/email side effects unless explicitly approved and verified.

### Layer 7 - Pricing/add-ons/media/dependency services

Purpose: separate source meaning from approval and runtime truth.

Subsystems:

- Pricing: ERPNext Item Price for checkout rates; source/live prices need review status.
- Add-ons: approved checkout add-ons vs quote-only/review-only families.
- Dependencies: valid combinations executable over required axes only.
- Media: primary/variant/gallery/reference/hold classification.

Required output:

- Human review packets for price/add-on/media/color/customization decisions.
- No checkout route for unresolved or business-review-required units.

### Layer 8 - Fail-loud verifier system

Purpose: every customer-facing claim needs a matching verifier or named blocker.

Required evidence types:

- Static code checks for infrastructure files.
- Runtime architecture readiness report.
- Browser witness for public/customer paths.
- Backend record witness for Sales Order / Sales Invoice / Lead / Quotation survival.
- Cleanup/no-side-effect witness for test-created records.
- Human approval witness where business judgment is required.

## New work plan

### Phase 0 - Pin the perspective and stop drift

Status: mostly done.

Artifacts now serving as the front door:

- `workstreams/ecommerce-audit/ecommerce-infrastructure-doc-map-and-synthesis-2026-05-10.md`
- `workstreams/ecommerce-audit/ecommerce-infrastructure-research-synthesis-2026-05-10.md`
- `workstreams/ecommerce-audit/README.md`

Done when:

- All future ecommerce reports start from infrastructure layers, not product readiness.
- Product proof matrices are explicitly labeled downstream.

### Phase 1 - Repair evidence freshness

Goal: stop relying on stale-ish or half-failed verifier evidence.

Actions:

1. Diagnose the `product_page_architecture_readiness.py` / `bench execute failed` blocker.
2. Determine whether CSS parser messages are noise or part of the failure path; do not assume.
3. Rerun architecture readiness in the intended ecommerce mode.
4. Save dated report under `output/`.
5. If rerun cannot be completed quickly, write a blocker artifact with exact failure and next diagnostic step.

Deliverable:

- `output/product-page-architecture-readiness-infrastructure-plan-v2-20260510.json` or a named blocker report.

Gate:

- No fresh architecture-ready claim until this passes.

### Phase 2 - Finish convergence research

Goal: close the missing Lane E gap.

Actions:

1. Create `workstreams/ecommerce-audit/catalog_data-docs-agent-action-convergence-2026-05-10.md`.
2. Reconcile:
   - official ERPNext/Frappe/Webshop docs,
   - official catalog_data ecommerce behavior/doc concepts where useful,
   - local catalog_data source witness,
   - current LT ERPNext code/runtime behavior,
   - prior agent actions and artifacts.
3. Label mismatches:
   - `[VERSION-MISMATCH]`
   - `[DOCS-MISMATCH]`
   - `[SOURCE-MISMATCH]`
   - `[LIVE-MISMATCH]`
   - `[ERPNext-GAP]`
   - `[UNKNOWN]`

Deliverable:

- Lane E convergence artifact with sources, commands/actions, findings, blockers, and confidence.

Gate:

- No final synthesis should claim docs/source/current-action convergence while this is missing.

### Phase 3 - Build the infrastructure readiness packet

Goal: create the real dashboard.

Actions:

1. List every infrastructure layer.
2. For each layer, name:
   - owner file/service/template/DocType,
   - expected ERPNext/native destination,
   - LT custom destination,
   - last evidence artifact,
   - verifier command,
   - status: pass / partial / blocked / no evidence / stale risk,
   - launch/import implication.
3. Include stop conditions and next proof command.

Deliverable:

- `workstreams/ecommerce-audit/ecommerce-infrastructure-readiness-packet-2026-05-10.md`

Gate:

- This packet becomes the launch/import conversation surface. Product tables feed it; they do not replace it.

### Phase 4 - Prove runtime paths by infrastructure behavior

Goal: representative proof that the receiving system works end-to-end for classes of behavior.

Proof paths:

1. Ready-to-order configured product.
2. Ready-to-order single-SKU product.
3. Same-SKU different configuration separation.
4. Approved paid add-on.
5. Review-only add-on rejection.
6. Quote-first complex product.
7. Malformed/stale/unsupported payload failure.
8. Media/browser display where media claims are made.

Required witness for each path:

- browser/customer view,
- cart/checkout resolver,
- backend records,
- customer-safe failure copy where relevant,
- cleanup/no-side-effect proof for test data.

Deliverable:

- `workstreams/ecommerce-audit/ecommerce-runtime-path-proof-bundle-2026-05-10.md`

Gate:

- No "checkout works" claim without named backend records and preserved customer intent.

### Phase 5 - Human/business approval packets

Goal: separate architecture proof from business judgment.

Packets:

1. Source witness/version decision packet.
2. Price review packet.
3. Add-on approval packet.
4. Media classification packet.
5. Color/customization/operator workflow packet.
6. Public copy/policy/payment/email scope packet.

Human decisions needed:

- GL/Jeff approve whether each behavior is checkout, quote-first, hidden/excluded, or blocked.
- GL/Jeff approve price source/override decisions.
- GL/Jeff approve media/gallery meaning.
- GL/Jeff approve whether real payment/email is in launch scope.

Gate:

- Architecture green is not business approval green.
- Business approval green is not launch green.

### Phase 6 - Import/reopen plan only after infrastructure gates

Goal: design the smallest safe import/reopen batch.

Actions:

1. Use product/source rows only after infrastructure readiness packet exists.
2. Select the smallest proof batch by infrastructure class, not by product excitement.
3. Prepare rollback/dry-run plan.
4. Rebuild/import only into approved scope.
5. Verify batch-by-batch.

Deliverable:

- `workstreams/ecommerce-audit/ecommerce-import-reopen-safety-plan-2026-05-10.md`

Gate:

- No purge/import/rebuild without explicit GL approval, rollback anchor, dry-run report, and success/failure criteria.

### Phase 7 - Launch decision packet

Goal: make the final go/no-go impossible to fake.

Required sections:

- Infrastructure readiness status.
- Runtime proof paths and backend evidence.
- Human approvals.
- Payment/email/tax/delivery scope.
- Excluded/blocked items and customer-facing behavior.
- Rollback plan.
- Known risks accepted by GL/Jeff.

Deliverable:

- `workstreams/ecommerce-audit/ecommerce-launch-decision-packet-2026-05-10.md` or later dated equivalent.

Gate:

- Launch green only exists if architecture proof, business approval, and customer-facing/payment scope all pass together.

## Immediate next actions I recommend

1. **Diagnose the readiness verifier blocker.** This is the highest-leverage unblocker because it tells us whether current infrastructure proof is fresh or stale-risk.
2. **Create Lane E convergence artifact.** This closes the missing research lane without broad subagent fanout.
3. **Create the infrastructure readiness packet.** This becomes the control panel for GL/Jeff/me.
4. **Only then return to product/source rows** as inputs into the receiving register.

## What I will not do under this plan

- I will not call product matrices the main proof.
- I will not claim checkout works from visual browser success alone.
- I will not click/write/mutate authenticated catalog_data admin surfaces without preflight and no-write guard.
- I will not purge/import/rebuild products without explicit approval and rollback/dry-run gates.
- I will not treat old agent completion output as evidence without reading the artifact.
- I will not hide `[NO EVIDENCE]` lanes in prose.

## Definition of done for this plan

This plan is done when we can point to one infrastructure dashboard that says, for each ecommerce receiving layer:

- what meaning it receives,
- where it stores that meaning,
- what runtime path uses it,
- what verifier proves it,
- what blocks it,
- what GL/Jeff still need to decide,
- and whether the result is checkout, quote-first, hold, blocked, or excluded.

Only after that do product rows become safe launch/import planning material.
