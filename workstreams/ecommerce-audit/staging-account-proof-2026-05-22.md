# Staging Account And Product Visibility Proof - 2026-05-22

Role: Worker A in the required LT release triad.

Date boundary: 2026-05-22 America/Denver / 2026-05-23 UTC.

Scope: staging/account/product visibility proof only. No source code, live, DNS, Stripe, Search Console, Cloudflare, or production mutation.

## Decision

**BLOCKED for owner ecommerce review.**

The Frappe Cloud staging site is active and running the latest `locally_twisted` app mirror hash, but the staging database is not populated for owner review:

- `Item` count is `0`.
- `Website Item` count is `0`.
- `Website Slideshow` count is `0`.
- `Website Slideshow Item` count is `0`.
- `locallytwisted@gmail.com` does not exist as a staging `User`.
- `marketing@exploringnotboring.com` does not exist as a staging `User`.
- Authenticated `/shop-items` renders the shop shell, but representative product/category routes return `404` because product/catalog records are missing.

This is not a code-deploy failure anymore. It is now a staging site data/provisioning gap.

## Commands Run

All commands were run from:

`C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\locally-twisted`

No secrets, API keys, API secrets, cookies, or session IDs were printed.

```powershell
git rev-parse --abbrev-ref HEAD
git status --short --branch
```

Result: branch `main`; clean against `origin/main`.

Final containment check later showed concurrent dirty files outside this Worker A scope. Worker A did not edit or revert those files; this pass changed only the three documentation files listed in this proof packet.

```powershell
Get-Content C:\Users\baenb\agent-coordination\STARTUP-CHECKLIST.md -TotalCount 160
Get-Content C:\Users\baenb\agent-coordination\LIVE-BOARD.md -TotalCount 220
Get-Content C:\Users\baenb\agent-coordination\SESSION-REGISTRY.md -TotalCount 220
```

Result: shared LT release lane confirmed. Worker A did not edit coordination files because this pass was constrained to the audit/research docs.

```powershell
Invoke-RestMethod https://cloud.frappe.io/api/method/press.api.site.get
Invoke-RestMethod https://cloud.frappe.io/api/method/press.api.site.installed_apps
Invoke-RestMethod https://cloud.frappe.io/api/method/press.api.site.site_config
Invoke-RestMethod https://cloud.frappe.io/api/method/press.api.site.running_jobs
Invoke-RestMethod https://cloud.frappe.io/api/method/press.api.bench.jobs
```

Result: Frappe Cloud staging provider proof below.

```powershell
Invoke-RestMethod https://locallytwisted-staging.frappe.cloud/api/method/frappe.ping
```

Result: `pong`.

```powershell
# Auth bootstrap via Frappe Cloud site.login, then staging /app?sid=...
# Session ID was used in memory only and not printed.
Invoke-WebRequest https://locallytwisted-staging.frappe.cloud/app?sid=[redacted]
Invoke-RestMethod https://locallytwisted-staging.frappe.cloud/api/method/frappe.auth.get_logged_user
Invoke-RestMethod https://locallytwisted-staging.frappe.cloud/api/method/frappe.client.get
Invoke-RestMethod https://locallytwisted-staging.frappe.cloud/api/method/frappe.client.get_count
```

Result: authenticated as `Administrator`; user and record proofs below.

```powershell
Invoke-WebRequest https://locallytwisted-staging.frappe.cloud/
Invoke-WebRequest https://locallytwisted-staging.frappe.cloud/shop-items
Invoke-WebRequest https://locallytwisted-staging.frappe.cloud/shop-items/bouquets/mickey-mouse-bouquet
Invoke-WebRequest https://locallytwisted-staging.frappe.cloud/shop-items/columns
Invoke-WebRequest https://locallytwisted-staging.frappe.cloud/app
Invoke-WebRequest https://locallytwisted-staging.frappe.cloud/robots.txt
Invoke-WebRequest https://locallytwisted-staging.frappe.cloud/sitemap.xml
Invoke-WebRequest https://locallytwisted-staging.frappe.cloud/ready-to-order-paused?from=%2Fshop-items
```

Result: route proofs below.

## Provider Proof

Checked at `2026-05-23T00:17:49Z` through Frappe Cloud API:

