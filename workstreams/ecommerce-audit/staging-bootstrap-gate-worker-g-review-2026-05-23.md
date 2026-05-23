# Worker G Review - Hardened Staging Bootstrap And Owner Review Gate

Date: 2026-05-23
Role: Worker G, staging release-triad source-review lens
Scope: source review only against Worker D blockers. No Frappe Cloud, live, DNS, Stripe, Search Console, or git mutation. Only this artifact was written.

2026-05-23 freeze note: this review remains useful as source-level blocker
evidence, but it is not a release plan. Release execution is frozen until
`../frappe-cloud-release-prevention-action-items-2026-05-23.md` is converted
into executable gates.

## Reviewed Target

- Source: `f89e31bd9f5068f379402c715a4359f54596ea92` (`Harden staging owner review bootstrap gate`), current local `HEAD`.
- App mirror: `409a64758dd8377e5541bf2ad019b0ba59042aef`, verified with read-only `git ls-remote https://github.com/CBaen/Locally-Twisted-Frappe-App.git HEAD`.
- Reviewed files:
  - `AGENTS.md`
  - `apps/locally_twisted/locally_twisted/staging_owner_review_bootstrap.py`
  - `scripts/verify/staging_owner_review_gate.py`
  - `workstreams/ecommerce-audit/staging-bootstrap-gate-worker-d-review-2026-05-22.md`
  - relevant staging/release capability and failure cards.

## Verdict

BLOCK.

The hardened changes close several of Worker D's direct blockers, but the gate is still not strong enough to be the final staging owner-review release-control gate. The remaining blockers are source-level and do not require touching provider state to identify.

## PASS Findings

1. PASS - The old package-level pinned deployed hash blocker is fixed.

   Evidence:
   - Worker D required runtime-explicit or mirror-derived expected hash: `workstreams/ecommerce-audit/staging-bootstrap-gate-worker-d-review-2026-05-22.md:46`
   - `package.json:38` now runs `staging_owner_review_gate.py --expected-hash-from-mirror`.
   - `scripts/verify/staging_owner_review_gate.py:62` to `scripts/verify/staging_owner_review_gate.py:69` resolves the expected hash before running the gate.
   - `scripts/verify/staging_owner_review_gate.py:275` to `scripts/verify/staging_owner_review_gate.py:285` resolves mirror `HEAD` with `git ls-remote`.
   - Read-only mirror check returned `409a64758dd8377e5541bf2ad019b0ba59042aef`.

   Note: for a frozen release packet, the controller can still pass `--expected-hash 409a64758dd8377e5541bf2ad019b0ba59042aef` to avoid a later mirror `HEAD` move changing the target under review.

2. PASS - The staging lock no longer has the broad config bypass Worker D flagged.

   Evidence:
   - Worker D required an explicit allowlist: `workstreams/ecommerce-audit/staging-bootstrap-gate-worker-d-review-2026-05-22.md:64` to `workstreams/ecommerce-audit/staging-bootstrap-gate-worker-d-review-2026-05-22.md:66`.
   - `apps/locally_twisted/locally_twisted/staging_owner_review_bootstrap.py:21` defines `STAGING_SITE = "locallytwisted-staging.frappe.cloud"`.
   - `apps/locally_twisted/locally_twisted/staging_owner_review_bootstrap.py:129` to `apps/locally_twisted/locally_twisted/staging_owner_review_bootstrap.py:142` requires the exact staging site/host and blocks the known live vanity surfaces.

3. PASS - Cache-only bootstrap status is materially improved.

   Evidence:
   - Worker D required durable proof instead of Redis-only status: `workstreams/ecommerce-audit/staging-bootstrap-gate-worker-d-review-2026-05-22.md:68` to `workstreams/ecommerce-audit/staging-bootstrap-gate-worker-d-review-2026-05-22.md:81`.
   - `apps/locally_twisted/locally_twisted/staging_owner_review_bootstrap.py:145` to `apps/locally_twisted/locally_twisted/staging_owner_review_bootstrap.py:157` now writes status to cache and a private site file.
   - `apps/locally_twisted/locally_twisted/staging_owner_review_bootstrap.py:160` to `apps/locally_twisted/locally_twisted/staging_owner_review_bootstrap.py:174` reads that durable file when cache is empty or returns a loud parse failure.
   - `scripts/verify/staging_owner_review_gate.py:131` to `scripts/verify/staging_owner_review_gate.py:134` now fails unless bootstrap state is exactly `success`.

