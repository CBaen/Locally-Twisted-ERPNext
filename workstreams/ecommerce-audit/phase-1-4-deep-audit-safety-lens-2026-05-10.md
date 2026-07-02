D:2026-05-10 | Check:local source/docs static audit 2026-05-10 | Confidence:[LOCAL-PROOF]
# Phase 1-4 ecommerce/shop deep audit — adversarial safety lens

> 2026-05-11 count correction: this audit was written before the final all-enabled-SKU verifier. Treat any Phase 3 wording about sample/representative checkout-family proof, Easter deferral, or 27/28 order rows as superseded by `checkout-enabled-sku-parity-proof-2026-05-11.md` and `2026-05-10-2330-phase-1-4-shop-audit/checkout-product-family-all-skus-final.json`: 15 checkout Website Item families/pages, 47 enabled sale SKUs, 39 add-on rows, 86 Sales Order/Sales Invoice rows, rollback clean. Public ecommerce still remains paused.

## 1. Scope and lens

Adversarial read-only audit of Phases 1-4 as a receiving ecosystem, with current ERPNext products treated only as test fixtures per `workstreams/ecommerce-audit/phase-1-4-deep-audit-brief-2026-05-10.md:12-14`.

Primary bypass questions checked:

- Can quote-first / needs-review products enter paid checkout through product controls, cart API, direct `/checkout?item=...`, malformed payloads, or stale localStorage?
- Do blank, partial, or inferred `Website Item` fields fail closed rather than infer checkout?
- Does paused public ecommerce prevent public shop/cart/checkout purchase paths while `lt_ecommerce_paused=1`?
- What would a future purge/reupload/import need to prove so it does not weaken the current contract?

No DB-mutating verifiers, purge/reupload/import, catalog_data mutation, public ecommerce opening, payment processing, commits, staging, or pushes were run. I only performed static/code/doc inspection plus `git rev-parse --abbrev-ref HEAD` (`main`).

## 2. What I inspected

- Brief and phase evidence:
  - `workstreams/ecommerce-audit/phase-1-4-deep-audit-brief-2026-05-10.md`
  - `workstreams/ecommerce-audit/ready-to-order-ecommerce-goal-progress-2026-05-10.md`
  - `workstreams/ecommerce-audit/phase-4-quote-event-path-hardening-result-2026-05-10.md`
  - `capabilities/recipes/erpnext-ecommerce-receiving-architecture.md`
- Runtime and API code:
  - `apps/locally_twisted/locally_twisted/product_page_runtime.py`
  - `apps/locally_twisted/locally_twisted/product_options.py`
  - `apps/locally_twisted/locally_twisted/api/cart.py`
  - `apps/locally_twisted/locally_twisted/www/checkout.py`
  - `apps/locally_twisted/locally_twisted/public/js/lt-guest-cart.js`
- Product templates:
  - `apps/locally_twisted/locally_twisted/templates/generators/item/item_details.html`
  - `apps/locally_twisted/locally_twisted/templates/generators/item/item_quote_first.html`
  - `apps/locally_twisted/locally_twisted/templates/generators/item/item_configure.html`
- Verifiers:
  - `apps/locally_twisted/locally_twisted/verify/website_item_classification_contract.py`
  - `apps/locally_twisted/locally_twisted/verify/quote_event_checkout_boundary_contract.py`
  - `apps/locally_twisted/locally_twisted/verify/product_page_architecture_readiness.py`
  - `scripts/verify/ecommerce_pause_contract.py`
  - `scripts/verify/website_item_classification_contract.py`
  - `scripts/verify/quote_event_checkout_boundary_contract.py`
  - `scripts/verify/product_page_architecture_readiness.py`

## 3. Findings by severity

### PASS — explicit checkout allowlist is fail-closed

Paid checkout requires explicit `simple_product|checkout`; inferred checkout is not enough.

Evidence:

- `product_page_runtime.py:236-270` resolves field combinations. It allows checkout only at `product_page_runtime.py:252`, returns `needs_review|needs_review` for explicit needs-review/partial needs-review at `product_page_runtime.py:258`, blocks partial checkout without simple page type, and blocks inferred checkout at `product_page_runtime.py:270`.
- `quote_event_checkout_boundary_contract.py:111-168` directly asserts blank, partial, inferred, explicit checkout, and explicit quote-first precedence cases.
- Parent durable result records the same contract precedence proof in `phase-4-quote-event-path-hardening-result-2026-05-10.md:84-93`.

