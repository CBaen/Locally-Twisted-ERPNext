D:2026-05-10 | Check:local source/docs/artifacts + read-only static inspection 2026-05-10 | Confidence:[LOCAL-PROOF]
# Phase 1-4 ecommerce/shop deep audit — verifier lens

> 2026-05-11 count correction: this audit was written before the final all-enabled-SKU verifier. Treat any Phase 3 wording about sample/representative checkout-family proof, Easter deferral, or 27/28 order rows as superseded by `checkout-enabled-sku-parity-proof-2026-05-11.md` and `2026-05-10-2330-phase-1-4-shop-audit/checkout-product-family-all-skus-final.json`: 15 checkout Website Item families/pages, 47 enabled sale SKUs, 39 add-on rows, 86 Sales Order/Sales Invoice rows, rollback clean. Public ecommerce still remains paused.

## 1. Scope and lens

Verifier lens only. I inspected whether the current Phase 1-4 evidence proves the claimed ecommerce/shop boundaries without treating the current 53 ERPNext products as final catalog truth.

Boundaries held for this audit:

- No purge/reupload/import, no public ecommerce open, no DB-mutating verifier runs, no branch/stage/commit/push.
- Current ERPNext products are test fixtures only.
- PASS claims below are limited to current source/runtime/verifier artifacts and durable JSON/docs already present in the repo.

## 2. What I inspected

Primary sources:

- Brief: `workstreams/ecommerce-audit/phase-1-4-deep-audit-brief-2026-05-10.md`.
- Runtime: `apps/locally_twisted/locally_twisted/product_page_runtime.py`, `apps/locally_twisted/locally_twisted/api/cart.py`, `apps/locally_twisted/locally_twisted/www/checkout.py`, `apps/locally_twisted/locally_twisted/public/js/lt-guest-cart.js`, `apps/locally_twisted/locally_twisted/ecommerce_pause.py`.
- Verifiers: `apps/locally_twisted/locally_twisted/verify/website_item_classification_contract.py`, `apps/locally_twisted/locally_twisted/verify/checkout_product_family_contract.py`, `apps/locally_twisted/locally_twisted/verify/quote_event_checkout_boundary_contract.py`, `apps/locally_twisted/locally_twisted/verify/product_page_architecture_readiness.py`, plus script wrappers under `scripts/verify/`.
- Durable artifacts: `workstreams/ecommerce-audit/phase-3-checkout-product-family-contract-20260510.json`, `workstreams/ecommerce-audit/phase-4-quote-event-checkout-boundary-contract-20260510.json`, `workstreams/ecommerce-audit/ready-to-order-ecommerce-goal-progress-2026-05-10.md`, `workstreams/ecommerce-audit/ready-to-order-product-cut-plan-2026-05-10.md`, `workstreams/ecommerce-audit/phase-4-quote-event-path-hardening-result-2026-05-10.md`, `capabilities/recipes/erpnext-ecommerce-receiving-architecture.md`, `CODING-HANDOFF.md`.

## 3. Findings by severity

### PASS — Phase 1-4 runtime boundary is evidence-backed for current fixtures

The paid-checkout allowlist is server-side and fail-closed:

- `product_page_runtime.py` says paid checkout is allowed only when Website Item explicitly stores `simple_product` + `checkout`; inferred checkout fails closed to `needs_review` (`product_page_runtime.py:236-276`).
- `api/cart.py` resolves sellable cart lines from the server and returns `quote_required` when the product page contract lane is not `checkout` (`api/cart.py:80-150`).
- `/checkout` resolves sale lines server-side and blocks missing/quote-required items; malformed cart JSON fails validation (`www/checkout.py:442-515`).
- Public checkout APIs are pause-guarded and return a 403/no-purchase response while ecommerce is paused (`www/checkout.py:663-676`, `www/checkout.py:718-830`; pause source `ecommerce_pause.py:35-37`).

Verdict: Phase 1-4 proves a reusable backend boundary for the current fixture set. It does not prove final catalog/import truth.

### PASS — Phase 2 classification proof is fixture-scoped and narrow

The classification verifier is explicit about scope:

