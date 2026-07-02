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
- Approved Product Setup media rules can drive customer-facing image changes.
  Product Setup media wins first. Simple checkout variant `Item.image` values
  are also approved selected media when the parent Website Item is
  `simple_product|checkout`. Complex/custom raw variant images remain held
  back unless an approved Product Setup media rule exists.
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
- `python scripts/verify/product_blueprint_contract.py`
- `python scripts/verify/product_page_runtime_contract.py`
- `python scripts/verify/cart_checkout_contract.py`
- `python scripts/verify/product_blueprint_live_contract.py`
- `python scripts/verify/backend_workspace_parity.py`
- `python scripts/verify/product_page_architecture_contract.py`
- `python scripts/verify/checkout_product_family_contract.py`
- `python scripts/verify/quote_event_checkout_boundary_contract.py`
- `python scripts/verify/stripe_amount_parity_contract.py`
- `python scripts/verify/payment_cascade_contract.py`
- `python scripts/verify/variant_media_contract.py`
- `python scripts/verify/verifier_cli_contract.py`
- `python scripts/verify/ecommerce_pause_contract.py`

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

## 2026-05-17 Simple Variant Media Regression Repair

- GL caught Encanto Bouquet size selection keeping the parent image even though
  ERPNext variant Items still had Small/Medium/Large images.
- Root cause: the unclassified source extra-image hold was applied broadly
  enough to hide simple checkout variant `Item.image` values, and the verifier
  had been rewritten to expect the broken behavior.
- Added the shared `product_variant_media.py` helper. Product Setup media
  rules still take precedence; simple checkout variant Item media now renders
  and cascades to cart, Sales Order payload, and receipt helpers; complex raw
  Item media remains held without Product Setup approval.
- Guard:
  `python scripts/verify/variant_media_contract.py`.
- Feature handoff:
  `workstreams/ecommerce-audit/variant-item-media-restore-2026-05-17.md`.

## 2026-05-21 Product Setup Media And Copy Expansion

- GL flagged that "primary product photo" was not enough for Jeff's expected
  owner workflow. The Desk label is now `Fallback/Main Product Photo`, with
  separate Product Setup tables for product gallery photos, option-specific
  image rules, and option-specific copy rules.
- Product Setup can now express:
  - default/fallback product image,
  - multiple approved gallery photos that sync to a `Website Slideshow`,
  - selected-option or exact-variant image rules,
  - selected-option or exact-variant title/story/details copy rules.
- The product page runtime now swaps selected Product Setup copy along with
  already-verified selected images and prices, then resets to default copy when
  the selection no longer matches an approved content rule.
- Backfill now represents existing variant `Item.image` mappings inside Product
  Setup media rules so owner review has the same evidence the storefront can
  already use. The current local catalog has no existing Website Slideshow rows,
  so Product Setup gallery support is present but `checked_gallery_rows` is `0`
  until Jeff/GL approve gallery images.
- Follow-up witness review found and closed guard gaps: local Product Setup
  apply now always keeps Website Items unpublished, `Visible in shop` requests
  cannot save with validation blockers such as missing customer-facing media,
  exact checkout price rows cannot target another product's Items, direct owner
  edits to `Website Slideshow` and `Website Slideshow Item` are blocked, and
  selected Product Setup copy is preserved into cart/checkout/Sales Order line
  payloads instead of remaining page-only state.
- Guards:
  `python scripts/verify/product_setup_catalog_coverage.py`,
  `npm run test:product-setup-content`,
  `python scripts/verify/product_blueprint_live_contract.py`,
  `python scripts/verify/variant_media_contract.py`,
  `npm run test:product-price-display`, and
  `npm run test:owner-product-safety`.

## 2026-05-22 Owner Guard Closeout Refinements

- The owner-product lane was re-run through a triad witness/recorder/fixer
  review after GL clarified this cannot be solo work. The closeout handoff is
  `owner-product-setup-guard-closeout-2026-05-22.md`.
- Local Product Setup apply now preserves existing public Website Item
  `published` state. It refuses hidden->visible, public->hidden, and public
  route-change requests for existing Website Items; those changes belong to
  the reviewed staging/live release and redirect path.
- Product Setup sync dry runs now truthfully report existing records that
  would be updated, and missing price-row fills no longer clear existing option
  rows.
- Desk preview includes `target_item_code` and `target_website_item`, so
  preview and apply validation share the same target-link context.
- Product option display now splits stored option values into short display
  labels and included-copy detail. This fixes the duplicate long selected text
  GL showed in screenshots while keeping backend option matching intact.
- Foil-number add-ons remain add-ons, not variant axes; they now accept up to
  3 numeric digits and update visible price display with the add-on total.
- Owner guard coverage expanded from the original small probe set to `19/19`
  owner-like probes, including existing Item/Website Item save/delete/rename,
  Item Attribute, Item Attribute Value, Item Variant Attribute, Item Group,
  Website Slideshow, Website Slideshow Item, Webshop Settings, and the allowed
  Product Blueprint server context.
- Focused latest guards:
  `python scripts/verify/owner_catalog_guard_contract.py`,
  `python scripts/verify/product_blueprint_live_contract.py`, and
  `python scripts/setup/sync_product_blueprints_from_catalog.py`.
- Final pre-commit closeout additionally passed
  `npm run test:owner-product-safety`,
  `npm run test:product-options-experience`, `npm run test:public-network`,
  `npm run test:form-experience`, `npm run test:public-assets`,
  `allow_guest_surface_inventory.py`, `smoke_forms.py --shape-only
  --skip-newsletter`, `newsletter_concurrency_contract.py`, Python compile,
  JSON parse checks, and `git diff --check`.

## Known Remaining Gates

- `python scripts/verify/product_import_readiness_gate.py --json` is still blocked by a stale catalog snapshot dated 2026-05-11. This is an import/destructive-readiness blocker, not a Product Setup runtime failure.
- Browser product-page media proof and one real local Stripe test-card purchase
  now pass when ecommerce is temporarily opened in local testing mode, and the
  pause lock has been restored afterward.
- Public/staging/live ecommerce still requires the normal Frappe Cloud, Stripe, webhook, policy, product scope, and real low-risk payment gates.
