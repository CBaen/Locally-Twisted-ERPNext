---
name: Frappe password reset silent/generic drift
type: failure
failure_kind: recurring_pattern
schema_version: 0.1
date_discovered: 2026-06-13
last_updated: 2026-06-13
status: guarded
scope: project
owner_context: Locally Twisted external marketing/vendor account reset delivery
related_capabilities:
  - ../recipes/erpnext-external-marketing-access-reset.md
  - ../recipes/customer-email-delivery-branding-contract.md
  - ../recipes/fail-loud-operating-law.md
related_failures:
  - public-form-stale-email-queue-idempotency.md
  - frappe-cloud-staging-email-scheduler-stale.md
tags:
  - locally-twisted
  - frappe
  - password-reset
  - email-queue
  - external-access
  - fail-loud
---

# Failure Recipe: Frappe Password Reset Silent/Generic Drift

## Symptom

An operator tries to send a real password reset to a known external account, but
the workflow either:

- appears to succeed from the public forgot-password UI while no verified email
  is delivered; or
- produces Frappe's generic `Password Reset` copy instead of a client-specific
  Locally Twisted reset email.

## Trigger Conditions

- Using the public reset endpoint as an operator proof path.
- Trusting a UI success message instead of User/Email Queue evidence.
- Letting Frappe's default reset template or `reset_password(send_email=True)`
  generate the email.
- Checking only unencoded preview HTML while Email Queue stores MIME or
  quoted-printable encoded content.
- Treating a generic reset subject/body as acceptable because the link itself is
  technically valid.

## Known Instances

| Date | Project | Surface | Bad outcome | Evidence | Guard state | Status |
|---|---|---|---|---|---|---|
| 2026-06-13 | Locally Twisted | ENB marketing account reset | First real send attempt was blocked before delivery because Frappe tried to create/queue a generic reset path; earlier public forgot-password attempts had been silent/no-op from an operator perspective | Live helper dry-run/send reports, Email Queue guard, source commit `456c9a3`, app commit `8b10a92`, final queue `e4aqh31606` Sent | Fail-loud helper, branded reset template, generic guard with MIME/quoted-printable decoding, dry-run/preview/send wrappers | guarded |

## Root Pattern

Public account-reset UX optimizes for account enumeration safety, not operator
certainty. That is correct for strangers, but wrong for a known account-access
handoff where the operator needs proof that the exact vendor account received a
specific branded reset email.

Email Queue proof also has layers: rendered template, queued MIME content,
queue status, SMTP acceptance, recipient inbox visibility, and token validity are
not the same thing.

## Detection Signals

- Public `/login#forgot` returns success but no current Email Queue row is found.
- Subject is only `Password Reset` after removing any site prefix.
- Body contains `Dear Jeff`, `Thank you, Administrator`, `Please click on the
  following link to set your new password`, `Built by Cameron`, `Dear
  Marketing`, or generic `marketing access` language.
- Body does not show the target account email.
- Body does not identify the Locally Twisted website account.
- Reset link host is not `https://locallytwisted.com`.
- Guard checks pass on raw preview HTML but fail on queued encoded content.

## Required Guard

Use the fail-loud operator helper:

```powershell
npm run test:marketing-access-reset
npm run preview:marketing-access-reset
npm run send:marketing-access-reset
```

For template-only changes:

```powershell
npm run test:password-reset-template
```

The guard must decode/check queued content after MIME and quoted-printable
encoding, not only the pre-send template preview.

## Recovery Recipe

1. Do not keep clicking public forgot-password as a proof path.
2. Confirm the User, role, and user type match the intended access lane.
3. Run the no-send readiness helper.
4. Confirm sender/outgoing Email Account readiness.
5. Confirm branded reset template is active in System Settings.
6. Confirm the generic Email Queue guard blocks Frappe's default reset copy.
7. Send exactly once after approval.
8. Verify the resulting Email Queue row status/recipient/sender/copy contract.
9. If needed, fetch the reset page without cookies and without changing the
   password, then confirm the key still exists afterward.

## What Not To Do

- Do not report success from the UI message alone.
- Do not paste or commit the reset token/full URL.
- Do not weaken the generic-email guard to get a send through.
- Do not send a second reset just to prove the first verified Email Queue row.
- Do not treat Email Queue `Sent` as inbox-visible delivery proof.
- Do not grant broad admin/website roles to bypass a reset or access-boundary
  problem.

## Cross-Links

- `../../workstreams/external-marketing-builder-access-reset-2026-06-13.md`
- `../recipes/erpnext-external-marketing-access-reset.md`
- `../recipes/customer-email-delivery-branding-contract.md`
- `../recipes/fail-loud-operating-law.md`

## Evidence Quality

Direct live evidence for the Locally Twisted ENB account reset. Inbox-visible
receipt was not independently inspected; ERPNext proved queued SMTP acceptance
and reset-page validity without exposing or consuming the token.
