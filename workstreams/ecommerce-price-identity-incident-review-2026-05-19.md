# Ecommerce Price Identity Incident Review - 2026-05-19

This is the current incident lane for the Easter Bunny Ear Arch size-price
failure and the wider ERPNext ecommerce price-identity risk it exposed.

## Incident Statement

This was not a one-product import defect. It was a failure to protect the
enterprise ecommerce invariant:

> A customer-selected option set must resolve to one enabled sellable Item, and
> that exact Item's selling price must match the source pricing logic everywhere:
> product page, cart, checkout, Sales Order, Stripe amount, invoice, and receipt.

GL found the failure on:

`/shop-items/arches/easter-balloon-arch-bunny-ear`

Observed symptom: selecting `20ft` and `25ft` showed the same price even though
the source Odoo shop priced those options differently.

## Source Architecture

Official ERPNext docs confirm the relevant architecture:

- ERPNext Item Variant docs: an Item with variants becomes a template, and the
  template itself cannot be used directly in transactions. The variants are the
  practical transaction Items. Source:
  `https://docs.frappe.io/erpnext/user/manual/en/item-variants`
- ERPNext Item Price docs: Item Price is the record that logs the selling or
  buying rate for an Item and Price List. Source:
  `https://docs.frappe.io/erpnext/user/manual/en/item-price`
- ERPNext Shopping Cart docs: products with variants must be configured into a
  specific variant before cart. Source:
  `https://docs.frappe.io/erpnext/user/manual/en/shopping-cart`

LT's local runtime mostly follows that shape:

- `Item` variant is the sellable/accounting identity.
- `Website Item` is the route/display/commerce-lane wrapper.
- `/cart` and `/checkout` reprice from server-side `Item Price`; browser prices
  are presentation only.
- Sales Order, Stripe, invoice, and receipt helpers consume the resolved server
  line, so downstream systems can be perfectly consistent with a wrong backend
  Item Price.

## Forensic Findings

Team review lanes:

| Lane | Finding |
|---|---|
| Git history | `9aa117f` introduced `seed_catalog.py` with the explicit assumption that Odoo did not expose per-variant pricing and that base price applied to all combinations. That was the original flattening point. |
| ERPNext/Webshop architecture | Cart and checkout are structurally right to trust server `Item Price`; the corruption was upstream in the Item Price table and import path. Native Webshop selector/cache and public methods still need bypass/freshness guards. |
| Verification | Older gates proved variant shape, price existence, downstream ERPNext/Stripe parity, or bouquet-specific recovery. They did not prove source dynamic price parity for arches, columns, garlands, height, length, LED, topper, design, or other priced option axes. |
| Documentation/conversation evidence | Prior docs already warned that count parity and bouquet repair did not equal full catalog price correctness. Those warnings were not promoted into a blocking launch/import gate. |

Important distinction:

- A verifier saying "all variants have an Item Price" is not enough.
- A Stripe parity verifier saying "Stripe matches ERPNext" is not enough.
- A browser route proof saying "cart/checkout opens" is not enough.
- The required proof is source price logic -> ERPNext Item Price -> visible page
  -> cart -> checkout/order/payment/invoice/receipt.

## Immediate Local Containment

Local ERPNext has been repaired for the reported item and the wider local active
variant set.

Verified source sample:

| Variant | Odoo dynamic price | Local ERPNext after repair |
|---|---:|---:|
| `easter-balloon-arch-bunny-ear-20F` | `$375` | `$375` |
| `easter-balloon-arch-bunny-ear-25F` | `$440` | `$440` |

Local repair added:

- `apps/locally_twisted/locally_twisted/seed/repair_variant_price_modifiers_from_odoo.py`
- `scripts/verify/product_price_modifier_contract.py`
- `scripts/verify/product_price_display.spec.js`

Local apply evidence:

- 49 variant products inspected.
- 10,186 active variants checked.
- 8,405 `Item Price` rows corrected.
- Post-apply dry-run: 0 active variant prices would change.

