---
id: erpnext-external-review-access
name: ERPNext External Review Access
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted external website-review access for non-operator reviewers
currently_true: verified
verification_level: 3
last_verified: 2026-05-21
evidence_quality: direct
successful_uses: 2
failed_uses: 1
regressions: 0
depends_on:
  - customer-client-portal-contract
  - erpnext-simplified-role-verification
  - erpnext-maintenance-heartbeat-boundary
used_by:
  - marketing-review-access-2026-05-15
  - user-access-audit-2026-05-15
tags:
  - Locally Twisted
  - ERPNext
  - Frappe
  - external review
  - marketing access
  - Website User
---

# ERPNext External Review Access

Use this recipe when creating or auditing an outside reviewer account that only
needs to review the public website, not operate ERPNext.

Current LT example: `Exploring Not Boring` marketing review access. For controlled Desk-bound vendor building/reset work, use sibling recipe `erpnext-external-marketing-access-reset.md`, not this review-only recipe.

## Contract

- External reviewers are standard Frappe `Website User` accounts.
- The access grant is an explicit narrow role, currently
  `LT Marketing Review Access`.
- The role has `desk_access = 0`.
- The role has no DocPerm rows.
- The reviewer does not get `Desk User`, `Customer`, `Supplier`,
  `Website Manager`, `System Manager`, `Item Manager`, sales, finance, owner,
  accountant, maintenance, or other backend roles.
- The owned public review route is `/marketing-review`.
- `/me` redirects marketing reviewers to `/marketing-review`; it does not place
  them in the customer portal.
- The route is `noindex` and shows only public review links plus the protected
  backend-generated Marketing Review Packet download.
- The packet is generated fresh at request time and stays sanitized: public
  review links, sitemap, robots, review status, and access boundaries only.
  It must not include backend record exports, customer data, files, orders,
  invoices, payments, Leads, or product source records.
- Backend-sensitive DocTypes are hidden and denied through marketing-only
  permission query conditions, `has_permission`, and mutation guards.

## Implementation Surfaces

```text
apps/locally_twisted/locally_twisted/marketing_review_access.py
apps/locally_twisted/locally_twisted/seed/sync_marketing_review_access.py
apps/locally_twisted/locally_twisted/verify/marketing_review_access_boundary.py
apps/locally_twisted/locally_twisted/www/marketing-review/index.py
apps/locally_twisted/locally_twisted/www/marketing-review/index.html
apps/locally_twisted/locally_twisted/www/me.py
apps/locally_twisted/locally_twisted/hooks.py
scripts/setup/sync_marketing_review_access.py
scripts/verify/marketing_review_access_boundary.py
```

Feature handoff:

```text
workstreams/marketing-review-access-2026-05-15.md
```

Access-audit handoff:

```text
workstreams/user-access-audit-2026-05-15.md
```

## Role Check Rule

For this boundary, do not use broad/effective role helpers as the authority.
Check explicit `Has Role` membership on the User record.

Reason: Administrator/bench contexts can appear to have broad framework roles.
Using effective role lookup for a narrow reviewer guard can misclassify admin
execution as an external reviewer and block unrelated contracts or setup work.

Use broad role helpers only for normal UI adaptation where admin over-inclusion
is acceptable.

## Verification

Run:

```bash
python scripts/setup/sync_marketing_review_access.py
python scripts/verify/marketing_review_access_boundary.py
npm run test:marketing-review-access
```

After changing `/me`, hooks, role logic, or any adjacent portal route, also run:

```bash
python scripts/verify/customer_portal_home_contract.py
python scripts/verify/customer_portal_v1_contract.py
python scripts/verify/customer_portal_inventory.py --base-url http://localhost:8081 --strict-menu
```

After changing Desk/persona access at the same time, also run:

```bash
python scripts/verify/backend_workspace_parity.py
python scripts/verify/finance_workspace_parity.py
$env:LT_DESK_TEST_PASSWORD='LocalTemp2026!'; npm run test:desk-personas
$env:LT_DESK_TEST_USER='lt-owner-temp@example.com'; $env:LT_DESK_TEST_PASSWORD='LocalTemp2026!'; npm run test:desk-owner
```

For live local HTTP proof:

1. Create a temporary marketing `Website User` through
   `locally_twisted.verify.marketing_review_access_boundary.create_fixture`.
2. Log in through `/api/method/login`.
3. Verify `/me` resolves to `/marketing-review`.
4. Verify `/marketing-review` renders `data-lt-marketing-review` and
   `Exploring Not Boring`.
5. Verify the packet download is present and only available to the explicit
   marketing review role.
6. Verify the page body contains no backend route markers such as `/app/` and
   no backend labels such as `Sales Invoice`, `Email Queue`, or
   `Payment Entry`.
7. Delete the temporary User through
   `locally_twisted.verify.marketing_review_access_boundary.cleanup_fixture`.

## Failure Modes

- Adding `Desk User` because the reviewer wants to "look around."
- Giving `Customer` access and accidentally routing the reviewer into the
  customer portal.
- Adding DocPerm rows to the reviewer role instead of using public routes.
- Relying on `frappe.get_roles()` for the least-privilege boundary and
  misclassifying Administrator or bench execution.
- Letting the review account edit website pages, products, policies, blog
  posts, customer records, or files.
- Uploading a static review packet and forgetting to refresh it.
- Adding private backend exports or customer/order data to the packet because
  the reviewer asked for "view privileges."
- Running rollback-heavy customer/marketing verifiers in parallel and confusing
  session/user context.
- Reusing the review-only recipe to justify broad builder/admin access; builder access has its own narrower contract and reset proof path.

## Current LT Receipt

Verified on 2026-05-15:

- marketing role exists;
- `desk_access = 0`;
- no DocPerm rows;
- marketing verifier passes and rolls back its temporary user;
- customer portal home and V1 contracts pass after the explicit-role fix;
- live local HTTP proof passes and deletes its temporary User;
- Owner, Manager, Employee, and Accountant browser Desk proofs pass after the
  hook/cache restart.
