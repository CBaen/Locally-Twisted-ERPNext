D:2026-05-10 | Check:local artifacts 2026-05-10 | Confidence:[LOCAL-PROOF]
# Ecommerce Audit Handoff — Odoo witness → native ERPNext receiving ecosystem

## Current peer state

This directory is the evidence packet for the May 10 ecommerce architecture audit. It is not a product import, not a destructive migration rehearsal, and not permission to copy Odoo code. Odoo is the source witness for business meaning; ERPNext/Frappe v15 receives that meaning through native DocTypes, custom fields, app services, templates, and verifiers.

2026-05-14 GL correction for peer GPT 5.5 agents: `lt_ecommerce_paused=1`
is a live/customer exposure safety lock, not an implementation blocker. The
reason ecommerce is not public is that the product, cart, checkout, pricing,
media, staff-authoring, and verification paths are not trustworthy enough yet.
Local and staging/test-harness ecommerce work must continue under the lock and
must name actual blockers. Keep the architecture lens backend-first: ERPNext
v15.105.0 / Frappe v15 Webshop integration must preserve Item, Item Variant,
Website Item, Item Price, Item Attribute, media/gallery, Webshop Settings,
cart/checkout, payment, and Frappe Cloud persistence meaning into product-page
UX and search/discovery. Current visible/imported products are test products
only; real catalog truth requires a separate approved catalog/import proof
gate.

## 2026-05-22 Owner Product Setup Guard Closeout

Use `owner-product-setup-guard-closeout-2026-05-22.md` as the front-door
handoff for the recovered owner product-management safety lane. It records the
triad witness/recorder/fixer review, the owner catalog guard expansion, Product
Setup exact-price/gallery/copy/backfill behavior, local apply visibility and
route protections, and the focused proof set.

Current evidence: owner raw catalog mutations are blocked across `19/19`
probes, existing public Website Items keep their published state during local
Product Setup apply, local apply refuses public hide/route-change requests, and
Product Setup sync dry run reports `51` Website Items with `0` creates and
`21` truthful would-update rows. Final pre-commit
`npm run test:owner-product-safety` passed. This is local-only.

## 2026-05-22 Product Gallery Restoration

Use `product-gallery-restoration-2026-05-22.md` as the front-door handoff for
product-page additional-photo galleries. It records the source-approved gallery
media -> Product Setup -> Website Slideshow -> Webshop template architecture,
the role split between `gallery`, `variant_image`, `reference`, and
`ignored_artifact`, and the rendered-route regression guard.

Current evidence: Product Setup owns `68` approved live gallery rows, `47`
Website Items have native `Website Slideshow` links, `68` Website Slideshow
Item rows exist, and rendered product routes prove the thumbnail rail. Final
local gates passed through `product_gallery_projection_contract.py`,
`test:product-gallery-experience`, `test:owner-product-safety`, and
`test:ecommerce-full`. This is local-only.

## 2026-05-22 Product Option Selection UX

Use `product-option-selection-ux-2026-05-22.md` for the screenshot-reported
option-text and foil-number add-on repair. This keeps stored backend option
values intact while splitting short display labels from included-copy details
on the product page.

Current evidence: final pre-commit `npm run test:product-options-experience`
passed `4/4`, and visible price display plus cart/checkout passed through the
owner-product umbrella. Rerun those gates if source changes before staging.

## 2026-05-20 Product Page Local Review

Use `product-page-local-review-2026-05-20.md` for the current local product-page
design/logic review slice before staging. It records the mobile image/details
spacing repair, the fulfillment-panel runtime lane fix, Classic Arch
`complex_custom_product|quote_first` proof alignment, and the local verifier
receipt set.

This handoff is not a staging packet and not live approval. Its open blocker is
the broader product-classification conflict:
`quote_event_checkout_boundary_contract.py` still expects some older
quote-first rows, including `basketball-arch`, while the current DB has at
least that product as checkout. `website_item_classification_contract.py`
dry-run wants 17 lane changes from an older target model. Do not apply those
classification changes without current GL review.

## 2026-05-22 Shop Category Generated Heroes

Use `shop-category-hero-imagery-2026-05-22.md` as the current front-door
handoff for `/shop-items/<group>` route hero imagery. It supersedes the first
bad local attempt that cropped product photos into banners.

Current evidence after the 2026-05-24 taxonomy refresh: all 8 active category
detail routes have unique generated hero WebP crops for mobile, tablet, and
desktop. The source prompt authority is the category shape plus owner-approved
balloon color names and swatch references, with hex values documented only as
web-match approximations. `shop_category_hero_images.spec.js` passed for the
active route set and the category routes passed public asset checks. No
ERPNext Item Group `image` fields were changed, and no staging/live release
was performed.

