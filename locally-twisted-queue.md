# Locally Twisted — Work Queue

Current work only. **When an item is completed, DELETE it from this file.** Git tracks completion history. Queues are not for history.

Format: `- [priority] description — context / blocking notes`

LT-specific work only. Cross-client / agency-wide work lives at `Built_by_Cameron/built-by-cameron-queue.md`.

---

## Active

**P0 ENB replacement, lead proof, and shop/payment go-live plan (2026-06-08):**
Active controller packet is
`workstreams/enb-replacement-shop-go-live-2026-06-08.md`; root decision packet
is `MARKETING-REPLACEMENT-AND-SHOP-GO-LIVE-PLAN-2026-06-08.md`. Goal: replace
ENB's useful lead-generation function with LT/BBC-owned landing URLs,
conversion tracking, reporting, and explicit shop/payment go-live gates that
fit the ERP-backed system. This lane is documentation/source proof only until
GL approves the next stage. Do not touch staging/live/provider/DNS/Search
Console/Stripe/ad accounts/customer data/ENB access or production ERPNext data
from this lane without a separate approval.

**P0 owner staging review and change intake (2026-05-25):** Active handoff is
`workstreams/frappe-cloud-staging-owner-review-2026-05-24.md`, with checkout
detail in `workstreams/ecommerce-audit/staging-checkout-product-flow-2026-05-24.md`
and taxonomy detail in
`workstreams/ecommerce-audit/shop-primary-secondary-taxonomy-map-2026-05-24.md`.
Decision packet: `decisions/2026-05-24-staging-owner-review-recovery.md`.
Current staged source for owner review is full repo `4722a1c` and app mirror
`3ca46bb`. Frappe Cloud staging installed app commit `3ca46bb`; site update
`Migrate` `Success` and cache clear have completed. Hosted staging proof
passes checkout `4/4`, product gallery `4/4`, search `4/4`, category heroes
`25/25`, and public asset
integrity for `31` routes / `315` local asset URLs. The next safe step is owner
review on staging and a change log from that review. Do not touch live payment
settings, DNS, Search Console, live Stripe, or production data from this queue
item. Delivery-only fulfillment handoff:
`workstreams/ecommerce-audit/delivery-only-fulfillment-staging-2026-05-25.md`;
mixed carts must stay mixed.

**P0 capability graduation cleanup (2026-05-21):** Active handoff is
`workstreams/capability-graduation-ladder-2026-05-21.md`. LT now has the global
Capability Graduation Ladder seed (`schema_version: 2.5`) but must adopt it
cleanup-first because the local capability graph already has older
project-specific validation debt. Next safe step is a read-only graduation
audit plus small action packets for high-risk cards such as Frappe
Cloud/Cloudflare/Stripe launch, public storefront security, ecommerce
receiving architecture, Webshop Guest party, shared inquiry form, and
multi-agent coordination. Do not promote cards, write registries, change trust
metadata, edit ERPNext data, or touch staging/live/provider/payment/DNS paths
from this lane without a separate approved packet.

**P0 coordination safety pilot (2026-05-21):** Active handoff is
`workstreams/coordination-safety-pilot-2026-05-21.md`. LT is the protected
clean child/client pilot for the neutral multi-agent workflow. First action is
a read-only cold-agent dry run from the LT root: confirm Git root, parent repo
above, nested repos below, branch/status, worktree routing, Six-Box ownership,
and proposed live-board/session-registry entries. Do not use this pilot as
permission for product, ERPNext, Frappe Cloud, DNS, Stripe, staging, or live
release work.

**P1 Chrome plugin console-debug bridge repair (2026-05-21):** Deferred source
is `workstreams/browser-verification-runtime.md`. Chrome 148, the Codex Chrome
Extension, and the native host manifest all checked out locally, but the bridge
still failed with `browser-client is not trusted`. Retry only when Chrome and
Codex are in the intended single account/profile context; do not claim
extension-backed console debugging works until `browser.tabs.list()` succeeds.

**Domain, provider cleanup, and reindex repair (2026-05-19):** Source handoff
is `workstreams/domain-provider-reindex-cleanup-2026-05-19.md`. Verified live
chain is GoDaddy registrar -> Cloudflare authoritative DNS/email routing ->
Frappe Cloud -> ERPNext/Frappe. Hetzner/legacy_source `5.78.136.133` is old reference
and decommission scope, not current public DNS. Bluehost is the former
nameserver/likely hosting cleanup target; Wix remains unverified. Reindexing is
blocked until the live sitemap/canonical host drift is released: current live
`sitemap.xml` has 29/29 locs on `https://locallytwisted.v.frappe.cloud`, and
`/about` canonical/`og:url` also use the vanity host. Source fix and SEO guard
are started in `seo.py`, `www/sitemap.py`, and `seo_contract.spec.js`, but no
app mirror sync, Frappe Cloud deploy/site update, cache clear, Search Console
submission, provider cancellation, or DNS mutation has been performed. Next
safe step is local SEO verification, then normal Frappe Cloud release gate,
then live `LT_BASE_URL=https://locallytwisted.com npm run test:seo-contract`,
then Search Console sitemap submit/URL Inspection.
2026-05-21 source follow-up adds selective indexing: stable business pages can
index after review, ecommerce discovery paths are excluded/noindex while
`lt_ecommerce_paused=1`, the pause page is always noindex, and staging can be
globally noindexed with `lt_public_indexing_enabled=0`. This is not live until
the same release gate runs.

**Google Ads / Meta account takeover (2026-05-19):** Source handoff is
`workstreams/ad-account-takeover-2026-05-19.md`. Verified support evidence from
LT Gmail/Drive identifies Google Ads account `Locally Twisted` / customer ID
`437-723-0551`, historical customer ID `295-025-7991`, ENB manager account
`124-663-1239`, ENB admin-user evidence for `tosh@exploringnotboring.com`, and
current policy issue on campaign `22063769748`
(`ENB_Sales_Search_Custom Balloon Arches + Delivery - $5/day | 12.27.24`) for
HTTP `404` destination failure. Meta evidence is not dashboard-complete: there
is Facebook Business Manager email evidence and ENB/HighLevel
`Facebook Painting Leads` evidence, but no verified Meta ad account ID,
campaign export, pixel/dataset, lead-form, partner, or billing inventory yet.
2026-06-10 launch update: GL reports Google-side tools are logged in for the
reindex/ads/analytics push, but Meta Business Manager is not available because
the Facebook/Meta password still needs recovery. Keep Meta Business inventory
queued and blocked until credential recovery; do not search saved password
stores or treat old Gmail/Drive evidence as dashboard proof. Live crawl
readiness is green: production robots/sitemap respond on `locallytwisted.com`,
`www` redirects to the canonical host, live SEO contract passed 13/13, live
search contract passed 4/4, and the sitemap currently lists 26 canonical public
URLs. Google Search Console sitemap submission and URL Inspection can proceed
from the logged-in dashboard; sitemap submission completed successfully on
2026-06-10. Google Ads/Analytics inventory can proceed, but
live campaign spend, budget, conversion, tag, billing, or access mutations still
need explicit action approval.
Next safe step is authenticated provider-dashboard inventory using
`capabilities/recipes/ad-account-takeover-provider-control.md`; do not remove
ENB/agency access, billing, pixels/tags, lead forms, tracking phone numbers, or
manager links until dashboard exports and HighLevel/lead-routing dependencies
are captured. No live-site deploy, ad mutation, billing mutation, or access
mutation was performed.


**Ecommerce launch execution posture (2026-05-11 GL/Leader correction):** The
goal is to open and prove the ecommerce path, not preserve pause posture.
2026-05-14 GL correction: `lt_ecommerce_paused=1` is a live/customer exposure
safety lock, not an implementation blocker. Continue local and staging/test
harness ecommerce work under the lock and name actual blockers: incomplete UI,
missing apply flow, unsafe checkout, unmapped add-ons, unresolved pricing,
unverified media, failed verifier, missing staging proof, or owner approval.
Use the matching Frappe Cloud/staging, product import, live payment, DNS, and
staging-to-live gates to decide what can safely go live. Current
visible/imported product records are fixture/test products for architecture
proof only; Locally Twisted itself is a real client project.

**P0 Ready-to-Order category menu local review (2026-05-21):** Superseded for
category content by the 2026-05-24 taxonomy implementation; keep the menu
architecture but use the 8 active primary category model. Handoff is
`workstreams/ready-to-order-category-menu-2026-05-21.md`. Source branch
`codex/ready-order-category-menu` changes the public `Ready-to-Order` desktop
submenu, search overlay, and mobile drawer from product quick links to
ERPNext/Frappe `Item Group` category links under `Shop Items`. The dropdown copy
is customer-facing and must not mention ERPNext, Website Item, or backend
approval concepts. Branch-level syntax and nav IA checks pass. The local Docker
stack was repointed with a temporary compose override so
`http://localhost:8081/` now mounts this worktree, `python
scripts/dev/clear_website_cache.py` passed, and `python
scripts/verify/smoke_shop.py` passed with all shop smoke checks. GL confirmed
the rendered local menu looks correct on `http://localhost:8081/`. This is
local acceptance only, not staging/live release approval. Do not stage, deploy,
or promote this feature live until a separate release gate is explicitly opened
and passed.

**P0 product-page local review before staging (2026-05-20):** Active handoff is
`workstreams/ecommerce-audit/product-page-local-review-2026-05-20.md`. Local
source now fixes the mobile product image/details gap and makes the visible
fulfillment panel read from the runtime Website Item commerce lane, so Classic
Arch / quote-first products show quote/install language instead of checkout
pickup copy. Passed local receipts: `product_page_runtime_contract.py`,
`proof_product_contract.py`, `commerce_rules_contract.py`,
`npm run test:product-price-display`, `npm run test:variant-media`,
`python scripts\verify\smoke_shop.py`, `npm run test:layout-fit -- --grep
"variant-product|single-product|seasonal-category"` (39/39), and Python
compile for touched modules. No staging/live/Frappe Cloud/Stripe/DNS change was
performed. Remaining blocker before staging is not this CSS/copy slice; it is
the broader product-classification verifier conflict. Do not apply
`website_item_classification_contract.py` planned changes or treat
`quote_event_checkout_boundary_contract.py` as current truth until the
Basketball Arch/current-DB checkout conflict and the dry-run's 17 planned lane
changes are reviewed against the current business model.

