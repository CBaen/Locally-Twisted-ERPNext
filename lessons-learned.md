# Lessons Learned — Locally Twisted

**Append-only.** Newest entries at the top. Each entry: what happened, what was learned, what to do differently next time.

LT-specific patterns. Cross-client / agency-wide lessons go to `Built_by_Cameron/lessons-learned.md`. If a lesson is broadly applicable across all ERPNext builds, it ALSO goes to the global `C:\Users\baenb\.claude\lessons-learned.md`.

---

## 2026-05-23 - A docs closeout should close the loop, not reopen the release

After `849d8c2`, the repo already had a clean local guard archive for the app
mirror sync-plan helper. The useful follow-up was to make peer-facing docs and
capability evidence agree, remove ignored runtime cache folders, and leave the
forensic-freeze boundary intact. Creating another no-go packet would have made
the archive longer without changing staging reality.

**Counter-move:** when a release lane is frozen and only docs move, write a
bounded documentation parity closeout. Record what changed, what did not
change, and which artifacts are still required before mutation. Do not convert
that closeout into provider proof, staging proof, or another packet loop.

---

## 2026-05-23 - Pre-sync plans are not mirror sync proof

A valid `app-mirror-sync-plan.json` is only a local precondition for a future
approved mirror sync. It proves source review, target, rollback hash, required
files, and post-sync proof requirements. It does not prove the app mirror was
updated, Frappe Cloud deployed, hosted preflight passed, catalog data exists,
or owner-review users/routes are ready.

**Counter-move:** generate sync plans through
`scripts/release/app_mirror_sync_plan_artifact.py`, validate them through the
controller, then require post-sync `app-mirror-freshness.json` before any
downstream deploy/preflight/bootstrap claim.

---

## 2026-05-23 - Prep helpers can accidentally look like release proof

The next useful movement after the forensic freeze was not another no-go packet
or a provider call. It was reducing post-approval packet ambiguity. The first
draft of that idea could have written controller-consumable artifact names,
which would make prep files look like release evidence.

**Counter-move:** prep-only helpers must not write final artifact filenames.
Use a manifest with negative flags such as `controller_consumable: false`,
`mutation_capable: false`, and `provider_mutation_executed: false`. Keep
approval, provider snapshot, app mirror freshness, deploy completion, hosted
preflight, owner-review gate, and triad artifacts absent until real proof
exists. Agency-level mirror:
`../../lessons-learned.md`.

---

## 2026-05-23 - A no-go packet loop can become its own failure

The repeated read-only staging packets were valuable while each one answered a
new question about mirror freshness, hosted preflight, approval shape, or guard
behavior. After a docs-only closeout, repeating the packet solely because the
commit hash changed does not improve staging truth. It creates another stale
archive and consumes the next agent's attention.

**Counter-move:** separate release input changes from documentation archive
changes. If only docs moved, write a next-agent closeout and keep the lock
intact. Generate fresh packet artifacts only when release input state changes,
explicit freeze-reopen approval exists, or mutation-capable release work is
being prepared.

---

## 2026-05-23 - Artifact encoding can become a fake release blocker

The `9e63fef` read-only staging packet initially wrote `read-receipt.json` with
a UTF-8 BOM from PowerShell. The controller blocked before reaching the real
release authority issue. The real blocker remained the missing explicit
`freeze-reopen-approval.json`; the BOM was packet-writing friction.

**Counter-move:** release guard JSON loading now uses `utf-8-sig`, and the
release controller contract includes a BOM read-receipt fixture. Continue to
prefer UTF-8 without BOM when writing artifacts, but do not let encoding noise
mask the true go/no-go gate.

---

## 2026-05-23 - Approval artifacts need a generator, not a template copy

The release controller required `freeze-reopen-approval.json`, but a future
agent could still hand-copy the artifact from a template or old packet. That
would satisfy the file-name expectation while risking stale source binding,
unsupported action scope, missing approval evidence, or unsafe approval timing.

**Counter-move:** give the approval transition a local helper and contract.
`scripts/release/freeze_reopen_approval_artifact.py` previews with `ok=false`,
writes only with explicit `--write`, approver, and approval evidence, binds to
current `HEAD` and the active lock, refuses non-staging actions, and validates
through `npm run test:freeze-reopen-approval`.

---

## 2026-05-23 - Reopen approval must expire mechanically

A release-freeze approval can look valid as JSON while still being unsafe:
it may be copied from a prior attempt, missing a timezone, already expired, or
open for too long. Without timestamp validation, a future agent could satisfy
the artifact requirement with stale approval and restart mutation from the
wrong moment.

**Counter-move:** validate approval time in the release controller. Require
ISO-8601 timezone-bearing `approved_at` and `expires_at`, reject future-dated,
expired, reversed, malformed, timezone-less, and longer-than-24-hour approval
windows, and make verifier fixtures use dynamic current timestamps instead of
fixed dates.

---

## 2026-05-23 - Read receipts can be too narrow to prevent stale release work

The release controller had a required-doc read receipt, but the required list
did not include every doc a future agent would naturally use to author the next
release packet. That left room for an agent to satisfy the gate while missing
the current handoff, release-artifact README, script contract, or chain-binding
handoff.

**Counter-move:** treat read receipts as release infrastructure. When a new
handoff, packet README, script README, or guard handoff becomes necessary for
safe release execution, add it to the lock and controller read-receipt list in
the same closeout.

---

## 2026-05-23 - Valid release files can still form an invalid release packet

The local release controller had validators for individual artifacts, but
separate files can still be stale or borrowed from different moments. That is
dangerous for Frappe Cloud release work because source commit, app mirror hash,
payload app hash, provider target hash, deploy completion, hosted preflight,
rollback hash, and site all need to describe one release attempt.

**Counter-move:** validate the artifact chain before mutation. The controller
now rejects mismatched source commits, payload app hashes, provider snapshot
hashes, deploy-completion hashes, hosted-preflight hashes, rollback hashes, and
sites even when each individual artifact has the right shape.

---

## 2026-05-23 - Latest archive and underlying fix are different facts

A top-level handoff can become stale even when the underlying feature handoff
is correct. After `5e11003` documented the template parity work, some front-door
handoffs still named `f5e2e91` as the latest archive because that was the
commit that changed the template itself.

**Counter-move:** name both facts when they differ: current GitHub archive and
underlying feature/source commit. For LT staging freeze work, `5e11003` is the
current docs archive, while `f5e2e91` is the template fix. Do not let either
commit imply app mirror freshness, freeze reopen approval, provider deploy
completion, hosted preflight proof, or owner-review readiness.

---

## 2026-05-23 - Templates can become stale even when guards are correct

The release controller and verifier suite required new artifacts, but the
staging-freeze packet template still showed the old packet shape. That leaves a
future agent one copy/paste away from a packet that looks complete in docs but
fails the controller.

**Counter-move:** treat release packet templates as part of the guard surface.
When adding or tightening a required artifact, update the starter template in
the same closeout and verify it includes the same shape the validator expects.
For LT, `f5e2e91` updated the staging-freeze template for reopen approval, app
mirror sync plan, deploy completion, and hosted preflight `checks`.

---

## 2026-05-23 - Reopen gaps need to become controller inputs

After the post-`ebb7151` packet, the remaining release risks were precise:
approval had no artifact shape, app mirror sync was deadlocked by requiring
post-sync proof before sync, deploy completion was not a first-class artifact,
and owner-review packets could still carry raw prior traceback text.

**Counter-move:** make each risk a controller input and an offline contract:
`--reopen-approval`, `--app-mirror-sync-plan`, `--deploy-completion`, and
`--json --release-artifact` for owner-review output. The next provider run
still needs real artifacts, but the local path no longer depends on prose.

---

## 2026-05-23 - Post-guard commits still need post-guard reality checks

A guard commit can make the source safer while staging remains unchanged. After
`ebb7151`, the source had the hosted preflight guard, but the app-root mirror
and deployed staging app were still on hash
`181076c239b2d1d3d508a41ac471c71f9d2b5158`, so hosted preflight still failed
and owner-review data was still absent.

**Counter-move:** after a release-guard commit, run a read-only packet against
the actual provider/staging target before changing the next-step claim. Source
archive proof, app mirror proof, deployed app proof, staging data proof, and
owner-review readiness remain separate layers.

---

## 2026-05-23 - A hosted preflight file must prove target and checks, not just exist

The first hosted-preflight guard closed the "artifact required" gap but still
allowed a wrong-site, wrong-hash, or minimal hand-shaped `ok=true` artifact to
look valid. That is not enough for staging bootstrap, because the point of the
preflight is to prove the actual deployed staging app can run the exact
non-mutating checks for the exact release hash.

**Counter-move:** bind hosted preflight artifacts to provider snapshot
site/hash and app-mirror hash, require the hosted `required_checks` / `checks`
payload, sanitize HTTP error artifacts, and prove the controller path rejects
missing, no-go, wrong-site, and wrong-hash artifacts.

---

## 2026-05-23 - Last bootstrap status is forensic evidence, not a fresh preflight

The staging owner-review gate can read the last durable bootstrap status, which
is useful for explaining an earlier failure. It does not prove the current
hosted app can safely run the non-mutating bootstrap preflight now.

**Counter-move:** store the old bootstrap status in the no-go packet as
history only. Future staging bootstrap needs a fresh
`hosted-bootstrap-preflight.json` from the actual staging target after app
mirror freshness and provider snapshot proof.

---

## 2026-05-23 - Mirror sync changes release input state

The app-root mirror is not "just GitHub backup" in a Frappe Cloud custom-app
release. It is the source Frappe Cloud consumes. A mirror can be behind the
main source repo and still look like a harmless hash unless a verifier proves
the required hosted methods are actually present.

**Counter-move:** treat app mirror sync as a release-critical mutation during
forensic freeze. Use `scripts/verify/frappe_cloud_app_mirror_freshness.py` to
produce a read-only source-vs-mirror artifact before hosted preflight or
bootstrap. Do not sync the mirror while the freeze is active.

---

## 2026-05-23 - A no-go packet needs a post-commit docs parity pass

The read-only staging packet was correct as a no-go artifact, but some docs
still pointed at the guard-introduction commits (`58258fd`/`e44ecc2`) as if
they were the latest archive. That can make the next agent reason from the
wrong source state even when the no-go boundary is correct.

**Counter-move:** after a release artifact packet is committed, run a scoped
docs parity pass that names the latest GitHub archive separately from the app
mirror/deployed app hash. For the 2026-05-23 staging freeze, `ceab908` is
source archive proof only. It is not app mirror freshness, Frappe Cloud deploy
proof, staging data proof, or owner-review readiness.

---

## 2026-05-23 - Release verifier JSON must stay JSON when it fails

The staging owner-review gate supported `--json`, but on failure it appended
human failure lines after the JSON object. That made the most important release
artifact unparsable exactly when the release was blocked.

**Counter-move:** JSON mode must emit only machine-readable JSON and still
return nonzero on failure. Human failure summaries belong in non-JSON mode or a
separate parser/summary command.

---

## 2026-05-23 - A release packet needs artifact producers, not only validators

The release-prevention layer originally validated required artifacts, but the
provider snapshot itself still depended on ad hoc witness commands. That left
too much room for the next controller to improvise.

**Counter-move:** when a release gate requires an artifact, add either a
producer or an explicit contract for the producer. For LT, the provider
snapshot now has `scripts/verify/frappe_cloud_provider_snapshot.py`, and the
staging owner-review/bootstrap paths have offline contracts in
`scripts/verify/staging_owner_review_gate_contract.py` and
`scripts/verify/staging_owner_review_bootstrap_contract.py`.

---

## 2026-05-23 - A release stop rule needs a command agents already run

The release failure had correct-sounding process language, but the next agent
could still ignore it because no ordinary local command failed. The repair is
not another note. It is a package-level gate that fails locally before provider
mutation becomes reachable.

**Counter-move:** put release-prevention checks in `npm run` and make them
offline, fast, and explicit. For LT, use `npm run test:release-prevention` to
prove the active forensic-freeze lock, Frappe Cloud typed-payload contract, and
release-claim language gate. This does not prove staging; it prevents agents
from calling staging ready without the real gate.

---

## 2026-05-23 - Notes do not stop release churn unless scripts enforce them

The staging release failure already had warnings, handoffs, and triad language,
but the process still continued through repeated provider/bootstrap failures.
The failure was not only technical. It was a control failure: prose existed,
but no release lock, payload validator, circuit breaker, or required-doc gate
blocked more mutation.

**Counter-move:** release warnings must become executable stop gates. The
first local/offline guard layer was introduced at commit `58258fd`, and the
read-only no-go packet/provider snapshot was archived in `ceab908`. The next
release agent must still run the guard, preserve it, sync/prove app-root mirror
freshness after explicit freeze reopen, then take a fresh provider snapshot and
artifact-backed release packet before staging mutation. Use
`capabilities/failures/release-controller-churn-after-stop.md` before any
provider, staging, live, DNS, Stripe, Search Console, or launch recovery work.

---

## 2026-05-22 - Staging proof has separate layers that cannot borrow each other

The staging recovery failed operationally because several true statements were
allowed to sit too close together: local tests passed, GitHub had a commit, the
app mirror had a hash, Frappe Cloud accepted an API request, the site was
`Active`, and cache could be cleared. None of those facts proves the next
layer by itself.

**Counter-move:** every staging or release closeout must name the exact layer:
local source/test, GitHub archive, app mirror, Frappe Cloud deploy candidate,
site update/migrate, cache/config, staging routes, staging accounts/workflows,
or live/DNS/Stripe/Search Console. Use
`capabilities/failures/staging-proof-surface-conflation.md` before saying
anything is staging-ready or owner-ready.

---

## 2026-05-22 - Frappe Cloud API calls are enqueue signals until jobs are polled

The first Frappe Cloud staging deploy/update API request returned HTTP success
but passed nested `apps` and `sites` as form-encoded strings. The real failure
appeared later in the provider job as `'str' object has no attribute 'get'`.
The corrected JSON object-array payload did the right thing: it got far enough
to expose real migration failures instead of hiding behind a bad request
shape.

**Counter-move:** build Frappe Cloud nested payloads as typed JSON object
graphs, send `Content-Type: application/json`, then poll terminal provider
jobs. Treat `200`/`null` as enqueue-only. A deploy is not proved until deploy
candidate, site update/migrate, cache/config, installed hash/app order, no
running jobs, and staging route/account checks are all recorded.

---

## 2026-05-22 - Local role and settings state can hide Frappe Cloud migration bugs

Local migration and permission tests passed because the local database already
had the expected portal setting and custom LT roles. Staging did not. The site
update failed first on `Portal Settings.default_portal_home`, then on missing
`LT Owner Access` and `LT Manager Access` roles referenced by `Custom DocPerm`
rows.

**Counter-move:** source migration/sync code must own the target state it
writes. Safe staged setting drift should be repaired and then asserted; unsafe
or ambiguous drift should fail loudly with the exact field. Permission sync
must ensure custom Roles before writing permissions that link to them. Use
`capabilities/failures/frappe-cloud-release-site-migration-drift.md` and
`capabilities/failures/frappe-cloud-permission-role-fixture-order-drift.md`
before staging/backend access work.

---

## 2026-05-22 - Helper agents must own artifacts during release failures

The Frappe Cloud staging failure had helper agents, but the helpers were too
advisory to protect the release path. They produced useful analysis, but no
helper owned a required artifact: current provider-state proof, pre-mutation
payload-shape proof, or post-mutation success verifier. That let stale bench
assumptions, an invalid Frappe Cloud API payload shape, and deploy-hash versus
site-readiness confusion remain on the main agent's critical path.

**Counter-move:** release/build failure work needs owned outputs, not just
opinions. The Controller owns the critical path and stop/go gates; Witness owns
independent provider-state verification; Recorder owns docs/handoff parity;
Fixer owns concrete patch/verifier changes. Subagents must have narrow write
scopes, executable verification outputs, sanitized payload/response artifacts,
or blocking handoff sections that the Controller cannot bypass. Use
`capabilities/failures/artifactless-subagent-release-triad.md` before future
provider, staging, live, Search Console, Stripe, DNS, or major-build recovery.

---

## 2026-05-22 - Triads are required before release or patch-spiral claims

Release processes, major builds, and patch spirals are too easy to collapse
into "tests passed, ship it." The safe shape is a triad before commit, push,
staging, live, provider, or Search Console claims: one lens for risk, one for
handoff/docs/gates, and one for implementation gaps.

**Counter-move:** name the triad roles in the lane handoff and record what each
checked. Keep local proof, GitHub archive, staging proof, and live/provider
proof as separate states. If a verifier reads local Docker or local ERPNext
records, do not call it staging proof just because an HTTP base URL points at
staging.

---

## 2026-05-22 - Do not fix a runtime bypass by making the gate weaker

The Mickey Mouse Bouquet gallery regression looked like a missing thumbnail
problem, but triad review found a deeper risk: approved Product Setup media was
being read from raw child rows, bypassing the active Product Setup status gate.
When the helper was corrected to use active Product Setup schema, the local data
contract mismatch surfaced: published checkout backfills were still Draft, so
their approved media could not render.

**Counter-move:** keep runtime reads behind active Product Setup schema and fix
the data contract when published checkout products need that runtime data.
Published checkout backfills should be `Local Preview Ready`; non-checkout
backfills stay Draft. Run the Product Setup catalog sync with `--write`, then
run `product_setup_catalog_coverage.py` and `npm run
test:product-gallery-experience` before claiming product media is ready for
owner/staging review.

---

## 2026-05-22 - DB gallery rows are not enough without rendered route proof

The product-gallery restoration almost passed with the backend projection green
while some product routes still rendered no thumbnail rail. The root was a
template priority issue: Webshop fallback `slides` could be truthy with only a
primary image, so the LT Product Setup / Website Slideshow helper was never
used for some projected galleries.

**Counter-move:** product-gallery proof must cover all layers: source-approved
`gallery` rows, Product Setup rows, native Website Slideshow rows, linked
Website Items, and rendered browser routes. Keep selected variant media,
product gallery media, category/reference media, and ignored artifacts as
separate roles. Use
`workstreams/ecommerce-audit/product-gallery-restoration-2026-05-22.md`,
`python scripts\verify\product_gallery_projection_contract.py`, and
`npm run test:product-gallery-experience` before any staging/owner claim.

---

## 2026-05-22 - Do not use backend option text as the visible selected label

The option-text regression came from letting one string serve as both backend
source value and UI label. When the option value carried extra included-copy
detail, selecting a size made the product page repeat long text outside the
button and in the main details area.

**Counter-move:** keep source/stored option values for matching, but expose
separate display-label and included-copy fields in the rendered controls.
Selected tags should use the display label. Included-copy detail should be
rendered intentionally where the customer expects product details. Use
`workstreams/ecommerce-audit/product-option-selection-ux-2026-05-22.md` and
`npm run test:product-options-experience` before touching product option UI.

---

## 2026-05-22 - Owner access needs a business lane and a guard rail

The recovered owner-product work proved two things at once: Jeff needs real
product-control power, and raw ERPNext catalog tables are the wrong place for a
busy owner to exercise that power. Direct edits to Items, Website Items, Item
Prices, option attributes, Item Groups, gallery slideshows, or Webshop Settings
can make a page look fine while pricing, route, cart, checkout, or public media
truth drifts underneath it.

**Counter-move:** keep owner work in Product Setup and make raw catalog edits
fail loudly for owner-like users. Local apply must preserve existing public
Website Item visibility, reject publish/hide/reroute requests for existing
public products, keep published checkout backfills at `Local Preview Ready`
only when active runtime price/media preview needs them, keep non-checkout
backfills in Draft until reviewed, and verify the hook surface with real
owner-like probes. Use
`workstreams/ecommerce-audit/owner-product-setup-guard-closeout-2026-05-22.md`
and `npm run test:owner-product-safety` before staging owner product work.

---

## 2026-05-21 - Do not make indexing all-or-nothing during ecommerce review

After the site switch, the urgent question was whether to index everything,
keep everything hidden, or only hold products. The correct model is selective:
stable business pages can be discoverable while unfinished ecommerce remains
out of the sitemap and emits `noindex`.

**Counter-move:** separate crawler access from indexing permission. Keep
`robots.txt` crawlable so Google can see page-level `noindex`; use robots meta
for noindex; exclude paused ecommerce discovery paths from the sitemap; keep
staging globally noindex with `lt_public_indexing_enabled=0`; and submit
Search Console only after live canonical/sitemap/robots proof passes on
`https://locallytwisted.com`.

Feature handoff:
`workstreams/selective-indexing-gate-2026-05-21.md`.

---

## 2026-05-21 - Capability notes must become support systems when risk or value demands it

Writing a capability card is not enough when the pattern protects client money,
customer trust, live release paths, provider accounts, public forms, checkout,
or parallel-agent boundaries. A card can reduce rediscovery, but it cannot by
itself stop a bad push, prove a route, preserve a customer promise, or make an
agent remember the safe path.

**Counter-move:** use the Capability Graduation Ladder. Keep low-risk cards
`reference_only`, but graduate important patterns into `skill_backed`,
`verifier_backed`, `gate_backed`, `automation_backed`,
`architecture_backed`, or `release_live_approval_backed` support. In LT,
start cleanup-first through
`workstreams/capability-graduation-ladder-2026-05-21.md` because existing graph
debt must be repaired before trust promotion.

---

## 2026-05-21 - Clean child/client repos still need explicit coordination proof

LT being clean is not enough to make parallel agent work safe. Because it sits
inside the Built by Cameron repo forest and pays the bills, future agents must
prove the coordination workflow with a read-only dry run before using LT as a
parallel editing target.

**Counter-move:** start LT sessions by reading the neutral startup checklist,
confirming the child/client Git root, checking the live board and registry, and
naming the Six-Box write target before any edit. Use
`workstreams/coordination-safety-pilot-2026-05-21.md` as the pilot receipt.

---

## 2026-05-20 - Product-page copy can break the commerce contract

Classic Arch was correctly treated as a quote-first complex product by the
runtime product contract, but the fulfillment panel still showed checkout pickup
language because it used Item Group fallback instead of the resolved Website
Item commerce lane. The page looked visually acceptable, but it made the wrong
customer promise.

**Counter-move:** product-page proof must check the visible promises, not only
the selected variant, price, and add-to-cart controls. When a product is
`quote_first` or `needs_review`, the page must not contain checkout pickup copy
and must contain quote/install language. Keep `smoke_shop.py` as the customer
copy guard, and use
`capabilities/failures/product-fulfillment-copy-lane-drift.md` before changing
fulfillment panels, product contracts, or category fallback logic.

---

## 2026-05-19 - Price existence is not source-price truth

The Easter Bunny Ear Arch failure was not a product-page styling bug and not a
single Odoo import cleanup. GL selected different sizes and the price did not
change. The cart/checkout architecture was mostly doing the right thing by
trusting server-side ERPNext `Item Price`; the deeper failure was that many
variant Item Prices had been flattened upstream by an import path and the
guard stack did not block it.

**Counter-move:** ecommerce proof must start with source price identity, not
internal agreement. For source-derived variant products, verify source dynamic
price logic -> ERPNext variant `Item Price` -> visible product page -> cart ->
checkout/order/payment/invoice/receipt. A verifier that proves "every variant
has a price" or "Stripe matches ERPNext" is necessary but not sufficient; it
can perfectly preserve the wrong price. Use
`workstreams/ecommerce-price-identity-incident-review-2026-05-19.md` and
`capabilities/failures/ecommerce-variant-price-source-drift.md` before any
future ecommerce import, checkout launch, or broad product-pricing claim.

---

## 2026-05-19 - DNS cutover proof is not SEO discovery proof

Cloudflare and Frappe Cloud can be correctly serving a site while the sitemap,
canonical tags, Open Graph URLs, or structured data still point at a staging or
vanity host. LT's public domain returned `200` from Frappe Cloud, but the live
sitemap had 29/29 URLs on `locallytwisted.v.frappe.cloud`, and `/about`
canonical/`og:url` used the same vanity host. That would make a Search Console
reindex request actively harmful.

**Counter-move:** after any DNS/Frappe Cloud/custom-domain cutover, verify the
discovery layer separately: sitemap hosts, canonical hosts, `og:url`,
structured-data URLs, robots sitemap hint, and Search Console property. Run
the SEO contract against the public domain before submitting a sitemap or
requesting URL Inspection. Route health is necessary, but it is not enough.

---

## 2026-05-19 - Provider account control is not an inbox crawl

The ad takeover request started with a real Google Ads policy URL and a clear
business goal: take control of Google Ads and Facebook/Instagram ads. The
mailbox/Drive crawl found useful support evidence, including the Google Ads
customer ID, ENB manager/admin evidence, campaign history, billing warnings,
tracking issues, and Meta/HighLevel lead-pipeline clues. But it did not give
GL what was asked for: the ability to see and manage the current provider
accounts.

**Counter-move:** when GL gives a provider dashboard URL or asks to see/manage
an account, open the authenticated dashboard first and state the exact
dashboard state or blocker. Use Gmail, Drive, reports, and public ad libraries
only as supporting context after the account-control path is attempted. For
LT ads, use `workstreams/ad-account-takeover-2026-05-19.md` and
`capabilities/recipes/ad-account-takeover-provider-control.md`; do not remove
ENB/agency access until dashboard exports and lead-routing dependencies are
captured.

---

## 2026-05-18 - Sellable product does not mean raw-source checkout

The all-Odoo sellable reimport correctly restored every imported item as a
product, but the next review exposed a different failure: high-complexity
products with 50+ raw color choices were still direct checkout products. That
made products "sellable" by flattening business nuance into unsafe SKU axes.
Graduation products needed bounded college presets; Classic Arch, Classic
Column, custom school/corporate colors, Halloween, and baby scheme products
needed quote-request handling until their color logic and operator flow are
reviewed.

**Counter-move:** separate product existence from checkout readiness. A product
can be real and still require quote request. Write both guards: a negative
guard that fails if raw 50+ color axes can enter checkout, and a positive guard
that proves approved preset products still add to cart with price and selected
configuration intact. Do not use "all products are products" as permission to
expose every source option directly to payment.

---

## 2026-05-18 - One-off data repairs must become import closeout steps

After the all-Odoo sellable reimport, `catalog_variant_contract.py` failed
because 390 old `Add Foil Number` variants were enabled again as active SKU
choices. The repair script already existed and worked, but it was not wired
into the import runner, so the system depended on an agent remembering to run
it manually.

**Counter-move:** when a local repair corrects imported catalog shape, decide
whether it is a one-time rescue or a required import closeout step. If the
same stale state can reappear on rerun, wire the repair into the importer and
keep the verifier strict. Do not "fix" this class by updating counts to match
bad data.

---

## 2026-05-17 - Safety gates must preserve known-good product behavior

The Encanto Bouquet regression was not missing data. ERPNext still had
`encanto-bouquet-SMA`, `encanto-bouquet-MED`, and `encanto-bouquet-LAR` images
stored on the variant Items. The failure was an overbroad media safety gate:
while trying to hold unclassified source extra/gallery images, the code also
held simple checkout variant `Item.image` values that were already meaningful
customer-selection media. A later gallery pass proved the same lesson from the
other direction: source-approved product-page gallery media also needs its own
positive path, not a blanket hold. The verifier had been rewritten to expect
the broken behavior, which hid the regression until GL tested the product.

**Counter-move:** when adding a safety gate, first name the known-good
behaviors that must survive. Then write both positive and negative guards.
For LT variant media, the positive guard is Encanto Small/Medium/Large image
swap plus cart/order/receipt cascade. The negative guard is Classic Arch
complex raw media staying held without Product Setup approval. Do not collapse
different media classes - parent primary image, simple variant Item image,
Product Setup media rule, approved product gallery image, and unclassified
category/reference media - into one generic "hold everything" rule.

---

## 2026-05-17 - Browser proof route authority must be the live Website Item route

After the all-Odoo import, `post_import_checkout_proof.js` correctly loaded
all 53 products from the V1 manifest but initially used planned manifest routes
for browser navigation. `baby-shower-combination-photo-opt` failed at 404
because the current Website Item route is
`/shop-items/table-decor/baby-shower-combination-photo-opt`, not the planned
route in the import manifest. The product was fine; the verifier route source
was stale.

**Counter-move:** use the import manifest for inclusion/sale-unit authority
and the live/clean Website Item snapshot for public route authority. Browser
proofs should fail loudly if those two sources cannot be joined by item code,
because route drift is a storefront contract issue, not a product-exclusion
reason.

---

## 2026-05-17 - Product contract authority must outrank category fallback

The local all-Odoo sellable reimport correctly stored `7-butterfly-column` as
`complex_custom_product|checkout`, but the rendered page still showed the
quote-first gate until the Frappe web worker restarted. The immediate code
cause was older product-page/shop/cart paths using item-group/category checkout
lane fallback instead of the Website Item product contract. The operational
cause was assuming a green backend field meant the rendered route had picked
up the same authority.

**Counter-move:** after changing product import/classification rules, prove the
actual product routes in a browser, not just database fields. Product pages,
shop cards, cart display rows, and checkout preview must all read from the
same product-level Website Item contract before any legacy category fallback.
If Python/Jinja route output contradicts a fresh bench Python check, restart
the local Frappe backend worker, clear website cache, and re-test the route.

---

## 2026-05-17 - All-product browser proof must respect cart safety caps

