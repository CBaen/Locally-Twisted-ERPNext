# Ecommerce Operator Hardening - Red Alarm Index

Date: 2026-06-30

Status: incident mapping and project start. This is not a live fix, not a publish approval, and not a claim that the live database is healthy.

## Why This Exists

The owner-facing expectation is simple: when a business owner changes a product's price, description, photos, options, add-ons, or visibility in the backend, the customer-facing shop should reflect the approved change quickly and consistently.

The current system does not provide that simple owner contract. A public product page can read one set of fields while the owner edits another. Variant selection, cart, checkout, Sales Order lines, invoice fields, gallery projection, and payment labels each re-resolve product data through separate paths. Some of those paths are deliberate safety gates. Some are incomplete owner workflow. Some are stale architecture scaffolding.

That is a red alarm because it can make the backend appear editable while the live site continues showing old customer-facing truth.

## Current Evidence Snapshot

Live public route checked:

- `https://locallytwisted.com/shop-items/bouquets/large-head-missionary`
- Response showed Frappe Cloud and `x-from-cache: False`.
- Public page rendered `Large head Missionary`.
- Public page rendered custom LT story/details fields, not the standard ERPNext description fallback.
- Product setup JSON embedded on the page showed `base_price: 125.0`.
- Visible page and variant API showed a starting/sellable price of `$175.00`.

That specific product proves a split authority: Product Setup/base-price data can differ from the public sellable-price path, and public copy can differ from whichever backend field a human thought they edited.

The local LT Docker runtime was started for a bounded read-only proof, produced `/tmp/lt-large-head-missionary-db-snapshot.json`, and was stopped afterward. The local snapshot showed Product Setup, Product Setup exact prices, and Item Prices internally consistent at `175.0`.

Authenticated live read-only API proof later confirmed the owner save worked: live Product Setup base price and 30 Product Setup price rows changed to `125.0` at `2026-06-30 01:43:01.382176` by `locallytwisted@gmail.com`. The live sellable Item Price rows stayed at `175.0`, and the public customer page still rendered `from $ 175.00`. The live copy mismatch is the same authority split: public copy renders from Website Item fields, not top-level Product Setup story/details fields.

## Packet Files

