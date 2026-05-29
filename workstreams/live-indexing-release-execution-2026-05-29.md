# Live Indexing Release Execution - 2026-05-29

## Decision

Status: `NO-GO - stopped before live mutation`.

Guiding Light approved a narrow live public discovery/indexing release for
`https://locallytwisted.com` using app mirror branch
`live-seo-indexing-20260528` at commit
`5bbdc484d86729c4f2afdf7776e9f6649b02c080`.

The approved code was not deployed because the live Frappe Cloud bench does not
currently expose that exact commit as the deployable next release.

## What Was Verified

Approved app mirror:

- Path:
  `C:\Users\baenb\agent-worktrees\builtbycameron-lt\codex-20260528-lt-live-seo-indexing-patch__app-mirror-live-hotfix`
- Branch: `live-seo-indexing-20260528`
- HEAD: `5bbdc484d86729c4f2afdf7776e9f6649b02c080`
- Git state: clean

Live Frappe Cloud site:

- Public target: `https://locallytwisted.com`
- Frappe Cloud site object: `locallytwisted.v.frappe.cloud`
- Site status: `Active`
- Server: `f94-virginia.frappe.cloud`
- Release group: `bench-39776`
- Bench: `bench-39776-000015-f94v`
- Team: `5b8acl3gba`
- Running jobs: `0`

Current live `locally_twisted` app:

- Repository: `CBaen/Locally-Twisted-Frappe-App`
- Current branch: `main`
- Current hash: `b4b3bf80108234c12051b572ac9b9cd4728f0efc`
- Current release: `1m4hv2gag4`
- Rollback target before any mutation: current live hash/release above

Approved candidate diff from current live hash:

```text
M	locally_twisted/ecommerce_pause.py
M	locally_twisted/seo.py
M	locally_twisted/templates/generators/item_group.html
M	locally_twisted/www/ready_to_order_paused.py
A	locally_twisted/www/robots.py
A	locally_twisted/www/robots.txt
M	locally_twisted/www/sitemap.py
```

This diff is narrow and matches the indexing-only packet scope.

## Blocker

Frappe Cloud live deploy information for `bench-39776` shows the next available
`locally_twisted` release as:

- Next release: `bu86t39ov3`
- Next release hash: `ad0a408c2df5ecb711062f35887b94520220b2c8`

That is the larger staging candidate explicitly blocked by the approval.

The approved hotfix commit
`5bbdc484d86729c4f2afdf7776e9f6649b02c080` was not present as an available
release for the live bench. Deploying through the current available update path
would have promoted the wrong source.

## Boundary Kept

No live deploy/update was run.

No DNS, Search Console, checkout, Stripe, product/catalog, production data,
ERPNext production record, or email mutation was performed.

Local Frappe Cloud credentials were used only for read-only provider proof and
were not printed.

## Evidence Artifacts

Committed evidence summary:

- `workstreams/live-indexing-release-provider-proof-2026-05-29.json`

Temporary raw provider snapshots were used to build the summary and were not
needed as source-history artifacts. They contained sanitized provider responses
and no credential values.

## Next Safe Step

Create a deployable live hotfix release whose Frappe Cloud deploy information
proves `locally_twisted` next release hash is exactly
`5bbdc484d86729c4f2afdf7776e9f6649b02c080`, then repeat the pre-live gate.

Do not deploy the current live bench next release while it points to
`ad0a408c2df5ecb711062f35887b94520220b2c8`.

## Provider Source Correction Attempt

Guiding Light approved changing the live Frappe Cloud app source for
`locally_twisted` on `bench-39776` from `main` to
`live-seo-indexing-20260528` only to make approved commit
`5bbdc484d86729c4f2afdf7776e9f6649b02c080` deployable.

First API call result:

- Method: `press.api.bench.change_branch`
- Intended change: `main` -> `live-seo-indexing-20260528`
- Result: `308 Permanent Redirect`
- Provider state after poll: unchanged; live branch remained `main`
- Live next release remained blocked hash
  `ad0a408c2df5ecb711062f35887b94520220b2c8`
- Live deploy/update was not run

Guard before any corrected provider call:

- Use the slash-safe API method URL form for the corrected call.
- Re-read Frappe Cloud branch list or source state first.
- After source correction, deploy only if live deploy information proves
  `next_hash == 5bbdc484d86729c4f2afdf7776e9f6649b02c080`.
- Stop before live deployment if the next release remains `ad0a408` or any
  other hash.

Corrected API call result:

- Read-only branch list passed; `live-seo-indexing-20260528` is visible to
  Frappe Cloud.
- Corrected `press.api.bench.change_branch` call still returned
  `308 Permanent Redirect`.
- Provider state after polling remained unchanged:
  - branch: `main`
  - current hash: `b4b3bf80108234c12051b572ac9b9cd4728f0efc`
  - next release: `bu86t39ov3`
  - next hash: `ad0a408c2df5ecb711062f35887b94520220b2c8`
- Live deploy/update was not run.

Provider mutation is now stopped after two related API failures. The next
release-control plan needs a different execution path, such as provider UI
automation with visible source proof or a verified alternate API endpoint,
before attempting another source correction.

## Redirect-Aware Recovery And Live Deployment

Redirect root cause:

- `frappecloud.com` returned `308 Permanent Redirect` to `cloud.frappe.io` for
  API method calls.
- Read-only GET calls tolerated that redirect, but POST source-correction calls
  did not.

Recovery steps:

1. Called `press.api.bench.change_branch` directly on `cloud.frappe.io`.
2. Source correction returned HTTP `200`.
3. `locally_twisted` disappeared from deploy information until Frappe Cloud
   created a release for the new branch source.
4. Called `press.api.bench.fetch_latest_app_update`.
5. Frappe Cloud then proved:
   - branch: `live-seo-indexing-20260528`
   - next release: `1mh0jab7pc`
   - next hash:
     `5bbdc484d86729c4f2afdf7776e9f6649b02c080`
6. Ran `press.api.bench.deploy_and_update` for `locally_twisted` only.
7. Deploy response: `emuqqk2m1j`.

Final provider state:

- Site: `locallytwisted.v.frappe.cloud`
- Release group: `bench-39776`
- Bench: `bench-39776-000015-f94v`
- App: `locally_twisted`
- Installed branch: `live-seo-indexing-20260528`
- Installed hash:
  `5bbdc484d86729c4f2afdf7776e9f6649b02c080`
- Deploy status: no candidate, no deploy in progress, not validating
- Running jobs: `0`

## Hosted Live Verification

Direct public probes after deploy:

| Surface | Result |
|---|---|
| `https://locallytwisted.com/robots.txt` | HTTP 200; advertises `https://locallytwisted.com/sitemap.xml` |
| `https://locallytwisted.com/sitemap.xml` | HTTP 200; 14/14 `<loc>` values use `https://locallytwisted.com`; 0 Frappe vanity URLs |
| `/` | HTTP 200; canonical and `og:url` use `https://locallytwisted.com/`; robots `index, follow` |
| `/about` | HTTP 200; canonical and `og:url` use `https://locallytwisted.com/about`; robots `index, follow` |
| `/contact` | HTTP 200; canonical and `og:url` use `https://locallytwisted.com/contact`; robots `index, follow` |
| `/shop` | lands on `/ready-to-order-paused?from=%2Fshop`; robots `noindex, follow` |

Scripted verification:

```powershell
python scripts\verify\cloudflare_launch_readiness.py --base-url https://locallytwisted.com
$env:LT_BASE_URL='https://locallytwisted.com'; npm run test:seo-contract
```

Results:

- Cloudflare launch readiness: `PASS`, 10 checks, 0 blockers, 0 warnings.
- SEO contract: `PASS`, 13/13 tests.

## Final Decision

Status: `LIVE VERIFIED - indexing-only release`.

The live public discovery/indexing release is complete for
`https://locallytwisted.com`.

Still not approved or performed:

- live checkout;
- live Stripe;
- DNS changes;
- Search Console submission or removals;
- product/catalog changes;
- production data mutation;
- ERPNext production record mutation;
- email sending.

Follow-up: the live Frappe Cloud source now points at the hotfix branch
`live-seo-indexing-20260528`. Any later realignment back to `main` should be a
separate controlled release plan, not an incidental cleanup.
