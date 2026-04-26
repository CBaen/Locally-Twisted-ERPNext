# HANDOFF — Locally Twisted (First Professional Business Platform)

**Last updated:** 2026-04-26 (Opus 4.7, post-Slice-2 attempt — STOPPED after pattern surfaced)

Overwrite-not-append. ~60 lines. Git is the changelog.

## ⚠ Read this first

The previous session attempted Phase 1 Slice 2 (header + footer) and the custom Frappe app scaffolding. Both arrived in a **partially broken visible state** — and worse, were declared "done" multiple times during the session before GL surfaced what was actually rendering vs what was claimed. **Do NOT trust prior session reports about what's working until you visually verify.** Read the lessons-learned entries dated 2026-04-26 (Slice 2 build) before any code changes.

The session ended on a meta-pause. GL's direction: **study Frappe's website + ecommerce + checkout module conventions before resuming implementation, then replicate the Odoo project's approved structure/copy.** Tasks 5–10 in the active TaskList carry this work.

## Live state of the LT site at `http://localhost:8081`

| Surface | Status |
|---|---|
| ERPNext v15.105.0 stack | Running. 9 containers (compose project `locally-twisted-erpnext-v15`). Logins per `CLAUDE.md`. |
| Custom Frappe app `locally_twisted` | Scaffolded inside backend container, copied to host at `apps/locally_twisted/`, **bind-mounted into all 6 frappe-image services via `pwd.yml`** (volume mount line added to backend, configurator, create-site, frontend, queue-long, queue-short, scheduler, websocket), installed on the `frontend` site (`bench --site frontend list-apps` shows `locally_twisted 0.0.1`). |
| LT theme CSS | Now lives at `apps/locally_twisted/locally_twisted/public/css/lt-theme.css` (~21 KB). Registered via `web_include_css` in `apps/locally_twisted/locally_twisted/hooks.py`. Served at `/assets/locally_twisted/css/lt-theme.css`. The original `_resources/lt-theme.css` is now redundant — should be deleted in cleanup. |
| LT logo | PNG copied from Odoo source to `apps/locally_twisted/locally_twisted/public/icons/lt-logo.png` (1050x300, 78 KB). Wired via `Website Settings.brand_html` referencing `/assets/locally_twisted/icons/lt-logo.png`. |
| Social icons | Real SVG files at `apps/locally_twisted/locally_twisted/public/icons/{instagram,facebook,pinterest,twitter}.svg`. CSS uses `background-image: url(...)` referencing them. **Verified to serve as files but NOT visually verified to render correctly in the footer brand block — see "Known broken" below.** |
| `Website Settings` content | `top_bar_items`, `footer_items`, `address`, `copyright`, `home_page=home`, `head_html` (now just a one-line marker comment) all populated by `scripts/setup/setup_slice2_header_footer.py`. |
| Home Web Page | Created at route `home` with `content_type="Rich Text"` and minimal "Coming soon" placeholder body. Slice 3 will replace the body. |
| nginx Origin pass-through | **Re-applied this session and currently working** (verified `Access-Control-Allow-Origin: http://localhost:8081`). Lives in the frontend container's writable layer, lost on next recreation. Re-apply with `docker cp scripts/fix/patch_nginx_socketio_origin.py <frontend-container>:/tmp/patch.py && MSYS_NO_PATHCONV=1 docker exec <frontend> python3 /tmp/patch.py && MSYS_NO_PATHCONV=1 docker exec <frontend> nginx -s reload`. |

## Known broken (DO NOT trust prior "rendered correctly" claims)