Focused local proof:

```powershell
python scripts/verify/catalog_variant_contract.py
npm run test:product-prices
npm run test:product-price-display
npm run test:color-swatches
```

Exact product proof:

- Product page resolves `20ft` to `easter-balloon-arch-bunny-ear-20F` at
  `$375.00`.
- Product page resolves `25ft` to `easter-balloon-arch-bunny-ear-25F` at
  `$440.00`.
- `locally_twisted.api.cart.get_cart_items` returns server
  `price_list_rate=375.0` and `price_list_rate=440.0` for those two variants.

Gate caveat from the same closeout pass:

- `python scripts/verify/product_import_readiness_gate.py --json` now includes
  the new price commands but exits nonzero because the newest catalog snapshot
  is from 2026-05-17 and today is 2026-05-19. That is correct fail-loud
  behavior; destructive/import approval needs a fresh snapshot.
- `python scripts/verify/website_launch_verify.py` was started after wiring the
  new price steps. It passed verifier CLI, nav, public identity, passive layout,
  and container contract, then failed before reaching the new price steps on a
  separate contact-form layout target issue:
  `input#book_website` measured `6px by 44px`. Do not treat that as ecommerce
  price failure or price proof. The focused ecommerce price gates above are the
  current proof for this incident.

## Guard Changes

The guard stack now includes source-price parity, not only price existence.

- `npm run test:product-prices` now runs:
  - `scripts/verify/product_variant_price_contract.py`
  - `scripts/verify/product_price_modifier_contract.py`
- `npm run test:product-price-display` proves visible browser price and selected
  variant item code for the reported product.
- `npm run test:ecommerce-full` includes visible price display proof.
- `scripts/verify/website_launch_verify.py` now includes the broad source-price
  modifier gate and visible price-display gate.
- `scripts/verify/product_import_readiness_gate.py` now lists the broad price
  modifier, product-prices, visible price display, post-import checkout proof,
  and Stripe parity as required closeout commands.

## Remaining Risk

This incident is locally contained, not globally closed.

- The broad modifier repair assumes Odoo option price modifiers are additive for
  the required ERPNext variant axes. That matches the observed Odoo products,
  but it is not a full exhaustive customer-journey purchase for every option
  combination.
- Native Webshop selector/cache and public cart methods should be audited for
  bypasses around LT lane checks.
- Variant cache freshness needs a post-import/attribute-change guard.
- Same SKU with different configuration/media/add-ons needs deeper duplicate
  line proof through cart, Sales Order, invoice, receipt, and Stripe line labels.
- `python scripts/verify/cart_checkout_contract.py` currently has separate
  color-recipe drift because the tested color-recipe product routes to quote.
  Do not mix that with this price identity repair; handle it in the
  checkout/color-recipe lane.
- No staging/live deploy was performed by this incident lane.

## Required Next Gates Before Any Live Ecommerce Claim

1. Re-run source-price parity on the target site after import/release.
2. Prove visible price changes on at least one representative product from each
   priced-axis family: size, height, length, LED/design/topper/add-on where
   applicable.
3. Prove a cart/checkout/Sales Order/Stripe/invoice/receipt cascade with a
   non-first priced option such as `easter-balloon-arch-bunny-ear-25F`.
4. Prove color-only axes remain flat where they should be flat.
5. Prove quote-only/high-complexity products cannot silently enter paid checkout.
6. Keep `lt_ecommerce_paused=1` on staging/live until GL approves local design
   and logic, then staging proof, then live payment/cutover.

## Pattern To Teach Future Agents

When the surface is ecommerce, "it exists" is never proof. Correct proof must
follow the business truth through each identity boundary:

source option -> ERPNext sellable Item -> Item Price -> selector -> cart ->
checkout -> accounting document -> payment provider -> customer receipt.

If any step only checks internal agreement, it can faithfully preserve the wrong
business price.
