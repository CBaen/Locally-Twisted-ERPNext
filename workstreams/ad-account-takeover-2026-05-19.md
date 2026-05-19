# Google Ads And Meta Account Takeover - 2026-05-19

## Scope

This handoff covers taking operational control of Locally Twisted's Google Ads
and Meta/Facebook/Instagram advertising accounts.

This is not the same lane as `workstreams/marketing-review-access-2026-05-15.md`.
Marketing review access is a Frappe website-only review account. Ad account
takeover is provider account control: users, manager/partner links, billing,
campaigns, pixels/tags, lead forms, tracking numbers, and conversion setup.

No Google Ads, Meta, billing, user-access, campaign, or live-site mutation was
performed in this slice. No production deploy was performed.

## Verified Evidence From LT Gmail And Drive

Connector identity:

- Gmail account checked: `locallytwisted@gmail.com`.
- Google Drive account checked: `locallytwisted@gmail.com`.

Google Ads account evidence:

- Current Google Ads account name: `Locally Twisted`.
- Current Google Ads customer ID: `437-723-0551`.
- Older Google Ads customer ID found in historical messages: `295-025-7991`.
- ENB manager-link evidence: `ENB Manager Account`, manager customer ID
  `124-663-1239`, requested link to `437-723-0551` in December 2024.
- ENB admin-user evidence: `tosh@exploringnotboring.com` was invited with
  `Administrative` access to Google Ads account `437-723-0551` in November
  2024.

Current Google Ads issue from the policy email and GL-provided URL:

- Campaign: `ENB_Sales_Search_Custom Balloon Arches + Delivery - $5/day | 12.27.24`.
- Campaign ID: `22063769748`.
- Ad ID from GL URL: `727037766855`.
- Ad group ID from GL URL: `172271504586`.
- Policy issue: `Destination not working`.
- Google-reported failure: HTTP `404`.
- This is an account/campaign issue, not a local Frappe route proof.

Known Google Ads / ENB campaign history from Gmail reports:

- Face painting search ads were active in 2025.
- Balloon campaign performance was reported by ENB through 2025.
- Halloween keyword/ad content was researched and launched/updated in 2025.
- Planned or proposed Q1 2026 ads included Birthday Balloon Deliveries,
  Balloon Decor, Backdrops, Arches, Garlands, and Helium Balloon Deliveries.
- ENB reported Google Ads performance for Oct 1-Dec 31, 2025: 442 clicks,
  9.55% CTR, $1,065.42 ad spend plus $166.51 rev-share, 22 new leads,
  3 new orders, and $1,665.12 gross sales attributed in the report.

Tracking and measurement evidence:

- ENB reported updating the WordPress GA tracking ID from retired
  `UA-57420313-1` to `G-0Z0WY5XQRB` in April 2025.
- Google Ads emails reported enhanced conversion setup errors in 2026.
- Google Ads emails reported legacy Universal Analytics tag usage in January
  2026.
- The current Frappe site has not been proven to carry the same Google tag,
  GTM, conversion, remarketing, call, or enhanced-conversion setup.

Billing/account evidence:

- Google Ads service was suspended for past-due payment on March 3, 2026 for
  customer ID `437-723-0551`; amount reported: `$263.78`.
- Payment of `$272.89` was received the same day for customer ID
  `437-723-0551`.
- Payments profile observed in those messages: `0241-0787-0714`.
- Billing ownership and active payment method must still be verified in the
  Google Ads dashboard before any access removal.

Meta/Facebook/Instagram evidence:

- A 2024 Facebook Business Manager email requested confirmation that Jeffery
  Kimber's business email should be updated to `locallyTwisted@gmail.com`.
- ENB/HighLevel email threads show a `Facebook Painting Leads` pipeline and a
  Facebook Lead Notification path that created a contact/opportunity.
- Direct Meta Ad Account ID, current campaigns, pixels/datasets, billing,
  partners, and lead forms were not verified from dashboard/API in this slice.

HighLevel / ENB lead-pipeline dependency evidence:

- Face painting landing page observed in ENB materials:
  `https://locallytwisted.com/professional-face-painters`.
