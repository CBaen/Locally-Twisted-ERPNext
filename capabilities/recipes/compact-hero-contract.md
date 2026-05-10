---
id: compact-hero-contract
name: Compact Hero Contract
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted public page heroes in ERPNext/Frappe and Webshop routes
currently_true: yes
verification_level: 2
last_verified: 2026-05-10
evidence_quality: direct
successful_uses: 4
failed_uses: 1
regressions: 0
depends_on:
  - responsive-container-audit
used_by:
  - homepage-launch-proof-contract
  - website-launch
tags:
  - Locally Twisted
  - heroes
  - responsive layout
  - Playwright
  - Frappe
---

# Compact Hero Contract

Use this recipe before changing a public page hero. This is a layout contract,
not a design preference: heroes orient the visitor, then content and product
proof take over.

## Standard

| Viewport family | Standard height | Hard max | Padding cap | Title cap |
|---|---:|---:|---:|---:|
| Mobile `< 768px` | 220px | 280px | 24px top / 24px bottom | 32px |
| Tablet `768px-1199px` | 250px | 300px | 28px top / 28px bottom | 40px |
| Desktop `>= 1200px` | 280px | 320px | 32px top / 32px bottom | 44px |

## Rules

- If a route has a hero, it uses the same standard height as other heroes in
  that viewport family.
- Public page heroes use generated lifestyle photo layers with
  breakpoint-specific WebP crops: `*-mobile.webp`, `*-tablet.webp`, and
  `*-desktop.webp`. Do not source hero crops from the reserved real
  work/proof photo library.
- Keep source generations, prompts, and review sheets in `_resources/`; the
  public hero asset folder should contain only the breakpoint-ready crops.
- Hero text sits above a black landing-page-style readability overlay. Do not
  place hero text directly on a bare image, and do not use a single crop for
  all breakpoints.
- A hero may carry eyebrow, H1, and one short lede. Extra proof, terms, CTAs,
  and sales explanation move below the hero if they create crowding.
- Do not add page-local `min-height`, large `clamp()` title scales, or vertical
  padding that overrides the shared contract.
- Route-specific CSS is allowed only to fit real content into the contract, not
  to make that route special.
- On a common laptop viewport, the next section should be visible. A hero must
  never consume the first screen as if it is the website.

## Current Covered Routes

- `/` via `.lt-hero`
- `/event-balloons` via `.lt-authority-hero`
- `/civic-community`, `/corporate-events`, `/schools-campuses`, and
  `/private-celebrations` via `.lt-authority-hero`
- `/portfolio` via `.lt-portfolio__hero`
- `/balloon-twisting-and-face-painting` via `.lt-btfp__intro`
- `/contact` via `.lt-contact__intro`
- `/shop` via `.lt-shop__hero`
- `/shop-items/<group>` via `.lt-shop__hero`

## Root Cause This Prevents

LT accumulated page-local hero rules: global `section` padding, route-level
`min-height`, oversized title clamps, and inner padding all stacked differently
by route. The result was inconsistent hero heights from roughly 247px to 846px
desktop and 254px to 818px mobile, with some pages hiding all useful content
below the fold.

## Verification

```powershell
npm run test:interactive-layout -- --grep "compact hero height contract"
```

For broad closeout, also run:

```powershell
python scripts/dev/clear_website_cache.py
npm run test:layout-fit
npm run test:interactive-layout
npm run test:container-contract
npm run test:a11y
```

Restart the backend container before cache clear when a route-controller
`PAGE_CSS` constant changes.

For visual hero closeout, inspect screenshots at mobile, tablet, and desktop
breakpoints. The executable guard checks crop filenames and overlay presence,
but human inspection is still needed for subject framing.

## LT Receipt

On 2026-05-10, GL reported that the four Event Balloons audience-page mobile
heroes looked wrong. Root cause: the audience pages and the `/event-balloons`
hub still rendered old real-photo hero panels inside the fixed compact hero
shell, so mobile clipped the H1/CTA and started the proof band under a cropped
photo. The repair removed those hero panels, let the shared generated-photo
hero layer own the image, loaded `lt-photo-heroes.css`, and added a focused
phone regression for `/civic-community`, `/corporate-events`,
`/schools-campuses`, and `/private-celebrations`.

Verification for the event lane passed: focused audience hero regression 12/12,
event compact-hero checks for `/event-balloons` and the four audience pages,
targeted `layout-fit` 65/65, targeted `container-contract` 15/15, and
`test:a11y-manual`. Later 2026-05-10 launch verification repaired the unrelated
homepage/BTFP compact-hero and homepage carousel accessibility blockers:
full `interactive_layout.spec.js` passed 163/163 inside the website gate, and
`npm run test:a11y` passed 50 route/viewport axe checks with 0 violations.
