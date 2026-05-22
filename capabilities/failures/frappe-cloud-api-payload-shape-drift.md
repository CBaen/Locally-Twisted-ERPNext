---
name: Frappe Cloud API payload shape drift
type: failure
failure_kind: release_gate_gap
schema_version: 0.1
date_discovered: 2026-05-22
last_updated: 2026-05-22
status: guarded
scope: project
owner_context: Locally Twisted Frappe Cloud staging deploy and site update
related_capabilities:
  - ../recipes/frappe-cloud-cloudflare-stripe-launch-gate.md
related_failures:
  - frappe-cloud-release-site-migration-drift.md
  - provider-dashboard-work-bounced-to-gl.md
tags:
  - locally-twisted
  - frappe-cloud
  - provider-api
  - staging
  - payload-shape
  - async-jobs
  - fail-loud
---

# Failure Recipe: Frappe Cloud API Payload Shape Drift

## Symptom

Frappe Cloud accepts a deploy/update request with HTTP `200` and a `null`
response body, but the async job fails later because nested fields such as
`apps` or `sites` were submitted as strings instead of typed JSON arrays and
objects.

## Trigger Conditions

- Provider work uses the Frappe Cloud API or Press methods directly instead of
  only the dashboard.
- The API call contains nested app/site data.
- A PowerShell or form-encoded request serializes nested fields as strings.
- The response is treated as success before checking the provider job result.

## Known Instances

| Date | Project | Surface | Action being taken | Bad outcome | Evidence | Guard state | Status |
|---|---|---|---|---|---|---|---|
| 2026-05-22 | Locally Twisted | Frappe Cloud staging deploy/update | Deploy app mirror commit `f236d6d86deca0066c98e3776189b32c8818cb6d` to staging bench group `bench-40102` / bench `bench-40102-000003-f4v` while live remained on group `bench-39776` / bench `bench-39776-000015-f94v` | First `deploy_and_update` request used form-encoded nested `apps`/`sites`; the async job failed with `'str' object has no attribute 'get'`; corrected JSON deploy was attempted, but later checks still showed staging installed old hash `b4b3bf80108234c12051b572ac9b9cd4728f0efc`, `update_available=true`, site `Active`, and `0` running jobs | Parent staging-recovery check and Frappe Cloud job evidence; site update/migrate jobs `8vspcanje0` and `63lqkkrppt` failed, with recoveries succeeding | typed JSON payload and async terminal-result guard added | guarded |

## Root Pattern

Provider APIs can acknowledge request receipt without proving the provider
understood, ran, or finished the release. For Frappe Cloud nested payloads,
`application/x-www-form-urlencoded` can silently turn app/site objects into
strings that only fail after the job starts.

## Why It Seemed Reasonable At The Time

The API returned `200`, and the body did not contain an immediate error. That
looked like a successful provider action, but it was only an enqueue signal.

## Detection Signals

- Frappe Cloud deploy/update request includes nested `apps` or `sites`.
- Request uses `Content-Type: application/x-www-form-urlencoded`.
- Response is HTTP `200` with body `null`.
- Async job traceback contains `'str' object has no attribute 'get'`.
- Site shows `update_available=true` after a deploy/update attempt.
- Installed app hash remains old after the provider job appears to be done.

## Required Guard

Send nested Frappe Cloud provider payloads as `application/json` with real JSON
arrays and objects. Treat HTTP `200` plus `null` as enqueue-only. Release proof
requires the deploy candidate to reach terminal success, then the site
update/migrate job to reach terminal success, followed by cache clear,
installed hash/app order verification, site status, no running jobs, and
route/browser proof.

## Recovery Recipe

1. Stop treating the provider API response as release proof.
2. Rebuild the request body as JSON with typed nested `apps` and `sites`.
3. Submit the provider request with `Content-Type: application/json`.
4. Find the provider job created by the request.
5. Read terminal job status and traceback before continuing.
6. Run site update/migrate after the deploy candidate succeeds.
7. Clear cache only after site update/migrate success.
8. Verify installed app hash, installed app order, site status, running-job
   count, and route/browser behavior.

## What Not To Do

- Do not send nested Frappe Cloud app/site payloads as form-encoded strings.
- Do not call `200`/`null` a deploy success.
- Do not skip deploy job status because the site status is `Active`.
- Do not skip site update/migrate proof because the app mirror target exists.
- Do not move to live, DNS, Stripe, or Search Console from this evidence.

## Cross-links

- `../../workstreams/frappe-cloud-staging-owner-review-2026-05-22.md`
- `../../LT-LAUNCH-RUNBOOK.md`
- `../recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`
- `frappe-cloud-release-site-migration-drift.md`
- `provider-dashboard-work-bounced-to-gl.md`

## Evidence Quality

Documented from the 2026-05-22 staging-recovery chain and parent check. This
docs slice did not mutate provider state or reverify staging directly; it
records the guard future agents must apply before claiming staging recovery.
