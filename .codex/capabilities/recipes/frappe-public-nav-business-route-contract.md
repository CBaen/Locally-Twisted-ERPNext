---
id: frappe-public-nav-business-route-contract
name: Frappe Public Nav Business Route Contract
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted ERPNext/Frappe public navigation, header/footer IA, and service-route parity
currently_true: yes
verification_level: 2
last_verified: 2026-05-08
evidence_quality: direct
successful_uses: 2
failed_uses: 0
regressions: 0
depends_on:
  - frappe-sitewide-visual-overhaul
  - responsive-container-audit
used_by: []
tags:
  - Locally Twisted
  - Frappe
  - public navigation
  - route parity
  - business IA
---

# Frappe Public Nav Business Route Contract

Use this recipe when changing LT public navigation, footer links, mobile drawer
links, route pages, or verifier contracts that decide which business lanes are
visible to customers.

## Core Rule

Navigation is a business contract. Do not replace an approved line of business
with a generic explanatory page unless GL explicitly approves that trade.

For the current LT site:

- `Twisting & Face Painting` is a first-class service route at
  `/balloon-twisting-and-face-painting`.
- `Process` is not approved as a public top-level nav item or standalone route.
- `/contact` remains the shared quote/conversion path.
- Mobile search belongs at the bottom of the drawer, not in the mobile header
  action row. The mobile header control budget is logo plus cart/menu.
- Public navigation must not link to `/search`; the search overlay submits to
  `/shop?q=...`, and `/search` is a no-cache 404 fallback.

## Pattern

1. Read `_resources/STYLE-GUIDE.md` for the current primary navigation order.
2. Check `locally-twisted-decisions.md` for route/business-lane decisions.
3. Check `workstreams/menu-content-coordination.md` before editing shared chrome.
4. Update the same contract everywhere:
   - desktop header,
   - top utility/proof links,
   - mobile drawer,
   - footer,
   - navbar context data,
   - passive route list,
   - nav/shop smoke verifiers,
   - launch handoff/workstream docs.
5. Delete unapproved route files when a route is intentionally removed.
6. Add a negative verifier for the removed route/label, not only a positive
   verifier for the replacement link.
7. Clear Frappe website cache after Jinja/CSS edits.
8. Verify live route statuses and screenshots after cache clear.

## Verification Commands

```powershell
python scripts/dev/clear_website_cache.py
python scripts/verify/nav_ia.py
python scripts/verify/smoke_shop.py
npm run test:interactive-layout
npm run test:layout-fit
```

Use a direct route check to confirm removed routes are truly gone, not merely
hidden from nav.

## LT Receipt

On 2026-05-07 this recipe was created from the BTFP/Process correction. Codex
restored `Twisting & Face Painting` to the primary public nav, deleted
`www/process.html` and `www/process.py`, removed Process from header/footer and
route coverage, added nav verifier guards against Process returning, and
verified `/balloon-twisting-and-face-painting` as 200 while `/process` returned
404.

On 2026-05-08, GL reported that the mobile search button was smashing the cart
button and covering the logo. Codex removed the mobile header search button,
added `.lt-mega-drawer__search` at the bottom of the drawer, kept search as an
overlay that submits to `/shop`, and added a `/search` no-cache 404 override.
`nav_ia.py`, focused interactive header/search/drawer checks, and the focused
mobile drawer smoke helper passed.
