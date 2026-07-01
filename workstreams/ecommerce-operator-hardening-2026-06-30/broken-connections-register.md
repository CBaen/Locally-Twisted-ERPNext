# Broken Connections Register

Date: 2026-06-30

Status: initial red-alarm register. Each item needs live/local proof before closure.

## Severity Key

- P0: Can show customers wrong product, price, availability, payment, or order meaning.
- P1: Can block owner self-service or create developer-only workflow.
- P2: Can confuse maintainers, verifiers, or future release work.

## B001 - Public Description Authority Is Not Obvious

Severity: P0

Evidence:

- Product page story/details render `lt_brand_description` and `lt_product_details`.
- Standard `web_long_description`/`description` are fallback only.

Failure mode:

- Owner edits a normal ERPNext description field and public page stays unchanged.

Required fix:

- Product Setup must own public copy.
- Raw Website Item description fields should either sync from Product Setup or clearly fail/redirect owner edits.
- Verification must compare Product Setup, Website Item LT fields, and rendered product page.

## B002 - Product Setup Base Price Can Diverge From Sellable Item Prices

Severity: P0

Evidence:

- Public Large Head Missionary page embedded setup schema with `base_price: 125.0`.
- Public page/variant API showed `$175.00`.
- Runtime pricing reads variant `Item Price`.

Failure mode:

- Owner thinks they changed product price, while actual public/cart/checkout price remains tied to variant Item Prices.

Required fix:

- Define one owner price authority per product type.
- Product Setup price edits must produce exact Item Price mutations for all affected sellable Items.
- Price proof must cover listing, product page, variant API, cart, checkout, Sales Order, payment line items, invoice, and receipt.

## B003 - Owner Product Setup Is Not A Live Publishing Workflow

Severity: P1

Evidence:

- Local apply is gated to local/test behavior.
- Generated Website Items are unpublished/local.
- Existing public publish/hide/reroute changes are preserved and not applied by local apply.
- Live approval is intentionally blocked in the current local slice.

Failure mode:

- Owner can create a product setup but cannot make it live without developer/release work.

Required fix:

- Add explicit state machine: Draft -> Needs Review -> Local Proof -> Staging Proof -> Approved For Live -> Live Applied.
- Attach proof artifacts and make live publish a reviewed operation, not a raw save side effect.

2026-06-30 Phase 12 status:

- Offline publish readiness reporting now defines owner-visible blocked state
  language and allowed actions.
- Birthday Deliveries reads as `Blocked - Proof Needed`, not saved/live.
- Product Setup validation JSON now emits the readiness state and false
  publish/apply approvals.
- Desk now has a read-only `Show Readiness` display for readiness state and
  next owner step.
- Offline catalog readiness dashboarding now rolls saved authority packet
  blockers into 47 blocked product rows and grouped blocker counts.
- Desk now has a read-only `Show Catalog Readiness` summary over saved Product
  Setup validation rows with proof mode, blocked rows, next owner step, saved
  evidence time, and developer-help flags.
- Still open: owner-profile Desk proof, current live-proof refresh, durable
  last-proof timestamps beyond saved validation modified time, and any
  publish/apply controls that remain blocked until release proof exists.

## B004 - Raw Catalog Edits Are Protected, But Replacement Workflow Is Incomplete

Severity: P1

Evidence:

- Owner catalog guard blocks direct edits to raw product/page/price/category/gallery settings.
- Product Setup exists as replacement surface.

Failure mode:

- Safety guard protects the business from dangerous edits, but owner lacks a complete path for ordinary product maintenance.

Required fix:

- Keep the guard.
- Route every expected owner action through Product Setup or a scoped maintenance flow.
- Add owner-visible messages that explain what to do next, not just "cannot edit."

## B005 - Photos Are Split Across Multiple Authorities

Severity: P0

Evidence:

- Shop cards use `Website Item.website_image`.
- Product gallery uses Website Item, Website Slideshow rows, and approved Product Setup media.
- Variant media can be held back.
- Cart and payment can use selected media helpers.

