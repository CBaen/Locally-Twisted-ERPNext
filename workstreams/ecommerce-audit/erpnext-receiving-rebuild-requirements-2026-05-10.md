D:2026-05-10 | Check:local repo/docs/source + existing audit artifacts 2026-05-10 | Confidence:[CONFIDENT]

# ERPNext Receiving Rebuild Requirements - Locally Twisted Ecommerce

## Status block

- **Lane:** ERPNext Receiving Architect / rebuild requirements.
- **Scope:** research/design requirements for a future purge/rebuild/import of Locally Twisted ecommerce products into native ERPNext/Frappe/Webshop. This is not implementation.
- **Non-scope:** no code changes, no commits, no product deletes/purges/imports, no customer/live payment/email path, no production data mutation.
- **Repo/worktree witness:** repo `C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\locally-twisted`; branch check returned `main`; artifact did not previously exist. Worktree already had many unrelated modified files before this artifact was created.
- **Primary evidence read:**
  - `AGENTS.md`
  - `ROLE.md` from this agent workspace
  - `capabilities/recipes/erpnext-ecommerce-receiving-architecture.md`
  - `workstreams/ecommerce-audit/erpnext-receiving-parity-matrix-2026-05-10.md`
  - `workstreams/ecommerce-audit/cart-checkout-intent-preservation-audit-2026-05-10.md`
  - `workstreams/ecommerce-audit/native-frappe-product-template-architecture-2026-05-10.md`
- **Current destination version evidence inherited from audits:** local/test ERPNext stack reports `frappe 15.106.0`, `erpnext 15.105.0`, `payments 0.0.1`, `webshop 0.0.1`, `locally_twisted 0.0.1`; backend image witness in Lane B was `locally-twisted-erpnext:v15`, not dispatch anchor `frappe/erpnext:v15.105.0` **[VERSION-MISMATCH]**.
- **Current source witness mismatch inherited from Lane B:** local legacy_source module `19.0.2.15.0`; older handoff warns production DB may remain `19.0.2.14.0` **[VERSION-MISMATCH]**.
- **Confidence:** high that a simple import is unsafe; medium-high for the receiving model below because it is grounded in current repo contracts and same-day audit artifacts; medium for final product-by-product requirements until source/version mismatches and business review packets are resolved.

## Executive requirement

Do **not** purge/recreate or import every product until ERPNext can prove it can receive each product's full selling meaning: product-page class, required option logic, quote-vs-checkout lane, prices, add-ons, color/customization intent, media/gallery behavior, cart identity, checkout/order/invoice fields, quote-first records, operator review, rollback evidence, and fail-loud blockers.

A purge/rebuild should be treated as a **controlled receiving migration**, not a data transfer.

## Current verified project state relevant to rebuild

### What is already technically present

Current audit artifacts show a substantial receiving slice exists in `locally_twisted`:

1. **Two page lanes exist conceptually and in runtime code:**
   - `simple_product` / `checkout` for Ready-to-order pages.
   - `complex_custom_product` / `quote_first` for Custom quote pages.
   - `needs_review` as the safe default.
2. **Line-level configuration fields exist conceptually on downstream ERPNext rows:**
   - `Sales Order Item`, `Sales Invoice Item`, and `Quotation Item` carry product template, page type, configuration version, configuration summary, and configuration JSON fields.
3. **Quote-first bridge exists:**
   - Product quote payload can land on `Lead`, child `LT Product Quote Item`, draft `Quotation`, and accepted quote draft `Sales Order` paths in the proof slice.
4. **Cart identity exists for configured products:**
   - Same SKU with different selected configuration remains distinct by `cart_line_key`.
5. **Add-on proof exists for one add-on family:**
   - `foil_number` expands to `ADDON-FOIL-NUMBER`, is server-priced, preserves selected value, and copies into SO/SI payloads in rollback-safe tests.
6. **Dependency and fail-loud contracts exist:**
   - Impossible/unknown combinations and unsupported add-ons are expected to fail loudly, not silently become cartable.