**P0 ecommerce safety guard and release receipt matrix (2026-05-19):** Active
coordination source is
`workstreams/ecommerce-system-safety-guard-plan-2026-05-19.md`. This is
local-only, no live/staging deploy, no destructive catalog import, no Stripe
live payment, no secrets, and backend-first. Five GPT-5.5 worker lanes were
integrated locally. Passed receipts now cover backend product classification,
shop smoke, cart/checkout identity, visible price display, variant media,
checkout browser experience, payment amount/state, webhook/browser-return
reconciliation, payment cascade, checkout fulfillment, checkout lead conversion,
simple purchasable payment cascade, thank-you payment-state source guard, and
guest endpoint inventory. Remaining blockers before release language changes:
source-price modifier proof now passes after staging `_resources/catalog-source`;
fresh same-day snapshot, purge-scope dry run, backup, and guard-path dry run now
pass; import readiness remains blocked only on renewed explicit destructive
approval for the 2026-05-19 packet. Product-page galleries are no longer part
of the old "extra images held" blocker: `product-gallery-restoration-2026-05-22.md`
restored approved gallery media through Product Setup and Website Slideshow;
category/reference media remains separate. Permission-bypass lint now passes after
adding explicit guard comments to the 32 previously flagged existing production
`ignore_permissions=True` calls; guest endpoint inventory still passes with
11 guest endpoints and 3 public write endpoints. `npm run test:ecommerce-full`
now passes locally after the source-price and permission-bypass fixes.
Do not describe checkout/payment/catalog/public ecommerce as release-ready until
those blockers are cleared or explicitly accepted for the target release.

**Shop smoke gate (2026-05-11):** `d52c6888` cleared the
`/civic-community missing focused page title` blocker by rebaselining the
audience-page H1 expectations in `scripts/verify/smoke_shop.py` to match the
current `event_type_pages.py` source. Closeout command:
`npm run test:shop-smoke` passed with `=== All shop smoke checks PASSED ===`.
Future webshop/product-page work must stay backend-truth anchored to ERPNext
v15.105.0 / Frappe v15 Webshop fields, cart/checkout APIs, payment wiring, and
Frappe Cloud persistence, not frontend-only visual polish.

**Storefront ecommerce proof handoff (2026-05-11):** Current storefront-owned
handoff is `workstreams/ecommerce-audit/storefront-proof-and-complex-ui-handoff-2026-05-11.md`.
Ready-to-Order/search corrected and rendered proof passed; final post-import
checkout proof passed for Easter Balloon Cups, 7' Butterfly Column, Graduation
Grab n Go, 6' Graduation stands, and Unicorn Bouquet. The all-priced-page
frontend audit rendered 53 published priced routes: 18 full checkout passes and
35 products blocked at the first rendered layer by legacy internal hold or
needs-review state. `quote_first` is an old safety flag, not a business product
category; moving any held product into checkout still requires backend-truth UI
for multi-slot color recipes, add-ons, conditional pricing, image updates, and
cart/checkout/receipt summary parity.

**Ecommerce shop setup closeout (2026-05-12):** Current root handoff is
`ECOMMERCE-SHOP-HANDOFF.md`. Local ecommerce setup lanes are complete on
`main`: backend wiring `f82b8ef1` green with no edits, catalog/import/pricing
`4da4b135` published in `9a27b49`, media readiness `d2653ce8`/`d9543e5f`
published in `8e4a95b`, storefront UX/homepage verifier alignment
`3132de36`/`4fd5ae4f` published in `3179463`, and runner wrapper work
`786f962e` included in `e4186c1`. Current local counts are 53 published Website
Items, 10,686 Items, 49 templates, 10,629 variants, 10,186 active variants, 443
disabled variants, 10,668 Item Prices, 30 Item Attributes, and 32,049 Item
Variant Attribute rows after the college color preset repair. No local ERPNext
catalog/pricing/import/media/backend ecommerce blocker remains for the guarded
local architecture; remaining gates are GL local UI/UX approval, staging/live
release, Stripe, DNS, legal/policy, explicit real payment approval, and final
real catalog approval if the local product set is to become public catalog
truth.

**Backend product-page architecture contract (2026-05-12):** The architecture
layer corrected after the complex-scaffold drift is
`workstreams/ecommerce-audit/backend-product-page-architecture-contract-2026-05-12.md`.
Use `lt-product-page-architecture-contract-v1` as the source/local gate for
page controls -> versioned payload -> resolver fields -> SO/SI/Quotation line
parity. Product rows and the complex scaffold are downstream evidence only, not
the architecture. Guards: `python scripts/verify/product_page_architecture_contract_contract.py`,
`python scripts/verify/product_page_architecture_contract.py`, and
`npm run test:product-quote-first`. Post-review hardening now requires live
color variant axes to use source/backend recipe authority before targeting
`color_recipes`; otherwise they remain sale-unit `selected_options`.

**Frappe Cloud/Cloudflare/Stripe launch state (2026-05-16):** Source handoff is
`LT-LAUNCH-RUNBOOK.md`, with the deeper technical gate at
`workstreams/frappe-cloud-cloudflare-stripe-launch-2026-05-11.md`.
`locallytwisted.com` is now serving the Frappe Cloud site for pages/forms.
Current source is full repo `631f9a8 Run contact intake schema sync on install`
and Frappe app mirror `b4b3bf8 Run contact intake schema sync on install`.
Frappe Cloud site update `b48j584nua` and update job `b48oge6unq` succeeded;
the site is Active on `bench-39776-000015-f94v`, and cache clear job
`26es8svcaq` succeeded. Live route proof after update: `/`, `/#login`,
`/contact`, and `/login` returned expected surfaces. Live real company-email
smoke `smoke test from cameron` created Lead `CRM-LEAD-2026-00013`, stored five
private Lead Files and five CRM photo rows, sent owner Email Queue `683s86r04b`
with five attachment refs, and sent customer Email Queue `683suhfaa9` with no
photo attachments. 2026-05-14 connection audit still stands for Cloudflare
dynamic-route readiness. Remaining active launch blocker is not pages/forms; it
is live checkout. Keep Stripe/ecommerce blocked until live Stripe config,
product scope, policy URLs/webhook, and one real low-risk payment test pass.
Rerun Cloudflare dynamic-route and live form gates after any future
DNS/cache/security/Frappe Cloud release change. Future release review must
compare the previous live app hash to the target app mirror commit; do not use
the final commit alone as release scope proof.

**Sellable product reimport track (2026-05-17):** Current control
artifact is
the 2026-05-17 ecommerce audit sellable reimport handoff.
GL corrected the business model: every source-imported product is a product and
the local target is sellable checkout behavior. The local `frontend` site was
backed up, cleaned of local proof products, snapshotted, and reimported with
the then-current approved manifest. The 2026-05-24 taxonomy result now treats
51 published products as current and explicitly excludes 2 duplicate source
slugs. Backend gates should be re-run before using the old checkout-allowed
count as current proof.
Browser proof passed all 53 live Website Item routes in two batches under the
cart 50-line cap, at desktop and mobile widths, including cart and checkout
preview. `lt_ecommerce_paused=1` was restored and verified. Current media
caveats are narrower after 2026-05-22: product-page gallery media is restored
through Product Setup and Website Slideshow; category/reference media and 9
review-only add-on controls stay hidden/unmapped until approved. Follow-up on 2026-05-17 repaired the
Encanto/simple checkout variant media regression: selected simple variant
`Item.image` now renders and cascades to cart, Sales Order payload, and receipt
helper while complex raw media stays held. Handoff:
`workstreams/ecommerce-audit/variant-item-media-restore-2026-05-17.md`;
failure recipe:
`capabilities/failures/variant-media-overgating-regression.md`; guard:
`python scripts/verify/variant_media_contract.py`. Follow-up on 2026-05-18
disabled 390 stale enabled `Add Foil Number` optional-add-on variants in local
ERPNext and wired that idempotent cleanup into `seed_catalog.py`; handoff:
`workstreams/ecommerce-audit/catalog-optional-addon-variant-guard-2026-05-18.md`;
guard: `python scripts/verify/catalog_variant_contract.py`. Follow-up on
2026-05-18 added the school/seasonal color preset guard: Graduation Grab n Go
now has 4 college preset checkout variants, `6-graduation-stands` has 8
college preset checkout variants, and 19 hyperspecialized 50+ color products
route to quote request instead of raw-color checkout. Handoff:
`workstreams/ecommerce-audit/school-seasonal-color-preset-product-logic-2026-05-18.md`;
guards: `python scripts/verify/school_seasonal_color_preset_contract.py` and
`python scripts/verify/catalog_variant_contract.py`. No staging/live/Frappe
Cloud/Stripe/DNS/public exposure change was performed; GL local UI/UX testing
and explicit release approval are still required before any live promotion.

**Repo hygiene cleanup track (2026-05-17):** the cleanup track reconciled local
`main` with `origin/main` at `d541a0c` and deleted stale detached Codex
worktrees that held already-merged LT value after explicit approval. This is a
historical cleanup receipt, not a claim about the current feature commit stack.
Handoff:
`workstreams/repo-history-and-worktree-cleanup-2026-05-17.md`; capability:
`capabilities/recipes/launch-repo-cleanup-and-evidence-retention.md`. No live
deploy was performed.

