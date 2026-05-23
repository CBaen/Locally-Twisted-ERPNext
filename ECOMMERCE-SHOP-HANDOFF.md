# Ecommerce Shop Handoff

Status as of 2026-05-23 for peer GPT-5.5 Codex/OpenClaw agents.

## Current Repository State

- Branch: `main`
- 2026-05-23 freeze reopen approval timestamp guard:
  `workstreams/frappe-cloud-freeze-approval-timestamp-guard-2026-05-23.md`.
  Future mutation-capable packets now need a current, bounded, ISO-8601
  timezone-bearing `freeze-reopen-approval.json`; expired, malformed,
  future-dated, timezone-less, and longer-than-24-hour approval windows fail
  locally. This is local/offline prevention only and did not mutate provider,
  staging, live, DNS, Stripe, Search Console, app mirror, bootstrap, migrate,
  cache, checkout, or secrets.
- 2026-05-23 latest read-only staging packet:
  `workstreams/release-artifacts/2026-05-23-staging-reopen-fa38bc3-readonly/`.
  This packet is bound to source
  `fa38bc31a120f6d52f1e21e4ab011d5b03c2d74d` and performed no provider or
  staging mutation. It proves staging remains **NO-GO** for owner review:
  app-root mirror/deployed app hash is still `181076c...`, mirror freshness is
  `ok=false`, hosted preflight returns HTTP `417`, catalog/Product
  Setup/gallery rows are zero, owner/marketing users are missing,
  representative routes fail, and the release controller blocks
  `app_mirror_sync` because `freeze-reopen-approval.json` is missing.
- 2026-05-23 Gate/Fixer chain-binding guard:
  `workstreams/frappe-cloud-release-artifact-chain-binding-2026-05-23.md`.
  The release controller now rejects mutation-capable packets whose approval,
  app mirror plan/freshness, provider snapshot, deploy payload, deploy
  completion, or hosted preflight artifacts do not describe the same
  source/hash chain. This is local/offline prevention only; it did not mutate
  provider, staging, live, DNS, Stripe, Search Console, app mirror, bootstrap,
  migrate, cache, checkout, or secrets.
- 2026-05-23 archived snapshot-source read-only staging packet:
  `workstreams/release-artifacts/2026-05-23-staging-reopen-current-head-readonly/`.
  This packet is bound to source
  `69e4e9f2cf3c97e337b9e8046d4cd86cc5e1b68c` and performed no provider or
  staging mutation. The folder name is historical: after this packet was
  committed, repo `HEAD` moved, so it is not mutation-capable proof for a later
  commit. It proves staging remains **NO-GO** for owner review at that packet
  source: app-root mirror/deployed app hash is still `181076c...`, mirror
  freshness is `ok=false`, hosted preflight returns HTTP `417`, catalog/Product
  Setup/gallery rows are zero, owner/marketing users are missing, representative
  routes return `404`, and the release controller blocks `app_mirror_sync`
  because `freeze-reopen-approval.json` is missing.
- Source archive labels for this lane: run `git status -sb` and `git log
  --oneline -5` for current HEAD. Do not treat this handoff as a live HEAD
  oracle. The artifact-chain implementation archive is `3054396 Bind staging
  release artifacts`, with follow-up docs clarification at `a838d8d Clarify
  current release archive`. The previous documentation-parity archive is
  `5e11003 Document release artifact template parity`, and the underlying
  template change is `f5e2e91 Update staging release artifact template`, which
  updates the staging-freeze release packet template so future packets include
  `freeze-reopen-approval.json`,
  `app-mirror-sync-plan.json`, `deploy-completion.json`, and the hosted
  preflight `checks` payload shape. These commits do not create those real
  artifacts, do not reopen forensic-freeze, and do not mutate provider/
  staging/live/DNS/Stripe/Search Console/app mirror/bootstrap/migrate/cache
  state. Handoff:
  `workstreams/frappe-cloud-release-artifact-template-parity-2026-05-23.md`.
- Read-only no-go packet archive: `ceab908 Record staging read-only no-go
  packet`; verify current `HEAD` / `origin/main` with `git status -sb` before
  editing. The initial local release-prevention guard commit
  `58258fd Add release prevention guards` and older closeout baseline
  `1811cd6 Fix ecommerce closeout doc state` are historical anchors, not the
  current source state.
- This file is the front-door handoff for the local ecommerce shop setup and
  staff product-authoring slices.
- 2026-05-23 release-process failure: the Frappe Cloud owner-review staging
  attempt was stopped by GL and is not launch authority. Treat owner-review
  staging as blocked until a new release controller starts from current
  read-only provider state and satisfies the gates in
  `workstreams/frappe-cloud-staging-release-failure-forensics-2026-05-23.md`.
  Do not resume provider/bootstrap mutation from the interrupted session. The
  next fix-agent action list is
  `workstreams/frappe-cloud-release-prevention-action-items-2026-05-23.md`.
- 2026-05-23 release-prevention guard pass: the local/offline lock and
  verifier layer now exists. Active lock:
  `release_locks/locally-twisted-staging-forensic-freeze.json`. Controller:
  `scripts/release/frappe_cloud_release_controller.py`. Local guard command:
  `npm run test:release-prevention`. This command proves the prevention
  architecture only; it does not prove staging data, owner accounts, Product
  Setup/gallery projection, live checkout, DNS, Stripe, Search Console, or
  owner-review readiness.
- 2026-05-23 read-only staging reopen packet:
  `workstreams/release-artifacts/2026-05-23-staging-reopen-readonly/`.
  Controller `read_only_forensics` passed with no provider mutation. Frappe
  Cloud staging is Active, has no running jobs, correct app order,
  `lt_ecommerce_paused=1`, and `lt_public_indexing_enabled=0`, but it remains
  blocked for owner review: all catalog/Product Setup/gallery counts are zero,
  `locallytwisted@gmail.com` and `marketing@exploringnotboring.com` are
  missing, and representative shop/product routes return `404`. The deployed
  app hash/app mirror `181076c239b2d1d3d508a41ac471c71f9d2b5158` also lacks
  the current source `staging_owner_review_preflight.py`, so hosted bootstrap
  preflight is unavailable on staging. Do not bootstrap/import from this
  deployed app.