7. **Runtime proof exists for representative paths:**
   - Lane C verified Unicorn Bouquet ready-to-order + foil number, Classic Arch quote-first handoff, configured cart/checkout labels, backend SO/SI preservation, and negative cases.

### Exact gaps in current Website Item/product runtime state

These are the blockers that make a simple purge/import unsafe:

1. **All current published Website Items are still stored as review state.**
   - Lane C DB inventory found **53 published Website Items** and **all 53** had stored `lt_product_page_type=needs_review` and `lt_commerce_lane=needs_review`.
   - Representative runtime inference makes proof pages work, but stored catalog classification is not complete enough for a destructive rebuild.
2. **Full catalog import remains explicitly blocked.**
   - Lane B cites `15-product-page-contract-source-audit.json` with `blocked_for_destructive_import: true`.
   - Warning counts: `missing_resolver_prices: 49`, `unclassified_gallery_images: 49`, `axis_needs_review: 9`, `color_axis_customization: 25`.
3. **Media is not rebuild-ready.**
   - Lane B media visibility blocks on **49 products** and **95 unclassified extra images**.
   - There are no approved Website Slideshow records for parent-gallery media.
   - Variant image evidence exists only as partial/proof behavior, not a complete rebuild map.
4. **Prices are not all business-approved.**
   - Checkout-class proof paths have price coverage, but source price enrichment includes live-snapshot candidates that require business review.
   - Missing resolver prices remain a destructive-import blocker.
5. **Add-ons beyond foil number are not approved for checkout.**
   - Review-only source families include `Add Bouquet`, `Add ons`, `Orbz toppers`, and `Plush add ons`.
   - Current approval packet approves **0** of these review-only families for checkout.
6. **Color/customization semantics are not final.**
   - Color-heavy products are safely routed quote-first in current architecture, but color axes/customizations still require business/source review before a rebuild can claim parity.
7. **Source authority is not clean.**
   - legacy_source local module/source witness and possible production DB version differ.
   - Final rebuild requirements must specify which source witness controls.
8. **Aggregate readiness has a live mismatch to clear.**
   - Lane B says direct quote delivery contracts passed on rerun, but aggregate architecture readiness captured a transient MariaDB deadlock and must rerun cleanly before launch/rebuild approval.
9. **Payment/finance launch behavior is deferred.**
   - Quote acceptance is draft-only and guarded; real paid launch/payment readiness is not proven by these artifacts.

## Minimum native ERPNext/Frappe receiving model before purge/rebuild

### Required native ERPNext spine

ERPNext native records must remain the accounting/catalog spine:

- `Item`
- `Website Item`
- `Item Price`
- `Item Attribute`
- `Item Variant Attribute`
- `Quotation`
- `Quotation Item`
- `Sales Order`
- `Sales Order Item`
- `Sales Invoice`
- `Sales Invoice Item`
- `Lead`
- `Contact` / `Customer` where checkout/contact flow creates them
- Website/media records used by approved product image/gallery destinations, such as `Website Slideshow` and `Website Slideshow Item` if selected

### Required LT custom fields / schema surfaces

Before purge/rebuild, these must exist, be synced, and be verified in the target database:

1. **Website Item classification fields**
   - `lt_product_page_type` / operator label `Page Template`.
   - `lt_commerce_lane` / operator label `Buying Path`.
   - Valid values must include only proven storage classes: `simple_product`, `complex_custom_product`, `needs_review`; `hybrid` must remain disabled unless separately verified.
2. **Line configuration fields on `Sales Order Item`, `Sales Invoice Item`, `Quotation Item`**
   - template/source Website Item reference.
   - product page type.
   - configuration version.
   - customer/operator-readable configuration summary.
   - complete configuration JSON.
3. **Quote-first fields on `Lead` and `Quotation`**
   - source product page/template.
   - page type and commerce lane.
   - quote summary.
   - full product quote payload.
   - quote status/review status.
   - source Lead link.
   - acceptance/audit/idempotency fields where accepted quote creates a draft Sales Order.