## BLOCK Findings

1. BLOCK - Partial catalog recovery still uses loose minimum counts, not the full required catalog baseline.

   Worker D's first blocker was not only "do not skip when counts are nonzero." It required the bootstrap to fail loudly on partial baseline counts and recover or rebuild to the full required catalog baseline.

   Evidence:
   - Worker D required the full baseline: `workstreams/ecommerce-audit/staging-bootstrap-gate-worker-d-review-2026-05-22.md:29` to `workstreams/ecommerce-audit/staging-bootstrap-gate-worker-d-review-2026-05-22.md:32`.
   - Current verified local catalog state is higher than the gate baseline: `AGENTS.md:118` to `AGENTS.md:125` lists `53` Website Items, `10,674` Items, and `10,656` Item Prices.
   - Bootstrap thresholds are lower: `apps/locally_twisted/locally_twisted/staging_owner_review_bootstrap.py:25` to `apps/locally_twisted/locally_twisted/staging_owner_review_bootstrap.py:35` require only `50` Website Items, `10,000` Items, `10,000` Item Prices, `50` blueprints, and one slideshow/item.
   - The bootstrap skips catalog seeding when those loose gaps are absent: `apps/locally_twisted/locally_twisted/staging_owner_review_bootstrap.py:106` to `apps/locally_twisted/locally_twisted/staging_owner_review_bootstrap.py:111`.
   - The gate repeats the same loose minimums: `scripts/verify/staging_owner_review_gate.py:34` to `scripts/verify/staging_owner_review_gate.py:41`, checked at `scripts/verify/staging_owner_review_gate.py:135` to `scripts/verify/staging_owner_review_gate.py:138`.

   Impact:
   - A staging catalog with `50` Website Items, `10,000` Items, and `10,000` Item Prices can skip reseeding and pass the count layer while still missing known current catalog records.
   - This does not satisfy Worker D's "full required catalog baseline" requirement and can hide a late partial seed failure.

   Required before staging release gate PASS:
   - Replace loose minimums with source-owned expected catalog baselines, preferably generated from the seed data/manifest being promoted, or add an explicit staging purge/rebuild/resume contract that proves all expected Website Items, Items, Item Prices, Product Setups, and gallery projections landed.
   - The gate should fail on missing expected records, not merely on counts below broad lower bounds.

2. BLOCK - Durable bootstrap proof is not bound to the app hash that produced it.

   Worker D asked for durable proof containing state, app hash, counts, and timestamp. The new status file has state/counts/timestamp, but it does not record the installed app hash or expected target hash at bootstrap time.

   Evidence:
   - Worker D required state, app hash, counts, and timestamp: `workstreams/ecommerce-audit/staging-bootstrap-gate-worker-d-review-2026-05-22.md:79` to `workstreams/ecommerce-audit/staging-bootstrap-gate-worker-d-review-2026-05-22.md:81`.
   - Status payload includes `state`, `site`, `target_site`, `updated_at`, `counts`, and caller payload only: `apps/locally_twisted/locally_twisted/staging_owner_review_bootstrap.py:145` to `apps/locally_twisted/locally_twisted/staging_owner_review_bootstrap.py:157`.
   - Gate checks current installed app hash separately: `scripts/verify/staging_owner_review_gate.py:125` to `scripts/verify/staging_owner_review_gate.py:126`.
   - Gate accepts any durable bootstrap `success` state without comparing that success proof to the current or expected app hash: `scripts/verify/staging_owner_review_gate.py:131` to `scripts/verify/staging_owner_review_gate.py:134`.

   Impact:
   - A stale success file from an earlier app hash can satisfy the bootstrap-status layer after a later app update if current hash/count/route checks pass.
   - That weakens the exact failure class Worker D was closing: app mirror/deploy/source proof being mistaken for the runtime bootstrap that actually prepared staging.

   Required before staging release gate PASS:
   - Store the current `locally_twisted` installed app hash, expected app hash, and bootstrap app version in the durable status payload.
   - The gate must compare the durable status hash to the expected/current installed hash and fail on mismatch or missing hash.

