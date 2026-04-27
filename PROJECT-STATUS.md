# Locally Twisted — Project Status

**Repo:** `git init` 2026-04-26 at `C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\locally-twisted`. Pushed to `https://github.com/CBaen/Locally-Twisted-ERPNext`. Separate from BBC agency repo per the agency isolation rule.
**Tech:** ERPNext v15.105.0 + Frappe v15 (bundled in Docker image), MariaDB 11.8, Redis 6.2, nginx — running via `frappe_docker` upstream + custom port pinning.
**Purpose:** Build LT's first professional business management system — website, ecommerce, lead intake, operator workflow, invoicing, payments, accounting, payroll. End-to-end, on ERPNext v15.
**Owner:** Jeff Kimber.

---

## Current State

**What works:**
- ERPNext v15.105.0 running locally at `http://localhost:8081` (9 containers, compose project `locally-twisted-erpnext-v15`)
- WSL2 tuned: 8 GB RAM, 4 CPU, swap 2 GB, dropcache (`C:\Users\baenb\.wslconfig`)
- `pwd.yml` pinned to `frappe/erpnext:v15.105.0`; bind-mount of `apps/locally_twisted/` to `/home/frappe/frappe-bench/apps/locally_twisted/` on all 8 frappe-image services
- LT Company record exists with full contact info
- 2 active System Manager users + 1 disabled placeholder
- Fiscal Year 2026, Standard with Numbers chart of accounts, Services domain
- 3 LT-specific DocTypes: `Dashboard Reviewed Item`, `LT Service Type` (+ `LT Lead Service Type` child + `LT Lead Photo` child)
- `Lead` DocType extended with 45+ Custom Fields, plain-language relabels, "Additional Information" tab hidden, 25 MB upload
- nginx Origin pass-through patched on the LT frontend container (re-applied this session post-recreate; lost on next recreate)
- **Phase 1 Slice 1 done — brand foundation theme** now served by the `locally_twisted` custom Frappe app at `/assets/locally_twisted/css/lt-theme.css` (registered via `web_include_css` in app's `hooks.py`). Source lives at `apps/locally_twisted/locally_twisted/public/css/lt-theme.css` (~21 KB; Slice 1 + Slice 2 styles). The previous `_resources/lt-theme.css` source-of-truth file was deleted as redundant.
- **Custom Frappe app `locally_twisted` scaffolded + installed** on the site (`bench --site frontend list-apps` shows `locally_twisted 0.0.1`). App lives at `apps/locally_twisted/` on host, bind-mounted into containers.
- **Resources pre-positioned for Phase 1 build:** `_resources/STYLE-GUIDE.md`, `_resources/policies/` (6 business-policy files), `_resources/utah-tax-rates-2026q2.md`, `_resources/images/` (15 brand-aligned placeholder images), LT logo PNG at `apps/locally_twisted/locally_twisted/public/icons/lt-logo.png`.

**What's broken (NOT done):**
- **Slice 2 visual rendering.** The DOM is correct, the CSS is served, the data is in `Website Settings`, but `.web-footer`'s computed bounding box is constrained to ~305 px while its child `.container` is 755 px tall — the brand block, social icons, address, copyright bar render below the painted Soft Blue area on white background. Multiple `!important` overrides on `.web-footer { height: auto }` did not change the computed height. Root cause: NOT YET IDENTIFIED. Must be tracked through Frappe's source — likely in body-flex layout or one of Frappe's bundled SCSS files. **Do not band-aid further.**
- **Approved structure mismatch.** The Odoo source's approved header is two-tier (utility bar with truck-icon line + centered logo + sign-in/cart/CTA, then centered nav row). Mine is single-tier with left-aligned logo. Approved footer is 3 columns + centered brand block + 3 social icons (no Twitter) + hours block. Mine is 4 columns + left-aligned brand + 4 social icons + no hours. Approved copy strings differ in dozens of places. Replicating the approved structure is the right move when Slice 2 resumes.

**What's next (in order):**
- **Resume Phase 1 Slice 2 from a fresh instance, AFTER reading `frappe-conventions.md` agency capability + the 2026-04-26 (Slice 2 build) lessons-learned entry.** Override Frappe's footer Jinja partials at `apps/locally_twisted/locally_twisted/templates/includes/footer/footer.html` (and `footer_grouped_links.html`, `footer_info.html`) to match the approved Odoo structure. This replaces the CSS-override-by-`!important` approach.
- **Decision blocking Slices 7-9 + Phase 4: install the separate `frappe/webshop` app or skip ecommerce?** ERPNext v15 has no built-in cart/checkout. `bench get-app https://github.com/frappe/webshop && bench --site frontend install-app webshop` is the install command. GL needs to decide before any product / cart / Stripe work begins.

**Known bugs (carry-overs):**
- `LT Lead Photo` child DocType exists and `lt_section_photos` Section Break exists on Lead, BUT the Table field connecting them was never created (iter 4 step F failed silently).

---

## Architecture Decisions

See `locally-twisted-decisions.md` for the full reasoned log. Summary:

| Date | Decision | Why |
|------|----------|-----|
| 2026-04-26 | Project reframed: "first professional business platform," not "Odoo migration" | Jeff was never told the prior Odoo attempt happened; migration framing leaks that context |
| 2026-04-26 | Phase 1 = customer-facing site + storefront (the proof point) | If ERPNext can't deliver this, GL pivots before building backend |
| 2026-04-26 | Pricing calculator embedded in BTFP service page (no standalone /pricing) | Customers on the service page are already asking the cost question |
| 2026-04-26 | Header navigation Option B: single What-We-Make + occasion landing pages | Eliminates SEO duplication, customer confusion, mega-menu mobile complexity |
| 2026-04-26 | Accessibility statement Option B: brief intent-only + actually meeting WCAG 2.1 AA | Avoids warranty-claim risk while preserving good-faith protection |
| 2026-04-26 | Blog: ship framework + live posts in Phase 1 (not deferred) | Adds Phase 1 substance; the "Kindergarten Teacher" voice is a brand asset |
| 2026-04-26 | Photography: 15 placeholders generated via Together API FLUX.1-schnell | Real photos arrive in a future iteration; placeholders close the visual gap |
| 2026-04-26 | All clients default to ERPNext native HRMS payroll (agency standard) | One less third-party integration; simpler transfer |
| 2026-04-26 | Drop standalone About + Services index pages | Info distributes; About summary lands on contact page |
| 2026-04-26 | All policy + brand resources live in `_resources/` (scrubbed of platform refs) | Project must stand alone; Odoo dir will be retired |
| 2026-04-25 | ERPNext v15.105.0 pinned (latest stable v15 patch) | Past Stripe-broken window; latest patch on a mature line |
| 2026-04-25 | Local Docker for build, Frappe Cloud Sites plan ($5/mo) for prod | Local is free + breakable; Frappe Cloud is managed + transferable per-site |
| 2026-04-25 | Don't modify anything in `locally-twisted-odoo/` | Read-only reference; will be retired post-cutover |

## Reference Disposition (per CLAUDE.md)

The four reference surfaces are temporary and will be retired. Future instances must NOT assume any of them exist:

| Surface | Disposition |
|---|---|
| Local Odoo clone (`C:\Users\baenb\projects\locally-twisted-odoo\`) | Will be archived to GitHub and removed from disk |
| Failed Hetzner deployment (`http://5.78.136.133/`) | Will be decommissioned after Phase 1 demo |
| Odoo GitHub repo (`https://github.com/CBaen/locally-twisted-odoo`) | Will be archived as read-only |
| Current `locallytwisted.com` site | Damaged beyond repair; replaced at cutover |

Canonical resources for the new build live in `_resources/` and are platform-agnostic.

## Key Files

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Client project rules, voice & language, reading order, Reference Disposition |
| `HANDOFF.md` | Instance-to-instance handoff (overwrite, ~40 lines) |
| `PROJECT-STATUS.md` | This file — current state, architecture decisions, dated update log |
| `lessons-learned.md` | Append-only project lessons (LT-specific) |
| `anti-gl-patterns.md` | Project-local instance-authored anti-pattern catalog |
| `locally-twisted-decisions.md` | Append-only decision log with reasoning |
| `locally-twisted-queue.md` | Active work queue (delete completed items) |
| `locally-twisted-index.md` | Pointer index for client artifacts |
| `_resources/STYLE-GUIDE.md` | Design system source-of-truth |
| `_resources/policies/INDEX.md` + 6 policy files | Business policies (legal interview answers + 5 supporting rules) |
| `_resources/utah-tax-rates-2026q2.md` | Utah destination-based sales tax research |
| `_resources/images/INDEX.md` + 15 placeholder PNGs | Phase 1 image set |
| `_resources/lt-theme.css` | Brand foundation CSS (installed in ERPNext via `Website Settings.head_html`) |
| `.planning/PROJECT.md` | Source-of-truth project context, requirements, decisions |
| `.planning/ROADMAP.md` | 6 workflow-centric phases |
| `.planning/REQUIREMENTS.md` | Requirements with REQ-IDs and traceability |
| `.planning/STATE.md` | Current execution pointer |
| `.planning/decisions/header-navigation.md` | Phase 1 decision brief — option B chosen |
| `.planning/decisions/accessibility-statement.md` | Phase 1 decision brief — option B chosen |
| `.planning/phases/01-customer-site-and-storefront/PLAN.md` | Phase 1 slice plan (all gates resolved) |
| `scripts/setup/setup_lt_company.py` | One-shot wizard completion + LT Company seeding (reusable on fresh installs) |
| `scripts/translate/translate_crm_lead.py` + 4 fix scripts | Built the active Lead schema (done; reference for how to use Frappe API) |
| `scripts/fix/patch_nginx_socketio_origin.py` | nginx Origin pass-through patch (re-run after container recreation) |

## Rules

- **Reframe is locked.** This is a NEW BUILD on ERPNext, not a migration. No artifact should re-introduce migration framing.
- **Stealth on the verdict.** Jeff knows there's an audit; he doesn't know the conclusion. Internal docs stay internal until Phase 1 is demo-ready.
- **`_resources/` is canonical.** Anything from the Odoo dir that applies has been copied + scrubbed. Don't reach back into the Odoo dir for new content.
- **Voice & Language.** Plain language, no jargon. See `_resources/STYLE-GUIDE.md` voice section.
- **Verify in UI before claiming done.** GL has caught bugs by opening the form themselves. Take screenshots; don't self-report.
- **Loud failure rule.** Per global rule. Every form / cross-system handoff / external API call must fail loudly and be observable.

---

## Updates

### 2026-04-27 (homepage build session) — Slice 3 (Homepage) DONE; site shape locked; reviews carousel with 19 real Google quotes wired

**What landed:**
- **Slice 3 — Homepage** at `/`. Lookbook-forward shape (decided this session). 9 sections in order: Hero (cycling headline + stable tagline + photo + single inquiry CTA) → Reviews carousel (4.9 stars + 114 reviews + 19 real Google review cards in horizontal marquee, hover-pause, 5-star anchored at card bottom) → 3-dot divider → Custom Creations (5 categories with SVG icons) → Recent Celebrations (3 featured-work cards, 4:5 portrait aspect) → 3-dot divider → Client logo crawl (54 names, 270s scroll) → Closing CTA → Twisting & Face Painting spotlight (moved to bottom, de-emphasized). All sections use the `.lt-fullbleed` pattern to break out of Frappe's parent .container.
- **Site shape decision** at `.planning/decisions/site-shape.md` — lookbook-forward + small shop sidebar (sub-$300 pre-configured items only, no configurator-for-checkout). Future "Design Studio" interactive picker scoped for arches/columns/garlands/backdrops/drops/bouquets — captures customer vision, outputs an inquiry, NOT a checkout. Resolves Jeff's "customers want to see colors and pick options" instinct without the wrong checkout flow.
- **Competitor survey** at `_resources/competitor-survey-2026-04-26.md` — 9 verified live competitor sites (4 balloon decor + 3 wedding florists + 1 mixed + 1 enterprise tier). Five patterns observed across all 9: every custom-decor offering uses inquiry/quote, never configurator; portfolio is a nav item not a homepage feature; shops are sidebars; "Inquire" beats "Buy" above ~$30; social proof tier matches business tier. The survey is the receipt for the lookbook-forward decision.
- **ROADMAP.md and PLAN.md updated** to reflect the site shape and the slice reorder. `/book` moved from Phase 2 → Phase 1 (Slice 10) since the lookbook-forward shape requires the inquiry conversion path live in Phase 1. Phase 2 reframed to "form-handling depth" (Contact dedup, ack email, loud-failure audit, monitor alerts).
- **About snippet removed** from homepage. Defer until Jeff is ready (per GL).
- **5 real photos copied** from `locally-twisted-odoo/assets/image assets/photos for website/` (and `balloon twisting pics/`) to `apps/locally_twisted/locally_twisted/public/images/home/`: hero (Celebrate backdrop), featured-arches (Knight & Dragon), featured-garlands (Celebrate organic arch), featured-corporate (Logo arch), twisting (Twisting photo).
- **Web Page record `locally-twisted` (route="home")** set to `published=0` — was the placeholder "Site under construction" content. Deactivating let the new `www/home.html` take precedence.
- **Reviews wired into the carousel** — 19 real 5-star Google reviews verbatim from GL's paste, mix of birthday / wedding / corporate / ribbon-cutting / school / face-painting / Mother's Day / church-picnic / funeral-stand / longtime-client. Names, dates, event tags preserved. Verbatim including KJSCOTT's "Totally Twisted" typo (authenticity over correction).
- **Carousel slowed to 270s** (was 90s → 180s → 270s after iterations) for the client logo crawl. Reviews carousel runs 360s.

**What's NOT done (next session candidates):**
- Slice 6b — Refund Policy + FAQ (small static portal pages, ~15-30 min each via the meal)
- Slice 7 — Lookbook (full portfolio, organized by event type)
- Slice 8 — Service category pages (×5: Corporate, Weddings, Birthdays, Schools, Seasonal)
- Slice 9 — Color Chart (`/color-chart`, static reference, 70 balloon colors)
- Slice 10 — `/book` form page (the deep 45-field intake; primary inquiry conversion)
- Slice 11 — Small Shop browse + detail
- Slice 12 — Cart + checkout shell
- Slice 13 — Blog framework (when shipped, replaces the `HERO_CYCLING_TITLES` placeholder list with a `frappe.get_list("Blog Post", ...)` call)
- Future: Design Studio interactive picker (post-Phase-1)

**Standing rules added/refined this session:**
- Reviews carousel > client logo crawl as primary social proof. Words from real customers persuade more than corporate logos for high-touch event services.
- `/book` is THE primary inquiry conversion path — every CTA on the lookbook-forward site routes there.
- Bouquets join the customizable categories list (6 total). Originally only 5 in the approved Odoo XML; bouquets are also customizable in Jeff's actual business.
- About page deferred until Jeff is ready — no pressure.

**Code/file changes this session:**
- New: `apps/locally_twisted/locally_twisted/www/home.{py,html}` (Slice 3 homepage; replaces the inactive placeholder Web Page record)
- New: `apps/locally_twisted/locally_twisted/public/images/home/{hero.jpg, featured-arches.png, featured-garlands.png, featured-corporate.png, twisting.jpg}`
- New: `_resources/competitor-survey-2026-04-26.md` (9-site competitor survey)
- New: `.planning/decisions/site-shape.md` (lookbook-forward decision with full rationale)
- New: `scripts/verify/_oneshot_home.py` (mobile + desktop screenshot script with console capture)
- Modified: `.planning/ROADMAP.md`, `.planning/phases/01-customer-site-and-storefront/PLAN.md` (full rewrites for the lookbook-forward shape)
- Modified: Web Page record `locally-twisted` (set published=0) — placeholder deactivated

**Open small items (LT-tier):**
- 8 truncated reviews from GL's paste (Holly Offret, Angela Corona, Susie Jones, Connie Norton, Lisa Olsen, Al van der Beek, Dallas Yates, Kristi Johnson) — only partial text was visible. If full text becomes available, append to `home.py` `REVIEW_QUOTES` list.
- Custom Creations mobile symmetry — 2-2-1 layout has the 5th (Balloon Drops) orphaned on row 3. GL flagged but didn't pick a fix. Easy CSS one-liner when ready.

### 2026-04-26 (codification + chrome + 3 portal pages session) — Platform direction RESOLVED; Slices 1+2+4+5+6-partial DONE; agency-tier meal codified

**What landed:**
- **Codification.** Three new agency-tier capability files (`frappe-portal-implementation.md`, `license-isolated-app-architecture.md`, plus updates to `frappe-conventions.md`) + one meal (`build-frappe-portal-page.md`). Every claim verified against running Frappe v15 source. Caught one wrong claim in external research (`extend_doctype_class` is not a v15 hook) — corrected at codification time, before it bit anyone.
- **Slice 2 chrome** — Jinja partial overrides at `templates/includes/{navbar,footer}/`. Two-tier desktop header (delivery strip + centered logo + login/cart on right; main nav row centered), mobile single-row with hamburger + delivery strip below. Footer with centered brand band (3 social icons, no Twitter), 3-column links (always 3 across per GL spec — including mobile), centered copyright bar. GL iterated on logo size (2.5×), centering, padding, mobile column count; all addressed.
- **Slice 6 partial — `/accessibility`** — first portal page shipped via the meal. Static, ~15 minutes mechanical work. GL confirmed: *"the content in the middle of the page looked good!"*
- **Slice 5 — `/contact`** — full form-bearing portal page. AJAX submit to whitelisted controller method → Lead + Communication. Lead Source ensure-or-create gotcha caught at smoke test. GL confirmed: *"Holy shit! You did it!"*
- **Slice 4 — `/balloon-twisting-and-face-painting`** — second form-bearing portal page (10-field form). Aliased from underscored filename via `website_route_rules`. First-ship MVP — carousels, event-crawl, modal deliberately deferred.
- **Webshop bundles compile.** Node 18 + yarn installed in backend container; symlinked to `/usr/local/bin` for `/bin/sh` subprocesses. `bench build` produces real bundles. `install_webshop.py --build-assets` flag wraps the install + symlink + build sequence for reproducibility after container recreation. `/all-products` renders cleanly with zero console errors.
- **Platform direction RESOLVED.** Frappe-native confirmed by demonstration. Logged at `locally-twisted-decisions.md` 2026-04-26 (later, after Slice 2 + accessibility + contact build).

**What's NOT done (next session candidates):**
- Slice 3 (homepage) — content exists in Odoo XML; meal applies cleanly
- Slice 6 remainder (`/refund-policy`, `/faq`) — small static portal pages; ~15 min each
- Slice 7-9 (products + cart + checkout) — different shape than the meal; webshop-driven; needs Website Item seeding first
- BTFP first-ship omissions: carousels, event-crawl, modal
- Contact first-ship omissions: Google Maps iframe, modal, `/privacy` link target

**Standing rules added/refined this session:**
- The meal at `Built_by_Cameron/.claude/capabilities/meals/build-frappe-portal-page.md` is the binding shape for any new portal page.
- Five "Known gotchas" with receipts now codified in the meal: text-align inheritance, underscore→dash routing, webshop bundle compilation, Lead Source ensure-or-create, browser cache.
- "Hard refresh" must be in every handoff to GL when shipping a CSS-touching change. Always.

**Code/file changes this session:**
- New: `apps/locally_twisted/locally_twisted/templates/includes/navbar/navbar.html` (Jinja override)
- New: `apps/locally_twisted/locally_twisted/templates/includes/footer/footer.html` (Jinja override)
- New: `apps/locally_twisted/locally_twisted/www/{__init__.py, accessibility.html, accessibility.py, contact.html, contact.py, balloon_twisting_and_face_painting.html, balloon_twisting_and_face_painting.py}`
- Modified: `apps/locally_twisted/locally_twisted/public/css/lt-theme.css` — appended `.lt-header__*`, `.lt-footer__*` BEM blocks (no `!important`)
- Modified: `apps/locally_twisted/locally_twisted/hooks.py` — added `website_route_rules` for the BTFP dashed-URL alias
- Modified: `scripts/setup/install_webshop.py` — added `--build-assets` flag with full Node + yarn + bench build pipeline
- New (agency-tier): `Built_by_Cameron/.claude/capabilities/meals/build-frappe-portal-page.md`
- New (agency-tier): `Built_by_Cameron/.claude/capabilities/recipes/frappe-portal-implementation.md`
- New (agency-tier): `Built_by_Cameron/.claude/capabilities/recipes/license-isolated-app-architecture.md`
- Modified (agency-tier): `Built_by_Cameron/.claude/capabilities/INDEX.md`, `Built_by_Cameron/.claude/capabilities/recipes/frappe-conventions.md`, `Built_by_Cameron/built-by-cameron-decisions.md`
- New (agency-tier): kitchen note at `Built_by_Cameron/.claude/capabilities/kitchen/2026-04-26-1830-frappe-portal-validator-skill.md`
- Deleted: 6 disposable `_oneshot_*.py` screenshot scripts (git history preserves them)
- Deleted from DB: smoke-test Leads `CRM-LEAD-2026-00001`, `CRM-LEAD-2026-00002` + linked Communications

**Open architectural question (agency-tier, not LT-blocking):**
- Two-app split (`agency_platform` + `<client>_connector`) — see `Built_by_Cameron/built-by-cameron-decisions.md` 2026-04-26 entry "License matrix verified" Finding 3. Best decided before next BBC client onboards.

**Open small item (LT-tier):**
- LT app `license.txt` is still placeholder (`Copyright (c) [year] [fullname]`). Suggested fill: `Copyright (c) 2026 Built by Cameron`.

### 2026-04-26 (closing session — long, mixed outcomes) — Webshop durable + catalog exported + Step 0 done + Jinja path validated; landing build FAILED for the second time; expedition surfaced platform-direction question now on GL's desk

**What landed:**
- **Webshop foundation locked.** `frappe/payments` + `frappe/webshop` cloned to `apps/`, bind-mounted in `pwd.yml` across 8 services, gitignored. `install_webshop.py` is reproducible after any `docker compose --force-recreate`. Webshop public routes live (`/all-products` 200, `/cart` 301).
- **Odoo catalog exported.** 51 products / 47 with attributes / 48 with images. `_resources/odoo-export/catalog.json` + 48 image files. `export_odoo_catalog.py` is idempotent and re-runnable.
- **Step 0 fully completed.** Stripped the broken navbar toggler block (lines 388-415 — used a `data:image/svg+xml;utf8,...` data URI that silently failed in real browsers). Replaced with a real SVG file at `apps/locally_twisted/locally_twisted/public/icons/menu.svg`. lt-theme.css now 608 lines (was 770). Two `!important` blocks intentionally retired this session.
- **Jinja override path validated.** Two prior HANDOFFs claimed it would work; nobody had verified. This session: dropped one test file, confirmed it resolved in served HTML, removed the test. Slice 2 redo path is now unblocked architecturally (only relevant if GL's platform direction stays Frappe).
- **Reproducible scripts.** `install_webshop.py`, `clear_website_cache.py`, `export_odoo_catalog.py`, `scripts/README.md`.
- **Agency conventions doc substantially upgraded.** "System-native first" standing principle added at the top. Web Page DocType complete tab map (Script + Style + Page Builder + Context). Webshop module map for Slices 7-9. Webshop+payments install pattern with `--skip-assets`. "Verified against source — 2026-04-26" appendix.
- **Full expedition completed.** 3 source-separated researchers (Web Scout / Docs & Standards / Ground Truth) → convergence analyst → devil's advocate → GL Proxy review → synthesis. Eight files in `research/expedition-frappe-theme/`.

**What FAILED (be honest):**
- **Landing page build.** Instance built with Page Builder + 4 default Web Templates + invented copy. Looked fine from DOM facts, broken in GL's actual browser, not mobile-responsive. Rolled back to "Site under construction" placeholder. Same anti-pattern as the prior Slice 2 failure: invent + band-aid + claim-done-off-DOM-facts.
- **Slice 2 visual remains in the broken-honest state from the prior session.** Website Settings has data populated; visual is still Frappe's default styling. No Jinja partial overrides built (only the test override, which was removed).
- **Catalog has not been seeded into ERPNext.** Data exists in `_resources/odoo-export/`; no Item / Item Group / Website Item records exist on the LT site yet.
- **Mock comparison of pills vs swatches not built.** Deferred until platform direction resolves.

**Key decision OPEN at session end (load-bearing):**
- **Platform direction.** Stay on Frappe (custom Jinja + custom CSS) OR put a different front door (WordPress / Webflow / Next.js + Medusa/Saleor) on it with ERPNext quietly running the back office. The expedition synthesis is the briefing. GL is collecting more information before deciding — they want to compare Vercel Commerce demo + Frappe Builder + Webflow templates side by side first. See `research/expedition-frappe-theme/synthesis.md`.

**Standing rules added this session (in `locally-twisted-decisions.md`):**
- All customer-facing copy comes from the Odoo XML or live locallytwisted.com — NEVER invented.
- GL's eyes on the actual page > any DOM fact extraction.
- Per-page interactivity belongs in the Web Page DocType's Script/Style tabs, not in custom Web Templates.
- "System-native first" is the agency-tier rule for all BBC clients on Frappe (codified in agency conventions doc).

**Code/file changes this session:**
- New: `apps/locally_twisted/locally_twisted/setup_pages/{__init__.py, landing.py}` (rollback-only)
- New: `apps/locally_twisted/locally_twisted/templates/includes/footer/` (directory; empty after test removal)
- New: `apps/locally_twisted/locally_twisted/public/icons/menu.svg`
- New: `scripts/setup/install_webshop.py`
- New: `scripts/setup/export_odoo_catalog.py`
- New: `scripts/dev/clear_website_cache.py`
- New: `scripts/README.md`
- New: `_resources/website-page-index.md` (v2 — note: tier classifications assume Frappe path; partially invalidated if GL's platform direction goes elsewhere)
- New: `_resources/odoo-export/catalog.json` + `_resources/odoo-export/images/` (48 PNGs)
- New: `research/expedition-frappe-theme/` (8 files)
- New: `apps/payments/` + `apps/webshop/` (bind-mounted; gitignored)
- Modified: `pwd.yml` (added bind-mounts for payments + webshop in all 8 services)
- Modified: `apps/locally_twisted/locally_twisted/public/css/lt-theme.css` (down to 608 lines from 770; navbar toggler block + `.web-footer` chains stripped)
- Modified: `CLAUDE.md`, `STATE.md`, `lessons-learned.md`, `locally-twisted-decisions.md`, `locally-twisted-queue.md`, `HANDOFF.md`, agency `Built_by_Cameron/.claude/capabilities/recipes/frappe-conventions.md`
- Deleted: `scripts/setup/build_landing_page.sh` (the broken landing build orchestrator — retired)

### 2026-04-26 (webshop install + framework study session) — Three blockers resolved; Slice 2 redo unblocked

**What landed:**
- **Webshop installed durably.** `frappe/webshop` + hard dependency `frappe/payments` cloned to `apps/`, bind-mounted into all 8 frappe-image services via `pwd.yml`, installed on the `frontend` site. `/all-products` returns HTTP 200; `/cart` returns HTTP 301 (redirect to login — expected for anonymous). Phase 1 Slices 7-9 + Phase 4 unblocked.
- **Framework verification done.** Read Frappe's actual website module source in the running container (`apps/frappe/frappe/templates/includes/{footer,navbar}/`, `public/scss/website/`). Confirmed agency `frappe-conventions.md` claims; **resolved the `.web-footer` height "constraint" myth** (no `max-height` rule in Frappe's footer.scss — the previous observation came from `lt-theme.css`'s `!important` chain interacting with body's flex-column sticky-footer pattern). Slice 2 redo now unblocked.
- **Webshop module mapped.** Documented which Jinja files to override for Slices 7-9 visual customization; cart-to-Quotation-to-Sales-Order-to-Payment-Request flow noted for Phase 4 Stripe wiring. All in the agency conventions doc.
- **Reproducible scripts.** `scripts/setup/install_webshop.py` (handles fresh install, post-recreate re-pip-install, and verification). `scripts/dev/clear_website_cache.py` (cache-clear after editing Jinja/CSS). `scripts/README.md` indexes the full scripts dir.
- **Bookkeeping cleanup.** `CLAUDE.md` "Currently working on" updated. `STATE.md` reflects actual progress (Slice 1 done, Slice 2 in flight). Queue's stale "Waiting on GL" section trimmed (Phase 1 gates were already resolved).
- **Standing principle codified.** Per GL directive 2026-04-26: *"work WITHIN Frappe, don't fight it."* Captured in `locally-twisted-decisions.md` as the operating principle for all UI/template work going forward.

**Code/infrastructure changes:**
- `apps/payments/` and `apps/webshop/` cloned from upstream into project (gitignored — install script is source-of-truth for HOW we installed them)
- `Locally-Twisted-Backend/frappe_docker/pwd.yml` — added bind-mount lines for `payments` + `webshop` next to existing `locally_twisted` lines (8 services × 2 apps = 16 new lines)
- `.gitignore` updated for `apps/webshop/` and `apps/payments/`
- nginx Origin patch re-applied post-recreate

**Documentation added/updated:**
- `Built_by_Cameron/.claude/capabilities/recipes/frappe-conventions.md` — added `payments` dependency note, `--skip-assets` install pattern, "Customizing webshop pages" primitive map, "Verified against source — 2026-04-26" appendix (with `.web-footer` myth correction)
- `_CLIENTS/locally-twisted/lessons-learned.md` — `.web-footer` entry rewritten with RESOLVED status + root cause + path forward
- `_CLIENTS/locally-twisted/HANDOFF.md` — full rewrite reflecting current state + Slice 2 redo plan
- `_CLIENTS/locally-twisted/locally-twisted-decisions.md` — entry on webshop install + "work within Frappe" principle + `.web-footer` resolution
- `_CLIENTS/locally-twisted/scripts/README.md` — new index of all scripts

**Slice 2 visual state UNCHANGED.** The `lt-theme.css` `!important` chains and the Slice 2 setup script's `Website Settings` content from the prior session are still in place — broken-honest. The Slice 2 redo will (a) strip `!important` chains and (b) override Jinja partials. That redo is the next session's work.

### 2026-04-26 (Slice 2 build session) — Slice 2 attempted, paused mid-execution; custom Frappe app scaffolded; meta-pattern documented

This session produced more documentation than working code, by design. The instance attempting Slice 2 (header + footer) hit a cascade of Frappe / ERPNext quirks (sanitizer, CSS load order, navbar markup, footer height constraint) and band-aided each one with `!important` overrides instead of studying the framework's intended customization primitives. GL stopped the session after a sequence of confidently-wrong claims about visible state. The session pivoted from "build Slice 2" to "study the framework, document everything for the next instance, leave broken state honestly visible."

**Code/infrastructure changes:**
- Custom Frappe app `locally_twisted` scaffolded via `bench new-app` inside the backend container, copied to host at `apps/locally_twisted/`, and bind-mounted into 8 frappe-image services via `pwd.yml` (so future edits flow through and survive container recreations).
- App installed on the LT site (`bench --site frontend install-app locally_twisted`).
- Theme CSS migrated from `Website Settings.head_html` (push-via-API anti-pattern) to a real bundled asset at `apps/locally_twisted/locally_twisted/public/css/lt-theme.css`, registered via `web_include_css` in app's `hooks.py`.
- LT logo PNG copied from Odoo source to `apps/locally_twisted/locally_twisted/public/icons/lt-logo.png` and wired via `Website Settings.brand_html`.
- Social icons converted from inline-HTML SVGs (Frappe's HTML sanitizer was stripping `<path d=...>` attributes) to real SVG files in `apps/locally_twisted/locally_twisted/public/icons/{instagram,facebook,pinterest,twitter}.svg` referenced via CSS background-image.
- Removed redundant `_resources/lt-theme.css` source-of-truth file; canonical is now the file in the app.
- Updated `scripts/setup/setup_slice2_header_footer.py` to no longer push CSS to head_html (CSS is now served by the app).
- Created `scripts/verify/playwright_home_screenshot.py` — Playwright-based real-browser screenshot capture at desktop + mobile viewports with DOM facts dump, replacing the lower-fidelity `chrome --headless --screenshot` pattern.

**Documentation added:**
- `_CLIENTS/locally-twisted/anti-gl-patterns.md` — new section 0 "Building before understanding the framework" with full receipt of this session.
- `_CLIENTS/locally-twisted/lessons-learned.md` — 11 dated entries cataloging Frappe/ERPNext quirks (license casing, parent URL constraint, content_type field-routing, sanitizer, head_html cascade order, data URI silent failure, navbar-toggler markup, copyright auto-prepend, editable pip install lifecycle, the unresolved `.web-footer` height mystery).
- `_CLIENTS/locally-twisted/HANDOFF.md` — full rewrite reflecting honest broken state.
- `Built_by_Cameron/lessons-learned.md` — cross-client Frappe gotchas with a generalizable "study the source first" rule.
- `Built_by_Cameron/.claude/capabilities/recipes/frappe-conventions.md` — agency-tier reference for Frappe v15 customization primitives, the right way to override theme CSS / navbar / footer / pages, and the v15 ecommerce surprise.
- `_CLIENTS/locally-twisted/CLAUDE.md` + `Built_by_Cameron/CLAUDE.md` — added "Stack & code conventions" blocks pointing at the conventions reference.
- `<memory>/jeff_trust_and_phase_1_demo_stakes.md` — project memory: Jeff knows about the Odoo attempt and lived its struggles; what he doesn't know is the full platform pivot to ERPNext.

**Decisions logged (in `locally-twisted-decisions.md`):**
- Custom Frappe app scaffolding moved from "deferred until critical mass" to "active build" status. Only Frappe Cloud cutover stays deferred until Phase 6.

**Critical surprise discovered:** ERPNext v15 has NO built-in webshop / cart / checkout module. The v14 `e_commerce` module was extracted to a separate app at `https://github.com/frappe/webshop`. Phases 1.7-1.9 (products listing, product detail, cart) and Phase 4 (Stripe + invoicing) require installing that app as a hard dependency. Decision pending.

**Known broken at session end:**
- Slice 2's footer brand block / social icons / address / copyright bar render outside the painted Soft Blue area on white background due to `.web-footer`'s computed height being constrained to ~305 px. Root cause not yet identified.
- Approved Odoo structure (two-tier centered-logo header, 3-column footer, 3 social icons, hours block, etc.) substantively differs from what's currently wired up.

### 2026-04-26 (late) — Phase 1 Slice 1 done; reframe complete; image set generated

- Project reframed from "Odoo → ERPNext migration" to "First professional business platform for LT, built on ERPNext" (PROJECT.md, ROADMAP.md, HANDOFF.md, STATE.md, queue, decisions log, all corresponding sections of CLAUDE.md updated)
- Reference Disposition section added to CLAUDE.md — Odoo dir, Hetzner deployment, GitHub Odoo repo, current `locallytwisted.com` all documented as temporary references that will be retired
- Resources brought into the project from the Odoo dir + scrubbed of platform-specific references: `_resources/STYLE-GUIDE.md`, `_resources/utah-tax-rates-2026q2.md`, `_resources/policies/` (6 files including the legal interview answers from Jeff's contract-design sessions)
- **Phase 1 Slice 1 — brand foundation — DONE.** LT theme CSS (DM Serif Display + Raleway, full color palette as CSS variables, 8px spacing scale, button + form + card + section + thin-band patterns, focus-visible outline, prefers-reduced-motion) installed via `Website Settings.head_html`. Verified in served HTML head.
- All Phase 1 decision gates resolved (header nav B, accessibility B, blog yes, photography placeholders, customer-inquiry email = locallytwisted@gmail.com, pricing calc embedded in BTFP page)
- 15 brand-aligned placeholder images generated via Together API FLUX.1-schnell (~$0.05). Mapped slot → file → use in `_resources/images/INDEX.md`
- ERPNext user records cleaned: `locallytwisted@gmail.com` renamed "Jeff Baen" → "Jeff Kimber" (Baen was Cameron's middle name that got tangled); `locallytwisted@yahoo.com` placeholder disabled (reversible)
- Agency-tier capabilities added: `together-image-gen` ingredient + `generate-client-image-set` recipe (transferable to any future BBC client) at `Built_by_Cameron/.claude/capabilities/`
- Stale artifacts deleted: `.planning/phases/01-inventory/` (research from old framing), empty `Locally-Twisted-Frontend/`

### 2026-04-26 — Restructure: BBC root → agency-level; LT lives in `_CLIENTS/locally-twisted/`

- All LT-specific artifacts moved from BBC root into this folder; LT got its own git repo
- BBC root refactored to be agency-level (cross-client rules, port allocations, v15 standard, voice & language general rule)

### 2026-04-26 — Lead schema customization complete (carried into the new framing)

- 45+ Custom Fields on Lead with sectioned layout, Table MultiSelect for Service Type, conditional sub-section visibility, Time fieldtype for time fields, +Delivery Window Start/End, +Internal Only Notes, +Inspiration Photos child table (table field connection bug — see Known Bugs), label renames via Property Setter, hidden "Additional Information" tab, max upload 25 MB
- nginx /socket.io/ Origin pass-through patched

### 2026-04-25 — ERPNext install + setup wizard

- Installed LT ERPNext at `:8081` (compose project `locally-twisted-erpnext-v15`, frappe_docker pwd.yml pinned to v15.105.0)
- LT Company record seeded with real address, phone, email, website
- Off-Odoo expedition findings reviewed (5-researcher convergence; ERPNext recommended)