Safety impact: a future imported Website Item with blank fields, a lone checkout lane, or group-based checkout hints should not become purchasable by accident.

### PASS — product page controls separate quote/review from checkout controls

Quote-first and needs-review product pages render the quote CTA partial, not the add-to-cart partial.

Evidence:

- `item_details.html:64-71` sends `is_quote_first` or `needs_review` to `item_quote_first.html`, sends ready-to-order variants to `item_configure.html`, sends ready-to-order singles to `item_add_to_cart.html`, and falls back to quote-first.
- `item_quote_first.html:191-194` stores a `needs_operator_review: true` handoff payload in `sessionStorage` as `lt_product_quote_handoff_v1`.
- `quote_event_checkout_boundary_contract.py:170-200` asserts the quote partial markers and forbids checkout/cart markers in the quote-first partial.

Safety impact: polished product UI does not by itself create a checkout path for complex/event products.

### PASS — cart API blocks quote-first / needs-review and ignores client-side price truth

The server re-resolves item status and price. Client localStorage can request a line, but cannot authorize sale or price.

Evidence:

- `api/cart.py:108-112` gets the Website Item runtime contract and returns `quote_required` unless `commerce_lane == checkout`.
- `api/cart.py:156-266` accepts client cart entries, normalizes configuration, resolves each line server-side, and reports missing/blocked rows instead of returning saleable lines.
- `api/cart.py:278-312` builds visible base/add-on display lines from server-resolved Item Price/add-on runtime, not client price fields.
- `quote_event_checkout_boundary_contract.py:321-331` asserts quote/review sellable candidates fail as `quote_required` through cart API.

Safety impact: stale or hand-edited `lt_cart` entries cannot convert a quote product into a purchasable cart row.

### PASS — checkout submit and preview have an early paused-commerce guard

Direct checkout APIs are guarded before resolving cart items or creating records while ecommerce is paused.

Evidence:

- `checkout.py:663-704` defines `_assert_checkout_api_open()` and returns HTTP 403 customer-safe pause payload when paused.
- `checkout.py:714-724` calls the pause guard in `preview_checkout_totals` before `_resolve_cart_items` / `_resolve_sale_lines`.
- `checkout.py:750-793` calls the pause guard in `submit_guest_order` before customer validation, cart resolution, Customer/Contact/Address/Sales Order/Payment Request/Stripe work.
- `scripts/verify/ecommerce_pause_contract.py:122-154` statically checks this guard order against mutation markers.
- `scripts/verify/ecommerce_pause_contract.py:249-276` posts to checkout APIs and verifies 4xx pause errors plus unchanged purchase/order record counts.

Safety impact: even a direct POST to the whitelisted guest checkout methods should not create Customer, Contact, Address, Sales Order, Payment Request, or Stripe records while `lt_ecommerce_paused=1`.

### PASS — malformed / stale cart configuration fails loudly server-side

Configuration payloads must be parseable, current-schema, bounded JSON.

Evidence:

- `product_page_runtime.py:139-181` validates optional cart configuration and throws customer-safe validation errors for malformed JSON, non-dict data, wrong schema version, unserializable values, and oversize payloads.
- `product_page_runtime.py:165-172` specifically blocks older option formats.
- `checkout.py:434-487` normalizes `items_json` through `cart_line_key()`, which calls the same configuration normalizer.
- `quote_event_checkout_boundary_contract.py:379-424` asserts malformed JSON, non-list JSON, and old-schema configurations fail before sale-line resolution.

Safety impact: stale localStorage is not trusted as an implicit downgrade path.

### PASS — Sales Order / invoice product meaning preservation is present for checkout path

Selected options and approved add-ons are written onto line-level custom fields and copied to invoice lines.

Evidence:

- `product_page_runtime.py:321-369` builds Sales Order Item custom fields with schema version, template Website Item, page type, lane, selected variant options, add-ons, and JSON summary.
- `product_page_runtime.py:469-488` copies line configuration from Sales Order Item to Sales Invoice Item.
- `checkout.py:494-565` resolves sale lines, calls `sales_order_line_configuration_fields()`, adds validated add-on lines, and builds server-priced Sales Order rows.
- Parent phase evidence says `checkout_product_family_contract.py` passed with Sales Order/Sales Invoice preservation and rollback in `ready-to-order-ecommerce-goal-progress-2026-05-10.md:106-121`.

