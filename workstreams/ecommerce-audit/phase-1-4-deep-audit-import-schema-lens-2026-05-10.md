D:2026-05-10 | Check:local docs/source static audit 2026-05-10 | Confidence:[LOCAL-PROOF]
# Phase 1-4 deep audit — import/schema/automation builder lens

> 2026-05-11 count correction: this audit was written before the final all-enabled-SKU verifier. Treat any Phase 3 wording about sample/representative checkout-family proof, Easter deferral, or 27/28 order rows as superseded by `checkout-enabled-sku-parity-proof-2026-05-11.md` and `2026-05-10-2330-phase-1-4-shop-audit/checkout-product-family-all-skus-final.json`: 15 checkout Website Item families/pages, 47 enabled sale SKUs, 39 add-on rows, 86 Sales Order/Sales Invoice rows, rollback clean. Public ecommerce still remains paused.

## 1. Scope and lens

Scope: read-only/static audit of Locally Twisted ready-to-order ecommerce Phases 1-4 from the import/schema/automation builder lens after GL's 2026-05-10 correction that current ERPNext products are test fixtures only.

Non-scope: no branch, commit, push, staging, purge, reimport, catalog_data mutation, public ecommerce opening, live payment/customer messaging, or DB-mutating verifier execution.

Lens question: can a future controlled purge/reupload/import safely build the receiving ecosystem, not merely recreate product records?

## 2. What I inspected

- Brief and status: `workstreams/ecommerce-audit/phase-1-4-deep-audit-brief-2026-05-10.md`; `ready-to-order-ecommerce-goal-progress-2026-05-10.md`; `ready-to-order-product-cut-plan-2026-05-10.md`; Phase 2/3/4 result artifacts.
- Capability/architecture: `capabilities/recipes/erpnext-ecommerce-receiving-architecture.md`; `workstreams/erpnext-ecommerce-receiving-architecture.md`.
- Runtime/import/schema code: `product_page_runtime.py`; `product_options.py`; `product_quote_request.py`; `product_quote_runtime.py`; `lead_cascade.py`; `api/cart.py`; `www/checkout.py`; `seed/sync_commerce_rules.py`; `seed/seed_catalog.py`.
- Contract model/source code: `catalog_contract/models.py`; `catalog_contract/source_builder.py`; `catalog_contract/dependency_rules.py`.
- Product templates/JS: `templates/generators/item/item.html`; `item_details.html`; `item_configure.html`; `item_quote_first.html`; `public/js/lt-guest-cart.js`.
- Verifier wrappers/owners: `scripts/verify/website_item_classification_contract.py`; `scripts/verify/product_page_dependency_contract.py`; `scripts/verify/product_page_architecture_readiness.py` and related Frappe-side verifier references.

Commands run: `git rev-parse --abbrev-ref HEAD`; `git status --short`; targeted `rg`; file reads only. Branch was `main`. I did not run DB-mutating verifiers.

## 3. Findings by severity

### PASS — Phase 1-4 receiving runtime has real backend preservation points

Evidence:
- `apps/locally_twisted/locally_twisted/seed/sync_commerce_rules.py:145-159` defines `Website Item.lt_product_page_type` and `Website Item.lt_commerce_lane` as code-owned fields.
- `product_page_runtime.py:23-31` centralizes Website Item page/lane field names and downstream line payload fields.
- `product_page_runtime.py:190-281` resolves Website Item page/lane contracts fail-closed; Phase 4 docs confirm paid checkout now requires explicit `simple_product|checkout`.
- `www/checkout.py:434-553` resolves cart JSON into canonical configured lines, then calls runtime line/add-on builders before Sales Order creation.
- `product_page_runtime.py:377-457` builds Sales Order Item payloads and add-on lines; `product_page_runtime.py:459-484` copies line payloads to Sales Invoice rows.

Builder conclusion: the runtime destination for selected options/add-ons/page type exists. Future import should target this contract instead of relying on native ERPNext item/price/variant records alone.

### PASS — Quote-first/event lane has an automation path and record-level loud failure

