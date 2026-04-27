# Roadmap: Locally Twisted — First Professional Business Platform

## Overview

Six phases organized around what Locally Twisted delivers to whom.

**Phase 1 is the customer-facing proof point** — built lookbook-forward (portfolio leads, custom work goes through inquiry, small shop sidebar). If ERPNext / Frappe can't deliver this experience, GL has the off-ramp before building further. Decision recorded at `.planning/decisions/site-shape.md`.

**Phases 2-6 build on Phase 1's foundation:** form-handling depth, operator workflow, money & compliance, customer portal, cutover. Each phase ends with something Jeff (and customers) can see and use.

The brand foundation (style guide tokens, fonts, colors, typography) is baked into Phase 1; it's not a separate phase. Resources are pre-positioned in `_resources/` so Phase 1 starts on a complete brand baseline.

## Phases

- [~] **Phase 1 — Customer site (lookbook-forward, with small shop).** Public website organized around portfolio + inquiry, with a small e-commerce sidebar for sub-$200 items. **In flight; ~5 of ~14 slices done.**
- [ ] **Phase 2 — Form-handling depth.** Contact dedup, customer acknowledgment email, loud-failure compliance audit, monitor alerts. (`/book` itself moved into Phase 1; this phase covers the depth around all forms.)
- [ ] **Phase 3 — Operator workflow.** Lead → Quote → Booking → Calendar → Project Task. The pipeline Jeff runs his business through.
- [ ] **Phase 4 — Money & compliance.** Invoicing, Stripe, Utah tax, ERPNext accounting (replaces QuickBooks), ERPNext HRMS payroll.
- [ ] **Phase 5 — Customer portal.** Logged-in customer can see orders, invoices, quotes, account.
- [ ] **Phase 6 — Cutover & handoff.** Frappe Cloud, DNS, ownership transfer, Jeff onboarded, old site decommissioned.

## Phase Details

### Phase 1 — Customer site (lookbook-forward, with small shop)

**Goal:** A first-time visitor lands on the site, immediately understands LT does custom event balloon decor at the level visible in the portfolio, knows how to inquire for custom work, and can browse a small set of pre-configured themed items if they're shopping for a casual celebration. Jeff sees the result and says *"yes — show this to my next corporate prospect."*

**Strategic shape:** lookbook-forward + small shop sidebar. Decision and rationale at `.planning/decisions/site-shape.md`. Built atop the competitor survey at `_resources/competitor-survey-2026-04-26.md` — 9 live sites in the events-decor / luxury-floral category exemplify the same pattern.

**Surfaces in scope:**

| Surface | State | Notes |
|---|---|---|
| Brand foundation (theme tokens) | DONE | `apps/locally_twisted/.../public/css/lt-theme.css` |
| Header + footer | DONE | Jinja partial overrides; nav structure may shift slightly to elevate Lookbook + demote Shop |
| Balloon Twisting + Face Painting page (with embedded pricing calculator) | DONE | `/balloon-twisting-and-face-painting` |
| Contact page | DONE | `/contact` — form-bearing, AJAX → Lead + Communication |
| Accessibility statement | DONE | `/accessibility` |
| **Homepage (lookbook-forward)** | TODO | Hero portfolio image + single inquiry CTA + trust strip with corporate logos + services teaser + 3 case-study previews |
| **Lookbook (full portfolio)** | TODO | `/lookbook` — grid/masonry of all events organized by event type |
| **Service category pages** | TODO | `/services/corporate`, `/services/weddings`, `/services/birthdays`, `/services/schools`, `/services/seasonal` — each ends with inquiry CTA |
| **Color Chart** | TODO | `/color-chart` — static reference; visual swatches with names |
| **`/book` form page** | TODO | Primary inquiry conversion form; uses the existing 45-field Lead schema |
| **Small Shop browse** | TODO | `/shop` — webshop-driven; ~6–12 themed bouquets + gift items + simple kits, sub-$200 only |
| **Small Shop product detail** | TODO | webshop-driven; pre-configured items only — no configurator |
| **Cart + checkout shell** | TODO | webshop-driven; Stripe stubbed until Phase 4 |
| **Refund Policy + FAQ pages** | TODO | Small static portal pages from `_resources/policies/` |
| **Blog framework + 2-3 posts** | TODO (deferrable) | "Kindergarten Teacher" voice; ships before or after the demo to Jeff |

**Surfaces explicitly NOT in scope** (per the site-shape decision):
- Configurator UI for custom arches (3 sizes × 70 colors × 8 picks). Customers requesting that level of customization use the inquiry form.
- Standalone About page (info distributes across homepage, service pages, contact)
- Standalone Services index page (event-type service pages serve this purpose)
- "Featured products" homepage block (homepage features portfolio, not products)

