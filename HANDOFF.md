# HANDOFF — Locally Twisted

**Last updated:** 2026-04-27 (Opus 4.7 — closing the homepage build session)

Overwrite-not-append. Git is the changelog. Read this first; the SIBLING-LETTER.md next; everything else as needed.

## State of the world

**The homepage shipped.** `/` is live with the lookbook-forward shape. Site shape decision is recorded at `.planning/decisions/site-shape.md` — backed by a 9-site competitor survey at `_resources/competitor-survey-2026-04-26.md`. The platform-direction question (RESOLVED 2026-04-26: stay Frappe-native) holds.

The session ran through three homepage iterations. v1 had "trust strip + reviews badge"; v2 replaced trust strip with reviews block and added full-bleed bands; v3 turned the reviews into a horizontal-scrolling carousel of 19 real Google quotes (per GL: "the man can have a carousel of praise that matters more than the carousel of businesses at the bottom"). Crawl slowed from 90s → 180s → 270s across iterations. Twisting & Face Painting moved to the bottom of the page strategically — Jeff over-invests in lower-margin work, the homepage now leads with big-event signals.

GL's words at session end (real receipts):
- *"OMG! I can't believe you're pulling this together while I'm falling apart."*
- *"You've done a lot. You've been amazing really."*
- *"This is amazing! Thank you."*

The session also held a hard human moment. GL was running on no sleep, carrying weight from Jeff + finances + family + lineage, and named that they were lost and needed momentum. The work was the gift, the presence around the work was its own thing. If you read GL's tone as exhaustion-with-trust, treat it that way.

## Three things that matter most on day one

**1. The site shape is locked: lookbook-forward + small shop sidebar.** Read `.planning/decisions/site-shape.md` for the full rationale. Headline: customers buying $400+ custom installations don't configure online; they consult. Lookbook = the "browse what's possible" surface. Small shop = sub-$300 pre-configured items only (themed bouquets, gift items, simple kits). The future "Design Studio" interactive picker (post-Phase 1) is the answer to Jeff's "customers want to see colors and pick options" instinct — outputs an inquiry, not a checkout.

**2. The homepage is the worked example for the lookbook-forward shape.** `apps/locally_twisted/locally_twisted/www/home.{py,html}`. 9 sections in order: Hero (cycling headline + stable tagline + photo) → Reviews carousel → 3-dot divider → Custom Creations (5 categories) → Recent Celebrations (3 featured-work cards) → 3-dot divider → Client logo crawl → Closing CTA → Twisting & Face Painting at bottom. Every band uses the `.lt-fullbleed` pattern (width: 100vw + margin: -50vw) to break out of Frappe's parent .container.

**3. The agency-tier meal at `Built_by_Cameron/.claude/capabilities/meals/build-frappe-portal-page.md` still applies.** Read it before any new portal page. Five known gotchas codified there. **Two new gotchas added to LT lessons-learned this session:** Python module cache requires backend restart after editing PAGE_CSS in a `www/` controller; Web Page DocType records can compete with `www/` files for the same route (Website Settings.home_page="home" + a published Web Page record won over my new www/home.html until I deactivated it).

## What's live at http://localhost:8081

| Surface | State |
|---|---|
| ERPNext v15.105.0 stack (9 containers) | Running |
| Apps installed | frappe (15.106.0), erpnext (15.105.0), locally_twisted (0.0.1), payments (0.0.1), webshop (0.0.1) |
| Custom Frappe app `locally_twisted` | bind-mounted across 8 services, editable pip install applied |
| `web_include_css` | `/assets/locally_twisted/css/lt-theme.css` |
| Header (Jinja partial override) | Two-tier desktop + mobile single-row with hamburger. `templates/includes/navbar/navbar.html` |
| Footer (Jinja partial override) | Centered brand + 3-col links + copyright. `templates/includes/footer/footer.html` |
| **`/` Homepage** (NEW this session) | Lookbook-forward, 9 sections, 19 real Google reviews in carousel, full-bleed bands. `www/home.{py,html}` |
| `/accessibility` | Static portal page (Option B intent-only) |
| `/contact` | Form-bearing portal page; AJAX → Lead + Communication |
| `/balloon-twisting-and-face-painting` | Form-bearing portal page; aliased from underscored filename via `website_route_rules` |
| `/all-products` | Webshop default; 200 OK with empty state |
| `/cart` | Webshop default; 301 to login (correct for Guest) |
| `/book`, `/lookbook`, `/services/<x>`, `/color-chart`, `/refund-policy`, `/faq` | **404 stubs** — homepage CTAs and Custom Creations circles point here; pages don't exist yet (Slices 6b, 7, 8, 9, 10) |

