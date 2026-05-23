# Frappe Cloud Freeze Reopen Approval Helper - 2026-05-23

Status: **implemented local guard helper; no provider or staging mutation**.

## Scope

This workstream closes the remaining hand-authored approval gap in the LT
Frappe Cloud forensic-freeze path. The release controller already requires a
valid `freeze-reopen-approval.json` before mutation while the active lock is
present. This helper gives future agents a local, validated way to preview,
write, or validate that artifact instead of copying JSON from prose.

## Changed Files

- `scripts/release/freeze_reopen_approval_artifact.py`
- `scripts/verify/freeze_reopen_approval_artifact_contract.py`
- `package.json`
- `scripts/README.md`
- `workstreams/release-artifacts/README.md`
- `workstreams/release-artifacts/2026-05-23-staging-freeze/TEMPLATE.md`
- `CODING-HANDOFF.md`
- `locally-twisted-queue.md`
- `locally-twisted-decisions.md`
- `lessons-learned.md`
- `capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`
- `capabilities/evidence/capability-evidence.jsonl`

## Contract

`scripts/release/freeze_reopen_approval_artifact.py` is local-only. It does
not contact Frappe Cloud, sync the app mirror, deploy, bootstrap, migrate,
clear cache, touch live/DNS/Stripe/Search Console, unpause checkout, or read
secrets.

Default mode is preview only and returns `ok=false`. A mutation-capable
artifact can be written only with:

```powershell
python scripts\release\freeze_reopen_approval_artifact.py `
  --write `
  --output workstreams\release-artifacts\<fresh-packet>\freeze-reopen-approval.json `
  --approved-by "Guiding Light" `
  --approval-evidence "<exact fresh approval source>" `
  --json
```

The generated artifact is bound to:

- the active release lock,
- `locallytwisted-staging.frappe.cloud`,
- the current repo `HEAD`,
- staging-only reopen actions,
- timezone-bearing ISO-8601 timestamps,
- a maximum 24-hour approval window,
- and the live/DNS/Stripe/Search Console block.

The helper refuses unsupported/non-staging actions, including live release,
DNS, Stripe, Search Console, production indexing, and checkout unpause. It also
refuses to overwrite an existing output unless `--force` is supplied.

## Verification

Run:

```powershell
python -m py_compile scripts\release\freeze_reopen_approval_artifact.py scripts\verify\freeze_reopen_approval_artifact_contract.py
python scripts\verify\freeze_reopen_approval_artifact_contract.py
npm run test:release-prevention
python scripts\verify\verifier_cli_contract.py
```

The contract proves:

- preview mode cannot become mutation-capable,
- valid explicit `--write` output validates,
- existing approval artifacts are not overwritten accidentally,
- inactive or non-forensic release locks fail,
- missing `approval_evidence` fails on write and validation,
- live release actions fail,
- stale source commits fail current-HEAD binding,
- expired approvals fail,
- timezone-less approvals fail,
- approval windows longer than 24 hours fail.

## Next Safe Step

This helper does not create approval on its own. The next staging attempt still
needs a fresh dated release packet, a fresh explicit approval source, a helper-
generated `freeze-reopen-approval.json`, a current read receipt, artifact-owned
triad evidence, current provider snapshot, app mirror pre-sync plan, post-sync
freshness proof, deploy-completion proof, hosted preflight proof, and owner-
review gate proof.

Archived packets remain evidence for their packet source commit only. Do not
reuse `2026-05-23-staging-reopen-fa38bc3-readonly/` as mutation proof after
`HEAD` moves.