## 2026-05-17 Sellable Product Reimport

Use the 2026-05-17 sellable product reimport handoff as historical proof for
the local sellable product import slice. The 2026-05-24 taxonomy proof is now
the current category/count source.

Historical evidence: the local `frontend` site was backed up, cleaned of
generated proof products, snapshotted, reimported, and then browser-proved in
two batches under the cart 50-line cap. Desktop and mobile product page, cart,
and checkout preview passed. `lt_ecommerce_paused=1` was restored and
verified. No staging/live/Frappe Cloud/Stripe/DNS/public exposure change was
performed.

Remaining caveats: product-page gallery media is now approved through Product
Setup and native Website Slideshow projection. Category/reference media and 9
review-only add-on controls remain separate approval/mapping lanes. Those do
not make the base products non-products.

## 2026-05-11 Post-Import Checkout Closeout

Use `post-import-checkout-launch-closeout-2026-05-11.md` as the current
front-door handoff for the local ecommerce checkout slice. It supersedes stale
pause-centric, bouquet-only, cups-exclusion, and blanket high-variant exclusion
notes for this slice.

Historical evidence: the 2026-05-11 packet proved the earlier narrow checkout
slice. It is superseded for current import scope by the 2026-05-17 sellable
reimport above and the 2026-05-24 taxonomy proof.

## 2026-05-11 Storefront Proof And Complex UI Handoff

Use `storefront-proof-and-complex-ui-handoff-2026-05-11.md` for the
storefront-owned proof and next UI slice. It captures the corrected
Ready-to-Order/search rendered proof, final post-import checkout proof, the
all-priced-page frontend audit, Classic Arch's current internal hold state, the
legacy lane correction, and the complex-product UI checklist.

Current storefront evidence: 53 published priced product routes rendered; 18
direct-checkout pages passed option selection, `data-item-code`, add-to-cart,
cart-line configuration, and checkout summary preservation; 35 priced pages are
currently blocked at the first rendered layer by legacy internal hold or
needs-review state. `quote_first` is an old safety flag, not a business product
category. Moving any held product into checkout still needs backend-truth UI for
multi-color recipes, add-ons, conditional pricing, image updates, and
cart/checkout/receipt summary parity.

## 2026-05-12 Ready-to-Order Nav/Search Backend Gate

Use `ready-to-order-nav-search-backend-gate-2026-05-12.md` as historical
product-checkout eligibility evidence only. Public Ready-to-Order chrome was
superseded on 2026-05-21 by
`../ready-to-order-category-menu-2026-05-21.md`: header/menu/search/drawer
entries are category discovery from visible `Item Group` children of
`Shop Items`, not Website Item product quick links. Owner include codes and
`simple_product|checkout` fields still matter below the category page and in
checkout/product-page contracts.

## 2026-05-12 Complex Checkout Scaffold

Use `complex-checkout-scaffold-2026-05-12.md` for the current local-only
complex product-page checkout scaffold. `python
scripts/verify/complex_checkout_scaffold.py` refreshes ProductPatternContract
data and writes ignored `output/complex-checkout-scaffold.*` artifacts without
touching Frappe Cloud or the live domain.

Current scaffold proof should be rerun before launch use. The prior sellable
correction checked 53 products with no explicit checkout architecture gaps, but
the 2026-05-24 taxonomy proof is now the current category/count source.

## 2026-05-12 Ecommerce Shop Setup Closeout

Use the root `ECOMMERCE-SHOP-HANDOFF.md` for the current local ecommerce shop
setup closeout. Completed lanes:

- Backend wiring `f82b8ef1`: no backend edits; ProductPatternContract,
  selected config, cart line key, add-on SO/SI preservation, checkout lead
  conversion, quote fallback, fail-loud checkout blocks, all product quote
  contracts, and customer note preservation passed.
- Catalog/import/pricing `4da4b135`: commit `9a27b49`; guarded
  `website_item_classification_contract --apply` changed exactly 5 Website Item
  fields to `needs_review|needs_review`; no ERPNext catalog/pricing/import
  blocker remains.
- Media `d2653ce8` / `d9543e5f`: commit `8e4a95b` is historical. It forced
  source extras into a safe hold bucket. The current 2026-05-22 gallery
  restoration supersedes that blanket rule for product-page gallery media:
  approved `gallery` rows now project through Product Setup and Website
  Slideshow, while variant/category/reference media stay separate.
