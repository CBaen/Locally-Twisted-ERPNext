# SEO/GEO/AEO Contract

Last updated: 2026-05-10 by Codex after FAQ verifier drift repair.

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

## Verification

```powershell
npm run test:seo-contract
```

Latest result: 11/11 passed on 2026-05-10.

## Open Rules

- Do not hardcode exact Google review counts or ratings unless reverified in
  the same run.
- If FAQ visible content changes, update `FAQ_AEO_QUESTIONS` in `faq.py` and
  the verifier expectations in the same slice.
- If a public route alias is added, decide whether it redirects or declares a
  canonical route; do not leave duplicate canonicals ambiguous.
