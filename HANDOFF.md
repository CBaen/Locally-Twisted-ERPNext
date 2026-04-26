# HANDOFF — Locally Twisted (First Professional Business Platform)

**Last updated:** 2026-04-26 (Opus 4.7 — closing the long session that ran webshop install + framework verify + Odoo catalog export + failed landing build + full expedition)

Overwrite-not-append. Git is the changelog.

## Read this first — three things matter most

**1. The platform-direction question is OPEN, on GL's desk.** Two LT homepage builds have failed in two consecutive sessions. The expedition this session surfaced that the entire premise — "build the customer-facing site inside Frappe" — was never deliberately chosen by GL; it was just the inherited assumption. GL is now considering: stay on Frappe + custom Jinja, OR put a different front door (WordPress / Webflow / Next.js + Medusa/Saleor) on it with ERPNext quietly running the back office. **Do not assume Frappe is the answer when you arrive.** Read the expedition synthesis first: `research/expedition-frappe-theme/synthesis.md`. GL's last words at session end: *"I think I have to move forward with these bigger decisions with the next instance."*

**2. The approved Jeff content was sitting on disk the whole time.** Every previous instance invented placeholder copy when the actual Jeff-approved copy lived in `C:/Users/baenb/projects/locally-twisted-odoo/addons/locally_twisted/views/`. Hero is "Utah's Balloon Specialists." Tagline is "Making celebrations unforgettable since 1998." CTA section is "Make Your Celebration Unforgettable" + "From birthdays to weddings, baby showers to corporate events — we've been part of Utah celebrations since 1998. Yours is next." All verbatim. Captured in detail in `research/expedition-frappe-theme/ground-truth-findings.md` and `research/expedition-frappe-theme/synthesis.md`. **Do not invent copy.** The Web Scout also pulled current customer-facing content from locallytwisted.com (the WordPress site Jeff still uses) — both sources exist, GL has not yet picked which is "the" approved version.

**3. GL's eyes on the actual page > any DOM fact you can extract.** The biggest mistake this session was declaring a landing page "tier 1 native" and "rendered correctly" off DOM facts (curl showed all the HTML; Playwright captured a screenshot showing the hero) when GL opened the page in their actual browser and saw broken-on-mobile, content-not-visible. **Verify with GL's eyes, not assertions.** Mandatory per `anti-gl-patterns.md` section 0. The previous instance's rollback function lives at `apps/locally_twisted/locally_twisted/setup_pages/landing.py` (`bench --site frontend execute locally_twisted.setup_pages.landing.rollback`).

## What was done this session (deliveries that survived)

**Webshop installed durably.** `frappe/payments` + `frappe/webshop` cloned to `apps/`, bind-mounted into all 8 frappe-image services via `pwd.yml`, gitignored at the project. Reproducible via `python scripts/setup/install_webshop.py`. Public routes live: `/all-products` 200, `/shop-by-category` 200, `/cart` 301 (redirects to login when no customer session). Phase 1 Slices 7-9 + Phase 4 unblocked at the install layer.

**Framework verified against actual source.** Read Frappe's website module in the running container. Confirmed agency `frappe-conventions.md` claims; **resolved the `.web-footer` height "constraint" myth** (no `max-height` rule in Frappe's `footer.scss` — the previous observation came from `lt-theme.css`'s own `!important` chain interacting with body's flex sticky-footer pattern). The full conventions doc at `Built_by_Cameron/.claude/capabilities/recipes/frappe-conventions.md` was substantially updated with: Web Page DocType complete tab map (Script + Style + Page Builder + Context tabs that prior instances missed), webshop module map for Slices 7-9, webshop+payments install pattern (with `--skip-assets` for missing Node), and "System-native first" standing principle at the top.

