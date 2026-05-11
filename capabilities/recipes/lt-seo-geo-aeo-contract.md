---
id: lt-seo-geo-aeo-contract
name: LT SEO GEO AEO Contract
schema_version: 2.1
profile: foundation
level: recipe
maturity: candidate
scope: Locally Twisted public technical discovery surfaces
currently_true: unknown
last_verified: 2026-05-11
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
6. Run the verifier:

```powershell
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

## Rollback / revalidation path

If the SEO contract fails after copy or route changes, fix the visible page and
structured data in the same slice. Do not disable the verifier to ship stale
metadata.
