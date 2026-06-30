# Significant Change Register

Date: 2026-06-30

Status: initial register. Each change needs implementation design, verifier, and owner acceptance proof before it is closed.

Controlling safety contract: [protective-contracts.md](protective-contracts.md).

## SCR-001 - Variant Architecture Reset

Current state: LT has roughly 50 product pages but over 10k variant Items because earlier import logic treated many valid option combinations as ERPNext variants.

Target state: only SKU-defining choices become ERPNext variants. Colors, decoration choices, customer configuration, measurements, uploads, review-only options, and most add-ons become structured Product Setup/cart/order payloads or quote context.

Affected surfaces: Product Setup, Item/Item Variant generation, Item Price generation, product-page selector, variant selector, cart line key, checkout, Sales Order Item, Sales Invoice Item, quote flows, verifiers, catalog migration.

Verifier requirement: prove at least one high-cardinality product has bounded sellable variants while preserving customer-selected configuration in cart, checkout, Sales Order, invoice/receipt, and operator view.

Safety requirement: no existing variant, Item Price, Website Item, order, invoice, payment, or customer-message-linked record may be deleted, renamed, disabled, collapsed, or repurposed until dry-run dependency, replacement, historical-reference, rollback, and owner-scope approval pass.

## SCR-002 - Product Setup Becomes Owner Source Of Truth

Current state: Product Setup exists and can preview/local-apply, but live publish/hide/reroute and existing-product changes are not a complete owner-run workflow. Live proof on 2026-06-30 showed `large-head-missionary` Product Setup saved price rows at `125.0` while customer-facing Item Prices/public price stayed at `175.0`.

Target state: authorized backend users manage product business meaning through Product Setup. Raw ERPNext tables are generated/projection targets, not the normal human editing surface.

Affected surfaces: Desk workspace, Product Setup doctype, validation, preview, apply/projection, permissions, owner dashboard, guard messages.

Verifier requirement: non-developer owner-profile test can create a draft product, fix validation blockers, preview raw projections, and publish/apply through the approved workflow without raw Website Item permissions.

Safety requirement: Product Setup must enforce one active authority per target item, slug/route, and brand lane before runtime reliance on active Product Setup records.

## SCR-003 - Immediate Public Projection For Approved Product Changes

Current state: a backend save can update a field that public pages do not read, leaving live content unchanged.

Target state: approved product changes project to every relevant public authority immediately after validation. If projection or proof fails, the product status says not live and records the blocker.

Affected surfaces: Website Item custom fields, Item fields, Item Prices, Website Slideshow, Product Setup active schema, route cache, shop listing, product page, public APIs.

Verifier requirement: for one existing product, change price, description, and image through Product Setup and prove public route/shop/API reflect the change or a loud blocker prevents live status.

Safety requirement: "Approved For Live" is not customer-visible proof. Live requires target-site update evidence, cache evidence where applicable, public route/API proof, owner Desk proof, cart proof where relevant, and rollback proof.

## SCR-004 - Price Identity Rebuild

Current state: Product Setup base price, variant Item Prices, product-page display, cart, and checkout can diverge.

Target state: price intent resolves to exact sellable Item Price rows or approved add-on prices and cascades through visible page, variant selector, cart, checkout, Sales Order, payment, invoice, and receipt.

Affected surfaces: Product Setup price rows, Item Price, variant selector override, product page starting price, cart API, checkout totals, Stripe line items, invoice copy, price verifiers.

Verifier requirement: assert the same amount for selected product/option/add-on across public display, cart, checkout preview, Sales Order, payment payload, invoice, and receipt/customer-facing labels.

Safety requirement: prove the ordered price identity chain from source/Product Setup through Item Price before any downstream parity can count. Item Price proof must name `item_code`, variant/option key, Price List, currency, UOM if relevant, validity dates/scope, and source resolver or approval evidence.

## SCR-005 - Main Image, Gallery, And Variant/Option Media Workflow

Current state: primary image, Item image, Website Item image, Product Setup primary image, File attachment, gallery/slideshow, and selected variant media can diverge.

Target state: owner can choose main product image, gallery images, and selected-option/variant images from one Product Setup workflow. Public product page, shop card, cart, payment, SEO/social metadata, and receipt surfaces use the approved image role.

Affected surfaces: Product Setup media fields/rules, File attachments, Website Item image, Item image, Website Slideshow, product page gallery, variant media API, cart image, Stripe line image, homepage/favorites if merchandised.

Verifier requirement: prove main image and selected-option image change on product page and cascade to cart/payment/receipt where applicable.

Safety requirement: separate media roles for primary image, gallery, selected-option media, shop card, metadata, cart, payment, receipt, and merchandising references. Gallery proof alone is not enough. Simple checkout variant `Item.image` can be approved selected-option media only when Product Setup media rules accept it.

## SCR-006 - Add-On And Modifier Architecture

Current state: foil-number add-on is proven; other add-on-looking source axes remain review-only or dangerous if treated as variants/free options.

Target state: every add-on is classified as checkout-approved paid add-on, configuration-only, quote context, or unsupported. Paid add-ons require enabled Item and Standard Selling Item Price and expand to separate order lines.

Affected surfaces: Product Setup add-on rows, product page UI, cart display lines, checkout, Sales Order Item, Sales Invoice Item, payment line items, receipt labels, add-on verifier.

Verifier requirement: prove one paid add-on from owner setup to product page, cart, checkout, Sales Order, invoice, payment, and receipt; prove unsupported add-ons route to quote/review.

