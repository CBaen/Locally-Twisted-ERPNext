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
- Product Setup media now supports `Selection combination` rules with explicit
  `selection_conditions` such as `Proof Size=Large` and
  `Proof Finish=Chrome`. The same server resolver drives product-page API,
  cart, checkout, Sales Order line payload, Stripe Checkout line images, and
  paid receipt thumbnails.
- `LT Owner Home` `Products` / `Add Product` now route employees into `LT Product Blueprint`, not raw ERPNext `Item`.
- Rollback-safe staff proof now verifies an `Item Manager` user can create a Product Setup with 60 configuration choices, a max of 9 selections, 2 SKU-defining variants, and 1 approved media rule through the Product Blueprint document path.
- Owner-profile proof now verifies `locallytwisted@gmail.com` can create and locally apply Product Setup records through the guarded Product Blueprint path. The apply helper creates the generated unpublished `Website Item` server-side without requiring the owner profile to receive raw Website Item permissions.
- Product-create capability proof now covers both `Item Manager` and
  `System Manager` users applying local Product Setup records without granting
  raw Website Item creation to the profile.
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
  - Owner setup proof inside this verifier: `locallytwisted@gmail.com`, 2 SKU-defining variants, 2 price rows, unpublished Website Item.
  - Staff setup proof inside this verifier: 60 configuration choices, max 9, 2 variants, 1 media rule, rollback-safe.
- `python scripts/verify/checkout_product_family_contract.py` passed.
- `python scripts/verify/quote_event_checkout_boundary_contract.py` passed.
- `python scripts/verify/stripe_amount_parity_contract.py` passed.
- `python scripts/verify/payment_cascade_contract.py` passed.
- `python scripts/verify/payment_webhook_contract.py` passed.
- `python scripts/verify/payment_success_reconciliation_contract.py` passed.
- `python scripts/verify/checkout_lead_conversion_contract.py` passed.
- `python scripts/verify/payment_launch_readiness.py` passed in local/test mode.
- `python scripts/verify/verifier_cli_contract.py` passed.
- Controlled local open/restore proof passed:
  - `lt_ecommerce_paused` was temporarily set to `0` on local `frontend`.
  - `python scripts/verify/ecommerce_pause_contract.py` passed in open-testing mode.
  - `python scripts/verify/variant_media_contract.py` passed against rendered product pages.
  - `apps/locally_twisted/locally_twisted/verify/product_blueprint_release_smoke.py`
    created a local 48-variant employee-authored proof product with generated
    images: route `/shop-items/table-decor/release-proof-complex-product-1779036020`,
    Website Item `WEB-ITM-0055`, selected variant
    `release-proof-complex-product-1779036020-LARGE-CHROME-WEIGHT`.
  - Real local browser/Stripe test-card proof completed for Sales Order
    `SAL-ORD-2026-00023`: product page selected
    `/files/lt-proof-large-chrome.png`, cart and checkout showed the same
    image, Stripe test checkout accepted the fake card, Payment Request
    `ACC-PRQ-2026-00020` became Paid, Payment Entry `ACC-PAY-2026-00002`
    paid Sales Invoice `ACC-SINV-2026-00003`, and customer receipt Email Queue
    `q710cltm2i` contained the selected image path and sent to the customer
    plus `locallytwisted@gmail.com`.
  - `lt_ecommerce_paused` was restored to `1`.
  - `python scripts/verify/ecommerce_pause_contract.py` passed again in paused mode.

## Cleanup Reverification

Reran during dirty-file cleanup on 2026-05-15 and complex media/payment
closeout on 2026-05-17:

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
- `python scripts\verify\payment_cascade_contract.py`
- `python scripts\verify\variant_media_contract.py`
- `python scripts\verify\verifier_cli_contract.py`
- `python scripts\verify\ecommerce_pause_contract.py`

## 2026-05-17 Complex Variant Media And Payment Closeout

- Added `Selection combination` media rules plus shared frontend/server media
  scoring so one selection or a multi-selection combination can intentionally
  pick the customer-facing product image.
- Cart, checkout, Stripe Checkout, Sales Order line JSON, Sales Invoice receipt
  copy, and customer receipt email now use the trusted server-selected media.
- Payment cascade was hardened after real fake-card testing found two blockers:
  Guest-context paid-order reconciliation could not create Payment Entries, and
  dynamic checkout tax rows were pointing at the group account
  `2300 - Duties and Taxes - LT`. Reconciliation now runs the trusted paid
  settlement step with server authority, retries billed Sales Orders by paying
  the linked Sales Invoice, and checkout taxes resolve to a non-group
  `LT Sales Tax Payable - LT` account created by `sync_commerce_rules`.
- Temporary image-generation scripts and local screenshot artifacts from the
  proof run were deleted after the proof images were uploaded into local
  ERPNext Files.

## Known Remaining Gates

- `python scripts/verify/product_import_readiness_gate.py --json` is still blocked by a stale catalog snapshot dated 2026-05-11. This is an import/destructive-readiness blocker, not a Product Setup runtime failure.
- Browser product-page media proof and one real local Stripe test-card purchase
  now pass when ecommerce is temporarily opened in local testing mode, and the
  pause lock has been restored afterward.
- Public/staging/live ecommerce still requires the normal Frappe Cloud, Stripe, webhook, policy, product scope, and real low-risk payment gates.
