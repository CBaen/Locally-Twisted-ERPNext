# ERPNext Ecommerce Receiving Architecture

Status: active peer-agent handoff; core technical architecture and Phase 1-4
ready-to-order/quote-boundary proof are verified, but the current public/local
posture is paused by `lt_ecommerce_paused=1`. No destructive import, public
checkout, live payment, or production cutover is approved.
Owner context: Codex, 2026-05-09. GL explicitly redirected this lane away from OpenClaw cockpit/infrastructure work and toward backend-first product-page architecture.

## Prime directive

Do not migrate products as the goal. Build the ERPNext ecommerce receiving ecosystem first.

A product is not "received" when a record exists. It is received only when its field data, option logic, price logic, add-on logic, image/media relationships where applicable, cart behavior, checkout behavior, Sales Order / invoice meaning, fulfillment/operator meaning, and customer journey all have safe homes inside the ERPNext/Frappe system and fail loudly when incomplete.

## GL decision / framing

- ERPNext native ecommerce is visually, logically, and operationally insufficient for Locally Twisted.
- Odoo ecommerce is not the target infrastructure, but it is the conceptual witness for mature ecommerce behavior: variant-driven prices, variant media logic, backend-fed fields, option availability, add-ons, and meaningful configured cart/checkout payloads.
- Do not create or import Odoo-style fields that ERPNext cannot actually store/use. Unsupported fields silently fail unless the ERPNext receiving architecture exists first.
- Any incomplete, awkward, or unmappable logic must be brought to GL with plain explanation before import or build.
- If ERPNext native ecommerce cannot represent a required feature, design the missing ERPNext-side feature deliberately, including blast radius and cascading effects, before building it.
- Test products may be used as proof cases only. They are not proof of migration completion.

## Template types

These are logic/process classes, not product families.

1. `simple_product`
   - Few options and little customization.
   - Needs clear fields, media, option visibility, add-ons where allowed, dynamic price truth, cart/checkout/invoice preservation, and mobile/desktop flows.

2. `complex_custom_product`
   - Significant options, variants, customization, dependencies, or quote/checkout complexity.
   - Needs stronger cascading logic, unavailable-combination handling, customization axes, add-ons, dynamic pricing, visual option systems, quote-required escape paths, and invoice/operator detail preservation.

Unicorn Bouquet and Classic Arch are proof cases for these flows, not the ontology. Most future products should map to one of these two logic classes unless a researched exception proves a third class is required.

## Required receiving ecosystem

Before real import, define and verify:

- Product type classification and template assignment.
- Required backend fields and optional backend fields.
- Odoo concept -> ERPNext native/custom/missing/unsafe mapping.
- Destination existence for every imported field.
- Required variant axes vs optional add-ons vs customization axes vs backend-only fields vs needs-review fields.
- Add-on contract: eligibility, fields, dependencies, quantity, price, cart, tax, invoice, fulfillment notes.
- Server-authoritative pricing: frontend previews may exist, but backend/cart/checkout/invoice decide truth.
- Media/variant visibility: only flag missing variant images when source says a variant has/should expose one; not every variant requires its own image.
- Product detail rendering from backend truth; no frontend fake-success when backend fields are missing.
- Mobile and desktop customer journeys for each template type.
- Sales Order / invoice / fulfillment preservation of selected choices and add-ons.
- Fail-loud verifiers and reports.

## Explicit stop conditions

Stop and bring to GL if:

- A needed destination field/DocType/child table does not exist.
- A behavior exists only in frontend JS and not in backend/cart/checkout truth.
- A source Odoo concept maps only to a field label, not to executable ERPNext behavior.
- A price cannot be resolved authoritatively.
- Add-on dependencies or required fields are unclear.
- Cart, checkout, Sales Order, or invoice cannot preserve the configured product meaning.
- Mobile journey would hide or bury required decisions.
- A verifier cannot distinguish complete, incomplete, broken, and unverifiable.

## Blast-radius register required before building missing features

Each missing feature must get a small design review before implementation:

- What is missing?
- Why native ERPNext ecommerce cannot handle it safely?
- What records, fields, pages, APIs, templates, scripts, cart paths, checkout paths, and invoices are affected?
- What can silently fail?
- How does it fail loudly?
- What verifier proves it?
- What is the lowest-risk implementation path?

Expected feature entries include variant logic, add-on subsystem, server pricing resolver, variant/media visibility, custom option dependencies, product-template classification, cart/checkout metadata, invoice/order preservation, mobile journey behavior, and import readiness gates.

## Research requirement before build

Use the Claude `research-brief` skill shape first, then dispatch `/expedition` after GL approves the brief.

Brief must be exact to this stack:

- ERPNext/Frappe v15 in Docker/Frappe app `locally_twisted`.
- Current Webshop item override under `apps/locally_twisted/locally_twisted/templates/generators/item/`.
- Current product contract starter under `apps/locally_twisted/locally_twisted/catalog_contract/`.
- Odoo source is read-only reference at `C:/Users/baenb/projects/locally-twisted-odoo/` and old Odoo shop behavior is conceptual/reference input, not infrastructure to copy.
- Native ERPNext ecommerce is insufficient; research must identify implementation patterns and risks for building a safer ERPNext-side ecommerce logic layer.

No code/product import until research brief -> expedition -> synthesis -> GL architecture checkpoint.

## Current code facts to verify before expedition

Known current starting points from 2026-05-09 inspection:

- `catalog_contract/models.py` models a starter `ProductPageContract` with required axes, customization axes, add-ons, gallery, warnings, resolver-price presence, but it is too shallow for complete receiving architecture.
- `catalog_contract/addon_rules.py` confirms only `Add Foil Number` as a real add-on; other possible add-on axes are review-only.
- `catalog_contract/source_builder.py` originally separated required axes, color customization axes, confirmed add-ons, and warnings, but did not yet own full template type, dependency rules, invoice payloads, or complete fail-loud import gates. The completed slices below now cover template classification and required-axis source dependency matrices; deeper family-specific dependency rules and import gates remain open.
- `templates/generators/item/item_configure.html` currently renders inline ERPNext variant selectors, color drawers, variant price lookup, and variant image updates; it still contains temporary bridge logic and is not a complete product receiving ecosystem.

Treat these as current evidence to re-check, not final truth.

## Codex research synthesis - 2026-05-09

Durable research artifact:
`research/expedition-erpnext-ecommerce-receiving-architecture/research-synthesis.md`

OpenClaw cockpit witness:
`C:/Users/baenb/.openclaw/workspace/projects/lightdeck-command-center/workstreams/locally-twisted-paid-work-cockpit.md`

Current conclusion:

- ERPNext's transactional product unit is the concrete Item/variant, not the product template.
- LT's current product page/cart/checkout path can resolve a variant and server price, but it drops structured product configuration before Sales Order Item and Sales Invoice Item.
- Live ERPNext has LT custom fields on Website Item and Sales Order header, but no LT fields on Sales Order Item or Sales Invoice Item for selected options/add-ons/customization.
- Source contract verification proves the proof-product shape is useful but real import is still blocked: resolver-backed prices, media classification, high-cardinality color customization, and nine review-only axes need architecture before product migration.
- The first build slice should be backend preservation, not page rendering: line-level configuration storage, server-side resolver, cart payload versioning, checkout write, invoice copy, and verifiers.

## Backend preservation slice - 2026-05-10

Implemented first durable ERPNext-side runtime layer for the two reusable
product-page types. This is not product migration and does not make the public
shop ready to reopen.

Completed:

- Added code-owned `Website Item` fields for reusable page type and commerce
  lane: `lt_product_page_type` and `lt_commerce_lane`.
- Added a pure label map for reusable page types and commerce lanes so runtime
  and source-audit reports can show plain operator/customer labels instead of
  leaking raw snake-case values.
- Updated ERPNext Custom Field labels for the core template fields: `Page
  Template`, `Buying Path`, and `Product Page Template` replace raw LT/internal
  labels in Website Item, Quotation, and line-item child tables.