- Storefront/product UX `3132de36` plus homepage blocker `4fd5ae4f`: commit
  `3179463`; homepage container verifier was rebaselined to committed
  `show_custom_event_decor=False`; focused nav/search/shop/container checks
  pass.
- Runner `786f962e`: included in `e4186c1`; Playwright wrapper uses Program
  Files Node and focused runner proofs pass. Long broad sweeps may still see
  transient ERPNext HTTP 417/502, but exact reruns pass.

2026-05-18 school/seasonal color-preset follow-up:
`school-seasonal-color-preset-product-logic-2026-05-18.md` converted the two
graduation checkout products to college preset variants and moved
hyperspecialized 50+ color products to quote request. Current local counts:
53 published Website Items, 10,686 Items, 49 templates, 10,629 variants,
10,186 active variants, 443 disabled variants, 10,668 Item Prices,
30 Item Attributes, and 32,049 Item Variant Attribute rows.

## 2026-05-14 Product Blueprint Authoring

Use `product-blueprint-authoring-2026-05-14.md` for the current local-only
staff product-authoring slice. It adds `LT Product Blueprint` plus child tables
for options, color recipes, add-ons, and conditional pricing; validates page
type/buying path/payload targets against the backend product-page architecture;
previews a no-write apply plan; exposes a guarded Desk `Apply Locally` action;
and lets checkout-approved fixed-item-price blueprint add-ons cascade into
product options and checkout validation.

Boundaries: the local `frontend` site has `lt_allow_local_blueprint_apply=1`
for this test harness; generated Website Items stay unpublished unless a local
proof explicitly publishes them; `Approved For Live` remains blocked; no
Frappe Cloud, DNS, staging/live publish, or live checkout work was performed.
2026-05-17 local proof did perform one intentional test-mode Stripe checkout
against an employee-authored 48-variant proof product, then restored
`lt_ecommerce_paused=1`. Remaining product authoring work is richer
self-service UI for complex cases, conditional pricing runtime, broader real
catalog media approval UI, broader add-on family mapping, and refreshed import
safety evidence.

## 2026-05-17 Product Family Certification Truth Table

`product-family-certification-truth-table-2026-05-17.md` is now historical for
the tranche approach. Current product/product-page certification lives in
`odoo-sellable-product-reimport-2026-05-17.md`: 53 checkout products, 0
exclusions, 290 priced sale units, and all 53 live routes browser-proved in
local open mode before restoring `lt_ecommerce_paused=1`.

## 2026-05-17 Product Source Repair Map

Use `product-source-repair-map-2026-05-17.md` and
`product-source-repair-map-2026-05-17.json` for the current 53-product source
repair queue. The map is generated by
`python scripts/verify/product_source_repair_map.py` from the Odoo export,
price-enrichment artifact, and complex-checkout scaffold. It records GL's
correction that every product targets purchasable behavior; non-certified rows
are `blocked_until_certified` until source data, pricing, media, and checkout
cascade proof pass.

## 2026-05-17 Simple Purchasable Rehearsal

Use `simple-purchasable-rehearsal-2026-05-17.md` and
`simple-purchasable-rehearsal-2026-05-17.json` for the first backend-only
rehearsal of the simple repair lane. The rollback contract temporarily applies
`simple_product|checkout` in one ERPNext transaction for `large-head-missionary`,
`mothers-day-front-yard-7-column`, `easter-arch`, and `pride-arch`, proves 33
sale SKUs through Sales Order and Sales Invoice line preservation, and rolls
back with zero surviving records. It does not prove browser UX, Payment Request,
Payment Entry, receipt email, operator email, or live/customer approval.

## 2026-05-17 Simple Purchasable Browser Proof

Use `simple-purchasable-browser-proof-2026-05-17.md` and
`simple-purchasable-browser-proof-2026-05-17.json` for the local open-mode
browser proof of that same simple repair lane. The wrapper temporarily opens
local ecommerce, applies the checkout contract to the four Website Items, runs
desktop and mobile product/cart/checkout preview proof, then restores the
original Website Item contracts and `lt_ecommerce_paused=1`. It does not prove
Payment Request, Payment Entry, receipt email, operator email, or live/customer
approval.

## 2026-05-17 Simple Purchasable Payment Cascade

Use `simple-purchasable-payment-cascade-2026-05-17.md` and
`simple-purchasable-payment-cascade-2026-05-17.json` for the rollback-safe
payment/customer-message proof of that same simple repair lane. The contract
temporarily applies the checkout contract, resolves all 33 sale lines through
checkout logic, then proves Payment Request, Payment Entry, Sales Invoice,
customer receipt, operator email, welcome email, idempotency, and rollback
cleanup. It does not authorize customer exposure; final owner/product approval
is still required.

