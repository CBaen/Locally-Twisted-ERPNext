# Locally Twisted: Odoo → ERPNext Migration

## What This Is

A stealth migration of Locally Twisted's entire business platform from Odoo to ERPNext v15.105.0 — backend, automations, portal, theme, website, and ecommerce — built in parallel to the live Odoo install so Jeff (the business owner) doesn't see it until it's ready. Customer-facing surfaces (website + ecommerce + checkout) are not just translated; they're rebuilt to a higher quality bar than the current Odoo version. The eventual switchover replaces a system that has crashed in front of Jeff during demos with one that demonstrably won't.

## Core Value

**Jeff's next experience with this system makes him feel relieved, not nervous.** The migration must land as a *visible upgrade* that compensates for the cumulative trust damage of the prior Odoo failures. If everything else works but Jeff's first interaction is "huh, this is just Odoo with different colors," the project failed. If everything else slips but Jeff's first interaction is "this is so much better," the project succeeded.

## Requirements

### Validated

<!-- Shipped and confirmed valuable. -->

- ✓ ERPNext v15.105.0 install for Locally Twisted running locally on `:8081`, fully isolated from any other site — initialized 2026-04-25
- ✓ Odoo install at `C:\Users\baenb\projects\locally-twisted-odoo` continues running unchanged in parallel — no destructive moves while migration is in flight

### Active

<!-- Current scope. Building toward these. -->

- [ ] **Inventory pass.** Read the entire `C:\Users\baenb\projects\locally-twisted-odoo` codebase — manifest, models, views, controllers, automations, security, data, theme, snippets — and produce a structured map of what exists, what's load-bearing, what's already broken, what's half-finished, what's not in production. Status of non-production work noted explicitly.
- [ ] **Production `arch_db` inventory.** Read Locally Twisted's production database to inventory Jeff's UI-edited content (blog posts, product descriptions, page text). Surfaces irreplaceable content that doesn't live in source.
- [ ] **Backend replication.** Translate Odoo data models, security rules, and 17 cross-module automations into ERPNext equivalents (DocTypes, Server Scripts, Notification framework).
- [ ] **Utah tax replication.** Re-implement 16 tax rates + 105 fiscal positions (1,785 lines of `data/tax_data.xml`) as ERPNext Tax Templates.
- [ ] **Portal replication.** Translate the 333-line custom Odoo portal controller into ERPNext's portal model.
- [ ] **Stripe integration verified end-to-end.** Confirm live payment flow works on ERPNext v15.105.0 webshop (past the Oct 2024–Feb 2025 broken window). Test mode + at least one production-mode dry run before cutover.
- [ ] **Website + ecommerce rebuild/redesign — high quality, payment-ready.** Customer-facing surfaces (storefront, product pages, cart, checkout, account, order history) are *rebuilt* to a higher visual + UX quality than the current Odoo version. Brand identity preserved (fonts, colors, voice); UX freed to be better. Must be ready to take real payments at cutover.
- [ ] **Variant pricing.** Replicate `price_extra` per variant in the ERPNext webshop checkout flow.
- [ ] **Theme + brand parity.** Internal admin surfaces, transactional emails, and document templates (invoice/quote PDFs) match Locally Twisted's existing brand language so the transition feels continuous.
- [ ] **Verification harness.** Side-by-side smoke tests comparing Odoo and ERPNext behavior for every critical user journey (browse → cart → checkout → confirmation; portal login → order history; admin → quote → invoice → payment). Repeat-failure protection.
- [ ] **Frappe Cloud deployment + transfer.** Spin up the production site on Frappe Cloud at handoff time. Transfer site ownership from Cameron's account to Jeff's `locallytwisted@gmail.com`. Verify code-only / data-no boundary post-transfer.
- [ ] **Cutover sequence.** DNS flip, Odoo decommission, Jeff onboarded to the new system. Stealth maintained until GL chooses to surface it.

### Out of Scope

<!-- Explicit boundaries. Includes reasoning to prevent re-adding. -->

