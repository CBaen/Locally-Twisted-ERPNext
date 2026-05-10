---
name: Public header contrast and safe-area regression
type: failure
failure_kind: regression_pattern
schema_version: 0.1
date_discovered: 2026-05-10
last_updated: 2026-05-10
status: guarded
scope: project
owner_context: Locally Twisted public header/banner CSS
related_capabilities:
  - ../recipes/frappe-public-nav-business-route-contract.md
  - ../recipes/responsive-container-audit.md
related_failures:
  - public-nav-seo-verifier-drift.md
  - C:\Users\baenb\projects\Built_by_Cameron\capabilities\failures\client-public-header-contrast-safe-area-regression.md
tags:
  - locally-twisted
  - header
  - accessibility
  - contrast
  - safe-area
  - mobile
---

# Failure Recipe: Public Header Contrast And Safe-Area Regression

## Symptom

The gold public header/banner looks acceptable at rest, but hover/focus text
drops below contrast requirements or mobile landscape notch padding protects
the wrong side.

## Trigger conditions

- Header top banner background changes to brass/gold.
- Hover/focus styles are copied from a dark-banner treatment.
- Mobile top strip uses CSS shorthand with safe-area vars.
- Verification checks text/link presence but not the interaction state or
  asymmetric safe-area mapping.

## Known instances

| Date | Project | Surface | Action being taken | Bad outcome | Evidence | Guard state | Status |
|---|---|---|---|---|---|---|---|
| 2026-05-10 | Locally Twisted | `lt-mega-menu.css` header banner | Header banner cleanup after owner CTA correction | Hover/focus changed banner text to `#fffdf9` on brass `#b89a5b` at 2.65:1 contrast; mobile safe-area left/right vars were reversed | Reviewer output, direct contrast calculation, source diff | `nav_ia.py` CSS guard added | guarded |

## Root pattern

The template contract was repaired, but the interaction-state CSS and mobile
safe-area contract were treated as visual polish instead of launch-facing
accessibility and device-fit behavior.

## Why it seemed reasonable at the time

The previous top strip used a dark background, where white hover text was
reasonable. When the banner became brass, the old hover convention no longer
held. Safe-area shorthand also looks symmetrical until a device has asymmetric
notch insets.

## Detection signals

- `#fffdf9` inside `.lt-mega-header__top-message` or
  `.lt-mega-header__mobile-message` hover/focus rules.
- CSS shorthand on `.lt-mega-header__mobile-top` with
  `safe-area-inset-left` in the right-padding slot or
  `safe-area-inset-right` in the left-padding slot.
- Header banner color changes without a focused contrast check.
- Mobile landscape or notched device complaints after header work.

## Required guard

`scripts/verify/nav_ia.py` must fail if the banner hover/focus text is not
`var(--lt-mega-ink)` or if mobile safe-area padding swaps the left/right vars.
Rendered header/drawer checks still cover fit; source CSS catches the exact
regression before visual review.

## Recovery recipe

1. Keep banner hover/focus text dark on brass.
2. Use underline for hover/focus and outline only for keyboard focus.
3. Map CSS shorthand as top, right, bottom, left.
4. Clear Frappe website cache after CSS/template changes.
5. Run `python scripts\verify\nav_ia.py`.
6. Run focused interactive header/drawer/mobile checks.
7. Record the failure before removing review evidence from memory.

## What not to do

- Do not use white text on the brass banner for hover/focus.
- Do not rely on default link focus styling after removing contrast.
- Do not treat safe-area shorthand as obvious without checking the side order.
- Do not call a static banner screenshot proof of hover/focus accessibility.

## Cross-links

- Related workstream: `../../workstreams/public-header-banner-contract-2026-05-10.md`
- Related verifier: `../../scripts/verify/nav_ia.py`
- Related CSS: `../../apps/locally_twisted/locally_twisted/public/css/lt-mega-menu.css`
- Related agency failure: `C:\Users\baenb\projects\Built_by_Cameron\capabilities\failures\client-public-header-contrast-safe-area-regression.md`

## Evidence quality

The LT instance is verified by reviewer finding, direct source patch, direct
contrast calculation, cache clear, `nav_ia.py`, and focused Playwright
interactive header coverage. The source guard is current as of 2026-05-10.
