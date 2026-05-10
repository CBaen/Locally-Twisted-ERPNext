---
id: erpnext-ecommerce-receiving-architecture
name: ERPNext Ecommerce Receiving Architecture
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted ERPNext/Frappe ecommerce product import, product detail logic, cart, checkout, and invoice integration
currently_true: backend_preservation_foil_addon_draft_quotation_live_checkout_price_price_enrichment_and_media_visibility_gates_verified_public_ecommerce_paused
verification_level: 2
last_verified: 2026-05-10
evidence_quality: GL decision + official docs + live DB metadata + current code inspection + focused source verifiers + live price-readiness verifier + source price-enrichment verifier + media visibility verifier + rollback-safe runtime verifier + cart/checkout contract verifier
successful_uses: 1
failed_uses: 0
regressions: 0
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
  - checkout
  - invoice
---

# ERPNext Ecommerce Receiving Architecture

Use this before importing, repairing, or claiming completion for Odoo-derived products in ERPNext ecommerce.

## Rule

Do not treat product transfer as the goal. ERPNext must first be able to safely receive products and integrate their meaning everywhere: backend fields, product template type, variant logic, add-on logic, cascading dependencies, dynamic pricing, media visibility, product pages, cart, checkout, Sales Order, invoice, fulfillment/operator meaning, desktop/mobile customer journeys, and fail-loud verifiers.

Odoo is a conceptual witness for mature ecommerce behavior, not infrastructure to copy. Do not import Odoo fields into ERPNext unless the ERPNext destination field, behavior owner, and verifier exist.

## Current LT Contract

- No real product import until incomplete/awkward/missing logic is surfaced to GL and resolved.
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
- `/contact` preserves a structured product-page quote payload on the Lead and
  in a child row for operator review.
- Product-page quote Leads can create an internal draft Quotation through
  `locally_twisted.product_quote_runtime`. The bridge links the source Lead,
  preserves the quote JSON/summary/version on Quotation and Quotation Item,
  marks the Lead child row drafted, and is idempotent. It does not submit,
  email, request payment, or imply customer success.
- Future human-approved quote acceptance must preserve that payload when a
  Quotation becomes a Sales Order. `product_quote_runtime` owns the
  Quotation Item to Sales Order Item copy helper; it must not create, submit,
  email, invoice, or request payment.
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
- Source contract dry-run classifies every saved Odoo/source product into
  `simple_product` or `complex_custom_product` with plain labels. Current
  source evidence classifies 15 Ready-to-order page candidates and 38 Custom
  quote page candidates while still blocking import.
- Live price-readiness now has a separate gate. Current ERPNext Item Price
  coverage passes for checkout-classified page contracts: 15 Ready-to-order
  page candidates and 47 expected sale units.
- Source price-enrichment now has a separate candidate gate. Current coverage
  preserves 10,828 source variant rows and collapses them into 290 / 290
  expected import sale units: 17 source base-price units and 273
  current-live-ERPNext snapshot units. Live-snapshot candidates are explicitly
  business-review required and are not public price approval. The generated
  artifact records source combos, dropped axes, projected required combos,
  sale-unit keys, live match status, and purge status.
- Media visibility now has a separate read-only gate. Current ERPNext has live
  primary Website Item images for all source products and partial active
  variant-image evidence, but source media import remains blocked until extra
  images are classified and an approved parent-gallery destination exists.
- `LT-PRODUCT-QUOTE-REVIEW` is a code-owned zero-dollar review Item used when
  ERPNext refuses template Items on Quotation rows; the requested product page
  still lives in LT custom fields and JSON.
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
  plus priced add-ons. Current public `/cart` and `/checkout` still redirect to
  the pause page for guests.
- The cart API must reject quote-first variants as `quote_required`; priced
  complex decor cannot be treated as retail checkout just because Item Price
  exists.
- Cart/add-on summary honesty has a focused guard: configured duplicate lines
  cannot silently fall back to item-code matching, multi-digit foil add-ons
  show selected value/quantity/line total, checkout setup errors strip
  internal item codes/custom-field names, and Stripe/receipt/thank-you labels
  preserve selected add-on values.

Primary verifier:

```powershell
python scripts/verify/product_page_runtime_contract.py
python scripts/verify/cart_checkout_contract.py
npm run test:product-quote-first
```

This does not mean public ecommerce is ready. It proves the first storage,
runtime, confirmed foil-number add-on with eligibility and selector UI, configured cart-line identity, Lead
quote handoff, automatic draft Quotation bridge, internal packet visibility, and
desktop/mobile proof for the two reusable product-page control types only.

## Required Gates

Before importing a product family, prove:

1. Product has a valid template type.
2. Every required source concept has a real ERPNext/custom destination.
3. Every destination exists and is executable, not just a label.
4. Required variant axes, optional add-ons, customization axes, backend-only fields, and needs-review axes are separated.
5. Server-side pricing resolves base variant, add-ons, and modifiers.
6. Product page, cart, checkout, Sales Order, invoice, and fulfillment/operator views preserve selected meaning.
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

Expected feature notes: add-on subsystem, server pricing resolver, variant/media visibility, cascading option dependencies, product-template classification, cart metadata, checkout validation, Sales Order / invoice payload preservation, mobile journey behavior, and import readiness gates.

## Current Research Receipt

Codex synthesis exists at
`research/expedition-erpnext-ecommerce-receiving-architecture/research-synthesis.md`.

Original conclusion: LT needed line-level product configuration preservation
before rendered product-page rebuild. The first preservation slice is now
implemented and verified, including a Lead JSON + child-row quote handoff and a
confirmed `foil_number` add-on proof slice. Internal draft Quotation creation is
now verified and wired into the Lead cascade, but the operator quote-edit/review/send/acceptance workflow,
product-family add-on dependencies and additional add-on classes, broader price resolver coverage, media
classification, color recipes, dependencies, and mobile/desktop UX gates remain
open.

Focused evidence:

```powershell
python scripts/verify/proof_product_contract.py
python scripts/verify/product_page_runtime_contract.py
python scripts/verify/product_page_contract_source_audit.py
python scripts/verify/product_page_price_readiness_contract.py
python scripts/verify/product_page_price_enrichment_contract.py
python scripts/verify/product_page_media_visibility_contract.py
python scripts/verify/variant_media_contract.py
```

Expected current result: proof product contract and runtime contract pass;
live price-readiness passes for current checkout-classified ERPNext prices;
source price-enrichment passes for candidate coverage while marking
live-snapshot candidates review-needed;
variant media passes through authenticated/internal product-page access while
guest product routes stay paused; source contract audit and media visibility
still block destructive import until media classification, color customization,
review-only axes, and price business-review decisions are handled.

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
