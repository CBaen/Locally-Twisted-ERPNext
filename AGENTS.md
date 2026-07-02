# Locally Twisted - Agent Instructions

This is the agent-neutral entrypoint for Codex / ChatGPT / other coding agents working in this repo.

This project inherits the machine-wide Guiding Light communication protocol from `/home/guidingl/AGENTS.md` and the shared capability framework. Use that protocol for communication, tangent handling, plain-language explanations, verification discipline, and deciding what to ask Guiding Light versus what the agent should own.

Do not treat old handoff files as truth. Treat them as claims, then verify important facts against git, files, and the running ERPNext database before relying on them.

## Mandatory LT Capability Gate

Before any LT edit or release action, run the capability context gate from this
repo root and load the project capability index:

```bash
python /home/guidingl/codex-framework/tools/capability_context_gate.py \
  --cwd "$PWD" \
  --task "<plain-English LT task>" \
  --loaded "capabilities/INDEX.md" \
  --loaded "<specific LT recipe/failure/skill used for this task>"
```

This is not optional for public-site, catalog, checkout, payment, Frappe Cloud,
Cloudflare, Stripe, provider, live-release, form, customer-message, document,
or backend automation work. For those tasks, `capabilities/INDEX.md` alone is
not enough; load the specific recipe, failure note, gate, or skill that governs
the path before editing or claiming readiness.

Required LT release/provider resources:

- Live/Frappe Cloud/Cloudflare/Stripe/DNS/provider work must load
  `capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`.
- Before changing the release path or app mirror path, load the relevant failure
  notes, including
  `capabilities/failures/frappe-cloud-release-site-migration-drift.md` and
  `capabilities/failures/frappe-cloud-app-mirror-release-scope-drift.md` when
  they apply.
- Source push and app-mirror push are not live proof. Live proof requires the
  loaded release capability path plus a successful Frappe Cloud/site update and
  fresh public-route verification.

If the gate fails, stop before editing or publishing. Fix the missing capability
context first or state the blocker plainly. Status and closeout must include
`Capability gate: PASS` and the loaded resources.

## Coordination Safety Pilot

This repo is the protected clean child/client pilot for the neutral multi-agent
coordination system. Before edits, read
`/home/guidingl/agent-coordination/STARTUP-CHECKLIST.md`, check
`LIVE-BOARD.md` and `SESSION-REGISTRY.md`, and apply the Six-Box Rule from the
machine guide.

For this repo, normal LT client work is Box 4: child/client repo. Machine-wide
coordination updates are Box 5 and belong in `/home/guidingl/agent-coordination`,
not in LT source. Parent/company Built by Cameron tasks are separate from LT
client tasks unless Guiding Light explicitly says the task crosses that boundary.

## Git Policy - Main And Reviewed Worktrees

`main` remains the trusted base and default path. Normal single-session LT work stays on `main`.

Task branches are allowed only in dedicated linked worktrees under:

`/home/guidingl/agent-worktrees/builtbycameron-lt/<agent-session-id>__<task-slug>`

- Do not create, switch to, commit on, push from, or open PRs from feature, codex, topic, experiment, or task branches inside the main checkout.
- Before editing, run `git rev-parse --abbrev-ref HEAD`; `main` is allowed in the main checkout. If it prints anything else, verify the folder is a linked worktree for the current task before continuing.
- A linked LT worktree must be created from the actual LT Git root: `/home/guidingl/projects/Built_by_Cameron/_CLIENTS/locally-twisted`.
- A linked LT worktree must live outside all project repos, under the approved neutral worktree root above. Do not create LT worktrees inside `/home/guidingl/projects`, the Built by Cameron parent repo, `_CLIENTS`, this repo, or any nested repo.
- The shorter `builtbycameron-lt` project ID is intentional and remains the stable LT worktree identifier on Kubuntu.
- Before creating or using a worktree, claim the task in `/home/guidingl/agent-coordination/LIVE-BOARD.md` and `/home/guidingl/agent-coordination/SESSION-REGISTRY.md`.
- Use one task per worktree and clear branch names such as `codex/<task-slug>`, `claude/<task-slug>`, `human/<task-slug>`, or `agent/<task-slug>`.
- Do not push, merge, rebase, or land a task branch to `main` without explicit review or publish approval. If a task branch must be pushed for review or backup, push only the current task branch from its matching linked worktree.
- Pushes to `origin/main` must come from local `main` after verification and an approved publish path. GitHub is the archive; task branches are not holding areas or queue lanes.
- Machine-wide hooks currently live at `/home/guidingl/.codex/git-hooks/controlled-branches` and allow non-main commits only from linked worktrees. The older `no-branches` hook path is a fallback/archive, not the active policy.
- Do not report unrelated repository file state as routine status, progress chatter, or closeout filler. Surface other changed files only when they block the LT task, overlap files you must touch, affect commit/push safety, or GL asks for git state. Treat repeated unsolicited changed-file commentary as a mental-load/accessibility issue.

## No Monoliths

