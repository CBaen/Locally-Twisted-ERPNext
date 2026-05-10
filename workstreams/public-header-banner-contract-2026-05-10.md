# Public Header Banner Contract - 2026-05-10

Status: complete and guarded.
Owner context: Locally Twisted public header/top banner.
Primary files:
- `apps/locally_twisted/locally_twisted/templates/includes/navbar/navbar.html`
- `apps/locally_twisted/locally_twisted/public/css/lt-mega-menu.css`
- `scripts/verify/nav_ia.py`
- `workstreams/menu-content-coordination.md`
- `capabilities/failures/public-nav-seo-verifier-drift.md`
- `capabilities/failures/public-header-contrast-safe-area-regression.md`

## Current Contract

- Desktop top banner has the centered linked short-notice message:
  `SHORT NOTICE? LET US KNOW. WE CAN OFTEN HELP WITH 24 HOURS NOTICE!`
- That short-notice link points to `/contact`.
- Mobile has its own visible gold short-notice strip, also linked to
  `/contact`.
- `Free Event Quote` appears only in the desktop top-banner utility links.
- `Free Event Quote` must not appear in primary nav, mobile drawer, search
  quick results, or the desktop CTA button.
- `Contact Us` remains the visible menu/drawer CTA to `/contact`.
- `Ready-to-Order`, `Cart`, and `Recent Work` do not belong in the top banner.
  They may appear in their approved primary/search/drawer/shop contexts while
  ecommerce is open for local testing.
- Banner hover/focus text stays `var(--lt-mega-ink)` on brass. Do not use
  white text on the brass banner for hover or focus.
- Mobile safe-area padding maps right inset to right padding and left inset to
  left padding.

## Why This Exists

GL corrected two different classes of header drift:

- Owner-removed banner items came back, and `Free Event Quote` was duplicated
  in the banner and menu/search.
- A later CSS review found the fixed gold banner used low-contrast hover/focus
  white text and reversed mobile safe-area padding.

The header is customer-facing business signage. SEO/GEO/AEO or route work may
need metadata, structured data, sitemap rules, page content, and visible FAQ
answers. It must not mutate header, footer, menu, drawer, or search quick-link
IA without explicit approval.

## Verification

Fresh checks from the closeout:

```powershell
python scripts\dev\clear_website_cache.py
python scripts\verify\nav_ia.py
npm run test:interactive-layout -- --grep "header|drawer|mega|mobile"
git diff --check -- apps\locally_twisted\locally_twisted\public\css\lt-mega-menu.css
```

Results:

- Website cache clear passed.
- `nav_ia.py` passed and now checks the linked short notice, top-banner-only
  quote CTA, forbidden banner items, dark banner hover/focus color, and safe-area
  padding order.
- Focused interactive header/drawer/search/mega/mobile run passed 55/55.
- Direct contrast calculation showed `#0a0a0b` on `#b89a5b` at 7.36:1; the
  rejected white state was 2.65:1.

## Next-Agent Rules

- Do not call header/footer/menu edits "SEO" unless the task explicitly names
  that public chrome surface and the approval evidence.
- If a new banner item is requested, decide which existing slot it replaces
  before adding it.
- Update `scripts/verify/nav_ia.py` before changing the template when fixing a
  known bad state.
- Keep completed work out of `locally-twisted-queue.md`; the queue is active
  work only.
