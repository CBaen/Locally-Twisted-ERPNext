---
name: Webshop Guest Party Cleanup Regression
type: failure
failure_kind: regression_pattern
schema_version: 0.1
date_discovered: 2026-05-21
last_updated: 2026-05-21
status: guarded
scope: project
owner_context: Locally Twisted ERPNext/Frappe local fake-data cleanup and public Webshop
related_capabilities:
  - erpnext-webshop-guest-party-contract
  - frappe-public-storefront-security
  - launch-repo-cleanup-and-evidence-retention
related_failures:
  - ecommerce-variant-price-source-drift
tags:
  - ERPNext
  - Frappe
  - Webshop
  - Guest
  - cleanup
  - public-pricing
---

# Failure Recipe: Webshop Guest Party Cleanup Regression

## Symptom

Public local pages suddenly look broadly broken. The browser console reports a
failed Webshop POST, for example:

```text
Failed to load resource: the server responded with a status of 400 (BAD REQUEST)
website.js:83 POST http://localhost:8081/ 400 (BAD REQUEST)
```

Product pages and category/listing pages may show 400/500 method failures while
trying to calculate prices or variants for anonymous visitors.

## Trigger conditions

- A local cleanup deletes all `Customer` and `Contact` records because "all
  local data is fake."
- A report treats `Customer:Guest` or `Contact:Guest-Guest` as ordinary fake
  client data.
- A broad SQL/script cleanup deletes child rows such as `Portal User` or
  `Dynamic Link` without recognizing them as anonymous Webshop plumbing.
- An agent verifies only CRM/sales/payment counts and does not load public
  product pages afterward.

## Known instances

| Date | Project | Surface | Action being taken | Bad outcome | Evidence | Guard state | Status |
|---|---|---|---|---|---|---|---|
| 2026-05-21 | Locally Twisted | Local ERPNext/Webshop at `http://localhost:8081` | Deleting fake/demo/smoke operational data from the local database | `Customer:Guest` and `Contact:Guest-Guest` were removed; Webshop guest pricing and variant calls crashed; local pages reported `POST /` 400/500 failures | Webshop traceback through `variant_selector.utils.get_next_attribute_and_values` -> `_set_price_list` -> `get_party().get("name")`; restored Guest Customer/Contact/Dynamic Link/Portal User; `npm run test:public-network -- --workers=1` passed afterward | added | recovered-local/guarded |

## Root pattern

The cleanup classified all `Customer` and `Contact` records as business data.
ERPNext/Webshop actually uses one `Customer`/`Contact`/`Portal User` chain as
anonymous platform infrastructure.

That is the trap: the record names look fake, but the framework uses them to
answer real public ecommerce questions.

## Why it seemed reasonable at the time

The local database is not live customer truth, and the user explicitly wanted
fake data cleared before ecommerce launch. A zero-customer local database sounds
clean. In ERPNext/Webshop, though, a zero-customer database can be less clean
than it looks because the anonymous shopper still needs a party context.

## Detection signals

- Cleanup scripts or docs say `Customer = 0` without an exception for Guest
  infrastructure.
- `rg -n "delete.*Customer|truncate.*Customer|Customer.*Guest|Portal User|Dynamic Link" scripts apps workstreams`
  finds broad cleanup logic.
- Webshop stack traces mention `_set_price_list`, `get_party()`, `get_product_info_for_website`,
  or `get_next_attribute_and_values`.
- Browser console shows `website.js` POST failures on public pages.
- `python scripts/verify/webshop_guest_party_contract.py` fails.
- `npm run test:public-network -- --workers=1` sees same-origin 400/500s.

## Required guard

Every local fake-data cleanup that touches customer/contact/user-like data must
run:

```powershell
python scripts/verify/webshop_guest_party_contract.py
npm run test:public-network -- --workers=1
```

The cleanup report must say one of these exact things:

- "Guest Webshop infrastructure preserved."
- "Guest Webshop infrastructure restored after cleanup."
- "Guest Webshop infrastructure intentionally absent because Webshop is fully
  disabled and product routes were verified under that disabled state."

The third option needs direct route proof and should not be used for LT while
public ecommerce is being built.

Runtime protection now also exists in the custom app:

- `locally_twisted.webshop_guest_party_guard` blocks normal Frappe saves,
  deletes, and child-row mutations that would break the Guest party contract.
- `hooks.py` wires the guard through Frappe `doc_events`.
- The verifier includes rollback-safe destructive probes and must show every
  `runtime_guard_probes` attempt as blocked.

This is architectural protection for normal ERPNext/Frappe code paths. Direct
SQL and external database tooling can still bypass document hooks, so broad
cleanup scripts remain responsible for backups plus before/after verifier runs.

## Recovery recipe

1. Confirm whether the broken environment is local, staging, or live.
2. Restore `Customer:Guest`, `Portal User:Guest -> Customer Guest`,
   `Contact:Guest-Guest`, and `Dynamic Link:Guest-Guest -> Customer Guest`.
3. Confirm `User:Guest` is an enabled `Website User` and has no extra roles.
4. Confirm `Webshop Settings` still match the intended public-shopping state:
   enabled, show price, no login required to view products, no hide price for
   guest, `Standard Selling`, `Individual`.
5. Clear the Frappe website cache.
6. Run the Guest party verifier.
7. Run the public network verifier.
8. Update the cleanup workstream and coordination board so "zero data" does not
   mean "zero Guest infrastructure."

## What not to do

- Do not delete `Guest` infrastructure to make customer/contact counts prettier.
- Do not treat `Guest` as a real lead, client, or marketing-review account.
- Do not add Desk/system roles to `Guest`.
- Do not attach real customer emails, orders, invoices, or payment records to
  the Guest customer.
- Do not use LT's guest-safe product-info override as permission to delete the
  underlying party chain.
- Do not claim staging/live risk from this local incident without checking that
  environment directly.

## Cross-links

- Related capability: `capabilities/recipes/erpnext-webshop-guest-party-contract.md`
- Related recipe: `capabilities/recipes/frappe-public-storefront-security.md`
- Related workstream: `workstreams/user-access-audit-2026-05-15.md`
- Related workstream: `workstreams/erpnext-backend-simplification.md`
- Related verifier: `scripts/verify/webshop_guest_party_contract.py`
- Related verifier: `scripts/verify/public_network_integrity.spec.js`

## Evidence quality

Verified locally on 2026-05-21 against the running ERPNext/Frappe site and
installed Webshop source. Official ERPNext/Frappe docs confirm the general
guest/Webshop settings model; the exact Guest party chain and blast radius are
local LT runtime facts. Staging/live are unverified by this failure recipe.
