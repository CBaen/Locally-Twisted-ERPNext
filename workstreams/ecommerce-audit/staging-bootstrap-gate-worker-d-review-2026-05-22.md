# Worker D Review - Staging Bootstrap And Owner Review Gate

Date: 2026-05-22
Role: Worker D, release-triad review lens
Scope: source review only for staging owner-review bootstrap/gate; no source edits.

2026-05-23 freeze note: this blocker review remains useful evidence, but the
release process has been stopped and superseded by
`../frappe-cloud-staging-release-failure-forensics-2026-05-23.md` and
`../frappe-cloud-release-prevention-action-items-2026-05-23.md`.

## Verdict

BLOCK.

The staging gate correctly fails the current target, but the implementation is
not yet safe enough to be the release-control architecture that prevents this
failure class from recurring.

## Critical Findings

1. Partial catalog bootstrap cannot self-recover.

   `staging_owner_review_bootstrap.run_staging_owner_review_bootstrap()` only
   calls `seed_catalog` when `Website Item == 0` or `Item == 0`. However
   `seed_catalog.execute()` commits after each product. If the long seed fails
   after one or more products land, a rerun can skip the catalog seed and leave
   staging permanently partial until manual cleanup.

   Evidence:
   - `apps/locally_twisted/locally_twisted/staging_owner_review_bootstrap.py:92`
   - `apps/locally_twisted/locally_twisted/seed/seed_catalog.py:678`

   Required fix: the bootstrap must fail loudly on partial baseline counts and
   either require an explicit purge/rebuild mode for staging or be able to resume
   idempotently to the full required catalog baseline. Do not let nonzero counts
   mean "seed complete."

2. `npm run test:staging-owner-review` is pinned to the old deployed hash.

   `package.json` still expects
   `3e86bc149d6dcc04daa194b740c1733f5c796261`, while the app mirror candidate
   containing the bootstrap is `6573d1e0a57f563d371343a032e586ed87241af6`.
   This makes the package-level release gate drift-prone every time the app
   mirror changes.

   Evidence:
   - `package.json:38`
   - app mirror HEAD observed as `6573d1e0a57f563d371343a032e586ed87241af6`

   Required fix: make the expected hash explicit at runtime, for example via
   `LT_EXPECTED_APP_HASH`, or generate it from the deployed app mirror release
   being promoted. A hardcoded hash in `package.json` is not stable enough for a
   release gate.

## High Findings

3. Staging lock has a config override that can bypass the site-name signal.

   `_assert_staging()` allows execution if either the site/host contains
   `staging` or `lt_allow_staging_bootstrap` is truthy. It blocks the known live
   vanity host string, but the config override is broader than the target site.

   Evidence:
   - `apps/locally_twisted/locally_twisted/staging_owner_review_bootstrap.py:117`
   - `apps/locally_twisted/locally_twisted/staging_owner_review_bootstrap.py:118`
   - `apps/locally_twisted/locally_twisted/staging_owner_review_bootstrap.py:119`

   Required fix: lock the bootstrap to an explicit allowlist such as
   `locallytwisted-staging.frappe.cloud`, with the config flag acting only as an
   additional requirement, not an alternate path.

4. Bootstrap proof is cache-only and can disappear.

   `get_staging_owner_review_bootstrap_status()` reads Redis cache with a
   one-day expiry. The staging gate treats missing state as acceptable if the
   method exists. This can erase the strongest proof of how staging was seeded.

   Evidence:
   - `apps/locally_twisted/locally_twisted/staging_owner_review_bootstrap.py:68`
   - `apps/locally_twisted/locally_twisted/staging_owner_review_bootstrap.py:136`
   - `scripts/verify/staging_owner_review_gate.py:121`

   Required fix: write a durable bootstrap proof record or site config marker
   containing state, app hash, counts, and timestamp. The gate should not accept
   an empty bootstrap proof after this recovery path exists.

5. Owner-review route proof is too thin for product-gallery readiness.

   The gate checks counts and a few route status codes, but only requires one
   slideshow and one slideshow item across the whole site. It does not prove
   Classic Arch/Mickey gallery thumbnails, representative product types, or
   mobile/desktop gallery behavior on staging.

   Evidence:
   - `scripts/verify/staging_owner_review_gate.py:31`
   - `scripts/verify/staging_owner_review_gate.py:39`

   Required fix: staging owner-review gate should either call the gallery
   projection/product-gallery staging verifier or add target-product checks for
   expected slideshow rows and rendered thumbnail affordances.

## Current Staging Evidence

Command:

```powershell
python scripts\verify\staging_owner_review_gate.py --expected-hash 6573d1e0a57f563d371343a032e586ed87241af6 --json
```

Result: FAIL.

Observed target:
- staging site active
- app order correct
- deployed `locally_twisted` hash still `3e86bc149d6dcc04daa194b740c1733f5c796261`
- bootstrap status method unavailable on staging
- `Item`, `Item Price`, `Website Item`, `Website Slideshow`,
  `Website Slideshow Item`, and `LT Product Blueprint` counts all `0`
- `locallytwisted@gmail.com` missing
- `marketing@exploringnotboring.com` missing
- Mickey Mouse Bouquet and Columns routes return `404`

## Commands Run

```powershell
git rev-parse --abbrev-ref HEAD
git status --short --branch
Get-Content C:\Users\baenb\projects\codex-framework-backup\skills\triadic-work\SKILL.md
Get-Content C:\Users\baenb\projects\codex-framework-backup\skills\security-release-gate\SKILL.md
Get-Content C:\Users\baenb\projects\codex-framework-backup\skills\frappe-site-build-proof\SKILL.md
Get-Content C:\Users\baenb\projects\codex-framework-backup\skills\locally-twisted-reality-check\SKILL.md
Get-Content C:\Users\baenb\agent-coordination\STARTUP-CHECKLIST.md
Get-Content C:\Users\baenb\agent-coordination\LIVE-BOARD.md
Get-Content C:\Users\baenb\agent-coordination\SESSION-REGISTRY.md
python -m py_compile apps\locally_twisted\locally_twisted\staging_owner_review_bootstrap.py scripts\verify\staging_owner_review_gate.py apps\locally_twisted\locally_twisted\seed\seed_catalog.py apps\locally_twisted\locally_twisted\seed\sync_product_blueprints_from_catalog.py
python scripts\verify\staging_owner_review_gate.py --expected-hash 6573d1e0a57f563d371343a032e586ed87241af6 --json
```

## Files Changed By Worker D

- `workstreams/ecommerce-audit/staging-bootstrap-gate-worker-d-review-2026-05-22.md`
