# Failures

Things that were tried and didn't work. Kept here, not deleted, so the next contributor doesn't repeat the experiment.

## Why this folder exists

Without a record of dead ends, every new contributor and every new agent instance rediscovers them. The cost is paid over and over: time spent attempting something that has already been disproven, debugging that leads nowhere, and the slow erosion of trust as the same anti-pattern resurfaces.

A dedicated failures folder is cheap insurance. One Markdown file per documented dead end. Same `.md` format as capabilities, different schema (see [../SCHEMA.md](../SCHEMA.md#failure-entries-separate-schema)).

## What goes here

- Approaches you tried in good faith that did not produce the result you wanted.
- Patterns that *seem* like they should work but break for non-obvious reasons.
- Tools or libraries you reached for that turned out to be unfit for the job.

## What doesn't

- **Bugs in working capabilities.** Those go in the capability's `## Failure modes` section.
- **One-off mistakes from typos or misconfiguration.** Those aren't dead ends — they're noise.
- **Approaches that work but you didn't like the aesthetics of.** Subjective preferences belong in a style doc, not here.

## When to remove a failure entry

When the underlying cause is fixed (a tool got better, an API stabilized, a library released a fix), update or delete the entry. **Always note the reason in the commit message** — `git log` becomes the record of how the dead end stopped being one.

Don't remove failure entries because the folder feels cluttered. Clutter here is the feature, not the bug.

## Naming

Same kebab-case Markdown convention as capabilities. Filename should describe the failed approach, not the symptom: `mocking-llm-responses-in-tests.md`, not `tests-keep-breaking.md`.
