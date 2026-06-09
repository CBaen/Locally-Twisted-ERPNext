# Jeff / ENB Transition Communication Lane - 2026-06-08

## Scope

This lane is for owner/vendor communication only.

Write target: `workstreams/jeff-enb-transition-communication-lane-2026-06-08.md`.

Do not use this lane to change Google Ads, Meta, HighLevel, WordPress, Frappe
Cloud, Cloudflare, DNS, Stripe, Search Console, billing, customer data, live
site state, provider access, ad spend, pixels, tags, forms, phone routing, or
campaign settings.

## Current Evidence

Conversation recall status for this lane: `coverage_incomplete`.

The usable current evidence is repo evidence, not transcript memory:

- LT has an ERPNext/Frappe-backed website and ecommerce system, not a simple
  marketing-site edit path.
- Prior ENB evidence is support evidence: Gmail/Drive reports, account emails,
  and HighLevel clues. It is not current provider-control evidence.
- Google Ads support evidence identifies account `Locally Twisted` /
  `437-723-0551`, historical account `295-025-7991`, ENB manager ID
  `124-663-1239`, ENB admin-user evidence for
  `tosh@exploringnotboring.com`, and campaign `22063769748` with a
  `Destination not working` / HTTP `404` issue.
- Meta evidence is incomplete. Email and ENB/HighLevel clues exist, but current
  Meta ad account ID, current campaigns, pixels/datasets, lead forms, partner
  access, and billing are not dashboard-proven.
- HighLevel / ENB dependency evidence includes face-painting lead pipelines,
  `app.exploringnotboring.com`, and tracking phone number `(801) 784-3426`.
- Existing project rules say not to remove ENB/agency access before exports,
  billing, tracking, lead-routing, phone ownership, and conversion context are
  understood.

## Plain-English Position

The message to Jeff is:

ENB may have supported the old marketing setup, but they cannot logically be
responsible for the new ERP-backed system unless they are working inside the new
source of truth.

That is not a blame statement. It is a system boundary:

- The new site is not just page content. It includes ERPNext records, product
  catalog behavior, inquiry records, checkout gates, fulfillment logic,
  operator notifications, and fail-loud verification.
- Old WordPress, HighLevel, or ad-report context does not prove what happens in
  the new ERP-backed site.
- Ads, lead forms, tracking numbers, pixels, and landing pages may still depend
  on ENB-managed paths. Those must be exported before access changes.
- Replacement proof should be based on specific working paths, not a broad
  promise that the new system is "ready" or that marketing performance will
  improve immediately.

The message to ENB is:

Locally Twisted is moving its operating website and lead flow into a new
ERP-backed system, so the handoff needs a clean transition export. This is a
continuity request, not a dispute.

## Communication Goals

1. Give Jeff a calm reason this needs transition work instead of asking ENB to
   keep supporting a system they do not control.
2. Ask ENB for enough export data to preserve lead routing, tracking, reporting,
   and ad continuity.
3. Avoid accusation, threats, or "prove you did your job" wording.
4. Keep provider changes gated until exports and replacement proof exist.
5. Separate "we can replace the operating website path" from "we have proven
   ad performance, tracking parity, and live checkout readiness."

## Data To Request From ENB

Request exports or screenshots where export is unavailable. Do not ask for raw
passwords, secrets, OAuth tokens, API keys, private keys, or billing-card
numbers.

Google Ads:

- Current account name and customer ID.
- User access table, including ENB manager links, invited users, accepted users,
  access levels, and manager account IDs.
- Campaign, ad group, ad, asset, keyword, negative keyword, audience, location,
  schedule, budget, bidding, experiment, recommendation, and policy-issue
  exports.
- Final URLs, tracking templates, URL suffixes, UTM rules, landing page URLs,
  and any known 404 or retired-page destinations.
- Conversion actions, Google tag, GTM container references, GA4 links,
  enhanced conversions, remarketing, call assets, call recording settings,
  lead-form assets, offline conversion settings, linked accounts, and change
  history.
- Current billing owner/status summary without exposing full payment details.

Meta / Facebook / Instagram:

- Business Manager ID and owner.
- People, partners, Pages, Instagram accounts, ad accounts, pixels/datasets,
  domains, apps, system users, connected CRMs, billing/payment status, and lead
  forms.
- Active and inactive campaigns, ad sets, ads, creatives, audiences, custom
  conversions, event sources, placements, budgets, schedules, and results.
- Any lead form field mappings, webhook/CRM integrations, and destination URLs.
- Confirmation of whether `Facebook Painting Leads` is a Meta native lead form,
  a HighLevel pipeline, or both.