**Success criteria:**
1. Visitor can browse from homepage → lookbook → service-category page → inquiry form without hitting a broken layout, missing image, or JavaScript error
2. Inquiry form (`/book`) successfully creates a Lead in ERPNext with the existing 45-field schema populated correctly; visitor sees a confirmation page (no blank screen)
3. Small Shop: visitor can add a sub-$200 themed item to cart and reach the checkout shell; payment integration stubbed until Phase 4
4. Visual identity matches `_resources/STYLE-GUIDE.md` — verified by side-by-side check against the spec
5. SEO baseline: each page has unique title + meta description, semantic HTML, schema.org LocalBusiness markup, OpenGraph tags
6. AEO/GEO baseline: FAQ schema on FAQ page, LocalBusiness schema with service area on homepage and contact page
7. WCAG 2.1 AA passes on every page in scope — automated tool + manual keyboard navigation
8. Mobile-first: every page works at 375px width with no horizontal scroll, all touch targets ≥44px
9. **GL viewing the result says "yes — show this to Jeff."** This is the off-ramp gate.

### Phase 2 — Form-handling depth

**Goal:** Every form on the site (contact, book, BTFP, any other) has loud-failure protection, a customer acknowledgment, and Contact dedup against existing records. Jeff sees the new lead in his admin within minutes, pre-linked to a Contact if one exists.

**Depends on:** Phase 1 forms shipping (which they will, including `/book`).

**Scope:**
- Contact dedup logic: when a Lead is created, lookup existing Contact by email_id / mobile_no / phone; attach if found, create if not. Implemented as a Server Script on Lead `before_insert`.
- Customer acknowledgment email: auto-fired on Lead creation with a branded "we received your inquiry" template; stored as a Communication linked to the Lead.
- Loud-failure compliance audit: every form has user-facing error message on failure (no blank screens), exception logged at ERROR level with sanitized payload, monitor alert configured.
- Monitor alerts: Better Stack (or equivalent) configured to alert if `/book` or `/contact` form-creation rate drops to zero for >24 hours.
- Form-handler routing for any new forms that emerge from Phase 1 build.

**Success criteria:**
1. New Lead from `/book` auto-links to existing Contact when email or phone matches; otherwise creates new Contact
2. Customer receives acknowledgment email within 5 minutes of submitting any form
3. Intentionally broken submission shows real error message to customer + logs at ERROR level + triggers monitor alert
4. Loud-failure audit doc covers every form on every Phase 1 surface

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

**Note:** The smaller storefront (sub-$200 small-shop only) means Stripe scope is genuinely modest. The big-ticket payments still flow through invoicing, where Stripe is wired to the invoice rather than the cart.

**Success criteria:**
1. Test-mode small-shop checkout completes end-to-end and the order has a Stripe charge ID stored
2. Test-mode invoice payment via Stripe completes end-to-end (the path big-ticket events use)
3. Stripe webhook delivery verified: webhook fires, ERPNext endpoint receives, order/invoice status updates
4. At least one production-mode dry run with a real card; charge appears in Stripe dashboard
5. Invoice line items show Utah sales tax as its own visible line; rate matches the delivery / event city
6. Corporate invoices age correctly: day 31 produces a late-fee notification; "may waive" + "may suspend" workflow gives Jeff one-click discretion
7. ERPNext accounting books the same numbers Jeff's accountant would see in QuickBooks for the same transactions (verified for at least 5 representative transactions)
8. Payroll: Frappe HRMS produces a sample payroll run for Jeff's actual employee structure
9. North Peak (Jeff's accountant) gets a heads-up that LT is moving off QuickBooks; transition plan agreed with her

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

| Phase | Status | Slices done | Notes |
|-------|--------|-------------|-------|
| 1. Customer site (lookbook-forward) | In flight | 5 of ~14 | Brand, chrome, BTFP, contact, accessibility done. Homepage + lookbook + service pages + /book + shop remain. |
| 2. Form-handling depth | Not started | — | Reframed; /book moved into Phase 1 |
| 3. Operator workflow | Not started | — | — |
| 4. Money & compliance | Not started | — | Smaller scope due to small-shop framing |
| 5. Customer portal | Not started | — | — |
| 6. Cutover & handoff | Not started | — | — |

---
*Last updated: 2026-04-26 — strategic shift to lookbook-forward shape (replaces the prior implicit "ecommerce-first" framing). Backed by competitor survey + decision doc at `.planning/decisions/site-shape.md`.*
