# Phase 6 Source Authority Packet Reporting

Date: 2026-06-30

Status: source-only offline authority packet reporting update implemented and verified. No deploy, cache clear, live ERPNext mutation, provider/payment/DNS/Frappe Cloud change, customer message, secret read, or product-scope decision occurred.

## Purpose

Make saved-artifact authority packets understand the new Product Setup source contract without pretending it is live proof.

`operating_brand` and same-brand active uniqueness are now reported as source-only evidence. They remain separate from live/public brand-lane proof, route proof, rollback packets, mutation approval, deploy approval, cache approval, payment/document identity, and customer-facing readiness.

## Witness Result

Review type: witnessed work with two read-only witness lanes.

Convergence:

- Technical witness found the collectors did not preserve `operating_brand`, and the packet report only had the older binary brand-lane model.
- Critical witness warned that `source_declared` must never become softer wording for `proved`.

Decision:

- Add a first-class `source_authority` packet section.
- Preserve `brand_lane_proved=False` unless separate live/public proof exists.
- Keep old saved artifacts blocked when they lack source-brand evidence or still contain price/copy/media/public-route/rollback blockers.

## Source Changes

- `scripts/dev/lt_product_setup_authority_packet_report.py`
  - Adds `source_authority.operating_brand`.
  - Adds `source_authority.same_brand_source_uniqueness`.
  - Distinguishes `source_declared`, `missing`, `invalid`, and live-proved brand states.
  - Keeps source uniqueness separate from mutation/release readiness.
- `scripts/dev/lt_live_readonly_catalog_authority_audit.py`
  - Preserves `LT Product Blueprint.operating_brand` in future live read-only saved artifacts and candidate summaries.
- `scripts/dev/lt_live_readonly_product_api_audit.py`
  - Preserves `operating_brand` in future single-product live read-only artifacts.
- `scripts/verify/product_setup_authority_packet_contract.py`
  - Adds synthetic offline contract tests for source-declared brand and same-brand source uniqueness.
- `scripts/verify/product_setup_authority_parity_contract.py`
  - Detects authority packet reports and fails if packet blockers remain or source-declared brand is treated as live proof.

## Verification

Commands passed:

```bash
python -m py_compile scripts/dev/lt_product_setup_authority_packet_report.py scripts/dev/lt_live_readonly_catalog_authority_audit.py scripts/dev/lt_live_readonly_product_api_audit.py scripts/verify/product_setup_authority_packet_contract.py scripts/verify/product_setup_authority_parity_contract.py
python scripts/verify/product_setup_authority_packet_contract.py
python scripts/dev/lt_product_setup_authority_packet_report.py --input /tmp/lt-catalog-authority-full-20260630 --output /tmp/lt-catalog-authority-full-20260630/authority-packet-report-source-authority-check.json --pretty --fail-on-blocker
python scripts/dev/lt_product_setup_authority_packet_report.py --input /tmp/lt-catalog-authority-full-20260630/037-large-head-missionary.json --pretty --fail-on-blocker > /tmp/lt-large-head-missionary-authority-packet-report-source-authority-check.json
python scripts/verify/product_setup_authority_parity_contract.py --input /tmp/lt-large-head-missionary-authority-packet-report-source-authority-check.json --input-type packet
```

Expected fail-loud results:

- Full old saved catalog packet report exited `1` with 47 blocked products and 265 blockers.
- Old `large-head-missionary` packet report exited `1` with seven blockers.
- Packet-aware parity verifier failed the old `large-head-missionary` packet with seven blockers.

The old blocker count changed from the Phase 4 report because same-brand source uniqueness is now checked only for the active source authority statuses that the save guard actually enforces: `Local Preview Ready`, `Staging Ready`, and `Approved For Live`.

Capability gate: PASS.

Loaded resources:

- `capabilities/INDEX.md`
- `capabilities/failures/product-setup-projection-authority-drift.md`
- `capabilities/recipes/erpnext-product-blueprint-authoring.md`
- `capabilities/recipes/erpnext-catalog-variant-price-parity.md`
- `capabilities/recipes/erpnext-ecommerce-receiving-architecture.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/protective-contracts.md`

## Not Fixed

This phase does not fix or prove:

- live Product Setup migration;
- live/public brand-lane proof;
- public product-page price/copy/media projection;
- runtime brand-aware lookup for cross-brand same-slug Product Setups;
- database-level uniqueness;
- rollback packet completeness;
- Item Price mutation or parity;
- cart/checkout/payment/document identity;
- customer-facing route proof;
- provider, DNS, Frappe Cloud, payment, or customer-message behavior.

## Next Safe Work

- Make runtime Product Setup lookup brand-aware before cross-brand same-slug active setups are allowed.
- Add owner-visible blocker reporting using the same blocker categories.
- Start variant-axis classification on Birthday Deliveries before any variant-collapse or price repair write.
- Build row-level rollback packet capture before any repair mutation.
