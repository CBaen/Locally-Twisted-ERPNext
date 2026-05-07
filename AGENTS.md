# Locally Twisted - Agent Instructions

This is the agent-neutral entrypoint for Codex / ChatGPT / other coding agents working in this repo.

This project inherits the machine-wide Guiding Light Codex communication protocol from `C:\Users\baenb\AGENTS.md` and the global Codex framework. Use that protocol for communication, tangent handling, plain-language explanations, verification discipline, and deciding what to ask Guiding Light versus what the agent should own.

Do not treat old handoff files as truth. Treat them as claims, then verify important facts against git, files, and the running ERPNext database before relying on them.

## Project Reality

- Client: Locally Twisted, owned by Jeff Kimber.
- Business: custom balloon decor, balloon twisting, and face painting on the Wasatch Front, Utah.
- Build: Locally Twisted's ERPNext v15 install — the destination of a migration of LT's business intent + catalog data into a fresh ERPNext install (frame revised 2026-04-30 — see `locally-twisted-decisions.md`).
- "Fresh install" — destination is greenfield ERPNext; no auto-translated Odoo modules or DB dumps.
- "Migration" — catalog records, form intent, policies, voice/brand were carried across from the prior Odoo attempt and the legacy `locallytwisted.com` site, and the new storefront replaces `locallytwisted.com` at cutover.
- The failed Odoo test deployment is reference material only. It never served customers.
- `C:\Users\baenb\projects\locally-twisted-odoo\` is the separate source of truth for Locally Twisted business details. Treat customer-facing business claims, policy terms, product/service details, voice, and legacy decisions inside this ERPNext repo/site as suspect unless traced back to the Odoo business-detail folder or GL/legal approval.
- The live Odoo test shop at `http://5.78.136.133/shop` was the catalog source/reference for the 2026-04-30 catalog port.
- Do not modify `C:\Users\baenb\projects\locally-twisted-odoo\` from this project.

## Current Verified State

Verified against the ERPNext database on 2026-05-06:

| Record | Count |
|---|---:|
| Website Items | 53 |
| Items total | 10,633 |
| Variant templates | 49 |
| Non-variant root Items | 6 |
| Variants | 10,578 |
| Item Prices | 10,615 |
| Item Variant Attribute rows | 32,002 |
| Item Attributes | 26 |

Important correction: older files may claim `10,631 Items`, `10,613 Items`, `10,613 Item Prices`, `8,925 Item Prices`, `4 single-SKU templates`, or `10,560 variants`. Those counts are stale as current DB totals. The 6 non-variant root Items are 4 catalog single-SKU products plus 2 delivery service Items. Re-check DB before changing catalog docs or seed logic.

## Local Stack

| Item | Value |
|---|---|
| Compose project | `locally-twisted-erpnext-v15` |
| Host URL | `http://localhost:8081` |
| Stack dir | `Locally-Twisted-Backend/frappe_docker/` |
| ERPNext image | `frappe/erpnext:v15.105.0` |
| Frappe site | `frontend` |
| Admin login | `Administrator` / `admin` |
| Dev login | `cameron@builtbycameron.com` / `LocalDev2026!` |

Installed app order must keep `locally_twisted` last:

```python
["frappe", "erpnext", "payments", "webshop", "locally_twisted"]
```

If another app is installed, re-set `installed_apps` so LT template overrides still win Frappe's reversed app order.

## Read First

1. `CODING-HANDOFF.md` - compact verified state and next work.
2. `.planning/PROJECT.md` - project frame and requirements.
3. `locally-twisted-queue.md` - active queue, but verify because it can drift.
4. `locally-twisted-decisions.md` - decision log; read newest entries first.
5. `_resources/STYLE-GUIDE.md` - the only current visual style guide: brand, page treatments, components, icons, photography, voice, and accessibility.
6. `git log --oneline -20`.

Claude-era files such as `CLAUDE.md`, `HANDOFF.md`, and `PROJECT-STATUS.md` may contain useful operational history, but they are not authoritative unless verified.

## Multi-Handoff Framing

This project supports multi-agent / multi-handoff work. Active handoffs should be organized by the feature or customer-facing outcome being worked on, not by generic frontend/backend ownership.

- Use the queue for active work selection.
- Use feature-specific `workstreams/<feature-slug>.md` files for live coordination when multiple agents are active on different slices.
- Treat `PROJECT-STATUS.md` as a broad project map only when it is current. Do not treat it as the active source of truth by default.
- Treat `HANDOFF.md` as still valid reference guidance, not the only active handoff surface. Read it for context, then verify against the current feature lane, git state, files, and the running ERPNext site before acting.

## Capabilities

Project-level Codex capability docs live at `.codex/capabilities/INDEX.md`.

