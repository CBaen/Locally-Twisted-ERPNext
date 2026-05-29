# Staging Checkout Penny Parity - 2026-05-29

Status: item 2 is agent-approved for human review. The two known one-cent
checkout mismatches now match from checkout preview through Stripe, thank-you,
customer receipt email, and internal paid-order notification on hosted staging.

## Scope

This item only covers checkout total parity for the current staging checkout
paths. It does not approve live checkout, live Stripe keys, DNS, Search
Console, production data, catalog import, or broad product changes.

Known bad staging examples before the fix:

- Mixed cart preview showed `$176.17`; final order/payment/receipt showed
  `$176.18`.
- Unicorn bouquet with foil-number add-on preview showed `$116.01`; final
  order/payment/receipt showed `$116.00`.

## Source Points

- Source branch: `codex/checkout-penny-match`
- Source commit: `82f1d56 Fix checkout preview total rounding`
- App mirror code commit already used for the prior staging proof:
  `39e20ca Fix checkout preview total rounding press-deploy-bench-40102`
- App mirror trigger commit already used for the prior staging proof:
  `35ac2b1 Trigger checkout penny staging deploy press-deploy-bench-40102`

No additional Frappe Cloud or staging provider update is authorized before
item 3. The next staging push should be one combined push after the approved
batch is ready.

## Root Cause

The preview calculator rounded tax per line/add-on. ERPNext's final Sales Order
tax engine rounds after grouping taxable subtotal by tax rate. For some carts,
that made the customer-facing preview disagree with the amount Stripe and
ERPNext charged by one cent.

The fix changes `checkout_fulfillment.build_totals()` to group taxable subtotal
by tax rate and round tax once per rate group. Delivery stays non-taxable.

## Files

- `apps/locally_twisted/locally_twisted/checkout_fulfillment.py`
- `apps/locally_twisted/locally_twisted/verify/checkout_fulfillment_contract.py`
- `scripts/README.md`
- `workstreams/ecommerce-audit/staging-checkout-penny-parity-2026-05-29.md`

## Verification

Local/source checks:

```powershell
python -m py_compile apps\locally_twisted\locally_twisted\checkout_fulfillment.py apps\locally_twisted\locally_twisted\verify\checkout_fulfillment_contract.py
python scripts\verify\checkout_fulfillment_contract.py
python scripts\verify\stripe_amount_parity_contract.py
```

Hosted staging checks:

```powershell
$env:LT_BASE_URL='https://locallytwisted-staging.frappe.cloud'
npm run test:checkout-experience
```

Observed hosted result: `4/4` passed.

Hosted API proof after the staging Pull success:

- Mixed cart: subtotal `$150.00`, delivery `$15.00`, tax `$11.18`, total
  `$176.18`.
- Foil-number add-on cart: subtotal `$94.00`, delivery `$15.00`, tax `$7.00`,
  total `$116.00`.

Paid staging proof:

| Case | Preview | Stripe | Thank-you | Receipt email | Internal email | Order |
|---|---:|---:|---:|---:|---:|---|
| Mixed cart | `$176.18` | `$176.18` | `$176.18` | `$176.18` | `$176.18` | `SAL-ORD-2026-00030` |
| Foil-number add-on | `$116.00` | `$116.00` | `$116.00` | `$116.00` | `$116.00` | `SAL-ORD-2026-00031` |

Gmail proof found customer receipt, welcome email, and internal paid-order
notification for both plus-address test orders.

## Boundaries

- This is not live payment approval.
- This is not permission to push another staging update before item 3.
- This does not claim all product combinations are complete.
- A one-cent mismatch is a payment-trust failure. Future preview/order/Stripe
  parity checks must fail if cents differ.

## Next Item Gate

Do not start item 3 until Guiding Light accepts item 2 or explicitly tells the
agent to move on.
