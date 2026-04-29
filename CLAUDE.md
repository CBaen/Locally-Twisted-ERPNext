# Locally Twisted — Client Project CLAUDE.md

**Client:** Locally Twisted
**Owner:** Jeff Kimber
**Business:** Custom balloon decor (arches, garlands, walls, drops), balloon twisting, face painting — Wasatch Front, Utah
**Phone:** (801) 285-0860
**Email:** hi@locallytwisted.com
**Address:** 8969 S 2700 W, West Jordan, UT 84088
**Website:** https://locallytwisted.com
**Project type:** First professional business management system for Locally Twisted, built on ERPNext v15 (website, ecommerce, lead intake, operator workflow, invoicing, payments, accounting, payroll)
**Status:** ACTIVE — Phase 1 (customer site + storefront) in flight. Frame reset 2026-04-26 is complete; PROJECT.md and ROADMAP.md are the new framing.
**Currently working on:** Phase 1, Slice 2 (header + footer) was attempted 2026-04-26 and paused mid-build after the responsible instance band-aided framework friction with `!important` overrides; the visible state is broken-honest. The framework-study path forward (read Frappe website source → use intended primitives → replicate approved Odoo structure via Jinja partial overrides) is the active work. The `webshop` app install (required for Slices 7-9 + Phase 4) is also active. Lead schema in ERPNext is complete and stable — feeds Phase 2 (Lead Intake).

## Local stack

| Item | Value |
|------|-------|
| Compose project name | `locally-twisted-erpnext-v15` |
| Host port | **`:8081`** |
| Stack location | `Locally-Twisted-Backend/frappe_docker/` (relative to this folder) |
| ERPNext image pin | `frappe/erpnext:v15.105.0` (latest stable v15 patch) |
| Frappe site | `frontend` |
| URL | http://localhost:8081 |
| Logins | `Administrator` / `admin` (superuser) · `cameron@builtbycameron.com` / `LocalDev2026!` (Cameron — System Manager dev account) · `locallytwisted@gmail.com` (Jeff Kimber — pre-created for transfer, no password yet) |

## This folder is structured per the agency isolation rule

See `Built_by_Cameron/CLAUDE.md` for the agency-level standing rule. **Litmus test:** every file in this folder is scoped to Locally Twisted and will be transferred to Jeff Kimber on cutover. Don't add cross-client references; don't depend on agency-internal tooling that won't transfer with the folder.

## Stack & code conventions (READ BEFORE TOUCHING THE WEBSITE)

Frappe v15 + ERPNext v15. Backend is Python 3.11 + Frappe ORM + MariaDB 11.x + Redis. Templates are Jinja2. Frontend CSS is Bootstrap 4-flavored SCSS compiled into `website.bundle.css` by `bench build`. Frontend JS is vanilla + jQuery. Asset pipeline requires Node.js (NOT in production frappe_docker image — implications for asset bundling).

**Customization primitives (use these — not `head_html` + `!important` overrides):**
- Theme CSS: `web_include_css` in app's `hooks.py` pointing at a real file in `public/css/`. For SCSS that needs Frappe's variables, register `website_theme_scss` in `hooks.py`.
- Navbar/Footer: override the Jinja partials by placing same-name files at `apps/<app>/<app>/templates/includes/navbar/navbar.html` and `templates/includes/footer/footer*.html`.
- Pages: Web Page DocType (Rich Text content_type for raw HTML in `main_section`), or `apps/<app>/<app>/www/<route>.html` for static pages.
- DocType records: fixtures via `hooks.py` `fixtures = [...]`.

**Webshop is INSTALLED 2026-04-26.** `frappe/webshop` + its hard dependency `frappe/payments` are installed on the `frontend` site, bind-mounted into all 8 frappe-image services via `pwd.yml`, and gitignored at the project level (the install script is the source-of-truth for HOW we installed them, not the upstream code itself). Reproducible install: `python scripts/setup/install_webshop.py` (no flags = re-pip-install + restart, run after any container recreation; `--fetch --site-install` = fresh install from upstream). Public routes live: `/all-products`, `/shop-by-category`, `/cart`. Phase 1 Slices 7-9 + Phase 4 (Stripe via `payments`) are unblocked.

