---
name: Public nav changed by SEO or verifier drift
type: failure
failure_kind: process_failure
schema_version: 0.1
date_discovered: 2026-05-10
last_updated: 2026-05-10
status: guarded
scope: project
owner_context: Locally Twisted ERPNext public site
related_capabilities:
  - ../recipes/frappe-public-nav-business-route-contract.md
  - ../recipes/lt-seo-geo-aeo-contract.md
related_failures:
  - C:\Users\baenb\capabilities\failures\agent-owned-capability-root-fragmentation.md
  - C:\Users\baenb\projects\Built_by_Cameron\capabilities\failures\erpnext-public-nav-seo-verifier-drift.md
tags:
  - locally-twisted
  - public-nav
  - header
  - seo
  - geo
  - aeo
  - verifier
  - approval
---

# Failure Recipe: Public Nav Changed By SEO Or Verifier Drift

## Symptom

Owner-removed public header/banner/menu links return after agent work, or a
conversion label appears in multiple public chrome zones.

## Trigger conditions

- SEO/GEO/AEO or public-route work touches header, footer, search overlay,
  mobile drawer, top banner, or menu verification.
- Public ecommerce labels are treated as useful discovery links rather than
  approved business architecture.
- A verifier encodes an old or unapproved navigation state.

## Known instances

| Date | Project | Surface | Action being taken | Bad outcome | Evidence | Guard state | Status |
|---|---|---|---|---|---|---|---|
| 2026-05-10 | Locally Twisted | `navbar.html`, search quick links, `nav_ia.py` | About/service-nav and SEO-adjacent public-site work | Top banner included `Ready-to-Order`, `Cart`, `Recent Work`; `Free Event Quote` appeared in both top banner and menus/search | User correction; `git blame`; red/green `scripts/verify/nav_ia.py` behavior | project guard added | guarded |

## Root pattern

The public header and menu were treated as an optimization surface instead of
owner-approved business signage. The old verifier preserved duplicate quote
labels rather than protecting the approved IA.

## Why it seemed reasonable at the time

Links to quote, shop, cart, and portfolio can look helpful for conversion,
crawling, and navigation. Because the verifier expected duplicate quote chrome,
the bad state looked intentional to future agents.

## Detection signals

- Diffs in `apps/locally_twisted/locally_twisted/templates/includes/navbar/`.
- Diffs in `scripts/verify/nav_ia.py` that add or preserve duplicate CTA
  labels.
- `Ready-to-Order`, `Cart`, or `Recent Work` in the top banner.
- `Free Event Quote` outside the top banner.
- Search quick links duplicating top-banner-only CTA language.

## Required guard

`Free Event Quote` belongs only in the top header banner. `Ready-to-Order`,
`Cart`, and `Recent Work` do not belong in the top banner. SEO/GEO/AEO work must
not change header, footer, menu, search quick links, or public chrome without
explicit owner approval.

## Recovery recipe

1. Update `scripts/verify/nav_ia.py` so it fails against the bad header.
2. Repair the smallest navbar/search/drawer template surface.
3. Clear Frappe website cache after Jinja/CSS changes.
4. Run `python scripts\verify\nav_ia.py`.
5. Run search and layout checks that cover header/search behavior.
6. Update this Failure Recipe if another public-chrome regression occurs.

## What not to do

- Do not call public chrome changes SEO if approval is missing.
- Do not keep duplicate `Free Event Quote` labels because both point to
  `/contact`.
- Do not rewrite the verifier to protect unapproved header state.
- Do not remove the known instance because the current template was repaired.

## Cross-links

- Related capability: `../recipes/frappe-public-nav-business-route-contract.md`
- Related capability: `../recipes/lt-seo-geo-aeo-contract.md`
- Related agency failure: `C:\Users\baenb\projects\Built_by_Cameron\capabilities\failures\erpnext-public-nav-seo-verifier-drift.md`
- Related verifier: `..\..\scripts\verify\nav_ia.py`
- Related template: `..\..\apps\locally_twisted\locally_twisted\templates\includes\navbar\navbar.html`

## Evidence quality

Verified by direct user correction, local file history, and the current
`nav_ia.py` guard. The broader agency pattern is documented separately and
remains probationary outside LT.
