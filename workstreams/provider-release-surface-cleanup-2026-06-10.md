# Provider Release Surface Cleanup - 2026-06-10

## Status

Inventory complete. Provider deletion is blocked until the exact target name is
confirmed.

## User Direction

GL verified that `https://locallytwisted.com` is correct and approved deletion
of the Frappe bench that is no longer needed for staging cleanup.

## Current Provider Inventory

Read-only Frappe Cloud API inventory on 2026-06-10:

| Site | Host Name | Status | Bench | Group | Title |
|---|---|---|---|---|---|
| `locallytwisted-staging.frappe.cloud` | `locallytwisted.com` | Active | `bench-40102-000031-f4-virginia` | `bench-40102` | `LT Staging - Inquiry Filter` |
| `locallytwisted.v.frappe.cloud` | `locallytwisted.v.frappe.cloud` | Active | `bench-39776-000016-f94-virginia` | `bench-39776` | `Version 15 (Localisation) - Cloned` |

Bench inventory:

| Bench Group | Title | Status | Sites | Apps |
|---|---|---|---:|---:|
| `bench-39776` | `Version 15 (Localisation) - Cloned` | Active | 1 | 5 |
| `bench-40102` | `LT Staging - Inquiry Filter` | Active | 1 | 5 |

## Live Proof

- `https://locallytwisted.com/api/method/frappe.ping` returned `200` with
  `{"message":"pong"}`.
- `https://www.locallytwisted.com/api/method/frappe.ping` redirected `308` to
  `https://locallytwisted.com/api/method/frappe.ping`.
- `https://locallytwisted-staging.frappe.cloud/api/method/frappe.ping`
  redirected `308` to `https://locallytwisted.com/api/method/frappe.ping`.
- `https://locallytwisted.com/thank-you?order=SAL-ORD-2026-00043` returned
  `200`, contained `SAL-ORD-2026-00043`, and contained `Payment Received`.
- `https://locallytwisted.com/sitemap.xml` returned `200` and used
  `https://locallytwisted.com`.

## Obsolete-Surface Evidence

- `https://locallytwisted.v.frappe.cloud/api/method/frappe.ping` still returns
  `200`, but it is not the public-domain site.
- `https://locallytwisted.v.frappe.cloud/thank-you?order=SAL-ORD-2026-00043`
  returned `200` and showed `Payment Received`, but did **not** contain
  `SAL-ORD-2026-00043`.
- `https://locallytwisted.v.frappe.cloud/sitemap.xml` returned `200` and used
  the vanity host, not `https://locallytwisted.com`.

## Safety Decision

Do not delete `bench-40102` or site
`locallytwisted-staging.frappe.cloud` by the word "staging." Current provider
metadata says that surface owns `host_name: locallytwisted.com`, and its
frappe-cloud URL redirects to the live domain.

Likely delete target:

- Site: `locallytwisted.v.frappe.cloud`
- Bench group: `bench-39776`
- Bench: `bench-39776-000016-f94-virginia`
- Title: `Version 15 (Localisation) - Cloned`

## Required Final Approval

Before deletion, GL must approve the exact target name:

`Delete site locallytwisted.v.frappe.cloud and bench group bench-39776. Do not delete bench-40102.`

## Source Protocol

Use `capabilities/recipes/provider-release-surface-cleanup.md` and
`capabilities/failures/stale-provider-surface-poison.md`.
