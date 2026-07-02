D:2026-05-10 | Check:local verifier outputs + ERPNext Website Item apply 2026-05-10 | Confidence:[LOCAL-PROOF]
# Phase 2 Website Item classification result — ready-to-order ecommerce

## Scope / non-scope

Scope: targeted Website Item classification only for the 53 source-backed product pages in the accepted ready-to-order ecommerce Phase 2 lane.

Non-scope: no catalog_data mutation, no product publish/unpublish/hide/delete/purge/reimport, no price/media/business-copy changes, no public ecommerce opening, no payment/customer messaging action.

## Files changed

- `apps/locally_twisted/locally_twisted/verify/website_item_classification_contract.py` — Frappe-side dry-run/apply verifier for the 53 Website Item classifications.
- `scripts/verify/website_item_classification_contract.py` — CLI wrapper for dry-run/apply/report execution.
- `workstreams/ecommerce-audit/phase-2-website-item-classification-result-2026-05-10.md` — this result artifact.
- `workstreams/ecommerce-audit/README.md` — Phase 2 index entry.
- `workstreams/ecommerce-audit/ready-to-order-ecommerce-goal-progress-2026-05-10.md` — Phase 2 progress update.

Generated local evidence artifacts:

- `output/phase-2-website-item-classification-dry-run-20260510.json`
- `output/phase-2-website-item-classification-apply-20260510.json`
- `output/phase-2-website-item-classification-post-apply-report-20260510.json`
- `output/product-page-architecture-readiness-infrastructure-research-20260510.json` updated by the required safe gate.

## Classification counts

| Lane | Website Item fields | Count | Result |
|---|---|---:|---|
| `checkout_ready_after_small_fix` | `lt_product_page_type=simple_product`, `lt_commerce_lane=checkout` | 15 | Stored after apply |
| `quote_first` | `lt_product_page_type=complex_custom_product`, `lt_commerce_lane=quote_first` | 33 | Stored after apply |
| `hide_or_needs_review` | `lt_product_page_type=needs_review`, `lt_commerce_lane=needs_review` | 5 | Already/still stored |
| Total targeted Website Items | Only the two classification fields | 53 | Matched exactly |

## Dry-run output

Command:

```bash
python scripts/verify/website_item_classification_contract.py --report output/phase-2-website-item-classification-dry-run-20260510.json
```

Output:

```text
[WEBSITE ITEM CLASSIFICATION CONTRACT] wrote output/phase-2-website-item-classification-dry-run-20260510.json
[WEBSITE ITEM CLASSIFICATION CONTRACT] PASS (dry_run)
  expected_total: 53
  matched_count: 53
  desired_counts: {'checkout_ready_after_small_fix': 15, 'quote_first': 33, 'hide_or_needs_review': 5}
  planned_change_count: 48
  applied_change_count: 0
  only_mutated_doctype: Website Item
  only_mutated_fields: ['lt_product_page_type', 'lt_commerce_lane']
  stored_counts_for_targets: {'simple_product|checkout': 0, 'complex_custom_product|quote_first': 0, 'needs_review|needs_review': 5}
  reversal_note: Use each record's name with reverse_set.product_page_type and reverse_set.commerce_lane to restore prior Website Item field values. No publish/delete/reimport/media/price fields are touched by this verifier.
```

Dry-run gate result: exact expected 53 Website Items, no missing identities, no ambiguous identities, and only the two Website Item classification fields targeted. Apply was allowed by the Phase 2 stop conditions.

## Apply output

Command:

```bash
python scripts/verify/website_item_classification_contract.py --apply --report output/phase-2-website-item-classification-apply-20260510.json
```

Output:

```text
[WEBSITE ITEM CLASSIFICATION CONTRACT] wrote output/phase-2-website-item-classification-apply-20260510.json
[WEBSITE ITEM CLASSIFICATION CONTRACT] PASS (apply)
  expected_total: 53
  matched_count: 53
  desired_counts: {'checkout_ready_after_small_fix': 15, 'quote_first': 33, 'hide_or_needs_review': 5}
  planned_change_count: 48
  applied_change_count: 48
  only_mutated_doctype: Website Item
  only_mutated_fields: ['lt_product_page_type', 'lt_commerce_lane']
  stored_counts_for_targets: {'simple_product|checkout': 15, 'complex_custom_product|quote_first': 33, 'needs_review|needs_review': 5}
  reversal_note: Use each record's name with reverse_set.product_page_type and reverse_set.commerce_lane to restore prior Website Item field values. No publish/delete/reimport/media/price fields are touched by this verifier.
```

Note: an initial apply wrapper attempt failed before reaching the verifier because Frappe `bench execute --kwargs` expects a Python literal (`True`) rather than JSON (`true`). The wrapper was corrected and rerun. The successful apply above is the mutation witness.

## Post-apply report output

Command:

```bash
python scripts/verify/website_item_classification_contract.py --report output/phase-2-website-item-classification-post-apply-report-20260510.json
```

Output:

```text
[WEBSITE ITEM CLASSIFICATION CONTRACT] wrote output/phase-2-website-item-classification-post-apply-report-20260510.json
[WEBSITE ITEM CLASSIFICATION CONTRACT] PASS (dry_run)
  expected_total: 53
  matched_count: 53
  desired_counts: {'checkout_ready_after_small_fix': 15, 'quote_first': 33, 'hide_or_needs_review': 5}
  planned_change_count: 0
  applied_change_count: 0
  only_mutated_doctype: Website Item
  only_mutated_fields: ['lt_product_page_type', 'lt_commerce_lane']
  stored_counts_for_targets: {'simple_product|checkout': 15, 'complex_custom_product|quote_first': 33, 'needs_review|needs_review': 5}
  reversal_note: Use each record's name with reverse_set.product_page_type and reverse_set.commerce_lane to restore prior Website Item field values. No publish/delete/reimport/media/price fields are touched by this verifier.
```

