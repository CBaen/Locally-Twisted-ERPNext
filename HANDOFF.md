# HANDOFF — Locally Twisted (First Professional Business Platform)

**Last updated:** 2026-04-26 (Opus 4.7 — webshop install + framework study session)

Overwrite-not-append. ~80 lines. Git is the changelog.

## Read this first

This session resolved three blockers from the prior session and installed the webshop foundation. **Slice 2 (header + footer) is still broken-honest** — its visible state has not changed — but the path forward is now clear and unblocked. The next instance can start the Slice 2 redo immediately following the plan in "Hot direction" below.

**GL's standing directive (2026-04-26):** *"I don't want to fight Frappe or ERPNext. I want to work within it."* Every decision in this session is grounded in that. The next instance must, too.

## What was done this session

1. **Webshop installed and made durable.** `frappe/webshop` + its hard dependency `frappe/payments` are installed on the `frontend` site and bind-mounted into all 8 frappe-image services via `pwd.yml`. Reproducible install: `python scripts/setup/install_webshop.py` (no flags = re-pip-install + restart, run after any container recreation).
2. **Framework verification done.** Read Frappe's actual website module source inside the running container. Confirmed conventions doc claims; corrected the `.web-footer` height "constraint" myth (no max-height rule exists — the previous observation came from band-aid CSS interacting with body's flex-column sticky-footer pattern). See `Built_by_Cameron/.claude/capabilities/recipes/frappe-conventions.md` "Verified against source — 2026-04-26" appendix and the new "Webshop module map" section.
3. **Webshop module mapped.** Documented which Jinja files to override for Phase 1 Slices 7-9 (cart, all-products, shop-by-category, item card, etc.). All in the agency conventions doc.
4. **Reproducible scripts.** `scripts/setup/install_webshop.py` and `scripts/dev/clear_website_cache.py`. `scripts/README.md` indexes everything.
5. **Bookkeeping cleanup.** `CLAUDE.md` "Currently working on" updated; `STATE.md` reflects Slice 1 done + Slice 2 paused; queue's stale "Waiting on GL" section trimmed (Phase 1 gates were already resolved).

## Live state of the LT site at `http://localhost:8081`

| Surface | Status |
|---|---|
| ERPNext v15.105.0 stack | Running, recreated this session with new pwd.yml. 9 containers. |
| Apps installed on site | `frappe`, `erpnext`, `locally_twisted` (0.0.1), `payments` (0.0.1), `webshop` (0.0.1) |
| Apps bind-mounted in pwd.yml | `locally_twisted`, `payments`, `webshop` — all 8 frappe-image services |
| Webshop public routes | `/all-products` HTTP 200, `/shop-by-category` should work (not yet seeded with products), `/cart` HTTP 301 (redirects to login when no customer session — expected) |
| Custom Frappe app `locally_twisted` | Editable pip install re-applied this session via `install_webshop.py` |
| LT theme CSS | Still at `apps/locally_twisted/locally_twisted/public/css/lt-theme.css`, served at `/assets/locally_twisted/css/lt-theme.css`. **Contains `!important` band-aid chains from the previous session that should be removed before the Slice 2 redo** — they interfere with the framework rather than working with it. |
| nginx Origin patch | Re-applied this session post-recreate. Verified `Access-Control-Allow-Origin: http://localhost:8081`. |
| `Website Settings` content | Still populated by the prior session's `setup_slice2_header_footer.py` (top_bar_items, footer_items, brand_html, address, copyright, home_page). |
| Home Web Page | Still the "Coming soon" placeholder. Slice 3 will replace. |

## Known broken (DO NOT trust prior "rendered correctly" claims)

Same as prior session, with one resolution:

- **Footer brand block area renders invisibly.** `.web-footer`'s computed bounding box vs its child `.container` mismatch reported as ~305px vs 755px. **Root cause now known** (see `lessons-learned.md` 2026-04-26 (Slice 2 build) — RESOLVED entry): there is NO `max-height` rule in Frappe's `footer.scss`. The observation came from the LT theme's own `!important` chain interacting with the body flex sticky-footer pattern, not from a framework constraint. The fix is to override the Jinja partial AND remove the `!important` chains, NOT more CSS overrides.
- **Footer Soft-Blue band cuts off after one row of column items.** Same root cause as above.
- **Approved Odoo structure not yet matched.** Header is single-tier (approved is two-tier centered logo). Footer is 4 columns (approved is 3 + hours block). 4 social icons (approved is 3, no Twitter).

## Hot direction (load-bearing for next session — Slice 2 redo)