- Added line-level configuration fields to `Sales Order Item` and
  `Sales Invoice Item`: template item, page type, schema version,
  human-readable summary, and machine-readable JSON.
- Added Lead quote-handoff fields and `LT Product Quote Item` child rows for
  quote-first product pages: requested product page, product-page type, product
  quote summary, structured JSON quote payload, and operator-review status.
- Added `locally_twisted.product_page_runtime` as the server-owned runtime
  contract for configuration validation, quote-first checkout blocking,
  Sales Order Item field generation, and invoice-line copy.
- Updated the guest cart schema to preserve an optional versioned
  `configuration` payload instead of only `item_code` and `qty`.
- Updated product variant add-to-cart to send `lt-product-config-v1` selected
  option payloads.
- Updated checkout line resolution to write the structured configuration to
  Sales Order Item rows, and updated payment-success invoice creation to copy
  the same payload onto Sales Invoice Item rows.
- Added a quote-first product-page partial and runtime context so explicit
  `quote_first` pages do not fall through Webshop's add-to-cart controls.
- Updated `/contact` intake so product-page quote links preserve a structured
  product-page quote payload on the Lead instead of only free-text notes.
- Added code-owned Quotation header fields and `Quotation Item` configuration
  fields so quote-first product-page meaning can continue past Lead intake.
- Added `locally_twisted.product_quote_runtime` as the internal draft
  Quotation bridge from a product-page quote Lead. It creates a draft only,
  links back to the source Lead, preserves the quote payload on the Quotation
  and Quotation Item, marks the Lead child row drafted, and is idempotent.
- Wired the Lead after-insert cascade so product-page quote Leads automatically
  create that internal draft Quotation. If draft creation fails, the Lead gets
  record-level backend failure evidence instead of silently stopping at intake.
- Updated the draft-only quote/proposal packet review so product-page quote
  summary, source Lead, requested product page, page type, commerce lane,
  status, and payload are visible in the operator review fields.
- Added code-owned zero-dollar `LT-PRODUCT-QUOTE-REVIEW` because ERPNext
  rejects variant template Items on Quotation rows. The requested template page
  is preserved in LT custom fields and JSON instead of being flattened.
- Added `scripts/verify/product_page_runtime_contract.py`, which proves
  field existence, versioned cart configuration, Sales Order Item
  preservation, Sales Invoice Item preservation, quote-first checkout blocking,
  structured Lead quote payload preservation, automatic draft Quotation
  cascade, Quotation Item payload preservation, internal packet visibility,
  product-page template labels, idempotency, and stale-cart loud failure in a
  rolled-back live ERPNext transaction.
- Updated the source contract dry-run so every saved Odoo/source product is
  classified into one of the two reusable template types with plain labels.
  Current source-audit classification is 15 `simple_product` /
  Ready-to-order page candidates and 38 `complex_custom_product` / Custom quote
  page candidates. The audit remains blocked for import because resolver
  prices, gallery/media classification, color customization handling, and
  review-only axes are still unresolved.
- Added a separate live price-readiness gate so current ERPNext checkout price
  coverage is not confused with source reimport readiness. The current live DB
  has active Item Price coverage for all checkout-classified contract sale
  units: 15 Ready-to-order page candidates and 47 sale units. Source
  `erpnext_variant_price` enrichment is still missing for destructive
  purge/import and remains a separate blocker.
- Added a separate source price-enrichment gate and candidate artifact for
  purge/reimport rehearsal. Current row-level coverage preserves 10,828 source
  variant rows and collapses them into 290 / 290 expected import sale units:
  17 source base-price units and 273 current-live-ERPNext snapshot units. This
  closes price-candidate coverage, but the 273 live-snapshot candidates are
  explicitly marked business-review required and are not public price approval.
  The generated candidate artifact records source combos, dropped axes,
  projected required combos, sale-unit keys, live match status, and purge
  status. Price enrichment passes, while purge/reimport remains blocked for 49
  products because non-price review gates still exist.
