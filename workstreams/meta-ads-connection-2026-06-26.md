# Meta Ads Connection Validation - 2026-06-26

## Boundary

This workstream validates how Locally Twisted can connect to Meta advertising
tools. It does not authorize account changes.

Hard stops:

- Do not remove, downgrade, or change ENB access.
- Do not change partners, people, roles, pages, Instagram accounts, domains,
  pixels, datasets, lead forms, billing, payment methods, campaigns, ad sets,
  ads, audiences, budgets, spend, OAuth permissions, or API tokens.
- Do not export customer, lead, conversion, or offline event data.
- Stop at Meta login, MFA, OAuth consent, app creation, or any permission
  dialog unless GL gives explicit approval for that exact step.

## Verified Today

- No Meta/Facebook/Instagram Ads connector is available in the installed Codex
  app tools. The visible connectors are unrelated tools such as Canva, Gmail,
  Google Calendar, and Google Drive.
- Local command/browser tooling exists: `node`, `npm`, `npx`,
  `google-chrome`, `brave-browser`, `firefox`, `gh`, and Codex CLI
  `0.142.1`.
- The Playwright CLI wrapper works from this machine:
  `/home/guidingl/.codex/skills/playwright/scripts/playwright_cli.sh`.
- Wardenclyffe has no visible `$DISPLAY` in this shell, so normal headed
  Playwright did not open a user-visible window from the Codex process.
- Headless Playwright opened `https://business.facebook.com/settings` and Meta
  redirected to the Meta Business login page.
- Clicking `Continue with Facebook` opened the normal Facebook login page with
  email/mobile and password fields. No credentials were entered.
- No authenticated Meta Business session was available inside the Playwright
  session.

## Best Control Path

1. Use browser automation for the first dashboard control pass.
   Meta Business Settings is the source of truth for business ID, owner,
   people, partners, Pages, Instagram accounts, ad accounts, pixels/datasets,
   domains, apps, lead forms, billing, payment methods, CRMs, and system users.
2. After dashboard access is proven, add API access for repeatable read-only
   inventory and reporting. The official Meta path is the Marketing API /
   Business SDK with a registered Meta app, a user access token, and the
   required permissions. Permissions such as `ads_read`, `ads_management`,
   `business_management`, and `leads_retrieval` are approval-sensitive and must
   not be connected casually.
3. Keep local Frappe tracking changes separate. The LT site already has a
   disabled-by-default marketing measurement bridge; no Meta pixel should be
   activated until dashboard ownership and approval are clear.

## Repo Tool Added

`scripts/verify/meta_ads_connection_probe.py` is a read-only Graph API
connection probe for later use after a token exists.

Safe dry run:

```bash
python scripts/verify/meta_ads_connection_probe.py --dry-run
```

Token-backed validation, only when GL approves the token/OAuth step:

```bash
META_ACCESS_TOKEN="<set in shell only>" \
  python scripts/verify/meta_ads_connection_probe.py --include-businesses
```

The script performs only GET requests. It does not store tokens and does not
write to Meta.

## 2026-06-26 Still Unverified - Superseded In Part

This list was true before GL created the app and added the system-user token.
The 2026-06-28 API inventory below supersedes the business, ad account, Page,
pixel, system-user, and campaign-count parts of this list. Keep the remaining
dependency questions until the Page-token, dashboard, lead-routing, billing,
and ENB/HighLevel mapping lanes are completed.

- Meta Business Manager ID and owner.
- Current Meta ad account ID.
- Current users, partners, and ENB/agency access.
- Pages and Instagram account connection state.
- Pixel/dataset/domain/app ownership.
- Lead forms and whether `Facebook Painting Leads` is Meta native, HighLevel,
  or both.
- Billing/payment ownership.
- Campaign/ad set/ad inventory, final URLs, and current status.

## 2026-06-26 Next Safe Step - Superseded In Part

This was the right next step before token-backed API inventory existed. The
current next safe steps are in the 2026-06-28 update below.

## 2026-06-28 Broad Supervised Meta Ownership Update

GL confirmed the intent: LT should have broad supervised operating capability
across Facebook and Instagram, including ads, posting, replies, leads, and
measurement. GL remains the human approver. Broad access is not unsupervised
access.

Hard boundary carried forward:

- ENB access is not to be removed, downgraded, or changed.
- No campaign, spend, billing, post, message, lead, pixel, dataset, customer
  data, or partner/access change is approved by this inventory.
- No token or secret is to be printed or committed.

Read-only API inventory is now working through:

```bash
python scripts/verify/meta_operations_inventory.py
```

Verified by API on 2026-06-28:

- Token is valid for app `Locally Twisted API`, app ID `1924409031609353`.
- Token type is `SYSTEM_USER`.
- Business ID `1327185764080942` reads as `Jeffery Kimber`.
- Ad account `act_27813262` / `27813262` is readable, USD,
  America/Denver.
- Page `Locally Twisted`, ID `110889248970340`, is visible as an owned Page.
- Readable ad inventory: 72 campaigns, 73 ad sets, 85 ads.
- Readable measurement inventory: 2 pixels, 0 custom conversions.
- Readable system users: `ltautomation` and `locallytwistedautomation`.
- Last-7-day insights endpoint is accessible but returned 0 rows.

