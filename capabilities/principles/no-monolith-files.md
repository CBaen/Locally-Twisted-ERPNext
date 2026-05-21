---
id: no-monolith-files
name: No Monolith Files
schema_version: 2.0
level: principle
maturity: candidate
scope: portable file design for hand-authored production code, docs, tests, scripts, verifiers, and templates
currently_true: unknown
verification_level: 1
last_verified: 2026-05-08
evidence_quality: direct
successful_uses: 0
failed_uses: 0
regressions: 0
depends_on:
  - current-truth-needs-evidence
used_by: []
tags:
  - maintainability
  - file boundaries
  - no monoliths
  - agent handoffs
  - context safety
---

## What it does

Prevents agents from creating or expanding giant catch-all files. A file with
too many responsibilities becomes harder to read, harder to verify, harder to
handoff, and easier to damage with partial-context edits.

## Law

NO MONOLITHS. Hand-authored production source, templates, stylesheets, scripts,
verifiers, tests, and project docs should have one clear job and a readable
boundary.

Research/reference artifacts are the only intentional long-form exception.
Generated, vendor, lock, cache, and export files are artifacts, not a design
precedent, and must not be hand-expanded as project logic.

## Required behavior

1. Before adding to a large or broad file, identify the file's current job.
2. If the new work introduces a second unrelated concern, split it into a named
   module, partial, helper, recipe, workstream doc, or capability card.
3. If an existing monolith blocks a full split, keep the immediate change
   surgical and record the split as follow-up in the queue, handoff, lesson, or
   capability card.
4. Do not use generated, vendor, lock, cache, or export files as examples for
   how hand-authored project code should be shaped.
5. Keep research/reference long-form files labeled clearly so agents do not
   mistake them for production structure.

## Failure modes

- A file becomes a dumping ground for unrelated business, UI, data, verifier,
  and documentation concerns.
- Future agents hit truncation or context limits and silently miss important
  sections.
- Tests and verifiers become too broad to identify which behavior failed.
- A small requested change requires reading or editing a whole unrelated
  subsystem.
- Handoffs become unreliable because the relevant logic is hidden inside a
  large file with no clear boundary.
