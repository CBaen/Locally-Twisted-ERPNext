# Domain, Provider, And Reindex Cleanup - 2026-05-19

## Scope

This handoff records the current Locally Twisted public web chain after the
Cloudflare/Frappe Cloud move, the old-provider cleanup targets, and the
Google reindexing blockers that must be fixed before asking Google to crawl
again.

This is connected to ad takeover work, but it is not the Google Ads/Meta
dashboard lane. Ad account control lives in
`workstreams/ad-account-takeover-2026-05-19.md`.

No provider cancellation, DNS mutation, Frappe Cloud deploy, Search Console
submission, Google Ads change, Meta change, billing change, or live checkout
change was performed in this slice.

## Verified Public Chain

Current live path:

```text
GoDaddy registrar
  -> Cloudflare authoritative nameservers and DNS
  -> Frappe Cloud public web target
  -> ERPNext/Frappe Locally Twisted site
```

Verified on 2026-05-19:

| Surface | Current state |
|---|---|
| Cloudflare zone | `locallytwisted.com`, active, full setup, not paused |
| Cloudflare nameservers | `edward.ns.cloudflare.com`, `laura.ns.cloudflare.com` |
| Cloudflare original registrar | `godaddy.com, llc (id: 146)` |
| Cloudflare original nameservers | `ns1.bluehost.com`, `ns2.bluehost.com` |
| Apex web record | `locallytwisted.com A 34.226.39.121`, DNS-only |
| `www` web record | `www.locallytwisted.com CNAME locallytwisted.v.frappe.cloud`, DNS-only |
| Public apex HTTP | `https://locallytwisted.com/` returns `200`, `Server: Frappe Cloud`, `X-Page-Name: home` |
| Public ping | `https://locallytwisted.com/api/method/frappe.ping` returns `{"message":"pong"}` |
| Email DNS | Cloudflare Email Routing MX records and SPF are active |
| Google verification | TXT `google-site-verification=uGj_dRyc_8pH_grRnmef1w4ZpNA5ZrLQC1NS4jfw64k` exists |

This confirms the site has moved to Cloudflare DNS and Frappe Cloud hosting for
the customer-facing domain. It does not prove Frappe Cloud dashboard ownership,
Search Console ownership inside the UI, Google Ads control, or Meta Business
control.

## Hetzner / Odoo Status

`http://5.78.136.133/` is the old Odoo/Hetzner reference deployment. It is not
the current public `locallytwisted.com` web path.

Keep it read-only until the old-platform archive/decommission decision is
complete. Do not modify the old Odoo source or server from this ERPNext repo.

Cleanup target:

1. Confirm any remaining Hetzner server, snapshot, DNS, or billing surface.
2. Archive the old Odoo repo/source state if not already done.
3. Confirm no live DNS, ads, Search Console, Meta, or customer workflows still
   point to `5.78.136.133`.
4. Only then shut down/decommission with owner approval.

## Legacy Provider Inventory

| Provider | Evidence | Cleanup posture |
|---|---|---|
| GoDaddy | Cloudflare zone reports original registrar `godaddy.com`; Gmail renewal email for `LOCALLYTWISTED.COM` with billing date `2026-05-20` | Keep the domain registration renewed unless/until owner explicitly transfers registrar. Review/cancel only unnecessary add-ons after dashboard proof. |
| Bluehost | Cloudflare reports original nameservers `ns1.bluehost.com` / `ns2.bluehost.com`; Bluehost emails show customer ID `75612299` and shared-hosting dashboard language | Likely old hosting/DNS account. Inventory subscriptions, WordPress install, SSL, email, backups, and billing before canceling. |
| WordPress / WooCommerce | Google still shows old WordPress/WooCommerce-style indexed URLs; WooCommerce email evidence exists | Determine whether this was Bluehost-hosted WordPress/WooCommerce, WordPress.com, WooCommerce.com, or ENB-managed plugin/account state before canceling anything. |
| Wix | Search/mail evidence is weak and not current-proof | Treat as unverified until a dashboard, invoice, DNS record, or account email proves an active LT Wix property. |
| Frappe Cloud | Public serving verified; direct dashboard/API control from Codex is separate | Current production host. Do not cancel or change. |
| Cloudflare | Zone and DNS verified through Cloudflare API and public DNS | Current authoritative DNS and email-routing surface. Do not disable. |

