# Frappe Cloud Staging App Deploy Closeout - 2026-05-23

Status: **staging app hash updated; owner-review remains NO-GO**.

This handoff is for peer GPT-5.5-shaped agents. It records the approved
staging-only app mirror sync and Frappe Cloud deploy/update that followed the
forensic freeze reopen approvals. It is not authority for any later mutation
after the archive commit.

## Verified State

- Source used for this attempt:
  `5edb641de4a3f09cc6c292904fb70551c87db3df`.
- App-root mirror after approved sync:
  `5dd674c5ae9d6b3cb125ecf7ba2dd2e4e65e3831`.
- Staging installed `locally_twisted` hash after approved deploy/update:
  `5dd674c5ae9d6b3cb125ecf7ba2dd2e4e65e3831`.
- Frappe Cloud deploy/release id: `eu92fvbhpp`.
- Site update job: `41ftn09ocp`, job type `Update Site Pull`, status
  `Success`.
- Site status: `Active`; running jobs: none.
- Installed app order:
  `["frappe", "erpnext", "payments", "webshop", "locally_twisted"]`.
- Staging safety flags: `lt_ecommerce_paused=1` and
  `lt_public_indexing_enabled=0`.

Evidence packet:
`workstreams/release-artifacts/2026-05-23-staging-reopen-5edb641-use-now/`.

Archive commit for the deploy evidence:
`c82c92f Archive staging deploy evidence`.

## What Was Approved And Done

GL approved exactly two staging-only mutations:

- `app_mirror_sync` from source `5edb641` for
  `locallytwisted-staging.frappe.cloud`.
- Frappe Cloud deploy/update from app mirror hash
  `5dd674c5ae9d6b3cb125ecf7ba2dd2e4e65e3831`.

Both mutations stayed inside that boundary. No live, DNS, Stripe, Search
Console, checkout unpause, bootstrap/import, manual migrate, or manual cache
clear action was performed.

## New Failure Class Found

Attempt 1 used `Content-Type: application/json` and typed arrays/objects, but
the `sites` row only contained `name`. That was still insufficient for the
Press/Frappe Cloud update path. Current Press source reads site rows using:

- `name`
- `server`
- `bench`
- `skip_backups`
- `skip_failing_patches`

The first attempt did not update staging. The packet records this as
`provider_payload_site_object_incomplete`.

Guard added in this closeout: `scripts/verify/frappe_cloud_payload_contract.py`
now rejects deploy/update payloads whose `sites[]` rows do not include the
complete provider site object. `scripts/verify/release_controller_contract.py`
now writes complete provider site objects in its valid deploy payload fixture.

## Current NO-GO Blockers

Read-only hosted bootstrap preflight now reaches the correct deployed app hash,
but returns `ok=false`. Current blockers:

- Missing Role `LT Marketing Review Access`.
- `Webshop Settings.enable_checkout=0`, expected `1` for the bootstrap
  preflight contract.
- Destructive catalog seed has no current real `backup_artifact` and no
  explicit `zero_data_proof`.

Preflight passes inside the same artifact:

- target app hash
- installed app order
- app hooks
- standard report check

Staging still has zero business catalog/owner-review rows, including
`Item=0`, `Item Price=0`, `LT Product Blueprint=0`, `Website Item=0`,
`Website Slideshow=0`, and `Website Slideshow Item=0`.

## Next Safe Step

Do not bootstrap/import yet. Do not clear cache, migrate, unpause checkout,
touch live/DNS/Stripe/Search Console, or call staging owner-review ready.

Next work should be a fresh, explicitly approved staging-only packet that
addresses the hosted preflight blockers and reruns the controller for the exact
next action. If the next action could mutate catalog data, it must provide
either a real current staging backup artifact or explicit zero-data proof before
the destructive seed path runs.

## Backlinks

- `CODING-HANDOFF.md`
- `ECOMMERCE-SHOP-HANDOFF.md`
- `LT-LAUNCH-RUNBOOK.md`
- `locally-twisted-queue.md`
- `locally-twisted-decisions.md`
- `lessons-learned.md`
- `workstreams/frappe-cloud-staging-route-map-2026-05-23.md`
- `workstreams/frappe-cloud-release-prevention-action-items-2026-05-23.md`
- `workstreams/release-artifacts/README.md`
- `capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`
- `capabilities/failures/frappe-cloud-deploy-site-object-drift.md`
