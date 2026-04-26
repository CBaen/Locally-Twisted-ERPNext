# REQUIREMENTS — Locally Twisted: Odoo → ERPNext Migration

**v1 scope:** the LT migration end-to-end, from inventory through cutover.
**REQ-ID format:** `[CATEGORY]-[NUMBER]`.
**Status legend:** `[ ]` not started · `[~]` in progress · `[x]` done

---

## v1 Requirements

### Inventory & Discovery (INV)

- [ ] **INV-01**: Read the entire `C:\Users\baenb\projects\locally-twisted-odoo` codebase and produce a structured map of every model, view, controller, automation, security rule, data file, theme file, snippet, and migration script. Note the production status of each (in production / not in production / half-finished / broken). Output: `INVENTORY.md` consumable by every subsequent phase.
- [ ] **INV-02**: Read Locally Twisted's production database to inventory all `ir.ui.view` records where `arch_db != arch_fs` (Jeff's UI-edited content) and any other tables holding irreplaceable user-edited content. Output: `ARCHDB-INVENTORY.md` listing every record, its content, and a rebuild plan.

### Backend Data & Logic (DATA)

- [ ] **DATA-01**: Translate every Odoo model from the inventory into ERPNext DocTypes with equivalent fields, types, computed fields, validations, and relationships. Custom domain models (LT-specific) included.
- [ ] **DATA-02**: Replicate the 17 cross-module automations (CRM → Sale → Project → Calendar → email sequences) as ERPNext Server Scripts and Notification rules. Each automation has a verification test proving the cascade fires correctly.
- [ ] **DATA-03**: Re-implement Utah sales tax (16 rates, 105 fiscal positions, 1,785-line `data/tax_data.xml`) as ERPNext Tax Templates. Verified against at least 5 representative ZIP+4 transactions.

### Portal (PORTAL)

- [ ] **PORTAL-01**: Translate the 333-line custom Odoo portal controller into ERPNext's portal model. Customer login, order history, account management, invoice/quote viewing all functional and verified end-to-end.

### Storefront / Website / Ecommerce (STORE)

- [ ] **STORE-01**: **Customer-facing rebuild/redesign.** Storefront, product pages, cart, checkout, account, order history rebuilt to a higher visual + UX quality than the current Odoo version. Brand identity preserved (fonts, colors, voice); UX freed to be better. Must be ready to take real payments at cutover.
- [ ] **STORE-02**: Replicate `price_extra` per variant in the ERPNext webshop. Variant selection on product page reflects correct price; checkout charges correct amount; verified against current Odoo pricing for at least 3 multi-variant products.
- [ ] **STORE-03**: Theme + brand parity for non-customer-facing surfaces. Internal admin navigation, transactional emails (order confirmation, shipping notification, invoice receipt), and document templates (invoice/quote PDFs) match LT's existing brand language so the transition feels continuous to Jeff.

### Payments (PAY)

- [ ] **PAY-01**: Stripe integration verified end-to-end on ERPNext v15.105.0 webshop. Test mode passes a full checkout → payment → confirmation cycle. At least one production-mode dry run with a real card before cutover. Webhook handling verified. Receipt persistence (Stripe charge ID stored on the sale order) verified.

### Verification (VER)

- [ ] **VER-01**: Side-by-side verification harness. Automated smoke tests covering every critical user journey on both the Odoo install and the ERPNext install. Journeys include: anonymous browse → cart → checkout → confirmation; portal login → view orders; admin → quote → sale order → invoice → payment received. Each journey produces a screenshot pair for visual diff. Run on every deploy.

### Production Deployment (DEPLOY)

- [ ] **DEPLOY-01**: Spin up the production ERPNext site on Frappe Cloud under Cameron's account. Migrate site data from local Docker to Frappe Cloud. Verify all functionality works on Frappe Cloud's infrastructure (custom apps, custom controllers, Stripe). Custom domain configured. SSL verified.
- [ ] **DEPLOY-02**: Cutover sequence executed. DNS flipped from Odoo to ERPNext. LT site ownership transferred from Cameron's Frappe Cloud team to Jeff's `locallytwisted@gmail.com` team via the dashboard Actions tab. Code-only / data-no boundary verified post-transfer (Cameron retained as developer-role team member only). Old Odoo install decommissioned (snapshot retained for 90 days). Jeff onboarded with documentation tailored to his existing workflows.

---

## v2 Requirements

<!-- Things deferred to a future milestone, not v1. -->

(None yet — v1 is the full migration. Post-cutover enhancements get logged here as Jeff reports them.)

---

## Out of Scope

<!-- Explicit boundaries with reasoning. -->

- **Other BBC concerns** — own ops, attorney clients, agency platform decisions. Each is its own project.
- **jakenfriends migration** — archived (friend not interested; off-Odoo expedition META-3 also flags JNF as poor ERPNext fit).
- **Lawyer / `Example_Lawyer_*` template** — deferred until LT migration is done.
- **Multi-company-in-one-site model** — rejected; compromises isolation.
- **Self-hosted Hetzner production** — superseded by Frappe Cloud (off-Odoo expedition recommendation).
- **Automated content migration tool** — none of production quality exists. Hand-rebuild guided by inventory.
- **Telling Jeff before ready** — stealth is a hard constraint.

---

## Traceability

<!-- Maps each REQ-ID to the phase that owns it. -->

| REQ-ID | Phase | Status |
|--------|-------|--------|
| INV-01 | Phase 1 | Not started |
| INV-02 | Phase 1 | Not started |
| DATA-01 | Phase 2 | Not started |
| DATA-02 | Phase 3 | Not started |
| DATA-03 | Phase 3 | Not started |
| PORTAL-01 | Phase 4 | Not started |
| STORE-01 | Phase 5 | Not started |
| STORE-02 | Phase 6 | Not started |
| STORE-03 | Phase 6 | Not started |
| PAY-01 | Phase 7 | Not started |
| VER-01 | Phase 8 | Not started |
| DEPLOY-01 | Phase 9 | Not started |
| DEPLOY-02 | Phase 10 | Not started |

---
*Last updated: 2026-04-25 after roadmap creation*
