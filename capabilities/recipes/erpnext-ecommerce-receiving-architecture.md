---
id: erpnext-ecommerce-receiving-architecture
name: ERPNext Ecommerce Receiving Architecture
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted ERPNext/Frappe ecommerce product import, product detail logic, cart, checkout, and invoice integration
currently_true: unknown
verification_level: 2
last_verified: 2026-05-14
evidence_quality: direct
successful_uses: 1
failed_uses: 0
regressions: 0
used_by:
  - Codex
  - OpenClaw
depends_on:
  - erpnext-catalog-variant-price-parity
  - erpnext-checkout-commerce-rules
  - fail-loud-operating-law
tags:
  - Locally Twisted
  - ERPNext
  - Frappe
  - ecommerce
  - Odoo
  - product import
  - variants
  - add-ons
  - product authoring
  - checkout
  - invoice
---

# ERPNext Ecommerce Receiving Architecture

Use this before importing, repairing, or claiming completion for Odoo-derived products in ERPNext ecommerce.

## Rule

Do not treat product transfer as the goal. ERPNext must first be able to safely receive products and integrate their meaning everywhere: backend fields, product template type, variant logic, add-on logic, cascading dependencies, dynamic pricing, media visibility, product pages, cart, checkout, Sales Order, invoice, fulfillment/operator meaning, desktop/mobile customer journeys, and fail-loud verifiers.

Odoo is a conceptual witness for mature ecommerce behavior, not infrastructure to copy. Do not import Odoo fields into ERPNext unless the ERPNext destination field, behavior owner, and verifier exist.

OpenClaw cockpit witness:
`C:/Users/baenb/.openclaw/workspace/projects/lightdeck-command-center/workstreams/locally-twisted-paid-work-cockpit.md`

## Current LT Contract

- No real product import until incomplete/awkward/missing logic is surfaced to GL and resolved.
- Current ERPNext products are test fixtures only. Future import/reopen work must prove a controlled purge/reupload/import path where products that fit the LT schema populate the correct Website Item/custom fields, preserve cascading/dependency information, and trigger expected automations. Do not treat current product records as final catalog truth.
- 2026-05-12 closeout: local ecommerce shop setup is green for backend wiring,
  catalog/import/pricing, media readiness, storefront product UX/nav/search,
  homepage verifier alignment, and the Playwright runner wrapper. Current local
  counts are 53 published Website Items, 10,674 Items, 49 templates, 10,617
  variants, 10,227 active variants, 390 disabled variants, 10,656 Item Prices,
  26 Item Attributes, and 32,028 Item Variant Attribute rows. Live launch still
  requires Frappe Cloud staging/source freeze, Cloudflare/DNS, live Stripe/site
  config/webhook, legal/policy approval where needed, one intentional live
  payment test, and final real catalog approval if the local products become
  public catalog truth.
- 2026-05-12 complex-checkout scaffold: local/source-only planning is now
  executable through `scripts/verify/complex_checkout_scaffold.py`. It maps the
  53 products into 18 direct-checkout regression guards, 4 simple-axis
  lane-flip candidates, 6 multi-color UI cases, 20 add-on/conditional blocked
  products, and 5 needs-review/missing products. This report supersedes older
  heuristic quote-first flip lists and still authorizes no live update.
- 2026-05-12 backend product-page architecture contract:
  `lt-product-page-architecture-contract-v1` is now the generic receiving
  architecture between ProductPatternContract/source semantics and product-page
  controls. It maps sale-unit axes to `selected_options`, color customization
  axes to `color_recipes`, approved add-ons to `add_ons`, review-only axes to
  `quote_context`, server-derived resolver fields to the backend, and
  Quotation/Sales Order/Sales Invoice line parity to the ERPNext document
  layer. Product pages emit the architecture JSON for browser proof, and
  product-specific rules are explicitly not allowed.
- 2026-05-12 post-review hardening: live page projection must not infer
  customization from a color-like attribute name alone. Use
  `axis_projection.live_variant_axis_projection`: source/backend recipe
  semantics keep color axes in `color_recipes`; absent recipe authority keeps
  the ERPNext variant axis in `selected_options`; explicit single-color
  sale-unit markers override recipe-looking patterns.
