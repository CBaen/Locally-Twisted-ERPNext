# Locally Twisted - Coding Handoff

Codex release-prevention guard pass on 2026-05-23: the forensic-freeze state
now has executable local/offline guards. The active lock is
`release_locks/locally-twisted-staging-forensic-freeze.json`. The controller
gate is `scripts/release/frappe_cloud_release_controller.py`; it blocks
Frappe Cloud deploy/provider poll/bootstrap/migrate/cache/live/DNS/Stripe/Search
Console/checkout-unpause actions while the lock is active and requires a
read-receipt, typed payload artifact, failure ledger, provider snapshot, and
artifact-owned triad before future mutation can pass. The guard suite now also
includes a read-only provider snapshot producer self-test, offline staging
owner-review gate contract, and hosted bootstrap preflight/source contract.
Local verifier command: `npm run test:release-prevention`. This is prevention
architecture only. It is not staging proof, owner-review readiness, live
approval, DNS/Search Console/Stripe approval, or checkout exposure.

Codex read-only staging reopen packet on 2026-05-23:
`workstreams/release-artifacts/2026-05-23-staging-reopen-readonly/` is the
current proof packet. It used the release controller in `read_only_forensics`
mode and performed no provider/staging/live/DNS/Stripe/Search Console mutation.
Current staging is `Active`, installed `locally_twisted` hash is
`181076c239b2d1d3d508a41ac471c71f9d2b5158`, app order is correct, running jobs
are empty, ecommerce is paused, and public indexing is disabled. It is still
**not owner-review ready**: staging has `Item=0`, `Website Item=0`,
`LT Product Blueprint=0`, `Website Slideshow=0`, `Website Slideshow Item=0`,
missing `locallytwisted@gmail.com` / `marketing@exploringnotboring.com`, and
representative shop/product routes return `404`. The deployed app-root mirror
is also stale relative to source `e44ecc2`: mirror/app hash `181076c...` does
not contain `locally_twisted/staging_owner_review_preflight.py`, so the hosted
preflight endpoint fails with "module ... has no attribute
`preflight_staging_owner_review_bootstrap`." Next controlled release packet
must sync the app-root mirror from reviewed source, take a fresh provider
snapshot, run the hosted preflight, then bootstrap/import only if the active
lock is explicitly reopened and the controller gates pass.

Codex Frappe Cloud staging failure forensics on 2026-05-23: release execution
was stopped by GL. Treat owner-review staging as **not ready** until a new
release controller proves otherwise from current state. Source `origin/main`
reached `a5fb5f5`; the Frappe Cloud app-root mirror reached
`181076c239b2d1d3d508a41ac471c71f9d2b5158`; the last known provider poll was
interrupted while deploy `52caqn2v57` was running and the installed app hash was
still `3fd5a87eca6a6d2e23c95592f07d41196e4cd68f`. Do not resume mutation from
that momentum. Required reading before any future staging/live action:
`workstreams/frappe-cloud-staging-release-failure-forensics-2026-05-23.md`
and the action-item handoff
`workstreams/frappe-cloud-release-prevention-action-items-2026-05-23.md`.
The release lock, typed-payload validator, circuit breaker helper, controller
CLI contract, claim-language gate, and release-artifact directory contract now
exist locally at commit `58258fd`. The next agent must not rebuild those from
scratch; it must run the prevention gates, take a fresh read-only provider
snapshot, produce the artifact-backed release packet, and keep
`scripts/verify/staging_owner_review_gate.py` as the hard owner-review stop
gate before any new provider mutation is reopened.
Gate/Fixer witness follow-up on 2026-05-23 is now implemented locally:
`scripts/verify/staging_owner_review_gate_contract.py`,
`scripts/verify/staging_owner_review_bootstrap_contract.py`,
`scripts/verify/frappe_cloud_provider_snapshot.py`,
mandatory `--payload-file` for future deploy/update controller actions, and a
hosted bootstrap preflight path that requires real backup evidence or explicit
zero-data proof before destructive catalog seed paths. These are local gates
only; before controlled staging bootstrap/import can reopen, a future release
packet still needs real read-only provider snapshot output and real hosted
bootstrap preflight output from the actual staging target. No provider,
bootstrap, live, DNS, Stripe, Search Console, or checkout mutation was
performed in this guard-hardening pass.

Codex Frappe Cloud staging recovery on 2026-05-22: save state tag
`savepoint/lt-staging-recovery-20260522-173929` exists. Source `main` is
pushed at `2ca1b85 Ensure LT access roles before permission sync`; the private
Frappe Cloud app-root mirror `CBaen/Locally-Twisted-Frappe-App` is pushed at
`3e86bc1 Ensure LT access roles before permission sync`; staging installed
`locally_twisted` app hash is
`3e86bc149d6dcc04daa194b740c1733f5c796261`. Frappe Cloud staging deploy,
site migration, config update, and cache clear succeeded on
`locallytwisted-staging.frappe.cloud`; staging is paused
(`lt_ecommerce_paused=true`) and public indexing is disabled
(`lt_public_indexing_enabled=false`). This is still **not** owner-review ready:
the staging target has app code but no business data. Worker A's staging proof
found `Item=0`, `Website Item=0`, `Website Slideshow=0`,
`Website Slideshow Item=0`, and missing `locallytwisted@gmail.com` plus
`marketing@exploringnotboring.com` user records. The mandatory executable gate
before saying "staging owner-review ready" is
`python scripts\verify\staging_owner_review_gate.py --expected-hash 3e86bc149d6dcc04daa194b740c1733f5c796261`.
It must fail on zero catalog rows or missing users even when Frappe Cloud app
deploy/migrate succeeded. Historical next step at that moment was staging
bootstrap/import for catalog, Product Setup/gallery projection, and required
accounts, then rerun that gate. That path is now superseded by the 2026-05-23
forensic-freeze lock: bootstrap/import may resume only after GL explicitly
reopens release execution and the release controller/artifact plan allows it.
Live, DNS, Stripe, Search Console, and production indexing remain untouched.
Handoff:
`workstreams/frappe-cloud-staging-owner-review-2026-05-22.md`.

Codex release/docs gate integrity patch on 2026-05-22: release processes,
major builds, and patch spirals require triad review before any commit, push,
staging, live, provider, or Search Console claim. Staging proof must be
environment-specific. `product_gallery_projection_contract.py` reads the local
Docker `frontend` ERPNext database; setting `LT_BASE_URL` to a staging URL only
retargets the rendered HTML fetch and does not prove staging Product Setup,
Website Slideshow, app-mirror, site update/migration, or cache state.

Codex product gallery architecture restoration on 2026-05-22: product-page
additional photos are restored as permanent architecture, not staging polish.
The kept chain is source-approved gallery media -> `LT Product Blueprint
Gallery Image` -> ERPNext `Website Slideshow` / `Website Slideshow Item` ->
`Website Item.slideshow` -> the Webshop product gallery template. Source
additional product photos now use explicit roles: `gallery` renders after
Product Setup projection, `variant_image` stays selected-option media only,
`reference` stays retained evidence, and `ignored_artifact` never renders.
Current local proof: `70` deduped source gallery images in the classification
packet, `68` approved live Product Setup gallery rows, `47` Website Items with
slideshows, `68` Website Slideshow Item rows, and `30` published checkout
Product Setups promoted to `Local Preview Ready` so active Product Setup
runtime media is available for local/staging preview. The product image
template now treats `get_product_gallery_slides()` as LT authority and uses
Webshop `slides` only as fallback, so projected one-extra routes cannot
silently render no thumbnail rail. Approved simple checkout exact-variant media
can join the thumbnail set only through active Product Setup schema; arbitrary
variant/reference/category media still cannot populate the rail. Feature handoff:
`workstreams/ecommerce-audit/product-gallery-restoration-2026-05-22.md`;
research brief:
`research/research-product-gallery-architecture/research-brief.md`; failure
recipe: `capabilities/failures/product-gallery-projection-regression.md`.
Verified locally: `python scripts\verify\product_gallery_projection_contract.py`
passed with rendered-route checks, `npm run test:product-gallery-experience`
passed `4/4` including the Mickey bouquet regression, `python
scripts\verify\product_setup_catalog_coverage.py` passed, `npm run
test:owner-product-safety` passed, and `npm run test:ecommerce-full` passed.
This is local-only; no staging/live, Frappe Cloud, DNS, Stripe, or Search
Console action was performed.

Codex owner Product Setup guard closeout on 2026-05-22: the recovered owner
product-management lane is now triad-reviewed and documented in
`workstreams/ecommerce-audit/owner-product-setup-guard-closeout-2026-05-22.md`.
Jeff/owner users keep Product Setup access through `LT Product Blueprint`, but
direct raw catalog edits are blocked for Items, Website Items, Item Prices,
option axes/values, Item Groups, Webshop Settings, and product gallery
slideshow records. Local apply now preserves existing public Website Item
visibility, blocks hidden->visible, public->hidden, and public route-change
requests. Published checkout backfills are `Local Preview Ready` for runtime
media/price preview; non-checkout backfills stay Draft until reviewed.
Product Setup sync dry runs now truthfully report missing-field updates and
fill missing child rows without wiping existing options. Focused local proof:
`python scripts\verify\owner_catalog_guard_contract.py` passed `19/19`,
`python scripts\verify\product_blueprint_live_contract.py` passed including
existing public visibility and route-change guards, and
`python scripts\setup\sync_product_blueprints_from_catalog.py` dry run passed
for `51` Website Items with `0` creates / `21` would-update rows. Final
pre-commit umbrella `npm run test:owner-product-safety` passed. This is
local-only. It is not staging/live release, Stripe, DNS, Search Console, or
Frappe Cloud approval.

Codex product-option UX repair on 2026-05-22: the screenshot-reported behavior
where a selected size/option copied long text outside the button now has a
focused handoff at
`workstreams/ecommerce-audit/product-option-selection-ux-2026-05-22.md`.
Option controls split the short display label from included-copy detail,
selected tags show the short label, intentional included-copy detail renders
inside product details, Product Setup copy rules can swap/reset page copy, and
the foil-number add-on is capped/validated at 3 digits with matching price
display. Recovered-lane proof: `npm run test:product-options-experience`
passed `4/4`; final pre-commit run also passed `4/4`. Rerun if source changes
again before staging.

Codex shop category hero/color-catalog closeout on 2026-05-22: all 11
`/shop-items/<group>` compact hero routes now use category-specific generated
WebP crops instead of the repeated generic shop lifestyle image. The generated
source authority is the owner/Odoo balloon swatch system and exact balloon
color names, not hex-only prompts. Source assets and manifest:
`_resources/generated-hero-sources/2026-05-22/`; color authority:
`_resources/STYLE-GUIDE-BALLOON-COLOR-ADDENDUM.md`; feature handoff:
`workstreams/ecommerce-audit/shop-category-hero-imagery-2026-05-22.md`;
capability: `capabilities/recipes/lt-balloon-color-generated-hero-contract.md`;
research brief: `research/research-shop-category-generated-heroes/research-brief.md`.
This did not mutate ERPNext Item Group `image` fields, did not approve
category card/mega-menu photography, and did not stage or deploy live. Verified
locally: `python scripts\verify\odoo_color_swatch_contract.py`,
`python -m py_compile scripts\setup\generate_shop_category_heroes.py`,
`python scripts\dev\clear_website_cache.py`,
`scripts\verify\run_playwright.cmd test scripts/verify/shop_category_hero_images.spec.js --reporter=line --workers=1`
passed 35/35, `npm run test:public-assets`,
`npm run test:container-contract -- --grep "seasonal-category|shop"`, and
`npm run test:layout-fit -- --grep "seasonal-category|shop"`.

Codex selective indexing gate on 2026-05-21: local source now supports
indexing stable public business pages while keeping unfinished ecommerce out of
public discovery. `seo.py` owns `robots_meta_for_path()` and
`should_noindex_path()`, `sitemap.py` excludes ecommerce discovery paths while
`lt_ecommerce_paused=1`, `/ready-to-order-paused` is always noindex,
`/products` is treated as an ecommerce discovery path, and
`lt_public_indexing_enabled=0` globally noindexes staging/owner-review
environments. Feature handoff:
`workstreams/selective-indexing-gate-2026-05-21.md`; related handoffs:
`workstreams/seo-geo-aeo-contract.md` and
`workstreams/domain-provider-reindex-cleanup-2026-05-19.md`; capability:
`capabilities/recipes/lt-seo-geo-aeo-contract.md`. Verified locally:
`python -m py_compile` for touched Python files, `node --check
scripts\verify\seo_contract.spec.js`, `python
scripts\dev\clear_website_cache.py --restart`, `npm.cmd run
test:seo-contract` passed 13/13, and helper proof confirmed paused
shop/category/product paths noindex while `/contact` remains indexable. Live is
unchanged and still unreleased: `https://locallytwisted.com/sitemap.xml` still
uses the Frappe Cloud vanity host, live `/robots.txt` is blank, and live
`/about` canonical/`og:url` still point at the vanity host. Do not submit
Search Console or request recrawl until this ships through the Frappe Cloud
release gate and live SEO proof passes.

Codex marketing review packet access on 2026-05-21: the external marketing
review lane now includes a protected, generated-at-request-time Marketing
Review Packet download on `/marketing-review`. The packet is generated by
`locally_twisted.marketing_review_access.download_marketing_review_packet`,
requires explicit `LT Marketing Review Access`, and contains public review
links, sitemap/robots links, and no-indexing/no-Desk/no-editing boundaries only.
It does not add DocPerm rows, Desk access, customer records, order/invoice data,
files, or product source exports. Feature handoff:
`workstreams/marketing-review-access-2026-05-15.md`; capability:
`capabilities/recipes/erpnext-external-review-access.md`; guard:
`python scripts/verify/marketing_review_access_boundary.py`. On 2026-05-22 the
standing local reviewer `marketing@exploringnotboring.com` was created as an
enabled `Website User` with only `LT Marketing Review Access`; the human access
matrix now fails if that account is missing, disabled, or broadened. No
staging/live/provider/indexing mutation or Search Console action was performed.

Codex capability graduation adoption on 2026-05-21: LT now carries the global
Capability Graduation Ladder seed as cleanup-first infrastructure. Updated
`capabilities/SCHEMA.md` to v2.5, added
`capabilities/principles/capability-graduation-ladder.md`, added
`capabilities/recipes/capability-graduation-sweep.md`, and opened
`workstreams/capability-graduation-ladder-2026-05-21.md`. This is docs and
capability-root adoption only. No ERPNext DB, product code, staging, live,
provider, DNS, Stripe, public indexing, registry write, or trust promotion was
performed. Next safe step is a read-only graduation audit and small action
packets for high-risk cards. Treat existing LT graph debt as still open.

Codex Ready-to-Order category-menu branch on 2026-05-21: branch
`codex/ready-order-category-menu` changes the public `Ready-to-Order` desktop
submenu, search overlay, and mobile drawer from individual Website Item product
quick links to category links sourced from visible `Item Group` children of
`Shop Items`. The dropdown copy is now customer-facing and source verifiers
reject ERPNext, Website Item, and backend-approval language in the menu. Feature
handoff: `workstreams/ready-to-order-category-menu-2026-05-21.md`; capability
failure card: `capabilities/failures/ready-order-menu-product-dump.md`; nav
recipe update: `capabilities/recipes/frappe-public-nav-business-route-contract.md`.
Fresh branch-level checks passed:
`python -m py_compile apps\locally_twisted\locally_twisted\navbar_context.py scripts\verify\nav_ia.py scripts\verify\smoke_shop.py scripts\verify\ecommerce_pause_contract.py`,
`node --check apps\locally_twisted\locally_twisted\public\js\lt-megamenu.js`,
`node --check scripts\verify\search_contract.spec.js`, and
`python scripts\verify\nav_ia.py`. Codex then repointed the local Docker stack
with a temporary compose override so `http://localhost:8081/` mounts this
worktree instead of the main checkout, cleared website cache, and ran
`python scripts\verify\smoke_shop.py`; it passed with all shop smoke checks.
Direct homepage HTML proof showed category links present, product links absent,
and no ERPNext/Website Item/backend-approved wording. GL confirmed the rendered
local change looks correct on `http://localhost:8081/`. This is local
acceptance only, not staging/live release approval. Do not deploy or promote
this branch live until a separate release gate is explicitly opened and passed.

