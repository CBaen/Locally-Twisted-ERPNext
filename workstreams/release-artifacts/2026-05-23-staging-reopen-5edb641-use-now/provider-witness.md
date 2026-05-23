# Provider Witness

Role: prove provider and app-root mirror state before and after the approved
app mirror sync.

Target: app-root mirror state and staging provider state for the approved
`app_mirror_sync` boundary.

Evidence: `provider-snapshot.json` and
`app-mirror-freshness-before-sync.json`, then `app-mirror-freshness.json` and
`provider-snapshot-post-mirror-sync.json`.

Read-only evidence captured in this packet:

- `provider-snapshot.json`: staging site is Active, no running jobs,
  `lt_ecommerce_paused=1`, `lt_public_indexing_enabled=0`, installed app hash
  `181076c239b2d1d3d508a41ac471c71f9d2b5158`, recent update jobs successful.
- `app-mirror-freshness-before-sync.json`: app-root mirror is not fresh
  against source `5edb641de4a3f09cc6c292904fb70551c87db3df`.

Post-sync evidence captured in this packet:

- `app-mirror-sync-result.json`: app-root mirror changed from
  `181076c239b2d1d3d508a41ac471c71f9d2b5158` to
  `5dd674c5ae9d6b3cb125ecf7ba2dd2e4e65e3831`.
- `app-mirror-freshness.json`: app-root mirror is fresh against source
  `5edb641de4a3f09cc6c292904fb70551c87db3df`.
- `provider-snapshot-post-mirror-sync.json`: staging is Active, has no running
  jobs, remains paused and not indexing, and reports update available because
  the installed app hash is still
  `181076c239b2d1d3d508a41ac471c71f9d2b5158`.

Important provider truth:
the app-root mirror is now fresh, but Frappe Cloud has not deployed/updated the
staging site to that mirror hash.

Current result: **PASS** for completed app mirror sync proof; **BLOCK** for
deploy/update/bootstrap until a fresh approval artifact authorizes the next
specific action.

Deploy/update result:

- Attempt 1 was incomplete: the typed JSON payload used arrays/objects but did
  not include the full Frappe Cloud site object.
- Attempt 2 used `name`, `server`, `bench`, `skip_backups`, and
  `skip_failing_patches` from current `deploy_information.sites`.
- Provider deploy `eu92fvbhpp` reached `Success`.
- Site update job `41ftn09ocp` reached `Success`.
- `provider-snapshot-poll-6.json` proves staging installed app hash
  `5dd674c5ae9d6b3cb125ecf7ba2dd2e4e65e3831`, no running jobs, site `Active`,
  `lt_ecommerce_paused=1`, and `lt_public_indexing_enabled=0`.

Current result after deploy/update: **PASS** for staging app-hash update proof;
**NO-GO** for owner-review readiness until hosted preflight, any approved
bootstrap/import, and owner-review gates pass.
