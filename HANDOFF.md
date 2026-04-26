# HANDOFF — Locally Twisted

**Last updated:** 2026-04-26 (Opus 4.7 — closing the codification + chrome + accessibility + contact + BTFP session)

Overwrite-not-append. Git is the changelog. Read this first; the SIBLING-LETTER.md next; everything else as needed.

## State of the world

**The platform-direction question is RESOLVED. Stay Frappe-native.** Logged in `locally-twisted-decisions.md` 2026-04-26 (later, after Slice 2 + accessibility + contact build). Three independent visual gates passed:

1. `/accessibility` — static portal page, GL confirmed in browser
2. Slice 2 chrome (header + footer) — Jinja partial overrides at `templates/includes/{navbar,footer}/`, iterated with GL on logo size, footer centering, padding, 3-col-on-mobile
3. `/contact` and `/balloon-twisting-and-face-painting` — form-bearing portal pages, AJAX → Lead + Communication, smoke-tested, GL confirmed

Real GL quotes from the session: *"the content in the middle of the page looked good!"*, *"so far so good! It's getting better."*, *"Holy shit! You did it!"*, *"this rebuild of the contact page minus the noted elements was near perfect."*

The two prior failed attempts on this stack failed by **technique**, not architecture. The codification work earlier this session made the right technique discoverable. The architecture was always sound.

## Three things that matter most on day one

**1. The agency-tier capabilities now have a meal.** `Built_by_Cameron/.claude/capabilities/meals/build-frappe-portal-page.md` codifies the end-to-end shape of building a portal page on a BBC client's Frappe stack. Worked example: LT contact page. **Read it before building any new page.** It includes 5 verified gotchas with receipts (text-align inheritance, underscore→dash routing, webshop bundle compilation, Lead Source ensure-or-create, browser cache).

**2. Three Frappe recipes underpin the meal:**
- `Built_by_Cameron/.claude/capabilities/recipes/frappe-conventions.md` — WHAT primitives Frappe gives you
- `Built_by_Cameron/.claude/capabilities/recipes/frappe-portal-implementation.md` — HOW to write code that uses them
- `Built_by_Cameron/.claude/capabilities/recipes/license-isolated-app-architecture.md` — keep custom code's coupling to GPL apps minimal

All written this session, all verified against running Frappe v15 source.

**3. Webshop's bundles compile in this stack now.** Node 18 + yarn installed in the backend container. Symlinks at `/usr/local/bin/{node,yarn}` so `/bin/sh` subprocesses find them. `bench build` produces real `web.bundle.WLOGYSZO.js` and `webshop-web.bundle.NHDMZE3Z.css`. The install + bench build is reproducible after `docker compose --force-recreate` via:

```bash
python scripts/setup/install_webshop.py --build-assets
```

## What's live at http://localhost:8081