The first all-53 browser proof failed at `/cart` because the verifier added 53
line items into one browser cart. That was not a product failure; it hit the
intentional 50-line cart API cap that protects public requests. Splitting the
same live-route list into 27-product and 26-product batches made the proof
valid and both batches passed.

**Counter-move:** when proving whole-catalog checkout surfaces, match the
verifier shape to production safety limits. A batch proof can still cover
every product, but each batch must stay under request caps and state that the
split is intentional.

---

## 2026-05-17 - Browser proofs should click visible product controls

The multi-color browser proof failed on the first attempt because the verifier
used Playwright `check()` directly on the color checkbox input. The actual
customer control is the visible color card label, and clicking the label is
what reliably triggers the UI's hidden-select sync and variant refresh path.

**Counter-move:** for product-page browser proofs, interact through the visible
control the customer sees: chip label, color card label, select, or button.
Then wait for the real downstream state, such as checked input plus hidden
color select plus cart `color_recipes`, instead of trusting the low-level input
action alone.

---

## 2026-05-17 - Source color casing drift can break product proof

The multi-color rehearsal initially failed before checkout because Odoo had
duplicate source color labels with different casing, such as `Blue Slate` /
`Blue slate` and `Smoke Grey` / `Smoke grey`. The Item Attribute fixture path
already knew to collapse those values, but the runtime color canonicalizer did
not yet know the same aliases.

**Counter-move:** color cleanup must be shared by import, product-page runtime,
cart/checkout validation, and verifier expectations. When a source product
looks short by one or two color values, check the Odoo value-normalize map
before assuming the product export or ERPNext variants are wrong.

---

## 2026-05-17 - Variant media proof is not done until payment and receipt pass

The Product Setup selected image worked on the product page/cart/checkout path,
but the real fake-card purchase still exposed two backend failures: Stripe
return reconciliation ran under Guest and could not create the Payment Entry,
then the invoice path used a group tax account. The customer page correctly
said reconciliation was pending, but the ecommerce proof itself was not done.

**Counter-move:** for ecommerce Product Setup work, verify the whole customer
money path before calling it release-ready: selected media -> cart -> checkout
-> Stripe test card -> Payment Request Paid -> Payment Entry -> Sales Invoice
-> customer receipt email. Contracts should include the ugly retry shape too,
where an invoice already exists before the Payment Request is settled.

---

## 2026-05-17 - Merged worktrees still need value review before deletion

During repo cleanup, two detached Codex worktrees were clean and already
merged into `main`, but GL asked the right follow-up: had their value actually
been reviewed and applied? A clean ancestor check proves deletion is unlikely
to lose commits; it does not prove the agent understood what the worktree was
for or whether a newer doc/code path had superseded it.

**Counter-move:** before deleting stale LT worktrees, check four things:
status clean, HEAD is an ancestor of `main` and `origin/main`, the latest
visible topic is already present in current source/docs/verifiers, and GL has
approved the exact path deletion. Record the review in the cleanup handoff so
future agents can see that feature value was preserved, not merely discarded.

---

## 2026-05-17 - Clean-clone publishing can leave duplicate local history

Publishing from clean temporary clones protected the shared LT checkout from
unrelated local work, but it left local `main` with duplicate commits beside
the clean pushed hashes on `origin/main`. The files were clean, but the graph
looked ahead/behind and could confuse later agents or pushes.

**Counter-move:** after clean-clone publishing is finished, reconcile local
`main` back to `origin/main`. Use rebase only from a clean file tree, map each
local duplicate to the pushed commit that already contains it, skip/drop only
after that evidence, then verify `HEAD == origin/main`, no file diffs, no
untracked files, no conflict markers, and no stale temp clones.

---

## 2026-05-15 - Assistant access needs a business DTO before provider adapters

The owner access request started with ChatGPT language, then expanded to
OAuth-agnostic/API-compatible access. Building directly for one assistant would
have made the provider look like the architecture and would have encouraged
raw ERPNext record access before the business boundary was clear.

**Counter-move:** define the owner-safe business DTO first, then let ChatGPT,
MCP, OpenAPI, OAuth, API-key, or other clients become adapters. Keep the first
write narrow and verifiable. For LT owner access, the first write is only
`log_contact_attempt`, which creates one Comment and does not send customer
messages or mutate business/accounting state. Prove the real owner login,
phone page, DTO contract, and fake local data cleanup before discussing any
external provider integration.

---

## 2026-05-15 - Narrow reviewer roles need explicit membership checks

The first marketing review access guard used Frappe's effective role lookup.
That looked fine for a temporary Website User, but it misclassified
Administrator/bench contexts because Administrator can appear to have framework
roles broadly. The result was not a marketing data leak; it was the opposite
failure mode: customer portal verifiers could not create rollback fixtures
because the marketing mutation guard treated admin execution as a marketing
reviewer.

**Counter-move:** for narrow external-access lanes, check the explicit
`Has Role` child row on the User record before applying the boundary. Keep
effective role helpers for normal role-aware UI logic, not for least-privilege
access guards that must distinguish admin/test contexts from the external
account. After touching auth hooks, rerun both the new boundary verifier and
the adjacent customer/Desk contracts.

---

## 2026-05-15 - Lead File attachments are not CRM photo storage

The missing production inquiry photo was not missing from ERPNext entirely:
Lead `CRM-LEAD-2026-00007` had private File `44b4de500d`, but
`custom_inspiration_photos_count` was `0` and owner Email Queue rows had
`attachments: []`. The old verifier proved a count and queue existence, but it
did not prove the backend storage surface the business owner sees or the
queued attachment refs Frappe uses for owner mail.

**Counter-move:** public inquiry photo proof must check all three backend
surfaces: private Lead `File` rows, matching `custom_inspiration_photos` child
rows, and owner-only `Email Queue.attachments` JSON `fid` refs. Customer
confirmations stay attachment-free and count-only. Do not use Gmail or
personal inboxes as the source of truth for form-upload storage.

---

## 2026-05-14 - Route health and provider control are separate claims

The 2026-05-14 Frappe Cloud check could honestly say the live site is served by
Frappe Cloud and that Cloudflare dynamic routes are healthy. It could not
honestly say Codex has direct Frappe Cloud dashboard/API/CLI control. No direct
Frappe Cloud CLI, host `bench`, or Frappe Cloud env vars were present on the
host during the audit.

**Counter-move:** every launch/provider handoff must name the verified surface:
public route, dynamic Cloudflare route, local Docker stack, SSH key readiness,
dashboard session, API token, or CLI. Use `frappe_cloud_preflight.py` for
GitHub/app/SSH/DNS shape and `cloudflare_launch_readiness.py` for route health,
but do not use either as dashboard-login proof.

---

## 2026-05-14 - A live safety lock is not an implementation excuse

The ecommerce lane started looping on the phrase "intentionally paused" as if
the pause itself explained why local product/cart/checkout work could stop.
GL corrected the frame: live ecommerce is locked because it is broken,
incomplete, and not trustworthy for customers yet. The lock protects customers
while the local work fixes the actual problems.

**Counter-move:** when `lt_ecommerce_paused=1` is present, first decide whether
the task is about public/live exposure or local/staging/test-harness build work.
For live exposure, keep the lock until release gates pass. For build work,
continue under the lock and name the real blocker: incomplete UI, missing
employee authoring, unmapped add-ons, unresolved pricing, unsafe checkout,
unverified media, failed verifier, missing staging proof, or owner approval.

---

## 2026-05-14 - Employee product authoring cannot depend on an agent editing code

The ecommerce architecture could preserve existing fixture/Odoo-derived product
meaning, but GL clarified that employees must be able to add future highly
custom products through the software interface. A flow where Codex writes each
product as code does not bridge the operational gap.

**Counter-move:** custom product work needs a staff-facing record, validation
evidence, preview/apply plan, and runtime cascade proof. For LT that surface is
`LT Product Blueprint`, backed by `product_blueprint_contract.py` and
`product_blueprint_live_contract.py`. Treat Odoo as a behavior witness, not the
boundary of what the product architecture can express.

---

## 2026-05-12 - Complex checkout needs a scaffold, not a product-name hunch

The storefront proof showed which products were currently quote-gated, but the
first heuristic lane-flip list mixed simple sale-unit products with
multi-color recipes, add-ons, conditional pricing, freeform text, and
needs-review products. That could let a product look ready because it renders,
while checkout would still lose the customer's selected meaning or price it
wrong downstream.

**Counter-move:** before flipping any quote-first product, run the
source-backed complex checkout scaffold. It must classify the product lane,
name the missing UI/server contracts, preserve direct-checkout regression
guards, and keep live checkout enablement false until the focused local proof
passes.

---

## 2026-05-12 - A Frappe Cloud deploy hash is not live release proof

The live app hash changed while the site was still serving old behavior because
the site update/migration had not completed successfully. The failed migrations
were real release blockers: blank mandatory System Settings fields, local-only
Lead/custom DocType schema drift, and an unguarded optional legacy
`custom_services` query.

**Counter-move:** for Frappe Cloud, require both bench deploy success and site
update/migrate success before claiming the release. Then run live route/API/form
verifiers against the public domain. Source must own every custom field/DocType
needed by live code, and optional legacy fields must be metadata-guarded before
querying.

---

## 2026-05-12 - Email smoke tests must read the message, not just the flag

The form smoke test was not sufficient because it did not prove the content GL
needed: what the client said, the details they provided, and the owner-facing
version of the same information. A queued flag can still hide wrong recipients,
customer-directed owner copy, missing submitted fields, or internal fallback
markers leaking into the message.

**Counter-move:** public form launch proof must inspect the actual Email Queue
body and recipients for both customer and owner paths. Owner copy should be
directed at the business while carrying the same customer-submitted details.
Customer and owner email bodies must strip internal markers such as
`Customer email:` before display.

---

## 2026-05-12 - Repeat customers are not duplicate inquiries

After DNS cutover, repeat same-email public form submissions returned `409`
because ERPNext's linked Email Address record is unique. That platform rule is
not the business rule: one customer can ask for multiple events, and every one
must create a separate opportunity.

**Counter-move:** public inquiry code must accept repeat same-email Leads. If
the unique Email Address link blocks the insert, retry without `email_id`,
preserve the customer email in a controlled internal fallback, and ensure
customer/owner rendering still shows the real submitted email without leaking
the fallback marker.

---

## 2026-05-12 - Logged-in launch access means agents own dashboard work

During the Frappe Cloud launch, the agent gave GL manual dashboard steps after
GL had already logged into Frappe Cloud and Cloudflare and had prepared the
research/process path. That converted agent-owned deployment work into human
busywork at the exact cutover point.

**Counter-move:** once GL says the account is logged in or access is available,
the agent owns the provider workflow through browser automation, CLI/API, SSH,
or the documented project process. Ask GL only for MFA, missing credentials,
payment/business approval, or a destructive go/no-go. Do not hand GL a checklist
for Frappe Cloud app install, site config, cache clear, or DNS mutation when the
agent has an available execution path.

---

## 2026-05-12 - Lead reference names are not email idempotency boundaries

The Contact form reused `CRM-LEAD-2026-00073`, and an older sent Email Queue row
from the prior Lead with that name suppressed the new customer confirmation.
The customer saw success while the current Lead initially had no current
confirmation queue row.

**Counter-move:** public-form confirmation idempotency must include the current
Lead's creation boundary for both `Email Queue` and `Communication` lookups.
After `frappe.sendmail`, assert a current queue row exists before returning
`message.ok`. Preserve historical queue rows; narrow the query instead of
deleting evidence.

---

## 2026-05-12 - Playwright speed settings can become fixture corruption

Changing Playwright to run tests inside each spec file concurrently looked like
a harmless speed improvement, but LT specs often share backend fixtures,
markers, or cleanup inside a file. `quote_accept_experience.spec.js` is the
known reviewed example.

**Counter-move:** default Playwright to one worker and no in-file parallelism.
Use `LT_PLAYWRIGHT_FULLY_PARALLEL=1` only for specs that prove per-test fixture
isolation. If proof is slow, split independent specs or create unique per-test
namespaces; do not weaken cleanup.

---

## 2026-05-12 - Owner include is not checkout eligibility

The Ready-to-Order nav/search patch almost let an owner-included item code
advertise as checkout-ready even if ERPNext Website Item fields later reverted
to `quote_first` or `needs_review`. The same review also caught a false test
assumption: the search overlay hides filtered quick-link nodes with `hidden`
instead of removing them from the DOM.

**Counter-move:** keep merchandising allowlists separate from backend commerce
eligibility. Assert both: owner-included products still need explicit
`simple_product|checkout`, and search tests must distinguish hidden entries
from absent owner-excluded entries.

---

## 2026-05-11 - Stale written contracts can be the regression

The public short-notice banner regressed from deep navy to brass/gold because a
May 10 change updated CSS and docs/guards together in the wrong direction. The
next agent could read the stale handoff/capability text and reasonably believe
gold was approved, even after the live site had been corrected back to blue.

**Counter-move:** when a visual regression repeats, trace both code history and
contract history. Fix the source CSS, rendered verifier, static verifier,
feature handoff, queue/handoff notes, and capability/failure recipe together.
Do not close banner/header work while active docs still describe the wrong
color as approved.

---

## 2026-05-11 - Page fixes need the actual requested fix first

The landing-page pass started from a broad "fix the landing page" frame before
the exact requested fix was named. GL corrected the failure: without direction,
the agent was guessing at the surface and creating distrust before the real task
arrived.

**Counter-move:** when a visual/page request is broad and GL has not named the
specific defect, stop at orientation and ask for the exact target. Once GL names
the target, keep the slice narrow, preserve requested recovery assets, and do
not fold unrelated polish into the same closeout.

---

## 2026-05-11 - A working logout endpoint is not a working logout experience

Frappe's `/?cmd=web_logout` path worked, but the LT custom header/account shell
did not expose it clearly enough. A signed-in user could reach public/account
surfaces with no obvious way out, which is a customer-trust failure even when
the backend endpoint is healthy.

**Counter-move:** auth/session UX needs a visible signed-in escape hatch in
every custom public chrome and account shell. Verify the full loop: login,
visible logout affordance, click logout, and return to logged-out state.

---

## 2026-05-11 - Hiding a visual block needs a recovery artifact

GL asked to hide Custom Event Decor but keep the icons and a screenshot in case
the block comes back. A code flag alone is not enough: future agents need the
visual state and icon source without relying on memory or guessing from Git.

**Counter-move:** when a user asks to hide, park, or remove a visual section but
explicitly wants it recoverable, create a small durable archive with a screenshot,
source assets, and a manifest. Document the restoration flag and verification
commands in the feature handoff.

---

## 2026-05-11 - Technical preflight is not account access

The launch prep initially grouped Frappe Cloud, Cloudflare, and Stripe as if
they were the same kind of readiness check. They are not. Frappe Cloud preflight
can prove GitHub/app/SSH shape while dashboard ownership is still unconfirmed.
Cloudflare nameservers can be delegated while Codex still cannot edit DNS.
Stripe CLI can be logged into a live-capable account while the business still
needs to decide whether that is the right merchant account for LT.

**Counter-move:** split launch docs into machine-verifiable gates and human
account-control gates. For LT, use `LT-LAUNCH-RUNBOOK.md` for the operator
checklist and `workstreams/frappe-cloud-cloudflare-stripe-launch-2026-05-11.md`
for the technical cutover gate. Do not claim DNS/payment readiness until both
the technical gate and human account-control boundary are satisfied.

---

## 2026-05-11 - No cards means no containers, labels, or helpful filler

GL rejected the homepage review-platform treatment because "no cards" also
meant no visual containers, no smaller proof marks, no poor logo assets, no
visible count copy, and no invented `reviews` label under each platform. The
request was for logo proof, not a review widget.

**Counter-move:** when GL removes a visual pattern, strip the whole pattern
family. If the instruction is "just the logo," do not add helper text,
counts, cards, borders, shadows, padded boxes, or explanatory labels unless
asked.

---

## 2026-05-11 - An unapproved route should die loudly before launch

`/event-balloons` had not launched or been indexed, so a redirect would have
preserved an unapproved page instead of cleaning the route. The correct repair
was deletion plus negative route/link/sitemap/canonical guards: 404 with no
redirect, no source links, no sitemap entry, no compatibility page.

**Counter-move:** before launch, do not invent redirects for pages GL rejects.
Delete the route source, remove every discovery path, then add negative
verifiers so future agents cannot recreate the page by "fixing" the 404.

---

## 2026-05-11 - Family/page counts are not SKU proof

The checkout audit initially reported 15 checkout products because the classifier counted Website Item families/pages. GL correctly challenged that wording: current enabled checkout coverage is 15 families/pages but 47 sellable SKUs, and the backend proof must account for 86 order/invoice rows once bouquet add-ons are included.

**Counter-move:** in ecommerce migrations, always name the counting unit: Website Item/page, product family, enabled sale SKU, add-on line, Sales Order row, Sales Invoice row. A representative variant is useful for a first cut, but closeout proof for checkout architecture must walk every enabled sellable SKU or explicitly state it is sample-only.

---


## 2026-05-10 - Test products are not import proof

The ecommerce phases proved important receiving behavior against current ERPNext product records, but GL corrected the frame: those products are test fixtures. The real catalog proof is whether a clean purge/reupload/import path fills the right LT schema fields, preserves cascading/dependency information, and triggers the intended automations.

**Counter-move:** when auditing ecommerce/shop, separate runtime behavior proof from import/rebuild proof. Use current products to exercise verifiers, but do not make final catalog claims until a controlled import audit proves the receiving system from clean input. Destructive purge/reupload requires fresh preflight and explicit approval.

---

## 2026-05-10 - Checkout eligibility is an allow-list, not an inference

Phase 4 proved that blank or partial Website Item ecommerce fields are dangerous. A price, a sellable variant, or an inferred page template can make a product look checkout-ready while the business meaning still belongs in quote/review.

**Counter-move:** direct paid checkout must require an explicit `simple_product|checkout` contract. Treat blank fields, mixed fields, inferred checkout, `needs_review`, stale localStorage, old cart schemas, and direct checkout URLs as fail-closed paths. Verifiers should attack every bypass, not just the normal add-to-cart button.

---

## 2026-05-10 - Review CONCERNs are build inputs, not commentary

Phase 4 architecture and edge-case reviews both found real gaps after the first implementation: partial Website Item drift, no-sellable-candidate coverage, malformed/stale cart shapes, and sample-only artifact rows. Treating those as reviewer notes would have left the false-checkout boundary porous.

**Counter-move:** when an independent review returns CONCERN, add code and verifier cases until the reviewer can reread a durable artifact and pass it. The parent agent must read the artifact, not just accept the rerun summary.

---


## 2026-05-10 - Launch cleanup needs an evidence-retention rule

The launch repo had several different kinds of weight mixed together: generated test output, old mirror/audit folders, raw photo drops, stale research throwaways, active feature work, and production source. Treating all of that as either "junk" or "keep" would have been wrong.

**Counter-move:** sort cleanup candidates by role before deleting. Remove regenerable ignored output. Move raw useful drops outside the repo until curated. Delete tracked old experiments only after their production value has been translated and Git history can be the archive. Leave active modified work from other agents alone, and commit cleanup through an explicit file list or isolated index.

---

## 2026-05-10 - A passing live verifier can still fail cleanup

The repeat-email/five-photo form verifier proved the customer path but left fake Leads, uploaded Files, Communications, Email Queue rows, Contacts, Tasks, and Comments behind. Those records then polluted later email previews, paperwork counts, and operator evidence even though the verifier itself had passed.

**Counter-move:** any verifier that creates real ERPNext records needs a cleanup contract as part of the test, not as a manual afterthought. Use a guarded fake namespace, delete old residue before the run, delete current records after the run, and fail if cleanup is unavailable or incomplete unless an explicit debugging flag keeps records.

---

## 2026-05-10 - Header/footer chrome is not a side effect of SEO work

Owner-removed header/banner items came back while the work was framed around
public-site/SEO/service-nav improvement. `Free Event Quote` also appeared in
multiple chrome zones because an older verifier encoded that duplicate state.

**Counter-move:** treat header, footer, menu, mobile drawer, search quick
links, and top-banner slots as customer-facing business signage. SEO/GEO/AEO
agents can change metadata, sitemap, canonical, structured data, FAQ/AEO
content, and page copy inside their scope; they need explicit approval before
changing chrome. Update the verifier first so it fails against the current bad
state, then repair the smallest template surface.

## 2026-05-10 - Header accessibility can fail outside the static screenshot

The gold banner looked repaired at rest, but hover/focus text became white on
brass at 2.65:1 contrast and mobile landscape safe-area padding protected the
wrong side.

**Counter-move:** when a public header strip changes color or padding, verify
the interaction-state color and safe-area side order, not just text presence.
For LT, `nav_ia.py` now checks the exact CSS failure alongside the template IA
contract.

## 2026-05-10 - Capability path ownership is architecture, not cleanup

Moving LT capabilities from `.codex/capabilities/` to `capabilities/` was not a
cosmetic path cleanup. The path itself was teaching future agents that Codex
owned the project operating knowledge, which breaks parity with OpenClaw,
Claude, and future agents.

**Counter-move:** put capability roots where their scope is true:
`C:\Users\baenb\capabilities` for system/user knowledge,
`Built_by_Cameron/capabilities` for agency knowledge, and
`<project>/capabilities` for project knowledge. Runtime folders are adapters or
compatibility pointers only.

---

## 2026-05-10 - Header microcopy slots need explicit ownership

The short-notice message was initially placed as a utility-list item beside `Free Event Quote` and account links while the old prepared-design proof copy/truck icon stayed in the left proof slot. GL's correction showed the actual contract: replace the proof slot with the short-notice promise, keep the conversion/account links, and delete stale proof chrome.

**Counter-move:** treat header/banner slots as named surfaces, not generic places to stuff copy. If a message supersedes an existing proof line, remove the old copy/icon and add verifier checks for both presence of the new slot and absence of the retired slot. Positive checks for new copy are not enough.

## 2026-05-10 - No artifact means no evidence, even when an agent reports completion

The ecommerce audit dispatch proved the failure mode clearly: Lane B, C, and D produced named files that can be inspected. Lane A and Lane E did not. Their routed completion text may be useful debugging context, but it is not evidence for source mapping, docs convergence, import safety, or launch readiness.

**Counter-move:** any delegated research/build lane that affects product migration, checkout, payment, customer records, or launch decisions must name its artifact path up front and write the file before reporting complete. Parent agents must reject artifactless lanes as `[NO EVIDENCE]`, update the handoff with the gap, and rerun narrowly rather than synthesizing from memory or truncated transcript text.

## 2026-05-10 - Version mismatch labels are part of ecommerce evidence

The destination runtime reported ERPNext `15.105.0` and Frappe `15.106.0`, while the dispatch anchor named `frappe/erpnext:v15.105.0` and the container image appeared as `locally-twisted-erpnext:v15`. The Odoo source witness local module reported `19.0.2.15.0`, while prior notes warn production may be `19.0.2.14.0`.

**Counter-move:** carry `[VERSION-MISMATCH]` or equivalent labels directly in research artifacts and handoffs. Do not let a useful proof slice become a false universal claim when source/destination versions are unresolved.


## 2026-05-10 - Optional add-ons are not variant-chip checkboxes

When public ecommerce reopened, `smoke_shop.py` failed because it counted every checkbox inside `.lt-product__configure` as a variant-chip failure. The only checkbox on the tested page was the optional foil-number add-on toggle; the variant choices themselves were already radio/single-select.

**Counter-move:** scope selector assertions to the behavior they own. Variant chip contracts should inspect `.lt-product__chips`, while optional add-on contracts should separately prove add-ons are explicit toggles with backend eligibility, value requirements, cart/checkout preservation, and invoice/order line behavior.

## 2026-05-10 - Commerce smoke tests must follow the configured commerce mode

`smoke_shop.py` was still asserting open-shop navigation, category rails, cards, and product-detail controls after public ecommerce had intentionally been paused. That made the verifier red for the wrong reason and hid the real state: the pause contract was working.

**Counter-move:** launch/shop smoke tests must detect the configured commerce mode first. In paused mode, prove the branded pause routes, current public chrome, service lanes, and safe quote fallback; skip open-shop card/rail/product-detail checks. In open-commerce mode, run the full shop/product/cart assertions.

---

## 2026-05-10 - Rollback-safe Frappe verifiers are not parallel-safe

A batch run launched several rollback-style ERPNext/Frappe verifiers against the same local site in parallel. One product quote customization contract briefly failed because another verifier's rollback/test mutation made its fake Lead disappear mid-contract. The same contract passed immediately when rerun alone.

**Counter-move:** run rollback-safe Frappe database verifiers sequentially unless they are explicitly designed for parallel isolation. Browser-only Playwright checks can run in their normal worker model, but tests that monkeypatch `frappe.db.commit`, create fake Leads/Quotations/Sales Orders, or call `frappe.db.rollback()` share the same site state and can invalidate each other.

---

## 2026-05-10 - Cleared business blockers and live commerce state are separate gates

The product-page architecture audit had real source/business blocker rows for add-ons, live-snapshot prices, and media classification. After GL cleared those blocks for commerce-lane testing, the site still needed to be paused again for V1 launch. A green open-commerce architecture pass is not the same thing as permission to leave checkout open to customers.

**Counter-move:** model business approval rows, technical architecture health, and public live/open state separately. A readiness gate should say exactly which layer is blocking. When GL clears a business review blocker and then says pause, verify both modes: pass while temporarily open, then restore the pause config and prove the public pause contract.

---

## 2026-05-10 - Approval links need their own backend gate, not just Desk controls

The product-page quote Desk send button already checked `Ready For Customer Review`, but the token issuance and customer-acceptance helpers could still be called directly. That left a backend path where a submitted/priced quote in `Needs Operator Review` could create a draft Sales Order.

**Counter-move:** treat token creation, public acceptance, and downstream order creation as separate trust boundaries. Each one must enforce the same readiness gate and have verifier coverage that calls the helper directly, not only through the UI wrapper.

---

## 2026-05-10 - Missing audit fields are blockers, not optional enrichment

The quote acceptance bridge copied source quote and written-approval details to Sales Order fields only when the fields existed. If fixtures/custom fields were missing, it could still create a draft Sales Order without idempotency or audit trace fields.

**Counter-move:** any downstream record that depends on custom fields for idempotency, audit, accounting traceability, or customer approval must fail before mutation if those fields are absent. The verifier should temporarily remove field metadata and prove the path fails loudly.

---

## 2026-05-10 - SEO structured-data tests must follow visible page truth

The SEO contract failed because it still expected an older FAQ set while `/faq` had moved to service-specific questions. The structured-data gate became stale even though the page itself was current.

**Counter-move:** when FAQ content changes, update the visible question source and the FAQPage JSON-LD verifier in the same slice. Tests should assert parity between current visible questions and structured data, not preserve old content as a hidden requirement.

---

## 2026-05-10 - Service lanes are business inventory, not nav copy

`Twisting & Face Painting` disappeared from public chrome twice: first when broad nav/style work replaced it with an unapproved `/process` route, then again when a quote-label request was over-inferred into removing the BTFP service lane from header/search/mobile. In both cases, the route still existed, but customer discovery was damaged.

**Counter-move:** treat any customer-facing business lane, service field, form field, price field, payment term, document field, route, or menu item as canonical business inventory. Renaming, hiding, replacing, merging, or deleting it requires either an explicit GL approval marker or a fail-loud verifier failure. Positive tests for the new label are not enough; add invariant tests for the old/canonical business thing that must not silently disappear.

---

## 2026-05-10 - FAQ answers must be lane-specific when policies differ

The FAQ mixed service rules under generic buckets. The most dangerous example was `Booking and pricing`: the answer gave the hourly face-painting/twisting formula in a way that could mislead event decor/install customers.

**Counter-move:** when service policies differ, structure customer-facing FAQ by service lane first, then shared policy second. Schema/AEO questions must mirror the visible lane-specific FAQ, not preserve a stale generic question set.

---

## 2026-05-10 - Email preview HTML cannot rely on cid images

Email Queue messages can be correct for real email clients while still rendering
broken in browser/PDF review files. The queued MIME contains inline image parts
with `Content-ID`, but standalone HTML opened through Playwright, Chrome, or a
PDF renderer cannot resolve `src="cid:..."` without an email client.

**Counter-move:** email preview/export tooling must parse the queued MIME image
parts or use the same local assets, rewrite preview HTML to embedded data URLs,
and then run a browser check that every `<img>` has nonzero natural dimensions.
Do not treat the queued email MIME as visual-preview proof until the standalone
artifact itself loads the logo/images.

---

## 2026-05-10 - ERPNext Lead duplicate-email setting can silently break inquiry reality

ERPNext's Lead controller blocks repeat `email_id` values unless `CRM Settings.allow_lead_duplication_based_on_emails` is enabled. That default is wrong for LT's public inquiry form: one person can ask about multiple events from the same email address.

**Counter-move:** for inquiry-led client sites, treat repeat email as an explicit CRM decision, not a database nuisance. Enable the setting through a durable patch when the business expects multiple inquiries per contact, and verify with two public submissions using the same email. Contact dedupe/linking can still preserve the relationship; Lead uniqueness must not block new customer intent.

---

## 2026-05-10 - A carousel that looks static is still broken to the customer

The BTFP cards technically had CSS fade animation across multiple images, but GL still saw them as static. That was a valid product failure because there were no controls, count, or obvious affordance that more photos existed.

