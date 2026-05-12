---
name: Playwright in-file parallel fixture race
type: failure
failure_kind: regression_pattern
schema_version: 0.1
date_discovered: 2026-05-12
last_updated: 2026-05-12
status: guarded
scope: project
owner_context: Locally Twisted Playwright verifier runtime
related_capabilities:
  - ../recipes/codex-browser-verification-surface.md
tags:
  - locally-twisted
  - playwright
  - verifier
  - parallelism
  - fixtures
---

# Failure Recipe: Playwright In-File Parallel Fixture Race

## Symptom

Playwright specs that pass serially start racing or flaking when tests inside a
single spec file run concurrently. One test can clean up another test's backend
fixture while it is still running.

## Trigger conditions

- `playwright.config.js` defaults `fullyParallel` to true.
- `LT_PLAYWRIGHT_FULLY_PARALLEL` is interpreted as opt-out instead of opt-in.
- A spec has shared module state, shared markers, `afterEach` cleanup, or
  rollback-safe ERPNext fixtures.

## Known instances

| Date | Project | Surface | Bad outcome | Evidence | Guard state | Status |
|---|---|---|---|---|---|---|
| 2026-05-12 | Locally Twisted | `playwright.config.js` review | Default in-file parallelism could race `quote_accept_experience.spec.js` shared fixture cleanup | External review comment; focused rerun passed with 1 worker | default restored to serial and opt-in parallel | guarded |

## Root pattern

Browser-level parallelism is not the same as fixture isolation. LT Playwright
tests often drive one ERPNext site and use shared fake records, markers, or
cleanup routines. Those specs are serial by design until rewritten with
per-test namespaces and independent cleanup.

## Detection signals

- Diff changes `fullyParallel` from `process.env.LT_PLAYWRIGHT_FULLY_PARALLEL === "1"` to a true-by-default expression.
- Diff raises default `LT_PLAYWRIGHT_WORKERS` from `1`.
- Specs contain shared variables such as `fixtureMarker`, shared cleanup in
  `afterEach`, or backend fixture setup helpers.
- A broad launch verifier fails intermittently on missing fake Leads, Quotes,
  Files, Email Queue rows, or cleanup artifacts.

## Required guard

Default Playwright config stays serial in-file:

```js
const workerCount = Number.parseInt(process.env.LT_PLAYWRIGHT_WORKERS || "1", 10) || 1;
const fullyParallel = process.env.LT_PLAYWRIGHT_FULLY_PARALLEL === "1";
```

Specs may opt into parallelism only after proving fixture isolation.

## Recovery recipe

1. Restore default `workers = 1` and `fullyParallel = false`.
2. Run `node --check playwright.config.js`.
3. Run the reviewed shared-fixture spec, currently
   `npm run test:quote-accept-experience`.
4. Run the affected feature spec, such as `npm run test:form-experience`.
5. If speed is needed, split independent specs or add per-test fixture
   namespaces before increasing parallelism.

## What not to do

- Do not set global in-file Playwright parallelism to true for launch speed.
- Do not use successful independent UI specs as proof that rollback-safe
  backend fixture specs are parallel-safe.
- Do not "fix" flakes by weakening cleanup or leaving fake ERPNext records
  behind.

## Cross-links

- `../../workstreams/playwright-verifier-runtime-2026-05-12.md`
- `../../playwright.config.js`
- `../../scripts/verify/quote_accept_experience.spec.js`
- `../recipes/codex-browser-verification-surface.md`

## Evidence quality

Verified by review output and focused local reruns on 2026-05-12. Broader
parallel-safe classification is not complete; keep opt-in only.