- [lane-charter.md](lane-charter.md): feature-lane scope, route record, evidence rules, and operating assumptions.
- [significant-change-register.md](significant-change-register.md): high-impact architecture changes this lane must plan, build, and verify.
- [research-map.md](research-map.md): local prior-research roots, external/official research sources, expedition lanes, and research questions.
- [operating-brief.md](operating-brief.md): sanitized owner intent, hard constraints, safe-proceed rules, and default approach.
- [plan-deepen-notes.md](plan-deepen-notes.md): stress review of the approach with adjusted plan, risks, and gates.
- [owner-workflow-map.md](owner-workflow-map.md): what a business owner can and cannot do today.
- [public-runtime-flow-map.md](public-runtime-flow-map.md): where public shop, product page, cart, checkout, payment, and documents read product data.
- [broken-connections-register.md](broken-connections-register.md): concrete disconnects and red-alarm risks.
- [hardening-milestones.md](hardening-milestones.md): rebuild plan for making ecommerce owner-operable.
- [triad-critique-plan-brief.md](triad-critique-plan-brief.md): briefing packet used for the focused triad critique of the tightened plan.
- [triad-critique-2026-06-30.md](triad-critique-2026-06-30.md): real multi-agent triad synthesis and required plan adjustments before build.
- [construction-build-brief-2026-06-30.md](construction-build-brief-2026-06-30.md): build brief for the first protective-contract implementation slice.
- [protective-contracts.md](protective-contracts.md): controlling safety and owner-workflow contracts for later implementation.
- [construction-review-2026-06-30.md](construction-review-2026-06-30.md): real multi-agent construction review and second-pass acceptance for the protective contracts.
- [phase-0-1-build-brief-2026-06-30.md](phase-0-1-build-brief-2026-06-30.md): implementation-ready brief for the approved read-only Phase 0/1 incident and authority-matrix slice.
- [phase-0-public-evidence-large-head-missionary.md](phase-0-public-evidence-large-head-missionary.md): GET-only public evidence note and safe audit helper usage.
- [phase-0-incident-audit-large-head-missionary-2026-06-30.md](phase-0-incident-audit-large-head-missionary-2026-06-30.md): partial incident audit from public/source evidence with DB proof gaps.
- [phase-0-1-progress-2026-06-30.md](phase-0-1-progress-2026-06-30.md): completed Phase 0/1 non-deploy progress, verification results, and next safe action.
- [phase-0-local-runtime-proof-2026-06-30.md](phase-0-local-runtime-proof-2026-06-30.md): local stack/manual-start proof and local read-only DB snapshot result.
- [phase-0-db-snapshot-integration-plan.md](phase-0-db-snapshot-integration-plan.md): how to integrate local DB snapshot evidence without treating it as live proof.
- [phase-0-local-db-snapshot-analysis-2026-06-30.md](phase-0-local-db-snapshot-analysis-2026-06-30.md): local-only row analysis showing local price authority is internally consistent at `175.0` while live public Product Setup still reports `125.0`.
- [triad-control-phase-0-1-continuation-2026-06-30.md](triad-control-phase-0-1-continuation-2026-06-30.md): triad lane control record for the local-runtime continuation.
- [phase-0-1-continuation-progress-2026-06-30.md](phase-0-1-continuation-progress-2026-06-30.md): continuation closeout showing triad lanes used, local runtime proof, snapshot result, and the former live read-only blocker before it was closed by the later live API audit.
- [live-api-audit-control-2026-06-30.md](live-api-audit-control-2026-06-30.md): live read-only API safety/control record.
- [live-readonly-api-audit-large-head-missionary-2026-06-30.md](live-readonly-api-audit-large-head-missionary-2026-06-30.md): authenticated live read-only finding showing Product Setup saved at `125.0` while sellable Item Prices/public customer price stayed at `175.0`, and public copy renders from Website Item fields.
- [phase-2-projection-preview-parity-2026-06-30.md](phase-2-projection-preview-parity-2026-06-30.md): no-write projection preview, parity verifier, and offline blast-radius report tooling closeout.
- [phase-3-catalog-authority-audit-2026-06-30.md](phase-3-catalog-authority-audit-2026-06-30.md): live read-only full published-catalog authority artifact collection, catalog-wide blocker counts, and next resolver/packet work.
- [phase-4-authority-packet-resolver-2026-06-30.md](phase-4-authority-packet-resolver-2026-06-30.md): offline blocker/resolver report over saved catalog artifacts, 284 blocker breakdown, and first variant-explosion targets.
- [phase-5-operating-brand-source-contract-2026-06-30.md](phase-5-operating-brand-source-contract-2026-06-30.md): source-only Product Setup `operating_brand` field, validation contract, same-brand active uniqueness save guard, runtime duplicate fail-closed behavior, runtime schema propagation, and verifier proof.
- [phase-6-source-authority-packet-reporting-2026-06-30.md](phase-6-source-authority-packet-reporting-2026-06-30.md): offline authority packet reporting for `source_declared` operating brand and same-brand source uniqueness without treating either as live/public proof.
- [phase-7-runtime-brand-aware-lookup-2026-06-30.md](phase-7-runtime-brand-aware-lookup-2026-06-30.md): source-only runtime lookup hardening so Product Setup schema/API/gallery resolution uses explicit or source-declared operating brand and fails closed on ambiguity.
- [phase-8-owner-visible-runtime-authority-blockers-2026-06-30.md](phase-8-owner-visible-runtime-authority-blockers-2026-06-30.md): Product Setup Desk validation blockers for linked Website Item brand metadata and target-identity conflicts before active authority states.
- [phase-9-variant-axis-classification-birthday-deliveries-2026-06-30.md](phase-9-variant-axis-classification-birthday-deliveries-2026-06-30.md): offline Birthday Deliveries variant-axis classification report showing a 2,430 current-variant shape and a blocked 3-SKU candidate model.
- [phase-10-dependency-rollback-capture-birthday-deliveries-2026-06-30.md](phase-10-dependency-rollback-capture-birthday-deliveries-2026-06-30.md): offline Birthday Deliveries dependency/rollback target capture receipt, including row-level saved-artifact rollback rows and mutation blockers.
- [phase-10-critical-review-2026-06-30.md](phase-10-critical-review-2026-06-30.md): critical review artifact for Phase 10 overclaim risks, minimum blockers, and verification expectations.
- [phase-11-no-write-replacement-model-birthday-deliveries-2026-06-30.md](phase-11-no-write-replacement-model-birthday-deliveries-2026-06-30.md): offline no-write Birthday Deliveries replacement model combining Phase 9 classification and Phase 10 rollback blockers.
- [phase-12-owner-visible-publish-readiness-birthday-deliveries-2026-06-30.md](phase-12-owner-visible-publish-readiness-birthday-deliveries-2026-06-30.md): offline owner-visible publish readiness report translating replacement blockers into blocked/not-live state language.
- [phase-13-product-setup-readiness-validation-wiring-2026-06-30.md](phase-13-product-setup-readiness-validation-wiring-2026-06-30.md): Product Setup validation JSON wiring for owner-visible readiness state and false publish/apply approvals.
- [phase-14-product-setup-readiness-desk-display-2026-06-30.md](phase-14-product-setup-readiness-desk-display-2026-06-30.md): Desk read-only Show Readiness display for Product Setup validation readiness state.
- [phase-15-catalog-readiness-dashboard-2026-07-01.md](phase-15-catalog-readiness-dashboard-2026-07-01.md): offline catalog readiness dashboard over saved authority packet reports.
- [phase-15-critical-review-2026-07-01.md](phase-15-critical-review-2026-07-01.md): critical witness review for the catalog dashboard phase.
- [phase-16-release-packet-design-2026-07-01.md](phase-16-release-packet-design-2026-07-01.md): offline pre-mutation release packet report over saved catalog readiness dashboard JSON.
- [phase-16-critical-review-2026-07-01.md](phase-16-critical-review-2026-07-01.md): critical witness review for the release packet design phase.
- [phase-17-desk-catalog-readiness-summary-2026-07-01.md](phase-17-desk-catalog-readiness-summary-2026-07-01.md): Desk read-only catalog readiness summary from saved Product Setup validation JSON.
- [phase-17-critical-review-2026-07-01.md](phase-17-critical-review-2026-07-01.md): critical witness review for the Desk catalog readiness summary.
- [witness-state-phase-5-operating-brand-source-2026-06-30.md](witness-state-phase-5-operating-brand-source-2026-06-30.md): triad/witness state packet for the source-only operating-brand contract.
- [authority-matrix-template.md](authority-matrix-template.md): reusable non-mutating product authority matrix template.
- [authority-packet-large-head-missionary.md](authority-packet-large-head-missionary.md): first partial authority packet for the incident product.

