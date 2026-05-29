# Staging Deployment Approval - 2026-05-29

Status: approved for Locally Twisted staging execution only

## Plain Meaning

Guiding Light approved moving this release candidate from release-preparation
into the actual staging execution path.

This approval is intentionally narrow. It lets the release controller use the
approved staging/provider path for `locallytwisted-staging.frappe.cloud`; it
does not approve live launch or unrelated provider/account work.

## Approved Source

- Release branch: `codex/lt-staging-release-candidate-freeze`
- Approved source-freeze commit: `9ef89e7`
- Worktree:
  `C:\Users\baenb\agent-worktrees\builtbycameron-lt\release-candidate`
- Target site: `locallytwisted-staging.frappe.cloud`

## Approved Actions

- Use the local `.env` Frappe Cloud credential without printing secrets.
- Update the Frappe app mirror from this source-freeze branch.
- Run the Frappe Cloud staging app update/site update/migrate/cache-clear steps
  required for `locallytwisted-staging.frappe.cloud`.
- Run hosted staging verification afterward.

## Not Approved

- live checkout
- live Stripe
- DNS
- Search Console
- production data changes
- ERPNext production mutation
- email sending beyond test-mode/staging verification
- live deployment

## Approval Text

> I approve staging deployment preparation and execution for branch
> codex/lt-staging-release-candidate-freeze at 9ef89e7 to Locally Twisted
> staging only.
>
> This approval includes using the local .env Frappe Cloud credential without
> printing secrets, updating the app mirror from this source-freeze branch,
> running the Frappe Cloud staging app update/site update/migrate/cache-clear
> steps required for locallytwisted-staging.frappe.cloud, and running hosted
> staging verification afterward. This does not approve live checkout, live
> Stripe, DNS, Search Console, production data changes, ERPNext production
> mutation, email sending beyond test-mode/staging verification, or live
> deployment.

## Release Controller Notes

Before provider mutation, re-run the release-prevention gate and prove the
branch is clean. After provider mutation, prove source identity and hosted
staging behavior against the actual staging URL.
