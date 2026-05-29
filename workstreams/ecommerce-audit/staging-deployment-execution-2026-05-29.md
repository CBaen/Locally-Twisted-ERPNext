# Staging Deployment Execution - 2026-05-29

Status: staging push executed; hosted public/customer proof passed with one
reusable Desk-credential note

## Plain Meaning

The approved release candidate was pushed through the Locally Twisted staging
path. The staging URL is now attached to the new Frappe Cloud bench running the
new `locally_twisted` app mirror commit.

This is staging-only proof. It does not approve live checkout, live Stripe,
DNS, Search Console, production data changes, ERPNext production mutation, or
live deployment.

## Approved Release Source

- Release branch: `codex/lt-staging-release-candidate-freeze`
- Approval artifact commit: `1374fc3`
- App source exported from: `apps/locally_twisted`
- App mirror repo: `CBaen/Locally-Twisted-Frappe-App`
- App mirror commit deployed: `ad0a408c2df5ecb711062f35887b94520220b2c8`
- App mirror commit message:
  `Sync staging app mirror from release candidate press-deploy-bench-40102`

The mirror sync removed 11 stale generated public-image/manifest artifacts that
existed in the app mirror but not in the release-candidate app source. No code
references to those removed files were found, and hosted asset integrity passed
after deployment.

## Provider Actions

- Frappe Cloud API account context: `locallytwisted@gmail.com`
- Release group: `bench-40102`
- Frappe Cloud deploy/update request returned: `1vfb1b729k`
- Deploy candidate: `8u9qkscvih`, `Success`
- New bench: `bench-40102-000027-f4-virginia`
- New bench deployed on: `2026-05-29 11:10:44.557117`
- Site update id: `14u0a7dnmm`
- Site moved to: `bench-40102-000027-f4-virginia`
- Frappe Cloud installed app proof:
  `locally_twisted` branch `main`, repo `CBaen/Locally-Twisted-Frappe-App`,
  hash `ad0a408c2df5ecb711062f35887b94520220b2c8`
- `last_migrate_failed`: `false`
- Frappe Cloud cache clear: HTTP `200`

## Hosted Verification

Run against `https://locallytwisted-staging.frappe.cloud`:

- `frappe.ping`: `pong`
- `/shop`: HTTP `200`
- `python scripts\verify\payment_launch_readiness.py --base-url https://locallytwisted-staging.frappe.cloud`:
  `PASS`
- `python scripts\verify\public_asset_integrity.py --base-url https://locallytwisted-staging.frappe.cloud`:
  `PASS`, 31 routes, 315 unique local asset URLs
- `LT_BASE_URL=https://locallytwisted-staging.frappe.cloud npm run test:checkout-experience`:
  `PASS`, 4/4
- `LT_BASE_URL=https://locallytwisted-staging.frappe.cloud npm run test:product-gallery-experience`:
  `PASS`, 4/4
- `LT_BASE_URL=https://locallytwisted-staging.frappe.cloud npm run test:search-contract`:
  `PASS`, 4/4

## Desk Verification Note

`npm run test:public-network` passed 39/40 hosted checks. The only failing
check was the logged-in Desk session because this worktree did not have valid
`LT_DESK_TEST_USER` / `LT_DESK_TEST_PASSWORD`, and the verifier's fallback
`Administrator` / `admin` was rejected by staging.

The logged-in session/CSRF path was then proved with a Frappe Cloud provider
session without printing the session token:

- provider session source: `press.api.site.login`
- verified site user: `Administrator`
- route checked: `/app` then `/shop-items/arches`
- result: `[DESK CSRF SESSION PROOF] PASS`

Plain meaning: the public/customer staging surface passed. The reusable Desk
test-credential setup still needs cleanup so future agents can rerun
`npm run test:public-network` without a one-off provider session.

## Current Boundary

This execution completes the staging push. It does not approve:

- live checkout
- live Stripe
- DNS
- Search Console
- production data changes
- ERPNext production mutation
- live deployment

## Next Safe Step

Use this staging site for owner/customer-path review and keep the Desk
credential cleanup as a separate small follow-up, not as a reason to rerun the
staging deploy.
