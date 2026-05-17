# Simple Purchasable Browser Proof

## Purpose

Local open-mode browser proof for the first simple repair-lane products. This
does not promote the products, keep ecommerce open, send email, create payment
records, or authorize live/customer exposure. The wrapper temporarily opened
local ecommerce and applied `simple_product|checkout` to the four Website Items,
ran the shared product/cart/checkout browser proof at desktop and mobile
widths, then restored the original Website Item contracts and
`lt_ecommerce_paused=1`.

## Products

| Product | Route | Browser item code | Price | Result |
|---|---|---|---:|---|
| Easter Arch | `/shop-items/arches/easter-arch` | `easter-arch` | 250.00 | PASS |
| Large head Missionary | `/shop-items/bouquets/large-head-missionary` | `large-head-missionary-ELD-BLU-BLA` | 175.00 | PASS |
| Mother's day front yard 7' Column | `/shop-items/columns/mothers-day-front-yard-7-column` | `mothers-day-front-yard-7-column` | 140.00 | PASS |
| Pride Arch | `/shop-items/arches/pride-arch` | `pride-arch` | 325.00 | PASS |

## Verification

Command:

```powershell
python scripts\verify\simple_purchasable_browser_proof.py
```

Result:

- PASS
- Desktop and mobile viewports passed.
- Product proof rows: 8.
- Cart and checkout preview accepted all four products at both widths.
- Pickup subtotal: 890.00.
- Pickup tax: 66.31.
- Pickup total: 956.31.
- Restoration verified after the run: all four Website Items returned to their
  original internal hold contracts and `lt_ecommerce_paused` returned true.

## What This Proves

- The four products can render direct checkout controls when locally opened.
- Large head Missionary preserves one representative selected option set for
  `Missionary`, `skin color`, and `Hair color` into the cart line. The paired
  backend rehearsal covers all 30 sale variants.
- The three single-SKU products add to cart and remain visible in cart and
  checkout.
- The cart and checkout preview API accepts the four-product cart at desktop
  and mobile widths.
- The browser runner now clicks visible chip labels instead of hidden radio
  inputs, matching customer interaction.

## Still Not Proven

- Payment Request, Payment Entry, Sales Invoice, customer receipt email,
  operator email, and first-order welcome proof using this tranche.
- Final owner/product-scope approval.
- Staging/live checkout exposure.
