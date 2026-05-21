---
id: lt-seo-geo-aeo-contract
name: LT SEO GEO AEO Contract
schema_version: 2.1
profile: foundation
level: recipe
maturity: candidate
scope: Locally Twisted public technical discovery surfaces
currently_true: false
last_verified: 2026-05-19
evidence_quality: direct
verification_level: 1
tags:
  - Locally Twisted
  - SEO
  - GEO
  - AEO
  - FAQPage
  - sitemap
  - structured data
---

## What it does

Keeps Locally Twisted's launch discovery surfaces aligned across visible copy,
canonical routes, sitemap entries, metadata, and structured data.

## When to reach for it

Use this before editing `/about`, `/faq`, `/sitemap.xml`, route aliases,
canonical tags, Open Graph/Twitter metadata, JSON-LD, service-page SEO copy,
content-image alt text, or removed-route behavior.

## How to use it

1. Read `workstreams/seo-geo-aeo-contract.md`.
2. Update page content and structured data together.
3. Keep FAQ visible questions and FAQPage JSON-LD in parity.
4. Avoid unverified rating, review-count, or hours claims.
5. Keep rejected prelaunch routes out of sitemap/canonical maps unless GL
   explicitly approves a redirect.
6. For production, sitemap, canonical, Open Graph URL, and structured-data URLs
   must use `https://locallytwisted.com`, not the Frappe Cloud vanity host.
7. While `lt_ecommerce_paused=1`, keep Ready-to-Order shop, product category,
   product detail, cart, checkout, `/products`, and pause-doorway URLs out of
   public indexing. Stable public business pages may be indexable after review.
8. For staging or owner-review environments, set `lt_public_indexing_enabled=0`
   so every route emits `noindex, follow`.
9. Run the verifier:

```powershell
npm run test:seo-contract
```

After a Frappe Cloud release and before Search Console reindex work, run the
same contract against production:

```powershell
$env:LT_BASE_URL='https://locallytwisted.com'
npm run test:seo-contract
```

## What it depends on

- `apps/locally_twisted/locally_twisted/seo.py`
- Route controllers under `apps/locally_twisted/locally_twisted/www/`
- `scripts/verify/seo_contract.spec.js`

## Current removed routes

- `/event-balloons`
- `/event_balloons`

These return 404 without redirect and are excluded from sitemap/canonical
coverage. The four event audience pages remain crawlable.

## Current Watch

On 2026-05-19, the live public site served from Frappe Cloud through Cloudflare,
but the live sitemap and about-page discovery metadata advertised
`https://locallytwisted.v.frappe.cloud`. Source was patched and the verifier was
strengthened, but `currently_true` remains false until the fix is deployed to
Frappe Cloud, cache is cleared, and the production SEO contract passes.

On 2026-05-21, selective indexing source guards were added: paused ecommerce
discovery paths are noindex and excluded from sitemap, the pause doorway is
always noindex, and `lt_public_indexing_enabled=0` can noindex staging/owner
review environments globally. This is local source proof only until released
through the Frappe Cloud gate.

## Rollback / revalidation path

If the SEO contract fails after copy or route changes, fix the visible page and
structured data in the same slice. Do not disable the verifier to ship stale
metadata.
