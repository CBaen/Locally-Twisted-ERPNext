# SEO/GEO/AEO Contract

Last updated: 2026-05-11 by Codex after `/event-balloons` removal and no-redirect sitemap guard.

## Scope

This handoff owns the launch technical discovery gate for canonical public
routes, sitemap shape, social metadata, business/service structured data,
FAQPage AEO answers, and content-image alt text. It is not a content strategy
plan and does not certify search rankings.

## Current Contract

- `/about` is source-owned and exposes canonical, Open Graph, Twitter card, and
  LocalBusiness/Organization JSON-LD without unverified ratings or hours.
- Legacy route aliases declare canonical public routes instead of creating SEO
  duplicates.
- `/sitemap.xml` prefers canonical public routes while preserving ecommerce
  URLs that still need discovery continuity through testing and launch review.
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

## Verification

```powershell
npm run test:seo-contract
```

Latest focused route-removal result: 2/2 passed on 2026-05-11 with
`npm run test:seo-contract -- --grep "removed Event Balloons|sitemap" --workers=1`.

## Open Rules

- Do not hardcode exact Google review counts or ratings unless reverified in
  the same run.
- If FAQ visible content changes, update `FAQ_AEO_QUESTIONS` in `faq.py` and
  the verifier expectations in the same slice.
- If a public route alias is added, decide whether it redirects or declares a
  canonical route; do not leave duplicate canonicals ambiguous.
- Do not add redirects for owner-rejected prelaunch routes unless GL explicitly
  asks for a redirect. A clean 404 is the correct state for `/event-balloons`.
