D:2026-05-10 | Check:indexed memory + local repo/artifact readback + official ERPNext/Frappe docs fetched 2026-05-10 + static compile check 2026-05-10 | Confidence:[LOCAL-PROOF]

# Locally Twisted Ecommerce Infrastructure Research Synthesis

## Correction

The operative question is not “which products are ready?” It is whether the ERPNext/Frappe destination has a trustworthy ecommerce **receiving infrastructure** capable of preserving catalog_data-derived business meaning without silent loss.

A product matrix is a downstream audit view. It is not the architecture. The architecture is the contract layer, runtime preservation layer, quote/checkout bridges, record-level failure evidence, and verifier gates.

## Decision this answers

Can Locally Twisted safely continue building native ERPNext ecommerce infrastructure from catalog_data’s behavior witness without copying catalog_data code or pretending ERPNext Webshop alone is enough?

Answer: **yes for the infrastructure direction; no for any claim that native ERPNext alone solves the problem.** ERPNext/Frappe needs LT-owned infrastructure around Webshop before product import/reopen claims are safe.

## Evidence lanes

### 1. Indexed memory / prior conversation recall

- 2026-05-07 durable rule: fake data is allowed, fake success is not; every field/automation that can or should happen must either happen or fail loudly with record-level evidence. Source: `memory/2026-05-07.md#L4-L6`.
- 2026-05-08 catalog/product-page lane created contract-layer files and verifiers, but source contract audit was intentionally blocked by unresolved/import-hardening issues; no full catalog import readiness claim. Source: `memory/2026-05-08.md#L45-L52`.
- Project framing says this is a migration of business intent + catalog data into a fresh ERPNext install, not an automated catalog_data schema/module translation. Source: `.planning/PROJECT.md`.

### 2. Official ERPNext/Frappe docs checked 2026-05-10

- ERPNext Item Variants: a template item with variants is not directly transactional; only concrete variants are used in Sales Orders, Delivery Notes, invoices, etc.
- ERPNext Shopping Cart: non-variant items get direct add-to-cart; variant templates require a configure step; RFQ exists when checkout is disabled.
- ERPNext Item Price: price is an Item Price record tied to item, price list, UOM, validity, etc.; transaction pricing fetches from price lists.
- Frappe Child DocTypes: many-to-one structured detail belongs in child rows attached to parent docs, with parent/parenttype/parentfield/idx metadata.

Infrastructure implication: ERPNext gives sellable items, variants, item prices, cart, quotations, and child records. It does **not** natively preserve LT-specific configuration intent across custom decor flows. That must be LT infrastructure.

### 3. Existing LT research synthesis

`research/expedition-erpnext-ecommerce-receiving-architecture/research-synthesis.md` already asked the right infrastructure question:

> What backend product contract must LT add around ERPNext/Webshop so two product-page types can preserve option meaning, prices, add-ons, media, cart payloads, checkout totals, Sales Order lines, invoice meaning, fulfillment/operator meaning, and fail-loud reporting?

Its key finding remains right: the hard backend gap is **line-level preservation**. Header fulfillment fields and Website Item copy fields are not enough. Product configuration/add-on/customization meaning must survive into transactional records.

### 4. Current LT architecture capability

`capabilities/recipes/erpnext-ecommerce-receiving-architecture.md` states the core rule:

> Do not treat product transfer as the goal. ERPNext must first be able to safely receive products and integrate their meaning everywhere: backend fields, product template type, variant logic, add-on logic, cascading dependencies, dynamic pricing, media visibility, product pages, cart, checkout, Sales Order, invoice, fulfillment/operator meaning, desktop/mobile customer journeys, and fail-loud verifiers.

This is the right infrastructure frame.

### 5. Current code/artifact readback

Readback confirmed the infrastructure exists in these layers:

- `apps/locally_twisted/locally_twisted/product_page_runtime.py`
  - owns `lt-product-config-v1`, selected configuration validation, line field names, add-on eligibility, quote-first blocking, and customer-safe checkout errors.
- `apps/locally_twisted/locally_twisted/product_quote_runtime.py`
  - creates draft Quotations from product-page quote Leads, preserves payload on Quotation and Quotation Item, and explicitly does not submit/email/request payment/imply success.
- `apps/locally_twisted/locally_twisted/catalog_contract/*`
  - separates required axes, customization axes, add-ons, dependency matrices, media classification, price review, and source-backed contract construction.
- `apps/locally_twisted/locally_twisted/failure_recorder.py`
  - provides reusable record-level evidence for backend partial failures.
- `output/product-page-architecture-readiness-current.json`
  - existing read-only evidence says `technical_architecture_ok: true`, `import_reopen_ok: true`, 14 pass, 0 blocked, 1 deferred, generated 2026-05-10T07:38:02.958904.
- `output/business-automation-index.json`
  - existing read-only evidence says 30 business surfaces indexed, 12 required, 27 connected, 0 loud-failure gaps.

Important caveat: a fresh attempt to run `product_page_architecture_readiness.py` on 2026-05-10 failed before report generation because `bench execute` failed after CSS parser messages. That failure is **not** a product/business finding. It is a verification-environment blocker to resolve before using a fresh architecture report as current evidence.