4. **Child table `LT Product Quote Item`**
   - one row per product quote request in a Lead/contact flow.
   - stores product page, page type, commerce lane, summary, payload JSON, status, and review/draft linkage.
5. **Code-owned service Items**
   - `LT-PRODUCT-QUOTE-REVIEW` as internal zero-dollar review placeholder only; must never be customer-ready pricing.
   - `ADDON-FOIL-NUMBER` as current confirmed add-on Item.
   - Future add-on Items only after approval record + price + verifier exists.

### Required custom DocTypes or generated artifacts before destructive rebuild

A simple set of generated JSON/Markdown artifacts is acceptable for the next stage; promote to Desk DocTypes only if operators need to review/edit them in ERPNext.

1. **Product receiving staging register**
   - One row per source product.
   - Required columns: source slug/id, source evidence id/version, target Website Item, target Item/template, page class, commerce lane, required axes, customization axes, color axes, source add-on families, dependency matrix id, media plan status, price plan status, import action, blocker status.
2. **Dependency matrix register**
   - One row per product/axis matrix.
   - Must encode valid required-axis combinations and dropped/transformed axes.
   - Must mark impossible/unknown axes as blockers.
3. **Add-on approval register**
   - One row per source add-on family/value.
   - Required fields: normalized key, label, eligible products/groups, target Item, pricing source, quantity rule, fulfillment/operator notes, checkout-approved vs quote-only vs dropped, approval evidence.
4. **Price review register**
   - One row per expected sale unit.
   - Must distinguish source resolver, source base price, current ERPNext live snapshot, and human-approved override.
   - Live-snapshot prices must stay `business_review_required` until approved.
5. **Media classification register**
   - One row per source image/media asset.
   - Classification values: primary product image, variant image, parent gallery, category/reference/marketing, hold until classified.
   - Must map approved destinations to native Website Item/Item/Slideshow targets.
6. **Purge/rebuild audit ledger**
   - Planned action per current ERPNext product/variant/price/media record: keep, update, recreate, disable, delete/purge.
   - Must include pre-purge counts, record ids/names, rollback package path, and post-rebuild verification status.

## Required services/templates/verifiers at concept level

### Services

- **Product page runtime service**: validates `lt-product-config-v1`, resolves Item/variant, enforces page lane, builds configuration summaries, produces line field payloads.
- **Dependency service**: narrows customer options from source-backed valid combinations and fails loudly for impossible or unknown axes.
- **Pricing service**: server-resolves base Item and add-on prices from approved ERPNext `Item Price` / approved import price register; never trusts browser price.
- **Add-on service**: allows only approved checkout add-ons; routes review-only add-ons to quote-first.
- **Quote-first service**: normalizes product quote payload, writes Lead child rows, creates draft Quotation review packets, supports approved quote to draft Sales Order with no invoice/payment side effects.
- **Media service/classifier**: maps primary/variant/gallery images only from approved classification; does not invent gallery claims.
- **Failure recorder**: records customer-safe, operator-actionable failures for malformed payloads, missing prices, quote-required checkout attempts, dead/expired tokens, and source/import blockers.
- **Migration dry-run service**: builds the receiving staging register and refuses destructive import while any row is blocked.

### Templates/UI surfaces

- Native Webshop product template override with two stable partials:
  - Ready-to-order/configured checkout partial.
  - Quote-first/custom request partial.
- Cart and checkout surfaces that display selected options/add-ons and customer-safe loud errors.
- Contact/quote handoff surface that preserves product payload instead of flattening into free text.
- Operator Desk/report surfaces for product quote review, price review, media classification, and import blockers.

### Verifiers/gates

Before purge/rebuild, the following verifier classes must exist and pass against the target database:

- product page class/lane verifier.
- source contract/destructive import blocker verifier.
- dependency matrix verifier.
- add-on approval/dependency verifier.
- price readiness + price review packet verifier.
- media visibility + media classification verifier.
- cart line identity verifier.
- checkout-to-Sales-Order preservation verifier.
- invoice-copy verifier if invoice path is in launch scope.
- quote-first Lead/Quotation verifier.
- quote acceptance draft-Sales-Order verifier.
- customer quote delivery/operator send verifier if quote delivery is in scope.
- ecommerce pause/reopen verifier.
- public browser tests for product, cart, checkout, quote-first, and quote acceptance surfaces.
- purge/rebuild rollback verifier comparing pre/post record counts and expected action ledger.

## What must be proven before any product purge/rebuild

No product purge/rebuild/import may start until all items below have evidence artifacts:

1. **Source authority chosen.**
   - Resolve or explicitly choose between legacy_source local `19.0.2.15.0` and possible production `19.0.2.14.0`.
2. **Every source product has a receiving row.**
   - No missing class/lane.
   - No unresolved target Website Item/Item strategy.
3. **Every current Website Item has an intended action.**
   - keep/update/recreate/disable/delete must be explicit.
   - No accidental orphan cleanup.
4. **Every checkout-class sale unit has approved server price.**
   - Not merely live snapshot unless business-approved.
5. **Every required axis has a destination.**
   - variant axis, dependency-matrix option, quote/customization field, add-on register, or explicit drop with approval.
6. **Every color/customization axis is preserved as operator/customer intent.**
   - If not safe for checkout, route quote-first.
7. **Every add-on family/value is approved or blocked.**
   - No source add-on silently imported as free text, variant explosion, or free checkout option.
8. **Every media asset is classified or held.**
   - No gallery/multi-photo claims without approved destination.
   - Variant-changing photos need explicit variant-image evidence and UI proof.
9. **Runtime proof passes after staging data is loaded.**
   - Product page -> cart -> checkout -> SO Item -> SI Item where paid checkout is in scope.
   - Product page -> contact Lead -> draft Quotation -> approved quote draft SO where quote-first is in scope.
10. **Rollback plan exists and is rehearsed.**
   - Record ledger, database backup/snapshot, git/tag anchor, generated reports, and post-rollback verifier.
11. **Public ecommerce remains paused/guarded until reopen gate.**
   - Current native proof slice does not equal whole-catalog launch readiness.

## Staged migration/rebuild plan with gates

### Stage 0 - Freeze and protect

- Confirm repo branch `main` and record current git SHA/tag.
- Capture database backup/snapshot and Website Item/Item/Price/media counts.
- Freeze public ecommerce mode or confirm guarded testing mode.
- Produce rollback package path and restore instructions.

**Gate:** rollback package exists and a non-destructive verifier can read expected baseline counts.

### Stage 1 - Source authority and receiving register

- Choose controlling source witness/version.
- Generate product receiving staging register for all source products and current ERPNext Website Items.
- Reconcile 53 published Website Items and all current `needs_review` classifications.

**Gate:** zero products without class/lane/action; unresolved rows are explicit blockers, not assumptions.

### Stage 2 - Price, dependency, add-on, media review packets

- Generate dependency matrices for required axes.
- Generate price review packet with source labels.
- Generate add-on approval packet.
- Generate media classification packet for primary, variant, and multi-photo/gallery behavior.

**Gate:** checkout-class rows have approved price/add-ons/media; quote-first rows preserve option/customization/media intent; unknowns stay blocked.

### Stage 3 - Dry-run rebuild plan

- Run import simulation without changing records.
- Compare expected Items/variants/prices/media/slideshow records.
- Produce purge/recreate action ledger.

**Gate:** destructive import verifier says not blocked; GL/business approval exists for purge scope.

### Stage 4 - Small proof batch rebuild

- Rebuild the smallest ready-to-order family first, e.g. Unicorn/Bouquet proof slice.
- Rebuild one quote-first complex family second, e.g. Classic Arch proof slice.
- Do not broaden until both pass runtime/customer/operator gates.