Codex product-page local review closeout on 2026-05-20: local-only product page
work repaired two customer-facing issues before staging. Mobile product detail
spacing now removes the large dead zone between product image and details, and
the fulfillment panel now follows the Website Item runtime commerce lane
instead of item-group fallback. This keeps Classic Arch and other
`quote_first`/`needs_review` products on quote/install language instead of
showing checkout pickup copy. Classic Arch proof contracts were aligned to
`complex_custom_product|quote_first`, and `smoke_shop.py` now fails if
quote-first product pages show "Pickup is requested at checkout" or omit
"Quoted event work." Feature handoff:
`workstreams/ecommerce-audit/product-page-local-review-2026-05-20.md`; failure
recipe: `capabilities/failures/product-fulfillment-copy-lane-drift.md`.
Verified locally after cache clear/restart: `product_page_runtime_contract.py`,
`proof_product_contract.py`, `commerce_rules_contract.py`,
`npm run test:product-price-display`, `npm run test:variant-media`,
`python scripts\verify\smoke_shop.py`, `npm run test:layout-fit -- --grep
"variant-product|single-product|seasonal-category"` (39/39), and
`python -m py_compile` for touched Python files. No staging/live/Frappe
Cloud/Stripe/DNS/public exposure change was performed. Remaining blocker before
staging: reconcile the broader product-classification guard conflict instead of
applying stale verifier expectations. `quote_event_checkout_boundary_contract.py`
expects `basketball-arch` to be `complex_custom_product|quote_first` while the
current DB has it as checkout, and `website_item_classification_contract.py`
dry-run wants 17 classification changes from an older target model. Do not
apply those classification changes without explicit local review and GL
approval.

Codex ecommerce safety guard closeout on 2026-05-19: the P0 coordination source
is `workstreams/ecommerce-system-safety-guard-plan-2026-05-19.md`, with the
active queue item in `locally-twisted-queue.md`. Five GPT-5.5 worker lanes were
used and integrated locally. No staging/live deploy, Frappe Cloud update, DNS
mutation, Stripe live payment, destructive catalog import, or secret access was
performed. Verified local passes: syntax for touched Python files,
`website_item_classification_contract.py`, `npm run test:shop-smoke`,
`cart_checkout_contract.py`, `product_variant_price_contract.py`,
`npm run test:product-price-display`, `variant_media_contract.py`,
`stripe_amount_parity_contract.py`, `payment_success_reconciliation_contract.py`,
`payment_webhook_contract.py`, `payment_cascade_contract.py`,
`checkout_fulfillment_contract.py`, `checkout_lead_conversion_contract.py`,
`simple_purchasable_payment_cascade_contract.py`,
`npm run test:checkout-experience`, `thank_you_payment_state_contract.py`,
`allow_guest_surface_inventory.py`, and
`product_import_readiness_gate_contract.py`. Follow-up on the same day restored
source-price proof and fresh import-readiness evidence: `stage_seed_data.py`
made `_resources/odoo-live` container-visible, `product_price_modifier_contract.py`
passed for 49 products / 10,186 active variants, fresh snapshot
`current-state-snapshot-2026-05-19-2314` passed, purge-scope dry run passed for
53 templates / 10,629 variants / 10,664 prices, bench backup
`20260519_171525` completed, and guard-path dry run accepted the packet with no
purge/import/delete. Remaining blockers: `product_import_readiness_gate.py` is
11 pass / 1 blocker because final destructive approval has not been renewed for
the 2026-05-19 packet. Permission-bypass review follow-up cleared in the same
track: explicit guard comments were added beside the 32 previously flagged
production `ignore_permissions=True` uses, `ignore_permissions_justification_lint.py`
now passes with 150 bypasses scanned / 0 requiring attention, and
`allow_guest_surface_inventory.py` still passes with 11 guest endpoints / 3
public write endpoints. Public ecommerce is still not release-ready until final
destructive approval and target release gates are explicitly handled. Final
local umbrella rerun after those fixes: `npm run test:ecommerce-full` passed,
including ecommerce pause/open-testing contract, shop smoke, product prices,
visible price display, variant media, checkout experience, checkout
fulfillment, and checkout lead conversion.

Codex domain/provider/reindex cleanup on 2026-05-19: public DNS and Cloudflare
API confirm the current web chain is GoDaddy registrar -> Cloudflare
authoritative DNS -> Frappe Cloud -> ERPNext/Frappe. Cloudflare zone
`locallytwisted.com` is active, nameservers are `edward.ns.cloudflare.com` and
`laura.ns.cloudflare.com`, original nameservers were Bluehost
`ns1.bluehost.com` / `ns2.bluehost.com`, and original registrar is GoDaddy.
Live `https://locallytwisted.com/` returns `200` from `Server: Frappe Cloud`;
the old Hetzner/Odoo IP `5.78.136.133` is reference/decommission scope, not
the current public site path. Reindex blocker found: live sitemap and canonical
metadata currently advertise `https://locallytwisted.v.frappe.cloud` instead
of `https://locallytwisted.com` (29/29 sitemap locs use the vanity host).
Source fix started in `seo.py`, `www/sitemap.py`, and
`scripts/verify/seo_contract.spec.js`, but it is not live until app mirror sync,
Frappe Cloud deploy/site update, cache clear, and live SEO verification pass.
Feature handoff:
`workstreams/domain-provider-reindex-cleanup-2026-05-19.md`; failure recipe:
`capabilities/failures/frappe-cloud-sitemap-public-domain-drift.md`. No
provider cancellation, Search Console submission, DNS mutation, Frappe Cloud
deploy, app mirror push, Google Ads change, Meta change, or live-site deploy
was performed.

Codex ad-account takeover documentation closeout on 2026-05-19: GL clarified
that the goal is account control, not another research crawl. Support evidence
from LT Gmail/Drive identifies Google Ads account `Locally Twisted` / customer
ID `437-723-0551`, historical customer ID `295-025-7991`, ENB manager account
`124-663-1239`, ENB admin-user evidence for `tosh@exploringnotboring.com`, and
the current policy issue on campaign `22063769748`
(`ENB_Sales_Search_Custom Balloon Arches + Delivery - $5/day | 12.27.24`) for
HTTP `404` destination failure. Meta evidence is still not dashboard-complete:
Facebook Business Manager email evidence and ENB/HighLevel
`Facebook Painting Leads` evidence exist, but the Meta ad account ID, current
campaigns, pixels/datasets, lead forms, partners, and billing are unverified.
Feature handoff: `workstreams/ad-account-takeover-2026-05-19.md`; capability:
`capabilities/recipes/ad-account-takeover-provider-control.md`; failure guard:
`capabilities/failures/ad-dashboard-research-vs-control-drift.md`. No ad
account mutation, billing mutation, user/partner/access mutation, website code
change, live deploy, Frappe Cloud, Cloudflare, Stripe, DNS, or production
change was performed. Next agent should open authenticated Google Ads and Meta
Business dashboards first, export access/campaign/billing/tracking/lead-form
state, and only then propose ENB/agency access changes.

Codex school/seasonal color-preset product repair on 2026-05-18: local
ERPNext now blocks the unsafe raw 50+ color checkout path for
hyperspecialized products while keeping them real products. Graduation
Grab n Go now has 4 checkout variants using `College Color Preset`
(`graduation-grab-n-go-WSU`, `-UTU`, `-BYU`, `-USU`) at the original $85.
`6-graduation-stands` now has 2 designs x 4 college presets = 8 checkout
variants at the original $45. Nineteen high-cardinality school/corporate/
seasonal/baby products moved to internal `quote_first` / customer quote
request flow so stale localStorage or direct cart API calls return
`quote_required`. Source-owned repair:
`apps/locally_twisted/locally_twisted/seed/repair_school_seasonal_color_presets.py`;
rules: `apps/locally_twisted/locally_twisted/color_preset_rules.py`;
guard: `python scripts/verify/school_seasonal_color_preset_contract.py`.
Browser proof confirmed the two graduation product pages render college
preset chips, no raw `latex colors` selector, correct enabled Add to Cart
variants/prices, and cart line configuration preserving the selected preset
label. No staging/live/Frappe Cloud/Stripe/DNS/public exposure change was
performed.

Codex variant media regression repair on 2026-05-17: GL caught
`/shop-items/bouquets/encanto-bouquet` keeping the parent image after
Small/Medium/Large size selection even though the backend variant Items still
had size images. The root cause was overbroad media hardening from `019bf27`
/ `8e4a95b`: unclassified source extra/gallery media needed to stay held, but
the API also held simple checkout variant `Item.image` values. Source now uses
`product_variant_media.py` so Product Setup media rules win first, simple
`simple_product|checkout` variant Item images render as selected media, and
complex/custom raw Item images remain held without Product Setup approval.
The selected simple variant image cascades through product page, cart,
Sales Order line JSON, and customer-facing receipt helper. Feature handoff:
`workstreams/ecommerce-audit/variant-item-media-restore-2026-05-17.md`;
failure recipe:
`capabilities/failures/variant-media-overgating-regression.md`. Verified:
`python -m py_compile ...`, `python scripts\verify\variant_media_contract.py`,
`python scripts\verify\cart_checkout_contract.py`, and
`python scripts\verify\product_page_runtime_contract.py`. No live deployment
or Frappe Cloud update was performed. At closeout, local `frontend` ecommerce
is intentionally open with `lt_ecommerce_paused=0` so GL can test
`localhost:8081`; restore it to `1` after local acceptance or before any
release-packet work. GL local testing is still required before any live
promotion.

Codex all-Odoo sellable reimport closeout on 2026-05-17: GL corrected the
catalog contract again: every Odoo-imported product is a product and the local
target is sellable checkout behavior, not a permanent quote-first category.
The local `frontend` ERPNext site was backed up, cleaned of two generated proof
products, snapshotted, and reimported with 53 included products, 0 exclusions,
and 290 priced sale units. The first import proved the all-53 write path; the
second import repaired flattened bouquet-size prices by staging the price
enrichment artifact into `seed_catalog.py`. Product-level Website Item
contracts now outrank stale group/category lane fallbacks in shop cards,
product-page controls, and cart display rows. Browser proof passed for all 53
live Website Item routes in two batches under the cart 50-line safety cap, at
desktop and mobile widths, including cart and checkout preview. Local ecommerce
was restored to `lt_ecommerce_paused=1`; no Frappe Cloud, staging, live,
Stripe live, DNS, or public exposure change was performed. Feature handoff:
`workstreams/ecommerce-audit/odoo-sellable-product-reimport-2026-05-17.md`.
Primary gates: `python scripts/verify/product_import_readiness_gate.py --report
output/product-import-readiness-gate.json`,
`python scripts/verify/v1_odoo_erpnext_import_manifest.py`,
`python scripts/verify/product_variant_price_contract.py`,
`python scripts/verify/cart_checkout_contract.py`,
`python scripts/verify/product_page_architecture_contract.py`,
`node scripts/verify/post_import_checkout_proof.js` with all-53 live-route
batches, and `python scripts/verify/ecommerce_pause_contract.py`.

Codex repo hygiene closeout on 2026-05-17: local `main` is reconciled with
`origin/main` at `d541a0c6fdb12ac280ec7eb044b7a4397be7fd8c`, the working tree
is clean, and only the main LT worktree remains registered. The cleanup
reviewed then deleted two stale detached Codex worktrees after proving they
were clean, ancestor-contained, and had no unique feature value left to apply:
`C:\Users\baenb\.codex\worktrees\84e7\locally-twisted` and
`C:\Users\baenb\.codex\worktrees\lt-backend-checkout-docs-20260503`.
Feature/value review confirmed contact prefill and checkout lead-conversion
work from those worktrees already exists in current `main`. Handoff:
`workstreams/repo-history-and-worktree-cleanup-2026-05-17.md`; capability:
`capabilities/recipes/launch-repo-cleanup-and-evidence-retention.md`.

Codex live inquiry release closeout on 2026-05-16: full repo commit
`631f9a8 Run contact intake schema sync on install` and Frappe app mirror commit
`b4b3bf8 Run contact intake schema sync on install` are live on
`locallytwisted.v.frappe.cloud`. Frappe Cloud site update `b48j584nua`
completed successfully with update job `b48oge6unq`, deploy type `Migrate`,
source bench `bench-39776-000013-f94-virginia`, destination bench
`bench-39776-000015-f94v`, and the site now reports Active with no update
available. Live cache clear job `26es8svcaq` succeeded. Route proof after the
update: `/`, `/#login`, `/contact`, and `/login` all returned HTTP 200 on the
expected public surfaces. The accepted live smoke used contact name
`smoke test from cameron`, created Lead `CRM-LEAD-2026-00013`, stored five
private Lead `File` rows and five `custom_inspiration_photos` rows, sent owner
Email Queue `683s86r04b` to `locallytwisted@gmail.com` with five attachment
refs, and sent customer Email Queue `683suhfaa9` with zero photo attachments.
The staging panic URL was staging, not live: staging root and `/#login`
rendered Sign In because `Website Settings.home_page` and branding fields had
drifted; staging was repaired by setting `home_page=home`, LT app branding,
Standard theme, and clearing cache via Frappe Cloud job `fb85o6ncdh`.

Release-scope warning for the next agent: no uncommitted dirty workspace files
were mixed into the deployed release commits, but the app mirror release scope
was broader than the final two-file commit. Compare the previous live app hash
to the target app mirror commit before promotion, not only `git show HEAD`.
Failure Recipes:
`capabilities/failures/frappe-cloud-app-mirror-release-scope-drift.md` and
`capabilities/failures/frappe-cloud-staging-website-settings-drift.md`.

Codex owner-access hotfix on 2026-05-15: `locallytwisted@gmail.com` now has
immediate local backend access with the temporary owner password
`LocalTemp2026!` until GL changes it later. The account is an enabled
`System User`, defaults to `LT Owner Home`, has owner/operator roles without
`System Manager`, and is the business-owner account for leads/inquiries.
Verification passed with `python scripts/verify/backend_workspace_parity.py`
and `$env:LT_DESK_TEST_USER='locallytwisted@gmail.com';
$env:LT_DESK_TEST_PASSWORD='LocalTemp2026!'; npm run test:desk-owner`.
Access-track handoff: `workstreams/user-access-audit-2026-05-15.md`.

Codex inquiry-form hardening closeout on 2026-05-15: the shared `inquiry-v1`
form now puts Contact Details first, keeps `What are you celebrating?`
optional, removes redundant optional/helper copy, alternates Event Basics to
`#F6F7F8`, widens AM/PM controls, and adds `Even Estimates Help` under event
start/end time. Public submit now requires a signed hidden `lt_form_token` and
empty invisible `website` honeypot; missing/too-fast/stale/honeypot posts fail
before Lead creation, emails, or files. High-confidence sales solicitations are
soft-filtered: save the Lead and customer-safe confirmation path, add audit
evidence, and suppress only the owner "New website inquiry" email. Feature
handoff: `workstreams/inquiry-form-spam-sales-filter-2026-05-15.md`;
capabilities: `capabilities/recipes/shared-inquiry-form-experience.md`,
`capabilities/recipes/erpnext-intake-form-parity.md`, and
`capabilities/recipes/frappe-public-storefront-security.md`; guards:
`python scripts/verify/inquiry_spam_gate.py --base-url http://localhost:8081`,
`python scripts/verify/inquiry_sales_solicitation_filter.py --base-url http://localhost:8081`,
`npm run test:form-experience`,
`python scripts/verify/lead_backend_intake_parity.py`,
`python scripts/verify/contact_service_logic.py --base-url http://localhost:8081`,
`python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --form-path /contact --skip-newsletter`,
`python scripts/verify/book_form_repeat_email_photos.py --base-url http://localhost:8081`,
and `python scripts/verify/customer_email_policy_contract.py`. This source is
now live as part of `631f9a8` / app mirror `b4b3bf8`. The 2026-05-16 live
happy-path smoke proved the shared form can still save a Lead, store photos,
and send the owner/customer queues; rerun the dedicated spam/sales fixture gates
after any future form-security change.

