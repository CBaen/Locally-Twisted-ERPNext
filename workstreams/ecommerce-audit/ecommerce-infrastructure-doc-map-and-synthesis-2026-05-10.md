D:2026-05-10 | Check:indexed memory + local artifact existence/readback + official ERPNext/Frappe docs fetched 2026-05-10 | Confidence:[LOCAL-PROOF]

# Locally Twisted Ecommerce Infrastructure Doc Map and Synthesis

## Why this exists

GL corrected the lane: this is not a product-row conversation. The real launch blocker is infrastructure: whether ERPNext/Frappe can safely receive, preserve, reject, price, quote, order, invoice, and expose legacy_source-derived ecommerce meaning without silent loss.

This document is the clear map of the infrastructure docs already made, the plan that was supposed to guide the work, what each artifact is for, and what remains to research/prove before any launch/import/purge decision.

## The plan we were supposed to stay on

Found in `workstreams/legacy_source-erpnext-ecommerce-parity-plan-deepen-2026-05-10.md`:

> The audit must prove the receiving architecture, not the migration. A product is not "migrated" until ERPNext can preserve or intentionally reject every customer-facing and operator-facing unit of meaning that product can generate.

The plan's seven guardrails:

1. Separate source extraction, destination mapping, runtime preservation, native architecture, and synthesis lanes.
2. Require durable named artifacts from every lane.
3. Treat quote-first / hold / blocked outcomes as first-class success states, not hidden failures.
4. Use cart, checkout, order, invoice, and operator records as the proof path, not just product pages.
5. Do not copy legacy_source code or blindly reproduce legacy_source data-model quirks.
6. Require exact legacy_source / ERPNext / Frappe / Webshop version evidence before version-sensitive claims.
7. Keep product import and public launch blocked until synthesis names what is safe.

This is the operating plan. Product rows are downstream evidence. Infrastructure proof is the main lane.

## Core infrastructure thesis

ERPNext native ecommerce provides the spine:

- Item / Item Variant
- Website Item
- Item Price / Price List
- Cart / Quotation / Sales Order / Sales Invoice
- Custom Fields / Child DocTypes

But ERPNext native Webshop does not, by itself, preserve Locally Twisted's ecommerce meaning:

- multi-axis product-page decisions,
- color/customization recipes,
- optional add-ons and add-on quantities,
- quote-first vs paid-checkout boundaries,
- valid-combination dependencies,
- media/gallery/variant-photo meaning,
- line-level customer intent on SO/SI/Quotation rows,
- operator review status,
- customer-safe fail-loud behavior.

Therefore LT needs an owned receiving layer around ERPNext/Webshop:

1. Source witness intake.
2. Product-page contract builder.
3. Runtime configuration payloads.
4. Server-side validation/pricing/dependency/add-on services.
5. Line-level preservation on Quotation Item, Sales Order Item, Sales Invoice Item.
6. Quote-first Lead -> Quotation -> reviewed quote -> draft Sales Order bridge.
7. Record-level failure evidence.
8. Import/reopen/verifier gates.

## Infrastructure artifact map

### A. Strategic plan / research framing

| Artifact | Status | Role | What it contributes |
|---|---:|---|---|
| `workstreams/legacy_source-erpnext-ecommerce-parity-research-brief.md` | present | Research brief | Defines the launch-blocker question: can native ERPNext/Frappe preserve product-page depth, add-ons, customer intent, operator meaning, pricing, media, cart/checkout, and backend records before deletion/reimport/public launch. |
| `workstreams/legacy_source-erpnext-ecommerce-parity-plan-deepen-2026-05-10.md` | present | Stress-tested plan | The plan GL is asking us to recover: prove receiving architecture, not migration; require lane artifacts; make quote/hold/blocked first-class outcomes. |
| `research/expedition-erpnext-ecommerce-receiving-architecture/research-synthesis.md` | present | Original infrastructure synthesis | Establishes the backend gap: ERPNext can sell concrete variants, but LT needs line-level configuration preservation and quote-first infrastructure. |
| `workstreams/erpnext-ecommerce-receiving-architecture.md` | present | Running handoff / architecture ledger | Long-lived implementation/research handoff that records the prime directive, current slice, verified commands, remaining gaps, and immediate safe work. |
| `capabilities/recipes/erpnext-ecommerce-receiving-architecture.md` | present | Reusable capability/operating law | Encodes the rule: do not treat product transfer as the goal; every imported concept needs an ERPNext/custom destination, runtime owner, and verifier. |