HighLevel / ENB lead-routing:

- Pipelines, stages, automations, forms, landing pages, calendars, workflows,
  tags, lead-source labels, notification rules, missed-call/text behavior, and
  webhook destinations.
- Tracking number `(801) 784-3426`: ownership, forwarding target, call routing,
  recording status if any, texting status if any, and transfer options.
- Historical lead export for ENB-captured LT leads, subject to Jeff approval
  and secure transfer: created date, source, campaign, form/landing page,
  pipeline/stage, name, phone, email, message, appointment/request details,
  consent/source notes, owner/assignee, and current disposition.
- Any active URLs that point to ENB-hosted pages or forms.

Reporting and creative:

- Monthly reports, dashboards, attribution assumptions, KPI definitions, and
  date ranges for 2024-2026 work.
- Ad creative, landing page copy, images, videos, offer language, audience
  notes, keyword themes, and campaign naming conventions.
- Known seasonal campaign plans or paused campaigns that may need to be
  preserved or retired.

Transfer method:

- Prefer dashboard exports, CSVs, screenshots, and shared Drive folder files.
- For personal/customer lead data, use a Jeff-approved secure transfer path.
- Do not send private keys, passwords, or token files.

## Approval Gates

Before sending Jeff draft:

- GL/Built by Cameron approves the plain-English framing.
- GL confirms whether Jeff should see "ENB cannot logically support" wording
  or a softer version such as "ENB cannot be accountable for the new system
  until the new source of truth is in place."

Before sending ENB request:

- Jeff approves the vendor tone and data list.
- Jeff approves requesting historical lead/customer-contact export.
- Jeff approves who should be copied.
- Jeff approves a transfer path for sensitive lead/customer-contact data.

Before any provider/access action:

- Google Ads and Meta dashboard exports exist or are explicitly marked missing.
- HighLevel/lead-routing and tracking-phone dependencies are captured.
- Billing owner/status is understood.
- Replacement lead path is proven in the new system.
- Jeff separately approves pausing spend, changing final URLs, removing ENB
  access, removing manager links, replacing pixels/tags, replacing tracking
  numbers, or changing live provider settings.

Before replacement proof is described externally:

- Define the proof target: inquiry path, quote path, checkout path, tracking
  path, campaign URL path, or owner operations path.
- Record what was verified, where it was verified, and what remains unverified.
- Do not treat local proof, staging proof, ad-dashboard export, and live release
  as interchangeable.

## Replacement Proof Without Overpromising

Use narrow proof statements:

- "The new ERP-backed site can receive and store a test inquiry through the
  approved path."
- "The product and inquiry paths are controlled in the new ERP system, not in
  the old page-builder or HighLevel setup."
- "We can map current ad destinations once ENB exports the final URLs and
  tracking templates."
- "We can prove the replacement path in stages before changing live ads or
  removing ENB access."

Do not use broad claims:

- "The new system is fully ready."
- "We have replaced ENB."
- "All tracking is migrated."
- "Ads can be switched today."
- "Checkout is live-ready."
- "Lead reporting will match the old reports."
- "No customer data will be lost."

Proof checklist:

- Owner-approved target paths are named.
- Test lead/inquiry record is created in ERPNext where applicable.
- Operator notification or review path is proven where applicable.
- Public route loads without false success states.
- If tracking is involved, the exact tag/pixel/conversion event is installed
  and verified in the correct provider surface.
- If ads are involved, final URLs are exported before edits and then tested.
- If live checkout is involved, it uses the separate checkout/payment release
  gate, not this communication lane.

## Draft Email To Jeff

Subject: Clean transition plan for ENB and the new Locally Twisted system

Hi Jeff,

I want to separate two things so this stays calm and practical.

ENB may have supported the older marketing setup, but the new Locally Twisted
system is not just a website edit. It is tied into ERPNext: products, inquiry
records, checkout gates, operator review, and the business workflow behind the
site.

That means ENB cannot logically be accountable for the new system unless they
are working from the new source of truth. This is not a blame statement. It is
just a boundary between the old marketing stack and the new operating system.

The safe next step is to ask ENB for a transition export before anyone removes
access or changes ads. We need their current ad, tracking, landing page,
HighLevel, phone-routing, and lead-pipeline information so we do not break a
working lead path by accident.

What I would like to ask them for:

- Google Ads users, manager links, campaigns, final URLs, tracking templates,
  conversions, tags, call assets, lead forms, billing status, and change
  history.
