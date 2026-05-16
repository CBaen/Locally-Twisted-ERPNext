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

Owner phone/action feature handoff:
`workstreams/owner-phone-action-center-2026-05-15.md`.

## Current Direction

GL correction on 2026-05-15: this access track should focus on the business
owner's access and use, plus Cameron/Built by Cameron support access. Those are
the only profiles that require active access design right now.

Primary required profiles:

- Jeff/business owner: the real daily operator who needs the simplest possible
  LT owner Desk path.
- Cameron/Built by Cameron support: the build/support account that needs
  enough admin reach to maintain and repair the system.

Secondary boundary profiles:

- Manager, Employee, Accountant, Customer, Supplier, Maintenance Admin, and
  Marketing Reviewer profiles stay documented for audit and regression
  boundaries only.
- Do not turn these secondary profiles into separate feature lanes unless they
  directly protect or unblock business-owner/support use, or GL explicitly
  reopens that profile.
- Keep this track local to this handoff and
  `workstreams/erpnext-backend-simplification.md`. Cross-link into commerce,
  paperwork, customer portal, marketing review, or public-site handoffs only
  when an owner workflow, verifier, or permission boundary actually requires
  it.

## Current Live Inventory

Verified from the running local ERPNext database on 2026-05-15.

Enabled users:

- `Administrator`: `System User`, full admin; not a normal operating persona.
- `cameron@builtbycameron.com`: `System User`, `LT Owner Home`,
  `LT Owner Access`, plus `System Manager` and `Website Manager`.
- `locallytwisted@gmail.com`: `System User`, `LT Owner Home`,
  owner/operator sales, customer, project, and catalog access; no
  `System Manager`. Temporary local password set on 2026-05-15:
  `LocalTemp2026!` until GL changes it later.
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
- `Call or Text` is now the first owner fast path and opens `/owner-actions`,
  a phone-first local page backed by owner-safe DTOs instead of raw ERPNext
  records.
- Owner personas can work inquiries, bookings, customers, contacts, tasks,
  projects, and catalog tools.
- `cameron@builtbycameron.com` also retains support/admin roles.
- Next access work should verify the exact Jeff/business-owner cutover account,
  what Jeff must see first after login, and which owner actions must be one
  click from `LT Owner Home`.
- Immediate-access receipt on 2026-05-15: `locallytwisted@gmail.com` was
  verified through `npm run test:desk-owner` with the temporary owner password
  and landed on the Owner Home command center.
- Assistant integration boundary: ChatGPT is only one future adapter. The
  current local implementation is provider-neutral and OAuth/API-compatible at
  the DTO boundary, but external assistant auth is not enabled. Future OAuth,
  API-key, MCP, OpenAPI, or other provider adapters must consume the owner DTOs
  and pass their own auth verifier before exposure.
- Initial owner write surface is `log_contact_attempt` only. It creates one
  Comment on the source record and must not queue customer email, send texts,
  place calls, mutate stages, create finance records, or submit orders.

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
- Employee no longer gets a visible Booking Calendar shortcut; Manager retains
  booking visibility.
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
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.verify.persona_workspace_permissions.run
python scripts/verify/finance_workspace_parity.py
python scripts/verify/maintenance_admin_boundary.py
python scripts/verify/maintenance_heartbeat.py
python scripts/verify/customer_portal_v1_contract.py
python scripts/verify/customer_portal_home_contract.py
python scripts/verify/customer_account_provisioning_contract.py
python scripts/verify/customer_documents_contract.py
python scripts/verify/customer_contact_points_contract.py
python scripts/verify/marketing_review_access_boundary.py
python scripts/setup/sync_owner_demo_data.py
python scripts/verify/owner_business_access_contract.py
npm run test:marketing-review-access
$env:LT_DESK_TEST_USER='locallytwisted@gmail.com'; $env:LT_DESK_TEST_PASSWORD='LocalTemp2026!'; npm run test:owner-actions
$env:LT_DESK_TEST_PASSWORD='LocalTemp2026!'; npm run test:desk-personas
$env:LT_DESK_TEST_USER='lt-owner-temp@example.com'; $env:LT_DESK_TEST_PASSWORD='LocalTemp2026!'; npm run test:desk-owner
$env:LT_DESK_TEST_USER='locallytwisted@gmail.com'; $env:LT_DESK_TEST_PASSWORD='LocalTemp2026!'; npm run test:desk-owner
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

- Verify the exact Jeff/business-owner cutover account and owner daily path
  before improving any secondary profile.
- Before any real assistant integration, add the external-provider auth gate
  and token verifier. Local Frappe session proof is not enough for ChatGPT,
  MCP, OpenAPI, or other API clients.
- Keep `/owner-actions` fake records local and clearly marked with
  `LT-DEMO-OWNER-ACTIONS`; remove them with
  `python scripts/setup/sync_owner_demo_data.py --cleanup` when no longer
  useful for demo/training.
- Keep Cameron/Built by Cameron support access intact while narrowing the
  client-facing owner path.
- Add focused failing permission-matrix verifiers only for exposure that
  affects the required owner/support profiles.
- Decide whether Manager should retain any `Item Price` create/write/delete
  permission only if that exposure affects owner/support delegation or
  handoff safety.
- Decide whether to remove or disable the leftover enabled customer visual
  test user if it affects owner/support account clarity or launch safety.
- If a real Exploring Not Boring account is created, create it as a `Website
  User` with only `LT Marketing Review Access`, no customer/supplier/Desk/admin
  roles, and rerun the marketing boundary verifier plus live HTTP proof.
- If a Maintenance Admin account is created, keep it role-only and rerun the
  maintenance boundary verifier before sharing credentials.