| Field | Result |
|---|---|
| Staging site | `locallytwisted-staging.frappe.cloud` |
| Site status | `Active` |
| Bench group | `bench-40102` |
| Server | `f4-virginia.frappe.cloud` |
| Installed app order | `frappe, erpnext, payments, webshop, locally_twisted` |
| `locally_twisted` hash | `3e86bc149d6dcc04daa194b740c1733f5c796261` |
| `lt_ecommerce_paused` | `1` |
| `lt_public_indexing_enabled` | `0` |

Checked at `2026-05-23T00:23:39Z`:

| Field | Result |
|---|---|
| Running jobs | `0` |

Latest relevant bench jobs sampled at `2026-05-23T00:18:52Z`:

| Job | Type | Status |
|---|---|---|
| `eu27r8q4to` | Clear Cache | Success |
| `3u20303jfl` | Update Site Configuration | Success |
| `crn5pskff4` | Update Site Migrate | Success |

## Account Proof

Authenticated staging session was bootstrapped through Frappe Cloud `press.api.site.login`, then `/app?sid=[redacted]`. The staging session reported `Administrator`.

Checked at `2026-05-23T00:22:50Z`:

| Account | Result |
|---|---|
| `locallytwisted@gmail.com` | `404 Not Found` from `frappe.client.get`; user missing |
| `marketing@exploringnotboring.com` | `404 Not Found` from `frappe.client.get`; user missing |

This means the required owner/backend and external marketing review accounts are not present on staging at this proof point.

## Data Proof

Checked at `2026-05-23T00:22:50Z` through authenticated staging `frappe.client.get_count`:

| Doctype | Count |
|---|---:|
| `Item` | 0 |
| `Website Item` | 0 |
| `Website Slideshow` | 0 |
| `Website Slideshow Item` | 0 |

This is the direct reason product detail pages and category pages cannot prove owner ecommerce review readiness yet.

## Route Proof

Checked at `2026-05-23T00:22:50Z`:

| Route | Auth | Status | Evidence |
|---|---|---:|---|
| `/` | Guest | 200 | Homepage title renders; `noindex` present |
| `/shop-items` | Guest | 302 | Redirects to `/ready-to-order-paused?from=%2Fshop-items` |
| `/shop-items/bouquets/mickey-mouse-bouquet` | Guest | 302 | Redirects to paused page |
| `/shop-items` | Administrator | 200 | Shop shell title `Ready-to-Order Balloon Decor` renders |
| `/shop-items/bouquets/mickey-mouse-bouquet` | Administrator | 404 | Product record/route missing |
| `/shop-items/columns` | Administrator | 404 | Category/product-group record/route missing |
| `/app` | Administrator | 200 | Desk shell title `Locally Twisted` renders |

Checked at `2026-05-23T00:23:21Z`:

| Route | Status | Evidence |
|---|---:|---|
| `/api/method/frappe.ping` | 200 | `pong` |
| `/robots.txt` | 200 | Allows crawl and points to staging sitemap |
| `/sitemap.xml` | 200 | Lists staging routes |
| `/ready-to-order-paused?from=%2Fshop-items` | 200 | Contains `noindex` |

Indexing note: site config has `lt_public_indexing_enabled=0` and checked pages contain `noindex`, but `robots.txt` still allows crawling and `sitemap.xml` still publishes staging URLs. Treat this as a separate SEO/indexing gate item before any search-engine work.

## Blockers

1. Staging has app code but no ecommerce/catalog data.
2. Staging has app code but missing required human users.
3. Authenticated product/category page proof is impossible until records exist.
4. Gallery proof is impossible on staging until Website Item and Website Slideshow records exist.
5. Search/indexing readiness is not approved by this pass because robots/sitemap behavior still needs the SEO gate.

## Next Required Work For The Release Triad

1. Run the staging-safe seed/provisioning path that creates required users, roles, catalog Items, Website Items, Product Setup records, Website Slideshows, and Website Slideshow Items on `locallytwisted-staging.frappe.cloud`.
2. Re-run authenticated account proof for `locallytwisted@gmail.com` and `marketing@exploringnotboring.com`.
3. Re-run staging product route proof for Classic Arch, Mickey Mouse Bouquet, Columns, Arches, and representative product types.
4. Re-run gallery proof after data exists.
5. Re-run indexing proof and decide whether `robots.txt`/`sitemap.xml` behavior is acceptable for staging or must be tightened.