### B. Infrastructure synthesis / current durable entry points

| Artifact | Status | Role | What it contributes |
|---|---:|---|---|
| `workstreams/ecommerce-audit/ecommerce-infrastructure-research-synthesis-2026-05-10.md` | present | Current corrected synthesis | Corrects the lens from product rows to infrastructure. Summarizes the receiving layer, official docs implications, existing code evidence, and fresh verifier blocker. |
| `workstreams/ecommerce-audit/ecommerce-infrastructure-doc-map-and-synthesis-2026-05-10.md` | this artifact | Clear doc map + synthesis | Maps all infrastructure docs, recovers the plan, and states the current architecture/readiness sequence. |
| `workstreams/ecommerce-audit/README.md` | present, updated | Audit packet index | Should point people to infrastructure synthesis first, with product matrices explicitly downstream. |

### C. Architecture/design lanes

| Artifact | Status | Role | What it contributes |
|---|---:|---|---|
| `workstreams/ecommerce-audit/native-frappe-product-template-architecture-2026-05-10.md` | present | Native architecture design | Recommends the smallest safe Frappe/ERPNext extension layer: page classes, custom fields, child tables, payload schemas, pricing/dependency/media/add-on boundaries, quote vs checkout tree. |
| `workstreams/ecommerce-audit/erpnext-receiving-rebuild-requirements-2026-05-10.md` | present | Rebuild/import requirements | States minimum receiving model before purge/rebuild: native ERPNext spine, LT custom schema, staging registers, services, templates, verifiers, rollback. |
| `workstreams/ecommerce-audit/erpnext-receiving-parity-matrix-2026-05-10.md` | present | Destination parity audit | Maps source meaning to current ERPNext/Frappe receiving destinations, owner modules/services/templates/verifiers, and blockers. |

### D. Runtime preservation / customer-intent proof gates

| Artifact | Status | Role | What it contributes |
|---|---:|---|---|
| `workstreams/ecommerce-audit/cart-checkout-verification-gates-2026-05-10.md` | present | Gate definition | Defines minimum evidence before claiming page -> cart -> checkout -> backend preservation. Bans visual-only checkout claims. |
| `workstreams/ecommerce-audit/cart-checkout-intent-preservation-audit-2026-05-10.md` | present | Representative proof slice | Evidence for configured line identity, foil-number add-on, quote-first rejection/handoff, backend SO/SI preservation for named proof paths only. |
| `output/product-page-architecture-readiness-current.json` | present existing output | Existing readiness evidence | Existing artifact says `technical_architecture_ok: true`, `import_reopen_ok: true`, 14 pass, 0 blocked, 1 deferred, generated 2026-05-10T07:38:02.958904. Treat as existing evidence, not fresh proof. |
| `output/business-automation-index.json` | present existing output | Automation/fail-loud evidence | Existing artifact says 30 surfaces, 12 required, 27 connected, 0 loud-failure gaps. Supports broader fail-loud infrastructure context. |

### E. Safety / acceptance / human review

| Artifact | Status | Role | What it contributes |
|---|---:|---|---|
| `workstreams/ecommerce-audit/ecommerce-rebuild-safety-referee-2026-05-10.md` | present | Safety referee | Names must-block conditions for go-live, purge/rebuild/import, checkout/public ecommerce; requires evidence artifacts before Lane F confidence. |
| `workstreams/ecommerce-audit/gl-proxy-ecommerce-rebuild-acceptance-2026-05-10.md` | present | Human/business acceptance lens | States what GL/Jeff/business users must see and approve: no fake checkout, honest quote-first paths, plain labels, no unresolved prices/media/add-ons hidden under polish. |

