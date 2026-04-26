# Roadmap: Locally Twisted — First Professional Business Platform

## Overview

Six phases organized around what Locally Twisted delivers to whom.

**Phase 1 is the customer-facing proof point.** If ERPNext can't deliver a visual + UX experience that's at least as good as what GL approved on the prior attempt, GL pivots away from ERPNext before building further. This is the off-ramp.

**Phases 2-6 build on Phase 1's foundation:** lead intake, operator workflow, money & compliance, customer portal, cutover. Each phase ends with something Jeff (and customers) can see and use.

The brand foundation (style guide tokens, fonts, colors, typography) is baked into Phase 1; it's not a separate phase. Resources are pre-positioned in `_resources/` so Phase 1 starts on a complete brand baseline.

## Phases

- [ ] **Phase 1 — Customer site + storefront (the proof point).** Public website + ecommerce. Decision gate: does ERPNext deliver?
- [ ] **Phase 2 — Lead intake.** Customer forms (`/book`, `/contact`) into the existing Lead schema with confirmation and Contact dedup.
- [ ] **Phase 3 — Operator workflow.** Lead → Quote → Booking → Calendar → Project Task. The pipeline Jeff runs his business through.
- [ ] **Phase 4 — Money & compliance.** Invoicing, Stripe, Utah tax, ERPNext accounting (replaces QuickBooks), ERPNext HRMS payroll.
- [ ] **Phase 5 — Customer portal.** Logged-in customer can see orders, invoices, quotes, account.
- [ ] **Phase 6 — Cutover & handoff.** Frappe Cloud, DNS, ownership transfer, Jeff onboarded, old site decommissioned.

## Phase Details

### Phase 1 — Customer site + storefront

**Goal:** A customer can land on the site, browse what LT makes, learn enough to choose LT, and either complete a small purchase through the store or know how to start a custom booking conversation. The site looks and feels professional enough that Jeff says "yes, this is the LT experience" without prompting.

**Surfaces in scope:**

| Surface | Source | Notes |
|---|---|---|
| Header + footer | Carry forward design pattern | Resolves the super-menu question (see decision gate below) |
| Landing page | Style-guide-driven build | Hero, services snapshot, featured products, social proof, closing CTA |
| Balloon Twisting + Face Painting page | Carry forward content + visuals | Was already correct on prior attempt |
| Contact page | Carry forward + add brief "about" summary | About info merges in here per GL directive |
| Accessibility page | Build new with caveats | See "Accessibility statement nuance" decision gate below |
| Refund Policy page | Build new from `_resources/policies/legal-interview-answers.md` Part 2C | Plain-language version of the cancellation rules |
| FAQ page | Build new from `_resources/policies/` | Pricing math, no-combination-discount framing, any-character rule, service area, deposit & cancellation, weather |
| Products listing page | Rebuild on Frappe webshop primitives | Visual pattern from prior attempt |
| Individual product pages | Rebuild on Frappe webshop primitives | Variant pricing must work; visual pattern from prior attempt |
| Cart + checkout | Rebuild on Frappe webshop primitives | Stripe wired in Phase 4; checkout shell built here, payments stubbed until Phase 4 |
| Pricing calculator (artist services) | Build new | Per-artist line-item math; "no combination" framing prominent |

**Surfaces explicitly NOT in scope** (per GL 2026-04-26):
- Standalone About page
- Standalone Services index page

**Decision gates inside Phase 1** (need GL input before/during build):
1. **Header navigation structure.** Are "Special Occasions" / "Holidays & Seasons" / "What We Make" each their own mega-menu, or is "What We Make" the only product menu and the others become filters / landing pages? See `.planning/decisions/header-navigation.md`.
2. **Accessibility statement nuance.** GL flagged the small-business lawsuit risk of accessibility statements. Three options: (a) publish a real statement and commit to actually meeting WCAG 2.1 AA, (b) publish a brief statement of intent without specific commitments, (c) skip the published statement entirely. See `.planning/decisions/accessibility-statement.md`.
3. **Blog presence.** The style guide includes a "Kindergarten Teacher" voice for a blog. Do we ship Phase 1 with the blog framework in place (even if empty) or defer until later?
4. **Real photography sourcing.** Style guide says "Photography is the star." Where does real LT event photography live, or do we ship Phase 1 with stubbed/placeholder slots?

**Success criteria:**
1. Anonymous visitor can browse from landing page through service pages and product pages without hitting a broken layout, missing image, or JavaScript error
2. Anonymous visitor can add a product to cart and reach a checkout page (payment integration stubbed until Phase 4)
3. Visual identity matches `_resources/STYLE-GUIDE.md` — verified by side-by-side check against the spec, not by self-report
4. SEO baseline: each page has unique title + meta description, semantic HTML, schema.org LocalBusiness markup, OpenGraph tags
5. AEO/GEO baseline: FAQ schema on the FAQ page, LocalBusiness schema with service area on the homepage and contact page
6. WCAG 2.1 AA passes on every page in scope — verified by automated tool + manual keyboard navigation
7. Mobile-first: every page works at 375px width with no horizontal scroll, all touch targets ≥44px
8. **GL viewing the result says "yes — show this to Jeff."** This is the off-ramp gate.

### Phase 2 — Lead intake

**Goal:** A customer who fills `/book` or `/contact` on the new site lands a Lead in ERPNext with all fields mapped correctly, deduped against existing Contacts, and gets an immediate acknowledgment. Jeff sees the new lead in his admin within minutes.

**Depends on:** Phase 1 (site is live); existing Lead schema already in ERPNext.