**Counter-move:** for customer-visible proof photos, especially on service pages, add explicit carousel affordances: next/previous controls, visible count/status, and a reduced-motion path. Guard the behavior in Playwright by clicking next and checking the status changes, not just by counting image tags in HTML.

---

## 2026-05-10 - Multi-file upload claims need a repeatable five-file proof

The form said "Up to 5 images," but GL could not upload five photos in the real flow while a duplicate email error masked the result. A one-file or no-file smoke test would not have caught the advertised contract.

**Counter-move:** when a public form advertises a file count, create a verifier that posts exactly that many files through the same endpoint and asserts the backend attached that many records. Pair upload proof with the real customer identity constraints, such as repeat-email submissions, because the first failing validation can hide upload bugs.

---

## 2026-05-10 - Email Queue subjects with emoji must be decoded from MIME

The public inquiry acknowledgment now uses a balloon-emoji subject. A raw
`Email Queue.message LIKE "%Subject: ...%"` check is brittle because queued
messages can MIME-encode non-ASCII subjects.

**Counter-move:** find the Email Queue row by the business reference
(`reference_doctype` / `reference_name`) and parse the message headers with
Python's email parser. Keep the old subject checks as forbidden-copy guards,
not as the lookup path.

---

## 2026-05-10 - Sent email is not delivery proof when aliases loop back

ERPNext and Gmail can report an email as sent while a Cloudflare-routed
`@locallytwisted.com` alias loops back into the same Gmail sender and never
appears where the operator expects it.

**Counter-move:** treat `Email Queue.status = Sent` as SMTP acceptance only.
For current LT Gmail sending, internal business copies use
`locallytwisted@gmail.com`, while public reply identities stay role-based
(`hi@`, `legal@`, `billing@`). Keep the Email Queue insertion guard so live
console probes cannot bypass the copy helper.

---

## 2026-05-10 - Header CTA copy is a route contract, not copy polish

Changing `Twisting & Face Painting` to `Free Event Quote` and the header CTA
from `Free Event Quote` to `Contact Us` touched desktop nav, utility links,
search quick links, mobile drawer labels, cache, rendered HTML, and nav
verifiers.

**Counter-move:** treat public chrome label changes as one contract across
`navbar.html`, `nav_ia.py`, live cache, and Playwright header/drawer coverage.
Run a red precheck or add a failing verifier first when the old label is meant
to disappear.


## 2026-05-10 - Empty upload slots are not failed uploads

A browser can submit an empty file input part even when the customer never chose
a file. Treating that empty slot as a real upload made the BTFP success modal
claim inspiration photos had trouble attaching, which was false and alarming.

**Counter-move:** filter upload parts with no filename and no bytes before
validation. Only a real selected file can create a customer-visible photo
warning. Keep the submit modal short; fail-loud evidence belongs on the backend
record and verifier output, not as a lecture in the customer's success state.
## 2026-05-10 - Form success must be a backend-proven state, not a browser state

The shared inquiry form looked like a simple UX polish task, but the old
experience made success feel route/browser-driven: a forced redirect and modal
state can make a customer believe the inquiry landed even when the backend path
is broken. The cookie banner also created a practical UX failure by being able
to cover form controls.

**Counter-move:** treat form success UI as part of the backend contract. Show
progress while sending, but only show final success after the submit handler
returns `message.ok`. Do not let `#received`, cookies, localStorage, or a stale
route state open a fake success modal. On form-heavy pages, place consent or
preference notices inline so they cannot block fields or buttons.

---

## 2026-05-08 - Fake data lowers disclosure urgency, not state-integrity standards

The security review correctly found public-order and public-file exposure, but
GL clarified that all current LT data is fake and the business context is not
high sensitivity. Treating those fake-data disclosure findings as urgent launch
blockers overstated the practical risk.

**Counter-move:** separate disclosure severity from automation correctness.
Fake public records can become cleanup or cutover-hardening work. False
business state still needs a fix: checkout should not mark a Lead
`Converted` / `Approved` until the paid-order cascade has verified payment.

---

## 2026-05-08 - Internal preview routes need real gates, not hidden navigation

`/event-playground` was not linked in public navigation, but the route still
accepted a guest request and embedded a visitor-local `127.0.0.1:<port>` iframe
when the URL was known. "Hidden" did not mean access-controlled.

**Counter-move:** internal Frappe preview routes should require an explicit
role gate or be removed from the route set. Keep the guest gate verifier even
if deeper authenticated preview tests are skipped without local credentials.

---

## 2026-05-08 - Frappe templates can emit raw route data

`/shop?q=` proved that the current route template path did not protect a
query-string value by default. The search summary rendered the raw payload and
a browser-executed marker confirmed the XSS path.

**Counter-move:** escape at the exact Jinja sink for every customer-controlled
value, even when the value looks harmless or is only being shown inside text.
For JavaScript/DOM work, create nodes or set attributes through safe APIs
instead of interpolating HTML strings from route or database values.

---

## 2026-05-08 - ERPNext document names are not receipt secrets

The thank-you page used `?order=<Sales Order>` as the only proof for showing
order details. Sales Order names are sequential enough to guess, and the page
showed line items and totals without a customer/session proof.

**Counter-move:** payment-return pages need a receipt token, paid Stripe
Session proof, or equivalent nonce tied to the actual customer flow. If the
token is missing or invalid, show a generic payment-check page and leave
operator evidence, not order details.

---

## 2026-05-08 - Customer inspiration uploads are private by default

The contact form accepted inspiration photos and attached them to Leads as
public `File` records. Even when the customer intends to share a photo with LT,
the image can include homes, venues, kids, event details, or private planning
context.

**Counter-move:** set public inquiry uploads to `is_private = 1` unless GL
explicitly approves a public gallery/publication path. Existing public Lead
files need a migration/review; fixing the upload default only protects new
submissions.

---

## 2026-05-08 - Mobile chrome has a control budget

The mobile header failed because it tried to carry logo, cart, search, and menu
inside a 320px row. The search control was reasonable on desktop, but on mobile
it collided with the cart and logo. Shrinking the logo would have protected the
extra control by weakening the brand signal.

**Counter-move:** mobile chrome needs a hard control budget. Keep the primary
brand mark plus the actions that must be available instantly, and move
secondary actions into the drawer or another intentional surface. Guard the
budget with a 320px browser check, not a desktop mental model.

---

## 2026-05-08 - Component sizing contracts must cover proof sections, not only heroes

The project already had compact hero, container, and stateful layout contracts,
but the Google review block still became huge on mobile. It did not fail from
document overflow; it failed from inherited global `section` padding plus
oversized proof-card spacing and height.

**Counter-move:** when GL flags "cards and padding are huge," add a component
sizing contract for the exact proof section. For moving review/proof cards,
guard block height, badge height, track padding, card width/height, and card
padding across small mobile widths. Broad layout-fit tests are necessary but
not enough for perceived mobile density.

---

## 2026-05-08 - Delight is optional; brand clarity is not

The red balloon cursor was technically bounded and verified, but GL quickly
asked to remove it. The useful brand move was not the cursor; it was using the
red balloon dog as a small favicon where it supports recognition without
changing basic site interaction.

**Counter-move:** retire decorative interaction experiments promptly when they
do not serve the launch surface. Keep the reusable behavior that reduces
friction, such as whole-card product navigation, and move brand marks into
stable UI assets like the favicon or logo.

---

## 2026-05-08 - Wide proof bands need equal or higher containment specificity

The homepage featured-work CSS tried to make the three photo cards wide, but
the shared containment layer still capped `.lt-featured__inner` at the normal
1160px page max. A later simple `.lt-featured__inner` override did not win
because the grouped `:is(...)` containment selector had higher specificity.

**Counter-move:** when a Frappe public section is intentionally a visual proof
band rather than a reading/workflow surface, put the width decision in the
containment layer with matching specificity, for example
`.lt-featured .lt-featured__inner`. Then verify rendered widths at desktop
sizes, not just the stylesheet text.

---

## 2026-05-08 - Microinteraction demos are not production sources

The balloon cursor started from a standalone HTML demo. It was useful as a
behavior reference, but keeping it in the repo after production extraction would
have created a second source of truth and invited future agents to edit the
demo instead of the Frappe app assets.

**Counter-move:** translate demos into focused app CSS/JS, load them through
Frappe hooks with cache-busted URLs, verify the served behavior, then delete the
transient demo unless it has been explicitly approved as `_resources/` reference
material. Decorative UI still needs real layout gates: this slice's first broad
run caught cursor/click-ring overflow, and the fix was to clamp decorative
elements before closeout.

---

## 2026-05-08 - Whole-card clicks must not steal product actions

Making product cards easier to click is good storefront UX, but cards already
contain buttons, links, selectors, and quote/cart actions. A full-card anchor or
aggressive click handler can quietly break the purchase path while appearing to
solve the browsing problem.

**Counter-move:** use delegated card navigation that ignores real interactive
descendants, modified clicks, and text selection. Restrict inferred targets to
known product routes, add only a pointer affordance class, and verify both
sides: card-body clicks navigate, while `Add to cart`, `Choose options`, and
`Request quote` keep their original behavior.

---

## 2026-05-08 - Service calculators cannot flatten independent workers

The first BTFP price-check calculator used one hours input and multiplied it by
one artist count. That looked workable for "both services for the same time,"
but it could not represent the real booking shape: multiple artists, different
services, different durations, and half-hours applying only after each
individual artist's first hour.

**Counter-move:** if pricing is per worker, rental, room, vehicle, or other
independent unit, model the calculator as one row per unit. Each row owns its
own type and duration; totals are the sum of row prices. Write the verifier
against a mixed-duration case, not only the symmetric easy case.

---

## 2026-05-08 - A product-family repair is not a catalog pricing certificate

After the bouquet-size prices were repaired, a fresh audit question exposed the
next risk: the system had proof for the repaired bouquet family, not for every
product. Live ERPNext still had 36 non-bouquet variant templates with one price
point each, and quick Odoo resolver probes proved several longer arch variants
were still underpriced.