Evidence:
- `templates/generators/item/item_details.html:57-73` routes quote-first/needs-review pages to `item_quote_first.html`, not checkout controls.
- `item_quote_first.html:181-190` writes a versioned product quote payload into session storage for `/contact` handoff.
- `product_quote_request.py:18-60` normalizes selected options, add-ons, customizations, and color recipes into a bounded payload.
- `lead_cascade.py:134-181` isolates Lead cascades and records backend failure evidence if product quote draft creation fails.
- `product_quote_runtime.py:45-108` creates an internal draft Quotation, preserves payload fields, and explicitly avoids submit/email/payment side effects.

Builder conclusion: intended automation triggers exist for the quote-first lane. A future import must prove source-driven quote-first pages generate payloads that survive Lead -> draft Quotation -> accepted draft Sales Order.

### PASS — Source contract layer can classify axes and build dependency matrices

Evidence:
- `catalog_contract/models.py:8-74` defines the product-page contract shape: page type, commerce lane, required axes, customization axes, add-ons, dependency matrices, gallery roles, and warnings.
- `catalog_contract/source_builder.py:138-221` builds `ProductPageContract` rows from source products, separating required axes, balloon-color customization axes, add-ons, warnings, gallery review, pricing evidence, and dependency matrices.
- `catalog_contract/dependency_rules.py:9-30` provides `available_options_for_selection()` and fails loudly on unknown or impossible selections.
- `scripts/verify/product_page_dependency_contract.py:61-151` explicitly checks Classic Arch/Unicorn dependency matrices and loud helper failures.

Builder conclusion: the source-side schema model is better than a flat import. It should become the required pre-import register for any purge/reupload.

### PASS — Current Phase 2/3/4 verifiers are narrow and useful for fixtures

Evidence:
- `verify/website_item_classification_contract.py:1-8` states it only updates the 53 named source-backed product-page records.
- Phase 2 artifact records exact stored counts: 15 `simple_product|checkout`, 33 `complex_custom_product|quote_first`, 5 `needs_review|needs_review`.
- Phase 3 artifact proves 13 bouquet-family checkout pages plus Mother's Day simple path under rollback, with Easter deferred.
- Phase 4 artifact proves 33 quote-first + 5 needs-review products are blocked from cart API, direct checkout URL, stale localStorage, malformed payloads, and no-sellable paths.

Builder conclusion: the fixture proofs are credible for the current receiving ecosystem. They are not by themselves a future import proof.

### BLOCKER — Current bulk import path does not build the Phase 2 classification contract

Evidence:
- `seed/seed_catalog.py:241-279` creates/updates Website Items, sets `published = 1`, route, descriptions, and images.
- The same `_upsert_website_item()` block has no assignment for `lt_product_page_type` or `lt_commerce_lane`.
- `seed/seed_catalog.py:391-421` imports product by product and commits each product, but never calls `build_product_page_contract()` or a source-backed classification writer.
- `verify/website_item_classification_contract.py:17-68` hard-codes the current 53 item codes and target lanes; it is not a source-derived import contract.

Impact: a real purge/reupload using the existing catalog seeder would recreate products as published Website Items without writing the LT page/lane schema. Public pause and Phase 4 fail-closed rules reduce customer danger, but the import itself would not prove the schema GL asked for.

Required before real catalog rebuild: a source-driven importer or pre-import register that writes/validates `lt_product_page_type` and `lt_commerce_lane` for every source row, blocks missing/ambiguous rows, and refuses publish/open if classifications are unset or stale.

### BLOCKER — No persistent import contract/register currently bridges source product meaning to ERPNext destinations

Evidence:
- `catalog_contract/models.py` and `source_builder.py` define an in-memory/source-derived contract shape.
- `seed/sync_commerce_rules.py` creates runtime custom fields and code-owned add-on Items, but not an ERPNext DocType/register for source slug -> Website Item -> page class -> axes/add-ons/dependencies/media/price/import action.
- `seed/seed_catalog.py` consumes `catalog.json`, `slug_to_group.json`, image files, variants, and prices, but does not persist the contract model or source evidence id alongside Website Items.
- `capabilities/recipes/erpnext-ecommerce-receiving-architecture.md:274-295` requires every destination to be executable and every missing/incomplete source concept to fail loudly.

