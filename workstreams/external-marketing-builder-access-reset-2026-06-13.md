# External Marketing Builder Access And Password Reset Closeout - 2026-06-13

## Purpose

Record the live Locally Twisted / Exploring Not Boring account-access closeout
that followed the ENB replacement and marketing-access lane.

This is the source-of-truth handoff for the two client-facing asks handled in
this slice:

1. give the ENB marketing account a controlled builder lane instead of broad
   website/admin access;
2. send the actual password-reset email to `marketing@exploringnotboring.com`
   and prove it is a Locally Twisted-branded reset for the live site.

## Live Result

Status: **complete** as of 2026-06-13.

- Source repo `main`: `456c9a3 Fix branded reset email queue guard decoding`.
- Frappe app mirror live branch: `8b10a92274f1699eeb89713dff347f66a0db75f3`.
- Frappe Cloud patch pipeline: `eutojcn0ei`.
- Active bench after deploy: `bench-40102-000037-f4v`.
- Live site status after deploy: Active.
- Actual reset Email Queue row: `e4aqh31606`.
- Queue status: `Sent`.
- Recipient: `marketing@exploringnotboring.com`.
- Sender: `Locally Twisted <accounting@locallytwisted.com>`.
- Subject: `Reset your Locally Twisted website password`.

No reset token or full reset URL belongs in repo docs, handoffs, logs, or chat
summaries.

## Access Boundary Implemented

ENB/marketing access is not System Manager, Website Manager, Item Manager,
Accounts, Sales, owner, accountant, maintenance, customer, or supplier access.
The controlled builder lane is:

- Role: `LT External Marketing Builder`.
- User type: `System User`.
- Allowed Desk surface: `LT External Marketing Builder Home`.
- Allowed editing lane: landing/campaign Web Pages under `/campaigns/`,
  `/landing/`, or `/marketing/`.
- Allowed supporting settings: `LT Marketing Tracking Settings`.
- Read-only product-page marketing review is allowed through the explicit
  DocPerm/guard surface.
- Business records, pricing, variants, checkout, customers, orders, invoices,
  payments, files, Email Queue, logs, and raw Website/Webshop settings remain
  denied.

Implementation surfaces:

```text
apps/locally_twisted/locally_twisted/external_marketing_builder_access.py
apps/locally_twisted/locally_twisted/seed/sync_external_marketing_builder_access.py
apps/locally_twisted/locally_twisted/marketing_vendor_access.py
scripts/setup/sync_marketing_vendor_access.py
scripts/verify/external_marketing_builder_access_contract.py
```

Useful local commands:

```powershell
npm run test:external-marketing-builder-access
npm run sync:marketing-vendor-builder-access
```

Do not use those commands as permission to create or change a live account
without the current operator/client approval context.

## Password Reset Flow Implemented

The live reset flow is intentionally fail-loud because Frappe's public reset
endpoint can return generic success even when the operator's real goal did not
happen.

Implemented surfaces:

```text
apps/locally_twisted/locally_twisted/marketing_access_reset.py
apps/locally_twisted/locally_twisted/password_reset_email.py
apps/locally_twisted/locally_twisted/email_delivery_guard.py
apps/locally_twisted/locally_twisted/patches/configure_password_reset_email.py
scripts/setup/send_marketing_access_reset.py
scripts/setup/sync_password_reset_template.py
```

NPM wrappers:

```powershell
npm run test:marketing-access-reset
npm run preview:marketing-access-reset
npm run send:marketing-access-reset
npm run sync:password-reset-template
npm run test:password-reset-template
```

Only `send:marketing-access-reset` sends the real reset email. Dry-run/test and
preview paths must be used first unless the user/client has already approved the
specific live send.

## Email Contract

The actual live reset email must:

- address `marketing@exploringnotboring.com` directly;
- identify the account as a `Locally Twisted website account`;
- show `Account email: marketing@exploringnotboring.com`;
- link to `https://locallytwisted.com/update-password?...`;
- say the link does not reset email, Google, Facebook, ENB, or other accounts;
- sign as `Locally Twisted`;
- use sender `Locally Twisted <accounting@locallytwisted.com>`;
- avoid Built by Cameron, generic `Dear Marketing`, generic `marketing access`,
  `Dear Jeff`, `Thank you, Administrator`, and Frappe's generic password-reset
  language.

## Verification Receipts

Pre-send readiness checks confirmed:

- the target user existed;
- mode was `builder`;
- expected role was `LT External Marketing Builder`;
- expected user type was `System User`;
- outgoing email account/sender were ready;
- reset link host matched `https://locallytwisted.com`;
- rendered copy passed the branded account contract;
- generic fallback reset copy was blocked.

Live send proof:

- actual send returned `ok=true`;
- Email Queue row `e4aqh31606` reached `Sent`;
- independent readback confirmed row status and recipient state;
- a safe, non-consuming page check fetched the reset page and got HTTP `200`;
- the reset page exposed password-reset context/fields;
- the user's reset key still existed after the page check, so the test did not
  consume the recipient's link.

## Failure Found And Fixed

The first real send attempt did not deliver. That was the correct failure mode:
`Email Queue.before_insert` blocked the generic/reset path before delivery.

Root cause: the guard examined the queued MIME/quoted-printable message too
literally and could not see the account email/required branded copy after the
message was encoded.

Fix: `password_reset_email.py` now builds multiple text variants from raw,
quoted-printable-decoded, and parsed MIME text/html parts before deciding whether
an email is generic or branded. This keeps the generic-email blocker active and
allows the real branded reset email through.

## Stop Rules For Future Agents

- Do not resend the reset email just to prove the old send. Verify the existing
  row/status unless ENB/Jeff/GL asks for a new reset.
- Do not print, store, paste, screenshot, or commit the reset token/full link.
- Do not click through a live reset link in a way that changes the recipient's
  password or consumes the token.
- Do not grant broad Desk/system roles to ENB or another vendor as a shortcut.
- Do not remove ENB access, mutate ad accounts, change budgets, change live
  tracking, or alter customer data from this handoff.
- Do not treat Email Queue `Sent` as inbox-visible delivery proof. It proves SMTP
  acceptance from ERPNext's perspective.

## Cross-Links

- `workstreams/enb-replacement-shop-go-live-2026-06-08.md`
- `MARKETING-REPLACEMENT-AND-SHOP-GO-LIVE-PLAN-2026-06-08.md`
- `capabilities/recipes/erpnext-external-marketing-access-reset.md`
- `capabilities/failures/frappe-password-reset-silent-generic-drift.md`
- `capabilities/recipes/customer-email-delivery-branding-contract.md`
- `capabilities/recipes/erpnext-external-review-access.md`