**Success criteria:**
1. Submitting `/book` form posts every field into the matching ERPNext Lead Custom Field — verified by completing one of each branch (decor, twisting, painting, delivery-only, package, other)
2. Submitting `/contact` form (simpler) creates a Lead with the right subset of fields populated
3. If the customer's email or phone matches an existing Contact, the Lead links to that Contact; otherwise a new Contact is created (Customer/Contact dedup logic, mirrors prior `_find_matching_partner`)
4. Customer sees a confirmation page (not a blank screen) and receives an acknowledgment email within 5 minutes
5. **Loud failure verified:** intentionally break the form with a malformed submission and confirm the customer sees a real error message, the failure is logged at ERROR level with the payload, and a monitor alert fires

### Phase 3 — Operator workflow

**Goal:** Jeff (or a team member) can take a new Lead and run it through to a completed event without leaving ERPNext. Every screen uses plain language Jeff and his employees recognize, not ERPNext jargon.

**Pipeline:** Lead → Quote → Booking confirmation (deposit invoice if needed) → Calendar event → Project task → Day-of crew + supplies dispatch → Event completion → Final invoice → Review request.

**Success criteria:**
1. Jeff can move a Lead to a Quote in 3 clicks or fewer
2. Quote PDF uses LT brand fonts and colors and shows the per-artist pricing breakdown for service bookings
3. Booking confirmed → calendar event auto-created with the right date, location, crew assignment fields populated
4. Booking confirmed → project task auto-created with crew, supplies, equipment checklist fields
5. Day-of view: a crew member can pull up the day's events on mobile and see customer name, address, services, time, contact phone, supplies needed
6. Every cross-model automation logs entry + exit at INFO level (loud-failure compliance)
7. Plain-language labels everywhere: no "Qualification Status," no "Opportunity," no "Pipeline Stage." See CLAUDE.md Voice & Language table.

### Phase 4 — Money & compliance

**Goal:** Money in (Stripe payments + invoicing), money out (vendor / payroll), and compliance (Utah tax + accounting) are all handled inside ERPNext. Jeff can stop using QuickBooks. Payroll is on Frappe HRMS.

**Components:**
- Stripe end-to-end (test mode + production-mode dry run with real card)
- Invoice generation with LT brand templates
- Utah tax: city-based auto-calc applied to every invoice
- Tax research from `_resources/utah-tax-rates-2026q2.md` integrated into Tax Templates
- Corporate Net 30 + 10% simple late fee logic per `_resources/policies/deposits.md`
- ERPNext native accounting set up; QuickBooks data migration planned (separate sub-task)
- Frappe HRMS installed and configured for LT's salary structure

**Success criteria:**
1. Test-mode checkout completes end-to-end and the order has a Stripe charge ID stored
2. Stripe webhook delivery verified: webhook fires, ERPNext endpoint receives, order status updates
3. At least one production-mode dry run with a real card; charge appears in Stripe dashboard
4. Invoice line items show Utah sales tax as its own visible line; rate matches the delivery / event city
5. Corporate invoices age correctly: day 31 produces a late-fee notification; "may waive" + "may suspend" workflow gives Jeff one-click discretion
6. ERPNext accounting books the same numbers Jeff's accountant would see in QuickBooks for the same transactions (verified for at least 5 representative transactions)
7. Payroll: Frappe HRMS produces a sample payroll run for Jeff's actual employee structure
8. North Peak (Jeff's accountant) gets a heads-up that LT is moving off QuickBooks; transition plan agreed with her

### Phase 5 — Customer portal

**Goal:** A logged-in LT customer can see their order history, invoices, quotes, and account details through the ERPNext portal.

**Depends on:** Phase 4 (so portal can show invoices and orders that exist).

**Success criteria:**
1. Customer can log in to portal using their email + password
2. Logged-in customer sees their full order + booking history with line items and totals
3. Logged-in customer can view and download invoices and quotes as branded PDFs
4. Customer can update their email, password, address through the portal
5. Portal session verified: login → orders → invoice download → logout — no errors

### Phase 6 — Cutover & handoff

**Goal:** Locally Twisted's business runs on the new system. Jeff owns his Frappe Cloud account. The old `locallytwisted.com` site is decommissioned.

**Success criteria:**
1. ERPNext site deployed to Frappe Cloud at `locallytwisted.com` over HTTPS
2. DNS flipped: `locallytwisted.com` resolves to the Frappe Cloud site
3. The LT site is owned by Jeff Kimber's Frappe Cloud team account, not Cameron's
4. Cameron retains developer-role access only — verified by trying (and failing) to access billing
5. Jeff can log in, place a test order in his own admin, and navigate without assistance
6. Old `locallytwisted.com` site (the dying current one) is decommissioned and a snapshot is archived
7. References retired per CLAUDE.md "Reference Disposition": `locally-twisted-odoo/` archived to GitHub and removed from local; failed Hetzner deployment shut down; GitHub Odoo repo marked read-only

## Progress

| Phase | Status | Plans | Completed |
|-------|--------|-------|-----------|
| 1. Customer site + storefront | Not started | 0 / TBD | — |
| 2. Lead intake | Not started | 0 / TBD | — |
| 3. Operator workflow | Not started | 0 / TBD | — |
| 4. Money & compliance | Not started | 0 / TBD | — |
| 5. Customer portal | Not started | 0 / TBD | — |
| 6. Cutover & handoff | Not started | 0 / TBD | — |

---
*Last updated: 2026-04-26 — frame reset (replaces prior 10-phase translation-centric ROADMAP).*
