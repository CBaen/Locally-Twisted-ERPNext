# Frappe Cloud Required Read Docs Refresh - 2026-05-23

Status: **implemented local/offline read-receipt guard refresh; no release
mutation**.

## Scope

The active forensic-freeze lock and shared release guard constant now require
future mutation-capable packets to include the latest packet-authoring handoffs
in `read-receipt.json`.

Newly direct-required docs:

- `workstreams/frappe-cloud-staging-next-agent-closeout-2026-05-23.md`
- `workstreams/frappe-cloud-staging-reopen-packet-prep-2026-05-23.md`
- `workstreams/frappe-cloud-app-mirror-sync-plan-helper-2026-05-23.md`
- `workstreams/frappe-cloud-failure-ledger-artifact-helper-2026-05-23.md`
- `workstreams/frappe-cloud-doc-parity-849d8c2-2026-05-23.md`
- `workstreams/frappe-cloud-a5ed680-readonly-closeout-2026-05-23.md`
- `workstreams/frappe-cloud-staging-app-deploy-closeout-2026-05-23.md`
- `workstreams/frappe-cloud-release-learning-ledger-2026-05-23.md`
- `capabilities/failures/frappe-cloud-deploy-site-object-drift.md`

This closes a local gate gap: a future approved `app_mirror_sync` packet should
not pass the controller after reading only the older forensic report, lock,
and first helper docs.

## Boundary

This change does not:

- create `freeze-reopen-approval.json`;
- create a mutation-capable packet;
- sync the app-root mirror;
- call Frappe Cloud;
- deploy, bootstrap, migrate, import, seed, clear cache, create users, index
  staging, or unpause checkout;
- touch live, DNS, Stripe, Search Console, production indexing, or live
  checkout;
- read or print secrets.

It only tightens the local read-receipt gate.

## Why It Matters

The current blocked release path depends on newer instructions that were added
after the first read-receipt widening:

- do not create another no-go packet solely because docs moved `HEAD`;
- use the prep helper only for prep-only output;
- generate the app-mirror sync plan through the helper;
- generate or validate the failure ledger through the helper;
- treat the `849d8c2` docs closeout as documentation parity, not release
  proof;
- treat the `a5ed680` packet as pre-deploy no-go evidence, not current-source
  mutation authority;
- treat the later staging app deploy closeout as app-hash proof plus
  owner-review NO-GO proof, not bootstrap/import or client-review authority;
- require complete Frappe Cloud provider site objects in deploy/update payloads;
- preserve the good/bad/important lessons, including that GL's dual-account
  workflow is expected and official Frappe Cloud docs must be refreshed before
  release execution.

Those rules now need to be mechanically present in the required-doc receipt,
not only discoverable through handoffs.

## Verification

Required verification:

```powershell
npm run test:release-prevention
python scripts\verify\verifier_cli_contract.py
git diff --check
```

Passing these proves local prevention only. It does not prove staging is
owner-review ready.
