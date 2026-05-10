# White-label customer/client surfaces — 2026-05-09

## Status

[VERIFIED LOCAL PASS — customer-surface white-label gate added; one unrelated backend blocker remains in business automation index]

Launch-blocking cleanup for Locally Twisted customer/client-facing surfaces. Goal: Jeff, customers, accounts payable contacts, event buyers, procurement contacts, and public visitors do not see ERPNext/Frappe/Odoo/platform branding or framework-language leakage in outward surfaces.

## Scope

Customer/client/public surfaces include public website pages and menus, login/customer portal chrome, checkout/cart/open-commerce states, pause-mode fallback states if re-enabled, payment result pages, customer order confirmation emails, customer receipts, sales invoices and invoice PDFs/print formats, payment receipts, quote/estimate/proposal packets, statements/payment reminders, vendor setup/W-9 packets, contract acceptance summaries, outbound document previews, visible error messages returned to public APIs, email subjects/body copy/footers, and generated document titles/headers/footers.

## Preserve stability

Do not blindly rename internal machinery: Python imports, DocType names used by ERPNext/Frappe internals, database fields, fixture `doctype` keys, and internal-only comments can remain when they do not render or send to customers/clients. Backend platform language may remain when it is purely implementation detail.

## Evidence state

A white-label leak scout completed, but its displayed result was truncated. Treat that report as [TRUNCATED][UNVERIFIED AS COMPLETE]. Use fresh scans before patching or claiming coverage.

## Hot zones

- `apps/locally_twisted/locally_twisted/www/payment_success.py`
- `apps/locally_twisted/locally_twisted/www/thank_you.py`
- `apps/locally_twisted/locally_twisted/www/checkout.py`
- `apps/locally_twisted/locally_twisted/www/checkout.html`
- `apps/locally_twisted/locally_twisted/www/search.py` / `search.html`
- `apps/locally_twisted/locally_twisted/templates/base.html`
- `apps/locally_twisted/locally_twisted/templates/includes/navbar/navbar.html`
- `apps/locally_twisted/locally_twisted/communication_copy_policy.py`
- `apps/locally_twisted/locally_twisted/verify/customer_documents_contract.py`
- `apps/locally_twisted/locally_twisted/verify/invoice_branding_contract.py`
- `scripts/verify/render_outbound_document_previews.py`
- `apps/locally_twisted/locally_twisted/outbound_documents/registry.py`
- `apps/locally_twisted/locally_twisted/outbound_documents/templates/*.md`

## Build lanes

A. Web/customer API surfaces: customer-safe route/page/API copy while preserving route contracts.
B. Outbound documents/emails: Locally Twisted/client-safe titles, bodies, email copy, and previews while preserving accounting/legal meaning.
C. Verification: durable white-label gates that separate backend false positives from rendered/customer-output risks.

## Minimum forbidden outward markers

- ERPNext
- Frappe
- Odoo
- Built on Frappe
- framework/platform phrasing that exposes implementation
- internal terms such as Desk, DocType, Sales Order, Lead, Payment Entry when shown to public customers where a friendly label exists

Operator-only emails may keep backend record labels/links when needed for operations. Customer/client outputs should not.

## Gates before done

- `python -m py_compile` for touched Python files
- customer document contract verifier
- invoice branding contract verifier
- outbound document preview render/check
- public rendered route bad-term gate
- `npm run test:search-contract`
- targeted Playwright: `npm run test:interactive-layout -- --grep "white-label platform leakage"`

## Local progress 2026-05-09 23:20 MDT

- Stripped customer-facing backend record names from outbound document body copy where friendly labels exist, while preserving frontmatter/internal record-source metadata for generator stability.
- Added `scripts/verify/white_label_customer_surfaces.py` to check:
  - outbound document template bodies,
  - rendered outbound preview HTML,
  - public/local rendered route visible text,
  - generator/banner source leaks without failing on framework asset URLs.
- Expanded Playwright public white-label word gate to include Odoo.
- Regenerated HTML previews under `output/playwright/outbound-documents-white-label-20260509/`.

## Verified gates 2026-05-09 23:20 MDT

- `python -m py_compile scripts/verify/white_label_customer_surfaces.py apps/locally_twisted/locally_twisted/www/payment_success.py apps/locally_twisted/locally_twisted/www/thank_you.py apps/locally_twisted/locally_twisted/www/checkout.py apps/locally_twisted/locally_twisted/www/search.py apps/locally_twisted/locally_twisted/outbound_documents/registry.py` — PASS
- `python scripts/verify/render_outbound_document_previews.py --slug outbound-documents-white-label-20260509 --skip-browser --no-open` — PASS, 20 scenarios
- `python scripts/verify/white_label_customer_surfaces.py --base-url http://localhost:8081 --preview-dir output/playwright/outbound-documents-white-label-20260509` — PASS across 10 templates, 21 preview HTML files, 15 local routes
- `python scripts/verify/customer_documents_contract.py` — PASS
- `python scripts/verify/invoice_branding_contract.py` — PASS
- `python scripts/verify/ecommerce_pause_contract.py` — PASS
- `python scripts/verify/customer_contact_points_contract.py` — PASS
- `npm run test:search-contract` — PASS, 2 tests
- `npm run test:interactive-layout -- --grep "white-label platform leakage|homepage hero uses one visible stable headline"` - PASS, 46 tests at the time of this lane. Later 2026-05-10 open-commerce testing is covered by `npm run test:public-verify` and `npm run test:ecommerce-full`.

## Known non-white-label blocker

Resolved by later 2026-05-10 backend runs: `python scripts/verify/business_automation_index.py` now passes with no record-level launch blocker. Keep this section as historical context for the white-label lane only.