- 2026-05-23 post-packet docs parity handoff:
  `workstreams/frappe-cloud-doc-parity-ceab908-2026-05-23.md`. This records
  `ceab908` as source archive proof only, not app mirror freshness, provider
  deploy proof, staging data proof, or owner-review readiness.
- 2026-05-23 app mirror freshness guard:
  `scripts/verify/frappe_cloud_app_mirror_freshness.py` is wired into
  `npm run test:release-prevention` in offline self-test mode. Real read-only
  proof is
  `workstreams/release-artifacts/2026-05-23-app-mirror-freshness-readonly/`.
  It proves app mirror hash `181076c...` is missing the hosted preflight module
  and has a stale bootstrap module relative to source `24c8465`. The active
  release lock now blocks `app_mirror_sync`; do not sync the mirror until GL
  explicitly reopens forensic-freeze under an artifact-backed packet.
- 2026-05-23 hosted preflight guard refresh:
  `workstreams/frappe-cloud-hosted-preflight-guard-refresh-2026-05-23.md` and
  `workstreams/release-artifacts/2026-05-23-staging-reopen-readiness-refresh/`.
  The hosted preflight verifier now writes a sanitized artifact, and the
  release controller requires a passing hosted-preflight artifact for future
  `staging_bootstrap`. That artifact must match the provider snapshot site,
  provider target/installed app hash, app-mirror hash, and the hosted
  preflight `required_checks` payload. The current packet remains no-go because
  staging returns HTTP `417` for the preflight method.
- 2026-05-23 post-`ebb7151` read-only proof:
  `workstreams/frappe-cloud-post-ebb7151-staging-readonly-2026-05-23.md` and
  `workstreams/release-artifacts/2026-05-23-staging-reopen-post-ebb7151-readonly/`.
  This pass rechecked staging after source commit `ebb7151` and performed no
  provider/staging mutation. It confirms the app-root mirror/deployed hash is
  still `181076c239b2d1d3d508a41ac471c71f9d2b5158`, the mirror is still
  missing `staging_owner_review_preflight.py`, hosted preflight still returns
  HTTP `417`, staging owner-review data is still zero/missing, and required
  owner/marketing accounts are still absent. Treat `ebb7151` as source archive
  proof only, not staging readiness.
- 2026-05-23 local release-guard gap closure: `npm run
  test:release-prevention` now covers explicit freeze-reopen approval,
  app-mirror pre-sync/post-sync separation, post-deploy/update completion
  artifact validation, and sanitized owner-review release artifacts. This
  removes the local controller deadlock but does not reopen forensic-freeze or
  mutate staging.
- 2026-05-23 Provider Witness recheck after `5e11003`: repo source was clean on
  `main` / `origin/main`; the app-root mirror was still
  `181076c239b2d1d3d508a41ac471c71f9d2b5158`; mirror freshness against
  `5e11003` was still `ok=false`; and the controller blocked `app_mirror_sync`
  with `freeze reopen approval artifact is required before mutation`. The
  current goal/chat context is not enough to create `freeze-reopen-approval.json`.
- Owner Product Setup guard closeout was recovered and triad-reviewed on
  2026-05-22. Owner-like users can use `LT Product Blueprint` / Product Setup,
  but direct raw catalog mutations are blocked and local apply cannot publish,
  hide, or reroute existing public Website Items. Handoff:
  `workstreams/ecommerce-audit/owner-product-setup-guard-closeout-2026-05-22.md`.
- Product option selection UX was repaired locally on 2026-05-22. Selected
  option labels now use short display text while included detail appears
  intentionally in product details, and foil-number add-ons are capped at
  3 digits. Handoff:
  `workstreams/ecommerce-audit/product-option-selection-ux-2026-05-22.md`.
- Category detail heroes were repaired locally on 2026-05-22. All 11
  `/shop-items/<group>` routes now use generated category-specific hero crops
  built from owner/Odoo balloon swatches and exact color names. This is route
  hero art only: ERPNext Item Group `image` fields remain unapproved and
  unchanged. Handoff:
  `workstreams/ecommerce-audit/shop-category-hero-imagery-2026-05-22.md`;
  color authority: `_resources/STYLE-GUIDE-BALLOON-COLOR-ADDENDUM.md`.
- Product page galleries were restored locally on 2026-05-22 as native
  Product Setup -> Website Slideshow architecture. Approved source gallery
  media now creates Product Setup gallery rows, projects to
  `Website Slideshow`, and renders in the product gallery rail. Approved
  simple checkout exact-variant media can join the rail only through active
  Product Setup schema; arbitrary selected-variant/reference/category media
  stays separate. Handoff:
  `workstreams/ecommerce-audit/product-gallery-restoration-2026-05-22.md`.
- Historical Frappe Cloud staging recovery ran on 2026-05-22. Source `main`
  was pushed at `2ca1b85`; the private app-root mirror was pushed at `3e86bc1`; staging
  installed `locally_twisted` app hash is
  `3e86bc149d6dcc04daa194b740c1733f5c796261`. Provider proof shows current
  staging on bench group `bench-40102` / bench `bench-40102-000003-f4v`; live
  remains on bench group `bench-39776` / bench `bench-39776-000015-f94v`.
  Frappe Cloud deploy, site migration, config update, and cache clear
  succeeded with ecommerce paused and public indexing disabled. This is not
  owner-review ready: staging currently has app code but no business data.
  Worker A's target-site proof found `Item=0`, `Website Item=0`,
  `Website Slideshow=0`, `Website Slideshow Item=0`, and missing
  `locallytwisted@gmail.com` plus `marketing@exploringnotboring.com` users.
  `scripts/verify/staging_owner_review_gate.py` is now the mandatory
  executable gate before calling staging owner-review ready; it must fail on
  zero catalog/users even when app deploy succeeded. Handoff:
  `workstreams/frappe-cloud-staging-owner-review-2026-05-22.md`. This section
  is retained as historical evidence only; the old `3e86bc1` staging gate
  command is superseded by the 2026-05-23 forensic-freeze lock and the
  `181076c...` read-only no-go packet.
