# Staging Deployment Approval - 2026-05-29

Status: approved for Locally Twisted staging shop-discovery execution only

## Plain Meaning

Guiding Light approved moving the shop-discovery release candidate from
release-preparation into the actual staging execution path.

This approval is intentionally narrow. It lets the release controller use the
approved staging/provider path for `locallytwisted-staging.frappe.cloud`; it
does not approve live launch, live checkout, or unrelated provider/account
work.

## Approved Source

- Release-controller branch: `codex/lt-staging-release-candidate-freeze`
- Approved source branch: `codex/lt-live-shop-discovery-gate`
- Approved source behavior commit:
  `423bd044353cb7170508bbaa22ea4326afc30b2b`
- Approved app mirror branch: `live-shop-discovery-20260529`
- Approved app mirror commit:
  `cc5426401b4d3f69a57b8efb77320d943c5c95ea`
- Worktree:
  `C:\Users\baenb\agent-worktrees\builtbycameron-lt\release-candidate`
- Target site: `locallytwisted-staging.frappe.cloud`

## Approved Actions

- Use the local `.env` Frappe Cloud credential without printing secrets.
- Deploy/update only the approved shop-discovery app mirror candidate.
- Set staging shop-discovery mode with checkout paused.
- Run the Frappe Cloud staging app update/site update/migrate/cache-clear steps
  required for `locallytwisted-staging.frappe.cloud`.
- Run hosted staging verification afterward, including security,
  SEO/AEO/GEO, accessibility, shop/product, route, log/job, and no-checkout
  checks.

## Not Approved

- live checkout
- live Stripe
- DNS
- Search Console
- production data changes
- ERPNext production mutation
- email sending beyond test-mode/staging verification
- live deployment
- live checkout
- live Stripe
- DNS
- Search Console
- product/catalog mutation
- production data mutation
- ERPNext production record mutation

## Approval Text

> I approve staging deployment and verification for the Locally Twisted
> shop-discovery candidate only, using app mirror branch live-shop-
> discovery-20260529 at cc5426401b4d3f69a57b8efb77320d943c5c95ea and
> source branch codex/lt-live-shop-discovery-gate at
> 423bd044353cb7170508bbaa22ea4326afc30b2b.
>
> This approval includes setting staging to shop-discovery mode with checkout
> paused, running security, SEO/AEO/GEO, accessibility, shop/product, route,
> log/job, and no-checkout verification. This does not approve live deployment,
> live checkout, live Stripe, DNS, Search Console, product/catalog mutation,
> production data mutation, ERPNext production record mutation, or email
> sending outside staging/test-mode verification.

## Release Controller Notes

This record supersedes the earlier staging approval text for the older
`9ef89e7` candidate. The release-controller branch was fast-forwarded to the
approved shop-discovery source behavior commit before this approval record was
updated.

Before provider mutation, re-run the release-prevention gate and prove the
branch is clean. After provider mutation, prove source identity and hosted
staging behavior against the actual staging URL.
