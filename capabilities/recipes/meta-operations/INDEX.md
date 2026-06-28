---
name: Meta operations supervised ownership
level: recipe-family
maturity: candidate
verification_level: local-api-read-only
last_verified: 2026-06-28
currently_true: true
---

# Meta Operations Supervised Ownership

## What It Does

Gives Locally Twisted a supervised operating framework for Facebook and
Instagram work: paid ads, organic posts, comments, direct messages, lead forms,
measurement, account governance, and approval evidence.

This is intentionally broad. GL remains the human approver. Broad API and
Business access is treated as operating capacity, not permission for unattended
spend, customer communication, access changes, or data export.

## Verified State

Verified read-only through `scripts/verify/meta_operations_inventory.py` on
2026-06-28:

- Meta app: `Locally Twisted API`, app ID `1924409031609353`.
- Token type: `SYSTEM_USER`; token is stored outside Git in `.env`.
- Business: `Jeffery Kimber`, ID `1327185764080942`.
- Ad account: `act_27813262` / `27813262`, USD, America/Denver.
- Page: `Locally Twisted`, ID `110889248970340`.
- Readable inventory: 72 campaigns, 73 ad sets, 85 ads, 2 pixels, 2 system
  users, 0 custom conversions, and 0 last-7-day insight rows.
- Page posts and lead-form metadata still require a Page Access Token lane.
- ENB access was not changed.

## Operating Lanes

| Lane | What We Can Do Now | Next Connection | Approval Boundary |
|---|---|---|---|
| Governance | Read business, ad account, Page, system users, owned assets | Dashboard export for people/partners/ENB | Any access, partner, role, billing, or ENB change |
| Paid ads | Inventory/report campaigns, ad sets, ads, insights, pixels | Campaign draft and final URL review | Any campaign, budget, bid, audience, creative, status, or spend change |
| Organic social | Draft FB/IG content plans | Page Access Token and IG asset confirmation | Any post, story, reel, comment reply, or deletion |
| Messaging | Design supervised reply workflows | Page/IG messaging token proof and SOP | Reading or replying to customer messages |
| Leads | Map native Meta vs HighLevel lead paths | Page Access Token with lead permissions | Exporting leads or routing customer data |
| Measurement | Inventory pixels/custom conversions | Approved Frappe tracking and event plan | Pixel/dataset/domain/CAPI/custom conversion changes |

## Universal Rules

- ENB access stays untouched unless GL later approves a specific access action
  after dependency mapping.
- Read-only inventory and draft planning are safe defaults.
- Live writes require exact, current GL approval for the exact object and
  change.
- No customer messages, lead records, offline conversions, custom audiences, or
  customer lists are read or exported without approval for that lane.
- API tokens, app secrets, Page tokens, and OAuth artifacts are never committed,
  printed, or pasted into docs.

## Source Basis

- Local API proof: `scripts/verify/meta_operations_inventory.py`.
- Meta Marketing API: `https://developers.facebook.com/docs/marketing-api/`.
- Meta Insights API: `https://developers.facebook.com/docs/marketing-api/insights/`.
- Meta Pages API overview: `https://developers.facebook.com/docs/pages-api/overview`.
- Meta permissions reference: `https://developers.facebook.com/docs/permissions/`.
- Meta system-user token handling:
  `https://developers.facebook.com/docs/business-management-apis/system-users/install-apps-and-generate-tokens/`.

## Files In This Family

- [access-governance](access-governance.md)
- [ads-operations](ads-operations.md)
- [organic-social-operations](organic-social-operations.md)
- [messaging-and-engagement](messaging-and-engagement.md)
- [lead-routing](lead-routing.md)
- [measurement-and-assets](measurement-and-assets.md)
- [approval-and-evidence](approval-and-evidence.md)

## Revalidation

Run the inventory verifier before relying on current account state:

```bash
python scripts/verify/meta_operations_inventory.py
```

Revalidate after token rotation, app review changes, Business Manager access
changes, Page-token setup, ENB dependency changes, or any approved live Meta
mutation.