## Reindex State

Google still has stale old-site results for `locallytwisted.com`, including old
WordPress/WooCommerce paths such as `/product/standard-balloon-arch/`.

Current live old-path behavior:

| Old path | Current result |
|---|---|
| `/product/standard-balloon-arch/` | 301 slash normalization, then Frappe Cloud 404 |
| `/contact-us/` | 301 slash normalization, then Frappe Cloud 404 |
| `/event-installations/` | 301 slash normalization, then Frappe Cloud 404 |
| `/about-us/` | Redirects/canonicalizes to live `/about` |
| `/shop/` | Redirects to `/ready-to-order-paused?from=%2Fshop` while ecommerce is paused |

Live discovery blocker found on 2026-05-19:

- `https://locallytwisted.com/sitemap.xml` returns 29 URLs.
- All 29 sitemap `<loc>` values currently point at
  `https://locallytwisted.v.frappe.cloud/...`.
- Zero sitemap `<loc>` values point at `https://locallytwisted.com/...`.
- `https://locallytwisted.com/about` currently emits canonical and `og:url`
  values on `https://locallytwisted.v.frappe.cloud/about`.

That must be fixed before Search Console reindex work. Asking Google to recrawl
while the sitemap and canonical tags advertise the Frappe Cloud vanity host
would reinforce the wrong discovery target.

## Source Fix Started

Source patch in this slice:

- `apps/locally_twisted/locally_twisted/seo.py` now prefers the current request
  host before Frappe's configured `get_url()` when building canonical, Open
  Graph, and structured-data URLs.
- `apps/locally_twisted/locally_twisted/www/sitemap.py` now uses the same SEO
  absolute-URL helper instead of calling `frappe.utils.get_url()` directly.
- `scripts/verify/seo_contract.spec.js` now fails if sitemap URLs advertise
  `locallytwisted.v.frappe.cloud` or any host other than the tested public host.

This source fix is not live until the app mirror is synced, Frappe Cloud deploy
and site update/migration succeed, cache is cleared, and the live SEO contract
is rerun.

Local verification after the source patch:

- `python -m py_compile apps\locally_twisted\locally_twisted\seo.py apps\locally_twisted\locally_twisted\www\sitemap.py`
- `npm run test:seo-contract` passed 11/11 against `http://localhost:8081`.
- `python scripts/verify/cloudflare_launch_readiness.py --base-url https://locallytwisted.com` passed 10/10 against current live, proving route health only.

2026-05-21 local follow-up:

- `apps/locally_twisted/locally_twisted/www/robots.py` and `.txt` now make
  `/robots.txt` advertise the current-host sitemap instead of returning blank
  content.
- The local SEO helper preserves `http://localhost:8081` when the Frappe nginx
  request host drops the port, while still preferring the real request host for
  production.
- `npm run test:seo-contract` now includes the robots check and passed 12/12
  against `http://localhost:8081`.

2026-05-21 selective indexing follow-up:

- Decision: index stable approved public business pages first; do not index
  Ready-to-Order shop, product category, product detail, cart, checkout, or
  pause-doorway pages while ecommerce is paused or owner product approval is
  still in progress.
- Source guard: `seo.py` now emits page-level robots metadata through
  `robots_meta_for_path()`. Stable public pages emit `index, follow`; ecommerce
  discovery paths emit `noindex, follow` when `lt_ecommerce_paused=1`; the
  pause doorway is always `noindex, follow`.
- Staging guard: `lt_public_indexing_enabled=0` makes every route emit
  `noindex, follow` for private staging/owner-review environments without
  needing to block crawlers in `robots.txt`.
- Sitemap guard: `www/sitemap.py` excludes ecommerce discovery paths while
  `lt_ecommerce_paused=1`. When ecommerce is reopened, those URLs may re-enter
  the sitemap and must pass product-page review before Search Console
  submission.
- Extra blocked discovery path added: `/products`, because it is an upstream
  ecommerce/product discovery surface and should not be public during the pause.
- Local proof: source compiled, `npm run test:seo-contract` passed 13/13 in the
  current local open-ecommerce mode, `/ready-to-order-paused` rendered
  `<meta name="robots" content="noindex, follow">`, and a helper proof verified
  paused `/shop`, `/shop-items/...`, and product detail paths noindex while
  `/contact` remains indexable.

