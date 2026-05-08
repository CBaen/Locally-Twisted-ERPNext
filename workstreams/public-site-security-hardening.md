# Public Site Security Hardening

Last updated: 2026-05-08 by Codex after parallel Codex Security review and first small fixes.

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

Open launch blockers:

- `/thank-you?order=<Sales Order>` still renders order id, line items, quantities, totals, currency, and status to an unauthenticated visitor who knows or guesses a Sales Order name. Replace this with a receipt token tied to the paid Stripe Session or Payment Request, then show only generic payment-check copy when the token is absent or invalid.
- Tracked docs still contain local Administrator/dev login credentials in `AGENTS.md` and `CLAUDE.md`. Do not repeat the passwords in reports. Rotate those credentials before any broader sharing/cutover, then replace tracked docs with a local-vault/operator note.
- Existing Lead attachments include at least one public `File` row under `/files/...`. New uploads are private after this patch, but existing customer/test uploads still need a migration/review to flip `is_private=1` or delete intentionally.
- `submit_guest_order` can promote a Contact/Lead into Customer/Converted/Approved by email before Stripe payment completes. Review whether that CRM mutation should move after payment success or be marked pending until payment is verified.
- `/event-playground?port=<port>` is an unauthenticated internal preview bridge to visitor-local `127.0.0.1:<port>`. Gate it to development/System Manager or remove it from the public production route set before launch.

## Evidence From Review

- Live `/shop?q=<script>...` reproduced a browser-executed marker before the escape patch.
- Live `/thank-you?order=SAL-ORD-2026-00019` returned HTTP 200 and exposed the order id plus item/total details.
- Live DB contained a Lead-attached public file at `/files/doc logo.png`, and the URL returned HTTP 200.
- Static trace confirmed checkout Lead conversion happens inside the guest checkout submit path before the Stripe redirect/payment completion boundary.

## Files Touched By This Closeout

- `apps/locally_twisted/locally_twisted/www/shop.html`
- `apps/locally_twisted/locally_twisted/templates/generators/item/item_image.html`
- `apps/locally_twisted/locally_twisted/www/book.py`
- `workstreams/public-site-security-hardening.md`
- `.codex/capabilities/recipes/frappe-public-storefront-security.md`

## Required Verification

After each security hardening change:

```powershell
python scripts/dev/clear_website_cache.py
python -m py_compile apps\locally_twisted\locally_twisted\www\book.py apps\locally_twisted\locally_twisted\www\shop.py apps\locally_twisted\locally_twisted\www\thank_you.py apps\locally_twisted\locally_twisted\www\payment_success.py
npm run test:shop-smoke
npm run test:interactive-layout
```

Also run targeted checks for the exact security symptom:

- `/shop?q=<script>window.__lt_xss_marker="owned"</script>` must render escaped text and leave `window.__lt_xss_marker` unset.
- A known Sales Order name must not expose order details without a valid receipt token.
- A new inquiry upload must create `tabFile.is_private = 1`.
- A payment-not-complete checkout path must not mark an existing Lead as converted/approved.