**Reconciliation note (2026-05-07; refreshed 2026-05-11):** `scripts/verify/layout_fit.spec.js` is restored and currently verifies through `npm run test:layout-fit` (325 checks inside `npm run test:public-verify` after route/breakpoint matrix expansion and generated hero work). `npm run test:container-contract` is the executable route-level public container contract and is part of `npm run test:website-verify` / `npm run test:public-verify`. `npm run test:interactive-layout` adds stateful public UI checks, including the compact generated-photo hero contract. `npm run test:checkout-experience` now covers open `/cart` and `/checkout` rendering in the current ecommerce testing mode; `npm run test:ecommerce-full` adds shop smoke, prices, variant media, and rollback-safe checkout backend contracts. Event Playground / PlayCanvas source work moved to `C:\Users\baenb\projects\design-studio\workstreams\locally-twisted-plan-custom-decor-v2\` and is no longer part of the ASAP website launch lane; the LT repo owns only the hidden Frappe wrapper and contact handoff. Its latest source handoff is `event-playground-v2` plus `design-studio-v1`, with quote math gated behind LT review. Treat `.planning/phases/01-customer-site-and-storefront/PLAN.md` as historical; `/contact` is still the primary quote/inquiry route and `/book` redirects to `/contact?intent=quick`.

**Operating law (2026-05-08):** if it can fail, it must fail loudly. Apply this to forms, automations, payments, documents, customer communication, containers, route contracts, verification, and agent handoffs. The project recipe is `capabilities/recipes/fail-loud-operating-law.md`; future queue items should name the verifier, Error Log, blocker field, mutation guard, route contract, or report row that makes failure visible.

**Public form email success rule (2026-05-12):** `/contact` and BTFP form
success requires current customer confirmation and owner/business notification
proof. Do not show `Request received` unless the backend returns `message.ok`,
and do not return `message.ok` unless the customer and owner Email Queue rows
exist for the current Lead or a current same-Lead queue row exists. Stale
`Email Queue` / `Communication` rows from an older reused Lead name are not
idempotency proof. Repeat same-email inquiries must be accepted; ERPNext's
unique Email Address link cannot turn a legitimate second inquiry into a 409.
Smoke proof must inspect customer-submitted details in both customer and owner
email bodies, not only queue flags. Handoff:
`workstreams/form-email-confirmation-regression-2026-05-12.md`; Failure
Recipes:
`capabilities/failures/public-form-stale-email-queue-idempotency.md` and
`capabilities/failures/public-form-repeat-email-lead-conflict.md`.

**Public form photo storage/owner attachment rule (2026-05-16):** inquiry
photos are not proven by a body count or a generic Lead `File` attachment.
They must exist as private Lead `File` rows, CRM-visible
`custom_inspiration_photos` rows, and owner-only Email Queue attachment refs.
Customer confirmations remain attachment-free and only report the received
count. Source fix was deployed to live in full repo `631f9a8` and app mirror
`b4b3bf8`; the accepted 2026-05-16 live smoke proved five private Files, five
CRM photo rows, owner Email Queue `683s86r04b` with five attachment refs, and
customer Email Queue `683suhfaa9` with zero attachment refs.
Handoff: `workstreams/inquiry-photo-storage-owner-attachments-2026-05-15.md`;
release handoff: `workstreams/inquiry-form-live-release-2026-05-16.md`;
capability:
`capabilities/recipes/erpnext-inquiry-photo-delivery-contract.md`; Failure
Recipe:
`capabilities/failures/public-form-photo-storage-owner-attachment-gap.md`.

**Public inquiry form spam/solicitation rule (2026-05-15):** `/contact` and
BTFP keep one shared `inquiry-v1` form. The form must render a signed
`lt_form_token` and invisible `website` honeypot; backend submit must reject
missing/too-fast/stale/honeypot posts before Lead creation, emails, or file
handling. High-confidence sales solicitations are soft-filtered: keep the Lead
and customer-safe confirmation path for audit/review, suppress only the owner
notification, and never block plausible event customers because they mention
corporate, marketing, school, nonprofit, decor, balloons, dates, guests, or
services. Source handoff:
`workstreams/inquiry-form-spam-sales-filter-2026-05-15.md`; capabilities:
`capabilities/recipes/shared-inquiry-form-experience.md`,
`capabilities/recipes/erpnext-intake-form-parity.md`, and
`capabilities/recipes/frappe-public-storefront-security.md`; guards:
`python scripts/verify/inquiry_spam_gate.py --base-url http://localhost:8081`
and
`python scripts/verify/inquiry_sales_solicitation_filter.py --base-url http://localhost:8081`.
This code is live as of `631f9a8` / `b4b3bf8`; the 2026-05-16 live smoke proved
the happy path, but not the dedicated live bot/sales fixture branches. Rerun the
spam and sales gates against live after any future form-security change.

**External review access rule (2026-05-15):** outside review accounts for
Locally Twisted use standard Frappe `Website User` accounts plus a narrow
explicit role, not custom User Types or Desk access. Current marketing lane:
`LT Marketing Review Access`, `desk_access = 0`, no DocPerm rows,
`/marketing-review` only, and `/me` redirect. Use explicit `Has Role`
membership for this boundary; do not rely on broad/effective role helpers that
can make Administrator look like every role. Feature handoff:
`workstreams/marketing-review-access-2026-05-15.md`; broader access audit:
`workstreams/user-access-audit-2026-05-15.md`; capability:
`capabilities/recipes/erpnext-external-review-access.md`; guard:
`npm run test:marketing-review-access`. 2026-05-21 follow-up: the protected
`/marketing-review` page now includes a backend-generated Marketing Review
Packet download with public review links, sitemap/robots links, and explicit
no-indexing/no-Desk/no-editing boundaries. The packet is sanitized and
marketing-only; do not attach customer data, backend exports, product source
records, invoices, orders, files, or Leads.

**Owner/support access focus (2026-05-15 GL correction):** the active access
track is the business owner's day-to-day use plus Cameron/Built by Cameron
support access. The only profiles that require active access design right now
are Jeff/business owner and Cameron/support. Manager, Employee, Accountant,
Customer, Maintenance Admin, Supplier, and Marketing Reviewer profiles stay as
documented boundary/audit profiles unless they directly protect or unblock
owner/support use. Keep this track contained to
`workstreams/user-access-audit-2026-05-15.md` and
`workstreams/erpnext-backend-simplification.md`; do not spread it into
commerce, paperwork, customer-portal, or public-site handoffs unless a specific
verifier, permission boundary, or owner workflow requires that cross-link.
2026-05-15 owner phone-action slice:
`workstreams/owner-phone-action-center-2026-05-15.md`. `LT Owner Home` now has
`Call or Text` leading to `/owner-actions`; local fake owner demo records are
managed by `python scripts/setup/sync_owner_demo_data.py`; provider-neutral
owner DTO/API boundaries are guarded by `npm run test:owner-actions` and
`python scripts/verify/owner_business_access_contract.py`. Future ChatGPT,
OAuth, API, MCP, or OpenAPI work must stay as adapters over this DTO boundary,
not direct raw ERPNext access.

**Operating law (2026-05-08):** no hand-authored production monoliths. Files should have one clear job unless they are explicitly research/reference artifacts. Use `workstreams/no-monolith-operating-contract.md` and the global capability `C:\Users\baenb\capabilities\principles\no-monolith-files.md` before expanding large source, template, CSS, verifier, script, or project-doc files.

**Verification surface note (2026-05-09):** public internet lookup, rendered browser proof, and LT route-contract verifiers are different evidence classes. Current handoff: `workstreams/browser-verification-runtime.md`; capability: `capabilities/recipes/codex-browser-verification-surface.md`. Use `web.run` for outside facts, repo-local Playwright/LT npm gates for rendered-route proof, and re-test Browser Use before claiming in-app browser control works.

**Playwright runtime rule (2026-05-12):** keep in-file Playwright parallelism
opt-in. Default `playwright.config.js` workers stay at `1` and
`fullyParallel` stays false because several LT specs share backend fixtures and
cleanup markers. Use `LT_PLAYWRIGHT_FULLY_PARALLEL=1` only for specs with
proven fixture isolation. Handoff:
`workstreams/playwright-verifier-runtime-2026-05-12.md`; Failure Recipe:
`capabilities/failures/playwright-in-file-parallel-fixture-race.md`.

**Cockpit priority correction (2026-05-09 GL):** the command-center/cockpit work exists to serve paid Locally Twisted infrastructure and website progress first, especially the ERPNext ecommerce receiving/product-page/backend ecosystem rebuild. LOOMTEM implementation is parked. Active cockpit source: `C:/Users/baenb/.openclaw/workspace/projects/lightdeck-command-center/workstreams/locally-twisted-paid-work-cockpit.md`.

**Fixture-data clarification (2026-05-07 GL; corrected 2026-05-11):** current visible/imported product records and verifier-created records are fixture/test evidence until GL explicitly approves a real catalog source/import. Do not call the client project or launch a test project. Fixture data is allowed; fake success is not. The system must prove every field/automation that can/should happen either happens or fails loudly with record-level evidence. Source lane: `workstreams/fail-loud-record-level-hardening.md`. First record-level backend slices are implemented: reusable recorder, Lead cascade blockers, inquiry upload rejection/failure blockers, checkout partial-failure blockers, paid-order missing-recipient receipt blocker, thank-you pending-reconciliation copy, external document send-readiness blockers, automation-index record health rows, synthetic contract coverage, the internal customer reminder Desk report, and the no-send customer/operator email policy boundary contract.

**Operations readiness note (2026-05-09):** product work is parked. The paperwork digest now reports company/operator, vendor/contractor, accountant/finance, and customer/user readiness rows and calls the automation index without runtime fake-data contracts so internal Desk/report review stays read-only. Remaining non-product blockers are setup/approval gates: Bank Account/default bank, Supplier/vendor records plus W-9 secure-send workflow, HRMS/payroll/provider approval, and customer reminder send approval.

**Finance backburner correction (2026-05-10 GL):** finance/banking/vendor/payroll/customer-reminder-delivery work is deferred indefinitely. Keep finance verifiers/report rows for visibility, but do not pick bank connection, reconciliation, Supplier/W-9 secure-send, payroll/HRMS, or customer reminder send-delivery implementation until GL explicitly reopens finance.

**Paperwork copy-routing rule (2026-05-09 GL corrected, delivery follow-up; public inbox map refreshed 2026-05-10):** customer-facing inboxes are role-based: `hi@locallytwisted.com` for general inquiry/web copy, `legal@locallytwisted.com` for legal/policy/accessibility copy and legal paperwork, and `billing@locallytwisted.com` for invoices, billing, refunds, payment reconciliation, accounts payable, and payroll. Code-owned internal paperwork copies still deliver to `locallytwisted@gmail.com` because Cloudflare routes `hi@locallytwisted.com` and `cameron@locallytwisted.com` back into the same Gmail account used as the SMTP sender. Do not use routed aliases for internal copies or one-time QA sends while the sender is `locallytwisted@gmail.com`; use a non-LT mailbox for Cameron QA review. `email_delivery_guard.py` blocks routed-alias loop sends at `Email Queue.before_insert`, including live probes that bypass the copy helper. Public inquiry acknowledgments now use the branded LT email shell with logo, mirrored red balloon-dog footer mark, no ERPNext standard footer, and dynamic public-form-only subject `Locally Twisted U+1F388 Thanks {first_name}! We'll be in touch within a day`; the form path defers confirmation until after uploads so it can echo non-empty submitted fields, free-text notes, and a reference-file count only when files attach. Do not reuse that playful subject for legal, billing, invoice, receipt, quote approval, operator, or other finance/legal emails. Paid receipts, first-order welcome, reviewed quote approval emails, and operator paid-order notifications now use restrained formal recipient-specific shells. Current customer-form print proof is one real queued five-photo confirmation ingested as a 1-page PDF at ignored path `output/email-print-fit/customer-form-confirmation.pdf`; other email families still need their own print-fit proof. Current code-owned coverage is `communication_copy_policy.py`, `customer_email_theme.py`, inquiry acknowledgments, paid-order receipts, paid-order operator notifications, first-order welcome emails, quote approval emails, and outbound document send-readiness blockers. Verification: `python scripts/verify/customer_email_policy_contract.py`, `python scripts/verify/customer_documents_contract.py`, `python scripts/verify/book_form_repeat_email_photos.py --base-url http://localhost:8081`, `python scripts/verify/payment_cascade_contract.py`, `python scripts/verify/product_quote_customer_delivery_contract.py`, and `python scripts/verify/outbound_document_send_readiness_contract.py`. Capability: `capabilities/recipes/customer-email-delivery-branding-contract.md`.