- It targets only `Website Item.lt_product_page_type` and `Website Item.lt_commerce_lane` for the 53 named source-backed product-page records (`website_item_classification_contract.py:1-5`).
- It expects 53 total records, split 15 checkout-ready-after-small-fix, 33 quote-first, 5 hide/needs-review (`website_item_classification_contract.py:96-100`).
- It reports `only_mutated_doctype: Website Item` and stored target counts in its result shape (`website_item_classification_contract.py:260-265`).

Verdict: Good evidence that the current 53 fixtures have the intended stored Website Item contracts. Not evidence that a future purge/reupload will recreate those fields.

### PASS — Phase 3 checkout-family proof preserves backend meaning and rolls back

Durable Phase 3 artifact proves the scoped checkout family, not the whole catalog:

- 13 bouquet-family pages are represented (`phase-3-checkout-product-family-contract-20260510.json:108`).
- The proof includes line fields for LT configuration version/summary/json/page type/template item (`phase-3-checkout-product-family-contract-20260510.json:119-126`).
- The artifact reports `ok: true`, `rolled_back: true`, and zero survivor Customers/Sales Orders/Sales Invoices (`phase-3-checkout-product-family-contract-20260510.json:134-140`).
- The verifier itself is rollback-only and states it proves cart/checkout, submitted Sales Order rows, and copied Sales Invoice rows (`checkout_product_family_contract.py:3-8`).
- Runtime has explicit Sales Order Item line field generation and Sales Invoice Item copying (`product_page_runtime.py:326-379`, `product_page_runtime.py:469-473`).

Verdict: Strong runtime-fixture proof for first checkout-family preservation. It is not import/reupload proof and should stay serial because it creates records inside a rollback transaction (`checkout_product_family_contract.py:60-82`, `checkout_product_family_contract.py:490-523`).

### PASS — Phase 4 quote/event boundary proof covers all current non-checkout fixtures

Durable Phase 4 artifact covers the claimed non-checkout boundary:

- 38 total blocked current non-checkout fixture candidates through cart API / direct checkout URL / stale localStorage: `cart_api_blocked_count: 38`, `direct_checkout_url_blocked_count: 38`, `stale_localstorage_blocked_count: 38` (`phase-4-quote-event-checkout-boundary-contract-20260510.json:2`, `:48`, `:811`).
- The 38 split is 33 quote-first + 5 needs-review (`phase-4-quote-event-checkout-boundary-contract-20260510.json:55`, `:219`).
- Malformed JSON and old-schema payloads are now blocked (`phase-4-quote-event-checkout-boundary-contract-20260510.json:49-53`).
- Record count deltas are empty and rollback is true (`phase-4-quote-event-checkout-boundary-contract-20260510.json:809-810`).
- The verifier checks stored contract, runtime context, no checkout add-ons, cart API, direct checkout URL, stale localStorage, malformed/non-list JSON, old schema, and no-sellable synthetic paths (`quote_event_checkout_boundary_contract.py:228-461`).

Verdict: Strong fixture proof for quote/event/non-checkout safety. It proves current rows cannot sneak into paid checkout through the tested surfaces.

### PASS — Public ecommerce remains intentionally paused, and architecture readiness separates technical readiness from reopen readiness

- `capabilities/recipes/erpnext-ecommerce-receiving-architecture.md` says current local/public posture is paused with `lt_ecommerce_paused=1`, and `technical_architecture_ok: true` may coexist with `import_reopen_ok: false` because public reopen is blocked by config (`capabilities/recipes/erpnext-ecommerce-receiving-architecture.md:239-258`).
- `product_page_architecture_readiness.py` computes `technical_architecture_ok` separately from `import_reopen_ok`, with `public_ecommerce_reopen` blocked when paused (`product_page_architecture_readiness.py:55-79`, `product_page_architecture_readiness.py:311-323`).
- Goal progress records the same split: technical architecture true, import reopen false, blocked only on public ecommerce pause (`ready-to-order-ecommerce-goal-progress-2026-05-10.md:69`, `:87-89`, `:236-247`).

Verdict: This boundary is correctly represented in code/docs. Do not collapse “architecture ready” into “public/import reopen ready.”

### CONCERN — Some Phase 4 prose is stale relative to the durable JSON