**Odoo catalog exported.** 51 products from the live Odoo at `http://5.78.136.133/` — 47 with attributes, 48 with image URLs. All in `_resources/odoo-export/catalog.json` + 48 product images downloaded to `_resources/odoo-export/images/`. Exporter at `scripts/setup/export_odoo_catalog.py`. The Hetzner Odoo IS reachable via `curl` (HTTP 200 on product images); Web Scout's WebFetch tool just doesn't handle raw IPs (known issue per LT lessons-learned).

**Reproducible scripts.** New scripts this session:
- `scripts/setup/install_webshop.py` — fresh install OR post-recreate re-pip-install of all 3 apps (locally_twisted + payments + webshop) in 4 services
- `scripts/dev/clear_website_cache.py` — clear after editing Jinja/CSS
- `scripts/setup/export_odoo_catalog.py` — Odoo HTML scraper, idempotent
- `scripts/README.md` — full index with run-when guidance

**Step 0 (the !important strip) finally completed properly.** The session-prior partial strip removed the `.web-footer` block. This session's full pass also fixed the broken navbar toggler at lines 388-415 (was a `data:image/svg+xml;utf8,...` data URI that silently failed in real browsers — replaced with a real SVG file at `apps/locally_twisted/locally_twisted/public/icons/menu.svg` referenced via plain `background-image: url(...)`). Theme CSS now 608 lines (down from 770 originally; some `!important` remain in inactive sections — flagged below).

**Jinja override path validated in our Docker setup.** The HANDOFF claimed for two sessions that "override Jinja partials" was the path forward, but nobody had verified the override actually resolved in our specific bind-mounted bench setup. This session: dropped a minimal `apps/locally_twisted/locally_twisted/templates/includes/footer/footer.html` with a test string, cleared cache, confirmed it appeared in served HTML, removed the test file. The architecture works. Slice 2 redo path is unblocked — but only relevant if GL's platform direction stays Frappe.

**Full expedition completed.** Three source-separated researchers (Web Scout / Docs & Standards / Ground Truth) → convergence analyst → devil's advocate → GL Proxy review → synthesis. Eight files in `research/expedition-frappe-theme/`. The synthesis is the briefing for the platform-direction question.

## What was NOT accomplished (be honest)

- **No visible customer-facing page exists.** The homepage is the "Site under construction" placeholder (rolled back from the broken landing build).
- **Slice 2 (header + footer) is still in the broken-honest state from the prior session.** Website Settings has `top_bar_items` + `footer_items` data populated, but the visual is still Frappe's default styling. The Jinja partial overrides have NOT been built yet (only the test override was done, then removed).
- **Catalog has not been seeded into ERPNext.** The 51 products + 48 images live in `_resources/odoo-export/` as data, but no Item / Item Group / Website Item records exist on the LT site yet.
- **Mock comparison of pills vs swatches not built.** Was queued; deferred until platform direction resolves.
- **Phase 1 deliverables 1-9: zero shipped.**

## Live state of the LT site at `http://localhost:8081`