- **Other Built by Cameron concerns** — BBC's own internal ops install, future attorney clients, agency platform decisions. Each is its own project. This GSD project is *only* the LT migration.
- **jakenfriends migration** — archived. Friend isn't interested.
- **Lawyer / `Example_Lawyer_*` template** — deferred until LT migration is done.
- **Multi-company-in-one-site model** — rejected. Compromises isolation.
- **Self-hosted Hetzner production** — superseded by Frappe Cloud (per off-Odoo expedition recommendation; GL accepted 2026-04-25).
- **Automated Odoo→ERPNext content migration tool** — none of production quality exists. Hand-rebuild guided by the existing implementation.
- **Telling Jeff before it's ready** — stealth is a hard constraint. The Odoo install stays running normally throughout build.

## Context

- **Trust repair.** Multiple prior instances have crashed Jeff's Odoo production, including during a live walkthrough. Per `feedback_odoo_deployment_trust.md`: "GL does not trust instances with Odoo deployments. This is earned distrust, not caution." The migration is the remedy — not just a platform change but the structural fix to the failure classes (silent COW drift, asset bundle breaks, form widget DOM traps) that did the damage.
- **Off-Odoo expedition completed 2026-04** (5 source-separated researchers, MODERATE confidence). Convergent finding: ERPNext is the only viable open-source replacement for LT's feature surface. Critical caveats: ERPNext fails *noisily* (loud crashes, fast detection) rather than *silently* (Odoo's failure mode). Frappe Cloud reduces upgrade risk vs self-hosted. v15.105.0 is past the Stripe-broken window of v15.0–.52 (Oct 2024–Feb 2025).
- **Hidden migration cost: `arch_db`.** The expedition flagged that anything Jeff has edited via Odoo's website editor lives only in the production database, not in git. Could be substantial or negligible — must be inventoried before scope is finalized.
- **Existing Odoo build is rich.** 17 cross-module automations, 14 migration scripts (testifying to past upgrade pain), custom QWeb snippets, 333-line custom portal controller, 1,785-line tax XML, custom Stripe controller. Migration is rebuild work, not transfer.
- **Built by Cameron is the venue, not the project.** The LT migration lives at `C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\locally-twisted\Locally-Twisted-Backend\frappe_docker\` because BBC is the convenient session-start root. Other BBC concerns are separate projects.
- **Frappe Cloud transfer mechanism confirmed.** Site-level ownership transfer is self-service in the dashboard (Actions tab). When Jeff is ready, he creates a Frappe Cloud account at `locallytwisted@gmail.com`, GL transfers the LT site to his team, billing follows ($5/mo per site).

## Constraints

- **Stack:** ERPNext v15.105.0 + Frappe v15 (bundled). Pinned tag, no rolling.
- **Local environment:** Windows 11 + Docker Desktop (WSL2 backend, 8 GB / 4 CPU). LT's stack runs on `:8081`; Odoo install at `locally-twisted-odoo` runs separately.
- **Cost:** $0 during build. Frappe Cloud Sites plan ($5/mo) only at deployment time. Bill follows site ownership after transfer.
- **Stealth:** Jeff cannot know about the migration plan until GL chooses to surface it. The Odoo install at `C:\Users\baenb\projects\locally-twisted-odoo` continues running normally throughout build.
- **Verification before any client-visible work.** Repeats of "deployed without checking" Odoo failures are not acceptable. Smoke tests, screenshots, end-to-end checks — every step. See `feedback_odoo_deployment_trust.md` for the trust-rebuilding protocol.
- **Compliance:** Per-business isolation is structural, not policy-based. Code-yes / data-no boundary verified post-transfer.
- **Read access to Locally Twisted production database** granted by GL 2026-04-25 for the `arch_db` inventory step.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| ERPNext v15.105.0 (latest stable v15 patch) | Past the Stripe-broken window; latest patch on a mature line. | ✓ Good |
| LT's ERPNext stack on port 8081, fully isolated from BBC's on 8080 | Each business gets its own everything. | ✓ Good |
| Local Docker for build, Frappe Cloud for production | Local is free + breakable; Frappe Cloud is managed + transferable per-site. | ✓ Good |
| Site-level transfer, not bench-level or server-level | Simplest transfer path; self-service in the dashboard. | ✓ Good |
| Customer-facing surfaces are rebuilt/redesigned, not just translated | Quality lift is part of the trust-repair. Brand identity preserved; UX freed to be better. | — Pending |
| Internal admin surfaces translated 1:1 where possible | Continuity for Jeff's existing workflows. | — Pending |
| Inventory pass before any planning | Migration plan built on guesses is how trust gets re-broken. | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-25 after initialization (post-rewrite to lead with the LT migration, not the agency framing)*
