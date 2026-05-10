D:2026-05-10 | Check:local runtime/source 2026-05-10 | Confidence:[LOCAL-PROOF]

# Product Page Backend Reconciliation Research Brief

Researcher contract: start any report/handoff with `D:YYYY-MM-DD | Check:<source/date> | Confidence:<label>`. Current source/runtime checks beat prior summaries. If no named artifact is written, the lane is `[NO EVIDENCE]`.

### 1. Want

Locally Twisted needs a credible answer for how to make ERPNext product records explicitly carry product-page behavior before any visual rebuild or broad catalog work continues. Success means a researcher can determine how `Website Item` records should store `lt_product_page_type` and `lt_commerce_lane`, how that should align with source catalog evidence, and how to verify that product page, cart, quote, checkout, Sales Order, and Sales Invoice behavior still preserve customer intent without relying on hidden fallback inference.

### 2. Have

Verified on 2026-05-10 in the local LT stack: `erpnext 15.105.0`, `frappe 15.106.0`, `locally_twisted 0.0.1`, `payments 0.0.1`, and `webshop 0.0.1` run in Docker at `http://localhost:8081`. The current codebase has backend/runtime ownership in `apps/locally_twisted/locally_twisted/product_page_runtime.py`, source classification in `apps/locally_twisted/locally_twisted/catalog_contract/source_builder.py`, field creation in `apps/locally_twisted/locally_twisted/seed/sync_commerce_rules.py`, and current audit evidence in `workstreams/ecommerce-audit/cart-checkout-intent-preservation-audit-2026-05-10.md`. Live DB verification shows 53 `Website Item` records, all currently stored as `lt_product_page_type=needs_review` and `lt_commerce_lane=needs_review`. Existing runtime inference still makes representative proof pages behave as quote-first or checkout, and the backend verifier suite has recently passed for product runtime, cart/checkout, quote review, quote acceptance, customer delivery, operator send control, dependency matrices, and intake parity.

### 3. Won't Accept

- Do not treat visual rendering as proof that backend plumbing is wired.
- Do not mark a product checkout-ready unless product classification, live variant resolution, and price behavior agree.
- Do not silently fall back from unknown or unsafe products into paid checkout.
- Do not bury a data migration inside Jinja templates, client JavaScript, or display-only code.
- Do not overwrite ERPNext catalog fields without a dry-run diff and rollback-safe verification.
- Do not rely on stale handoffs or audit packets as approval when current source code, DB state, or live site behavior contradict them.
- Do not expose internal field names, schema markers, or raw implementation labels to customers.
- Do not research only official docs; include credible ERPNext/Frappe/Webshop user reports, forum discussions, and operational patterns where they affect practical risk.

### 4. Open To

Research may recommend changing the field sync shape, adding a dedicated verifier, changing how source catalog contracts are persisted, tightening runtime fallback rules, splitting checkout-ready products from quote-first products in staged gates, or adding an operator review surface before bulk updates. The final approach should still fit the current Frappe app, ERPNext/Webshop override model, and fail-loud verification discipline.

### 5. Questions

1. In current ERPNext/Frappe/Webshop practice, what is the safest way to persist custom product-page behavior on `Website Item` while keeping storefront behavior, cart behavior, and backend order records consistent?
2. Should `lt_product_page_type` and `lt_commerce_lane` be synced from source catalog classification, from runtime inference, from an operator-approved review packet, or from a combined gate?
3. What exact evidence should be required before a product can move from `needs_review` to `checkout`, and what evidence is enough to move a product to `quote_first`?
4. How should the system handle products with incomplete prices, unclassified gallery/media, color customization axes, or review-only add-ons without blocking the whole catalog?
5. What verifier should fail if all stored `Website Item` records remain `needs_review`, while still allowing conservative quote-first operation for uncertain products?
6. What risks do ERPNext/Frappe users report around custom fields, Website Item overrides, cart customization, checkout mutation, and migrations that could affect this implementation?
7. What external examples or community patterns exist for preserving configured customer intent from product page through order/invoice records in ERPNext or similar commerce systems?
8. What rollback and audit evidence should exist before applying classification changes to all 53 products?