Failure mode:

- Owner changes one photo, but another customer surface still shows an old image.

Required fix:

- Media proof must cover primary image, gallery, selected variant image, cart image, Sales Order/customer-facing line image, payment image, and receipt/invoice surfaces where present.

## B006 - Add-Ons Are Not Just Product Options

Severity: P0

Evidence:

- Add-ons must be approved, fixed-price, backed by enabled Items and Item Prices.
- Checkout creates separate Sales Order Item lines.

Failure mode:

- Owner adds an add-on-looking option that appears selectable but is not priced/documented correctly.

Required fix:

- Product Setup add-on rows must require checkout approval packets.
- Verifier must prove add-on UI, cart line, checkout totals, Sales Order line, payment line, invoice line, and receipt/customer message.

2026-06-30 Phase 9 status:

- Offline classification tooling now identifies Birthday Deliveries current
  SKU-defining axes that should be reclassified before mutation.
- Saved artifact result: `Delivery Size` is the only candidate SKU-defining
  axis; `Delivery themes` is a configuration payload candidate; `Add Foil
  Number` and `Add Bouquet` are paid add-on candidates.
- Still open: paid add-on Items/Prices, cart expansion, checkout summary,
  Sales Order/Invoice/payment/receipt labels, historical references, rollback,
  and owner approval.

2026-06-30 Phase 10 status:

- Offline dependency/rollback tooling now captures saved-artifact rollback rows
  for Birthday Deliveries variant Items, Item Prices, Product Setup option
  rows, and media/gallery pointers.
- The report still fails loudly because live route proof, brand-lane proof,
  historical references, File/slideshow references, add-on/runtime behavior,
  and owner mutation approval remain missing.
- Still open: no-write replacement model design, paid add-on implementation
  proof, cart/order/document/payment label proof, and a reviewed release packet
  before any catalog write.

2026-06-30 Phase 11 status:

- Offline replacement-model tooling now proposes three design-only candidate SKU
  rows from `Delivery Size`.
- `Delivery themes` is modeled as configuration payload.
- `Add Foil Number` and `Add Bouquet` are modeled as paid add-on candidates;
  `Add Bouquet` remains blocked as a current price-affecting non-SKU axis.
- The report still fails loudly until add-on/runtime pricing, payload
  preservation, live route, brand-lane, historical-reference, owner approval,
  and release packet proof exist.

## B007 - Conditional Pricing Is Captured But Not A Complete Owner Price Engine

Severity: P1

Evidence:

- Conditional price rows exist in Product Setup.
- Product apply planning creates exact prices from exact rows or base price.
- Runtime has pricing rule/schema gates, but not a complete owner-safe dynamic price engine for all conditions.

Failure mode:

- Owner enters pricing rules that do not become public/cart/checkout price behavior.

Required fix:

- Decide which pricing patterns are SKU prices, add-on prices, fulfillment
  charges, quote-only rules, or dynamic runtime rules.
- Each category needs a verifier and loud owner-facing unsupported-state
  message.

## B008 - Product Brand Lane Was Not A First-Class Product Setup Authority

Severity: P0

Evidence:

- Phase 4 authority packet report blocked all 47 published products on
  `brand_lane_unproved`.
- Active uniqueness cannot be safely evaluated when product authority is not
  scoped by operating brand.
- Product changes can imply public route, file/media, document, payment,
  portal, automation, and customer-message identity.

Failure mode:

- A future repair or publish packet could project the right product data into
  the wrong brand lane, or treat a guessed/default route namespace as business
  identity proof.

Required fix:

- Product Setup must declare `operating_brand`.
- Saved artifacts and runtime authority packets must distinguish
  `source_declared` from `proved`.
- Active uniqueness, projection, payment/document identity, media/file
  ownership, portal/automation behavior, and public-route proof must remain
  blocked until the brand lane is proved for the target packet.

2026-06-30 status:

- Source-level `operating_brand` exists and is guarded by
  `scripts/verify/product_blueprint_contract.py`.
