# Public Header Banner Contract - 2026-05-10

Status: corrected and guarded as navy on 2026-05-11.
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
- Mobile has its own visible deep-navy short-notice strip, also linked to
  `/contact`.
- `Free Event Quote` appears only in the desktop top-banner utility links.
- `Free Event Quote` must not appear in primary nav, mobile drawer, search
  quick results, or the desktop CTA button.
- `Contact Us` remains the visible menu/drawer CTA to `/contact`.
- `Ready-to-Order`, `Cart`, and `Recent Work` do not belong in the top banner.
  They may appear in their approved primary/search/drawer/shop contexts while
  ecommerce is open for local testing.
- Desktop and mobile short-notice strips use `var(--lt-mega-navy)` with
  `var(--lt-mega-warm)` text. Brass is an accent for focus/underline only.
- Mobile safe-area padding maps right inset to right padding and left inset to
  left padding.

## Why This Exists

GL corrected two different classes of header drift:

- Owner-removed banner items came back, and `Free Event Quote` was duplicated
  in the banner and menu/search.
- A later CSS review incorrectly normalized a gold/brass banner as the guarded
  state. GL re-caught the live regression on 2026-05-11: the public strip
  belongs to the navy authority-band treatment from the May 6 header repair.
- Forensic trace: commit `f091c72` changed `.lt-mega-header__top` and
  `.lt-mega-header__mobile-top` to `var(--lt-mega-brass)` and updated nearby
  docs/guards so the wrong color looked intentional. Future fixes must correct
  source CSS, rendered checks, and written contracts together.

The header is customer-facing business signage. SEO/GEO/AEO or route work may
need metadata, structured data, sitemap rules, page content, and visible FAQ
answers. It must not mutate header, footer, menu, drawer, or search quick-link
IA without explicit approval.

## Verification

Fresh checks from the closeout:

```powershell
python -m py_compile scripts\verify\nav_ia.py scripts\verify\smoke_shop.py apps\locally_twisted\locally_twisted\navbar_context.py
python scripts\verify\nav_ia.py
npx.cmd playwright test scripts/verify/interactive_layout.spec.js --grep "header breakpoint contract" --reporter=line
python scripts\verify\smoke_shop.py
```

Results:

- Python compile passed for the touched verifier/search modules.
- `nav_ia.py` passes and now checks the linked short notice, top-banner-only
  quote CTA, forbidden banner items, navy desktop/mobile banner color,
  warm-white banner text, and safe-area padding order.
- Focused Playwright header breakpoint contract passed 8/8.
- `smoke_shop.py` passed and now checks rendered desktop navy.
- Direct live browser probes showed desktop `.lt-mega-header__top` at
  `rgb(14, 34, 64)`, warm text `rgb(250, 247, 242)`, height `49`; mobile
  `.lt-mega-header__mobile-top` at `rgb(14, 34, 64)`, warm text
  `rgb(250, 247, 242)`, height `43`.

## Next-Agent Rules

- Do not call header/footer/menu edits "SEO" unless the task explicitly names
  that public chrome surface and the approval evidence.
- If a new banner item is requested, decide which existing slot it replaces
  before adding it.
- Update `scripts/verify/nav_ia.py` before changing the template when fixing a
  known bad state.
- If the banner color changes in code, scan `CODING-HANDOFF.md`,
  `locally-twisted-queue.md`, `workstreams/`, and `capabilities/` for stale
  banner-color language before closeout. A stale doc was the regression source.
- Keep completed work out of `locally-twisted-queue.md`; the queue is active
  work only.