## 2026-05-17 Multi-Color Purchasable Rehearsal

Use `multi-color-purchasable-rehearsal-2026-05-17.md` and
`multi-color-purchasable-rehearsal-2026-05-17.json` for the rollback-safe
backend rehearsal of the six multi-color repair-lane products. The contract
temporarily applies `simple_product|checkout` in one ERPNext transaction,
proves 563 enabled color SKUs resolve through checkout with `color_recipes`,
preserves all Sales Order/Sales Invoice line fields, and rolls back with zero
surviving records. It does not prove browser UX, Payment Request, Payment
Entry, receipt/operator/welcome emails, media update behavior, owner approval,
or staging/live exposure.

## 2026-05-17 Multi-Color Purchasable Browser Proof

Use `multi-color-purchasable-browser-proof-2026-05-17.md` and
`multi-color-purchasable-browser-proof-2026-05-17.json` for the local open-mode
browser proof of that same multi-color repair lane. The wrapper temporarily
opens local ecommerce, applies the checkout contract to the six Website Items,
runs desktop and mobile product/cart/checkout preview proof, verifies 14
visible color drawer selections preserve `color_recipes`, then restores the
original Website Item contracts and `lt_ecommerce_paused=1`. It does not prove
Payment Request, Payment Entry, receipt/operator/welcome emails, media update
behavior, owner approval, or staging/live exposure.

## Evidence inventory

