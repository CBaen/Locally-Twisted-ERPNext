# Staging Release Candidate Freeze - 2026-05-29

Status: branch-only release candidate freeze, not deployment approval
Branch: `codex/lt-staging-release-candidate-freeze`
Worktree: `C:\Users\baenb\agent-worktrees\builtbycameron-lt\release-candidate`

## Plain Meaning

The graduation support work fits the larger release candidate as repo/process
support. It does not belong inside the item 5 checkout packet itself.

Practical split:

- Item 5 packet owns checkout staging release/no-go readiness.
- Graduation support packet owns capability/verifier/process support.
- This release-candidate freeze branch can include both, because it names them
  separately and keeps the deployment boundary closed.

This branch does not approve staging deployment, provider changes, app mirror
update, migrate, cache clear, live checkout, live Stripe, DNS, Search Console,
product data mutation, ERPNext record mutation, email sending, or remediation.

## Integrated Sources

Base:

- local committed `main`: `82c86f4` (`Document catalog scope authority rule`)

Merged sources:

- checkout audit packet chain:
  `origin/codex/item5-staging-release-packet-scope` at `86d6908`
- graduation support packet:
  `origin/codex/lt-graduation-support-packet` at `4147dcb`
- release-controller decision packet:
  `origin/codex/lt-staging-release-controller-packet` at `708fac0`

Resulting branch commits:

- `ac6a19d` integrates the checkout audit packet chain.
- `5f771c2` integrates the graduation support packet.
- `b5ef808` integrates the release-controller packet after resolving handoff
  text conflicts.

## Fit Decision

Graduation support should be included in this branch as support evidence, not
as a customer checkout behavior change.

It fits here because:

- the branch is a source-freeze candidate, not a staging mutation;
- the graduation support files are capability cards, verifier manifest entries,
  index wording, and a support packet;
- the work makes future agents safer when reading the release candidate;
- the checkout and graduation concerns remain separately named in the packet.

It would not fit if:

- it were treated as item 5 checkout proof;
- it were used to justify provider mutation;
- it masked checkout, payment, email, or ERPNext evidence requirements;
- it forced unrelated product-data, staging, live, DNS, Stripe, Search Console,
  or email work into the release.

## Merge Findings

The checkout audit packet chain merged cleanly into local committed `main`.

The graduation support packet merged cleanly after the checkout chain.

The release-controller packet had expected text conflicts in:

- `CODING-HANDOFF.md`
- `workstreams/ecommerce-audit/README.md`

Those conflicts were handoff/front-door ordering conflicts, not runtime checkout
code conflicts. The resolution keeps the release-controller packet first, then
the shop audit evidence.

## Included Change Surfaces

Checkout/customer path:

- `apps/locally_twisted/locally_twisted/checkout_fulfillment.py`
- `apps/locally_twisted/locally_twisted/verify/checkout_fulfillment_contract.py`
- `scripts/verify/public_network_integrity.spec.js`
- checkout audit proof packets under `workstreams/ecommerce-audit/`

Capability/process support:

- `capabilities/INDEX.md`
- `capabilities/recipes/fail-loud-operating-law.md`
- `capabilities/recipes/frappe-portfolio-proof-reel.md`
- `capabilities/recipes/shared-inquiry-form-experience.md`
- `verifier-manifest.json`
- `workstreams/capability-graduation-support-packet-2026-05-29.md`

Release control:

- `workstreams/ecommerce-audit/staging-release-controller-packet-2026-05-29.md`
- this freeze packet
- front-door handoff updates

## Verification Run In This Freeze

Run from `C:\Users\baenb\agent-worktrees\builtbycameron-lt\release-candidate`:

```powershell
python C:\Users\baenb\projects\capabilities-framework\tools\validate_verifier_manifest.py --project . --json
python C:\Users\baenb\projects\capabilities-framework\tools\capability_graduation_audit.py --root capabilities --json --fail-on-required
python scripts\verify\checkout_fulfillment_contract.py
node --check scripts\verify\public_network_integrity.spec.js
git diff --check
```

Results:

- Verifier manifest: `PASS`, 1 manifest, 8 bundles, 0 errors, 0 warnings.
- Capability graduation audit: `PASS`, 72 cards, 5 declared graduated, 0
  required blockers, 0 active-without-artifacts, 27 candidates.
- Checkout fulfillment contract: `PASS`; verifier rolled back generated
  records.
- Public network integrity syntax check: `PASS`.
- `git diff --check`: `PASS`.

## Required Verification Before Any Deploy Request

Before this branch can be used to request staging deployment approval, run and
record:

- payment/backend contract set that item 5 required;
- hosted proof only after a separately approved staging deployment;
- provider-backed app/source identity proof only with explicit credential
  approval.

If any source commit changes after this packet, this packet becomes archive
evidence and must be refreshed.

## Stop Conditions

Stop before deployment if:

- this branch is dirty;
- any included source branch changes without refreshing the packet;
- checkout totals, Stripe/test amount, thank-you page, receipt, internal
  notification, ERPNext record, or email proof differs by one cent;
- quote-first products can enter paid checkout;
- Frappe Cloud source identity cannot be proven before deploy approval;
- graduation support is treated as checkout proof;
- staging/provider, app mirror, migrate/cache, live checkout, live Stripe, DNS,
  Search Console, product data, ERPNext records, email sending, or remediation
  are requested without separate approval.

## Next Safe Step

Run local validations on this release-candidate branch. If they pass, push the
branch for review and use it as the source-freeze candidate for the next
separate staging deployment approval conversation.