- Current local product import proof treats all 53 Odoo-imported products as
  real products. Direct checkout is now bounded for high-complexity color
  products: the two graduation products use college color preset checkout
  variants, while hyperspecialized 50+ color products route to quote request
  until their UI/UX, pricing, color logic, and operator flow are approved.
  Do not promote this local proof to public/live without GL local approval
  plus the separate Frappe Cloud, Stripe, DNS, webhook, and live payment
  cutover gates.
- Encanto/simple checkout variant media was repaired after GL caught the
  product page keeping the parent image. Simple `simple_product|checkout`
  variant `Item.image` now renders and cascades; complex/unclassified media
  remains held.
- `Add Foil Number` is confirmed as an add-on, not a required SKU axis. The
  local DB repair disabled 390 stale optional-add-on variants, and
  `seed_catalog.py` now runs that idempotent cleanup after destructive import.
- `College Color Preset` is now a code-owned Item Attribute for the first
  local graduation checkout set: Weber State, University of Utah, BYU, and
  Utah State. `seed_catalog.py` runs the school/seasonal preset repair after
  destructive import so raw graduation color variants do not reappear as active
  checkout choices.
- Current local runtime note: `frontend` has `lt_ecommerce_paused=0` so GL can
  test localhost product/cart behavior. Restore it to `1` after local
  acceptance or before release-packet work.
- `lt_ecommerce_paused=1` is a public/live exposure safety lock, not a reason
  to stop local build/test work. Name the actual blocker when ecommerce work is
  incomplete.

## Release And Staging Gate Integrity

Release processes, major builds, and patch spirals now require triad review
before any commit, push, staging, live, provider, or Search Console claim. For
this ecommerce lane, the staging-safe list is:

1. Confirm the intended source commit, app-mirror commit, staging host, rollback
   path, and whether the push is archive-only or deploy-triggering.
2. Run local hard gates for the changed slice before staging.
3. Prove Frappe Cloud staging deploy/update/migration/cache clear, app order,
   and `lt_ecommerce_paused=1`.
4. Run `python scripts\verify\staging_owner_review_gate.py --expected-hash
   <installed-locally_twisted-hash>` against staging. This gate is mandatory
   before any "owner-review ready" language and must fail if catalog/Product
   Setup/gallery rows or required users are missing, even when app deploy and
   migrate succeeded.
5. Run staging HTTP/browser checks against the staging URL.
6. Run database-side Product Setup/gallery/checkout proof in staging, or mark
   that proof unverified. Do not claim staging from local Docker database reads.
7. Keep live checkout, Stripe, DNS, Search Console, and provider mutations
   behind their separate gates.

2026-05-23 failure-prevention addition: after one provider/bootstrap failure,
stop for forensic classification and write the prevention guard before retry.
After two related failures, all provider mutation stops until a new
artifact-owning triad approves a fresh release plan. A helper opinion is not a
gate; the triad must own concrete artifacts. This is now tracked as
`capabilities/failures/release-controller-churn-after-stop.md`.

Executable local prevention gates now in this repo:

- `release_locks/locally-twisted-staging-forensic-freeze.json`
- `scripts/release/frappe_cloud_release_controller.py`
- `scripts/verify/release_lock_contract.py`
- `scripts/verify/release_controller_contract.py`
- `scripts/verify/frappe_cloud_payload_contract.py`
- `scripts/verify/frappe_cloud_app_mirror_freshness.py`
- `scripts/verify/frappe_cloud_provider_snapshot.py`
- `scripts/verify/staging_owner_review_gate_contract.py`
- `scripts/verify/staging_owner_review_hosted_preflight.py`
- `scripts/verify/staging_owner_review_bootstrap_contract.py`
- `scripts/verify/release_claim_language_contract.py`
- `npm run test:release-prevention`

Provider mutation remains blocked while the forensic-freeze lock is active.
Gate/Fixer witness follow-up on 2026-05-23 is now local/offline code:
reopening staging bootstrap/import requires the expanded prevention suite,
real provider snapshot output, real hosted bootstrap preflight output,
backup-or-zero-data proof before destructive catalog seed paths, and mandatory
payload artifacts for future provider deploy/update controller actions.
The hosted preflight output must be bound to the same staging site and release
hash as `provider-snapshot.json` and `app-mirror-freshness.json`; a hand-shaped
minimal `ok` artifact is not acceptable.
The current read-only packet produced the provider snapshot and tried hosted
preflight; hosted preflight is blocked because staging is still running app
hash `181076c...`, which does not include the source preflight method.
Post-`ceab908` docs parity handoff:
`workstreams/frappe-cloud-doc-parity-ceab908-2026-05-23.md`.

2026-05-22 staging-prep nuance: official Frappe Cloud docs support
`press-deploy` commit markers, including bench-specific markers. For LT, do
not use generic `press-deploy`. Current provider proof supersedes older repo
history: staging is `bench-40102` / `bench-40102-000003-f4v`, and live remains
`bench-39776` / `bench-39776-000015-f94v`. Owner review is blocked until
staging bootstrap/import completes and the mandatory staging owner-review gate
passes. Historical 2026-05-22 blocker language said the blocker was not app
hash because staging had `3e86bc1` installed but no catalog/shop/gallery
records or required users. The current 2026-05-23 blocker is broader: staging
now reports app hash `181076c...`, the app-root mirror is still behind current
source and lacks the hosted preflight method, and the actual staging target
still has zero catalog/Product Setup/gallery rows plus missing owner/marketing
users.

