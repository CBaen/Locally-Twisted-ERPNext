# Marketing Review Access - 2026-05-15

## Scope

This slice creates a website-only access lane for the external marketing
company `Exploring Not Boring`.

It is for public website review only: copy, layout, navigation, proof,
portfolio, contact path, and policy-surface review.

It is not backend access. It must not expose ERPNext Desk, Leads, Customers,
Contacts, Files, Communications, Email Queue, Orders, Invoices, Payments,
Products, maintenance rows, raw logs, reports, or customer portal records.

## Implementation

Source files:

- `apps/locally_twisted/locally_twisted/marketing_review_access.py`
- `apps/locally_twisted/locally_twisted/seed/sync_marketing_review_access.py`
- `apps/locally_twisted/locally_twisted/verify/marketing_review_access_boundary.py`
- `apps/locally_twisted/locally_twisted/www/marketing-review/index.py`
- `apps/locally_twisted/locally_twisted/www/marketing-review/index.html`
- `scripts/setup/sync_marketing_review_access.py`
- `scripts/verify/marketing_review_access_boundary.py`

Role:

- `LT Marketing Review Access`
- `desk_access = 0`
- no DocPerm rows
- sensitive DocTypes are protected by marketing-role-only permission hooks and
  mutation blockers
- intended user type: `Website User`
- role checks must test the explicit `Has Role` row on the User record. Do not
  use broad/effective role helpers for this boundary; `Administrator` can
  appear to have framework-wide roles and can otherwise be misclassified.

Protected route:

- `/marketing-review`
- redirects guests to `/login?redirect-to=/marketing-review`
- requires `LT Marketing Review Access`
- shows only public review links
- marketing users who land on `/me` are redirected to `/marketing-review`

## Guardrails

- Do not create a custom Frappe `User Type` for this lane. Use standard
  `Website User` plus the narrow role.
- Do not add `Desk User`, `Website Manager`, `Customer`, `Supplier`,
  `System Manager`, finance, sales, item, owner, accountant, or maintenance
  roles to a marketing reviewer.
- Do not add DocPerm rows to `LT Marketing Review Access`.
- If Frappe framework defaults expose owner-scoped records such as `Contact`,
  keep the marketing-role hook boundary in place rather than weakening the
  global customer/contact permissions.
- Do not use customer portal routes as the marketing review surface.
- Do not use this account for editing website pages, products, blog posts,
  policy copy, or customer records. It is review-only.
- Keep this lane separate from the customer portal lane documented in
  `workstreams/customer-client-portal-translation-2026-05-10.md`.
- Cross-link: the broader current access audit is documented in
  `workstreams/user-access-audit-2026-05-15.md`.

## Verification

```powershell
python scripts/setup/sync_marketing_review_access.py
python scripts/verify/marketing_review_access_boundary.py
npm run test:marketing-review-access
```

The verifier creates a temporary marketing `Website User`, checks it has the
marketing role and none of the forbidden roles, confirms the review context is
available to that role only, confirms `/me` redirects to `/marketing-review`,
checks forbidden DocTypes for no actual list/read/write/delete access, proves
Contact creation is blocked, and rolls the temporary user back.

Local receipt from 2026-05-15:

- `python -m py_compile` passed for the new access files plus `hooks.py` and
  `www/me.py`.
- `python scripts/setup/sync_marketing_review_access.py` passed.
- `python scripts/verify/marketing_review_access_boundary.py` passed.
- `python scripts/dev/clear_website_cache.py --restart` ran after hook/route
  changes.
- HTTP proof with a temporary marketing Website User: login returned 200,
  `/me` resolved to `/marketing-review`, `/marketing-review` returned 200,
  `data-lt-marketing-review` rendered, `Exploring Not Boring` rendered, and
  customer/ERP markers such as `Sales Invoice`, `Email Queue`, and `CRM-LEAD`
  were absent from the page body. The temporary User was deleted.

Follow-up audit receipt from 2026-05-15:

- A broader access review found the first version of the guard was too broad in
  bench/Admin contexts because it relied on effective role lookup. Customer
  portal contract verifiers failed while creating rollback fixtures.
- The guard was tightened to explicit `Has Role` membership, and `/me` now uses
  the same explicit-role helper before redirecting marketing reviewers.
- Reverification after restart: `python scripts/verify/marketing_review_access_boundary.py`,
  `npm run test:marketing-review-access`,
  `python scripts/verify/customer_portal_home_contract.py`,
  `python scripts/verify/customer_portal_v1_contract.py`, the live HTTP
  marketing proof, `npm run test:desk-personas`, and `npm run test:desk-owner`
  passed.

## Current Non-Work

- No permanent Exploring Not Boring user has been created in the local DB.
- No production/Frappe Cloud deploy was performed in this slice.
- GitHub push to `origin/main` is source archive only; it is not a
  production/Frappe Cloud deploy and does not push code live.
