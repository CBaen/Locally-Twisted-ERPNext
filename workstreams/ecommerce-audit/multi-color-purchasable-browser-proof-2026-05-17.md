# Multi-Color Purchasable Browser Proof - 2026-05-17

## Purpose

Local open-mode browser proof for the six multi-color repair-lane products.
This does not promote the products, keep ecommerce open, send email, create
payment records, or authorize live/customer exposure. The wrapper temporarily
opened local ecommerce and applied `simple_product|checkout` to the six Website
Items, ran the shared product/cart/checkout browser proof at desktop and mobile
widths, then restored the original Website Item contracts and
`lt_ecommerce_paused=1`.

## Products

| Product | Route | Browser item code | Color drawer axes | Price | Result |
|---|---|---|---|---:|---|
| 7' Epic Column | `/shop-items/columns/7-epic-column` | `7-epic-column-REF` | `latex colors` | $100 | PASS |
| Baby Shower Combination Photo opt | `/shop-items/table-decor/baby-shower-combination-photo-opt` | `baby-shower-combination-photo-opt-REF` | `latex colors` | $650 | PASS |
| Baby Table decor | `/shop-items/table-decor/baby-table-decor` | `baby-table-decor-GIR` | `Baby color` | $30 | PASS |
| classic organic for easel | `/shop-items/stands-easels/classic-organic-for-easel` | `classic-organic-for-easel-REF` | `latex colors` | $100 | PASS |
| Number Balloon Columns | `/shop-items/columns/number-balloon-columns` | `number-balloon-columns-GOL-REF` | `Number colors`, `latex colors` | $55 | PASS |
| Sleepy Baby Column | `/shop-items/columns/sleepy-baby-column` | `sleepy-baby-column-REF` | `latex colors` | $220 | PASS |

## Verification

Command:

```powershell
python scripts\verify\multi_color_purchasable_browser_proof.py
```

Result:

- PASS.
- Desktop and mobile viewports passed.
- Product proof rows: 12.
- Color drawer proofs: 14.
- Cart and checkout preview accepted all six products at both widths.
- Pickup subtotal: 1155.00.
- Pickup tax: 86.05.
- Pickup total: 1241.05.
- Restoration verified after the run: all six Website Items returned to their
  original internal hold contracts and `lt_ecommerce_paused` returned true.

## What This Proves

- The six products can render direct checkout controls when locally opened.
- Visible color card selections update the hidden variant bridge and cart line.
- Color axes stay in `color_recipes` and do not leak into `selected_options`.
- Number Balloon Columns preserves both color axes in the cart payload.
- The cart and checkout preview API accepts the six-product cart at desktop and
  mobile widths.

## Still Not Proven

- Payment Request, Payment Entry, receipt, operator email, and welcome email
  cascade for these six products.
- Variant or combination image updates for these six products beyond existing
  media guard behavior.
- Final owner/product-scope approval.
- Staging/live checkout exposure.

## Backlinks

- `workstreams/ecommerce-audit/multi-color-purchasable-rehearsal-2026-05-17.md`
- `workstreams/ecommerce-audit/product-family-certification-truth-table-2026-05-17.md`
- `workstreams/ecommerce-audit/product-source-repair-map-2026-05-17.md`
- `workstreams/ecommerce-audit/README.md`
- `scripts/verify/multi_color_purchasable_browser_proof.py`
- `scripts/verify/post_import_checkout_proof.js`
