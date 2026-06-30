# Public Runtime Flow Map

Date: 2026-06-30

Status: source/public-render mapping. Local runtime and live Desk rows were not authenticated during this pass.

## High-Level Flow

The public ecommerce path is not one pipeline. It is a chain of resolvers:

1. `/shop` listing.
2. Product page render.
3. Product options and variant selector.
4. Product Setup runtime schema.
5. Browser cart state.
6. Cart server resolution.
7. Checkout server resolution.
8. Sales Order lines.
9. Payment Request and hosted payment session.
10. Payment success/webhook reconciliation.
11. Sales Invoice and receipt/customer communications.

A backend product change must be proven across every resolver that can display, price, sell, or document the product.

## `/shop` Listing

Primary file: `apps/locally_twisted/locally_twisted/www/shop.py`

Current behavior:

- Reads published root `Website Item` rows.
- Joins `Item Price` for `Standard Selling`.
- Filters out variant child rows by checking the linked Item's `variant_of`.
- Calls `apply_variant_starting_price` for variant templates.
- Resolves product page type and commerce lane through `product_page_contract_for_website_item`.
- Renders cards through `shop.html`.

Important split:

- Listing can display a product/card from Website Item state while cart/checkout later reject it for missing disabled Item, missing checkout lane, or missing Item Price.

Immediate red-alarm check:

- The listing SQL does not explicitly require `Item.disabled = 0`.
- A missing or disabled linked Item should not produce a public card.

## Product Page Copy

Primary file: `apps/locally_twisted/locally_twisted/templates/generators/item/item_details.html`

Current behavior:

- Title uses `doc.web_item_name`.
- Main story uses `doc.lt_brand_description`.
- "What's Included" uses `doc.lt_product_details`.
- Standard `web_long_description` or `description` is only a fallback when both LT custom fields are empty.

Meaning:

- The public description authority is LT custom Website Item copy, not the standard description field in the normal ERPNext path.
- A human can edit a standard field and see no public change.

## Product Page Price

Primary files:

- `apps/locally_twisted/locally_twisted/templates/generators/item/item_configure.html`
- `apps/locally_twisted/locally_twisted/product_options.py`
- `apps/locally_twisted/locally_twisted/api/variant_selector.py`
- `apps/locally_twisted/locally_twisted/overrides/website_item.py`

Current behavior:

- Starting price for variant templates is the lowest active variant `Item Price` in `Standard Selling`.
- Exact selected variant price comes from Webshop/ERPNext variant selector logic through LT override.
- Product Setup `base_price` can be embedded in the page schema but does not override live variant Item Prices.

Live product evidence:

- Large Head Missionary embedded setup schema showed `base_price: 125.0`.
- Public product display and variant API showed `$175.00`.

Meaning:

- Product Setup commerce metadata and sellable Item Price rows can diverge.
- The customer-facing price chain currently trusts Item Price for sellable variants.

## Product Page Options

Primary files:

- `apps/locally_twisted/locally_twisted/product_options.py`
- `apps/locally_twisted/locally_twisted/product_page_runtime.py`
- `apps/locally_twisted/locally_twisted/product_setup_runtime.py`
- `apps/locally_twisted/locally_twisted/templates/generators/item/item_configure.html`

Current behavior:

- Webshop variant attributes are filtered/projected through LT rules.
- Required variant attributes become selectors.
- Product Setup schema can add configuration groups, color recipes, media rules, content rules, add-ons, and pricing rules.
- Browser selection posts to variant/media/product setup APIs.

Meaning:

- SKU-defining options and configuration-only options are different architectural categories.
- They must not be merged casually. SKU-defining choices need variant Items and Item Prices. Configuration-only choices need runtime JSON, validation, and document preservation.

## Product Media And Gallery

Primary files:

- `apps/locally_twisted/locally_twisted/templates/generators/item/item_image.html`
- `apps/locally_twisted/locally_twisted/product_options.py`
- `apps/locally_twisted/locally_twisted/api/variant_media.py`
- `apps/locally_twisted/locally_twisted/product_variant_media.py`

Current behavior:

- Main product page gallery prefers LT projected gallery slides.
- Product-level gallery source is Website Item primary image plus Website Slideshow rows plus approved Product Setup media rules.
- Variant Item images are held back unless the product/page/media rule allows them.
- Cart can select Product Setup media or approved variant media.

Meaning:

- Photos are not one field.
- A media change needs proof for Website Item primary image, gallery rail, selected variant image, cart image, and payment/order images when applicable.

## Add-Ons

Primary file: `apps/locally_twisted/locally_twisted/product_page_runtime.py`

Current behavior:

- Static foil-number add-on exists for approved product families.
- Product Setup-authored add-ons can become runtime add-on contracts only when approved for checkout and using fixed Item Price.
- At checkout, add-ons become separate Sales Order Item lines.
- Missing add-on Item or missing Item Price logs and fails loudly.

Meaning:

- Add-ons are not just frontend option labels.
- A paid add-on needs an enabled Item, Item Price, runtime contract, cart display, Sales Order line, invoice copy, and payment label.

## Cart

Primary files:

- `apps/locally_twisted/locally_twisted/www/lt_cart.py`
- `apps/locally_twisted/locally_twisted/public/js/lt-guest-cart.js`
- `apps/locally_twisted/locally_twisted/api/cart.py`

Current behavior:

- Browser cart state lives in localStorage.
- Server endpoint `get_cart_items` resolves each submitted item code/configuration.
- Server rejects unavailable, unpublished, quote-required, unpriced, disabled, or option-incomplete items.
- Server ignores client-supplied prices and rereads Item Price.
- Server expands display lines for add-ons.

Meaning:

- Cart is a second source of truth check after product page display.
- If product page display and cart resolution disagree, customer trust breaks.

## Checkout And Sales Order

Primary file: `apps/locally_twisted/locally_twisted/www/checkout.py`

Current behavior:

- Checkout re-resolves cart items server-side.
- Pricing comes from Item Price only.
- Configuration fields are written onto Sales Order Item rows.
- Add-ons are written as additional Sales Order Item rows.
- Fulfillment/tax rules are applied per line.
- Ecommerce pause can block checkout APIs with a customer-safe message and Error Log evidence.

Meaning:

- Checkout is safer than product display because it revalidates, but that also means display can promise something checkout refuses.

## Payment, Invoice, Receipt

Primary files:

- `apps/locally_twisted/locally_twisted/payments/stripe_session.py`
- `apps/locally_twisted/locally_twisted/payments/stripe_webhook.py`
- `apps/locally_twisted/locally_twisted/www/payment_success.py`
- `apps/locally_twisted/locally_twisted/product_page_runtime.py`

Current behavior:

- Payment line items are built from Sales Order rows.
- Payment session amount is checked against Sales Order grand total.
- Webhook/session success must reconcile metadata, amount, currency, Payment Request, and Sales Order before downstream success.
- Sales Order Item configuration fields can be copied to Sales Invoice Item rows.

Meaning:

- Payment can be internally consistent with ERPNext while still wrong if upstream Item Price or product meaning is wrong.
- The price identity invariant must start at product setup/source, not only at Stripe amount reconciliation.

## Cache Reality

The observed product URL returned `x-from-cache: False`, and `/shop`, `/cart`, and `/checkout` use dynamic/no-cache patterns. Frappe still has website and document caches, and the app has explicit cache clear scripts after Jinja/CSS/controller changes.

This incident should not be treated as "probably cache" unless an authenticated DB comparison proves the live row is correct and only rendered output is stale.
