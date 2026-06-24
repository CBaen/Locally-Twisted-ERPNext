# Homepage Seasonal Hero Carousel — 2026-05-10

## Outcome

Superseded current state as of 2026-06-24:

The Fourth of July seasonal slide was removed from local source after GL
rejected the hero image and asked to remove the Fourth of July hero entirely.
The homepage carousel now rotates through four quote-led audience slides:

1. Civic & Community
2. Corporate Events
3. Schools & Campuses
4. Private Celebrations

Current follow-up handoff:
`workstreams/homepage-hero-photoreal-refresh-2026-06-24.md`.

Historical state:

Homepage hero previously rotated through five quote-led slides. The first slide
was updated on 2026-06-21 for the Fourth of July seasonal push:

1. Fourth of July events first (`july-4-home-hero-desktop.webp`)
2. Civic & Community
3. Corporate Events
4. Schools & Campuses
5. Private Celebrations

## Contract

- First slide owns the only page-level H1.
- Later slides use H2s, not extra H1s.
- The first slide owns the active H1. As of the 2026-06-24 follow-up, this is
  Civic & Community until a future seasonal slot is explicitly approved again.
- Audience slides link to their matching audience routes and include a secondary quote/contact CTA.
- The seasonal slide no longer has a secondary `/event-balloons` CTA because
  the `/event-balloons` hub route is removed.
- Do not add a hero CTA to `/event-balloons`; use `/contact`, `/portfolio`, or
  the four audience routes only.
- Copy remains quote-led. Even while public ecommerce is open for testing, do
  not turn the homepage hero into a checkout/order-forward surface without a
  fresh GL marketing decision.
- Reduced-motion users get a stable first slide.
- Keep compact hero sizing and next-band visibility guarded by `interactive_layout.spec.js`.

## Files

- `apps/locally_twisted/locally_twisted/www/home.py`
- `apps/locally_twisted/locally_twisted/www/home.html`
- `scripts/verify/interactive_layout.spec.js`
- `capabilities/recipes/homepage-launch-proof-contract.md`
- `workstreams/event-balloons-route-removal-2026-05-11.md`

## Verification Receipt

- Historical custom rendered contract confirmed 5 slides, graduation first image/topic, and all four audience ads.
- 2026-06-24 follow-up proof confirmed 4 slides, Civic & Community first H1,
  no Fourth of July body copy, home layout-fit `13 passed`, home container
  contract `3 passed`, and focused interactive homepage/compact-hero
  `62 passed`.
- Targeted Playwright after implementation passed: `npm run test:interactive-layout -- --grep "homepage hero|white-label platform leakage|balloon twisting"` -> 31 passed.
- White-label customer surface verifier passed after the public route change.

## Next Safe Changes

- Seasonal swaps require explicit approval and should be one small update to
  `HOME_HERO_SLIDES[0]` plus a focused homepage hero test update. If the swap
  needs generated balloon imagery, first use
  `capabilities/recipes/lt-photoreal-balloon-homepage-hero-contract.md`.
- Do not reintroduce blog/product/shop/purchase slides unless GL explicitly reopens that lane.
- Do not restore the removed `/event-balloons` hub as a hero destination unless
  GL makes a fresh route decision.
- If the hero becomes manually controlled, preserve one H1 and accessible reduced-motion fallback.