Codex access closeout on 2026-05-15: local human-user access was audited
against the running ERPNext/Frappe site and DB. Current enabled operator
personas are Owner, Manager, Employee, Accountant, Admin/support, Customer
Website User, and Guest; no enabled Supplier user, Maintenance Admin user, or
permanent marketing reviewer user was found. `User Permission` rows are empty,
so the current boundary is role/profile/workspace/portal/hook based. The new
external marketing lane is `Website User` + explicit
`LT Marketing Review Access`, `desk_access = 0`, no DocPerm rows, `/me`
redirect to `/marketing-review`, and backend-sensitive DocTypes denied through
marketing-only hooks. The first guard version used broad/effective role lookup
and misclassified Administrator/bench contexts; it was repaired to require the
explicit `Has Role` child row. Feature handoffs:
`workstreams/marketing-review-access-2026-05-15.md` and
`workstreams/user-access-audit-2026-05-15.md`; capability:
`capabilities/recipes/erpnext-external-review-access.md`; guards:
`python scripts/verify/marketing_review_access_boundary.py`,
`npm run test:marketing-review-access`,
`python scripts/verify/customer_portal_inventory.py --base-url http://localhost:8081 --strict-menu`,
`python scripts/verify/backend_workspace_parity.py`,
`python scripts/verify/finance_workspace_parity.py`,
`python scripts/verify/maintenance_admin_boundary.py`,
`python scripts/verify/custom_doctype_permission_boundary.py`,
`npm run test:desk-personas`, and `npm run test:desk-owner`. Follow-up:
Manager workspace hides catalog tools, but the role matrix still allows
`Item Price` create/write/delete; add failing permission-matrix verifiers
before broad ERPNext role changes.

Codex inquiry-photo hotfix on 2026-05-15: production Lead
`CRM-LEAD-2026-00007` had private File `44b4de500d`
(`/private/files/image.jpg`) but no `custom_inspiration_photos` rows and no
owner Email Queue attachment refs. Source is fixed and pushed in the full repo
as `4422793 Fix inquiry photo storage and owner attachments`; the Frappe Cloud
app mirror is fixed and pushed as `6a06062 Fix inquiry photo storage and owner
attachments`. Local proof passed with customer confirmations attachment-free,
owner notifications carrying queued private File `fid` refs, and CRM photo
rows matching uploaded Files. Live release proof on 2026-05-16 updated the site
to app mirror commit `b4b3bf8` and the accepted real smoke proved Lead
`CRM-LEAD-2026-00013` had five private Lead Files, five CRM photo rows, owner
Email Queue `683s86r04b` with five queued attachment refs, and customer Email
Queue `683suhfaa9` with no photo attachments. Feature handoff:
`workstreams/inquiry-photo-storage-owner-attachments-2026-05-15.md`;
capability:
`capabilities/recipes/erpnext-inquiry-photo-delivery-contract.md`; failure
recipe:
`capabilities/failures/public-form-photo-storage-owner-attachment-gap.md`.

Codex provider connection audit on 2026-05-14: the public Frappe Cloud route
layer is healthy, but direct Frappe Cloud management automation is not proven
as a Codex connector. `https://locallytwisted.com` returned HTTP 200 with
`Server: Frappe Cloud`, and `/api/method/frappe.ping` returned
`{"message":"pong"}`. `python scripts/verify/cloudflare_launch_readiness.py
--base-url https://locallytwisted.com` passed 10 checks with 0 blockers and 0
warnings. `python scripts/verify/frappe_cloud_preflight.py` passed after the
DNS target wording was corrected to recognize `www.locallytwisted.com` pointing
at `locallytwisted.v.frappe.cloud`; the verifier remains read-only and is not
dashboard login proof. On the host, no direct `fcloud`/Frappe Cloud CLI, host
`bench`, or Frappe Cloud env vars were found. Use the documented dashboard,
SSH, browser, or provider API path only after an authenticated management
session exists. Local LT stack was also up with the DB container healthy.
Feature handoff:
`workstreams/frappe-cloud-cloudflare-stripe-launch-2026-05-11.md`; capability:
`capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`.

Codex ecommerce product-blueprint update on 2026-05-14: staff product creation
now has a local ERPNext surface instead of requiring developer-coded product
packets. `LT Product Blueprint` validates product basics, options, color
recipes, add-ons, conditional pricing, page type, buying path, and base price;
previews a no-write apply plan; and can apply locally from Desk only for
`System Manager` / `Item Manager` users when `lt_allow_local_blueprint_apply=1`
is set. Generated Website Items stay unpublished; live approval is blocked; no
Frappe Cloud, DNS, Stripe, order, invoice, Payment Request, or public publish
mutation is part of this slice. Blueprint-authored fixed-price checkout add-ons
now cascade into product options and checkout validation when backed by an
enabled Item and Standard Selling Item Price. Feature handoff:
`workstreams/ecommerce-audit/product-blueprint-authoring-2026-05-14.md`;
capability: `capabilities/recipes/erpnext-product-blueprint-authoring.md`;
guards: `python scripts/verify/product_blueprint_contract.py`,
`python scripts/verify/product_blueprint_live_contract.py`,
`python scripts/verify/product_page_runtime_contract.py`, and
`python scripts/verify/product_add_on_dependency_contract.py`.
`lt_ecommerce_paused=1` remains a live/customer exposure safety lock, not an
implementation blocker for local ecommerce build work.

Codex complex Product Setup media/payment update on 2026-05-17: Product Setup
media rules now support explicit selection combinations, and the server-selected
media image is carried through product page API, cart, checkout, Sales Order
line JSON, Stripe Checkout line images, Sales Invoice/receipt copy, and the
customer receipt thumbnail. Local proof created a 48-variant employee-authored
product with generated/uploaded images and completed one real local Stripe
test-card purchase: `SAL-ORD-2026-00023`, Payment Request
`ACC-PRQ-2026-00020`, Payment Entry `ACC-PAY-2026-00002`, Sales Invoice
`ACC-SINV-2026-00003`, selected image `/files/lt-proof-large-chrome.png`.
The paid-order cascade also now guards two failures found by that proof:
trusted Stripe reconciliation runs with server authority instead of Guest
permissions, and checkout taxes resolve to non-group `LT Sales Tax Payable -
LT` instead of the parent Duties and Taxes account. Local ecommerce was restored
to `lt_ecommerce_paused=1`; no staging/live ecommerce release was performed.
Feature handoff:
`workstreams/ecommerce-audit/generic-product-setup-runtime-2026-05-15.md`;
capability: `capabilities/recipes/erpnext-product-blueprint-authoring.md`;
additional guards: `python scripts/verify/cart_checkout_contract.py`,
`python scripts/verify/stripe_amount_parity_contract.py`,
`python scripts/verify/payment_cascade_contract.py`,
`python scripts/verify/payment_launch_readiness.py`, and
`python scripts/verify/ecommerce_pause_contract.py`.

Codex ecommerce architecture correction on 2026-05-12: product-page receiving
architecture is now explicit and generic through
`lt-product-page-architecture-contract-v1`. The new contract maps
ProductPatternContract/source axes to backend-driven controls, versioned cart
payload targets, server-derived resolver fields, and Quotation/Sales
Order/Sales Invoice line parity. Product pages now emit
`.js-lt-product-page-architecture` JSON; the browser verifier proves it on both
quote-first and ready-to-order product pages. No live site, Frappe Cloud, DNS,
Stripe, destructive import, or Website Item lane update was made. Feature
handoff:
`workstreams/ecommerce-audit/backend-product-page-architecture-contract-2026-05-12.md`;
guards: `python scripts/verify/product_page_architecture_contract_contract.py`,
`python scripts/verify/product_page_architecture_contract.py`,
`python scripts/verify/product_page_runtime_contract.py`, and
`npm run test:product-quote-first`. The readiness gate is expected to report
`technical_architecture_ok: True` and `import_reopen_ok: False` while public
ecommerce live exposure remains locked.

Post-review follow-up published as `88a708c Harden product page axis
projection`: live product-page projection now uses
`catalog_contract/axis_projection.py`. Do not infer `customization` from a
balloon-color-like attribute name alone. Source/backend recipe authority keeps
color axes in `color_recipes`; absent recipe authority keeps ERPNext variant
axes in `selected_options`; explicit single-color sale-unit source markers win
over recipe-looking patterns. The live architecture verifier now checks
source-backed color-axis projection, and `npm run test:product-quote-first`
opens `7-butterfly-column`, selects a visible color, adds it to local cart, and
asserts the cart payload has `color_recipes` with no color in
`selected_options`.

Codex live form/email/Frappe Cloud closeout on 2026-05-12:
`locallytwisted.com` is now serving the Frappe Cloud app release
`72a4se4v64` / app hash `04de8212aa7dbf4895716717865fc6e1029c757b`;
bench deploy `62q1r0otg1` and site update job `15s16992i2` both ended
`Success`. `/contact` and `/balloon-twisting-and-face-painting` pass live
smoke after DNS cutover, and the strict live repeat-email/five-photo verifier
passed against `https://locallytwisted.com` with customer and business
notification Email Queue body/recipient proof. Public success now requires both
current customer confirmation and owner/business notification evidence. The
business owner email goes to `locallytwisted@gmail.com`, uses owner-directed
copy, and includes the same customer-submitted details without internal fallback
markers. Root causes fixed: repeat same-email Lead insert returned 409 because
ERPNext's Email Address link is unique; stale same-Lead Email Queue/Communication
rows were treated as idempotency proof; prior smoke only trusted queue flags;
Frappe Cloud bench deploy hash changed before the site update/migration and
source-owned schema were actually live. Feature handoffs:
`workstreams/form-email-confirmation-regression-2026-05-12.md` and
`workstreams/frappe-cloud-cloudflare-stripe-launch-2026-05-11.md`. Failure
Recipes:
`capabilities/failures/public-form-stale-email-queue-idempotency.md`,
`capabilities/failures/public-form-repeat-email-lead-conflict.md`, and
`capabilities/failures/frappe-cloud-release-site-migration-drift.md`. Guards:
`python scripts/verify/book_form_repeat_email_photos.py --base-url https://locallytwisted.com --admin-base-url https://locallytwisted.v.frappe.cloud --cdp-url http://127.0.0.1:9222`,
`python scripts/verify/smoke_forms.py --base-url https://locallytwisted.com --form-path /contact --skip-newsletter`,
and
`python scripts/verify/smoke_forms.py --base-url https://locallytwisted.com --form-path /balloon-twisting-and-face-painting --skip-newsletter`
with `LT_BACKEND_BASE_URL=https://locallytwisted.v.frappe.cloud` and
`LT_BACKEND_CDP_URL=http://127.0.0.1:9222`.

Codex verifier-runtime closeout on 2026-05-12: Playwright in-file parallelism
is opt-in only. Keep `playwright.config.js` defaults at one worker and
`fullyParallel = false`; use `LT_PLAYWRIGHT_FULLY_PARALLEL=1` only for specs
that prove fixture isolation. Shared ERPNext fixture specs such as
`quote_accept_experience.spec.js` can race if global in-file parallelism is
enabled. Handoff: `workstreams/playwright-verifier-runtime-2026-05-12.md`;
Failure Recipe:
`capabilities/failures/playwright-in-file-parallel-fixture-race.md`; guards:
`node --check playwright.config.js`, `npm run test:quote-accept-experience`,
and `npm run test:form-experience`.

Codex ecommerce review closeout on 2026-05-12: Ready-to-Order nav/search links
now require both owner include and backend Website Item checkout eligibility.
`READY_TO_ORDER_OWNER_INCLUDE_CODES` is an allowlist only; it cannot bypass
`lt_product_page_type = simple_product` and `lt_commerce_lane = checkout`.
The search contract now treats filtered backend-approved quick links as hidden,
not absent. Feature handoff:
`workstreams/ecommerce-audit/ready-to-order-nav-search-backend-gate-2026-05-12.md`;
guards: `python scripts\verify\nav_ia.py` and `npm run test:search-contract`.

Codex ecommerce scaffold update on 2026-05-12: complex product checkout
planning is now source-backed and local-only through
`scripts/verify/complex_checkout_scaffold.py`. After the 2026-05-17 all-Odoo
sellable reimport, the scaffold passes with 53 direct checkout guards, 0
simple lane-flip candidates, 0 complex UI blockers, 0 add-on/conditional
product blockers, and 0 needs-review products. It supersedes older heuristic
quote-first flip lists and does not authorize live site, Frappe Cloud, DNS, or
Stripe exposure. Feature handoff:
`workstreams/ecommerce-audit/complex-checkout-scaffold-2026-05-12.md`; current
closeout:
`workstreams/ecommerce-audit/odoo-sellable-product-reimport-2026-05-17.md`;
guards: `python scripts/verify/complex_checkout_scaffold_contract.py` and
`python scripts/verify/complex_checkout_scaffold.py`.

Codex public-site update on 2026-05-11: `/event-balloons` is removed as a
route, with no redirect and no compatibility page. The app no longer has
`www/event_balloons.*`, the `/event-balloons` route rule, the `/event_balloons`
canonical mapping, footer/search/hero/portfolio links, or sitemap inclusion.
Direct local checks return 404 with no `Location` header for `/event-balloons`
and `/event_balloons`. The four event audience routes remain live. Feature
handoff: `workstreams/event-balloons-route-removal-2026-05-11.md`; guards:
`scripts/verify/nav_ia.py` and `scripts/verify/seo_contract.spec.js`.

Codex homepage update on 2026-05-11: the review proof strip is now
multi-platform: GigSalad, Google, and Facebook appear as unboxed logos with
platform-appropriate proof marks. It intentionally shows no exact review
counts and no visible `reviews` label under the logos. Feature handoff:
`workstreams/homepage-review-platform-proof-2026-05-11.md`; capability:
`capabilities/recipes/homepage-launch-proof-contract.md`.

Codex policy/content update on 2026-05-11: checkout and policy surfaces now
plainly state that checkout email is used for invoices, receipts, support, and
order-related messages. Marketing email is separate and requires newsletter or
marketing opt-in. The BTFP Mirabel twisting photo was also pixel-rotated into
the correct orientation rather than relying on EXIF orientation. Commit
`0e9d4f8` already pushed this code/image slice; the docs below now record it.

Codex backend closeout on 2026-05-11 is historical. The old 48 kept / 5
Classic-excluded local import packet is superseded by the 2026-05-17 all-Odoo
sellable reimport: 53 products included, 0 excluded, 290 priced sale units, all
53 routes browser-proved locally, and `lt_ecommerce_paused=1` restored. Current
front-door handoff:
`workstreams/ecommerce-audit/odoo-sellable-product-reimport-2026-05-17.md`.

Codex update on 2026-05-11: homepage Custom Event Decor is hidden for the
launch page, but its recovery assets are preserved intentionally. The homepage
now sets `show_custom_event_decor = False` and wraps the `lt-categories` block
plus its following divider in that flag. Recovery archive:
`_resources/homepage-custom-event-decor-2026-05-11/`, containing the before-hide
screenshot, extracted SVG icons, and manifest. The next `One of a Kind Designs`
photo swap is a photo-only proof-band task: use whole photos with shadows; do
not add text overlays, cards, background-image crops, fixed-height containers,
or any clipping wrapper.

Codex update on 2026-05-11: signed-in users now have visible logout exits on
public and account surfaces. The public desktop header and mobile drawer show
`Log Out` beside `My Account`; LT account pages show `Log Out` in the top action
area and menu footer; the account-access-blocked state keeps its visible logout
path. Verification used `python -m py_compile`, `node --check`, cache clear,
focused logout Playwright coverage with `LT_DESK_TEST_USER` /
`LT_DESK_TEST_PASSWORD`, header/drawer checks, `nav_ia.py`,
`customer_portal_inventory.py`, and `customer_portal_visual.spec.js`.