Source of truth:
`/home/guidingl/capabilities/principles/no-monolith-files.md`.

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
- DBA boundary: Locally Twisted is the accounting/ERPNext operating company for
  three customer-facing brand lanes: `locally_twisted`,
  `commercial_balloon_decor`, and `memorial_balloons`. Keep websites,
  branding/styling, copy, invoices, portals, automations, ads, files, and
  customer-facing claims separate by lane. Do not treat one brand's facts,
  assets, style, Meta state, or customer data as global truth for the others.
  No fourth brand is approved in current scope. Read `BRAND-BOUNDARY.md` and
  `capabilities/recipes/three-brand-dba-boundary-contract.md` before any work
  that can cross brand lanes.
- Build: Locally Twisted's ERPNext v15 install — the destination of a migration of LT's business intent + catalog data into a fresh ERPNext install (frame revised 2026-04-30 — see `locally-twisted-decisions.md`).
- "Fresh install" — destination is greenfield ERPNext; no auto-translated legacy_source modules or DB dumps.
- "Migration" — catalog records, form intent, policies, voice/brand were carried across from the prior legacy_source attempt and the legacy `locallytwisted.com` site, and the new storefront replaces `locallytwisted.com` at cutover.
- The failed legacy_source test deployment is reference material only. It never served customers.
- The old local `locally-twisted-legacy_source` checkout is not an active local dependency on Wardenclyffe. Treat customer-facing business claims, policy terms, product/service details, voice, and legacy decisions inside this ERPNext repo/site as suspect unless traced back to committed `_resources/` source material, restored external backup evidence that GL explicitly approves for use, or GL/legal approval.
- The live legacy_source test shop at `http://5.78.136.133/shop` was the catalog source/reference for the 2026-04-30 catalog port.
- Do not recreate, modify, or depend on an unverified legacy_source checkout from this project.

## Catalog Authority And Product Scope

Product counts, product inclusion, exclusions, and catalog scope are
time-sensitive operating facts, not permanent truths.

Do not treat old docs, manifests, snapshots, handoffs, verifier expectations, or
audit artifacts as having complete authority over the current product set. They
are evidence only.

The active authority for catalog scope is:

1. Guiding Light's current explicit decision.
2. Work recently implemented by Guiding Light or with Guiding Light's explicit
   approval.
3. Indexed conversation evidence showing the approval trail or decision context,
   especially before asking Guiding Light to repeat a product-scope decision.
4. Fresh verification against the current repo/database/runtime, only for facts
   it can actually prove.

If a change, verifier, branch, restore, or cleanup would include, exclude,
retire, revive, rename, or count active products, check indexed conversations
for an existing approval trail first. If the approval trail is missing or
unclear, stop and ask Guiding Light before choosing product scope. Agents may
report inconsistency and make safety tools fail loudly, but must not choose
product scope from stale artifacts.

## Current Verified State

Verified against the local ERPNext database on 2026-06-21 after the requested
public product retirement:

| Record | Count |
|---|---:|
| Website Items total | 51 |
| Published Website Items | 47 |
| Retired/unpublished Website Items | 4 |
| Items total | 10,685 |
| Variant templates | 49 |
| Non-variant root Items | 7 |
| Active customer-facing variants | 10,186 |
| Disabled variant records | 443 |
| All variant records | 10,629 |
| Item Prices | 10,666 |
| Item Variant Attribute rows | 32,049 |
| Item Attributes | 30 |

Important correction: older files may claim `53 Website Items`, `51 published
products`, `30 checkout products`, `21 quote-first products`, `10,631 Items`,
`10,613 Items`, `10,633 Items`, `10,672 Items`, `10,674 Items`, `10,686 Items`,
`10,613 Item Prices`, `10,615 Item Prices`, `10,654 Item Prices`, `10,656 Item
Prices`, `10,668 Item Prices`, `8,925 Item Prices`, `4 single-SKU templates`,
`6 non-variant root Items`, `8 non-variant root Items`, `10,560 variants`,
`10,578 variants`, `10,617 variants`, or `10,227 active variants` as current DB
totals. Those counts are stale as current DB totals. The 4 retired/unpublished
Website Items are `large-garland`, `mothers-day-bouquet`,
`large-organic-column`, and `pride-progress-rainbow-balloon-arch`; they should
remain hidden as `needs_review|needs_review` unless GL explicitly re-approves
one. Re-check DB before changing catalog docs or seed logic.

## Local Stack

| Item | Value |
|---|---|
| Compose project | `locally-twisted-erpnext-v15` |
| Host URL | `http://localhost:8081` |
| Stack dir | `Locally-Twisted-Backend/frappe_docker/` |
| ERPNext image | `frappe/erpnext:v15.105.0` |
| Frappe site | `frontend` |
| Admin/dev login | Not stored in committed docs. Use approved local credentials from the operator or environment variables such as `LT_DESK_TEST_USER` / `LT_DESK_TEST_PASSWORD` for verifiers. |

## Local Docker Runtime Posture

Docker stays as a boxed workshop, but it does not get to live rent-free in the
background. The LT ERPNext stack is an on-demand local runtime: turn it on only
when actively working or verifying LT, then turn it back off when the local proof
task is done.