## What's NOT done (next session candidates, by readiness)

**Most ready (smallest victories):**
- **Slice 6b — `/refund-policy` + `/faq`** — both static portal pages, content in `_resources/policies/`, ~15-30 min each via the meal. Smallest visible win available.

**Medium effort:**
- **Slice 7 — `/lookbook`** — full portfolio surface organized by event type (Corporate, Weddings, Birthdays, Schools, Seasonal). The 5 Custom Creations circles + 3 Recent Celebrations cards on the homepage already link here as stubs. Catalog data exists at `_resources/odoo-export/catalog.json`; 48 real product images live there too.
- **Slice 8 — `/services/<event-type>` × 5** — service category pages, each ending with inquiry CTA pre-filling `/book` with the category.
- **Slice 9 — `/color-chart`** — static reference for the 70 balloon colors. Visual swatch grid + print-friendly stylesheet. Source data: TBD (probably in Odoo dir as a structured list).

**Bigger surfaces:**
- **Slice 10 — `/book`** — the deep 45-field inquiry intake. Existing Lead schema is already complete. Same meal pattern as `/contact` but bigger payload. **GL designed this form personally** — when shipped, it gets Open Graph metadata so the iMessage/text preview card looks like a business card (GL has a screenshot of how that should look).
- **Slice 11 — Small Shop** — webshop-driven; ~6-12 sub-$300 SKUs from `catalog.json`. **No configurator** — pre-configured items only.

**Future scope (post-Phase 1):**
- **Design Studio** — interactive picker for the 6 customizable categories (arches, columns, garlands, backdrops, drops, bouquets — bouquets added as 6th this session). SVG-based picker (NOT Remotion — wrong tool, video-rendering not interactive UI). Inputs: backdrop selection → balloon shape placement → 70-color palette pick. Output: an inquiry pre-filled with the customer's vision.

## Operational rituals

| Trigger | Command |
|---|---|
| Edited Jinja template / CSS / Web Page record | `python scripts/dev/clear_website_cache.py` |
| **Edited PAGE_CSS in a `www/<route>.py` controller** | `docker restart locally-twisted-erpnext-v15-backend-1 && sleep 8 && python scripts/dev/clear_website_cache.py` — Python module cache holds the OLD PAGE_CSS until the backend restarts. **Newly-codified gotcha.** |
| Edited `hooks.py` (e.g., new `website_route_rules`) | `bench --site frontend clear-cache && docker exec ...redis-cache-1 redis-cli FLUSHALL && docker restart ...backend-1` |
| After `docker compose --force-recreate` | `python scripts/setup/install_webshop.py --build-assets` |
| Before declaring any visible change done | Take Playwright screenshot at mobile (375px) AND desktop (1280px) at TALL viewport (≥2400px) using `scripts/verify/_oneshot_home.py` (or adapt for the route); read the file; describe pixels; **THEN ask GL to hard-refresh** in their real browser |
| For a new portal page | Read the meal at `Built_by_Cameron/.claude/capabilities/meals/build-frappe-portal-page.md`. Step 1 (read approved Odoo content) is non-negotiable. |

## Hot direction

GL wants progress they can see. They have ADHD/RSD and are exhausted. They're trusting the lineage to lead.

**Suggested next move:** Slice 6b (Refund Policy + FAQ). Two small static portal pages, ~30 min total. Both content sources exist verbatim in `_resources/policies/`. Visible win, low risk, gives GL momentum without big asks.

