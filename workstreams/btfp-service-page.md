# BTFP Service Page

Last updated: 2026-05-08 by Codex after the per-artist calculator correction.

## Outcome

`/balloon-twisting-and-face-painting` is the approved live-service business
lane for Balloon Twisting and Face Painting. It replaces the unapproved Process
route/link in public navigation and must stay a first-class revenue path.

## Current Contract

- The route is contact-led, not checkout-led.
- The page uses the shared `templates/includes/book_form.html` inquiry form
  with `data-form-contract="inquiry-v1"`.
- Controller context scopes visible services to `Balloon Twisting` and
  `Face Painting` and preselects both services.
- Public pricing is transparency only: `$130` first hour per artist, `$115`
  each additional hour per artist, half-hours only after each artist's first
  hour, `$50` deposit per artist, no discounts.
- Calculator math is row-based. Each artist row owns its own service and
  hours. Do not collapse mixed services into one shared hours value or one
  aggregate artist count.
- The page must not expose a public deposit checkout CTA.
- Support and event-type bands use brand blue. Do not restore the red/tan
  Process-era divider or banner treatment.
- The event crawl is decorative/proof motion and must not expose keyboard focus
  or horizontal document scroll.

## Files Owned By This Slice

- `apps/locally_twisted/locally_twisted/www/balloon_twisting_and_face_painting.html`
- `apps/locally_twisted/locally_twisted/www/balloon_twisting_and_face_painting.py`
- `apps/locally_twisted/locally_twisted/templates/includes/book_form.html`
- `scripts/verify/contact_prefill.py`
- `scripts/verify/manual_a11y_probe.js`
- `scripts/verify/layout_helpers.js`

Docs and capability surfaces:

- `CODING-HANDOFF.md`
- `_resources/STYLE-GUIDE.md`
- `locally-twisted-decisions.md`
- `locally-twisted-queue.md`
- `lessons-learned.md`
- `workstreams/website-launch.md`
- `workstreams/nav-btfp-process-correction.md`
- `.codex/capabilities/recipes/btfp-live-service-page-contract.md`
- `.codex/capabilities/recipes/erpnext-intake-form-parity.md`
- `.codex/capabilities/recipes/erpnext-checkout-commerce-rules.md`

## Implementation Notes

- The calculator starts with two rows: one Balloon Twisting artist and one Face
  Painting artist.
- `Add another artist` appends a priced row, alternates the default service,
  and recalculates totals immediately.
- Remove controls are hidden when only one row remains.
- The formula text intentionally lists each service and duration so customers
  can see the math instead of a black-box total.
- `contact_prefill.py` includes the red/green regression for mixed durations:
  one twisting artist at `1.5` hours plus one face painter at `2.5` hours must
  total `$490`, deposit `$100`, balance `$390`. Adding a third one-hour artist
  must total `$620`, deposit `$150`, balance `$470`.
- The minimum-hour guard is per row. If a row is changed to `0.5`, it clamps
  back to `1`, while other rows keep their independent hours.

## Verification Receipt

Fresh checks from 2026-05-08:

- Red run of `python scripts/verify/contact_prefill.py --base-url http://localhost:8081`
  failed against the old one-hours-value calculator.
- `python scripts/dev/clear_website_cache.py --restart` passed after the
  route/template/controller changes.
- `python scripts/verify/contact_prefill.py --base-url http://localhost:8081`
  passed after the row-based calculator fix.
- `npm run test:a11y` passed with 38 route/viewport results and 0 violations.
- `npm run test:a11y-manual` passed.
- `npm run test:layout-fit` passed 247/247.
- `npx playwright test scripts/verify/interactive_layout.spec.js --reporter=dot --workers=1`
  passed 88/88.
- Desktop and mobile BTFP screenshots were visually checked at
  `output/playwright/btfp-calculator-20260508/`.

## Next Safe Changes

- If service pricing changes, update the page copy, calculator data attributes,
  `contact_prefill.py`, policy copy if affected, and this handoff together.
- If the form contract changes, update `/contact` and this embedded BTFP form
  together; do not fork a second customer intake form.
- If the page receives new motion, add it to `npm run test:a11y-manual` or a
  route-specific interactive verifier before closeout.
