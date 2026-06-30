# Phase 3 Catalog Authority Audit

Date: 2026-06-30

Status: live read-only full-catalog authority artifact collection completed. No live writes, cache clear, deploy, payment/provider action, or customer-message action occurred.

## Purpose

Scale the Product Setup authority proof from one incident product to the whole published shop catalog. The output is evidence for planning and repair packets only. It is not a live repair plan and not approval to mutate ERPNext.

## Skill And Coordination

Capability gate: PASS.

Loaded resources:

- `capabilities/INDEX.md`
- `capabilities/failures/product-setup-projection-authority-drift.md`
- `capabilities/recipes/erpnext-product-blueprint-authoring.md`
- `capabilities/recipes/erpnext-catalog-variant-price-parity.md`
- `capabilities/recipes/erpnext-ecommerce-receiving-architecture.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/protective-contracts.md`

Witness process: real multi-agent triad.

- Worker lane built the first scoped collector.
- Technical/adversarial witness warned that missing Product Setup, duplicate Product Setup authority, missing price rows, and unproved brand lane must be blockers, not clean results.
- Main integration hardened matching, chunked large Item Price reads, fixed noisy false-positive reporting in existing offline verifiers, and ran live read-only smoke/full-catalog proof.

## New And Updated Tools

New:

- `scripts/dev/lt_live_readonly_catalog_authority_audit.py`

Updated:

- `scripts/dev/lt_product_setup_catalog_blast_radius_report.py`
- `scripts/verify/product_setup_authority_parity_contract.py`

The collector uses Frappe Cloud only to obtain a temporary site session, then performs live ERPNext `GET` requests and optional public route `GET` requests. It writes local JSON artifacts only.

Blocked flags intentionally exit nonzero:

- `--clear-cache`
- `--write-erpnext`
- `--deploy`

## Verification Run

Commands:

```bash
python -m py_compile scripts/dev/lt_live_readonly_catalog_authority_audit.py scripts/dev/lt_product_setup_catalog_blast_radius_report.py scripts/verify/product_setup_authority_parity_contract.py
python scripts/dev/lt_live_readonly_catalog_authority_audit.py --dry-run --limit 2 --output-dir /tmp/lt-catalog-authority-dryrun
python scripts/dev/lt_live_readonly_catalog_authority_audit.py --dry-run --clear-cache
python scripts/dev/lt_live_readonly_catalog_authority_audit.py --dry-run --write-erpnext
python scripts/dev/lt_live_readonly_catalog_authority_audit.py --dry-run --deploy
python scripts/dev/lt_live_readonly_catalog_authority_audit.py --limit 1 --public-get --output-dir /tmp/lt-catalog-authority-smoke
python scripts/dev/lt_live_readonly_catalog_authority_audit.py --output-dir /tmp/lt-catalog-authority-full-20260630 --timeout 60
python scripts/dev/lt_product_setup_catalog_blast_radius_report.py --input /tmp/lt-catalog-authority-full-20260630 --output /tmp/lt-catalog-authority-full-20260630/blast-radius.json --fail-on-risk
python scripts/verify/product_setup_authority_parity_contract.py --input /tmp/lt-catalog-authority-full-20260630/037-large-head-missionary.json
python scripts/dev/lt_product_setup_projection_preview.py --audit-json /tmp/lt-catalog-authority-full-20260630/037-large-head-missionary.json --output /tmp/lt-catalog-authority-full-20260630/037-large-head-missionary-projection.json --fail-on-drift
```

Expected results:

- Dry-run passed without env, login, network, or writes.
- Dangerous flags exited `2`.
- One-product smoke wrote one artifact and failed only on intended business blockers.
- Full published-catalog collection wrote 47 product artifacts and exited `1` because blockers were found.
- Catalog blast-radius report exited `1` because risk/blockers were found.
- `large-head-missionary` parity verifier exited `1` with price/copy drift plus brand-lane blocker.
- `large-head-missionary` projection preview exited `1` with proposed no-write changes and blockers.

## Full Catalog Findings

Saved local evidence directory:

- `/tmp/lt-catalog-authority-full-20260630`

Important: this `/tmp` directory is local runtime evidence, not committed source truth.

Full collector index summary:

- Published Website Items processed: 47.
- Product artifacts written: 47.
- Product Setup matches: 47.
- Missing Product Setup matches: 0.
- Ambiguous Product Setup matches: 0.
- Products with failures: 47.
- Total failures: 66.
- Product Setups seen: 51.

Failure categories:

- Brand lane not proved: 47 products.
- Matched Product Setup not in an active authority status: 19 products.

Product Setup status distribution across the 47 published products:

- `Local Preview Ready`: 28.
- `Draft`: 19.

Variant/price scale:

- Maximum variants on one published product: 2,430.
- Maximum Item Price rows on one published product: 2,430.
- Products with zero Item Price rows: 0.
- Distinct Item Price value sets across published products: 30.

## Incident Product Recheck

Artifact:

- `/tmp/lt-catalog-authority-full-20260630/037-large-head-missionary.json`

The parity verifier reports:

- 30 Product Setup price rows at `125.0`.
- 30 `Standard Selling` Item Price rows at `175.0`.
- Price drift for 30 item codes.
- Product Setup story copy differs from Website Item public story copy.
- Product Setup details copy differs from Website Item public details copy.
- Brand lane is not proved by current Website Item/Product Setup fields, so mutation remains blocked.

The projection preview reports:

- 30 proposed `Item Price.price_list_rate` changes from `175.0` to `125.0`.
- 2 Website Item copy suggestions.
- Rollback targets are limited to fields present in the saved artifact.
- Limitations remain for brand lane proof, active Product Setup uniqueness, rollback snapshot completeness, and business copy approval.

## Tooling Fixes From This Phase

The first live smoke hit a real catalog-scale failure: one product had hundreds of variants, and a single Item Price query became too long. The collector now chunks Item Price reads in small batches.

The blast-radius helper previously treated `index.json` as a product artifact when pointed at a collector output directory. It now skips collector/report index files.

The projection verifier previously treated a nested `{"drift_detected": false}` object as drift because the object was nonempty. It now honors `drift_detected` as an explicit false signal.

## Next Safe Work

Do not repair live products yet.

Next implementation should build a catalog authority resolver/packet layer that:

- resolves or explicitly blocks brand lane per product;
- enforces one active Product Setup per target Item, route/slug, and brand lane;
- classifies each option axis as SKU-defining variant, configuration-only, color recipe/customization, measurement/upload, review-only quote context, paid checkout add-on, or unsupported;
- identifies which products have variant explosion that should collapse into non-SKU configuration choices;
- creates pre-mutation rollback snapshots for Website Item, Item, Item Price, media, copy, and relevant child rows;
- only then proposes a Product Setup publish/apply or direct-runtime-authority implementation.