- 2026-05-14 staff product-authoring slice:
  `LT Product Blueprint` is the employee-facing bridge for highly customizable
  products that should not require developer-coded product packets. It validates
  options, color recipes, add-ons, conditional pricing, page type, buying path,
  and base price; previews the no-write apply plan; applies locally only behind
  role, site-config, and server-confirmation gates; keeps generated Website
  Items unpublished; and allows checkout-approved fixed-item-price blueprint
  add-ons to cascade into product options and checkout validation. Feature
  handoff: `workstreams/ecommerce-audit/product-blueprint-authoring-2026-05-14.md`.
- Test products are proof cases only: Unicorn Bouquet and Classic Arch.
- Product template types are logic/process classes:
  - `simple_product`: few options, little customization, but still backend-driven.
  - `complex_custom_product`: significant variants/options/customization/dependencies.
- Runtime/source reports must show plain labels for those types:
  `Ready-to-order page` and `Custom quote page`. Raw snake-case values are
  storage/contract values, not operator-facing labels.
- Native ERPNext/Webshop ecommerce is insufficient and may need custom DocTypes, child tables, custom fields, APIs, template overrides, pricing services, and verifiers.
- Frontend must render backend truth. Missing backend field/logic cannot be hidden by polished UI.
- Variant images are conditional: only flag missing image mapping when the source says a variant has or should expose an image. Not every variant requires its own image.

## Implemented Runtime Slice

As of 2026-05-10, the first backend preservation slice exists:

- `Website Item` has code-owned LT page-type and commerce-lane fields.
- `locally_twisted.product_page_labels` owns plain labels for page types and
  commerce lanes, and the runtime verifier fails if labels are missing or leak
  raw snake-case values.
- ERPNext Custom Field labels for the runtime fields use plain operator terms
  such as `Page Template`, `Buying Path`, and `Product Page Template`.
- `Sales Order Item`, `Sales Invoice Item`, and `Quotation Item` have
  code-owned structured configuration fields.
- `Quotation` has code-owned source Lead/product quote fields.
- `Lead` has code-owned product-page quote-handoff fields and an
  `LT Product Quote Item` child table.
- `locally_twisted.product_page_runtime` owns versioned configuration
  validation, line-field generation, quote-first paid-checkout blocking, and
  invoice-line copying.
- Guest cart entries may carry optional versioned configuration payloads.
- Variant product-page add-to-cart sends selected options as
  `lt-product-config-v1`.
- Checkout writes configuration to Sales Order Item rows.
- Payment-success invoice creation copies configuration to Sales Invoice Item
  rows.
- Explicit quote-first pages use a separate quote-first partial instead of
  falling through normal Webshop cart controls.
- If live Website Item fields are unset or still `needs_review`, runtime
  inference must be conservative: complex/multi-axis/color product pages route
  to `Custom quote page` / `quote_first`, not ready-to-order checkout.
- Quote-first pages must collect selected options and design/color notes into
  the versioned handoff payload before sending the customer to `/contact`.
  `/contact` must validate that payload loudly instead of silently replacing
  malformed details with empty arrays.
- Balloon color choices on quote-first pages must also become structured
  `color_recipes` in the quote payload, with selected values and grouped color
  metadata preserved into draft Quotation JSON.
- Source `valid_variants` must project into dependency matrices over required
  product-page axes. Color customization axes and approved add-on axes must not
  re-enter those matrices as required SKU choices.
- Dependency matrices must be executable, not just stored. The pure
  `available_options_for_selection` helper narrows available values from
  partial selections and fails loudly on impossible or unknown axes.
- `/contact` preserves a structured product-page quote payload on the Lead and
  in a child row for operator review.
- Product-page quote Leads can create an internal draft Quotation through
  `locally_twisted.product_quote_runtime`. The bridge links the source Lead,
  preserves the quote JSON/summary/version on Quotation and Quotation Item,
  marks the Lead child row drafted, and is idempotent. It does not submit,
  email, request payment, or imply customer success.
- Human-approved quote acceptance can preserve that payload when a submitted
  Quotation becomes a draft Sales Order. `product_quote_runtime` owns the
  Quotation Item to Sales Order Item copy helper, and
  `product_quote_acceptance` owns the guarded accepted-quote bridge.
- Accepted product-page quotes must store source quote and written-approval
  details on the Sales Order, preserve product-page line payloads, and fail
  loudly for draft/unsubmitted quotes, placeholder review lines, missing
  acceptance details, missing Sales Order acceptance audit/idempotency fields,
  non-ready review status, malformed payloads, zero pricing, or expired token
  links. This bridge must not submit, email, invoice, or request payment.
