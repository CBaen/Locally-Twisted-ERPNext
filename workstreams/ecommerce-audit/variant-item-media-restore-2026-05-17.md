# Variant Item Media Restore - 2026-05-17

## Purpose

Restore the product behavior GL caught on Encanto Bouquet: when a customer
selects a simple checkout variant with its own approved `Item.image`, the
product page, cart, checkout payload, and receipt helper must use that selected
variant image.

This is source/local work only. No Frappe Cloud, staging, live, Stripe, DNS, or
public ecommerce exposure change was performed.

## User-Visible Failure

Route tested by GL:

- `http://localhost:8081/shop-items/bouquets/encanto-bouquet`

Selecting `Small`, `Medium`, or `Large` kept the main product image on
`/files/encanto-bouquet.png` even though the backend Item variants already had
their own images:

- `encanto-bouquet-SMA` -> `/files/encanto-bouquet-small.webp`
- `encanto-bouquet-MED` -> `/files/encanto-bouquet-medium.webp`
- `encanto-bouquet-LAR` -> `/files/encanto-bouquet-large.webp`

## Root Cause

Commits `019bf27 gate unclassified product media rendering` and `8e4a95b
harden ecommerce media readiness contract` correctly tried to prevent
unclassified source extra/gallery media from rendering. The implementation
overreached: it held every raw variant `Item.image` unless a Product Setup media
rule approved it. That erased an older working behavior where simple
ready-to-order variant images were customer-facing product selection evidence.

The bad pattern was also captured in the verifier: the old
`variant_media_contract.py` had been rewritten to expect ready-to-order variant
images to stay held. That made the regression look intentional until GL tested
the actual product.

## Implemented Fix

- Added `apps/locally_twisted/locally_twisted/product_variant_media.py` as the
  shared approval helper for direct variant Item media.
- `locally_twisted.api.variant_media.get_variant_media` now resolves media in
  this order:
  1. approved Product Setup media rule,
  2. simple checkout variant `Item.image`,
  3. parent Website Item fallback image.
- Complex/custom product raw Item images remain held unless Product Setup media
  approves them.
- `api/cart.py` and `product_page_runtime.py` now use the same helper, so the
  selected simple variant image cascades into cart display, Sales Order line
  JSON, and customer-facing receipt image helpers.
- `scripts/verify/variant_media_contract.py` now has both positive and negative
  guard coverage:
  - Encanto Small/Medium/Large must render their variant images.
  - Classic Arch complex raw Item image must remain held.
  - Encanto selected media must reach cart, Sales Order payload, and receipt
    helper.

## Verification

Passed locally after restarting the local Frappe backend worker and clearing
website cache:

- `python -m py_compile apps/locally_twisted/locally_twisted/product_variant_media.py apps/locally_twisted/locally_twisted/api\variant_media.py apps/locally_twisted/locally_twisted/api\cart.py apps/locally_twisted/locally_twisted/product_page_runtime.py scripts/verify/variant_media_contract.py`
- `python scripts/verify/variant_media_contract.py`
- `python scripts/verify/cart_checkout_contract.py`
- `python scripts/verify/product_page_runtime_contract.py`

## Boundary

This does not approve the 95 unclassified source extra images for parent
galleries, category/reference use, or complex Product Setup media. Those remain
held until classified.

This does not approve live ecommerce promotion. GL local testing and a separate
release packet are still required before any live push.

At closeout, the local `frontend` site is intentionally open with
`lt_ecommerce_paused=0` so GL can test `localhost:8081`. Restore it to `1`
after local acceptance or before starting release-packet work.

## Next Safe Step

GL tests the local Encanto product page and then the broader local ecommerce
journey. If accepted, prepare a separate staging/live release packet from the
source commit with Frappe Cloud, Stripe, DNS, webhook, and low-risk payment
gates.
