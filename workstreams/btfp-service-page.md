# BTFP Service Page

Last updated: 2026-05-10 by OpenClaw/Moji after GL exact-page corrections for blank form state, repeat-email submissions, five-photo uploads, and explicit service-photo carousels.

## Outcome

`/balloon-twisting-and-face-painting` is the approved live-service business lane for Balloon Twisting and Face Painting. It is contact-led, quote/inquiry-led, and V1-launch-safe while public ecommerce is paused.

## Current Contract

- The route is contact-led, not checkout-led.
- The page uses the shared `templates/includes/book_form.html` inquiry form with `data-form-contract="inquiry-v1"`.
- Controller context scopes visible services to `Balloon Twisting` and `Face Painting`.
- Beginning form state is blank: neither service checkbox is preselected.
- Repeat inquiries from the same email are allowed and should create separate Leads. Contact dedupe/linking can associate the same person; Lead uniqueness must not block a new event inquiry.
- The form advertises and supports up to five inspiration photos per inquiry.
- New inquiry uploads should attach as private Lead files; rejected/failed real uploads need customer-safe copy plus record-level evidence.
- Public pricing is transparency only: `$130` first hour per artist, `$115` each additional hour per artist, half-hours only after each artist's first hour, `$50` deposit per artist, no discounts.
- Calculator math is row-based. Each artist row owns its own service and hours. Do not collapse mixed services into one shared hours value or one aggregate artist count.
- The two service-card image areas are explicit carousels: 10 images each, previous/next controls, visible `n / 10` status, auto-advance when motion is allowed, and manual controls in reduced-motion mode.
- The page must not expose a public deposit checkout CTA.
- Support and event-type bands use brand blue. Do not restore the red/tan Process-era divider or banner treatment.
- The event crawl is decorative/proof motion and must not expose keyboard focus or horizontal document scroll.

## Files Owned By This Slice

- `apps/locally_twisted/locally_twisted/www/balloon_twisting_and_face_painting.html`
- `apps/locally_twisted/locally_twisted/www/balloon_twisting_and_face_painting.py`
- `apps/locally_twisted/locally_twisted/templates/includes/book_form.html`
- `apps/locally_twisted/locally_twisted/www/book.py`
- `apps/locally_twisted/locally_twisted/patches/configure_crm_duplicate_lead_emails.py`
- `scripts/verify/contact_prefill.py`
- `scripts/verify/book_form_repeat_email_photos.py`
- `scripts/verify/interactive_layout.spec.js`

Docs and capability surfaces:

- `CODING-HANDOFF.md`
- `locally-twisted-decisions.md`
- `locally-twisted-queue.md`
- `lessons-learned.md`
- `workstreams/website-launch.md`
- `.codex/capabilities/recipes/btfp-live-service-page-contract.md`
- `.codex/capabilities/recipes/shared-inquiry-form-experience.md`
- `.codex/capabilities/recipes/erpnext-intake-form-parity.md`

## Implementation Notes

- `get_context()` sets `context.preselected_services = []`; do not restore the old combined-route default of both artist services checked.
- `CRM Settings.allow_lead_duplication_based_on_emails` is required for the public form. The local setting was enabled and the project patch keeps it durable.
- The calculator still starts with two estimate rows: one Balloon Twisting artist and one Face Painting artist. This is pricing-estimator state, not form service-selection state.
- `Add another artist` appends a priced row, alternates the default service, and recalculates totals immediately.
- Remove controls are hidden when only one row remains.
- The formula text intentionally lists each service and duration so customers can see the math instead of a black-box total.
- Carousel controls stop auto-advance after manual/focus/hover interaction so the page does not fight the visitor.

## Verification Receipt

Fresh checks from 2026-05-10:

- Exact route HTML at `http://localhost:8081/balloon-twisting-and-face-painting` showed both `x_services` checkboxes unchecked.
- `python scripts/verify/book_form_repeat_email_photos.py --base-url http://localhost:8081` passed: two separate public submissions with the same email, five PNG uploads each, separate fake Leads, 5/5 photos attached on each.
- `npm run test:interactive-layout -- --grep "twisting and face painting inquiry|service photos expose working carousels|white-label platform leakage"` passed 31/31.
- `python scripts/verify/white_label_customer_surfaces.py --base-url http://localhost:8081` passed.
- `python -m py_compile` passed for touched route/patch Python files.

Earlier 2026-05-08 calculator receipt remains valid: `contact_prefill.py` covers mixed durations (one twisting artist at `1.5` hours plus one face painter at `2.5` hours totals `$490`, deposit `$100`, balance `$390`; adding a third one-hour artist totals `$620`, deposit `$150`, balance `$470`).

## Next Safe Changes

- If service pricing changes, update the page copy, calculator data attributes, `contact_prefill.py`, policy copy if affected, and this handoff together.
- If the form contract changes, update `/contact` and this embedded BTFP form together; do not fork a second customer intake form.
- If the carousel timing/controls/images change, update the Playwright carousel test and verify reduced-motion behavior.
- If repeat-email policy changes, update the CRM Settings patch, `book_form_repeat_email_photos.py`, this handoff, and the LT decision log together.