**Email preview review rule (2026-05-10 GL caught):** queued emails can correctly carry inline logo assets as `cid:` MIME parts, but standalone browser/PDF preview files cannot resolve those URLs. Before showing email review artifacts from `output/email-previews/` or `output/email-print-fit/`, rewrite inline image parts to embedded data URLs and run a browser image-dimension check so broken first-page logos fail loudly.

**Verifier cleanup rule (2026-05-10 Codex):** public-form proof scripts that create real ERPNext records must own cleanup. `scripts/verify/book_form_repeat_email_photos.py --base-url http://localhost:8081` now deletes old and current verifier-owned `lt-repeat-email-photo-*@example.invalid` Leads, uploaded Files, Communications, Email Queue rows, Contacts, Tasks, and Comments by default, and fails if cleanup is unavailable or incomplete unless `--keep-records` is explicit.

**Removed route rule (2026-05-11 GL/Codex):** `/event-balloons` is not a launch page. It should return 404 with no redirect, no sitemap entry, no canonical mapping, no search quick link, no footer link, no portfolio button, and no hero CTA. The four event audience pages remain live. Handoff: `workstreams/event-balloons-route-removal-2026-05-11.md`; guards: `scripts/verify/nav_ia.py` and `scripts/verify/seo_contract.spec.js`.

### Phase 1 — Customer site (lookbook-forward, with small shop)

See `.planning/phases/01-customer-site-and-storefront/PLAN.md` for the full slice list. Highlights:

**Done / current launch proof state:**
- Slice 3 — Homepage (launch proof shape, repaired 2026-05-07; featured-work band updated 2026-05-08; mobile review compactness updated 2026-05-08; seasonal carousel update 2026-05-10; Custom Event Decor hidden 2026-05-11; review platform proof and `/event-balloons` route cleanup updated 2026-05-11). The hero is now a five-slide quote-led carousel: graduation season first, then the four event audience lanes. The first slide owns the only page-level H1; subsequent slides use H2s. GigSalad, Google, and Facebook review proof sits immediately after the hero as unboxed platform logos with no visible counts and no visible `reviews` label; compact mobile review proof remains active. Inline cookie band stays after reviews, homepage trust/authority bar remains removed for now, `One of a Kind Designs` follows reviews as a wide custom-install proof band, review and client crawls move left-to-right at matched visible speed, Custom Event Decor is hidden behind `show_custom_event_decor = False`, and the closing CTA stays corporate/school/civic/community-first. Recovery assets for the hidden block live at `_resources/homepage-custom-event-decor-2026-05-11/`. Feature handoffs: `workstreams/landing-page-repair.md`, `workstreams/homepage-seasonal-hero-carousel-2026-05-10.md`, `workstreams/homepage-review-platform-proof-2026-05-11.md`, and `workstreams/event-balloons-route-removal-2026-05-11.md`; mobile compactness handoff: `workstreams/mobile-nav-review-compactness.md`; capability contract: `capabilities/recipes/homepage-launch-proof-contract.md`.
- Site shape decision: lookbook-forward + small shop sidebar, with future "Design Studio" interactive experience for arches/columns/garlands/backdrops/drops/bouquets categories (captures customer vision → routes to inquiry, NOT a checkout). See `.planning/decisions/site-shape.md`.

**Already DONE in prior sessions:**
- Slice 1 (brand foundation theme), Slice 2 (header + footer chrome), Slice 4 (BTFP page), Slice 5 (Contact page), Slice 6a (Accessibility statement). All form-bearing pages have AJAX → Lead + Communication wiring.

**Mirror Rebuild Phase 1 (Chrome) DONE 2026-04-30 evening:**
- Hetzner-shaped header + footer + 3 mega menus + mobile drawer + newsletter strip + `LT Newsletter Signup` DocType + endpoint + smoke test. 6 pre-task fixes (including unblocking /book). Triadic-construction-v2 + GL Proxy + fix round + audit pass. See `HANDOFF.md`, `MIRROR-REBUILD-COMPLETE.md`, `research/triadic-build-chrome-rebuild/` for receipts.

**Remaining (in priority order):**
- [P0] **Contact form local copy closeout.** Local copy-only contact changes are
  resolved and verified; live deploy/proof remains separate. Source handoff:
  `workstreams/contact-form-ux-readiness-2026-05-14.md`; audit packet:
  `workstreams/paperclip-change-audit-2026-05-15.md`. Latest local form gates
  passed on 2026-05-15, but live is still on the older form release and still
  needs Frappe Cloud deploy/site update plus live proof before production
  claims.
- [P0] **Ready-to-order ecommerce launch hardening and real catalog import gate.** Active front-door handoff: `workstreams/ecommerce-audit/README.md`; current sellable reimport closeout is the 2026-05-17 ecommerce audit handoff; import gate handoff: `workstreams/ecommerce-audit/product-import-hardening-gate-2026-05-11.md`; payment cutover checklist: `workstreams/payment-portal-live-cutover-checklist-2026-05-11.md`; receiving architecture handoff/capability: `workstreams/erpnext-ecommerce-receiving-architecture.md` and `capabilities/recipes/erpnext-ecommerce-receiving-architecture.md`. Current local proof is superseded by the 2026-05-24 taxonomy result for category counts: 51 published products, 30 checkout products, 21 quote-first products, and 2 duplicate source slugs excluded from the import subset. The approved local reimport completed against the local ERPNext `frontend` site only after fresh backups and guard evidence; it is not a staging/live release. Browser proof covered the product page, cart, and checkout preview paths. Product-level Website Item contracts now outrank stale item-group/category lane fallback in product pages, shop cards, and cart display rows. Read this lane together with the 2026-05-19 price-identity incident below: source-price truth now requires the broad modifier and visible price guards, not only the original import/browser proof. Current media caveat: product-page gallery media is restored through Product Setup and Website Slideshow; category/reference media and 9 review-only add-on controls remain separate approval/mapping lanes. Current product records are still local import/proof evidence until GL completes local testing and explicitly approves any live release; live Frappe Cloud/Stripe/DNS/webhook/real payment gates remain separate.
  2026-05-12 nav/search review closeout is `workstreams/ecommerce-audit/ready-to-order-nav-search-backend-gate-2026-05-12.md`: Ready-to-Order quick links now require owner include plus backend `simple_product|checkout`, owner include cannot bypass checkout eligibility, and the search contract treats filtered backend-approved links as hidden rather than removed from the DOM.
  2026-05-14 product blueprint authoring handoff is `workstreams/ecommerce-audit/product-blueprint-authoring-2026-05-14.md`; capability is `capabilities/recipes/erpnext-product-blueprint-authoring.md`. Employees can now define product basics, options, color recipes, add-ons, and conditional pricing in `LT Product Blueprint`, preview a no-write apply plan, and use guarded local Desk apply to create unpublished ERPNext product records. Local `frontend` has `lt_allow_local_blueprint_apply=1` for this test harness. Do not enable that gate on staging/live or publish generated Website Items without product-page browser proof, cart/checkout proof, media/conditional-pricing/add-on family mapping, refreshed import safety evidence, and explicit release approval.
  2026-05-15 generic Product Setup runtime handoff is `workstreams/ecommerce-audit/generic-product-setup-runtime-2026-05-15.md`: selection groups are generic, SKU-defining axes resolve to ERPNext variants, configuration-only groups stay out of variant generation, setup schemas/API feed the product page, cart/checkout validates server-side, Sales Order/Sales Invoice/Quotation records preserve structured details, approved media rules can drive customer images, and `LT Owner Home` Add Product opens Product Setup. 2026-05-17 proof now verifies `Item Manager`, `System Manager`, and the real owner account can create/apply local Product Setup without raw Website Item access; a 48-variant employee-authored proof product supports single-selection and combination media rules; and one real local Stripe test-card purchase proved selected image parity from product page to cart, checkout, Sales Order JSON, Stripe Checkout, paid invoice, and receipt email before restoring `lt_ecommerce_paused=1`. Remaining gates are fresh import snapshot/readiness, staging/live Stripe/webhook/payment approval, and final product scope approval.
  2026-05-17 product source repair map is `workstreams/ecommerce-audit/product-source-repair-map-2026-05-17.md`; the 2026-05-24 taxonomy result now supersedes the old all-product count for category work: 51 published products, with 2 duplicate source slugs intentionally excluded.

- [P0] **Complex product-page controls, add-ons, media, and browse follow-through.** Active storefront
  handoff: `workstreams/ecommerce-audit/storefront-proof-and-complex-ui-handoff-2026-05-11.md`.
  Current local scaffold:
  `workstreams/ecommerce-audit/complex-checkout-scaffold-2026-05-12.md`.
  `python scripts/verify/complex_checkout_scaffold.py` previously passed with 53
  direct checkout guards, 0 simple lane flips, 0 complex UI blockers, 0
  add-on/conditional product blockers, and 0 needs-review products after the
  sellable reimport. Re-run before using it as current proof. Remaining work is narrower: classify/approve 95
  extra images, map 9 hidden review-only add-on controls into explicit priced
  add-on contracts where GL wants them exposed, keep backend-driven media
  updates and cart/checkout/receipt summaries green, and preserve the all-53
  browser proof while GL tests locally.

