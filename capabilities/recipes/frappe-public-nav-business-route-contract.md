---
id: frappe-public-nav-business-route-contract
name: Frappe Public Nav Business Route Contract
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted ERPNext/Frappe public navigation, header/footer IA, and service-route parity
currently_true: yes
verification_level: 2
last_verified: 2026-05-21
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
- Current launch desktop primary header labels include a non-link
  `Event Balloons` audience dropdown, `Twisting & Face Painting`, the public
  shop category dropdown, `Portfolio`, `About Us`, `FAQ`, and `Contact Us`
  when ecommerce is open for testing. Source and live now expose the shop
  category dropdown as `Pickups & Deliveries`. Older docs may still say
  `Ready-to-Order` or `Balloons-to-Order`; treat those as historical shorthand
  unless source and live proof say otherwise. The event dropdown links only to
  `/civic-community`, `/corporate-events`, `/schools-campuses`, and
  `/private-celebrations`; `/event-balloons` is removed and must not be linked
  or redirected. The top utility banner replaces the old proof copy/icon with a
  centered deep-navy `/contact` short-notice link:
  `SHORT NOTICE? LET US KNOW. WE CAN OFTEN HELP WITH 24 HOURS NOTICE!`, while
  keeping `Free Event Quote` and the account link on the right.
- `Twisting & Face Painting` points to `/balloon-twisting-and-face-painting`.
- The public shop category dropdown points to `/shop` when
  `lt_ecommerce_paused=0`.
- The public shop category header, mobile drawer, and search quick links are
  category discovery, not product merchandising. They must come from visible
  ERPNext `Item Group` children of `Shop Items`, ordered by weightage, matching
  the `/shop` category source. Copy must be customer-facing category language
  and must not mention ERPNext, Website Item, backend approval, or internal
  checkout-lane concepts.
- `Free Event Quote` and `Contact Us` point to `/contact`; `Free Event Quote`
  belongs in the top utility banner and must not replace the BTFP service lane
  in primary nav, mobile drawer, or search quick links.
- Removing, hiding, renaming, or replacing a canonical service lane requires an
  explicit GL approval marker; quote/conversion copy requests do not imply
  service removal approval.
- Mobile search belongs at the bottom of the drawer, not in the mobile header
  action row. In open ecommerce testing, the mobile header control budget is
  logo plus cart plus menu, with a separate deep-navy short-notice `/contact`
  strip above the mobile header row.
- Public navigation must not link to `/search`; the search overlay submits to
  `/shop` while ecommerce is open and `/search` is a no-cache 404 fallback.
- Public navigation, footer, search, hero CTAs, and portfolio actions must not
  link to `/event-balloons`.

## Pattern

1. Read `_resources/STYLE-GUIDE.md` for the current primary navigation order.
2. Check `locally-twisted-decisions.md` for route/business-lane decisions.
3. Check `workstreams/menu-content-coordination.md` before editing shared chrome.
4. Update the same contract everywhere:
   - desktop header,
   - top utility/proof links,
   - mobile drawer,
   - search quick links,
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
npm run test:search-contract
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

On 2026-05-10, after GL paused public ecommerce and corrected header copy,
Codex removed Ready-to-Order/cart product chrome from public launch navigation,
changed search to submit to `/contact`, changed the former header CTA label to
`Contact Us`, changed the adjacent service label to `Free Event Quote`, and
kept both labels pointed at `/contact`. `nav_ia.py`, live rendered HTML checks,
cache clear, and focused Playwright header/search/drawer checks passed.

Later on 2026-05-10, GL caught that the quote-label change had silently removed
BTFP from desktop nav, mobile drawer, and search quick links. OpenClaw/Moji
restored `Twisting & Face Painting` as a canonical public service lane and
added `CANONICAL_SERVICE_NAV_LINKS` / `NAV_SERVICE_REMOVAL_APPROVALS` to
`scripts/verify/nav_ia.py`. The BTFP lane may now disappear only when
`workstreams/nav-service-removal-approvals.md` contains the exact explicit
approval marker. `python scripts/verify/nav_ia.py`, live desktop/mobile link
checks, and focused Playwright header/drawer checks passed.

Later on 2026-05-10, GL reopened public ecommerce for full local testing.
Codex set `lt_ecommerce_paused=0`, cleared website cache, and restored the
active proof posture to open Ready-to-Order/cart/search behavior. `npm run
test:ecommerce-full` and `npm run test:public-verify` passed with open
ecommerce checks included.

