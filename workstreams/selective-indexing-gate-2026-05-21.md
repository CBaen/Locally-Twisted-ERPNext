# Selective Indexing Gate - 2026-05-21

## Scope

This handoff records the local source guard for indexing stable Locally Twisted
business pages while keeping ecommerce/product discovery out of search until
owner approval.

This is a local source and documentation slice only. It does not perform
Frappe Cloud release, app mirror sync, DNS mutation, Search Console submission,
Google Ads change, Meta change, Stripe change, product approval, staging
promotion, or live release.

## Decision

Indexing should be selective:

- Stable public business pages may be indexable after SEO/GEO/AEO review.
- Staging and owner-review environments must not be indexable.
- Ready-to-Order shop, product category, product detail, cart, checkout,
  upstream product discovery aliases, and the pause doorway must stay out of
  public indexing while ecommerce is paused or owner product approval is still
  pending.

This preserves public business discoverability without letting unfinished
products or paused checkout become search results.

## Source Changes

Primary files:

- `apps/locally_twisted/locally_twisted/ecommerce_pause.py`
- `apps/locally_twisted/locally_twisted/seo.py`
- `apps/locally_twisted/locally_twisted/www/sitemap.py`
- `apps/locally_twisted/locally_twisted/www/ready_to_order_paused.py`
- `apps/locally_twisted/locally_twisted/templates/generators/item_group.html`
- `scripts/verify/seo_contract.spec.js`

Behavior:

- `seo.robots_meta_for_path()` returns `index, follow` or `noindex, follow`.
- `seo.should_noindex_path()` noindexes ecommerce discovery paths when
  `lt_ecommerce_paused=1`.
- `/ready-to-order-paused` is always `noindex, follow`.
- `lt_public_indexing_enabled=0` globally noindexes the site for staging or
  private owner-review environments.
- `www/sitemap.py` excludes ecommerce discovery paths from `/sitemap.xml` while
  `lt_ecommerce_paused=1`.
- `/products` is treated as an ecommerce discovery path so upstream/product
  aliases cannot leak during the pause.
- `item_group.html` no longer hardcodes `index, follow`; it reads the shared
  SEO robots context.

## Current Local State

Local `frontend` was open for another ecommerce work lane when this gate was
verified:

- `python scripts/verify/ecommerce_expected_mode.py --expect open` passed.
- Because the shared local site was open, paused-mode path logic was verified
  through helper-level proof instead of flipping the shared site config.
- The helper proof showed paused `/shop`, `/shop-items/...`, and product detail
  paths noindex while `/contact` remains indexable.
- `/ready-to-order-paused` rendered `noindex, follow` even while ecommerce was
  locally open.

## Live State

Live is not updated.

Fresh read-only live probes on 2026-05-21 still showed:

- `https://locallytwisted.com/sitemap.xml` returns 29 URLs.
- Live sitemap still uses `https://locallytwisted.v.frappe.cloud`.
- Live sitemap still includes ecommerce discovery URLs.
- `https://locallytwisted.com/robots.txt` is blank.
- `https://locallytwisted.com/about` canonical and `og:url` still use the
  Frappe Cloud vanity host.
- `https://locallytwisted.com/shop` redirects to
  `/ready-to-order-paused?from=%2Fshop`.

Do not submit Search Console or request recrawl until the Frappe Cloud release
gate ships this source and the live SEO contract passes against
`https://locallytwisted.com`.

## Verification

Commands run:

```powershell
python -m py_compile apps\locally_twisted\locally_twisted\ecommerce_pause.py apps\locally_twisted\locally_twisted\seo.py apps\locally_twisted\locally_twisted\www\sitemap.py apps\locally_twisted\locally_twisted\www\ready_to_order_paused.py
node --check scripts\verify\seo_contract.spec.js
python scripts\dev\clear_website_cache.py --restart
npm.cmd run test:seo-contract
python scripts\verify\ecommerce_expected_mode.py --expect open
```

Focused helper proof:

```text
paused shop: /shop -> noindex, follow
paused category: /shop-items/arches -> noindex, follow
paused product: /shop-items/arches/classic-arch -> noindex, follow
paused service: /contact -> index, follow
open shop: /shop -> index, follow
pause doorway: /ready-to-order-paused -> noindex, follow
global off service: /contact -> noindex, follow
```

Result:

- Syntax proof passed.
- Local cache clear/restart completed.
- `npm.cmd run test:seo-contract` passed 13/13.
- No staging/live/provider/indexing mutation was performed.

## Release Gate

Before Search Console submission:

1. Keep staging/private owner-review target on `lt_public_indexing_enabled=0`.
2. Release the source through the normal Frappe Cloud gate only after local
   review approval.
3. Clear Frappe Cloud website cache.
4. Run:

```powershell
$env:LT_BASE_URL='https://locallytwisted.com'
npm run test:seo-contract
```

5. Confirm live sitemap, canonical, `og:url`, robots, and ecommerce noindex
   behavior.
6. Submit only the approved live sitemap in Search Console.

## Backlinks

- `workstreams/seo-geo-aeo-contract.md`
- `workstreams/domain-provider-reindex-cleanup-2026-05-19.md`
- `capabilities/recipes/lt-seo-geo-aeo-contract.md`
- `locally-twisted-decisions.md`
- `lessons-learned.md`
- `locally-twisted-queue.md`