- Preferred Wardenclyffe helper: `client-stack start lt`, `client-stack stop lt`,
  and `client-stack check lt`.
- Normal local proof URL is `http://localhost:8081`.
- Do not leave temporary Tailscale-IP or host-IP port bindings in `pwd.yml` as
  project truth. Use localhost unless the task explicitly requires a temporary
  remote-access bind, and document/revert that workaround before closeout.
- Stopping the stack is safe after work; deleting stored data is not. Never use
  `docker compose down -v`, Docker prune, volume deletion, database reset, or
  account/provider changes without explicit approval.

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
- When Guiding Light asks for triad/subagent help on implementation work, do not default the lanes to read-only review. Decide lane mode from the task: use implementation-capable builder lanes when scoped edits, test artifacts, or verifiers can help, and use read-only lanes only when the work is explicitly audit/review/research or when write access would be unsafe.

## Capabilities

Project-level shared capability docs live at `capabilities/INDEX.md`.

Read the index through the mandatory LT capability gate above. Then open only
the specific capability files needed for the current task.

Treat `last_verified` dates older than about 90 days as stale until rechecked.

This repo uses the Capability Graduation Ladder. When a capability affects
checkout, payment, public forms, customer communication, provider accounts,
launch, staging/live release, or multi-agent coordination, check whether it has
or needs a skill, verifier, gate, automation, architecture, or release/live
approval boundary before treating prose as enough.

For public layout, Frappe container, `.lt-fullbleed`, Webshop surface, crawl/marquee, breakpoint, nav, drawer, modal, form, product selector, cart, checkout, or broad visual work, read `capabilities/recipes/frappe-public-container-contract.md` and `capabilities/recipes/responsive-container-audit.md` before editing. If the work touches a hero, intro, masthead, or page-header treatment, also read `capabilities/recipes/compact-hero-contract.md`. Container fit and compact same-height heroes are launch requirements, not polish.

Older Claude skills and rules are not active local project truth on Wardenclyffe. If GL explicitly restores a Claude-era reference library from external backup for a narrow task, treat it as read-only reference evidence only. For Frappe/ERPNext launch work, older ideas such as `frappe-payment-safety`, `frappe-form-integrity`, `frappe-fixture-discipline`, `frappe-migration-guard`, and `frappe-deploy-safety` may be used as checklists only after the current LT capability gate passes. Do not read secrets, runtime state, logs, caches, sessions, or token files there, and do not copy Claude-era files wholesale into this repo.

## Frappe / ERPNext Rules

Work within Frappe and ERPNext.

- Theme CSS lives in the app and is registered through `web_include_css`.
- Header/footer customization should use Jinja partial overrides.
- Static/portal pages should live under `apps/locally_twisted/locally_twisted/www/<route>.html` with a same-name controller when needed.
- Webshop pages should use Webshop/Frappe override hooks and templates instead of replacing the cart pipeline.
- Avoid `head_html` CSS injection and avoid `!important` chains. The known exception is the contained `.product-code` hide for Webshop's compiled product-card JS.
- After Jinja/CSS/Web Page edits, run `python scripts/dev/clear_website_cache.py`.
- Before declaring visual work done, verify with browser screenshots at desktop and mobile widths, plus the layout gates below.
- Browser verification is repo-local. `playwright.config.js` prefers installed Brave/Chromium/Chrome/Edge on Kubuntu. Use `npm run test:layout-fit` for passive public route layout checks, `npm run test:interactive-layout` for stateful menus/drawers/modals/forms/product controls, `npm run test:public-verify` for broad public-site closeout, and `npm run test:desk-owner` with `LT_DESK_TEST_USER` / `LT_DESK_TEST_PASSWORD` for the owner Desk route check.

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
- Live legacy_source catalog scrape output: `_resources/catalog-source/`
- `/book` and `/contact` snapshots: `_resources/retired-source-snapshot/hetzner-book.html` and `hetzner-contact.html`

The old `_resources/design-guide/` design-competition synthesis was deleted on 2026-05-05 because it conflicted with the approved Civic Celebration + Slate Blue/Berry + Brand Direction visual contract and kept reintroducing light-blue/blush styling. Do not recreate it or treat old screenshots/TSX from that direction as current design guidance.

The legacy_source snapshots are canonical for the rebuilt `/book` and `/contact` form shape where explicitly stated. They are not blanket authority for the rest of the system.

## Current Work Selection

Use `locally-twisted-queue.md` and the active `workstreams/*.md` files for current P0 selection. The old April `/book` P0 is superseded: `/book` now redirects to `/contact?intent=quick`, and `/contact` is the customer inquiry route.

Current active lanes are launch proof, paperwork/backend automation, fail-loud record-level hardening, brand/shop/portfolio follow-through, and cutover readiness. Before changing any route, form, catalog, checkout, payment, document, or backend automation behavior, verify the current lane file and run the matching verifier.

## Trust Rules

- Never claim a route, form, count, or visual state is working without verification.
- Say when something is unverified.
- Prefer small complete slices over broad rewrites.
- If prior docs conflict, verify against the running system and tell GL what changed.
- Do not hide errors behind "probably" or "should".
