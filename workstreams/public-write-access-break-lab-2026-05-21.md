# Public Write And Access Break Lab - 2026-05-21

Status: local-only break lab completed through first architectural guard.

Safe return:

- Git safe return commit: `75c02cd`
- Git safe return tag:
  `safe/public-write-access-prebreak-2026-05-21-75c02cd`
- Local bench backup with files:
  `./frontend/private/backups/20260521_133852-frontend-database.sql.gz`
- Site: local Docker ERPNext/Frappe site `frontend` at
  `http://localhost:8081`
- No staging, live, DNS, Frappe Cloud, Stripe live, provider, or indexing work
  was touched.

## Fast Operator Map

Use this section when something is broken and the cause is not obvious.

| Symptom | Suspect Layer | First Test | Restore | Prevention |
|---|---|---|---|---|
| Signup/account access appears for strangers | Website/Portal Settings | `python scripts/verify/customer_portal_inventory.py --base-url http://localhost:8081 --strict-menu` | `docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.verify.public_access_break_lab.restore_invite_only_portal` | `npm run test:public-access-guard` and `doc_events` guard |
| Customer portal shows supplier/procurement links | Portal Settings menu role drift | `python scripts/verify/customer_portal_inventory.py --base-url http://localhost:8081 --strict-menu` | `docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.verify.public_access_break_lab.restore_supplier_routes` | `npm run test:public-access-guard` and `doc_events` guard |
| Marketing can see Leads, Customers, or Desk | Role/DocPerm/User role drift | `npm run test:marketing-review-access` | `docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.verify.public_access_break_lab.restore_marketing_docperms` | `npm run test:public-access-guard` and `doc_events` guard |
| New public write endpoint appears | Guest API surface drift | `python scripts/verify/allow_guest_surface_inventory.py --json` | Review endpoint, add/remove intentionally | Public-write allowlist still needed |
| Cleanup/import wants broad data mutation | Unsafe destructive process | `python scripts/verify/product_import_readiness_gate.py` | Stop; require fresh backup and dry-run | Cleanup/import wrapper still needed |

## Current Restored State

After the break probes, the local site was restored:

- `Website Settings.disable_signup = 1`
- `Portal Settings.default_role = None`
- `Portal Settings.default_portal_home = me`
- Supplier portal routes remain `Supplier` role only.
- `LT Marketing Review Access` has no direct `DocPerm` rows.
- Marketing reviewer remains website-only and no-Desk.

## Triad Summary

Observer lane found the current public access surface is small but load-bearing:

- `12` guest-callable endpoints;
- `3` public-write endpoints: newsletter signup, inquiry form, guest checkout;
- `157` `ignore_permissions` bypasses, with `0` currently requiring attention;
- customer portal strict inventory passes after restores;
- human access matrix passes after restores.

Breaker lane ranked these next probes:

- public signup auto-grants Customer;
- marketing role gets Lead DocPerm;
- supplier routes exposed to Customers;
- stock ERPNext customer routes re-enabled;
- newsletter public write abuse;
- checkout public write while ecommerce is paused;
- destructive catalog import without a fresh packet.

Review lane recommendation:

- Keep break recipes and research as capabilities.
- Promote public signup/default role, supplier-route role drift, and marketing
  DocPerm/Desk/mixed-role drift into architecture.
- Direct SQL, imports, restores, and broad cleanup still need wrapper gates
  because Frappe `doc_events` do not protect those paths.

## Breaks Actually Run

### Break 1 - Public Signup Auto-Grants Customer

Trigger:

```bash
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.verify.public_access_break_lab.break_public_signup_default_customer
```

Observed failures:

- `customer_portal_inventory.py --strict-menu` failed:
  - `Website Settings.disable_signup must stay enabled`
  - `Portal Settings.default_role should stay empty`
- `npm run test:human-access` failed on the same two settings.

Blast radius:

- Strangers could create account-shaped records.
- New users could auto-inherit the `Customer` role.
- Invite-only portal posture would be broken without changing source code.

Seriousness: Critical access exposure.

Recovery:

```bash
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.verify.public_access_break_lab.restore_invite_only_portal
python scripts/verify/customer_portal_inventory.py --base-url http://localhost:8081 --strict-menu
npm run test:human-access
```

Prevention added:

- `locally_twisted.public_access_guard`
- `doc_events` guard on `Website Settings` and `Portal Settings`
- `npm run test:public-access-guard`

### Break 2 - Supplier Routes Exposed To Customers

Trigger:

```bash
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.verify.public_access_break_lab.break_supplier_routes_as_customer
```

