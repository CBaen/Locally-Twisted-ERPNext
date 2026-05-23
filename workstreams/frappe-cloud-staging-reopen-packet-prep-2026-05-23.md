# Frappe Cloud Staging Reopen Packet Prep - 2026-05-23

Status: **implemented local/offline prep guard; no provider mutation**.

## Scope

This work adds a prep-only lane for the next Locally Twisted staging reopen
attempt. It reduces post-approval packet assembly ambiguity without creating
release authority.

The helper is:

`scripts/release/staging_reopen_packet_prepare.py`

The verifier is:

`scripts/verify/staging_reopen_packet_prepare_contract.py`

Package gate:

```powershell
npm run test:staging-reopen-packet-prepare
```

It is also included in:

```powershell
npm run test:release-prevention
```

## Contract

The helper writes only prep files:

- `README.md`
- `packet-prep-manifest.json`
- `missing-release-artifacts.md`
- `freeze-reopen-approval-preview.json`

It refuses to write into a directory containing final release artifact names and
does not create:

- `freeze-reopen-approval.json`
- `read-receipt.json`
- `failure-ledger.json`
- `app-mirror-sync-plan.json`
- `provider-snapshot.json`
- `app-mirror-freshness.json`
- `sanitized-payload.json`
- `deploy-completion.json`
- `hosted-bootstrap-preflight.json`
- mutation-valid triad artifacts

The manifest intentionally does not use top-level `ok: true`; it uses
`artifact_status: prep_only`, `controller_consumable: false`,
`mutation_capable: false`, `provider_mutation_executed: false`, and explicit
negative proof flags.

## Boundaries

- No Frappe Cloud call.
- No app-root mirror sync.
- No deploy, provider poll, migrate, cache clear, bootstrap, import, user
  creation, indexing, checkout unpause, live release, DNS, Stripe, or Search
  Console mutation.
- No secrets, tokens, session IDs, credential reads, raw provider logs, or
  customer records.
- No owner-review readiness claim.

The helper may carry a rollback hash as context only. A real mutation-capable
packet still needs a fresh read-only provider snapshot and controller-validated
final artifacts.

## Witness Review

Intent Witness `019e53e6-dcc5-7683-ac80-d164f7f655d3` found this aligned only
if it remains a safer repeatable pre-approval prep lane and does not create
another no-go packet loop or false release authority.

Technical Guard Witness `019e53e6-fac1-72e2-a7cf-e07045d0fa8c` required the
safer contract that final artifact filenames are not generated. The
implementation follows that stricter contract.

## Cross-References

- LT decision: `../locally-twisted-decisions.md`
- LT lesson: `../lessons-learned.md`
- LT capability recipe:
  `../capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`
- Agency decision: `../../../built-by-cameron-decisions.md`
- Agency lesson: `../../../lessons-learned.md`

## Verification

- `python -m py_compile scripts\release\staging_reopen_packet_prepare.py scripts\verify\staging_reopen_packet_prepare_contract.py`
- `python scripts\verify\staging_reopen_packet_prepare_contract.py`
- `npm run test:release-prevention`
- `python scripts\verify\verifier_cli_contract.py`
- JSONL parse of `capabilities/evidence/capability-evidence.jsonl`
- `git diff --check`
