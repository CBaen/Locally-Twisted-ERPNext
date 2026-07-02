D:2026-05-10 | Check:GL 22:18 correction + local Phase 1-4 proof state | Confidence:[LOCAL-PROOF]
# Phase 1-4 ecommerce/shop deep audit brief

> 2026-05-11 count correction: this audit was written before the final all-enabled-SKU verifier. Treat any Phase 3 wording about sample/representative checkout-family proof, Easter deferral, or 27/28 order rows as superseded by `checkout-enabled-sku-parity-proof-2026-05-11.md` and `2026-05-10-2330-phase-1-4-shop-audit/checkout-product-family-all-skus-final.json`: 15 checkout Website Item families/pages, 47 enabled sale SKUs, 39 add-on rows, 86 Sales Order/Sales Invoice rows, rollback clean. Public ecommerce still remains paused.

## Purpose

Run a deep, separated-lens audit of Locally Twisted ready-to-order ecommerce Phases 1-4 after GL corrected the product-import frame.

This audit must answer: are Phases 1-4 genuinely safe as a receiving ecosystem, and what must be proven before a future purge/reupload/import can be trusted?

## Current GL correction

Current ERPNext products are **test products only**. Do not treat the 53 current products as final catalog truth.

Future ecommerce/shop proof must include a controlled purge/reupload/import path showing that products fitting the LT schema:

- populate the right Website Item/custom fields,
- preserve product page type and commerce lane classifications,
- use cascading option/dependency information correctly,
- preserve backend cart/order/invoice/quote meaning,
- trigger intended automations and fail loudly when they cannot.

Do **not** run a purge/reupload in this audit. Destructive product import/purge requires a fresh preflight, rollback plan, and explicit approval.

## Non-negotiable boundaries

- Worktree: `/home/guidingl/projects/Built_by_Cameron/_CLIENTS/locally-twisted`.
- Branch rule: `main` only. Do not create branches.
- Do not commit, push, stage, reset, purge, reimport, mutate catalog_data, open public ecommerce, process live payments, or send real customer messages.
- Public ecommerce stays paused with `lt_ecommerce_paused=1`.
- Use current products only as test fixtures.
- Rollback/Frappe DB verifiers are not parallel-safe. Audit agents should avoid DB-mutating verifiers. Parent will run serial gates.
- If you run anything, prefer read-only/static checks. If a command might create Customers, Leads, Quotations, Sales Orders, Payment Requests, Invoices, Email Queue rows, Files, or Communications, do not run it; instead list it as a parent serial verification need.
- Write exactly one audit artifact in `workstreams/ecommerce-audit/` and do not modify production code.

## Current Phase state to audit

Phase 1 — verifier foundation:
- checkout fulfillment verifier repaired;
- customer note checkout preservation verifier passes rollback-safe;
- payment cascade/customer-note gates exist.

Phase 2 — Website Item classification:
- target counts: 15 checkout-after-small-fix, 33 quote-first, 5 hide/needs-review;
- stored fields: `Website Item.lt_product_page_type`, `Website Item.lt_commerce_lane`;
- current records are test fixtures, so audit must identify what import/reupload would need to prove.

Phase 3 — first checkout product family proof:
- 13 bouquet-family pages are proven as the scoped first checkout family;
- Mother's Day simple path has proof but should be held unless seasonal;
- Easter Balloon Cups deferred pending seasonal approval;
- selected options/add-ons/customer note must preserve through cart, Sales Order, invoice, and operator view.

Phase 4 — quote/event boundary hardening:
- direct paid checkout requires explicit `simple_product|checkout`;
- blank/partial/inferred/quote-first/needs-review states fail closed;
- latest parent serial proof: 33 quote-first + 5 needs-review products blocked through product controls, cart API, direct checkout URL, stale localStorage, malformed/old payloads, and no-sellable candidate paths;
- rollback created no business records.

## Current proof commands already rerun by parent

Latest serial evidence before this audit:

```text
python -m py_compile apps/.../product_page_runtime.py apps/.../api/cart.py apps/.../www/checkout.py apps/.../verify/quote_event_checkout_boundary_contract.py scripts/verify/quote_event_checkout_boundary_contract.py
python scripts/verify/quote_event_checkout_boundary_contract.py                         PASS
python scripts/verify/product_page_runtime_contract.py                                  PASS
python scripts/verify/checkout_product_family_contract.py                               PASS
python scripts/verify/checkout_fulfillment_contract.py                                  PASS
python scripts/verify/customer_note_checkout_preservation_contract.py                    PASS
python scripts/verify/ecommerce_pause_contract.py                                       PASS after reverting paused product-search leakage
python scripts/verify/smoke_shop.py                                                     PASS in paused mode
python scripts/verify/nav_ia.py                                                         PASS
```

## Important files

Code / runtime:
- `apps/locally_twisted/locally_twisted/product_page_runtime.py`
- `apps/locally_twisted/locally_twisted/product_options.py`
- `apps/locally_twisted/locally_twisted/commerce_rules.py`
- `apps/locally_twisted/locally_twisted/api/cart.py`
- `apps/locally_twisted/locally_twisted/www/checkout.py`
- `apps/locally_twisted/locally_twisted/public/js/lt-guest-cart.js`
- product templates under `apps/locally_twisted/locally_twisted/templates/generators/item/`

Verifiers:
- `scripts/verify/product_page_runtime_contract.py`
- `scripts/verify/website_item_classification_contract.py`
- `scripts/verify/checkout_product_family_contract.py`
- `scripts/verify/checkout_fulfillment_contract.py`
- `scripts/verify/customer_note_checkout_preservation_contract.py`
- `scripts/verify/quote_event_checkout_boundary_contract.py`
- `scripts/verify/ecommerce_pause_contract.py`
- `scripts/verify/product_page_architecture_readiness.py`

Docs/artifacts:
- `workstreams/ecommerce-audit/README.md`
- `workstreams/ecommerce-audit/ready-to-order-ecommerce-goal-progress-2026-05-10.md`
- `workstreams/ecommerce-audit/ready-to-order-product-candidate-list-2026-05-10.md`
- `workstreams/ecommerce-audit/ready-to-order-product-cut-plan-2026-05-10.md`
- `workstreams/ecommerce-audit/phase-4-quote-event-path-hardening-result-2026-05-10.md`
- `workstreams/ecommerce-audit/phase-4-quote-event-checkout-boundary-contract-20260510.json`
- `workstreams/erpnext-ecommerce-receiving-architecture.md`
- `capabilities/recipes/erpnext-ecommerce-receiving-architecture.md`
- `locally-twisted-decisions.md`
- `locally-twisted-queue.md`

## Output artifact requirements

Write a concise but deep artifact with:

1. Scope and lens.
2. What you inspected.
3. Findings by severity: PASS / CONCERN / BLOCKER / QUESTION.
4. Evidence with file paths and, when possible, line references.
5. Specific missing proof for future purge/reupload/import.
6. Any verifier gaps or recommended new verifier names.
7. No generic advice; every recommendation must map to LT code/docs/verifiers.