Later on 2026-05-10, GL clarified the top menu banner should add the short
notice line while leaving `Free Event Quote` and the account link in place.
The nav contract now keeps `Free Event Quote` top-banner-only, `Contact Us` as
the primary conversion CTA, and `Twisting & Face Painting` as the service lane.
`nav_ia.py`, `smoke_shop.py`, and full `npm run test:public-verify` passed.

Follow-up correction: the short-notice line belongs in the former proof slot.
The old `Prepared design, clean installs, and invoiced event support across
Utah.` copy and `delivery-install.svg` icon are removed from the header.
`nav_ia.py`, `smoke_shop.py`, and direct Playwright header metrics passed after
cache clear/restart.

Final GL correction on 2026-05-11: the short-notice sentence is a `/contact`
link, centered to the screen on desktop, deep navy on desktop and mobile,
visible on mobile, and slightly letter-spaced on desktop. Warm-white text is
required; brass is only an accent/focus treatment, not the banner background.
`nav_ia.py`, focused `interactive_layout.spec.js --grep "header breakpoint contract"`,
`smoke_shop.py`, and direct desktop/mobile browser probes passed.

Review closeout on 2026-05-11: the 2026-05-10 gold/brass banner language was a
regression source. The top strip must remain `var(--lt-mega-navy)` on desktop
and mobile, and the mobile banner safe-area shorthand must map right inset to
right padding and left inset to left padding. `nav_ia.py` now fails if the
source contract moves the strip away from navy, and rendered guards verify
`rgb(14, 34, 64)` for desktop/mobile banner backgrounds.

On 2026-05-11, GL rejected the standalone `/event-balloons` hub before launch.
Codex deleted `www/event_balloons.html` and `.py`, removed the route alias and
canonical mapping, removed footer/search/home/portfolio links, and added
negative guards in `nav_ia.py`, `seo_contract.spec.js`, `interactive_layout`,
and route lists. Direct local checks return 404 with no redirect for both
`/event-balloons` and `/event_balloons`; sitemap search is clean. The four
event audience routes remain live.

On 2026-05-12, review closeout hardened the then-current Ready-to-Order product
quick-link contract. That product-link contract is superseded for public chrome
by the 2026-05-21 category-menu decision below, but remains useful history for
product-page checkout eligibility. `READY_TO_ORDER_OWNER_INCLUDE_CODES` is now
only an allowlist, and
`navbar_context.py` still requires backend Website Item `simple_product|checkout`
before nav/search exposure. `search_contract.spec.js` now asserts filtered
backend-approved quick links are hidden rather than removed, while Classic
owner-excluded products remain absent. `python scripts\verify\nav_ia.py`,
`npm run test:search-contract`, and live ERPNext reads of the four included item
codes passed.

On 2026-05-21, GL corrected the menu level: the public Ready-to-Order dropdown
must not be a product list or expose ERPNext/backend copy. Codex changed
`navbar_context.py` to source menu/search/drawer entries from `Item Group`
children under `Shop Items`, aligned navbar/search/mobile labels to
customer-facing category concepts, and updated `nav_ia.py`, `smoke_shop.py`,
`search_contract.spec.js`, and `ecommerce_pause_contract.py` to reject the old
product quick-link contract. Branch-level syntax and source nav verification
passed. Codex then repointed the local Docker stack with a temporary compose
override so `localhost:8081` mounted the branch worktree, cleared website
cache, and `python scripts/verify/smoke_shop.py` passed with all shop smoke
checks.

On 2026-06-24, GL confirmed the next customer-facing label for this category
menu should be `Pickups & Deliveries`. Codex implemented the rename in
source across desktop nav, mobile drawer, search quick links, footer language,
shop category rail/select, `/shop` copy, paused-shop negative checks,
nav/smoke/ecommerce verifiers, and current docs. Preserve the 2026-05-21
category-discovery rule; do not turn this menu into product merchandising while
renaming it. Local verification passed nav IA, ecommerce pause, search
contract, shop smoke, interactive layout, layout-fit, and container contract.
Live release then advanced app mirror tracked branch
`live-shop-discovery-20260529` to `8d8d205` with `press-deploy-bench-40102`.
Fresh live proof on `https://locallytwisted.com/` shows `Pickups & Deliveries`
and `All Pickups & Deliveries`, no `Balloons-to-Order`, `/shop` title
`Pickups & Deliveries Balloon Decor`, Cloudflare route gate pass, and live SEO
contract pass. Implementation handoff:
`workstreams/homepage-july-favorites-nav-plan-2026-06-24.md`.