Still open, not a campaign blocker:

- Page post and lead-form endpoints require the Page Access Token lane.
- Lead record export remains blocked until separately approved.
- Customer message reading/replies remain blocked until separately approved.

New capability framework:

- `capabilities/recipes/meta-operations/INDEX.md`
- `capabilities/recipes/meta-operations/access-governance.md`
- `capabilities/recipes/meta-operations/ads-operations.md`
- `capabilities/recipes/meta-operations/organic-social-operations.md`
- `capabilities/recipes/meta-operations/messaging-and-engagement.md`
- `capabilities/recipes/meta-operations/lead-routing.md`
- `capabilities/recipes/meta-operations/measurement-and-assets.md`
- `capabilities/recipes/meta-operations/approval-and-evidence.md`

Next safe steps:

1. Complete Page Access Token setup for Page posts, Page/IG engagement, and
   lead-form metadata checks.
2. Build a read-only Page-token verifier before any publishing, messaging, or
   lead-record retrieval.
3. Use the paid-ads lane for campaign planning: inventory, draft brief,
   approval packet, then only approved live changes.

## 2026-06-28 Meta Pixel Source Support

Source support for direct Meta Pixel loading now exists in
`lt-marketing-measurement.js`. It remains disabled by default because the
public tracking config still has a blank `meta_pixel_id` unless a System
Manager or approved marketing operator configures it.

Guardrails:

- The Pixel ID is not hard-coded in source.
- The browser loader only runs after
  `window.LT_COOKIE_CONSENT.hasAcceptedOptional()` returns true.
- The default site state does not activate Meta Pixel, create custom
  conversions, send Conversions API events, upload offline events, or change
  Meta provider state.
- Recommended Pixel candidate from read-only API inventory is
  `1079085392230103` (`locally twisted`), because it is owned by business
  `1327185764080942` and last fired in 2026. The older Shopify-named Pixel
  `149178523772697` last fired in 2021 and should not be used without a
  separate reason.
- Live activation still needs exact GL approval for the Pixel ID, target
  environment, release path, and post-change Events Manager proof.

Local source proof:

```bash
python scripts/verify/marketing_measurement_bridge_contract.py
node --check apps/locally_twisted/locally_twisted/public/js/lt-marketing-measurement.js
python -m py_compile scripts/verify/marketing_measurement_bridge_contract.py
```

Activation approval packet:

```text
Platform: Meta / Locally Twisted website
Object: Meta Pixel `1079085392230103` (`locally twisted`)
Current state: Pixel is owned by Business `1327185764080942`, source support
  exists, public config remains blank by default, and no custom conversions
  exist.
Proposed change: configure `LT Marketing Tracking Settings.meta_pixel_id` to
  `1079085392230103` on the approved target site, release the source support,
  accept optional tracking consent in a test browser, and verify PageView in
  Meta Events Manager.
Business reason: measure Meta ad traffic on the Frappe-owned LT site before
  drafting or relaunching campaigns.
Data touched: browser PageView event after optional consent; no lead records,
  customer lists, offline events, messages, or CAPI payloads in this step.
Spend/billing impact: none.
Customer-visible impact: cookie/tracking consent banner already discloses
  advertising and marketing measurement.
Rollback: clear `meta_pixel_id`, redeploy/reload, and verify no
  `connect.facebook.net/en_US/fbevents.js` request after consent.
Exact approval needed: "Approve configuring LT Meta Pixel `1079085392230103`
  for Locally Twisted PageView tracking on the approved site."
```

## 2026-06-28 Paid Ads Starting Point

The API connection gives enough control surface to start supervised paid-ads
work, but the account should be treated as a cleanup-and-rebuild lane before
new spend decisions. Read-only inspection found 72 campaigns, 73 ad sets, 85
ads, 0 custom conversions, and no insight rows for today, yesterday, last 7
days, last 14 days, last 30 days, or last 90 days.

Status snapshot from read-only inspection:

- Campaigns: 70 active, 2 paused.
- Ad sets: 58 active, 8 paused, 5 with issues, 2 campaign-paused.
- Ads: 50 active, 9 paused, 10 disapproved, 8 with issues, 6 ad-set-paused,
  2 campaign-paused.
- Sample final URL hosts include `locallytwisted.com`,
  `www.locallytwisted.com`, and `www.facebook.com`; several examples use older
  URLs such as `/products/adopt-a-grandma`.

First ads work packets:

1. Current-account cleanup brief: identify active objects, issue/disapproval
   causes, old final URLs, and anything that should be paused, archived, or
   rebuilt after GL approval.
2. Measurement brief: activate the preferred Pixel only after approval, then
   define event names and any custom conversions before campaign launch.
3. Campaign brief: draft offer, audience, creative, landing page, budget,
   tracking, and verification plan before creating or editing campaigns.
4. Page-token lane: add read-only Page-token proof for Page posts, lead-form
   metadata, and engagement workflows; do not read messages or export lead
   records without separate approval.

No live paid-ads mutation is approved by this document.