## Completed Lanes

### Product gallery restoration - 2026-05-22

Owner: `Codex` with triad review.

Result: complete locally for product-page additional photos. No staging/live
site update, Frappe Cloud update, DNS change, Stripe live change, Search
Console action, ERPNext Item Group image mutation, or public exposure change
was made.

Feature handoff:

- `workstreams/ecommerce-audit/product-gallery-restoration-2026-05-22.md`

Evidence summary: source/Odoo additional product photos are now role-based
media, not a blanket held bucket. `gallery` media renders only after Product
Setup owns it and the guarded apply path projects it into native ERPNext
`Website Slideshow` rows. `variant_image`, `reference`, and
`ignored_artifact` do not populate the gallery rail. Approved simple checkout
exact-variant media can join the rail only from active Product Setup schema,
which is why published checkout backfills now sit at `Local Preview Ready`
instead of `Draft`. The product image template now reads LT projected gallery
slides before Webshop fallback `slides`, so one-extra projected galleries
render on real product pages.

Green gates:

- `python scripts\verify\product_page_media_classification_packet.py`
- `python scripts\verify\product_page_media_visibility_contract.py`
- `python scripts\verify\product_setup_catalog_coverage.py`
- `python scripts\verify\product_gallery_projection_contract.py`
- `npm run test:product-gallery-experience`
- `npm run test:owner-product-safety`
- `npm run test:ecommerce-full`

Current local counts: `68` approved live Product Setup gallery rows, `47`
Website Items with slideshows, `68` Website Slideshow Item rows, and `30`
published checkout Product Setups at `Local Preview Ready`. The source packet
still records `70` deduped source gallery images because `easter-arch` and
`pride-arch` are source products but not current live Website Items.

### Product option selection UX - 2026-05-22

Owner: `Codex`

Result: complete locally for the screenshot-reported option-text/add-on UX
slice. No staging/live site update, Frappe Cloud update, DNS change, Stripe
live change, or public exposure change was made.

Feature handoff:

- `workstreams/ecommerce-audit/product-option-selection-ux-2026-05-22.md`

Evidence summary: option values that carried both a label and included-copy
detail were showing the full stored text outside the selected button. The UI
now splits display label from included detail, keeps selected tags short, and
renders included detail intentionally in the product details area. Product
Setup copy rules can swap/reset title/story/details. Foil-number add-ons are
still add-ons, not SKU axes, and now validate/price up to 3 digits.

Recovered-lane proof:

- `npm run test:product-options-experience` passed `4/4`.
- Final pre-commit proof also passed `npm run test:product-options-experience`
  `4/4`, and the visible price display plus cart/checkout checks passed inside
  `npm run test:owner-product-safety`.

Rerun before staging if source changes again:

- `npm run test:product-options-experience`
- `npm run test:product-price-display`
- `python scripts\verify\cart_checkout_contract.py`

### Owner Product Setup guard closeout - 2026-05-22

Owner: `Codex` with triad witness/recorder/fixer review.

Result: complete locally for the owner-product safety slice. No staging/live
site update, Frappe Cloud update, DNS change, Stripe live change, Search
Console action, provider mutation, destructive import, or public exposure
change was made.

Feature handoff:

- `workstreams/ecommerce-audit/owner-product-setup-guard-closeout-2026-05-22.md`

Evidence summary: Jeff needs owner control over products, but direct ERPNext
catalog tables are too sharp for daily business editing. The kept path is
Product Setup via `LT Product Blueprint`. Owner-like direct edits to raw Items,
Website Items, Item Prices, option axes/values, Item Groups, Webshop Settings,
and product gallery slideshow records are blocked. Published checkout
backfills are `Local Preview Ready` for runtime media/price preview;
non-checkout backfills stay Draft. Local apply preserves current published state
for existing Website Items and refuses hidden->visible, public->hidden, and
public-route changes outside the reviewed release path. Product Setup sync dry runs now
truthfully report missing-field updates and fill missing rows without wiping
existing options.

Green focused gates:

- `python -m py_compile` for Product Blueprint local apply, Product Blueprint
  verifier, Product Setup sync, DocType controller, and owner catalog guard.
- `python scripts\verify\owner_catalog_guard_contract.py` passed `19/19`.
- `python scripts\verify\product_blueprint_live_contract.py` passed with
  existing-public visibility, hide, and route-change protections.
- `python scripts\setup\sync_product_blueprints_from_catalog.py` dry run
  passed for `51` Website Items, `0` creates, `21` would-update rows.
- `npm run test:owner-product-safety` passed in the final pre-commit state.
- `npm run test:public-network` passed `40/40`.

Remaining before staging: have GL/Jeff test the local owner workflow, then
prepare a separate staging packet. Rerun the owner-product umbrella if source
changes again. This handoff is not live checkout approval.

### Shop category generated heroes and balloon color catalog - 2026-05-22

Owner: `Codex`

Result: complete locally for the route-hero slice. No staging/live site update,
Frappe Cloud update, DNS change, Stripe live change, ERPNext Item Group image
mutation, or public exposure change was made.

Feature handoff:

- `workstreams/ecommerce-audit/shop-category-hero-imagery-2026-05-22.md`

Evidence summary: the previous category pages all inherited the same generic
shop hero image. A first repair using Odoo/photo crops was rejected. The kept
repair generates representative wide hero art per category, prompts with the
category shape plus owner/Odoo balloon color names and swatch references, crops
to the compact hero breakpoints, and maps each `/shop-items/<group>` route to a
unique WebP set. The style guide now has a balloon color addendum with 53
drawer options, swatch references, and best web-match hex values for matching
only. Hex values are not image-generation authority.