Safety impact: the first checkout product family is not merely UI-proven; line meaning has backend preservation evidence.

### PASS — quote-first / needs-review boundary has row-level verifier coverage for current fixtures

The current 33 quote-first + 5 needs-review products have direct boundary proof.

Evidence:

- Classification constants list 15 checkout candidates, 33 quote-first, and 5 needs-review products in `website_item_classification_contract.py:19-101`.
- `quote_event_checkout_boundary_contract.py:64-89` runs precedence, product template, quote-first, needs-review, malformed/stale, and no-candidate assertions.
- `quote_event_checkout_boundary_contract.py:205-244` applies cart API, direct checkout URL, stale localStorage, and no-add-on exposure checks per item.
- Durable parent result records `quote_first_count: 33`, `needs_review_count: 5`, `cart_api_blocked_count: 38`, `direct_checkout_url_blocked_count: 38`, `stale_localstorage_blocked_count: 38`, `record_count_deltas: {}`, and rollback in `phase-4-quote-event-path-hardening-result-2026-05-10.md:56-73`.

Safety impact: the current test fixture set does not show a quote/event checkout bypass in the scoped paths.

### PASS — public ecommerce remains intentionally paused and treated as a reopen blocker

The system distinguishes technical architecture from public ecommerce readiness.

Evidence:

- Brief requires public ecommerce paused at `phase-1-4-deep-audit-brief-2026-05-10.md:29`.
- `product_page_architecture_readiness.py:67-72` sets `ok` equal to `import_reopen_ok`, not just `technical_architecture_ok`.
- `product_page_architecture_readiness.py:311-320` marks `public_ecommerce_reopen` blocked when ecommerce is paused.
- Phase progress records `technical_architecture_ok: True`, `import_reopen_ok: False`, blocked only on `public_ecommerce_reopen` pause in `ready-to-order-ecommerce-goal-progress-2026-05-10.md:87-89`.
- `ecommerce_pause_contract.py:190-276` verifies paused route behavior and direct checkout API blocks.

Safety impact: passing Phase 1-4 gates cannot be mistaken for permission to open the public shop.

### CONCERN — future purge/reupload/import is not yet proven by the current named-record classifier

The current classifier is safe for the 53 test fixture Website Items, but it is identity-list based. A purge/reupload could recreate different Website Item names, omit fields, alter routes, change item codes, or split/merge products while still leaving the runtime code intact. The current Phase 2 verifier proves today’s fixture values, not that the future importer populates correct fields for every source product.

Evidence:

- Brief explicitly says current products are test products only and future proof must include controlled purge/reupload/import at `phase-1-4-deep-audit-brief-2026-05-10.md:12-22`.
- `website_item_classification_contract.py:19-101` hard-codes the 53 current item codes and expected counts.
- `website_item_classification_contract.py:280-282` builds desired rows from those fixed tuples.
- Phase progress says Phase 2 parent proof was `53 matched`, `0 planned changes`, and stored counts for the current records in `ready-to-order-ecommerce-goal-progress-2026-05-10.md:24`.

Required missing proof before future purge/reupload/import:

- Add a source-to-ERPNext post-import gate, recommended name: `scripts/verify/product_import_receiving_contract.py`.
- It must compare source product identity -> Website Item -> Item/variant -> Item Price -> page type/lane -> route -> published state -> required fields.
- It must fail if any imported product has blank/invalid `lt_product_page_type` or `lt_commerce_lane`, duplicate Website Item identity, missing Website Item, missing route, unexpected published state, or mismatched source classification.

### CONCERN — current no-sellable-candidate proof is synthetic, not importer-wide

The boundary verifier proves the behavior for a synthetic missing item and reports all current quote/review fixtures have a sellable candidate. That is enough for current bypass checks, but not enough for future imported products with partial Item/Website Item creation.

Evidence:

- `quote_event_checkout_boundary_contract.py:426-489` uses `__lt_phase4_no_sellable_candidate__` as the no-candidate case.
- Durable result reports `no_sellable_candidate_count: 0` for real rows and a synthetic no-candidate object in `phase-4-quote-event-path-hardening-result-2026-05-10.md:61-70`.

Required missing proof before future purge/reupload/import:

- Extend `product_import_receiving_contract.py` or add `scripts/verify/product_import_sellable_candidate_contract.py`.
- For every imported Website Item, assert exactly the intended sellable candidate shape: template-vs-variant relation, disabled state, `has_variants`, Item Price coverage for checkout lines, and quote/no-sale behavior for non-checkout lines.

