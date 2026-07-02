# 2026-07-02 - Kubuntu Active Guidance And Static Doctor

## Decision

LT active agent guidance must use current Kubuntu paths and must not point
agents at nonexistent local retired-host folders. The fast Kubuntu doctor bundle
is now static/source preflight by default through `--static-only`; full local
runtime proof remains available as the separate `lt-kubuntu-runtime-doctor`
manifest bundle after the on-demand LT stack is intentionally started.

## Reasoning

Machine-wide migration safety work found active LT instructions still teaching
old-platform paths for the machine guide, coordination hub, worktree root, hooks,
no-monolith capability source, catalog data checkout, and Claude reference
library. That made a clean repo still unsafe for future agents because the
first-read instructions could route work to paths that do not exist on
Wardenclyffe Kubuntu.

The existing `lt-kubuntu-doctor` also failed when the LT Docker stack was
intentionally stopped. That was correct for full runtime proof, but too noisy
for source/preflight cleanup because LT's local ERPNext stack is on-demand.

## Implementation Boundary

- `AGENTS.md` now uses `/home/guidingl/...` paths for active machine,
  coordination, worktree, hook, and capability guidance.
- Missing local legacy/Claude folders are described as inactive local
  dependencies, not as active source paths.
- `scripts/verify/kubuntu_doctor.py --static-only` checks branch, dirty state,
  Docker/Node/npm availability, and repo-local Playwright presence without
  requiring containers or routes.
- `python3 scripts/verify/kubuntu_doctor.py --runtime` keeps the full read-only
  local stack proof for containers, `http://127.0.0.1:8081`, bench versions,
  and app order.
- No ERPNext data, Docker volumes, provider accounts, live routes, payment
  settings, customer records, or external services were changed.

## Receipts

- `AGENTS.md`
- `scripts/verify/kubuntu_doctor.py`
- `verifier-manifest.json`
- `capabilities/recipes/kubuntu-repo-recovery-cleanup.md`
- `capabilities/recipes/fail-loud-operating-law.md`
- `capabilities/recipes/erpnext-business-automation-index.md`
- `CODING-HANDOFF.md`
- `locally-twisted-queue.md`

## Decided By

Guiding Light's accessibility-mode migration cleanup request and the
machine-wide migration safety audit, implemented on Wardenclyffe Kubuntu on
2026-07-02.
