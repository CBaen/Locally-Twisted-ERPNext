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

## B007 - Conditional Pricing Is Captured But Not A Complete Owner Price Engine

Severity: P1

Evidence:

- Conditional price rows exist in Product Setup.
- Product apply planning creates exact prices from exact rows or base price.
- Runtime has pricing rule/schema gates, but not a complete owner-safe dynamic price engine for all conditions.

Failure mode:

- Owner enters pricing rules that do not become public/cart/checkout price behavior.

Required fix:

- Decide which pricing patterns are SKU prices, add-on prices, fulfillment charges, quote-only rules, or dynamic runtime rules.
- Each category needs a verifier and loud owner-facing unsupported-state message.

## B008 - Duplicate Active Product Setup Records Can Win By Modified Time

Severity: P0

Evidence:

- Runtime active setup lookup selects the latest modified active Product Setup for a target item/slug.

Failure mode:

- Two active records can silently change public copy/media/options/add-ons depending on modified timestamp.

Required fix:

- Enforce one active Product Setup per target item/slug per brand lane.
- Add a verifier and Desk validation blocker for duplicates.

## B009 - `/shop` May Show A Card That Cart Later Rejects

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
- Build Product Setup projection preview and parity verifier for existing
  products.
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