- **Footer brand block area renders invisibly.** `.web-footer`'s computed bounding box is 305 px tall while its child `.container` is 755 px tall. `.footer-info` (containing the brand wordmark, social icons, address, copyright bar) sits at y=1024–1398 — outside the painted blue footer area, on the page's white background. Why `.web-footer`'s height is constrained: **unknown, not yet investigated against Frappe's source**. Multiple `!important` overrides on `height/min-height/max-height/overflow` did NOT change the computed height. Lessons-learned has the full forensic.
- **Footer Soft-Blue band cuts off after one row of column items.** Walls / Drops / Accessibility / parts of the address column are rendering on white instead of blue. Same root cause as the brand-block issue.
- **Social icons may or may not render correctly.** Files serve at HTTP 200, CSS references real file URLs (no longer data URIs), but visual verification was incomplete when session paused. Verify with Playwright + `Read` of the screenshot pixel content before believing.
- **Header "Login" link is Frappe's auto-injected one.** A separate "Switch To Desk" / "Apps" / "My Account" / "Log out" dropdown lives in the rendered HTML for logged-in admins and is JS-hidden for anonymous visitors. Not a bug for the public site — but worth knowing when looking at desktop screenshots taken via headless Chromium with no session cookie.

## Hot direction (load-bearing for next session)

1. **DO NOT resume implementation until the framework study (TaskList items 5–8) is done.** GL has explicitly paused build work because the band-aid pattern was setting bad precedent. The path forward is study → document → build, not more `!important` overrides.
2. **Phase 1 is still the customer-facing proof point.** When build resumes: replicate the structure + content from the Odoo source at `C:\Users\baenb\projects\locally-twisted-odoo\addons\locally_twisted\views\` (header.xml, footer.xml, homepage.xml, page_balloon_twisting.xml, blog_templates.xml). That's the approved-by-Jeff content; the new ERPNext build should mirror it where possible.
3. **Verify with Playwright, not headless Chrome `--screenshot`.** The latter cropped or scaled in ways that hid broken visual state for many turns. Use `scripts/verify/playwright_home_screenshot.py` (full-page Chromium capture + DOM facts) and **always Read the screenshot file and describe pixel-visible content before declaring anything done**.
4. **The bigger anti-pattern is documented** — see `anti-gl-patterns.md` section "0. Building before understanding the framework". Read that BEFORE writing any code in Frappe/ERPNext.
5. **Voice + content reference still applies.** "Quiet Confidence" voice per `_resources/STYLE-GUIDE.md`. The Odoo views in the locally_twisted addon are the structural reference; pull from there, don't re-invent.

## What's already built and carries forward (from earlier sessions)

- **Lead schema** — 45+ Custom Fields on Lead, plain-language relabels, hidden "Additional Information" tab, 25 MB upload. Built via `scripts/translate/translate_crm_lead.py` + 4 fix scripts. Feeds Phase 2 (Lead Intake).
- **`Dashboard Reviewed Item` DocType** — built via `scripts/translate/translate_dashboard_review.py`. No current phase depends on it.
- **Resources** — `_resources/STYLE-GUIDE.md`, `_resources/policies/` (6 business policy files), `_resources/utah-tax-rates-2026q2.md`, `_resources/images/` (15 placeholder PNGs).

## Known carry-overs from earlier sessions

- **Inspiration Photos Table field missing** on Lead — `LT Lead Photo` child DocType + `lt_section_photos` Section Break exist, but the Table field connecting them never landed. Empty section heading on the Lead form. Tied to the deferred photo UX decision.
- **"This is one Lead" realization** — GL was thinking each tab was a Lead category; reality is sections of one Lead form. Don't redesign without explicit direction.

## Not in flight

No spawned processes. Docker daemon runs LT compose stack detached. No background agents.

## Reading order on arrival

1. Global `C:\Users\baenb\.claude\CLAUDE.md` (auto-injected)
2. `Built_by_Cameron\CLAUDE.md`
3. `_CLIENTS/locally-twisted/CLAUDE.md`
4. **This file**
5. **`anti-gl-patterns.md` — read section 0 ("Building before understanding the framework") in full**
6. **`lessons-learned.md` — the 2026-04-26 (Slice 2 build) entry has the full Frappe-quirks dossier**
7. `.planning/PROJECT.md`
8. `.planning/phases/01-customer-site-and-storefront/PLAN.md`
9. `locally-twisted-decisions.md`
10. Active TaskList — items 5–10 are the study-and-document path forward
11. `git log --oneline -20`
