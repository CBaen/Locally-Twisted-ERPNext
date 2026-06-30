# 2026-06-30 - Product Setup Save Is Not Public Authority Until Projection Proof Exists

## Decision

Product Setup is not allowed to imply a live customer-facing product change
from a normal Desk save alone.

For ecommerce product fields, LT must implement one explicit authority model
per field:

- Product Setup is the direct runtime authority; or
- Product Setup is a draft/review source that projects to Website Item, Item,
  Item Price, media, cart, checkout, document, and payment records through an
  explicit publish/apply contract.

Until that contract exists, agents must treat Product Setup saves as real
backend saves but not as public product-change proof.

## Trigger

GL reported that live Product Setup edits to `large-head-missionary` saved
successfully but did not change the public page.

Live authenticated read-only API proof confirmed:

- Product Setup `large-head-missionary` modified
  `2026-06-30 01:43:01.382176` by `locallytwisted@gmail.com`.
- Product Setup `base_price` and 30 Product Setup price rows were `125.0`.
- 30 live `Standard Selling` Item Price rows stayed `175.0`.
- The public product page still rendered `from $ 175.00`.
- Public product copy rendered from Website Item fields, not Product Setup
  top-level story/details fields.

## Reasoning

The owner-facing expectation is that an authorized backend user can manage the
shop without a developer for ordinary product maintenance. The current
architecture violates that expectation because a successful Product Setup save
can update an authoring record while the live website and commerce flow read
other records.

The raw catalog guard remains useful and should not be weakened. The missing
piece is a complete owner-safe replacement workflow that either projects
Product Setup data into the runtime records or makes Product Setup itself the
runtime authority with verifiers and fail-loud blockers.

## Alternatives Considered

- Hand-edit the one product's Item Price rows and Website Item copy. Rejected
  as a final answer because it would hide the architecture failure and leave
  the next product broken.
- Remove raw catalog protection so owners can edit Website Item and Item Price
  directly. Rejected because it increases the risk of unsafe catalog, checkout,
  and document drift.
- Treat this as cache. Rejected because live row proof showed Product Setup and
  Item Price/Website Item authorities actually disagree.

## Required Guard

Future repair work must create no-write preview and rollback proof before any
mutation. A product cannot be called live merely because Product Setup saved or
shows `Approved For Live`.

Required proof for existing-product price/copy changes:

- Product Setup row and child rows.
- Website Item public copy fields.
- Item template and active variant Items.
- Standard Selling Item Price rows.
- Public route visible price/copy.
- Cart/checkout resolver proof for checkout products.
- Modified timestamps and modified_by for every authority row.
- Rollback target before mutation.

## 2026-06-30 No-Write Tooling Follow-Up

The first saved-artifact tools now exist:

- `scripts/dev/lt_product_setup_projection_preview.py`
- `scripts/verify/product_setup_authority_parity_contract.py`
- `scripts/dev/lt_product_setup_catalog_blast_radius_report.py`

They intentionally fail on the saved `large-head-missionary` live
audit/projection artifacts. They do not approve mutation; they create the
evidence needed before repair planning.

## Receipts

- `workstreams/ecommerce-operator-hardening-2026-06-30/live-readonly-api-audit-large-head-missionary-2026-06-30.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/phase-2-projection-preview-parity-2026-06-30.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/phase-0-incident-audit-large-head-missionary-2026-06-30.md`
- `capabilities/failures/product-setup-projection-authority-drift.md`

## Decided By

Guiding Light requested the live API proof and approved stronger protective
contracts. Codex confirmed the live authority split and recorded the decision
on 2026-06-30.
