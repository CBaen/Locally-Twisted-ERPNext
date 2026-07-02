# catalog_data Commerce Source Extraction + ERPNext/Frappe Ecommerce Parity/Safety Audit — Research Brief

Date: 2026-05-10
Status: draft, plan-deepened before dispatch
Owner context: Locally Twisted ERPNext/Frappe ecommerce receiving architecture
Required researcher header: `D:YYYY-MM-DD | Check:<source/date> | Confidence:<label>`
Parent accountability: Moji/parent is responsible for injecting this contract into spawned-agent prompts and rejecting missing-header/missing-evidence reports; do not blame spawned agents for omissions the parent failed to require.

## 1. Decision / Research Question

Can Locally Twisted safely launch native ERPNext/Frappe ecommerce without losing the product-page depth, add-on behavior, customer intent, operator meaning, pricing logic, media meaning, cart/checkout behavior, and backend order/invoice/fulfillment data that the catalog_data system either supported or exposed as necessary?

This is not a product-import task. The question is whether the new ERPNext/Frappe ecommerce receiving architecture can safely receive and use the business meaning of the old commerce system before products are deleted, reimported, normalized, opened publicly, or treated as launch-ready.

## 2. Background / Current Known State

Current evidence shows the ERPNext/Frappe stack has a real backend-first architecture direction, but only a proved slice is approved.

Version/context anchors researchers must treat as part of the problem, not trivia:

- Destination stack is Locally Twisted ERPNext/Frappe v15, documented locally as custom Docker image `locally-twisted-erpnext:v15` built from base `frappe/erpnext:v15.105.0`, compose project `locally-twisted-erpnext-v15`, apps `frappe`, `erpnext`, `payments`, `webshop`, and `locally_twisted`.
- Source witness stack is Locally Twisted catalog_data 19 Community. The tracked local module manifest currently says `addons/locally_twisted` version `19.0.2.15.0`; prior migration-risk docs warn production DB may be `19.0.2.14.0` while `origin/main` contains `19.0.2.15.0`, so source-version parity must be verified before any source claim is treated as complete.
- catalog_data version behavior matters: website editor / `arch_db` drift, `noupdate`, Copy-on-Write, asset behavior, `website_sale` combination/variant resolver behavior, and production-vs-source divergence may change what is true.
- ERPNext/Frappe version behavior matters: Webshop v15 cart/checkout APIs, Website Item/Item Price behavior, custom field sync, fixtures, hooks, scheduler, and Sales Order/Sales Invoice copying paths are version-specific.

Proved current slice:

- Public local ecommerce has been reopened for testing by setting `lt_ecommerce_paused=0`.
- `ADDON-FOIL-NUMBER` is the one confirmed paid add-on proof slice:
  - code-owned ERPNext Item,
  - priced from ERPNext Item Price,
  - expands into Sales Order / Sales Invoice lines,
  - appears in cart API display rows,
  - requires product/template eligibility,
  - preserves selected foil-number value in versioned configuration payload.
- Same-SKU configured cart lines use stable line keys, so different options/add-ons do not collapse into one cart line.
- Other source add-on families remain review-only / quote-first until source-backed approval exists.
- Existing verifiers include product-page architecture readiness, runtime contract, dependency contracts, add-on approval packet, cart/checkout contract, quote-first experience, quote acceptance, price/media gates, and ecommerce full smoke.
- catalog_data is source witness/context, not infrastructure to copy. The target implementation must be native ERPNext/Frappe with secure fields, DocTypes, APIs, template overrides, pricing services, and fail-loud verifiers where needed.

The dangerous failure mode is not “the page looks bad.” The dangerous failure mode is: a customer selects meaningful options, add-ons, dates, quantities, prices, or quote context, and the system visually accepts it while ERPNext receives incomplete, flattened, silently changed, or operator-useless records.

## 3. Scope for Researchers

Researchers must produce artifact-first evidence. Chat-only opinions are not findings. Every report/artifact must start with `D:YYYY-MM-DD | Check:<source/date> | Confidence:<label>`, use current docs/source/runtime/web checks for current technology or company-impacting claims, and label missing checks/artifacts as `[NOT CHECKED]`, `[STALE-RISK]`, `[NO EVIDENCE]`, or `[BLOCKED]`.