### F. Source witness / convergence artifacts

| Artifact | Status | Role | What it contributes |
|---|---:|---|---|
| `workstreams/ecommerce-audit/legacy_source-source-commerce-map-2026-05-10.md` | present, parent-verified earlier | legacy_source source witness map | Maps legacy_source commerce meaning into ERPNext requirements. Use as source witness, not implementation source. |
| `workstreams/ecommerce-audit/legacy_source-docs-agent-action-convergence-2026-05-10.md` | missing / `[NO EVIDENCE]` | Docs/observed convergence | Still missing. Needed to reconcile legacy_source docs, observed legacy_source behavior, ERPNext docs/current behavior, and agent actions. |

### G. Downstream-only product/source matrices

| Artifact | Status | Role | How to treat it |
|---|---:|---|---|
| `workstreams/ecommerce-audit/ecommerce-product-proof-matrix-2026-05-10.md` | present | Downstream source/product audit view | Useful only after infrastructure gates. Do not let this become the main architecture artifact. |
| `workstreams/ecommerce-audit/ecommerce-knowledge-base-index-2026-05-10.md` | present | Supporting index | Useful locator for memory/artifacts/docs, but not the infrastructure decision itself. |
| `audits/catalog-import-audit-2026-05-08/*price*`, `*media*`, `*add-on*` packets | present | Downstream review packets | Feed import/reopen review. They do not approve launch by themselves. |

## Current infrastructure state from readback

### Strong / usable evidence

- The project has the correct infrastructure direction: LT-owned receiving layer around ERPNext/Webshop.
- Existing research and capability docs converge on the same model: ERPNext native records are the spine; LT custom runtime preserves meaning.
- `workstreams/erpnext-ecommerce-receiving-architecture.md` documents implemented slices including:
  - code-owned page type and commerce-lane fields,
  - line-level configuration fields on Sales Order Item / Sales Invoice Item / Quotation Item,
  - `lt-product-config-v1` runtime payload,
  - quote-first Lead/Quotation bridge,
  - draft-only quote acceptance and operator review controls,
  - add-on proof for `foil_number`,
  - review-only boundaries for unapproved add-on families,
  - source dependency matrices,
  - price/media review packet infrastructure,
  - public/local testing verifiers from the earlier evidence run.
- Static compile proof from 2026-05-10 passed for core infrastructure files:
  - `product_page_runtime.py`
  - `product_quote_runtime.py`
  - `api/cart.py`
  - `www/checkout.py`
  - `verify/product_page_architecture_readiness.py`

### Evidence that must be handled carefully

- `output/product-page-architecture-readiness-current.json` is an existing current-day artifact, not a fresh rerun from this moment.
- A later fresh attempt to run `product_page_architecture_readiness.py` failed before report generation with `bench execute failed` after CSS parser messages. Do not claim fresh current architecture readiness until this is diagnosed and rerun cleanly.
- Lane E remains `[NO EVIDENCE]` unless created.
- legacy_source and destination version mismatches remain material:
  - destination runtime evidence includes ERPNext `15.105.0`, Frappe `15.106.0`, apps `payments`, `webshop`, `locally_twisted`, but image naming/version anchoring had mismatch risk;
  - legacy_source source module local `19.0.2.15.0`, prior warning production DB may still be `19.0.2.14.0`.

## Infrastructure layers that must exist before any safe import/reopen claim

1. **Source authority decision**
   - Which legacy_source witness controls: local source, production DB, public page capture, export, or some reconciled bundle.
   - Version mismatch must be labeled or resolved.

2. **Receiving staging register**
   - One row per source/current ecommerce object.
   - Must name destination fields/services/actions and blockers.
   - Product rows belong here, downstream of architecture.

3. **Page class and buying path infrastructure**
   - Page Template / Buying Path fields.
   - Conservative fallback for `needs_review`.
   - Plain operator/customer labels; no raw snake_case leaking.

4. **Runtime configuration contract**
   - Versioned payload.
   - Reject stale/malformed/oversized/unsupported payloads loudly.
   - Server owns validation and pricing.

