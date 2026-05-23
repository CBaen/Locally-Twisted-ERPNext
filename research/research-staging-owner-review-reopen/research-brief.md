### 1. Want

Get the Locally Twisted ecommerce shop visible on Frappe Cloud staging for Jeff/owner review, with product pages, Product Setup/gallery projection, owner backend access, and marketing reviewer access present on the staging target, while live, DNS, Stripe, Search Console, production indexing, and checkout unpause remain untouched.

### 2. Have

The ERPNext/Frappe v15 Locally Twisted repo is `C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\locally-twisted`. This brief was written against packet source commit `69e4e9f2cf3c97e337b9e8046d4cd86cc5e1b68c`; do not treat that as current `HEAD` after later documentation/archive commits. Re-check `git status -sb` and `git rev-parse HEAD` before producing mutation-capable artifacts. The active lock is `release_locks/locally-twisted-staging-forensic-freeze.json`, status `active`, stage `forensic-freeze`. Local release gates live in `scripts/release/frappe_cloud_release_controller.py` and `scripts/release/release_guard_common.py`. The read-only proof for the packet source shows staging is `Active`, ecommerce paused, public indexing disabled, app order correct, and app hash/app-root mirror still `181076c239b2d1d3d508a41ac471c71f9d2b5158`; mirror freshness is `ok=false` because the mirror lacks `staging_owner_review_preflight.py` and has stale bootstrap code.

### 3. Won't Accept

- No live release, DNS, Stripe, Search Console, production indexing, or checkout unpause.
- No provider/staging/app-mirror mutation while the forensic-freeze lock is active without a valid `freeze-reopen-approval.json`.
- No owner-review-ready claim from local Docker, GitHub commits, app mirror hashes, deploy IDs, or successful read-only provider snapshots.
- No hand-shaped passing artifacts; provider snapshot, app mirror freshness, hosted preflight, and owner-review gate evidence must come from the current verifier/controller paths.
- No secrets, tokens, credential values, raw provider logs, customer records, or session IDs in docs/artifacts.
- No staging bootstrap/import until hosted preflight passes on the actual staging target after app mirror freshness is restored.

### 4. Open To

The next release packet may add local artifact producers or tighten controller gates if they reduce ambiguity before mutation. The app-root mirror sync path can reopen only through a fresh artifact-bound approval and controller pass. Staging data bootstrap/import can happen only after the mirror/deploy/preflight chain proves the target can run the current source safely.

### 5. Questions

1. What exact current artifacts are sufficient for the controller to allow `app_mirror_sync`, and which are still missing?
2. After app mirror sync, what command should produce the post-sync `app-mirror-freshness.json` and what hash should downstream payload/deploy artifacts bind to?
3. Which hosted preflight checks must pass before staging bootstrap/import can run, and which failure would stop the release immediately?
4. What staging owner-review gate evidence proves the owner and marketing accounts exist with the correct roles and the catalog/Product Setup/gallery rows render?
5. Which docs should be updated after each packet so future agents do not confuse source archive, app mirror freshness, provider deploy completion, staging data proof, and owner-review readiness?