### In scope

1. catalog_data source behavior extraction
   - Product templates/pages
   - Variant axes and valid-combination logic
   - Add-on families and dependencies
   - Optional vs required choices
   - Price sources and price transformations
   - Product/category/media visibility
   - Cart and checkout behavior
   - Quote vs paid checkout boundaries
   - Backend order/invoice/operator fields

2. ERPNext/Frappe destination parity audit
   - Existing Website Item / Item / Item Price / Sales Order / Sales Invoice / Quotation / Lead custom fields
   - Product page runtime payloads
   - Cart line identity and configured-line preservation
   - Checkout translation into Sales Order Item rows
   - Invoice-line copying
   - Quote-first handoff into Lead and Quotation
   - Operator review and quote acceptance flows
   - Fail-loud backend failure evidence

3. Native architecture proposal
   - Which behavior belongs in ERPNext custom fields
   - Which behavior belongs in custom DocTypes / child tables
   - Which behavior belongs in versioned JSON payloads
   - Which behavior belongs in Python services / whitelisted APIs
   - Which behavior belongs in Jinja/templates/frontend controllers
   - Which behavior should stay quote-first, not paid checkout

4. Launch safety gates
   - Proof that customer intent survives product page → cart → checkout → Sales Order → invoice/operator review
   - Proof that unknown/unapproved source behavior fails loudly or routes quote-first
   - Proof that public ecommerce cannot silently accept unsupported combinations
   - Proof that product import/reopen gates are separated from technical architecture gates

### Out of scope

- Copying catalog_data code into Frappe.
- Treating catalog_data data shape as automatically correct for ERPNext.
- Deleting and reimporting products before receiving architecture is proven.
- Launch claims based only on visual frontend inspection.
- “Checkout passed” claims that do not verify Sales Order, Sales Invoice, operator fields, quote payloads, and failure records.
- Treating existing test products as approval for full catalog import.

## 4. Required Research Lanes and Artifacts

### Lane A — catalog_data Source Mapper

Goal: extract source commerce meaning without proposing implementation first.

Required artifact:
`workstreams/ecommerce-audit/catalog_data-source-commerce-map-2026-05-10.md`

Must include:
- exact catalog_data edition/version/module version evidence used for source claims, including whether evidence comes from source files, live/public pages, captured mirrors, exports, or production DB notes,
- product/page classes found in catalog_data source,
- variant axes and valid-combination rules,
- add-on families and affected products,
- pricing source(s) and gaps,
- media/gallery/variant-image signals,
- quote vs checkout behavior,
- backend order/invoice/operator data that mattered,
- explicit unknowns and source files/records used.

### Lane B — ERPNext/Frappe Receiving Parity Auditor

Goal: map each source meaning to current ERPNext/Frappe receiving destination or mark it missing.

Required artifact:
`workstreams/ecommerce-audit/erpnext-receiving-parity-matrix-2026-05-10.md`

Must include a matrix with:
- exact ERPNext/Frappe/Webshop/app version evidence used for destination claims,
- source behavior / field / rule,
- current ERPNext destination,
- owner module/service/template/verifier,
- current status: preserved / transformed / quote-first / missing / blocked,
- evidence path,
- required gate before import or launch.

### Lane C — Cart / Checkout / Silent-Failure Auditor

Goal: prove whether customer intent survives the runtime journey.

Required artifact:
`workstreams/ecommerce-audit/cart-checkout-intent-preservation-audit-2026-05-10.md`

Must include:
- product page payload examples,
- cart line identity behavior,
- same-SKU configured-line behavior,
- add-on line expansion behavior,
- checkout translation into Sales Order Item rows,
- invoice copying behavior,
- quote-first rejection paths,
- user-facing and operator-facing error states,
- negative tests for unsupported options/add-ons.

### Lane D — Native Product Template Architecture Designer

Goal: propose the smallest native Frappe architecture that can safely receive the catalog.

Required artifact:
`workstreams/ecommerce-audit/native-frappe-product-template-architecture-2026-05-10.md`