`phase-4-quote-event-path-hardening-result-2026-05-10.md` says malformed/stale-schema config coverage was outside the Phase 4 artifact (`phase-4-quote-event-path-hardening-result-2026-05-10.md:119`), but the durable Phase 4 JSON now includes malformed/non-list/old-schema blocking (`phase-4-quote-event-checkout-boundary-contract-20260510.json:49-53`).

Recommendation: update or supersede the stale prose before using that doc as client/status evidence. The JSON and verifier are fresher than that paragraph.

### CONCERN — Current proof is heavily runtime-fixture proof, not import/reupload proof

The architecture recipe now states the corrected contract clearly: current ERPNext products are test fixtures only, and future import/reopen work must prove controlled purge/reupload/import field population, cascading/dependency preservation, and automation triggers (`capabilities/recipes/erpnext-ecommerce-receiving-architecture.md:44-58`). The product cut plan repeats this correction and says the plan is not permission to trust/preserve current product records as final catalog truth (`ready-to-order-product-cut-plan-2026-05-10.md:10`, `:103`).

Fixture proofs currently cover:

- Stored fields on existing 53 Website Items.
- Runtime checkout/quote/needs-review behavior for those rows.
- Rollback-safe Sales Order / Sales Invoice meaning preservation for selected checkout fixtures.
- Fail-closed stale/malformed cart and direct-checkout paths for current non-checkout fixtures.

Missing for import/reupload:

- Source packet to imported Item/Website Item identity mapping.
- Automated creation/population of `lt_product_page_type` and `lt_commerce_lane` during import.
- Cascading/dependency/add-on/price/media fields created from source, not hand-applied fixture state.
- Post-import rerun proving the new records, not the current 53, satisfy the same runtime boundaries.

### BLOCKER — Future purge/reupload/import is not yet serial-gated

This is not a blocker to closing Phase 1-4 as fixture/runtime safety. It is a blocker to trusting any future catalog import/reopen.

Required future serial gates before treating a new catalog as real:

1. `scripts/verify/product_import_preflight_contract.py` — read-only source packet check: product identities, template type, commerce lane, required fields, dependency/add-on/price/media destinations.
2. `scripts/verify/product_import_dry_run_mapping_contract.py` — proves import would populate `Website Item.lt_product_page_type`, `Website Item.lt_commerce_lane`, structured option/dependency/add-on fields, pricing/media references, and fail-loud review rows without DB mutation.
3. Parent-approved destructive gate only after preflight: `scripts/verify/product_purge_reupload_serial_contract.py` — serial, explicit approval, snapshot/rollback plan, no parallel agents.
4. `scripts/verify/post_import_website_item_classification_contract.py` — reruns the Phase 2 classification expectations against the newly imported records, not the old 53 fixtures.
5. `scripts/verify/post_import_checkout_family_contract.py` — reruns the Phase 3 checkout-family preservation against the imported launch shelf.
6. `scripts/verify/post_import_quote_event_boundary_contract.py` — reruns the Phase 4 boundary against every imported quote-first / needs-review / no-sellable row.
7. `scripts/verify/post_import_ecommerce_pause_contract.py` — proves public shop/cart/checkout are still paused after import unless explicitly opened for a temporary proof and then restored.

These names are recommendations mapped to existing verifier boundaries: classification, checkout-family preservation, quote/event blocking, and pause-mode safety.

### QUESTION — Seasonal/simple products need owner policy before becoming launch shelf truth

Phase 3 includes Mother's Day and Easter Balloon Cups entries in the artifact (`phase-3-checkout-product-family-contract-20260510.json:110`, `:126`), while the cut plan says Mother's Day should be held unless seasonal and Easter Balloon Cups deferred pending seasonal approval (`ready-to-order-product-cut-plan-2026-05-10.md:30-83`).

Question for owner/GL before import/reopen: should seasonal products be imported as hidden/needs-review, quote-first, or checkout-disabled until their season window?

### CONCERN — Rollback verifiers are not parallel-safe operationally

The rollback proofs are good evidence, but Phase 3 and similar checkout/order verifiers still create business records inside a transaction before rolling back. The verifier intercepts commits and performs rollbacks (`checkout_product_family_contract.py:60-82`), then checks generated records did not survive (`checkout_product_family_contract.py:596-597`; durable artifact `phase-3-checkout-product-family-contract-20260510.json:135-140`). Phase 4 also patches commit and rolls back (`quote_event_checkout_boundary_contract.py:44-60`).

