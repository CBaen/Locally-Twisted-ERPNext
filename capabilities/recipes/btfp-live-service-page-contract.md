---
id: btfp-live-service-page-contract
name: BTFP Live Service Page Contract
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted Balloon Twisting and Face Painting public route, shared inquiry form, and customer pricing calculator
currently_true: yes
verification_level: 2
last_verified: 2026-05-10
evidence_quality: direct
successful_uses: 2
failed_uses: 1
regressions: 0
depends_on:
  - erpnext-intake-form-parity
  - erpnext-checkout-commerce-rules
  - frappe-public-container-contract
  - responsive-container-audit
used_by:
  - website-launch
tags:
  - Locally Twisted
  - BTFP
  - service page
  - calculator
  - inquiry form
  - accessibility
---

# BTFP Live Service Page Contract

Use this before changing `/balloon-twisting-and-face-painting`, the embedded
public inquiry form on that page, the artist-time calculator, or any public
copy that describes Balloon Twisting and Face Painting pricing.

## Contract

- This route is an approved, vital Locally Twisted business lane.
- The public nav/search label is `Twisting & Face Painting`.
- The lane must stay discoverable in desktop nav, mobile drawer, and search quick links unless GL explicitly approves removal/hiding/renaming/replacement in `workstreams/nav-service-removal-approvals.md`.
- `/contact`, `Free Event Quote`, and `Contact Us` are conversion paths/labels; they do not replace this service lane.
- `/process` is not an approved route or replacement for this service lane.
- The route uses the shared `inquiry-v1` form contract instead of a forked BTFP
  intake form.
- Visible service choices on the page are only `Balloon Twisting` and
  `Face Painting`; neither is preselected on initial page load.
- The form accepts repeat inquiries from the same email address; Contact linking/dedupe handles person identity while separate Leads represent separate event inquiries.
- The form supports up to five inspiration-photo uploads per inquiry.
- The two service-card photo areas are explicit 10-image carousels with previous/next controls and visible status.
- The customer calculator is transparency only. It does not create checkout,
  deposit, Quote, Sales Order, Payment Request, or Stripe state.
- Published math is `$130` first hour per artist, `$115` each additional hour
  per artist, half-hour increments only after each artist's first hour, `$50`
  deposit per artist, no discounts.
- Calculator inputs are row-based: one row per artist, with independent service
  and hours. Never flatten mixed artists into one shared hours value.
- The old short-notice contact band is not part of the page contract. Do not
  restore the "Need help on short notice?" phone/email banner.
- The event suggestion crawl sits directly after the compact hero, before the
  service cards, in the former support-band slot.
- The event crawl stays brand blue, uses the expanded BTFP event list, moves
  left-to-right, and must keep running infinitely without hover/focus pause or
  horizontal document scroll.

## Source Files

- `apps/locally_twisted/locally_twisted/www/balloon_twisting_and_face_painting.html`
- `apps/locally_twisted/locally_twisted/www/balloon_twisting_and_face_painting.py`
- `apps/locally_twisted/locally_twisted/templates/includes/book_form.html`
- `scripts/verify/contact_prefill.py`
- `scripts/verify/book_form_repeat_email_photos.py`
- `scripts/verify/manual_a11y_probe.js`
- `scripts/verify/layout_helpers.js`

## Verification

Focused route contract:

```bash
python scripts/dev/clear_website_cache.py --restart
python scripts/verify/contact_prefill.py --base-url http://localhost:8081
python scripts/verify/book_form_repeat_email_photos.py --base-url http://localhost:8081
```

Public layout and accessibility:

```bash
npm run test:a11y
npm run test:a11y-manual
npm run test:layout-fit
npx playwright test scripts/verify/interactive_layout.spec.js --reporter=dot --workers=1
```

Use `npm run test:public-verify` for broad public-site closeout when the change
also touches chrome, containers, Webshop surfaces, or shared CSS.

## Red Flags

- A service page rebuild mentions Process, links to `/process`, or removes the
  BTFP nav/search lane without the exact approval marker.
- Calculator UI has one global `hours` input plus an artist count.
- The formula cannot show one twisting artist at one duration and one face
  painter at another duration.
- A public deposit checkout CTA returns on the BTFP route.
- The page forks a second customer intake form instead of using the shared
  inquiry partial.
- The service checkboxes are preselected again on first load.
- Repeat-email public submissions fail with ERPNext duplicate Lead email copy.
- The service photos only change through hidden/subtle animation with no controls or status.
- The embedded inquiry form loses the shared status panel, backend-proven
  success modal, or inline cookie notice placement.
- The old short-notice phone/email banner returns, the event crawl moves below
  the service cards again, or the crawl pauses on hover/focus.
- The brand-blue event crawl is replaced with red, tan, blush, or a Process-era
  treatment.
- Decorative crawls/carousels are keyboard focusable while offscreen or hidden.

## Receipt

On 2026-05-08, GL flagged that the first calculator did not handle multiple
artists with different services and rental hours. The first verifier update
failed because the page only exposed one shared hours input and one aggregate
artist count. The repair changed the calculator to per-artist rows, then
`contact_prefill.py`, `test:a11y`, `test:a11y-manual`, `test:layout-fit`, and
`interactive_layout.spec.js` passed against the live local route.

On 2026-05-10, the shared embedded form was revalidated through the new
`shared-inquiry-form-experience` contract. `npm run test:form-experience`
proved the BTFP page uses inline cookie placement and does not rely on a forked
or fake-success form path.

On 2026-05-10, after GL caught BTFP missing from public navigation again,
OpenClaw/Moji restored `Twisting & Face Painting` to desktop nav, mobile drawer,
and search quick links, then added a fail-loud approval-marker guard in
`scripts/verify/nav_ia.py`. This recipe now treats BTFP discoverability as part
of the service-page contract, not a cosmetic nav preference.


On 2026-05-10, GL verified the exact localhost BTFP route and found the beginning form state still selected both artist services, repeat emails were blocked by ERPNext Lead duplicate validation, five-photo upload was not proven in the real flow, and the photo areas still read as static. The repair blanked the initial service selection, enabled duplicate Lead emails through durable CRM Settings patching, added `book_form_repeat_email_photos.py`, and changed the service photos to explicit controlled carousels. The repeat-email/five-photo verifier, focused Playwright BTFP carousel/form tests, and white-label surface verifier passed against `http://localhost:8081`.

Later on 2026-05-10, GL requested removal of the old short-notice phone/email
band and replacement with the event suggestion crawl in that slot. Codex moved
the brand-blue crawl directly below the hero, expanded the event list, guarded
infinite left-to-right motion including hover/focus non-pause, and updated the
container contract. `contact_prefill.py`, focused BTFP interactive/layout/
container checks, `smoke_shop.py`, and full `npm run test:public-verify` passed
against `http://localhost:8081`.
