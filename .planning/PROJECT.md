# Locally Twisted: ERPNext Migration

## What This Is

Locally Twisted is a 27-year-old Utah balloon-decor and event-services business owned by Jeff Kimber. Until now, LT has run on improvisation — manual records, paper notes, QuickBooks for accounting, a website built years ago that customers still reach but that has degraded beyond practical repair. A prior attempt to give LT a backend (an Odoo build) failed in testing — never went live to customers and Jeff was never told the audit's verdict.

**This project is a migration of LT's business intent + catalog data into a fresh ERPNext v15 install** (frame revised 2026-04-30 — see `locally-twisted-decisions.md`; supersedes the 2026-04-26 "first professional business platform / new build, not a migration" reframe). "Fresh install" because ERPNext was greenfield — no auto-translated Odoo modules, no DB dumps imported, no Odoo configuration carried across; everything was hand-built informed by Odoo discovery. "Migration" because the catalog data (53 Website Items / 10,578 variants / 10,613 Item Prices, ported 2026-04-30), the 45-field Lead schema, the `/book` and `/contact` form intent, the business policies, the brand identity, and the voice rules were all carried across from the Odoo attempt — and at cutover (Phase 6), the new ERPNext storefront replaces `locallytwisted.com` at the same domain.

End-to-end destination scope: customer-facing website + ecommerce storefront + lead intake forms + operator workflow (lead → quote → booking → calendar → project) + invoicing + Stripe payments + Utah tax compliance + native ERPNext accounting + native ERPNext HRMS payroll + customer self-service portal.

The build runs locally on `:8081` until it's ready to show Jeff. At cutover it deploys to Frappe Cloud and ownership transfers to Jeff Kimber's own account.

The Odoo work informs this build (forms, models, copy, business policies all came out of that attempt's discovery work) but the destination doesn't depend on the Odoo system continuing to exist. See `CLAUDE.md` "Reference Disposition" for how the Odoo references will be retired.

## Core Value

**Jeff's first interaction with the destination system makes him feel equipped — like he finally has the tools he should have had years ago.** He doesn't need to know it took two attempts. The end result must look obvious, professional, and trustworthy: the system a serious balloon business in Utah would have. If the customer-facing experience doesn't pass that bar in Phase 1, ERPNext is the wrong destination and we pivot before building further.

## Requirements

### Validated

<!-- Shipped and confirmed valuable. -->

- ✓ ERPNext v15.105.0 install for Locally Twisted running locally on `:8081`, fully isolated — initialized 2026-04-25
- ✓ Lead schema in ERPNext built and stable: 45+ Custom Fields on Lead, sectioned, plain-language relabels of standard fields, "Additional Information" tab hidden, file upload to 25 MB. Feeds directly into Phase 2 (Lead Intake)
- ✓ Business policies fully captured (legal interview + 5 supporting business rules) — see `_resources/policies/`. Sufficient for attorney to draft v1 Client Event Contract.
- ✓ Brand identity captured — see `_resources/STYLE-GUIDE.md`. Color system, typography, components, "Quiet Confidence" voice, accessibility (WCAG 2.1 AA), blog "Kindergarten Teacher" voice, photography rules.

### Active

<!-- Current scope. Building toward these. See ROADMAP.md for phase ordering. -->

- [ ] **Customer-facing site + storefront (Phase 1 — the proof point).** Header, footer, landing page, balloon-twisting-and-face-painting service page, contact page, accessibility statement, refund policy page, FAQ, products browse + product detail + cart + checkout flow, pricing calculator. Visually matches the brand identity in `_resources/STYLE-GUIDE.md`. **If this doesn't pass the visual + UX bar, ERPNext gets reconsidered.**
- [ ] **Lead intake (Phase 2).** `/contact` and `/book` forms post into the existing ERPNext Lead schema with field mapping, Contact dedup, and a customer acknowledgment. Loud-failure protected.
- [ ] **Operator workflow (Phase 3).** Backend pipeline Jeff and his team run a job through: Lead → Quote → Booking confirmation → Calendar event → Project task → Day-of operations. Plain-language labels on every screen.
- [ ] **Money & compliance (Phase 4).** Invoicing, Stripe end-to-end, Utah tax (city-based auto-calc), ERPNext accounting (replaces QuickBooks), ERPNext HRMS payroll setup. Late-fee + corporate Net 30 + deposit logic per `_resources/policies/`.
- [ ] **Customer portal (Phase 5).** Logged-in customer can see orders, invoices, quotes, account.
- [ ] **Cutover & handoff (Phase 6).** Frappe Cloud deploy, DNS to ERPNext, ownership transfer to Jeff Kimber's account, Jeff onboarded, current `locallytwisted.com` site decommissioned.

### Out of Scope

<!-- Explicit boundaries. Reasoning included so they don't get re-added. -->

- **Automated Odoo→ERPNext translation tooling** — the Odoo dir is reference material; we hand-build informed by what was learned. The migration carries business intent + catalog data, not modules or schemas. (Catalog port 2026-04-30 was a record-by-record port from the live Odoo site, not an automated module/data conversion.)
- **Standalone Services index page** — redundant. Service info lives on individual service pages and on the homepage. (GL directive 2026-04-26)
- **Standalone About page** — about info distributes across the site (homepage, service pages); a brief summary lands on the contact page. (GL directive 2026-04-26)
- **Gusto / third-party payroll** — agency standard is ERPNext native HRMS for all clients. (Decision 2026-04-26)
- **Surfacing the failed Odoo attempt to Jeff** — Jeff knows there's an audit; he doesn't yet know the prior Odoo attempt failed in testing. Internal docs use the migration framing freely; Jeff-facing communications still don't leak that context until Phase 1 is in a state GL can demo. (Was framed as "no migration framing of any kind" pre-2026-04-30; the actual constraint is Jeff-disclosure, not internal vocabulary.)
- **Multi-company in one ERPNext site** — rejected; per-client isolation is structural.
- **Hosting on Hetzner / self-hosted** — superseded by Frappe Cloud (managed, transferable per-site).
- **Telling Jeff before there's a working replacement to show** — Jeff has been told there's an audit / debug / stress test of his existing system. The audit's conclusion (that the prior platform isn't sufficient) is not surfaced to him until Phase 1 is in a state GL can demo. Until then, all docs that mention the verdict stay internal to this folder.

