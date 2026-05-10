# ERPNext Checkout Commerce Rules

Status: project recipe
Scope: Locally Twisted ERPNext/Frappe checkout, cart, service intake, and payment-rule verification.
Last verified: 2026-05-08

## Use When

- Checkout pricing, delivery fees, pickup/delivery rules, service deposits, or tax behavior changes.
- A public product/service page needs to describe what can be bought now versus quoted.
- A future service/deposit Item is added to ERPNext and must not accidentally become taxable.
- A verifier catches Sales Order tax totals that differ from checkout preview totals.

## Core Contract

Keep three decisions separate:

1. Fulfillment location decides the Utah tax rate.
2. Line type decides whether that rate applies.
3. Quote-required work never becomes a paid checkout workaround.

For the current LT contract:

- Ready-to-order goods are taxable.
- Services are non-taxable.
- Balloon twisting and face painting are services.
- Deposits for those services are non-taxable.
- Delivery charges are non-taxable.
- The BTFP public calculator is pricing transparency only. It must not create a
  public deposit checkout CTA, Sales Order, Payment Request, Stripe session, or
  shortcut around the shared inquiry path.
- Product group is not a quote gate for fixed-price products. If a product has a valid fixed price and is otherwise checkoutable, it stays cartable.
- Out-of-area delivery requires a quote, even if the typed city name resembles a standard service city.
- Out-of-area delivery redirects the customer to `/contact` with the checkout/customer/cart context prefilled as an interested-item quote request.
- Checkout must not create duplicate Lead records for the out-of-area delivery fallback before the customer reaches `/contact`.

## Source Files

- `apps/locally_twisted/locally_twisted/commerce_rules.py`
- `apps/locally_twisted/locally_twisted/www/checkout.py`
- `apps/locally_twisted/locally_twisted/www/book.py`
- `apps/locally_twisted/locally_twisted/api/cart.py`
- `apps/locally_twisted/locally_twisted/seed/sync_commerce_rules.py`
- `apps/locally_twisted/locally_twisted/seed/sync_contact_intake_backend.py`
- `apps/locally_twisted/locally_twisted/patches.txt`

## ERPNext Notes

- Do not rely on a raw `item_tax_rate` string alone for non-taxable lines. ERPNext can recalculate Sales Order tax from the linked Item Tax Template.
- The local non-taxable override is the 0 percent Item Tax Template titled `LT Non-Taxable Sales`. Frappe may store the document name with a suffix such as `LT Non-Taxable Sales - LT`; look it up by title/company.
- The delivery fee checkout Item and any service/deposit Items should either sit in Item Group `Services` or be explicitly covered by the non-taxable item-code rule.
- Keep delivery charge Items and prices idempotently synced through `sync_commerce_rules`.

## Verification

Run the focused contract first:

```powershell
python scripts/verify/commerce_rules_contract.py
python scripts/verify/checkout_fulfillment_contract.py
python scripts/verify/cart_checkout_contract.py
python scripts/verify/contact_prefill.py --base-url http://localhost:8081
python scripts/verify/lead_backend_intake_parity.py
npm run test:checkout-experience
```

For broad launch confidence, add:

```powershell
python scripts/verify/checkout_lead_conversion_contract.py
python scripts/verify/payment_launch_readiness.py
python scripts/verify/payment_cascade_contract.py
python scripts/verify/payment_webhook_contract.py
```

If setup records changed, sync and test the patch path too:

```powershell
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.seed.sync_commerce_rules.execute
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.patches.sync_commerce_rules.execute
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.seed.sync_contact_intake_backend.execute
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.patches.sync_contact_intake_backend.execute
```

## Red Flags

- A delivery line changes Sales Order tax.
- A face-painting, balloon-twisting, or deposit Item lands outside `Services`.
- A service pricing calculator starts acting like checkout or deposit purchase.
- A priced product becomes uncartable only because it belongs to an arches, columns, garlands, drops, or similar product group.
- A ZIP that is outside the standard/Park City zones still gets a delivery fee instead of quote-required behavior.
- An out-of-area checkout creates a Lead, Sales Order, Payment Request, or Stripe session before redirecting to `/contact`.
- `/contact` loses the customer's checkout contact details, delivery location, notes, or interested item after the delivery-quote redirect.
- Public policy copy says tax/legal/payment terms are final before GL/legal/accountant approval.
- A checkout test checks preview totals only and never checks the submitted Sales Order tax rows.
