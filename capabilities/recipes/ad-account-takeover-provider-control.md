---
name: Ad account takeover provider control
level: recipe
last_verified: 2026-05-19
currently_true: true
---

# Ad Account Takeover Provider Control

## What It Does

Keeps Google Ads and Meta/Facebook/Instagram takeover work rooted in the
provider dashboards instead of substituting inbox research, reports, or public
ad-library lookup for account control.

The active LT handoff is
`workstreams/ad-account-takeover-2026-05-19.md`.

## Current LT Facts

- Google Ads account: `Locally Twisted`, customer ID `437-723-0551`.
- Historical Google Ads customer ID: `295-025-7991`.
- ENB manager-link evidence: manager customer ID `124-663-1239`.
- ENB admin-user evidence: `tosh@exploringnotboring.com`.
- Current Google Ads issue: campaign `22063769748` has a
  `Destination not working` / HTTP `404` policy issue.
- Meta evidence is incomplete: Facebook Business Manager email plus
  ENB/HighLevel `Facebook Painting Leads` evidence exist, but Meta dashboard
  account IDs/campaigns/pixels/billing are not verified.

## Evidence Classes

Do not mix these up:

- Provider dashboard/API export: account-control evidence.
- Gmail/Drive reports and policy emails: support evidence.
- Public ad libraries: public visibility evidence.
- Local repo/site scans: implementation evidence.
- ENB/HighLevel emails: dependency evidence.

Only provider dashboard/API export can prove current users, partners, billing,
active campaigns, pixels, datasets, lead forms, and conversion setup.

## Google Ads Control Pass

Start in the dashboard, with GL already logged in or available for MFA.

1. Confirm the selected account is `Locally Twisted` / `437-723-0551`.
2. Export or screenshot `Tools > Admin > Access and security`.
3. Record every user, invitation, access level, 2FA state, and manager link.
4. Record manager accounts, especially ENB manager ID `124-663-1239`.
5. Export campaigns, ad groups, ads, assets, asset groups, keywords, search
   terms, audiences, locations, budgets, bidding, experiments, policy issues,
   change history, and recommendations.
6. Inspect billing profile, payment method, unpaid balance, invoicing, and
   account ownership before changing access.
7. Inspect conversions, Google tag, GTM, GA4 links, enhanced conversions,
   remarketing, call assets, call recording, lead-form assets, offline
   conversions, and linked accounts.
8. For the known 404 policy issue, export final URLs before repairing or
   pausing anything.

## Meta Business Control Pass

Start in Meta Business Settings, not Ads Manager alone.

1. Confirm the Business Manager ID and owner.
2. Export or screenshot people, partners, Pages, Instagram accounts, ad
   accounts, pixels/datasets, domains, apps, lead forms, billing, payment
   methods, connected CRMs, and system users.
3. Record ENB/agency partner access before changing it.
4. Export all active and inactive campaigns, ad sets, ads, creatives, lead
   forms, audiences, custom conversions, and event sources.
5. Determine whether `Facebook Painting Leads` is a Meta native lead form,
   HighLevel integration, or both.

## Dependency Pass

Before removing ENB or partner access:

- Export HighLevel/ENB lead pipelines and lead routing.
- Confirm ownership and forwarding of tracking number `(801) 784-3426`.
- Confirm active landing pages, tracking templates, UTM templates, and final
  URLs.
- Identify ads that point to ENB-owned pages, HighLevel forms, old WordPress
  URLs, or paths that now 404 on the Frappe site.

## Mutation Rules

- Read-only exports first.
- No access removal until billing, tracking, and lead capture dependencies are
  known.
- No campaign pause/enable/delete/budget mutation without GL business approval,
  unless GL explicitly tells the agent to stop spend.
- No pixel/tag/conversion replacement until the new Frappe-owned measurement
  path is proven.
- No Meta partner removal until Pages, Instagram, ad accounts, pixels,
  datasets, lead forms, domains, and payment methods are owned or recoverable.

## Failure Modes

- Treating Gmail policy emails as a Google Ads account crawl.
- Treating ENB reports as dashboard export.
- Treating public ad-library lookup as account control.
- Giving GL a dashboard checklist after GL has already opened the account page.
- Removing ENB access before exporting lead routing, tracking phone numbers,
  billing, tags, pixels, and landing-page dependencies.

## Verification Output

The next complete pass should leave:

- A dashboard-derived user/partner access table.
- A campaign/ad inventory with current status and final URLs.
- A billing/payment ownership note.
- A tracking/conversion/pixel inventory.
- A lead-routing dependency map.
- A list of actions needing GL approval.

## Cross-Links

- Active handoff: `workstreams/ad-account-takeover-2026-05-19.md`
- Failure recipe:
  `capabilities/failures/ad-dashboard-research-vs-control-drift.md`
- Related process failure:
  `capabilities/failures/provider-dashboard-work-bounced-to-gl.md`
