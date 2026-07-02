# Playwright Verifier Runtime - 2026-05-12

## Scope

This handoff owns the May 12 verifier-runtime correction for LT Playwright
tests. It is infrastructure for browser proof, not a public-site feature.

## Decision

Default Playwright execution must remain serial inside each spec file and use
one worker unless a verifier explicitly opts into parallel execution.

`LT_PLAYWRIGHT_FULLY_PARALLEL=1` is the opt-in for in-file parallelism.
`LT_PLAYWRIGHT_WORKERS` may be raised only for specs that are known to be
fixture-isolated.

## Why

Several LT specs share mutable module state, backend fixtures, or cleanup
markers inside a file. `quote_accept_experience.spec.js` is the concrete
reviewed example: it uses a shared fixture marker that `afterEach` cleans up.
Running tests inside that file concurrently can clean up another test's fixture
while it is still using it.

The correct default is slower but honest. Parallel browser workers are only
safe when the spec has a per-test namespace and no shared backend fixture state.

## Current State

`playwright.config.js` is back to:

- default `workers = 1`
- default `fullyParallel = false`
- in-file parallelism only when `LT_PLAYWRIGHT_FULLY_PARALLEL=1`

No alternate browser framework is needed for this issue. The failure was the
default concurrency policy, not Playwright as a tool.

## Verification Receipt

Passed on 2026-05-12:

```bash
node --check playwright.config.js
npm run test:quote-accept-experience
npm run test:form-experience
```

Both Playwright runs reported `using 1 worker`.

## Guardrails

- Do not set `fullyParallel: true` by default in this repo.
- Do not treat `LT_PLAYWRIGHT_WORKERS=4` as safe for rollback-safe or
  fixture-owning specs unless the specific spec proves isolation.
- Broad launch verifiers may orchestrate multiple independent specs, but
  shared-ERPNext fixture specs should stay serial unless rewritten.
- If speed becomes a blocker, split independent specs or add per-test fixture
  namespaces instead of turning on global in-file parallelism.

## Cross-links

- `playwright.config.js`
- `scripts/verify/quote_accept_experience.spec.js`
- `scripts/verify/form_experience.spec.js`
- `capabilities/failures/playwright-in-file-parallel-fixture-race.md`
