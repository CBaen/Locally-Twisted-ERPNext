# Construction Review - Protective Contracts Slice

Date: 2026-06-30

Review type: real multi-agent construction review with second-pass acceptance.

Status: accepted as planning-contract work. This is not code implementation approval, not a live mutation approval, and not a release approval.

## Build Brief

Source brief: [construction-build-brief-2026-06-30.md](construction-build-brief-2026-06-30.md)

Goal: convert the prior triad critique into enforceable planning contracts before Product Setup, catalog, cart, checkout, migration, or release implementation begins.

Non-goals:

- no live product repair;
- no ERPNext record mutation;
- no payment, provider, DNS, Frappe Cloud, cache, deployment, or customer-message action;
- no final product-scope decisions.

## Ownership And Overlap

Primary write scope:

- [README.md](README.md)
- [construction-build-brief-2026-06-30.md](construction-build-brief-2026-06-30.md)
- [protective-contracts.md](protective-contracts.md)
- [hardening-milestones.md](hardening-milestones.md)
- [plan-deepen-notes.md](plan-deepen-notes.md)
- [significant-change-register.md](significant-change-register.md)
- [construction-review-2026-06-30.md](construction-review-2026-06-30.md)

Anti-overlap rule: this slice owns planning contracts only. Later code work must open a new build brief with disjoint file ownership and a fresh capability gate.

## Review Findings

### Owner Workflow Lens

Initial verdict: not yet acceptable as a complete owner-operable planning contract.

Findings:

- State contract was a state list, not a real transition matrix.
- Role approval versus execution was blurred.
- Change-type proof matrix missed option/configuration changes, lane changes, new products, retire/revive, fulfillment/tax/fee, and catalog repair/migration.
- Owner blocker report lacked canonical categories and sample non-developer wording.
- Build brief evidence bar implied live proof was refreshed in this slice.

Fixes applied:

- Added allowed transition matrix and blocked unlisted transitions.
- Added role-by-responsibility table.
- Expanded change-type proof matrix and added default block for unlisted change types.
- Added blocker categories and owner-facing example messages.
- Clarified that this slice cites previously captured public-route evidence and does not refresh live proof.

Second-pass verdict: accepted.

### Technical And Data Architecture Lens

Initial verdict: acceptable after medium wording fixes.

Findings:

- `Checkout Enabled` was ambiguous as a state.
- Item Price identity was too loose.
- Active Product Setup uniqueness needed a composite key and active-status definition.
- Media role rules needed the selected-option image guard from prior regressions.

Fixes applied:

- Removed `Checkout Enabled` as a state and made checkout readiness a Contract 8 invariant.
- Required price proof to name `item_code`, variant/option key, Price List, currency, UOM if relevant, validity dates/scope, and source resolver or approval evidence.
- Defined Product Setup uniqueness as target item + public slug/route + brand lane and listed active statuses.
- Added media guard: simple checkout variant `Item.image` can be approved selected-option media only when Product Setup media rules accept it; complex/custom raw variant images remain held unless approved.

Second-pass verdict: accepted.

### Release And Safety Lens

Initial verdict: not complete enough to serve as controlling release contract.

Findings:

- Frappe Cloud release-scope proof was too generic.
- Phase 0 cache wording could be read as allowing cache clear during read-only incident proof.
- No-downtime/customer-impact was not a release-packet field.
- Brand-lane proof did not enumerate allowed lanes or inheritance proof.
- Live payment proof needed sharper provider constraints.
- `Checkout Enabled` appeared as an uncontracted state.

Fixes applied:

- Added old live app hash, target app-mirror branch/commit, old-live-to-target diff, deploy pipeline status, dirty-overlap audit, site update result, and migrate result where applicable.
- Clarified Phase 0 forbids cache clearing.
- Added no-downtime/customer-impact section to pre-mutation packets.
- Added allowed brand lanes: `locally_twisted`, `commercial_balloon_decor`, and `memorial_balloons`; blocked any fourth lane.
- Required brand inheritance proof through route, file/media, document, payment metadata, customer message, portal, and automation surfaces.
- Added live payment/provider constraints, including correct provider identity and no unapproved one-time code burn.

Second-pass verdict: accepted.

## Fixes Required

No remaining blockers from the construction-review lanes for this planning-contract slice.

This does not mean code work is approved. It means the planning contracts are now strong enough to govern the next build brief.

## Verification

- Capability gate: PASS.
- Restricted-term scan: PASS.
- Construction reviewers: three independent lanes, all accepted second pass.
- No code, live data, provider, payment, deployment, cache, or customer-message changes were made.

## Remaining Risk

- The contracts still need implementation into schema rules, validation, verifiers, owner UI, dry-run reports, and release packets.
- Authenticated read-only incident proof for `large-head-missionary` has not been performed in this slice.
- No local Docker, Desk, or browser runtime proof was run in this slice because it was contract-only.

## Next Build Brief

The next safe build brief should be Phase 0 plus Phase 1 only:

1. Authenticated read-only incident audit for `large-head-missionary`.
2. Non-mutating authority matrix template and one-product authority packet.
3. No cache clear, no product write, no payment/provider action, no deployment.
4. Stop before any repair path that mutates live or local ERPNext data.