- [P0] **Website launch workstream.** Active launch coordination lane at `workstreams/website-launch.md`. Goal: get the public site and inquiry path live today, with ecommerce hidden if needed and preserved for follow-up. Navigation correction handoff: `workstreams/nav-btfp-process-correction.md`; removed hub route handoff: `workstreams/event-balloons-route-removal-2026-05-11.md`; active canonical-service guard handoff: `workstreams/nav-service-removal-guard.md`; mobile search/review compactness handoff: `workstreams/mobile-nav-review-compactness.md`; BTFP service page/form/calculator handoff: `workstreams/btfp-service-page.md`; FAQ service-lane handoff: `workstreams/faq-service-lane-rewrite.md`; public microinteraction handoff: `workstreams/public-site-microinteractions.md`; current menu label source: `workstreams/menu-content-coordination.md`. Current header/menu has `Twisting & Face Painting` pointing to `/balloon-twisting-and-face-painting`, the event dropdown pointing only to the four audience routes, `Contact Us` pointing to `/contact`, and top-banner `Free Event Quote` pointing to `/contact` beside the account link. Ready-to-Order is config-gated: hidden in the current pages/forms-first launch posture and restored when ecommerce is reopened. The 24-hour short-notice message is a centered deep-navy `/contact` link on desktop and a matching visible deep-navy `/contact` strip on mobile; the old prepared-design proof copy and delivery/truck icon are removed. Removing, hiding, renaming, or replacing the BTFP lane requires the exact approval marker in `workstreams/nav-service-removal-approvals.md`; `scripts/verify/nav_ia.py` fails without it. Keep `/event-balloons` and `/process` out unless GL explicitly reopens them. Keep mobile search at the bottom of the drawer, not in the mobile header action row. Current hidden-commerce launch proof: `python scripts\verify\website_launch_verify.py --with-a11y --with-contact-smoke` passed 15/15 steps and `python scripts/verify/ecommerce_pause_contract.py` passed. Ignored `.tmp` preflight snapshots are not retained after launch cleanup; rerun the snapshot command when fresh local evidence is needed. Open ecommerce proof remains available through `npm run test:ecommerce-full` when the switch is reopened.
- [P0] **Public storefront security hardening.** Active handoff: `workstreams/public-site-security-hardening.md`; capability: `capabilities/recipes/frappe-public-storefront-security.md`. The 2026-05-08 security review reproduced `/shop?q=` reflected XSS, unauthenticated `/thank-you?order=<Sales Order>` order-summary exposure, a public Lead attachment URL, tracked local credentials in docs, pre-payment guest checkout Lead conversion, and an unauthenticated `/event-playground?port=` internal preview bridge. Fixed now: `/shop?q=` escaping, product-gallery image rendering, new private inquiry uploads, checkout Lead conversion delayed until the paid-order cascade, and Event Playground guest/auth gating. GL clarified current data/files are fake, the order-summary and existing public fake-file findings are not immediate launch blockers for this balloon business/fake-data state, and GL owns credential rotation/doc cleanup. Remaining: credential rotation before broader sharing/cutover, optional token-bound receipt hardening before real customer cutover, and fake public Lead file cleanup if the test files should not remain.
- [P0] **Paperwork and backend automation workstream.** Active coordination lanes at `workstreams/paperwork-backend-automation.md`, `workstreams/business-automation-index.md`, `workstreams/synthetic-business-pipeline.md`, `workstreams/customer-reminder-dry-run.md`, `workstreams/customer-reminder-review-report.md`, and `workstreams/fail-loud-record-level-hardening.md`. Fresh 2026-05-08 baseline verified finance inventory, customer document policy blocks, paid-order cascade, CRM stage guardrails, payment config/webhook/local readiness, checkout-to-Lead conversion, Accountant Home parity, the read-only `scripts/verify/paperwork_status.py` report, AP-friendly black/gray Sales Invoice output through `scripts/setup/sync_invoice_branding.py` + `scripts/verify/invoice_branding_contract.py`, the answer-first standard outbound document registry through `scripts/verify/outbound_documents_contract.py`, external document send-readiness blockers through `scripts/verify/outbound_document_send_readiness_contract.py`, and draft-only quote/proposal packets through `scripts/verify/quote_proposal_draft_packet_contract.py`. `scripts/verify/product_quote_operator_review.py --report output/product-quote-operator-review.json` and `scripts/verify/product_quote_operator_review_contract.py` now cover no-send product-page quote operator review readiness without Sales Orders, invoices, Payment Requests, or customer acceptance. `scripts/verify/customer_email_policy_contract.py` statically proves inquiry acknowledgment, paid receipt, operator notification, first-order welcome, and payment-cascade email policy/no-PDF boundaries without customer sending, Email Queue creation, or invoice mutation. `scripts/verify/maintenance_heartbeat.py` verifies the sanitized client operations heartbeat, owner-selected notification topics/cadence surface, approval tiers, and Maintenance Admin raw-log/customer-data boundary. `scripts/verify/unpaid_invoice_review.py --report output/unpaid-invoice-review.json` now produces draft-only reminder/statement candidates for unpaid or overdue invoices, and `scripts/verify/unpaid_invoice_draft_packet.py --report output/unpaid-invoice-draft-packet.json` renders those candidates into draft-only human-review packet sections while proving no customer send or accounting mutation happens. `scripts/verify/unpaid_invoice_draft_packet_contract.py` covers normal/outlier packet behavior with fake data, including missing payment links and malformed approval gates. `scripts/verify/paperwork_review_digest.py --report output/paperwork-review-digest.json` combines paperwork status, automation index, unpaid invoice review, and draft packets into one read-only internal review payload. `scripts/verify/customer_reminder_dry_run.py --report output/customer-reminder-dry-run.json` builds a no-live internal reminder queue with cadence suggestions, draft sections, and customer-send blockers; `scripts/verify/customer_reminder_dry_run_contract.py` covers overdue/current/missing-payment-path/malformed-send scenarios with fake data. `scripts/verify/customer_reminder_review_report.py --report output/customer-reminder-review-report.json` turns the dry-run queue into no-live report rows and review/hold/blocked groups, and `scripts/verify/finance_workspace_parity.py` now proves those rows are reachable through the internal `LT Customer Reminder Review` Desk report; `scripts/verify/customer_reminder_review_report_contract.py` covers mixed/empty/malformed-send source scenarios with fake data. `scripts/verify/record_level_failure_contract.py --report output/record-level-failure-contract.json` proves rollback-safe record-level backend failure evidence, `scripts/verify/inquiry_upload_failure_contract.py --report output/inquiry-upload-failure-contract.json` proves rejected inspiration photos produce customer-visible and Lead-level evidence, and `scripts/verify/payment_success_reconciliation_contract.py --report output/payment-success-reconciliation-contract.json` proves paid browser-return reconciliation errors show pending receipt/invoice copy on `/thank-you`. `scripts/verify/synthetic_business_pipeline.py --report output/synthetic-business-pipeline.json` is the no-live pipeline gate: it runs fake-data/rollback-safe contracts for record-level failure evidence, inquiry upload failure evidence, product add-on dependency boundaries, product quote operator-review outliers, Stripe amount parity, checkout-to-Lead conversion, checkout fulfillment, paid-order cascade, payment-success pending reconciliation, mocked webhook behavior, customer documents, customer email policy boundaries, outbound templates, outbound send-readiness, quote/proposal outliers, unpaid invoice outliers, customer reminder dry-run outliers, and customer reminder report outliers, with zero broken piping in the latest run. `scripts/verify/business_automation_index.py --report output/business-automation-index.json` indexes intake, CRM, checkout, payment, paperwork, finance, and checkup surfaces plus record-level backend blockers; current result is 27 indexed surfaces, 12 launch-required, 24 connected, 3 exists-but-not-connected, 0 launch-required missing, 0 useful future surfaces missing, and 0 loud-failure gaps. The product quote operator-review surface is split into `apps/locally_twisted/locally_twisted/verify/business_automation_product_quote.py` so the main index stays a registry. The Frappe scheduler runs the business automation checkup daily plus the maintenance heartbeat light check hourly and full check daily, and `stripe_amount_parity_contract.py` guards Stripe Checkout totals against ERPNext Sales Order totals. External document standards live at `capabilities/recipes/external-document-audience-contract.md`; source templates and send-readiness gates live at `apps/locally_twisted/locally_twisted/outbound_documents/`, where every outbound family must answer the recipient's practical question first and block send until recipient, approval, branding, payment path, and required business fields are present. Synthetic/test operating readiness is healthy without live inputs; live Stripe keys, webhook secret, production host, and real operator/customer data are cutover-only, not current fake-data blockers. Bank account, suppliers/vendors, payroll/HRMS, reminder approval, and manual stage-to-finance thresholds are still incomplete. Next safe slice: keep no-send paperwork/reporting verifiers green while avoiding approval-gated vendor, bank, payroll, customer quote sending, and customer reminder delivery work.
- [P0] **Brand style-guide implementation follow-through.** Source authority is consolidated in `_resources/STYLE-GUIDE.md` v4.6 and `workstreams/brand-style-guide-consolidation.md`; the old `_resources/design-guide/`, stale shop/spec comparison docs, and generic icon comparison are gone. The 2026-05-05 rendered-site repair pass restored the deliberate premium mega-menu, loaded the menu/containment/product CSS through Frappe hooks, and verified public route fit with `smoke_shop.py`, `nav_ia.py`, `layout_fit` 260/260, `interactive_layout` 39/39, and post-fix screenshots. The 2026-05-07 nav correction restored the approved `Twisting & Face Painting` service route and removed the unapproved standalone `/process` route; the 2026-05-10 service-removal guard pass keeps `Twisting & Face Painting`, `Ready-to-Order`, and `Contact Us` in the primary header/menu when ecommerce is open for testing, with `Free Event Quote` retained in the desktop top banner and the 24-hour short-notice banner guarded as deep-navy linked desktop/mobile chrome. The 2026-05-11 route cleanup removed `/event-balloons` with no redirect while preserving the four event audience pages. Current launch posture hides `Ready-to-Order` and cart behind `lt_ecommerce_paused=1` while preserving that open-ecommerce proof for follow-up. Latest full closeout verification passed with `python scripts\verify\website_launch_verify.py --with-a11y --with-contact-smoke`; the run passed 15/15 hidden-ecommerce launch steps, including `layout-fit` 325/325, `container-contract` 75/75, `interactive-layout` 163/163, search, portfolio, pause contract, shop pause smoke, product prices, variant media, checkout experience, accessibility, and contact smoke backend proof/cleanup. `npm run test:ecommerce-full`, `python scripts/verify/synthetic_business_pipeline.py`, and `python scripts/verify/business_automation_index.py` remain the paired ecommerce/backend proof gates when ecommerce is reopened. Compact heroes are now a launch rule and agency rule: `/`, the four event audience pages, `/portfolio`, `/balloon-twisting-and-face-painting`, `/contact`, `/shop`, and `/shop-items/<group>` use the 220px mobile / 250px tablet / 280px desktop contract plus breakpoint-specific generated lifestyle photo crops under the black landing-page readability overlay, guarded by `interactive_layout.spec.js` and `capabilities/recipes/compact-hero-contract.md`. Reserved real/proof photos are not hero sources. Public containers are now an executable route contract guarded by `container_contract.spec.js`; any new visible direct `.page_content` child must be declared in `CONTAINER_CONTRACT_ROUTES` before closeout. Container/breakpoint integrity has its own lane at `workstreams/responsive-container-integrity.md` and capability recipe at `capabilities/recipes/responsive-container-audit.md`. The 2026-05-06 shop showroom repair now treats category UX and symmetry as product-showcase requirements: `/shop` and `/shop-items/<group>` use the shared desktop category rail/native mobile select instead of a chip wall or top button wall, and product grids avoid avoidable lone orphan cards while keeping product photos large when ecommerce is open. `/portfolio` now has a proof-first collage reel and route verifier at `npm run test:portfolio-reel`; the page keeps the large imagery/center-column balance, uses no captions, no frame wrappers, no route-specific contact/index footer block, keeps mobile full-width slide-in reveal, and obeys the sitewide compact hero contract. Remaining: review portfolio/photo order and quality with GL/Jeff/designer, review category/product imagery with GL/Jeff using the regenerated `output/category-media-candidates.md` packet, verify exact review/trust counts before launch copy is treated as final, and continue photo edits toward the Image #3 quality bar. Do not reopen the old pastel/rainbow/light-blue/blush identity unless GL explicitly reverses the Civic + Slate/Berry + Brand Direction decision.
- [P0] **Shop category hero/color catalog follow-through.** Route hero slice is complete locally and refreshed for the 2026-05-24 taxonomy: all 8 active `/shop-items/<group>` compact heroes use generated category-specific WebP crops prompted from owner-approved balloon color names and swatch references, not hex-only prompts. Handoff: `workstreams/ecommerce-audit/shop-category-hero-imagery-2026-05-22.md`; source catalog: `_resources/STYLE-GUIDE-BALLOON-COLOR-ADDENDUM.md`; capability: `capabilities/recipes/lt-balloon-color-generated-hero-contract.md`; verifier: `scripts/verify/shop_category_hero_images.spec.js`. Remaining: GL local visual review before any release gate. This does not approve ERPNext Item Group `image` fields or future category card/mega-menu photos.
- [P0] **Portfolio/photo finishing lane.** Desktop next: make the existing portfolio photos feel more professional without changing density or captions. Add consistent light color grading/post-processing direction, subtle per-photo vignette if it improves polish, all-photo shadow depth, stronger shadow logic when a back photo is selected and brought forward, and a guard that front photos never cover the hero. Keep this desktop-only until verified; mobile needs its own separate design pass rather than a squeezed desktop treatment. Verify with `npm run test:portfolio-reel` plus the relevant public layout gate after implementation.
- [P0] **White-label platform leakage follow-through.** Public/login visible text, menu states, favicon/logo chrome, reduced-motion proof crawls, and the generated platform banner/meta now have a guard in `scripts/verify/interactive_layout.spec.js`; `nav_ia.py` blocks the specific Ready-to-Order platform-copy regression. The local owner/client Desk route now defaults to `LT Owner Home`, assigns owner roles directly instead of using a destructive role profile, preserves the Built by Cameron support/admin roles, hides public platform-named workspaces, removes platform support links from the Desk help menu, and is guarded by `npm run test:desk-owner` plus `scripts/verify/backend_workspace_parity.py`. Remaining source-level exposure is deeper framework plumbing such as required `/assets/frappe`, `/assets/erpnext`, `frappe.boot`, and inline login command identifiers, plus any non-owner admin route a client might be given. Next safe slice: audit the exact role/account Jeff will use at cutover and decide whether technical source-path rewriting is worth the fragility.
- [P1] **Commerce rules and checkout policy follow-through.** Active lane at `workstreams/commerce-rules-checkout.md`; capability recipe at `capabilities/recipes/erpnext-checkout-commerce-rules.md`. Local ecommerce may be opened temporarily for proof runs, but the safe resting state is `lt_ecommerce_paused=1`; checkout policy changes must be tested through the actual cart/checkout flow plus rollback-safe backend contracts. Production launch still waits for GL local acceptance, staged review, and live payment/cutover approval.
- [P0] **Ecommerce price identity incident and catalog variant price recovery.** Active incident lane: `workstreams/ecommerce-price-identity-incident-review-2026-05-19.md`; recovery handoff: `workstreams/catalog-variant-price-recovery.md`; capability: `capabilities/recipes/erpnext-catalog-variant-price-parity.md`; failure recipe: `capabilities/failures/ecommerce-variant-price-source-drift.md`. GL caught `easter-balloon-arch-bunny-ear` showing the same price for `20ft` and `25ft`. Root cause: older import/verification proved variant shape, Item Price existence, and downstream ERPNext/Stripe consistency, but did not block source-price drift from legacy_source's dynamic `/website_sale/get_combination_info` logic. Local containment on 2026-05-19 corrected the reported variants (`20ft=$375`, `25ft=$440`) and applied legacy_source option price modifiers across 49 variant products / 10,186 active variants, correcting 8,405 local `Item Price` rows with 0 remaining dry-run changes. Guards now include `npm run test:product-prices`, `npm run test:product-price-display`, and the broad modifier gate inside `scripts/verify/website_launch_verify.py`. Current truth: local source-price parity is guarded for the active variant set; staging/live/public pricing is not approved until target-site source-price proof, cart/checkout/order/payment cascade proof, GL local acceptance, and separate live payment/cutover approval pass.
- [P0] **ERPNext Backend simplification and access hardening workstream.** Multi-handoff lane at `workstreams/erpnext-backend-simplification.md`; latest access audit at `workstreams/user-access-audit-2026-05-15.md`. GL correction on 2026-05-15: this lane's active center is business-owner use plus Cameron/Built by Cameron support access. Owner keeps the command center plus secondary catalog tools; `cameron@builtbycameron.com` keeps support/admin capability for build and maintenance. Manager, Employee, Accountant, Customer, Supplier, Maintenance Admin, and Marketing Reviewer are boundary profiles, not active UX tracks, unless they directly protect or unblock owner/support use. The 2026-05-15 live permission matrix found no User Permission rows and confirmed current restrictions are role/profile/workspace/portal/hook based; it also found Manager still has `Item Price` create/write/delete through ERPNext roles even though catalog tools are hidden from the workspace. Guards: `python scripts/verify/backend_workspace_parity.py`, `python scripts/verify/finance_workspace_parity.py`, `python scripts/verify/custom_doctype_permission_boundary.py`, `python scripts/verify/maintenance_admin_boundary.py`, `npm run test:desk-owner`, and `npm run test:desk-personas`. Lead photo table wiring, first stale Lead-script cleanup, idempotent workspace sync, the six-stage custom CRM pipeline, non-financial stage-to-Task cascades, repeatable backend schema inventory, and checkout/Lead conversion parity are done. Next safe slice: verify the exact Jeff/business-owner cutover account and owner daily path first, keep Cameron/support access intact, then add failing permission-matrix verifiers only for exposure that affects those two required profiles. Do not broaden this into manager/employee/accountant/customer/marketing feature work or stage-to-finance automation without a specific owner workflow or permission-boundary reason.
- [P1] **Customer/client portal translation.** Active handoff: `workstreams/customer-client-portal-translation-2026-05-10.md`. Current verified state: `/login#login` is a branded LT customer account doorway with working Frappe Website User authentication, `/login#signup` is branded invite-only help, guest `/me` is blocked, public signup is disabled, guest shop/cart/checkout remain open, and signed-in users have visible logout exits in public header/mobile drawer plus LT account surfaces. The customer portal is now LT-owned: `/me`, `/account/events`, `/account/quotes`, `/account/billing`, `/account/files`, `/account/checklist`, `/account/repeat`, `/account/follow-up`, plus separate organization routes under `/organization`. Portal Settings/menu sync is code-owned through `apps/locally_twisted/locally_twisted/seed/sync_customer_portal.py` and `scripts/setup/sync_customer_portal.py`; old native `/quotations`, `/orders`, `/invoices`, and `/addresses` menu rows are disabled and compatibility-routed to LT-owned pages. Backend contract: `customer_portal.py` resolves User -> Contact -> Customer and returns allowlisted summaries; customer edits/repeat requests create `LT Customer Change Request`, files require same-user/same-source ownership before `LT Customer Portal File` can be created, checklist state uses `LT Customer Checklist Response`, and organization access requires `LT Organization Portal Membership`. Guards: `npm run test:customer-login-visual`, `npm run test:customer-portal-visual`, focused `interactive_layout.spec.js` logout coverage with `LT_DESK_TEST_USER`/`LT_DESK_TEST_PASSWORD`, `python scripts/verify/customer_portal_v1_contract.py`, `python scripts/verify/customer_portal_home_contract.py`, `python scripts/verify/customer_account_provisioning_contract.py`, and `python scripts/verify/customer_portal_inventory.py --base-url http://localhost:8081 --strict-menu --report output/customer-portal-inventory.json`. Remaining safe slices: reviewed account-invite email sender, richer per-record detail pages, customer-visible upload UI after file policy approval, and organization AP/people workflows after GL/Jeff approval. Do not turn on public signup or require login for inquiry/cart/checkout.
- [P0] **Finance/payroll/QuickBooks migration workstream.** Active lane at `workstreams/finance-payroll-quickbooks-migration.md`, now coordinated by the paperwork lane for launch. First slice added read-only finance inventory, Accountant Home finance cards, reminder-review report access, and parity checks. Accountant Home now intentionally hides bank, supplier/vendor, payment-term, statement-reminder, and employee/payroll shortcuts until those lanes are approved and populated. Fresh 2026-05-06 inventory shows Payment Terms exist, but Bank Account, Suppliers, and payroll/HRMS setup are still missing. Next: GL/accountant approval for QuickBooks export scope, bank import path, payment terms/reminder timing, HRMS payroll evaluation, and contractor/1099 reporting. Do not auto-submit finance records, send reminders, enable bank sync, or claim payroll readiness before those gates are approved and verified.
- [P0] **Blog channel index + 2 ported posts.** Use Frappe's NATIVE `Blog Post` DocType (NOT a custom one — plan-deepen 2026-04-30 caught the regression). Add `tags` field via `Customize Form` linking to a tiny `LT Blog Tag` DocType. Override `templates/pages/blog_post.html` for SEO meta tags Frappe's native template doesn't emit.
- [P1] **Catalog media reconciliation follow-up.** PARKED at the 2026-05-06 stopping point until GL/Jeff photo approval. First launch-safe pass completed 2026-05-02: `scripts/setup/sync_variant_media.py` staged the source image set, `locally_twisted.seed.sync_variant_media` mapped 1,712 variant `Item.image` values where source image labels clearly matched size/height/length/design/lights/topper/theme options, and product pages now swap images through `locally_twisted.api.variant_media`. Refreshed detailed review report on 2026-05-06 with `python scripts/setup/sync_variant_media.py --dry-run --include-details --report output/catalog-media-review.json`; latest report checked 49 products, found 35 with candidate image labels, flagged 45 for review, left 1,712 mapped variants unchanged, and skipped 6,831 assignments that were not safe to infer. `python scripts/verify/category_media_candidates.py` now generates a no-mutation category-image review packet for the 8 active customer-facing Item Groups, and `scripts/setup/sync_category_media.py` provides the dry-run-first post-approval assignment path. Resume only by reviewing skipped/unmatched products and approving category imagery with GL/Jeff; do not assign photos by judgment. Do not treat unmapped products as missing if the source labels are not specific enough.
- [P1] **Localo marketing resource mining.** GL/Jeff confirmed 2026-05-02 that `https://locally-twisted.localo.site/` is tied to Jeff's marketing company and the material is Locally Twisted's to use per contract. Use `workstreams/localo-secondary-site-inventory.md` as the source lane. Localo is not the brand and should not be a customer destination; mine photos, review themes, proof structure, service language, social links, and SEO clues. If linking publicly, link only to `https://locally-twisted.localo.site/reviews` as multi-site review-trust proof. Keep a source log; prefer original/highest-quality files where available; rewrite blog/service copy before publishing; verify phone/address/hours/website links before launch. Known stale fact: Localo shows Tuesday closed, but Jeff confirmed LT is open Tuesdays.
- [P1] **Newsletter X-Forwarded-For strip at nginx layer (Option B).** Option A (email-keyed rate limit) shipped on `/api/method/locally_twisted.api.newsletter.signup` this session. Option B would protect `/contact`, `/checkout`, `/balloon-twisting-and-face-painting` too — they all use IP-based `@rate_limit` and share the same XFF-spoofing vulnerability. Ops/infra task: edit nginx config to strip/overwrite X-Forwarded-For before forwarding to gunicorn. See `Built_by_Cameron/built-by-cameron-decisions.md` 2026-04-30 entry "Frappe `@rate_limit` IP+key combine into ONE identity, not two."
- [P1] **`/privacy` + `/terms-of-service` Stripe Dashboard wiring.** Pages now exist locally; after GL/legal approval, update Stripe Dashboard's "Privacy policy URL" + "Terms of service URL" (currently `example.com/...` placeholders blocking live-mode activation).
- [P1] **Category browse imagery.** Route hero slice is complete locally and refreshed for the 2026-05-24 taxonomy: all 8 active `/shop-items/<group>` pages have generated category-specific compact hero WebP crops, prompted from owner-approved balloon color names and swatch references. Current handoff: `workstreams/ecommerce-audit/shop-category-hero-imagery-2026-05-22.md`; color catalog: `_resources/STYLE-GUIDE-BALLOON-COLOR-ADDENDUM.md`; verifier: `scripts/verify/shop_category_hero_images.spec.js`. Still parked for ERPNext Item Group/category-card media: live DB `image` fields remain unchanged and unapproved. A no-mutation approval packet can be regenerated with `python scripts/verify/category_media_candidates.py`; `python scripts/setup/sync_category_media.py --write-template` creates the approval template and `python scripts/setup/sync_category_media.py --selection output/category-media-selection.template.json` dry-runs the Frappe update path. Do not run `--apply` or assign live Item Group images until GL/Jeff explicitly approve selections. Do not revive the retired `/shop-by-category` card index for launch; use representative category media for category cards or a future image-rich mega-menu only after photos are selected.
- [P1] **Slice 8 — Service category pages.** `/services/<event-type>` × 5 (Corporate, Weddings, Birthdays, Schools, Seasonal). Each ends with inquiry CTA to `/contact`.
- [P1] **Slice 9 — Color Chart page.** `/color-chart` remains pending as a public route, but the source catalog now exists in `_resources/STYLE-GUIDE-BALLOON-COLOR-ADDENDUM.md`: 53 owner-approved latex colors, swatch refs, drawers, and best web-match hex values. Build the public page from that addendum, not from guessed CSS colors or hex-only image prompts. Visual swatch grid + print-friendly stylesheet.
- [P1] **Sample data for backend tour.** First owner phone-action seed exists
  for localhost: `python scripts/setup/sync_owner_demo_data.py` creates marked
  fake Leads, one Customer/Contact, and one draft upcoming Sales Order for
  `/owner-actions`. Follow-up only if Jeff needs broader Desk-tour data such
  as completed orders or post-event history. Cleanup:
  `python scripts/setup/sync_owner_demo_data.py --cleanup`.