Impact: after purge/reupload, there is no durable row-level witness that a product's source axes, dropped axes, add-ons, dependency matrix, price plan, media plan, and automation lane were intentionally mapped or held. That makes idempotent rebuild review too dependent on current fixture records and generated reports.

Required before real catalog rebuild: create either a committed import packet artifact consumed by the importer or an ERPNext review DocType/child table. Minimum columns: source slug/id, source evidence version, target Item, target Website Item, page type, commerce lane, required axes, customization axes/color axes, source add-on families, dependency matrix id/status, media plan, price plan, publish action, blocker status, and last import hash.

### CONCERN — Dependency matrices exist, but product-page UI does not yet consume them as the option source

Evidence:
- `product_options.py:18-25` pulls visible variant options from Webshop's `get_attributes_and_values()` and filters to required variant names.
- `item_configure.html:17-20` uses `get_variant_attribute_options()` plus checkout add-on options for ready-to-order rendering.
- `item_configure.html:452-456` sends selected options/add-ons in the cart payload.
- `catalog_contract/dependency_rules.py:9-30` owns executable dependency narrowing, but I did not find it wired into `item_configure.html` or `product_options.py` for public ready-to-order selectors.

Impact: Phase 3 is safe for one-axis bouquet fixtures and quote-first complex decor, but a future direct-checkout product with multiple dependent axes could display impossible combinations unless the Webshop selector/variant lookup catches them. That may still fail at add-to-cart, but it is not yet a clean dependency-matrix customer journey.

Required proof: direct checkout must remain limited to one-axis/simple fixtures until `available_options_for_selection()` or equivalent source-backed matrix logic drives the UI/server verifier for any multi-axis checkout candidate.

### CONCERN — Current Website Item classifier is fixture-specific, not import-idempotent

Evidence:
- `verify/website_item_classification_contract.py:17-68` encodes the 15/33/5 classification lists directly.
- `scripts/verify/website_item_classification_contract.py:56-77` can dry-run/apply/report those current records, but it is not parameterized by a future source packet.
- `phase-2-website-item-classification-result-2026-05-10.md` proves this was a safe targeted mutation for current records, not a general import schema contract.

Impact: if the source catalog changes, products are renamed, products are held/removed, or a future import uses a curated subset, the classifier can pass for old fixture identities while failing to prove the actual import set.

Required proof: a new source-driven classification verifier should compare every candidate source row to the intended ERPNext Website Item and fail on extra/missing/stale fixture rows.

### CONCERN — `seed_catalog.py` publishes every Website Item during import

Evidence:
- `seed/seed_catalog.py:254` and `seed/seed_catalog.py:271` set `wi.published = 1` for existing and new Website Items.
- The same import path does not check `lt_ecommerce_paused`, page/lane classification, price/media review status, or seasonal holds before publishing.
- The cut plan holds Easter/Mother's Day unless seasonal and treats current products as test fixtures.

Impact: public ecommerce pause currently prevents purchase exposure, but publication still affects browse/search/showroom behavior and can create review debt. A future purge/reupload should not publish by default; it should publish only rows whose contract and visibility state are approved for the current mode.

Required proof: import must distinguish `imported`, `published_showroom_quote`, `published_checkout`, and `hidden_needs_review` actions.

### CONCERN — Business-review clearances for testing are not final product approval

Evidence:
- `product_page_architecture_readiness.py:268-320` marks add-on, price, and media readiness PASS because GL cleared blocks for commerce-lane testing.
- `ready-to-order-product-cut-plan-2026-05-10.md` says current products are test products only and future product work must prove purge/reupload/import before catalog truth.
- Existing docs still name media/price/seasonality as remaining non-claims for public launch.

Impact: future import must not convert "cleared for testing" into final price/media/add-on approval.

Required proof: import/reopen gates should report these as explicit business approval states, not generic architecture passes.

### QUESTION — Where should the durable product import register live?

Options:
1. Committed JSON/MD packet consumed by import scripts, easiest to review and diff.
2. ERPNext custom DocType/register, better for operator review and Desk blockers.
3. Both: committed generated source packet plus ERPNext register rows created during dry-run/apply.

Recommendation: both, but start with a committed JSON packet and a read-only verifier. Add ERPNext register rows only when GL approves the next import implementation lane.

## 4. Specific missing proof for future purge/reupload/import