**Counter-move:** phrase pricing closeout by family and verifier. "Bouquet
size pricing is repaired and guarded" is true after `npm run
test:product-prices`; "all product pricing is correct" is not true until the
remaining product families have resolver dry-runs, reviewed repairs, and
price-contract coverage.

---

## 2026-05-08 - Odoo page base price is not variant price

The Unicorn Bouquet repair proved the catalog importer had flattened dynamic
Odoo variant prices into the page base price. The page JSON-LD/base price showed
$35, but Odoo's `/website_sale/get_combination_info` returned the real bouquet
size prices: Small $35, Medium $70, Large $85. Full combos with the optional
foil-number add-on returned a different number again, so optional add-ons must
not be confused with the ERPNext-required variant price.

**Counter-move:** any Odoo-to-ERPNext product import that touches variants must
resolve prices through Odoo's combination endpoint, not the product page base
price. If optional axes are intentionally dropped from ERPNext variants, query
Odoo with only the required attribute IDs for the ERPNext Item Price. Guard
launch-critical products with `npm run test:product-prices` or an equivalent
price contract.

---

## 2026-05-08 - Monolith files make product fixes worse

Large catch-all files turn simple LT fixes into risky broad edits. Product page
containers, portfolio motion, Frappe overrides, public CSS, and verification
logic all need readable boundaries so agents can work on one concern without
dragging unrelated behavior into the change.

**Counter-move:** before adding to a broad hand-authored file, name the file's
current job. If the new work is a separate concern, split it into a module,
partial, helper, recipe, workstream doc, or focused verifier. Research/reference
artifacts may be long-form. Generated/vendor/lock/cache/export files are not a
model for production structure.

---

## 2026-05-08 - Moving proof surfaces must not leak hidden keyboard focus

The axe pass was clean, but the manual keyboard/zoom probe found two real
focus failures: homepage review crawl cards were non-interactive articles with
`tabindex="0"` and could receive focus while translated offscreen, and
portfolio photo figures were focusable while still opacity-hidden by the
entry animation. Both looked fine visually until Tab exposed them.

**Counter-move:** moving/collage/proof surfaces must keep hidden or offscreen
items out of the tab order. Non-interactive moving cards should not have
`tabindex`. JS-driven photo buttons should start at `tabindex="-1"` with
`aria-hidden="true"` and become keyboard reachable only when actually visible.
Run `npm run test:a11y-manual` after changing crawls, carousels, portfolio
reels, product selectors, or other motion-heavy public surfaces.

---

## 2026-05-08 - Public accessibility is a launch gate, not a visual polish pass

The full-site axe scan caught issues that looked small in isolation but are
real launch blockers together: nested `<main>` landmarks inside Frappe's own
page-level main, low-contrast labels, product-card heading jumps, a nested
category-rail landmark, breadcrumb region/contrast drift, a hidden unnamed
Explore link, and a color-only checkout link.

**Counter-move:** route templates must not add page-level `<main>` landmarks
inside Frappe's existing `main.container`. Public route closeout now needs
`npm run test:a11y` alongside layout/container/interactive checks. Treat
contrast, landmarks, link names, heading order, breadcrumb regions, and
keyboard/screen-reader semantics as launch blockers, not after-the-fact polish.
Follow it with `npm run test:a11y-manual` when motion, focus order, image
loading, or zoom-pressure behavior is in scope.

## 2026-05-08 - Delight motion still needs a settle point

The portfolio reel felt better after the no-caption/no-frame correction, but
the pointer-follow sway and front-photo tilt made the whole page keep moving
while the visitor was trying to look at proof photos. A delightful click pop can
still become an accessibility problem if it never clearly settles.

**Counter-move:** separate entrance/popup motion from ongoing motion. For LT
`/portfolio`, keep scroll entry and click-to-front pop, but do not track pointer
movement and do not keep tilting the front photo after the click animation.
Tests should prove both sides: the click pop still changes the transform, and
later pointer movement leaves the settled front photo unchanged.

---

## 2026-05-07 - Fake data is useful only when fake success is impossible

GL clarified that all current LT data is fake/test data for automation testing. That means agents should stop hesitating around fake-data contracts and use them as the safe proving ground for the business system. It also means fake records cannot be used as proof that the business is operational.

**Counter-move:** when testing LT, distinguish synthetic readiness from live cutover readiness. Fake/test data should prove every field, cascade, document, payment handoff, reminder surface, and checkup path. If something can/should happen and does not, the affected Lead, Sales Order, Payment Request, Sales Invoice, report, or verifier must expose the failure. Error Log-only evidence is not enough for business-critical customer intent, payment context, or paperwork readiness.

---

## 2026-05-08 - Portfolio does not need a route-local contact/index footer

The portfolio page kept a route-specific footer block after the photo field:
Inquire, Studio, Index, phone number, install count, and a Locally Twisted mark.
That was leftover page furniture from the external portfolio reference, not
necessary proof. It made the portfolio feel like a copied section instead of a
focused photo field inside the real LT site chrome.

**Counter-move:** let the global Frappe/LT header and footer own navigation and
contact paths. `/portfolio` owns only the compact branded hero, proof reel,
empty state, JSON-LD, and no-script image fallback. Do not restore `.lt-foot`,
`Portfolio contact`, Inquire/Studio/Index labels, phone/index rows, or
route-local contact/footer CSS. The route verifier and container contract must
fail if that block returns.

---

## 2026-05-08 - Fail loudly is one law, not one feature

LT had separate fail-loud ideas for forms, automation indexes, payment parity,
invoice/reminder drafts, and container contracts. Treating them as separate
rules made the project depend on GL noticing the same pattern again under a
different name.

**Counter-move:** use one operating mantra everywhere: if it can fail, it must
fail loudly. For LT, that means no false success states, no swallowed backend
errors, no unverified customer messages, no document output that hides missing
approval/payment paths, no silent automation skips, no hidden container
overflow, and no agent completion claims without current evidence. Encode the
rule as a verifier, report row, Error Log, blocker field, or route contract
wherever possible.

---

## 2026-05-08 - Photo scale is not reel density

The portfolio correction used `density = 1.65` to make desktop photos 1.5x
larger. That was the wrong lever because the same value also feeds vertical
spacing: `VERTICAL_SPACING * (2 - density)`. The photos got bigger, but the
collage rhythm tightened and felt worse.

**Counter-move:** keep visual controls separate. In `/portfolio`,
`density = 1.10` owns the approved reel rhythm and `photoScale = 1.5` owns the
larger image size. Tests must guard both: desktop photos stay enlarged, and
early reel offsets keep the looser spacing instead of collapsing into higher
density.

---

## 2026-05-08 - Portfolio proof photos are not caption cards

The portfolio reel regressed because Codex treated captions and frames as a
safer way to explain the photos. GL rejected that outright. The white/cream
stripes were not mysterious browser paint; they came from forcing design-slot
aspect ratios and `object-fit: contain` inside a light wrapper instead of sizing
each real optimized photo by its real dimensions.

**Counter-move:** for LT `/portfolio`, the photo is the surface. Do not add
captions, visible frame wrappers, card backgrounds, or forced aspect boxes.
Desktop proof photos now use `photoScale 1.5` while preserving `density 1.10`;
mobile photos are full viewport width and slide in. The route verifier must fail
if `.lt-frame`, `.lt-cap`, `figcaption`, old desktop widths, mobile side
gutters, image/photo rect mismatches, or compressed higher-density spacing
return.

---

## 2026-05-08 - Portfolio mobile cannot lose the collage motion

**Status:** Superseded later on 2026-05-08 for caption treatment. Keep the
mobile-motion lesson, but the current portfolio contract has no photo captions
at all.

The portfolio page technically had a proof reel, but mobile CSS forced the
photos into a static stack and captions sat below the frames. That stripped the
movement GL approved from the design handoff and made the page feel like a
plain gallery instead of a game-like, sliding collage of installed work.

**Counter-move:** protect the portfolio as a motion surface, not just a layout.
The current LT `/portfolio` contract is large whole-photo collage movement,
desktop drift/click-to-front behavior, mobile slide-in reveal, and no photo
captions at all. Tests must fail any returned caption/frame treatment and must
fail a static mobile stack.

---

## 2026-05-07 - Container contracts must be executable, not advisory

LT already had prose saying Frappe's stock `main.container` is neutralized and
public sections must own their own containment. That did not stop drift:
homepage twisting content exceeded the page max, contact/location reused raw
Bootstrap containers, document pages lost narrow widths to selector specificity,
the portfolio footer declared an inner wrapper that did not exist, and the BTFP
route contract was stale after the page changed.

**Counter-move:** treat public containers as a route-level contract in code.
Every visible direct child of `.page_content` on a launch route must be listed
in `CONTAINER_CONTRACT_ROUTES` with an explicit mode. Keep
`lt-page-containment.css` late in `web_include_css`, update the route contract
when route markup changes, and run `npm run test:container-contract` before
claiming public layout work is done. If a route adds a crawl/marquee, the
viewport must clip instead of exposing a native scrollbar.

---

## 2026-05-07 - Product options are controls, not containers

After the recommendation panel was removed, product detail pages still looked
cheap because the variant form, size chips, select/dropdown, and price/add-cart
group were styled as little bordered boxes. The pickup/delivery notice was the
only framed product-page element GL wanted to keep.

**Counter-move:** do not style product options as cards, pills, or boxed
selection panels. Size, latex color, add-on numbers, and other variant controls
should be clear text-level controls with selected-state emphasis, not nested
containers. Keep the pickup/delivery panel as the framed exception. Guard this
with `scripts/verify/smoke_shop.py` and
`capabilities/recipes/frappe-product-clear-control-contract.md`.

---

## 2026-05-07 - Product pages cannot become generic ecommerce pages

The product detail template kept Webshop's lower Additional Info, Reviews, and
Recommended Items area even when it had no useful customer content. Once LT CSS
made that wrapper visible, customers saw a random white box under the product
area, and the page felt like ecommerce itself was the product.

**Counter-move:** ready-to-order shopping supports the company; it does not lead
the brand. Product pages should show the photo, name, price, useful options,
fulfillment notes, product copy, and a clear cart/contact path. Do not restore
recommendation panels, generic upsells, empty reviews tabs, or visible boxes
that exist only because the Webshop template offered a section. Guard this with
`scripts/verify/smoke_shop.py` and the
`capabilities/recipes/frappe-product-page-company-first.md` contract.

---

## 2026-05-07 - Render density is not quote math

The Event Playground preview looked plausible with fuller 11-inch classic arch
and column density, but the manufacturer/physics audit showed those render
counts are too risky to treat as production quantities. A future automation
could accidentally turn a pretty planning count into an ERPNext quote, material
plan, or customer promise.

**Counter-move:** keep visual planning facts and production estimate facts in
separate payload fields. Render counts can support the canvas, but production
estimates must be candidate-only, internal, `quote_ready: false`, and clearly
blocked on LT approval for formulas, overage, fill/support method, venue review,
safety, and pricing. Any Frappe adapter must fail loudly if a customer-facing
or quote path tries to use unapproved render density.

---

## 2026-05-07 - Design references can be partially approved

The portfolio route copied too much from the Claude/Frappe design reference.
GL wanted the collage and movement, not the whole page shell. Preserving the
reference's internal nav, custom cursor, route-local font imports, and off-brand
hero made the page feel disconnected from the current Locally Twisted site even
though the moving photo reel was useful.

**Counter-move:** extract the approved part of a visual reference before coding.
Write tests for both sides: what must survive and what must be excluded. For
LT `/portfolio`, the protected behavior is the large whole-photo drift/collage
reel; the excluded behavior is copied internal page chrome, custom cursor,
portfolio-specific Google font imports, and prototype hero copy.

---

## 2026-05-07 - Homepage proof order is a launch contract

The homepage briefly had multiple plausible proof paths competing directly
under the hero: trust/authority bar, installed-work proof, Google reviews, and
cookie notice. Technically each could be defended, but launch hierarchy matters:
GL clarified that Google reviews belong immediately below the hero right now.

**Counter-move:** make first post-hero content an explicit contract, not a local
layout preference. For LT launch, the order is hero, Google reviews, inline
cookie notice, then the installed-work proof band currently labeled `One of a
Kind Designs`. Do not restore the homepage trust bar or put installed-work
proof above reviews without a fresh GL decision and matching tests.

---

## 2026-05-07 - Branch stacks break GL's operating model

Multiple Codex branches and stacked draft PRs accumulated even though GL does
not use branches and relies on GitHub/main history as the rollback archive. The
result was not safer collaboration; it made it unclear what was real, what had
landed, and what still needed a decision.

**Counter-move:** LT work is main-only. Before editing, verify `HEAD` is on
`main`; commit and push directly to `origin/main`; do not create feature,
codex, topic, experiment, or PR-stack branches. Use workstream docs and
uncommitted work review for coordination, not branch names. Machine-wide hooks
block non-main commits and pushes, but agents must still obey the rule because
Git cannot fully prevent branch creation before checkout completes.

---

## 2026-05-07 - Heroes became layout debt because every route guessed

LT had no enforceable hero contract. Home, Event Balloons, Portfolio, BTFP,
Contact, Shop, and category pages each carried different hero min-heights,
section padding, title clamps, and inner spacing. Some routes made the hero
larger than the first laptop viewport, so the actual products, proof, forms, and
booking content were pushed out of view.

**Counter-move:** treat heroes as standardized orientation surfaces. Use the
compact hero contract everywhere: 220px mobile, 250px tablet, 280px desktop;
padding caps of 24/28/32px; title caps of 32/40/44px. Add or update Playwright
coverage before claiming a route is visually ready. If a hero needs more room,
the page content is too dense for a hero and the extra material belongs below
it.

---

## 2026-05-07 - Verification caveats expire after broader gates pass

The homepage handoff and capability receipt still carried a temporary caveat
that broad layout verification was blocked by unrelated portfolio work even
after a later full `npm run test:website-verify` pass was green. That would send
the next Codex agent chasing a resolved blocker.

**Counter-move:** when a focused feature handoff records "full gate blocked,"
revisit that caveat after the broader gate is rerun. If the full gate later
passes, update the feature handoff, launch workstream, queue, decision receipt,
and capability receipt in the same documentation parity slice. Verification
notes are operational state for agents, not historical prose.

---

## 2026-05-07 - Homepage proof motion needs one contract

The homepage had two proof banners that behaved differently by platform: review
cards could become a scrollbar, trusted-business names could stack instead of
crawling, and reduced-motion branches did not preserve GL's requested visual
behavior. At the same time, the hero still carried old rotating-title thinking
and the cookie notice could cover mobile CTAs.

**Counter-move:** treat homepage proof crawls as one shared banner contract, not
two decorative widgets. Both review cards and trusted-business names must span
the stage and move left-to-right. The review-card crawl owns the canonical
`540s` loop; the trusted-business crawl must be measured and assigned a
proportional duration so its visible pixel speed matches the reviews. For these
two proof bands only, the reduced-motion branch is a slow-crawl exception:
it must remain horizontal, moving, and scrollbar-free unless GL explicitly
changes the business-proof contract. The homepage cookie notice should sit
inline after the review band so accounting, corporate, school, and civic
visitors can see the primary CTAs without dismissing an overlay first.

---

## 2026-05-07 - Frappe controller CSS constants may outlive cache clears

Changing `PAGE_CSS` inside a Python route controller did not fully update the
homepage after `python scripts/dev/clear_website_cache.py`. The website cache was
clear, but the running backend process still held the imported controller module
and its string constants.

**Counter-move:** after changing route-controller constants such as `PAGE_CSS`,
clear the website cache and restart the affected Frappe backend container before
declaring the browser view current. Use this especially when a CSS fix appears
correct in source but not in the rendered page.

---

## 2026-05-07 - Navigation can erase a business line

The public menu had replaced the approved `Twisting & Face Painting` service
lane with an unapproved generic `Process` page. Technically the new page loaded,
but business-wise it cut a major Locally Twisted service out of the primary
customer path and made the nav less truthful.

**Counter-move:** treat nav labels and route presence as business facts, not
decoration. When a top-level route changes, verify that it represents an
approved line of business, add negative tests for removed labels/routes, delete
unapproved route files, and update the style guide, queue, handoff, workstream,
decision log, and capability docs in the same slice. For LT, `nav_ia.py` now
fails if Process returns to public chrome, and `/process` should stay 404 unless
GL explicitly reopens it.

---

## 2026-05-06 - Exact design exports are source, not mood boards

The portfolio page failed because Codex treated a Frappe-ready design export as a loose reference. The shipped correction used tests and numeric constraints to produce "bigger photos, three columns, compact hero," but it stripped the actual exported design language: editorial serif hero, portfolio row, muted paper/ink system, custom cursor, slow drift/fade, approved scales, and center-photo rhythm.

**Counter-move:** when a handoff says the Frappe export is approved and deviations are bugs, diff production against that export first and restore its locked values before inventing any local design solution. Translate only fake business details and production hazards. Add verifiers for the exported constants and visual behavior so tests protect fidelity, not the agent's reinterpretation.

---

## 2026-05-06 - Portfolio proof pages fail when the center column starts late

**Status:** Superseded for `/portfolio` by the approved-export lesson above. This remains useful for generic proof galleries, but it was the wrong priority for the approved LT export.

The first portfolio correction made photos bigger than cards but still let the layout behave like two edge columns with occasional center statements. That read cheap because the opening viewport did not immediately establish the intended left/right/center rhythm, and the images were still too small for a page whose job is to sell installed visual work.

**Counter-move:** for proof-first pages, verify the first viewport geometry directly. The `/portfolio` verifier now checks a compact hero against the live menu height, a first photo around the corrected large scale, an opening center photo above the fold, and all three left/right/center sides present in the scroll rhythm. Do not claim a portfolio layout is fixed just because it passes mobile overflow; it also has to look like a deliberate proof gallery.

---

## 2026-05-06 - Report rows can become a hidden send surface

The customer reminder report looked like a harmless display layer because it only turned dry-run queue items into table rows. In a business system, a table row can still become the surface a future agent wires to a send button or schedule.

**Counter-move:** carry no-live flags into the report payload and every row, not just the source queue. For LT, `customer_reminder_review_report.py` marks the whole report `send_allowed: false`, `customer_delivery_enabled: false`, and `mutation_allowed: false`, and `customer_reminder_review_report_contract.py` rejects malformed send-enabled source rows before a Desk UI exists.

---

## 2026-05-06 - No-live reminder setup still needs send blockers

Customer reminders can feel safe when the code only builds an internal queue. They are still one step away from customer-facing collections, so every queue item needs explicit blockers for approval, recipient, invoice status, cadence, copy, and payment path.

**Counter-move:** keep the reminder surface `internal_review_only` and `draft_only_not_sent`, and test malformed send-enabled packets with fake data. For LT, `customer_reminder_dry_run_contract.py` proves overdue/current/missing-payment-path/malformed scenarios without creating database records, while the live dry-run verifier proves no Email Queue, Communication, Error Log, invoice, payment, or journal counts change.

---

## 2026-05-06 - Synthetic audits must not inherit live cutover blockers

The paperwork/backend lane started mixing two very different questions: "Can fake data safely flush out broken cascading information?" and "Are live Stripe keys and production site settings ready?" The live checks were not needed for the current work and made a fake-data audit look blocked by credentials GL explicitly barred.

**Counter-move:** keep synthetic operating readiness and live cutover readiness separate in code, verifier output, and docs. For LT, `paperwork_status.py` now runs in `synthetic_without_live_credentials` mode, `paperwork_review_digest.py` reports `cutover_deferred_not_blocking`, and `synthetic_business_pipeline.py` fails if live payment readiness is labeled as a current blocker. Run live Stripe readiness only when cutover work begins.

---

## 2026-05-06 - Aggregate digests need recursion and mutation boundaries

The paperwork review digest needed to summarize the business automation index, and the automation index also needed to classify the digest. Calling the full index from the digest would create a self-check loop once the digest was indexed.

**Counter-move:** aggregate review surfaces should call index/report helpers in a scoped mode that excludes the aggregate itself, and they need their own mutation guard. For LT, `business_automation_index.run(include_digest=False, include_synthetic=False)` lets `paperwork_review_digest.run` summarize partial connections without recursively checking the digest or synthetic pipeline surface. The digest also guards Email Queue, Communication, Payment Request, Payment Entry, Journal Entry, Sales Invoice, and Error Log counts.

---

## 2026-05-06 - Rendering a draft is still an automation boundary

The unpaid invoice draft packet renderer feels safer than reminder sending because it only produces review output. It still touches a dangerous business boundary: customer communication and invoice follow-up. If a renderer quietly creates an Email Queue row, Communication, Payment Request, Payment Entry, Journal Entry, or invoice mutation, it has become delivery or accounting automation without approval.

**Counter-move:** draft renderers need the same negative proof as review queues. The unpaid invoice packet verifier now confirms `read_only`, `send_allowed: false`, `mutation_allowed: false`, draft-only packet/section status, human approval gates, and unchanged guarded counts. Use that pattern before building Desk queues, scheduled digests, statement generators, or reminder send paths.

---

## 2026-05-06 - A draft-only reminder still needs a mutation guard

The unpaid invoice review surface looked safe because it only reads invoices and returns candidate data. That is not enough proof in a business system. If a future helper accidentally queues an email, creates a Communication, or changes a Payment Request while building the review list, the surface becomes collections automation without approval.

**Counter-move:** finance review helpers should prove the negative. The unpaid invoice verifier now checks `read_only`, `send_allowed: false`, `mutation_allowed: false`, draft-only document status, and guarded counts for Email Queue, Communication, Sales Invoice, Payment Request, Payment Entry, and Journal Entry. Use that pattern before adding any reminder, statement, or collections-related review queue.

---

## 2026-05-06 - Keep the useful prototype behavior, not the whole prototype

The portfolio correction after the exact-handoff pass showed a second failure mode: once a reference is rendered correctly, it can still be wrong for production if Codex carries over the whole prototype instead of the part GL actually wants. GL wanted the overlapping collage and stronger center balance. She did not want the tall hero, copied font imports, custom cursor, fake shell, or small production photos.

**Counter-move:** after matching a visual reference, immediately identify what
belongs to production and encode that boundary in source and verifiers. For LT
`/portfolio`, the current rule is: branded compact portfolio hero, native LT
shell/global typography, large whole installed-work images, frequent
center-column photos, no portfolio-specific Google font imports, no custom
cursor artifacts, no copied internal nav, and warm page-matched image frames.
The verifier should fail if the page regresses into either a small safe row or a
wholesale prototype copy.

---

## 2026-05-06 - Automation needs a machine-readable map, not only a handoff paragraph

The paperwork/backend lane had many working pieces: contact intake, Lead cascade, checkout, payment success, receipts, invoice branding, outbound templates, and finance visibility. The risk was that future agents could treat "exists" as "connected" or treat a native ERPNext DocType as operational readiness. That is exactly how silent failures slip into business systems.

**Counter-move:** create a verifier-backed automation index for cross-system business work. The index should separate connected surfaces, partial surfaces, required missing surfaces, useful future surfaces, fake-data test paths, and loud-failure gaps. Keep it scheduled in Frappe when the site is expected to operate as a business system, and update the index whenever a new automation surface is added.

---

## 2026-05-06 - Hosted checkout amount parity is not implied by ERPNext totals

The money-path audit found that Stripe Checkout line items could be generated from Sales Order item rates while ERPNext `grand_total` includes taxes or charges. That means the ERPNext order can be right while hosted checkout charges the wrong amount. A local payment-readiness check is not enough proof for amount parity.

**Counter-move:** contract-test the Stripe payload builder directly. Convert money to cents, compare line-item totals to the ERPNext `grand_total`, add an explicit tax/charges adjustment when needed, and raise before redirect when the item lines exceed the ERPNext total. Any future checkout/payment refactor must rerun `python scripts/verify/stripe_amount_parity_contract.py`.

---

## 2026-05-06 - Symmetry does not rescue the wrong category-control pattern

The first shop repair responded to GL's symmetry rule by turning category controls into equal tiles. That fixed ragged rows, but it still left customers facing a button wall. GL's rejection was not just about spacing; it was about the product showcase feeling cheap and unintuitive.

**Counter-move:** when GL rejects a category or product-control surface, question the interaction pattern before polishing spacing. For LT, the current contract is a desktop category rail plus mobile native select, with product cards and large photos given the main space. Verifiers should prove the old chip/button walls are absent, not merely symmetrical.

---

## 2026-05-06 - Privacy-extension blocks can be filename-triggered

The `/shop` console showed `ERR_BLOCKED_BY_CLIENT` for `lt-cookie-consent.js`. The local server could serve the file, but the customer's browser environment treated the filename as a blocker target. The bug was not solved by explaining the extension; the visible site contract needed a less blocklist-prone asset name.

**Counter-move:** when a required public-site helper is blocked by a browser extension, inspect the URL and filename as part of the root cause. Keep consent behavior honest, but avoid shipping asset names that look like common ad/tracker/cookie blocker patterns. For LT, the kept asset is `lt-site-preferences.js`; the deleted name is `lt-cookie-consent.js`.

---

## 2026-05-06 - The exact folder matters when a designer handoff exists

The second portfolio failure happened because the implementation was judged against a copied/derived reference path instead of the exact folder GL named: `research/a unique portfolio page for a high end corporate balloon events_/design_handoff_locally_twisted_portfolio/`. That lost important details: the huge editorial hero, oklch palette, Cormorant/Inter Tight pairing, visible captions below photos, and the approved aspect sequence.

**Counter-move:** when GL provides a design handoff path, render that exact folder first, compare production to it, and translate only the intentional production differences. For this LT page, keep the real Frappe header/footer and real LT photos, but otherwise treat the handoff's Frappe files as the visual baseline until GL closes the critique loop.

---

## 2026-05-06 - Portfolio edge bleed is the design, not an overflow bug

The strict portfolio rework exposed the real failure in the first translation: Codex tried to make the designer's collage safer by moving photos into fully visible rows. That protected the layout in a generic web sense, but it destroyed the portfolio concept GL wanted. The portfolio is supposed to feel like an intentional scrolling collage of whole installed-work photos, not a card grid with larger images.

**Counter-move:** when a visual reference intentionally uses edge anchoring, overlap, bleed, or asymmetric motion, preserve that behavior first and verify it in the browser before applying generic container instincts. In LT, the Frappe shell owns the header/footer and route lifecycle, but the portfolio reel owns its full-bleed photo field. Tests must fail a static row, fail text covering gallery photos, and prove Chrome/Brave show the same placement pattern.

---

## 2026-05-06 - Product showcase rows need symmetry, not just fit

The first shop showroom pass made `/shop`, `/shop-items`, and `/shop-items/<group>` larger and more responsive, but GL correctly rejected the result as cheap because the category controls were ragged text-width chips and some category grids left a lone product card hanging on the last desktop row. The page technically fit in the viewport, but it did not meet the visual bar for showing off products.

**Counter-move:** for LT shop/category/product showcase pages, test symmetry as part of the design contract. Category controls should use equal-width and equal-height grid tracks, not variable-width chips. Add a neutral "all" tile when it creates an even category matrix. Product grids should avoid single-card orphan rows in both category pages and filtered `/shop` states; when a 3-up layout leaves one card and the count can be split evenly, use paired 2-up rows. Verify with browser geometry checks, not only generic overflow tests.

---

## 2026-05-06 - Designer reference code is a contract, not a suggestion pile

Claude produced a useful portfolio design reference, but the first translation failed the ownership handoff: Codex blended the reference with old local portfolio assumptions, kept stale claims in docs, and made the result harder for the designer to critique. The important distinction is that external design code can own the visual contract, while Codex owns the Frappe translation.

**Counter-move:** when GL brings code from Claude, a designer, or another agent, first write down what must survive visually and what should be ignored. For the LT portfolio, the preserved contract is large whole photos, left/right/center drifting placement, no cropped cards, no text covering the product, visible reference captions below photos, optimized real images, and mobile full-width natural-ratio stacking. Do not add filters, modal behavior, Frappe boxing, or other "helpful" local patterns unless GL explicitly accepts them. Keep the reference folder while critique is active, but label production source as the Frappe route, CSS/JS, optimized assets, and verifier.

---

## 2026-05-06 - Translate design references into kept source, then delete the raw reference

**Current status:** superseded while the portfolio designer critique loop is active. Keep the raw reference folder available for critique until GL explicitly closes it; delete only after that approval.

The portfolio reel used a generated/reference folder as a temporary design source. Keeping that folder after translation would train the next agent on the wrong artifact and leave another stale path to reconcile.

**Counter-move:** when a reference artifact has been translated into Frappe/Jinja/CSS/JS, keep the route implementation, verifier, and feature handoff. Delete the raw generated/reference folder unless it is still an explicit source of truth. For proof galleries, preserve real image dimensions in code metadata and verify natural-ratio display instead of keeping mock source files.

---

## 2026-05-06 - Required fixture fields can block unrelated work

`Item Attribute` fixture rows without explicit `disabled` values can block `bench migrate` or fixture sync after unrelated app changes because ERPNext treats the field as required. That makes a visual or feature slice look broken even when the failure is stale fixture shape.

**Counter-move:** keep required ERPNext fixture fields explicit in tracked fixtures, and verify fixture JSON before committing. This is not a reason to add broad new ERPNext setup records; it is a parity fix for existing fixture ownership.

---

## 2026-05-06 - Customer document policy copy needs one lane helper

LT policy copy now appears in several places: public Terms/Refund pages, checkout notices, paid-order receipts, and inquiry auto-ack emails. When those surfaces are edited independently, the checkout/legal story can drift or accidentally imply the wrong tax/refund rule for services, deposits, delivery, or ready-to-order products.

**Counter-move:** keep customer-document policy language behind `locally_twisted.policy_documents` and anchored public policy lanes. Do not add ERPNext Terms and Conditions or Email Template sync records unless a real customer-facing invoice path requires them; LT should stay whitelabel/code-owned where practical. After changing customer-facing document copy, run `python scripts/verify/customer_documents_contract.py` and the paid-order cascade verifier. Decode/normalize Frappe `Email Queue.message` content in verifiers because queued mail may be quoted-printable encoded.

---

## 2026-05-06 - Event Playground handoff needs one payload contract

The PlayCanvas game, Frappe wrapper, contact-form prefill, and browser tests all depend on the same design facts: venue preset, placed balloon pieces, props, positions/rotations/scales, colors/materials/patterns, screenshot reference, suggestions, and contact handoff state. If those facts drift between the game and contact handoff, the route can look playable while sending weak or misleading inquiry text to LT.

**Counter-move:** keep Event Playground state and payload construction in a pure module first, then have the renderer and route verifier consume that schema. Browser checks must prove the canvas and controls are usable and that Submit Inquiry lands on `/contact` with the same design summary prefilled. Do not add a DocType, backend save API, Lead creation, or migration until persistence is deliberately approved.

---

## 2026-05-06 - Event Playground construction truth must be tested before rendering

GL caught the arch balloons pointing down. That was a real manufacturing mistake, not a styling preference: a classic quad cluster is tied/twisted at a shared center, so each balloon neck/knot points into that tie point. The renderer defaulted all balloon necks downward and still passed canvas tests because those tests only proved "nonblank and interactive."

**Counter-move:** use `C:\Users\baenb\projects\design-studio\capabilities\recipes\event-playground-construction-truth.md` before any Event Playground geometry work. Put construction slots in pure modules first, test neck/knot vectors against the shared tie center, and make PlayCanvas consume those slots. A nonblank canvas is never enough proof for balloon construction.

---

## 2026-05-06 - Frappe container work needs an explicit contract

Older notes correctly found that Frappe wraps normal web pages in `.page-content-wrapper > main.container.my-4`, and LT later neutralized that stock visual box so full-width brand bands could span the viewport. The missing piece was that "break out of Frappe" became too easy to treat as a general page-building move. GL saw the real effect: some sections felt detached from the Frappe page rhythm, while crawls/reviews broke differently across browsers and cache states.

Research against the installed local stack confirmed the current contract: Frappe/Webshop still owns the website lifecycle, route templates, header/footer hooks, product/listing/cart selectors, and asset loading. LT owns the visual containment inside that lifecycle through `lt-theme.css` and `lt-page-containment.css`. That means every public section must choose a mode before CSS work starts: contained workflow/reading surface, or deliberate full-bleed band with its own inner wrapper and browser-verified clipping.

**Counter-move:** before changing public layout, `.lt-fullbleed`, crawls, review tracks, Webshop pages, or shared CSS, read `capabilities/recipes/frappe-public-container-contract.md`. Classify the section, preserve Frappe/Webshop hooks and selectors, use LT inner containment instead of relying on the neutralized parent container, and verify no document overflow, visible unintended scrollbar, or browser-specific fallback.

---

## 2026-05-06 - Do not turn cartable products into quote-only failures

The checkout rule briefly treated product groups like Arches and Garlands as `quote_required`, which meant a priced product already in the cart could disappear from checkout or be described as not purchasable. GL caught the customer logic problem: putting something in a cart means "I can buy this." The only clear system-configured checkout quote fallback is fulfillment, especially a delivery ZIP outside the standard zone.

**Counter-move:** keep product CTA rules and fulfillment quote rules separate. If a product should not be sold online, do not let it enter the cart. If a priced product is in the cart, do not mark it `quote_required` because of item group. Use delivery-zone preview/submit contracts to route out-of-area customers to `/contact` with cart and customer details prefilled.

---

## 2026-05-06 - Tax jurisdiction is not the taxable base

The checkout code already knew how to pick a Utah tax rate from ZIP/city, but that did not mean the whole order should be taxed. GL clarified the actual LT rule: only goods are taxable. Services, face painting, balloon twisting, deposits for those services, and delivery charges are not taxable. The failure was visible only when the Sales Order contract compared expected goods-only tax to ERPNext's submitted tax rows; West Jordan delivery produced `$5.96` tax instead of the expected `$4.84` because delivery was being included in the taxable base.

**Counter-move:** for ERPNext checkout work, test two contracts separately: jurisdiction/rate selection and taxable-line classification. Use a real 0 percent Item Tax Template for non-taxable service/deposit/delivery lines because ERPNext can recalculate Sales Order tax from templates, not just raw preview math. Verify both preview totals and submitted Sales Order tax rows. Keep service deposits as Lead/payment guidance until an approved service money path exists.

---

## 2026-05-06 - Fresh headless checks can miss persistent-browser motion state

The homepage review marquee was checked in Playwright and the computed CSS said it was animating. GL then showed two real browser screenshots with different failures: Chrome exposed the horizontal scrollbar from the reduced-motion fallback, while Brave showed the older stacked-card fallback. The code path existed, but the verification did not cover the states GL was actually seeing: persistent browser sessions, stale rendered CSS, and the `prefers-reduced-motion` branch.

**Counter-move:** when a visual behavior depends on animation, overflow, media queries, or browser preferences, verify more than the happy-path computed style in one fresh browser. Check the served HTML/CSS, then run Chrome and Brave with fresh profiles and inspect the user-visible state: `matchMedia('(prefers-reduced-motion: reduce)')`, animation name/duration/play state, overflow/scrollbar behavior, and element positions over time. Also force both `no-preference` and `reduce` in Playwright. A reduced-motion fallback still has to match the intended visual contract; it cannot quietly become a stacked grid, visible scrollbar, wrong direction, or different speed unless GL explicitly accepts that.

---

## 2026-05-05 - Container stability fails at breakpoint edges and open states

The site looked acceptable in some default screenshots while real containers were still at risk: nav between legacy and active desktop breakpoints, mobile drawer accordions, product selectors, contact conditionals, portfolio state, and text sitting too close to panels. A 320/375/1366 check alone was not enough for the design requirement GL was reacting to.

**Counter-move:** treat every public container as unsafe until checked across breakpoint edges and stateful UI. The LT gate now uses `scripts/verify/layout_helpers.js`, expands `npm run test:layout-fit` to 260 passive route/viewport checks, adds `npm run test:interactive-layout` for 39 open-state checks, keeps checkout preview behavior under `npm run test:checkout-experience`, and exposes `npm run test:public-verify` for broad closeout. New containers need either coverage in those specs or a deliberate reason they are out of scope.

---

## 2026-05-05 - Disk source is not proof that Frappe is serving the design

The restored mega-menu, page-containment CSS, and product-polish CSS existed in the repo, but the running site was still missing the menu behavior and product/page styling because the assets were not wired through `hooks.py` and the Frappe processes/cache had not been refreshed. That made the site look like agents were editing against each other even when useful source changes existed.

**Counter-move:** for Frappe visual work, verify the served HTML and asset URLs after editing `hooks.py`, not just the file tree. Restart backend/frontend when hooks change, clear website cache after restart, confirm the cache-busted URLs appear in page HTML, and then run browser checks.

---

## 2026-05-05 - Mega menus need separate hover-open and click-pin behavior

The desktop mega menu technically opened on hover, but Playwright click exposed a real interaction flaw: moving over the trigger opened the panel, and the click then interpreted the open state as a request to close it. That made the menu feel broken for users who click instead of hover.

**Counter-move:** treat hover as preview and click as pin. A click on a hover-open menu should keep it open and set `aria-expanded=true`; only a second click on an already pinned menu, outside click, Escape, or another menu should close it. Verify this with a real browser, not only source inspection.

---

## 2026-05-05 - Retired design references must be deleted, not politely deprioritized

The old `_resources/design-guide/` and several shop/icon comparison artifacts were still present after the visual direction changed. Even with a stronger style guide, those files could keep training future agents back toward light-blue/blush UI, old fonts, weak generic icons, and stale shop mockups.

**Counter-move:** when GL explicitly rejects a visual direction, delete the conflicting tracked references if they are no longer current source material. Then update the active reading paths, workstream, queue, decisions, lessons, and capability recipe in the same closeout. Keep true catalog/business evidence, but separate it from style authority.

---

## 2026-05-05 - Icon quality has to match the business, not just the proof-bar slot

The first professional icon pass still acted like Locally Twisted needed four generic proof marks. GL rejected that correctly: this is a balloon company, and the icon system needs Utah/local proof, event context, and multiple balloon forms.

**Counter-move:** for brand icon systems, start from the customer's actual business vocabulary. LT now has balloon pair, cluster, arch, organic garland, column, bouquet, civic parade, corporate entrance, school spirit, premium private event, delivery/install, and proof icons. Balloon pages should use balloon-form icons before abstract trust icons.

---

## 2026-05-03 - Sitewide visual passes need cache-bust plus screenshot proof

The Civic overhaul changed shared CSS, Jinja partials, Python controller constants, generated imagery, Webshop surfaces, and policy/success pages. Route 200 checks and layout tests were necessary, but they would not have caught the old header treatment, stale controller output, unreadable hero treatment, blank map embed, or mobile header overlap on their own.

**Counter-move:** for broad Frappe visual work, bump the CSS query string, clear website cache, restart the backend when controller constants changed, then verify with route checks, layout/contract checks, and real desktop/mobile screenshots. Treat screenshot inspection as part of the acceptance test, not polish.

---

## 2026-05-03 - Lead conversion has to update both ERPNext status and the LT board

Checkout already converted a Contact-linked Lead by setting native `Lead.status = Converted` and filling `Lead.customer`, but Jeff's LT board still showed the Lead as `New Inquiry` and kept the old follow-up Task open. ERPNext's native conversion fields and the client-facing business stage are separate contracts.

**Counter-move:** when a checkout, import, or manual process converts a Lead, verify native ERPNext fields, the custom pipeline stage, related Tasks, and finance records together. A conversion is not operationally complete if the owner board still tells staff to treat it as a fresh inquiry.

---

## 2026-05-03 - Live inventory should not overlap rollback-based verifiers

A backend inventory pass briefly saw temporary records created by checkout/payment/cascade verification. Those records were real while the verifier was running, but they were not stable business state because the verifier rolled them back.

**Counter-move:** run live DB inventory after mutating verifiers finish and their cleanup checks pass. If parallel verification is unavoidable, label counts as test-window counts and rerun the inventory sequentially before documenting them.

---

## 2026-05-03 - Engine comparisons need one payload truth source

The PlayCanvas/Babylon event-builder spike could have drifted into two separate demos with matching screenshots but different facts. That would be useless for a future sales/design tool because the payload, balloon counts, scale rules, and interaction behavior matter as much as the pixels.

**Counter-move:** for renderer comparisons, put scene facts and payload construction in shared code first, then make each engine renderer consume the same scene objects. Verify payload parity between engines except for the explicit engine field, and test at least one interaction that mutates the payload. Screenshots prove the canvas rendered; shared facts prove the engine comparison did not change the business contract.

---

## 2026-05-02 - Inventory existing cascades before adding new stage automation

ERPNext may already be doing part of the business workflow through checkout, payment success, webhooks, or native document helpers. In LT, `/checkout` already creates Customer/Contact, Sales Order, and Payment Request records, while `/payment-success` and the Stripe webhook reconcile paid orders into Sales Invoices and transactional emails.

**Counter-move:** before connecting a CRM stage to finance or accounting, run a live backend inventory and map existing document creators first. Add automation only where it coordinates with the existing path instead of creating a parallel path.

---

## 2026-05-02 - Wire uncertain stage cascades to reversible operations first

Stage movement needs to do real work, but not every stage is ready to carry finance meaning. The CRM pipeline is now safe because `Archive` is off-board only; the next risk would be letting early automation create Sales Orders, invoices, payment requests, or win/loss stats before the business threshold is settled.

**Counter-move:** when a cascade is directionally right but the finance/accounting threshold is not approved yet, start with reversible operational records such as Tasks. Verify that moving stages does not change financial document counts, and make the next finance-trigger decision explicit instead of hidden inside a stage label.

---

## 2026-05-02 - Client CRM stages should not hijack ERPNext native status

The Odoo reference used `Archive` to remove cards from the active Kanban, but its local stage data also marked Archive like a won/folded stage. Copying those values into ERPNext `Lead.status` would risk distorting conversion logic, finance/reporting assumptions, or future workflow triggers.

**Counter-move:** when translating CRM stages into ERPNext, first separate "what the operator needs to see" from "what ERPNext uses internally." Put client-friendly board stages on a custom Select field when there is any chance native status affects reporting or accounting. Treat `Archive` as off-board only unless the business explicitly says it is won, lost, billable, or ready for a finance cascade.

---

## 2026-05-02 - Estimated event times should not be Frappe Time fields

Frappe `Time` Custom Fields render as awkward time controls in Desk and can make estimated event times look overly precise. In this repo, the Lead time fields also carried customer helper copy inside employee-facing labels and old records displayed machine-style values with seconds/microseconds.

**Counter-move:** for estimated times that staff need to edit quickly, use `Data` fields with plain labels and a short example description. Keep customer helper copy on the public form. If an existing Custom Field must move from `Time` to `Data`, use a guarded sync/migration path and verify the actual Desk route, because Frappe blocks that fieldtype change through normal validation.

---

## 2026-05-02 - ERPNext Workspace widgets are two-part wiring

The Owner Home command center needed Number Cards and a Dashboard Chart, but creating the backend widget records was not enough. Frappe Workspaces also need matching child rows (`Workspace Number Card` / `Workspace Chart`) and matching content blocks in `Workspace.content`. The first sync attempt also used internal Number Card names that differed from their labels; Frappe's Number Card naming followed the label/autoname, so Workspace link validation failed.

**Counter-move:** when building Desk dashboards, verify all layers together: widget document exists, Workspace child row points to the actual widget name, Workspace content has the block, and the non-admin role can see it in Desk. Keep widget names and displayed labels aligned unless there is a verified reason to separate them.

---

## 2026-05-01 - Desk conditionals need the real child-table field, not a text echo

The public `/contact` form looked correct, but the ERPNext Desk form still depended on `custom_event_type`, a Table MultiSelect. The submit handler was only echoing services into text-style data, so real inquiries could arrive without the Desk conditional sections opening. **Counter-move:** when a public form feeds a Desk workflow, verify the exact backend field that drives Desk behavior, not just that the submission created a Lead.

The useful verifier checks three layers together: current service records, Lead Custom Field labels/depends_on logic, and the submit helper that builds child rows. A browser success modal alone is not enough for CRM parity.

---

## 2026-05-01 - Form labels are behavior contracts

### Lesson 1 - "Only" means the UI must enforce exclusivity.

Delivery Only and Pickup Only sounded clear in isolation, but the form lets customers stack services. That label was therefore wrong: it implied selecting Delivery/Pickup should lock out decor, twisting, face painting, or Events Inquiry. **Counter-move:** if a service can combine with other services, do not label it "Only." If the business truly wants an only path, enforce that logic in the UI and backend mapping.

### Lesson 2 - The ideal customer path needs structure, not a blank box.

Events Inquiry is the high-value path for large, multi-piece packages. A freeform "What type of decor?" field made the best customer do the most work. **Counter-move:** give ideal buyers structured choices pulled from the real catalog/homepage categories, then add color and notes fields for personality and nuance.

### Lesson 3 - Conditional fields should ask only the people who can answer them.

"Shade is required for outdoor events" matters for live artists, not outside balloon decor, pickup, delivery, or Something Else. Every irrelevant dropdown makes the form feel less intelligent. **Counter-move:** verify each service choice independently with an automated form-logic script, including the absence of stale labels.

### Lesson 4 - GL tangent flow needs queue capture, not a forced linear review.

GL named an ADHD inattentive working style during this session. Product direction arrived as a chain of quick corrections: Events Inquiry, shade logic, pickup, location wording, "Only" labels. **Counter-move:** keep the active slice small, restate the current target, convert tangents into queue/docs when they are not the current task, and avoid making GL re-review stale items one by one.

---

## 2026-05-01 - Actual fit needs a geometry gate, not a confidence statement

### Lesson 1 - Offscreen controls are usually framework residue, not just CSS drift.

The Seasonal category page showed `Prev` / `Next` half off screen. The visible controls were not the themed `#lt-pagination` block; Webshop was injecting a second `.product-paging-area` row inside `#product-listing` with Bootstrap rows and inline float styles. CSS aimed only at the themed block could never fix it. **Counter-move:** inspect the rendered DOM before polishing. If a control ignores scoped CSS, find whether the framework injected a second copy.

### Lesson 2 - A fit check must distinguish visible overflow from clipped carousel internals.

The expanded layout spec initially failed the homepage because the reviews carousel track intentionally extends far outside the viewport, but the page had no document overflow and the track is clipped by its wrapper. That was a false positive. **Counter-move:** layout-fit tests should flag document overflow and visible un-clipped element overflow, while allowing descendants inside an overflow-clipping ancestor.

### Lesson 3 - Python Playwright and Node Playwright are different installations.

`python scripts/verify/smoke_shop.py` failed because `C:\Python314\python.exe` has no Python `playwright` package. Playwright was still installed: Node/CLI Playwright 1.59.1 lives in npm's npx cache at `C:\Users\baenb\AppData\Local\npm-cache\_npx\420ff84f11983ee5\node_modules\.bin\playwright.cmd`. **Counter-move:** when someone says "Playwright is installed," locate which runtime owns it before declaring a verifier unavailable.

---

## 2026-05-01 - Navigation labels must match customer intent

### Lesson 1 - "Plan by Occasion" in a shop means product discovery first.

I initially routed every occasion link to `/contact?occasion=...` because it was easy to connect the event labels to the Lead form. GL corrected it hard: customers opening an occasion dropdown in a shop are asking "show me the products for this occasion," not "send me to a generic contact form." **Counter-move:** when a nav label sounds like browsing (`Shop`, `Plan`, `Browse`, `Occasion`, `Category`), route to product/category/content discovery first. Inquiry CTAs belong where they are explicitly framed as inquiry.

### Lesson 2 - Verify nav against real catalog routes before inventing landing pages.

The fix did not require new occasion pages. The ERPNext catalog already had product-backed answers: Birthday Deliveries, Baby Shower Garland, Graduation Grab n Go, Get-Well Bouquets, Large head Missionary, Easter Arch, etc. **Counter-move:** query Website Items and Item Groups before adding routes. Prefer existing real product/category pages over placeholder landing pages or contact shortcuts.

### Lesson 3 - Source-level IA checks catch regressions that screenshots miss.

The opened-dropdown screenshots showed a clean layout, but they would not by themselves prevent someone from re-pointing every occasion link back to contact later. `scripts/verify/nav_ia.py` now encodes the behavioral contract: no duplicate Contact CTA in mobile drawer, no nav `/book`, and no `contact?occasion` routes in Plan by Occasion. **Counter-move:** pair visual checks with a small source-level invariant script for nav IA.

---

## 2026-05-01 — Storefront correction pass: preserve framework contracts and accessibility

### Lesson 1 — Category listing bugs can be wrapper-contract bugs, not catalog bugs.

