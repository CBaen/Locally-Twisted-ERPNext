# Public Site Security Hardening

Last updated: 2026-05-11 by Codex after customer portal file-registration review hardening.

## Outcome

Close launch-blocking public storefront security issues without weakening the Frappe/Webshop ownership model.

This handoff owns public customer/security boundaries found during the 2026-05-08 `$codex-security` pass. It coordinates with `workstreams/website-launch.md`, `workstreams/shop.md`, `workstreams/commerce-rules-checkout.md`, and `workstreams/fail-loud-record-level-hardening.md`.

## Current Stage

Active P0 launch hardening lane.

Fixed in this closeout:

- `/shop?q=` no longer renders raw search text in the result summary.
- Product-gallery thumbnail `src` and `alt` values are escaped in the Jinja template.
- Product-gallery zoom preview now creates the `<img>` through jQuery attributes instead of an HTML template string.
- New `/contact` inspiration-photo uploads are stored as private Frappe `File` records.
- Guest checkout no longer marks an existing inquiry Lead as `Converted` / `Approved` before payment succeeds. The paid-order cascade now performs the final Lead conversion after the payment boundary.
- `/event-playground?port=<port>` now redirects guests to login and requires `Administrator` or `System Manager` before exposing the internal local preview iframe.

Customer portal follow-up on 2026-05-11:

- `register_customer_portal_file` now requires the referenced `File` to be owned
  by the logged-in customer and already attached to the same source record before
  creating `LT Customer Portal File`.
- `customer_portal_v1_contract.py` proves a valid customer-owned file registers
  and staff-owned or wrong-source files fail without creating portal metadata.

GL triage on 2026-05-08:

- Current LT records and files are fake/test data until GL says otherwise. Existing fake public Lead files are cleanup/review work, not current real-customer exposure.
- `/thank-you?order=<Sales Order>` order-summary exposure is downgraded from immediate launch blocker for this business/fake-data state. Token-bound receipt proof is still the stronger production pattern before real customer cutover.
- Tracked local credentials remain user-owned: GL said they will fix/rotate them. Do not repeat the passwords in reports.

Remaining follow-ups:

- Before real customer cutover, decide whether to add token-bound receipt proof to `/thank-you` or accept the current order-name flow for this low-sensitivity ready-to-order context.
- Existing fake public Lead `File` rows can be deleted or flipped private during cleanup; new uploads already default private.
- Rotate/remove tracked local credentials before broader sharing/cutover, then replace tracked docs with a local-vault/operator note.

## Evidence From Review

- Live `/shop?q=<script>...` reproduced a browser-executed marker before the escape patch.
- Live `/thank-you?order=SAL-ORD-2026-00019` returned HTTP 200 and exposed the order id plus item/total details.
- Live DB contained a Lead-attached public file at `/files/doc logo.png`, and the URL returned HTTP 200.
- Static trace confirmed checkout Lead conversion happens inside the guest checkout submit path before the Stripe redirect/payment completion boundary.
- `python scripts/verify/checkout_lead_conversion_contract.py` now proves checkout keeps the Lead in `Open` / `New Inquiry`, then the paid-order cascade converts it to `Converted` / `Approved`.
- `python scripts/verify/event_playground_gate.py` now proves guest access redirects to `/login` and does not expose the local preview iframe URL.

## Files Touched By This Closeout

- `apps/locally_twisted/locally_twisted/www/shop.html`
- `apps/locally_twisted/locally_twisted/templates/generators/item/item_image.html`
- `apps/locally_twisted/locally_twisted/www/book.py`
- `apps/locally_twisted/locally_twisted/www/checkout.py`
- `apps/locally_twisted/locally_twisted/www/payment_success.py`
- `apps/locally_twisted/locally_twisted/www/event_playground.py`
- `apps/locally_twisted/locally_twisted/verify/checkout_lead_conversion_contract.py`
- `apps/locally_twisted/locally_twisted/verify/business_automation_index.py`
- `scripts/verify/checkout_lead_conversion_contract.py`
- `scripts/verify/event_playground_gate.py`
- `scripts/verify/event_playground.spec.js`
- `workstreams/public-site-security-hardening.md`
- `capabilities/recipes/frappe-public-storefront-security.md`

## Required Verification

After each security hardening change:

```powershell
python scripts/dev/clear_website_cache.py
python -m py_compile apps\locally_twisted\locally_twisted\www\book.py apps\locally_twisted\locally_twisted\www\shop.py apps\locally_twisted\locally_twisted\www\thank_you.py apps\locally_twisted\locally_twisted\www\checkout.py apps\locally_twisted\locally_twisted\www\payment_success.py apps\locally_twisted\locally_twisted\www\event_playground.py
npm run test:shop-smoke
npm run test:interactive-layout
python scripts/verify/checkout_lead_conversion_contract.py
python scripts/verify/payment_cascade_contract.py
python scripts/verify/event_playground_gate.py
npm run test:event-playground
python scripts/verify/business_automation_index.py --report output\business-automation-index.json
python scripts/verify/synthetic_business_pipeline.py --report output\synthetic-business-pipeline.json
```

Also run targeted checks for the exact security symptom:

- `/shop?q=<script>window.__lt_xss_marker="owned"</script>` must render escaped text and leave `window.__lt_xss_marker` unset.
- If token-bound receipts are implemented, a known Sales Order name must not expose order details without a valid receipt token.
- A new inquiry upload must create `tabFile.is_private = 1`.
- A payment-not-complete checkout path must not mark an existing Lead as converted/approved.
- A guest `/event-playground?port=<port>` request must redirect or deny access without exposing `127.0.0.1:<port>`.
- A customer portal file registration attempt with an arbitrary, staff-owned, or
  wrong-source `File.name` must fail before `LT Customer Portal File` is
  created.
