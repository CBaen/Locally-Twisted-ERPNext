# SEO/GEO/AEO Contract

Last updated: 2026-05-21 by Codex after local robots discovery and
current-host canonical verification were tightened. Indexing submission is
parked until shop staging and owner product approval.

## Scope

This handoff owns the launch technical discovery gate for canonical public
routes, sitemap shape, social metadata, business/service structured data,
FAQPage AEO answers, and content-image alt text. It is not a content strategy
plan and does not certify search rankings.

This handoff does not authorize the external marketing company to index the
site. Per GL on 2026-05-21, no Search Console submission, sitemap submission,
recrawl request, external indexing work, or shop/product discovery push should
happen until the shop is on staging and the owner approves products to go live.

## Current Contract

- `/about` is source-owned and exposes canonical, Open Graph, Twitter card, and
  LocalBusiness/Organization JSON-LD without unverified ratings or hours.
- Legacy route aliases declare canonical public routes instead of creating SEO
  duplicates.
- `/sitemap.xml` prefers canonical public routes while preserving ecommerce
  URLs that still need discovery continuity through testing and launch review.
- `/robots.txt` allows public crawling, advertises the current-host sitemap,
  and must not point crawlers at the Frappe Cloud vanity host.
- Public sitemap, canonical, Open Graph URL, and structured-data URLs must use
  the tested public host. For production, that means `https://locallytwisted.com`,
  not `https://locallytwisted.v.frappe.cloud`.
- `/event-balloons` and `/event_balloons` are intentionally removed. They must
  return 404 with no redirect and must not appear in `/sitemap.xml`, canonical
  maps, route aliases, or public links.
- Home and service routes expose stable business/service structured data
  without hardcoded ratings or hours.
- `/faq` visible questions must match FAQPage JSON-LD. The current AEO question
  set is:
  - `How are face painting and balloon twisting priced?`
  - `How is event balloon decor priced?`
  - `What payment is required for personal balloon decor?`
  - `How do pickup and delivery usually work for ready-to-order items?`
  - `Do corporate clients pay deposits?`
- BTFP carousel content images need descriptive alt text.

## 2026-05-10 Closeout

Review found the SEO gate was failing because it still expected three older
generic FAQ questions while the page now renders service-specific FAQ content.
The verifier now uses the current FAQ question list for both visible summaries
and FAQPage JSON-LD.

## 2026-05-11 Route Removal Closeout

GL rejected `/event-balloons` before launch. The route is removed with no
redirect, and the SEO contract now treats `/event-balloons` plus
`/event_balloons` as excluded discovery paths. The four event audience routes
remain the crawlable event-discovery pages.

## 2026-05-19 Public Domain Drift

Live provider audit confirmed `locallytwisted.com` serves from Frappe Cloud
through Cloudflare, but the discovery layer still points at the Frappe Cloud
vanity host:

- `https://locallytwisted.com/sitemap.xml` returned 29 locs, all on
  `https://locallytwisted.v.frappe.cloud`.
- `https://locallytwisted.com/about` emitted canonical and `og:url` values on
  `https://locallytwisted.v.frappe.cloud/about`.

Source was patched so SEO helpers prefer the current request host and sitemap
generation uses the same absolute URL helper. The Playwright SEO contract now
rejects sitemap URLs on `locallytwisted.v.frappe.cloud` or any host other than
the tested base host.

This is not live until the Frappe Cloud app release/site update/cache clear
sequence completes and the SEO contract passes against
`https://locallytwisted.com`.

## 2026-05-21 Robots And Local Host Closeout

Local verification found `/robots.txt` returned 200 with blank content, so it
was not blocking crawlers but also was not advertising the sitemap. The LT app
now owns `www/robots.py` and `www/robots.txt`, allowing public crawl and
emitting `Sitemap: <current-host>/sitemap.xml`.

The local nginx/Frappe request host drops the `:8081` port, while site config
correctly knows `http://localhost:8081`. The SEO helper now falls back to the
configured URL only when the configured URL has the same host plus an explicit
port that the request lost. Production still prefers the request domain so
`locallytwisted.com` can replace the Frappe Cloud vanity host.

Local result after cache clear and web-process restart: `npm run
test:seo-contract` passed 12/12 against `http://localhost:8081`.

## Verification

```powershell
npm run test:seo-contract
```

Latest focused route-removal result: 2/2 passed on 2026-05-11 with
`npm run test:seo-contract -- --grep "removed Event Balloons|sitemap" --workers=1`.

Live reindex gate after Frappe Cloud release:

```powershell
$env:LT_BASE_URL='https://locallytwisted.com'
npm run test:seo-contract
```

## Open Rules

- Do not hardcode exact Google review counts or ratings unless reverified in
  the same run.
- Do not submit the sitemap, request reindexing, hand off Search Console, or
  give the external marketing company indexing authority until the shop is on
  staging and the owner approves products to go live.
- If FAQ visible content changes, update `FAQ_AEO_QUESTIONS` in `faq.py` and
  the verifier expectations in the same slice.
- If a public route alias is added, decide whether it redirects or declares a
  canonical route; do not leave duplicate canonicals ambiguous.
- Do not add redirects for owner-rejected prelaunch routes unless GL explicitly
  asks for a redirect. A clean 404 is the correct state for `/event-balloons`.
- Do not submit a sitemap or ask Google to recrawl while sitemap/canonical
  output advertises the Frappe Cloud vanity host.