Per GL's directive "work WITHIN Frappe, don't fight it" and the framework study findings:

1. **Strip `!important` chains from `apps/locally_twisted/locally_twisted/public/css/lt-theme.css`.** Specifically the `.web-footer` block (lines 477-503) and the `.web-footer ul/li/footer-group` blocks (505-526). They are receipts of fighting the framework.
2. **Override the footer Jinja partials** at `apps/locally_twisted/locally_twisted/templates/includes/footer/footer.html` (and `footer_grouped_links.html`, `footer_info.html`, `footer_logo_extension.html`). Your override resolves before Frappe's standard one. Use whatever class names you want — no inheritance from `.web-footer`. Match the approved Odoo structure (two-tier header with centered logo, 3-column footer with hours block, 3 social icons, centered brand block, "Tue-Fri 12-6 / Sat 10-4").
3. **Same pattern for the navbar** — override `apps/locally_twisted/locally_twisted/templates/includes/navbar/navbar.html` for the two-tier centered-logo structure.
4. **After every edit:** `python scripts/dev/clear_website_cache.py`. After hooks.py changes: `--restart`.
5. **Verify with Playwright before declaring done.** `python scripts/verify/playwright_home_screenshot.py` then `Read` the screenshot file and describe pixel-visible content. Mandatory per `anti-gl-patterns.md` section 0.
6. **Approved structure source:** `_resources/STYLE-GUIDE.md` for design system; `Built_by_Cameron/.claude/capabilities/recipes/frappe-conventions.md` "Approved LT structure" table for the specific Odoo header/footer patterns to replicate.

After Slice 2 lands cleanly: Slices 3-9 of Phase 1, in order. Webshop foundation is in place for Slices 7-9 — the conventions doc maps which webshop Jinja files to override for visual customization.

## Operational rituals

- **After `docker compose up --force-recreate`** (any reason): `python scripts/setup/install_webshop.py` then `bash scripts/fix/patch_nginx_socketio_origin.py` (or its docker-cp + exec equivalent — see HANDOFF in container).
- **After editing any Jinja template / CSS / Web Page record:** `python scripts/dev/clear_website_cache.py`.
- **Before declaring any visible change done:** `python scripts/verify/playwright_home_screenshot.py` + Read the screenshot.

## What's already built and carries forward

- **Lead schema** — 45+ Custom Fields on Lead, plain-language relabels, hidden "Additional Information" tab, 25 MB upload. Feeds Phase 2 (Lead Intake).
- **Custom Frappe app `locally_twisted`** — scaffolded, bind-mounted, installed. `web_include_css` registered in `hooks.py` pointing at `/assets/locally_twisted/css/lt-theme.css`.
- **Webshop foundation** — `frappe/payments` + `frappe/webshop` installed and durable. Phase 1 Slices 7-9 + Phase 4 unblocked.
- **Resources** — `_resources/STYLE-GUIDE.md`, `_resources/policies/` (6 business policy files), `_resources/utah-tax-rates-2026q2.md`, `_resources/images/` (15 placeholder PNGs).

## Known carry-overs from earlier sessions

- **Inspiration Photos Table field missing** on Lead — `LT Lead Photo` child DocType + `lt_section_photos` Section Break exist, but the Table field connecting them never landed. Empty section heading. Tied to deferred photo UX decision.
- **"This is one Lead" realization** — GL was thinking each tab was a category; reality is sections of one form. Don't redesign without explicit direction.

## Not in flight

No spawned processes. Docker daemon runs LT compose stack detached. No background agents.

## Reading order on arrival

1. Global `C:\Users\baenb\.claude\CLAUDE.md` (auto-injected)
2. `Built_by_Cameron\CLAUDE.md`
3. `_CLIENTS/locally-twisted/CLAUDE.md`
4. **This file**
5. **`Built_by_Cameron/.claude/capabilities/recipes/frappe-conventions.md`** — including the "Verified against source — 2026-04-26" appendix and the "Customizing webshop pages" table. THIS IS YOUR PRIMARY REFERENCE for any code change in Frappe/ERPNext.
6. `anti-gl-patterns.md` — section 0 (Building before understanding the framework). Re-read in full.
7. `lessons-learned.md` — the 2026-04-26 (Slice 2 build) entry (Frappe quirks dossier) + the resolved `.web-footer` entry.
8. `.planning/PROJECT.md`
9. `.planning/phases/01-customer-site-and-storefront/PLAN.md`
10. `locally-twisted-decisions.md`
11. `scripts/README.md`
12. `git log --oneline -20`