Safety requirement: any visible add-on without enabled Item, Standard Selling Item Price, order-line behavior, document label, and payment/customer-label proof where relevant is a false-success blocker.

## SCR-007 - Explicit Product Publishing State Machine

Current state: published Website Item, commerce lane, Product Setup status, ecommerce pause, and route visibility are separate and can be misunderstood.

Target state: product states are explicit: Draft, Needs Review, Local Proof Ready, Staging Ready, Approved For Live, Live, Retired, Hidden, Quote Only, and Paused. Checkout readiness is a proved invariant, not a separate state. No URL rendering implies checkout readiness by itself.

Affected surfaces: Product Setup status, Website Item published flag, commerce lane fields, route visibility, shop listing, owner dashboard, verifiers, live release gate.

Verifier requirement: each state has expected public route/shop/cart/checkout behavior and owner-visible reason.

Safety requirement: every state transition must name actor, proof required, public behavior, failure message, and rollback behavior. Any unlisted transition is blocked until added to the controlling contract.

## SCR-008 - Owner Dashboard And Failure Register

Current state: blockers exist in verifiers, Error Logs, and scattered docs, but not as an owner-friendly product readiness dashboard.

Target state: owner/admin can see product status, public projection status, price/media/add-on blockers, last proof time, and required next step.

Affected surfaces: owner workspace, Product Setup validation output, failure recorder, product readiness report, maintenance heartbeat.

Verifier requirement: seeded failing products show actionable blockers; passing products show proof links/timestamps.

Safety requirement: verifier failures must feed owner-readable blockers, not only developer logs or Error Logs.

## SCR-009 - Existing Catalog Repair And Migration

Current state: current product records reflect historical import decisions and scaffold/test fixture assumptions. Counts and shape may be stale or excessive.

Target state: every live/published product is reconciled into the owner authority model with bounded variants, clean price rows, media roles, product copy, add-ons, and publish state.

Affected surfaces: current Item/Website Item/Product Setup/Item Price/Gallery records, migration scripts, dry-run reports, rollback plan.

Verifier requirement: catalog-wide report shows product authority packet for every published product and exact repair plan for each mismatch.

Safety requirement: first catalog-wide output is a report, not a write. Any write requires a pre-mutation release packet and rollback contract.

## SCR-010 - External Research Translation Gate

Current state: prior ERP research and other ecommerce platform lessons are useful but scattered and sometimes forbidden to name/copy.

Target state: research lessons are stored as architecture-neutral LT requirements with source pointers, no copied implementation/names, and clear acceptance tests.

Affected surfaces: research docs, capability docs, lane docs, implementation plans.

Verifier requirement: every external lesson used in implementation has an LT-native behavior statement and a source pointer; no forbidden term appears in generated LT docs unless explicitly required as a file/path reference.

## SCR-011 - Listing And Cart Eligibility Parity

Current state: `/shop` and cart eligibility can be proven through different resolver rules. A product may appear checkout-ready before cart rejects it.

Target state: any product that appears checkout-ready in `/shop` must also resolve through cart with enabled Item, correct checkout lane, sellable Item or selected variant, Standard Selling Item Price, Product Setup authority, public route proof, and cart API proof.

Affected surfaces: shop listing query, product cards, Website Item, Item enabled state, Product Setup status, cart API, quote-only/hidden/retired/paused states, layout/verifier tests.

Verifier requirement: catalog report flags every product shown in `/shop` that cannot enter cart; checkout-looking UI is blocked until listing/cart eligibility matches.

Safety requirement: quote-only, hidden, retired, paused, or blocked products must not appear checkout-ready.

## SCR-012 - Brand-Lane Proof For Product Changes

Current state: product records can carry route, media, payment, invoice, file, portal, and automation implications without a single product-change packet proving brand lane.

Target state: every product authority packet and release packet resolves one allowed brand lane before public, payment, document, file, portal, or automation behavior is touched. Allowed lanes are `locally_twisted`, `commercial_balloon_decor`, and `memorial_balloons`; no fourth lane is approved.

Affected surfaces: Product Setup, public routes, Website Item, files/media, invoices, payment labels, customer messages, portals, automations, verifiers.

Verifier requirement: each product-change packet records brand lane, route namespace/public route, customer-facing copy surface, invoice/document identity, payment/customer-message identity, file/media ownership, portal/automation behavior, inheritance proof through those surfaces, and fail-closed behavior when unclear.

Safety requirement: ambiguous brand lane blocks mutation.

## SCR-013 - Pre-Mutation Release Packet And Rollback Contract

Current state: product changes can be discussed as "ready" before the exact environment, row diffs, backup, rollback, cache, verifier, and proof mode are bound together.

Target state: every write path beyond no-write proof requires a pre-mutation release packet and rollback contract before local apply, staging write, or live write.

Affected surfaces: Product Setup apply workflow, migration scripts, staging/live release process, cache handling, public proof, owner Desk proof, rollback tooling, workstream artifacts.

Verifier requirement: a planned product write cannot run unless the packet names environment, branch/hash, target products/routes, actor, row-level diff, snapshot method, rollback command/procedure, cache plan, verifier list, brand-lane proof, payment/document proof mode, no-downtime/customer-impact section, stop condition, and approvals. Frappe Cloud app releases must also include old live app hash, target app-mirror branch/commit, old-live-to-target diff, deploy pipeline status, dirty-overlap audit, site update result, and migrate result where applicable.

Safety requirement: if rollback cannot be defined and re-proved publicly, mutation is blocked.
