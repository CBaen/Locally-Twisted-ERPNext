# Capability File Schema

Schema version: 2.4

Capabilities are reusable operating knowledge. They help an agent find the
right tool, rule, workflow, or project pattern without making the user repeat
the same context in every session.

Every formal capability is one Markdown file. Use ASCII text, short sections,
and plain language. The framework is progressive: install the full reference
structure everywhere, but use the lightest profile that honestly fits the work.

## Compatibility

Existing `1.0`, `1.1`, `2.0`, `2.1`, and `2.2` files remain readable as
legacy or current capability cards. Schema `2.0` maps to the governed profile
in `2.1+`. Do not rewrite old files just to fill unknown history. When a legacy card is
touched for real work, upgrade it honestly:

- Use `evidence_quality: retrofitted` if old proof is incomplete.
- Use `currently_true: unknown` until the new evidence rules are met.
- Do not set `maturity: verified` or `maturity: staple` from memory alone.

## Progressive Profiles

Use capabilities to make agents faster, not to create paperwork. Start with
foundation. Add governed evidence, composition tracking, or cascade watch only
when complexity, risk, repeated use, or dependency impact earns it.

| Profile | Use it for | Required behavior |
|---|---|---|
| `foundation` | Simple routing cards, contracts, kitchen promotions, known tools, "what this helps with" notes. | Keep it easy to write. Do not treat it as proven. |
| `governed` | Cards that make confidence claims, promotion decisions, reusable workflows, or cross-project guidance. | Track evidence, successful uses, failures, regressions, verification level, and evidence quality. |
| `composition` | Meals, feasts, or contracts that depend on other capabilities. | Track dependencies and watch status so inherited risk is visible. |
| `cascade` | Failure handling when a composed capability or dependency breaks. | Retest the layer below, put affected dependents on watch, and restore confidence only after revalidation. |

Evolution is gated. A capability can change, but trust-bearing changes need
evidence, date, result, confidence, and a rollback or revalidation path. A
living kitchen is not permission for every pantry item to mutate constantly.

## Formal Levels

| Level | Folder | Meaning |
|---|---|---|
| `atomic_ingredient` | `atomic_ingredients/` | The smallest reusable behavior, command, check, field, or event. |
| `ingredient` | `ingredients/` | A small reusable building block made from one or more atomic ingredients. |
| `principle` | `principles/` | A rule or constraint that guides many capabilities. |
| `recipe` | `recipes/` | A workflow with a clear start and finish. |
| `meal` | `meals/` | An end-to-end composition of recipes that completes a meaningful project shape. |
| `feast` | `feasts/` | A proven operating system made from meals, recipes, principles, and staples. |

If the level is unclear, start in `kitchen/` and promote only after use.

## Roots And Topology

A capability root is any folder with a capability `INDEX.md` and the framework
shape. Every project should have a first root. Projects may add more roots when
that improves discovery: by agent, feature, domain, subsystem, or subject.

For new project roots, prefer visible top-level folders such as
`capabilities/` and `capabilities-<scope>/`. Hidden agent-specific roots such
as `.codex/capabilities/` or `.openclaw/capabilities/` remain valid for runtime
adapters and existing installs, but the framework package itself is portable.

Each root index must label:

- what this root does
- what belongs here
- what does not belong here
- related roots and backlinks

Roots are not silos. Capabilities may link across roots, projects, agents, and
subjects. Use normal Markdown links for readability and metadata fields for
stable relationships.

Placement rule:

- Ingredients and recipes live where they are most reusable.
- A meal lives in the consuming capability root: the root that references and
  uses the ingredient chain.
- If multiple roots consume the same meal, either keep local meal cards in each
  consuming root or create one explicitly shared meal with every consuming root
  linked through `used_by`, `related_roots`, tags, and prose.
- If an external ingredient fails, every consuming meal that inherits it loses
  confidence until the chain is revalidated.

Use hub/spoke indexing for token protection: root `INDEX.md` files route;
spokes and cards hold detail.

## Maturity

| Maturity | Meaning |
|---|---|
| `kitchen` | Rough idea, experiment, or project lesson. It may be useful, but it is not formal. |
| `candidate` | Structured enough to try, but not proven enough to trust automatically. |
| `verified` | Proven within the stated scope by repeated successful use and checks. |
| `staple` | A hardened, preferred path for future work in its scope. |
| `deprecated` | Kept for history or migration, but should not guide new work. |

## Frontmatter

### Foundation Profile

This is the default for new formal cards unless there is already enough
evidence to justify a heavier profile.

