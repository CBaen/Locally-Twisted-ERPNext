# Phase 2 Projection Preview And Parity Proof

Date: 2026-06-30

Status: no-write tooling slice complete for the incident product. This is not
repair approval, not cache approval, not deploy approval, and not live mutation.

## Scope

This slice added offline artifact-backed tooling so future agents can prove the
Product Setup/runtime split without touching production:

- `scripts/dev/lt_product_setup_projection_preview.py`
- `scripts/verify/product_setup_authority_parity_contract.py`
- `scripts/dev/lt_product_setup_catalog_blast_radius_report.py`

All three tools read saved JSON artifacts only. They do not read `.env`, call
the network, inspect Docker, clear website cache, deploy, write ERPNext, touch
payments, or send customer messages.

## Triad Result

Review type: real multi-agent triad.

Lane A built the no-write projection preview. Lane B built the offline parity
contract. Lane C performed adversarial review and required two corrections:

- do not reuse the live audit helper's `PASS` as parity proof, because it only
  means collection succeeded;
- do not let projection preview imply mutation approval. It must show proposed
  row-level changes plus limitations and unresolved blockers.

The main integration pass accepted those corrections and added explicit preview
limitations for brand-lane proof, active Product Setup uniqueness, rollback
snapshot incompleteness, field-level scope, and business copy approval.

## Verified Commands

```bash
python -m py_compile \
  scripts/dev/lt_product_setup_projection_preview.py \
  scripts/dev/lt_product_setup_catalog_blast_radius_report.py \
  scripts/verify/product_setup_authority_parity_contract.py

python scripts/dev/lt_product_setup_projection_preview.py \
  --audit-json /tmp/lt-live-large-head-missionary-api-audit-2026-06-30.json \
  --output /tmp/lt-product-setup-projection-preview-main-review.json \
  --pretty

python scripts/dev/lt_product_setup_projection_preview.py \
  --audit-json /tmp/lt-live-large-head-missionary-api-audit-2026-06-30.json \
  --fail-on-drift

python scripts/verify/product_setup_authority_parity_contract.py \
  --input /tmp/lt-live-large-head-missionary-api-audit-2026-06-30.json

python scripts/verify/product_setup_authority_parity_contract.py \
  --input /tmp/lt-product-setup-projection-preview-main-review.json

python scripts/dev/lt_product_setup_catalog_blast_radius_report.py \
  --input /tmp/lt-product-setup-projection-preview-main-review.json \
  --output /tmp/lt-catalog-blast-radius-main-review.json \
  --pretty

python scripts/dev/lt_product_setup_catalog_blast_radius_report.py \
  --input /tmp/lt-product-setup-projection-preview-main-review.json \
  --fail-on-risk
```

Expected/current results:

- Projection preview on the saved live audit exits `0` by default and `1` with
  `--fail-on-drift`.
- Projection preview reports 30 Item Price changes from `175.0` to `125.0`,
  two Website Item copy suggestions, 30 Item Price rollback targets, and five
  limitations.
- Parity verifier fails on the live audit artifact with three drift findings:
  one price authority mismatch across 30 item codes and two copy mismatches.
- Parity verifier fails on the projection artifact with 32 drift findings:
  30 price changes and two copy suggestions.
- Blast-radius report on the projection artifact reports one risky product
  with `price_drift`, `copy_drift`, and `preview_limitations`; `--fail-on-risk`
  exits `1`.

## Tool Boundaries

`lt_product_setup_projection_preview.py`:

- input: one saved live-audit JSON;
- output: proposed Product Setup -> runtime row diffs, rollback targets, drift
  summary, blockers, limitations;
- refuses to invent a price projection when Product Setup price rows cannot map
  uniformly or by item code;
- marks copy changes as suggestions requiring business approval.

`product_setup_authority_parity_contract.py`:

- input: saved audit JSON or saved projection JSON;
- fails when Product Setup price/copy differs from runtime/public authority;
- distinguishes evidence collection from parity;
- allowance flags affect exit status only, not reported drift.

`lt_product_setup_catalog_blast_radius_report.py`:

- input: one or more saved audit/projection JSON artifacts or directories;
- output: product-by-product risk summary and next safe actions;
- is catalog-wide only when fed one saved artifact per relevant product.

## Remaining Blockers Before Repair

- Business price decision: whether this product should be live at `125.0` or
  remain `175.0`.
- Customer-approved copy decision: Product Setup top-level copy vs current
  Website Item public copy.
- Brand-lane proof on the affected rows.
- One-active-Product-Setup proof by target item, route, and brand lane.
- Full rollback snapshot for every row that would be touched.
- Cart/checkout no-write or local/test proof for selected variants.
- Catalog-wide saved read-only artifacts for every published Website Item.
- Pre-mutation release packet if any live/staging/local write path is opened.

## Next Safe Step

Generate saved read-only authority artifacts for the full published catalog,
then run projection preview/parity/blast-radius reporting across the artifact
set. Do not mutate live rows, clear cache, deploy, repair one product, or change
payments/customer messages from this phase alone.
