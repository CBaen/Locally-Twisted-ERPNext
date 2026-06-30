# Phase 4 Authority Packet Resolver

Date: 2026-06-30

Status: offline blocker/resolver report implemented and verified from saved Phase 3 catalog artifacts. No live reads, live writes, cache clear, deploy, payment/provider action, or customer-message action occurred.

## Purpose

Turn saved catalog authority artifacts into product-by-product blocker packets. This is not a repair packet and not approval to mutate ERPNext. It is a safer planning layer that says why each product cannot be treated as owner-operable/live-authority-ready yet.

## Skill And Coordination

Capability gate: PASS.

Loaded resources:

- `capabilities/INDEX.md`
- `capabilities/failures/product-setup-projection-authority-drift.md`
- `capabilities/recipes/erpnext-product-blueprint-authoring.md`
- `capabilities/recipes/erpnext-catalog-variant-price-parity.md`
- `capabilities/recipes/erpnext-ecommerce-receiving-architecture.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/protective-contracts.md`

Witness process: real multi-agent witnessed work.

- Worker lane implemented the offline report tool.
- Technical witness required explicit blockers for brand lane, Product Setup match/status, price/copy gaps, option/add-on classification, rollback completeness, and artifact freshness.
- Main integration added stronger blockers for rollback packet incompleteness, public route proof, option/add-on/media runtime proof, and missing copy evidence.

## New Tool

- `scripts/dev/lt_product_setup_authority_packet_report.py`

The tool reads saved audit artifacts only. It does not read `.env`, call the network, inspect Docker, access ERPNext, use a browser, clear cache, deploy, or mutate data.

CLI:

```bash
python scripts/dev/lt_product_setup_authority_packet_report.py --input <artifact-file-or-dir> --output <report.json> --pretty --fail-on-blocker
```

Expected behavior:

- Directories skip collector/report indexes such as `index.json`, `blast-radius.json`, and `authority-packet-report.json`.
- Explicitly passing `index.json` is blocked as invalid input.
- `--fail-on-blocker` exits `1` when any product is blocked.

## Verification Run

Commands:

```bash
python -m py_compile scripts/dev/lt_product_setup_authority_packet_report.py
python scripts/dev/lt_product_setup_authority_packet_report.py --input /tmp/lt-catalog-authority-full-20260630 --output /tmp/lt-catalog-authority-full-20260630/authority-packet-report.json --pretty --fail-on-blocker
python scripts/dev/lt_product_setup_authority_packet_report.py --input /tmp/lt-catalog-authority-full-20260630/037-large-head-missionary.json --pretty --fail-on-blocker > /tmp/lt-large-head-missionary-authority-packet-report.json
python scripts/dev/lt_product_setup_authority_packet_report.py --input /tmp/lt-catalog-authority-full-20260630/index.json
python scripts/dev/lt_product_setup_catalog_blast_radius_report.py --input /tmp/lt-catalog-authority-full-20260630/037-large-head-missionary.json --fail-on-risk
python scripts/verify/product_setup_authority_parity_contract.py --input /tmp/lt-catalog-authority-full-20260630/037-large-head-missionary.json
```

Expected results:

- `py_compile` passed.
- Full-catalog authority packet report exited `1` with 47 blocked products and 284 blockers.
- Incident-product authority packet report exited `1` with 1 blocked product and 7 blockers.
- Explicit `index.json` input exited `2`.
- Existing blast-radius/parity tools still fail on `large-head-missionary` as expected.

## Catalog Blocker Breakdown

Full report output:

- `/tmp/lt-catalog-authority-full-20260630/authority-packet-report.json`

Counts:

- Products: 47.
- Blocked products: 47.
- Total blockers: 284.

Blocker breakdown:

- `brand_lane_unproved`: 47.
- `active_uniqueness_unproved`: 47.
- `public_route_proof_missing`: 47.
- `pre_mutation_rollback_packet_missing`: 47.
- `media_role_proof_missing`: 31.
- `product_setup_inactive`: 19.
- `missing_setup_price_values`: 19.
- `ambiguous_base_price_to_many_variants`: 19.
- `variant_explosion`: 6.
- `price_mismatch`: 1.
- `copy_authority_drift`: 1.

## Variant Explosion Targets

The first products that need SKU-axis review are:

| Item Code | Product | Variants | Severity |
|---|---|---:|---|
| `birthday-deliveries` | Birthday Deliveries | 2,430 | critical |
| `classic-column` | Classic Column | 1,836 | high |
| `star-column` | Star Column | 1,160 | high |
| `classic-arch` | Classic Arch | 816 | high |
| `pemium-organic-column` | Pemium Organic Column | 612 | high |
| `classic-organic-arch` | Classic Organic Arch | 612 | high |

These products should not be repaired by simply updating every generated SKU. They need axis classification: SKU-defining variant versus configuration-only selection, color recipe/customization, measurement/upload, review-only quote context, paid checkout add-on, or unsupported.

## Incident Product Packet

`large-head-missionary` is blocked by:

- `brand_lane_unproved`.
- `active_uniqueness_unproved`.
- `price_mismatch`: 30 Product Setup rows at `125.00` versus 30 Item Prices at `175.00`.
- `media_role_proof_missing`: 15 media rule rows need role proof.
- `public_route_proof_missing`: the full-catalog artifact skipped public GET.
- `pre_mutation_rollback_packet_missing`.
- `copy_authority_drift`: Product Setup story/details differ from Website Item public fields.

Next action for the product remains: resolve brand lane proof before any Product Setup authority or repair decision.

## Next Safe Work

Do not repair live products yet.

The next implementation slice should build source-level Product Setup authority controls:

- add or resolve an explicit brand-lane source for Product Setup/Website Item authority;
- enforce one active Product Setup per target Item, route/slug, and brand lane;
- add an owner-visible blocker report using the same blocker categories;
- start variant-axis classification on the six explosion products, with Birthday Deliveries first;
- only after that, design the no-write projection-to-rollback packet for a controlled repair.