- [P2] **Slice 13 — Blog framework + 2-3 first posts.** "Kindergarten Teacher" voice. Deferrable. The homepage hero is a seasonal/audience carousel; do not reintroduce cycling blog titles into the launch hero.
- [P2] **Variant cache rebuild on Webshop Settings change.** If the next instance enables/disables variants or attribute filters, run `for template in templates: ItemVariantsCacheManager(template).rebuild_cache()` to flush stale Redis state.
- [P2] **Visual asset generation/source cleanup.** Non-urgent tangent pinned 2026-05-02. Revisit Facebook/Instagram/X icon assets as one small slice of the larger visual asset system after the higher-priority Localo/resource-mining work. Use the global capability recipe at `C:\Users\baenb\capabilities\recipes\safe-visual-asset-sourcing-and-generation.md` for icons, SVGs, generated lifestyle images, representative balloon decor renders, blog visuals, proof-photo handling, rights checks, post-production, and site verification.
- [P1] **Workspace asset intake cleanup.** Triage any future untracked LT asset drops before new visual work. 2026-05-10 launch cleanup moved raw local photo drops `assets/landing page pics/` and `assets/New Balloon Pics 3.7.26/` out of the repo to `C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\locally-twisted-local-drops\` and added ignore guards so they do not re-enter the launch worktree. 2026-05-11 follow-up removed duplicate tracked raw launch photos from `assets/what we do photos/` after exact blob matches were verified in `C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\locally-twisted-local-drops\landing-page-pics-20260510\`. Remaining raw/drop candidates named in older queue entries, such as `assets/landing page assets/`, `assets/hero assets/`, or loose logo source PNGs, should be either committed intentionally as production/source assets, moved to the same local holding area, or deleted after review. Do not leave floating untracked assets as a second source of truth. The red dog cartoon source used for the favicon is kept with the committed favicon source set. Cleanup handoff/capability: `workstreams/launch-repo-cleanup-2026-05-10.md` and `capabilities/recipes/launch-repo-cleanup-and-evidence-retention.md`.
- [P6] **Phase 6 cutover work item — fixture pruning.** BEFORE Jeff's first post-takeover deploy, REMOVE operator-state-sensitive Item Attribute fixtures from `hooks.py fixtures = [...]` (especially `latex colors` — 51 values Jeff is most likely to edit as supplier inventory shifts). Otherwise BBC fixture sync silently overwrites his renames on every `bench migrate`. Document in `NOUPDATE-DRIFT.md` (TBD). See `locally-twisted-decisions.md` 2026-04-30 entry.

**Slice numbering (current state):** 1-7 done (brand, chrome, homepage, BTFP, Contact, Accessibility, Refund+FAQ, Lookbook). Slice 8 (service categories), Slice 9 (color chart), Slice 13 (blog) — PENDING. Slice 10 (`/book`) is retired; `/contact` is the primary inquiry route and `/book` redirects to `/contact?intent=quick`. Slice 11 (browse) + Slice 12 (cart+checkout) DONE. **2026-04-30 catalog port shipped on top of Slice 11/12** — original catalog baseline was 53 Website Items, 10,578 raw/customer variants, and 10,613 catalog Item Prices. Current local DB totals were rechecked on 2026-05-18 as 53 Website Items, 10,686 Items, 10,186 active customer-facing variants, 443 disabled variant records, 10,629 all variant records, and 10,668 Item Prices after delivery service Items, support Items, the optional-add-on bouquet repair, and the college color preset repair. Product detail, mega menu, `/shop` hub, and category detail pages are built. `/shop-by-category` is now a compatibility redirect to `/shop`. See `locally-twisted-decisions.md` 2026-04-30 and 2026-05-02 entries. Historical "Already DONE" entries removed from queue per the "GitHub is our archive" rule — `git log` is the changelog.

### Future scope (post-Phase 1)

- [P1] **Event Playground review and V1.1 hardening.** Source work is parked in the standalone design-studio repo at `C:\Users\baenb\projects\design-studio\workstreams\locally-twisted-plan-custom-decor-v2\`; LT only owns the hidden `/event-playground` Frappe wrapper and contact handoff in `workstreams/event-playground.md`. Latest research source reframes the browser preview as `Plan Custom Decor`, emits `event-playground-v2`, carries a nested `design-studio-v1` adapter contract, and shows quote-honesty warnings. Keep this out of the ASAP website launch lane unless GL explicitly reopens it here. Backend saves, automatic Lead/Quote/Sales Order creation, pricing, checkout, room scanning, share links, and full organic/twisting physics remain out of scope until deliberately approved.

- **Event Playground / Design Studio expansion for customizable categories** (arches, columns, garlands, backdrops, drops, bouquets). 6th category (Bouquets) added 2026-04-27 per GL — bouquets are also customizable. V1 route is game-like PlayCanvas event planning, not checkout. Future source/prototype work belongs in `C:\Users\baenb\projects\design-studio\`; only final Frappe integration outputs should return to this LT repo. Future work can add honest organic/twisting engines, richer prop packs, venue libraries, branded signs, vendor booths, people groups, sponsor tables, and proposal templates. Output remains inquiry/planning payload unless a later finance/pricing decision changes that. Do not surface render balloon counts as final quote/manufacturing counts; production estimates stay internal and `quote_ready: false` until LT approves the formulas.

### First-ship omissions to revisit (deliberate deferrals)

- [P2] **Symmetry fix for Custom Creations on mobile** — currently 2-2-1 layout (Balloon Drops orphan on row 3). GL flagged the orphan-on-row-3 violates symmetry preference. Options: (a) center the orphan via `grid-column: 1 / -1` on `:nth-child(5)` (cleanest minimal change), (b) 1-per-row stack on mobile. Easy CSS fix; defer until next homepage iteration.

### Open iterations on already-built Lead schema (carried into Phase 2)

- [P1] **Inspiration Photos thumbnail UX decision.** Frappe blocks `in_list_view` on Attach Image AND Image fieldtypes in child tables. GL hasn't picked among: (a) click-to-expand (current state), (b) Frappe Client Script for inline gallery rendering, (c) drop child table for built-in attachments sidebar. Resume after GL chooses.
- [P1] **GL's "this is one Lead!" realization.** GL was thinking each tab was a Lead category; reality is sections of one Lead form. GL hasn't said what they actually wanted to model differently. Don't redesign without their explicit direction. Resume conversation when GL is ready.

### Phase 2 — Form-handling depth (reframed 2026-04-27)

`/contact` is the primary inquiry route. `/book` is retired and redirects to `/contact?intent=quick`. Phase 2 now covers depth around all forms:

- [P0] Contact form UX readiness planning is captured at
  `workstreams/contact-form-ux-readiness-2026-05-14.md`. It is not live-release
  approval for new form changes. Legal-impact changes still need legal counsel;
  exact requested changes, UX/CMO/CTO review, and local/staging/live gates are
  listed in that handoff.
- [P0] Verify Contact dedup logic now in `apps/locally_twisted/locally_twisted/lead_cascade.py` (Lead → existing Contact match by email/phone, else create new). Queue previously listed this as unbuilt; confirm with a smoke record before deleting.
- [P0] Loud-failure compliance audit across every form on Phase 1 surfaces
- [P0] Keep the shared form submission UX honest: no success state unless the backend returns `message.ok`, no forced success redirect, no `#received` fake success, no `message.ok` unless current confirmation-email queue proof exists, and update `scripts/verify/form_experience.spec.js` plus `capabilities/recipes/shared-inquiry-form-experience.md` with any future form-state changes.
- [P1] Monitor alerts (Better Stack or equivalent) — fire if `/contact` form-creation rate drops to zero for >24 hours

