# Customer / Client Portal Translation

Last verified: 2026-05-11 by Codex.

## Purpose

Translate ERPNext's default customer portal into a Locally Twisted account
experience without breaking guest-first public flows. This lane is for customers
and clients only; owner, employee, accountant, contractor, vendor, and backend
Desk access stay in their own lanes.

## Current Verified State

Commands:

```powershell
python scripts/verify/customer_portal_v1_contract.py
python scripts/verify/customer_portal_inventory.py --base-url http://localhost:8081 --strict-menu --report output/customer-portal-inventory.json
python scripts/verify/customer_portal_home_contract.py
python scripts/verify/customer_account_provisioning_contract.py
```

Result on 2026-05-11: all listed contracts passed locally.

Hard boundaries currently holding:

- `/login` returns HTTP 200.
- `/me` as a guest returns HTTP 403.
- Public signup is disabled: `Website Settings.disable_signup = 1`.
- Login remains visible: `Website Settings.hide_login = 0`.
- Guest shop/cart/checkout remain open:
  - `Webshop Settings.enabled = 1`
  - `enable_checkout = 1`
  - `login_required_to_view_products = 0`
  - `hide_price_for_guest = 0`
- Checkout still must not create a `User`.
- Supplier portal routes still exist and remain Supplier-only; they are not the
  customer account experience.

## Implemented V1 Shape

The customer account product is now LT-owned instead of native ERPNext list
pages.

Owned individual routes:

- `/me`
- `/account/events`
- `/account/quotes`
- `/account/billing`
- `/account/files`
- `/account/checklist`
- `/account/repeat`
- `/account/follow-up`

Owned organization routes:

- `/organization`
- `/organization/events`
- `/organization/billing`
- `/organization/files`
- `/organization/people`

Compatibility redirects/rules:

- `/quotations` -> `account/quotes`
- `/orders` -> `account/events`
- `/invoices` -> `account/billing`
- `/addresses` -> `account/events`
- `/account/follow-up` -> `account/follow_up`

Portal Settings now shows Customer menu rows for the eight owned surfaces:
Quotes, Event Details, Invoices & Receipts, Files & Inspiration, Customer
Checklist, Repeat Client, After-Event Follow-Up, and Organization Portal. The
old `/quotations`, `/orders`, `/invoices`, and `/addresses` rows remain in the
single DocType as disabled history, along with the hidden stock ERPNext routes.

## Backend Contract

Source modules:

- `apps/locally_twisted/locally_twisted/customer_portal.py`
- `apps/locally_twisted/locally_twisted/customer_portal_pages.py`
- `apps/locally_twisted/locally_twisted/templates/includes/customer_portal_page.html`

The portal reads through `get_customer_portal_summary(user)` and
`get_organization_portal_summary(user)`. Those functions resolve
`User -> Contact -> Customer`, then return only customer-safe fields from
Lead, Quotation, Sales Order, Sales Invoice, Payment Request, Address, and
LT-owned portal metadata.

Do not expose:

- raw `doc.as_dict()`
- raw Communications
- internal Files
- cost, margin, payroll, procurement, or supplier data
- Desk/backend routes
- raw ERPNext workflow language when a customer-safe status exists

Customer actions write review or portal metadata records:

- `LT Customer Change Request`
- `LT Customer Portal File`
- `LT Customer Checklist Response`
- `LT Organization Portal Membership`

Important behavior:

- Customer event/order edits create `LT Customer Change Request`; they do not
  directly mutate Sales Order, Address, Quotation, Sales Invoice, or Payment
  Request records.
- Repeat-client requests also create review requests; they do not create direct
  repeat orders.
- File visibility is explicit through `LT Customer Portal File`; raw File rows
  are not customer-visible by default. The customer-facing registration method
  only accepts a `File` owned by the logged-in customer and already attached to
  the same allowed source record. Staff-owned files, unrelated files, and files
  attached to another source fail before portal metadata is created.
- Organization portal access requires `LT Organization Portal Membership`, not
  a shared email domain guess.

## Odoo Reference Signals

Reference files inspected read-only:

- `C:\Users\baenb\projects\locally-twisted-odoo\addons\locally_twisted\controllers\portal.py`
- `C:\Users\baenb\projects\locally-twisted-odoo\addons\locally_twisted\views\portal_templates.xml`
- `C:\Users\baenb\projects\locally-twisted-odoo\addons\locally_twisted\security\lt_groups.xml`
- `C:\Users\baenb\projects\locally-twisted-odoo\addons\locally_twisted\security\lt_rules.xml`

Translated intent:

- Adaptive portal home.
- Customer-safe event details.
- Day-of/event status cards.
- Narrow customer prep updates.
- Completed-event photo/file support.
- Company/crew photos excluded from customer visibility.
- Portal controller/service ownership instead of backend record exposure.

Do not port Odoo code or schema directly.

## Verifier Contract

Primary V1 gate:

```powershell
python scripts/verify/customer_portal_v1_contract.py
```

This creates rollback-safe Customer, Contact, User, Sales Order, and
organization membership records, renders all individual and organization
routes, proves the eight module keys exist, proves change/repeat actions create
review requests, proves the Sales Order is not directly mutated, and proves the
customer file-registration guard blocks arbitrary File attachment by name.

Supporting gates:

```powershell
python scripts/verify/customer_portal_inventory.py --base-url http://localhost:8081 --strict-menu --report output/customer-portal-inventory.json
python scripts/verify/customer_portal_home_contract.py
python scripts/verify/customer_account_provisioning_contract.py
```

Future portal work must update or extend these contracts before claiming a
customer/account behavior is ready.

## Remaining Work

- Build a reviewed invite-email sender on top of
  `provision_customer_account(contact_name)`; do not send account setup email
  through routed-alias loops.
- Add richer per-record detail pages when real customer review requires more
  than the current summary cards.
- Add browser screenshots for the new routes after the next visual pass.
- Add customer-visible file upload UI after file-size/type/cap policy is
  finalized.
- Add organization AP/people management actions only after Jeff/GL approve the
  exact business workflow.
