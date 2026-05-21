---
id: source-provenance-and-adoption
name: Source Provenance And Adoption
schema_version: 2.4
profile: foundation
level: recipe
maturity: candidate
scope: capability framework
currently_true: unknown
last_verified: 2026-05-21
source_kind: user_practice
adoption_state: adapted
rights_status: not_applicable
attribution_required: false
depends_on:
  - current-truth-needs-evidence
  - capability-evidence-and-promotion
  - organic-capability-growth
  - perfect-bite-contest-layer
used_by: []
tags:
  - provenance
  - source intake
  - adoption
  - attribution
  - combined learning
---

## What it does

Turns borrowed, researched, inspired, agent-generated, official-docs-based, or
user-practice-derived learning into capability material without pretending the
source is local proof.

## When to reach for it

Use this when a capability, kitchen note, Failure Recipe, meal, or Perfect Bite
candidate is shaped by someone else's ingredient, someone else's recipe,
outside research, official docs, prior agent output, a user's lived practice, a
public repo, a tool, a visual reference, or a cross-root learning packet.

Use it especially when rights, attribution, source freshness, client privacy,
or "this worked for them, but have we proven it here?" could affect future
trust.

## How to use it

1. Capture the source before summarizing it away.
   - Keep a safe source pointer in `source_refs`, a research note, or the body.
   - Record the user's reason for caring when that signal matters.
   - Do not paste secrets, private client content, long copyrighted excerpts, or
     raw source dumps into a capability card.
2. Classify the source with the lightest useful metadata:

   ```yaml
   source_kind: local_evidence | user_practice | official_docs | external_research | third_party_pattern | agent_output | mixed | unknown
   adoption_state: reference_only | adapted | verified_local | rejected | unknown
   source_refs: [safe source pointer]
   rights_status: checked | unchecked | not_applicable | restricted | unknown
   attribution_required: true | false | unknown
   ```

3. Extract the reusable principle instead of copying the source.
   - Ask what the source teaches: tool behavior, UX shape, process sequence,
     business pattern, risk guard, data model, verification method, or style
     reference.
   - Keep the original source's authority separate from the local adaptation's
     evidence.
4. Pick the correct home.
   - `kitchen/`: rough idea, source note, possible adaptation, or scraps that
     still have a clear test.
   - `failures/`: tried-and-stopped paths, rejected external ideas, rights
     blockers, misleading examples, or recurring source misuse.
   - Formal card: reusable local behavior worth routing future agents toward.
   - Evidence ledger: a real use, downvote, fix, promotion, rollback, or
     revalidation event tied to a capability.
   - Perfect Bite report: a high-value combination proposal that still needs
     review before promotion.
5. Add a `## Source / Provenance` section when origin affects trust:

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

6. Verify local adoption before raising trust.
   - `reference_only` means useful to remember but not adopted.
   - `adapted` means transformed for this scope, but not yet proven enough for
     local-trust claims.
   - `verified_local` means the local adaptation was checked in the stated
     scope. It does not make the original source universally true.
   - `rejected` usually belongs in a Failure Recipe or evidence downvote.
7. Keep intelligence layers proposal-first.
   - Growth and Perfect Bite reports may surface combinations from provenance
     metadata.
   - They may create research holds, review tasks, or proposed cards.
   - They must not promote cards, write evidence, or mutate trust fields by
     themselves.

## What it depends on

- [Current Truth Needs Evidence](../principles/current-truth-needs-evidence.md)
- [Capability Evidence And Promotion](capability-evidence-and-promotion.md)
- [Organic Capability Growth](organic-capability-growth.md)
- [Perfect Bite Contest Layer](perfect-bite-contest-layer.md)

## Failure modes

- **Source becomes authority.** External research, official docs, or another
  person's workflow is treated as local proof before this root verifies it.
- **Attribution disappears.** Future agents cannot tell what was borrowed,
  adapted, or locally discovered.
- **Rights drift.** A repo, screenshot, social post, course, private doc, or
  client source inspires a capability, then future work copies too much.
- **Scraps become storage.** Rough leftovers are kept forever without a test,
  lane, or warning value.
- **Metadata becomes chores.** Agents fill every field on every card instead of
  using provenance only when it improves trust, discovery, rights, or reuse.

## Examples

A public repo can supply an ingredient pattern, but its license and runtime
health must be checked before code is reused. The capability card should record
what was learned and what changed locally.

A consultant's process can inspire a recipe, but the local recipe should say
which steps were adopted, which were changed, and what local proof exists.

A prior agent's research packet can become a source reference, but the card
should preserve whether the packet had artifacts, current-source checks, and
bounded confidence.

## Source / Provenance

- Origin: framework design discussion and prior source-intake practice.
- Source type: user practice and local framework evidence.
- License/terms: not applicable.
- What we adopted: provenance/adoption states as optional metadata and notes.
- What we changed: kept the idea agent-neutral and proposal-first instead of
  adding new top-level piles.
- What is not proven here: that every project needs these fields on every card.
- Last source check: 2026-05-21.

## Rollback / revalidation path

If provenance fields create clutter, remove them from cards where origin does
not affect trust or rights. Keep the recipe as guidance only, rerun registry
and graph validation, and preserve any useful source-intake behavior in
project-specific roots.