### New asset drops at `assets/` (GL added 2026-04-27)

- [P1] **`assets/blue dog logo.png`** — the balloon dog logo (companion to the existing text logo). Possible future use: header chrome, footer brand block, OG image for social shares, proposals, event packets, reorder follow-ups, and other marketing/support surfaces. Do not use it on ordinary Sales Invoices.
- [P2] **`assets/product photos/`** — additional product photography. Inventory + match against `_resources/legacy_source-export/catalog.json` SKUs when seeding the small shop (Slice 11).
- [P2] **`assets/what we do photos/`** — now only the intentionally retained tracked event/decor source photos. `Giant Pumpkin Balloon.png`, `Happy Easter Carrot balloons.jpg`, and `balloon Ferris wheel Salt lake city utah.jpg` were moved to the local raw-drop holding area above and should not be re-added unless a future feature makes them production source. Candidate image work should prefer committed public assets or a fresh approval pass from `locally-twisted-local-drops`.

### Real customer reviews — ongoing

- [P3] When new 5-star reviews land, append to `home.py` `REVIEW_QUOTES` list. Carousel auto-scales to any count. The platform strip above the crawl is logo/proof only: no exact counts, no visible `reviews` label, and no platform cards/containers. Truncated reviews from the 2026-04-27 paste (Holly Offret, Angela Corona, Susie Jones, Connie Norton, Lisa Olsen, Al van der Beek, Dallas Yates, Kristi Johnson) are dropped — if you can get the full text, wire them in.
- [P3] When blog framework ships, keep blog promotion out of the stable launch hero unless GL explicitly reopens rotating homepage headlines.