```yaml
---
id: stable-kebab-case-id
name: Human-readable name
schema_version: 2.1
profile: foundation
level: atomic_ingredient | ingredient | principle | recipe | meal | feast
maturity: candidate | deprecated
scope: global | agency | project | repo | client | task-specific description
currently_true: false | unknown
last_verified: YYYY-MM-DD | unknown
tags: []
---
```

Foundation cards may include `depends_on`, `used_by`, `verification_level`, or
short evidence notes, but they should not claim `currently_true: true`,
`maturity: verified`, or `maturity: staple`. Upgrade to governed first.

### Governed Profile

Use governed fields when the card is reused, promoted, or asked to carry
confidence across sessions.

```yaml
---
id: stable-kebab-case-id
name: Human-readable name
schema_version: 2.1
profile: governed
level: atomic_ingredient | ingredient | principle | recipe | meal | feast
maturity: kitchen | candidate | verified | staple | deprecated
scope: global | agency | project | repo | client | task-specific description
currently_true: true | false | unknown
verification_level: 0 | 1 | 2 | 3
last_verified: YYYY-MM-DD | unknown
evidence_quality: direct | inferred | retrofitted | mixed | unknown
successful_uses: 0
failed_uses: 0
regressions: 0
depends_on: []
used_by: []
tags: []
---
```

### Composition And Cascade Profiles

Composition and cascade cards add dependency watch fields to the governed
frontmatter:

```yaml
watch_status: clear | watch | failed | stale | probation | revalidating | unknown
last_success: YYYY-MM-DD | unknown
last_failure: YYYY-MM-DD | unknown
confidence_notes: short reason for the current trust state
```

Use `depends_on` for ingredients, recipes, principles, or external contracts the
card relies on. Use `used_by` for higher-level cards that inherit this card's
risk.

For durable cross-root relationships, use a root-qualified reference in
metadata and a normal Markdown link in the body for readability:

```yaml
depends_on: [shared::capability-id, project-a::recipes/example.md]
used_by: [tesla-launch::meal-id]
```

The alias before `::` is resolved by tooling when the caller supplies the
related root path, for example:

```powershell
python tools\capability_dependency_report.py --root capabilities --related-root shared=C:\Users\<user>\capabilities --json
```

If a root-qualified dependency fails, consuming cards in other roots inherit
watch status until the dependency and the consuming chain are revalidated.

Traffic light state is derived from `watch_status`; do not add a
`traffic_light` frontmatter field in v1 of the organic growth layer:

| Derived light | `watch_status` values | Meaning |
|---|---|---|
| green | `clear` | The card is clear within its stated scope. |
| yellow | `watch`, `probation`, `revalidating`, `unknown` | The card can be inspected or cautiously reused, but trust is not greenlit. |
| red | `failed`, `stale` | The card or dependency chain is not trusted for normal use until repaired. |

Field meanings:

- `id`: stable key used by registries and evidence ledgers.
- `name`: what to call this capability in conversation.
- `schema_version`: the schema version used by this file.
- `profile`: how much tracking the card has earned.
- `level`: which formal layer owns the file. It must match the parent folder.
- `maturity`: how much trust future agents should place in this capability.
- `scope`: where the claim is meant to hold. Keep this narrow enough to test.
- `currently_true`: whether this can be treated as true in the stated scope.
- `verification_level`: practical confidence score, not fake precision.
- `last_verified`: last date this capability was checked in real use.
- `evidence_quality`: how strong the evidence is.
- `successful_uses`: count of evidence-backed successful uses.
- `failed_uses`: count of evidence-backed failures or downvotes.
- `regressions`: known regressions caused or exposed by this capability.
- `depends_on`: capability ids or relative links this builds on.
- `used_by`: known higher-level capability ids or relative links.
- `related_roots`: optional list of capability roots this card expects agents
  to know about.
- `home_root`: optional plain-language root where this capability is maintained
  when links cross projects.
- `watch_status`: whether dependency or downstream risk needs attention.
- `last_success`: last date a real use or revalidation succeeded.
- `last_failure`: last date a failure or regression was observed.
- `confidence_notes`: short explanation of the current confidence state.
- `tags`: retrieval terms, project names, tools, synonyms, and user phrasing.
- `source_kind`: optional source/provenance class for where the learning came
  from.
- `adoption_state`: optional adoption state for whether the source is only a
  reference, locally adapted, locally verified, rejected, or unknown.
- `source_refs`: optional flat source pointers, links, root-qualified refs, or
  safe source names.
- `rights_status`: optional rights/terms state when reuse, attribution, or
  copying could matter.
- `attribution_required`: optional `true`, `false`, or `unknown` flag for
  whether visible attribution is required.

