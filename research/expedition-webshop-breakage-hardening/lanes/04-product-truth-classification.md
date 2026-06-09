# Lane 04: Product Truth Classification

D:2026-05-21 | Check:local DB read-only queries + repo/source references | Confidence:LOCAL-PROOF with source-contract gaps

## Decision Question

Why is the live local DB at `51` Website Items while project instructions still mention `53`; which products were deleted or changed; and what contract should prevent stale product counts or wrong checkout/quote classification from reaching checkout proof?

## Sources Checked

- `research/expedition-webshop-breakage-hardening/research-brief.md` - lane question and current `51`/`10666` claim.
- Local ERPNext DB, site `frontend`, container `locally-twisted-erpnext-v15-backend-1`; read-only `frappe.client.get_count` and `SELECT` queries only.
- `_resources/catalog-source/catalog.json` and `_resources/catalog-source/slug_to_group.json` - legacy_source source export still says `product_count: 53`.
- `audits/catalog-import-audit-2026-05-08/current-state-snapshot-2026-05-17-2132-clean-legacy_source-products/summary.json` - read-only snapshot with `website_items: 53`, `items: 10674`, `item_prices: 10656`.
- `apps/locally_twisted/locally_twisted/seed/_guard/current-state-snapshot-2026-05-19-2314/summary.json` and `route_category_map.md` - read-only snapshot with `website_items: 53`, `items: 10686`, `item_prices: 10668`; includes `easter-arch` and `pride-arch` as `complex_custom_product|checkout`.
- `workstreams/ecommerce-audit/product-source-repair-map-2026-05-17.md` - maps 53 source products and marks both `easter-arch` and `pride-arch` certified checkout.
- `workstreams/ecommerce-audit/legacy_source-sellable-product-reimport-2026-05-17.md` - says 53 included products, 0 exclusions, browser proof for all 53, with later holds for unsafe direct checkout.
- `workstreams/ecommerce-audit/school-seasonal-color-preset-product-logic-2026-05-18.md` - explains quote-request as safety hold for high-cardinality products, not product deletion.
- Current contract sources: `apps/locally_twisted/locally_twisted/verify/website_item_classification_contract.py`, `apps/locally_twisted/locally_twisted/verify/simple_purchasable_rehearsal_contract.py`, `apps/locally_twisted/locally_twisted/verify/simple_purchasable_browser_support.py`, `scripts/verify/simple_purchasable_rehearsal_contract.py`, `scripts/verify/smoke_shop.py`.
- Stale docs found: `AGENTS.md`, `CODING-HANDOFF.md`, `locally-twisted-queue.md`, `scripts/README.md`, `workstreams/ecommerce-audit/README.md`.

## Local Evidence

- Current count facts:
  - `frappe.client.get_count` returned `Website Item = 51`, `Item = 10685`, `Item Price = 10666`.
  - `tabWebsite Item` has `published=1 -> 51`; no unpublished Website Item rows.
  - Stored Website Item classifications are `simple_product|checkout = 17`, `complex_custom_product|checkout = 13`, `complex_custom_product|quote_first = 21`.
  - `tabItem` summary is `10685` rows, `49` variant templates, `10629` variants, `56` root items, `444` disabled Items; variants split `10186` active and `443` disabled.
- Source-vs-DB compare:
  - `_resources/catalog-source/catalog.json` has `product_count = 53` and 53 source slugs.
  - Current DB Website Item item codes count is `51`.
  - Source slugs missing from DB Website Items are exactly `easter-arch, pride-arch`.
  - Current DB Website Item slugs not found in source: none.
- Missing-product DB facts:
  - `easter-arch`: `0` Website Items; `1` Item family row; the Item row is `disabled=1`, `published_in_website=0`, `has_variants=0`, modified by `Administrator` at `2026-05-21 08:04:49.561520`; `0` Item Prices.
  - `pride-arch`: `0` Website Items; `0` Item family rows; `0` disabled root Items; `0` Item Prices.
  - `tabVersion`, `tabDeleted Document`, and `tabActivity Log` each currently have `0` rows, so the DB no longer contains deletion/change provenance.
- Source history facts:
  - Current `website_item_classification_contract.py` now hard-codes `EXPECTED_TOTAL = 51` and `17/13/21/0` lane counts; it excludes `easter-arch` and `pride-arch`.
  - `git show e0ec264` shows the classification contract changed from 53 to 51, moved 13 products into `complex_custom_product|checkout`, removed all `hide_or_needs_review` rows, and dropped `easter-arch`/`pride-arch` from the target set.
  - The same commit removed `easter-arch` and `pride-arch` from the simple purchasable rehearsal and browser-support helpers, changing rehearsal expectations from 4 products / 33 sale SKUs to 2 products / 31 sale SKUs.
  - `scripts/verify/website_item_classification_contract.py` passed read-only dry run now: expected `51`, matched `51`, planned changes `0`, stored counts `17/13/21`.
