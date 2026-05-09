# ERPNext Ecommerce Receiving Architecture

Status: active Codex takeover handoff; no build/import approved.
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
- `catalog_contract/source_builder.py` separates required axes, color customization axes, confirmed add-ons, and warnings, but does not yet own full template type, dependency rules, invoice payloads, or complete fail-loud import gates.
- `templates/generators/item/item_configure.html` currently renders inline ERPNext variant selectors, color drawers, variant price lookup, and variant image updates; it still contains temporary bridge logic and is not a complete product receiving ecosystem.

Treat these as current evidence to re-check, not final truth.

## Codex research synthesis - 2026-05-09

Durable research artifact:
`research/expedition-erpnext-ecommerce-receiving-architecture/research-synthesis.md`

Current conclusion:

- ERPNext's transactional product unit is the concrete Item/variant, not the product template.
- LT's current product page/cart/checkout path can resolve a variant and server price, but it drops structured product configuration before Sales Order Item and Sales Invoice Item.
- Live ERPNext has LT custom fields on Website Item and Sales Order header, but no LT fields on Sales Order Item or Sales Invoice Item for selected options/add-ons/customization.
- Source contract verification proves the proof-product shape is useful but real import is still blocked: resolver-backed prices, media classification, high-cardinality color customization, and nine review-only axes need architecture before product migration.
- The first build slice should be backend preservation, not page rendering: line-level configuration storage, server-side resolver, cart payload versioning, checkout write, invoice copy, and verifiers.

## Immediate next safe work

1. Design the smallest line-level configuration preservation contract for Sales Order Item and Sales Invoice Item.
2. Prove `unicorn-bouquet` can carry Bouquet Size plus optional foil-number meaning through cart, checkout, Sales Order, invoice, and Stripe amount parity.
3. Prove `classic-arch` blocks checkout and creates/validates a structured quote payload until price/media/dependency gaps are resolved.
4. Produce the implementation blast-radius note before code changes: fields, DocTypes/child tables, templates, APIs, cart payload, checkout, invoice copy, reports, and verifiers.

No imports. No build. No purge. No product-transfer claims.
