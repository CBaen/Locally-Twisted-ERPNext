# Civic Sitewide Redesign Workstream

Last updated: 2026-05-03 by Codex.

## Status

Implemented and verified locally as the current V1 visual direction.

This workstream is the feature handoff for the site-wide Civic Celebration redesign. The broader brand rationale remains in `workstreams/brand-audience-style-reset.md`; the canonical style rules live in `_resources/STYLE-GUIDE.md`.

## Approved Direction

Use Civic Celebration as the structure:

- Utah civic/event authority.
- City and Wasatch Front territory cues.
- Deep navy, ink, warm white, sandstone, brass, and restrained crimson.
- Corporate, school, city, venue, public-event, and premium private-event buyers first.

Use Locally Twisted Brand Direction as the polish layer:

- Stronger premium serif hierarchy.
- Brass/gold line icons.
- Cleaner proof structure.
- A readable `LOCALLY TWISTED` wordmark instead of the old delicate script treatment.

Keep Jeff as founder/context only. Locally Twisted, the team, and the company promise should carry public copy.

## Implemented

- Shared header and mobile header restyled.
- Shared theme CSS moved to the Civic palette and typography.
- Homepage hero replaced with the generated city/Wasatch asset:
  - `apps/locally_twisted/locally_twisted/public/images/home/hero-wasatch-city-20260503.png`
- Homepage proof/authority presentation aligned with brass line-icon treatment.
- `/contact` and the shared book form restyled; blank third-party map iframe replaced with a controlled service-area panel.
- `/balloon-twisting-and-face-painting`, `/portfolio`, `/faq`, `/privacy`, `/terms-of-service`, `/refund-policy`, `/accessibility`, `/thank-you`, `/payment-success`, `/shop`, category pages, product detail, `/cart`, and `/checkout` received the visual pass.
- Founder-centered public copy was removed from BTFP and portfolio where it was not a direct customer review quote.
- `hooks.py` CSS cache-bust was bumped for the Civic pass.

## Verification Receipt

Verified locally on 2026-05-03:

```bash
python scripts/dev/clear_website_cache.py --restart
python scripts/verify/nav_ia.py
npm run test:layout-fit
python scripts/verify/smoke_shop.py
python scripts/verify/cart_checkout_contract.py
python scripts/verify/catalog_variant_contract.py
python scripts/verify/variant_media_contract.py
python scripts/verify/contact_prefill.py --base-url http://localhost:8081
python scripts/verify/contact_service_logic.py --base-url http://localhost:8081
python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --shape-only --skip-newsletter
```

Also checked route statuses across the main customer routes. `/payment-success` redirects without a payment context, which is expected for that route.

Screenshots were captured and inspected at:

- `output/playwright/civic-overhaul-20260503-verified/`

## Remaining Work

- Final launch QA after any later content/media changes.
- Gallery and inspiration presentation still need a stronger photo-led treatment.
- Category/product media needs GL/Jeff review before assigning generic imagery by judgment.
- Blog channel and two ported posts remain separate P0 launch work.
- Exact review counts and third-party trust claims must be rechecked before launch because they drift.

## Next Agent Notes

- Do not reintroduce the pastel/rainbow UI as the company identity.
- Do not rebuild `/shop-by-category` as a separate card index.
- Use `_resources/STYLE-GUIDE.md` as the current visual authority.
- Use `frappe-sitewide-visual-overhaul` capability before another broad visual pass.
