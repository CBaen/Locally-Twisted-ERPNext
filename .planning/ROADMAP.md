# Roadmap: Locally Twisted — Odoo → ERPNext Migration

## Overview

The migration runs in three arcs: first, understand what actually exists (inventory both the codebase and the production database before touching anything); second, rebuild the backend, portal, storefront, and payments on ERPNext locally until every critical journey works; third, deploy to Frappe Cloud and hand Jeff a system that makes him feel relieved, not nervous. Every phase gates on verified observable behavior — "deployed without checking" is the failure pattern this project was created to end.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [~] **Phase 1: Inventory** — **DEFERRED 2026-04-25 evening.** INV-01 superseded by the existing off-Odoo expedition's `inventory-findings.md` (covers ~65%; remaining 35% filled inline by reading source files during translation phases). INV-02 (production `arch_db` read) deferred to slot before Phase 10 cutover — content-migration concern, not rebuild concern. Plan files deleted; `01-RESEARCH.md` + `01-VALIDATION.md` kept as reference.
- [ ] **Phase 2: Backend Models** — Translate every Odoo model into ERPNext DocTypes with fields, validations, and relationships **(now the active phase — start here)**
- [ ] **Phase 3: Automations and Tax** - Replicate the 17 cross-module automations and Utah tax data as ERPNext Server Scripts and Tax Templates
- [ ] **Phase 4: Portal** - Translate the custom Odoo portal controller into ERPNext's portal model
- [ ] **Phase 5: Storefront Rebuild** - Rebuild customer-facing surfaces to a higher quality bar than Odoo
- [ ] **Phase 6: Variant Pricing and Brand Parity** - Replicate variant price_extra and apply brand identity to admin, emails, and document templates
- [ ] **Phase 7: Payments** - Verify Stripe end-to-end on ERPNext v15.105.0
- [ ] **Phase 8: Verification Harness** - Automated side-by-side smoke tests covering every critical user journey
- [ ] **Phase 9: Cloud Deployment** - Spin up production on Frappe Cloud, verify all functionality
- [ ] **Phase 10: Cutover** - DNS flip, ownership transfer, Jeff onboarding, Odoo decommission

## Phase Details

### Phase 1: Inventory — DEFERRED

**Status: DEFERRED 2026-04-25 evening.** The original goal was elaborate inventory-before-build. GL named the drift after the planning machinery had spun up multiple agents without producing any rebuild work: "you haven't even rebuilt the site in ERPNext?!"

**Resolution:**
- **INV-01 (codebase inventory)** is satisfied by the existing off-Odoo expedition's `locally-twisted-odoo/research/extended-expedition-off-odoo-replacement/inventory-findings.md` — covers ~65% of the work. The remaining 35% (per-migration-script summaries, data file inventory, production-status annotations) is filled inline as each translation phase reads the relevant Odoo source files.
- **INV-02 (production `arch_db` read)** is deferred to slot before Phase 10 cutover. Jeff's UI-edited content only matters at content-migration time; reading it now is premature.
- **Plan files (01-01-PLAN.md through 01-06-PLAN.md) deleted from disk.** Git history preserves them. `01-RESEARCH.md` and `01-VALIDATION.md` retained as reference.

**Don't reactivate Phase 1 unless GL explicitly asks.** The decision is in `built-by-cameron-decisions.md` (2026-04-25 evening).

### Phase 2: Backend Models
**Goal**: Every Odoo data model has a working ERPNext DocType equivalent that Cameron can verify by creating and saving records
**Depends on**: Phase 1
**Requirements**: DATA-01
**Success Criteria** (what must be TRUE):
  1. Every DocType from INVENTORY.md is present in the ERPNext instance at `:8081`
  2. Field types, computed fields, validations, and relationships match their Odoo equivalents — verified by creating at least one representative record per DocType
  3. No DocType errors appear in the ERPNext error log during record creation
  4. LT-specific custom domain models (not standard Odoo) are present and functional
**Plans**: TBD

### Phase 3: Automations and Tax
**Goal**: All 17 cross-module automations fire correctly and all Utah tax rates are loaded and apply to the right transactions
**Depends on**: Phase 2
**Requirements**: DATA-02, DATA-03
**Success Criteria** (what must be TRUE):
  1. Each of the 17 automations has a corresponding ERPNext Server Script or Notification rule, and each produces a verified cascade output (e.g., CRM lead created → sale order linked → project task spawned) observable in the admin UI
  2. Utah tax configuration has 16 tax rates and 105 fiscal-position equivalents present in ERPNext Tax Templates
  3. At least 5 representative ZIP+4 transactions apply the correct tax rate — verified by creating test transactions and confirming the tax line
  4. No automation fires silently: each one logs entry and exit in the ERPNext server log at INFO level
**Plans**: TBD

### Phase 4: Portal
**Goal**: A logged-in customer can view their orders, invoices, and account details through the ERPNext portal just as they could through the Odoo portal
**Depends on**: Phase 2
**Requirements**: PORTAL-01
**Success Criteria** (what must be TRUE):
  1. Customer can log in to the ERPNext portal using their credentials
  2. Logged-in customer can view their full order history with correct line items and totals
  3. Logged-in customer can view and download invoices and quotes as PDFs
  4. Customer account management (email, password, address) works end-to-end
  5. Portal behavior verified by completing a full portal session (login → order history → invoice view → logout) without errors
**Plans**: TBD
**UI hint**: yes