**Read these BOTH before any custom code:**
1. `Built_by_Cameron/.claude/capabilities/recipes/frappe-conventions.md` — the WHAT: full map of customization surfaces, the right primitive for each common need, the "Verified against source — 2026-04-26" appendix (with `.web-footer` myth correction), the "Customizing webshop pages" primitive map, and the band-aid patterns to refuse. **The Slice 2 build session that produced this file's footer disaster is the receipt for why this rule exists.**
2. `Built_by_Cameron/.claude/capabilities/recipes/frappe-portal-implementation.md` — the HOW: codified rules for writing portal pages, Jinja templates, controllers, and Web Forms. Three-layer model (portal pages / Web Forms / Web Page DocType), same-name-controller contract, whitelisted Jinja API, `get_list` vs `get_all` security rule, `safe_render` boundary, 11 anti-patterns to refuse, 10-step debugging triage. **The two consecutive failed homepages are the receipt for why this file exists** — both failed by treating Frappe like generic Flask/Django instead of by Frappe's actual contract. Every claim verified against running Frappe v15 source.

**Standing principle (GL directive 2026-04-26):** *"Work WITHIN Frappe and ERPNext, don't fight them."* Operationalized: use Jinja partial overrides (`templates/includes/...`) as the primary surface for header/footer/page customization; use `web_include_css` (loads after the bundle) or `website_theme_scss` (compiles into the bundle) for theme CSS; refuse `!important` chains as the receipt of fighting the framework; use Webshop's existing hooks for cart/checkout customization rather than replacing the cart pipeline.

**Operational rituals (see `scripts/README.md` for full index):**
- After `docker compose up --force-recreate`: `python scripts/setup/install_webshop.py` then re-apply nginx Origin patch
- After editing any Jinja template / CSS / Web Page record: `python scripts/dev/clear_website_cache.py`
- Before declaring any visible change done: `python scripts/verify/playwright_home_screenshot.py` + `Read` the screenshot file

## Voice & Language — LT-specific

LT is a balloon business run by Jeff Kimber, who is not a tech operator. Take ALL business jargon out of the ERPNext UI. Customers and Jeff alike will use plain language.