- Meta/Facebook/Instagram business access, ad accounts, campaigns, pixels,
  datasets, lead forms, partners, Pages, Instagram accounts, billing status,
  and connected CRMs.
- HighLevel pipelines, forms, workflows, landing pages, notification rules,
  tracking number ownership/routing, and a Jeff-approved export of historical
  LT leads they captured.
- Monthly reports, creative, copy, campaign naming, seasonal plans, and any
  active URLs that still point to ENB-hosted pages or forms.

I would frame this as a continuity request, not a conflict. Something like:
"We are moving the website and lead flow into a new ERP-backed system and need
a clean transition export so active leads, tracking, and reporting are not lost."

What this does not mean yet:

- It does not mean ads are ready to switch today.
- It does not mean live checkout is approved.
- It does not mean we should remove ENB access before exports are captured.
- It does not mean old reporting will automatically match the new system.

Once we have the export, we can prove replacement in small pieces: inquiry path,
ad destination URLs, tracking/conversion setup, lead notifications, and only
then any provider/access changes you approve.

Please confirm whether you want me to send ENB a transition-export request in
that tone, and whether you approve requesting the historical lead export through
a secure transfer path.

## Draft Email To ENB

Subject: Locally Twisted transition export request

Hi [ENB contact],

Jeff is moving Locally Twisted's website and lead flow into a new ERP-backed
system. We want to make the transition clean and avoid breaking active ads,
tracking, lead routing, or reporting.

This is a continuity request. We are not asking for passwords, private keys, or
token files. We are asking for exports, screenshots, or summaries of the current
marketing setup so Jeff can preserve the working pieces during the transition.

Could you please provide the following for Locally Twisted?

Google Ads:

- Current account name/customer ID, user access, manager links, and access
  levels.
- Campaigns, ad groups, ads, assets, keywords, audiences, locations, schedules,
  budgets, bidding, policy issues, final URLs, tracking templates, URL suffixes,
  and change history.
- Conversion actions, Google tag/GTM/GA4 references, enhanced conversions,
  remarketing, call assets, call recording settings, lead-form assets, offline
  conversions, linked accounts, and billing-status summary.

Meta / Facebook / Instagram:

- Business Manager ID/owner, people, partners, Pages, Instagram accounts, ad
  accounts, pixels/datasets, domains, apps, system users, connected CRMs, lead
  forms, and billing-status summary.
- Active and inactive campaigns, ad sets, ads, creatives, audiences, custom
  conversions, event sources, placements, budgets, schedules, and results.

HighLevel / lead routing:

- Pipelines, stages, forms, landing pages, calendars, workflows, tags,
  notification rules, missed-call/text behavior, webhook destinations, and
  source labels.
- Tracking number `(801) 784-3426`: ownership, forwarding/routing, recording
  or texting status if applicable, and transfer options.
- Any active URLs that point to ENB-hosted pages, forms, or redirects.
- Historical export of Locally Twisted leads captured through ENB-managed
  forms or pipelines, using the secure transfer method Jeff approves.

Reporting and creative:

- Monthly reports, dashboards, KPI definitions, date ranges, attribution notes,
  ad creative, landing page copy, campaign naming conventions, keyword themes,
  seasonal plans, and paused campaigns worth preserving.

If a requested item cannot be exported directly, screenshots or a short written
summary are fine. If a requested item does not exist, please mark it as not
applicable so we do not assume it was missed.

Thanks for helping keep the handoff clean.

## What Should Not Be Said

Do not say:

- "ENB broke the site."
- "ENB failed."
- "ENB has to prove they did the work."
- "We are firing you."
- "We need your passwords."
- "Send all customer data over email."
- "The new site is ready to replace everything."
- "Ads can be switched immediately."
- "Tracking is already migrated."
- "Checkout is ready."
- "We will remove your access after this email."
- "Built by Cameron owns all of ENB's strategy, creative, or proprietary
  internal systems."
- "The 404 proves all ENB work is bad."

Use instead:

- "We are moving the operating website and lead flow into a new ERP-backed
  system."
- "We need transition exports so nothing useful is lost."
- "We want to preserve active lead paths before changing access."
- "If something cannot be exported, a screenshot or summary is fine."
- "Provider changes will happen only after Jeff approves them."

## Closeout Criteria

This lane is complete when the repo has:

- Jeff-facing draft.
- ENB-facing draft.
- Exact transition data request.
- Approval gates.
- Replacement-proof framing.
- What-not-to-say guardrails.
- No provider, live, staging, DNS, Stripe, Search Console, ad account,
  customer-data, secret, billing, or access mutation.