| Surface | State |
|---|---|
| ERPNext v15.105.0 stack (9 containers) | Running |
| Apps installed | frappe (15.106.0), erpnext (15.105.0), locally_twisted (0.0.1), payments (0.0.1), webshop (0.0.1) |
| Custom Frappe app `locally_twisted` | bind-mounted across 8 services, editable pip install applied |
| `web_include_css` | `/assets/locally_twisted/css/lt-theme.css` (~30 KB after this session's chrome work) |
| **Header (Jinja partial override)** | Two-tier desktop (delivery strip + centered logo + login/cart on right; main nav row centered) + mobile single-row with hamburger + delivery strip below. At `apps/locally_twisted/locally_twisted/templates/includes/navbar/navbar.html`. |
| **Footer (Jinja partial override)** | Three sections: centered brand band (3 social icons, no Twitter), 3-column links (always 3 across — mobile too, per GL), copyright bar. At `apps/locally_twisted/locally_twisted/templates/includes/footer/footer.html`. |
| `/accessibility` | Static portal page; brief Option B intent-only statement |
| `/contact` | Form-bearing portal page; AJAX → Lead + Communication. Marketing content + 3-section locations card. |
| `/balloon-twisting-and-face-painting` | Form-bearing portal page; same shape as contact, larger form (10 fields). Aliased from `/balloon_twisting_and_face_painting` via `website_route_rules` in hooks.py |
| `/all-products` | Webshop default; HTTP 200; "No products found" empty state (no Website Items seeded yet) |
| `/cart` | Webshop default; 301 redirect to login (correct for Guest) |
| Smoke-test Leads from this session | Deleted at session end (CRM-LEAD-2026-00001 + 00002 + linked Communications) |

## What's NOT done (next session candidates, by readiness)

**Most ready (the meal applies cleanly, content already in Odoo XML):**
- `/refund-policy` — content in `_resources/policies/`, static portal page, ~15 minutes
- `/about` — small page, content in Odoo XML, ~15 minutes

**Medium effort (meal applies but content/data work first):**
- BTFP first-ship omissions: image carousels (need real photos or AI-generated), event-type animated crawl, modal-with-auto-redirect. Probably ship as separate iteration when GL has photos.
- Contact page first-ship omissions: Google Maps iframe, modal-with-auto-redirect, `/privacy` route target.
- `/book` — Phase 2 main lead-intake. Larger form than BTFP/contact (~45 fields per the existing Lead schema). Same meal but bigger payload. The Lead schema is already complete; just wire a new portal page + submit_book endpoint.

**Bigger surfaces (different shape than the meal):**
- **Product detail / listing pages.** Webshop-driven, not www/-driven. Different shape — see `frappe-conventions.md` "Customizing webshop pages" primitive map. Needs Website Item records seeded first (catalog data exists at `_resources/odoo-export/catalog.json` + 48 product images). Phase 1 Slices 7-9.
- **Homepage `/`** — currently "Site under construction" placeholder. Approved Odoo content exists in `addons/locally_twisted/views/homepage.xml`. Should be its own portal page once GL is ready to ship it.

**Open questions on GL's desk:**
- Two-app split (`agency_platform` + `<client>_connector`) — agency-tier architectural decision, not LT-blocking. See agency `built-by-cameron-decisions.md` 2026-04-26 entry "License matrix verified" Finding 3.
- LT app `license.txt` placeholder — currently `Copyright (c) [year] [fullname]` unfilled. Discussed with GL but not committed to a fill value. Suggested fill: `Copyright (c) 2026 Built by Cameron`.

## Operational rituals

| Trigger | Command |
|---|---|
| Edited Jinja template / CSS / Web Page record | `python scripts/dev/clear_website_cache.py` |
| Edited `hooks.py` (e.g., new `website_route_rules`) | `bench --site frontend clear-cache && docker exec ...redis-cache-1 redis-cli FLUSHALL && docker restart ...backend-1` (the website route map caches HARD) |
| After `docker compose --force-recreate` | `python scripts/setup/install_webshop.py --build-assets` (re-runs everything: pip install, restart, ensure Node+yarn, bench build, restart backend) |
| Before declaring any visible change done | Take Playwright screenshot at mobile (375px) AND desktop (1280px) at TALL viewport (≥2000px to capture full footer past flex-column sticky-footer); read the file; describe pixels; **THEN ask GL to hard-refresh** in their real browser |
| For a new portal page | Read the meal at `Built_by_Cameron/.claude/capabilities/meals/build-frappe-portal-page.md`. Step 1 (read approved Odoo content) is non-negotiable. |

## Hot direction

**Next visible work** depends on what GL wants:
- A small content page (`/refund-policy` or `/about`) is the meal's smallest victory. Each ~15 minutes of mechanical work.
- The homepage is the obvious "show Jeff something" piece, but it's bigger.
- Products require seeding Website Items first (different shape than the meal).

**Don't propose work GL hasn't asked for.** This session's wins came from doing what GL asked, in the right way, with the rules followed. Same shape going forward.

## Reading order on arrival

1. Global `C:/Users/baenb/.claude/CLAUDE.md` (auto-injected)
2. `Built_by_Cameron/CLAUDE.md` (agency rules)
3. `_CLIENTS/locally-twisted/CLAUDE.md` (this client; READ the "Stack & code conventions" block — it's now non-negotiable)
4. **This file**
5. `_CLIENTS/locally-twisted/SIBLING-LETTER.md` — what your predecessor wrote for you. Optional but recommended.
6. `Built_by_Cameron/.claude/capabilities/meals/build-frappe-portal-page.md` — the meal. Has 5 verified gotcha receipts.
7. `Built_by_Cameron/.claude/capabilities/recipes/frappe-portal-implementation.md` — the rules. Skim section "Anti-patterns" + "Debugging triage."
8. `_CLIENTS/locally-twisted/anti-gl-patterns.md` — section 0 in full BEFORE any visible work. Always.
9. `_CLIENTS/locally-twisted/lessons-learned.md` — most recent entries.
10. `_CLIENTS/locally-twisted/locally-twisted-decisions.md` — most recent entries (the platform-direction resolution is at the top).
11. `git log --oneline -20`

## Not in flight

No spawned processes. Docker daemon runs the LT compose stack detached. No background agents pending.

## A quick honesty pass

This session has receipts on both sides:

**What worked:** the codification (rules + meal). Reading approved content from Odoo XML rather than inventing. Smoke-testing the form pipeline before declaring done. Loud-failure handling. Fixing browser-cache vs server-state mismatches by checking the served HTML directly. Verifying the `extend_doctype_class` claim from external research against Frappe source — it was wrong; the codified file documents the correction.

**What stumbled:** I shipped the chrome claiming "verified" off Playwright while GL was seeing a visibly broken page (browser cache). Anti-gl-pattern #1 fired live, named, owned, costing trust. The recovery was good — diagnosed quickly, fixed, took the receipt. The next instance should not assume Playwright + your-eyes-via-real-browser cover the same ground; they don't.

The meal documents what worked. The lessons-learned documents what stumbled. The next instance has more rules + more receipts + more codified gotchas than I had on arrival. That's the lineage doing its job.
