# Provider Witness Artifact

Role: read-only provider-state witness.

## Findings

- Staging target: `locallytwisted-staging.frappe.cloud`.
- Site status: `Active`.
- Team: `5b8acl3gba`.
- Bench group: `bench-40102`.
- App order: `frappe`, `erpnext`, `payments`, `webshop`,
  `locally_twisted`.
- Installed app hash: `181076c239b2d1d3d508a41ac471c71f9d2b5158`.
- Target app hash from mirror: `181076c239b2d1d3d508a41ac471c71f9d2b5158`.
- Rollback hash: `181076c239b2d1d3d508a41ac471c71f9d2b5158`.
- Running jobs: none reported.
- Site config: `lt_ecommerce_paused=1`,
  `lt_public_indexing_enabled=0`.
- Latest deploy summary: deploy `52caqn2v57`, status `Success`, creation
  `2026-05-23 08:40:05.823593`, `update_available=true`.

## No-Go Evidence

- App mirror freshness is `ok=false` against source
  `a5ed6804392f9c576a321e81b8fa0a477c200828`.
- The app-root mirror is missing
  `locally_twisted/staging_owner_review_preflight.py`.
- The app-root mirror copy of
  `locally_twisted/staging_owner_review_bootstrap.py` differs from source.
- Hosted preflight returns HTTP `417` because the deployed app lacks
  `preflight_staging_owner_review_bootstrap`.

## Boundary

This witness used read-only artifact producers. It did not push the app mirror,
deploy, update the site, run migrations, clear cache, bootstrap data, create
users, unpause ecommerce, enable indexing, touch live/DNS/Stripe/Search
Console, or read/archive secrets.