- Runtime Product Setup lookup is now brand-aware in source and fails closed
  on missing/invalid brand or active ambiguity.
- Active Product Setup Desk validation now blocks when linked Website Item
  runtime brand fields are missing, mismatched, not `source_declared`, or target
  identity disagrees.
- Still open: live brand-lane proof, public projection repair,
  payment/document identity, media/file ownership, owner dashboard rollup, and
  release packet proof.
- Saved-artifact authority packets now report `source_authority.operating_brand`
  separately from live proof.
- Live proof, projection, and payment/document/media inheritance proof are
  still open blockers.

## B009 - Duplicate Active Product Setup Records Can Win By Modified Time

Severity: P0

Evidence:

- Runtime active setup lookup selects the latest modified active Product Setup for a target item/slug.

Failure mode:

- Two active records can silently change public copy/media/options/add-ons depending on modified timestamp.

Required fix:

- Enforce one active Product Setup per target item/slug per brand lane.
- Add a verifier and Desk validation blocker for duplicates.

2026-06-30 status:

- Source validation now blocks active same-brand Product Setup records that
  claim the same slug, target Item, or target Website Item.
- Runtime active lookup now logs ambiguity and returns no setup when duplicate
  active records match the same runtime key.
- Active Desk validation now surfaces runtime authority blockers when existing
  linked Website Item metadata cannot satisfy the brand-aware runtime contract.
- Saved-artifact authority packets now report same-brand source uniqueness
  separately from live proof.
- Still open: route-level uniqueness after route authority is modeled,
  database-level uniqueness, and live/global active authority proof.

## B010 - `/shop` May Show A Card That Cart Later Rejects

Severity: P0

Evidence:

- `/shop` filters published Website Items and excludes variant children, but does not explicitly require linked Item `disabled = 0`.
- Cart later requires enabled Item, published parent Website Item, checkout lane, and Item Price.

Failure mode:

- Customer sees a product card that cannot be purchased or added cleanly.

Required fix:

- Align listing eligibility with cart eligibility for checkout products.
- Add a verifier that every displayed checkout product resolves in cart.

## B010 - Stale Catalog Counts And Comments Can Mislead Verification

Severity: P2

Evidence:

- Current AGENTS state says 51 Website Items total / 47 published.
- Some older verifiers/workstreams still contain all-53 expectations.
- `shop.py` comments still describe Webshop owning cart logic even though LT now owns a guest localStorage cart plus server validation endpoint.

Failure mode:

- Future work proves the wrong scope or trusts stale architecture comments.

Required fix:

- Update source comments and verifier expectations only after DB proof.
- Any count-based verifier must state date, site, and source of proof.

## B011 - Product Setup Route Planning May Not Match Existing Category Routes

Severity: P1

Evidence:

- Apply plan uses `shop-items/{slug}` for planned Website Item route.
- Existing live product route includes category path `shop-items/bouquets/large-head-missionary`.

Failure mode:

- New locally-applied products may not land on the same route pattern customers and shop navigation expect.

Required fix:

- Decide canonical route pattern.
- Migration/redirect rules must be explicit.
- Product Setup preview must show final public route and redirects.

## B012 - Live Proof Confirmed Owner Save But Not Public Projection

Severity: P0

Evidence:

- Live authenticated read-only API proof was completed after the initial
  public/local pass.
- Product Setup `large-head-missionary` modified
  `2026-06-30 01:43:01.382176` by `locallytwisted@gmail.com`.
- Product Setup base price and 30 Product Setup price rows are `125.0`.
- Live sellable `Standard Selling` Item Price rows are still `175.0`.
- Public page still renders `from $ 175.00`.
- Public copy renders from Website Item fields, not Product Setup top-level
  story/details fields.

Failure mode:

- Owner receives a real saved confirmation but customer-facing product data
  still comes from separate runtime authorities.

Required fix:

- Do not repeat this as an access problem; live API proof exists in
  `live-readonly-api-audit-large-head-missionary-2026-06-30.md`.
