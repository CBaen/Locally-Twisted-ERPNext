# REQUIREMENTS — Locally Twisted: First Professional Business Platform

**v1 scope:** end-to-end, from customer-facing site through cutover.
**REQ-ID format:** `[CATEGORY]-[NUMBER]`.
**Status legend:** `[ ]` not started · `[~]` in progress · `[x]` done

> 2026-06-28 update: This requirements doc predates the current three-brand DBA
> boundary. Current scope is one Locally Twisted accounting/ERPNext operating
> company with three protected brand lanes: Locally Twisted, Commercial Balloon
> Decor, and Memorial Balloons. Older "multi-company" rejection language blocks
> unapproved client/company mixing; it does not block the approved
> DBA/service-brand lane model. Read `../BRAND-BOUNDARY.md` before relying on
> this file for brand/accounting scope.

---

## v1 Requirements

### Customer-Facing Site (SITE) — Phase 1

- [~] **SITE-01**: Brand foundation. ERPNext theme installed with the current LT design system: Cormorant Garamond + Lato fonts, Civic Celebration + Slate Blue/Berry + Brand Direction palette, 8px spacing scale, button + form + card patterns, focus indicators, reduced-motion, and premium brass-line icon rules. Verified by opening any page at `:8081` and inspecting the head. **DONE 2026-04-26 (Slice 1); rebrand contract superseded 2026-05-05.**
- [ ] **SITE-02**: Site-wide header and footer. Header navigation must follow the current two-level accessible nav direction with the approved Locally Twisted logo asset, large nav labels, and dark/navy/ink/brass treatment. Footer uses the same premium brand system with legal links, social icons, accessibility link, and copyright. Mobile-responsive.
- [ ] **SITE-03**: Landing page. Hero, services snapshot (3 cards), featured products, social proof, closing CTA. Style-guide-driven build with placeholder photography from `_resources/images/`.
- [ ] **SITE-04**: Balloon Twisting + Face Painting service page WITH embedded pricing calculator. Per-artist live math, "Why no combination discount?" expander, "Get a quote" CTA with pre-filled inputs.
- [ ] **SITE-05**: Contact page with brief about summary embedded. Service area display, business hours, contact form (form-action stubbed until SITE-12 wires it).
- [ ] **SITE-06**: Blog framework + first 2-3 live posts. "Kindergarten Teacher" voice per style guide.
- [ ] **SITE-07**: Accessibility + Refund Policy + FAQ pages. Brief intent-only accessibility statement (Option B); refund policy from `_resources/policies/legal-interview-answers.md` Part 2C; FAQ consolidated from policies.
- [ ] **SITE-08**: Products listing page. Frappe webshop product list with brand styling overrides. Filter by category. Mobile-responsive.
- [ ] **SITE-09**: Individual product pages. Photo, info, variant selector with `price_extra` math, "Add to cart". Schema.org Product markup.
- [ ] **SITE-10**: Cart + checkout shell. Add-to-cart, view cart, proceed through checkout to confirmation page. Stripe stubbed until PAY-01.

### Lead Intake (LEAD) — Phase 2

- [ ] **LEAD-01**: `/contact` and `/book` forms post into the existing ERPNext Lead schema with field mapping. Each form-field branch verified end-to-end.
- [ ] **LEAD-02**: Customer/Contact dedup on Lead `before_insert`. Lookup by `email_id` / `mobile_no` / `phone`; attach to existing Contact if matched, create new Contact if not.
- [ ] **LEAD-03**: Customer acknowledgment. Submission produces a confirmation page (not blank) and an acknowledgment email within 5 minutes.
- [ ] **LEAD-04**: Loud failure verified. Intentionally broken submission shows a real error message to the customer, logs at ERROR level with sanitized payload, and fires a monitor alert.

### Operator Workflow (WORK) — Phase 3

- [ ] **WORK-01**: Lead → Quote → Booking confirmation pipeline. Plain-language labels everywhere. Quote PDF uses LT brand fonts and per-artist pricing breakdown.
- [ ] **WORK-02**: Booking confirmed → Calendar event auto-created with date, location, crew assignment fields populated.
- [ ] **WORK-03**: Booking confirmed → Project Task auto-created with crew, supplies, equipment checklist fields.
- [ ] **WORK-04**: Day-of view. Crew member can pull up the day's events on mobile and see customer name, address, services, time, contact phone, supplies needed.
- [ ] **WORK-05**: Every cross-model automation logs entry + exit at INFO level (loud-failure compliance).

### Money & Compliance (MONEY) — Phase 4