### CONCERN — corrupt client localStorage resets silently in the browser

This is not a checkout bypass because the server rejects malformed/stale payloads, but the browser cart engine currently drops corrupted cart JSON to an empty cart without a visible customer notice. If public ecommerce opens, that can look like a silent disappearance of cart contents.

Evidence:

- `lt-guest-cart.js:64-98` catches corrupted localStorage JSON, logs to console, and returns `emptyCart()`.
- Server-side malformed/stale proof exists in `product_page_runtime.py:139-181` and `quote_event_checkout_boundary_contract.py:379-424`.

Recommended verifier gap:

- Add `npm run test:cart-storage-recovery` or `scripts/verify/cart_storage_recovery_contract.py` to assert corrupted/stale localStorage shows a customer-safe notice and does not silently imply success.
- This is a UX/fail-loud concern, not a current paid-checkout bypass.

### CONCERN — paused route coverage is sample-based, not generated from all ecommerce routes/products

The pause verifier covers the main public ecommerce routes and one direct product checkout URL. That is useful, but a future import could create new product routes/category routes not in the static route list.

Evidence:

- `scripts/verify/ecommerce_pause_contract.py:28-39` defines a fixed `BLOCKED_ROUTES` sample list.
- `scripts/verify/ecommerce_pause_contract.py:190-213` asserts each listed route lands on `/ready-to-order-paused` in paused mode.
- The route list includes one product URL and one direct checkout URL, not all current/future Website Item routes.

Recommended verifier gap:

- Add `scripts/verify/ecommerce_pause_all_website_items_contract.py`.
- It should read all published Website Items/product routes in a read-only way and assert every product/category/shop/cart/checkout URL either redirects to the pause page in paused mode or, in controlled open mode, matches the intended ecommerce surface.

### QUESTION — future import classification source of truth needs one canonical artifact

The code safely enforces runtime fields, but the audit did not find one future-import artifact that is the canonical source for assigning every new product’s page type/lane after purge/reupload. The current verifier owns current tuples; the brief says future products must fit the LT schema and preserve lane classifications.

Evidence:

- Brief requires future products to “populate the right Website Item/custom fields” and “preserve product page type and commerce lane classifications” at `phase-1-4-deep-audit-brief-2026-05-10.md:14-18`.
- Current classification source is code tuple lists in `website_item_classification_contract.py:19-101`.

Decision needed:

- Before purge/reupload, choose whether source classification lives in a generated source contract JSON, importer mapping module, or ERPNext fixture packet.
- The verifier should consume that same artifact so classification proof is not duplicated manually in a test-only tuple list.

## 4. Specific missing proof for future purge/reupload/import

Before any destructive catalog purge/reupload/import, require a fresh preflight, rollback plan, and explicit approval, then prove at minimum:

1. `product_import_receiving_contract.py` — source product -> Website Item/Item/variant/route/fields parity, including required `lt_product_page_type` and `lt_commerce_lane`.
2. `product_import_sellable_candidate_contract.py` — each imported product has the intended sellable candidate shape or fails closed as no-sale/quote.
3. `product_import_checkout_lane_contract.py` — imported `simple_product|checkout` products can preserve selected options/add-ons/customer notes through cart, Sales Order, invoice, and operator view; imported `quote_first` / `needs_review` products cannot.
4. `ecommerce_pause_all_website_items_contract.py` — paused mode blocks every generated Website Item/category/shop/cart/checkout route, not only a static sample.
5. `cart_storage_recovery_contract.py` or browser test equivalent — corrupted/stale localStorage produces a customer-visible safe recovery notice.
6. Import report artifact — one canonical source-backed classification packet consumed by the importer and verifiers, not manually re-entered lists.

## 5. Bottom-line verdict

Phases 1-4 look safe for the current scoped receiving ecosystem and current test fixtures: checkout bypasses through product controls, cart API, direct checkout URL, stale/malformed cart payloads, quote-first/needs-review field states, and paused public checkout APIs are covered by code and durable verifier evidence.

The main safety gap is not today’s checkout boundary; it is future catalog churn. A purge/reupload/import could accidentally weaken safety unless the next proof layer verifies the importer’s produced Website Items, custom fields, sellable candidates, routes, prices, and pause behavior from source-backed import output rather than today’s 53 hard-coded fixture identities.