### Optional Organic Growth Metadata

These fields are optional flat metadata. They help agents discover useful
combinations, propose recipes, and run contests without changing the core
substrate or creating nested dependency objects.

```yaml
building_block_type: action | noun | principle | guard | workflow | contract | custom plain scalar
composition_roles: [speed, safety, revenue, learning, reliability, creativity, leverage]
portability: local | project | cross-project | global | experimental
combination_potential: low | medium | high
```

Rules:

- Missing fields are not warnings.
- Values are plain scalars or flat lists only.
- `depends_on` and `used_by` stay string references only.
- New metadata values may be proposed by growth reports, but they are not
  standardized until reviewed.
- Growth and contest tools may report candidates, but they do not promote
  cards, write evidence, or mutate trust-bearing fields.

`building_block_type` answers "what kind of block is this?" `composition_roles`
answers "what job can it play inside a meal?" `portability` answers "where
could this travel?" `combination_potential` answers "how promising is it for
future recipes, meals, feasts, or contests?"

### Optional Source / Provenance Metadata

These fields are optional flat metadata for borrowed, researched, inspired,
agent-generated, official-docs-based, or user-practice-derived learning. They
help agents distinguish "someone else's ingredient," "someone else's recipe,"
"reference only," and "verified local practice" without creating new piles.

```yaml
source_kind: local_evidence | user_practice | official_docs | external_research | third_party_pattern | agent_output | mixed | unknown
adoption_state: reference_only | adapted | verified_local | rejected | unknown
source_refs: [safe source link, root-qualified card ref, local research note, source name]
rights_status: checked | unchecked | not_applicable | restricted | unknown
attribution_required: true | false | unknown
```

Rules:

- Missing fields are not warnings.
- Values are plain scalars or flat lists only.
- Use `source_refs` for safe pointers, not copied secrets, private client
  material, long quotes, or raw source dumps.
- `source_kind` and `adoption_state` do not prove the capability is currently
  true. They only tell an agent where the learning came from and how far it has
  been adopted.
- `adoption_state: verified_local` means the local adaptation was checked in
  this root's scope. It does not mean the original source is universally true.
- External adopted cards should keep either `source_refs` or a
  `## Source / Provenance` section so inspiration is not mistaken for local
  proof.
- If rights, terms, or attribution can matter, record `rights_status` and
  `attribution_required` before a card becomes a preferred path.
- Rejected external ideas usually belong in `failures/` or evidence downvotes;
  use `adoption_state: rejected` on a formal card only when the card itself is
  the durable warning or boundary.

### Perfect Bite Candidates

A Perfect Bite is not a formal card type in v1. It is a high-bar contest
candidate generated from capability evidence, dependency state, optional
metadata, and agent justification.

A candidate must name the combined ingredients, meals, recipes, or principles;
explain why the combination is better than separate use; name the prize it
competes for; show evidence and traffic-light state; list failure points and a
repair path; declare reuse scope; and state whether current internet,
official-source, rights, or provenance/adoption review is required.

Promotion is manual. A Perfect Bite report can create action items, research
brief holds, or proposed cards, but it cannot greenlight trust by itself.

## Verification Levels

| Level | Meaning |
|---|---|
| `0` | Unverified, imported, guessed, or only remembered. |
| `1` | Plausible and structured, with at least one direct inspection or use. |
| `2` | Reused successfully in the stated scope with checks and no known regression. |
| `3` | Staple-grade: repeated success, no open regression, and preferred path status. |

## Currently True Rule

`currently_true: true` is a scoped claim, not a universal truth.

Only use `currently_true: true` when all are true:

- The card uses the governed, composition, or cascade profile.
- The capability has at least 3 evidence-backed successful uses in the stated scope.
- The desired result was achieved in those uses.
- There are no open regressions tied to the capability.
- Any failures have either been fixed, scoped out, or documented as limits.
- The surrounding tool, repo, project, or machine state has not drifted enough to invalidate it.
- If the capability or any required dependency recently failed, there have been
  three subsequent evidence-backed successful uses after the repair.

If any of those are unknown, use `currently_true: unknown`.

## Upvotes And Downvotes

Upvotes are operational evidence, not praise.

An upvote means:

- The capability was used in real work.
- It achieved the intended result.
- Verification was recorded.
- No known bug, regression, privacy issue, or user-facing mismatch was introduced.
- The scope still matches the evidence.

A downvote means the capability failed, caused friction, caused a regression,
or was used outside its valid scope. Downvotes should point to the fix,
deprecation, or branch that should happen next.

## Evidence Ledger