### Cross-cutting / housekeeping

- [P1] **Clean legacy capability-card registry warnings.** The project capability root is now visible at `capabilities/`, but some older LT cards still carry legacy/maturity/frontmatter warnings when `capability_registry.py` runs. Do not block current launch work on this, but the next capability-maintenance slice should update only the stale cards it owns, regenerate the registry, and aim for warnings=0 without inventing evidence.
  - 2026-05-21 update: v2.4 framework seed parity is complete, but validation
    still reports 32 registry warnings, 35 graph errors, and 45 graph warnings.
    Start from
    `workstreams/capabilities-framework-v2-4-seed-update-2026-05-21.md`.

- ~~**Sweep `scripts/verify/_screenshots/` accumulated bloat.**~~ DONE 2026-04-30: added `scripts/verify/_screenshots/` to `.gitignore` (option B). 127MB of accumulated diagnostic captures no longer reach git. Existing on-disk dirs not auto-deleted but gitignored — GL or future instance can `rm -rf scripts/verify/_screenshots/*` to reclaim disk space when desired.

- [P1] **No-monolith follow-through.** Standing handoff: `workstreams/no-monolith-operating-contract.md`. Before adding to large hand-authored files such as `lt-theme.css`, `business_automation_index.py`, `book_form.html`, checkout/home route controllers, broad Playwright verifiers, or product/shop CSS, split by responsibility or record why the immediate change must stay surgical. First logical split should happen where the next real feature already touches one of those files, not as a broad refactor for its own sake. Delete this queue item after the first dedicated split pass removes the current high-risk candidates or converts them into owned feature-specific follow-ups.

- [P1] **Product detail photo/options polish from real product states.** The 2026-05-07 company-first/clear-control cleanup removed the lower Additional Info/Reviews/Recommended Items panel and guards against recommendation/auxiliary boxes plus boxed product controls returning. Remaining product-page polish should use actual representative products and focus on photo quality/scale, option clarity, and a balanced image/detail layout. Continue removing tacky/low-value containers from product pages while preserving the pickup/delivery framed exception and the main page-level wrapper. Verify against multiple real product routes, not only `unicorn-bouquet`. The shop supports the company; do not add upsells, recommendation panels, empty reviews/spec tabs, boxed size/color/add-on controls, or generic ecommerce blocks as "engagement." Start with `capabilities/recipes/frappe-product-page-company-first.md`, `capabilities/recipes/frappe-product-clear-control-contract.md`, and `workstreams/shop.md`.

- [P1] **Keep launch gates green after every visual/backend slice.** After portfolio, product, asset, container, microinteraction, or page work, run the route-specific verifier first, then the relevant public layout/website gate such as `npm run test:portfolio-reel`, `npm run test:shop-smoke`, `npm run test:layout-fit`, `npm run test:container-contract`, `npm run test:interactive-layout`, `npm run test:public-verify`, `npm run test:ecommerce-full`, or `npm run test:launch-verify`. For backend/business automation work, run the specific contract verifier that owns the path instead of using a proxy. Do not claim visual or automation completion without fresh verifier output.

### Gate-kit follow-ups (added 2026-04-26 by gate-kit install — see `docs/GATE-KIT-INSTALL-NOTES.md`)

- [P1] **Add `requirements.txt` at repo root.** Currently `playwright` and `requests` are install-time prerequisites for the gate kit but not declared anywhere. Minimum: `playwright>=1.40` and `requests>=2.31`.
- [P2] **Document the human-review-commit deploy ritual in `scripts/README.md`.** The gate at `scripts/deploy.py:gate_human_review_commit()` refuses to deploy when HEAD's commit message starts with `auto:`. Routine remediation: `git commit --allow-empty -m "review: <pre-deploy summary>"` before running deploy.
- [P2] **Set `STAGING_URL` secret in GitHub repo settings + uncomment the CI form-shape step.** `.github/workflows/ci.yml` lines 35-36 are commented out pending a staging URL. Defer until staging exists.
- [P3] **At cutover (Phase 6): flip `scripts/deploy.py` `CONFIG["site_url"]` and `smoke_test_screenshot_paths`.** Currently `http://localhost:8081`; production URL TBD.
- [P3] **Wire `/contact` smoke test into deploy config.** `CONFIG["smoke_test_form_path"]` should target `/contact`; `/book` redirects to `/contact?intent=quick`.


## Blocked

*nothing*

## Waiting on GL

- **Stage 1 legal owner questions** - answer `STAGE-1-LEGAL-OWNER-QUESTIONS.md` before final public policy/live checkout claims. If Stage 1 launches inquiry/lookbook only and holds live Stripe checkout, mark the checkout/payment questions as deferred instead of blocking the public site.
- **Inspiration Photos thumbnail UX** — pick (a)/(b)/(c) from the Lead-schema iteration item above (carries into Phase 2)
- **"This is one Lead" realization** — what did you want to model that you thought was happening? (carries into Phase 2)
- **One of a Kind Designs replacement photo packet** — GL will provide a folder of photos to replace the current proof-band photos. Use the photos as photos: no text on the images, no captions inside the photo surface, no background-image cropping, no fixed-height image containers, no cards/wrappers that clip the balloon art. Shadow treatment is allowed; clipping the design is not.
- **Real photo replacements** — the 5 home photos in `apps/locally_twisted/locally_twisted/public/images/home/` are GL-acceptable for v1 but future swaps possible (especially the Twisting photo — there are 9 others in legacy_source `assets/image assets/balloon twisting pics/` that could rotate in).

*All other Phase 1 decision gates resolved.*

## Deferred (intentional, not blocked)

- **Finance/back-office automation** — deferred indefinitely per GL on 2026-05-10. This includes bank connection, reconciliation, Supplier/vendor/W-9 secure-send workflow, payroll/HRMS/provider approval, and customer reminder send-delivery. Reports and verifiers may keep showing these as known setup gaps, but they are not active work until GL reopens finance.
- **About page** — deferred until Jeff is ready (GL 2026-04-27). Contact page covers the basics; no About in v1.
- **Custom Frappe app scaffolding for LT** — DONE (the `locally_twisted` app exists and is installed). Marked complete; no longer deferred.
- **Frappe Cloud signup + production deployment** — Phase 6 (cutover).
- **Reading Jeff's UI-edited content from any prior platform's database** — Not applicable; the prior platform never went live.
- **Two-app split (`agency_platform` + `<client>_connector`) and three-tier alternative** — agency-wide architectural decision; deferred until BBC has 2-3 clients to inform pattern (see `Built_by_Cameron/built-by-cameron-decisions.md` 2026-04-26).

### Design Studio contest — post-synthesis follow-ups (added 2026-04-29 late evening; updated by next-day instance after surface)

**Contest itself is COMPLETE.** Render gallery (56 PNGs) + `FINAL-SURFACE.md` shipped. GL holding 5 agents (Proxy + 4 contestants by ID) for synthesis follow-ups. Shutdown deferred until GL signals contest fully done.

- [P1] **Write LT-tier lessons-learned + decisions log entries** for the contest outcomes. Capture *after* GL completes synthesis with the picked pieces — entries should reflect what GL chose and why, not the orchestration itself.
- [P2] **Possible global capabilities update** about the persistent-agent-by-ID pattern (the contest skill's name-addressing assumption is wrong-shaped per session learning).
- [P2] **Send shutdown SendMessages to the 5 contest agents** once GL signals the contest is fully done. IDs: Proxy `aa3108d9ab3c5a978`, C1 `a76396efd739881c3`, C2 `a3a7df4f715615f21`, C3 `ad72af232430d89f3`, C4 `a30d848ce821198bb`.