- ENB materials reference `app.exploringnotboring.com` / HighLevel.
- Face painting ad leads used a tracking phone number: `(801) 784-3426`.
- ENB reported `Face Painting Leads` and `Facebook Painting Leads` pipelines.
- Do not remove ENB/HighLevel access until lead routing, tracking phone
  ownership, missed-call behavior, and historical lead export are understood.

Other advertising inventory:

- Drive contains an iHeartMedia/KJMY-FM advertising trade agreement signed for
  Locally Twisted, dated `02/01/2025`, with `$3,120.00` airtime / balloon
  credit value and an airtime use-by date of `02/28/2026`.
- This is advertising inventory, but not Google Ads or Meta account control.

## Actions Performed In This Slice

- Read-only Gmail and Drive search for account, campaign, billing, tracking,
  ENB, Google Ads, and Facebook/Meta evidence.
- Read-only repo search for local marketing/ad/tag evidence.
- Opened GL's exact Google Ads URL in Chrome:
  `https://ads.google.com/aw/ads/edit/search?ocid=110242822&adId=727037766855&adGroupIdForAd=172271504586&returnTo=/aw/policymanager/issues?ocid%3D110242822&euid=122544742&__u=1190795958&uscid=110242822&__c=4620865878&authuser=1&from=policyemail`.

## Not Done

- No Google Ads dashboard crawl was completed from an authenticated automation
  surface.
- No Meta Business dashboard crawl was completed.
- No campaign was edited, paused, enabled, deleted, copied, or published.
- No user, manager, partner, billing, pixel, tag, lead form, dataset, or
  conversion setting was changed.
- No local website code or production site code was changed.
- No Frappe Cloud, Cloudflare, Stripe, DNS, or live ecommerce action was taken.

## Control Checklist For Next Agent

Use `capabilities/recipes/ad-account-takeover-provider-control.md`.

Google Ads dashboard:

- Confirm selected account is `Locally Twisted` / customer ID `437-723-0551`.
- Export/screenshot `Tools > Admin > Access and security`.
- Record all users, access levels, accepted/invited state, and 2FA state.
- Record linked manager accounts, especially ENB manager ID `124-663-1239`.
- Export campaigns, ad groups, ads, assets, keywords, search terms, audiences,
  locations, bidding, budgets, policy issues, change history, and experiments.
- Inspect billing/payment settings before any access removal.
- Inspect conversions, Google tag, GTM/GA4 links, call assets, call recording,
  enhanced conversions, offline conversions, lead-form assets, and linked
  accounts.
- Fix or document the 404 destination issue for campaign `22063769748` only
  after final URLs are exported.

Meta Business dashboard:

- Confirm Business Manager owner and business ID.
- Export/screenshot people, partners, Pages, Instagram accounts, ad accounts,
  pixels/datasets, domains, apps, lead forms, billing, payment methods, and
  connected CRMs.
- Record ENB/agency partner access before changing it.
- Export active and inactive campaigns/ad sets/ads, lead forms, creatives,
  audiences, pixels, custom conversions, and events.
- Confirm whether the `Facebook Painting Leads` path belongs to Meta native
  lead forms, HighLevel, or both.

HighLevel / ENB dependency review:

- Export lead pipelines and current routing before removing manager/partner
  access.
- Confirm ownership and forwarding of `(801) 784-3426`.
- Confirm which landing pages and tracking URLs are still live.
- Identify whether any active ads point to ENB-owned pages, HighLevel forms,
  or old WordPress paths that now 404.

## Safe Takeover Order

1. Inventory dashboard access and exports first.
2. Verify billing, tracking, lead routing, and landing page dependencies.
3. Repair active 404 destinations or pause broken spend with GL approval.
4. Move/clone critical tracking and lead capture into LT/BBC-owned surfaces.
5. Only then downgrade/remove ENB users, manager links, or partner links.

## Cross-Links

- Project decision: `locally-twisted-decisions.md`
- Project lesson: `lessons-learned.md`
- Project queue: `locally-twisted-queue.md`
- Capability: `capabilities/recipes/ad-account-takeover-provider-control.md`
- Failure recipe: `capabilities/failures/ad-dashboard-research-vs-control-drift.md`
- Related provider failure:
  `capabilities/failures/provider-dashboard-work-bounced-to-gl.md`
- Website-only ENB review lane:
  `workstreams/marketing-review-access-2026-05-15.md`