| Surface | Status |
|---|---|
| ERPNext v15.105.0 stack | Running. 9 containers. Recreated 2x this session — `pwd.yml` change for webshop bind-mounts, then app reinstalls survived. |
| Apps installed on site | `frappe`, `erpnext`, `locally_twisted` (0.0.1), `payments` (0.0.1), `webshop` (0.0.1) |
| Apps bind-mounted in pwd.yml | `locally_twisted`, `payments`, `webshop` — all 8 frappe-image services |
| Webshop public routes | `/all-products` 200, `/shop-by-category` 200, `/cart` 301 (expected) |
| Custom Frappe app `locally_twisted` | Editable pip install applied via `install_webshop.py`. `templates/` directory exists (created for the override test, kept; empty currently). `setup_pages/` module exists with `landing.py` (rollback-only — see below). |
| LT theme CSS | At `apps/locally_twisted/locally_twisted/public/css/lt-theme.css`, served at `/assets/locally_twisted/css/lt-theme.css`. 608 lines. Two `!important` blocks intentionally retired this session (navbar toggler + `.web-footer` chains). Some `!important` remain in inactive selector blocks (`.lt-footer-brand`, `.lt-footer-social*` etc. — these style elements that don't currently exist anywhere; harmless but worth deleting in a future cleanup pass). |
| menu.svg icon | At `apps/locally_twisted/locally_twisted/public/icons/menu.svg` — real SVG file replacing the broken data URI. Served at `/assets/locally_twisted/icons/menu.svg` (HTTP 200). |
| nginx Origin patch | Applied this session post-recreate. `Access-Control-Allow-Origin: http://localhost:8081` confirmed. |
| `Website Settings` content | Still populated by the prior session's `setup_slice2_header_footer.py` (top_bar_items, footer_items, brand_html, address, copyright, home_page). **Known issue:** that script populates 4 social icons including Twitter; approved Odoo XML says 3 (no Twitter). Documented in queue. |
| Home Web Page record | Web Page name=`locally-twisted`, route=`home`, content_type=Rich Text, body="Site under construction." Rolled back from a broken build attempt this session. |
| Catalog data | 51 products + 48 images at `_resources/odoo-export/`. Not yet imported into ERPNext. |
| Expedition findings | All 8 files at `research/expedition-frappe-theme/`. Synthesis is the briefing. |

## Known broken / known stale (DO NOT trust prior "rendered correctly" claims)

- **Slice 2 header + footer visual is Frappe's default**, not the LT design. Approved structure is captured in `research/expedition-frappe-theme/ground-truth-findings.md` (verbatim from Odoo XML).
- **`setup_slice2_header_footer.py` data has Twitter in the social icons row.** Approved Odoo XML has 3 icons (Facebook, Instagram, Pinterest — NO Twitter). Either fix the data or surface for GL to confirm. Documented in queue + decisions log this session.
- **`scripts/setup/build_landing_page.sh` was deleted this session.** It built the broken Page-Builder landing page; the approach is documented as failed in lessons-learned. The `landing.py` `rollback()` function in `setup_pages/` is the only useful piece left from that work.
- **`apps/locally_twisted/locally_twisted/templates/includes/footer/footer.html` does NOT exist** (the test file was removed after path-validation). This is intentional — the next instance creates the real one only if GL's platform direction is "stay on Frappe."

## Hot direction (load-bearing for next session)

**ABSOLUTELY MANDATORY first step:** Read `research/expedition-frappe-theme/synthesis.md`. Then confirm with GL the platform direction. Without that, every build path is the wrong path.

**If GL says "stay on Frappe":** the build sequence is in the synthesis. Summary:
1. Verify the Jinja override path one more time in case Docker state changed (one test file, see "What was done this session").
2. Override `apps/locally_twisted/locally_twisted/templates/includes/navbar/navbar.html` with two-tier centered-logo header per the approved Odoo XML structure.
3. Override `apps/locally_twisted/locally_twisted/templates/includes/footer/` partials with 3-column footer + hours block per Odoo XML.
4. Build the homepage at `apps/locally_twisted/locally_twisted/www/index.html` (Jinja static page) using the approved Odoo XML copy verbatim.
5. Build BTFP service page at `apps/locally_twisted/locally_twisted/www/balloon-twisting-and-face-painting.html` — calculator collapses to tier 1 via Web Page Script tab pattern (see decisions log entry 2026-04-26 "Web Page tabs finding").
6. Build contact page at `apps/locally_twisted/locally_twisted/www/contact.html` (form-to-Lead wiring is Phase 2).
7. Seed catalog into Item / Item Group / Website Item records using `_resources/odoo-export/catalog.json`.
8. After every Jinja edit: `python scripts/dev/clear_website_cache.py`.
9. After every visible change: `python scripts/verify/playwright_home_screenshot.py` AND have GL look at the actual page in their browser. Mandatory.

**If GL says "different front door":** scope changes substantially.
- ERPNext stays as the back office (Lead intake, invoicing, accounting, payroll).
- Customer-facing site moves to WordPress / Webflow / Next.js. The 51 product catalog + approved copy + photos all transfer to the new front-end.
- Webshop becomes optional or replaced by the new front-end's cart (Stripe-direct, Medusa.js, etc.).
- The custom Frappe app `locally_twisted` may stay (for Lead schema customizations) or be substantially trimmed.
- This is a real rewrite. Do not minimize.

**If GL is still deciding:** they wanted a comparison. Concrete cheap experiment they asked about: install Frappe Builder in our Docker stack (~20 min test), pull up Vercel Commerce demo URL, look at Webflow ecommerce template gallery — all three side by side. None of these have been done yet. If GL wants to proceed via comparison, set those up.

## Operational rituals (unchanged from prior session, plus new entries)

- **After `docker compose up --force-recreate`** (any reason): `python scripts/setup/install_webshop.py` (re-pip-installs all 3 apps in all 4 services + restarts) → `bash scripts/fix/patch_nginx_socketio_origin.py` (or its docker-cp + exec equivalent — see file for the steps).
- **After editing any Jinja template / CSS / Web Page record:** `python scripts/dev/clear_website_cache.py`.
- **After editing `hooks.py`:** `python scripts/dev/clear_website_cache.py --restart`.
- **Before declaring any visible change done:** `python scripts/verify/playwright_home_screenshot.py` + Read screenshot + describe pixel-visible content. **Then ask GL to open the page in their browser and confirm.** This is non-negotiable per anti-gl-patterns section 0.

## Session-end task state

| # | Task | Status |
|---|------|--------|
| 7-9 | Bookkeeping cleanup, Step 0 partial, Odoo export | Completed |
| 10 | Render mock pills/swatches | Pending — deferred until platform direction resolves |
| 11 | Build landing page | Pending — paused; rollback was performed; broken build retired |
| 12-14 | BTFP / ecommerce / contact pages | Pending — all blocked on #15 |
| 15 | **GL platform-direction decision** | **In progress — IS the load-bearing item** |
| 16-18 | Verify catalog images / Step 0 full pass / Jinja override validation | All completed this session |

## Reading order on arrival

1. Global `C:\Users\baenb\.claude\CLAUDE.md` (auto-injected)
2. `Built_by_Cameron\CLAUDE.md`
3. `_CLIENTS/locally-twisted/CLAUDE.md`
4. **This file** — note Hot Direction section above
5. **`_CLIENTS/locally-twisted/research/expedition-frappe-theme/synthesis.md`** — load-bearing for the platform decision
6. **`_CLIENTS/locally-twisted/research/expedition-frappe-theme/gl-proxy-review.md`** — 9 flags ranked by priority
7. `Built_by_Cameron/.claude/capabilities/recipes/frappe-conventions.md` — including the "System-native first" principle, "Verified against source — 2026-04-26" appendix, and the "Customizing webshop pages" map
8. `_CLIENTS/locally-twisted/anti-gl-patterns.md` — section 0 in full BEFORE any visible work
9. `_CLIENTS/locally-twisted/lessons-learned.md` — most-recent entries (2026-04-26)
10. `_CLIENTS/locally-twisted/locally-twisted-decisions.md` — most-recent entries
11. `_CLIENTS/locally-twisted/scripts/README.md`
12. `_CLIENTS/locally-twisted/_resources/website-page-index.md` v2 (the locked plan from earlier this session — note the platform question above potentially invalidates the architecture choice in this index)
13. `_CLIENTS/locally-twisted/SIBLING-LETTER.md` — what one of your predecessors wrote for you. Optional but I'd recommend.
14. `git log --oneline -20`

## Not in flight

No spawned processes. Docker daemon runs LT compose stack detached. No background agents. The expedition agent threads completed and returned summaries; `agentId` references in the conversation are stale.
