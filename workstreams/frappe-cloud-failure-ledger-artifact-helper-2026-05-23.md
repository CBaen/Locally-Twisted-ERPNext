# Frappe Cloud Failure Ledger Artifact Helper - 2026-05-23

Status: **implemented local/offline release-prevention guard; no release
mutation**.

## Scope

The release controller already required `failure-ledger.json` before any
mutation-capable Frappe Cloud staging action. This pass makes that artifact
real instead of hand-wavy:

- `scripts/release/failure_ledger_artifact.py` previews, writes, or validates a
  source-bound `failure-ledger.json`.
- `scripts/verify/failure_ledger_artifact_contract.py` proves the helper and
  controller reject missing, empty, stale, unsafe, or fake ledgers.
- `scripts/release/release_guard_common.py` now validates the failure ledger as
  a strict object bound to the active lock, current repo `HEAD`, the staging
  target, concrete guard paths, and no provider mutation.
- `npm run test:failure-ledger-artifact` is part of
  `npm run test:release-prevention`.

## Boundary

This change does not:

- create `freeze-reopen-approval.json`;
- create a mutation-capable release packet;
- sync the app-root mirror;
- call Frappe Cloud;
- deploy, bootstrap, migrate, import, seed, clear cache, create users, index
  staging, or unpause checkout;
- touch live, DNS, Stripe, Search Console, production indexing, or live
  checkout;
- read, print, or archive secrets.

It only tightens local release-prevention behavior.

## Artifact Contract

A controller-consumable `failure-ledger.json` must include:

- `ok: true`;
- `artifact_type: failure_ledger`;
- active lock id `lt-staging-forensic-freeze-2026-05-23`;
- current full source commit;
- target site `locallytwisted-staging.frappe.cloud`;
- `provider_mutation_executed: false`;
- `fresh_release_plan_approved`;
- a non-empty `failures` list.

Each failure row must include:

- `failure_class`;
- `summary`;
- `source_evidence`;
- `guard_written: true`;
- repo-relative `guard_path` that exists.

Repeated failure classes are allowed only with
`fresh_release_plan_approved: true` and non-empty
`fresh_release_plan_evidence`.

The validator rejects raw or secret diagnostic fields such as tokens, sessions,
raw provider logs, body excerpts, and stack traces.

## Why It Matters

The previous controller gate required a failure ledger, but the validator could
accept a thin hand-authored object. That preserved the name of the gate without
proving the actual circuit breaker. A future release packet could have passed
with no concrete failure-class evidence, no guard paths, and no source binding.

This helper makes the artifact explicit and reproducible. Preview mode returns
`ok=false` and `controller_consumable=false`; a packet artifact requires
`--write`, an output named `failure-ledger.json`, and `--reviewed-source`.

## Verification

Required local checks:

```powershell
npm run test:failure-ledger-artifact
npm run test:release-prevention
python scripts\verify\verifier_cli_contract.py
git diff --check
```

Passing these proves local prevention only. It does not prove staging is
owner-review ready.

## Related

- `workstreams/frappe-cloud-required-read-docs-refresh-2026-05-23.md`
- `workstreams/frappe-cloud-release-prevention-action-items-2026-05-23.md`
- `workstreams/release-artifacts/README.md`
- `capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`