Must include:
- recommended product-page classes,
- required custom fields / child tables / DocTypes,
- versioned payload schema boundaries,
- pricing and dependency service boundaries,
- media destination strategy,
- add-on approval workflow,
- quote-first vs checkout decision tree,
- migration/import staging plan with rollback/fail-loud gates.

### Lane E — catalog_data Documentation / Agent-Action Convergence Researcher

Goal: compare what catalog_data's official/user-facing ecommerce model says should happen with what agents observe by clicking through the Locally Twisted catalog_data witness surfaces and current ERPNext/Frappe surfaces.

This lane is not allowed to copy catalog_data code. It is allowed to read catalog_data documentation, local source structure, public/live/captured pages, and current ERPNext/Frappe behavior to understand concepts, blast radius, and mismatch risk.

Required artifact:
`workstreams/ecommerce-audit/catalog_data-docs-agent-action-convergence-2026-05-10.md`

Must include:
- exact catalog_data documentation pages/versions consulted,
- exact catalog_data local/source/live/captured surfaces clicked or inspected,
- exact ERPNext/Frappe pages/actions clicked or inspected,
- a convergence table: documented behavior / observed catalog_data behavior / observed ERPNext behavior / discrepancy / risk / required decision,
- special attention to product variants, `website_sale` combination behavior, add-ons/accessories/options, cart preservation, checkout payloads, order/invoice semantics, and customer-visible promises,
- every discrepancy labeled `[DOCS-MISMATCH]`, `[SOURCE-MISMATCH]`, `[LIVE-MISMATCH]`, `[ERPNext-GAP]`, or `[UNKNOWN]`.

### Lane F — Referee / Synthesis

Goal: reconcile lanes into one launch-blocker decision packet.

Required artifact:
`workstreams/ecommerce-audit/ecommerce-launch-readiness-synthesis-2026-05-10.md`

Must include:
- what is safe now,
- what is only technically proven but not business-approved,
- what is missing,
- what must stay quote-first,
- what blocks product import,
- what blocks public launch,
- exact verifier commands that must pass,
- exact GL decisions needed,
- discrepancies between catalog_data documentation, catalog_data observed behavior, and ERPNext observed behavior.

## 5. Acceptance Bar / Definition of Done

The audit is usable only if it produces source-backed, repo-backed, artifact-backed findings.

Minimum acceptance:

- Every source claim cites a file, record export, script output, or current code path.
- Every ERPNext claim cites a current code path, verifier, database metadata check, or browser/runtime proof.
- Every unknown is labeled `[UNKNOWN]`, `[UNVERIFIED]`, or `[BLOCKED]` instead of smoothed over.
- Exact catalog_data and ERPNext/Frappe versions are verified and cited before version-sensitive claims are trusted.
- catalog_data code is not copied; catalog_data is used only as a source witness.
- Full product import remains blocked unless every required source behavior has a safe ERPNext receiving destination or explicit quote-first/hold behavior.
- Public ecommerce launch remains blocked unless customer intent preservation is verified through backend order/invoice/operator surfaces.
- Existing verifier suite is named, run where appropriate, and extended where it cannot catch a silent drop.

## Initial Verifier Baseline

Known relevant verifier commands:

```bash
python scripts/verify/product_page_architecture_readiness.py --report output/product-page-architecture-readiness.json
python scripts/verify/product_page_runtime_contract.py
python scripts/verify/product_add_on_dependency_contract.py
python scripts/verify/product_add_on_approval_packet.py
python scripts/verify/cart_checkout_contract.py
python scripts/verify/product_quote_operator_review_contract.py
python scripts/verify/product_quote_acceptance_contract.py
npm run test:quote-accept-experience
python scripts/verify/product_quote_customer_delivery_contract.py
python scripts/verify/product_quote_operator_send_control_contract.py
python scripts/verify/product_quote_customization_contract.py
python scripts/verify/product_page_dependency_contract.py
npm run test:ecommerce-full
npm run test:product-quote-first
```

Researchers may add focused verifiers, but must not replace backend proof with visual-only checks.