Green gates:

- `python scripts\verify\odoo_color_swatch_contract.py`
- `python -m py_compile scripts\setup\generate_shop_category_heroes.py`
- `python scripts\dev\clear_website_cache.py`
- `scripts\verify\run_playwright.cmd test scripts/verify/shop_category_hero_images.spec.js --reporter=line --workers=1`
- `npm run test:public-assets`
- `npm run test:container-contract -- --grep "seasonal-category|shop"`
- `npm run test:layout-fit -- --grep "seasonal-category|shop"`

Remaining before live release: GL local visual review on localhost, then the
normal release gate if approved. Separate future work still owns ERPNext Item
Group `image` field approval for category cards or image-rich menus.

### School/seasonal color preset product logic - 2026-05-18

Owner: `Codex`

Result: complete locally for the first guarded slice. No staging/live site
update, Frappe Cloud update, DNS change, Stripe live change, or public exposure
change was made.

Feature handoff:

- `workstreams/ecommerce-audit/school-seasonal-color-preset-product-logic-2026-05-18.md`

Evidence summary: raw 50+ `latex colors` axes were failing because many
hyperspecialized products were still `complex_custom_product|checkout`.
The new verifier fails that state, then the local repair converts
`graduation-grab-n-go` to 4 college preset checkout variants at $85, converts
`6-graduation-stands` to 2 designs x 4 college preset variants at $45, and
moves 19 school/corporate/seasonal/baby high-cardinality color products to
quote request. Cart API guards now return `quote_required` for those quote
request products. Browser proof confirmed graduation pages render college
preset chips, hide raw `latex colors`, enable Add to Cart with the expected
variant/prices, and store the selected preset label in cart configuration.

Green gates:

- `python -m compileall apps/locally_twisted/locally_twisted/color_preset_rules.py apps/locally_twisted/locally_twisted/seed/repair_school_seasonal_color_presets.py apps/locally_twisted/locally_twisted/verify/school_seasonal_color_preset_contract.py scripts/verify/school_seasonal_color_preset_contract.py scripts/verify/catalog_variant_contract.py`
- `python -m json.tool apps/locally_twisted/locally_twisted/fixtures/item_attribute.json`
- `python scripts\verify\school_seasonal_color_preset_contract.py`
- `python scripts\verify\catalog_variant_contract.py`
- `python scripts\dev\clear_website_cache.py`
- Browser Playwright probes for `/shop-items/grab-go/graduation-grab-n-go`,
  `/shop-items/stands-easels/6-graduation-stands`, and
  `/shop-items/arches/classic-arch`

Remaining before live release: enrich order/invoice/receipt configuration with
structured preset metadata beyond the current selected-option label if GL wants
that explicit downstream fielding, design the quote-request preset/custom color
UI for arches/columns/seasonal/baby products, and get GL local UI/UX approval.

### Catalog optional add-on variant guard - 2026-05-18

Owner: `Codex`

Result: complete locally. No staging/live site update, Frappe Cloud update,
DNS change, Stripe live change, or public exposure change was made.

Feature handoff:

- `workstreams/ecommerce-audit/catalog-optional-addon-variant-guard-2026-05-18.md`

Evidence summary: `catalog_variant_contract.py` caught 13 bouquet templates
with 30 stale enabled `Add Foil Number` variants each. The existing
`repair_optional_addon_variants` routine was run against local `frontend`,
which disabled 390 stale optional-add-on variants and left the 39 required
Bouquet Size variants enabled. `seed_catalog.py` now runs that cleanup after
destructive import so a future import rerun does not rely on a manual memory
step. Product Setup/readiness labels now use `Configurable product page`; the
old `Custom quote page` label remains accepted as a legacy safe alias.

Green gates:

- `bench --site frontend migrate`
- `python scripts\verify\catalog_variant_contract.py`
- `python scripts\verify\product_page_architecture_readiness.py --json`
- `python scripts\verify\product_import_readiness_gate.py --report output\product-import-readiness-gate.json`
- `python scripts\verify\product_blueprint_contract.py`
- `bench --site frontend execute locally_twisted.verify.product_blueprint_contract.run`
- `python scripts\verify\cart_checkout_contract.py`
- `python scripts\verify\variant_media_contract.py`
- `python scripts\verify\checkout_product_family_contract.py`
- `python scripts\verify\product_add_on_dependency_contract.py`
- `python scripts\verify\product_page_runtime_contract.py`

### Variant item media restore - 2026-05-17

Owner: `Codex`

Result: complete locally. No staging/live site update, Frappe Cloud update,
DNS change, Stripe live change, or public exposure change was made.

Feature handoff:

- `workstreams/ecommerce-audit/variant-item-media-restore-2026-05-17.md`

Evidence summary: Encanto Bouquet size variants already had backend
`Item.image` values, but the media API held them because the source extra-image
hold gate had been applied too broadly. Source now routes selected media
through `product_variant_media.py`: Product Setup media wins first, simple
checkout variant `Item.image` is approved selected media, and complex raw Item
media stays held unless Product Setup approves it. Cart, Sales Order payload,
and receipt helpers share the same selected-media path.

Green gates:

- `python -m py_compile apps\locally_twisted\locally_twisted\product_variant_media.py apps\locally_twisted\locally_twisted\api\variant_media.py apps\locally_twisted\locally_twisted\api\cart.py apps\locally_twisted\locally_twisted\product_page_runtime.py scripts\verify\variant_media_contract.py`
- `python scripts\verify\variant_media_contract.py`
- `python scripts\verify\cart_checkout_contract.py`
- `python scripts\verify\product_page_runtime_contract.py`

### All-Odoo sellable product reimport - 2026-05-17

Owner: `Codex`

Result: complete locally. No staging/live site update, Frappe Cloud update,
DNS change, Stripe live change, or public exposure change was made.

Feature handoff:

- `workstreams/ecommerce-audit/odoo-sellable-product-reimport-2026-05-17.md`

Evidence summary: GL corrected the product model: every Odoo-imported product
is a product. The local `frontend` site was backed up, cleaned of two generated
proof products, snapshotted, and reimported with 53 included products, 0
exclusions, and 290 priced sale units. Price enrichment now feeds
`seed_catalog.py`, preventing bouquet-size variants from flattening to the page
base price. Product-level Website Item contracts now outrank stale
item-group/category fallback in product pages, shop cards, and cart display
rows. Browser proof passed all 53 live Website Item routes in two batches under
the 50-line cart cap at desktop and mobile widths, including cart and checkout
preview. `lt_ecommerce_paused=1` was restored and verified.

Green gates:

- `python scripts\verify\product_import_readiness_gate.py --report output\product-import-readiness-gate.json`
- `python scripts\verify\v1_odoo_erpnext_import_manifest.py`
- `python scripts\verify\catalog_purge_scope_dry_run.py`
- `python scripts\verify\product_source_repair_map.py`
- `python scripts\verify\complex_checkout_scaffold.py`
- `python scripts\verify\product_pattern_contract_report.py`
- `python scripts\verify\product_page_architecture_contract.py`
- `python scripts\verify\product_page_runtime_contract.py`
- `python scripts\verify\cart_checkout_contract.py`
- `python scripts\verify\product_variant_price_contract.py`
- `node scripts\verify\post_import_checkout_proof.js` with all-53 manifest/snapshot batch proof
- `python scripts\verify\ecommerce_pause_contract.py`

Remaining local product-data caveats: product-page gallery media is no longer
held under the old blanket extra-image rule; it is approved through Product
Setup and Website Slideshow. Category/reference media and 9 review-only add-on
controls remain separate approval/mapping lanes. Simple checkout variant
`Item.image` is selected media, not gallery media.

### Backend checkout/order wiring - `f82b8ef1`

Owner: `erpnext-backend-specialist`

Result: complete on `main` at `e4186c1`; no backend edits were needed.

Green gates:

- `python scripts\verify\product_pattern_contract.py`
- `python scripts\verify\product_pattern_contract_report.py`
- `python scripts\verify\cart_checkout_contract.py`
- `python scripts\verify\product_page_runtime_contract.py`
- `python scripts\verify\checkout_product_family_contract.py`
- `python scripts\verify\product_add_on_dependency_contract.py`
- `python scripts\verify\checkout_fulfillment_contract.py`
- `python scripts\verify\checkout_lead_conversion_contract.py`
- `python scripts\verify\product_quote_customization_contract.py`
- `python scripts\verify\product_quote_acceptance_contract.py`
- `python scripts\verify\product_quote_operator_review_contract.py`
- `python scripts\verify\product_quote_customer_delivery_contract.py`
- `python scripts\verify\product_quote_operator_send_control_contract.py`
- `python scripts\verify\customer_note_checkout_preservation_contract.py`

Evidence summary after the 2026-05-17 reimport: 53 published/priced Website
Items are checkout-ready at the product-page architecture layer. ProductPatternContract,
selected config, cart line keys, fail-loud checkout blocks, add-on Sales
Order/Sales Invoice line preservation, checkout lead conversion, quote
fallback, and customer note preservation are green.

### Catalog/import and pricing - `4da4b135`

Owner: `catalog-purge-import-executor`

Result: complete. Commit pushed: `9a27b49 treat needs review lane as fail closed catalog state`.

Guarded data repair:

- `python scripts\verify\website_item_classification_contract.py --apply`
- Changed exactly 5 Website Item classification fields to `needs_review|needs_review`.

Current local ERPNext counts after the 2026-05-18 school/seasonal color-preset
repair:

- 53 published Website Items
- 10,686 Items
- 49 templates
- 10,629 variants
- 10,186 active variants
- 443 disabled variants
- 10,668 Item Prices
- 30 Item Attributes
- 32,049 Item Variant Attribute rows

Result: no ERPNext catalog/pricing/import blocker remains for the local setup.

### Media readiness - `d2653ce8` and `d9543e5f`

Owners: `media-classification-sprinter`

Result: complete. Commit pushed: `8e4a95b38822d67300a3c66b17275acaf548e4ee` (`harden ecommerce media readiness contract`).

Files changed in that lane:

- `apps/locally_twisted/locally_twisted/api/variant_media.py`
- `apps/locally_twisted/locally_twisted/catalog_contract/media_classification.py`
- `apps/locally_twisted/locally_twisted/catalog_contract/media_visibility.py`
- `apps/locally_twisted/locally_twisted/catalog_contract/models.py`
- `apps/locally_twisted/locally_twisted/catalog_contract/product_pattern_contract.py`
- `apps/locally_twisted/locally_twisted/catalog_contract/source_builder.py`
- `scripts/verify/product_page_media_classification_packet.py`
- `scripts/verify/variant_media_contract.py`

Evidence summary: superseded by the 2026-05-22 product gallery restoration.
The old lane correctly forced a safe media review boundary but over-described
all source extras as held. Current source media is role-based: approved
product-page `gallery` media projects through Product Setup into native
Website Slideshow rows, simple checkout variant `Item.image` remains selected
variant media guarded by `variant_media_contract.py`, and category/reference
media stays separate until explicitly approved.

### Storefront/product UX and homepage contract - `3132de36`, `4fd5ae4f`

Owner: `ecommerce-webshop-builder`

Result: complete. Commit pushed: `3179463 Align homepage container contract with hidden decor`.

Change: `scripts/verify/layout_helpers.js` rebaselined the homepage container contract to the current committed design where `show_custom_event_decor=False`. This was verifier alignment, not an app behavior change.

Green gates:

- `python scripts/dev/clear_website_cache.py`
- focused container contract
- focused interactive-layout checks
- `python scripts\verify\nav_ia.py`
- `npm run test:search-contract`
- `python scripts\verify\smoke_shop.py`

