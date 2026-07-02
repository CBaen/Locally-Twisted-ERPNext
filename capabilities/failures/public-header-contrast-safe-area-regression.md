---
name: Public header contrast and safe-area regression
type: failure
failure_kind: regression_pattern
schema_version: 0.1
date_discovered: 2026-05-10
last_updated: 2026-05-11
status: guarded
scope: project
owner_context: Locally Twisted public header/banner CSS
related_capabilities:
  - ../recipes/frappe-public-nav-business-route-contract.md
  - ../recipes/responsive-container-audit.md
related_failures:
  - public-nav-seo-verifier-drift.md
  - /home/guidingl/projects/Built_by_Cameron/capabilities/failures/client-public-header-contrast-safe-area-regression.md
tags:
  - locally-twisted
  - header
  - accessibility
  - contrast
  - safe-area
  - mobile
---

# Failure Recipe: Public Header Color, Contrast, And Safe-Area Regression

## Symptom

The public short-notice header/banner regresses from the approved deep-navy
authority band to brass/gold, or its hover/focus/mobile safe-area behavior
drifts while the text/link content still looks correct.

## Trigger conditions

- Header top banner background changes to brass/gold.
- Static source guards check text/link presence but not the color token.
- Hover/focus styles are copied between dark and brass treatments without
  revalidating the approved banner color.
- Mobile top strip uses CSS shorthand with safe-area vars.
- Verification checks text/link presence but not the interaction state or
  asymmetric safe-area mapping.

## Known instances

| Date | Project | Surface | Action being taken | Bad outcome | Evidence | Guard state | Status |
|---|---|---|---|---|---|---|---|
| 2026-05-10 | Locally Twisted | `lt-mega-menu.css` header banner | Header banner cleanup after owner CTA correction | Deep-navy banner was changed to brass/gold and docs/verifiers then described brass as the protected state | `git blame` pins `.lt-mega-header__top` brass rule to `f091c72`; `workstreams/public-header-banner-contract-2026-05-10.md` and `menu-content-coordination.md` said gold/brass | `nav_ia.py`, `smoke_shop.py`, and `interactive_layout.spec.js` now guard navy desktop/mobile color | guarded |

## Root pattern

The content/IA contract and the visual color contract split. A later commit
correctly guarded banner copy and link placement, but normalized brass/gold as
the intended banner color even though the May 6 header repair had moved the
public chrome to a deep-navy authority band.

## Why it seemed reasonable at the time

The banner task was framed around copy placement and utility-link cleanup, so
the visual color was treated as incidental. The stale docs then made the wrong
color look approved to the next agent.

## Detection signals

- `background: var(--lt-mega-brass)` on `.lt-mega-header__top` or
  `.lt-mega-header__mobile-top`.
- Docs that describe the short-notice strip as gold/brass.
- CSS shorthand on `.lt-mega-header__mobile-top` with
  `safe-area-inset-left` in the right-padding slot or
  `safe-area-inset-right` in the left-padding slot.
- Header banner color changes without a focused contrast check.
- Mobile landscape or notched device complaints after header work.

## Required guard

`scripts/verify/nav_ia.py` must fail if desktop or mobile top banner CSS is not
`background: var(--lt-mega-navy)` with warm text. Rendered checks must also
assert `rgb(14, 34, 64)` for `.lt-mega-header__top` and
`.lt-mega-header__mobile-top`. Source CSS catches contract drift before visual
review; rendered checks catch stale-cache or load-order failures.

## Recovery recipe

1. Keep desktop and mobile short-notice strips deep navy.
2. Keep banner text warm white; use brass only as focus/underline accent.
3. Map CSS shorthand as top, right, bottom, left.
4. Clear Frappe website cache after CSS/template changes.
5. Run `python scripts/verify/nav_ia.py`.
6. Run focused interactive header/drawer/mobile checks.
7. Record the failure before removing review evidence from memory.

## What not to do

- Do not describe or implement the public short-notice strip as brass/gold.
- Do not rely on default link focus styling after removing contrast.
- Do not treat safe-area shorthand as obvious without checking the side order.
- Do not call a static source check proof of the live rendered banner color.

## Cross-links

- Related workstream: `../../workstreams/public-header-banner-contract-2026-05-10.md`
- Related verifier: `../../scripts/verify/nav_ia.py`
- Related CSS: `../../apps/locally_twisted/locally_twisted/public/css/lt-mega-menu.css`
- Related agency failure: `/home/guidingl/projects/Built_by_Cameron/capabilities/failures/client-public-header-contrast-safe-area-regression.md`

## Evidence quality

The LT instance is verified by reviewer finding, direct source patch, direct
contrast calculation, cache clear, `nav_ia.py`, and focused Playwright
interactive header coverage. The source guard is current as of 2026-05-10.
