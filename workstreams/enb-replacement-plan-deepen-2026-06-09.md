# ENB Replacement Plan-Deepen - 2026-06-09

## Outcome

Status: `adjust`.

The existing ENB replacement plan is directionally correct, but it needs a
clearer split between:

1. lead rescue work that can create inquiries immediately;
2. package work that makes tracking/reporting trustworthy;
3. long-term SEO/AEO/GEO work that improves visibility but will not replace
   paid lead flow fast enough by itself.

This note is planning only. It does not approve ad spend, ad-account mutation,
ENB removal, Search Console changes, live checkout, provider changes, customer
data export, or live tracking.

## Evidence Checked

Current repo evidence:

- `MARKETING-REPLACEMENT-AND-SHOP-GO-LIVE-PLAN-2026-06-08.md`
- `workstreams/enb-replacement-shop-go-live-2026-06-08.md`
- `workstreams/marketing-lead-replacement-lane-2026-06-08.md`
- `workstreams/conversion-tracking-architecture-lane-2026-06-08.md`
- `workstreams/payment-shop-go-live-gate-lane-2026-06-08.md`
- `capabilities/recipes/lt-seo-geo-aeo-contract.md`

Official source snapshot checked 2026-06-09:

- Google Ads conversion measurement:
  `https://support.google.com/google-ads/answer/1722022`
- Google Ads qualified and converted leads:
  `https://support.google.com/google-ads/answer/11459091`
- Google Ads lead form assets:
  `https://support.google.com/google-ads/answer/9423234`
- GA4 ecommerce:
  `https://developers.google.com/analytics/devguides/collection/ga4/ecommerce`
- Meta lead ads with website and instant forms:
  `https://www.facebook.com/business/ads/ad-objectives/lead-generation/lead-ads-with-forms`
- Meta Conversions API:
  `https://www.facebook.com/business/help/AboutConversionsAPI`
- Google SEO starter guide:
  `https://developers.google.com/search/docs/fundamentals/seo-starter-guide`
- Google Product structured data:
  `https://developers.google.com/search/docs/appearance/structured-data/product`
- Google Business Profile performance:
  `https://support.google.com/business/answer/9918094`

## Section 1 - Immediate Lead Rescue

Evidence checked:

- ENB replacement packet says Jeff valued leads, not vendor access.
- Google Ads and Meta both support lead-focused campaigns.
- Meta supports both website forms and instant forms.
- Google Ads lead form assets can generate leads directly in ads, but those
  leads do not behave the same as website/GA analytics traffic.

Risks found:

- If the plan waits for ecommerce checkout, SEO, or full tracking before any
  campaign work, Jeff can lose another week with no replacement proof.
- If ads point at checkout before the shop/payment gate passes, customers may
  hit a broken or paused purchase path.
- If Google or Meta native lead forms are used without CRM retrieval and
  follow-up ownership, leads can exist in a dashboard while LT never works
  them.

Plan adjustment:

- Run a 72-hour lead rescue lane that does not depend on live checkout.
- Point immediate campaigns to verified inquiry/service routes, not checkout:
  `/contact`, twisting/face-painting service pages, and approved category or
  product pages only after product-page smoke proof passes.
- Use website-form leads as the default because they enter LT's ERP path.
- Allow Google/Meta native lead forms only as a fast fallback after lead
  retrieval, notification, and owner follow-up are proven.
- Track first results as practical proof: calls, website clicks, form
  submissions, ERPNext Leads, and booked jobs.

Open approval:

- Jeff/GL must approve platform, budget, first offer, destination URLs, and
  whether native lead forms are allowed before live ad changes.

## Section 2 - Package Build Needed Now

Evidence checked:

- Current repo search found planning docs for GA4/Google/Meta tracking, but no
  implemented app-level tag/conversion bridge in `apps/`.
- Conversion lane correctly states Lead creation and paid-order reconciliation
  are the business authorities.