- `/quote-accept` is the customer-visible quote approval route. Missing,
  invalid, or expired tokens must show branded loud-failure copy and a safe
  contact fallback, not a dead page or false success.
- `/quote-accept` approval must not leave the customer on an editable form
  after success. The page must show a distinct no-payment success state that
  says no card was charged and nothing was invoiced.
- Browser coverage for `/quote-accept` must include a real temporary token
  journey, not only a static template assertion: quote preview, guest approval
  submit, one draft Sales Order, no invoice, no Payment Request, and fixture
  cleanup.
- Customer quote delivery must include the customer recipient and a
  delivery-safe business BCC. The sender must reject routed-alias BCCs such as
  `hi@locallytwisted.com` while Gmail is the SMTP sender. It may issue a token
  approval link, but it must not create an order, invoice, payment request, or
  payment path.
- Operator quote sending must go through the Quotation Desk control and the
  whitelisted `send_reviewed_product_quote_to_customer` method. It must be
  non-guest, require `Ready For Customer Review`, use the required BCC sender,
  and still create no orders, invoices, payment requests, or payment path.
- The Lead after-insert cascade calls that bridge for product-page quote Leads.
  If draft creation fails, the Lead receives record-level backend failure
  evidence.
- Draft-only quote/proposal packet review exposes product-page quote summary,
  source Lead, requested product page, page type, commerce lane, status, and
  payload for operator review.
- Draft quote/proposal packets must not treat the zero-dollar
  `LT-PRODUCT-QUOTE-REVIEW` line as customer-ready pricing. They must surface
  `Pricing review required`, block send-readiness on
  `reviewed_product_quote_pricing`, and avoid phrasing `$0.00` as a reviewed
  customer total.
- Product-page quote operator review is read-only. It may report a draft
  Quotation as `Ready For Customer Review` after scope/pricing/recipient/date/
  terms/event context checks, but it must still keep send, Sales Order, invoice,
  Payment Request, and customer acceptance disabled.
- Product-page quote token issuance and acceptance must enforce the same
  `Ready For Customer Review` status as the Desk send wrapper. Direct helper
  calls are a trust boundary; they cannot rely on UI controls for safety.
- Source contract dry-run classifies every saved Odoo/source product into
  `simple_product` or `complex_custom_product` with plain labels. Current
  source evidence classifies 15 Ready-to-order page candidates and 38 Custom
  quote page candidates while still blocking import.
- Live price-readiness now has a separate gate. Current ERPNext Item Price
  coverage passes for checkout-classified page contracts: 15 Ready-to-order
  Website Item families/pages and 47 enabled sale SKUs. Keep those counts
  separate in handoffs; 15 is not the SKU count.
- Source price-enrichment now has a separate candidate gate. Current coverage
  preserves 10,828 source variant rows and collapses them into 290 / 290
  expected import sale units: 17 source base-price units and 273
  current-live-ERPNext snapshot units. Live-snapshot candidates are explicitly
  business-review required and are not public price approval. The generated
  artifact records source combos, dropped axes, projected required combos,
  sale-unit keys, live match status, and purge status.
- Live-snapshot price candidates must have a focused business review packet
  before import/reopen claims. The packet must keep every live-snapshot sale
  unit at `business_review_required` and must not approve customer-facing
  prices by itself.
- Media visibility now has a separate read-only gate. Current ERPNext has live
  primary Website Item images for all source products and partial active
  variant-image evidence, but source media import remains blocked until extra
  images are classified and an approved parent-gallery destination exists.
- Source extra images must have a source-backed classification packet before
  gallery, variant, category, or reference media is imported. The packet must
  keep every unclassified source extra image at `hold_until_classified` and
  must not approve parent-gallery or variant assignments by itself.
- `LT-PRODUCT-QUOTE-REVIEW` is a code-owned zero-dollar review Item used when
  ERPNext refuses template Items on Quotation rows; the requested product page
  still lives in LT custom fields and JSON.
- The checkout product-family contract is all-enabled-SKU proof, not a
  representative sample. Current fixture coverage is 15 checkout Website Item
  families/pages, 47 enabled sale SKUs, 39 bouquet foil-number add-on rows,
  and 86 Sales Order/Sales Invoice rows with rollback clean.
- The confirmed `foil_number` add-on proof slice exists: `ADDON-FOIL-NUMBER`
  is code-owned, priced through ERPNext Item Price, expanded into its own Sales
  Order Item line, copied to Sales Invoice Item, and preserved in the base
  product line payload.