## Context

- **Trust state with Jeff.** Jeff has paid GL real money and watched the existing website crash in meetings repeatedly. Trust has been eroded but not lost. The recovery move is to deliver a working replacement before announcing the verdict — a finished thing, not a fresh apology. This is the Core Value translated into operational behavior.
- **Jeff's working style.** Hyperactive + inattentive ADHD. Tangent-jumps in meetings. Won't audit code, won't read documentation. Will tell GL when something on the website confuses him but won't articulate why well. Meetings need to be tightly scoped and visually anchored. End results matter; infrastructure does not.
- **GL's working style.** Inattentive ADHD. Designer / creator, not a coder. Needs Claude to take the lead on technical work, flag dependencies GL doesn't know to ask about, apply obvious companion features and report back. "Make me look good" was a stated request 2026-04-26 — the operating mode.
- **Why ERPNext.** Off-Odoo expedition (2026-04, 5 source-separated researchers, MODERATE confidence) found ERPNext is the only viable open-source replacement for LT's feature surface. Critically: ERPNext fails *noisily* (loud crashes, fast detection) where the prior platform failed *silently* (the failure mode that did the trust damage). Frappe Cloud reduces upgrade risk vs. self-hosted.
- **Reference material.** All canonical resources for this build live in `_resources/` (style guide, business policies, tax data). The Odoo dir, the failed Hetzner site, and the Odoo GitHub repo are reference-only and will be retired — see `CLAUDE.md` "Reference Disposition." After cutover, they don't exist.
- **First BBC client.** Locally Twisted is BBC's first client. The work needs to be exemplary. Jeff plans to refer other businesses; the referral pipeline depends on him being delighted by the deliverable.

## Constraints

- **Stack:** ERPNext v15.105.0 + Frappe v15 (bundled). Pinned tag, no rolling.
- **Local environment:** Windows 11 + Docker Desktop (WSL2 backend, 8 GB / 4 CPU). LT's stack runs on `:8081`.
- **Cost:** $0 during build. Frappe Cloud Sites plan ($5/mo) only at deployment. Bill follows site ownership after transfer.
- **Stealth on the verdict:** Jeff knows there's an audit; he does not yet know the audit's conclusion. No artifact on disk should leak that conclusion in a way that would surprise him. Internal planning docs (this file included) stay in BBC's hands.
- **Verification before any client-visible work.** Verify in the actual UI before claiming anything is done. Repeats of "deployed without checking" failures are not acceptable.
- **Compliance:** Per-business isolation is structural, not policy-based. Code-yes / data-no boundary verified post-transfer.
- **Loud failure rule.** Per global rule at `C:\Users\baenb\.claude\rules\loud-failure.md`. Every form, every cross-system handoff, every external API call must fail loudly and be observable to user / developer / monitor.

## Key Decisions

| Date | Decision | Why |
|---|---|---|
| 2026-04-26 | Project reframed from "Odoo → ERPNext migration" to "First professional business platform for LT, built on ERPNext" | Jeff was never told the prior attempt happened; the migration framing leaks that context and structures the work around the wrong arc |
| 2026-04-26 | Customer-facing website + storefront is Phase 1 | Visual + UX proof point. If ERPNext can't deliver this, GL pivots before building backend |
| 2026-04-26 | All clients default to ERPNext native HRMS payroll (no third-party payroll integration) | Agency-wide standard; one less integration to learn / configure / hand off |
| 2026-04-26 | Drop standalone About page and standalone Services index | Redundant; info distributes across homepage + service pages; brief about summary lands on contact page |
| 2026-04-26 | All policy and brand resources live in `_resources/` and are scrubbed of platform-specific references | Project must stand alone; Odoo dir will be retired |
| 2026-04-25 | ERPNext v15.105.0 (latest stable v15 patch) pinned | Past Stripe-broken window; latest patch on a mature line |
| 2026-04-25 | Local Docker for build, Frappe Cloud Sites plan for production | Local is free + breakable; Frappe Cloud is managed + transferable per-site |
| 2026-04-25 | Site-level transfer (not bench-level or server-level) | Self-service in Frappe Cloud dashboard |
| 2026-04-25 | Don't modify anything in `locally-twisted-odoo/` | Read-only reference; preserves prior project's own gates and history |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition:**
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions

**After each milestone:**
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-26 — frame reset (replaces prior "Odoo → ERPNext migration" framing).*
