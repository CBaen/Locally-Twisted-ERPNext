# Customer / Client Portal Translation

Last verified: 2026-05-11 by Codex.

## Purpose

Translate ERPNext's default customer portal into a Locally Twisted account
experience without breaking guest-first public flows. This lane is for customers
and clients only; owner, employee, accountant, contractor, vendor, and backend
Desk access stay in their own lanes.

## Ownership And Gate Decision

Codex owns customer/client portal closeout for now. OpenClaw/Moji can continue
shop, product, cart, and checkout closeout without bundling this portal slice.
The two lanes may share a dirty worktree, but they must not share one closeout
claim, one commit, or one proof packet unless GL explicitly merges them later.

Portal-owned closeout files:

- `apps/locally_twisted/locally_twisted/customer_portal_pages.py`
- `apps/locally_twisted/locally_twisted/templates/includes/customer_portal_page.html`
- `apps/locally_twisted/locally_twisted/public/css/lt-customer-portal.css`
- `apps/locally_twisted/locally_twisted/www/login.html`
- `apps/locally_twisted/locally_twisted/www/login.py`
- `apps/locally_twisted/locally_twisted/public/css/lt-login.css`
- `apps/locally_twisted/locally_twisted/verify/customer_portal_home_contract.py`
- `apps/locally_twisted/locally_twisted/verify/customer_portal_v1_contract.py`
- `apps/locally_twisted/locally_twisted/verify/customer_portal_review_fixture.py`
- `scripts/verify/customer_login_visual.spec.js`
- `scripts/verify/customer_portal_visual.spec.js`
- `capabilities/recipes/customer-client-portal-contract.md`
- this workstream

Shared files requiring hunk-level review before staging:

- `apps/locally_twisted/locally_twisted/hooks.py`
- `package.json`
- `capabilities/INDEX.md`
- `capabilities/registry/capability-registry.jsonl`

## Current Verified State

Commands:

```bash
python scripts/verify/customer_portal_v1_contract.py
python scripts/verify/customer_portal_inventory.py --base-url http://localhost:8081 --strict-menu --report output/customer-portal-inventory.json
python scripts/verify/customer_portal_home_contract.py
python scripts/verify/customer_account_provisioning_contract.py
npm run test:customer-login-visual
npx playwright test scripts/verify/interactive_layout.spec.js --grep "logged-in public header exposes logout" --reporter=line --workers=1
```

Result on 2026-05-11: all listed contracts passed locally. The focused logout
regression passed with `LT_DESK_TEST_USER` and `LT_DESK_TEST_PASSWORD` set to
the local dev account.

Hard boundaries currently holding:

- `/login#login` returns the branded LT customer login shell and preserves
  working Frappe authentication for Website Users.
- `/login#signup` returns a branded invite-only account message; public signup
  remains closed.
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
- Signed-in public users can log out from both desktop header and mobile drawer.
- Signed-in customer portal users can log out from the top action area and the
  menu footer.
- Signed-in accounts without a connected LT customer record land on the
  account-access-blocked screen with a visible logout action instead of a dead
  end.

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
- `apps/locally_twisted/locally_twisted/public/css/lt-customer-portal.css`

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
- LT-owned account pages hide Frappe's default portal sidebar and use the
  branded account shell plus in-page nav. Organization Portal appears in the
  account nav because it is one of the eight customer-facing value surfaces.

## catalog_data Reference Signals

Reference files inspected read-only from retired catalog-data source material.
These are historical intent signals only, not active local dependencies:

- `addons/locally_twisted/controllers/portal.py`
- `addons/locally_twisted/views/portal_templates.xml`
- `addons/locally_twisted/security/lt_groups.xml`
- `addons/locally_twisted/security/lt_rules.xml`

Translated intent:

- Adaptive portal home.
- Customer-safe event details.
- Day-of/event status cards.
- Narrow customer prep updates.
- Completed-event photo/file support.
- Company/crew photos excluded from customer visibility.
- Portal controller/service ownership instead of backend record exposure.

Do not port catalog_data code or schema directly.

## Verifier Contract

Primary V1 gate:

```bash
python scripts/verify/customer_portal_v1_contract.py
```

This creates rollback-safe Customer, Contact, User, Sales Order, and
organization membership records, renders all individual and organization
routes, proves the eight module keys exist, proves change/repeat actions create
review requests, proves the Sales Order is not directly mutated, and proves the
customer file-registration guard blocks arbitrary File attachment by name.

Supporting gates:

```bash
python scripts/verify/customer_portal_inventory.py --base-url http://localhost:8081 --strict-menu --report output/customer-portal-inventory.json
python scripts/verify/customer_portal_home_contract.py
python scripts/verify/customer_account_provisioning_contract.py
npm run test:customer-portal-visual
npm run test:customer-login-visual
```

Future portal work must update or extend these contracts before claiming a
customer/account behavior is ready.

Visual shell proof added on 2026-05-11:

- `lt-customer-portal.css` is registered through `web_include_css`, not kept as
  a Python inline style block.
- `/login` is overridden with `www/login.html`, `www/login.py`, and
  `lt-login.css`. The page uses the premium-concierge account visual direction,
  hides public marketing chrome, keeps Frappe's `#login_email`,
  `#login_password`, `.form-login`, and `.btn-login` hooks, and keeps signup as
  invite-only account help instead of public self-service signup.
- `scripts/verify/customer_login_visual.spec.js` checks `/login#login` on
  mobile and desktop, checks `/login#signup`, proves a fixture Website User can
  sign in through the visible form, then reaches `/me`.
- `scripts/verify/customer_portal_visual.spec.js` creates a temporary
  customer account, logs in through the real `/api/method/login` path, verifies
  desktop/mobile containment, verifies the LT logo loads, blocks native/internal
  portal words, snapshots account home, and cleans up the temporary customer
  records.
- `scripts/verify/interactive_layout.spec.js` includes a focused session test
  proving API login, blocked-account logout visibility, public header logout,
  mobile drawer logout, and return to logged-out `Sign In` state.
- Python module edits can leave local web workers serving mixed old/new portal
  state. If the visual contract reports stale nav counts after route-context
  edits, restart the local backend/frontend containers, clear website cache, and
  rerun the browser contract.

## Remaining Work

- Build a reviewed invite-email sender on top of
  `provision_customer_account(contact_name)`; do not send account setup email
  through routed-alias loops.
- Add richer per-record detail pages when real customer review requires more
  than the current summary cards.
- Add customer-visible file upload UI after file-size/type/cap policy is
  finalized.
- Add organization AP/people management actions only after Jeff/GL approve the
  exact business workflow.
