# Simple Purchasable Rehearsal

## Purpose

Backend-first proof for the first four blocked product families from the
source repair map. These products are not live-approved and were not promoted
in ERPNext. The verifier temporarily applies `simple_product|checkout` inside
one ERPNext transaction, proves source-backed price and line preservation, and
rolls everything back.

## Products

| Product | Slug | Source price | Sale SKUs | Result |
|---|---|---:|---:|---|
| Large head Missionary | `large-head-missionary` | 175.00 | 30 | PASS |
| Mother's day front yard 7' Column | `mothers-day-front-yard-7-column` | 140.00 | 1 | PASS |
| Easter Arch | `easter-arch` | 250.00 | 1 | PASS |
| Pride Arch | `pride-arch` | 325.00 | 1 | PASS |

## Verification

Command:

```powershell
python scripts\verify\simple_purchasable_rehearsal_contract.py --report workstreams/ecommerce-audit/simple-purchasable-rehearsal-2026-05-17.json
```

Result:

- PASS
- Products: 4
- Enabled sale SKUs: 33
- Sales Order lines: 33
- Sales Invoice: `ACC-SINV-2026-00004` inside rollback
- Survivor counts: Customer 0, Sales Order 0, Sales Invoice 0

## What This Proves

- Odoo source prices match the local ERPNext checkout prices for this tranche.
- `large-head-missionary` preserves all 30 variant combinations across
  `Missionary`, `skin color`, and `Hair color` as selected options.
- The three single-SKU products resolve as purchasable single lines.
- No checkout add-ons are exposed for this tranche.
- Sales Order and Sales Invoice item rows preserve the LT configuration version,
  summary, JSON, template item, and page type fields.
- Rollback leaves no generated Customer, Sales Order, or Sales Invoice records.

## Still Not Proven

This is not live checkout approval. The remaining gates for this tranche are:

- Open-mode desktop and mobile product-page UX proof.
- Cart and checkout browser proof after an intentional local lane flip.
- Payment Request, Payment Entry, customer receipt email, operator email, and
  first-order welcome proof using these tranche products.
- Final owner/product-scope approval before any customer exposure.