- Contradictory/stale source facts:
  - `AGENTS.md` still says `Website Items | 53`.
  - `CODING-HANDOFF.md` and `locally-twisted-queue.md` still preserve 2026-05-18/older `53` current-count claims.
  - `scripts/README.md` and `workstreams/ecommerce-audit/README.md` still describe the simple purchasable lane as four products / 33 sale SKUs including `easter-arch` and `pride-arch`.
  - `apps/locally_twisted/locally_twisted/verify/simple_purchasable_payment_cascade_contract.py` and its wrapper still expect 4 products / 33 sale SKUs, so that lane is stale against the current 51-product DB.

## Findings

1. `51` is the current local DB truth. The old `53` is still the source-export and older snapshot truth, but it is no longer the live local Website Item count.
2. The entire two-product gap is `easter-arch` and `pride-arch`.
3. `easter-arch` was changed, not fully deleted: the Item remains as a disabled, unpublished, non-priced root Item with no Website Item.
4. `pride-arch` appears deleted from current catalog DB objects: no Item, Website Item, or Item Price family remains.
5. Current committed code intentionally supports a 51-Website-Item local target, but I did not find an explicit business/source contract saying those two products are owner-approved removals. Treat the current 51 as a local quarantine/safety posture, not settled product truth.
6. `quote_first` is still overloaded language. Project docs say there are no business quote-first products; the safer reading is: quote/request is an internal safety hold until bounded price, media, fulfillment, and checkout cascade are proven.
7. The current hard-coded classification contract can pass while the source export still has two unaccounted products. That is the core stale-count failure mode.

## Resolution Recommendation

- **Support:** Support the current DB as the local operating state only: 51 published Website Items, 17 simple checkout, 13 complex checkout, 21 quote-request safety holds. Also support the `smoke_shop.py` change that compares the visible count label to rendered cards instead of hard-coding `53`.
- **Quarantine:** Quarantine `easter-arch` and `pride-arch` from public checkout/product proof until there is an explicit product disposition row for each. `easter-arch` should stay disabled/unpublished; `pride-arch` should be treated as missing/deleted until rebuilt from source or explicitly eliminated.
- **Eliminate:** Eliminate unqualified hard-coded product counts in docs and tests. `53` may remain only as "legacy_source source export count" or "historical snapshot count"; `51` may remain only as "current local DB count as of 2026-05-21" unless rechecked.
- **Refresh:** Refresh the product source contract into a small versioned manifest that lists each source slug, current DB status, customer flow, and disposition: `checkout`, `quote_request_hold`, `quarantined`, `eliminated`, or `rebuild_required`. The manifest must require a reason, date, evidence file, and owner/source basis for any source slug not present as a published Website Item.
- **Rebuild:** Rebuild the classification verifier so it derives expected count and lane expectations from that manifest plus live DB, not from scattered hard-coded arrays. It should fail loudly when source has 53 but DB has 51 unless the two missing slugs have explicit quarantine/elimination entries.

## Required Tests

- Keep `python scripts/verify/website_item_classification_contract.py` green, but only after it is manifest-driven or explicitly checks source-missing dispositions.
- Add a product truth/source contract that checks: source slug count, current Website Item count, source-not-in-DB list, DB-not-in-source list, per-slug disposition, and lane counts. It should fail on unapproved source gaps.
- Add/update a read-only DB count verifier that records `Website Item`, `Item`, `Item Price`, active variants, disabled variants, and lane group counts with the run date.
- Update or quarantine stale simple purchasable tests before running them: rehearsal/browser/payment-cascade docs and wrappers must agree on 2/31 or restore 4/33 by rebuilding `easter-arch` and `pride-arch`.
- If `easter-arch` or `pride-arch` are restored, rerun source import readiness, product source repair map, classification contract, product-page runtime, variant/price contracts, cart/checkout contract, browser product proof, and payment cascade proof for the restored products.

## Remaining Gaps

- The DB provenance is missing: `Version`, `Deleted Document`, and `Activity Log` are empty, so I cannot prove from DB logs whether the 2026-05-21 removal/disable action was a deliberate product decision or collateral cleanup.
- I found committed source changes that accept 51, but not a clear owner-approved removal record for `easter-arch` or `pride-arch`.
- The legacy_source source export still says 53 and `catalog_import_subset.py` has no owner-excluded slugs, so current source and current DB are not reconciled.
- Some stale docs/tests still point at 53 or four simple purchasable products. Those should not be used as release proof until refreshed.
