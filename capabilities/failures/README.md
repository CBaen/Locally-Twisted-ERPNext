# Failures / Failure Recipes

This folder stores durable warning labels for future work. It started as a place
for dead-end notes: things tried in good faith that did not work. It now also
stores **Failure Recipes**: structured records of recurring failure patterns,
regressions, and process failures with the guards that should prevent them next
time.

Keep the path `failures/` for compatibility. Use the human-facing name
**Failure Recipes** when the entry describes a repeated or reusable pattern.

## Why this folder exists

Without a record of dead ends and recurring failure patterns, every new
contributor and every new agent instance rediscovers them. The cost is paid over
and over: time spent attempting something already disproven, regressions that
look new but are familiar, and trust erosion when the same anti-pattern
resurfaces.

A dedicated failures folder is cheap insurance. Use one Markdown file per
documented dead end or Failure Recipe. Same `.md` format as capabilities,
different schema (see [../SCHEMA.md](../SCHEMA.md#failure-entries)).

## What goes here

- Approaches tried in good faith that did not produce the intended result.
- Patterns that *seem* like they should work but break for non-obvious reasons.
- Recurring regressions, process failures, or bad-outcome workflows with a
  reusable trigger, guard, or recovery path.
- Tools, libraries, delegations, or verification approaches that turned out to
  be unfit for the job.

## What does not go here

- **Ordinary bugs in working capabilities.** Put those in the capability's
  `## Failure modes` section unless the bug reveals a recurring pattern.
- **Isolated typos or one-off misconfiguration.** Those are noise unless they
  expose a reusable trigger or missing guard.
- **Subjective dislikes.** Preferences belong in style docs, not failures.
- **Shame records.** Failure Recipes are operational memory, not blame logs.

## Choosing a failure kind

Use `type: failure` for all files in this folder until the tooling intentionally
supports another machine type. Add `failure_kind` to clarify intent:

- `dead_end` - a specific approach was tried and should not be repeated.
- `recurring_pattern` - the same trap can reappear across surfaces or projects.
- `regression_pattern` - a behavior repeatedly breaks after changes.
- `process_failure` - the workflow, delegation, evidence, or approval process
  failed even if no single code artifact is the root cause.

Older dead-end entries without `failure_kind` remain valid. When you touch one,
add `failure_kind: dead_end` if it still applies.

## When to check this folder

Check Failure Recipes before or during work when:

- an idea feels familiar but you cannot remember why;
- a task touches a surface with known regressions or business risk;
- a verifier expectation, approval gate, or source-of-truth rule is being
  changed;
- a subagent, tool lane, or research dispatch times out or produces no durable
  artifact;
- a bug looks isolated, but the trigger or guard failure could recur.

## Failure Recipe contents

A Failure Recipe should stay compact but source-backed. It should answer:

1. **Symptom** - what it looks like when the pattern appears.
2. **Trigger conditions** - what kind of work tends to start it.
3. **Known instances** - dated rows with surface, action, bad outcome,
   evidence, and status.
4. **Root pattern** - the deeper process/control/verification failure.
5. **Detection signals** - search terms, diffs, timeouts, missing artifacts,
   test smells, user language, or CI symptoms.
6. **Required guard** - verifier, approval marker, source lookup, artifact
   requirement, or human decision gate.
7. **Recovery recipe** - how to repair without hiding the pattern.
8. **Cross-links** - affected capabilities, principles, recipes, workstreams,
   adapters, and related Failure Recipes.
9. **Evidence quality** - what is verified, inferred, stale, unresolved, or
   blocked.

Use [TEMPLATE.failure-recipe.md](TEMPLATE.failure-recipe.md) for recurring
patterns. Use the simpler dead-end shape from the schema for one-off failed
approaches.

## Evidence and trust

Use both human-readable cards and compact evidence rows when the pattern is
important enough. The card keeps the pattern understandable; append-only
evidence rows preserve dated operational facts.

If a Failure Recipe is open or recently recovered, linked capabilities may need
`watch_status: watch` or `watch_status: probation`. A new guard does not make a
pattern controlled by itself; mark it guarded or probationary until revalidated.

## When to remove a failure entry

When the underlying cause is genuinely fixed or obsolete, update the entry and
mark why. Delete only when the warning no longer prevents repeated waste, and
let git history preserve the removal reason.

Do not remove failure entries because the folder feels cluttered. Curated burn
marks are the feature, not the bug.

## Naming

Use kebab-case Markdown filenames. Describe the failed approach or failure
pattern, not just the symptom:

- `mocking-llm-responses-in-tests.md`
- `artifactless-research-delegation.md`
- `source-example-counted-as-approval.md`