`/shop-items/arches` returned non-arches because the LT Item Group template override removed Webshop's expected `.item-group-content` class. Webshop's listing JavaScript reads that wrapper to find the active Item Group; without it, the listing fell back to broader product results. **Counter-move:** before changing catalog data, inspect the stock Webshop template/JS contract and keep framework semantic classes even when adding LT BEM classes.

### Lesson 2 — Add listing-card fields by wrapping Webshop APIs, not patching upstream.

GL wanted brand descriptions visible on product listing cards. Webshop's stock product filter response did not include LT's brand-description field. The clean fix was a local `override_whitelisted_methods` wrapper around `webshop.webshop.api.get_product_filter_data`: delegate to stock Webshop, then append `lt_brand_description`. **Counter-move:** for small Webshop data enrichments, preserve framework behavior and add the missing field locally instead of editing upstream app code.

### Lesson 3 — Accessibility sizing is not a compression knob.

Footer/header balance must not be solved by shrinking text or controls below accessible sizes. GL explicitly rejected that direction. **Counter-move:** fix density through content removal, centering, grid/flex layout, and responsive wrapping. Preserve readable text and practical 44px interactive targets.

### Lesson 4 — Verification screenshots are receipts, not source.

Header/footer/menu/product verification generated many Chrome/Edge profile folders and screenshots. Those are useful during QA but not canonical project artifacts. **Counter-move:** summarize verified results in docs, keep only intentionally promoted reference assets, and ignore/delete generated browser profiles and throwaway verification captures.

---

## 2026-04-30 (evening) — Mirror rebuild Phase 1 chrome via /triadic-construction-v2

### Context

GL exhausted. Catalog port shipped that morning but visually disappointed them ("I hate the entire shop"). They directed: clone Hetzner Odoo deployment wholesale into ERPNext-coded chrome + pages, keep only the homepage, use agent teams. Then went to nap. I ran an autonomous chain: tool research → mirror → /plan-deepen → 6 pre-tasks → triadic chrome rebuild → fix round → audit. Chrome shipped (with desktop polish flagged); Phase 2 page rebuilds deferred to next session.

### Lesson 1 — When GL names a frame, the live correction beats the documented rule.

I opened the session by parroting CLAUDE.md's "new build, not a migration" frame on the first message. GL corrected immediately: *"it is a migration, not a new build."* The "Reframe is locked" rule in CLAUDE.md was itself superseded by GL's live directive. I had to undo a multi-file framing cascade across 8 docs. **Counter-move:** when GL names something authoritatively in conversation, treat that as ground truth even when documentation contradicts. Update the docs to match GL, not the reverse.

### Lesson 2 — The "load-bearing 404" was always infrastructure, never missing code.

`/book` had been 404 every prior session for ~weeks. Plan-deepen agent found that `www/book.{py,html}` already exist with full implementation per the `frappe-form-integrity` skill. The 404 was a stale Frappe website cache + nginx upstream-IP staleness after a backend restart. Cache flush + frontend container restart unblocked it in <30 minutes. **Counter-move:** before assuming a Frappe route is missing code, run the cache flush + check container restart status. The site exists where you put it; cache lies louder than missing files.

### Lesson 3 — Triadic-construction-v2 reviewers caught what solo build would have shipped broken.

Round 1 chrome shipped with **mobile drawer always visible** (CSS class mismatch — every mobile page would have looked broken to customers), **2 of 3 mobile mega menu accordions completely dead** (data-attribute mismatch + querySelector singular bug), **megamenu panel had no CSS rules** (would render as inline blocks pushing content down), and **mega-trigger CSS open-state targeting wrong class**. Architect + Execution Engine reviewers found these via Active Agreement (independent flags, same defects). SecOps reviewer caught a separate set (rate-limit X-Forwarded-For bypass, hash instability, /book Esc-key UX bug). All caught in the same round; all fixed mechanically because the findings cited file:line. **Counter-move:** for high-blast-radius work (chrome, payment flows, schema changes), pay the triadic context cost. The discipline earns its keep.

### Lesson 4 — Triadic Build Brief must specify class-name alignment per element, not just namespaces.

The single biggest time-sink in the triadic round was Builder Jinja choosing different BEM class names than what Builder CSS had pre-existing rules for. Build Brief said "BEM namespace `lt-*`" but didn't enumerate specific names. Round 1 shipped with 8+ template-vs-CSS class divergences (`lt-header__mobile-nav` vs `lt-header__mobile-nav-collapse`, `lt-header__mega-item` vs `lt-header__has-mega`, `lt-megamenu__*` vs `lt-header__mega-*`, etc.). **Counter-move:** for any future triadic dispatch involving template-CSS coordination, include a class-name alignment table in the Build Brief: "trigger `<li>` uses `.lt-header__has-mega`; panel `<div>` uses `.lt-header__mega`; inner container uses `.lt-header__mega-inner`; link uses `.lt-header__mega-link`." Specificity per element prevents the divergence.

### Lesson 5 — Sub-agents need explicit skill-invocation instructions in their briefs (agency gate is per-session).

The agency pretooluse gate fires on Edit/Write to Frappe app files unless `frappe-form-integrity` / `frappe-asset-pipeline` / etc. skills have been invoked **in that session**. Sub-agents have their own session context. Each builder I dispatched had to invoke the relevant safety skill BEFORE their first edit. I documented this in each builder brief; without it, the gate blocks the build silently from the agent's perspective and they fall back to Bash workarounds. **Counter-move:** every Frappe-app-file-touching agent gets a "Required skill invocation BEFORE any edit" section in its brief. Builder JS this session reported a `frappe-migration-guard` gate detection edge case for sub-agent contexts — flagged for ops/infra.

### Lesson 6 — `@rate_limit(key="X", ip_based=True)` does NOT create two counters.

I wrote a synthesis fix-shape calling for "two-tier rate limiting" (IP + email). GL Proxy caught it: Frappe's `@rate_limit` combines `ip` and `key` into a SINGLE `ip:key` identity, not two independent counters. The correct shapes are Option A (`key="email", ip_based=False` — defeats X-Forwarded-For spoofing, accepts email-enumeration trade-off) OR Option B (nginx-level XFF strip — higher leverage, protects all rate-limited endpoints). **Counter-move:** read the actual Frappe source before describing decorator behavior. Don't synthesize from training memory. The Proxy review at Phase 2.5 is the safety net — don't lean on it for what you should verify yourself.

### Lesson 7 — Frappe nginx upstream-IP is sticky after backend container restart.

After `docker restart locally-twisted-erpnext-v15-backend-1`, nginx in the frontend container kept hitting the OLD container's IP (`172.22.0.8`) and returning 502 even though backend was up at a new IP. Cause: Frappe's bundled `frappe.conf` for nginx has no `resolver` directive — nginx resolves backend's IP once at startup and caches forever. **Counter-move:** any time you restart the backend container, also restart frontend OR document that the user expects 502s for ~5 min until you do. Logged as agency-tier auto-behavior B5.

### Lesson 8 — `hash(email)` is randomized per Python process — useless for log correlation.

Python's `hash()` builtin uses PYTHONHASHSEED which is randomized per process by default. Across container restarts, the same email produces different hashes. SecOps reviewer caught it. Replace with `hashlib.sha256(email.encode("utf-8")).hexdigest()[:16]` for stable, non-reversible-in-practice log correlation. **Counter-move:** any time you use `hash()` for cross-process correlation (logs, dedup keys, cache keys), reach for `hashlib.sha256` instead. The builtin is for in-memory dictionary keys only.

### Lesson 9 — Auto-orchestrate the architectural calls + log reversibility, don't ask GL when they're asleep.

