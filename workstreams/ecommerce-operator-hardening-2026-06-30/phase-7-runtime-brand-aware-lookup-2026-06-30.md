# Phase 7 - Runtime Brand-Aware Product Setup Lookup

Date: 2026-06-30

Status: source-only runtime lookup hardening complete and verified. No deploy,
cache clear, live ERPNext mutation, provider/payment/DNS/Frappe Cloud change,
customer message, or product-scope decision occurred.

## Purpose

Close the next source/runtime authority gap after Product Setup gained
`operating_brand`: runtime code must not resolve Product Setup by item/slug
alone when the same slug can later exist in more than one operating brand.

## What Changed

- `apps/locally_twisted/locally_twisted/product_setup_runtime.py`
  - Added `active_product_setup_name_for_website_item`.
  - `product_setup_schema_for_website_item` now accepts optional
    `operating_brand`.
  - Runtime lookup derives brand only from explicit input or source-declared
    Website Item metadata.
  - Lookup checks target Item, target Website Item, then product slug within
    the resolved brand.
  - Missing/invalid brand, invalid active Product Setup brand, same-brand
    duplicate active records, or target-item ambiguity returns no setup and
    logs `LT Product Setup active authority conflict`.
  - Target-item ambiguity no longer falls through to slug lookup.
- `apps/locally_twisted/locally_twisted/api/product_setup.py`
  - Public Product Setup API accepts optional `operating_brand` for future
    brand-aware frontends.
- `apps/locally_twisted/locally_twisted/product_options.py`
  - Product gallery/media lookup no longer uses direct `frappe.db.get_value`
    by `target_item_code`/`product_slug`; it uses the same active resolver.
- `apps/locally_twisted/locally_twisted/templates/generators/item/item_details.html`
  - Product-page embedded schema JSON passes `doc.get("operating_brand")`
    when Website Item metadata is available.
- `apps/locally_twisted/locally_twisted/seed/sync_commerce_rules.py`
  - Existing commerce custom-field seed now includes Website Item
    `operating_brand` and `operating_brand_authority_state` fields.
- `apps/locally_twisted/locally_twisted/patches/sync_product_setup_brand_runtime_fields_20260630.py`
  - Re-runs the idempotent commerce sync on migration so existing sites receive
    the Website Item brand metadata fields.
- `apps/locally_twisted/locally_twisted/patches.txt`
  - Registers the Website Item brand runtime field patch.
- `scripts/verify/product_blueprint_contract.py`
  - Added fake-Frappe verifier coverage for brand-scoped lookup, missing-brand
    failure, same-brand duplicate failure, and target-item ambiguity blocking
    fallback.

## Witness Review

Review type: real multi-agent witness/triad support.

- Intent/risk witness confirmed this phase should prevent wrong-brand runtime
  authority and must not claim live projection repair.
- Technical witness identified the exact resolver functions, direct call
  sites, the separate gallery/media shortcut, the need to avoid target-item
  ambiguity fallthrough, and the need for focused fake-Frappe verifier
  coverage.

Witness concern integrated: missing brand cannot quietly proceed. Runtime now
requires explicit brand input or source-declared Website Item metadata.

## Verification

Passed:

```bash
python -m py_compile apps/locally_twisted/locally_twisted/product_setup_runtime.py apps/locally_twisted/locally_twisted/api/product_setup.py apps/locally_twisted/locally_twisted/product_options.py apps/locally_twisted/locally_twisted/seed/sync_commerce_rules.py apps/locally_twisted/locally_twisted/patches/sync_product_setup_brand_runtime_fields_20260630.py scripts/verify/product_blueprint_contract.py
python scripts/verify/product_blueprint_contract.py
git diff --check
```

`product_blueprint_contract.py` result: 26 tests passed.

Capability gate: PASS.

Loaded resources:

- `capabilities/INDEX.md`
- `capabilities/failures/product-setup-projection-authority-drift.md`
- `capabilities/recipes/erpnext-product-blueprint-authoring.md`
- `capabilities/recipes/erpnext-catalog-variant-price-parity.md`
- `capabilities/recipes/erpnext-ecommerce-receiving-architecture.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/protective-contracts.md`

## Still Not Claimed

- No live Product Setup records were migrated or repaired.
- No public product page was re-proved after this source change.
- No Item Price, Website Item copy, media, cart, checkout, payment, document,
  or customer-message authority was repaired.
- Website Item `operating_brand` remains source-declared metadata, not live
  brand-lane proof.
- Database-level unique indexes were not added.
- Owner-visible blocker UI is still unbuilt.
- Publish/apply workflow is still unbuilt.

## Next Safe Work

1. Add owner-visible Product Setup blockers for runtime authority conflicts.
2. Start variant-axis classification/collapse planning with Birthday
   Deliveries as the first high-cardinality proof target.
3. Capture row-level rollback targets before any catalog mutation.
4. Design owner-visible publish/apply or direct runtime-authority workflow
   before repairing live product rows.