Recommendation: keep these parent-serial only. Do not run them concurrently with purge/import, live checkout, or other agents creating Customers, Leads, Quotations, Sales Orders, Payment Requests, Invoices, Email Queue rows, Files, or Communications.

## 4. Runtime fixture proofs vs import/reupload proofs

| Claim | Current proof type | Evidence | Import/reupload status |
|---|---:|---|---|
| 53 current products have intended page/lane fields | Runtime fixture / current DB rows | `website_item_classification_contract.py:96-100`; progress `ready-to-order-ecommerce-goal-progress-2026-05-10.md:63-65` | Not proven for future imported rows |
| Paid checkout requires explicit `simple_product|checkout` | Code/static + runtime verifier artifact | `product_page_runtime.py:236-276`; Phase 4 JSON `:49-53` | Import must prove fields are populated correctly |
| Quote-first/needs-review cannot enter checkout | Runtime fixture proof | Phase 4 JSON `:2`, `:48-55`, `:809-811` | Must rerun after import against all new rows |
| Checkout-family configuration survives Sales Order and Sales Invoice | Runtime fixture rollback proof | Phase 3 JSON `:119-140`; `product_page_runtime.py:326-379`, `:469-473` | Must rerun against imported launch shelf |
| Public ecommerce paused | Config/runtime proof | `ecommerce_pause.py:35-37`; architecture recipe `:239-258` | Must prove still paused after import/reopen work |
| Cascading/dependency/source media/price import quality | Partial architecture/verifier scaffolding | required gates in recipe `:260-285`, future pattern `:352-365` | Not yet proven by controlled import |

## 5. Specific missing proof for future purge/reupload/import

Before a destructive product purge/reupload/import, require direct proof that:

- Every imported product has a source identity and desired destination identity before mutation.
- Every imported Website Item receives `lt_product_page_type` and `lt_commerce_lane` from source/mapping logic, not hand-fixup.
- Products not fitting checkout schema are imported as `quote_first` or `needs_review`, never inferred into checkout.
- Cascading options/dependency matrices are source-backed and executable in backend logic, matching the recipe gates for destination existence and reachability (`capabilities/recipes/erpnext-ecommerce-receiving-architecture.md:260-285`).
- Add-ons have backend pricing/eligibility, not just frontend cards; runtime already blocks missing/mispriced checkout add-ons (`product_page_runtime.py:409-430`, `:563-603`).
- Media/gallery mappings use source-backed classification and do not make missing variant images a blanket blocker where the source has no image requirement (`capabilities/recipes/erpnext-ecommerce-receiving-architecture.md:44-58`).
- Post-import checkout/quote/pause verifiers run serially and prove record count deltas/rollback behavior before any public open.

## 6. Verifier gaps / recommended new verifier names

Add these as thin wrappers around existing contracts rather than broad new suites:

- `scripts/verify/product_import_preflight_contract.py`
- `scripts/verify/product_import_dry_run_mapping_contract.py`
- `scripts/verify/product_purge_reupload_serial_contract.py`
- `scripts/verify/post_import_website_item_classification_contract.py`
- `scripts/verify/post_import_checkout_family_contract.py`
- `scripts/verify/post_import_quote_event_boundary_contract.py`
- `scripts/verify/post_import_ecommerce_pause_contract.py`
- `scripts/verify/product_import_automation_trigger_contract.py` — proves expected Lead/Quotation/Sales Order/operator automation hooks are installed for imported products without sending customer messages.

## 7. Bottom line

Phase 1-4 can be treated as PASS for the current ecommerce receiving ecosystem boundary: explicit checkout allowlist, quote/event fail-closed behavior, checkout-family backend preservation, rollback evidence, and paused public ecommerce are all supported by direct witnesses.

Do not treat Phase 1-4 as catalog import/reopen PASS. The next catalog-truth step is a controlled, serial, approval-gated purge/reupload/import proof that recreates the same Website Item contracts and backend preservation from source/mapping logic, then reruns the Phase 2-4 verifiers against the new records.
