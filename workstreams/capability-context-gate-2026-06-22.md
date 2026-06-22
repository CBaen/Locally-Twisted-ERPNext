# Capability Context Gate - 2026-06-22

## Status

Implemented and locally verified for LT. This workstream records the process
guardrail created after the 2026-06 product/hero release slice broadened and
agents failed to use the project capability framework consistently.

This is a process/infrastructure closeout. It did not perform a Frappe Cloud
site update, live deploy, provider dashboard mutation, Stripe change, DNS
change, ERPNext data mutation, or customer communication.

## What Triggered This

GL asked for a narrow LT slice:

- retire four public products:
  - `large-garland`
  - `mothers-day-bouquet`
  - `large-organic-column`
  - `pride-progress-rainbow-balloon-arch`
- update the landing hero to a Fourth of July treatment;
- keep docs/count parity consistent.

The code slice was committed and pushed to the full LT source repo as
`4427e70 Retire products and update July hero`, and the scoped app mirror was
pushed as `96be0c5 Retire products and update July hero`.

Local proof existed:

- homepage showed the Fourth of July hero locally;
- the four requested product URLs returned `404` locally;
- shop taxonomy, website item classification, catalog public sellability, and
  local payment launch readiness checks passed.

Live proof did not match:

- `https://locallytwisted.com/` still showed the old Graduation hero;
- the four requested product URLs still returned `200`.

The missing live step was Frappe Cloud/site update proof, not another local code
rewrite. After GL stopped the deploy/release tangent, the approved scope became:
create enforceable guardrails so future agents must use capabilities before
editing, releasing, or claiming readiness.

## What Changed

Machine/framework guard:

- Added `/home/guidingl/codex-framework/tools/capability_context_gate.py`.
- Updated `/home/guidingl/AGENTS.md`.
- Updated `/home/guidingl/codex-framework/framework/machine-wide-AGENTS.md`.
- Updated `/home/guidingl/projects/capabilities-framework/templates/serious-project/PROJECT-AGENTS.template.md`.

Agency/LT guard:

- Updated `/home/guidingl/projects/Built_by_Cameron/AGENTS.md`.
- Updated `AGENTS.md` in this repo.
- Added LT capability docs:
  - `capabilities/recipes/mandatory-capability-context-gate.md`
  - `capabilities/failures/capability-context-gate-bypass-drift.md`

## Gate Behavior

The gate requires:

1. nearest local `capabilities/INDEX.md` loaded;
2. high-risk tasks to load a task-specific recipe, failure note, gate, or skill
   in addition to the index;
3. git-backed projects to fail when no local capability index exists;
4. nested projects to use the nearest nested capability index, not a parent
   root substitute;
5. task-relevance for high-risk files, so unrelated release notes cannot satisfy
   product/catalog work.

High-risk vocabulary includes release/live/provider/payment/checkout/form/data
terms and LT-relevant product/catalog/public-site/hero/document/backend
automation terms.

## Witness Review

Used `$witnessed-work` in read-only mode after the guard was built.

Intent witness initially found that product/catalog/public-site/document terms
were not covered by the executable gate. That was patched.

Technical witness initially found that required index selection could prefer a
git-root capability index over a nearer nested capability index. That was
patched.

Final witness status:

- no remaining blocker;
- unrelated release/deploy capability no longer satisfies `LT public product retirement`;
- relevant catalog recipe passes for product retirement;
- no-loaded and index-only high-risk cases fail;
- release and checkout cases pass with relevant recipes;
- local/nearest index enforcement remains in place.

Witness state packet:
`/home/guidingl/.codex/tmp/witness-state/2026-06-22-lt-capability-context-gate.md`.

## Verification

Commands run from LT root unless noted:

```bash
python -m py_compile /home/guidingl/codex-framework/tools/capability_context_gate.py

python /home/guidingl/codex-framework/tools/capability_context_gate.py \
  --cwd /home/guidingl/projects/Built_by_Cameron/_CLIENTS/locally-twisted \
  --task "deploy live Frappe Cloud product hero payment checkout"

python /home/guidingl/codex-framework/tools/capability_context_gate.py \
  --cwd /home/guidingl/projects/Built_by_Cameron/_CLIENTS/locally-twisted \
  --task "deploy live Frappe Cloud product hero payment checkout" \
  --loaded /home/guidingl/projects/Built_by_Cameron/_CLIENTS/locally-twisted/capabilities/INDEX.md

python /home/guidingl/codex-framework/tools/capability_context_gate.py \
  --cwd /home/guidingl/projects/Built_by_Cameron/_CLIENTS/locally-twisted \
  --task "deploy live Frappe Cloud product hero payment checkout" \
  --loaded /home/guidingl/projects/Built_by_Cameron/_CLIENTS/locally-twisted/capabilities/INDEX.md \
  --loaded /home/guidingl/projects/Built_by_Cameron/_CLIENTS/locally-twisted/capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md

python /home/guidingl/codex-framework/tools/capability_context_gate.py \
  --cwd /home/guidingl/projects/Built_by_Cameron/_CLIENTS/locally-twisted \
  --task "LT public product retirement" \
  --loaded /home/guidingl/projects/Built_by_Cameron/_CLIENTS/locally-twisted/capabilities/INDEX.md \
  --loaded /home/guidingl/projects/Built_by_Cameron/_CLIENTS/locally-twisted/capabilities/failures/frappe-cloud-release-site-migration-drift.md

python /home/guidingl/codex-framework/tools/capability_context_gate.py \
  --cwd /home/guidingl/projects/Built_by_Cameron/_CLIENTS/locally-twisted \
  --task "LT public product retirement" \
  --loaded /home/guidingl/projects/Built_by_Cameron/_CLIENTS/locally-twisted/capabilities/INDEX.md \
  --loaded /home/guidingl/projects/Built_by_Cameron/_CLIENTS/locally-twisted/capabilities/recipes/erpnext-catalog-variant-price-parity.md
```

Expected results:

- no-loaded high-risk task: fail;
- index-only high-risk task: fail;
- index plus relevant Frappe Cloud launch recipe: pass;
- product retirement plus unrelated release failure note: fail;
- product retirement plus catalog parity recipe: pass.

Additional targeted checks passed:

- nearest nested capability root beats parent root;
- git-backed repo without a local capability index fails;
- touched-file `git diff --check` passed for LT, BBC, codex-framework, and
  capabilities-framework guard files.

## Next Agent Instructions

Before touching LT again, run the gate. For product/hero/catalog work, load:

- `capabilities/INDEX.md`
- `capabilities/recipes/erpnext-catalog-variant-price-parity.md` or another
  specific catalog/product capability that actually governs the task.

For Frappe Cloud/live/provider/Stripe/DNS work, load:

- `capabilities/INDEX.md`
- `capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`
- relevant release failure notes such as:
  - `capabilities/failures/frappe-cloud-release-site-migration-drift.md`
  - `capabilities/failures/frappe-cloud-app-mirror-release-scope-drift.md`

Do not claim the 2026-06 product/hero fixes are live until the Frappe Cloud
site update/migration/cache/live route proof path has actually passed.
