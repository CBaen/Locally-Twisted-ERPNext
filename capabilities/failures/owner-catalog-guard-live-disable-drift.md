---
name: Owner catalog guard live disable drift
type: failure
failure_kind: process_failure
schema_version: 0.1
date_discovered: 2026-06-23
last_updated: 2026-06-23
status: guarded
scope: project
owner_context: Locally Twisted live product visibility changes
related_capabilities:
  - ../recipes/erpnext-live-product-visibility-retirement.md
  - ../recipes/erpnext-product-blueprint-authoring.md
  - ../recipes/erpnext-ecommerce-receiving-architecture.md
related_failures:
  - capability-context-gate-bypass-drift.md
tags:
  - locally-twisted
  - erpnext
  - catalog
  - product-visibility
  - owner-guard
  - live
  - fail-loud
---

# Failure Recipe: Owner Catalog Guard Live Disable Drift

## Symptom

An approved live product visibility change gets stuck because the normal Item
form reports `Protected Owner Catalog Guard`. The blocker is misread as an
external cybersecurity issue, or the agent keeps retrying the blocked form
instead of using the scoped admin maintenance path.

## Trigger Conditions

- GL has approved an exact product hide/disable list.
- The logged-in user has owner-like access, not unrestricted developer
  maintenance context.
- The normal Item or Website Item save path touches protected raw catalog
  records.
- The agent treats "blocked" as "cannot perform the business change" instead
  of identifying which guard fired and why.

## Known Instances

| Date | Project | Surface | Action being taken | Bad outcome | Evidence | Guard state | Status |
|---|---|---|---|---|---|---|---|
| 2026-06-23 | Locally Twisted | Live Desk Item form and System Console doc save | Disable four documented retired products on `locallytwisted.com` | Normal Item save and document save were blocked by `Protected Owner Catalog Guard`; work risked being mislabeled as cybersecurity instead of catalog guard behavior | `workstreams/ecommerce-audit/live-product-disable-2026-06-23.md`; final scoped `frappe.db.set_value` write; public routes returned `404` | recipe and decision packet added | recovered/guarded |

## Root Pattern

The owner catalog guard is a correct business safety guard for raw owner-like
catalog edits. It is not proof that the approved change is forbidden. For exact
admin maintenance work, the safe path is to keep the guard intact, narrow the
target list, mutate only the approved fields, and prove the live result.

## Why It Seemed Reasonable At The Time

The guard message appears during a live-site change and uses strong blocking
language. Without the owner Product Setup history, it is easy to classify the
block as a security issue or a permission wall instead of a project-specific
catalog mutation guard.

## Detection Signals

- Dialog title: `Protected Owner Catalog Guard`.
- Message includes `Please use Product Setup or a guarded product update`.
- The task is to hide, disable, publish, reroute, or price a product.
- A normal Desk save fails, but direct read-only status queries still work.

## Required Guard

Use `../recipes/erpnext-live-product-visibility-retirement.md`.

The agent must:

- confirm exact product scope before writing;
- keep the owner catalog guard enabled;
- use System Console direct field updates only for approved admin maintenance;
- prove root Item, variants, Website Item, product route, and `/shop` state
  after the write.

## Recovery Recipe

1. Stop retrying the blocked form.
2. Identify the guard as LT's owner catalog guard.
3. Reconfirm exact product scope and approval.
4. Run a read-only status query.
5. Run the scoped admin write for only the target fields and target records.
6. Rerun the read-only status query.
7. Check public routes and `/shop`.
8. Record the process in the feature handoff and decision log.

## What Not To Do

- Do not call the owner catalog guard an external cybersecurity issue.
- Do not weaken or remove the guard to complete one live change.
- Do not publish/re-enable old products to satisfy stale product counts.
- Do not mutate price, order, customer, Stripe, DNS, Frappe Cloud, or unrelated
  catalog records during a visibility retirement.

## Cross-links

- Related recipe:
  `../recipes/erpnext-live-product-visibility-retirement.md`
- Related handoff:
  `../../workstreams/ecommerce-audit/live-product-disable-2026-06-23.md`
- Related decision:
  `../../decisions/2026-06-23-live-product-visibility-disable.md`

## Evidence Quality

Direct live behavior and direct live recovery proof on 2026-06-23. Route proof
was public on `https://locallytwisted.com`; the exact write path was through
authenticated Desk System Console.
