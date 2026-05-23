---
name: Provider dashboard work bounced to GL
type: failure
failure_kind: process_ownership_failure
schema_version: 0.1
date_discovered: 2026-05-12
last_updated: 2026-05-22
status: guarded
scope: project
owner_context: Locally Twisted Frappe Cloud / Cloudflare launch
related_capabilities:
  - recipes/frappe-cloud-cloudflare-stripe-launch-gate.md
  - recipes/ad-account-takeover-provider-control.md
  - recipes/codex-browser-verification-surface.md
related_failures:
  - ad-dashboard-research-vs-control-drift.md
  - frappe-cloud-api-payload-shape-drift.md
  - frappe-cloud-release-site-migration-drift.md
  - staging-proof-surface-conflation.md
tags:
  - launch
  - frappe-cloud
  - provider-api
  - cloudflare
  - browser-automation
  - agent-ownership
  - google-ads
  - meta-business
---

# Failure Recipe: Provider dashboard work bounced to GL

## Symptom

The agent reports correct provider steps but tells GL to perform them manually,
even though GL has already made the account/session available and the repo has a
documented process.

## Trigger conditions

- Frappe Cloud, Cloudflare, Stripe, DNS, hosting, or other production-provider
  work is in scope.
- Google Ads, Meta Business, Facebook Ads, Instagram Ads, or other marketing
  provider account-control work is in scope.
- The provider operation is dashboard-first or account-session dependent.
- The agent has no simple CLI and mistakes that for "human must do it."

## Known instances

| Date | Project | Surface | Action being taken | Bad outcome | Evidence | Guard state | Status |
|---|---|---|---|---|---|---|---|
| 2026-05-12 | Locally Twisted | Frappe Cloud staging launch | Custom app install/site config after GL logged in | Agent handed GL manual install/config steps instead of taking over with automation/process | Conversation, staging probe showing `locally_twisted` not installed | added | guarded |
| 2026-05-19 | Locally Twisted | Google Ads / Meta account takeover | GL supplied a Google Ads dashboard URL and wanted to see/manage the account | Agent initially substituted Gmail/Drive research inventory for dashboard control; GL corrected the goal | `workstreams/ad-account-takeover-2026-05-19.md` and `capabilities/failures/ad-dashboard-research-vs-control-drift.md` | added | guarded |
| 2026-05-22 | Locally Twisted | Frappe Cloud ecommerce staging owner review | App mirror was pushed for staging prep and provider deploy was next | Agent stopped at the abstract statement "need Frappe Cloud provider proof" before searching for the concrete provider artifacts already in repo/history | Follow-up search found app mirror `f236d6d`, bench IDs, Press dashboard/API methods, dashboard URL `https://cloud.frappe.io/dashboard/groups/bench-39776/deploys/6g85b2nqj7`, no local API token, no SSH certificate, and unauthenticated dashboard/API state as `Guest` / `403` | added | guarded |
| 2026-05-22 | Locally Twisted | Frappe Cloud staging provider API | Provider/API recovery was required for staging group `bench-40102` / bench `bench-40102-000003-f4v` while live stayed on group `bench-39776` / bench `bench-39776-000015-f94v` | API work risked being called successful from enqueue/status fragments instead of terminal deploy plus site-update proof; first form-encoded nested payload failed with `'str' object has no attribute 'get'`, then corrected JSON exposed real migration failures | Target hash `f236d6d86deca0066c98e3776189b32c8818cb6d`; portal setting failures on jobs `8vspcanje0` and `63lqkkrppt`; role-order failure on `6itfpob0ra`; final Controller evidence showed app mirror hash `3e86bc149d6dcc04daa194b740c1733f5c796261`, site migrate `crn5pskff4`, config `3u20303jfl`, and clear-cache `eu27r8q4to` successful | typed provider payload, terminal job proof, migration repair, and role-first permission guard added | guarded |

## Root pattern

The agent confused "account access is human-gated" with "provider work is
human-owned." Once access exists, the provider task is agent-owned unless it
requires MFA, secrets, payment approval, legal/business approval, or destructive
go/no-go confirmation. The follow-on trap is treating a provider API enqueue,
dashboard status, or stable site status as complete before terminal job and
route/browser proof.

## Why it seemed reasonable at the time

The local preflight script correctly cannot mutate Frappe Cloud, and there was
no `fc` CLI on the machine. That made dashboard instructions look like the only
available path, but the project also has browser automation and launch-process
capabilities for account-session workflows.

## Detection signals

- Phrases like "do this in Frappe Cloud now" or "tell me when done" during an
  active launch.
- A provider dashboard URL in chat followed by manual instructions instead of
  browser/API/SSH investigation.
- A launch verifier blocked on missing provider setup while the agent has not
  attempted the documented provider workflow.
- An abstract provider-proof blocker is reported before searching local
  runbooks, app mirrors, Frappe Cloud bench IDs, Press source, prior indexed
  conversations, dashboard URLs, API-token setup, SSH certificate state, and
  authenticated browser surfaces.
- Frappe Cloud API returns `200`/`null` and the agent treats it as deploy proof.
- A nested provider payload is sent form-encoded instead of as JSON.
- Site status is `Active`, but `update_available=true` or installed hash still
  points at the old app.
- Provider state is mutated by the Controller while helpers have not produced
  artifacts the Controller must consume.

## Required guard

For provider launch work, first attempt an agent-owned execution path:

1. Use available CLI/API/SSH if documented and authenticated.
2. Use Playwright/browser automation when the user has logged into a provider.
3. Use screenshots/snapshots to navigate dashboard state.
4. Ask GL only for MFA, credentials not available to the agent, business
   approval, or final destructive mutation approval.
5. For Frappe Cloud API work, send nested payloads as `application/json` typed
   arrays/objects and treat `200`/`null` as enqueue-only until deploy candidate
   terminal success, site update/migrate success, cache clear, installed
   hash/app order, site status, no running jobs, and route/browser proof all
   pass.

## Recovery recipe

1. Record the process failure in lessons and capabilities.
2. Verify current source/site state.
3. Find the documented project/provider process.
4. Try the agent-owned execution path.
5. For provider APIs, verify request payload shape and terminal async job
   status before continuing.
6. Only escalate a concrete blocker the agent cannot technically cross.
7. Resume verification from the failing gate.

## What not to do

- Do not paste a dashboard checklist to GL as the next action when logged-in
  access exists.
- Do not treat lack of a local CLI as proof the agent cannot proceed.
- Do not ask GL to repeat research that is already encoded in project
  capabilities or workstreams.

## Cross-links

- Related capability: `capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`
- Related capability: `capabilities/recipes/ad-account-takeover-provider-control.md`
- Related capability: `capabilities/recipes/codex-browser-verification-surface.md`
- Related failure: `capabilities/failures/ad-dashboard-research-vs-control-drift.md`
- Related failure: `capabilities/failures/frappe-cloud-api-payload-shape-drift.md`
- Related failure: `capabilities/failures/frappe-cloud-release-site-migration-drift.md`
- Related failure: `capabilities/failures/staging-proof-surface-conflation.md`
- Related workstream: `workstreams/frappe-cloud-cloudflare-stripe-launch-2026-05-11.md`

## Evidence quality

Verified from the active launch conversation and staging probes. The guard is
process-level; future launches should validate it by using browser/API/SSH
before escalating provider-dashboard tasks to GL.
