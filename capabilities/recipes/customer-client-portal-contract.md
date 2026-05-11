---
id: customer-client-portal-contract
name: Customer Client Portal Contract
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted invite-only customer/client account portal routes, summaries, actions, and branded shell
currently_true: unknown
verification_level: 2
last_verified: 2026-05-11
evidence_quality: direct
successful_uses: 1
failed_uses: 0
regressions: 0
depends_on:
  - fail-loud-operating-law
used_by: []
tags:
  - Locally Twisted
  - ERPNext
  - Frappe
  - customer portal
  - account portal
---

# Customer Client Portal Contract

Use this recipe when changing customer login, `/me`, `/account/*`,
`/organization/*`, portal menu sync, customer-safe summaries, portal file
registration, checklist state, repeat requests, account provisioning, or the
customer account visual shell.

## Current Contract

- Customer accounts are optional and invite-first. Public signup stays disabled.
- Guest public inquiry, shop, cart, and checkout paths must remain usable; do
  not require login for public browsing or checkout.
- `/me` is the customer account home. Guest `/me` must not be readable.
- The account experience is LT-owned, not ERPNext native list pages.
- The individual account routes are `/me`, `/account/events`,
  `/account/quotes`, `/account/billing`, `/account/files`,
  `/account/checklist`, `/account/repeat`, and `/account/follow-up`.
- The organization account routes are `/organization`, `/organization/events`,
  `/organization/billing`, `/organization/files`, and `/organization/people`.
- Old native customer routes such as `/quotations`, `/orders`, `/invoices`,
  and `/addresses` are compatibility-routed to LT-owned pages.
- Customer-visible data comes through allowlisted DTO summaries from
  `customer_portal.py`. Do not expose raw ERPNext docs, Communications,
  internal Files, internal notes, cost, margin, payroll, procurement, supplier
  data, or Desk/backend routes.
- Customer edits and repeat requests create `LT Customer Change Request`; they
  do not directly mutate Sales Orders, Addresses, Quotations, Sales Invoices, or
  Payment Requests.
- Customer-visible files require `LT Customer Portal File`. The customer upload
  registration endpoint only accepts a `File` owned by the logged-in customer
  and already attached to the same source record.
- Organization access requires `LT Organization Portal Membership`; do not infer
  organization access from shared email domains.
- The visible account shell uses `lt-customer-portal.css`, hides the default
  Frappe portal sidebar on LT-owned pages, and renders the eight customer
  surfaces in the branded in-page nav.

## Implementation Surfaces

- `apps/locally_twisted/locally_twisted/customer_portal.py`
- `apps/locally_twisted/locally_twisted/customer_portal_pages.py`
- `apps/locally_twisted/locally_twisted/templates/includes/customer_portal_page.html`
- `apps/locally_twisted/locally_twisted/public/css/lt-customer-portal.css`
- `apps/locally_twisted/locally_twisted/customer_account_provisioning.py`
- `apps/locally_twisted/locally_twisted/seed/sync_customer_portal.py`
- `apps/locally_twisted/locally_twisted/verify/customer_portal_review_fixture.py`

## Verification

Run the full portal gate after account data, menu, route, permission, file, or
visual-shell changes:

```powershell
python scripts/verify/customer_portal_v1_contract.py
python scripts/verify/customer_portal_home_contract.py
python scripts/verify/customer_account_provisioning_contract.py
python scripts/verify/customer_portal_inventory.py --base-url http://localhost:8081 --strict-menu --report output/customer-portal-inventory.json
npm run test:customer-portal-visual
```

After Jinja, Python route context, or CSS edits, clear website cache. If browser
proof serves mixed old/new portal shell state after Python module edits, restart
the local Frappe backend/frontend containers and rerun the visual verifier.

## Failure Modes

- Treating Portal Settings rows as the customer experience. They are route
  affordances; LT pages own the customer-visible account product.
- Letting the default Frappe sidebar reappear next to the branded portal nav.
- Creating customer Users from guest checkout or failed payment state.
- Marking a staff-owned or unrelated File as a customer-uploaded portal file.
- Exposing ERPNext workflow labels, supplier routes, Desk routes, or raw records
  to customers.
- Sending invite/setup email before the account invite sender has a reviewed
  delivery path.