| Lane | Required artifact | Current state | Use it for |
|---|---|---|---|
| A — Odoo source commerce map | `odoo-source-commerce-map-2026-05-10.md` | Present, read back | Cite for Odoo source/product/page/option/pricing/media/cart meaning, with version mismatch labels. |
| B — ERPNext receiving parity matrix | `erpnext-receiving-parity-matrix-2026-05-10.md` | Present | Destination parity, custom-field/service/verifier matrix, blockers. |
| C — Cart/checkout intent preservation | `cart-checkout-intent-preservation-audit-2026-05-10.md` | Present | Browser/backend proof slice for configured checkout and quote-first paths. |
| D — Native Frappe template architecture | `native-frappe-product-template-architecture-2026-05-10.md` | Present | Smallest safe native architecture and required custom layer. |
| E — Odoo/docs/agent-action convergence | `odoo-docs-agent-action-convergence-2026-05-10.md` | Present, parent-created / recovered artifact-first | Cite for converged Odoo witness → ERPNext receiving architecture, including no-variant options, cart intent, quote-first, checkout/payment boundary, automations, and verifier state. |
| Infrastructure doc map + synthesis | `ecommerce-infrastructure-doc-map-and-synthesis-2026-05-10.md` | Present, parent-created | Front-door map of every infrastructure artifact, the recovered plan, current evidence, sequencing, and what remains blocked. Start here. |
| Infrastructure plan v2 | `ecommerce-infrastructure-plan-v2-2026-05-10.md` | Present, parent-created | New infrastructure-first action plan: source authority, receiving contract register, runtime payloads, cart/checkout/quote proof, human approval packets, import/reopen gates, and launch decision packet. |
| Live Odoo backend architecture witness | `odoo-backend-architecture-and-checkout-logic-2026-05-10.md` | Present, parent-created / live read-only backend + source proof | Direct Odoo backend/public read-only observations: product/variant/no-variant architecture, 53-color behavior, cart/order-line preservation, checkout/payment boundary, delivery, CRM fields, automations, and ERPNext receiving requirements. |
| Infrastructure readiness packet | `ecommerce-infrastructure-readiness-packet-2026-05-10.md` | Present, parent-created | Current launch-readiness packet: what is proven, what remains blocked, Odoo logic to preserve, verifier state, and next engineering gates. |
| ERPNext receiving build spec from Odoo | `erpnext-receiving-build-spec-from-odoo-2026-05-10.md` | Present, parent-created | Converts live Odoo backend logic into concrete ERPNext/Frappe object model, gaps, gates, and coding order. |
| Ready-to-order checkout scope decision | `ready-to-order-checkout-scope-decision-2026-05-10.md` | Present, GL-directed / parent-recorded | Narrows launch scope: direct checkout only for ready-to-order/simple products; complex/high-variant/high-dollar decor routes quote-first/invoice-first. |
| Ready-to-order product candidate list | `ready-to-order-product-candidate-list-2026-05-10.md` | Historical, superseded by 2026-05-17 full import closeout | Earlier staged scope artifact that classified products into checkout/quote/hide buckets; do not use as the current product model. |
| Ready-to-order product cut plan | `ready-to-order-product-cut-plan-2026-05-10.md` | Historical, superseded by 2026-05-17 full import closeout | Earlier first-shelf plan; all 53 Odoo products now target sellable checkout behavior locally unless GL explicitly excludes a product. |
| Event pages vs ready-to-order shop contract | `event-pages-vs-ready-to-order-shop-contract-2026-05-10.md` | Present, GL-directed / parent-recorded | Public IA/merchandising rule: high-ticket decor lives as examples on event pages with quote CTAs; shop stays simple/low-variation and preserves customer notes. |
| Customer note checkout preservation audit | `customer-note-checkout-preservation-audit-2026-05-10.md` | Present, subagent-created / parent-read | Finds optional `order_notes` is code-wired to Sales Order timeline Communication and operator/payment-success lookup, but lacks a single passing end-to-end checkout-note verifier. |
| Ecommerce infrastructure agent playbook | `ecommerce-infrastructure-agent-playbook-2026-05-10.md` | Present, subagent-created / parent-read | Reusable future-agent playbook: scope rules, Odoo witness rules, ready-to-order vs event quote split, customer-note rule, artifact-first behavior, verifier gates, and failure modes. |
| Ready-to-order ecommerce plan-deepen | `ready-to-order-ecommerce-plan-deepen-2026-05-10.md` | Present, parent-created after `/plan_deepen` | Deepens the narrowed plan: direct checkout only for simple products, event decor quote-first, Phase 1 verifier repair before product edits, explicit Website Item classification sequence, delivery/payment/operator gates, and current `checkout_fulfillment_contract.py` pause-harness diagnosis. |
| Phase 1 verifier foundation result | `phase-1-verifier-foundation-result-2026-05-10.md` | Present, subagent-created / verifier-backed | Repairs checkout fulfillment pause harness/KeyError failure and adds rollback-safe customer-note checkout preservation proof with exact verifier output. |
| Phase 2 Website Item classification result | `phase-2-website-item-classification-result-2026-05-10.md` | Present, verifier-backed / applied | Adds targeted dry-run/apply classifier, applies the exact 53 Website Item lane/type decisions, and proves stored counts: 15 checkout, 33 quote-first, 5 needs-review. |
| Phase 3 checkout product-family proof result | `phase-3-checkout-product-family-proof-result-2026-05-10.md` + `phase-3-checkout-product-family-contract-20260510.json` | Present, superseded by 2026-05-11 all-SKU verifier | Original representative-family proof; use the 2026-05-11 all-SKU parity handoff for current counts. |
| Checkout enabled-SKU parity proof | `checkout-enabled-sku-parity-proof-2026-05-11.md` + `2026-05-10-2330-phase-1-4-shop-audit/checkout-product-family-all-skus-final.json` | Present, verifier-backed / parent-verified | Corrects the count boundary: 15 checkout Website Item families/pages, 47 enabled sale SKUs, 39 foil add-on rows, 86 Sales Order/Sales Invoice rows, rollback clean. |
| Phase 4 quote/event path hardening result | `phase-4-quote-event-path-hardening-result-2026-05-10.md` + `phase-4-quote-event-checkout-boundary-contract-20260510.json` | Present, verifier-backed / parent-verified | Proves 33 quote-first + 5 needs-review products cannot enter paid checkout through product page controls, cart API, direct checkout URL, or stale localStorage; fail-closed precedence prevents inferred/partial checkout drift. |
| Verifier failure diagnosis | `product-page-architecture-readiness-failure-diagnosis-2026-05-10.md` | Present, parent/subagent-created then parent-verified | Explains why the prior `bench execute failed` no longer reproduces; latest exact verifier command passes. |
| Phase 5 delivery/payment/operator packet | `phase-5-delivery-payment-operator-packet-2026-05-10.md` | Present, parent-verified / local proof | Proves delivery fee mapping, pickup, tax boundaries, payment backend config, mocked webhook, paid cascade, payment-success reconciliation, operator quote review/send control, customer quote delivery BCC safety, local launch readiness, and pause-state safety. |
| Product import hardening gate | `product-import-hardening-gate-2026-05-11.md` + `../../scripts/verify/product_import_readiness_gate.py` | Present, backend-owned / read-only gate | Minimum real-catalog import readiness gate for peer GPT agents: source packets, approvals, fail-loud import fields, dry-run/destructive/backup guards, snapshot and rollback plan. Expected current result is blocked until hardening and approvals are complete. |
| Payment portal live cutover checklist | `../payment-portal-live-cutover-checklist-2026-05-11.md` | Present, backend-owned / checklist | Moves passing local/test payment contracts into staging/live cutover steps for Frappe v15.106.0 / ERPNext v15.105.0, Frappe Cloud site config, Stripe webhook/policy setup, and one approved low-risk live payment test. |
| Sellable product reimport | `odoo-sellable-product-reimport-2026-05-17.md` + `../../scripts/verify/v1_odoo_erpnext_import_manifest.py` + `../../scripts/verify/product_import_readiness_gate.py` + `../../scripts/verify/post_import_checkout_proof.js` | Historical, local-only full import/proof closeout | Superseded for category/count truth by the 2026-05-24 taxonomy proof: 51 published products, 30 checkout, 21 quote-first, and 2 duplicate source slugs excluded. |
| Post-import checkout launch closeout | `post-import-checkout-launch-closeout-2026-05-11.md` | Historical, superseded by 2026-05-17 full import closeout | Older 48 kept / 5 Classic-excluded proof packet; use only for history. |
| Storefront proof and complex UI handoff | `storefront-proof-and-complex-ui-handoff-2026-05-11.md` | Present, rendered storefront proof / frontend-owned handoff | Captures Ready-to-Order/search proof, final post-import checkout proof, all-priced-page audit, Classic Arch proof, quote-first lane correction, complex UI requirements, and regression proof ladder. |
| Ready-to-Order nav/search backend gate | `ready-to-order-nav-search-backend-gate-2026-05-12.md` | Present, review-closeout / local DB + rendered proof | Captures owner-include-as-allowlist rule, backend `simple_product|checkout` requirement, hidden-vs-removed search quick-link assertion, mobile drawer label correction, and nav/search verifier receipts. |
| Complex checkout scaffold | `complex-checkout-scaffold-2026-05-12.md` + `../../scripts/verify/complex_checkout_scaffold.py` | Present, local ProductPatternContract scaffold / source-owned gate | Historical 53-product scaffold; rerun with the current 2026-05-24 taxonomy proof before using for launch decisions. |
| Backend product-page architecture contract | `backend-product-page-architecture-contract-2026-05-12.md` + `../../scripts/verify/product_page_architecture_contract.py` | Present, post-review / source+live projection gate | Owns `lt-product-page-architecture-contract-v1`, source/backend axis role projection, payload target mapping, line-field parity, and the post-review color-axis regression proof. |
| Ecommerce shop setup closeout | `../../ECOMMERCE-SHOP-HANDOFF.md` | Present, current root closeout | Current completed-lane summary for backend wiring, catalog/import/pricing, media readiness, storefront UX/homepage verifier alignment, runner wrapper, remaining live gates, and scoped worktree caveats. |
| Product blueprint authoring | `product-blueprint-authoring-2026-05-14.md` + `../../scripts/verify/product_blueprint_contract.py` + `../../scripts/verify/product_blueprint_live_contract.py` | Present, local-only staff authoring / rollback-safe apply proof | Adds employee Desk product setup, validation evidence, dry-run apply plan, guarded unpublished local apply, and fixed-price blueprint add-on runtime cascade. |
| Generic Product Setup runtime | `generic-product-setup-runtime-2026-05-15.md` + `../../scripts/verify/product_blueprint_live_contract.py` + `../../scripts/verify/cart_checkout_contract.py` + `../../scripts/verify/payment_cascade_contract.py` | Present, local-only complex Product Setup media/payment proof | Proves generic selection groups, SKU-defining variants, configuration-only choices, combination media rules, server-selected image parity through cart/checkout/Stripe/receipt, role-gated local apply, and fake-card local payment cascade. |
| Product family certification truth table | `product-family-certification-truth-table-2026-05-17.md` | Historical tranche map, superseded by sellable reimport and taxonomy proof | Older staged certification split; current source/import truth must be read with the 2026-05-24 taxonomy proof. |
| Product source repair map | `product-source-repair-map-2026-05-17.md` + `product-source-repair-map-2026-05-17.json` + `../../scripts/verify/product_source_repair_map.py` | Present, source-backed repair queue | Maps every Odoo-export product to `purchasable_product`, reports 53/53 source rows found, and assigns the remaining 35 products to focused repair lanes instead of treating legacy holds as a product model. |
| Simple purchasable rehearsal | `simple-purchasable-rehearsal-2026-05-17.md` + `simple-purchasable-rehearsal-2026-05-17.json` + `../../scripts/verify/simple_purchasable_rehearsal_contract.py` | Present, rollback-safe backend proof | Proves the four simple repair-lane products can preserve source-backed prices and 33 sale SKU lines through Sales Order and Sales Invoice when temporarily treated as checkout inside one transaction. |
| Simple purchasable browser proof | `simple-purchasable-browser-proof-2026-05-17.md` + `simple-purchasable-browser-proof-2026-05-17.json` + `../../scripts/verify/simple_purchasable_browser_proof.py` | Present, local-only browser proof | Proves the same four products pass desktop/mobile product pages, cart, and checkout preview after temporary local opening, then verifies local contracts and ecommerce pause are restored. |
| Simple purchasable payment cascade | `simple-purchasable-payment-cascade-2026-05-17.md` + `simple-purchasable-payment-cascade-2026-05-17.json` + `../../scripts/verify/simple_purchasable_payment_cascade_contract.py` | Present, rollback-safe payment proof | Proves the same four products and all 33 sale lines pass Payment Request, Payment Entry, Sales Invoice, receipt, operator email, welcome email, idempotency, and rollback cleanup. |
| Phase 6 launch decision packet | `phase-6-launch-decision-packet-2026-05-10.md` | Present, parent decision | Keeps public ecommerce paused; live checkout remains blocked until production HTTPS host, explicit live Stripe/site config, policy approval, webhook setup, and one intentional real payment test pass. |
| Infrastructure synthesis | `ecommerce-infrastructure-research-synthesis-2026-05-10.md` | Present, parent-created | Corrected synthesis for the real question: ERPNext receiving infrastructure, contract/runtime layers, line-level preservation, quote/checkout bridges, fail-loud evidence, and verifier gates. |
| Knowledge base index | `ecommerce-knowledge-base-index-2026-05-10.md` | Present, parent-created | Supporting index of recalled memory, local artifacts, source repos, verified docs, blockers, and next actions. |
| Product proof matrix | `ecommerce-product-proof-matrix-2026-05-10.md` | Present, parent-created / downstream only | 53-row source/product matrix. Use only after infrastructure gates; not the architecture decision artifact. |
| User-provided Odoo surfaces | `user-provided-odoo-surfaces-2026-05-10.md` | Present | Read-only surface references supplied by GL; do not click admin/auth surfaces without preflight. |