- Use Product Setup projection preview and parity verifier for existing
  products. Initial offline tools now exist:
  `scripts/dev/lt_product_setup_projection_preview.py`,
  `scripts/verify/product_setup_authority_parity_contract.py`, and
  `scripts/dev/lt_product_setup_catalog_blast_radius_report.py`.
- Decide direct runtime authority vs explicit publish/apply authority per
  field.
- Capture rollback target before mutation.

## B013 - Prior ERP Research Is Not Yet Converted Into LT-Native Architecture

Severity: P1

Evidence:

- Prior ERP research exists and is allowed only as structural/business-process research.
- Current LT decision requires native ERPNext/Frappe contracts, not copied implementation.

Failure mode:

- The useful process insight remains in research notes while LT ecommerce remains a partial scaffold.

Required fix:

- Extract architecture-neutral lessons:
  - owner action state machine,
  - product publication packet,
  - price identity ledger,
  - media projection proof,
  - option/add-on type taxonomy,
  - live/staging proof gates.
- Do not copy naming, code, paths, or implementation patterns from the forbidden source.

## B014 - Catalog Blockers Were Not Visible As One Operator Map

Severity: P1

Evidence:

- Phase 4 authority packet reporting produced product-level blockers, but an
  operator still had to inspect a large JSON/report artifact or per-product
  receipts.
- Phase 14 Desk readiness display showed one record at a time, not the catalog
  blast radius.

Failure mode:

- Agents or operators can fix whichever product is loudest while missing the
  catalog-wide pattern: all 47 saved published products were blocked in the
  saved packet, with authority, public proof, rollback, price, media, and
  variant-shape blockers.

Required fix:

- Keep a catalog-level readiness dashboard that summarizes product rows,
  blocker groups, owner-safe actions, developer next actions, and variant
  explosion risks.
- Keep all publish/apply/cache/deploy/mutation approvals false in that dashboard
  until a separate release packet and live proof path exists.

2026-07-01 status:

- `scripts/dev/lt_product_setup_catalog_readiness_dashboard.py` and
  `scripts/verify/product_setup_catalog_readiness_contract.py` now provide the
  offline saved-packet dashboard and verifier.
- Against `/tmp/lt-catalog-authority-full-20260630/authority-packet-report.json`,
  the dashboard reports 47 products, 47 blocked, 284 blockers, six
  variant-explosion products, zero ready products, and all approvals false.
- Still open: owner-facing Desk dashboard, current live refresh, proof
  timestamps, and release-packet design.

2026-07-01 Phase 16 status:

- `scripts/dev/lt_product_setup_release_packet_report.py` now turns one Phase
  15 dashboard product row into a source-only pre-mutation release packet.
- The `large-head-missionary` saved packet remains blocked with seven
  dashboard blockers and nine missing release gates.
- Still open: current live refresh, target-site proof, Desk dashboard, owner
  approval workflow, and any actual release execution.

## B015 - Release Approval Can Be Confused With Packet Existence

Severity: P0

Evidence:

- Phase 15 creates a catalog dashboard and Phase 16 creates a product release
  packet, but both are built from saved/offline evidence.
- A named "release packet" can sound like approval if the artifact does not
  fail loudly.

Failure mode:

- An agent or operator treats packet completeness, owner desire, or saved
  dashboard counts as permission to mutate Item, Website Item, Item Price, File,
  cache, deploy, provider, payment, or customer-message state.

Required fix:

- Every source-only release packet must keep approval booleans false until the
  target environment, row-level diff, rollback, public proof, owner approval,
  developer review, and no-downtime/customer-impact gates pass.
- Verifiers must fail if source-only packet output approves mutation, cache
  clear, deploy, provider, payment, customer message, or public success.

2026-07-01 status:

- `scripts/verify/product_setup_release_packet_contract.py` verifies blocked
  products remain blocked and zero-dashboard-blocker products still remain
  blocked without target proof.
- Still open: actual staging/live release gate execution and target-site proof,
  which must be a separate approval path.