Remaining broad layout-fit noise is transient ERPNext HTTP 417/502 during long sweeps; exact reruns passed and it is not a product behavior or runner primitive blocker.

### Storefront runner - `786f962e`

Result: complete in `e4186c1 Hide homepage custom decor block`.

Evidence: `run_playwright.cmd` uses Program Files Node and package scripts call the wrapper. Search contract, checkout experience, ecommerce browser proof, and focused interactive layout passed. Broad layout-fit showed 310/312 then exact rerun 2/2 pass; remaining issue is transient ERPNext HTTP behavior only.

### Odoo option-pattern mapper

Older mapper task `991323ce` was already published in `d0d5c41`. No docs work was done by `source-contract-sprinter` for `60a5e721`; this handoff replaces that missing closeout.

### Complex checkout scaffold - 2026-05-12

Owner: `Codex`

Result: complete as local/source scaffolding only. No live site update, Frappe
Cloud update, DNS change, Stripe change, or Website Item lane flip was made.

Files added:

- `apps/locally_twisted/locally_twisted/catalog_contract/complex_checkout_scaffold.py`
- `scripts/verify/complex_checkout_scaffold.py`
- `scripts/verify/complex_checkout_scaffold_contract.py`
- `workstreams/ecommerce-audit/complex-checkout-scaffold-2026-05-12.md`

Green gates:

- `python -m py_compile apps\locally_twisted\locally_twisted\catalog_contract\complex_checkout_scaffold.py scripts\verify\complex_checkout_scaffold.py scripts\verify\complex_checkout_scaffold_contract.py`
- `python scripts\verify\complex_checkout_scaffold_contract.py`
- `python scripts\verify\complex_checkout_scaffold.py`

Evidence summary after the 2026-05-17 reimport: 53 products checked; 53 direct
checkout regression guards; 0 simple lane-flip candidates; 0 complex UI
blockers; 0 add-on or conditional product blockers; 0 needs-review/missing
products; 0 explicit checkout architecture gaps. Generated evidence lives
under ignored `output/complex-checkout-scaffold.*` and can be regenerated.

### Backend product-page architecture contract - 2026-05-12

Owner: `Codex`

Result: complete as source/local architecture. This is the corrected
architecture layer; the complex scaffold is only downstream planning evidence.
Post-review hardening is pushed in `88a708c Harden product page axis
projection`.

Files added/changed:

- `apps/locally_twisted/locally_twisted/catalog_contract/axis_projection.py`
- `apps/locally_twisted/locally_twisted/catalog_contract/product_page_architecture_contract.py`
- `apps/locally_twisted/locally_twisted/catalog_contract/product_pattern_contract.py`
- `apps/locally_twisted/locally_twisted/verify/product_page_architecture_contract.py`
- `apps/locally_twisted/locally_twisted/product_options.py`
- `apps/locally_twisted/locally_twisted/templates/generators/item/item_configure.html`
- `apps/locally_twisted/locally_twisted/templates/generators/item/item_quote_first.html`
- `apps/locally_twisted/locally_twisted/templates/generators/item/item_details.html`
- `scripts/verify/product_page_architecture_contract.py`
- `scripts/verify/product_page_architecture_contract_contract.py`
- `scripts/verify/product_page_architecture_readiness.py`
- `scripts/verify/product_quote_first_experience.spec.js`
- `workstreams/ecommerce-audit/backend-product-page-architecture-contract-2026-05-12.md`

Green gates:

- `python scripts/verify/product_page_architecture_contract_contract.py`
- `python scripts/verify/product_page_architecture_contract.py`
- `python scripts/verify/product_page_runtime_contract.py`
- `docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.verify.direct_checkout_target_contract.run`
- `npm run test:product-quote-first`
- `npm run test:form-experience`
- `python scripts/verify/ecommerce_pause_contract.py`

Expected gated result:

- `python scripts/verify/product_page_architecture_readiness.py --report output/product-page-architecture-readiness.json`
  reports `technical_architecture_ok: True` and `import_reopen_ok: False`
  because the public/live exposure safety lock is on. That lock does not block
  local ecommerce implementation work.

Evidence summary after the 2026-05-17 reimport: 53 product rows are mapped
through the generic receiving architecture and all 53 are checkout allowed.
There are no business quote-first product categories; legacy `quote_first`
values are internal holds only where field names remain. Payload targets are
`selected_options`, `color_recipes`, `add_ons`, and `quote_context`;
product-specific rules are explicitly not allowed.

Post-review axis rule: live ERPNext variant axes are not classified by
attribute name alone. Source/backend recipe patterns keep color axes in
`color_recipes`; missing recipe authority keeps the axis as sale-unit
`selected_options`; explicit single-color sale-unit source markers override
recipe-looking patterns. The browser regression proves `7-butterfly-column`
emits `latex colors -> color_recipes` and preserves the selected color in the
cart payload without leaking it into `selected_options`.

### Product blueprint authoring - 2026-05-14

Owner: `Codex`

Result: complete as a local-only staff product-authoring and unpublished apply
slice. No live site update, Frappe Cloud update, DNS change, Stripe change,
public publish, order, invoice, or Payment Request was made.

Files added/changed:

- `apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_product_blueprint/`
- `apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_product_blueprint_option/`
- `apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_product_blueprint_color_recipe/`
- `apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_product_blueprint_add_on/`
- `apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_product_blueprint_conditional_price/`
- `apps/locally_twisted/locally_twisted/product_blueprint_validation.py`
- `apps/locally_twisted/locally_twisted/product_blueprint_apply_plan.py`
- `apps/locally_twisted/locally_twisted/product_blueprint_local_apply.py`
- `apps/locally_twisted/locally_twisted/product_page_runtime.py`
- `apps/locally_twisted/locally_twisted/product_options.py`
- `apps/locally_twisted/locally_twisted/verify/product_blueprint_contract.py`
- `scripts/verify/product_blueprint_contract.py`
- `scripts/verify/product_blueprint_live_contract.py`
- `workstreams/ecommerce-audit/product-blueprint-authoring-2026-05-14.md`