- Added a focused business price review packet extracted from the price
  enrichment artifact. `python scripts/verify/product_page_price_review_packet.py`
  writes `audits/odoo-erpnext-migration-audit-2026-05-08/24-product-page-price-review-packet.md`
  and `.json` with only the live-snapshot-priced sale units that still need
  approval or replacement. Current packet covers 36 products and 273 review
  units, with 0 approved public prices.
- Added a separate read-only media visibility gate so live primary/variant
  image behavior is not confused with approved source media classification.
  Current live ERPNext has primary `Website Item` images for all 53 source
  products and 1,751 active variant image rows, but source media is still
  blocked for import because 95 extra images across 49 products are
  unclassified and no ERPNext `Website Slideshow` records exist for approved
  parent-gallery media.
- Added a source-backed media classification packet for those unclassified
  source extras. `python scripts/verify/product_page_media_classification_packet.py`
  writes `audits/odoo-erpnext-migration-audit-2026-05-08/23-product-page-media-classification-packet.md`
  and `.json` with one row per source extra image, allowed roles, and the
  enforced safe default `hold_until_classified`. Current packet covers 49
  products and 95 source extra images, with 0 approved parent-gallery images
  and 0 assigned variant images.
- Added the first confirmed add-on runtime slice for `foil_number`:
  `ADDON-FOIL-NUMBER` is a code-owned ERPNext Item with a Standard Selling
  price, checkout expands it into an explicit Sales Order Item line, invoices
  copy its structured payload, and the base product line preserves the selected
  add-on in JSON.
- Added explicit `foil_number` eligibility at the Website Item/template level.
  Checkout now fails loudly if a cart payload tries to attach that add-on to an
  unapproved product instead of treating every bouquet-like SKU as eligible.
- Added the first product-page add-on selector surface for eligible checkout
  pages. The selector renders only when backend eligibility says the page can
  use the add-on, requires a number before add-to-cart, and writes the add-on
  into the same versioned cart configuration payload used by checkout.
- Updated cart identity to use configured line keys, so the same SKU with
  different selected add-ons/options does not collapse into one cart line.
- Updated the cart API and cart/checkout summary rendering to expose visible
  base-plus-add-on display rows and line totals when ecommerce is deliberately
  opened for controlled proof. Current public/local posture is paused with
  `lt_ecommerce_paused=1`, and the data/display contract is no longer
  base-item-only.
- Hardened configured cart/add-on customer honesty: multi-digit foil add-ons
  now expose selected value, add-on quantity, unit price, and add-on total in
  cart/checkout summaries; cart and checkout no longer fall back from a
  configured line key to item code when server normalization drifts; customer
  checkout setup errors strip internal item codes/custom-field names; and
  Stripe, thank-you, receipt, and operator summary labels preserve selected
  add-on values without exposing parent/internal setup text.
- Added the first add-on dependency boundary. Known but unapproved source
  add-on families (`Add ons`, `Plush add ons`, `Orbz toppers`, `Add Bouquet`)
  are explicit review-only contracts and route to quote instead of paid
  checkout. The source audit now writes
  `15-product-page-contract-source-audit.json` with review-only family counts:
  `Add ons` 3, `Plush add ons` 3, `Orbz toppers` 2, and `Add Bouquet` 1.
- Added a source-backed add-on approval packet for those review-only families.
  `python scripts/verify/product_add_on_approval_packet.py` writes
  `audits/odoo-erpnext-migration-audit-2026-05-08/22-product-add-on-approval-packet.md`
  and `.json` with affected products, source values, decision needed, and the
  enforced safe default `quote_only_until_approved`. Current packet covers 4
  review axes, 9 affected products, and 0 checkout-approved add-ons.
- Hardened quote-first product pages past a simple contact link. The
  quote-first partial now renders reusable option/custom-note controls,
  writes selected options and design/color notes into the versioned product
  quote handoff, and `/contact` normalizes that payload instead of silently
  dropping bad shapes to empty arrays.