Read the index when a task depends on local tools, reusable workflows, project-specific operating knowledge, or prior lessons. Then open only the specific capability files needed for the current task.

Treat `last_verified` dates older than about 90 days as stale until rechecked.

For public layout, Frappe container, `.lt-fullbleed`, Webshop surface, crawl/marquee, breakpoint, nav, drawer, modal, form, product selector, cart, checkout, or broad visual work, read `.codex/capabilities/recipes/frappe-public-container-contract.md` and `.codex/capabilities/recipes/responsive-container-audit.md` before editing. Container fit is a launch requirement, not polish.

Older Claude skills and rules under `C:\Users\baenb\.claude\` are a read-only reference library, not project truth. The useful entrypoints are `C:\Users\baenb\.claude\skills\README.md`, specific `SKILL.md` files, and `C:\Users\baenb\.claude\rules\reach-paths.md`. For Frappe/ERPNext launch work, especially consider the older `frappe-payment-safety`, `frappe-form-integrity`, `frappe-fixture-discipline`, `frappe-migration-guard`, and `frappe-deploy-safety` skills as checklists for what to verify. Do not read secrets, runtime state, logs, caches, sessions, or token files there, and do not copy Claude-era files wholesale into this repo.

## Frappe / ERPNext Rules

Work within Frappe and ERPNext.

- Theme CSS lives in the app and is registered through `web_include_css`.
- Header/footer customization should use Jinja partial overrides.
- Static/portal pages should live under `apps/locally_twisted/locally_twisted/www/<route>.html` with a same-name controller when needed.
- Webshop pages should use Webshop/Frappe override hooks and templates instead of replacing the cart pipeline.
- Avoid `head_html` CSS injection and avoid `!important` chains. The known exception is the contained `.product-code` hide for Webshop's compiled product-card JS.
- After Jinja/CSS/Web Page edits, run `python scripts/dev/clear_website_cache.py`.
- Before declaring visual work done, verify with browser screenshots at desktop and mobile widths, plus the layout gates below.
- Browser verification is repo-local. `playwright.config.js` prefers installed Chrome/Edge on Windows when Playwright's bundled Chromium is missing. Use `npm run test:layout-fit` for passive public route layout checks, `npm run test:interactive-layout` for stateful menus/drawers/modals/forms/product controls, `npm run test:public-verify` for broad public-site closeout, and `npm run test:desk-owner` with `LT_DESK_TEST_USER` / `LT_DESK_TEST_PASSWORD` for the owner Desk route check.

## Voice And UI Language

Jeff is not a technical operator. Customer and backend UI copy should be plain.

Avoid:

- "Qualification Status"
- "Qualified By"
- "Qualified On"
- "Lead Owner"
- "Pipeline Stage"
- "Opportunity"

Prefer:

- "Status of Inquiry"
- "Reviewed and First Contact By"
- "Reviewed On"
- "Who's Handling This"
- "Where We Are" / "What Stage"
- "Booking" where a customer-facing label is needed

Do not invent business facts, policy terms, product details, or legal language. Use `_resources/` sources or ask.

## Canonical Resources

- Style guide: `_resources/STYLE-GUIDE.md`
- Business policies: `_resources/policies/`
- Utah tax research: `_resources/utah-tax-rates-2026q2.md`
- Live Odoo catalog scrape output: `_resources/odoo-live/`
- `/book` and `/contact` snapshots: `_resources/odoo-live-snapshot/hetzner-book.html` and `hetzner-contact.html`

The old `_resources/design-guide/` design-competition synthesis was deleted on 2026-05-05 because it conflicted with the approved Civic Celebration + Slate Blue/Berry + Brand Direction visual contract and kept reintroducing light-blue/blush styling. Do not recreate it or treat old screenshots/TSX from that direction as current design guidance.

The Odoo snapshots are canonical for the rebuilt `/book` and `/contact` form shape where explicitly stated. They are not blanket authority for the rest of the system.

## Current P0 Work

As of 2026-04-30, the next safest implementation slices are:

1. `/book` form page: primary inquiry conversion path, currently expected to be missing/404, backed by the existing Lead schema.
2. `/privacy` and `/terms-of-service`: required for Stripe live-mode readiness.
3. Fix stale documentation counts so future agents stop repeating catalog errors.

For `/book`, verify the existing Lead schema before building. The intended source is the Hetzner `/book` snapshot and live source if reachable, with native ERPNext Lead field names.

## Trust Rules

- Never claim a route, form, count, or visual state is working without verification.
- Say when something is unverified.
- Prefer small complete slices over broad rewrites.
- If prior docs conflict, verify against the running system and tell GL what changed.
- Do not hide errors behind "probably" or "should".
