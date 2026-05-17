# Simple Purchasable Payment Cascade

## Purpose

Rollback-safe payment and customer-message proof for the first simple
repair-lane products. This does not promote Website Items, keep ecommerce open,
create live Stripe sessions, send real email, or authorize live/customer
exposure. The verifier temporarily applies `simple_product|checkout` inside one
ERPNext transaction, resolves all simple-tranche sale lines through checkout
logic, runs the paid-order reconciliation helper, verifies downstream records
and queued messages, and rolls everything back.

## Products

| Product | Sale SKUs | Price Basis | Result |
|---|---:|---|---|
| Large head Missionary | 30 | Odoo base price plus live ERPNext snapshot price parity | PASS |
| Mother's day front yard 7' Column | 1 | Odoo base price | PASS |
| Easter Arch | 1 | Odoo base price | PASS |
| Pride Arch | 1 | Odoo base price | PASS |

## Verification

Command:

```powershell
python scripts\verify\simple_purchasable_payment_cascade_contract.py --report workstreams/ecommerce-audit/simple-purchasable-payment-cascade-2026-05-17.json
```

Result:

- PASS
- Products: 4
- Enabled sale SKUs: 33
- Sales Order lines: 33
- Grand total: 6409.39
- Payment Request: `ACC-PRQ-2026-00021` inside rollback
- Payment Entry: `ACC-PAY-2026-00003` inside rollback
- Sales Invoice: `ACC-SINV-2026-00004` inside rollback
- Customer receipt Email Queue: `ajt7qtniga` inside rollback
- Operator Email Queue: `ajub1o3pmq` inside rollback
- Welcome Email Queue: `ajv7jomgis` inside rollback
- Survivor counts: Customer 0, Contact 0, Address 0, Sales Order 0,
  Payment Request 0, Payment Entry 0, Sales Invoice 0, Email Queue 0

## What This Proves

- All 33 simple-tranche sale lines can enter one checkout-sourced Sales Order.
- Sales Order and Sales Invoice rows preserve LT configuration fields.
- Payment Request becomes paid and creates a submitted Payment Entry.
- Paid-order reconciliation creates a submitted Sales Invoice.
- Customer receipt, operator notification, and first-order welcome email queues
  are created with required internal copy recipients.
- Receipt and operator messages include product evidence for all four products.
- Checkout notes are preserved into the operator path.
- A second reconciliation remains idempotent for the multi-line order.
- Rollback leaves no generated ERPNext records behind.

## Still Not Proven

- Final owner/product-scope approval.
- Staging/live checkout exposure.
