---
id: erpnext-external-marketing-access-reset
name: ERPNext External Marketing Access And Reset
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted external marketing builder/reviewer account setup and fail-loud password reset delivery
currently_true: unknown
verification_level: 3
last_verified: 2026-06-13
evidence_quality: direct
successful_uses: 1
failed_uses: 1
regressions: 0
depends_on:
  - erpnext-external-review-access
  - customer-email-delivery-branding-contract
  - fail-loud-operating-law
used_by: []
tags:
  - Locally Twisted
  - ERPNext
  - Frappe
  - external marketing
  - password reset
  - Email Queue
---

# ERPNext External Marketing Access And Reset

Use this recipe when creating, auditing, previewing, or sending account-access
reset emails for an outside marketing vendor such as Exploring Not Boring.

## Contract

External marketing access has two separate lanes:

1. **Review lane** - no-Desk `Website User` with `LT Marketing Review Access`.
2. **Builder lane** - controlled `System User` with `LT External Marketing
   Builder`, narrow Desk access, and no business-record access.

Do not turn either lane into broad Website Manager, System Manager, Item Manager,
Sales, Accounts, owner, customer, supplier, or maintenance access.

## Builder Boundary

`LT External Marketing Builder` may work only inside the source-controlled
marketing lane:

- landing/campaign Web Pages under `/campaigns/`, `/landing/`, or `/marketing/`;
- `LT Marketing Tracking Settings`;
- explicitly allowed review/edit surfaces for product-page marketing copy only
  where the guard permits it.

Denied surfaces include Leads, Customers, Contacts, Addresses, Quotes, Sales
Orders, Sales Invoices, Payment Requests, Payment Entries, Communications, Email
Queue, Files, Items, Item Prices, Website Settings, Webshop Settings, logs,
Tasks, Projects, and raw operational records.

## Reset Email Contract

Use the fail-loud helper for known operator/vendor resets. Frappe's public
password-reset endpoint intentionally hides existence/delivery failures and must
not be used as proof that a known vendor received access.

The real reset email must:

- render through the Locally Twisted branded reset copy;
- identify the `Locally Twisted website account`;
- show the exact account email;
- use a reset URL on `https://locallytwisted.com/update-password?...`;
- make clear it does not reset email, Google, Facebook, ENB, or any other login;
- sign as Locally Twisted;
- avoid Built by Cameron, `Dear Marketing`, generic `marketing access`, `Dear
  Jeff`, `Thank you, Administrator`, and generic Frappe reset wording.

Do not print or persist the token/full link.

## Implementation Surfaces

```text
apps/locally_twisted/locally_twisted/external_marketing_builder_access.py
apps/locally_twisted/locally_twisted/seed/sync_external_marketing_builder_access.py
apps/locally_twisted/locally_twisted/marketing_vendor_access.py
apps/locally_twisted/locally_twisted/marketing_access_reset.py
apps/locally_twisted/locally_twisted/password_reset_email.py
apps/locally_twisted/locally_twisted/email_delivery_guard.py
apps/locally_twisted/locally_twisted/patches/configure_password_reset_email.py
scripts/setup/sync_marketing_vendor_access.py
scripts/setup/send_marketing_access_reset.py
scripts/setup/sync_password_reset_template.py
scripts/verify/external_marketing_builder_access_contract.py
```

## Safe Command Order

```powershell
npm run test:external-marketing-builder-access
npm run test:password-reset-template
npm run test:marketing-access-reset
npm run preview:marketing-access-reset
```

Only after explicit approval for the exact recipient/send:

```powershell
npm run send:marketing-access-reset
```

For role/user sync when approved:

```powershell
npm run sync:marketing-vendor-builder-access
npm run sync:marketing-vendor-review-access
```

## Live Verification Pattern

For a real send, verify all of the following without exposing the token:

1. target User exists and is enabled;
2. expected mode/role/user type are present;
3. forbidden roles are absent;
4. outgoing sender/account are ready;
5. dry-run rendered contract passes;
6. real send returns `ok=true`;
7. Email Queue row reaches `Sent` with the expected recipient and sender;
8. branded body/copy contract passes from the queued row;
9. a safe unauthenticated GET of the reset page returns the password-reset page;
10. the User still has a reset key afterward if the test is supposed to be
    non-consuming.

## Known Live Receipt

2026-06-13 live receipt:

- source commit `456c9a3`;
- app mirror branch commit `8b10a92274f1699eeb89713dff347f66a0db75f3`;
- Frappe Cloud pipeline `eutojcn0ei` succeeded;
- active bench `bench-40102-000037-f4v`;
- Email Queue `e4aqh31606` reached `Sent` for
  `marketing@exploringnotboring.com` from
  `Locally Twisted <accounting@locallytwisted.com>`;
- reset page check returned HTTP `200` and did not consume the key.

## Failure Modes

- Treating a public `/login#forgot` success message as proof the email was sent.
- Sending Frappe's generic `Password Reset` template to an external vendor.
- Allowing branded reset proof to pass only before MIME/quoted-printable encoding
  but fail after the row reaches Email Queue.
- Treating `Email Queue.status = Sent` as inbox-visible proof.
- Granting broad website/admin roles because a marketing vendor needs page work.
- Printing, saving, or committing the real reset token/link.
- Re-sending a reset email only to prove a previous successful send.

## Recovery

If the helper fails before delivery, preserve the loud failure report, fix the
contract/role/sender/template issue, rerun dry-run readiness, and only then do
one real send if still approved. If a row is `Sent` but the recipient reports no
inbox delivery, treat that as an SMTP/inbox visibility investigation, not as
license to weaken the branding/access guards.