### Phase 5: Storefront Rebuild
**Goal**: The ERPNext webshop delivers a customer experience that is visibly better than the current Odoo storefront — same brand, better UX, ready to take real payments
**Depends on**: Phase 1, Phase 2
**Requirements**: STORE-01
**Success Criteria** (what must be TRUE):
  1. Anonymous visitor can browse products, add to cart, proceed through checkout, and reach a confirmation page on the ERPNext storefront
  2. Storefront uses LT's brand fonts, colors, and voice — verified by visual comparison against the Odoo storefront
  3. Product pages, cart, checkout, account creation, and order history are all reachable and functional with no broken layouts or JavaScript errors
  4. The experience is observably higher quality than Odoo's version — at least one UX improvement that Odoo's template could not deliver (documented in phase summary)
**Plans**: TBD
**UI hint**: yes

### Phase 6: Variant Pricing and Brand Parity
**Goal**: Variant pricing reflects correct price extras everywhere a customer sees prices, and Jeff's internal experience (admin, emails, documents) matches LT's existing brand language
**Depends on**: Phase 2, Phase 5
**Requirements**: STORE-02, STORE-03
**Success Criteria** (what must be TRUE):
  1. Selecting a variant on a product page updates the displayed price to include the correct `price_extra` — verified against current Odoo pricing for at least 3 multi-variant products
  2. Checkout charges the variant-correct amount — verified by completing a test checkout with variant products and confirming the order total
  3. Order confirmation emails, shipping notification emails, and invoice receipt emails display LT's brand fonts and colors — verified by triggering each email type and comparing against Odoo's output
  4. Invoice and quote PDFs use LT's brand header, fonts, and layout — verified by generating one of each and comparing against the current Odoo PDF output
**Plans**: TBD
**UI hint**: yes

### Phase 7: Payments
**Goal**: Stripe payments work end-to-end on ERPNext v15.105.0 — test mode and at least one production-mode dry run both pass
**Depends on**: Phase 5
**Requirements**: PAY-01
**Success Criteria** (what must be TRUE):
  1. A full test-mode checkout (add to cart → checkout → enter Stripe test card → submit → order confirmation) completes without errors
  2. The resulting sale order has the Stripe charge ID stored as a field — visible in the admin order record
  3. Stripe webhook delivery is verified: a test webhook fires, hits the ERPNext endpoint, and the order status updates accordingly
  4. At least one production-mode dry run with a real card completes and the charge appears in the Stripe dashboard with the correct amount
**Plans**: TBD

### Phase 8: Verification Harness
**Goal**: Automated smoke tests run against both Odoo and ERPNext on every deploy, catching regressions before Cameron sees them — not after Jeff does
**Depends on**: Phase 7
**Requirements**: VER-01
**Success Criteria** (what must be TRUE):
  1. Running the verification harness produces a screenshot pair (Odoo + ERPNext) for each critical journey: anonymous browse → cart → checkout → confirmation; portal login → order history; admin → quote → sale order → invoice → payment received
  2. The harness exits non-zero and surfaces a clear failure message if any journey breaks — not a silent pass
  3. The harness can be invoked with a single command and completes without manual intervention
  4. At least one deliberately-broken journey is tested and the harness correctly catches and reports it (regression coverage verified)
**Plans**: TBD

### Phase 9: Cloud Deployment
**Goal**: The ERPNext site runs on Frappe Cloud with all functionality intact — custom apps, custom controllers, Stripe, and the custom domain all work on Frappe Cloud's infrastructure
**Depends on**: Phase 8
**Requirements**: DEPLOY-01
**Success Criteria** (what must be TRUE):
  1. The ERPNext site is accessible at the custom LT domain over HTTPS on Frappe Cloud — not just on localhost
  2. Running the verification harness against the Frappe Cloud URL produces the same passing results as against localhost
  3. Stripe payment flow works on Frappe Cloud (not just locally) — verified by running the test-mode checkout against the live URL
  4. Custom apps and controllers are deployed and active — no fallback to default ERPNext behavior for LT-specific features
**Plans**: TBD

### Phase 10: Cutover
**Goal**: Jeff's business runs on ERPNext — DNS points to the new system, Jeff owns his own site on Frappe Cloud, and the Odoo install is decommissioned
**Depends on**: Phase 9
**Requirements**: DEPLOY-02
**Success Criteria** (what must be TRUE):
  1. DNS has been flipped: `locallytwisted.com` (or the live domain) resolves to the ERPNext Frappe Cloud site, not Odoo
  2. The LT site appears under Jeff's `locallytwisted@gmail.com` Frappe Cloud team, not Cameron's — verified in the Frappe Cloud dashboard
  3. Cameron retains developer-role access only — verified by confirming Cameron cannot access billing or site ownership controls
  4. Jeff can log in, place a test order, and navigate the admin without assistance — verified during the onboarding session
  5. Odoo snapshot retained and documented; Odoo install confirmed decommissioned (not just stopped)
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10

Note: Within Phase 1, INV-01 (codebase) and INV-02 (production database) run in parallel as independent data sources.

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Inventory | 0/6 | Not started | - |
| 2. Backend Models | 0/TBD | Not started | - |
| 3. Automations and Tax | 0/TBD | Not started | - |
| 4. Portal | 0/TBD | Not started | - |
| 5. Storefront Rebuild | 0/TBD | Not started | - |
| 6. Variant Pricing and Brand Parity | 0/TBD | Not started | - |
| 7. Payments | 0/TBD | Not started | - |
| 8. Verification Harness | 0/TBD | Not started | - |
| 9. Cloud Deployment | 0/TBD | Not started | - |
| 10. Cutover | 0/TBD | Not started | - |