Observed failures:

- `customer_portal_inventory.py --strict-menu` failed for:
  - `/rfq`
  - `/supplier-quotations`
  - `/purchase-orders`
  - `/purchase-invoices`
- `npm run test:human-access` still passed.

Blast radius:

- Customer portal navigation could expose supplier/procurement paths.
- The broad human-access matrix was not enough; the portal-specific strict
  verifier is required.

Seriousness: High customer/supplier boundary drift.

Recovery:

```bash
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.verify.public_access_break_lab.restore_supplier_routes
python scripts/verify/customer_portal_inventory.py --base-url http://localhost:8081 --strict-menu
```

Prevention added:

- `doc_events` guard blocks supplier portal routes from saving as Customer.
- `npm run test:public-access-guard` proves the block.

### Break 3 - Marketing Role Gets Lead DocPerm

Trigger:

```bash
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.verify.public_access_break_lab.break_marketing_docperm_lead_read
```

Observed failures:

- `npm run test:marketing-review-access` failed:
  - `LT Marketing Review Access can read forbidden DocType Lead`
- `npm run test:human-access` failed:
  - marketing can read forbidden Lead
  - marketing role has direct DocPerm rows

Blast radius:

- External marketing could see real CRM/inquiry data.
- The inserted `DocPerm` row also carried write/create/delete values in the
  stored state, so this was worse than a simple read leak.

Seriousness: Critical data exposure.

Recovery:

```bash
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.verify.public_access_break_lab.restore_marketing_docperms
npm run test:marketing-review-access
npm run test:human-access
```

Prevention added:

- `doc_events` guard on `DocPerm`, `Role`, `User`, and `Has Role`
- blocks direct marketing `DocPerm` rows
- blocks Desk access for the marketing review role
- blocks mixing marketing review users with internal business roles
- `npm run test:public-access-guard`

## Architectural Guard Added

`apps/locally_twisted/locally_twisted/public_access_guard.py`

Blocks normal Frappe document saves for:

- public signup enabled;
- login hidden while customer account routes exist;
- portal default role set;
- portal home changed away from `me`;
- supplier routes assigned to Customer;
- stock ERPNext customer/public routes re-enabled;
- direct `DocPerm` rows for `LT Marketing Review Access`;
- Desk access on `LT Marketing Review Access`;
- mixing external marketing review access with internal business roles.

Verifier:

```bash
npm run test:public-access-guard
```

Current result:

- `6/6` rollback probes passed.

## Capability Still Needed

Frappe `doc_events` guard normal document saves. They do not fully protect:

- direct SQL;
- MariaDB console edits;
- backup restores;
- data imports that bypass standard document saves;
- destructive cleanup scripts;
- external provider actions.

Those need capability/process wrappers:

- fresh backup required;
- dry-run required;
- protected-record denylist;
- before/after record counts;
- post-run verifier bundle;
- no broad repo scan that includes `.tmp`, vendor, cache, or generated folders.

## Verification Run

```bash
python -B -m py_compile apps/locally_twisted/locally_twisted/public_access_guard.py apps/locally_twisted/locally_twisted/verify/public_access_guard_contract.py apps/locally_twisted/locally_twisted/verify/public_access_break_lab.py scripts/verify/public_access_guard_contract.py
python scripts/dev/clear_website_cache.py
npm run test:public-access-guard
npm run test:marketing-review-access
npm run test:human-access
python scripts/verify/customer_portal_inventory.py --base-url http://localhost:8081 --strict-menu
npm run test:webshop-guest-party
npm run test:ecommerce-open-mode
npm run test:owner-catalog-guard
python scripts/verify/allow_guest_surface_inventory.py --json
python scripts/verify/ignore_permissions_justification_lint.py --json
python scripts/verify/newsletter_concurrency_contract.py
```

Result:

- public access guard passed `6/6`;
- marketing review access passed;
- human access matrix passed;
- customer portal strict inventory passed.
- Webshop Guest party passed with `11/11` destructive runtime probes blocked;
- expected local ecommerce open mode passed;
- owner catalog guard passed;
- allow-guest inventory passed with `12` guest endpoints and `3` public-write
  endpoints;
- permission-bypass lint passed with `157` bypasses and `0` requiring
  attention;
- newsletter concurrency contract passed.

## Parallel-Agent Note

During this lane, another agent changed public API/inventory files and added
additional catalog sellability/sidecar research files. This workstream records
only the public access break lab and guard slice. Do not broad-stage the repo;
preserve other-agent files as their own slice.