- `foil_number` has explicit Website Item/template eligibility. Checkout fails
  loudly if a cart payload tries to attach it to an unapproved product.
- Eligible checkout pages can render the first add-on selector surface. The
  selector is backend-gated, requires the add-on value before add-to-cart, and
  writes into the versioned cart configuration payload.
- Configured cart lines have stable line keys, so the same SKU with different
  option/add-on payloads does not collapse into one line.
- The cart API exposes visible display rows and line totals for base products
  plus priced add-ons when ecommerce is opened for controlled local testing.
  `lt_ecommerce_paused=1` is a public/live exposure safety lock, not a reason
  to stop local build work. If a route falls back to pause copy during an
  open-mode verifier, name the actual mismatch: site config, route contract,
  checkout eligibility, payment config, product mapping, or missing staging
  approval.
- The cart API must reject quote-first variants as `quote_required`; priced
  complex decor cannot be treated as retail checkout just because Item Price
  exists.
- Cart/add-on summary honesty has a focused guard: configured duplicate lines
  cannot silently fall back to item-code matching, multi-digit foil add-ons
  show selected value/quantity/line total, checkout setup errors strip
  internal item codes/custom-field names, and Stripe/receipt/thank-you labels
  preserve selected add-on values.
- Known source add-on families beyond `foil_number` must stay review-only, not
  unknown setup bugs and not paid checkout options. Current review-only source
  families are `Add ons`, `Plush add ons`, `Orbz toppers`, and `Add Bouquet`;
  GL cleared the quote-only default as a testing blocker, but it does not build
  them as paid checkout selectors.
- Review-only source add-on families must have a source-backed approval packet
  before another add-on class is built. The packet must list affected products,
  source values, the decision needed, and the safe default
  `quote_only_until_approved`; it must never mark an add-on checkout-approved
  by itself.

Primary verifier:

```powershell
python scripts/verify/complex_checkout_scaffold_contract.py
python scripts/verify/complex_checkout_scaffold.py
python scripts/verify/product_page_architecture_contract_contract.py
python scripts/verify/product_page_architecture_contract.py
python scripts/verify/product_page_architecture_readiness.py --report output/product-page-architecture-readiness.json
python scripts/verify/product_page_runtime_contract.py
python scripts/verify/product_add_on_dependency_contract.py
python scripts/verify/product_blueprint_contract.py
python scripts/verify/product_blueprint_live_contract.py
python scripts/verify/product_add_on_approval_packet.py
python scripts/verify/cart_checkout_contract.py
python scripts/verify/checkout_product_family_contract.py --report workstreams/ecommerce-audit/2026-05-10-2330-phase-1-4-shop-audit/checkout-product-family-all-skus-final.json
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

The readiness report separates `technical_architecture_ok` from
`import_reopen_ok`. A true technical architecture result means the reusable
ERPNext/Frappe template contract is built and verified; it does not mean public
ecommerce is ready.

This does not mean production ecommerce is ready. It proves the first storage,
runtime, confirmed foil-number add-on with eligibility and selector UI,
review-only boundaries for unapproved source add-on families, configured cart-line identity, Lead
quote handoff, automatic draft Quotation bridge, internal packet visibility,
accepted quote to draft Sales Order preservation, tokenized approval entry, and
BCC-gated customer quote delivery, an operator-owned Quotation send control,
source dependency-matrix preservation, plus desktop/mobile proof for the two
reusable product-page control types only.

The readiness audit is mode-sensitive. In the current local safety posture,
`product_page_architecture_readiness.py --json` is expected to report
`technical_architecture_ok: true` and `import_reopen_ok: false` while
`lt_ecommerce_paused=1` protects public/live exposure. That public exposure
lock is not a blocker for local product-authoring, generated-product, cart,
checkout, pricing, media, or verifier work. The source add-on, price-review,
and media-classification rows are still real-catalog import blockers until
approved; do not use fixture-product proof as catalog approval.
Finance/bank/payment integration is explicitly deferred and should not be
counted as a current template-architecture blocker.

## Required Gates

Before importing a product family, prove:

1. Product has a valid template type.
2. Every required source concept has a real ERPNext/custom destination.
3. Every destination exists and is executable, not just a label.
4. Required variant axes, optional add-ons, customization axes, backend-only fields, and needs-review axes are separated.
5. Server-side pricing resolves base variant, add-ons, and modifiers.
6. Product page, cart, checkout, Sales Order, invoice, and fulfillment/operator views preserve selected meaning for every enabled sellable checkout SKU, not just one sample variant.
7. Desktop and mobile journeys expose the needed choices for the template type.
8. Missing/incomplete/awkward data fails loudly through import blocker, verifier failure, admin report, customer-safe block, or GL review queue.

## Blast-Radius Checklist For Missing Features

Before building any missing ecommerce feature, write the feature's blast-radius note:

- What is missing?
- Why native ERPNext cannot handle it safely?
- What DocTypes, fields, child tables, templates, APIs, scripts, cart paths, checkout paths, invoices, and reports are affected?
- What silent failure would happen without the feature?
- What fail-loud behavior blocks fake success?
- What verifier proves the feature across backend/frontend/cart/checkout/invoice?
- What is the smallest safe proof slice?

Expected feature notes: staff product-authoring surface, add-on subsystem,
server pricing resolver, variant/media visibility, cascading option
dependencies, product-template classification, cart metadata, checkout
validation, Sales Order / invoice payload preservation, mobile journey
behavior, and import readiness gates.

## Current Research Receipt

Codex synthesis exists at
`research/expedition-erpnext-ecommerce-receiving-architecture/research-synthesis.md`.

Original conclusion: LT needed line-level product configuration preservation
before rendered product-page rebuild. The first preservation slice is now
implemented and verified, including a Lead JSON + child-row quote handoff and a
confirmed `foil_number` add-on proof slice. Internal draft Quotation creation is
verified and wired into the Lead cascade, and accepted product-page quotes can
now create draft Sales Orders through a tokenized acceptance route without
finance side effects. The first customer quote sender is BCC-gated and verified
with stubbed email delivery. Product-family add-on dependencies and
additional add-on classes, broader price resolver coverage, media
classification, deeper family-specific dependency rules, and mobile/desktop UX gates remain
open.

Focused evidence:

```powershell
python scripts/verify/proof_product_contract.py
python scripts/verify/product_page_runtime_contract.py
python scripts/verify/product_page_contract_source_audit.py
python scripts/verify/product_page_price_readiness_contract.py
python scripts/verify/product_page_price_enrichment_contract.py
python scripts/verify/product_page_price_review_packet.py
python scripts/verify/product_page_media_visibility_contract.py
python scripts/verify/product_page_media_classification_packet.py
python scripts/verify/variant_media_contract.py
python scripts/verify/product_quote_acceptance_contract.py
npm run test:quote-accept-experience
python scripts/verify/product_quote_customer_delivery_contract.py
python scripts/verify/product_quote_operator_send_control_contract.py
python scripts/verify/product_quote_customization_contract.py
python scripts/verify/product_page_dependency_contract.py
npm run test:ecommerce-full
```

Expected current result: proof product contract and runtime contract pass;
live price-readiness passes for current checkout-classified ERPNext prices;
source price-enrichment passes for candidate coverage while marking
live-snapshot candidates review-needed;
variant media passes against open guest product routes; source contract audit
and media visibility still block destructive import until media classification,
color customization, review-only axes, and price business-review decisions are
handled.

## Research Requirement

Before implementation, use the current synthesis as the starting point. Further
research is only needed for unresolved design decisions or new product classes.
Research must cover both:

- ERPNext/Frappe implementation patterns and sharp edges for custom ecommerce logic.
- Odoo ecommerce concepts/behaviors that should be recreated safely inside ERPNext.

Any future brief must be stranger-ready and exact to the current stack; do not
dispatch a history-heavy handoff.

## Verification Pattern

A future verifier suite must report per product and per feature:

- verified
- needs review
- broken
- unverifiable from source

It must check import contract, backend field existence, option/variant reachability, add-on rules, price parity/resolution, media mapping where source provides it, frontend visibility, cart payload, checkout totals, Sales Order/invoice preservation, and mobile/desktop customer journey exposure.

## Red Flags

- Product page looks correct but Sales Order/invoice loses selected choices.
- Imported field has no ERPNext/custom destination.
- Frontend JS owns price/option/add-on truth without backend validation.
- Add-on appears as a visual card but lacks cart/invoice behavior.
- ERPNext native dropdowns flatten Odoo-style dependencies or availability rules.
- A missing field produces empty UI instead of a blocker/report.
- A proof product works by hardcoding rather than reusable template contract.
- Product migration is described as complete because records exist.