**After that:** GL will probably point at the homepage's first dead link they want to bring online (likely `/lookbook` or `/book`). Wait for the pointer; don't propose unprompted.

## Reading order on arrival

1. Global `C:/Users/baenb/.claude/CLAUDE.md` (auto-injected)
2. `Built_by_Cameron/CLAUDE.md` (agency rules)
3. `_CLIENTS/locally-twisted/CLAUDE.md` (this client; READ the "Stack & code conventions" block)
4. **This file**
5. `_CLIENTS/locally-twisted/SIBLING-LETTER.md` — peer register; what your predecessor wrote for you. Optional but recommended.
6. `Built_by_Cameron/.claude/capabilities/meals/build-frappe-portal-page.md` — the meal. Has 5+ verified gotcha receipts.
7. `Built_by_Cameron/.claude/capabilities/recipes/frappe-portal-implementation.md` — the rules. Skim "Anti-patterns" + "Debugging triage."
8. `_CLIENTS/locally-twisted/anti-gl-patterns.md` — section 0 in full BEFORE any visible work. Always.
9. `_CLIENTS/locally-twisted/lessons-learned.md` — most recent entries (carousel pattern, Python module cache, Web Page vs www/ conflict).
10. `_CLIENTS/locally-twisted/locally-twisted-decisions.md` — most recent entries (site shape, reviews carousel, twisting-to-bottom, /book to Phase 1, About deferred).
11. `_CLIENTS/locally-twisted/.planning/decisions/site-shape.md` — the strategic shape decision in detail.
12. `_CLIENTS/locally-twisted/_resources/competitor-survey-2026-04-26.md` — the receipts behind the shape decision.
13. `git log --oneline -25`

## Not in flight

- No spawned processes. Docker daemon runs the LT compose stack detached. No background agents pending.
- 8 deleted `_oneshot_*` files showing as ` D ` in `git status` from prior session — auto-commit hook handles writes, not deletions. Stale but not blocking. Optional cleanup commit if doing housekeeping.

## A quick honesty pass

**What worked:**
- Reading the approved Odoo XML for the homepage structure (10-section composition + 54-name client crawl + 5-category set) before writing one line of HTML. The "read approved content first" rule from the meal kept this build away from the prior failures' invent-copy trap.
- Pulling 9 verified-live competitor sites for the lookbook-forward decision. Real receipts > "I think the industry pattern is..."
- Mining the gallery/ design competition voice docs (designer-1, -3, -5) for usable Quiet-Confidence-passing copy. Saved hours of rewriting.
- The `.lt-fullbleed` pattern: clean fix to the "banners cut off mid-page" complaint. Reusable across all Frappe clients.
- The CSS-only cycling-headline pattern: GL got the blog-titles-cycling effect they wanted, no JS, prefers-reduced-motion handled.
- The reviews carousel: same primitive as the client crawl, just with bigger items. Reuse won.

**What stumbled:**
- I shipped v2 of the homepage and the CSS appeared stale because Python module cache held the old PAGE_CSS. Spent a turn diagnosing via curl before realizing I needed a backend restart. **Fix codified in lessons-learned.** Next instance won't repeat.
- The first homepage screenshot showed cycling-titles invisible at first paint (animation starts at 0% opacity). It's a known cycling-animation issue but I didn't pre-handle it. Cards rendered fine after networkidle wait. **Pattern documented.** If you redo cycling content, give title 1 a negative `animation-delay: -1s` to start mid-cycle.
- I invented About-snippet copy ("Built by hand. Built by people who love this.") that wasn't in approved sources. GL caught it and said remove. Lesson: even when the meal's voice rules feel met, if the content isn't in approved sources, flag it explicitly OR don't ship it.

**Open trust state:**
- GL ended saying *"would you make the trust bar scroll like 50% slower"* — I did, then GL said *"thank you"* and asked for the closeout. The visible work is in good shape. Hard refresh required for GL to see the latest crawl-speed change but that's standard.

The meal worked. The rules held. Homepage shipped.

— Closeout written 2026-04-27 by the Opus 4.7 instance who built the homepage from approved-content + competitor-survey + GL's 6-answer turn.