GL gave clear authorization: *"if it's Odoo only and there's an ERPNext equivalent, do that. OR DON'T, and just tell me what you couldn't do."* Two architectural decisions came up mid-build (mega menu IA — extend Item Group tree vs template-grouping; category URL shape — match Hetzner's `/shop/category/X-N` vs ERPNext native `/shop-items/X`). I picked the lower-blast-radius option for both, logged them as reversible in `locally-twisted-decisions.md`, and proceeded. GL's wake-up message confirmed this was the right shape: "you've done a really good job so far." **Counter-move:** when GL is unavailable and authorization is broad, decide + log + proceed. Don't pile up gates that block work.

### Lesson 10 — Read the actual screenshots, don't just trust DOM facts + script flags.

The Playwright audit script extracted DOM facts (`.lt-header` count, `.lt-footer` count, `.lt-header__mega` count, `mobile_drawer_visible`) and reported all routes "OK." But when I read the actual home-desktop.png file as an image, the centered logo dominating + tagline wrapping vertically was immediately visible. DOM-says-rendered ≠ pixels-look-right. The agency's standing rule from 2026-04-29 lessons: "viewport-only Playwright screenshots are the verification method, NOT full-page screenshots... DOM widths are preconditions, not verdicts." **Counter-move:** Read every screenshot file you capture as an image. Describe what's pixel-visible. Don't ship a verification report based on DOM facts alone.

### What this means for the next instance

The chrome work shipped (Phase 1 of the mirror rebuild). Phase 2 page rebuilds (~12 routes) are next — single focused builder per page is probably the right shape (lower interdependency than chrome). Reserve full triadic for things touching every page. The mirror at `_resources/odoo-live-mirror/` IS the spec — read the relevant page file before each rebuild. GL named the desktop chrome polish issue at session close; address it early in your session as a quick win. Don't ask GL questions they've already answered. Document architectural calls as reversible. Read your own screenshots.

---

## 2026-04-30 — Full catalog port from live Odoo to ERPNext webshop

### Six lessons from a 53-Website-Item / 10,631-Item / 10,613-Item-Price port

**Context.** GL's directive: rebuild the entire old live Odoo test shop catalog (`http://5.78.136.133/shop`) into ERPNext webshop. Every product, every variant, every option, no exceptions. Result after DB verification: 53 Website Items, 10,631 Items total, 49 variant templates, 4 single-SKU templates, 10,578 variants, 10,613 Item Prices, 32,002 Item Variant Attribute child rows, 11 Item Group children + restructured hierarchy, mega menu, on-brand product detail pages with inline variant selectors. Smoke tests pass. This was catalog-data porting into a new ERPNext build, not an Odoo migration.

### Lesson 1 — The catalog source of truth is the LIVE site, not the cached export.

The existing `_resources/odoo-export/catalog.json` (created 2026-04-26) had 51 products. The live re-scrape on 2026-04-30 found **53 products** — Odoo had added `birthday-deliveries` and `large-head-missionary` since the cached export. Five products had `image_url=null` in the cached file but DO have images on the live site (the original scraper's regex missed `data-src` lazy-load patterns). For any catalog work: re-scrape live, don't trust caches.

**To do differently:** treat `_resources/odoo-export/catalog.json` as historical reference; produce a fresh `_resources/odoo-live/catalog.json` from the live site at the start of any catalog rebuild.

### Lesson 2 — Frappe `installed_apps` order determines who wins template ChoiceLoader resolution.

`frappe.get_installed_apps()` reads from `db.get_global("installed_apps")` (a JSON list). `template_page.py:53` iterates that list **REVERSED**, picking the first match. With our default order `[frappe, erpnext, locally_twisted, payments, webshop]`, reversed = `[webshop, payments, locally_twisted, ...]` — webshop won every template at `templates/generators/item/...`. The override files we placed at `apps/locally_twisted/locally_twisted/templates/generators/item/` were silently ignored.

**The fix:** put `locally_twisted` LAST in the installed apps list.

```python
# bench --site frontend console
import json
new = ["frappe", "erpnext", "payments", "webshop", "locally_twisted"]
frappe.db.set_global("installed_apps", json.dumps(new))
frappe.db.commit()
# then docker restart the backend
```

This is irreversible-feeling but reversible. After the change, `apps/locally_twisted/.../templates/...` overrides win for any path webshop also defines.

**Verification before any template-override work:** drop a marker file at the override path (e.g. add a unique CSS class to a copied-verbatim template), restart backend, hit the URL, grep the response for the marker. If absent, fix load order before continuing.

### Lesson 3 — Webshop's `WebsiteItem.make_route()` adds `random_string(5)` to every auto-generated route. Always set `route` explicitly.

`apps/webshop/webshop/webshop/doctype/website_item/website_item.py:108–118` returns `<group_route>/<scrubbed_name>-<random5>` when `self.route` is empty. Result: ugly unstable URLs like `/shop-items/arches/basketball-arch-tljq2`. Customer bookmarks would break on every `make_website_item` re-run.

**The fix:** in `_upsert_website_item`, compute the clean route (`<group_route>/<slug>`) and set `wi.route = clean_route` BEFORE save. Webshop's make_route only fires when `self.route` is empty, so the explicit set wins.

### Lesson 4 — Item Price cannot exist on a template Item with `has_variants=1`.

`tabItem Price.validate_item_template()` throws `InvalidItemTemplateError` if you try to create one. Item Price must live on each variant's item_code instead. For "from $X" display on the listing card (template), query `MIN(price_list_rate)` across the variant set in the controller and surface as `price_is_from`.

### Lesson 5 — Setting `Item.image = "/files/<x>.png"` directly silently fails when there's no `File` doctype record.

Per webshop's `validate_website_image()`, the field gets cleared on save if no matching `File` doc exists for that URL. The `Item.image` field expects an attached `File`. Pattern that works:

```python
f = frappe.get_doc({
    "doctype": "File",
    "file_name": "basketball-arch.png",
    "file_url": "/files/basketball-arch.png",
    "is_private": 0,
    "attached_to_doctype": "Item",
    "attached_to_name": "basketball-arch",
}).insert(ignore_permissions=True)
# Then Item.image = "/files/basketball-arch.png" sticks.
```

The image file must exist on disk at `sites/<site>/public/files/<slug>.png` before the File doc is created. Copy via `shutil` or pre-stage outside the script.

### Lesson 6 — Webshop variant cards are JS-rendered, not Jinja-templated. Override via CSS, not template.

`apps/webshop/webshop/public/js/product_ui/list.js:101` bakes `${item.item_group} | Item Code : ${item.item_code}` into the card markup at compile time. There's no Jinja template to override — it's compiled into the bundle. Any product listing route (`/shop-items/<group>`, `/all-products`) renders cards through this JS.

**The fix:** CSS hide `.product-code` in the listing context. Add to lt-theme.css:

```css
.product-list .product-code,
.item-card-group-section .product-code,
#product-listing .product-code {
    display: none !important;
}
```

This is the right call here even though `!important` chains are normally a code smell — we can't override a compiled JS bundle without forking it. The CSS-hide is contained and removes the jargon at customer-render time.

### Bonus — Odoo's per-product attribute-exclusions data is captured in the scrape and respected.

Odoo's product page emits `data-attribute-exclusions="{exclusions: {...}, mapped_attribute_names: {...}}"` JSON in the form HTML. The scraper parses it, builds the cartesian product of all attribute values, then filters out combinations where any selected ptav_id appears in another's exclusion list. For LT's catalog this filtered down to 10,578 ERPNext Item Variants (vs the naive cartesian count of more). Odoo's `archived_combinations` is also captured but currently empty for LT's catalog.

The math sanity-check: `birthday-deliveries` has 4 attributes (Delivery Size 3 �- Delivery themes 27 �- Add Foil Number 10 �- Add Bouquet 3 = 2,430 cartesian; 0 exclusions; 2,430 valid). Confirmed.

### Bonus — Variant ABBR uniqueness is non-negotiable.

ERPNext's `make_variant_item_code` builds variant `item_code` as `<template>-<abbr1>-<abbr2>-...`. If two attribute values share an `abbr` (or the abbr is blank), variant inserts collide on duplicate-key DB error. Solution in `build_item_attribute_fixture.py`: deterministic abbr generation with collision detection (3-char prefix → 4 → 5 → 6 → fallback `prefix+counter`). 195 values produced 195 unique abbrs.

### Bonus — Item Attribute Value rejects case-only duplicates.

Odoo had `Blue Slate` (ptav 1357) AND `Blue slate` (ptav 1399) for `latex colors` — same color, two ptav rows from different attribute lines. ERPNext's Item Attribute validate() throws `Attribute value: Blue Slate must appear only once` (case-insensitive). The fixture builder dedupes case-insensitively + whitespace-normalized, preserves first-seen casing as canonical, and persists a `value_normalize_map.json` so the bulk import script remaps Odoo's lower-case ptav references to the canonical capitalized name. 197 raw values → 195 canonical.

---

## 2026-04-29 late (Hetzner /book spec session — "fighting GL" pattern) — One critical lesson

**Superseded form labels 2026-05-01:** the lesson below is still valid as a stale-source receipt, but the old Hetzner labels `Delivery Only` and `Event Package` are no longer current LT form truth. Current labels are `Delivery`, `Pickup`, and `Events Inquiry`.

### When GL points at a URL, read the URL. Stop pivoting to stale local files when one tool fails to reach it.

**What happened.** GL asked me to rebuild `/book` to match `http://5.78.136.133/book` exactly. My first WebFetch on that URL returned `ECONNREFUSED`. I took that as proof Hetzner was offline — plausible per the project's Reference Disposition ("Failed Hetzner deployment ... will be decommissioned"). I pivoted to the local Odoo clone at `C:\Users\baenb\projects\locally-twisted-odoo\` as my canonical spec, read `addons/locally_twisted/views/pages/page_book.xml`, and reported what I saw there as authoritative.

**The local clone was stale.** Its XML had:
- Single-select `x_event_type` (one service per Lead)
- 3-file �- 10 MB photo upload
- No per-service conditional notes (one generic textarea)

**Hetzner had been independently updated** to:
- Multi-select `x_services` checkboxes (Balloon Decor / Twisting / Painting / Delivery Only / Event Package / Something Else)
- Per-service conditional notes — `decor_notes`, `twisting_notes`, `painting_notes`, etc. — show/hide via Odoo's `data-visibility-dependency="x_services"` + `data-visibility-comparator="contains"` pattern
- Environment fields (Indoor/Outdoor, Shade Required, Colors) appearing when ANY service is selected
- 5 files �- 25 MB photo upload

The ERPNext Lead Custom Fields (45 of them — `custom_event_type` as Table MultiSelect, per-service Long Text notes, etc.) had been built to mirror Hetzner's richer schema. GL was right when they said *"some of it's already implemented in the backend."*

I kept reporting the local clone's old spec as canonical and surfacing every difference as a question for GL to confirm: *"Are you sure about 5/25 photos? Multi-select or single-select? Are these CRM stages still right?"* Each question was me trusting my stale local read over GL's URL. Each one cost GL tokens to walk me through what they'd already shown me. GL named the dynamic directly:

> *"I don't know where the hell you're looking! ... Why the hell are you fighting me on it? ... Stop fighting me on this. What's the problem? ... I'm nervous about you touching anything if you keep saying this."*

**The technical fix that broke me out:** Bash `curl http://5.78.136.133/book` returned HTTP 200 cleanly (68 KB of HTML). The earlier `ECONNREFUSED` was a WebFetch tool sandbox limitation, not a real network outage. Different tools have different network surfaces. The snapshot files at `_resources/odoo-live-snapshot/hetzner-{book,contact}.html` are now on disk as the canonical spec going forward — they survive even after Hetzner decommissions.

**Three lessons:**

1. **One tool failing on a URL is not a network outage.** When WebFetch (or any single tool) reports a URL unreachable, try `curl` from Bash, Playwright, or a browser screenshot before treating the URL as down. Especially when GL has named that URL as canonical.

2. **Stale local clones are not "the spec" just because the live source seems unreachable.** A local checkout can be commits behind production AND production can have been updated independently of git history. *"The file in front of me"* is not equivalent to *"the URL GL pointed at."* When the two diverge, GL's URL is canonical — by definition, since GL named it.

3. **When GL has named a source of truth, don't surface differences as questions.** *"Are you sure about X?"* reads as doubt — and IS doubt — when GL has been showing you the URL since the second message of the conversation. The discipline is: read the URL, build to what's there, only ask when something genuinely cannot be inferred from the spec. **GL points, you read.**

**Why this matters past this incident.** The pattern compounded over five turns. Each verification question added trust cost. By the fifth, GL was *nervous about me touching anything*. That's the load-bearing failure mode — not the wrong photo limit, but the erosion of trust that would have cascaded into the actual build. The rule (now in `CLAUDE.md` "Hetzner `/book` and `/contact` are the canonical spec for the rebuild" section) is here so the next instance doesn't have to relearn this from inside GL's frustration.

**Codified in:** `CLAUDE.md` "Hetzner `/book` and `/contact` are the canonical spec for the rebuild" section, added 2026-04-29.

---

## 2026-04-29 evening (mobile-responsiveness + design-guide-import session) — Six lessons

### Frappe wraps every page in `<main class="container my-4">` — opt OUT of confinement, don't fight it section-by-section

Every Frappe website page renders inside `<main class="container my-4">` inside `.page-content-wrapper`. Frappe's bundled `apps/frappe/frappe/public/scss/website/index.scss:117-122` adds `.page-content-wrapper .container { padding: 1.5rem }` at `(max-width: map-get($grid-breakpoints, "lg"))` (= 992px). At desktop, the `.container` itself has `max-width: 1290px; padding: 80px each side` (computed). Net result: page content at 1280 viewport sits inside a 1120px-wide centered column with 80px white gutters on each side.

This is fine for content pages that want centered readable widths. It is BROKEN for full-bleed hero bands with background colors — the colored band only spans 1120px and white gutters show on each side, which reads as "stuck in container" to anyone with a designer's eye.

**Lesson:** the right structural pattern is to override `.page-content-wrapper .container` in `lt-theme.css` to remove ALL its horizontal opinion (padding 0, max-width 100%) at every breakpoint, so sections own their own layout. Sections that want full-bleed bands span the viewport. Sections that want narrow centered content use their own inner wrapper with `max-width + margin: 0 auto`. Webshop product detail (`.product-container`) and cart (`.cart-container`) need their OWN intentional centered max-width because they were designed expecting the parent container's confinement — added at `_resources/lt-theme.css` (max-width: 1200px). The structural fix is global; per-page CSS is not needed.

### Specificity matters when overriding Bootstrap-style parent-container rules

My first override of Frappe's `.page-content-wrapper .container` rule used `body main.container` (specificity 0,0,1,2 — one class + two types). It LOST to Frappe's `.page-content-wrapper .container` (specificity 0,0,2,0 — two classes). CSS specificity: classes outweigh types. Two classes wins against one class + N types. The `max-width` part of my rule applied (it was new), but the `padding-left: 0` lost because Frappe's rule had matching specificity and was loaded later.

**Lesson:** when overriding a bundled rule, MATCH its selector specificity (or exceed it without `!important`). Use Chrome DevTools or Playwright's CDP `CSS.getMatchedStylesForNode` to see exactly which rules are applying and at what specificity. The fix: `.page-content-wrapper .container` (two classes — matches Frappe's rule, wins by source order since lt-theme.css loads after the bundle).

### Full-page screenshots LIE at extreme aspect ratios

Playwright with `full_page=True` captures the entire scrollable height. On a tall mobile page (6691px tall on home, 3387px on contact), the screenshot dimensions become extreme (e.g., 410�-6691). When displayed at any reasonable rendering size, the image gets compressed to ~123�-2000 — that's a 33�- vertical compression. Sections that should be visible become slivers of pixels indistinguishable from white space. I declared mobile responsiveness "fixed" three times based on these compressed renders; each time the actual visual state was different from what I'd inferred.

**Lesson:** for visual verification, use **viewport-only screenshots at concrete device widths** — 320 (iPhone SE), 375 (iPhone), 414 (iPhone Plus), 1280 (desktop). These don't compress because they're not full-page. Pair with: DOM probes for element widths and overflow (preconditions); programmatic checks of element positions and computed styles; AND ALWAYS GL opening the page in their real browser before declaring done. Full-page is useful for documenting what's there at a glance, but it's not a verdict on visual correctness.

### Brand logo + hamburger fit at 375 viewport math: 88px reserved, calc() max-width

The mobile brand logo CSS at `lt-theme.css:783-788` had `max-width: 350px; height: 100px` (1.25�- of an earlier 80/280 spec). At 375 viewport with row padding 32 + hamburger 44 = 76px reserved, the logo had only 299px of available space. The 350px fixed cap pushed the hamburger 35px past the right edge. Previous instance hid the visual symptom with `body { max-width: 100vw; overflow-x: hidden }` — but the hamburger remained functionally unreachable: only 9px of the 44px tap target was inside the visible viewport on a 375px screen.

**Lesson:** mobile brand logo needs a **responsive cap** that scales with viewport, not a fixed pixel max-width. The shape that works:

```css
.lt-header__brand--mobile img,
.lt-header__brand--mobile .lt-logo {
  height: auto;        /* preserves natural aspect ratio at every viewport */
  max-height: 90px;    /* upper bound on tablets so the logo doesn't grow oversized */
  max-width: calc(100vw - 88px);  /* 88px reserves: 44 hamburger + 32 row padding + 12 gap */
}
```

Tested at 320 (iPhone SE), 375, 414 — hamburger fits cleanly with breathing room at each. The principle: any header element with fixed pixel dimensions that competes for finite viewport width is a responsive bug waiting to fire.

### Webshop's bundled wrappers need their own intentional max-width when the parent is fullbleed

Removing `.page-content-wrapper main.container`'s confinement at all breakpoints gave LT-designed pages the full viewport (good — hero bands now span edge-to-edge). But it also removed webshop's product detail (`.product-container`) and cart (`.cart-container`) constraints — those were designed expecting `.container`'s max-width to constrain them. Result: product detail bled edge-to-edge on desktop (1280px wide) with no readable centering.

**Lesson:** when stripping a wrapper's max-width globally, audit downstream pages for ones that DEPENDED on it. Webshop pages in particular were built expecting `.container`'s centered max-width to do the framing — give them their own intentional max-width:

```css
.product-container,
.cart-container {
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
  padding-left: 1rem;     /* mobile */
  padding-right: 1rem;
}
@media (min-width: 768px) {
  .product-container,
  .cart-container {
    padding-left: 1.5rem;  /* desktop */
    padding-right: 1.5rem;
  }
}
```

This is structural — applies once, every webshop page inherits. Mobile responsive automatically because `max-width: 1200px` becomes `max-width: 100% - padding` once the viewport drops below 1200.

### Cross-project knowledge gaps are invisible until they're surfaced — paths matter

GL ran a 7-designer LT design competition on 2026-04-26 in a separate project directory (`C:\Users\baenb\projects\zoho-locally-twisted\gallery\`). The synthesis (D3 + D5 + D7 hybrid) was the approved design contract. PLAN.md line 47 referenced "Opus Competition Redesign concept" with NO PATH. The standard arrival reading order led every instance through every artifact and not one of them pointed at the gallery. **Multiple build instances over multiple sessions never found the design contract.** Each built the customer-facing pages without the design reference. GL had to point an instance at it explicitly on 2026-04-29 to break the cycle.

**Lesson:** if a plan or doc references a file or concept, write the path. Always. Conversation-only knowledge gets compacted away — references that point at conversation-only knowledge become dead links. The fix here was structural: import the synthesis + screenshots into `_resources/design-guide/`, add a dedicated section in CLAUDE.md ("Design guide — where it is, why it's here, and why it must stay"), update PLAN.md line 47 to point at concrete file paths, log the systemic gap in decisions. The agency client-isolation rule says every client folder is self-contained for transfer — this means EXTERNAL references break that contract, both for transferability and for findability. **If the design contract lives outside the client folder, it might as well not exist.**

### Reporting without watching, escalated: trying to canonize unverified work is "scary"

I declared the structural CSS fix done off DOM probes (no overflow, hamburger at 304 R-edge on 320 viewport, etc.) and started writing it up as the agency-wide pattern in `Built_by_Cameron/.claude/capabilities/recipes/frappe-conventions.md` and `HOW-TO-WIN-AT-FRAPPE/auto-behaviors.md`. GL stopped this with: *"do not put that on the agency tier, because you did not prove anything. In fact, you essentially showed what you were doing wrong and trying to codify it, and that is scary."*

The agency tier exists to hold STABLE, PROVEN, MULTI-VALIDATED patterns that future BBC clients inherit. Putting fresh single-instance work there spreads bugs forward into every future client — they read the bad pattern as truth. Reporting without watching is a single-session trust withdrawal; canonifying without watching is a cross-client trust withdrawal.

**Lesson:** the agency tier is downstream of repeated proof, not upstream of single-session enthusiasm. The instinct to canonize fires before proof exists; it must be refused until validation lands. The right shape: do the work, prove it stands up across iterations, document the receipt at LT-tier (this file + decisions log), STOP. Agency tier docs emerge when a pattern proves itself across multiple clients/sessions — and they're written by whichever instance recognizes the stable pattern at THAT future moment, not by the instance that first encountered it.

---

## 2026-04-29 (guest-cart + Stripe-Link + cascade session) — Six lessons

### Frappe's `frappe.Redirect` raised in `get_context` BYPASSES the template

`payment_success.py` `_handle_stripe_session` calls `_redirect()` which sets `frappe.local.flags.redirect_location` and raises `frappe.Redirect`. The browser gets a 302 → /thank-you and never sees the `payment_success.html` body. Any JS in that template never executes. My first attempt to clear `LT_CART` in `payment_success.html` was inert. Cart-clear had to live in `thank_you.html` (the page the browser actually renders).

**Lesson:** When putting JS in a Frappe template, trace the controller flow. If `get_context` raises `frappe.Redirect`, the template is a stub that never renders. Such pages are useful as routing-only controllers but can't carry browser-executed code. Customer-side JS goes in the destination page.

**Receipt:** 2026-04-29. GL reported "the cart show 2 item in it. The order processed and now the cart needs to clear" after their successful /thank-you landing. Diagnosed by reading `payment_success.py` line 102 `_redirect(...)` and tracing the raise.

### Stripe `payment_method_types=["card"]` does NOT suppress Link UI — that's account-level

`payment_method_types=["card"]` on a Checkout Session restricts which payment METHODS appear, but Stripe layers Link UI ("Save my information for faster checkout" + "Pay with Bank via Link" + Link Terms/Privacy) on top regardless. The skill content says it explicitly: *"Link is controlled through the Dashboard. Create a custom payment method configuration with Link off."* I half-read it on first pass.

**Fix:** Create a Payment Method Configuration on the account with `link.display_preference={"preference": "off"}`, pass `payment_method_configuration: <pmc_id>` on every Checkout Session. PMC creation has a quirk: `preference="off"` is rejected on parent (default) PMCs — child-only restriction. Workaround: create a NEW top-level PMC without specifying parent. We did: `pmc_1TRZH2DfnlZQv66ncb001soG` ("LT No Link"). Hard-coded constant in `payments/stripe_session.py`.

**Verification gate:** Render the actual Stripe page in Playwright before claiming Link is gone. The API response will say `payment_method_types: ["card"]` even when the Link UI is showing — the Session config doesn't reflect the page render.

**Receipt:** 2026-04-29. GL reported "straight to link again" after the first fix shipped. Rendered in Playwright, saw "Save my information for faster checkout" + "Pay securely at Locally Twisted and everywhere Link is accepted" + Link Terms still rendering. Custom PMC fixed it.

### Webshop `templates/pages/cart.html` wins route resolution over `www/cart.py` — rename to avoid collision

Frappe resolves `/cart` against `templates/pages/cart.html` BEFORE applying `website_route_rules`. Webshop ships such a template at `apps/webshop/webshop/templates/pages/cart.html`. Even with our `hooks.py` route rule mapping `/cart → cart`, webshop's pages-style template wins and our `www/cart.{py,html}` never serves.

**Fix:** Rename our files to `lt_cart.{py,html}` and update the route rule to `/cart → lt_cart`. Verified by `curl /cart | grep lt-cart__title` — present means ours, absent means webshop's.

**Lesson generalizes:** When overriding any webshop / payments / erpnext stock page, our local module name MUST NOT collide with theirs OR we lose resolution silently.

**Receipt:** 2026-04-29. Initial implementation lived in `www/cart.{py,html}` and rendered webshop's "Your cart is Empty" page despite the route rule. Cache-clear + redis flush + bench restart didn't help. Renaming to `lt_cart` resolved it.

### `Address.address_display` is NOT a stored DB column — it's computed at render time and lives on the SO

Tried `frappe.db.get_value("Address", name, "address_display")` and got `OperationalError: (1054, "Unknown column 'address_display'")`. The Address doctype's `address_display` is a virtual/computed field that gets HTML-rendered at SO save time and stored on `Sales Order.shipping_address` (HTML string), not on `tabAddress` itself.

**Fix:** Read the components — `address_line1`, `address_line2`, `city`, `state`, `pincode`, `country` — and assemble inline.

**Lesson:** Verify field-as-DB-column before reading via `frappe.db.get_value`. Quick check: `frappe.get_meta("Address").get_field("address_display")` returns the field metadata; if `fieldtype == "Small Text"` with no DB column, it's computed. Or: just check the existing schema visually.

### Stripe PMC parent-child permissions — child configs require parent ownership

Tried to create a child PMC under both pre-existing parent configs on LT's account. Both rejected with `"Child configurations can only be created by the parent configuration's owner"`. The two pre-existing PMCs (`pmc_1RdVUoDfnlZQv66nVzkbi0JH` and `pmc_1R2KesDfnlZQv66nLj0Smbnn`) are platform-managed (created by Stripe internally when LT's account was provisioned), not LT-owned.

**Fix:** Create a new top-level PMC without specifying `parent` — that succeeds because LT IS the owner of the new config. Stripe accepts a top-level config that lives alongside the platform-managed ones.

**Lesson:** When a Stripe account inherits a default PMC from platform/account-creation, you can't modify it OR child it. Create your own top-level config. The Stripe documentation doesn't make this distinction obvious; trial revealed it.

### Customer dedup must handle the Lead-from-Contact case explicitly

The original `submit_guest_order` checked Contact Email → Contact → Dynamic Link → Customer. If no Customer link, it created a NEW Customer with a NEW Contact — orphaning any existing Contact (which often came from a previous /contact form Lead submission). Result: same email, multiple Customer records, broken one-source-of-truth.

**Fix:** Three-case branching:
1. Customer link exists → reuse (returning customer)
2. Contact exists but no Customer link → create Customer, attach Customer link to existing Contact, find any Lead linked to Contact and mark `status="Converted"` + back-fill `lead.customer`
3. No prior records → create both fresh

The Lead-from-Contact case is the load-bearing one for the "everything cascades" architecture GL named this session. Without it, every customer who fills /contact then /shop becomes an orphan.

**Receipt:** 2026-04-29. GL named the ambition: *"Everything should cascade. We should also be adding the customer information in contacts unless it's a duplicate."* The orphan hole would have shipped silently broken without GL's framing.

---

## 2026-04-29 (Stripe migration session) — Six things learned migrating Charges API → Checkout Sessions

### `/payment-success` upstream URL bug + guest 403 require route override

Frappe's `payments` app builds the post-charge redirect URL at `apps/payments/payments/payment_gateways/doctype/stripe_settings/stripe_settings.py:272`. When `redirect_to` is `None`, the code unconditionally appends `?redirect_to=None` (literal string "None") even when the URL already has `?`. The result is a malformed URL like:

```
/payment-success?doctype=Payment%20Request&docname=ACC-PRQ-...?redirect_to=None
                                                              ^ should be & not ?
```

The malformed second `?` mashes the redirect_to suffix into the docname value. AND — even with a clean URL — Frappe's bundled `payment_success.py` calls `frappe.get_doc("Payment Request", docname)` under the GUEST session, which 403s because Payment Request is restricted.

**Fix (don't patch upstream — `apps/payments/` is bind-mounted from a gitignored upstream clone):** Override the route in our app via `website_route_rules` in `hooks.py`, with our own `www/payment_success.py` that:
1. Strips any `?redirect_to=None` tail off `docname`
2. Verifies the linked `Integration Request` (or Stripe session) is `Completed` — proves the charge actually succeeded; defends against guessing PR names
3. Looks up the SO with elevated read perms (we never read PR as guest)
4. Redirects to `/thank-you?order=<so_name>`

**Receipt:** GL hit this 2026-04-29 with the bug-report URL `/payment-success?doctype=Payment%20Request&docname=ACC-PRQ-2026-00008?redirect_to=None` returning 403. Override pattern fixed it. See `apps/locally_twisted/locally_twisted/www/payment_success.py`.

### Frappe payments app uses legacy Charges API — every BBC client needs Checkout Sessions before customer-facing work

Frappe's `payments` app (`apps/payments/payments/payment_gateways/doctype/stripe_settings/stripe_settings.py:create_charge_on_stripe`) calls `stripe.Charge.create()` — the **legacy Charges API**. The `stripe-best-practices` skill explicitly says: "Never recommend the Charges API." Reasons:

- No 3DS / SCA support (will fail in EU; may fail with US issuers requiring 3DS)
- No dynamic payment methods (no Apple Pay, Google Pay, Link auto-injection)
- No fraud signals as rich as PaymentIntents

The customer-facing form Frappe ships (`/stripe_checkout`) is also a custom card UI that looks unbranded and erodes trust at point of payment. GL's reaction 2026-04-29: *"This looks unprofessional. I don't trust it."*

**Fix:** Bypass Frappe's payment_url entirely. Create a Stripe Checkout Session directly from our app and hand the customer the `checkout.stripe.com/c/pay/cs_test_...` URL. Customer sees Stripe's polished hosted page with their full UI: dynamic payment methods, security badges, real-time validation, "Powered by Stripe" footer.

**Pattern:** New `apps/locally_twisted/locally_twisted/payments/stripe_session.py` with `create_session_for_sales_order(...)`. Called from `submit_guest_order` after PR creation. Returns the hosted URL.

**For every future BBC client on Frappe**: do this BEFORE any customer-facing demo. The Frappe-bundled card form is too embarrassing to ship.

### Stripe CLI's `--api-key` flag bypasses login when CLI auth is blocked

Stripe CLI normally requires browser-based login + 2FA via `stripe login`. For LT, Jeff's phone holds the 2FA — not always reachable when GL needs to test. Workaround: `stripe listen --api-key <sk_test_...>` accepts the secret key directly and bypasses the stored auth entirely.

**Pattern that works:**
```bash
export STRIPE_LT_KEY=$(grep '^STRIPE_TEST_SECRET_KEY=' .env | sed 's/^STRIPE_TEST_SECRET_KEY=//')
stripe listen --api-key "$STRIPE_LT_KEY" --forward-to http://localhost:8081/api/method/locally_twisted.payments.stripe_webhook.stripe_webhook
```

The listener prints `whsec_...` on the second line. Pass that to `scripts/setup/set_stripe_webhook_secret.py whsec_<value>` to persist in `site_config.json`. Restart backend.

**Caveat:** the secret rotates each time the listener restarts. So this is for dev convenience, not a stable production webhook. For prod, use Stripe Dashboard → Webhooks → Add endpoint, get the stable signing secret.

**Receipt:** 2026-04-29. The CLI's stored auth was BBC's (and BBC's test key had expired). Fresh login to LT's account was blocked by 2FA. The `--api-key` flag let us point the listener at LT's account using the secret key already in `.env`.

### Webhook signing secret belongs in `site_config.json`, not Stripe Settings doctype

Per-environment values that should NEVER travel between dev/staging/production live in `site_config.json`. Doctypes get backed up + restored across sites; `site_config` does not. The Stripe webhook secret for the local dev listener is different from the one Stripe Cloud will issue for production.

**Pattern:** `frappe.conf.get('stripe_webhook_signing_secret')` reads from `site_config.json` at the site root. Setup helper at `scripts/setup/set_stripe_webhook_secret.py` writes via `bench --site frontend set-config`.

This was a deliberate choice over adding a Custom Field to Stripe Settings. Custom Fields are fixtures that travel; `site_config` is per-site by design.

### Server-side reconciliation on `/payment-success` keeps the demo working without webhooks

The customer-facing flow can mark the SO/PR Paid synchronously when the customer's browser lands on `/payment-success?session_id=...` — using `stripe.checkout.Session.retrieve()` to verify `payment_status == 'paid'`, then calling `pr.set_as_paid()`.

This makes the webhook **optional** for demo purposes. The webhook handler still exists (and is signature-verified, idempotent) for production where it's the safety net for browser-closed-before-redirect cases. Whichever path fires first marks the PR Paid; the second path no-ops.

**Trade-off accepted:** if the customer closes their browser between Stripe success and our redirect, the SO won't be marked Paid until the webhook fires. For LT's controlled-demo and small-customer-volume situation, that's fine. For a high-volume e-commerce build, the webhook should be the source of truth.

### "I had it backwards" — the .env keys are the auth, the CLI is separate

Twice this session I asked GL for credentials they'd already provided. The .env file's `STRIPE_TEST_PUBLISHABLE_KEY` + `STRIPE_TEST_SECRET_KEY` ARE LT's authentication for ERPNext's Stripe integration. The Stripe CLI's stored auth (visible via `stripe config --list`) is a SEPARATE auth context for the listener tool.

**Lesson for the next instance:** before asking GL for credentials, check (a) `.env` for service-side keys, (b) `stripe config --list` for CLI auth, (c) `bench --site frontend execute frappe.client.get_value` against Stripe Settings. If something is already there, don't ask GL to redo it.

GL named this directly: *"I've already done this authentication!"* — the second time. Anti-pattern #5 fired on top of #5: don't make GL prove they've done something.

---

## 2026-04-29 (mobile-drawer build) — `web_include_css` browser-cache trap

### What happened

Edited `lt-theme.css` to add a mobile drawer overlay (drawer + backdrop + body scroll lock). Server-side everything was correct: `curl /assets/locally_twisted/css/lt-theme.css` returned the new content with `Last-Modified` set to the edit time. Playwright (fresh browser context, no cache) rendered the page perfectly — drawer hidden on desktop via `position: fixed; visibility: hidden; transform: translateX(100%)`.

But on GL's actual browser, the drawer rendered as inline content on **every page**, on desktop. The "Menu" heading, X close button, and all 7 nav links appeared in normal page flow below the desktop nav.

### Why

`web_include_css` injects a static URL (`/assets/locally_twisted/css/lt-theme.css`) with no version query string. Nginx serves it with `Last-Modified` and `ETag`, so a polite browser should revalidate — but in practice, Chromium-family browsers cache aggressively and serve stale CSS for hours-to-days unless explicitly forced.

When GL navigated to a page after the edit:
- The HTML was fresh (Frappe templates are server-rendered per request) → new drawer markup loaded
- The CSS was cached (browser served the old `lt-theme.css`) → no `position: fixed` rule for `.lt-header__mobile-nav-collapse` → drawer fell into normal document flow

The new HTML + old CSS combination is the worst case: the user sees the new structure rendered with the old (or missing) styles. This is invisible to Playwright (fresh context, no cache) and to `curl` (always fetches fresh) — only a real long-lived browser session reproduces it.

### What to do differently

**Standing rule:** every edit to `lt-theme.css` requires a bump to the `?v=` query string in `hooks.py`'s `web_include_css` line. Format: `YYYYMMDD-N`.

Current line:
```python
web_include_css = "/assets/locally_twisted/css/lt-theme.css?v=20260429-1"
```

Each edit → bump the version. Each version bump → backend restart (`docker restart locally-twisted-erpnext-v15-backend-1`) so Frappe re-reads `hooks.py`. The query string change forces every browser to fetch fresh CSS the next time the page loads — no hard-refresh needed by the user.

### Verification gate (post-CSS-edit ritual update)

The existing operational ritual was:
> Edit Jinja / CSS / Web Page record → `python scripts/dev/clear_website_cache.py`

That clears server-side template cache but does NOT bust browser caches. Updated ritual:
1. Edit `lt-theme.css`
2. Bump `?v=` in `hooks.py`
3. `docker restart locally-twisted-erpnext-v15-backend-1 && sleep 8`
4. `python scripts/dev/clear_website_cache.py`
5. Verify in a fresh-incognito Playwright AND in GL's actual browser before declaring done

Without step 2, GL's browser will serve stale CSS even though the server-side file is current. This pattern bit us 2026-04-29 with the mobile drawer overlay.

### Belt-and-suspenders option (deferred)

A more durable fix: compute the version dynamically from the file's mtime in `hooks.py`. Sketch:
```python
import os
_THEME = os.path.dirname(os.path.abspath(__file__)) + "/public/css/lt-theme.css"
_V = int(os.path.getmtime(_THEME)) if os.path.exists(_THEME) else 0
web_include_css = f"/assets/locally_twisted/css/lt-theme.css?v={_V}"
```

Pro: no manual bump, no rule to remember. Con: needs to be tested against Frappe's hooks.py loader (does it tolerate computed values? do containers see the right file path?). Park as a future cleanup once the manual rule has lived through enough sessions to confirm it's reliable.

---

## 2026-04-29 (Stripe wiring + true guest checkout session) — Five Frappe internals discovered

### Frappe Payment Request `payment_url` is gated behind `send_mail` — manual call required when suppressed

`Payment Request.on_submit` (apps/erpnext/...accounts/doctype/payment_request/payment_request.py:215) calls `set_payment_request_url()` ONLY inside the `if send_mail and self.payment_channel != "Phone":` branch. `send_mail` becomes False when EITHER `ref_doc.order_type == "Shopping Cart"` OR `self.flags.mute_email = True` (line 211). Both are necessary for guest checkout — but they ALSO suppress the URL-generation call.

**Fix:** after `pr.submit()`, call `pr.set_payment_request_url()` manually then `pr.reload()`. See `apps/locally_twisted/locally_twisted/www/checkout.py` for the working pattern.

**Receipt:** smoke test #3 (URL Test customer, since cleaned). After fixing wkhtmltopdf error, `payment_url` came back None. Traced to `set_payment_request_url` not being called. Manual call populated it correctly.

### wkhtmltopdf inside the Frappe Docker container can't reach localhost:8081

Anywhere Frappe auto-renders a PDF inside the running container — `attach_print()`, Sales Order print formats, Payment Request emails — wkhtmltopdf is invoked and tries to fetch CSS/assets from the site's public URL. Inside the container's network namespace, `localhost:8081` doesn't resolve. Result: `OSError: wkhtmltopdf reported an error: Exit with code 1 due to network error: ConnectionRefusedError`.

**Workaround for Payment Request:** set `Sales Order.order_type = "Shopping Cart"` AND `payment_request.flags.mute_email = True` BEFORE `pr.submit()`. Both checks are at `payment_request.py:211`. Either alone may not be enough.

**Long-term fix (deferred):** configure `host_name` in `site_config.json` to a docker-internal hostname (e.g., `http://frontend:80`) so wkhtmltopdf can reach back to the site from inside the network. Future hardening item.

**Receipt:** smoke test #2 (Trace Test, since cleaned). Got the full traceback chain: `Payment Request on_submit → send_email → attach_print → pdfkit.to_pdf → wkhtmltopdf → ConnectionRefusedError`.

### `Contact.links` is a child table, NOT a column — query Dynamic Link directly

`Contact` has a `links` field that looks like a column in Customize Form, but it's a Table-fieldtype (child of Contact). Querying `frappe.db.get_value("Contact", ..., ["links"])` errors with `pymysql.err.OperationalError: (1054, "Unknown column 'links' in 'SELECT'")`.

**Fix pattern for Contact → Customer lookup:**
```python
contact_name = frappe.db.get_value("Contact Email", {"email_id": email}, "parent")
if contact_name:
    customer_name = frappe.db.get_value(
        "Dynamic Link",
        {"parent": contact_name, "link_doctype": "Customer", "parenttype": "Contact"},
        "link_name",
    )
```

Same pattern applies to any parent doctype's Table fields — query the child table by `parent` field, not the parent's "column."

**Receipt:** first guest-checkout smoke test failed with the Unknown column error. Fix is in `checkout.py:292-302` with comments.

### Stripe Settings auto-creates the entire payment chain on insert

Inserting a `Stripe Settings` record with `gateway_name`, `publishable_key`, `secret_key` triggers ERPNext's `on_update` hook which auto-creates:
- Payment Gateway named `Stripe-{gateway_name}` (e.g., `Stripe-Test`)
- Bank Account named `Stripe-{gateway_name} - {company_abbr}` (e.g., `Stripe-Test - LT`) — Currency = company default
- Payment Gateway Account linking the gateway to the bank account, marked default

You don't need to create any of those manually. Just insert the Stripe Settings → wire `Webshop Settings.payment_gateway_account` to the auto-created PGA name → done. Pattern codified in `scripts/setup/configure_stripe_test_mode.py`.

**Receipt:** session 2026-04-29. Wrote configure_stripe_test_mode.py expecting to need follow-up scripts for PG / PGA / Account creation. None needed — all four records existed after one insert.

### Webshop checkout requires `payment_gateway_account` set OR `enable_checkout=1` won't stick

`Webshop Settings.enable_checkout = 1` set via `frappe.client.set_value` silently reverts to 0 if `payment_gateway_account` is null. The save validator quietly rejects the change. Set both fields in the same `set_value` call (with the multi-field `fieldname` dict format) and both stick.

**Pattern:**
```python
frappe.client.set_value(
    doctype="Webshop Settings",
    name="Webshop Settings",
    fieldname={
        "payment_gateway_account": "Stripe-Test - USD - LT",
        "enable_checkout": 1,
    },
)
```

**Receipt:** session 2026-04-29. First attempt set only `enable_checkout=1`, saved silently, value was still "0" on read-back. Second attempt set both fields together — both took.

---

## 2026-04-28 (BTFP restructure + ribbons + font weight + color session) — Three CSS gotchas

### DM Serif Display is a single-weight font (400 only) — never override `font-weight` on heading classes

The brand serif at `https://fonts.googleapis.com/css2?family=DM+Serif+Display` has only the default cut. Setting `font-weight: 600` on `.lt-faq h1`, `.lt-faq__group-title`, `.lt-policy h1`, `.lt-policy h2`, etc. produces synthetic-bold (faux-bold) rendering — chunky, heavy, unrefined.

**Fix:** remove `font-weight: 600` from any class that targets a heading (h1/h2/h3) which inherits the global `h1, h2, h3 { font-family: 'DM Serif Display'; font-weight: 400; }` rule. Want emphasis? Use SIZE not WEIGHT (e.g., bumped FAQ group titles from 1.25rem → 1.5rem after removing the weight override).

`font-weight: 600` IS valid on Raleway-based classes (`.lt-faq__link`, `.lt-policy__link`, `.lt-faq__answer strong`) — Raleway has real 600. The rule is heading-class-specific.

**Receipt:** GL flagged the chunky look on /faq + /refund-policy. Comparing to BTFP intro h1 (no override → elegant) confirmed the cause. Fix landed in `faq.py` and `refund_policy.py` 2026-04-28.

### CSS `margin: 0` (shorthand) defeats `.lt-fullbleed` negative margins

`.lt-fullbleed` (in lt-theme.css) uses:
```css
margin-left: -50vw;
margin-right: -50vw;
```

Any rule with `margin: 0` or `margin: <something>` (the shorthand) wipes out the negative margins because shorthand sets all four sides. Result: the section stops at the parent container's edge instead of going edge-to-edge.

**Fix:** when defining a class that needs to coexist with `.lt-fullbleed`, use specific properties (`margin-top: 0; margin-bottom: 0;`) instead of the shorthand. Or just not set vertical margins at all.

**Receipt:** GL flagged "the ribbon containers that are thin and supposed to go across the whole page dont." The blush + soft-blue ribbons had `.lt-btfp__ribbon { margin: 0 }`. Replaced with specific top/bottom margins; ribbons span full width.

### `--lt-near-white` was too cold (#FBFBFB read as bluish-grey) — bumped to #fffcfc

GL: *"the main white background is so white it's bluish and/or gray... Try fffcfc for the main background."* Updating the CSS custom property at `:root { --lt-near-white: #FBFBFB }` → `#fffcfc` makes the body, BTFP booking section, and (later) the footer copyright bar feel warm rather than cold. `#FFFFFF` (the `--lt-white` token, used on cards and contrasted panels) stays unchanged for visible contrast.

**Pattern lesson:** `--lt-near-white` is the new "base white" token across the site. When choosing between `--lt-white` and `--lt-near-white` for a background, pick `--lt-near-white` for surfaces that should feel calm/quiet and `--lt-white` for surfaces that need to pop against the surrounding bands.

---

## 2026-04-27 (small-shop seed session) — Six webshop gotchas

### `upload_file` API does NOT auto-write the file_url to the parent doc's field

Called Frappe's `/api/method/upload_file` endpoint with `doctype=Item`, `docname=<slug>`, `fieldname=image`, `is_private=0` and got back a valid `{"file_url": "/files/<slug>.png"}` response. **The File record was created** with `attached_to_doctype=Item`, `attached_to_name=<slug>`, `attached_to_field=image`. **But `Item.image` stayed null.**

**Why:** the upload endpoint creates the File attachment record but does NOT write the file_url back into the parent doc's named field. Two separate operations.

**Fix:** explicit `frappe.client.set_value` call after upload — `Item.image = file_url`. AND for storefront display, also set the **separate** `Website Item.website_image` field (Item.image and Website Item.website_image are independent in v15).

**Receipt:** Seed script ran successfully, 33 File records created with the right attached_to_field, but the storefront showed empty placeholder boxes ("NB", "GG" letter avatars). Auditing Item records showed all 33 with `image: None` despite the File records existing.

### Webshop is OFF by default — `Webshop Settings.enabled = 0`

Fresh install of `frappe/webshop` ships with the storefront effectively disabled. **All these critical fields default to 0:** `enabled`, `show_price`, `show_stock_availability`, `enable_field_filters`, `enable_attribute_filters`, `enable_checkout`, `enable_wishlist`, `enable_reviews`, `allow_items_not_in_stock`. **And `price_list` defaults to None.**

**Fix:** explicitly set every field that matters BEFORE expecting browse / price-display / cart to work. Minimum to get a browseable shop with prices:
```
enabled = 1
show_price = 1
allow_items_not_in_stock = 1   # required for non-stock (made-to-order) items
products_per_page = 12         # default 0 = silently broken
price_list = "Standard Selling"  # default None = no prices visible
default_customer_group = "Individual"
enable_checkout = 1            # otherwise "Add to Quote" instead of "Add to Cart"
```

**Receipt:** Created 33 Website Items with `published=1`. /all-products rendered exactly 2 of them with no prices. Spent multiple turns chasing pagination + permission filter theories before discovering Webshop Settings.enabled=0 was silently filtering the entire result set in `add_display_details`.

### Webshop's whitelisted method path is `webshop.webshop.api.*`, not `webshop.api.*`

Folder layout: `apps/webshop/webshop/webshop/api.py`. Frappe convention says this Python module is `webshop.webshop.api`. The compiled JS bundle correctly calls `frappe.call({method: "webshop.webshop.api.get_product_filter_data"})`. **But intuitively the path "looks like" it should be `webshop.api.*` — and that's wrong.**

Calling `webshop.api.get_product_filter_data` returns HTTP 417 EXPECTATION FAILED with `ValidationError: Failed to get method ... with No module named 'webshop.api'`.

**Pattern:** Frappe apps double-namespace. The `<app_name>` Python package contains a `<app_name>` sub-module containing the module files. So `<app>.<module>.<file>` is the import path, even when `<app> == <module>`.

**Receipt:** Spent a turn convinced the JS was calling the wrong path because my direct curl was getting 417. The JS was correct; my curl was wrong.

### Frappe's `body { display: flex; height: 100vh; overflow-y: auto }` defeats Playwright `full_page=True`

The webshop pages set the body to a fixed-height flex container with internal overflow-scroll. **Playwright's `full_page=True` only captures `documentElement.scrollHeight`, which on these pages = viewport height = 800px** — even though the actual content (product grid) extends thousands of pixels below.

The user experience is fine: customers scroll inside the page body and see all the products. **But if you screenshot at the default 1280�-800 viewport and trust what you see, you'll declare the shop "broken" when only the first row visible.**

**Fix when verifying with Playwright:** use a tall viewport (`viewport={"width": 1280, "height": 3500}`). The DOM still renders identically; the viewport just captures more in the screenshot.

**Receipt:** Spent two iterations debugging "only 2 items render" before checking `body.offsetHeight` (= 800) vs `#products-grid-area.offsetHeight` (= 2707). 12 items WERE rendered, just below the captured frame.

**Pattern:** Always probe `document.documentElement.scrollHeight` AND the children's heights before trusting a Playwright screenshot's "what's missing" implication. Add the height probe to the standard verification preamble.

### Setting `Item.standard_rate` auto-creates an Item Price — explicit Item Price insert hits a duplicate-detection exception

When inserting an Item via `frappe.client.insert` with `standard_rate` populated, ERPNext's Item controller auto-creates a corresponding Item Price record (under "Standard Buying" by default, or "Standard Selling" for sales-only items). A subsequent explicit `Item Price` insert for the same item + price list raises `ItemPriceDuplicateItem` (HTTP 417), which is NOT caught by the standard `"already exists" / "DuplicateEntryError"` patterns.

**Fix:** expand idempotency-detection in any seed script to ALSO catch `ItemPriceDuplicateItem` and `"appears multiple times"`. Or skip the explicit Item Price insert entirely when standard_rate is set on the Item.

**Receipt:** First seeder run blew up at item #1 with HTTP 417 because of the duplicate. Patched the idempotency check, re-ran, succeeded.

### Webshop initial render goes through AJAX, not server-side Jinja

The `/all-products` page's index.html is empty for products (just `<div id="product-listing"><!-- Rendered via JS --></div>`). The JS in `index.js` instantiates `webshop.ProductView` which calls `frappe.call({method: "webshop.webshop.api.get_product_filter_data"})` and renders results client-side.

**Implication for verification:** `curl http://localhost:8081/all-products | grep <product-name>` returns nothing — products are not in the server-rendered HTML. Use Playwright with `wait_until="networkidle"` to capture post-JS state.

**Implication for SEO:** the storefront is JS-rendered, which is bad for crawlers without execution. If SEO matters for the small shop, server-side rendering of the first batch is a future concern. Out of scope for v1.

---

## 2026-04-27 (homepage build session) — Five gotchas + two reusable patterns

### Frappe Python module cache is sticky — restart backend after editing `www/<route>.py`

Edited `home.py` PAGE_CSS expecting the next `clear-website-cache` to refresh the served HTML. It did NOT. The HTML markup updated but the inline `<style>` block (injected via `context.colocated_css`) kept serving the OLD CSS.

**Why:** Frappe imports `www/home.py` once per Python worker process, then caches the module. `bench --site frontend clear-cache` clears Frappe's render cache, but doesn't reload Python imports. Editing the .py file means the running gunicorn worker still holds the old module in memory.

**Fix:** `docker restart locally-twisted-erpnext-v15-backend-1` — that bounces the gunicorn workers and forces re-import on next request. Sleep 8s for the container to come up, then test.

**Receipt:** Spent a turn confused why `lt-fullbleed` wasn't visibly working. `curl localhost:8081/ | grep "@keyframes lt-hero-cycle"` showed 0 matches (the v2 keyframes weren't in the served HTML). Restart fixed it immediately.

**Pattern:** Whenever PAGE_CSS or any Python data structure changes in a `www/` controller, the cycle is: edit → `docker restart <backend>` → `clear-website-cache` → test. Template-only changes (just HTML) re-render on next page hit; controller changes need the restart.

### Web Page DocType records compete with `www/` files for the same route

Visited `/` after creating `home.py` + `home.html` and got the prior "Site under construction" placeholder, NOT my new homepage. Diagnosed via SQL: `SELECT name, route, published FROM \`tabWeb Page\` WHERE route IN ('home');` → returned name="locally-twisted", route="home", published=1.

**Why:** Website Settings.home_page = "home". When `/` resolves, Frappe looks for a route named "home" via multiple resolvers. A published Web Page record AND a `www/home.html` file both claim that route. The Web Page record won.

**Fix:** `UPDATE \`tabWeb Page\` SET published = 0 WHERE name = 'locally-twisted';` — deactivates the placeholder. The www/home.html file then takes precedence.

**Pattern:** Before creating any new `www/<route>.<py|html>` file, check if a published Web Page record already claims that route. If yes, decide: (a) deactivate the Web Page record (cleanest), (b) move the Web Page content into your www/ template, (c) pick a different route. Don't assume www/ wins by default — it depends on Website Settings.home_page and which resolver runs first.

### Frappe full-bleed pattern — `width: 100vw` + `margin-left: -50vw` breaks out of the parent .container

Bands rendered as colored stripes inside the centered content column, leaving white margins on left and right (GL's "Image #5" complaint about banners cut off). The `templates/web.html` parent wraps content in a `.container` with max-width that constrains everything inside.

**Fix:** A `.lt-fullbleed` modifier class:

```css
.lt-fullbleed {
    width: 100vw;
    position: relative;
    left: 50%;
    right: 50%;
    margin-left: -50vw;
    margin-right: -50vw;
}
```

Applied to `<section>` elements that should read as full-width bands (hero, reviews, featured, crawl, CTA, twisting spotlight). Inside each section, an inner `.lt-<block>__inner` div with `max-width: 1200px; margin: 0 auto;` keeps content readable.

**Receipt:** The first homepage v2 deploy showed bands visibly constrained. Adding `.lt-fullbleed` to 6 sections fixed it without touching the parent template.

**Pattern:** This is the standard CSS technique for "break out of a constraining parent container." Document it in the meal — every BBC client's portal pages have the same parent.container constraint.

### CSS-only cycling content (hero headlines, blog post titles, etc.) — staggered animation-delay on absolutely-positioned children

GL wanted the hero headline to cycle through blog post titles while a stable tagline stays put underneath. Implemented with pure CSS (no JS):

```css
.lt-hero__cycling { position: relative; min-height: 4.4rem; }
.lt-hero__title {
    position: absolute; inset: 0;
    opacity: 0;
    animation: lt-hero-cycle 32s infinite;
}
.lt-hero__title:nth-child(1) { animation-delay: 0s; }
.lt-hero__title:nth-child(2) { animation-delay: 8s; }
.lt-hero__title:nth-child(3) { animation-delay: 16s; }
.lt-hero__title:nth-child(4) { animation-delay: 24s; }
@keyframes lt-hero-cycle {
    0%   { opacity: 0; }
    3%   { opacity: 1; }
    22%  { opacity: 1; }
    25%  { opacity: 0; }
    100% { opacity: 0; }
}
@media (prefers-reduced-motion: reduce) {
    .lt-hero__title { animation: none; opacity: 0; }
    .lt-hero__title:nth-child(1) { opacity: 1; }
}
```

**First-paint gotcha:** at t=0 the keyframe is at 0% which is opacity 0. Title 1 invisible until 1s into the cycle. Solutions: (a) negative `animation-delay: -1s` on title 1 to start mid-cycle, or (b) live with the 1s fade-in delay (current state — Playwright captures show title 1 visible by the time `wait_until="networkidle"` fires).

**Pattern:** Reuse for any cycling content where one stable element + one rotating element is the desired UX (testimonials, blog teasers, mood-to-quote in lookbook). Total cycle = N �- per-title duration; staggered delays = full duration / N.

### Carousel of cards — same CSS marquee pattern as text crawl, just bigger items

GL pivoted reviews from 5-inline-cards to a horizontal-scrolling carousel of all 19 reviews. Reused the existing `.lt-crawl` pattern verbatim, swapping text spans for full review cards:

- Outer viewport: `overflow: hidden; mask-image: linear-gradient(...);` for edge fade
- Track: `display: flex; gap: 1rem; width: max-content; animation: scroll Ns linear infinite;`
- Items: `flex: 0 0 320px;` (fixed card width, no shrink)
- Track has duplicate set (aria-hidden) for seamless loop
- `.viewport:hover .track { animation-play-state: paused; }` for reading-on-hover
- Original `prefers-reduced-motion` behavior fell back to flex-wrap (cards
  stack), but that was superseded on 2026-05-07 for homepage proof crawls:
  they now stay slow, moving, horizontal, and scrollbar-free in the reduced
  branch.

**Speed scaling:** text crawl = 270s for 54 names; card carousel = 360s for 19 cards. Cards are bigger and need reading time.

**Pattern:** Same primitive can do client-name marquee, review-card carousel, photo-strip carousel, etc. Worth a recipe (kitchen note dropped at agency-tier capabilities).

### `git status` showed 6 deleted `_oneshot_*` files persisting from prior session — auto-commit hook handles writes, not deletions

The git status at session start showed 6 ` D ` (working-tree-deleted, unstaged) entries from prior session's cleanup. These weren't blocking but they made `git status` noisy.

**Why:** the auto-commit hook fires on Write tool calls. Deletions via filesystem don't trigger it. Net effect: deleted files stay as unstaged deletions until someone commits them explicitly.

**Pattern:** If a session ends with stale ` D ` entries in git status, that's not a leak — but worth a cleanup commit if doing housekeeping. Otherwise the next instance will see them too.

---

## 2026-04-26 (codification + chrome + accessibility + contact + BTFP session) — Five gotchas worth carrying forward

This session shipped four real surfaces (chrome, accessibility, contact, BTFP) and one meal. Five gotchas hit during the work, each with a verified receipt. All five are now codified in `Built_by_Cameron/.claude/capabilities/meals/build-frappe-portal-page.md` "Known gotchas" section so the next instance doesn't rediscover.

### Frappe `www/` does NOT auto-translate underscored filenames to dashed URLs

A controller named `<app>/www/balloon_twisting_and_face_painting.py` serves at `/balloon_twisting_and_face_painting`, NOT at `/balloon-twisting-and-face-painting`. Python module names cannot have dashes; URLs typically should. Bridge the two with `website_route_rules` in `hooks.py`. After editing hooks.py: cache clear is not enough — also flush Redis and restart the backend; the route map caches aggressively.

### Frappe's website bundle has direct `<p>` rules that override inherited text-align

Setting `text-align: center` on a parent section does not reliably reach `<h1>` / `<p>` children — Frappe's bundle has direct selectors at higher specificity. Direct selectors always beat inherited values regardless of cascade order. **Fix:** declare `text-align: center` directly on each text-bearing block via its BEM class. This bit twice in the same session (footer brand block, BTFP intro lede); same pattern, same fix.

### Webshop's CSS/JS bundles need `bench build` (Node + yarn required)

`webshop/hooks.py` registers `web_include_css = "webshop-web.bundle.css"` + `web_include_js = "web.bundle.js"`. Without `bench build`, those bundles aren't compiled, `assets.json` lacks the entries, Frappe falls back to bare paths, browsers 404. Worse: `web.bundle.js` defines the global `webshop` JS namespace; without it, `/all-products` throws `Uncaught ReferenceError: webshop is not defined`. The frappe_docker production image has no Node, BUT Node v20 is available via nvm at `/home/frappe/.nvm/versions/node/v20.19.2/`. Symlink it into `/usr/local/bin` so `/bin/sh` subprocesses (which `bench build` uses) find it. Same for yarn (install via `npm install -g yarn`). All wrapped in `scripts/setup/install_webshop.py --build-assets` for reproducibility after container recreation.

### Lead Source records don't exist on a fresh ERPNext install

`Lead.source` is a Link to `Lead Source`. On a fresh install, that DocType has zero records. Setting `source="Website"` raises `LinkValidationError`. Fix: idempotently create the source before creating the Lead (`frappe.db.exists` + try-`insert` with `ignore_if_duplicate`). Caught at the LT contact-page first smoke test before GL ever saw it. The same pattern applies to any Link-field default: ensure-or-create the linked record before creating the parent.

### Browser cache + `web_include_css` files

Files registered via `web_include_css` serve via the symlink chain. Their `Last-Modified` and `ETag` update on edit, but Brave (and other browsers) sometimes don't re-validate within a session. Visual symptom: page shows a mix of old and new CSS rules; new BEM classes look unstyled (logo at native size, lists with bullets, no flex). DevTools Network shows the file from cache. **Fix:** hard-refresh (`Ctrl+Shift+R`). **For the meal:** ALWAYS include "hard refresh" in the handoff to GL when shipping a CSS-touching change. Saves a confused round-trip.

### Generalizable lesson promoted to agency-tier

Each of these is now in the meal's "Known gotchas" section with a receipt. The next instance reading the meal sees them as patterns-to-anticipate, not patterns-to-rediscover.

---

## 2026-04-26 (codification session) — `extend_doctype_class` is NOT consumed by Frappe v15

External research (Magic Research / `frappe-erpnext-non-gpl-hooks-comparison.md`) recommended preferring `extend_doctype_class` over `override_doctype_class` for "lower-conflict" coupling. Verified against running Frappe v15 source: `grep -rn 'extend_doctype_class' apps/frappe/` returns NO consumer in Frappe core. The Payments app declares `extend_doctype_class = {"Web Form": "..."}` in its `hooks.py`, but Frappe never reads that hook key — Payments' actual Web Form behavior change comes through `override_whitelisted_methods` instead.

**Generalizable lesson:** verify external research against the running source before codifying. If GL hadn't asked for it to be codified at agency tier, this wrong claim could have led the next instance to declare a hook that does nothing. The verify-against-source rule worked — it caught a 95%-correct external research piece's one wrong claim. Codified at `Built_by_Cameron/.claude/capabilities/recipes/license-isolated-app-architecture.md` "Corrections from source" section.

---

## 2026-04-26 (session end) — TWO consecutive landing-page failures share one pattern: invent + band-aid + claim-done-off-DOM-facts

**What happened:** This session's instance built a landing page using `Web Page` content_type=Page Builder with 4 default Web Templates. The build looked complete from DOM facts (curl showed all sections rendered, Playwright captured a 1366�-3818 screenshot, all the section IDs and class names were present). The instance reported it as "tier 1 native" and ready for review. GL opened the page in their actual browser. **It wasn't visible. It wasn't responsive. The copy was made-up.**

**Root cause is now nameable:** Both this session's failure AND the prior Slice 2 failure share the same anti-pattern:
1. **Invent placeholder copy** instead of pulling from the approved Odoo XML / live site source
2. **Use band-aid CSS** (`!important` chains in the prior session; default Page Builder template + thin theme CSS in this session) instead of using the framework's intended override surfaces
3. **Declare done off DOM facts** (the DOM has the elements; the page must be working) instead of verifying GL can see the rendered output in a real browser at multiple viewport widths

**The architectural primitives weren't the problem.** Web Page DocType + Page Builder + custom Frappe app + web_include_css are all valid Frappe paths. They CAN produce a working result. They DID NOT, twice in a row, because the technique inside the architecture was wrong.

**What the third instance must do differently:**
1. **Source content from the Odoo XML or live locallytwisted.com — never invent.** Documented as a standing decision this session.
2. **GL's eyes on the actual page > any DOM fact.** A successful Playwright capture is a precondition, not a verdict. GL opens the page on their phone and their laptop and confirms. THEN it's done.
3. **Match GL's STYLE-GUIDE.md visual identity.** Not "looks roughly right." The brand foundation has specific fonts, colors, spacing. Slop fails.
4. **Mobile-first verification.** 375px viewport BEFORE 1366px desktop. If it doesn't work on mobile, it isn't done — Jeff's customers use phones.
5. **The platform-direction decision (custom Jinja vs decoupled vs Frappe Builder) is GL's call, made consciously.** Don't presume Frappe is the answer because you arrive in a Frappe codebase. The expedition synthesis is the briefing.

**Generalizable lesson promoted to agency tier:** This is a specific case of the broader "verify with reality, not with claims" anti-pattern in the global `anti-gl-patterns.md`. The LT-specific receipts are now in this file's 2026-04-26 (Slice 2 build) entry AND this entry. Two strikes. The third instance must break the pattern.

---

## 2026-04-26 (Jinja override path validation) — The override DOES resolve in our Docker bind-mount setup

**What happened:** Two prior HANDOFFs claimed "override Jinja partials at `apps/locally_twisted/locally_twisted/templates/includes/footer/footer.html`" was the path forward for Slice 2. Nobody had verified the override actually resolved in our specific bench setup. This session: dropped a minimal test file with a visible string, cleared cache, fetched the home page, confirmed the test string appeared in served HTML.

**Verified working:**
```
apps/locally_twisted/locally_twisted/templates/includes/footer/footer.html
```
Place a file at this path in our custom app. Frappe's template lookup resolves it before Frappe's standard footer at `apps/frappe/frappe/templates/includes/footer/footer.html`. Same pattern works for navbar and other Jinja partials.

**Required after creating/editing the override:** `python scripts/dev/clear_website_cache.py` — Frappe caches the resolved template path; the cache must be cleared for the override to take effect on next request.

**The test file was REMOVED after validation** — it was overriding the real Frappe footer with the test string, which is not what we want long-term. The next instance creates the real footer override only when ready to build the actual Slice 2 redo.

**Generalizable lesson:** When a HANDOFF claims an architectural path is "the way forward" but nobody has executed even the minimal version, the next instance MUST verify the path before building substantively on top of it. One test file proves the assumption (or surfaces a deeper problem to fix). The cost of the test is minutes; the cost of building on an invalid assumption is a session.

---

## 2026-04-26 (webshop install + framework study + Web Page tabs finding) — Read the DocType schema BEFORE planning custom code

**What happened:** The pricing calculator on the BTFP service page was planned as a "tier 4 custom Web Template" build — meaning we'd write a custom Jinja template + register it via hooks + extend it from a Web Page record. Three instances in a row independently classified it this way, including me when I wrote the v1 index. The calculator was treated as the "irreducibly custom code" piece that justified opting into tier 4.

GL surfaced the actual answer mid-session: *"the previous instance edited this page http://localhost:8081/app/web-page/locally-twisted by using the content field update, not the scripting tab where you can literally just add javascript. You can create webpages with javascript but the prior instance just filled in the content field and it made everything look bad — because they should have used java! You can use java on these pages!"*

I went and read the Web Page DocType schema (`apps/frappe/frappe/website/doctype/web_page/web_page.json`). It has these tabs natively:

| Tab | Field | What it natively supports |
|---|---|---|
| Content | `content_type`, `main_section`/`main_section_html`/`main_section_md`, `page_blocks` | Body layout (multiple input modes including Page Builder) |
| Script | `javascript` (Code field) | **Per-page JavaScript that runs at page load** |
| Style | `css` (Code field), `insert_style` (Check) | **Per-page CSS scoped to this page** |
| Header and Breadcrumbs | `header` (HTML), `breadcrumbs` (Code), `dynamic_template` | Custom hero HTML, breadcrumb logic |
| Settings | `show_sidebar`, `enable_comments`, `full_width` | Layout toggles |
| Meta Tags | `meta_title`, `meta_description`, `meta_image`, `dynamic_route` | Per-page SEO |
| Context | `context_script` (Code, Python) | **Server-side Python that runs BEFORE render — inject variables into the Jinja context** |

**The calculator collapses from tier 4 to tier 1:**
- Page Builder for static layout (H1, intro, FAQ accordion) → `page_blocks`
- HTML form inputs → an HTML block in Page Builder OR `main_section_html`
- Live price math → `javascript` field
- Calculator-specific styling → `css` field (with `insert_style=1`)
- No custom Web Template, no hooks, no app code, no Jinja overrides. Pure DocType configuration.

**What was learned (load-bearing for future client work):**

1. **DocTypes are the configuration surface, including for "code" things.** Frappe's Code-fieldtype fields (javascript, css, context_script) are configuration, not code-in-the-traditional-sense. They live in DocType records. They're versioned via fixtures. They survive cleanly across upgrades. Writing a custom Web Template to hold the same JavaScript is strictly worse: more files, more places to break, no benefit.

2. **The previous instance's mistake is fully named:** they used `main_section` (Rich Text) only. They didn't open the Script tab or the Style tab or use Page Builder. They didn't read the schema. They assumed the page surface was just "what `main_section` accepts." Then when they needed interactivity, they assumed they'd need to override a template — when in fact the right answer was already on the same DocType form, in a different tab.

3. **The general rule:** before reaching for a custom Web Template, custom hook, custom controller, or template override — **read the DocType's `.json` schema in the running container.** Frappe DocTypes have many more fields than the desk UI immediately surfaces. Tabs are collapsed by default. Code-fieldtype fields are easy to miss. The schema is authoritative; the form layout is just one view of it.

**Generalizable lesson promoted to agency-tier:** added a "Standing principle: System-native first" section at the top of `Built_by_Cameron/.claude/capabilities/recipes/frappe-conventions.md` — every BBC client benefits.

---

## 2026-04-26 (Slice 2 build) — Frappe / ERPNext quirks discovered while building the website shell

A pile of gotchas hit during a single session of building the navbar + footer + scaffolding the custom Frappe app. Each one bit, each one was band-aided rather than learned-from in the moment, each one is real. Logging here so the next instance doesn't rediscover.

### `bench new-app` license validator is case-sensitive (lowercase `mit`)

The CLI prompt says `App License [mit]:` and looks like it accepts free text — it does not. Click validates against the exact list `mit`, `agpl-3.0`, `apache-2.0`, etc. Pass `MIT` (uppercase) and `bench new-app` aborts with a validation error and creates nothing. Pass `mit` (lowercase) and it proceeds.

**Lesson:** when feeding answers via heredoc/stdin to `bench new-app`, use lowercase license values. The list is documented in the prompt itself.

### Top Bar Item parent rows cannot have a URL when they have child items

`Website Settings.top_bar_items` accepts a child table where dropdown structure is encoded by `parent_label`: items with `parent_label = "Foo"` become children of the parent row whose `label = "Foo"`. **Frappe validates that a parent row's `url` is empty when it has children.** Set `{label: "What We Make", url: "/shop"}` while having children with `parent_label: "What We Make"` and the API returns `ValidationError: What We Make in row N cannot have both URL and child items`.

**Lesson:** parent dropdown rows are pure triggers, not link destinations. `url=""` for the parent; children carry the actual destinations.

### Footer Items need explicit URL-less parent rows (column headers) defined within the same table

Same shape as `top_bar_items`. `Website Settings.footer_items` rendering as columns by `parent_label` requires the parent value to exist as its own row in the same list. Skip the parent rows and Frappe raises `ValidationError: Shop does not exist in row 1` for every child whose `parent_label` doesn't match an in-list row.

**Lesson:** before child rows like `{label: "All Products", parent_label: "Shop"}`, prepend an empty-URL row `{label: "Shop", url: ""}`. Frappe groups under that parent.

### Web Page `content_type` is a hidden field-router (HTML reads `main_section_html`, Rich Text reads `main_section`)

The `Web Page` DocType has multiple body-content fields and `content_type` selects which one renders. Set `content_type="HTML"` and Frappe renders from `main_section_html`. Set `main_section` instead — the page article renders **empty** with no error, no warning, no log entry. The page exists, the title appears, but the body is just `<article>...</article>` with nothing inside.

**Lesson:** `content_type="Rich Text"` is the safe default if you're putting raw HTML in `main_section`. Always verify with a `curl` of the served page after writing a Web Page record — the article tag should contain your content.

### Frappe HTML sanitizer strips inline SVG `<path d="...">` from CMS fields like `Website Settings.address`

Wrote inline SVGs with explicit path data (Instagram, Facebook, etc. social icons) into the `address` field's HTML. Curl of the served page showed `<svg viewbox="0 0 24 24"><path></path></svg>` — viewBox lowercased, every `d=` attribute stripped, the SVG visually empty. The sanitizer treats CMS fields as untrusted user input and removes attributes deemed risky for XSS.

**Lesson:** for any iconography or styled rendering inside CMS-editable fields, use one of these instead:
- CSS `background-image: url(...)` referencing a real SVG file in `apps/<app>/<app>/public/icons/icon.svg`. Class names on the `<a>` survive sanitization; the icon comes from CSS.
- Inline SVG only inside `head_html` or `body_html` (less sanitized) or a Web Template's Jinja (not sanitized at all).
- Font icons via class names if your app loads an icon font.

### `head_html` styles load BEFORE Frappe's bundled stylesheets in the cascade

Pushed the entire LT theme CSS as a `<style>` block in `Website Settings.head_html`. The block lands in the `<head>` very early. Frappe's `website.bundle.css` and `erpnext-web.bundle.css` `<link>` tags load *after* — meaning equal-specificity rules in those bundles win. `.web-footer { background-color: var(--lt-soft-blue); }` is silently overridden by `.web-footer { background-color: ...; }` in Frappe's bundle.

**Lesson:** `head_html` is a fallback / quick-prototype surface, NOT the production override surface. The right way to override theme CSS in a custom Frappe app is `website_theme_scss` in `hooks.py` plus an SCSS file at `<app>/<app>/public/scss/website.scss`. That gets compiled INTO the website bundle and wins at equal specificity (because it's the LATER file in the merged bundle). For static CSS that doesn't need SCSS compilation, `web_include_css` in `hooks.py` is also fine because that `<link>` tag injects after the bundled CSS.

### `data:image/svg+xml;utf8,...` data URIs silently fail to render in real browsers

Tried to bypass the sanitizer issue by encoding social-icon SVGs as CSS `background-image: url("data:image/svg+xml;utf8,%3Csvg ...")`. Several browsers (real Chromium, Firefox) silently rendered the circles with no icon — accepting the CSS without error, painting the gradient/color background, but failing to decode the SVG. The headless `chrome --screenshot` flag rendered it slightly differently than Playwright's full Chromium, so the breakage was invisible in our quick captures.

**Cause:** the prefix `;utf8,` is non-standard. Real spec is `data:image/svg+xml;charset=utf-8,...` or just `data:image/svg+xml,...`. Additionally, unencoded spaces inside the SVG path `d` attribute trip stricter parsers.

**Lesson:** when you need icons in CSS, use real SVG files in the app's `public/icons/` folder and reference them via plain `url("/assets/<app>/icons/<name>.svg")`. Encoding ambiguity gone. The files are also greppable, version-controllable, and reusable across rules.

### Frappe's navbar-toggler markup is `<svg><use href="#icon-menu"/></svg>`, not Bootstrap's `.navbar-toggler-icon` span

Wrote CSS targeting Bootstrap's standard `.navbar-toggler-icon` span class to skin the mobile hamburger. The class doesn't exist in Frappe's rendered navbar — Frappe outputs `<button class="navbar-toggler"><span><svg class="icon icon-lg"><use href="#icon-menu"/></svg></span></button>` and references an SVG sprite for the icon.

**Lesson:** to override the toggler icon, hide the inner `<span>/<svg>` and put the icon as a `background-image` on the button itself:

```css
.navbar-toggler { background-image: url("/assets/<app>/icons/menu.svg") !important; ... }
.navbar-toggler > span, .navbar-toggler svg { display: none !important; }
```

### Frappe auto-prepends `©` to the copyright field

Set `Website Settings.copyright = "© 2026 Locally Twisted · Accessibility · Refund Policy"`. Rendered output: `© © 2026 Locally Twisted · ...`. Frappe's footer template prepends a `©` glyph itself; supplying one in the field value gives you doubles.

**Lesson:** copyright field value should NOT begin with `©`. Start with the year.

### Editable pip install (`uv pip install -e <app>`) lives in container's writable layer; lost on `docker compose up --force-recreate`

After scaffolding the custom Frappe app inside the backend container with `bench new-app`, the editable Python package was registered via `uv pip install -e /home/frappe/frappe-bench/apps/locally_twisted` so `import locally_twisted` resolves and Frappe's hook system picks up `hooks.py`. Then a docker compose recreate (e.g., to apply a new bind-mount) destroyed the container's writable layer and the editable install with it. New container had the app's source via the bind-mount, but no `locally_twisted` in the Python env — every page rendered HTTP 500 with `ModuleNotFoundError: No module named 'locally_twisted'`.

**Lesson:** the editable pip install must be re-run after every container recreation, in EVERY frappe-image service that imports app code (backend, queue-long, queue-short, scheduler — websocket runs Node so doesn't need it). The clean long-term fix is to bake the install step into the `configurator` service's command in `pwd.yml` so it runs automatically on stack startup. **Until that's done**, treat container recreations like a manual checkpoint that requires:

```bash
for svc in backend queue-long queue-short scheduler; do
  docker exec "<project>-${svc}-1" \
    uv pip install -e /home/frappe/frappe-bench/apps/<app> --python /home/frappe/frappe-bench/env/bin/python
done
docker restart <project>-backend-1 <project>-queue-long-1 <project>-queue-short-1 <project>-scheduler-1
```

### `.web-footer`'s computed height "constraint" — RESOLVED 2026-04-26 (current session)

The previous instance reported `.web-footer`'s computed height was "mysteriously constrained to ~305 px" while its child `.container` was 755 px tall. This was logged as UNRESOLVED.

**Root cause from reading Frappe's actual source in the running container** (`docker exec backend cat /home/frappe/frappe-bench/apps/frappe/frappe/public/scss/website/footer.scss`): there is **no `max-height` rule on `.web-footer`**. The actual SCSS is:

```scss
.web-footer {
  padding: 3rem 0;
  min-height: 140px;
  background-color: var(--fg-color);
  border-top: 1px solid $border-color;
  margin-top: auto;
}
```

The `margin-top: auto` participates in Frappe's intended sticky-footer pattern: `apps/frappe/frappe/public/scss/website/base.scss` declares `html { height: 100% }` and `body { display: flex; flex-direction: column }`. The footer is the last flex child and `margin-top: auto` pushes it to the bottom of body when the main content is shorter than viewport. **This is not a bug — this is Frappe's intended layout.**

The previous "305 px constraint" observation likely came from one or more of:
1. The previous instance's own `lt-theme.css` `!important` chain on `.web-footer` interacting with the body's flex column in unexpected ways
2. Measurement confusion between multiple `.container` elements on the page (the header has a `.container` too; the previous DOM-fact dump may have grabbed the wrong one)
3. The page state at measurement time differed from what the screenshot rendered (cached CSS bundle, stale cookies, etc.)

**The right move forward** (per the agency `frappe-conventions.md` "Verified against source — 2026-04-26" appendix and per GL's directive "work WITHIN Frappe, don't fight it"):

1. Override the Jinja partial at `apps/locally_twisted/locally_twisted/templates/includes/footer/footer.html`. Your override resolves before Frappe's standard one. Use whatever class names you want — no inheritance from `.web-footer` necessary.
2. Strip the `!important` chains from `lt-theme.css`. They were band-aids around the wrong problem.
3. Use `web_include_css` (already wired in `hooks.py`) for the LT theme CSS — it loads AFTER the website bundle in cascade order, so equal-specificity rules win without `!important`.
4. For SCSS that needs Frappe's variables and to be compiled into the bundle, register `website_theme_scss` in `hooks.py` and create `apps/locally_twisted/locally_twisted/public/scss/website.scss`.

**Status: resolved.** Slice 2 redo can proceed using the right primitives; the framework was never the obstacle.

---

## 2026-04-26 — "Jeff doesn't know" needs more precision than the standing docs gave it

**What happened:** Inherited HANDOFF.md and CLAUDE.md framing that read, in effect, "Jeff Kimber doesn't know about the prior failed Odoo attempt; no artifact on disk should leak that." Operated under that assumption for the first part of this session. GL corrected the framing directly: Jeff knows about the Odoo attempt and has lived its failures over months of paid work. What Jeff does not yet know is that GL has decided to migrate infrastructure entirely to ERPNext. The hidden piece is the platform pivot, not the existence of the prior work.

**What was learned:**

1. **One-line summaries of trust dynamics lose load-bearing nuance.** "Jeff doesn't know about the prior Odoo attempt" is a paraphrase that erased months of paid work Jeff has been watching firsthand. A future instance reading the cleaner version might guard the wrong fact and either over-disclose (treating the prior work as something to confess) or under-disclose (acting in conversation as if Odoo never existed, which would be jarring against Jeff's actual experience).

2. **The actual operating rule (per GL 2026-04-26):** Jeff knows the Odoo work happened and watched it struggle. He does not know that GL is migrating off Odoo entirely. The platform pivot stays internal until Phase 1 (customer-facing site + storefront) is demo-ready. The recovery move is showing Jeff a working customer-facing site as the result of months of work, not announcing a do-over.

3. **Operational implication:** Phase 1's bar is not "functional." It is "visibly polished enough that Jeff's reaction is 'oh, this is real.'" The visual quality is what makes the platform pivot land as "I built you something good" rather than "I had to throw it all out." Functional-but-ugly fails the demo even if every test passes.

**Generalizable lesson:** When standing docs use "X doesn't know Y" to encode a trust-state, ask whether Y is the precise fact being protected or a paraphrase of one. Paraphrases compound: each instance restates them slightly cleaner, and over a few sessions the actual nuance is lost. For load-bearing trust dynamics, ask GL once for the precise statement and write that verbatim. Don't tidy. (This receipt also lives in project memory at `<memory>/jeff_trust_and_phase_1_demo_stakes.md` — auto-injected on session start.)

---

## 2026-04-26 — A project frame can be wrong, not just labels. Reframe early, propagate everywhere, delete the old.

**What happened:** Inherited a project framed as "Odoo → ERPNext migration." Spent half a session deepening planning artifacts on top of that framing (PROJECT.md, ROADMAP.md, queue, decisions log, HANDOFF, scripts, capability docs). Then GL revealed: there is no production Odoo — it failed in testing, never went live, Jeff doesn't know. The frame wasn't just labeled wrong; it was structurally wrong. The 10-phase ROADMAP organized work around model translations from a system that's reference material, not a system being migrated. The "stealth migration / trust damage from prior failures" Core Value referenced damage Jeff never experienced.

**What was learned:**
1. **Surface framing assumptions BEFORE building artifacts on top of them.** The first instance who built the planning machinery never asked "wait, is this even a migration?" because the standing files said it was. Cost: significant churn to undo.
2. **A wrong frame deepens its own debt.** Every artifact written under the wrong frame must either be rewritten or deleted. The cost compounds with every layer.
3. **Reframing requires deletion, not just rewriting.** Stale REQUIREMENTS.md tied to old phases. Stale `phases/01-inventory/` research from a deferred-then-renamed phase. Empty `Locally-Twisted-Frontend/` placeholder. All deleted in this session. GitHub is the archive; we store nothing unnecessary.
4. **The reframe needs a "Reference Disposition" section in CLAUDE.md** so future instances can't accidentally re-introduce the old framing by reaching into the prior dir for resources. Make it explicit: these things will be retired; future instances must NOT assume they exist.

**Generalizable lesson:** When inheriting a project, sanity-check the frame against the human's current reality before extending the planning artifacts. Three honest questions cover most cases: "Who is this FOR (and do they know what we're doing for them)?" "What is this REPLACING (vs. building from scratch)?" "What does success LOOK LIKE on demo day?" If any of the answers contradicts what the standing docs assume, stop and reframe. The cost of pausing is low; the cost of compounding the wrong frame is high.

---

## 2026-04-26 — Don't trust API silent success — verify the field landed where you think

**What happened:** Set ERPNext Website Settings.`website_theme_css` via the Frappe `set_value` API. API returned `{"message": {...}}` — looked like success. Curled the served homepage; CSS wasn't in the head. Tried again with stronger parsing; still nothing. Spent two cycles debugging "why isn't my CSS appearing" before checking the DocType field list and finding `website_theme_css` doesn't exist as a field on Website Settings. The right field is `head_html`. Frappe's set_value silently accepted the write to the non-existent field.

**Generalizable lesson:** When a write API returns success but the visible state doesn't change, before re-trying the write, **list the actual fields available on the DocType**. Don't trust field names from memory or pattern-matching. The Frappe API for inspecting a DocType: `GET /api/resource/DocType/<NAME>` returns the full schema including the field list. Spend 30 seconds checking the schema before another 5 minutes debugging the wrong field.

---

## 2026-04-26 — WebFetch failure ≠ site down. Verify with a second tool before alarming the human.

**What happened:** WebFetch tool returned `ECONNREFUSED` for `http://5.78.136.133/`. Reported to GL "the live site is DOWN." This was wrong — `curl -sI` returned HTTP 200 immediately. The WebFetch tool just doesn't handle raw-IP URLs through its proxy layer; it has nothing to do with the site's actual reachability.

**Generalizable lesson:** When a network-dependent tool fails, the failure could be the tool, the network path, the URL format, or the actual server. Reach for a second tool (curl, ping, browser screenshot) before reporting a server outage to the human. **The cost of a false-alarm-then-correction is the same anti-pattern as "report without watching" — it withdraws trust from your reporting.**

---

## 2026-04-26 — Cloudflare blocks default Python urllib User-Agent

**What happened:** First call to `https://api.together.xyz/v1/images/generations` returned HTTP 403 with Cloudflare error code 1010. Worked immediately after adding a real browser User-Agent header.

**Generalizable lesson:** When a third-party API returns 403 + Cloudflare error, the User-Agent is the first thing to check. Default urllib UA looks like `Python-urllib/3.x` and is blocked by many Cloudflare-protected APIs as a generic-bot signature. Always pass `User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36` (or similar real-browser string) for any API call from Python.

---

## 2026-04-26 — `bench set-config host_name` is not enough — `frappe_docker` nginx rewrites the Origin header BEFORE socketio sees it

**What happened:** GL still saw `socketio_client.js:69 Error connecting to socket.io: Invalid origin` after Trellis's earlier fix. Server-side `bench --site frontend show-config` showed `host_name: http://localhost:8081` set correctly. `curl /socket.io/?EIO=4&transport=polling` returned HTTP 200 from the host. The websocket service itself was up and listening. Yet the browser kept rejecting.

**Root cause:** `frappe_docker`'s nginx config at `/etc/nginx/conf.d/frappe.conf:47` contains:
```
proxy_set_header Origin $proxy_x_forwarded_proto://frontend;
```
That line REWRITES the browser's `Origin: http://localhost:8081` header to `Origin: http://frontend` (the internal Docker service hostname) before proxying to the socketio upstream. The socketio Node service is configured with `origin: true` (echo whatever Origin you receive back as `Access-Control-Allow-Origin`). So the response comes back as `Access-Control-Allow-Origin: http://frontend` — which doesn't match the browser's actual origin → CORS rejection → "Invalid origin" surface in the JS client. **Trellis's earlier `bench set-config host_name` fix targeted the wrong layer entirely.**

**Fix (verified working):** Patch the in-container nginx config to pass through the original Origin:
```
proxy_set_header Origin $http_origin;
```
Then `nginx -s reload` (no container restart needed → no DNS cache trap).

This project ships the patch as `scripts/fix/patch_nginx_socketio_origin.py` (run via `docker cp` + `docker exec`). The patch is NOT persistent across container recreation — it edits the in-container file. For permanent fix, mount a custom `frappe.conf` via a docker-compose override.

**Verify:**
```bash
curl -sS -i "http://localhost:8081/socket.io/?EIO=4&transport=polling" -H "Origin: http://localhost:8081" | grep -i access-control-allow-origin
# Expected: Access-Control-Allow-Origin: http://localhost:8081  (matches what you sent)
```

**Why the upstream `frappe_docker` design rewrites Origin:** the assumption is TLS terminated at a load balancer in front of nginx, with consistent internal hostname `frontend`. For browser-direct localhost access (no LB, no TLS), pass-through is correct. Production deployments to Frappe Cloud won't hit this because Frappe Cloud uses its own nginx layer.

**Generalizable lesson:** When a CORS / origin error persists after the obvious config fix, check whether nginx is rewriting headers BEFORE the upstream sees them. `proxy_set_header` lines are easy to miss — but they silently override what the upstream thinks the request looks like. (Also captured in global lessons-learned 2026-04-26.)

---

## 2026-04-25 evening — Frappe socket.io throws "Invalid origin" when site is on a non-default port

**What happened:** Opened the LT ERPNext UI at `http://localhost:8081`. Browser console showed `Error connecting to socket.io: Invalid origin` and `GET /socket.io/... → 400`. Real-time UI features (notifications, live updates, multi-tab sync) silently broken.

**Root cause (incomplete — see 2026-04-26 entry above for the actual fix):** `frappe_docker`'s `pwd.yml` brings the site up assuming Frappe's default port 8080. We map host port 8081→8080 inside the container for LT (so BBC and LT can both run). The `host_name` in the site's config was unset, so Frappe's `get_allowed_origins()` defaulted to something that didn't include `http://localhost:8081`. The socketio server (Node, separate container) rejects mismatched Origin headers as a CSRF defense.

**The trap that bit me on first attempt:** I restarted only the websocket container. That fixed the origin check (it re-read host_name from site config), but Docker assigned the websocket container a *new internal IP* on restart. The frontend (nginx) container had cached the OLD IP from its initial DNS resolution and kept trying to proxy `/socket.io/` to the dead address — producing **502 Bad Gateway** with `connect() failed (113: No route to host)` in nginx's error log. Restarting the websocket without restarting nginx turned an "Invalid origin / 400" symptom into a "No route to host / 502" symptom. nginx in `frappe_docker` does not use a `resolver` directive, so it never re-resolves on its own.

The compose-level `restart` (or restarting frontend + websocket together) avoids this entirely because Docker re-establishes the network and nginx re-resolves on its first proxy attempt.

**What to do for any future site spinup at non-default port:** Run the `set-config host_name` step immediately after `bench new-site` finishes, BEFORE the user touches the UI. AND apply the nginx Origin patch (per 2026-04-26 entry).

**Generalizable lesson:** in `frappe_docker` (and similar nginx + Compose stacks), restarting an upstream container without also bouncing nginx will give you a confusing 502 because nginx caches DNS at startup. Default to `docker compose restart` for the whole project, not single-container `docker restart`, when troubleshooting the data plane.

---

## 2026-04-25 — `gsd-tools commit` returns "nothing_to_commit" because the post-Write auto-commit hook beats it

**What happened:** `node gsd-tools.cjs commit "..." --files PROJECT.md` repeatedly returned `{"committed": false, "reason": "nothing_to_commit"}` even though the file was clearly new. Confused me into staging manually.

**Root cause:** This workspace has a post-Write hook that auto-commits files after the Write/Edit tool succeeds. By the time the GSD `commit` call runs, the file is already in HEAD with an "auto: Write ..." commit message. There's nothing for `gsd-tools commit` to commit.

**What to do:** When `nothing_to_commit` returns, run `git log --oneline -3` to confirm the auto-commit happened (look for `auto: Write FILENAME`). If yes, the workflow can proceed — the file IS in version control, just under a different commit message than the GSD workflow expected. The workflow's commit calls are belt-and-suspenders; the auto-hook is the suspenders.

---

## 2026-04-25 — `git status` on Windows hides freshly-staged dotfiles in the porcelain output

**What happened:** Staged `.gitignore` and `.planning/PROJECT.md` via `git add`. `git ls-files --stage` showed both files indexed with their hashes. `git status --short` and `git status` showed neither as staged — and showed all the OTHER files as untracked. Misleading.

**Root cause:** Unknown — possibly Git Bash + Windows interaction with first-commit-on-empty-repo state. The plumbing (ls-files, commit, ls-tree) was correct; only the porcelain (status) lied.

**What to do:** Trust `git ls-files --stage` and `git ls-tree -r HEAD --name-only` over `git status` when verifying first-commit state on Windows. The actual commit succeeds; status display is unreliable.

---

## 2026-04-25 — Frappe `pwd.yml` defaults to v16.15.1 image; v15 line is stable but you must pin manually

**What happened:** Cloned `frappe_docker`, expected to bring up ERPNext v15. The default `pwd.yml` pinned all 8 service images to `frappe/erpnext:v16.15.1`. Had to swap them all to `frappe/erpnext:v15.105.0` before starting.

**What to do:** When installing Frappe via `frappe_docker`, immediately edit `pwd.yml` to pin the desired tag *before* `docker compose up`. The rolling `v15` tag exists and points to the latest patch (currently `v15.105.0`), but pin to a specific patch for reproducibility — rolling tags will silently pull a newer patch on next `up`. (Also see agency-level v15-stability standing rule in `Built_by_Cameron/CLAUDE.md`.)

---

## 2026-04-25 — Frappe images are large; cache them on the first install, second site comes up in seconds

**What happened:** First `docker compose up` for a Frappe stack took several minutes (image pull, layer extraction). The second compose project for LT used the same `frappe/erpnext:v15.105.0` image and came up in 18 seconds — Docker recognized the layers and just retagged.

**What to do:** When spinning up multiple ERPNext sites locally, reuse the same image tag across compose projects. Each site gets its own volumes (named differently per project) but shares the image. This is fast and disk-efficient.

---

## 2026-04-25 — WSL2 default RAM allocation is below ERPNext's working set; bump `.wslconfig` to 8 GB before installing

**What happened:** Initial WSL2 had 1.5 GB RAM cap (set in `.wslconfig` from a prior expedition). Frappe stack runs MariaDB + Redis + web + socketio + scheduler + 2 worker queues — 1.5 GB was below ERPNext's 4 GB minimum. Visible in `docker info` as `MemTotal: ~1.47 GB`.

**What to do:** Edit `C:\Users\baenb\.wslconfig` `[wsl2]` section to `memory=8GB processors=4 swap=2GB` (the machine has 47.7 GB total — 8 GB is conservative). After edit, `wsl --shutdown` then run any docker command to wake the daemon with the new limits. Verify with `docker info | grep MemTotal`.

---

## 2026-04-25 — Frappe Cloud Sites plan is $5/mo per site, not $25-100; transfer is self-service

**What happened:** Quoted GL "$25-100/mo per client" early in a Frappe Cloud cost discussion based on bad memory of the pricing. GL was about to make decisions on bad numbers. Re-checked the actual pricing page.

**Real numbers (2026-04, verified at frappe.io/cloud/pricing):**
- **Sites plan**: starts at $5/month per site, includes custom apps, custom domain, SSH access
- **Servers plan**: starts at $20/month for the whole server, unlimited sites/benches
- **Free trial**: 14 days, no payment method

**Site transfer mechanism (verified at discuss.frappe.io/t/transfer-ownership-on-frappe-cloud/122800):** Self-service via the dashboard's Actions tab. Receiving Frappe Cloud team must exist (have GL's client create their own account first). Server-level transfer requires a support ticket; site-level does not.

**What to do:** When quoting hosting costs, verify against the live pricing page. Frappe's pricing has changed; training-data memory is unreliable. The cheap-and-transferable model is the right fit for the agency's "build → sell → transfer ownership" pattern.

---

## 2026-04-25 — When GL forbids touching one file, the boundary is the file (don't extrapolate to "GL must do the work")

**What happened:** GL said "leave odoo specific scripts and skills alone — we need to create ERPNext specific ones." I extrapolated this to "GL must be the executor of any production-touching work" and drafted a human-in-the-loop pattern where GL would paste production query results back to me. GL corrected: "the standard process is YOU preparing the script and executing it once it's been researched and built correctly."

**What to do:** When GL sets a boundary on a *file*, the boundary is on that file. Build new tooling elsewhere. The standard process — agent builds, agent tests, agent executes — still applies. Don't outsource execution to GL based on a misread of the boundary's scope.

---

## 2026-04-25 — Building infrastructure ≠ building the thing GL asked for

**What happened:** Spent significant tokens scaffolding GSD project structure (PROJECT.md, REQUIREMENTS.md, ROADMAP.md, config), then planning Phase 1 with research + planner + checker + revision iterations + threat models + validation strategies. Two ERPNext sites running but completely empty. Zero translation from Odoo had occurred. GL: "you haven't even rebuilt the site in ERPNext?! Focus on the rebuild."

**What to do:** When GL asks for a *thing*, the score is "is the thing built yet?" not "is there a beautiful planning artifact for the thing." Set up the minimum scaffolding required to start building, then start building. The planning machinery is meant to *serve* the build, not to *be* the build. If you find yourself iterating planner-checker loops on a phase that hasn't moved one bit closer to the deliverable, stop and start doing the deliverable.

This is the global anti-pattern #2 (Drift from GL's actual ask). Receipt added to `anti-gl-patterns.md` (project-local).

---

## 2026-05-09 - Product imports fail when they copy fields instead of receiving logic

**Lesson:** For ERP/ecommerce migrations, importing product records is fake progress unless the destination system can receive the product's behavior everywhere. Field names and data values are not enough. The destination needs executable homes for variant logic, add-on logic, price resolution, media visibility, cart/checkout payloads, invoice/order meaning, fulfillment notes, mobile/desktop customer journeys, and fail-loud missing-data reports.

**What happened:** During the Locally Twisted product-page/catalog work, GL clarified that the goal is not to copy Odoo or decorate ERPNext product pages. Odoo is a conceptual witness for mature ecommerce behavior, while ERPNext native ecommerce is insufficient. The build must create an ERPNext-side ecommerce logic ecosystem before any real product migration matters.

**Do this next time:** Before importing customer-facing products from a more mature ecommerce source into a weaker shell, define the receiving architecture first: destination fields/DocTypes, ownership of each behavior, template/process classes, cart/checkout/invoice integration, and verifiers. Treat proof products as test fixtures, not migration completion.

**Avoid:** hardcoding proof products, frontend-only price/add-on logic, unsupported custom fields that silently disappear, missing invoice meaning, and claiming migration progress because records exist.
---

## 2026-05-09 - Do not let web lookup stand in for browser proof

**Lesson:** Internet access, source/page reading, and rendered browser verification are separate capabilities. A successful web lookup proves outside information access; it does not prove what an LT route renders or how JavaScript, CSS, forms, checkout, menus, or responsive layouts behave.

**What happened:** Codex verified `web.run` against `example.org` and separately verified repo-local Playwright by launching headless Chromium silently, reading rendered DOM text, and capturing a screenshot buffer. The Browser Use in-app path remained unproven because the required Node REPL control tool was not exposed in this session.

**Do this next time:** Name the evidence surface in closeout. Use `web.run` for current public facts and citations. Use LT's route-specific npm gates or direct Playwright for rendered behavior. Re-test Browser Use in the current session before claiming in-app browser control.

**Avoid:** saying "browser verified" when only page text was fetched, opening a visible window when headless Playwright is enough, or treating plugin availability as proof that its control path works.

---

## 2026-05-09 - Read-only reports must not run fake-data contracts

**Lesson:** A report can stop being read-only if it calls a verifier that creates rollback fake data behind the scenes. Accountant/operator review paths should consume summarized readiness state, not run Lead/upload/payment/document contracts while rendering.

**What happened:** While reviewing non-product operations, the customer reminder Desk/report chain consumed the paperwork digest, which consumed the business automation index. The full index mode can run rollback-heavy contracts. Under concurrent verifier/report execution, synthetic Lead/upload blocker evidence briefly surfaced as open record-level failures.

**Do this next time:** Give shared automation indexes a non-runtime mode for internal reports. Keep runtime fake-data contracts in explicit verifier/synthetic readiness commands, run DB-mutating verifiers serially, and make report payloads expose whether runtime contracts were executed.

**Avoid:** nesting full verifier suites inside Desk reports, parallelizing rollback-heavy Frappe DB verifiers, or treating `read_only: true` as sufficient when called dependencies can mutate state.

---

## 2026-05-11 - A Cloudflare `MISS` is not safe proof for dynamic Frappe routes

**Lesson:** For dynamic login, form, cart, checkout, payment, account, and webhook routes, `cf-cache-status: MISS` means the route was cache-eligible. That is a launch failure, not a pass.

**What happened:** The first Cloudflare launch verifier only blocked `HIT`, `STALE`, and `UPDATING`. Review caught that a route can return `MISS` immediately after a purge or Cache-Everything-style rule and later become `HIT`.

**Do this next time:** Use an allowlist for dynamic-route cache statuses. Absent header, `BYPASS`, and `DYNAMIC` are acceptable for this LT gate; `MISS` and unknown non-empty statuses fail loudly with a contract.

**Avoid:** small denylist checks for cache behavior on launch-critical dynamic routes.

---

## 2026-05-11 - File names are not customer portal authorization

**Lesson:** A Frappe `File.name` proves only that a row exists. Customer portal actions must prove who uploaded the file and which source record it belongs to before creating visibility metadata.

**What happened:** The first customer portal file-registration endpoint allowed any existing `File` name after source access passed, which could attach unrelated or staff-owned files to a customer's portal history.

**Do this next time:** Customer-uploaded portal files need both same-user ownership and same-source attachment before registration. Staff-published files need a separate operator path and must not be marked `uploaded_by_customer`.

**Avoid:** customer-facing whitelisted methods that accept arbitrary document names without checking source ownership and intended attachment context.

---

## 2026-05-12 - A product scaffold is not ecommerce architecture

**Lesson:** When GL asks for software architecture, product buckets and candidate
lists are not enough. Architecture must name the reusable contracts, ownership
boundaries, payloads, server-derived fields, downstream document destinations,
and verifiers that make product examples safe.

**What happened:** A complex checkout scaffold grouped products into planning
stages, but that answered a downstream product-readiness question instead of
the requested ERPNext ecommerce receiving architecture. The corrected slice
added `lt-product-page-architecture-contract-v1`, mapping source/ERPNext axes to
backend-driven controls, `lt-product-config-v1` payload targets, resolver
fields, and Quotation/Sales Order/Sales Invoice line parity.

**Do this next time:** Before discussing product accommodation, build or point
to the generic contract first. Product rows should prove sale-unit,
customization, add-on, review-only, quote-first, cart, checkout, and document
parity behavior. They should never be the architecture.

**Avoid:** product-name branches, frontend-only eligibility, treating a verifier
report as a system design, or saying "architecture" when the artifact only
classifies products.

---

## 2026-05-12 - Do not classify payload targets from attribute names alone

**Lesson:** A label like `latex colors` is not enough to decide whether a live
ERPNext product-page control targets `selected_options` or `color_recipes`.
The payload target has to come from the source/backend contract.

**What happened:** The live architecture projection treated any balloon-color
axis as `customization -> color_recipes`. Review caught the inverse risk for
ready-to-order products whose color-looking axis is really a required ERPNext
variant sale-unit. The fix moved this rule into
`catalog_contract/axis_projection.py`: source/backend recipe semantics target
`color_recipes`; absent recipe authority leaves the variant axis as
`selected_options`; explicit single-color sale-unit markers override
recipe-looking patterns.

**Do this next time:** Put semantic projection rules in a shared backend helper,
then verify both the generated contract and the rendered/cart payload. A pass
that only proves the Add to Cart button enables is not enough.

**Avoid:** name-based axis routing, frontend-only selector assumptions, and
verifiers that check emitted JSON without also proving the browser payload.

---

## 2026-05-15 - A pasted owner email is not proof of the local ERPNext environment

**Lesson:** When debugging a form notification, match the exact environment
that generated the email before drawing conclusions. A Lead number in an email
can exist locally with different data if the email came from staging, live, or
an older instance.

**What happened:** The Nicole/vettedvas owner-notification text matched LT's
ERPNext owner email template, but the local database had no Nicole/vettedvas
Lead, Communication, or Email Queue row. Local `CRM-LEAD-2026-00011` was an
older smoke-test Lead, not Nicole.

**Do this next time:** Verify Lead, Communication, Email Queue, File, and route
state in the exact local/staging/live environment under investigation. Do not
inspect personal email or unrelated mailboxes for LT ERPNext form evidence
unless GL explicitly asks and the mailbox is in scope.

**Avoid:** treating a pasted email as local database proof, using a proxy Lead
with the same name/number shape, or leaving the ERPNext/Frappe record path to
search unrelated personal mail.

---

## 2026-05-15 - Public form sales spam needs soft suppression, not broad keyword blocking

**Lesson:** A public business inquiry form can receive vendor sales pitches as
soon as it is live. Protect the owner notification path, but keep ambiguous
submissions reviewable so real customers are not lost.

**What happened:** The Nicole/vettedvas-style message was a virtual-assistant
sales pitch. The repair added a signed form token, honeypot, and conservative
sales-solicitation classifier. High-confidence sales pitches still save a Lead
for audit/review and follow the customer-safe confirmation path, but the owner
email is suppressed.

**Do this next time:** Require multiple vendor/sales signals before suppressing
owner notification, and let event/customer signals override the classifier.
Guard both the spam gate and the false-positive boundary with verifiers.

**Avoid:** blocking customers because they mention corporate, marketing,
school, nonprofit, or business context, or silently dropping all evidence of a
submission that might still need review.

---

## 2026-05-16 - A clean last commit is not a release-scope audit

**Lesson:** For Frappe Cloud custom app releases, release scope is the diff from
the previous live app hash to the target app mirror commit. A clean final
commit and a dirty-worktree audit answer narrower questions.

**What happened:** The 2026-05-16 inquiry release did not mix current
uncommitted dirty files into the deployed commits. However, the app mirror
target contained already-committed changes beyond the final source commit
`631f9a8`. That meant "dirty files were not deployed" was true, but not enough
to describe everything the live app update promoted.

**Do this next time:** Capture the current live app hash/source point, target
mirror commit, old-live-to-target file diff categories, site update/migrate
result, and live verifier receipt before promotion. Use the dirty-worktree
check only to prove uncommitted local edits were not staged.

**Avoid:** saying "only this commit went live" from `git show HEAD`, or treating
app mirror scope as equivalent to the final full-repo commit.

---

## 2026-05-16 - Name staging versus live before diagnosing a panic URL

**Lesson:** A Frappe Cloud staging URL can be broken while live is healthy.
Environment naming is not a formality during incident response; it determines
which records, settings, and blast radius are real.

**What happened:** GL reported `https://locallytwisted-staging.frappe.cloud/#login`
as live broken. That URL was staging. Staging root and `/#login` rendered Sign
In because `Website Settings.home_page` and branding fields were unset, while
live routes were separately healthy.

**Do this next time:** Say the environment out loud, check `/`, `/#login`,
`/home`, `/contact`, and Website Settings parity, then repair staging config
without implying production was changed. Verify live separately before making a
live outage claim.

**Avoid:** escalating a staging-only root/login drift into a live breakage
claim, or debugging source code before checking Frappe Website Settings.

---

## 2026-05-21 - Menu level must match the customer's decision level

**Lesson:** A public navigation submenu should expose the level a customer can
reason about. For LT `Ready-to-Order`, that means category concepts from Item
Group records, not a long list of individual Website Item products.

**What happened:** The local header showed product quick links in the
`Ready-to-Order` dropdown, and the current data made the menu look like almost
all bouquets. The copy also described ERPNext/backend approval instead of the
customer's choice: what kind of decor do I need?

**Do this next time:** Trace the rendered menu to the source data, compare that
data level to the intended customer decision, then update the context,
template, search behavior, and verifier contracts together. If the menu is
category browse, use the same source as `/shop`: visible `Item Group` children
of `Shop Items`.

**Avoid:** product dumps in primary nav, backend implementation copy in public
dropdowns, and verifiers that lock the UI to product examples when the business
intent is category discovery.

---

## 2026-05-21 - Derived worktree IDs still need Windows path-length reality checks

**Lesson:** A stable readable project ID can still be too long for a Windows
worktree when the repo has deep framework paths. Repo-forest safety and path
length both matter.

**What happened:** The first LT worktree path used the full derived ID
`built-by-cameron__clients__locally-twisted` plus a long session/task slug. Git
failed while checking out deep Frappe/ERPNext files with `Filename too long`.
The short ID `builtbycameron-lt` created a clean external worktree without
putting anything inside the parent/company repo or client repo.

**Do this next time:** Keep worktrees outside all project repos, but use short
stable IDs for deep repos. Verify the path before creation and update both the
project `AGENTS.md` and the neutral coordination hub when a shorter ID becomes
the real safe default.

**Avoid:** treating path readability as more important than checkout success,
or adding parent-repo `.gitignore` rules as the first fix for bad worktree
placement.

---

## 2026-05-21 - Capability Seed Parity Is Not LT Truth Repair

**Lesson:** A framework seed update can make LT aware of new capability
concepts without proving or repairing LT-specific capability claims.

**What happened:** v2.4 source/provenance, organic growth, and Perfect Bite
cards were propagated into LT. The root still reports older missing references,
backlinks, and trust warnings.

**Do this next time:** Regenerate the registry and graph report after seed
propagation, then split local cleanup into its own LT workstream. Verify each
missing reference or trust field against current LT files before editing.

**Avoid:** using a source-package update as cover to normalize LT
`currently_true`, dependency, or backlink fields without local evidence.

---

## 2026-05-22 - Balloon color prompts need swatch authority, not hex confidence

**Lesson:** For LT balloon visuals, exact owner/Odoo swatch images and balloon
color names outrank hex values. Hex can help web matching, but it is not enough
to make generated balloon imagery look like the colors Jeff actually offers.

**What happened:** The first category-hero repair used source-photo crops and
still produced bad category heroes. The next generated-image pass improved the
shape problem, but GL clarified the generation brief must name the balloon
colors and source context, not only hex. The kept repair uses generated
category-specific hero art, a 53-color addendum, a dated manifest, and a
verifier that checks the prompt/manifest boundary.

**Do this next time:** Before generating LT balloon imagery, open
`_resources/STYLE-GUIDE-BALLOON-COLOR-ADDENDUM.md`, pass the source color
names and swatch refs into the prompt, review the contact sheet for fake text
or mismatched palette, then run `scripts/verify/shop_category_hero_images.spec.js`
when route heroes are involved.

**Avoid:** hex-only prompts, treating model output as proof photography,
leaving fake signage/text in generated banners, or confusing route hero art
with ERPNext Item Group image approval.