Codex update on 2026-05-11: shop smoke closeout `d52c6888` is complete.
`scripts/verify/smoke_shop.py` was rebaselined for the current audience-page
H1 copy, clearing the `/civic-community missing focused page title` blocker.
Closeout command: `npm run test:shop-smoke` passed with
`=== All shop smoke checks PASSED ===`. The ecommerce/webshop lane is now an
open-ecommerce launch-execution lane, not a pause-preservation lane: future
shop/product-page work must be anchored to ERPNext v15.105.0 / Frappe v15
Webshop truth across Item, Item Variant, Website Item, Item Price, Item
Attribute, media/gallery, Webshop Settings, cart/checkout APIs, payments, and
Frappe Cloud persistence. Current visible/imported products are test products
only; the project and launch are real client work. Real catalog claims require
a separate approved product import/catalog proof gate.

Codex backend update on 2026-05-11: product import and payment cutover now have
owned backend launch handoffs. Product import readiness is guarded by
`scripts/verify/product_import_readiness_gate.py` and documented at
`workstreams/ecommerce-audit/product-import-hardening-gate-2026-05-11.md`.
Expected current result is blocked until the import runner has dry-run /
destructive guards, fresh backup/snapshot evidence, approved price/media/add-on
packets, and writes the `lt_product_page_type` / `lt_commerce_lane` plus order
line configuration fields. Payment cutover is documented at
`workstreams/payment-portal-live-cutover-checklist-2026-05-11.md`; local/test
payment contracts are enough for planning but not live approval. Future backend
recommendations must stay anchored to Frappe v15.106.0 / ERPNext v15.105.0,
Webshop, payments, Frappe Cloud Git-backed private bench behavior,
`locally_twisted` installed last, explicit site config keys, and
staging-to-live payment gates. This is a real client project; only the current
visible/imported product records are fixture/test products until a real catalog
import gate passes.

Codex update on 2026-05-11: customer login is now part of the branded
customer/client account product. `/login#login` renders the LT premium-concierge
account doorway, hides public marketing chrome, preserves Frappe's native login
form hooks, and was verified with a temporary Website User signing in through
the visible form and reaching `/me`. `/login#signup` renders branded
invite-only account help; public signup remains disabled and guest public
inquiry/shop/cart/checkout paths stay open. Feature handoff:
`workstreams/customer-client-portal-translation-2026-05-10.md`; capability:
`capabilities/recipes/customer-client-portal-contract.md`. Guards:
`npm run test:customer-login-visual` and `npm run test:customer-portal-visual`.