## Version anchors and mismatch labels

- Destination runtime verified by Lane B/C: `frappe 15.106.0`, `erpnext 15.105.0`, `payments 0.0.1`, `webshop 0.0.1`, `locally_twisted 0.0.1`.
- Dispatch anchor was `frappe/erpnext:v15.105.0`; local container image reported `locally-twisted-erpnext:v15`, so downstream claims should carry `[VERSION-MISMATCH]` unless the image digest/source is resolved.
- Odoo source witness local module is `addons/locally_twisted` `19.0.2.15.0`; prior handoff warns production DB may still be `19.0.2.14.0`, so source parity remains `[VERSION-MISMATCH]` until resolved.

## Current conclusion

Native ERPNext/Frappe can receive the ecommerce shop meaning safely when the
`locally_twisted` contract layer stays in charge: ProductPatternContract,
Website Item page/lane fields, versioned line payload fields, source-backed
dependency/add-on/pricing/media services, fail-loud verifiers, and scoped
import guards. As of the 2026-05-17 closeout, local backend wiring,
catalog/import/pricing, media primary-image readiness, storefront product UX,
cart/checkout preview, and runner wrapper lanes were green for the then-current
sellable import. The 2026-05-24 taxonomy proof is now the current count source:
51 published products, 30 checkout, 21 quote-first, and 2 duplicate source
slugs excluded. The staff blueprint slice still lets
employees define new customizable products in ERPNext locally, preview/apply
them unpublished, and prove fixed-price blueprint add-on cascades. This is
local ecommerce architecture/import/authoring proof, not final live cutover
approval. Remaining launch gates are GL local acceptance, Frappe Cloud
staging/source freeze, Cloudflare/DNS, live Stripe/site config/webhook, legal
or policy approvals where needed, one intentional low-risk live payment test,
and final real catalog approval if the local product set is to become public
catalog truth.