3. BLOCK - Product-gallery staging proof is still too narrow if this script is the final owner-review gate.

   The hardened gate adds a useful Mickey Mouse Bouquet thumbnail count check, but it still does not prove the Classic Arch desktop/mobile gallery behavior Worker D called out, nor does it run the richer gallery verifier already present in the repo.

   Evidence:
   - Worker D called out Classic Arch/Mickey gallery thumbnails and mobile/desktop behavior: `workstreams/ecommerce-audit/staging-bootstrap-gate-worker-d-review-2026-05-22.md:83` to `workstreams/ecommerce-audit/staging-bootstrap-gate-worker-d-review-2026-05-22.md:96`.
   - The staging gate route list contains `/shop-items/bouquets/mickey-mouse-bouquet` and the `/shop-items/columns` category, but not the Classic Arch product route: `scripts/verify/staging_owner_review_gate.py:42` to `scripts/verify/staging_owner_review_gate.py:48`.
   - The gate checks Mickey thumbnail count exactly `3`: `scripts/verify/staging_owner_review_gate.py:156` to `scripts/verify/staging_owner_review_gate.py:162`.
   - The gate only checks that `/shop-items/columns` looks like a category page: `scripts/verify/staging_owner_review_gate.py:163` to `scripts/verify/staging_owner_review_gate.py:165`.
   - The existing Playwright gallery verifier has the stronger Classic Arch desktop and mobile behavior checks: `scripts/verify/product_gallery_experience.spec.js:18` to `scripts/verify/product_gallery_experience.spec.js:66` and `scripts/verify/product_gallery_experience.spec.js:127` to `scripts/verify/product_gallery_experience.spec.js:170`.

   Impact:
   - This gate can prove one checkout-style product's rendered thumbnail count, but it cannot by itself prove the broader owner-review gallery surface is ready on staging.
   - If the release controller plans to run a separate authenticated staging browser/gallery pass, this can be an explicit separate gate. If this script is the sole staging owner-review gate, it remains blocking.

   Required before staging release gate PASS:
   - Add authenticated staging checks for the Classic Arch product route and either desktop/mobile browser behavior or a clearly separate staging browser gate that must pass before owner-ready signoff.
   - Record that separate gate result next to this gate so "owner-review ready" does not borrow proof from local-only browser tests.

## Non-Blocking Observations

- The source/app mirror target is correctly separated from live/DNS/Stripe/Search Console. This review did not approve any provider mutation.
- `scripts/verify/staging_owner_review_gate.py` is intentionally a real Frappe Cloud gate. Running it would read the default credential file and create a Frappe Cloud site login session via `press.api.site.login` at `scripts/verify/staging_owner_review_gate.py:207` to `scripts/verify/staging_owner_review_gate.py:215`. I did not run it under this source-review-only instruction.

## Commands Run

```powershell
git rev-parse --abbrev-ref HEAD
git rev-parse --short HEAD; git rev-parse HEAD
git log --oneline -20
git status --porcelain=v1
git worktree list
git show --stat --oneline --decorate --no-renames f89e31b
git show --format='%H%n%s%n%ct' --no-patch f89e31b
git ls-remote https://github.com/CBaen/Locally-Twisted-Frappe-App.git HEAD
git ls-remote https://github.com/CBaen/Locally-Twisted-Frappe-App.git refs/heads/main
@'
from pathlib import Path
for path in [
    Path('apps/locally_twisted/locally_twisted/staging_owner_review_bootstrap.py'),
    Path('scripts/verify/staging_owner_review_gate.py'),
]:
    compile(path.read_text(encoding='utf-8'), str(path), 'exec')
    print(f'compile ok: {path}')
'@ | python -
node -e "JSON.parse(require('fs').readFileSync('package.json','utf8')); console.log('package.json parse ok')"
python scripts\verify\staging_owner_review_gate.py --help
```

## Closeout

Stage: source-review artifact for staging gate triad.
Repo/branch: `C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\locally-twisted`, `main`, source `f89e31b`.
Provider/live/git mutation: none.
Files changed by Worker G: `workstreams/ecommerce-audit/staging-bootstrap-gate-worker-g-review-2026-05-23.md`.
