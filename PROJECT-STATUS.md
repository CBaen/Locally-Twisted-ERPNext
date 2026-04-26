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
