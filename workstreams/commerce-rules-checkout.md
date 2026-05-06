# Commerce Rules And Checkout

Last updated: 2026-05-06 by Codex.

## Outcome

Make checkout reflect Locally Twisted's mixed business model:

- ready-to-order goods can be purchased through cart/checkout
- custom decor and out-of-area delivery move to quote/Lead flow
- local delivery and Park City delivery can be charged in checkout
- service inquiries carry deposit/payment guidance on Leads without creating money records
- Utah tax rate is selected by fulfillment ZIP/city, but tax applies only to taxable goods

## Current Verified Local State

Verified against the local ERPNext/Frappe stack at `http://localhost:8081`:

- Standard local delivery is `$15`; Park City delivery is `$50`.
- Out-of-area ZIPs create a quote Lead instead of a paid checkout, even if the city text names a standard-delivery city.
- Checkout rejects past pickup/delivery dates server-side and sets the browser date minimum to today.
- Ready-to-order retail goods remain taxable using the ZIP/city tax rate.
- Delivery fee lines are non-taxable.
- `Services` item-group lines are non-taxable, which covers face painting, balloon twisting, and service/deposit items when they exist as ERPNext Items.
- The local site has a `LT Non-Taxable Sales` 0% Item Tax Template, currently named by Frappe as `LT Non-Taxable Sales - LT`.
- Contact inquiries store payment guidance on Lead fields: payment timing, deposit due, balance timing, and payment notes.
- Artist services use `$50 per artist` deposit guidance; mixed decor + artist inquiries keep the artist deposit and include full-before-prep guidance for quoted decor/event work.

Important split: location determines which Utah rate to use; line type determines whether that rate applies.

## Implementation Surface

Primary source files:

- `apps/locally_twisted/locally_twisted/commerce_rules.py`
- `apps/locally_twisted/locally_twisted/www/checkout.py`
- `apps/locally_twisted/locally_twisted/www/checkout.html`
- `apps/locally_twisted/locally_twisted/www/book.py`
- `apps/locally_twisted/locally_twisted/seed/sync_commerce_rules.py`
- `apps/locally_twisted/locally_twisted/seed/sync_contact_intake_backend.py`
- `apps/locally_twisted/locally_twisted/patches/sync_commerce_rules.py`
- `apps/locally_twisted/locally_twisted/patches/sync_contact_intake_backend.py`
- `apps/locally_twisted/locally_twisted/patches.txt`

Primary verifier files:

- `apps/locally_twisted/locally_twisted/verify/commerce_rules_contract.py`
- `apps/locally_twisted/locally_twisted/verify/checkout_fulfillment_contract.py`
- `apps/locally_twisted/locally_twisted/verify/checkout_lead_conversion_contract.py`
- `scripts/verify/cart_checkout_contract.py`
- `scripts/verify/checkout_experience.spec.js`
- `scripts/verify/lead_backend_intake_parity.py`

## Verification Receipts

Latest focused verification from this slice:

```powershell
python -m py_compile apps/locally_twisted/locally_twisted/commerce_rules.py apps/locally_twisted/locally_twisted/www/checkout.py apps/locally_twisted/locally_twisted/www/book.py apps/locally_twisted/locally_twisted/seed/sync_commerce_rules.py apps/locally_twisted/locally_twisted/seed/sync_contact_intake_backend.py apps/locally_twisted/locally_twisted/patches/sync_commerce_rules.py apps/locally_twisted/locally_twisted/patches/sync_contact_intake_backend.py apps/locally_twisted/locally_twisted/verify/commerce_rules_contract.py apps/locally_twisted/locally_twisted/verify/checkout_fulfillment_contract.py apps/locally_twisted/locally_twisted/verify/checkout_lead_conversion_contract.py
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.seed.sync_contact_intake_backend.execute
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.seed.sync_commerce_rules.execute
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.patches.sync_contact_intake_backend.execute
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.patches.sync_commerce_rules.execute
python scripts/verify/lead_backend_intake_parity.py
python scripts/verify/commerce_rules_contract.py
python scripts/verify/checkout_fulfillment_contract.py
python scripts/verify/checkout_lead_conversion_contract.py
python scripts/verify/cart_checkout_contract.py
python scripts/verify/contact_prefill.py --base-url http://localhost:8081
python scripts/verify/contact_service_logic.py --base-url http://localhost:8081
python scripts/verify/smoke_forms.py --base-url http://localhost:8081
python scripts/verify/smoke_shop.py
python scripts/verify/nav_ia.py
npm run test:checkout-experience
npm run test:layout-fit
npm run test:interactive-layout
python scripts/verify/payment_backend_config_contract.py
python scripts/verify/payment_cascade_contract.py
python scripts/verify/payment_launch_readiness.py
python scripts/verify/payment_webhook_contract.py
python scripts/dev/clear_website_cache.py
```

Observed tax regression receipt:

- Before the fix, West Jordan delivery checkout taxed goods plus delivery: expected `$4.84`, found `$5.96`.
- After the fix, `preview_checkout_totals` for `mothers-day-bouquet` delivered to `84088` returned `$65.00` goods, `$15.00` delivery, `$4.84` tax, `$84.84` total.

## Remaining Work

- Get GL/legal/accountant approval before treating public policy copy as final tax/legal language.
- Update customer-facing Terms/Delivery/Refund copy only after policy approval; do not invent legal terms.
- Run `python scripts/verify/payment_launch_readiness.py --mode live` before any real cutover claim.
- If service/deposit Items are added later, keep them in Item Group `Services` or explicitly add their item codes to the non-taxable rule.
- If a future service becomes taxable, do not change this globally; add a narrower taxable-service classification and contract test first.

## Trust Boundary

Do not say "checkout taxes are live-ready" from local/test-mode evidence alone. Current verified wording: local checkout calculates Utah rate by ZIP/city and applies it only to taxable goods; service, deposit, and delivery lines are non-taxable in the local ERPNext checkout contract.