Post-apply result: all 53 target Website Items now match the desired stored classifications; planned change count is 0.

## Reversal notes

The dry-run/apply JSON reports include per-record snapshots with:

- `name`
- `item_code`
- `web_item_name`
- `published`
- `before`
- `desired`
- `reverse_set`
- `modified_before`
- post-apply `after`/`expected` data in the apply report

Manual reversal, if needed, is to set only these two fields on each `Website Item` record using the report's `reverse_set` values:

- `lt_product_page_type`
- `lt_commerce_lane`

No product publishing, deleting, reimporting, price, media, or business-copy fields were touched by this verifier.

## Verification results

### Product-page architecture readiness

Command:

```bash
python scripts/verify/product_page_architecture_readiness.py --report output/product-page-architecture-readiness-infrastructure-research-20260510.json
```

Output:

```text
[PRODUCT PAGE ARCHITECTURE READINESS] wrote output/product-page-architecture-readiness-infrastructure-research-20260510.json
[PRODUCT PAGE ARCHITECTURE READINESS] BLOCKED
  technical_architecture_ok: True
  import_reopen_ok: False
  generated_at: 2026-05-10T15:52:31.706394
  pass: 13
  blocked: 1
  partial: 0
  deferred: 1
  info: 0
  - pass: research_and_plan_grounding - The lane is grounded in the ERPNext/Frappe receiving-architecture synthesis and OpenClaw/Codex handoff framing.
  - pass: two_reusable_template_types - The reusable types exist as logic classes, not product families: Ready-to-order page and Custom quote page.
  - pass: line_level_order_invoice_preservation - Selected product meaning is stored on Quotation Item, Sales Order Item, and Sales Invoice Item fields.
  - pass: ready_to_order_internal_cart_checkout - The internal ready-to-order path can preserve configured cart lines, checkout lines, and the confirmed foil-number add-on.
  - pass: quote_first_lead_to_draft_quotation - Custom quote pages preserve selected options, notes, and color recipes from product page to Lead and draft Quotation.
  - pass: accepted_quote_to_draft_sales_order - A human-approved product-page quote can create a draft Sales Order while preserving payloads and avoiding invoice/payment side effects.
  - pass: operator_quote_review_workflow - Internal product-page quote review reports customer-review readiness and blockers without creating orders, invoices, or payment requests.
  - pass: customer_quote_delivery_bcc - Reviewed product-page quote approval links have a customer sender and operator Desk send control with required business BCC.
  - pass: fail_loud_customer_and_operator_boundaries - Broken or incomplete paths block fake success with customer-safe copy and operator/developer evidence.
  - pass: source_dependency_matrices - Source-backed dependency matrices can narrow options and fail loudly for impossible or unknown selections.
  - pass: add_on_subsystem_beyond_foil_number - GL cleared the remaining source add-on approval block for commerce-lane testing.
  - pass: source_price_import_readiness - GL cleared the source price review block for commerce-lane testing.
  - pass: source_media_gallery_readiness - GL cleared the source media/gallery review block for commerce-lane testing.
  - blocked: public_ecommerce_reopen - Public shop, product, cart, checkout, and ready-to-order surfaces match the configured ecommerce mode.
    blocker: Public ecommerce is still paused by site config.
  - deferred: finance_bank_payment - Bank/finance/payment integration is explicitly backburnered and is not a current ecommerce-template blocker.
  blockers:
    - public_ecommerce_reopen: Public ecommerce is still paused by site config.
  import_reopen_blockers:
    - public_ecommerce_reopen: Public ecommerce is still paused by site config.
```

Result: technical architecture remains true; import/reopen remains blocked because public ecommerce is intentionally paused.

### Checkout fulfillment contract

Command:

```bash
python scripts/verify/checkout_fulfillment_contract.py
```

Output:

```text
[CHECKOUT FULFILLMENT CONTRACT] PASS
  rollback: verifier rolled back generated records
```

### Customer-note checkout preservation contract

Command:

```bash
python scripts/verify/customer_note_checkout_preservation_contract.py
```

Output:

```text
[CUSTOMER NOTE CHECKOUT PRESERVATION CONTRACT] PASS
  note_sales_order: SAL-ORD-2026-00021
  note_payment_request: ACC-PRQ-2026-00020
  note_communication: rbgjpvof5m
  operator_email_queue: rbjl9sfrq9
  no_note_sales_order: SAL-ORD-2026-00022
  no_note_payment_request: ACC-PRQ-2026-00021
  no_fake_customer_note: true
  survivor_counts: {'customer': 0, 'contact': 0, 'contact_email': 0, 'address': 0, 'sales_order': 0, 'payment_request': 0, 'payment_entry': 0, 'sales_invoice': 0, 'communication': 0, 'email_queue': 0}
  rollback: verifier rolled back all generated records
```

## Remaining blockers

- Public ecommerce remains paused by site config; this is expected and safe for Phase 2.
- Product price/media/business-copy approvals are still separate row-level launch gates.
- Phase 3 still needs first checkout product-family proof before any `checkout_ready_now` movement.
- No public launch/opening/payment/customer messaging action was performed.