Before destructive catalog rebuild, prove all of these with current source data, not current ERPNext fixture records:

1. **Source-to-target identity**: every source slug has exactly one intended Item and Website Item target; every old fixture row is explicitly keep/update/hide/delete/recreate.
2. **Classification**: every imported Website Item gets `lt_product_page_type` and `lt_commerce_lane`; no product can be published/opened with blank/default `needs_review` unless intentionally hidden/review-only.
3. **Field/schema sync**: `sync_commerce_rules.execute()` and contact/product quote field sync have run in the target environment before import; custom fields exist on Website Item, Sales Order Item, Sales Invoice Item, Quotation, Quotation Item, Lead, and Sales Order acceptance surfaces.
4. **Required/custom/add-on separation**: required SKU axes, color customization axes, optional add-ons, review-only add-ons, and dropped/held axes are reported per source product.
5. **Dependency matrices**: source `valid_variants` become executable matrices over required axes, and any multi-axis checkout candidate has UI + server proof for impossible combinations.
6. **Price plan**: every checkout sale unit has a server-side Item Price; every quote-first/review-only unit cannot leak into checkout just because an Item Price exists.
7. **Media plan**: primary, variant, gallery, category/reference, and hold images are classified; no Website Slideshow/gallery claim from unclassified extra images.
8. **Automation triggers**: checkout products preserve payload to Sales Order/Invoice/operator view; quote-first products preserve payload to Lead, child quote rows, draft Quotation, and accepted draft Sales Order; failures create record-level evidence.
9. **Idempotency**: running dry-run twice produces the same plan; running apply twice produces no unplanned changes; interrupted import can resume without duplicate Website Items, variants, Item Prices, Files, quote-review Items, add-on Items, or publish-state drift.
10. **Pause/reopen mode**: import can run with public ecommerce paused; reopening is a separate explicit gate.

## 5. Verifier gaps / recommended new verifier names

Recommended parent-serial or read-only gates:

- `scripts/verify/product_import_schema_contract.py` — read-only source packet verifier: source slug -> target Item/Website Item/page type/lane/axes/add-ons/dependencies/media/price/import action.
- `scripts/verify/website_item_classification_from_source_contract.py` — replaces hard-coded 53-row fixture classifier for future imports; fails on missing/extra/stale current records.
- `scripts/verify/catalog_purge_reupload_plan_contract.py` — destructive-preflight only; proves purge/reupload plan, rollback inputs, counts, and paused-mode before any mutation.
- `scripts/verify/product_import_idempotency_contract.py` — dry-run/apply/resume proof for duplicate prevention and per-product hashes.
- `scripts/verify/product_dependency_ui_contract.py` — proves dependency matrices drive customer-visible choices for any multi-axis checkout product; keep direct checkout one-axis/simple until this passes.
- `scripts/verify/product_import_automation_cascade_contract.py` — parent-serial rollback-safe proof that imported checkout and quote-first rows trigger the intended Sales Order/Invoice/Lead/Quotation paths and record-level failures.
- `scripts/verify/product_publish_scope_contract.py` — proves import publish action respects paused ecommerce, seasonal holds, quote-first vs checkout lanes, and hidden/needs-review rows.

Existing verifiers to keep in the closeout suite after import implementation:

- `website_item_classification_contract.py` only for current fixture regression until replaced.
- `product_page_runtime_contract.py`
- `checkout_product_family_contract.py`
- `checkout_fulfillment_contract.py`
- `customer_note_checkout_preservation_contract.py`
- `quote_event_checkout_boundary_contract.py`
- `ecommerce_pause_contract.py`
- `product_page_architecture_readiness.py`
- `product_page_dependency_contract.py`
- add-on/price/media packet verifiers, with testing approvals separated from final business approval.

## 6. Bottom line

PASS for Phases 1-4 as a receiving-runtime fixture proof: the backend can preserve product meaning for the scoped bouquet checkout lane and fail-closed for quote/event/review lanes.

BLOCKED for real catalog rebuild/import: the current bulk import path does not write or verify the LT page/lane schema, does not persist a source-backed import register, and publishes Website Items without import-action approval. A future purge/reupload must be driven by a source contract packet plus idempotent import verifiers, not by the current 53 fixture records.