- [ ] **MONEY-01**: Stripe end-to-end on ERPNext webshop. Test mode passes a full checkout cycle. At least one production-mode dry run with a real card. Webhook handling verified. Charge ID stored on the sale order.
- [ ] **MONEY-02**: Invoice generation with LT brand templates. Quote and invoice PDFs use LT fonts and colors.
- [ ] **MONEY-03**: Utah city-based auto-calculated tax. Tax line visible on invoices, rate matches the delivery / event city. Tax research from `_resources/utah-tax-rates-2026q2.md` integrated as ERPNext Tax Templates.
- [ ] **MONEY-04**: Corporate Net 30 + 10% simple late fee logic per `_resources/policies/deposits.md`. Day 31 produces a late-fee notification; "may waive" + "may suspend" workflow gives Jeff one-click discretion.
- [ ] **MONEY-05**: ERPNext native accounting set up. Books match what Jeff's accountant would see in QuickBooks for the same transactions (verified for at least 5 representative transactions).
- [ ] **MONEY-06**: Frappe HRMS installed and configured for LT's salary structure. Sample payroll run produces correct numbers.

### Customer Portal (PORTAL) — Phase 5

- [ ] **PORTAL-01**: Logged-in customer can view their order + booking history.
- [ ] **PORTAL-02**: Logged-in customer can view and download invoices and quotes as branded PDFs.
- [ ] **PORTAL-03**: Customer can update their email, password, address through the portal.
- [ ] **PORTAL-04**: Portal session verified end-to-end without errors.

### Cutover (CUTOVER) — Phase 6

- [ ] **CUTOVER-01**: ERPNext site deployed to Frappe Cloud at `locallytwisted.com` over HTTPS. Custom apps and controllers active.
- [ ] **CUTOVER-02**: DNS flipped — `locallytwisted.com` resolves to the Frappe Cloud site.
- [ ] **CUTOVER-03**: Site ownership transferred to Jeff Kimber's Frappe Cloud team account. Cameron retains developer-role access only.
- [ ] **CUTOVER-04**: Jeff onboarded — can log in, place a test order in his own admin, and navigate without assistance.
- [ ] **CUTOVER-05**: Old `locallytwisted.com` site decommissioned and snapshotted.
- [ ] **CUTOVER-06**: Retired reference sources remain out of active local guidance; use committed current-source material, explicitly approved restored evidence, or GL/legal approval for narrow recovery tasks.

---

## v2 Requirements

<!-- Things deferred to a future milestone, not v1. -->

(None yet — v1 is the full first-build. Post-cutover enhancements get logged here as Jeff reports them. Likely v2 candidates: real photography swap-in, North Peak / accountant onboarding, Frappe HRMS payroll first real run, blog post cadence, advanced product variant management.)

---

## Out of Scope

<!-- Explicit boundaries with reasoning. -->

- **Standalone About page** — about info distributes; brief summary lands on contact page (GL directive 2026-04-26)
- **Standalone Services index page** — service info lives on individual service pages and homepage (GL directive 2026-04-26)
- **Standalone /pricing page** — pricing calculator embedded on Balloon Twisting + Face Painting service page (GL directive 2026-04-26)
- **Gusto / third-party payroll** — agency standard is ERPNext native HRMS for all clients (decision 2026-04-26)
- **"Migration" framing of any kind** — this is a NEW BUILD; the catalog_data attempt is reference material that will be retired
- **Unapproved multi-company or multi-client mixing in one ERPNext site** —
  rejected; per-client isolation remains structural. This does not reject the
  2026-06-28 approved LT DBA/service-brand lane model for Locally Twisted,
  Commercial Balloon Decor, and Memorial Balloons under the same LT accounting
  operation.
- **Self-hosted current import capture production** — superseded by Frappe Cloud (managed, transferable per-site)
- **Telling Jeff the verdict before there's a working replacement** — stealth on the verdict until Phase 1 is demo-ready

---

## Traceability

| REQ-ID | Phase | Status | Plan |
|--------|-------|--------|------|
| SITE-01 | Phase 1 | DONE 2026-04-26 | `phases/01-customer-site-and-storefront/PLAN.md` Slice 1 |
| SITE-02 | Phase 1 | Not started | Slice 2 |
| SITE-03 | Phase 1 | Not started | Slice 3 |
| SITE-04 | Phase 1 | Not started | Slice 4 (with embedded pricing calc) |
| SITE-05 | Phase 1 | Not started | Slice 5 |
| SITE-06 | Phase 1 | Not started | Slice 5b |
| SITE-07 | Phase 1 | Not started | Slice 6 |
| SITE-08 | Phase 1 | Not started | Slice 7 |
| SITE-09 | Phase 1 | Not started | Slice 8 |
| SITE-10 | Phase 1 | Not started | Slice 9 |
| LEAD-01 | Phase 2 | Not started | TBD |
| LEAD-02 | Phase 2 | Not started | TBD |
| LEAD-03 | Phase 2 | Not started | TBD |
| LEAD-04 | Phase 2 | Not started | TBD |
| WORK-01..05 | Phase 3 | Not started | TBD |
| MONEY-01..06 | Phase 4 | Not started | TBD |
| PORTAL-01..04 | Phase 5 | Not started | TBD |
| CUTOVER-01..06 | Phase 6 | Not started | TBD |

---
*Last updated: 2026-04-26 — refreshed against the new 6-phase ROADMAP.*