Capability roots may include `evidence/capability-evidence.jsonl`. Each line is
one JSON object. Keep entries compact and do not include secrets or private
conversation text.

Recommended event shape:

```json
{"ts":"2026-05-05T00:00:00-06:00","capability_id":"stable-id","event":"use|upvote|downvote|failure|fix|promotion|deprecation|retest|watch|rollback","actor":"agent","scope":"project or machine scope","result":"short result","verification":"command, check, review, or human approval","confidence":0,"rollback":"how to undo, revalidate, or mark stale","notes":"short safe note"}
```

The ledger is append-only. If a prior event was wrong, add a correcting event.

## Required Sections

Use these sections in this order.

### What it does

One or two sentences. Plain language. No marketing.

### When to reach for it

The trigger conditions. Be specific enough that another agent can recognize the
moment without reading the whole project.

### How to use it

The actual steps, commands, file paths, prompts, or checks. Make them practical
and copy-pasteable when commands are needed.

### What it depends on

Links or ids for capabilities this builds on.

Use `None.` when there is no dependency.

## Optional Sections

### Failure modes

What can go wrong, what it looks like, and how to recover.

### Examples

Real situations where this capability helped.

### Evidence notes

Short, non-sensitive summary of why the current maturity and verification level
are justified. Detailed events belong in the evidence ledger.

### Source / Provenance

Use this when origin, rights, research status, or adaptation boundaries matter.
Keep it short:

```markdown
## Source / Provenance

- Origin:
- Source type:
- License/terms:
- What we adopted:
- What we changed:
- What is not proven here:
- Last source check:
```

### Rollback / revalidation path

What to do if this capability fails, a dependency changes, or a trust-bearing
edit needs to be reversed.

### Adapter notes

Use only when the same capability behaves differently across agents.

## Kitchen Entries

Files in `kitchen/` may be loose notes. They should still include date, scope,
and what would prove or disprove the idea when practical.

## Failure Entries

Files in `failures/` use a different shape. They are not capabilities; they are
warning labels for future work.

Keep machine compatibility by using `type: failure` for every file in this
folder. Use `failure_kind` when the entry needs more precision:

```yaml
---
name: Human-readable name of the failed approach or Failure Recipe
type: failure
failure_kind: dead_end | recurring_pattern | regression_pattern | process_failure
date_discovered: YYYY-MM-DD
last_updated: YYYY-MM-DD
status: open | guarded | probation | controlled | obsolete
---
```

`failure_kind` is optional for older dead-end entries. Add it when touching a
file or creating a new one.

### Dead-end failures

Use this compact shape for a specific approach that was tried and should not be
repeated:

```markdown
## What was tried

## Why it did not work

## What to do instead
```

### Failure Recipes

Use the human-facing name **Failure Recipe** for recurring, high-cost,
misleading, cross-surface, regression, or process-significant failures. These
entries still use `type: failure`, usually with `failure_kind` set to
`recurring_pattern`, `regression_pattern`, or `process_failure`.

Required sections:

```markdown
## Symptom

## Trigger conditions

## Known instances

## Root pattern

## Why it seemed reasonable at the time

## Detection signals

## Required guard

## Recovery recipe

## What not to do

## Cross-links

## Evidence quality
```

Known instances should name the trigger/action, surface, bad outcome, evidence,
guard state, and status. Use human-readable tables in the card; add append-only
evidence rows when tooling exists or the pattern is important enough.

If a Failure Recipe is open or recently repaired, linked capabilities may need
`watch_status: watch` or `watch_status: probation`. A guard added after a
failure should be treated as guarded/probationary until revalidated, not
immediately controlled.

Do not use `failures/` as a permanent scraps pile. Keep only durable warnings or
active revalidation notes; remove failed material that no longer prevents
repeated waste.

## Version History

- `1.0` - initial formal layers: ingredient, recipe, meal.
- `1.1` - adds the `principle` layer for reusable rules and constraints.
- `2.0` - adds atomic ingredients, feasts, maturity, currently-true evidence,
  scoped verification, upvotes/downvotes, and evidence ledgers.
- `2.1` - makes the schema progressive: foundation by default, governed when
  evidence is needed, composition/cascade when dependency risk needs tracking.
- `2.2` - evolves `failures/` into the Failure Recipes layer while preserving
  `type: failure` compatibility through `failure_kind`.
- `2.3` - adds optional organic growth metadata, derived traffic-light
  semantics, and Perfect Bite contest candidates as proposal-only reports.
- `2.4` - adds optional source/provenance and adoption metadata so borrowed,
  researched, inspired, agent-generated, official-docs-based, and local
  practice learning can be distinguished without new top-level folders.