Read-only helper scripts:

- `scripts/dev/lt_readonly_product_audit.py`: public GET-only product evidence collector.
- `scripts/dev/lt_readonly_product_db_snapshot.py`: local-container read-only row snapshot helper for the product authority packet.
- `scripts/dev/lt_live_readonly_product_api_audit.py`: live read-only API product authority collector using Frappe Cloud site login plus live ERPNext GET requests.
- `scripts/dev/lt_live_readonly_catalog_authority_audit.py`: live read-only published-catalog authority artifact collector using Frappe Cloud site login plus live ERPNext GET requests.
- `scripts/dev/lt_product_setup_authority_packet_report.py`: offline blocker/resolver report from saved catalog authority artifacts.
- `scripts/dev/lt_product_setup_projection_preview.py`: offline no-write Product Setup -> runtime row-diff preview from a saved audit artifact.
- `scripts/verify/product_setup_authority_parity_contract.py`: offline fail-loud parity verifier for saved audit/projection/authority-packet artifacts.
- `scripts/verify/product_setup_authority_packet_contract.py`: offline synthetic contract verifier for source-declared brand and same-brand source uniqueness packet boundaries.
- `scripts/dev/lt_product_setup_catalog_blast_radius_report.py`: offline product-by-product risk report from saved audit/projection artifacts.
- `scripts/dev/lt_product_setup_variant_axis_classification_report.py`: offline variant-axis classification report from saved catalog authority artifacts.
- `scripts/verify/product_setup_variant_axis_classification_contract.py`: verifier for the offline variant-axis classification report and Birthday Deliveries saved-artifact behavior.
- `scripts/dev/lt_product_setup_dependency_rollback_report.py`: offline dependency/rollback target report from saved catalog authority artifacts.
- `scripts/verify/product_setup_dependency_rollback_contract.py`: verifier for the offline dependency/rollback report and Birthday Deliveries saved-artifact behavior.
- `scripts/dev/lt_product_setup_replacement_model_report.py`: offline no-write replacement model report from classification, rollback, and optional saved source artifacts.
- `scripts/verify/product_setup_replacement_model_contract.py`: verifier for the offline replacement model report and Birthday Deliveries saved-artifact behavior.
- `scripts/dev/lt_product_setup_publish_readiness_report.py`: offline owner-visible publish readiness report from replacement-model blockers.
- `scripts/verify/product_setup_publish_readiness_contract.py`: verifier for the offline publish readiness report and Birthday Deliveries saved-artifact behavior.
- `scripts/dev/lt_product_setup_catalog_readiness_dashboard.py`: offline catalog readiness dashboard from saved authority packet reports.
- `scripts/verify/product_setup_catalog_readiness_contract.py`: verifier for the offline catalog readiness dashboard and saved full-catalog packet behavior.
- `scripts/dev/lt_product_setup_release_packet_report.py`: offline pre-mutation release packet report from saved catalog readiness dashboard JSON.
- `scripts/verify/product_setup_release_packet_contract.py`: verifier for the offline release packet report and saved dashboard behavior.
- Product Setup Desk `Show Catalog Readiness`: read-only catalog summary inside
  `lt_product_blueprint.py` and `lt_product_blueprint.js`, guarded by
  `scripts/verify/product_blueprint_contract.py`.

