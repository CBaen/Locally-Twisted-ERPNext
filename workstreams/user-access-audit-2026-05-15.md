# User Access Audit - 2026-05-15

## Scope

This handoff records the current human-user access review for the local
ERPNext/Frappe site at `http://localhost:8081`.

It covers:

- enabled users;
- Frappe `System User` versus `Website User` shape;
- LT role profiles, roles, default workspaces, and module profiles;
- customer portal, Desk persona, finance, maintenance, and marketing-review
  boundaries;
- follow-up hardening work that remains current.

Cross-link: the external marketing reviewer feature lives at
`workstreams/marketing-review-access-2026-05-15.md`.

## Current Live Inventory

Verified from the running local ERPNext database on 2026-05-15.

Enabled users:

- `Administrator`: `System User`, full admin; not a normal operating persona.
- `cameron@builtbycameron.com`: `System User`, `LT Owner Home`,
  `LT Owner Access`, plus `System Manager` and `Website Manager`.
- `locallytwisted@gmail.com`: `System User`, `LT Owner Home`,
  owner/operator sales, customer, project, and catalog access; no
  `System Manager`.
- `lt-owner-temp@example.com`: `System User`, `LT Owner` role profile,
  `LT Owner Calm Desk`, `LT Owner Home`.
- `lt-manager-temp@example.com`: `System User`, `LT Manager` role profile,
  `LT Manager Operations Desk`, `LT Manager Home`.
- `lt-employee-temp@example.com`: `System User`, `LT Employee` role profile,
  `LT Employee Job Desk`, `LT Employee Home`.
- `lt-accountant-temp@example.com`: `System User`, `LT Accountant` role
  profile, `LT Accountant Desk`, `LT Accountant Home`.
- `lt-admin-temp@example.com`: `System User`, `LT Admin` role profile.
- `Guest`: `Website User`, guest role only.
- `lt-portal-visual-1778476910635718999@example.invalid`: enabled customer
  test `Website User` with `Customer`.

Disabled users:

- `locallytwisted@yahoo.com`: disabled `System User`.
- `lt-contractor-temp@example.com`: disabled `Website User` with `Customer`.

Other current facts:

- No enabled Supplier user was found.
- No permanent marketing reviewer user was found.
- No enabled Maintenance Admin user was found.
- `User Permission` rows are empty, so current restrictions are based on role
  profiles, roles, permission hooks, workspaces, and portal code rather than
  per-user document restrictions.

## Access Boundaries

Owner:

- `LT Owner Home` is the owner Desk entry.
- Owner personas can work inquiries, bookings, customers, contacts, tasks,
  projects, and catalog tools.
- `cameron@builtbycameron.com` also retains support/admin roles.

Manager:

- `LT Manager Home` is the manager Desk entry.
- Manager workspace surfaces inquiry, booking, customer/contact, job, task, and
  add-record actions.
- The current role matrix still gives the manager `Item Price` create/write/delete
  through ERPNext roles, even though catalog tools are not surfaced in the
  manager workspace. This is a current hardening target, not a closed item.

Employee:

- `LT Employee Home` is the employee Desk entry.
- Employee workspace is narrowed to assigned work, tasks, task board, and event
  jobs.
- Employee does not get visible customer, finance, or catalog administration.

Accountant:

- `LT Accountant Home` is the accountant Desk entry.
- Accountant workspace covers Sales Invoices, Payment Requests, Payment
  Entries, Customers, Reminder Review Report, Journal Entries, and Chart of
  Accounts.
- Bank/vendor/payroll setup remains intentionally hidden and deferred.

Customer:

- Customer accounts are `Website User` plus `Customer`.
- Public signup is disabled.
- Guest `/me` is blocked.
- Customers use LT-owned `/me`, `/account/*`, and `/organization/*` pages.
- Customer actions use allowlisted portal DTOs and LT customer portal records;
  they must not expose raw Desk/backend records.

Marketing reviewer:

- Marketing reviewers are `Website User` plus explicit
  `LT Marketing Review Access`.
- `LT Marketing Review Access` has `desk_access = 0` and no DocPerm rows.
- `/marketing-review` is the only owned review doorway.
- `/me` redirects marketing reviewers to `/marketing-review`.
- Permission hooks deny sensitive backend DocType list/read/write/delete
  access and block sensitive record mutation for explicit marketing reviewers.

Supplier:

- Supplier portal menu rows exist for native supplier routes.
- They are intentionally separate from the customer/client portal.
- No enabled Supplier user was found in this audit.

Maintenance Admin:

- `LT Maintenance Admin Access` boundary passes.
- The role is intended for sanitized maintenance heartbeat/report visibility,
  not raw logs, customer records, finance records, or System Manager access.
- No enabled Maintenance Admin user was found in this audit.

## Verification Receipt

Commands passed locally on 2026-05-15:

```powershell
python scripts/verify/customer_portal_inventory.py --base-url http://localhost:8081 --strict-menu
python scripts/verify/custom_doctype_permission_boundary.py
python scripts/verify/backend_workspace_parity.py
python scripts/verify/finance_workspace_parity.py
python scripts/verify/maintenance_admin_boundary.py
python scripts/verify/maintenance_heartbeat.py
python scripts/verify/customer_portal_v1_contract.py
python scripts/verify/customer_portal_home_contract.py
python scripts/verify/customer_account_provisioning_contract.py
python scripts/verify/customer_documents_contract.py
python scripts/verify/customer_contact_points_contract.py
python scripts/verify/marketing_review_access_boundary.py
npm run test:marketing-review-access
$env:LT_DESK_TEST_PASSWORD='LocalTemp2026!'; npm run test:desk-personas
$env:LT_DESK_TEST_USER='lt-owner-temp@example.com'; $env:LT_DESK_TEST_PASSWORD='LocalTemp2026!'; npm run test:desk-owner
```

Manual/local proof also created a temporary marketing Website User, logged in
through `http://localhost:8081/api/method/login`, confirmed `/me` resolved to
`/marketing-review`, confirmed the review page rendered
`data-lt-marketing-review` and `Exploring Not Boring`, confirmed no backend
markers such as `/app/`, `Sales Invoice`, `Email Queue`, or `Payment Entry`
were present, and deleted the temporary User.

Known yellow/non-blocking result:

- `maintenance_heartbeat.py` still reports `client_notification_preferences`
  yellow until the owner chooses recipient, cadence, topic, and channel.

## Follow-Up Queue Inputs

- Add focused failing verifiers before changing broad ERPNext role permissions.
- Decide whether Manager should retain any `Item Price` create/write/delete
  permission; the current workspace hides catalog tools but the role matrix
  still allows the permission.
- Decide whether to remove or disable the leftover enabled customer visual
  test user.
- If a real Exploring Not Boring account is created, create it as a `Website
  User` with only `LT Marketing Review Access`, no customer/supplier/Desk/admin
  roles, and rerun the marketing boundary verifier plus live HTTP proof.
- If a Maintenance Admin account is created, keep it role-only and rerun the
  maintenance boundary verifier before sharing credentials.
