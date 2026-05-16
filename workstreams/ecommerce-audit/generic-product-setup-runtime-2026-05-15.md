# Generic Product Setup Runtime - 2026-05-15

## Purpose

Implement the ecommerce system around generic Product Setup behavior, not around current catalog products. Product Setup is now the staff-facing source of truth for selection groups, SKU-defining axes, configuration-only choices, add-ons, pricing status, media rules, and commerce outcome.

## Implemented

- `LT Product Blueprint` now has generic selection behavior fields: SKU-defining variant, configuration only, add-on, measurement/text, upload/reference, and review only.
- Product Setup schemas are built by `locally_twisted.product_setup_runtime`, exposed to product pages, and resolvable through `locally_twisted.api.product_setup`.
- The frontend loads `lt-product-setup-runtime.js`, renders backend-authored configuration groups, and sends those groups in the versioned cart payload.
- Checkout validates the Product Setup payload server-side before Sales Order line creation.
- Configuration-only selections are preserved in `configuration_groups` and do not create variant combinations.
- SKU-defining selections resolve against the actual ERPNext variant chosen for checkout.
- Cart line keys include the configuration payload, so different configurations of the same SKU remain separate.
- Sales Order, Sales Invoice, Quotation, receipt/payment labels, and operator review paths continue to preserve structured configuration JSON plus readable summaries through the existing line fields.
- Approved Product Setup media rules can drive customer-facing image changes. Raw variant images remain held back unless an approved media rule exists.
- `LT Owner Home` `Products` / `Add Product` now route employees into `LT Product Blueprint`, not raw ERPNext `Item`.
- Rollback-safe staff proof now verifies an `Item Manager` user can create a Product Setup with 60 configuration choices, a max of 9 selections, 2 SKU-defining variants, and 1 approved media rule through the Product Blueprint document path.
- Local `frontend` was migrated and workspace sync was run after DocType changes.

## Proof

- `bench --site frontend migrate` succeeded locally on 2026-05-15.
- `bench --site frontend execute locally_twisted.seed.sync_backend_workspaces.execute` updated `LT Owner Home`.
- `python scripts/verify/product_blueprint_contract.py` passed.
- `python scripts/verify/product_page_runtime_contract.py` passed.
- `python scripts/verify/cart_checkout_contract.py` passed.
- `python scripts/verify/backend_workspace_parity.py` passed.
- `python scripts/verify/product_page_architecture_contract.py` passed.
- `python scripts/verify/product_blueprint_live_contract.py` passed.
  - Staff setup proof inside this verifier: 60 configuration choices, max 9, 2 variants, 1 media rule, rollback-safe.
- `python scripts/verify/checkout_product_family_contract.py` passed.
- `python scripts/verify/quote_event_checkout_boundary_contract.py` passed.
- `python scripts/verify/stripe_amount_parity_contract.py` passed.
- `python scripts/verify/verifier_cli_contract.py` passed.
- Controlled local open/restore proof passed:
  - `lt_ecommerce_paused` was temporarily set to `0` on local `frontend`.
  - `python scripts/verify/ecommerce_pause_contract.py` passed in open-testing mode.
  - `python scripts/verify/variant_media_contract.py` passed against rendered product pages.
  - `lt_ecommerce_paused` was restored to `1`.
  - `python scripts/verify/ecommerce_pause_contract.py` passed again in paused mode.

## Cleanup Reverification

Reran during dirty-file cleanup on 2026-05-15:

- `python -m compileall ...` for Product Setup API/runtime/DocType modules.
- `docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend migrate`
- `docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.seed.sync_backend_workspaces.execute`
- `python scripts\verify\product_blueprint_contract.py`
- `python scripts\verify\product_page_runtime_contract.py`
- `python scripts\verify\cart_checkout_contract.py`
- `python scripts\verify\product_blueprint_live_contract.py`
- `python scripts\verify\backend_workspace_parity.py`
- `python scripts\verify\product_page_architecture_contract.py`
- `python scripts\verify\checkout_product_family_contract.py`
- `python scripts\verify\quote_event_checkout_boundary_contract.py`
- `python scripts\verify\stripe_amount_parity_contract.py`
- `python scripts\verify\variant_media_contract.py`
- `python scripts\verify\verifier_cli_contract.py`
- `python scripts\verify\ecommerce_pause_contract.py`

## Known Remaining Gates

- `python scripts/verify/product_import_readiness_gate.py --json` is still blocked by a stale catalog snapshot dated 2026-05-11. This is an import/destructive-readiness blocker, not a Product Setup runtime failure.
- Browser product-page media proof now passes when ecommerce is temporarily opened in local testing mode, and the pause lock has been restored afterward.
- Public/staging/live ecommerce still requires the normal Frappe Cloud, Stripe, webhook, policy, product scope, and real low-risk payment gates.