- Added the first structured color recipe preservation slice. Quote-first
  balloon color choices now become `color_recipes` with selected values,
  grouped color metadata, and operator-review status; the Lead-to-draft
  Quotation bridge preserves that structure on Quotation and Quotation Item
  JSON instead of flattening colors into loose notes only.
- Added the first source-backed option dependency matrix slice. Source
  `valid_variants` are projected onto required product-page axes after color
  customization and add-on axes are removed, so the reusable contract can
  preserve available combinations without turning colors or add-ons back into
  required SKU selectors.
- Added the first executable dependency helper for those matrices.
  `available_options_for_selection` narrows available axis values from a
  partial selection and fails loudly for impossible combinations or unknown
  axes instead of letting invalid frontend choices look valid.
- Added runtime fallback inference for live Website Items whose `Page
  Template` / `Buying Path` fields are unset or still `needs_review`. Complex
  live variant axes, especially balloon color axes and multi-axis arch-style
  products, route to `Custom quote page` / `quote_first` instead of falling
  through ready-to-order Webshop controls.
- Cart resolution now blocks quote-first variants as `quote_required` instead
  of letting priced complex decor enter the retail cart lane.
- Hardened draft quote/proposal packets for quote-first placeholder pricing.
  Product-page draft Quotations that still use the zero-dollar
  `LT-PRODUCT-QUOTE-REVIEW` line now surface `Pricing review required`, block
  send-readiness on `reviewed_product_quote_pricing`, and no longer phrase a
  placeholder `$0.00` as a reviewed customer total.
- Added a quote-to-order preservation helper for the human-approved acceptance
  path. It copies LT product-page line configuration from Quotation Item to
  Sales Order Item without submitting, emailing, invoicing, or requesting
  payment.
- Added the first internal operator-review evaluator for product-page quote
  Quotations. It reports placeholder review lines, zero-dollar pricing,
  malformed payloads, missing recipient/date/terms/event context, and a
  read-only `Ready For Customer Review` state. It does not send, create Sales
  Orders, create invoices, request payment, or enable acceptance.
- Added the first accepted-product-quote bridge. A submitted, priced,
  human-accepted product-page Quotation can create a draft Sales Order only,
  store the source quote plus written-approval details on Sales Order fields,
  and preserve the product-page payload on Sales Order Item rows. Placeholder
  review lines, draft/unsubmitted quotes, missing acceptance details, missing
  Sales Order acceptance audit fields, non-ready review status, malformed
  payloads, zero pricing, and expired quotes fail loudly. The bridge does not
  create invoices, payment requests, Email Queue rows, or Communications.
- Added the first customer-visible quote approval entry point at
  `/quote-accept`. Approval links are tokenized and hashed on the Quotation;
  missing, invalid, or expired links show a branded loud failure instead of a
  blank/dead route.
- Added the first `/quote-accept` customer-experience gate. Missing approval
  codes fail loudly with a safe `/contact` fallback, successful approval
  replaces the editable form with a distinct no-payment success panel, and the
  browser gate now creates a temporary real token, previews the quote, submits
  guest approval, confirms one draft Sales Order, confirms no invoice/payment
  request, and cleans up the fake records.
- Added the first customer quote sender. It sends reviewed product-page quote
  approval links to the customer, requires a delivery-safe business BCC,
  rejects routed-alias BCCs such as `hi@locallytwisted.com`, and does not
  create Sales Orders, invoices, payment requests, Email Queue rows, or
  Communications in the rollback-safe contract.
- Added the first operator-owned send control for reviewed product-page quotes.
  Submitted Quotations marked `Ready For Customer Review` get a Quotation Desk
  button that calls a non-guest whitelisted method, sends the approval link
  through the BCC-gated sender, and still creates no orders, invoices, payment
  requests, Email Queue rows, or Communications in the rollback-safe contract.

Verified 2026-05-10:

- `python scripts/verify/product_page_runtime_contract.py` PASS.
  Current runtime coverage includes Quotation Item to Sales Order Item payload
  copy for a future accepted quote path.