5. **Line-level preservation infrastructure**
   - Quotation Item, Sales Order Item, Sales Invoice Item custom fields or child rows.
   - Configuration summary and JSON copied through lifecycle.

6. **Checkout-safe add-on infrastructure**
   - Approved add-ons only.
   - Eligibility by product/page/family.
   - Server-priced add-on Items.
   - Unsupported add-ons route quote-first or block safely.

7. **Quote-first infrastructure**
   - Product page -> Lead child row -> draft Quotation -> operator review -> reviewed quote delivery -> accepted quote draft Sales Order.
   - No invoice/payment/email side effects unless the matching gate explicitly approves them.

8. **Dependency / option availability infrastructure**
   - Required-axis valid combinations are executable.
   - Color/customization axes do not explode SKU logic unless explicitly intended.
   - Impossible selections fail loudly.

9. **Media infrastructure**
   - Primary, variant, gallery, category/reference, and hold roles.
   - No multi-photo/variant-photo claim without classification and browser proof.

10. **Fail-loud and verifier infrastructure**
    - Record-level failure evidence.
    - Dated reports.
    - Browser + backend proof where customer intent or launch claims are involved.

## Correct sequencing from here

### Stage 0 - Stop product-row drift

Use this document and `ecommerce-infrastructure-research-synthesis-2026-05-10.md` as the front door. Product matrices are allowed only as downstream evidence.

### Stage 1 - Repair current proof freshness

Diagnose the fresh `product_page_architecture_readiness.py` / `bench execute failed` blocker. Generate a dated clean report in the intended ecommerce mode, or carry `[BLOCKED]` explicitly.

### Stage 2 - Finish missing convergence lane

Create or explicitly block `legacy_source-docs-agent-action-convergence-2026-05-10.md`. This should reconcile:

- official legacy_source ecommerce docs/behavior model,
- local legacy_source source witness,
- public/captured legacy_source behavior where safe,
- official ERPNext/Frappe docs,
- current LT ERPNext runtime behavior,
- discrepancy labels: `[DOCS-MISMATCH]`, `[SOURCE-MISMATCH]`, `[LIVE-MISMATCH]`, `[ERPNext-GAP]`, `[UNKNOWN]`.

### Stage 3 - Build infrastructure readiness packet

Create a gate table with:

- infrastructure layer,
- owner file/service/template,
- verifier command,
- last artifact path,
- last check date,
- status: pass / partial / blocked / no evidence / stale risk,
- launch implication.

This packet should replace product-row talk as the operational dashboard.

### Stage 4 - Only then use product matrices

Use source/product rows to feed the receiving staging register. Do not let them answer architecture readiness.

### Stage 5 - Lane F synthesis only with claim-to-witness mapping

Lane F must cite artifact paths per claim. Missing artifacts lower confidence or block the claim.

## Banned shortcuts

- “Products are ready” based on a matrix.
- “Checkout works” based only on browser/cart display.
- “ERPNext ecommerce works” without line-level SO/SI/Quotation evidence.
- “legacy_source parity” as a goal.
- Copying legacy_source code or schema without ERPNext destination ownership.
- Treating live-snapshot prices as business-approved.
- Treating unclassified media as gallery/variant-photo ready.
- Treating quote-first placeholder `$0` records as customer pricing.
- Treating an artifactless subagent completion as evidence.

## Bottom-line synthesis

The recovered plan is good: prove a receiving ecosystem, not product migration. The infrastructure docs already made are substantial and mostly coherent. The failure was presentation and attention: product matrices were allowed to step in front of the receiving architecture.

The correct current state is:

- Infrastructure direction: **sound and source-backed**.
- Existing implemented slice: **substantial, with same-day artifacts and many prior verifiers**.
- Fresh proof status: **blocked until architecture readiness rerun issue is diagnosed**.
- Missing research: **Lane E convergence artifact**.
- Launch/import status: **not approved**.
- Next durable artifact needed: **infrastructure readiness packet**, not another product table.
