# Phase 15 Critical Review - Catalog Readiness Dashboard Direction

Date: 2026-07-01

Status: critical review artifact only. No script, app code, queue, handoff,
capability, coordination, runtime, provider, payment, DNS, cache, deploy,
customer-message, product-scope, variant, or live record change occurred.

## Findings

Catalog-level readiness/dashboarding is a safe next phase after Phase 14 only if
it remains a source-only operator triage surface. Phase 14 made per-record Desk
readiness visible without adding a publish button; a dashboard can extend that
same contract across products so operators can see where work is blocked first.

The dashboard must not claim publish readiness. It should aggregate Product Setup
validation state and saved-artifact authority packet blockers, then keep every
live/public approval false until a separate release packet and fresh target-site
proof exist.

The dashboard must not turn source fields into live proof. `operating_brand`
with `source_declared` state is useful source authority, but it is not live
brand-lane proof. Same-brand source uniqueness is useful fail-closed protection,
but it is not live/global uniqueness proof. A saved audit artifact is useful
evidence, but it is not a current public route, cart, checkout, document,
payment, cache, deploy, or rollback proof.

The dashboard should help operators by grouping and counting blockers without
implying that any product is ready to publish. Minimum useful groups:

- Owner state: `Blocked - Proof Needed`, `Draft`, `Needs Review`, `Local Proof Ready`, `Staging Ready`.
- Product Setup authority state: active source status, inactive/draft status, missing setup, duplicate active source authority, invalid/missing source brand.
- Source authority: source-declared brand present, source brand invalid/missing, same-brand source uniqueness passed, same-brand uniqueness blocked or unproved.
- Runtime authority blockers: target Item mismatch, target Website Item mismatch, linked Website Item missing brand metadata, linked Website Item brand/state mismatch.
- Public/runtime proof blockers: public route proof missing, price mismatch, copy authority drift, media role proof missing, option/add-on payload proof missing, cart/checkout/document proof missing.
- Release safety blockers: pre-mutation rollback packet missing, historical-reference proof missing, cache clear not approved, deploy not approved, mutation not approved.
- Catalog-shape risks: variant explosion, ambiguous base price to many variants, missing setup price values, unclassified SKU axes, paid add-on proof gaps.

Counts should be presented as triage counts, not readiness scores. A product with
zero source blockers still needs the later public/runtime proof chain before it
can be called live-applied.

## Required Acceptance Criteria

Before the parent agent commits a Phase 15 dashboard slice, the work must meet
all of these criteria:

- Scope stays source-only/no-write: no ERPNext mutation, no cache clear, no
  deploy, no provider/payment/DNS action, no customer message, no product-scope
  choice, and no delete/disable/rename/collapse of variants.
- Dashboard output explicitly says its proof mode is saved/source evidence only.
- Dashboard output keeps live apply, mutation, cache clear, deploy, and public
  success approvals false unless a separate release packet path is created and
  proven later.
- Dashboard output separates `source_authority` from live/public proof and never
  promotes `source_declared` brand into live brand-lane proof.
- Dashboard output separates source same-brand uniqueness from live/global
  uniqueness and does not treat old saved artifacts as current catalog truth.
- Dashboard grouping includes owner state plus blocker counts by source
  authority, runtime authority, public proof, release safety, and catalog-shape
  risk.
- Dashboard includes product identifiers and sample blockers so operators can
  act, but it does not choose product scope or approve product business changes.
- Blocked catalog output exits nonzero when run with a fail-on-blocker flag.
- Static verification proves no publish/apply/live/cache/deploy/customer-send
  action is wired into the dashboard.
- Contract tests cover deterministic output, blocked products remaining blocked,
  stale/index artifact rejection, approval flags staying false, and saved
  artifact limitations remaining visible.
- Existing relevant contracts still pass, especially Product Setup validation
  and readiness contracts.
- Commit proof includes `Capability gate: PASS` with
  `capabilities/INDEX.md` and
  `capabilities/failures/product-setup-projection-authority-drift.md` loaded.
- Git status before commit shows only the intended Phase 15 files for the parent
  slice, with this review artifact included if used as the acceptance standard.

Verification that should block commit:

```bash
python -m py_compile <new-or-edited-dashboard-scripts> <new-or-edited-verifiers>
python scripts/verify/product_blueprint_contract.py
python scripts/verify/product_setup_publish_readiness_contract.py
<new-dashboard-contract-verifier>
<new-dashboard-command> --input <saved-artifact-dir-or-fixture> --fail-on-blocker
git diff --check
```

The dashboard command should be expected to exit nonzero while the known saved
catalog remains blocked. A zero exit on the currently blocked saved catalog
would be a release-safety bug, not a success.

## Residual Risk

Even if the dashboard script and verifier pass, it will still be a reporting
surface. It will not prove that the live site, cart, checkout, payment labels,
documents, customer receipts, media files, rollback path, cache state, or
provider-hosted target are correct.

Saved `/tmp` artifacts are useful but ephemeral and can go stale. Passing
against them proves the dashboard logic handles those artifacts; it does not
prove current live catalog state.

Counts can create false confidence. A dashboard that says "47 products grouped"
or "0 source duplicates" may still hide unproved public routes, stale prices,
missing rollback packets, or unapproved business behavior. The UI language must
stay blocker-first.

The largest product-shape risks remain unresolved. Birthday Deliveries and other
variant-explosion products still need no-write model review, dependency proof,
rollback proof, add-on/runtime pricing proof, payload preservation proof, and
owner approval before any catalog mutation.

## Recommendation

Proceed with Phase 15 only as a no-write catalog readiness dashboard over
existing source validation and saved authority-packet evidence. Treat the
dashboard as an operator map of blockers, not as a publish queue.

Do not build live publish/apply controls in this phase. Do not clear cache,
deploy, mutate catalog records, or claim live/public readiness from source-only
counts. The correct closeout should say that the dashboard makes blocker
visibility broader after Phase 14, while live proof and release approval remain
separate future gates.

Capability gate: PASS.

Loaded resources:

- `capabilities/INDEX.md`
- `capabilities/failures/product-setup-projection-authority-drift.md`