## Pre-Phase-5 hygiene verification (2026-05-10 18:xx MDT)

Parent reran the Phase 1-4 owned gates after documentation cleanup and stale ignored-output cleanup. All passed:

- `python -m py_compile ...` for ecommerce runtime/verifier/runner files.
- `python scripts/verify/product_page_runtime_contract.py` PASS.
- `python scripts/verify/website_item_classification_contract.py --report output/phase-4-website-item-classification-contract-20260510.json` PASS; generated JSON matched durable workstream copy, then the ignored output duplicate was removed.
- `python scripts/verify/checkout_fulfillment_contract.py` PASS; rollback confirmed.
- `python scripts/verify/payment_cascade_contract.py` PASS; rollback confirmed.
- `python scripts/verify/customer_note_checkout_preservation_contract.py` PASS; survivor counts stayed zero.
- `python scripts/verify/checkout_product_family_contract.py --report workstreams/ecommerce-audit/2026-05-10-2330-phase-1-4-shop-audit/checkout-product-family-all-skus-final.json` PASS; historical all-SKU fixture proof reports 15 checkout families/pages, 47 enabled sale SKUs, 39 add-on rows, 86 Sales Order/Sales Invoice rows, rollback clean. Current product scope must be read with the 2026-05-24 taxonomy proof.
- `python scripts/verify/quote_event_checkout_boundary_contract.py --report output/phase-4-quote-event-checkout-boundary-contract-20260510.json` PASS; generated JSON matched durable workstream copy, then the ignored output duplicate was removed.

