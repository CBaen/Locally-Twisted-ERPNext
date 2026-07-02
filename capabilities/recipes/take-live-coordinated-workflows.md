---
name: Take-live coordinated workflows
level: recipe
last_verified: 2026-05-14
---

## What it does

Organizes a launch push with multiple agents or coordinated sessions while preserving quality, ownership, and verification.

## When to reach for it

Use this when Locally Twisted is moving toward launch and multiple agents could work in parallel on independent lanes such as forms, shop, policy pages, media, accessibility, backend readiness, or release verification.

## Mandatory change-request release chain

Every Locally Twisted client change request follows this order:

1. Build and test the change locally first.
2. Push the same reviewed source/artifact to staging.
3. Test the affected frontend, backend, data, email, payment, and operator paths
   on staging as applicable.
4. Push live only after staging succeeds and the required owner/client approval
   is recorded.
5. Test the affected live paths after release before calling the change done.

If any stage fails, stop the release, fix source, and restart at the earliest
stage that can prove the fix. Do not make production-only fixes except to roll
back or stop active damage.

## How to use it

1. Assign one launch controller.
   - The controller owns `workstreams/website-launch.md`, the queue pointer, integration order, and final readiness call.
   - The controller should not hand off the immediate blocking task if their own next step depends on it.

2. Split work by user-facing lane, not technical layer.
   - Inquiry path: `/contact`, `/book` redirect, Lead/service taxonomy, loud failure behavior.
   - Trust/policy: `/privacy`, `/terms-of-service`, `/refund-policy`, `/accessibility`, Stripe URL readiness. Business/legal content should trace to `/home/guidingl/projects/locally-twisted-legacy_source/`, approved current resources, or GL/legal approval.
   - Shop/media: product/category media, variant correctness, Item Group images, product detail confidence. Product/service claims should trace to the legacy_source business-detail source or GL approval.
   - Visual/accessibility QA: desktop/mobile screenshots, layout fit, navigation, keyboard/screen-reader basics.
   - Backend readiness: Jeff-facing Lead/Contact/order flow, stale scripts, sample data after schema cleanup.
   - Release gate: final full-flow verification and launch-readiness report.

3. Set write ownership before dispatch.
   - Each implementation agent gets a disjoint file or behavior scope.
   - Read-only audit agents can run in parallel across lanes.
   - Do not run parallel implementation agents against the same files, DocTypes, fixtures, seed scripts, or checkout/form flows.

4. Give each agent a ready-to-paste prompt.
   - Include the lane outcome.
   - Include exact files/routes they may inspect or edit.
   - Include files/routes they must not touch.
   - Include verification commands they must run.
   - Require a return format: changed files, verification evidence, blockers, and handoff notes.

5. Use two-stage quality review for implementation lanes.
   - Spec review: did the agent solve the assigned lane and stay in scope?
   - Quality review: is the implementation maintainable, Frappe/ERPNext-native, accessible, and consistent with style?
   - Do not merge a lane into launch readiness until both reviews are resolved.

6. Keep a launch board in `workstreams/website-launch.md`.
   - Track lane, owner, status, write scope, verification, blocker, and integration state.
   - Update after each lane returns.
   - Promote durable decisions to `locally-twisted-decisions.md`.

7. Integrate in dependency order.
   - Inquiry path and policy/trust can run beside shop/media if write scopes do not overlap.
   - Variant/media correctness should precede final product-detail visual polish.
   - Backend demo/sample data should wait until schema cleanup.
   - Final visual/accessibility QA should run after page/layout changes.

8. Run the final release gate from the integrated workspace.
   - Verify exact launch-critical routes and flows.
   - Run the documented scripts for nav, layout, shop, forms, backend parity when relevant.
   - Capture desktop/mobile browser evidence for customer-facing surfaces.
   - Report remaining blockers honestly.

## What it depends on

- [claude-reference-library](claude-reference-library.md) - optional read-only reference for older Frappe launch, payment, form, fixture, migration, and deploy safety checklists.
- [visual-debugging](visual-debugging.md) - supports visual inspection when browser screenshots are needed.
- `/home/guidingl/capabilities/recipes/client-release-safety-gates.md` - agency-wide local/preflight, staging, approval, live, and post-live release gate.

## Failure modes

- A swarm without a controller creates conflicting edits and stale claims.
- Layer-based ownership such as frontend/backend hides real conflicts because launch work crosses routes, templates, data, CSS, JS, and ERPNext records.
- Parallel implementation against the same write scope causes merge conflicts or inconsistent behavior.
- Audit results are not launch evidence until the exact affected route, form, or flow is verified after integration.
- Beautiful pages can mask broken inquiry, cart, checkout, or product-option behavior. Launch quality must include function and trust, not only visuals.
- ERPNext app-build copy is not business truth by itself. Customer-facing business details should trace to the legacy_source business-detail source or explicit approval.
- Treating local success as live readiness skips the required staging proof and
  approval gate.

## Examples

Good parallel split:

- Agent A: read-only form audit on `/contact` and Lead submission.
- Agent B: policy/trust page refresh for `/refund-policy` and `/accessibility`.
- Agent C: shop media inventory and variant/media mapping plan.
- Controller: integrates findings and assigns next implementation slice.

Bad parallel split:

- Agent A edits product detail template.
- Agent B edits the same product detail template for accessibility.
- Agent C changes guest cart behavior without knowing Agent A changed variant selection.

## Adapter notes

### Codex

Use subagents only when the user explicitly asks for parallel agent work. Keep the controller local, delegate bounded sidecar tasks, and verify each returned result before integrating it.

### Other agents

Use the same lane/ownership pattern with that agent platform's native task or handoff mechanism.
