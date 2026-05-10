# Homepage Seasonal Hero Carousel — 2026-05-10

## Outcome

Homepage hero now rotates through five quote-led slides:

1. Graduation season first (`school-grad-garland.webp`)
2. Civic & community
3. Corporate events
4. Schools & campuses
5. Private celebrations

This implements GL's request for a seasonal first hero followed by the four Event Balloons submenu audience ads.

## Contract

- First slide owns the only page-level H1.
- Later slides use H2s, not extra H1s.
- First slide must stay graduation-seasonal until GL changes the seasonal campaign.
- Audience slides link to their matching audience routes and include a secondary quote/contact CTA.
- Copy remains quote-led. Do not make the hero checkout/order-forward while public ecommerce is paused.
- Reduced-motion users get a stable first slide.
- Keep compact hero sizing and next-band visibility guarded by `interactive_layout.spec.js`.

## Files

- `apps/locally_twisted/locally_twisted/www/home.py`
- `apps/locally_twisted/locally_twisted/www/home.html`
- `scripts/verify/interactive_layout.spec.js`
- `.codex/capabilities/recipes/homepage-launch-proof-contract.md`

## Verification Receipt

- Custom rendered contract confirmed 5 slides, graduation first image/topic, and all four audience ads.
- Targeted Playwright after implementation passed: `npm run test:interactive-layout -- --grep "homepage hero|white-label platform leakage|balloon twisting"` -> 31 passed.
- White-label customer surface verifier passed after the public route change.

## Next Safe Changes

- Seasonal swap should be one small update to `HOME_HERO_SLIDES[0]` plus a focused homepage hero test update.
- Do not reintroduce blog/product/shop/purchase slides unless GL explicitly reopens that lane.
- If the hero becomes manually controlled, preserve one H1 and accessible reduced-motion fallback.