- `python scripts/verify/cart_checkout_contract.py` PASS.
  Current cart coverage includes review-only source add-ons routing to quote
  instead of paid checkout.
- `python scripts/verify/product_add_on_dependency_contract.py` PASS.
  Current add-on dependency coverage proves confirmed `foil_number` remains a
  priced checkout add-on while the four source add-on families still needing
  product-family mapping cannot enter paid checkout.
- `python scripts/verify/product_add_on_approval_packet.py` PASS. Current
  packet covers `Add Bouquet`, `Add ons`, `Orbz toppers`, and
  `Plush add ons`; all default to `quote_only_until_approved` and none are
  approved for checkout.
- `python scripts/verify/quote_proposal_draft_packet_contract.py` PASS.
  Current contract includes the quote-first placeholder-pricing outlier and
  the reviewed-product-quote-still-draft-only scenario.
- `python scripts/verify/product_quote_operator_review_contract.py` PASS.
  Current contract covers placeholder zero-price blockers, malformed payload
  blockers, and a reviewed internal-ready quote that still forbids send/order/payment.
- `python scripts/verify/product_quote_operator_review.py --report output/product-quote-operator-review.json`
  PASS. Current fake-data site has 0 persisted product quote Quotations after
  rollback-safe tests, so the live report is empty and non-mutating.
- `python scripts/verify/product_quote_acceptance_contract.py` PASS. Current
  coverage creates a rollback-safe submitted product quote, records acceptance
  fields on a draft Sales Order, preserves LT product-page line payloads, and
  confirms Sales Invoice, Payment Request, Email Queue, and Communication
  counts do not change. It also proves token link creation and expired-token
  failure behavior. The 2026-05-10 review closeout added direct coverage for
  missing Sales Order acceptance audit/idempotency fields and for
  `Needs Operator Review` quotations blocking token issuance and acceptance.
- `Invoke-WebRequest http://localhost:8081/quote-accept` returned HTTP 200 with
  `Review your quote`, branded `Tiny snag` failure copy, and `/contact`
  fallback for a missing token.
- `npm run test:quote-accept-experience` PASS. Current browser coverage proves
  missing approval-code failure copy, safe contact fallback, no editable form
  in the failure state, a distinct post-approval no-payment success panel in
  the route template, and a real temporary token journey through public preview
  plus guest approval submission.
- `python scripts/verify/product_quote_customer_delivery_contract.py` PASS.
  Current coverage stubs `frappe.sendmail`, verifies the customer recipient,
  required delivery-safe business BCC, routed-alias BCC rejection,
  `/quote-accept` approval link, no internal marker leaks in the email body,
  and no order/finance/email record count changes.
- `python scripts/verify/product_quote_operator_send_control_contract.py` PASS.
  Current coverage proves the Quotation Desk button hook exists, the operator
  method is whitelisted but not guest-callable, only quotes marked
  `Ready For Customer Review` can send, required BCC is present, and
  order/finance/email record counts do not change.
- `python scripts/verify/product_quote_customization_contract.py` PASS.
  Current coverage proves quote-first balloon color choices become structured
  `color_recipes`, carry grouped color metadata, survive draft Quotation
  creation, and malformed color payloads fail loudly.
- `python scripts/verify/product_page_dependency_contract.py` PASS. Current
  source coverage proves Classic Arch preserves 848 source rows as 16
  required-axis combinations across Arch Size, Design, and LED Lights, while
  excluding `latex colors` from required dependency axes. Unicorn Bouquet
  preserves 30 source rows as 3 Bouquet Size combinations after foil-number
  add-on removal. The same verifier now proves executable dependency
  availability narrowing and loud failure for impossible/unknown selections.
- `python scripts/verify/product_page_architecture_readiness.py` passed in a
  temporary open-commerce proof with `technical_architecture_ok: True`,
  `import_reopen_ok: True`, 14 pass rows, 0 blocked rows, and 1 finance
  deferral. In current paused posture, `import_reopen_ok` should be false only
  because the public ecommerce switch is intentionally off.
