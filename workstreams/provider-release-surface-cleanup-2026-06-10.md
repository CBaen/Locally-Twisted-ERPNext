# Provider Release Surface Cleanup - 2026-06-10

## Status

Cleanup complete. `bench-39776` and `locallytwisted.v.frappe.cloud` are no
longer present in active Frappe Cloud site or bench-group listings.

## User Direction

GL verified that `https://locallytwisted.com` is correct and approved deletion
of the Frappe bench that is no longer needed for staging cleanup.

Exact approved instruction:

`Delete site locallytwisted.v.frappe.cloud and bench group bench-39776. Do not delete bench-40102.`

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

## Cleanup Execution

Completed on 2026-06-10:

- Archived/dropped site `locallytwisted.v.frappe.cloud` through Frappe Cloud.
- Confirmed the stale URL returns Frappe Cloud `404` for `/` and
  `/api/method/frappe.ping`.
- Confirmed active site inventory has zero records for
  `locallytwisted.v.frappe.cloud` or group `bench-39776`.
- Attempted release-group deletion for `bench-39776`; Frappe Cloud initially
  blocked it because stale app source `payments:develop` was incompatible with
  the Version 15 bench.
- Confirmed `bench-39776` had zero active sites before app cleanup.
- Removed the stale `payments` app reference from the empty obsolete release
  group only.
- Re-ran release-group deletion for `bench-39776`; API call succeeded.

## Final Proof

Read-only Frappe Cloud API proof after cleanup:

| Check | Result |
|---|---|
| Active target sites for `locallytwisted.v.frappe.cloud` / `bench-39776` | 0 |
| Active target bench groups named `bench-39776` | 0 |
| Protected bench group `bench-40102` | Active, 1 site, 5 apps |
| Protected live host | `locallytwisted.com` on `bench-40102` |

Route proof after cleanup:

- `https://locallytwisted.com/api/method/frappe.ping` returned `200`.
- `https://locallytwisted.com/thank-you?order=SAL-ORD-2026-00043` returned
  `200`, contained `SAL-ORD-2026-00043`, and contained `Payment Received`.
- `https://locallytwisted.v.frappe.cloud/api/method/frappe.ping` returned
  Frappe Cloud `404`.
- `https://locallytwisted.v.frappe.cloud/` returned Frappe Cloud `404`.

## Source Protocol

Use `capabilities/recipes/provider-release-surface-cleanup.md` and
`capabilities/failures/stale-provider-surface-poison.md`.