## Primary Local Evidence

- `apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_product_blueprint/lt_product_blueprint.json`
- `apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_product_blueprint/lt_product_blueprint.js`
- `apps/locally_twisted/locally_twisted/product_blueprint_validation.py`
- `apps/locally_twisted/locally_twisted/product_blueprint_apply_plan.py`
- `apps/locally_twisted/locally_twisted/product_blueprint_local_apply.py`
- `apps/locally_twisted/locally_twisted/owner_catalog_guard.py`
- `apps/locally_twisted/locally_twisted/www/shop.py`
- `apps/locally_twisted/locally_twisted/templates/generators/item/item_details.html`
- `apps/locally_twisted/locally_twisted/templates/generators/item/item_configure.html`
- `apps/locally_twisted/locally_twisted/templates/generators/item/item_image.html`
- `apps/locally_twisted/locally_twisted/product_options.py`
- `apps/locally_twisted/locally_twisted/product_page_runtime.py`
- `apps/locally_twisted/locally_twisted/product_setup_runtime.py`
- `apps/locally_twisted/locally_twisted/api/cart.py`
- `apps/locally_twisted/locally_twisted/www/checkout.py`
- `apps/locally_twisted/locally_twisted/payments/stripe_session.py`
- `capabilities/recipes/erpnext-ecommerce-receiving-architecture.md`
- `capabilities/recipes/erpnext-product-blueprint-authoring.md`
- `capabilities/recipes/erpnext-catalog-variant-price-parity.md`
- `capabilities/recipes/erpnext-webshop-guest-party-contract.md`
- `capabilities/failures/ecommerce-variant-price-source-drift.md`
- `capabilities/failures/product-gallery-projection-regression.md`
- `capabilities/failures/product-primary-media-attachment-drift.md`
- `capabilities/failures/product-setup-projection-authority-drift.md`

## Official Baseline References

ERPNext's native ecommerce model uses Website Items, Item Prices, Price Lists, Item Variants, and E Commerce/Webshop settings. LT has built custom operator, runtime, cart, and checkout logic on top of that model.

- ERPNext Website Item docs: https://docs.frappe.io/erpnext/website_item
- ERPNext Item Price docs: https://docs.frappe.io/erpnext/item-price
- ERPNext Price Lists docs: https://docs.frappe.io/erpnext/price-lists
- ERPNext Item Variants docs: https://docs.frappe.io/erpnext/item-variants
- ERPNext E Commerce Settings docs: https://docs.frappe.io/erpnext/e_commerce_settings
- Frappe cache commands: https://docs.frappe.io/framework/user/en/bench/frappe-commands
- Frappe hooks: https://docs.frappe.io/framework/user/en/python-api/hooks
- Prior ERP variant docs: official vendor documentation, URL intentionally omitted from tracked LT docs because the platform name is restricted.
- Saleor product configuration docs: https://docs.saleor.io/developer/products/configuration
- commercetools product modeling docs: https://docs.commercetools.com/learning-model-your-product-catalog/product-modeling/products
- Medusa Admin variant/media docs: https://docs.medusajs.com/user-guide/products/variants

## Triad / Expedition Record

Route record:

```markdown
Mode: real multi-agent triad plus expedition synthesis
Decision needed: how to turn LT ecommerce from developer-operated scaffold into owner-operated shop infrastructure
Scope owner: Locally Twisted ecommerce feature lane
System/project/runtime classification: single project + client/production surface + external research
Allowed actions: repo reads, public/official docs research, local evidence mapping, lane documentation
Forbidden actions: live provider mutation, logged-in account changes, product writes, deploys, payment changes, secret reads
Evidence bar: source-separated local code proof, prior-research evidence, official docs, and live public-route proof where available
Stop condition: stop before implementation or live changes until a scoped build packet and approval exist
```

Triad lanes used:

- LT ground-truth lane: current Product Setup, pricing, media, add-on, public projection, cart/checkout/document/payment surfaces.
- Prior-research lane: local historical ecommerce architecture research and prior ERP backend lessons, sanitized into architecture-neutral findings.
- External comparison lane: official/primary docs for ecommerce variant, option, media, pricing, and publishing patterns.

## Capability Gate

Capability gate: PASS.

Loaded resources:

- `capabilities/INDEX.md`
- `capabilities/recipes/erpnext-ecommerce-receiving-architecture.md`
- `capabilities/recipes/erpnext-product-blueprint-authoring.md`
- `capabilities/recipes/erpnext-catalog-variant-price-parity.md`
- `capabilities/recipes/erpnext-webshop-guest-party-contract.md`
- `capabilities/failures/ecommerce-variant-price-source-drift.md`
- `capabilities/failures/product-gallery-projection-regression.md`
- `capabilities/failures/product-primary-media-attachment-drift.md`
