# Locally Twisted: ERPNext Migration

> 2026-06-28 update: This planning doc predates the current three-brand DBA
> boundary. Current scope is one Locally Twisted accounting/ERPNext operating
> company with three protected brand lanes: Locally Twisted, Commercial Balloon
> Decor, and Memorial Balloons. Older "multi-company" rejection language means
> do not mix unrelated clients or create unapproved ERPNext companies/sites; it
> does not reject the current approved DBA/service-brand lane model. Read
> `../BRAND-BOUNDARY.md` before relying on this file for brand/accounting scope.

## What This Is

Locally Twisted is a 27-year-old Utah balloon-decor and event-services business owned by Jeff Kimber. Until now, LT has run on improvisation — manual records, paper notes, QuickBooks for accounting, and a website built years ago that customers still reach but that has degraded beyond practical repair.

**This project is a migration of LT's business intent + catalog data into a fresh ERPNext v15 install** (frame revised 2026-04-30 — see `locally-twisted-decisions.md`; supersedes the 2026-04-26 "first professional business platform / new build, not a migration" reframe). "Fresh install" because ERPNext was greenfield — no translated modules, no database dump import, and no inherited configuration. "Migration" because catalog records, the Lead schema, the `/book` and `/contact` form intent, business policies, brand identity, and voice rules were rebuilt from approved source evidence for the ERPNext destination. Current database totals must be rechecked before use. At cutover (Phase 6), the new ERPNext storefront replaces `locallytwisted.com` at the same domain.

End-to-end destination scope: customer-facing website + ecommerce storefront + lead intake forms + operator workflow (lead → quote → booking → calendar → project) + invoicing + Stripe payments + Utah tax compliance + native ERPNext accounting + native ERPNext HRMS payroll + customer self-service portal.

The build runs locally on `:8081` until it's ready to show Jeff. At cutover it deploys to Frappe Cloud and ownership transfers to Jeff Kimber's own account.

The destination is self-contained inside ERPNext/Frappe and the committed LT source resources.

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

- **Automated translation tooling into ERPNext** — the migration carries approved business intent and catalog data, not imported modules, inherited schemas, or blind field mapping. Product and form work must be hand-built for the ERPNext/Frappe destination.
- **Standalone Services index page** — redundant. Service info lives on individual service pages and on the homepage. (GL directive 2026-04-26)
- **Standalone About page** — about info distributes across the site (homepage, service pages); a brief summary lands on the contact page. (GL directive 2026-04-26)
- **Gusto / third-party payroll** — agency standard is ERPNext native HRMS for all clients. (Decision 2026-04-26)
- **Unapproved multi-company or multi-client mixing in one ERPNext site** —
  rejected; per-client isolation remains structural. This does not reject the
  2026-06-28 approved LT DBA/service-brand lane model for Locally Twisted,
  Commercial Balloon Decor, and Memorial Balloons under the same LT accounting
  operation.
- **Hosting on current import capture / self-hosted** — superseded by Frappe Cloud (managed, transferable per-site).
- **Client-facing replacement talk before there is a working system to show** — Jeff-facing communication stays focused on the usable ERPNext replacement GL can demo.

## Context

- **Trust state with Jeff.** Jeff has paid GL real money and watched the existing website crash in meetings repeatedly. Trust has been eroded but not lost. The recovery move is to deliver a working replacement before announcing the verdict — a finished thing, not a fresh apology. This is the Core Value translated into operational behavior.
- **Jeff's working style.** Hyperactive + inattentive ADHD. Tangent-jumps in meetings. Won't audit code, won't read documentation. Will tell GL when something on the website confuses him but won't articulate why well. Meetings need to be tightly scoped and visually anchored. End results matter; infrastructure does not.
- **GL's working style.** Inattentive ADHD. Designer / creator, not a coder.
  Needs the agent to take the lead on technical work, flag dependencies GL
  doesn't know to ask about, apply obvious companion features and report back.
  "Make me look good" was a stated request 2026-04-26 — the operating mode.
- **Why ERPNext.** The 2026-04 open-source ERP expedition (5 source-separated researchers, MODERATE confidence) found ERPNext is the only viable open-source replacement for LT's feature surface. Critically: ERPNext gives BBC room to build loud failures, visible records, and fast detection into the workflows. Frappe Cloud reduces upgrade risk vs. self-hosted.
- **Reference material.** All canonical resources for this build live in
  `_resources/` (style guide, business policies, tax data) and current
  ERPNext/Frappe source docs. Retired research material is not an active source
  after cutover.
- **First BBC client.** Locally Twisted is BBC's first client. The work needs to be exemplary. Jeff plans to refer other businesses; the referral pipeline depends on him being delighted by the deliverable.

## Constraints

- **Stack:** ERPNext v15.105.0 + Frappe v15.106.0 in the current local bench. Pinned ERPNext v15 image, no rolling major line.
- **Local environment:** Wardenclyffe Kubuntu with local Docker Engine. LT's
  stack runs on `:8081` when intentionally started.
- **Cost:** $0 during build. Frappe Cloud Sites plan ($5/mo) only at deployment. Bill follows site ownership after transfer.
- **Stealth on the verdict:** Jeff knows there's an audit; he does not yet know the audit's conclusion. No artifact on disk should leak that conclusion in a way that would surprise him. Internal planning docs (this file included) stay in BBC's hands.
- **Verification before any client-visible work.** Verify in the actual UI before claiming anything is done. Repeats of "deployed without checking" failures are not acceptable.
- **Compliance:** Per-business isolation is structural, not policy-based. Code-yes / data-no boundary verified post-transfer.
- **Loud failure rule.** Every form, every cross-system handoff, and every
  external API call must fail loudly and be observable to user, developer, and
  monitor. Current operating rules live in `AGENTS.md` and
  `capabilities/recipes/fail-loud-operating-law.md`.

## Key Decisions

| Date | Decision | Why |
|---|---|---|
| 2026-04-30 | Project frame revised to "migration of business intent + catalog data into a fresh ERPNext install" | Supersedes the 2026-04-26 reframe; the technical reality (catalog data ported 2026-04-30, form intent + policies carried across, domain cutover at Phase 6) is migration shape. Hand-build-not-auto-translate is the constraint that survives. (See decisions log 2026-04-30 frame entry.) |
| 2026-04-26 | Earlier reframe to "first professional business platform / new build" | Superseded 2026-04-30; the useful part that remains is avoiding too-mechanical translation framing. |
| 2026-04-26 | Customer-facing website + storefront is Phase 1 | Visual + UX proof point. If ERPNext can't deliver this, GL pivots before building backend |
| 2026-04-26 | All clients default to ERPNext native HRMS payroll (no third-party payroll integration) | Agency-wide standard; one less integration to learn / configure / hand off |
| 2026-04-26 | Drop standalone About page and standalone Services index | Redundant; info distributes across homepage + service pages; brief about summary lands on contact page |
| 2026-04-26 | All policy and brand resources live in `_resources/` and are scrubbed of platform-specific references | Project must stand alone |
| 2026-04-25 | ERPNext v15.105.0 (latest stable v15 patch) pinned | Past Stripe-broken window; latest patch on a mature line |
| 2026-04-25 | Local Docker for build, Frappe Cloud Sites plan for production | Local is free + breakable; Frappe Cloud is managed + transferable per-site |
| 2026-04-25 | Site-level transfer (not bench-level or server-level) | Self-service in Frappe Cloud dashboard |

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
*Last updated: 2026-04-30 — frame revised to "migration of business intent + catalog data into a fresh ERPNext install" (supersedes the 2026-04-26 "first professional business platform / new build" reframe).*
