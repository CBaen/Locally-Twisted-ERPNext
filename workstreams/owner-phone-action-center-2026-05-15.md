# Owner Phone Action Center - 2026-05-15

## Scope

Owner/support access lane only. This feature gives Jeff/business owner the
fewest-tap local path to call or text urgent Leads/Contacts/bookings from a
phone, while keeping future assistant access provider-neutral.

Do not spread this into Manager, Employee, Accountant, Customer, Marketing,
Maintenance, checkout, finance, or public-site lanes unless a specific owner
workflow or verifier requires it.

Related docs:

- `workstreams/user-access-audit-2026-05-15.md`
- `workstreams/erpnext-backend-simplification.md`
- `capabilities/recipes/erpnext-owner-business-access-api.md`
- `locally-twisted-decisions.md`
- `locally-twisted-queue.md`

## Implemented

- Added provider-neutral owner DTOs in
  `apps/locally_twisted/locally_twisted/owner_business_access.py`.
- Added whitelisted adapter methods in
  `apps/locally_twisted/locally_twisted/api/owner_business.py`.
- Added `/owner-actions`, a noindex owner page with urgent contacts, upcoming
  bookings, `tel:` links, `sms:` links, message drafts, and record links.
- Added `Call or Text` to `LT Owner Home` as the first owner action path.
- Added local fake-data seed:
  `python scripts/setup/sync_owner_demo_data.py`.
- Added cleanup:
  `python scripts/setup/sync_owner_demo_data.py --cleanup`.
- Added rollback-safe API contract:
  `python scripts/verify/owner_business_access_contract.py`.
- Added browser proof:
  `npm run test:owner-actions`.

## Current Contract

- `locallytwisted@gmail.com` and support/admin users with `LT Owner Access` or
  `System Manager` may read the owner action DTOs.
- Guests and non-owner users are blocked.
- The DTOs return small, client-safe objects; raw ERPNext records are not the
  external contract.
- Phone calls and texts require a human tap. The system creates links and
  message drafts only.
- Initial write surface is `log_contact_attempt`; it creates one Comment on
  Lead, Contact, Customer, or Sales Order and must not queue email, send
  messages, place calls, submit records, or change CRM/accounting state.
- ChatGPT is one possible future adapter. OAuth/API/MCP/OpenAPI or other
  provider adapters must consume this DTO layer and pass their own auth/token
  verifier before any external exposure.

## Fake Local Data

Persistent local demo records are marked with `LT-DEMO-OWNER-ACTIONS`.

The seed creates:

- three fake Leads across useful CRM stages;
- Lead-linked Task cascade records through the existing stage cascade;
- one fake Customer and Contact;
- one draft Sales Order for the booking/calendar side.

These records are for localhost owner experience and verifiers only. They are
not launch/customer data.

## Verification Receipt

Passed locally on 2026-05-15:

```bash
python -m compileall apps/locally_twisted/locally_twisted/owner_business_access.py apps/locally_twisted/locally_twisted/api/owner_business.py apps/locally_twisted/locally_twisted/www/owner-actions/index.py apps/locally_twisted/locally_twisted/seed/owner_demo_data.py apps/locally_twisted/locally_twisted/verify/owner_business_access_contract.py scripts/setup/sync_owner_demo_data.py scripts/verify/owner_business_access_contract.py
node --check scripts/verify/owner_action_center.spec.js
python scripts/setup/sync_backend_workspaces.py
python scripts/setup/sync_owner_demo_data.py
python scripts/verify/backend_workspace_parity.py
python scripts/verify/owner_business_access_contract.py
python scripts/dev/clear_website_cache.py
export LT_DESK_TEST_USER='locallytwisted@gmail.com'; export LT_DESK_TEST_PASSWORD='LocalTemp2026!'; npm run test:owner-actions
export LT_DESK_TEST_USER='locallytwisted@gmail.com'; export LT_DESK_TEST_PASSWORD='LocalTemp2026!'; npm run test:desk-owner
export LT_DESK_TEST_PASSWORD='LocalTemp2026!'; npm run test:desk-personas
python scripts/verify/synthetic_business_pipeline.py
```

Key proof:

- Owner action browser proof passed.
- Owner Desk route proof passed.
- Manager/Employee/Accountant persona route proof still passed.
- Backend workspace parity passed.
- Provider-neutral owner API contract passed and cleaned its temporary records.
- Synthetic business pipeline passed with `broken_piping: 0`.

## Next Safe Steps

- Add the external auth adapter only after choosing a provider shape. The
  adapter must verify tokens/scopes before calling the DTO layer.
- Add search UI on `/owner-actions` only if Jeff needs lookup beyond urgent
  cards.
- Add richer contact-log UI only if the Comment-only API remains the write
  boundary.
- Do not add automated text/call/customer-send behavior without a new decision,
  feature handoff, and verifier.
