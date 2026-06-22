---
id: mandatory-capability-context-gate
name: Mandatory Capability Context Gate
schema_version: 2.1
profile: foundation
level: recipe
maturity: candidate
scope: LT agent startup, edits, release, and high-risk work
currently_true: unknown
last_verified: 2026-06-22
tags:
  - capability
  - guard
  - agent-context
  - fail-loud
  - release-safety
---

## What it does

Forces LT agents to load the nearest capability index and a task-specific
capability resource before editing, releasing, or claiming readiness. This
prevents agents from replacing the project capability framework with memory,
terminal discovery, or confidence.

## When to use it

Use before any LT edit or release action. It is mandatory for public-site,
catalog, checkout, payment, Frappe Cloud, Cloudflare, Stripe, provider, live
release, form, customer-message, document, backend automation, customer-data,
or product-count/parity work.

## How to use it

From the LT repo root:

```bash
python /home/guidingl/codex-framework/tools/capability_context_gate.py \
  --cwd "$PWD" \
  --task "<plain-English LT task>" \
  --loaded "capabilities/INDEX.md" \
  --loaded "<specific LT recipe/failure/skill used for this task>"
```

For high-risk work, `capabilities/INDEX.md` alone is not enough. The second
loaded path must match the task:

- product/catalog work: load a product/catalog/shop/ecommerce capability such
  as `capabilities/recipes/erpnext-catalog-variant-price-parity.md`;
- public layout/hero work: load the public-container/responsive/hero recipes;
- checkout/payment work: load `capabilities/recipes/erpnext-checkout-commerce-rules.md`
  or the governing payment/commerce recipe;
- live/Frappe Cloud/provider work: load
  `capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md` and the
  relevant release failure notes.

## Failure modes

- Agent reads `AGENTS.md` but skips `capabilities/INDEX.md`.
- Agent loads the index but not the governing recipe/failure/skill.
- Agent satisfies a product task with an unrelated release note, or a release
  task with an unrelated product note.
- Agent treats source push, app-mirror push, or local proof as live proof.
- Agent continues provider/live work after GL stops or narrows scope.

## Evidence

- Gate script:
  `/home/guidingl/codex-framework/tools/capability_context_gate.py`.
- LT handoff:
  `workstreams/capability-context-gate-2026-06-22.md`.
- Witness state:
  `/home/guidingl/.codex/tmp/witness-state/2026-06-22-lt-capability-context-gate.md`.
- 2026-06-22 verification proved no-loaded and index-only high-risk tasks fail,
  product retirement rejects unrelated release notes, product retirement accepts
  the catalog parity recipe, nested roots require the nearest local index, and
  git-backed projects without a local capability index fail.