Green gates:

- `python scripts/verify/product_blueprint_contract.py`
- `python scripts/verify/product_blueprint_live_contract.py`
- `python scripts/verify/product_page_runtime_contract.py`
- `python scripts/verify/product_add_on_dependency_contract.py`
- `python scripts/verify/product_page_architecture_contract_contract.py`
- `python scripts/verify/ecommerce_pause_contract.py`
- `python scripts/verify/verifier_cli_contract.py`

Evidence summary: `LT Product Blueprint` is installed with child tables for
options, color recipes, add-ons, and conditional pricing. Validation maps
employee labels to `simple_product`, `complex_custom_product`, `checkout`,
`quote_first`, `needs_review`, `selected_options`, `color_recipes`, `add_ons`,
and `quote_context`. The dry-run apply plan writes no product records. Desk
apply is role-gated, local-site-config-gated, server-token-gated, and keeps the
generated Website Item unpublished. The rollback-safe verifier proves a
temporary direct-checkout blueprint creates one template Item, two variants,
one Item Attribute, two Item Prices, one unpublished Website Item, zero
orders/invoices/payments, and one checkout-approved fixed-price blueprint add-on
that appears in product options and fails loudly above its quantity max.

## Current Working Position

- Backend ecommerce architecture is green.
- Catalog/import/pricing local setup is green.
- Media readiness is green.
- Storefront product UX/nav/search/homepage verifier alignment is green.
- Runner wrapper is green.
- Complex checkout scaffold is green for local planning and blocks stale
  heuristic lane-flip lists from being used as checkout approval.
- Backend product-page architecture contract is green and emitted to product
  pages as a backend-owned JSON contract.
- Staff product blueprint authoring is green for validation, dry-run preview,
  guarded unpublished local apply, and fixed-price add-on runtime cascade.
- First simple repair-lane backend proof is green: `large-head-missionary`,
  `mothers-day-front-yard-7-column`, `easter-arch`, and `pride-arch` preserve
  source-backed prices and 33 sale SKU lines through Sales Order and Sales
  Invoice in rollback. Local open-mode browser proof is also green at desktop
  and mobile widths for product pages, cart, and checkout preview. Payment
  cascade proof is green for all 33 sale lines through Payment Request, Payment
  Entry, Sales Invoice, receipt email, operator email, welcome email, and
  rollback cleanup. Final owner/product approval and live exposure are still
  pending for that tranche.
- First multi-color repair-lane backend proof is green:
  `7-epic-column`, `baby-shower-combination-photo-opt`, `baby-table-decor`,
  `classic-organic-for-easel`, `number-balloon-columns`, and
  `sleepy-baby-column` preserve source-backed prices and 563 enabled color SKU
  lines through checkout, `color_recipes`, Sales Order, and Sales Invoice in
  rollback. Local open-mode browser proof is also green at desktop and mobile
  widths for product pages, visible color drawers, cart, and checkout preview.
  Payment/customer-message cascade, media update behavior, final owner/product
  approval, and live exposure are still pending for that tranche.
- The shared worktree may still show regenerated audit artifacts under `audits/odoo-erpnext-migration-audit-2026-05-08/`; do not broad-stage them without reviewing the producing lane.

## Remaining Launch Gates

These are not current local ecommerce architecture blockers:

- Frappe Cloud staging deployment and source-freeze review.
- Cloudflare/DNS cutover approval and verification.
- Live Stripe/site-config/webhook setup.
- Legal/policy copy approval where needed.
- One intentional low-risk live payment test after explicit owner approval.
- Final real catalog approval if the visible local product set is being treated as public launch catalog truth rather than architecture/import proof.
- Browser proof of applied blueprint products, richer self-service complex
  authoring UI, conditional pricing runtime, media assignment, broader add-on
  mapping, and refreshed import safety evidence before any product release.

## Do Not Regress

- `quote_first` is a legacy internal hold state, not a business product
  category or permanent product blocker.
- Direct checkout must still be backend-truth driven by Website Item fields, ProductPatternContract, resolver behavior, selected config, item code, price, media, add-ons, cart line key, checkout summary, and SO/SI preserved fields.
- `needs_review` and partial/blank Website Item classification must fail closed.
- Add-ons require explicit mapping, price, quantity/value limits, and SO/SI line preservation before checkout.
- Use the source repair map and complex-checkout scaffold before moving any
  held product into checkout.
  Current source-backed simple-axis candidates are only `large-head-missionary`,
  `mothers-day-front-yard-7-column`, `easter-arch`, and `pride-arch`; their
  backend SO/SI rehearsal and local browser cart/checkout preview are proven,
  and payment/customer-message proof is complete. Do not expose them to
  customers until final owner/product approval is explicit.
- Current source-backed multi-color candidates are only `7-epic-column`,
  `baby-shower-combination-photo-opt`, `baby-table-decor`,
  `classic-organic-for-easel`, `number-balloon-columns`, and
  `sleepy-baby-column`; their backend checkout/SO/SI rehearsal is proven. Do
  not expose them to customers until payment/customer-message, media behavior,
  and final owner/product approval gates pass.
- Product-page controls must be driven by the generic architecture contract,
  not by product-name branches or frontend-only checkout eligibility.
- Color-axis payload targets must come from source/backend semantics, not from
  attribute-name heuristics.
- Staff product creation must stay in `LT Product Blueprint` and its verifiers,
  not developer-only source packets, when the requirement is employee
  self-service authoring.
- Held media must not render as gallery/variant media until classified.
- Use scoped staging only; do not commit regenerated audit artifacts or unrelated changed files.
