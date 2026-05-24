# Frappe Cloud App Update Release Process - 2026-05-23

Status: **process correction and release infrastructure handoff; not deployment approval**.

## Corrected Goal

Run a routine Frappe Cloud code/app-only release:

1. update the reviewed custom app on staging;
2. prove owner-review readiness on the actual staging site;
3. let Jeff use staging as he would use the live site, within approved safety
   limits;
4. record explicit owner approval or blockers;
5. promote the same reviewed app code to live through an app-only path;
6. preserve production database records, products, customers, clients, private
   files, financial records, site settings, checkout/payment state, DNS, Stripe,
   Search Console, and indexing unless separately approved.

Staging is not the finish line. It is the rehearsal and approval gate for live.

## Truncation Recovery Receipt

The broad release/source searches initially truncated in chat. They were
recovered before this process correction was relied on:

- `.tmp/truncation-recovery/2026-05-23/rg-release-terms-intake/manifest.json`:
  `status=ok`, 108 chunks, 6,868 source lines, hash reassembly matched.
- `.tmp/truncation-recovery/2026-05-23/rg-data-live-terms-intake/manifest.json`:
  `status=ok`, 27 chunks, 1,929 source lines, hash reassembly matched.
- `.tmp/truncation-recovery/2026-05-23/rg-chunk-matches-intake/manifest.json`:
  `status=ok`, 29 chunks, 1,083 source lines, hash reassembly matched.

Subagent Banach confirmed the relevant spans were recovered through manifests,
source maps, targeted chunks, and direct source ranges. No unrecovered source
span remains for this release-goal decision.

## Current Reality

The e87a6b1 staging attempt proved the app can deploy cleanly to staging and
hosted preflight can pass. It did not produce an owner-review-ready shop.

Current blocker: bootstrap/RQ failed because catalog seeding still depended on
the local reference path `_resources/odoo-live`. Odoo/reference material must
be transformed into a Locally Twisted / ERPNext-owned seed source before it can
support hosted staging review.

2026-05-24 handoff boundary: GL stopped release execution and required
handoff-only cleanup. Do not resume staging/provider/live work from this packet
or conversation. Resume only from a fresh source freeze, fresh approval, and
the corrected app-update release skill.

No Jeff staging link should be sent until the actual Frappe Cloud staging host
has nonzero catalog/Product Setup/gallery data, required owner/reviewer users,
paused checkout, disabled indexing, `/shop`, and representative product routes.

## Guard Reassessment

Subagent Ohm classified the current guard pile for this corrected goal.

Keep as P0:

- `npm run test:release-prevention`
- `python scripts\release\release_status_report.py`
- release lock/controller/freeze-reopen/read-receipt/identity/status checks
- `test:frappe-cloud-payload`
- `test:app-mirror-sync-plan`
- real app mirror freshness, provider snapshot, deploy completion, hosted
  preflight, bootstrap, and staging owner-review artifacts
- `test:staging-owner-review`
- ecommerce pause/protection checks when checkout/Stripe are not approved

Keep as P1 or touched-surface proof:

- owner/product/catalog/price/media/gallery checks before owner review
- public/layout/SEO/a11y checks when the release touches those surfaces

Demote for this corrected goal unless explicitly reopened:

- checkout-open suites such as `test:ecommerce-full`,
  `test:checkout-experience`, `test:checkout-fulfillment`, and
  `test:checkout-lead-conversion`
- broad launch commands that can be mistaken for app-update/live authority

Rebuild as P0:

- owner approval artifact for live promotion;
- live code/app-only promotion protector that proves production data/settings
  are not overwritten, reseeded, purged, or changed outside approval.

Misleading label warning: package scripts that run only `--self-test` prove
verifier shape, not current Frappe Cloud reality. They must not be called
staging proof, provider proof, owner-review proof, or live proof.

## Good Route

1. Finish local source/docs needed for the update.
2. Freeze the source commit for the release attempt.
3. Run local release-prevention/status. If `NO-GO`, stop.
4. Get fresh exact approval for staging mutation.
5. Create a fresh dated release packet.
6. Generate current identity, read-receipt, freeze-reopen, failure-ledger,
   app-mirror, provider snapshot, and triad artifacts.
7. Sync/update app source to staging only.
8. Prove app mirror/app hash/deploy completion on staging.
9. Run hosted preflight on the actual staging site.
10. If bootstrap/import is needed, prove the LT-owned seed source exists on
    staging and run the bootstrap/RQ path only after preflight.
11. Run the staging owner-review route/data gate.
12. Give Jeff the staging link only if the owner-review gate passes.
13. Record Jeff's approval or requested changes.
14. If approved, open a separate live promotion packet that binds the reviewed
    staging hash and approval.
15. Snapshot live before, promote the approved app code only, then run live
    after-proof and monitoring.

## Bad Routes

- Treating staging owner review as the final outcome.
- Treating app deploy success as shop readiness.
- Treating self-tests as provider or staging proof.
- Reusing stale packets after `HEAD` moves.
- Letting a checkout-open test authorize checkout, Stripe, or live payments.
- Copying staging data over live production data.
- Running catalog purge/seed/import, cache clear, migrate, DNS, Stripe, Search
  Console, indexing, checkout unpause, or live settings changes without
  separate approval and rollback proof.
- Ignoring truncated output or making decisions from a visible fragment.

## Canonical Skill

Reusable process skill added in the canonical framework:

`C:\Users\baenb\projects\codex-framework-backup\skills\frappe-cloud-app-update-release\SKILL.md`

Use it together with the LT-specific staging gate and this workstream before
any future Frappe Cloud app update attempt.