**Gate:** product, cart, checkout, SO/SI, quote-first, and public browser verifiers pass for proof batches.

### Stage 5 - Family-by-family rebuild

- Rebuild in coherent families: bouquets, arches, columns, garlands, table decor, etc.
- After each batch, rerun targeted verifiers and compare counts.
- Keep unsupported add-ons/color-heavy options quote-first until approved.

**Gate:** each batch has post-rebuild audit rows and no unclassified public claims.

### Stage 6 - Full catalog synthesis and public reopen decision

- Rerun aggregate architecture readiness cleanly.
- Rerun ecommerce pause/reopen, checkout experience, quote-first, quote-accept, media, price, dependency, and source import gates.
- Produce GL summary with what remains quote-first/deferred.

**Gate:** public ecommerce only reopens if full-catalog and payment/finance scope are approved. Otherwise keep showroom/quote-first or paused mode.

## Rollback/audit evidence required

Minimum rollback/audit packet before any destructive work:

- git SHA/tag and dirty-worktree note.
- database backup/snapshot identifier and restore command/path.
- full pre-rebuild counts:
  - Website Items.
  - Items total.
  - variant templates.
  - active variants.
  - disabled/legacy variants.
  - Item Prices.
  - Item Variant Attribute rows.
  - Website Slideshow / Slideshow Item records.
  - relevant media/file counts.
- current product/price/media export or report artifact.
- purge/rebuild action ledger keyed by record name.
- generated receiving register, price packet, add-on packet, dependency packet, media packet.
- verifier report paths before and after each batch.
- browser evidence paths for representative journeys.
- explicit record cleanup proof for any test Sales Orders, Invoices, Leads, Quotations, Payment Requests, Email Queue rows.
- fail-loud evidence for blocked/unknown/malformed paths.
- signoff note for business-review decisions: prices, add-ons, image classification, product classes, payment readiness.

## Risks if simple import is attempted again

1. **Product meaning loss:** ERPNext may receive SKUs but lose customer option intent, colors, notes, add-ons, variation photos, and multi-photo gallery meaning.
2. **Variant explosion or flattening:** color/customization/add-on axes could become impossible SKU matrices or disappear into one generic product.
3. **False checkout success:** quote-first products with Item Prices could accidentally become payable cart lines without operator review.
4. **Silent price errors:** missing resolver prices or live-snapshot fallback prices could become public customer promises.
5. **Add-ons become wrong:** unapproved source add-ons may be dropped, free, required, or mispriced.
6. **Cart/order ambiguity:** same SKU with different configurations could collapse unless configured line identity is verified after import.
7. **Media regression:** variation-changing photos and multi-photo views may disappear or attach to wrong variants/products.
8. **Operator workload damage:** draft quote packets could lack enough context for Jeff/operator review.
9. **Accounting/audit damage:** Sales Orders/Invoices may lack the configuration fields needed to explain what was sold.
10. **Rollback uncertainty:** without a purge ledger and backup, bad imports could leave thousands of items/prices/variants in an unrecoverable mixed state.
11. **Launch trust failure:** polished UI could hide a nonfunctional receiving model, violating the project fail-loud law.

## Actionable next steps

1. Resolve source authority/version mismatch or record which legacy_source/source witness controls rebuild.
2. Generate a product receiving staging register for all 53 source/published Website Items and all current ERPNext product records affected by purge/recreate.
3. Convert current blockers into review packets:
   - 49 missing resolver price products.
   - 95 unclassified extra images across 49 products.
   - 9 axes needing review.
   - 25 color-axis customization cases.
   - all review-only add-on families.
4. Rerun aggregate architecture readiness after the transient deadlock and require a clean report.
5. Decide the target for variation-changing photos and multi-photo views before any media import.
6. Keep all products stored as `needs_review` or quote-first until their receiving row has approved price, media, axis, add-on, and verifier evidence.
7. Only after the above, prepare a no-mutation dry-run purge/rebuild action ledger for GL/business approval.