- `npm run test:product-quote-first` PASS. This authenticated browser gate
  now covers both reusable product-page controls at desktop and mobile widths:
  Classic Arch renders quote-first controls and carries selected notes into
  the `/contact` hidden product-quote payload, while Unicorn Bouquet keeps
  ready-to-order variant controls and eligible add-ons.
- `python scripts/verify/ecommerce_pause_contract.py` PASS in the restored
  paused launch posture.
- `npm run test:ecommerce-full` PASS when ecommerce is temporarily opened for
  controlled local testing: public ecommerce mode, shop smoke, product prices,
  variant media, checkout experience, checkout fulfillment, and
  checkout-to-Lead conversion. This is regression evidence, not the current
  public mode.
- Public website verification also passed in the pages/forms-first paused
  posture through `website_launch_verify.py --with-a11y --with-contact-smoke`;
  open-commerce checks remain a separate regression gate when the switch is
  intentionally reopened.
- `python scripts/verify/product_page_architecture_contract_contract.py` PASS.
  Current coverage proves the generic product-page architecture maps sale-unit
  axes to `selected_options`, color customization axes to `color_recipes`,
  approved add-ons to `add_ons`, review-only add-ons to `quote_context`, and
  forbids product-specific architecture rules.
- `python scripts/verify/product_page_architecture_contract.py` PASS. Current
  source/live coverage checks 53 products, 18 checkout-allowed and 35
  quote-first-allowed, with backend-owned payload targets and SO/SI/Quotation
  parity. Generated evidence lives under ignored
  `output/product-page-architecture-contract.*`.
- `python scripts/verify/lead_backend_intake_parity.py` PASS.
- `python scripts/verify/customer_contact_points_contract.py` PASS.
- `python scripts/verify/customer_email_policy_contract.py` PASS.
- `python scripts/verify/proof_product_contract.py` PASS.
- `python scripts/verify/product_page_contract_source_audit.py` produced the
  expected BLOCKED report plus JSON artifact with template classification,
  import blockers, and review-only source add-on counts.
- `python scripts/verify/product_page_price_readiness_contract.py` PASS and
  wrote `audits/odoo-erpnext-migration-audit-2026-05-08/19-product-page-price-readiness-report.md`.
- `python scripts/verify/product_page_price_enrichment_contract.py` PASS and
  wrote `audits/odoo-erpnext-migration-audit-2026-05-08/21-product-page-price-enrichment-report.md`
  plus `21-product-page-price-enrichment-candidates.json`.
- `python scripts/verify/product_page_price_review_packet.py` PASS. Current
  packet covers 36 products and 273 live-snapshot-priced sale units, all kept
  at `business_review_required` with 0 approved public prices. GL cleared this
  packet as an import/reopen business blocker for testing; keep the provenance
  visible in any import rehearsal.
- `python scripts/verify/product_page_media_visibility_contract.py` produced
  the expected BLOCKED report at
  `audits/odoo-erpnext-migration-audit-2026-05-08/20-product-page-media-visibility-report.md`.
- `python scripts/verify/product_page_media_classification_packet.py` PASS.
  Current packet covers 49 products and 95 source extra images; every image
  remains `review_needed` with safe default `hold_until_classified`. GL cleared
  this packet as an import/reopen business blocker for testing; it is still the
  source evidence trail before any actual media assignment.
- `python scripts/verify/variant_media_contract.py` PASS against open guest
  product routes and variant image swap behavior.
- `npm run test:checkout-experience` PASS against the open-mode cart/checkout
  route contract when ecommerce is intentionally reopened for testing.
- Authenticated product-page render check for temporarily marked
  `unicorn-bouquet` checkout page returned HTTP 200, rendered
  `lt-product__addons`, and had no server exception; the Website Item fields
  were restored to `needs_review` afterward.
