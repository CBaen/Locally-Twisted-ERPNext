---
name: Meta access governance
level: recipe
maturity: candidate
verification_level: local-api-read-only
last_verified: 2026-06-28
currently_true: true
---

# Meta Access Governance

## Purpose

Keep broad Facebook/Instagram access useful and supervised. Broad access is
expected for LT operations, but every account-control write remains approval
gated.

## Current Facts

- Business ID `1327185764080942` is readable by API.
- Ad account `act_27813262` is readable by API.
- Page `110889248970340` is readable as an owned Page.
- System users are visible: `ltautomation` and `locallytwistedautomation`.
- The current token is a system-user token for app `Locally Twisted API`.
- `.env` is ignored by Git and is the local secret container for the token.
- ENB access has not been changed.

## Rules

- Do not remove, downgrade, or change ENB access without a later exact GL
  approval for that specific access action.
- Do not change people, partners, roles, app permissions, system users, billing,
  payment methods, domains, pixels, datasets, Pages, Instagram accounts, or
  lead integrations without exact approval.
- Do not print access tokens, Page tokens, app secrets, OAuth codes, or raw
  authorization URLs containing secrets.
- Treat dashboard exports and API inventory as account-control evidence. Treat
  email threads, reports, or public ads libraries as support evidence only.

## Safe Work

- Read current asset inventory.
- Draft access maps.
- Identify missing token lanes.
- Prepare approval packets.
- Verify `.env` remains ignored and not staged.

## Needs Approval

- Any access, role, partner, ENB, app permission, billing, domain, Page,
  Instagram, dataset, pixel, CRM, webhook, or system-user mutation.

## Revalidation

Run:

```bash
python scripts/verify/meta_operations_inventory.py
git check-ignore -v .env
```

If either fails, stop before claiming API readiness.