Current durable JSON evidence remains only under this workstream directory. Ignored `output/phase-*20260510.json` duplicates are regenerated proof artifacts, not source, and were deleted after equality checks.

## Next safe actions

1. Treat Lane A as present only through the parent-verified artifact `odoo-source-commerce-map-2026-05-10.md`; do not trust the earlier artifactless child completion event.
2. Use recovered Lane E (`odoo-docs-agent-action-convergence-2026-05-10.md`) as the convergence artifact; no longer carry Lane E as `[NO EVIDENCE]`.
3. Use `ecommerce-infrastructure-doc-map-and-synthesis-2026-05-10.md` as the front-door architecture map, `ecommerce-infrastructure-plan-v2-2026-05-10.md` as the active action plan, `ecommerce-infrastructure-readiness-packet-2026-05-10.md` for the current proof/gate packet, and `erpnext-receiving-build-spec-from-odoo-2026-05-10.md` for the concrete coding order; use product matrices only downstream of infrastructure gates.
4. Treat the earlier `product_page_architecture_readiness.py` `bench execute failed` as transient unless it recurs; current exact command passes and the diagnosis artifact explains the failure mode.
5. Rerun the readiness verifier immediately before any import/public launch decision in the same intended ecommerce mode.
6. Run Lane F/final synthesis only after version mismatches and final launch gates are either resolved or explicitly labeled.
7. Do not delete/reimport products, click admin-like Odoo mutation paths, or mutate authenticated systems for this audit without a fresh rollback/preflight.
8. Do not use the May 10 candidate/cut-plan artifacts as the final product model. Use the 2026-05-17 reimport handoff, `product-source-repair-map-2026-05-17.md`, and the 2026-05-24 taxonomy proof together for current product-scope work.
9. Count precisely: the current taxonomy proof is 51 published Website Items, 30 checkout, 21 quote-first, and 2 duplicate source slugs excluded. Older 53-page, 15-family/47-SKU, and 18-family tranche counts are historical.
10. Treat the focused customer-note verifier as Phase 1 complete: `customer_note_checkout_preservation_contract.py` now passes in rollback-safe mode.
11. Use `ready-to-order-ecommerce-plan-deepen-2026-05-10.md`, `ready-to-order-ecommerce-goal-progress-2026-05-10.md`, `phase-5-delivery-payment-operator-packet-2026-05-10.md`, `product-import-hardening-gate-2026-05-11.md`, and `../payment-portal-live-cutover-checklist-2026-05-11.md` as active sequencing gates: Phases 1-5 are locally verifier-backed; import and live payment are the remaining backend cutover gates.
12. Treat `ready-to-order-product-cut-plan-2026-05-10.md` as historical launch-shelf evidence, not the business catalog model. There are no business quote-first products; complex/event/custom products are blocked or hidden only until source-backed purchasable behavior is implemented and verified.
13. Do not treat the current 53-product local proof as live approval. GL still needs local testing, then a separate staging/live release packet must prove Frappe Cloud, Stripe, DNS, and real payment gates.
14. Continue product-authoring work under the live-exposure lock. Use
    `product-blueprint-authoring-2026-05-14.md` and
    `capabilities/recipes/erpnext-product-blueprint-authoring.md`; do not cite
    `lt_ecommerce_paused=1` as a reason to stop local build/test work.