- `python scripts/verify/verifier_cli_contract.py` PASS.
- `python scripts/dev/clear_website_cache.py` completed after Jinja/CSS edits.
- `npm run test:product-quote-first` now also proves the emitted
  `.js-lt-product-page-architecture` JSON on quote-first and ready-to-order
  product pages.
- Post-review regression, 2026-05-12: live color-axis projection now uses the
  carried source/backend contract instead of classifying by attribute name.
  Source recipe axes such as `7-butterfly-column` stay `customization` ->
  `color_recipes`; ERPNext-only color variant axes without that source signal
  stay `sale_unit` -> `selected_options`. Browser proof now opens
  `7-butterfly-column`, selects a visible color, adds it to the local cart, and
  asserts the payload keeps the color in `color_recipes` with no color in
  `selected_options`.

## Backend product-page architecture contract - 2026-05-12

Implemented `lt-product-page-architecture-contract-v1` as the corrected
architecture layer between ProductPatternContract/source semantics and rendered
product-page controls. This is not a product accommodation list.

The contract now owns:

- axis role to payload target mapping;
- `lt-product-config-v1` client payload shape;
- server-derived resolver fields: resolved item, price provenance, readable
  summary, and canonical cart-line key;
- Quotation Item, Sales Order Item, and Sales Invoice Item line-field parity;
- no-product-specific-rule enforcement;
- live Webshop projection emitted from `item_details.html` for page JS/tests.

Feature handoff:
`workstreams/ecommerce-audit/backend-product-page-architecture-contract-2026-05-12.md`.

Still not complete:

- Add-on subsystem is only executable for the confirmed `foil_number` proof
  slice. Explicit eligibility, first selector UI, review-only boundaries, and
  the source-backed approval packet for four unapproved source families are
  now in place. GL cleared the current quote-only default as an import/reopen
  business blocker for testing, but additional paid-checkout add-on classes are
  still not built.
- Quote-first product-page payloads now preserve selected details, automatically
  create an internal draft Quotation, block zero-dollar review-line packets
  from sounding customer-ready, expose a no-send operator-review readiness
  evaluator, and can turn a submitted accepted quote into a draft Sales Order
  without payment/email/invoice side effects through a tokenized public
  acceptance route. The first customer quote sender is now built and BCC-gated,
  the first operator-owned Quotation send control is built, and the first
  real-token `/quote-accept` browser journey is covered. Broader customer
  review polish still needs review before live use.
- Source row-level price-candidate coverage and media classification now have
  verifiers, artifacts, and row-level packets. GL cleared those packets as
  import/reopen business blockers for testing, but they still do not make a
  destructive source purge/import safe by themselves. Deeper family-specific
  dependency UI/import rules and broader journey/acceptance UX gates are still
  open.
- Public ecommerce is currently paused by `lt_ecommerce_paused=1`.
- The architecture readiness audit now separates core technical architecture
  from import/reopen gates. Current expected paused-mode shape is
  `technical_architecture_ok: True` and `import_reopen_ok: False` because the
  public-open switch is intentionally off. Temporary open-mode proof may pass
  both, but must be restored to paused mode before launch work continues.
  Finance/bank remains deferred and is not counted as a current
  template-architecture blocker.

## Immediate next safe work

1. Build Phase 5: delivery mapping cleanup, tax/delivery-fee boundaries,
   Stripe/payment readiness, operator packet, and launch decision evidence
   without opening public ecommerce or claiming live payment success.
2. Extend the quote-first path from the current real-token `/quote-accept`
   browser journey into broader customer-review polish before live use.
3. Extend the add-on subsystem from the confirmed `foil_number` proof slice
   into real paid-checkout product-family add-on logic only when GL names the
   next add-on class to build.
4. Turn the source price-enrichment and media classification artifacts into an
   import/rebuild rehearsal input without hiding live-snapshot price provenance
   or the held media roles.
5. Extend desktop/mobile UX gates beyond the two core controls into the full
   quote review and checkout journeys before production cutover.

No destructive imports. No purge. No production/live ecommerce claim without
staging, owner approval, and live payment/cutover readiness.