- Google and Meta tracking require configured conversion events and platform
  identifiers; those should not be hard-coded into source.

Risks found:

- Without a package-level bridge, LT cannot prove ad return cleanly inside the
  ERP system.
- Thank-you page tracking alone can double-count or report fake success.
- Browser-only purchase tracking can lie if payment reconciliation fails.
- Live tags without consent and account ownership decisions create privacy and
  vendor-control risk.

Plan adjustment:

Build a small, disabled-by-default marketing measurement bridge in the
`locally_twisted` app:

1. `LT Marketing Settings` or equivalent config surface for non-secret IDs and
   enable flags.
2. No-send event envelope and schema verifier.
3. UTM/session capture for public visits, with source fields carried into
   Lead and later order context where safe.
4. Browser tag loader for GA4/Google Ads/Meta Pixel, disabled until approved.
5. Lead event hook after ERPNext Lead insert succeeds.
6. Purchase event hook after paid-order reconciliation succeeds.
7. Dedupe IDs: `lead:<Lead.name>` and `purchase:<Sales Order.name>`.
8. Guards proving paused checkout never fires checkout or purchase events.
9. Network/intercept tests proving no Google/Meta requests fire when disabled.

Open approval:

- Consent behavior, platform IDs, provider account ownership, and live event
  transmission require GL/Jeff approval.

## Section 3 - SEO / AEO / GEO Reality

Evidence checked:

- LT already has a local SEO/GEO/AEO contract, but its capability says
  `currently_true: false` until live sitemap/canonical proof is deployed.
- Google SEO guidance says changes can take time and there is no instant
  ranking guarantee.
- Google Product structured data can help product pages appear with richer
  product information when markup matches real page data.

Risks found:

- Treating SEO/AEO/GEO as the immediate lead replacement is unsafe.
- Product pages should not be indexed or given Product/Offer markup that
  implies purchasability while ecommerce is paused or quote-first.
- AEO/GEO copy can become fake if it invents service facts, service areas,
  reviews, hours, or pricing.

Plan adjustment:

- Use SEO/AEO/GEO as the durable visibility lane, not the 72-hour lead rescue
  lane.
- Prioritize stable service pages, local business structured data, FAQ parity,
  sitemap/canonical correctness, product structured data only when it matches
  real availability/checkout/quote state, and Google Business Profile alignment.
- Treat "EGO" as brand/entity visibility unless GL defines a different meaning.
- Do not submit Search Console or request reindexing until the production SEO
  contract passes on `https://locallytwisted.com`.

Open approval:

- Owner-approved hours, service area, policy language, review usage, and any
  product claims must be confirmed before public visibility changes.

## Section 4 - Paid Ads Architecture

Evidence checked:

- Current lane docs identify Google Ads account IDs and ENB manager evidence
  as items to preserve, but provider dashboards remain unverified.
- Google Ads supports qualified and converted lead stages from CRM/offline
  data.
- Meta recommends mixed lead strategies, including website forms and instant
  forms.

Risks found:

- Removing ENB before exporting campaigns, conversions, billing, tags, final
  URLs, lead forms, phone numbers, and pipeline data could destroy useful
  lead-source history.
- Native lead forms can create "leads" outside ERPNext unless retrieval is
  wired.
- Optimizing ads to raw leads can reward low-quality leads unless qualified or
  booked stages are fed back later.

Plan adjustment:

- Keep ENB removal separate from campaign replacement.
- Inventory/export first, then revoke only after approval.
- First Google Ads structure should separate:
  - high-intent search for decor/arches/garlands;
  - twisting/face-painting service leads;
  - ready-to-order purchase intent only after checkout passes live gate;
  - brand/local defense if needed.
- First Meta structure should separate:
  - instant-form lead capture if approved and retrieval is proven;
  - website-form lead capture to `/contact`;
  - event decor creative;
  - twisting/face-painting creative;
  - seasonal creative.