## Reindex Order

1. Prove the local source fix with `npm run test:seo-contract`.
2. Sync the app-root mirror and release through the normal Frappe Cloud gate.
3. Clear Frappe Cloud website cache.
4. Recheck live:

```powershell
python scripts/verify/cloudflare_launch_readiness.py --base-url https://locallytwisted.com
$env:LT_BASE_URL='https://locallytwisted.com'; npm run test:seo-contract
```

5. Confirm `https://locallytwisted.com/sitemap.xml` contains only
   `https://locallytwisted.com/...` URLs.
6. Confirm public canonical and `og:url` values use `https://locallytwisted.com`.
7. Confirm stable business pages are indexable and ecommerce discovery pages
   are absent/noindex while `lt_ecommerce_paused=1`.
8. Add targeted 301 redirects for high-value old WordPress/WooCommerce URLs
   before using removals for pages that should be preserved as traffic.
9. In Google Search Console, submit `https://locallytwisted.com/sitemap.xml`
   and use URL Inspection for priority pages.
10. Use Search Console Removals only for pages that should disappear quickly,
   and only after the site itself is returning the intended redirect, 404, or
   noindex behavior.

Google Search Central notes that URL Inspection is for a few URLs, sitemap
submission is the right path for many URLs or a site move, recrawling can take
days to weeks, and submission does not guarantee immediate indexing.

## Required Redirect Decisions

Do not blanket-redirect old URLs to home. Map useful old traffic to the closest
current customer path or leave it as a real 404.

Initial decision queue:

| Old URL pattern | Proposed target | Decision state |
|---|---|---|
| `/contact-us/` | `/contact` | safe likely redirect |
| `/product/standard-balloon-arch/` | current arch/product/category route | needs product-route match |
| `/event-installations/` | `/portfolio` or an approved event audience page | needs owner/content decision |
| old `/shop/*` WordPress/WooCommerce URLs | matching `/shop-items/...` route where one exists | needs crawl/export map |

## Dashboard Access Still Needed

- Google Search Console: needed to submit sitemap, inspect priority URLs, view
  indexing errors, and manage removals.
- Google Ads: needed for actual account takeover and 404 destination repair;
  see `workstreams/ad-account-takeover-2026-05-19.md`.
- Meta Business: needed for Facebook/Instagram account takeover; see the ad
  handoff.
- GoDaddy: needed to confirm registrar renewal, privacy/protection add-ons,
  domain lock, and transfer posture.
- Bluehost: needed to inventory and cancel old hosting/WordPress/SSL/email only
  after confirming no dependency remains.
- Frappe Cloud: needed for the source release/site update/cache clear.

## Verification Commands Used

```powershell
Resolve-DnsName locallytwisted.com NS
Resolve-DnsName locallytwisted.com A
Resolve-DnsName www.locallytwisted.com CNAME
Invoke-WebRequest -Uri https://locallytwisted.com/ -UseBasicParsing
Invoke-WebRequest -Uri https://locallytwisted.com/api/method/frappe.ping -UseBasicParsing
python scripts/verify/cloudflare_launch_readiness.py --base-url https://locallytwisted.com
python scripts/verify/frappe_cloud_preflight.py
```

Cloudflare API was used read-only to list the `locallytwisted.com` zone and DNS
records.

## Cross-Links

- Frappe Cloud cutover: `workstreams/frappe-cloud-cutover.md`
- Launch gate: `workstreams/frappe-cloud-cloudflare-stripe-launch-2026-05-11.md`
- SEO handoff: `workstreams/seo-geo-aeo-contract.md`
- Ad account takeover: `workstreams/ad-account-takeover-2026-05-19.md`
- SEO capability: `capabilities/recipes/lt-seo-geo-aeo-contract.md`
- Launch capability: `capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`
- Failure recipe:
  `capabilities/failures/frappe-cloud-sitemap-public-domain-drift.md`

## External Source Docs Checked

- Google Search Central, Ask Google to recrawl:
  https://developers.google.com/search/docs/crawling-indexing/ask-google-to-recrawl
- Google Search Central, Build and submit a sitemap:
  https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap
- Google Search Console Help, Removals tool:
  https://support.google.com/webmasters/answer/9689846
