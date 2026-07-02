---
name: Frappe Cloud sitemap public-domain drift
type: failure
failure_kind: regression_pattern
schema_version: 0.1
date_discovered: 2026-05-19
last_updated: 2026-05-19
status: open
scope: project
owner_context: Locally Twisted
related_capabilities:
  - capabilities/recipes/lt-seo-geo-aeo-contract.md
  - capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md
related_failures:
  - capabilities/failures/frappe-cloud-release-site-migration-drift.md
  - capabilities/failures/public-nav-seo-verifier-drift.md
tags:
  - Locally Twisted
  - Frappe Cloud
  - sitemap
  - canonical
  - Google Search Console
  - reindex
---

# Failure Recipe: Frappe Cloud Sitemap Public-Domain Drift

## Symptom

The public site serves correctly at `https://locallytwisted.com`, but sitemap,
canonical, Open Graph, or structured-data URLs point at the Frappe Cloud vanity
host `https://locallytwisted.v.frappe.cloud`.

## Trigger Conditions

- Frappe Cloud site config or `frappe.utils.get_url()` returns the vanity host.
- SEO helpers call `get_url()` before checking the request host.
- Sitemap generation calls `get_url()` directly instead of the same canonical
  URL helper used by page metadata.
- A launch verifier proves route health but does not inspect discovery URLs.

## Known Instances

| Date | Project | Surface | Action being taken | Bad outcome | Evidence | Guard state | Status |
|---|---|---|---|---|---|---|---|
| 2026-05-19 | Locally Twisted | `sitemap.xml`, `/about` canonical and `og:url` | Cloudflare/Frappe Cloud provider cleanup and reindex audit | Live public domain was healthy, but all 29 sitemap URLs and about-page discovery URLs advertised `locallytwisted.v.frappe.cloud` | `Invoke-WebRequest https://locallytwisted.com/sitemap.xml`; `Invoke-WebRequest https://locallytwisted.com/about` | source guard added, not live until Frappe Cloud release | open |

## Root Pattern

Route health and search discovery health were treated as the same proof. The
site could return `200` from Frappe Cloud through Cloudflare while still
telling search engines that the canonical site was the Frappe Cloud vanity
subdomain.

## Why It Seemed Reasonable At The Time

`frappe.utils.get_url()` is the usual Frappe helper for absolute URLs, and the
Cloudflare launch gate already proved the public host reached Frappe Cloud.
That made it easy to miss that Frappe's configured host and the browser's
public request host can differ after a custom-domain cutover.

## Detection Signals

- Live sitemap contains `locallytwisted.v.frappe.cloud`.
- Live canonical or `og:url` contains `locallytwisted.v.frappe.cloud`.
- `site:locallytwisted.com` still shows old WordPress/WooCommerce results after
  cutover.
- Search Console sitemap processing points to a vanity or staging host.
- SEO tests pass locally but were never run against `https://locallytwisted.com`.

## Required Guard

The SEO contract must fail if any sitemap `<loc>` host differs from the tested
public host or if the Frappe Cloud vanity host appears in sitemap output.

Before a reindex request, run:

```bash
export LT_BASE_URL='https://locallytwisted.com'
npm run test:seo-contract
```

## Recovery Recipe

1. Fix SEO URL helpers so page metadata prefers the public request host.
2. Make sitemap generation use the same absolute URL helper.
3. Add a verifier assertion that rejects the Frappe Cloud vanity host.
4. Deploy through the normal app-mirror and Frappe Cloud site update path.
5. Clear website cache.
6. Rerun the SEO contract against `https://locallytwisted.com`.
7. Submit the corrected sitemap in Google Search Console only after live
   sitemap and canonicals are public-domain clean.

## What Not To Do

- Do not submit the sitemap while it advertises the vanity host.
- Do not use Search Console removals before deciding which old URLs should
  redirect versus stay 404.
- Do not treat `Server: Frappe Cloud` as SEO discovery proof.
- Do not point Google Ads final URLs at routes that are still 404 or paused
  without a deliberate campaign decision.

## Cross-Links

- Related capability: `capabilities/recipes/lt-seo-geo-aeo-contract.md`
- Related capability: `capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`
- Related workstream: `workstreams/domain-provider-reindex-cleanup-2026-05-19.md`
- Related workstream: `workstreams/seo-geo-aeo-contract.md`
- Related workstream: `workstreams/frappe-cloud-cutover.md`

## Evidence Quality

Verified live on 2026-05-19 by public DNS, Cloudflare API zone/DNS read,
public HTTP headers, live sitemap parse, and live page metadata inspection.
Source guard is added locally/source-side, but the live site remains wrong
until a Frappe Cloud release updates the app and clears cache.
