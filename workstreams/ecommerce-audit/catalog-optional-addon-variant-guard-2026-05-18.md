# Catalog Optional Add-On Variant Guard - 2026-05-18

## Purpose

Close the local catalog regression where stale `Add Foil Number` variants were
enabled as if they were required SKU choices after the all-Odoo sellable
reimport.

This is a local/source repair only. No Frappe Cloud update, DNS change, Stripe
change, live deploy, or public checkout exposure was performed.

## Problem

`catalog_variant_contract.py` failed after local proof because 13 bouquet
templates had 33 enabled variants each instead of 3. The extra 30 per bouquet
were stale variants with `Add Foil Number` stored as an Item Variant Attribute.

That is wrong for the current product model:

- `Bouquet Size` is the required SKU axis.
- `Add Foil Number` is a paid add-on handled by the checkout add-on subsystem.
- Add-ons must not become required variant choices.

## Actions

- Ran the existing local ERPNext repair:
  `bench --site frontend execute locally_twisted.seed.repair_optional_addon_variants.execute`.
- The repair checked 13 bouquet templates and disabled 390 stale optional
  add-on variants while keeping the 39 required bouquet-size variants enabled.
- Wired that idempotent repair into `seed_catalog.py` after destructive import
  so a future rerun does not require a remembered manual cleanup step.
- Updated the product-page readiness label check from stale `Custom quote page`
  wording to the current `Configurable product page` label.
- Updated Product Setup source defaults/options to `Configurable product page`
  while preserving `Custom quote page` as a legacy safe alias for old drafts.
- Ran local `bench --site frontend migrate` so the Product Setup DocType label
  exists in the local database.

## Verification

Green after repair and migrate:

- `python scripts\verify\catalog_variant_contract.py`
- `python scripts\verify\product_page_architecture_readiness.py --json`
- `python scripts\verify\product_import_readiness_gate.py --report output\product-import-readiness-gate.json`
- `python scripts\verify\product_blueprint_contract.py`
- `bench --site frontend execute locally_twisted.verify.product_blueprint_contract.run`
- `python scripts\verify\cart_checkout_contract.py`
- `python scripts\verify\variant_media_contract.py`
- `python scripts\verify\checkout_product_family_contract.py`
- `python scripts\verify\product_add_on_dependency_contract.py`
- `python scripts\verify\product_page_runtime_contract.py`

Local DB check after migrate:

- `LT Product Blueprint.page_template` default:
  `Configurable product page`
- `LT Product Blueprint.page_template` options:
  `Ready-to-order page`, `Configurable product page`

## Current Boundary

Local ecommerce remains the test/proof surface. Live checkout still needs the
separate staging/live release packet, Stripe/live payment gates, and explicit
GL approval.
