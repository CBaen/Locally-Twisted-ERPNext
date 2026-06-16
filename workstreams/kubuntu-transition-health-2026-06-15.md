# Kubuntu Transition Health - 2026-06-15 MDT

## Status

This is the first in-repo Codex post-migration health pass after the LT working
environment moved from Windows paths to Kubuntu paths.

Current repo root:
`/home/guidingl/projects/Built_by_Cameron/_CLIENTS/locally-twisted`

Current local site:
`http://localhost:8081`

## Verified

- Git root is the LT repo and current branch is `main`.
- `main` is behind `origin/main` by 2 commits.
- Working tree is large WIP, not a clean baseline.
- `git fsck --no-dangling` passed.
- LT Docker containers are running from Kubuntu.
- Local homepage returns HTTP 200.
- Installed apps order is correct: `frappe`, `erpnext`, `payments`, `webshop`, `locally_twisted`.
- `npm run test:nav-ia` passed.
- `npm run test:layout-fit` passed 312/312, but took about 6 minutes and should not be used as a casual health check.
- `npm run test:verifier-cli` passed after Kubuntu verifier help-path repairs.
- `npm run test:layout-fit -- --list` lists the 312 tests quickly through the tracked Node Playwright CLI path.

## Live Runtime Counts

These counts were checked against the running local ERPNext site on 2026-06-15 MDT:

| Record | Count |
|---|---:|
| Website Items total | 51 |
| Published Website Items | 50 |
| Items total | 10,685 |
| Variant templates | 49 |
| Non-variant root Items | 7 |
| All variant records | 10,629 |
| Active variants | 10,186 |
| Disabled variants | 443 |
| Disabled `Add Foil Number` variants | 390 |
| Item Prices | 10,666 |
| Item Variant Attribute rows | 32,049 |
| Item Attributes | 30 |

## Migration Blockers

1. Stale worktree registrations remain in `.git/worktrees` and point to old
   `C:/Users/baenb/agent-worktrees/builtbycameron-lt/...` locations. Do not
   prune them without a branch/remote inventory.
2. The repo has a large dirty WIP surface. Do not pull, reset, rebase, or merge
   until that WIP is classified.
3. `AGENTS.md` and coordination docs still use Windows coordination paths.
   On Kubuntu, the current coordination root is `/home/guidingl/agent-coordination`.
4. Live catalog counts have drifted from `AGENTS.md` and `CODING-HANDOFF.md`.
   Treat older counts as stale until a catalog identity diff explains the
   missing Website Items and non-variant root.
5. Host Python lacks the Playwright package. Python browser verifiers now expose
   safe `--help`, but actual Python browser runs still require a Python
   environment with Playwright or a conversion to Node Playwright.

## Safe Repairs Applied

- Created the Linux LT worktree root:
  `/home/guidingl/agent-worktrees/builtbycameron-lt`.
- Changed npm browser scripts from Windows `.cmd` paths / untracked wrapper
  dependency to direct tracked Node Playwright CLI calls.
- Added `scripts/verify/browser_runtime.py` for Python verifier browser launch
  discovery.
- Moved Python Playwright imports behind argument parsing for affected browser
  verifiers so `--help` stays fast and safe.
- Normalized `scripts/verify/smoke_forms.py` to LF while touching its verifier
  import path, avoiding CRLF whitespace noise in Kubuntu diffs.

## Worktree Inventory

Fourteen stale worktree registrations are prunable according to Git because
their `gitdir` files point at old Windows paths.

Remote-backed branches with no ahead/behind drift:

- `codex/lt-live-indexing-release`
- `codex/checkout-penny-match`
- `codex/lt-graduation-support-packet`
- `codex/item3-product-diversity-scope`
- `codex/item4-internal-processing-scope`
- `codex/item5-staging-release-packet-scope`
- `codex/lt-live-shop-discovery-gate`
- `codex/lt-staging-release-controller-packet`

Branches needing care before any prune/delete:

- `codex/lt-staging-release-candidate-freeze` tracks its remote but is 2 commits
  ahead locally.
- `codex/clean-recovery-1f4520b` has no upstream and 1 commit not in
  `origin/main`.
- `codex/erpnext-catalog-cleanup` has no upstream and 2 commits not in
  `origin/main`.
- `codex/shared-inquiry-gate` has no upstream and 1 commit not in `origin/main`.
- `codex/portfolio-proof-reel-gate` has no upstream and 1 commit not in
  `origin/main`.
- `codex/lt-pause-verifier-selective-indexing` has no upstream and 1 commit not
  in `origin/main`.

## Dirty WIP Surface

At this pass, `git status --porcelain` showed 162 changed/untracked paths:

- 152 modified tracked paths.
- 10 untracked paths.
- largest buckets: 64 audit artifacts, 42 workstream files, 27 app paths, 20
  script paths, 4 `_resources` paths, 2 capability docs, plus package/config
  files.

This is a mixed WIP checkout. Treat it as preservation-first until the current
feature work and generated artifacts are classified.

Pull safety note: `main` is behind `origin/main` by 2 commits, and 4 untracked
local files overlap paths already tracked on `origin/main`:

- `apps/locally_twisted/locally_twisted/marketing_access_reset.py`
- `apps/locally_twisted/locally_twisted/marketing_vendor_access.py`
- `scripts/setup/send_marketing_access_reset.py`
- `scripts/setup/sync_marketing_vendor_access.py`

The two setup scripts are byte-identical to `origin/main`; the reset module has
small local drift. `package.json` is also locally modified and touched by the
remote reset-helper commits. Do not pull until these overlaps are preserved or
adopted deliberately.

## Catalog Drift Notes

The old 53 Website Item count is not current for the running local site. The
queue already contains later evidence that the 2026-05-24 taxonomy result
superseded the old all-product count and treats 51 products as current after 2
duplicate source slugs were excluded.

Current live Website Items:

- 51 total Website Items.
- 50 published Website Items.
- 1 unpublished Website Item: `pride-progress-rainbow-balloon-arch`.

Current non-variant root Items:

- `ADDON-FOIL-NUMBER`
- `DELIVERY-PARK-CITY`
- `DELIVERY-STANDARD`
- `easter-arch` disabled
- `LT-PRODUCT-QUOTE-REVIEW`
- `mothers-day-bouquet`
- `mothers-day-front-yard-7-column`

Current Item Attributes: 30. Querying `item_attribute_name` through
`frappe.client.get_list` is blocked by Frappe field permissions, but querying
`name` succeeds.

## Do Not Do Casually

- Do not run `git worktree prune` until stale worktree branches are mapped to
  remotes and local-only commits.
- Do not run `git pull` while the WIP tree is unclassified.
- Do not run `git reset`, `git clean`, or checkout away dirty files.
- Do not run launch, provider, DNS, Stripe, or contact-submission gates without
  an explicit release/testing lane.

## Next No-User-Blocker Steps

1. Classify the WIP tree into migration/tooling, current feature work, generated
   audit artifacts, and stale/transient outputs.
2. Decide a preservation path for local-only stale worktree branch commits before
   any `git worktree prune`.
3. Update the repo's current Kubuntu path guidance only after the WIP/pull
   situation is safe.
