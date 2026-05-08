# Nav BTFP / Process Correction

Last updated: 2026-05-08 by Codex after linking the BTFP service-page handoff.

## Outcome

Restore the approved `Twisting & Face Painting` business lane to the primary
public navigation and remove the unapproved standalone `Process` page from
customer-facing chrome and route contracts.

## Status

Complete for the current public website.

Follow-up BTFP service-page/form/calculator details live in
`workstreams/btfp-service-page.md`. Keep this file focused on the nav and
unapproved Process route correction.

## Source-Of-Truth Decision

See `locally-twisted-decisions.md` entry:

`2026-05-07 - Twisting & Face Painting restored; standalone Process removed`

Current rule:

- Primary nav: `Event Balloons`, `Portfolio`, `Twisting & Face Painting`,
  `Ready-to-Order`, `FAQ`.
- `Free Event Quote` points to `/contact`.
- `/balloon-twisting-and-face-painting` is the approved live-service route.
- `/process` is not an approved public route and should stay gone unless GL
  explicitly reopens it.

## Files Owned By This Slice

- `apps/locally_twisted/locally_twisted/templates/includes/navbar/navbar.html`
- `apps/locally_twisted/locally_twisted/templates/includes/footer/footer.html`
- `apps/locally_twisted/locally_twisted/navbar_context.py`
- `apps/locally_twisted/locally_twisted/public/css/lt-mega-menu.css`
- `apps/locally_twisted/locally_twisted/public/css/lt-theme.css`
- `apps/locally_twisted/locally_twisted/hooks.py`
- `scripts/verify/nav_ia.py`
- `scripts/verify/smoke_shop.py`
- `scripts/verify/layout_helpers.js`
- `apps/locally_twisted/locally_twisted/www/process.html` deleted
- `apps/locally_twisted/locally_twisted/www/process.py` deleted
- BTFP page follow-up owned by `workstreams/btfp-service-page.md`

Docs updated:

- `CODING-HANDOFF.md`
- `_resources/STYLE-GUIDE.md`
- `locally-twisted-decisions.md`
- `locally-twisted-queue.md`
- `lessons-learned.md`
- `workstreams/menu-content-coordination.md`
- `workstreams/website-launch.md`
- `workstreams/brand-style-guide-consolidation.md`
- `.codex/capabilities/INDEX.md`
- `.codex/capabilities/recipes/frappe-public-nav-business-route-contract.md`
- `.codex/capabilities/evidence/capability-evidence.jsonl`

## Implementation Notes

- Desktop nav and mobile drawer now expose `Twisting & Face Painting` at
  `/balloon-twisting-and-face-painting`.
- Top proof links and footer no longer link to `/process`.
- `SERVICE_LINKS` no longer carries Process or a duplicate BTFP helper link.
- The BTFP desktop nav label has a dedicated wrapping class so it fits at the
  active 1200px desktop breakpoint without shortening the approved label.
- The passive public route list no longer includes `/process`; it still includes
  `/balloon-twisting-and-face-painting`.
- `nav_ia.py` now fails if Process returns to public nav/footer source.
- `smoke_shop.py` now checks desktop/mobile BTFP nav links instead of Process.

## Verification Receipt

Fresh checks from 2026-05-07:

- `python scripts/dev/clear_website_cache.py` passed.
- `python scripts/verify/nav_ia.py` passed.
- `python -m py_compile scripts/verify/nav_ia.py scripts/verify/smoke_shop.py apps/locally_twisted/locally_twisted/navbar_context.py apps/locally_twisted/locally_twisted/hooks.py` passed.
- `python scripts/verify/smoke_shop.py` passed.
- `npm run test:portfolio-reel` passed 4/4.
- `npm run test:checkout-experience` passed 2/2.
- `npm run test:interactive-layout` passed 74/74.
- `npm run test:layout-fit` passed 247/247.
- Direct route check returned 200 for `/`, `/event-balloons`, `/portfolio`,
  `/balloon-twisting-and-face-painting`, `/contact`, `/shop`, and `/faq`.
- Direct route check returned 404 for `/process`.
- Manual Playwright audit checked desktop nav, mobile drawer, BTFP desktop,
  BTFP mobile, 32 BTFP images, 19 chrome/footer internal links, and no Process
  anchors in inspected chrome or BTFP page.

## Cleanup

- Deleted the unapproved `www/process.html` and `www/process.py` route files.
- Removed the transient `output/layout-fit-current.log`.
- Screenshot output remains ignored under `output/` and is not production source.

## Future Guardrail

If someone wants a planning/process explanation later, it must be explicitly
approved as a section on an approved business route or as a new named route. Do
not use a generic Process page to displace a real Locally Twisted service line.
