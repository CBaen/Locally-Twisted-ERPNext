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

Verified from the running local ERPNext database on 2026-05-15, tightened
with the combined human-access matrix on 2026-05-21, and rechecked after the
local fake-data cleanup on 2026-05-21.

Enabled users:

- `Administrator`: `System User`, full admin; not a normal operating persona.
- `cameron@builtbycameron.com`: `System User`, `LT Owner Home`,
  `LT Owner Access`, plus full support/repair roles including `System Manager`,
  `Website Manager`, finance, item, and newsletter access.
- `locallytwisted@gmail.com`: `System User`, `LT Owner Home`,
  owner/operator sales, customer, project, catalog, finance, website, and
  repair access. Temporary local password set on 2026-05-15:
  `LocalTemp2026!` until GL changes it later.
- `Guest`: `Website User`, guest role only.

Disabled users:

- None known after the local fake-data cleanup.

Other current facts:

- Temporary persona users and customer visual test users were deleted during
  the 2026-05-21 local data cleanup. Recreate them only for a deliberate
  verifier/demo pass, then clean them up again.
- The `Guest` Customer, `Guest` Portal User link, `Guest-Guest` Contact, and
  their Dynamic Link are Webshop guest-pricing infrastructure, not client data.
  Do not delete them during local fake-data cleanup; anonymous product pages,
  variant-price calls, cart, and checkout paths can fail without them. Guard:
  `python scripts/verify/webshop_guest_party_contract.py`. They now also have
  source-level Frappe `doc_events` protection in
  `locally_twisted.webshop_guest_party_guard`; the verifier proves destructive
  runtime probes are blocked.
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
- The older 2026-05-15 yellow flag is closed as of 2026-05-21: Manager no
  longer inherits `Sales Master Manager`, and the combined access matrix fails
  if Manager regains `Item Price`, `Website Item`, or `Web Page` access.

Employee:

- `LT Employee Home` is the employee Desk entry.
- Employee workspace is narrowed to assigned work, tasks, task board, and event
  jobs.
- Employee no longer gets a visible Booking Calendar shortcut; Manager retains
  booking visibility.
- Employee does not get visible customer, finance, or catalog administration.
- The stock ERPNext `All` permission rows were removed from `Contact` and
  `Address` on 2026-05-21 so employee logins no longer inherit direct customer
  contact/address access just because they can log in.

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
- Per GL on 2026-05-21, this role has no indexing authority. Do not use it for
  Search Console, sitemap submission, recrawl requests, SEO tooling access, or
  ecommerce launch approval before shop staging plus owner product approval.

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

## 2026-05-21 Combined Access Gate

`scripts/verify/human_access_silo_matrix.py` is now the combined gate to run
before giving out or changing a human login. It checks:

- admin/support and owner full access;
- default workspace landing pages for owner, manager, employee, and accounting;
- role-restricted workspaces for Owner Home, Manager Home, My Jobs,
  Accounting Home, Marketing Home, and Maintenance Home;
- direct persona permission checks that catch Manager `Item Price`/website
  access and Employee customer contact/address access;
- external marketing review isolation, including no Desk, no DocPerm rows,
  no website/product/customer/CRM/finance records, and no indexing authority;
- invite-only customer portal settings;
- sanitized maintenance status.

Commands passed locally on 2026-05-21:

```powershell
python scripts/setup/sync_backend_workspaces.py
python scripts/verify/human_access_silo_matrix.py
npm run test:human-access
python scripts/verify/marketing_review_access_boundary.py
python scripts/verify/backend_workspace_parity.py
python scripts/verify/finance_workspace_parity.py
python scripts/verify/marketing_workspace_parity.py
python scripts/verify/custom_doctype_permission_boundary.py
python scripts/verify/maintenance_admin_boundary.py
python scripts/verify/customer_portal_inventory.py --strict-menu
python scripts/verify/customer_portal_home_contract.py
python scripts/verify/customer_account_provisioning_contract.py
python scripts/verify/owner_business_access_contract.py
$env:LT_DESK_TEST_USER='locallytwisted@gmail.com'; $env:LT_DESK_TEST_PASSWORD='LocalTemp2026!'; npm run test:desk-owner
```

Post-cleanup verifier note: `persona_workspace_permissions.py` now skips
absent temp persona users instead of failing because the cleanup removed those
fake accounts. It still checks the shortcut/permission contract for any temp
persona user that is intentionally reprovisioned.

Local fake-data cleanup receipt on 2026-05-21:

- backup taken before cleanup:
  `./frontend/private/backups/20260521_102343-frontend-database.sql.gz`;
- operational customer/CRM/sales/payment/tasks/events/custom LT data,
  communications, queue rows, logs, route/access history, deletion history, and
  version history verified at `0`;
- system Webshop guest plumbing preserved/restored after cleanup:
  `Customer:Guest`, `Portal User:Guest -> Customer Guest`,
  `Contact:Guest-Guest`, and one Dynamic Link, with source-level runtime guard
  probes passing after restart/cache refresh;
- remaining users: `Administrator`, `cameron@builtbycameron.com`, `Guest`,
  and `locallytwisted@gmail.com`;
- catalog/config assets preserved: Items, Website Items, Item Prices,
  Workspaces, Role Profiles, and Files attached only to Item, Website Item, or
  unattached public/site assets.

## Follow-Up Queue Inputs

- Verify the exact Jeff/business-owner cutover account and owner daily path
  before improving any secondary profile.
- Before any real assistant integration, add the external-provider auth gate
  and token verifier. Local Frappe session proof is not enough for ChatGPT,
  MCP, OpenAPI, or other API clients.
- Do not recreate `/owner-actions` fake records unless GL asks for a fresh
  local demo/training pass. If they are recreated, keep them clearly marked
  with `LT-DEMO-OWNER-ACTIONS` and clean them up afterward.
- Keep Cameron/Built by Cameron support access intact while narrowing the
  client-facing owner path.
- Add focused failing permission-matrix verifiers only for exposure that
  affects the required owner/support profiles.
- Keep the combined access matrix in the release gate so Manager cannot regain
  `Item Price` through broad ERPNext roles and Employee cannot regain
  Contact/Address access through the stock `All` role.
- The leftover enabled customer visual test user was removed during the
  2026-05-21 local fake-data cleanup.
- On 2026-05-22 the standing local `marketing@exploringnotboring.com` account
  was created as a `Website User` with only `LT Marketing Review Access`.
  Future staging/live accounts must keep that exact boundary: no
  customer/supplier/Desk/admin roles. Rerun the marketing boundary verifier,
  human access silo matrix, and live HTTP proof after provisioning it.
- If a Maintenance Admin account is created, keep it role-only and rerun the
  maintenance boundary verifier before sharing credentials.
