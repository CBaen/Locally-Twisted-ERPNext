# 2026-06-28 - Meta Operations Uses Broad Supervised Access With Lane Gates

## Decision

Locally Twisted should use broad supervised Meta/Facebook/Instagram operating
access where it is needed for the business: ads, organic posting, customer
replies, lead handling, reporting, measurement, and account governance. GL
remains the human approver. Broad access is operating capacity, not unattended
permission to spend money, publish content, read customer conversations, export
leads, change access, or mutate account assets.

## Reasoning

GL explicitly corrected the framing during the Meta API setup: the goal is not
to minimize the assistant's access or treat broad access as suspicious. LT/BBC
is now expected to own Facebook and Instagram operations across multiple
surfaces. The disagreement was about supervision, not capability breadth.

Official Meta surfaces also separate token lanes. The current system-user token
can support ad-account inventory and ads-side reporting. Page posts, Page/IG
engagement, and lead-form metadata require Page-token handling. That Page-token
blocker is not a campaign-inventory blocker and should not be described as
"still blocked" for all Meta work.

## Implementation Boundary

Implemented in this slice:

- Added supervised Meta operations capability family under
  `capabilities/recipes/meta-operations/`.
- Added read-only verifier `scripts/verify/meta_operations_inventory.py`.
- Registered manual external-provider verifier bundle
  `lt-meta-operations-readonly-inventory` in `verifier-manifest.json`.
- Updated `workstreams/meta-ads-connection-2026-06-26.md`,
  `CODING-HANDOFF.md`, and `locally-twisted-queue.md`.

Not implemented or approved in this slice:

- No ENB access change.
- No campaign, ad set, ad, budget, bid, billing, payment, audience, creative,
  final URL, post, comment, message, lead, pixel, dataset, domain, custom
  conversion, webhook, CRM, or customer-data mutation.
- No customer messages read.
- No lead records exported.
- No Frappe Cloud, staging, live-site, DNS, Stripe, or ERPNext production
  mutation.

## Verified State

Read-only Graph API proof on 2026-06-28:

- App: `Locally Twisted API`, app ID `1924409031609353`.
- Token type: `SYSTEM_USER`.
- Business: `1327185764080942` / `Jeffery Kimber`.
- Ad account: `act_27813262` / `27813262`, USD, America/Denver.
- Page: `110889248970340` / `Locally Twisted`.
- Readable assets: 72 campaigns, 73 ad sets, 85 ads, 2 pixels, 2 system users,
  0 custom conversions.
- Last-7-day insights endpoint is accessible and returned 0 rows.
- Page post and lead-form metadata calls still require the Page Access Token
  lane.

## Guard

Future Meta work must choose the lane first:

- Ads: inventory, draft, approval packet, then exact approved mutation only.
- Organic social: Page-token verifier before publishing or scheduling.
- Messaging: explicit customer-message approval before reading or replying.
- Leads: metadata-only verifier before any lead-record export or routing.
- Measurement: Frappe/Meta event plan before pixel, dataset, CAPI, custom
  conversion, or offline event changes.
- Governance: no ENB, people, partner, billing, app, Page, Instagram, system
  user, or asset-access mutation without exact approval.

## Receipts

- `workstreams/meta-ads-connection-2026-06-26.md`
- `capabilities/recipes/meta-operations/INDEX.md`
- `scripts/verify/meta_operations_inventory.py`
- `verifier-manifest.json` bundle `lt-meta-operations-readonly-inventory`

## Decided By

Guiding Light approved broad supervised operating capability and corrected the
access framing on 2026-06-28. Codex implemented the read-only verifier,
capability family, and handoff updates.