- Build later feedback events for qualified and converted leads from ERPNext
  stages, not only public form submits.

Open approval:

- Budget, campaign activation, destination changes, ENB access changes, native
  form usage, call-tracking number ownership, and any customer-list/audience use.

## Section 5 - Analytics And Jeff Proof

Evidence checked:

- Google Ads and Google Business Profile both expose performance data, but
  external reports alone will not prove ERP-backed business outcomes.
- LT needs one report that connects ad/platform activity to ERPNext Leads,
  orders, and booked work.

Risks found:

- Jeff may see "clicks" but not understand whether leads or booked jobs are
  improving.
- Platform conversion counts can disagree with ERPNext if dedupe, native forms,
  phone calls, or offline lead stages are not reconciled.

Plan adjustment:

Create a Jeff-facing weekly proof report with:

- spend by platform;
- clicks and calls;
- website sessions or landing visits;
- submitted inquiries;
- ERPNext Leads by source;
- qualified leads;
- booked jobs or paid orders;
- cost per lead;
- cost per booked job or sale;
- broken route, missed call, or failed-notification incidents;
- next action for each campaign.

Launch a daily 24-hour watch during the first replacement campaign window.

Open approval:

- What Jeff considers a "good lead" and what stage counts as booked/converted.

## Section 6 - Security, Privacy, And Access

Evidence checked:

- Existing LT docs correctly reject broad external Website Manager/Desk access.
- Meta CAPI and Google enhanced/offline conversions may involve customer data
  or hashed user-provided data.

Risks found:

- Marketing access can accidentally become customer-data access.
- Tracking can become privacy-risky if email, phone, IP, user-agent, event
  messages, or uploaded-file metadata are sent without approval.
- Ad platforms can spend money if automation is not gated.

Plan adjustment:

- Keep ENB access limited to public review/export coordination unless approved.
- Do not add ad automation that can publish, pause, enable, or spend without
  human approval.
- Do not send customer identifiers to Google or Meta server APIs until consent
  and business approval are explicit.
- Keep all tracking disabled by default in source.

Open approval:

- Consent policy, privacy copy, enhanced conversion/CAPI customer-data rules,
  and vendor offboarding timing.

## Revised Execution Order

1. Finish current shop/product/contact cleanup enough that public routes are not
   embarrassing or broken.
2. Add no-send marketing measurement bridge and UTM/Lead attribution locally.
3. Verify no network sends when tracking is disabled.
4. Prepare first 72-hour Google/Meta lead rescue campaign drafts and destination
   map.
5. Inventory/export ENB/provider data before access removal.
6. With approval, enable tracking test mode and confirm provider dashboard test
   events.
7. With approval, launch the first small lead campaign to verified inquiry
   routes.
8. Run 24-hour watch and produce Jeff proof report.
9. Only after live checkout gate passes, add purchase-optimized campaigns.
10. After production SEO contract passes, submit sitemap/Search Console and
    continue SEO/AEO/GEO work.

## Decision Needed From GL / Jeff

1. Approve whether the immediate replacement campaign is Google only, Meta only,
   or both.
2. Approve the first budget window.
3. Approve the first offer: event decor quote, twisting/face-painting, or
   ready-to-order only after checkout is ready.
4. Decide whether ENB should be removed immediately after export or kept as
   temporary export-only support.
5. Approve whether native Google/Meta lead forms are allowed as a fast lead
   source, knowing they require explicit retrieval/reconciliation.

## Bottom Line

The plan should not wait for another packet. It should turn into two immediate
work lanes:

- `Lead rescue`: ads and local visibility pointed to verified inquiry paths.
- `Measurement bridge`: source-controlled tracking/attribution inside the
  Frappe app, disabled by default until approved.

SEO/AEO/GEO matters, but it is not the emergency lead engine. Paid Google/Meta
plus tight ERPNext attribution is the fast replacement for ENB's useful
function.
