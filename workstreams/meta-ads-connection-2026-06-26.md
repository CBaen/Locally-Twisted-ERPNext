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
