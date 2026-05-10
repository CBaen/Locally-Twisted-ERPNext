# FAQ Service-Lane Rewrite

Last updated: 2026-05-10 by Moji/OpenClaw.

## Purpose

Keep `/faq` from mixing policies across service types. The FAQ must answer by customer lane when booking, pricing, deposit, delivery, cancellation, or corporate terms differ.

## Trigger

GL flagged that the old generic `Booking and pricing` section answered pricing with the face-painting/balloon-twisting hourly artist formula. That is wrong for event balloon decor/installations and can mislead customers.

## Current Structure

`apps/locally_twisted/locally_twisted/www/faq.html` now groups visible FAQ content by:

1. Face painting and balloon twisting
2. Event balloon decor and installations
3. Ready-to-order balloons, pickup, and delivery
4. Corporate, school, civic, and venue events
5. Cancellations, weather, and rescheduling

`apps/locally_twisted/locally_twisted/www/faq.py` now publishes matching FAQPage/AEO questions through `FAQ_AEO_QUESTIONS` and `faq_schema(...)`.

## Policy Anchors

- Artist services: `$130` first hour + `$115` additional hours per artist; `$50` deposit per artist; balance due 72 hours before event.
- Personal decor/installations: scoped quote; paid in full before prep starts.
- Ready-to-order: pickup free when confirmed; standard delivery `$15`; Park City `$50`; out-of-area quoted before payment.
- Corporate: no deposit by default; Net 30; possible 10% simple late fee.
- Themes/characters: no tiny preset menu for BTFP; ask for the character/theme.

## Verification

Focused checks used after the rewrite:

```powershell
python scripts/dev/clear_website_cache.py
npm run test:container-contract -- --grep faq
npm run test:layout-fit -- --grep faq
npm run test:interactive-layout -- --grep "faq hero uses"
```

Live content check confirmed five service sections, 17 FAQ items, and no old generic `Booking and pricing` section.

## Guardrail

When FAQ policy differs by service type, do not collapse the answer into a shared generic bucket. If a schema/AEO verifier changes, keep visible FAQ questions and JSON-LD questions in parity.