OpenClaw/Moji update on 2026-05-11 00:02: checkout product-family proof now covers every enabled sellable checkout SKU, not just one sample SKU per checkout Website Item family. Exact current distinction: 15 `simple_product|checkout` Website Item families/pages, 47 enabled checkout sale SKUs, and 86 Sales Order/Sales Invoice rows in the rollback verifier (39 bouquet base rows + 39 foil add-on rows + 7 Easter base rows + 1 Mother's Day base row). Easter Balloon Cups is architecture-verified across all 7 variants but still not public/seasonal launch-approved; Mother's Day remains architecture-verified but held unless timely. Public ecommerce remains paused (`lt_ecommerce_paused=1`), current ERPNext products remain test fixtures, and future catalog truth still requires controlled purge/reupload/import proof. Feature handoff: `workstreams/ecommerce-audit/checkout-enabled-sku-parity-proof-2026-05-11.md`; final receipts: `workstreams/ecommerce-audit/2026-05-10-2330-phase-1-4-shop-audit/checkout-product-family-all-skus-final.json` and closeout in the same folder.

Codex update on 2026-05-11: repo hygiene follow-up closed the forbidden branch
and asset-location regression thread. The linked worktree branch
`ecommerce-phase-1-4-hygiene-20260510` was verified as already contained in
`main`, its linked worktree had no unstaged or untracked files, then the
worktree and branch ref were removed. Local branch state is main-only again.
The three deleted `assets/what we do photos/` images were traced by blob hash to
exact copies in
`C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\locally-twisted-local-drops\landing-page-pics-20260510\`;
the repo keeps Git history plus the local holding copy instead of duplicate raw
launch assets. Feature handoff:
`workstreams/launch-repo-cleanup-2026-05-10.md`; capability:
`capabilities/recipes/launch-repo-cleanup-and-evidence-retention.md`.

OpenClaw/Moji update on 2026-05-10 22:18: GL clarified that current ERPNext products are test products only. Future ecommerce/shop proof must include a controlled purge/reupload/import path that shows products fitting the LT schema populate the correct fields, preserve cascading option logic, and trigger intended automations. Do not perform that purge/reupload as part of this closeout/audit; use current products only as fixtures for verifier coverage.

OpenClaw/Moji update on 2026-05-10 closeout: Phase 4 ecommerce safety was rerun after public-regression cleanup and remains protected. The quote/event boundary verifier still blocks 33 quote-first + 5 needs-review products through product controls, cart API, direct checkout URL, and stale localStorage. A standard-product-page local slice adds runtime page/lane classes, a ready-to-order note, and thumbnail `aria-pressed` sync; `product_page_runtime_contract.py` passes, but this is not import-reopen or live-checkout readiness. The old source extra-image/Website Slideshow approval blocker is superseded by `workstreams/ecommerce-audit/product-gallery-restoration-2026-05-22.md`; remaining product readiness still depends on the current product-authoring/runtime, checkout, payment, and release gates. Product-scope handoff: `workstreams/ecommerce-audit/ready-to-order-product-cut-plan-2026-05-10.md`; recommended first checkout shelf is historical and must not override current Product Setup/runtime evidence.

OpenClaw/Moji update on 2026-05-10 late: ready-to-order ecommerce Phases 1-6 now have local proof/decision artifacts. Phase 5 proves delivery/payment/operator readiness locally: checkout fulfillment delivery fees + pickup + tax boundaries, local Stripe/test payment backend config, mocked webhook handling, paid-order cascade, payment-success reconciliation, operator quote review/send control, customer quote delivery BCC safety, and pause-mode safety all pass. Phase 6 decision: do not open live checkout yet; public ecommerce stays paused with `lt_ecommerce_paused=1` until HTTPS production host, explicit live Stripe/site config, policy approval, webhook setup, and one intentional low-risk real payment test pass. Current evidence: `workstreams/ecommerce-audit/phase-5-delivery-payment-operator-packet-2026-05-10.md` and `workstreams/ecommerce-audit/phase-6-launch-decision-packet-2026-05-10.md`. Safe wording: local ecommerce implementation is complete to the non-live boundary; live launch is an owner/access cutover.

OpenClaw/Moji update on 2026-05-10: ready-to-order ecommerce Phases 1-4 are closed with parent-verified artifacts before Phase 5. Phase 1 repaired checkout/customer-note verifier foundations. Phase 2 applied explicit Website Item contracts: 15 `simple_product|checkout`, 33 `complex_custom_product|quote_first`, 5 `needs_review|needs_review`. Phase 3 originally proved the scoped checkout families; the 2026-05-11 correction now proves all enabled sale SKUs inside those checkout families: 39 bouquet variants, 7 Easter variants, and 1 Mother's Day SKU, with 86 Sales Order/Sales Invoice rows and rollback clean. Phase 4 hardened quote/event boundaries: the 33 quote-first and 5 needs-review products cannot enter paid checkout through product-page controls, cart API, direct checkout URL, stale localStorage, malformed JSON, old cart schema, or unavailable/no-sellable candidates. Direct paid checkout now requires explicit `simple_product|checkout`; blank/partial/inferred fields fail closed. Public ecommerce remains paused by default with `lt_ecommerce_paused=1`; Phase 5 is delivery/payment/operator proof, not launch. Feature handoffs: `workstreams/ecommerce-audit/README.md`, `workstreams/ecommerce-audit/ready-to-order-ecommerce-goal-progress-2026-05-10.md`, `workstreams/ecommerce-audit/phase-4-quote-event-path-hardening-result-2026-05-10.md`, and `workstreams/erpnext-ecommerce-receiving-architecture.md`.

Codex update on 2026-05-11: the Frappe Cloud / Cloudflare / Stripe launch plan
is now a repo-owned cutover gate at
`workstreams/frappe-cloud-cloudflare-stripe-launch-2026-05-11.md`. It preserves
pages/forms-first launch with `lt_ecommerce_paused=1`, blocks live checkout
until staging/live payment/product proof passes, adds
`scripts/verify/cloudflare_launch_readiness.py` for dynamic-route cache/challenge
checks, treats `cf-cache-status: MISS` and every non-bypass cache status as a
dynamic-route blocker, and tightens `payment_launch_readiness.py --mode live`
so HTTPS `host_name` is a hard requirement. Fast guard:
`python scripts/verify/cloudflare_launch_readiness_contract.py`.

Codex update on 2026-05-10: launch repo cleanup is now a documented feature
slice. Raw local photo drops were moved out of the repo to
`C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\locally-twisted-local-drops\`,
stale generated/mirror/research debris was removed, old audience-page contest
output is Git-history-only, and `.gitignore` blocks those drop paths from
returning. Memorial Balloons is separate and not part of this LT launch repo.
Feature handoff: `workstreams/launch-repo-cleanup-2026-05-10.md`; capability:
`capabilities/recipes/launch-repo-cleanup-and-evidence-retention.md`.

Codex update on 2026-05-11: header/banner cleanup is now documented and
guarded as its own feature slice. `Free Event Quote` is top-banner-only,
`Contact Us` remains the menu/drawer CTA, the short-notice banner is a linked
deep-navy `/contact` strip on desktop and mobile, and `Ready-to-Order`, `Cart`,
and `Recent Work` are forbidden from the top banner. The follow-up forensic pass
found the 2026-05-10 brass/gold contract was the regression source, so navy is
now guarded in source and rendered checks. Feature handoff:
`workstreams/public-header-banner-contract-2026-05-10.md`; failure recipes:
`capabilities/failures/public-nav-seo-verifier-drift.md` and
`capabilities/failures/public-header-contrast-safe-area-regression.md`.
Verification: `python scripts/dev/clear_website_cache.py`,
`python scripts/verify/nav_ia.py`, and focused `npm run test:interactive-layout
-- --grep "header|drawer|mega|mobile"` passed 55/55.

Codex update on 2026-05-10: project capabilities are now a visible
agent-neutral root at `capabilities/`, not `.codex/capabilities/`. The
system/user shared root is `C:\Users\baenb\capabilities`, the BBC agency root is
`C:\Users\baenb\projects\Built_by_Cameron\capabilities`, and runtime folders
are adapters or compatibility junctions only. Read `capabilities/INDEX.md`
first, then check `capabilities/failures/` before recipes when touching known
risky surfaces.

Codex update on 2026-05-10: the repeat-email/five-photo public form verifier is no longer allowed to leave fake business records behind. `scripts/verify/book_form_repeat_email_photos.py --base-url http://localhost:8081` now calls `locally_twisted.verify.book_form_repeat_email_photos_cleanup` before/after the live form run and fails if verifier-owned Leads, uploaded Files, Communications, Email Queue rows, Contacts, Tasks, or Comments remain. The prior verifier-owned namespace was cleaned from the local DB: preview now reports 0 remaining `lt-repeat-email-photo-*@example.invalid` Leads/Files/email records. Use `--keep-records` only for intentional debugging. Source handoff: `workstreams/customer-email-policy-boundary.md`; capability: `capabilities/recipes/customer-email-delivery-branding-contract.md`.

OpenClaw/Moji update on 2026-05-10: the focused product-page backend reconciliation brief was moved out of the transient `research/` tree and into `workstreams/product-page-backend-reconciliation-research-brief-2026-05-10.md` with the date/check/confidence researcher contract. Use it for the next narrow question: how stored `Website Item.lt_product_page_type` and `lt_commerce_lane` should move from `needs_review` to explicit native ERPNext behavior without hidden runtime fallback. The old transient research folder was removed so Git only carries the durable workstream artifact.

OpenClaw/Moji update on 2026-05-10: ecommerce audit evidence now lives under `workstreams/ecommerce-audit/`. Treat it as an artifact-gated research packet, not a launch verdict. Lane B (`erpnext-receiving-parity-matrix-2026-05-10.md`), Lane C (`cart-checkout-intent-preservation-audit-2026-05-10.md`), and Lane D (`native-frappe-product-template-architecture-2026-05-10.md`) are present. Lane A (`odoo-source-commerce-map-2026-05-10.md`) and Lane E (`odoo-docs-agent-action-convergence-2026-05-10.md`) are missing and must be treated as `[NO EVIDENCE]` until rerun artifact-first. Do not run Lane F synthesis from routed completion text; named artifacts are the evidence boundary. Feature handoff: `workstreams/ecommerce-audit/README.md`.

Last updated: 2026-05-10 by Codex after the day-of-launch posture moved to pages/forms first with ecommerce hidden. Current peer handoff: fake data is allowed and useful; fake success is forbidden. Ecommerce is preserved and tested, but today's safe live posture can keep it hidden behind the branded pause fallback.

Codex update on 2026-05-10: GL clarified that going live today is
non-negotiable and ecommerce may stay hidden for V1. The local site is
currently configured with `lt_ecommerce_paused=1`; `/shop`, `/cart`, and
`/checkout` show the branded quote fallback. Hidden-commerce launch proof passed
with `python scripts\verify\website_launch_verify.py --with-a11y --with-contact-smoke`
15/15. The ignored `.tmp` preflight snapshot was deleted during launch cleanup;
rerun the verifier/snapshot command if a fresh local artifact is needed.
Earlier open-commerce proof also passed with `npm run test:ecommerce-full` and
`python scripts/verify/product_page_architecture_readiness.py`, but live
commerce still needs staged client review, live payment/DNS cutover, and the
agency preflight/staging-to-live process.

Late 2026-05-10 launch-gate repair: `scripts/verify/website_launch_verify.py`
now waits for localhost before browser sweeps and retries once when the local
site briefly blinks during restart. The stale homepage Custom Event Decor
hide-switch was removed so the homepage again matches the launch contract.
Earlier open-commerce `python scripts\verify\website_launch_verify.py` passed all 12 website
steps while ecommerce was temporarily enabled. The site was later restored to the current pages/forms-first paused posture (`lt_ecommerce_paused=1`). The extra launch checks also passed:
`npm run test:a11y` reported 50 route/viewport axe checks with 0 violations,
`npm run test:a11y-manual` passed, and contact smoke submitted, verified the
backend Lead, then cleaned up its test records.

Codex update on 2026-05-10: accepted product-page quote approvals now fail
loudly unless Sales Order acceptance audit/idempotency fields exist and the
Quotation is marked `Ready For Customer Review`. This closes the direct-token
gap where a submitted/priced but not operator-ready quote could create a draft
Sales Order, and the missing-field gap where source quote and written-approval
fields could be silently skipped. Verifier:
`python scripts/verify/product_quote_acceptance_contract.py`. Feature handoff:
`workstreams/erpnext-ecommerce-receiving-architecture.md`; capability:
`capabilities/recipes/erpnext-ecommerce-receiving-architecture.md`.

Codex update on 2026-05-10: the SEO/GEO/AEO gate is a launch verifier, not a
stale content snapshot. `npm run test:seo-contract` now checks the current FAQ
visible questions against FAQPage JSON-LD, plus canonical routes, sitemap,
business/service structured data, and BTFP image alt text. Feature handoff:
`workstreams/seo-geo-aeo-contract.md`; capability:
`capabilities/recipes/lt-seo-geo-aeo-contract.md`.

OpenClaw/Moji update on 2026-05-10: `/balloon-twisting-and-face-painting` was corrected against GL's exact localhost feedback. The embedded inquiry form now starts with no artist-service checkbox selected; repeat inquiries from the same email are allowed through durable `CRM Settings.allow_lead_duplication_based_on_emails` configuration; and the form's advertised five-photo upload path is guarded by `scripts/verify/book_form_repeat_email_photos.py`. The two service-card photos are now explicit 10-image carousels with prev/next controls and visible status. Source handoff: `workstreams/btfp-service-page.md`; capability: `capabilities/recipes/btfp-live-service-page-contract.md`.

OpenClaw/Moji update on 2026-05-10: the homepage hero now implements GL's seasonal carousel request. First slide is graduation season, followed by Civic & community, Corporate events, Schools & campuses, and Private celebrations audience slides. Source handoff: `workstreams/homepage-seasonal-hero-carousel-2026-05-10.md`; capability: `capabilities/recipes/homepage-launch-proof-contract.md`.

Codex update on 2026-05-10: public inquiry acknowledgments now use the branded
LT email shell with the LT logo, mirrored red balloon-dog footer mark, no
standard ERPNext footer, and the public-form-only dynamic subject `Locally
Twisted U+1F388 Thanks {first_name}! We'll be in touch within a day`.
The form path defers the customer confirmation until after photo upload
handling so it can echo the non-empty submitted fields, free-text notes, and a
reference-file count only when files attach. The message title is `Here is what
we received`, not a repeated subject line. This playful intake shell is not the
default for all email. Paid receipts, first-order welcome, reviewed quote
approval emails, and operator paid-order notices use restrained formal shells
specific to the recipient. Company copies still go to
`locallytwisted@gmail.com` as delivery-safe BCC while the sender is the same
Gmail account behind the routed `@locallytwisted.com` aliases. Keep the playful
subject out of legal, billing, invoice, receipt, and finance/legal emails.
One-page print proof exists for one real queued five-photo form confirmation
only; preview renderings are ignored under `output/email-previews/`. Standalone
browser/PDF review renders cannot resolve queued `cid:` image sources, so any
preview export must rewrite inline Email Queue images to embedded data URLs and
verify every `<img>` loads before review. Do not claim all email families print
to one page until each family has its own actual-HTML PDF proof. Source handoff:
`workstreams/customer-email-policy-boundary.md`; capability:
`capabilities/recipes/customer-email-delivery-branding-contract.md`.

OpenClaw/Moji update on 2026-05-10: GL caught a second significant BTFP nav-removal violation. `Twisting & Face Painting` is restored as a canonical public service lane in desktop nav, mobile drawer, and search quick links, pointing to `/balloon-twisting-and-face-painting`. `Free Event Quote` and `Contact Us` remain `/contact` conversion labels; they do not replace BTFP discovery. `scripts/verify/nav_ia.py` now fails if the canonical lane disappears unless `workstreams/nav-service-removal-approvals.md` contains the exact explicit approval marker. Coordination: `workstreams/menu-content-coordination.md`; feature handoff: `workstreams/nav-service-removal-guard.md`; capability: `capabilities/recipes/frappe-public-nav-business-route-contract.md`.
Codex update on 2026-05-10: GL corrected the stale pause assumption. Public
ecommerce is now in full local testing, so `/shop`, product pages, `/cart`, and
`/checkout` must be exercised as real customer paths. Do not convert that into
a production launch claim: live Stripe/payment, DNS, Frappe Cloud deployment,
client review, and staging-to-live approval remain separate release gates.

Codex update on 2026-05-08: GL also made no monoliths a system-wide law. The
LT lane is `workstreams/no-monolith-operating-contract.md`. Do not expand large
hand-authored source, template, CSS, verifier, script, or project-doc files
without checking whether the new concern should become a module, partial,
helper, recipe, or focused verifier first. Research/reference artifacts are the
intentional long-form exception.

Codex update on 2026-05-08: BTFP restoration is now covered by
`workstreams/btfp-service-page.md` and
`capabilities/recipes/btfp-live-service-page-contract.md`. The approved
route is `/balloon-twisting-and-face-painting`; `/process` stays gone. The
BTFP calculator is row-based: one row per artist, each with its own service and
hours. Do not return to one shared hours input multiplied by artist count.

Codex update on 2026-05-08: catalog variant pricing now has a dedicated
handoff at `workstreams/catalog-variant-price-recovery.md` and capability
recipe at `capabilities/recipes/erpnext-catalog-variant-price-parity.md`.
The bouquet-size family was repaired from Odoo's dynamic resolver and is
guarded by `npm run test:product-prices`.

Codex update on 2026-05-19: GL caught the wider price-identity failure on
`easter-balloon-arch-bunny-ear`, where `20ft` and `25ft` showed the same local
price even though Odoo's dynamic resolver returned `$375` and `$440`. Treat this
as an ecommerce architecture incident, not a one-product import bug. The active
incident lane is
`workstreams/ecommerce-price-identity-incident-review-2026-05-19.md`; failure
recipe is `capabilities/failures/ecommerce-variant-price-source-drift.md`.
Local containment corrected 8,405 `Item Price` rows across 49 variant products /
10,186 active variants, added `scripts/verify/product_price_modifier_contract.py`
and `scripts/verify/product_price_display.spec.js`, and wired the broad
source-price guard into `scripts/verify/website_launch_verify.py`. Do not claim
staging/live/public ecommerce price approval from local repair evidence; rerun
target-site source-price, visible-page, cart/checkout, and payment/accounting
cascade proof first.

Codex update on 2026-05-08: website launch verification and public
microinteractions now have a focused closeout. `npm run test:website-verify`
runs `scripts/verify/website_launch_verify.py` with serialized Playwright
workers by default; `npm run test:launch-verify` adds accessibility and
contact smoke. Whole-card product navigation is covered by
`workstreams/public-site-microinteractions.md` and
`capabilities/recipes/public-site-microinteraction-contract.md`. The red
balloon cursor was retired on 2026-05-08 at GL's request; its CSS/JS assets and
Frappe hook entries are removed. The public favicon is now the red balloon dog
asset at `/assets/locally_twisted/icons/lt-favicon.png?v=20260508-red-dog-1`.

Codex update on 2026-05-08: mobile public chrome and homepage review compactness
are covered by `workstreams/mobile-nav-review-compactness.md`. Mobile search
belongs at the bottom of the drawer, not in the header action row. The mobile
header must stay logo plus cart/menu only. The homepage Google review band now
has a compact mobile sizing contract in `interactive_layout.spec.js`; do not
change review card copy, padding, or marquee structure without rerunning that
contract.

Codex update on 2026-05-08: public storefront security has an active P0
handoff at `workstreams/public-site-security-hardening.md` and capability
recipe at `capabilities/recipes/frappe-public-storefront-security.md`.
The first patch escaped the live `/shop?q=` XSS path, hardened product-gallery
image rendering, and made new inquiry uploads private. Do not call the launch
security lane complete yet: `/thank-you?order=<Sales Order>` still needs a
token-bound receipt design, existing public Lead files need migration/review,
tracked local credentials need rotation/removal from tracked docs, guest
checkout Lead conversion needs payment-boundary review, and `/event-playground`
needs a dev/auth gate or production removal.

Codex update on 2026-05-09: browser/internet verification surfaces were checked
from this repo. `web.run` can search and open/read public pages; repo-local
Playwright can silently launch headless Chromium and capture rendered-page
evidence. The in-app Browser Use plugin path was not available in this session
because its required Node REPL JavaScript execution tool was not exposed. Use
`workstreams/browser-verification-runtime.md` and
`capabilities/recipes/codex-browser-verification-surface.md` before
claiming which web/browser surface proved a customer-facing route.

Codex update on 2026-05-09: paperwork/accountant/operator report paths now
consume `business_automation_index.run(run_runtime_contracts=False)` through
the digest chain. Full verification still runs runtime fake-data contracts, but
Desk/report rendering does not create rollback test Leads, upload blockers, or
document blocker evidence. Run DB-mutating verifiers serially.

Codex update on 2026-05-09, superseded on 2026-05-11 for the customer-facing
screen: `/login#login` is still the Frappe auth route, but LT now owns its
branded customer login shell while preserving native auth hooks. The local
owner/client test account is `lt-owner-temp@example.com`, verified by
`npm run test:desk-owner`; customers do not need login for `/contact`, `/cart`,
or `/checkout`. Paperwork/documentation copy routing is code-owned in
`communication_copy_policy.py`: public/business contact remains
`hi@locallytwisted.com`, but the current delivery-safe internal copy mailbox is
`locallytwisted@gmail.com` because Cloudflare routes the `@locallytwisted.com`
aliases back into the same Gmail account used for SMTP. Do not use
`hi@locallytwisted.com` or `cameron@locallytwisted.com` as internal copy targets
while the sender is `locallytwisted@gmail.com`; use Cameron's non-LT mailbox for
explicit one-time QA/review sends. `email_delivery_guard.py` is wired to
`Email Queue.before_insert` to block those routed-alias loop sends even when a
live probe bypasses the copy helper.
`customer_documents_contract.py`, `payment_cascade_contract.py`, and
`outbound_document_send_readiness_contract.py` prove the current standing
behavior and fail if a routed alias loop is accidentally added as a copy target.

Codex update on 2026-05-11: backend Desk personas are now guarded beyond the
owner route. `sync_backend_workspaces.py` owns deterministic Manager and
Employee workspace shortcut/content sets: Manager keeps inquiry, booking,
customer/contact, job, and add-record actions but no catalog tools; Employee is
narrowed to tasks, task board, booking calendar, and event jobs. `sync_finance_workspace.py`
now keeps Accountant Home to invoices, payment requests, payment entries,
customers, reminder review, journal entries, and chart of accounts, and hides
bank/vendor/payment-term/statement-reminder/employee-payroll setup links until
those lanes are approved and populated. Temp persona users now have explicit
default workspaces. New guard: `npm run test:desk-personas` with
`LT_DESK_TEST_PASSWORD` proves Manager, Employee, and Accountant temp users land
on the personalized Desk views. Run backend/finance syncs serially when applying
both because they both touch User records.

Codex update on 2026-05-11: customer/client portal V1 is now an LT-owned
account product, not styled ERPNext native list pages. `scripts/setup/sync_customer_portal.py`
runs `locally_twisted.seed.sync_customer_portal.execute` to keep public signup
disabled, keep guest shop/cart/checkout boundaries open, set the portal home to
`me`, keep `default_role` empty, expose Customer menu rows for `/account/quotes`,
`/account/events`, `/account/billing`, `/account/files`, `/account/checklist`,
`/account/repeat`, `/account/follow-up`, and `/organization`, hide stock
customer/public routes, and keep supplier routes Supplier-only. Compatibility
route rules send `/quotations`, `/orders`, `/invoices`, and `/addresses` to the
owned LT account routes so customers do not land on raw ERPNext list pages.
Primary guard: `python scripts/verify/customer_portal_v1_contract.py`. Menu
guard: `python scripts/verify/customer_portal_inventory.py --base-url http://localhost:8081 --strict-menu --report output/customer-portal-inventory.json`.
Feature handoff: `workstreams/customer-client-portal-translation-2026-05-10.md`.

Codex update on 2026-05-11: `/me` now renders the account dashboard from
`customer_portal.py` and `customer_portal_pages.py`. The dashboard and owned
routes show all eight modules: Event Details, Quotes, Invoices & Receipts,
Files & Inspiration, Customer Checklist, Repeat Client, After-Event Follow-Up,
and Organization Portal. Customer actions write review/metadata records through
`LT Customer Change Request`, `LT Customer Portal File`,
`LT Customer Checklist Response`, and `LT Organization Portal Membership`.
Customer change/repeat requests do not directly mutate Sales Orders, Addresses,
Quotations, invoices, or payment records. Customer-uploaded portal files now
require a `File` owned by the logged-in customer and already attached to the
same source record before `LT Customer Portal File` can be created; arbitrary
File names and staff-owned files fail loudly. Guard:
`python scripts/verify/customer_portal_home_contract.py`; the broader V1 guard
renders all individual and organization routes as a temporary Customer Website
User, proves the file registration boundary, and rolls back the fake records.

Codex update on 2026-05-10: invite-only customer account provisioning now has a
no-send backend helper at
`apps/locally_twisted/locally_twisted/customer_account_provisioning.py`.
`provision_customer_account(contact_name)` creates or reuses a `Website User`
with the `Customer` role only when the Contact has a primary email and a linked
Customer, links `Contact.user`, blocks missing Customer/email, blocks existing
backend/System User collisions, blocks supplier/customer portal crossover, and
does not send welcome/password emails. Guard:
`python scripts/verify/customer_account_provisioning_contract.py`; it creates
fake Customer/Contact/User cases in a rollback transaction and verifies no Email
Queue or Communication side effects.

## State Of Reality

The ERPNext build is active at `http://localhost:8081`. The project is **a migration of Locally Twisted's business intent + catalog data into a fresh ERPNext install** (frame revised 2026-04-30 — see `locally-twisted-decisions.md`). "Fresh install" — destination is greenfield ERPNext; no auto-translated Odoo modules or DB dumps. "Migration" — catalog records (53 Website Items / 10,578 original variants / 10,613 original catalog Item Prices, ported 2026-04-30), form intent, policies, voice/brand all carried across from the prior Odoo attempt and the legacy `locallytwisted.com` site, and the new storefront replaces `locallytwisted.com` at cutover. The current local DB now has 10,686 Items and 10,668 Item Prices after delivery service Items, support Items, the optional-add-on variant repair, and the college color preset repair.

The catalog port from the old Odoo test deployment appears real, but several docs had stale counts. The Odoo shop at `http://5.78.136.133/shop` was used as the catalog source/reference for that port because GL explicitly named it as the old live account/source for catalog data. That does not make Odoo the product truth for unrelated business scope.

Verified DB counts on 2026-05-18 after the school/seasonal color-preset repair:

| Record | Count |
|---|---:|
| Website Items | 53 |
| Items total | 10,686 |
| Variant templates | 49 |
| Non-variant root Items | 8 |
| Active customer-facing variants | 10,186 |
| Disabled variant records | 443 |
| All variant records | 10,629 |
| Item Prices | 10,668 |
| Item Variant Attribute rows | 32,049 |
| Item Attributes | 30 |

Docs that still mention `10,631 Items`, `10,613 Items`, `10,633 Items`, `10,672 Items`, `10,674 Items`, `10,613 Item Prices`, `10,615 Item Prices`, `10,654 Item Prices`, `10,656 Item Prices`, `8,925 Item Prices`, `4 single-SKU templates`, `6 non-variant root Items`, `10,560 variants`, `10,578 variants`, `10,617 variants`, or `10,227 active variants` as current DB totals are stale. The 8 non-variant root Items are 4 catalog single-SKU products, 2 delivery service Items, and 2 support Items (`ADDON-FOIL-NUMBER`, `LT-PRODUCT-QUOTE-REVIEW`). `Add Foil Number` is optional for bouquet-size products. Graduation products now use bounded college preset variants, so the customer-facing active variant count is lower than the raw color-axis port; disabled legacy add-on/raw-color variants remain in the database as history.

## Current Stopping Point

Record-level fail-loud hardening is the active backend automation handoff from GL/Codex/OpenClaw. All current LT data is fake/test data for automation testing until GL explicitly says otherwise. Use it aggressively to prove automation, but do not treat it as live business truth. The next safe implementation slice is documented in `workstreams/fail-loud-record-level-hardening.md`: create a reusable backend failure recorder, then wire Lead cascade partial failures, checkout note/Lead-conversion failures, paid-order receipt failures, and record-level business automation index rows.

Category browse media is parked as of 2026-05-06. The safe prep work is done: candidate report generation, approval-template generation, dry-run Frappe sync, and unapproved-apply refusal are available. No live Item Group images were assigned, and the latest DB check still showed all 11 customer-facing child Item Groups under `Shop Items` with `image = null`.

Resume the category media lane only after GL/Jeff approve the category image selections. The resume path is: regenerate `output/category-media-candidates.md`, create or update the approval file, mark only approved rows with `approved: true`, dry-run `scripts/setup/sync_category_media.py`, then use `--apply` only for approved selections. Do not assign category media by judgment and do not revive `/shop-by-category`.

## Actually Working, Pending Re-Verification

Verified or updated during the 2026-05-01 storefront correction and contact cleanup passes:

- `/contact` is the canonical customer inquiry form. `/book` returns a 301 to `/contact?intent=quick`; do not rebuild `/book` as a separate public page.
- Fail loudly is now the operating law across LT: forms, automations, payments, documents, customer communication, route/container contracts, verifiers, and agent claims must block false success and leave actionable evidence. Project entrypoint: `capabilities/recipes/fail-loud-operating-law.md`.
- `/balloon-twisting-and-face-painting` is now a contact-led editorial service page using real BTFP information, a brand-blue event suggestion crawl directly after the compact hero, and the shared inquiry form scoped to live artist service choices. The old static short-notice phone/email band is removed. It has no public deposit-checkout CTA. Its customer calculator uses the public `$130` first hour / `$115` additional hour / `$50` deposit-per-artist rules with one row per artist so mixed services can use different hours, and the formula keeps no-discount copy visible.
- `/contact` supports guided prefill for `?service=btfp`, `?service=twisting`, and `?service=face-painting`.
- `scripts/verify/smoke_forms.py` verifies localhost `/contact` submissions through the local Docker/Frappe bench container and cleans up the generated smoke Lead plus linked LT cascade Task. Latest run on 2026-05-10 created marker `SMOKE-TEST-1778380640428736700`, verified it, and reported cleanup OK.
- The shared `inquiry-v1` form submission experience was upgraded on 2026-05-10 for both `/contact` and the BTFP embedded form: it has an accessible progress/status panel, customer-safe failure state, quiet one-button success modal, no forced redirect, no direct `#received` fake-success path, no empty-upload photo warning, and inline cookie notice placement on form pages. The submit UX still fails loudly: it only shows success when the backend response includes `message.ok`. Durable handoff: `workstreams/form-submission-experience.md`; capability: `capabilities/recipes/shared-inquiry-form-experience.md`.
- The contact form service taxonomy is current: `Balloon Decor`, `Balloon Twisting`, `Face Painting`, `Delivery`, `Pickup`, `Events Inquiry`, `Something Else`. Do not reintroduce `Delivery Only`, `Pickup Only`, or `Event Package`.
- `Events Inquiry` is the high-value package planning path. It shows "Let's build a memory", package-piece checkboxes from the homepage custom categories, color prompt, and one planning text area. The server aggregates those values into `custom_package_notes`; no new ERPNext fields were added in this slice.
- `Event Environment` and "Shade is required for outdoor events" only appear for live artist services: Balloon Twisting and Face Painting.
- `Pickup` is stackable with other services and points customers to the locations section. Riverdale is labeled `Northern Utah Location (Residential Address)`.
- Backend Lead/CRM parity is synced: `LT Service Type` now has `Delivery`, `Pickup`, and `Events Inquiry`; stale `Delivery Only` / `Event Package` records are gone; Lead Custom Field labels/depends_on logic match the public form; website submissions populate the Desk Table MultiSelect `custom_event_type`.
- LT CRM pipeline parity is synced: the approved stages `New Inquiry`, `Quote Sent/Awaiting Approval`, `Approved`, `In Production`, `Event/Post Event`, and `Archive` live on `Lead.custom_pipeline_stage` and drive `LT Inquiry Board`. Native ERPNext `Lead.status` remains intact. `Archive` is off-board only, not a finance/win-rate trigger.
- LT CRM stage movement now creates/closes operational Tasks only. `stage_cascade.py` creates the next Task for non-Archive stages and closes open cascade Tasks on `Archive`; it does not create quotes, orders, invoices, payments, customers, or win/loss reporting state.
- Backend schema inventory is now repeatable with `python scripts/verify/backend_schema_inventory.py`. Latest live pass found 12 Leads, 25 Contacts, 4 Customers, 8 Sales Orders, 8 Payment Requests, 1 Sales Invoice, 0 Tasks, 106 Custom Fields, 103 Property Setters, and 5 custom/LT DocTypes. The inventory classifies 41 Custom Fields as code-owned and 65 as unclassified DB/app-owned records that still need keep/hide/export decisions.
- Existing `/checkout` is already the finance path: it creates/reuses Customer/Contact, creates Sales Order, creates Payment Request, and sends the customer to Stripe. `/payment-success` and the Stripe webhook reconcile paid orders by marking Payment Request paid, creating Sales Invoice, and sending paid-order emails. Do not add manual stage-to-finance automation until this existing path is coordinated with the custom LT pipeline.
- Checkout/Lead conversion parity is now coordinated with the custom LT pipeline. If checkout uses an email already tied to a Contact linked to a Lead, it converts native `Lead.status`, fills `Lead.customer`, moves `Lead.custom_pipeline_stage` to `Approved`, closes the old New Inquiry Task, and opens the Approved follow-up Task. Verified by `python scripts/verify/checkout_lead_conversion_contract.py`, which rolls back its generated records.
- Checkout commerce rules are now coordinated with fulfillment, tax, and inquiry lanes. Ready-to-order goods can check out; custom/quote-required products and out-of-area delivery stay in the quote/Lead path. Standard local delivery is `$15`, Park City delivery is `$50`, and past fulfillment dates are rejected server-side.
- Checkout tax now separates jurisdiction from taxable base. ZIP/city selects the Utah rate, but only goods are taxable. Services, face painting, balloon twisting, deposits for those services, and delivery charges are non-taxable. The local stack has a 0 percent `LT Non-Taxable Sales` Item Tax Template; delivery fee lines and `Services` item-group lines use that non-taxable override in Sales Orders.
- Contact/Lead intake now records service payment guidance fields: payment timing, deposit due, balance timing, and payment notes. Artist services use `$50 per artist` deposit guidance; mixed artist + decor/event inquiries preserve that deposit note and include the full-before-prep guidance for quoted work. This is guidance only, not an automatic service/deposit finance record.
- Header/menu uses the deliberate premium two-level mega-menu: full-height Locally Twisted logo image, a non-link `Event Balloons` audience dropdown, `Twisting & Face Painting`, `Portfolio`, `About Us`, `FAQ`, top utility row, search overlay, and `Contact Us` CTA in the current pages/forms-first launch posture with `lt_ecommerce_paused=1`. `Ready-to-Order` and cart are preserved behind the config gate and return when `lt_ecommerce_paused=0`; `/shop`, `/cart`, and `/checkout` redirect to the branded quote fallback while paused. `Twisting & Face Painting` points to `/balloon-twisting-and-face-painting`; the event dropdown links only to `/civic-community`, `/corporate-events`, `/schools-campuses`, and `/private-celebrations`; `Contact Us` points to `/contact`; top-banner `Free Event Quote` points to `/contact` and the account link remains. The short-notice copy `SHORT NOTICE? LET US KNOW. WE CAN OFTEN HELP WITH 24 HOURS NOTICE!` is a centered deep-navy `/contact` link on desktop and a matching visible deep-navy `/contact` strip on mobile; the old `Prepared design, clean installs, and invoiced event support across Utah.` proof copy and delivery/truck icon are removed. Menu coordination lives at `workstreams/menu-content-coordination.md`; route removal handoff is `workstreams/event-balloons-route-removal-2026-05-11.md`; the active service-removal guard handoff is `workstreams/nav-service-removal-guard.md`; the older BTFP/Process correction handoff remains historical context at `workstreams/nav-btfp-process-correction.md`.
- Mobile header compactness is now part of the nav contract: in hidden-ecommerce launch mode the header row carries logo and menu, with shop/cart chrome removed. Search lives as a bottom drawer button when ecommerce is open, opens the overlay, closes the drawer first, and submits to `/shop`; `/search` is kept as a no-cache 404 fallback, not a public page.
- Header color repair completed 2026-05-06 after GL flagged the all-black chrome as off-style and was corrected again 2026-05-11 after the short-notice banner regressed to brass/gold. The mega-menu contract stayed intact, but `lt-mega-menu.css` now uses a style-guide split: deep-navy desktop/mobile short-notice strips, warm-white text, warm-white mobile header/drawer surfaces, berry CTA, and brass accents. `hooks.py` cache-bust is `lt-mega-menu.css?v=20260511-blue-banner-2`, and `interactive_layout.spec.js`, `nav_ia.py`, and `smoke_shop.py` guard against regressing the short-notice strips away from navy.
- `/portfolio` and `/balloon-twisting-and-face-painting` are real public routes and return 200 locally. `/event-balloons` and `/event_balloons` are intentionally removed and return 404 with no redirect. `/process` was unapproved and has been removed from the customer-facing site contract. `/portfolio` now keeps only the approved collage-of-imagery and movement behavior from the external prototype: native LT shell/global typography, branded compact portfolio hero, 1.5x larger desktop installed-work images, frequent center-column photos, optimized WebP derivatives, no cropped cards, no captions, no visible frame wrappers, no route-specific Inquire/Studio/Index footer block, actual image dimensions, mobile full-width slide-in reveal, and click-to-front interaction. Do not reintroduce the copied prototype hero, portfolio-specific font imports, custom cursor, fake internal nav/shell, static mobile stacking, photo captions, frame/card wrappers, forced design-slot aspect ratios that create letterbox stripes, route-local portfolio contact/index/footer sections, or full Claude/designer page styling. Category/event query links still filter the photo payload server-side. The research folder remains critique input only; the Frappe implementation, optimized assets, and verifier are the kept production source.
- The mega-menu source contract is active: `navbar_context.py`, `templates/includes/navbar/navbar.html`, `public/css/lt-mega-menu.css`, and `public/js/lt-megamenu.js` must stay in parity with `hooks.py`, `nav_ia.py`, and `smoke_shop.py`.
- Footer no longer exposes `What We Make` or `Book an Event`; `All Ready-to-Order` is config-gated and hidden in the current pages/forms-first launch posture, and `Twisting & Face Painting` remains visible as a service lane.
- Product detail/configure templates no longer include the "Start a conversation" or "Tell us what you're imagining" sales-pitch blocks.
- `/shop-items/arches` now scopes to Arches. Root cause was missing Webshop `.item-group-content` class in the custom Item Group wrapper, not catalog data.
- `/shop` is the customer-facing all-decor hub. `/shop-items`, `/all-products`, and `/shop-by-category` route or redirect to `/shop`; individual category pages remain at `/shop-items/<group>`.
- Public microinteractions are production app assets, not demo pages. The red balloon cursor is retired and should not be reintroduced without a fresh GL decision. Product cards on `/shop` and Webshop-rendered category pages are whole-card clickable from non-interactive card areas, while `Add to cart`, `Choose options`, `Request quote`, selectors, links, modified clicks, and text selection keep their normal behavior.
- Shop category navigation was repaired 2026-05-06 after GL rejected the button/tile treatment: `/shop` and `/shop-items/<group>` now share `templates/includes/shop_category_nav.html`; desktop uses a slim left rail, mobile uses a native select, and future work must not restore `/shop` chips or the category-page button wall.
- Project-level Codex capabilities are installed at `capabilities/` and routed from `AGENTS.md`; ephemeral Codex validation found the index and read the `screenshot` ingredient.
- `/book` is retired as a customer-facing page and redirects to `/contact?intent=quick`. Current CTAs should use `/contact`; old `/book` traffic is compatibility only.
- `/privacy` and `/terms-of-service` exist as static Frappe routes and return HTTP 200 locally. Current copy reflects GL business-proxy answers from 2026-05-06 for delivery, returns, tax wording, cookies/tracking, children/privacy, opt-out event photo use, invoice acceptance, and temporary balloon/service limitations. A sitewide cookie/tracking accept/decline notice stores `lt_cookie_consent`; future optional analytics/ads/tracking must honor that stored choice. Legal/accounting review and Stripe Dashboard URL wiring are still separate follow-ups.
- Customer-facing policy documents now use anchored lanes on `/terms-of-service` and `/refund-policy`: event balloon decor, ready-to-order pickup/delivery, face painting/balloon twisting, and corporate invoicing. `locally_twisted.policy_documents` owns reusable policy blocks for code-owned receipt/inquiry emails. Do not add ERPNext Terms/Email Template records unless a verified customer-facing invoice path truly requires them; LT should stay as whitelabel/code-owned as possible. Run `python scripts/verify/customer_documents_contract.py` after changing customer document copy.
- Branded Sales Invoice output is now code-owned. `scripts/setup/sync_invoice_branding.py` creates/updates the `Locally Twisted Sales Invoice` Print Format, `Locally Twisted` Letter Head, and the Sales Invoice `default_print_format` Property Setter. The Print Format itself carries the visible logo/contact header so the normal default print view is branded. The default invoice is intentionally black/white/gray and accounts-payable friendly; gray vertical callouts are allowed for secondary AP/terms information, and the bottom support banner stays solid black with the approved customer-service/repeat-order copy. Keep dog-logo, gold, patriotic/civic proof, and marketing-style decoration for proposals, event packets, reorder follow-ups, portfolio, and client-facing marketing surfaces, not ordinary Sales Invoices. The current format uses smaller sizing, scoped table padding, fewer outlined containers, horizontal rules, and neutral gray left-rule callouts so ordinary invoices fit one PDF page. `scripts/verify/invoice_branding_contract.py` verifies the records, default print render, logo asset, AP fields, gray callouts, black support-banner treatment, forbidden gold/dog/promo markers, and rendered invoice HTML against `ACC-SINV-2026-00001`.
- Standard outbound document source now lives at `apps/locally_twisted/locally_twisted/outbound_documents/`. It includes an automation registry plus source templates for Sales Invoice, Payment Receipt, Quote / Estimate, Event Proposal Packet, Vendor Setup / W-9 Packet, Statement Of Account, Payment Reminder Draft, Event Install Work Order, Contract Acceptance Summary, and Post-event Reorder Follow-up. These are generator-ready with review gates; they do not authorize automatic sending. The standing outbound standard is answer-first: customer-facing document previews should show `Key fields to review` before internal automation concerns, and every source template must include `## Answer First`. `scripts/verify/outbound_documents_contract.py` guards the registry and required template fields. `scripts/verify/render_outbound_document_previews.py` renders fake-data normal/outlier HTML, PDF, and PNG review artifacts; the current answer-first set is at `output/playwright/outbound-documents-answer-first-20260506/index.html`.
- Business automation indexing is now code-owned and scheduled. `workstreams/business-automation-index.md` is the cross-system map; `locally_twisted.verify.business_automation_index.run` classifies intake, CRM, checkout, payment, paperwork, finance, and checkup surfaces as connected, partially connected, missing-required, or missing-useful. `python scripts/verify/business_automation_index.py` passed on 2026-05-10 in open ecommerce testing with 27 connected surfaces, 3 exists-but-not-connected future/setup surfaces, 0 missing required/useful surfaces, and 0 loud-failure gaps. The index now exposes `runtime_contracts_executed`; internal reports/digests call it with runtime contracts disabled so Desk review paths do not create rollback fake-data records. `hooks.py` runs `locally_twisted.verify.business_automation_index.scheduled_checkup` daily; if a launch-required connection breaks or a loud-failure gap appears, it writes a Frappe Error Log.
- Synthetic backend operating readiness is separate from live cutover readiness. `scripts/verify/synthetic_business_pipeline.py --report output/synthetic-business-pipeline.json` runs no-live/fake-data/rollback-safe checks for record-level failure evidence, inquiry upload failure evidence, Stripe amount parity, checkout-to-Lead conversion, checkout fulfillment, paid-order cascade, payment-success reconciliation, mocked webhook behavior, customer document/email policies, outbound templates, outbound send-readiness, quote/proposal outliers, unpaid invoice outliers, customer reminder dry-run outliers, and customer reminder review-report outliers. Latest result on 2026-05-10 in open ecommerce testing: 22 synthetic readiness contracts, 0 broken piping, 8 inefficiencies/partial connections, and 3 cutover-deferred items. It does not require live Stripe keys, real operator data, or real customer records.
- Stripe Checkout amount parity now has a contract. `stripe_line_items_for_sales_order()` builds hosted-checkout line items from the ERPNext Sales Order and adds a `Sales tax and charges` adjustment when needed so Stripe totals match `Sales Order.grand_total`. If item lines would exceed the ERPNext total, it raises `frappe.ValidationError` instead of under/overcharging silently. `scripts/verify/stripe_amount_parity_contract.py` covers taxable, nontaxable, and negative-adjustment cases.
- Legal/accounting review packet lives at `_resources/policies/legal-accounting-review-packet-2026-05-06.md`.
- `/event-playground` is a hidden internal-preview route for the first PlayCanvas decor planner. Keep it out of the ASAP website launch lane unless GL explicitly reopens it here. The PlayCanvas/Vite source, research packet, and design-studio capabilities moved to the standalone repo at `C:\Users\baenb\projects\design-studio\workstreams\locally-twisted-plan-custom-decor-v2\`; this LT repo retains only the Frappe route shell at `www/event_playground.html`/`.py`, the local iframe wrapper for `127.0.0.1:4306`, and the contact handoff contract. The browser preview is framed as `Plan Custom Decor`, emits `event-playground-v2`, adds `design_studio_contract.schema_version = design-studio-v1`, adds event date/city contact fields, and exposes quote-honesty warnings. Render counts are explicitly visual density, not quote math. Production estimates are candidate-only, `quote_ready: false`, and `customer_visible: false` until Locally Twisted approves formulas, fill/support assumptions, overage, venue review, and pricing. Submit Inquiry still hands the design to `/contact?intent=quote&source=event-playground` through `postMessage` + `sessionStorage`; the existing contact form now pre-fills name, email, phone, ISO event date, event location/city, services, colors, decor type, package notes, and the design summary. There is no public nav entry, committed production bundle, DocType, backend save API, automatic Lead/Quote/Sales Order creation, pricing, checkout, CAD, room scanning, share link, or full organic/twisting physics in this slice.
- Product listing cards can display `lt_brand_description` through the local Webshop API wrapper in `locally_twisted.api.product_listing`.
- Variant media first pass completed 2026-05-02. ERPNext now has 1,712 variant `Item.image` values mapped from `_resources/odoo-live/images/` where Odoo image labels clearly matched product options. Product detail pages call `locally_twisted.api.variant_media.get_variant_media` after exact option selection and swap the main image when a variant image exists. Cart/checkout use the variant image when present and fall back to the parent Website Item image otherwise. The review command `python scripts/setup/sync_variant_media.py --dry-run --include-details --report output/catalog-media-review.json` currently reports 49 products checked, 35 with candidate image labels, 45 needing review, 1,712 unchanged mapped variants, and 6,831 skipped variant image assignments.
- Category browse media is still empty in ERPNext: all 11 customer-facing child Item Groups under `Shop Items` have `image = null` as of the 2026-05-06 DB recheck. `python scripts/verify/category_media_candidates.py` now creates a no-mutation approval packet from existing product-source and portfolio-proof media, with quick picks for all 11 categories in ignored local `output/category-media-candidates.md`. `scripts/setup/sync_category_media.py` creates the approval template and dry-runs the Frappe-backed Item Group image update path; `--apply` only writes rows marked `approved: true`. Do not revive `/shop-by-category`; choose representative category media for `/shop-items/<group>` or future menu treatment only after Jeff/GL approval.
- Product detail breadcrumbs now use `All Balloon Decor > category > product`; the retired `Shop by Category` label/link is blocked by `scripts/verify/smoke_shop.py`.
- Product detail pages are now company-first and clear-control, not generic ecommerce recommendation or boxed-option surfaces. The Webshop lower Additional Info/Reviews/Recommended Items panel was removed on 2026-05-07, the old auxiliary/recommendation CSS selectors are gone, and product options/variant chips/selects/price-add-to-cart groups are no longer framed boxes. Pickup/delivery is the approved framed product-page exception. `smoke_shop.py` fails if the recommendation selectors return or if product option controls regain boxed backgrounds, borders, or shadows. Use `capabilities/recipes/frappe-product-page-company-first.md` and `capabilities/recipes/frappe-product-clear-control-contract.md` before changing product detail templates or product-page CSS.
- Civic Celebration is now the V1 visual direction across the public site. See `_resources/STYLE-GUIDE.md`, `workstreams/brand-audience-style-reset.md`, and `workstreams/civic-sitewide-redesign.md`. The pass covers shared header/footer/theme CSS, homepage, contact/book form, BTFP, portfolio, FAQ, policies, accessibility, thank-you/payment success, shop, category pages, product detail, cart, and checkout. The homepage hero now uses generated lifestyle hero crops from the project image-generation API; the real optimized install photo stays reserved for proof/portfolio surfaces.
- Compact hero standard is now implemented and guarded. Public page heroes use 220px mobile, 250px tablet, and 280px desktop standard heights, with padding/title caps documented in `_resources/STYLE-GUIDE.md` v4.5 and `capabilities/recipes/compact-hero-contract.md`. The current verifier covers `/`, the four event audience pages, `/portfolio`, `/balloon-twisting-and-face-painting`, `/contact`, `/shop`, and `/shop-items/seasonal-specialty` through `npm run test:interactive-layout -- --grep "compact hero height contract"`. `/event-balloons` is removed and should not return to the hero matrix unless a future GL decision recreates the route. The root cause was stacked page-local hero sizing: global `section` padding, route-level min-heights, inner padding, and giant title clamps all competing.
- Homepage launch repair completed on 2026-05-07: the hero uses one visible stable H1, the first viewport shows Google reviews immediately after the hero on desktop and 320px mobile, the homepage trust/authority bar is removed for now while the icon assets are preserved, the cookie notice renders inline after reviews instead of covering CTAs, Recent Celebrations appears after review cards, the closing CTA leads with corporate/school/civic/community work, and stale homepage v2/design-studio comments were removed.
- Homepage review cards and the trusted-business client crawl both crawl left-to-right as full-stage horizontal proof lines. Review cards use the canonical `540s` loop; a homepage-only sync script measures both duplicated tracks and assigns the trusted-business crawl a proportional duration so its visible pixel speed matches the reviews. Reduced-motion mode intentionally keeps these two business-proof crawls slow, moving, horizontal/full-stage, and scrollbar-free; do not restore the static/overflow fallback that caused the recurring real-browser failure.
- Current crawl verification on 2026-05-07 proved left-to-right deltas, hidden overflow, matched visible speed, and moving reduced-motion proof crawls. The deliberate red run failed 5/5 against the previous right-to-left direction; the corrected implementation then passed focused crawl regression 5/5, home layout 13/13, homepage/cookie 12/12, compact hero 14/14, and full `npm run test:website-verify`. Live diagnostics showed positive left-to-right deltas with hidden overflow and near-zero speed delta in both `no-preference` and `reduce`; screenshots are in `output/playwright/home-crawl-left-to-right-20260507/`.
- Homepage feature handoff: `workstreams/landing-page-repair.md`. Capability contract: `capabilities/recipes/homepage-launch-proof-contract.md`.
- `_resources/STYLE-GUIDE.md` version 4.3 is the only current visual authority. The old `_resources/design-guide/`, stale shop/spec comparison docs, and generic icon-comparison resources were deleted on 2026-05-05 because they conflicted with Civic Celebration + Slate Blue/Berry + Brand Direction and kept reintroducing light-blue/blush, old-font, and weak-icon choices.
- Rendered site repair pass completed 2026-05-05: mega-menu assets are served through hooks, desktop click pins mega menus open, mobile drawer opens accordions, product/shop pages use `lt-product-polish.css`, broad route containment uses `lt-page-containment.css`, and the homepage/portfolio/newsletter mobile clipping issues were fixed.
- Responsive container integrity is now a standing launch gate, not a one-off fix. `scripts/verify/layout_helpers.js` centralizes public routes, breakpoint-edge viewports, overflow/text-fit checks, and the executable route-level container contract. After the BTFP crawl/header update, `npm run test:layout-fit` covers 325 passive route/viewport checks across the current public route list and 13 viewport families; `npm run test:container-contract` covers 75 route/viewport container checks across launch public routes at 320px, 820px, and 1366px; `npm run test:interactive-layout` covers 163 stateful checks for compact generated-photo heroes, platform-name leakage, header breakpoint behavior, desktop mega panels, mobile drawer accordions, shop/product controls, contact conditionals, portfolio front-photo state, BTFP crawl motion, homepage proof crawls, cookie placement, and reduced-motion homepage states. `npm run test:portfolio-reel` is the route-specific proof-gallery gate.
- Public containers are now code-owned, not advisory prose. `CONTAINER_CONTRACT_ROUTES` declares every visible direct `.page_content` child and each section's mode (`band`, `fullbleed`, `contained`, `clip`, `raw-band`, `root`, or `visual-field`). The first full matrix exposed real drift in homepage twisting spotlight containment, portfolio footer markup, contact/location Bootstrap containers, document narrow-width selector specificity, BTFP route surfaces, and BTFP event-crawl data. `lt-page-containment.css` now loads after product/shop CSS so it remains the final public containment layer.
- `npm run test:website-verify` is the website-only closeout gate through `scripts/verify/website_launch_verify.py`: nav IA, passive layout, route-level container contract, interactive layout, search, portfolio reel, current ecommerce mode contract, shop smoke, product prices, variant media, and checkout experience, with Playwright workers serialized by default. `npm run test:public-verify` aliases to the same website-only gate; `npm run test:launch-verify` adds accessibility and contact smoke. `npm run test:ecommerce-full` is the focused full ecommerce gate including rollback-safe checkout fulfillment and checkout-to-Lead conversion when ecommerce is reopened. Event Playground remains separately available through `npm run test:event-playground` for the OpenClaw lane. Latest public verification on 2026-05-10 passed `python scripts\verify\website_launch_verify.py --with-a11y --with-contact-smoke` with 15/15 hidden-ecommerce launch steps, including accessibility and contact smoke backend proof/cleanup. Earlier open-ecommerce proof remains available for follow-up through `test:ecommerce-full`, `test:synthetic_business_pipeline.py`, and `test:business_automation_index.py`.
- The active theme/app source has been cleaned away from old font and UI-pastel references. Do not reintroduce `DM Serif`, `Raleway`, `Montserrat`, `Playfair`, `lt-blush`, `lt-soft-blue`, old `soft-blue`/`light-blue`, UI `blush`, or unresolved `--lt-primary` in customer-facing source.
- A 16-asset custom brass-line icon suite now lives at `apps/locally_twisted/locally_twisted/public/icons/brand/`. Balloon-specific surfaces should use balloon-form icons first: pair, cluster, arch, organic garland, column, and bouquet.
- The contact page no longer depends on an external map iframe for the main service-area proof; it uses a controlled service-area panel.
- Per-product variant correctness now compares normalized Odoo `valid_variants` plus approved graduation college-preset projection to active, required-choice ERPNext variants. Current pass on 2026-05-18: 53 products checked, 10,186 expected active variants, 10,186 live active variants, 4 single-SKU products. Disabled legacy optional-add-on/raw-color graduation variants are intentionally ignored by this customer-facing contract. This is shape parity only, not price parity.
- Catalog variant price parity is locally repaired and guarded for the active variant set after the 2026-05-19 price-identity incident. `c7f9da3` fixed the bouquet-size family first; the 2026-05-19 local modifier repair corrected the broader non-bouquet flattening class, including Easter Bunny Ear Arch `25ft`. Use `workstreams/ecommerce-price-identity-incident-review-2026-05-19.md` and `workstreams/catalog-variant-price-recovery.md` before any catalog price claim or repair. Local proof does not equal staging/live/public approval.
- Product option UX P0 pass completed 2026-05-02 and was reconciled with the current commerce lane on 2026-05-05. `item_configure.html` no longer runs per-attribute `frappe.get_all` lookups from Jinja; it uses `get_variant_attribute_options`, a project Jinja helper backed by Webshop's `get_attributes_and_values`. Quote-required custom installs such as Arches and Garlands intentionally show a `/contact?item=...` quote CTA instead of cart selectors. Retail variants such as `unicorn-bouquet` still render inline single-select chips/selects, consume `valid_options_for_attributes`, and write selected variant codes to `LT_CART`.
- Generated Webshop asset-map drift was corrected in the running ERPNext stack on 2026-05-02. The container already has Yarn Classic at `/home/frappe/.nvm/versions/node/v20.19.2/bin/yarn`, but non-interactive `docker exec` does not include that directory in `PATH`. Use `export PATH=/home/frappe/.nvm/versions/node/v20.19.2/bin:$PATH` before `bench build --app webshop`; no package install was needed. Important Docker nuance: the frontend/nginx container must be the final Webshop build target because `sites/assets/webshop` links to each container's own app-public files while `assets.json` is shared. Building only in the backend writes asset-map names nginx cannot serve. After rebuilding from the frontend container and clearing `assets_json` plus website cache, follow-up console checks returned 200s with 0 console errors/warnings.
- `scripts/verify/layout_fit.spec.js` is the committed passive Playwright Test gate. Latest full launch run: `python scripts\verify\website_launch_verify.py --with-a11y --with-contact-smoke` -> 15/15 hidden-ecommerce launch steps passed, including `layout-fit` 325/325 across the current route list and 13 viewport families, `container-contract` 75/75, `interactive-layout` 163/163, `search_contract` 3/3, `portfolio_reel` 6/6, ecommerce pause contract, shop pause smoke, product prices, variant media, checkout experience 2/2, axe accessibility 50 route/viewport checks with 0 violations, manual accessibility, and contact smoke backend proof/cleanup. `scripts/verify/container_contract.spec.js` is the route-level public container contract; focused rerun after the homepage Custom Event Decor repair passed 75/75. `scripts/verify/portfolio_reel.spec.js` is the route-specific proof-gallery gate.
- Catalog variant counts match the normalized Odoo source: the raw scrape has duplicate-case latex color values, but `_resources/odoo-live/value_normalize_map.json` collapses them and the normalized expected variant counts match ERPNext.
- Website cache was cleared after Jinja/CSS changes; the backend was restarted after `home.py` route CSS changed; `hooks.py` cache-busts were bumped for `lt-site-preferences.js` and `lt-page-containment.css`.

Claims from older docs still need re-verification before being repeated:

- ERPNext v15.105.0 stack on port `8081`.
- `locally_twisted` custom app installed.
- Webshop + payments installed.
- 53 Website Items published.
- `/shop-by-category` compatibility redirect to `/shop`.
- Payment backend launch-readiness now has a feature lane at `workstreams/payment-backend-launch-readiness.md`; use `scripts/verify/payment_launch_readiness.py` for non-secret structural checks. Local mode passes; live mode is expected to fail until production Stripe/site config exists.
- Existing pages including `/`, `/lookbook`, `/shop`, `/contact`, `/faq`, `/refund-policy`, `/accessibility`, `/cart`, `/checkout`, `/payment-success`, `/thank-you`.

Treat these as verified only after re-running smoke tests or checking the routes. Do not repeat a visual claim without screenshots.

## Paperwork / Backend Automation Focus

Current coordination lanes: `workstreams/paperwork-backend-automation.md`, `workstreams/business-automation-index.md`, `workstreams/synthetic-business-pipeline.md`, `workstreams/customer-reminder-dry-run.md`, `workstreams/customer-reminder-review-report.md`, and `workstreams/fail-loud-record-level-hardening.md`.

Fresh baseline on 2026-05-09:

- `finance_inventory.py --json`, `customer_documents_contract.py`, `payment_cascade_contract.py`, `crm_stage_cascade.py`, `backend_schema_inventory.py`, `payment_backend_config_contract.py`, `payment_webhook_contract.py`, `payment_launch_readiness.py`, `checkout_lead_conversion_contract.py`, `finance_workspace_parity.py`, and `finance_inventory_contract.py` passed locally.
- `paperwork_status.py --report output/paperwork-status.json` passed in `synthetic_without_live_credentials` mode. It does not run live payment readiness in this lane; live Stripe keys/webhook/production host/operator setup are reported under `cutover_deferred_not_blocking`.
- `business_automation_index.py --report output/business-automation-index.json` passed and generated the current cross-system automation report: 25 surfaces, 15 launch-required, 22 connected, 3 exists-but-not-connected, 0 launch-required missing, and 0 loud-failure gaps.
- `synthetic_business_pipeline.py --report output/synthetic-business-pipeline.json` passed with 16 no-live synthetic contracts, 0 broken piping, 8 inefficiencies/partial connections, and 3 cutover-deferred items.
- `stripe_amount_parity_contract.py` passed and now guards Stripe hosted-checkout totals against ERPNext Sales Order totals.
- `sync_invoice_branding.py` passed and is idempotent; `invoice_branding_contract.py` passed against rendered Sales Invoice HTML and now guards the gray invoice callouts plus black support-banner/no-gold/no-dog standard.
- `outbound_documents_contract.py` passed against the answer-first standard outbound document registry and templates.
- `render_outbound_document_previews.py --slug outbound-documents-20260506` generated 20 fake-data normal/outlier document previews for review.
- Live Stripe keys, webhook secret, production host, and real operator/customer data are cutover-only. They are intentionally not part of the current fake-data/synthetic readiness gate.
- Local finance inventory found 4 Customers, 8 Sales Orders, 1 Sales Invoice, 8 Payment Requests, 0 Payment Entries, 0 Bank Accounts, 0 Suppliers, and 0 Employees. Payment Terms exist locally; bank/supplier/payroll setup remains incomplete.
- The paperwork status report currently flags 1 unpaid/overdue Sales Invoice, 8 expected Payment Requests, Email Queue status counts of 30 Sent, and no pending email queue rows.
- The unpaid/overdue invoice review surface now exists at `locally_twisted.paperwork.unpaid_invoice_review.run` with host verifier `python scripts/verify/unpaid_invoice_review.py --report output/unpaid-invoice-review.json`. It currently returns 1 overdue-review candidate for `ACC-SINV-2026-00001`, with draft-only `payment_reminder_draft` and `statement_of_account` document candidates. It marks `read_only: true`, `send_allowed: false`, `mutation_allowed: false`, and includes a mutation guard for Email Queue, Communication, Sales Invoice, Payment Request, Payment Entry, and Journal Entry counts.
- The unpaid invoice draft packet renderer now exists at `locally_twisted.paperwork.unpaid_invoice_draft_packet.run` with host verifier `python scripts/verify/unpaid_invoice_draft_packet.py --report output/unpaid-invoice-draft-packet.json`. It turns review candidates into human-review packet sections for `payment_reminder_draft` and `statement_of_account`, still marked `draft_only_not_sent`, with `read_only: true`, `send_allowed: false`, `mutation_allowed: false`, and the same mutation guard. `python scripts/verify/unpaid_invoice_draft_packet_contract.py` covers fake normal/outlier packet behavior without touching ERPNext records.
- The internal paperwork review digest now exists at `locally_twisted.paperwork.paperwork_review_digest.run` with host verifier `python scripts/verify/paperwork_review_digest.py --report output/paperwork-review-digest.json`. It combines paperwork status, business automation index, unpaid invoice review, and draft packet output into one read-only review payload without sending customer messages or mutating accounting records. It labels live Stripe/production setup as `cutover_deferred_not_blocking`, not as a current blocker. It now includes `operations_readiness` rows for company/operator, vendor/contractor, accountant/finance reviewer, and customer/public-user readiness. The digest calls the automation index with `run_runtime_contracts=False` so Desk/report review does not execute rollback-heavy fake-data contracts.
- The customer reminder dry-run queue now exists at `locally_twisted.paperwork.customer_reminder_dry_run.run` with host verifier `python scripts/verify/customer_reminder_dry_run.py --report output/customer-reminder-dry-run.json`. It turns the digest and draft packets into internal review queue items with cadence suggestions, draft sections, and blockers. It is explicitly `no_live_internal_review`, with `send_allowed: false`, `customer_delivery_enabled: false`, `automatic_delivery_enabled: false`, and no Email Queue, Communication, Error Log, payment, journal, or invoice mutations. `python scripts/verify/customer_reminder_dry_run_contract.py` covers fake overdue/current/missing-payment-path/malformed-send scenarios.
- The customer reminder review report now exists at `locally_twisted.paperwork.customer_reminder_review_report.run` with host verifier `python scripts/verify/customer_reminder_review_report.py --report output/customer-reminder-review-report.json`. It turns dry-run queue items into report columns, rows, and `review_now` / `hold` / `blocked_send` groups for a future Desk page or internal-only report. It is explicitly no-live/read-only, with `send_allowed: false`, `customer_delivery_enabled: false`, `automatic_delivery_enabled: false`, and no Email Queue, Communication, Error Log, payment, journal, or invoice mutations. `python scripts/verify/customer_reminder_review_report_contract.py` covers fake mixed/empty/malformed-send source scenarios.
- The business automation index currently classifies vendor setup/W-9 packets, bank reconciliation, and payroll/HRMS as existing but not connected. These are not silent unknowns anymore. Quote/proposal packets are connected only as draft-only internal review output, not PDF generation or customer delivery.
- Customer document policy blocks, paid-order receipt/operator/welcome email cascade, and inquiry acknowledgment policy lanes are covered by verifiers.
- Sales Invoice print output defaults to the branded Locally Twisted format and includes the corporate invoicing policy lane.
- External document audience standards started at `capabilities/recipes/external-document-audience-contract.md`, with source templates in `locally_twisted/outbound_documents/`. Use those before building invoices, receipts, proposals, event packets, vendor setup/W-9 packets, statements, or other documents that leave the company.
- CRM stage movement remains operational Task-only and must not create finance records until thresholds are explicitly decided.

Next safe paperwork/backend slice: keep the no-send report chain green while resolving only approved setup gates. Company/operator readiness is blocked by missing Bank Account/default bank; vendor/contractor readiness is blocked by missing Supplier/vendor records plus approved W-9/secure-send workflow; accountant payroll readiness is blocked by missing HRMS payroll DocTypes and provider/accountant approval. Keep using synthetic/fake data to flush out cascading fields and broken piping, but run DB-mutating verifiers serially. Do not send reminders, create live bank sync, auto-submit accounting records, wire CRM stages to finance, or mix live credentials/real customer data into this work.

## Known Incorrect Or Risky Docs

- `CLAUDE.md`, `HANDOFF.md`, `PROJECT-STATUS.md`, `lessons-learned.md`, `locally-twisted-decisions.md`, and `locally-twisted-queue.md` contain stale catalog counts in places.
- `.planning/phases/01-customer-site-and-storefront/PLAN.md` is stale about slice completion. Use the queue/status plus git/files/routes instead.
- `CLAUDE.md` and related files contain tool-specific mythology and emotionally loaded handoff instructions. Useful technical receipts should be preserved in neutral docs; do not propagate the tone.
- Existing docs say `24` Item Attributes from the Odoo-derived catalog, but the DB currently has `26` Item Attribute records. Investigate before changing fixture logic.

## Next Safest Slice

P0 is no longer `/book`; GL retired that surface. The primary customer inquiry path is the standard `/contact` form, and `/book` is only a route alias for legacy traffic.

Next safest slices:

- Design and wire the remaining stage cascades deliberately: decide which LT CRM stage should create/update Quote, Sales Order, Project/job, Calendar invite, customer email/text follow-up, Customer record, and finance records. The Task-only layer is done; do not infer finance triggers from `Archive`.
- Before manual stage-to-finance automation, decide exact stage thresholds for Quote, Sales Order, Project/job, Calendar invite, customer follow-up, Customer record, invoice, and Payment Request changes. Checkout/Lead conversion parity is done; do not duplicate its Customer/Sales Order/Payment Request creation from stage movement.
- Finish the checkout/policy approval loop: GL business-proxy answers are reflected in current Terms/FAQ/Refund/Privacy/tax copy, receipt/inquiry emails, and a basic cookie/tracking notice. Legal/accounting review and future analytics/ads tracking integration remain before final live-readiness claims.
- Continue the paperwork/backend automation lane from `workstreams/paperwork-backend-automation.md`, `workstreams/business-automation-index.md`, `workstreams/customer-reminder-dry-run.md`, and `workstreams/customer-reminder-review-report.md`: the read-only paperwork status report, branded invoice output, outbound document registry, automation index, daily scheduler checkup, Stripe amount-parity guard, draft-only unpaid invoice review surface, draft-packet renderer, fake packet scenario contract, internal paperwork review digest, no-live customer reminder dry-run queue, no-live customer reminder review report, and no-live synthetic business pipeline exist. The next slice is reviewed Desk UX around the report rows, not customer sending. Do not send reminders, create live bank sync, auto-submit accounting records, wire CRM stages to finance, or use live credentials/real customer data in fake-data audits.
- Send `_resources/policies/legal-accounting-review-packet-2026-05-06.md` to Jeff/legal/accounting before treating the public policy set as final.
- Wire the Stripe Dashboard privacy/terms URLs to `/privacy` and `/terms-of-service` after GL/legal approval.
- Finish payment live-mode configuration and run `python scripts/verify/payment_launch_readiness.py --mode live` only when cutover work begins. It is not a blocker for current synthetic/backend automation work.
- Review skipped/unmatched catalog media with GL/Jeff: parked until approval. The automated pass only mapped photos whose Odoo labels clearly matched product options. Product-page source gallery media is now role-approved through Product Setup and Website Slideshow; category/reference/media-menu assignments are still separate approval lanes. Refresh `output/catalog-media-review.json` with the detailed dry-run command before assigning variant/category media. Regenerate `output/category-media-candidates.md` for the 11 category quick picks before the approval conversation. Do not assign generic category/reference images by guess.
- Keep product navigation product-backed: use `scripts/verify/nav_ia.py` before touching header/footer IA.
- Continue brand review from `workstreams/brand-style-guide-consolidation.md`. The emergency menu/container/product repair is verified; remaining visual work is GL/Jeff review of photos, proof hierarchy, exact review/trust counts, and category/product imagery.
- Keep the responsive container gate green for any new public UI. Add route-specific interactive checks when a change introduces a new drawer, modal, accordion, filter, product control, or breakpoint state.
- Review the new `/portfolio` proof reel with GL/Jeff/designer for photo order, photo quality, and whether any images should be removed before launch. Use the production files listed in `workstreams/portfolio-proof-gallery.md` for critique. Keep the raw generated/reference folder only while critique is active; do not delete or commit it without GL approval. Restart/clear cache after controller edits and run `npm run test:portfolio-reel`.
- Reconcile product/category media without reviving the retired `/shop-by-category` card index; this is parked until GL/Jeff approve the selections. Use `/shop` and `/shop-items/<group>` as the customer-facing browse surfaces. The next implementation after approval should mark explicit selections approved and run `scripts/setup/sync_category_media.py --apply`, not a judgment-based bulk assignment.
- Complete the blog channel and two ported posts.
- Leave Event Playground with OpenClaw unless GL explicitly reassigns it back into this repo lane. Do not make it a launch blocker for the public website.

## Verification Commands

Run DB counts with `bench execute` from the backend container:

```powershell
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute frappe.client.get_count --kwargs "{'doctype':'Item'}"
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute frappe.client.get_count --kwargs "{'doctype':'Website Item'}"
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute frappe.client.get_count --kwargs "{'doctype':'Item Price'}"
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute frappe.client.get_count --kwargs "{'doctype':'Item Variant Attribute'}"
```

Filtered counts:

```powershell
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute frappe.client.get_count --kwargs "{'doctype':'Item','filters':{'has_variants':1}}"
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute frappe.client.get_count --kwargs "{'doctype':'Item','filters':{'variant_of':['is','set']}}"
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute frappe.client.get_count --kwargs "{'doctype':'Item','filters':{'has_variants':0,'variant_of':['is','not set']}}"
```

After Jinja/CSS/Web Page changes:

```powershell
python scripts/dev/clear_website_cache.py
```

If Webshop assets need a real rebuild, expose the existing Yarn path and build from the frontend container last:

```powershell
docker exec locally-twisted-erpnext-v15-frontend-1 bash -lc 'export PATH=/home/frappe/.nvm/versions/node/v20.19.2/bin:$PATH; cd /home/frappe/frappe-bench && bench build --app webshop'
docker exec locally-twisted-erpnext-v15-redis-cache-1 redis-cli DEL assets_json
python scripts/dev/clear_website_cache.py
```

Navigation IA regression check:

```powershell
python scripts/verify/nav_ia.py
```

Variant media contract:

```powershell
python scripts/verify/variant_media_contract.py
```

Catalog variant contract:

```powershell
python scripts/verify/catalog_variant_contract.py
```

Catalog price contract and repair path:

```powershell
npm run test:product-prices
python scripts/setup/stage_seed_data.py
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.seed.repair_variant_prices_from_odoo.execute --kwargs "{'slug_filter':'unicorn-bouquet','dry_run':True}"
```

Business automation and paperwork launch spine:

```powershell
python scripts/verify/business_automation_index.py --report output/business-automation-index.json
python scripts/verify/stripe_amount_parity_contract.py
python scripts/verify/paperwork_status.py --report output/paperwork-status.json
python scripts/verify/unpaid_invoice_review.py --report output/unpaid-invoice-review.json
python scripts/verify/unpaid_invoice_draft_packet.py --report output/unpaid-invoice-draft-packet.json
python scripts/verify/unpaid_invoice_draft_packet_contract.py
python scripts/verify/paperwork_review_digest.py --report output/paperwork-review-digest.json
python scripts/verify/customer_reminder_dry_run.py --report output/customer-reminder-dry-run.json
python scripts/verify/customer_reminder_dry_run_contract.py
python scripts/verify/customer_reminder_review_report.py --report output/customer-reminder-review-report.json
python scripts/verify/customer_reminder_review_report_contract.py
python scripts/verify/payment_launch_readiness.py
python scripts/verify/payment_launch_readiness.py --mode live
```

Variant media sync from the captured Odoo image files:

```powershell
python scripts/setup/sync_variant_media.py --dry-run
python scripts/setup/sync_variant_media.py --dry-run --include-details --report output/catalog-media-review.json
python scripts/setup/sync_variant_media.py
```

Category media candidate packet:

```powershell
python scripts/verify/category_media_candidates.py
python -m json.tool output/category-media-candidates.json
python scripts/setup/sync_category_media.py --write-template
python scripts/setup/sync_category_media.py --selection output/category-media-selection.template.json
```

Public layout and interaction regression checks:

```powershell
npm run test:layout-fit
npm run test:interactive-layout
npm run test:portfolio-reel
npm run test:checkout-experience
python scripts/verify/smoke_shop.py
npm run test:website-verify
```

Event Playground source, browser, and Frappe handoff checks:

```powershell
cd C:\Users\baenb\projects\design-studio\workstreams\locally-twisted-plan-custom-decor-v2\design-studio-v2\event-builder-spike
npm run test:classic
npm run build
npm run verify:event-playground
npm run verify:v2
cd C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\locally-twisted
npm run test:event-playground
```

Contact form logic regression checks:

```powershell
python scripts/verify/contact_service_logic.py --base-url http://localhost:8081
python scripts/verify/contact_prefill.py --base-url http://localhost:8081
python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --form-path /contact --skip-newsletter
npm run test:form-experience
```

Backend Lead/CRM intake parity:

```powershell
python scripts/setup/sync_contact_intake_backend.py
python scripts/setup/sync_crm_pipeline.py
python scripts/setup/sync_stage_cascade.py
python scripts/verify/lead_backend_intake_parity.py
python scripts/verify/crm_pipeline_parity.py
python scripts/verify/crm_stage_cascade.py
python scripts/verify/checkout_lead_conversion_contract.py
python scripts/verify/backend_schema_inventory.py
```

Before declaring visible work done, run the passive and interactive layout gates, then capture and inspect desktop and mobile screenshots. Use the repo's existing Playwright scripts where possible; automated fit gates are necessary but do not replace screenshot review.