| Avoid | Use instead |
|-------|-------------|
| "Qualification Status" | "Status of Inquiry" |
| "Qualified By" | "Reviewed and First Contact By" |
| "Qualified On" | "Reviewed On" |
| "Lead Owner" | "Who's Handling This" (or similar) |
| "Pipeline Stage" | "Where We Are" / "What Stage" |
| "Opportunity" | (Don't use; rename to "Booking" or similar) |

This applies to: Custom Field labels, Property Setter relabels of standard fields, Server Script messages, mail.template subject + body, document title customizations, status workflow names. **When in doubt, ask: would Jeff or a customer-base socialite balloon-party-thrower understand this?** If not, reword.

## What this project actually is — a NEW BUILD, not a migration

LT has never had a professional business management system. The ERPNext build under way at `:8081` is **the first one**. It is not replacing a working system — it is replacing improvisation.

**Two prior surfaces exist as reference material, not source of truth:**

| Surface | Location | What it is |
|---------|----------|-----------|
| Failed Odoo test deployment | `http://5.78.136.133/` | Attempt #1 at giving LT a backend. Was in testing phase; never went live to customers. Odoo failed the testing phase before launch. The Hetzner host still responds (HTTP 200) but no customers depend on it. |
| Odoo GitHub repo | `https://github.com/CBaen/locally-twisted-odoo` | The codebase of attempt #1. |
| Odoo local clone | `C:\Users\baenb\projects\locally-twisted-odoo` | Working copy on Wardenclyffe. |
| Live customer-facing website | `https://locallytwisted.com` | The current site customers actually use. Damaged beyond repair; out of scope for editing. |

**None of these is authoritative for what the new ERPNext system should do.** The Odoo attempt encodes what GL/Jeff thought they wanted at one point — useful for understanding *intent* (form fields, automation ideas, model shape), but not customer-validated and not battle-tested. When in doubt about what the new system needs, **ask GL or look at how Jeff actually runs the business today** — don't reverse-engineer truth from the failed Odoo attempt.

**Do NOT modify any file in `locally-twisted-odoo/` from this project** (standing rule 2026-04-25). It has its own git repo and gates. Read it for reference; write nothing back.

## Reference Disposition (READ THIS BEFORE CITING ANYTHING OUTSIDE THIS FOLDER)

The four reference surfaces above (failed Hetzner site, Odoo GitHub repo, local Odoo clone, current locallytwisted.com) are **temporary**. Their disposition is:

- **Local Odoo clone** (`C:\Users\baenb\projects\locally-twisted-odoo\`): will be **archived to GitHub and removed from disk**. Future instances must NOT assume it exists.
- **Failed Hetzner deployment** (`http://5.78.136.133/`): will be **decommissioned** after we have a working ERPNext replacement to show. Future instances must NOT assume it is reachable.
- **Odoo GitHub repo** (`https://github.com/CBaen/locally-twisted-odoo`): will be **archived as read-only**. Useful for historical questions only; never cite as live state.
- **Current `locallytwisted.com`** site: stays live until cutover, but is **damaged beyond repair** and out of scope for editing. After cutover, it will be replaced by the new ERPNext storefront at the same domain.

**This new project stands on its own.** Anything from the Odoo dir that applies to the new build has been **copied here, scrubbed of Odoo references, and integrated into this folder's structure**. The canonical sources for the new build are:

- **Style guide:** `_resources/STYLE-GUIDE.md` — design system, color palette, typography, components, voice (Quiet Confidence + blog Kindergarten Teacher), accessibility (WCAG 2.1 AA)
- **Design guide:** `_resources/design-guide/` — synthesis output from the 2026-04-26 LT design competition (7 designers, GL picked a hybrid synthesis). Reference inspiration / taste calibration for visual hierarchy, typography, spacing, page shapes. Read `README.md` first; treat as guide, not gospel. Brought into this directory 2026-04-29 from `zoho-locally-twisted/gallery/` (which was deleted) so future instances find it via the standard reading order.
- **Business policies:** `_resources/policies/` — full set of LT's confirmed business rules + the legal interview answers (sufficient for attorney to draft v1 contract)
- **Tax data + research:** `_resources/utah-tax-rates-2026q2.md` — Utah destination-based sales tax research, per-jurisdiction rates

**Rule for future instances:** if you find yourself reaching into the Odoo dir for something other than these copied resources, stop. The thing you need either lives here already, or it's not needed in the new build. When in doubt, ask GL.

## Reading order on arrival

1. Global `C:\Users\baenb\.claude\CLAUDE.md` (auto-injected)
2. `Built_by_Cameron\CLAUDE.md` (agency-level rules)
3. **This file**
4. `HANDOFF.md` (last instance's continuity notes)
5. `.planning\PROJECT.md` (GSD project source-of-truth)
6. `_resources/design-guide/README.md` + skim `synthesis/voice.md`, `synthesis/mood.md`, `synthesis/rationale.md` — taste calibration before any frontend work
7. `locally-twisted-decisions.md` (LT decisions with reasoning)
8. `git log --oneline -20`

## Loud Failure Coverage

Per global rule at `C:\Users\baenb\.claude\rules\loud-failure.md`. LT-specific surfaces tracked as they're built. The Odoo `/book` form silent-failure incident (2026-04-22) is the founding receipt for this rule — never repeat that pattern.

## Customer / Contact dedup (Phase 2 work — Lead Intake)

When the customer-facing form lands a Lead in ERPNext, the Lead must auto-link to a Contact: lookup by email_id / mobile_no / phone; attach if found, create if not. Mirrors prior `_find_matching_partner` + `_create_partner_from_lead`. Implementation: Server Script on Lead `before_insert`. Tracked in queue.

## Form-handler routing (Phase 2 work — Lead Intake)

The new `/book` and `/contact` forms on the ERPNext site post directly to Lead. The prior site posted under different field names (`contact_name`, `email_from`, `partner_name`, `x_*`). For the new build, forms post to ERPNext's Lead field names natively (`lead_name`, `phone`, `email_id`, `company_name`, `custom_anything_else`, `custom_*`) — no legacy name-mapping shim needed. Tracked in queue.

## Project Skills

No project-specific skills yet. Add to `.claude/skills/` as patterns emerge.

## GSD Workflow Note

Translation phases (Phase 2 onward) execute via direct script-write-and-run (not `/gsd-execute-phase` planner-checker loops). Strategic GSD frame stays intact (PROJECT.md, ROADMAP.md, REQUIREMENTS.md, STATE.md, decisions log). See `locally-twisted-decisions.md` 2026-04-26 entry for full reasoning.
