# Live Indexing Release Packet - 2026-05-29

## Scope

This packet prepares a narrow Locally Twisted live discovery/indexing release.

The business goal is to make approved public business pages discoverable at
`https://locallytwisted.com` so Google and marketing campaigns stop seeing stale
or wrong public signals.

This packet does not approve live checkout, live Stripe, DNS, Search Console,
production data mutation, ERPNext record mutation, product/catalog changes,
email sending, or promotion of staged shop/checkout work.

## Current Live Proof

Read-only public probes on 2026-05-29 show the live discovery layer is still
wrong:

| Surface | Result |
|---|---|
| `https://locallytwisted.com/robots.txt` | HTTP 200, blank body |
| `https://locallytwisted.com/sitemap.xml` | HTTP 200, 29/29 `<loc>` hosts are `locallytwisted.v.frappe.cloud` |
| `https://locallytwisted.com/` | HTTP 200, canonical and `og:url` use `locallytwisted.v.frappe.cloud` |
| `https://locallytwisted.com/about` | HTTP 200, canonical and `og:url` use `locallytwisted.v.frappe.cloud` |
| `https://locallytwisted.com/contact` | HTTP 200, canonical and `og:url` use `locallytwisted.v.frappe.cloud` |
| `https://locallytwisted.com/shop` | HTTP 302 to `/ready-to-order-paused?from=%2Fshop` |

Read-only staging probes on 2026-05-29 show staging discovery uses the staging
host:

| Surface | Result |
|---|---|
| `https://locallytwisted-staging.frappe.cloud/robots.txt` | advertises `https://locallytwisted-staging.frappe.cloud/sitemap.xml` |
| `https://locallytwisted-staging.frappe.cloud/sitemap.xml` | 25/25 `<loc>` hosts are `locallytwisted-staging.frappe.cloud` |

## Source State

The durable LT source already contains the selective-indexing fix:

- `apps/locally_twisted/locally_twisted/seo.py`
- `apps/locally_twisted/locally_twisted/www/sitemap.py`
- `apps/locally_twisted/locally_twisted/www/robots.py`
- `apps/locally_twisted/locally_twisted/www/robots.txt`
- `apps/locally_twisted/locally_twisted/ecommerce_pause.py`
- `apps/locally_twisted/locally_twisted/www/ready_to_order_paused.py`
- `apps/locally_twisted/locally_twisted/templates/generators/item_group.html`
- `scripts/verify/seo_contract.spec.js`

Source checks run from the packet worktree on 2026-05-29:

```powershell
python -m py_compile apps\locally_twisted\locally_twisted\ecommerce_pause.py apps\locally_twisted\locally_twisted\seo.py apps\locally_twisted\locally_twisted\www\sitemap.py apps\locally_twisted\locally_twisted\www\robots.py apps\locally_twisted\locally_twisted\www\ready_to_order_paused.py
node --check scripts\verify\seo_contract.spec.js
```

Result: both passed.

`npm run test:seo-contract` did not run from this fresh worktree because
`node_modules` is not installed there. A live SEO contract run from the main
checkout timed out and is not counted as proof. The actual release execution
must rerun the SEO contract from a prepared tool surface.

## Recommended Candidate

Use the narrow app-mirror hotfix candidate for this indexing-only release:

| Item | Value |
|---|---|
| App mirror path | `C:\Users\baenb\agent-worktrees\builtbycameron-lt\codex-20260528-lt-live-seo-indexing-patch__app-mirror-live-hotfix` |
| Branch | `live-seo-indexing-20260528` |
| Commit | `5bbdc48 Fix live SEO indexing signals` |
| Direct commit change | 7 SEO/indexing files |

Do not deploy `C:\Users\baenb\agent-worktrees\builtbycameron-lt\app-mirror-release-20260529`
or app mirror commit `ad0a408` for this indexing-only slice. That mirror is the
larger staging candidate and carries shop/checkout staging work outside this
packet.

## Required Pre-Live Gates

These must pass before any live provider mutation:

1. Reverify the current live Frappe Cloud app/source identity on the same day as
   execution.
2. Confirm rollback target and rollback path before deploy/update.
3. Compare current live app hash to candidate `5bbdc48`.
4. Stop if the effective live deploy diff includes checkout/payment/custom
   DocType/fixture/patch scope unless Guiding Light separately approves that
   widened release.
5. Stop if the deploy diff from the reverified current live hash is broader
   than this exact packet scope, even if the branch name looks correct.
6. Confirm the release target is live `locallytwisted.com`, not staging.
7. Confirm live checkout remains paused before and after the release.

## Execution Boundary

Execution requires a separate approval sentence. Approval for this packet alone
does not approve mutation.

Allowed only after explicit approval:

- use the local Frappe Cloud credential without printing secrets;
- read-only verify current live source/app identity;
- deploy or update the live app only to the approved indexing candidate;
- run the required site update/migrate/cache-clear steps for the live site;
- run hosted live verification afterward.

Still blocked unless separately approved:

- live checkout;
- live Stripe;
- DNS changes;
- Search Console submission, URL Inspection, or removals;
- production data mutation;
- ERPNext production record mutation;
- product/catalog changes;
- email sending beyond passive verification;
- deploying the larger staging shop/checkout mirror.

## Post-Release Proof Required

After live update/cache clear, run and record:

```powershell
python scripts/verify/cloudflare_launch_readiness.py --base-url https://locallytwisted.com
$env:LT_BASE_URL='https://locallytwisted.com'
npm run test:seo-contract
```

The live release is not ready for Search Console until all are true:

- `robots.txt` is not blank and advertises
  `https://locallytwisted.com/sitemap.xml`;
- sitemap `<loc>` values use `https://locallytwisted.com`, not the Frappe Cloud
  vanity host;
- stable public business pages use `https://locallytwisted.com` canonical and
  `og:url`;
- paused ecommerce discovery stays absent from sitemap or emits noindex where
  applicable;
- `/shop` remains paused unless live checkout is separately approved.

## Witness Review

Three read-only witnesses reviewed the release shape on 2026-05-29:

| Lens | Result | Note |
|---|---|---|
| Business boundary | PASS | Use a narrow discovery/indexing packet; do not turn this into commerce launch. |
| Technical release control | PASS WITH CONCERN | Candidate `5bbdc48` is preferred, but current live app hash must be reverified before mutation. |
| Adversarial release risk | CONCERN | "App mirror" is ambiguous; packet must name the exact hotfix and block the staging mirror. |

Integrated decision: prepare the narrow indexing packet now. Do not execute live
mutation or Search Console until the pre-live gates pass and Guiding Light gives
explicit release approval.

## Approval Wording For Next Step

If Guiding Light chooses to execute this release, use this exact business-level
approval wording:

```text
I approve the Locally Twisted live public discovery/indexing release for
https://locallytwisted.com only, using app mirror
C:\Users\baenb\agent-worktrees\builtbycameron-lt\codex-20260528-lt-live-seo-indexing-patch__app-mirror-live-hotfix
branch live-seo-indexing-20260528 at commit 5bbdc48. This approval includes
using the local Frappe Cloud credential without printing secrets, re-verifying
current live source identity, deploying/updating only the approved indexing
candidate, running required live site update/migrate/cache-clear steps, and
running hosted live verification afterward. This does not approve live checkout,
live Stripe, DNS changes, Search Console submission or removals, production data
mutation, ERPNext production record mutation, product/catalog changes, email
sending, or deployment of app-mirror-release-20260529/ad0a408.
```

## Related Records

- `workstreams/domain-provider-reindex-cleanup-2026-05-19.md`
- `workstreams/selective-indexing-gate-2026-05-21.md`
- `workstreams/seo-geo-aeo-contract.md`
- `capabilities/recipes/lt-seo-geo-aeo-contract.md`
- `capabilities/failures/frappe-cloud-sitemap-public-domain-drift.md`