### 6. Static verification run 2026-05-10

Ran:

```bash
python -m py_compile apps/locally_twisted/locally_twisted/product_page_runtime.py apps/locally_twisted/locally_twisted/product_quote_runtime.py apps/locally_twisted/locally_twisted/api/cart.py apps/locally_twisted/locally_twisted/www/checkout.py apps/locally_twisted/locally_twisted/verify/product_page_architecture_readiness.py
```

Result: passed with no output.

This only proves Python syntax/loadability for the inspected infrastructure files. It does not replace runtime verifier evidence.

## Infrastructure map

| Layer | Owner | Why it exists | Evidence |
|---|---|---|---|
| Source witness intake | catalog_data repo + audit artifacts | Capture mature ecommerce meaning without copying catalog_data implementation. | `external-catalog-data`, `catalog_data-source-commerce-map-2026-05-10.md` |
| Contract builder | `catalog_contract/source_builder.py` + models | Classify source concepts before they touch Webshop. | `catalog_contract/models.py`, `source_builder.py` |
| Product-page class labels | `product_page_labels.py` + Website Item custom fields | Store machine values, show operator-friendly labels. | readiness output: `two_reusable_template_types` pass |
| Runtime configuration payload | `product_page_runtime.py` | Version and validate selected meaning before cart/checkout/quote. | `CONFIG_VERSION = lt-product-config-v1` |
| Line-level preservation | SO Item / SI Item / Quotation Item custom fields | Preserve selected meaning beyond UI and cart. | readiness output: `line_level_order_invoice_preservation` pass |
| Ready-to-order path | cart API + checkout + add-on contracts | Server-priced checkout only where safe. | readiness output: `ready_to_order_internal_cart_checkout` pass |
| Quote-first path | Lead → draft Quotation → reviewed quote → draft Sales Order | Preserve complex customer intent without fake paid checkout. | readiness output: quote-first rows pass |
| Failure evidence | `failure_recorder.py` + business automation index | Backend partial failures must attach visible record-level evidence. | `business-automation-index.json` |
| Import/reopen gates | architecture readiness + source price/media/add-on packets | Prevent fake success before public/shop/customer exposure. | `product-page-architecture-readiness-current.json` |

## What native ERPNext handles vs what LT must own

### Native ERPNext can handle

- Concrete Items / Item Variants as transaction rows.
- Item Prices and price lists.
- Shopping cart flow and quotation path.
- Sales Orders, Sales Invoices, Quotation records.
- Custom Fields and Child DocTypes as storage extension points.

### LT infrastructure must own

- Product-page class decision: ready-to-order vs quote-first vs needs-review.
- Which source axes are required SKU axes vs customization vs add-on vs backend-only vs needs-review.
- Versioned customer configuration payloads.
- Add-on eligibility and line expansion.
- Server-side pricing resolver and safe customer error handling.
- Structured handoff from product page to Lead/Quotation/Sales Order/Sales Invoice.
- Quote-first no-payment/no-invoice/no-order side-effect boundaries.
- Record-level failure evidence when automation fails.
- Verifier gates that separate architecture proof from customer go-live proof.

## Current infrastructure verdict

### Strong evidence

- The correct architectural layer exists: LT-owned contract/runtime infrastructure around ERPNext/Webshop.
- The current design aligns with official ERPNext/Frappe constraints instead of fighting them.
- Prior synthesis, capability recipe, code readback, and existing readiness output converge: ERPNext native records are the base, LT custom layer preserves meaning.
- The direction avoids catalog_data code copying; catalog_data remains a witness for behavior/meaning.

### Not safe to claim yet

- Do not claim a fresh current architecture pass until the `bench execute` verifier failure is diagnosed and rerun cleanly.
- Do not claim public/customer ecommerce readiness from product rows or source packets alone.
- Do not treat `import_reopen_ok` in an existing output as sufficient without knowing the exact mode/config and GL-cleared-testing context.
- Do not purge/import/rebuild products until the infrastructure verifier, backup/export/import-contract, and public-state gates are clean in the intended mode.

## Concrete next actions

1. **Fix verification-environment blocker**: diagnose why fresh `product_page_architecture_readiness.py` cannot generate a report now. Do not downgrade this to “CSS warning noise” until the `bench execute failed` cause is proven.
2. **Create an infrastructure readiness packet, not a product packet**: one table of infrastructure gates, owners, verifier command, last evidence artifact, and current status.
3. **Re-run architecture verifier in intended ecommerce mode** after the blocker is fixed, writing a dated report under `output/`.
4. **Only then** use source/product matrices as downstream input to import/reopen planning.
5. Keep catalog_data read-only and treat catalog_data docs/source as behavior witness only.

## Bottom line

The business risk is not “bad product rows.” The business risk is silent loss of intent between page → cart/quote → checkout → Sales Order → invoice/operator workflow. The LT codebase already has the right infrastructure pattern to prevent that, but the current live proof must be refreshed cleanly before it is safe to tell GL/Jeff that ecommerce infrastructure is ready for the next launch step.
