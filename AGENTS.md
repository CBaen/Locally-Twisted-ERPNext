# Locally Twisted - Agent Instructions

This is the agent-neutral entrypoint for Codex / ChatGPT / other coding agents working in this repo.

This project inherits the machine-wide Guiding Light communication protocol from `C:\Users\baenb\AGENTS.md` and the shared capability framework. Use that protocol for communication, tangent handling, plain-language explanations, verification discipline, and deciding what to ask Guiding Light versus what the agent should own.

Do not treat old handoff files as truth. Treat them as claims, then verify important facts against git, files, and the running ERPNext database before relying on them.

## Coordination Safety Pilot

This repo is the protected clean child/client pilot for the neutral multi-agent
coordination system. Before edits, read
`C:\Users\baenb\agent-coordination\STARTUP-CHECKLIST.md`, check
`LIVE-BOARD.md` and `SESSION-REGISTRY.md`, and apply the Six-Box Rule from the
machine guide.

For this repo, normal LT client work is Box 4: child/client repo. Machine-wide
coordination updates are Box 5 and belong in `C:\Users\baenb\agent-coordination`,
not in LT source. Parent/company Built by Cameron tasks are separate from LT
client tasks unless Guiding Light explicitly says the task crosses that boundary.

## Git Policy - Main And Reviewed Worktrees

`main` remains the trusted base and default path. Normal single-session LT work stays on `main`.

Task branches are allowed only in dedicated linked worktrees under:

`C:\Users\baenb\agent-worktrees\builtbycameron-lt\<agent-session-id>__<task-slug>`

- Do not create, switch to, commit on, push from, or open PRs from feature, codex, topic, experiment, or task branches inside the main checkout.
- Before editing, run `git rev-parse --abbrev-ref HEAD`; `main` is allowed in the main checkout. If it prints anything else, verify the folder is a linked worktree for the current task before continuing.
- A linked LT worktree must be created from the actual LT Git root: `C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\locally-twisted`.
- A linked LT worktree must live outside all project repos, under the approved neutral worktree root above. Do not create LT worktrees inside `C:\Users\baenb\projects`, the Built by Cameron parent repo, `_CLIENTS`, this repo, or any nested repo.
- The shorter `builtbycameron-lt` project ID is intentional. The longer derived repo-forest ID exceeded Windows path limits for deep Frappe/ERPNext files during worktree creation.
- Before creating or using a worktree, claim the task in `C:\Users\baenb\agent-coordination\LIVE-BOARD.md` and `C:\Users\baenb\agent-coordination\SESSION-REGISTRY.md`.
- Use one task per worktree and clear branch names such as `codex/<task-slug>`, `claude/<task-slug>`, `human/<task-slug>`, or `agent/<task-slug>`.
- Do not push, merge, rebase, or land a task branch to `main` without explicit review or publish approval. If a task branch must be pushed for review or backup, push only the current task branch from its matching linked worktree.
- Pushes to `origin/main` must come from local `main` after verification and an approved publish path. GitHub is the archive; task branches are not holding areas or queue lanes.
- Machine-wide hooks currently live at `C:\Users\baenb\.codex\git-hooks\controlled-branches` and allow non-main commits only from linked worktrees. The older `no-branches` hook path is a fallback/archive, not the active policy.
- Do not report unrelated repository file state as routine status, progress chatter, or closeout filler. Surface other changed files only when they block the LT task, overlap files you must touch, affect commit/push safety, or GL asks for git state. Treat repeated unsolicited changed-file commentary as a mental-load/accessibility issue.

## No Monoliths

Source of truth:
`C:\Users\baenb\capabilities\principles\no-monolith-files.md`.

Apply it here as: one hand-authored production file, one clear job. Split
cross-concern LT changes into named modules, partials, helpers, recipes,
workstream docs, or focused verifiers instead of expanding catch-all files.
Research/reference artifacts may be long-form; generated, vendor, lock, cache,
and export files are artifacts, not design precedent.

## Fail Loudly Law

Mantra: **If it can fail, it must fail loudly.**

This is the operating law for forms, automations, payments, checkout, documents,
customer messages, backend handoffs, route/layout contracts, containers,
verification, and agent communication. Silent failure is not a degraded state;
it is a business trust failure.

Customer-facing failures must follow the machine-wide warm-teacher voice rule:
sound calm, plain, and gently playful, like a kindergarten teacher helping a
student. Say what happened without blame or technical jargon, tell the customer
the next safe step, and never imply full success when a downstream path is
incomplete. Operator/developer evidence still needs the exact loud failure.

Failing loudly means:

- The customer or operator must not see false success. No success toast, receipt,
  invoice, quote, saved design, submitted form, or clean layout claim unless the
  downstream record/path actually exists.
- The developer must get an actionable failure: exception, nonzero verifier,
  failed test, explicit blocker field, or reproducible report row.
- The system monitor must get evidence when the failure is operational: Frappe
  Error Log, scheduler report, audit JSON, mutation guard, or equivalent.
- The source contract must name the missing connection, not hide it in prose.
  Forms map to fields, automations map to records, documents map to recipients,
  and containers map to executable route contracts.

Violations include swallowed exceptions, console-only errors, skipped fields,
fallback content that looks successful, hidden horizontal scrollbars, native
scrollbars on crawls, stale docs treated as proof, customer emails that silently
do not queue, and agent replies that imply success without verification.

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

Verified against the local ERPNext database on 2026-05-18:

| Record | Count |
|---|---:|
| Website Items | 53 |
| Items total | 10,674 |
| Variant templates | 49 |
| Non-variant root Items | 8 |
| Active customer-facing variants | 10,227 |
| Disabled legacy optional-add-on variants | 390 |
| All variant records | 10,617 |
| Item Prices | 10,656 |
| Item Variant Attribute rows | 32,028 |
| Item Attributes | 29 |

Important correction: older files may claim `10,631 Items`, `10,613 Items`, `10,633 Items`, `10,672 Items`, `10,613 Item Prices`, `10,615 Item Prices`, `10,654 Item Prices`, `8,925 Item Prices`, `4 single-SKU templates`, `6 non-variant root Items`, `10,560 variants`, or `10,578 variants`. Those counts are stale as current DB totals. The 8 non-variant root Items are 4 catalog single-SKU products, 2 delivery service Items, and 2 support Items (`ADDON-FOIL-NUMBER`, `LT-PRODUCT-QUOTE-REVIEW`). Active variants dropped from the old customer-facing `10,578` baseline because `Add Foil Number` is no longer a required variant axis for bouquet-size products; the old add-on variants remain disabled as history. Re-check DB before changing catalog docs or seed logic.

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

Project-level shared capability docs live at `capabilities/INDEX.md`.

Read the index when a task depends on local tools, reusable workflows, project-specific operating knowledge, or prior lessons. Then open only the specific capability files needed for the current task.

Treat `last_verified` dates older than about 90 days as stale until rechecked.

For public layout, Frappe container, `.lt-fullbleed`, Webshop surface, crawl/marquee, breakpoint, nav, drawer, modal, form, product selector, cart, checkout, or broad visual work, read `capabilities/recipes/frappe-public-container-contract.md` and `capabilities/recipes/responsive-container-audit.md` before editing. If the work touches a hero, intro, masthead, or page-header treatment, also read `capabilities/recipes/compact-hero-contract.md`. Container fit and compact same-height heroes are launch requirements, not polish.

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

## Launch Provider Ownership

For Frappe Cloud, Cloudflare, Stripe, DNS, hosting, and production-provider
work, agents own the execution once GL says the account/session is logged in or
available. Do not hand GL provider dashboard checklists as the next action. Use
the project capabilities, browser automation, provider CLI/API, SSH, and repo
verifiers first. Ask GL only for MFA, unavailable credentials, payment/legal or
business approval, or a final destructive go/no-go.

For the LT Frappe Cloud launch specifically:

- Install/update the Frappe Cloud custom app from the app-root mirror:
  `https://github.com/CBaen/Locally-Twisted-Frappe-App.git`.
- Keep `locally_twisted` installed last.
- Set `lt_ecommerce_paused=1` on staging/live before public verification.
- Prove the temporary Frappe Cloud URL before any Cloudflare DNS cutover.
- Do not expose checkout/Stripe unless that separate payment gate is explicitly
  reopened and passes.

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

## Current Work Selection

Use `locally-twisted-queue.md` and the active `workstreams/*.md` files for current P0 selection. The old April `/book` P0 is superseded: `/book` now redirects to `/contact?intent=quick`, and `/contact` is the customer inquiry route.

Current active lanes are launch proof, paperwork/backend automation, fail-loud record-level hardening, brand/shop/portfolio follow-through, and cutover readiness. Before changing any route, form, catalog, checkout, payment, document, or backend automation behavior, verify the current lane file and run the matching verifier.

## Trust Rules

- Never claim a route, form, count, or visual state is working without verification.
- Say when something is unverified.
- Prefer small complete slices over broad rewrites.
- If prior docs conflict, verify against the running system and tell GL what changed.
- Do not hide errors behind "probably" or "should".
