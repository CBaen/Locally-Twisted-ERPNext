# Locally Twisted — Project Status

> **Live product visibility correction, 2026-06-23:** the four documented
> retired products are now disabled/hidden on live `locallytwisted.com`:
> `large-garland`, `mothers-day-bouquet`, `large-organic-column`, and
> `pride-progress-rainbow-balloon-arch`. Root/template Items and child variants
> are disabled where present; Website Items remain unpublished and
> `needs_review|needs_review`; target product routes return `404`; `/shop`
> omits the slugs. Use
> `workstreams/ecommerce-audit/live-product-disable-2026-06-23.md`.

> **Live Stripe promotion-code correction, 2026-06-23:** live
> `locallytwisted.com` checkout now opens Stripe Checkout with the `Add code`
> promotion-code control visible. Five one-time `$100.00 USD` Stripe
> promotion-code gift cards exist under coupon `LT 100 Gift Cards - June
> 2026`. Exact code values are not stored in git because they are live
> stored-value instruments. Final full repo commit `3498fef`, app mirror
> `main` commit `7e3ab00`, Frappe Cloud tracked branch
> `live-shop-discovery-20260529` at `5d7c952`, Frappe Cloud pipelines
> `64v1t42tmv` and `3e3e0b8she` succeeded, and live proof reached
> `checkout.stripe.com` showing `Add code` without redeeming a code. Use
> `workstreams/ecommerce-audit/stripe-promo-codes-live-2026-06-23.md`.

> **Live ENB access/reset correction, 2026-06-13:** Controlled external marketing builder access and one branded Locally Twisted password-reset email for `marketing@exploringnotboring.com` are complete on live. Source commit `456c9a3`, app mirror commit `8b10a92`, Frappe Cloud patch pipeline `eutojcn0ei`, active bench `bench-40102-000037-f4v`, Email Queue `e4aqh31606` `Sent`. This proves ERPNext sent the reset email and the reset page responds without consuming the token; it is not inbox-visible proof and does not authorize more ENB access, ad/budget changes, or another reset send. See `workstreams/external-marketing-builder-access-reset-2026-06-13.md`.

> **Legacy status map as of 2026-05-02.** This file is no longer the active whole-project source of truth. It contains useful current-state summaries mixed with historical receipts and stale project details. For current coordination, use `locally-twisted-queue.md` for active lanes, `workstreams/<feature>.md` for feature-specific state, `locally-twisted-decisions.md` for durable reasoning, and `CODING-HANDOFF.md` for compact technical startup. Do not update this file just to chase full parity across active workstreams.
>
> **Current shop routing correction, 2026-05-02:** `/shop` is the all-decor hub. `/shop-items`, `/all-products`, and `/shop-by-category` now send broad browse traffic to `/shop`; individual category pages stay at `/shop-items/<group>`. The primary nav label is now `Balloon Decor`. Older lines below that say `Shop Balloon Decor` or that broad browse routes alias to `/shop-by-category` are historical receipts, not current routing.

> **Public ecommerce correction, 2026-05-17; taxonomy refreshed 2026-06-21; live product hide verified 2026-06-23:** Local ecommerce may be temporarily opened for proof runs, but local dev uses Stripe test records and is not live-payment proof. Production checkout/Stripe lives on the Frappe Cloud site. Current category/count proof is 47 published products, 4 requested products retired/unpublished, 8 active primary categories, and 9 hidden secondary occasion categories. The four retired product hides are live as of 2026-06-23; broader taxonomy/category changes still need their own release and live proof before being claimed on `locallytwisted.com`.

> **Domain/reindex correction, 2026-05-19:** Public pages/forms now serve through Cloudflare DNS and Frappe Cloud. Current chain is GoDaddy registrar -> Cloudflare DNS/email routing -> Frappe Cloud -> ERPNext/Frappe. Hetzner/legacy_source is old reference/decommission scope. Reindex work is blocked until the live sitemap/canonical fix is released because current live discovery URLs still advertise `locallytwisted.v.frappe.cloud`. Use `workstreams/domain-provider-reindex-cleanup-2026-05-19.md`.

> **Category hero/color correction, 2026-05-22:** `/shop-items/<group>`
> compact heroes now use generated, category-specific WebP crops sourced from
> owner-approved balloon swatches and exact color names. This does not mean
> ERPNext Item Group `image` fields were approved or changed. Use
> `workstreams/ecommerce-audit/shop-category-hero-imagery-2026-05-22.md` and
> `_resources/STYLE-GUIDE-BALLOON-COLOR-ADDENDUM.md`.

> **Kubuntu recovery correction, 2026-06-15:** the repo has been reconciled
> inside the Kubuntu checkout after the Windows-to-Kubuntu host move. Use
> `CODING-HANDOFF.md` and
> `workstreams/kubuntu-recovery-closeout-2026-06-15.md` for the current source
> baseline. This was source stabilization and archive cleanup only, not
> staging/live/provider/DNS/payment approval.

**Repo:** `git init` 2026-04-26 at `C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\locally-twisted`. Pushed to `https://github.com/CBaen/Locally-Twisted-ERPNext`. Separate from BBC agency repo per the agency isolation rule.
**Tech:** ERPNext v15.105.0 + Frappe v15.106.0 verified locally on 2026-05-08, MariaDB 11.8, Redis 6.2, nginx — running via `frappe_docker` upstream + custom port pinning.
**Purpose:** Migrate LT's business intent + catalog data into a fresh ERPNext v15 install — website, ecommerce, lead intake, operator workflow, invoicing, payments, accounting, payroll, end-to-end. Frame revised 2026-04-30 (see `locally-twisted-decisions.md`). The destination is greenfield ERPNext; the migration sources are the failed legacy_source attempt's discovery work, the catalog data ported 2026-04-30, and the legacy `locallytwisted.com` site that the new ERPNext storefront replaces at cutover.
**Owner:** Jeff Kimber.

---

## Current State

**What works:**
- ERPNext v15.105.0 running locally at `http://localhost:8081` (9 containers, compose project `locally-twisted-erpnext-v15`)
- WSL2 tuned: 8 GB RAM, 4 CPU, swap 2 GB, dropcache (`C:\Users\baenb\.wslconfig`)
- `pwd.yml` uses the custom baked image `locally-twisted-erpnext:v15` built from `docker/Dockerfile`, with `apps/locally_twisted` still bind-mounted into the Frappe services for local development. Verified by `docker inspect` on 2026-05-01.
- LT Company record + Fiscal Year 2026 + Services domain + Standard with Numbers chart of accounts
- 3 LT-specific DocTypes: `Dashboard Reviewed Item`, `LT Service Type` (+ `LT Lead Service Type` child + `LT Lead Photo` child)
- `Lead` DocType extended with 45+ Custom Fields, plain-language relabels, "Additional Information" tab hidden, 25 MB upload
- nginx Origin pass-through is present in the running LT frontend container and baked into the current custom image; `scripts/fix/patch_nginx_socketio_origin.py` is historical/fallback, not a routine post-recreate step.
- **Custom Frappe app `locally_twisted` installed**. **`installed_apps` order: `[frappe, erpnext, payments, webshop, locally_twisted]`** — locally_twisted MUST stay LAST so its template overrides win Frappe's reversed-app-order ChoiceLoader. Re-set via `db.set_global("installed_apps", json.dumps([...]))` if any new app installs append after locally_twisted.
- **Brand foundation theme** at `/assets/locally_twisted/css/lt-theme.css` (registered via `web_include_css`, cache-bust query string `?v=YYYYMMDD-N`).
- **Stripe end-to-end live (test mode).** `/checkout` → Stripe Checkout Session → `/payment-success` → `/thank-you`. ERPNext cascade: PR Paid → SI created → receipt + operator + welcome emails. GL completed real `4242` purchase 2026-04-29.
- **localStorage-backed guest cart** at `/cart` (LT-owned route; multi-item checkout).
- **Phase 1 customer surfaces live or compatibility-safe:** `/`, `/lookbook`, `/shop`, `/shop-by-category` redirecting to `/shop`, `/shop-items/<group>` for the 8 active primary categories, `/shop-items/<group>/<slug>` for the current 47 published products, `/balloon-twisting-and-face-painting`, `/contact`, `/all-products` routing to `/shop`, `/faq`, `/refund-policy`, `/accessibility`, `/cart`, `/checkout`, `/payment-success`, `/thank-you`. All form-bearing pages have AJAX → Lead + Communication wiring with three-channel loud-failure compliance.
- **Mobile responsiveness shipped 2026-04-29** at 320 / 375 / 414 viewports.
- **Current visual authority:** `_resources/STYLE-GUIDE.md` version 4.8 or newer plus `_resources/STYLE-GUIDE-BALLOON-COLOR-ADDENDUM.md`. The old `_resources/design-guide/` synthesis was deleted on 2026-05-05 because it conflicted with the Civic Celebration + Slate Blue/Berry + Brand Direction contract and kept reintroducing light-blue/blush styling. Stale shop/spec comparison docs and the old generic icon-comparison resource were also deleted. The current brand feature handoff is `workstreams/brand-style-guide-consolidation.md`, the current category hero handoff is `workstreams/ecommerce-audit/shop-category-hero-imagery-2026-05-22.md`, the current homepage July/favorites/nav handoff is `workstreams/homepage-july-favorites-nav-plan-2026-06-24.md`, and the current brand SVG suite is `apps/locally_twisted/locally_twisted/public/icons/brand/`.

**Catalog port complete (2026-04-30), taxonomy refreshed 2026-05-24:**
- **Prior source shop catalog rebuilt in ERPNext webshop end-to-end.** This was a catalog-data port into a new ERPNext build, not a business-system migration.
- **Current taxonomy proof rechecked 2026-06-21: 51 total Website Items, 47 published Website Items, 4 retired/unpublished needs-review Website Items, 8 visible primary Item Groups under `Shop Items`, 9 secondary groups under hidden `Shop Occasions`, 51 secondary Website Item Group rows, 28 checkout Website Items, and 19 quote-first Website Items.** Older 53-product, 51-published-product, 30-checkout-product, 21-quote-first-product, and 11-category claims are historical baseline language, not the active customer-facing contract.
- Item Group hierarchy: `Shop Items` (parent, `is_group=1`) → 8 children with `show_in_website=1`: Arches, Balloon Drops, Bouquets, Columns, Garlands, Photo Ops & Backdrops, Stands & Easels, and Table Decor. Secondary occasions live under hidden `Shop Occasions`. Captured as fixture at `apps/locally_twisted/locally_twisted/fixtures/item_group.json`.
- Item Attribute records: verified DB count is 26 as of 2026-05-01. Older docs that say 24 attributes are stale; fixture scope and the extra two DB records should be inspected before changing seed/fixture logic. Fixture at `apps/locally_twisted/locally_twisted/fixtures/item_attribute.json`.
- Webshop Settings flags: `enable_variants=1`, `enable_attribute_filters=1`, `show_attribute_dropdowns=1` (set via `scripts/setup/enable_webshop_variants.py`, NOT fixtured per fixture-discipline — Singles doctype with operator-edited fields).
- Bulk import: `apps/locally_twisted/locally_twisted/seed/seed_catalog.py` (idempotent, loud-fail, runs in-process via `bench execute locally_twisted.seed.seed_catalog.execute`). Honors legacy_source's `data-attribute-exclusions` to filter forbidden combinations from the cartesian product.
- **Current header/nav** uses the deliberate premium two-level mega-menu: `Event Balloons` and `Pickups & Deliveries` mega panels, `Twisting & Face Painting`, `Portfolio`, `About Us`, `FAQ`, search/cart, top short-notice banner, full-height logo image treatment, and mobile drawer accordions. The desktop top banner keeps `Free Event Quote` top-banner-only and links the short-notice message to `/contact`; the menu/drawer CTA is `Contact Us`. `/process` is not a public launch route unless GL reopens it. Menu data lives in `navbar_context.py`; shop/sidebar defaults live in `website_context.py`; both are active website context hooks.
- **Product detail templates** overridden at `apps/locally_twisted/locally_twisted/templates/generators/item/{item_details,item_add_to_cart,item_configure}.html`. "Item Code" jargon stripped, "/Nos" UoM stripped, **inline variant selectors** (chips ≤8 values, dropdown 9+) replacing webshop's "Select Variant" dialog button. `item_configure.html` uses `get_variant_attribute_options` for prepared option data, consumes `valid_options_for_attributes` on partial selection to disable invalid later choices, and keeps chips as radio/single-select controls.
- **`/shop-by-category`** compatibility override at `apps/locally_twisted/locally_twisted/www/shop-by-category/{index.py,index.html}` — redirects to `/shop` so the old placeholder-card index is not customer-facing.
- **`/shop`** updated: category navigation is sourced from active Item Group children (All + 8 primary categories). Drops the keyword categorizer.
- **CSS hide of `.product-code`** in lt-theme.css strips the "Item Code" jargon from compiled-JS-rendered listing cards (only `display: none !important` we kept; webshop's product_ui/list.js bakes the jargon at compile time; can't be Jinja-overridden).
- **Shop smoke checks pass:** `scripts/verify/smoke_shop.py` validates the current desktop/mobile mega-menu contract, `/shop` category navigation, `/shop-by-category` redirect, all 8 active category routes 200 + no jargon, variant detail inline, progressive invalid-option disabling, radio/single-select variant chips, variant add-to-cart, single-SKU clean, and `/shop` Pickups & Deliveries links.
- **Storefront correction pass shipped 2026-05-01:** header/footer IA cleaned to match current routes (`What We Make`, `About Us`, `Book an Event` removed; `All Products` kept), menu dropdowns contained, mobile cart/hamburger visible at 390px/430px, footer centered without shrinking below accessible sizes.
- **Navigation/routing cleanup superseded by the 2026-05-07 nav correction:** primary desktop IA is `Event Balloons`, `Portfolio`, `Twisting & Face Painting`, `Ready-to-Order`, `FAQ`, search/cart, with `Free Event Quote` on `/contact`. `/event-balloons`, `/portfolio`, `/balloon-twisting-and-face-painting`, `/shop`, `/faq`, and `/contact` return 200 locally. `/book` redirects to `/contact?intent=quick`; `/shop-items`, `/all-products`, and `/shop-by-category` send broad browse traffic to `/shop`.
- **Contact/BTFP inquiry consolidation shipped 2026-05-01:** `/contact` is the canonical inquiry form with stackable service choices, guided prefill URLs, service-specific conditional panels, Events Inquiry package planning, Pickup, and Delivery/Pickup labels without "Only." `/balloon-twisting-and-face-painting` is now a contact-led service page that sends customers to `/contact?service=btfp`, `/contact?service=twisting`, or `/contact?service=face-painting`. `/book` redirects to `/contact?intent=quick`.
- **Backend Lead/CRM intake parity shipped 2026-05-01; photo and time-entry wiring fixed 2026-05-02:** `LT Service Type` records now match the public form (`Delivery`, `Pickup`, `Events Inquiry`; no `Delivery Only` / `Event Package`). Lead Custom Field labels/depends_on logic match the revised taxonomy, web submissions populate `custom_event_type` child rows, Lead time fields are plain text entry for staff, and the Lead `Inspiration Photos` section is connected to the `LT Lead Photo` child table through `custom_inspiration_photos`.
- **Simplified backend workspace, safe CRM cascade sync, and backend inventory added 2026-05-02:** Owner, Manager, and Employee workspaces use current business labels (`Booking Calendar`, `Customers`, `People to Contact`) and the booking calendar opens Sales Orders by `delivery_date`. Owner Home is now an ADHD-friendly command center with Number Cards (`New Inquiries`, `Bookings`, `Customers`, `Overdue Follow-ups`), an incoming-inquiries chart, and a guided "What Jeff does next" flow. LT's six-stage board uses `Lead.custom_pipeline_stage`, and stage changes now create/close operational Tasks only; no quote/order/invoice/payment/customer/win-rate cascade is wired yet. `scripts/verify/backend_schema_inventory.py` now provides a read-only live inventory for schema ownership and cascade trigger decisions. `scripts/setup/sync_backend_workspaces.py`, `scripts/setup/sync_crm_pipeline.py`, `scripts/verify/backend_workspace_parity.py`, `scripts/verify/crm_pipeline_parity.py`, `scripts/verify/crm_stage_cascade.py`, `scripts/verify/backend_schema_inventory.py`, and `npm run test:desk-owner` verify this slice.
- **Privacy and Terms routes added 2026-05-01:** `/privacy` and `/terms-of-service` return HTTP 200 locally. Treat as plain-language drafts for Stripe readiness; Stripe Dashboard URL wiring and any legal review remain follow-ups.
- **Layout-fit gate current 2026-05-08:** `scripts/verify/layout_fit.spec.js` checks the current public/shop/cart/checkout/success route set across mobile, tablet, edge, and desktop viewports. Latest verified command: `npm run test:layout-fit` -> 247 passed.
- **Product listing/detail corrections shipped 2026-05-01:** item detail/configure sales-pitch blocks removed; `/shop-items/arches` fixed by preserving Webshop's `.item-group-content` wrapper contract; listing cards now receive `lt_brand_description` through `locally_twisted.api.product_listing` and prefer it in card copy.
- **Project-level shared capabilities visible at `capabilities/`:** originally installed 2026-05-01 and moved out of `.codex/` on 2026-05-10 so Codex, OpenClaw, Claude, and future agents read the same project root. `AGENTS.md` routes agents to `capabilities/INDEX.md`; check `capabilities/failures/` before recipes on known-risk surfaces.

**What's broken / pending:**
- **Frappe asset-map fallback guarded 2026-05-08:** product/shop pages now seed `frappe.boot.assets_json` from `frappe.utils.get_assets_json()` when Frappe's boot payload omits it, and `scripts/verify/smoke_shop.py` fails if the `file_uploader.bundle.js` boot error returns.
- Routes changed from `/shop/<item>` to `/shop-items/<group>/<item>`. Pre-launch — no public bookmarks broken.

**What's next (in order):**
- **ERPNext Backend simplification workstream** — multi-handoff lane at `workstreams/erpnext-backend-simplification.md`; owner/manager/employee Desk first pass, Owner Home command center, workspace sync, Lead photo wiring, Task-only stage cascade, and read-only backend inventory are done. Next: checkout/Lead conversion parity, Contact/Customer/order flow simplification, DB-only field keep/hide/export decisions, then backend-tour sample data.
- **Stripe Dashboard URL wiring for `/privacy` and `/terms-of-service`** after GL/legal approval; dashboard still has placeholder URLs until changed.
- **Sample data for backend tour** — realistic Lead records, paid SO, upcoming event for Jeff's desk demo.
- **Category browse imagery** - `/shop-items/<group>` route heroes are repaired locally with generated category-specific WebP crops. ERPNext Item Group `image` fields are still empty/unapproved for category cards or future image-rich menus; use the category-media approval lane before mutating DB images. Do not revive the retired `/shop-by-category` card index for launch.

**Phase 6 carry-forward (CRITICAL — must happen at cutover):**
- **Remove operator-state-sensitive Item Attribute fixtures from `hooks.py fixtures = [...]` BEFORE Jeff's first post-takeover deploy.** Especially the `latex colors` Item Attribute (51 values — the most likely category Jeff edits as his supplier inventory shifts). Otherwise BBC fixture sync silently overwrites his renames on every `bench migrate`. See `locally-twisted-decisions.md` 2026-04-30 entry "Phase 6 cutover work item." Document in `NOUPDATE-DRIFT.md` (TBD).

**Known bugs (carry-overs):**
- No current P0 backend schema bug is documented here. Use the queue and `workstreams/erpnext-backend-simplification.md` for the active backend lane.

---

## Architecture Decisions

See `locally-twisted-decisions.md` for the full reasoned log. Summary:

| Date | Decision | Why |
|------|----------|-----|
| 2026-05-01 | Website inquiries populate Lead `custom_event_type` child rows | Desk conditional sections depend on the Table MultiSelect, so CSV/text-only service storage is not enough for backend CRM usability. |
| 2026-05-01 | Contact service choices are stackable; Events Inquiry is the package planning path | "Only" implies mutual exclusion. GL wants large multi-piece/corporate event packages to be the ideal path, with structured package-piece choices and fewer irrelevant conditional questions. |
| 2026-04-30 | Frame revised: "migration of business intent + catalog data into a fresh ERPNext install" | Supersedes the 2026-04-26 reframe. Catalog port + form intent + policies + domain cutover are migration shape. Jeff-disclosure stealth and hand-build-not-auto-translate survive as constraints, not as a denial of migration reality. (See decisions log 2026-04-30 frame entry.) |
| 2026-04-26 | Earlier reframe: "first professional business platform," not "legacy_source migration" | Was motivated by Jeff-disclosure concerns and avoiding too-mechanical translation framing. Superseded 2026-04-30. |
| 2026-04-26 | Phase 1 = customer-facing site + storefront (the proof point) | If ERPNext can't deliver this, GL pivots before building backend |
| 2026-04-26 | Pricing calculator embedded in BTFP service page (no standalone /pricing) | Customers on the service page are already asking the cost question |
| 2026-04-26 | Header navigation Option B: single What-We-Make + occasion landing pages | Eliminates SEO duplication, customer confusion, mega-menu mobile complexity |
| 2026-04-26 | Accessibility statement Option B: brief intent-only + actually meeting WCAG 2.1 AA | Avoids warranty-claim risk while preserving good-faith protection |
| 2026-04-26 | Blog: ship framework + live posts in Phase 1 (not deferred) | Adds Phase 1 substance; the "Kindergarten Teacher" voice is a brand asset |
| 2026-04-26 | Photography: 15 placeholders generated via Together API FLUX.1-schnell | Real photos arrive in a future iteration; placeholders close the visual gap |
| 2026-04-26 | All clients default to ERPNext native HRMS payroll (agency standard) | One less third-party integration; simpler transfer |
| 2026-04-26 | Drop standalone About + Services index pages | Info distributes; About summary lands on contact page |
| 2026-04-26 | All policy + brand resources live in `_resources/` (scrubbed of platform refs) | Project must stand alone; legacy_source dir will be retired |
| 2026-04-25 | ERPNext v15.105.0 pinned (latest stable v15 patch) | Past Stripe-broken window; latest patch on a mature line |
| 2026-04-25 | Local Docker for build, Frappe Cloud Sites plan ($5/mo) for prod | Local is free + breakable; Frappe Cloud is managed + transferable per-site |
| 2026-04-25 | Don't modify anything in `locally-twisted-legacy_source/` | Read-only reference; will be retired post-cutover |

## Reference Disposition (per CLAUDE.md)

The four reference surfaces are temporary and will be retired. Future instances must NOT assume any of them exist:

| Surface | Disposition |
|---|---|
| Local legacy_source clone (`C:\Users\baenb\projects\locally-twisted-legacy_source\`) | Will be archived to GitHub and removed from disk |
| Failed Hetzner deployment (`http://5.78.136.133/`) | Will be decommissioned after Phase 1 demo |
| legacy_source GitHub repo (`https://github.com/CBaen/locally-twisted-legacy_source`) | Will be archived as read-only |
| Current `locallytwisted.com` site | Damaged beyond repair; replaced at cutover |

Canonical resources for the migration destination live in `_resources/` and are platform-agnostic.

## Key Files

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Client project rules, voice & language, reading order, Reference Disposition |
| `HANDOFF.md` | Instance-to-instance handoff (overwrite, ~40 lines) |
| `PROJECT-STATUS.md` | This file — current state, architecture decisions, dated update log |
| `lessons-learned.md` | Append-only project lessons (LT-specific) |
| `anti-gl-patterns.md` | Project-local instance-authored anti-pattern catalog |
| `locally-twisted-decisions.md` | Append-only decision log with reasoning |
| `locally-twisted-queue.md` | Active work queue (delete completed items) |
| `locally-twisted-index.md` | Pointer index for client artifacts |
| `_resources/STYLE-GUIDE.md` | Design system source-of-truth — color tokens, typography, components, voice ("Quiet Confidence") |
| `_resources/design-guide/` | Deleted 2026-05-05. Do not recreate it or use the old screenshots/TSX/light-blue-blush direction as current taste calibration. |
| `_resources/policies/INDEX.md` + 6 policy files | Business policies (legal interview answers + 5 supporting rules) |
| `_resources/utah-tax-rates-2026q2.md` | Utah destination-based sales tax research |
| `_resources/competitor-survey-2026-04-26.md` | 9 competitor sites surveyed; receipt for the lookbook-forward decision |
| `_resources/images/INDEX.md` + 15 placeholder PNGs | Phase 1 image set |
| `_resources/legacy_source-export/catalog.json` + 48 image PNGs | 51-product catalog from prior legacy_source attempt; reference for webshop seeding |
| `apps/locally_twisted/locally_twisted/public/css/lt-theme.css` | Brand foundation CSS (canonical, served via `web_include_css` in `hooks.py`) |
| `.planning/PROJECT.md` | Source-of-truth project context, requirements, decisions |
| `.planning/ROADMAP.md` | 6 workflow-centric phases |
| `.planning/REQUIREMENTS.md` | Requirements with REQ-IDs and traceability |
| `.planning/STATE.md` | Current execution pointer |
| `.planning/decisions/header-navigation.md` | Phase 1 decision brief — option B chosen |
| `.planning/decisions/accessibility-statement.md` | Phase 1 decision brief — option B chosen |
| `.planning/phases/01-customer-site-and-storefront/PLAN.md` | Phase 1 slice plan (all gates resolved) |
| `scripts/setup/setup_lt_company.py` | One-shot wizard completion + LT Company seeding (reusable on fresh installs) |
| `scripts/setup/sync_contact_intake_backend.py` + `scripts/verify/lead_backend_intake_parity.py` | Current Lead backend sync and parity verifier. Old one-off Lead translation/fix scripts were removed; use git history only if researching them. |
| `scripts/fix/patch_nginx_socketio_origin.py` | Historical/fallback nginx Origin pass-through patch; only use if a rebuilt image is verified missing the Origin header line |

## Rules

- **Frame (revised 2026-04-30):** This is a **migration of LT's business intent + catalog data into a fresh ERPNext install**. "Fresh install" — destination is greenfield ERPNext, hand-built informed by legacy_source discovery; no auto-translated modules or DB dumps. "Migration" — catalog records, form intent, policies, voice/brand, and the eventual domain cutover are real ports from the prior legacy_source attempt + the legacy `locallytwisted.com` site. Supersedes the 2026-04-26 "new build, not a migration" reframe. See `locally-twisted-decisions.md` 2026-04-30 frame entry.
- **Stealth on the verdict.** Jeff knows there's an audit; he doesn't know the conclusion. Internal docs stay internal until Phase 1 is demo-ready.
- **`_resources/` is canonical.** Anything from the legacy_source dir that applies has been copied + scrubbed. Don't reach back into the legacy_source dir for new content.
- **Voice & Language.** Plain language, no jargon. See `_resources/STYLE-GUIDE.md` voice section.
- **Verify in UI before claiming done.** GL has caught bugs by opening the form themselves. Take screenshots; don't self-report.
- **Loud failure rule.** Per global rule. Every form / cross-system handoff / external API call must fail loudly and be observable.

---

## Updates

**Current-state warning:** dated updates below are historical receipts. Older entries still describe bind-mounts, `/book` as primary, or unseeded catalog states that were later superseded by the 2026-04-30 custom Docker image/catalog port and the 2026-05-01 `/contact` route decision. Use the Current State section plus `CODING-HANDOFF.md` for live operating facts.

### 2026-05-01 (contact/BTFP inquiry consolidation) — canonical contact form + service-specific logic

- **BTFP page refreshed:** `/balloon-twisting-and-face-painting` is now a contact-led service page using actual Hetzner content and current LT styling. Service CTAs prefill `/contact`.
- **Book route retired:** `/book` redirects to `/contact?intent=quick`; it is not a separate public form and not a legacy alias to preserve as its own experience.
- **Service taxonomy cleaned:** `Event Package` became `Events Inquiry`; `Delivery Only` and `Pickup Only` became stackable `Delivery` and `Pickup`.
- **Backend CRM parity synced:** the live ERPNext Lead form now uses the revised service records and conditional logic, and public submissions populate the Lead `custom_event_type` Table MultiSelect.
- **Events Inquiry structured:** package-piece checkboxes mirror homepage custom categories, color prompt is more fun/customer-facing, and details aggregate into existing Lead text fields.
- **Conditional form logic corrected:** live-artist shade/environment questions appear only for Balloon Twisting and Face Painting; Something Else, Delivery, Pickup, and outside balloon decor do not get irrelevant dropdowns.
- **Pickup added:** pickup customers get a location prompt below the form, and Riverdale now reads `Northern Utah Location (Residential Address)`.
- **Verification:** `contact_service_logic.py`, `contact_prefill.py`, `smoke_forms.py --form-path /contact --skip-newsletter`, and `npm run test:layout-fit` passed locally. Backend record verification in `smoke_forms.py` needs `LT_ADMIN_PASSWORD` set.

### 2026-05-01 (storefront correction pass) — header/footer/menu cleanup + product listing/detail fixes

- **Header/footer IA corrected:** removed `What We Make`, `About Us`, and `Book an Event` from customer chrome. `All Products` remains. Footer columns were re-centered through layout/content cleanup, not by shrinking text below accessibility expectations.
- **Menu containment corrected:** desktop dropdowns are contained under the nav; mobile drawer/cart/hamburger visibility verified at narrow mobile widths with accessible touch sizing preserved.
- **Customer nav corrected again after GL review:** lower nav order was `Shop Balloon Decor`, `Plan by Occasion`, `Balloon Twisting & Face Painting`, `FAQ`, `Blog`, search; superseded 2026-05-02 by `Balloon Decor`, `Plan by Occasion`, `Balloon Twisting & Face Painting`, `FAQ`, `Blog`, search. No Gallery for now. No lower-nav Contact duplicate because the top utility bar already has `Contact Us`.
- **Occasion nav is product-backed:** `Plan by Occasion` links route to real product/category pages instead of `/contact?occasion=...`. Some visible product names still contain words like delivery or seasonal, but those are not active top-level shop categories after the 2026-05-24 taxonomy cleanup. The nav IA verifier now fails if occasion links regress to contact shortcuts.
- **Retired routes handled:** `/book` redirects to `/contact?intent=quick`; customer CTAs now point to `/contact`. `/shop-items` and `/all-products` now route to `/shop`, and `/shop-by-category` redirects to `/shop`.
- **Policy routes added:** `/privacy` and `/terms-of-service` are static Frappe routes for Stripe readiness. Both return HTTP 200 locally; Stripe Dashboard wiring remains separate.
- **Layout fit verifier restored:** `scripts/verify/layout_fit.spec.js` is present and runnable through `npm run test:layout-fit`. Latest current run is 80 passed as of 2026-05-05.
- **Product detail pitches removed:** stripped "Start a conversation" from `item_configure.html` and "Tell us what you're imagining" from `item_details.html`.
- **`/shop-items/arches` bug fixed:** root cause was missing Webshop `.item-group-content` class in the LT Item Group wrapper. Restored the framework contract so the Webshop listing JS scopes results to the active Item Group. Verified Arches API response returns only Arches.
- **Brand descriptions on listing cards:** added `locally_twisted.api.product_listing.get_product_filter_data` as a local wrapper for Webshop's product filter API and registered it with `override_whitelisted_methods`; listing cards now prefer `lt_brand_description` with existing description fallbacks.
- **Cleanup:** generated browser profile/screenshot output from local verification is ignored/deleted instead of treated as project source. Canonical state is source + docs + git history.

### 2026-04-30 (evening, autonomous nap session) — Mirror rebuild Phase 1 chrome shipped via /triadic-construction-v2

**See `HANDOFF.md` and `MIRROR-REBUILD-COMPLETE.md` for full session report.** Summary:

- **Project frame revised** from "new build, not a migration" → "migration of business intent + catalog data into a fresh ERPNext install" per GL directive at session open. 8 docs updated to reflect.
- **Hetzner mirror landed** at `_resources/retired-source-mirror/` — 346 pages + 510 assets via `crawl4ai` (chosen over httrack/wget for JS-rendering). Mirror script reusable at `scripts/mirror/mirror_hetzner.py`. Tool research at `research/website-mirror-tool-discovery.md`.
- **/book unblocked** — was 404 every prior session. Files existed; root cause was stale Frappe website cache + nginx upstream-IP staleness after backend restart. Pre-task chain (cache flush + frontend container restart) made it HTTP 200 with the full form rendering.
- **6 pre-task fixes shipped** before the chrome dispatch: `max_file_size = 25 MB` verified, smoke_forms.py selector aligned (`contact_name` vs `lead_name`), `lead.insert()` wrapped in try/except + `frappe.log_error` (loud-failure rule), `/contactus → /contact` redirect added, shop card `data-category` typo fixed (silently broken filter since launch), cache flush + `/book` verify.
- **Phase 1 chrome rebuild via /triadic-construction-v2** — 3 builders (Jinja / CSS / JS) + 3 reviewers (Architect / SecOps / Execution Engine) + GL Proxy + fix round + audit pass. Deliverables:
  - Hetzner-shaped header (utility bar + logo + 3 desktop mega menus + mobile drawer + accordion)
  - Hetzner-shaped footer (newsletter strip + 3-col + social + legal bar)
  - `lt-newsletter.js` (vanilla JS, no jQuery). Historical note: `lt-megamenu.js` was later removed during a simple-header pass, then restored deliberately on 2026-05-05 when GL chose the premium mega-menu architecture.
  - `LT Newsletter Signup` DocType + `api/newsletter.py` whitelisted endpoint (rate-limited 10/hr per email, idempotent)
  - `lt-theme.css` overhauled — ~340 lines of dead `.navbar.*` and `.web-footer` blocks deleted, ~163 lines of new BEM blocks added (`.lt-utility-bar__*`, `.lt-footer-newsletter__*`). Final 1,959 lines.
  - All chrome class/attribute names aligned across template / CSS / JS after Round 2 fix round
- **Triadic discipline caught real defects** that solo build would have shipped: mobile drawer always visible (CSS class mismatch), 2 of 3 mobile mega menu accordions completely dead (data-attr + querySelector singular bug), megamenu panel had no CSS rules, mega-trigger CSS open-state targeting wrong class, newsletter `showError` `textContent` strips `<a href="tel:">` phone fallback, `@rate_limit` X-Forwarded-For bypass, `hash(email)` instability across container restarts, Esc-key on `/book` navigates away from form, newsletter smoke test missing (loud-failure violation). All caught + fixed in Round 2.
- **Architectural decisions logged (reversible):** (A) mega menu IA — the old flat 11-group model was superseded on 2026-05-24 by 8 active primary categories plus hidden secondary occasions. (B) Category URLs — ERPNext-native `/shop-items/<slug>` retained. (C) Blog — use Frappe's NATIVE `Blog Post` DocType (plan-deepen caught a planned regression to a custom DocType). See `locally-twisted-decisions.md` entries for historical context and supersession notes.
- **Audit screenshots** at `_resources/audit-2026-04-30-chrome/` (6 PNGs at desktop 1280 + mobile 375 for /, /book, /shop). Zero console errors. Mobile chrome looks good. **Desktop chrome flagged for polish:** centered logo dominates utility bar (intrinsic 1050×300 from brand image), tagline wraps vertically — short CSS fix needed. GL named this at session close: *"There's serious issues with the bleed and container issues on desktop but you've done a really good job so far."*
- **GL trust state at close:** *"This looks like it could be usable... you've done a really good job so far."* Session was autonomous (GL napping). All architectural calls logged as reversible. Phase 2 page rebuilds (~12 routes) deferred to next session.
- **Cleanup:** Deleted `legacy_source Migration/5.78.136.133.har` (turned out to be DevTools-filtered to CSS/JS only — no HTML pages, useless) + `legacy_source Migration/book initial state.jpg` (superseded by full mirror at `pages/book.html`). Empty `legacy_source Migration/` dir removed.
- **Agency-tier additions** at `Built_by_Cameron/`: `built-by-cameron-decisions.md` 2026-04-30 entries (rate_limit composite-identity + nginx-resolver-cache + crawl4ai-as-mirror-tool); `HOW-TO-WIN-AT-FRAPPE/auto-behaviors.md` new traps B5 + B6; kitchen note for crawl4ai mirror pattern.

### 2026-04-29 (mobile-responsiveness + now-retired design-guide-import session) — Mobile responsive at 320/375/414, hamburger fits, design contest synthesis imported then later deleted

**See `HANDOFF.md` for current state at session end.** Summary:

- **Structural CSS fix shipped for `<main class="container my-4">` Frappe wrapper.** Frappe's bundled `index.scss` adds `.page-content-wrapper .container { padding: 1.5rem }` at `(max-width: 992px)` which was squeezing all content sections (compound padding with our own section gutters, confining full-bleed backgrounds). Override in `lt-theme.css` removes that confinement at all breakpoints — sections own their own layout. Webshop product detail (`.product-container`) and cart (`.cart-container`) get their own intentional centered max-width (1200px) so they don't bleed edge-to-edge on desktop.
- **Mobile brand logo cap fixed.** `.lt-header__brand--mobile img` was `max-width: 350px` — wider than viewport-row-padding-hamburger leftover space. Hamburger was clipped 35px offscreen, functionally unreachable on real phones. Fixed with `height: auto; max-height: 90px; max-width: calc(100vw - 88px)` (88px reserves space for 44px hamburger + 32px row padding + 12px gap). Tested at iPhone SE (320), iPhone (375), iPhone Plus (414) — hamburger fits cleanly at all three.
- **Removed previous instance's `body { max-width: 100vw; overflow-x: hidden }` band-aid** once the actual overflow source (the brand logo) was eliminated. `body { overflow-x: visible }` confirmed at 320/375/414 with zero overflow.
- **Color tokens cleaned per GL 2026-04-29:** removed `--lt-aqua: #80F5F3` and `--lt-lime-pastel: #B8FF9E` from CSS tokens, removed `.lt-band--aqua` and `.lt-band--lime` class definitions, removed Aqua and Lime Pastel rows from `_resources/STYLE-GUIDE.md` accent palette table. Brand teal `#008080` stays — CTA-button-only per the existing design rule "Teal is earned."
- **Shop hero cleaned:** Cart button removed (cart is in header chrome — was redundant), aqua stripe between products and CTA removed (was wrong color register), "a conversation" hyperlink removed from hero lede (kept the text). `.lt-shop__band--aqua` rule removed from `shop.py` PAGE_CSS.
- **Retired design-guide import receipt.** That session imported a 2026-04-26 design-competition synthesis into `_resources/design-guide/`. This is no longer current guidance. On 2026-05-05 the folder was deleted and active references were moved to `_resources/STYLE-GUIDE.md` because the old synthesis conflicted with the approved Civic Celebration + Slate Blue/Berry + Brand Direction contract.
- **`/shop`, `/shop-items`, `/shop/<item>` design-quality issues surfaced and queued.** GL named the current state "horrible" — vestigial bars, jargon labels visible to customers (Item Code), broken modal close-on-outside-click, breadcrumb bleed-left. NOT fixed this session. The fix is a holistic redesign against the new design guide — that's the actual next P0 for the next instance.
- **Trust-cost moments worth recording for future client work** (per `lessons-learned.md`):
  - I declared mobile responsiveness "fixed" three times before GL pushed back hard enough to surface what was actually wrong. Each round was based on full-page Playwright screenshots that compressed at extreme aspect ratios and lied about visual reality. The right verification is viewport-only screenshots at concrete device widths PLUS GL opening the page in their real browser. DOM widths are preconditions, not verdicts.
  - I tried to canonize the structural CSS fix into the agency-tier `frappe-conventions.md` and `auto-behaviors.md` BEFORE GL had even verified it in their browser. GL stopped this with the word "scary" — putting unverified work into the agency's stable layer means future BBC clients build on it as truth. Agency tier requires PROVEN, MULTI-VALIDATED patterns. Single-instance enthusiasm doesn't earn that layer. Closed task #7 with no replacement.
  - GL named the partnership gap directly: *"You are acting on my behalf but not with me."* I had been treating the work as discrete tickets to close — finding a defect, applying a CSS edit, declaring done. The shift required is to act as a partner with design eye who notices things GL hasn't enumerated, not a code-fix executor.
- **Historical files added then retired:** `_resources/design-guide/` was added in this session but deleted on 2026-05-05. Do not treat the old import as current guidance.
- **Files modified:** `apps/locally_twisted/locally_twisted/public/css/lt-theme.css` (structural override + brand logo cap + band-aid removal + color token cleanup), `apps/locally_twisted/locally_twisted/hooks.py` (cache-bust v8 → v13), `apps/locally_twisted/locally_twisted/www/shop.html` (Cart button removed, aqua band removed, "a conversation" un-linked), `apps/locally_twisted/locally_twisted/www/shop.py` (`.lt-shop__band--aqua` rule removed from PAGE_CSS), `_resources/STYLE-GUIDE.md` (aqua + lime removed from accent palette), `CLAUDE.md` (design guide section + reading order), `.planning/phases/01-customer-site-and-storefront/PLAN.md` line 47 (concrete paths replace vague reference).
- **Cleanup:** deleted MY session's diagnostic files only — `scripts/verify/_oneshot_diagnose_overflow.py`, `_oneshot_mobile_review.py`, `_oneshot_three_viewports.py` and 12 temp screenshot dirs. Did NOT touch prior sessions' accumulated screenshot bloat (~80 dirs back to 2026-04-26) — that's not my scope to delete unilaterally. Flagged for future cleanup decision.

### 2026-04-29 (guest-cart + Stripe-Link + cascade session) — localStorage cart shipped, Link killed at account level, ERPNext cascade wired

**See `HANDOFF.md` for current state at session end.** Summary:

- **localStorage-backed guest cart shipped (Path B).** Webshop's stock cart hard-redirects guests to /login at the JS layer — has always been login-only by architecture. GL chose Path B (true cookie cart) over the cheap "remove Add-to-Cart, only Buy-Now" alternative. New files: `apps/locally_twisted/locally_twisted/public/js/lt-guest-cart.js` (cart engine + capture-phase webshop overrides), `api/cart.py` (`get_cart_items` server endpoint, allow_guest), `www/lt_cart.{py,html}` (the /cart page — name MUST stay `lt_cart` because `cart` collides with webshop's `templates/pages/cart.html` and webshop wins resolution). hooks.py registers `web_include_js` and route rule `/cart → lt_cart`.
- **Multi-item checkout working.** `submit_guest_order` accepts EITHER buy-now params (item_code + qty) OR a JSON `items_json` array. `_resolve_cart_items` resolves both. Multi-line SO created. checkout.html branches: buy-now mode renders single line server-side; cart mode hydrates summary from localStorage on render.
- **Stripe Link disabled at account level.** Custom Payment Method Configuration `pmc_1TRZH2DfnlZQv66ncb001soG` ("LT No Link") created on LT's Stripe account with `link.display_preference="off"`. Wired into `payments/stripe_session.py` via `payment_method_configuration` parameter. **`payment_method_types=["card"]` alone was insufficient** — Stripe layers Link "Save info" + Bank-via-Link UI on top regardless. Verified Link is gone via Playwright render of the actual Stripe page.
- **GL completed first real `4242` test purchase end-to-end** — SAL-ORD-2026-00019. The pending verification from prior session is now closed.
- **ERPNext cascade wired into `/payment-success`.** Beyond marking PR paid: now also creates Sales Invoice from SO (idempotent, ERPNext's `make_sales_invoice`), sends transactional receipt email, sends operator notification to `locallytwisted@gmail.com` with desk deep link, sends welcome email if first-time customer. All four wrapped in try/except so backend hiccups don't block /thank-you redirect. All three emails idempotent via Communication-by-subject lookup.
- **Lead-aware Customer dedup** in `submit_guest_order`. Three cases: returning customer (reuse), Contact-from-Lead (attach Customer to existing Contact + mark Lead Converted with back-pointer), or fresh (create Customer + Contact). Closes the orphan-customer hole when the same email submits /contact then /shop.
- **Email Account configured.** `Locally Twisted` Email Account on smtp.gmail.com:587 TLS, default outgoing. Reads App Password from `.env` `GMAIL_APP_PASSWORD` (was already there from the legacy_source days). Backfill of order #19 sent all three emails successfully.
- **Cart-clear bug fixed.** First fix in `payment_success.html` was inert because that template never renders (`_redirect()` raises `frappe.Redirect` before Jinja). Moved `LT_CART.clear()` to `thank_you.html`.
- **Removed "Questions? Call (801) 285-0860..." contact line** from `/thank-you` per GL.
- **Files added:** `apps/locally_twisted/locally_twisted/public/js/lt-guest-cart.js`, `api/__init__.py`, `api/cart.py`, `www/lt_cart.py`, `www/lt_cart.html`. PMC `pmc_1TRZH2DfnlZQv66ncb001soG` on LT's Stripe account. `Locally Twisted` Email Account.
- **Files modified:** `payments/stripe_session.py` (PMC), `www/checkout.{py,html}` (multi-item + Lead-aware dedup), `www/payment_success.py` (full cascade), `www/thank_you.html` (cart clear, contact line removed), `www/shop.html` (LT_CART.add), `templates/includes/navbar/navbar.html` (cart count badge), `hooks.py` (route + JS registration).
- **Cleanup:** `Smoke LinkTest`, `Link Verify`, `Link Inspect` test customers + cascading records deleted at session close. `_oneshot_guest_cart.py` and `_oneshot_stripe_link.py` deleted (served their purpose; git history preserves).

### 2026-04-29 (Stripe Charges → Checkout Sessions migration session) — Hosted Stripe checkout live, /payment-success override fixed, agency-tier pattern codified

**See `HANDOFF.md` for current state at session end.** Summary:

- **Migrated from Frappe's bundled Stripe (legacy Charges API) to Stripe Checkout Sessions (Stripe-hosted page).** Customer's `/checkout?item=<code>&qty=<n>` form now submits → creates SO + PR (unchanged) → creates a Stripe Checkout Session → returns `https://checkout.stripe.com/c/pay/cs_test_...` URL → JS redirects there. Customer sees Stripe's polished hosted UI: dynamic payment methods (Card / Klarna / Affirm / Cash App Pay / Bank / Link), real-time validation, "Powered by Stripe" footer.
- **`/payment-success` override SHIPPED.** Fixes the Frappe `payments` app upstream URL bug at `stripe_settings.py:272` (appends `?redirect_to=None` even when None) AND the guest 403 (Frappe's bundled controller calls `frappe.get_doc("Payment Request", ...)` as guest). Our override at `www/payment_success.py` handles both `?session_id=cs_test_...` (modern) and `?doctype=Payment%20Request&docname=...` (legacy fallback). Route registered via `website_route_rules` in `hooks.py`.
- **Server-side reconciliation on `/payment-success`** marks the PR paid synchronously when the customer's browser lands — uses `stripe.checkout.Session.retrieve()` to verify `payment_status == 'paid'` then calls `pr.set_as_paid()`. Idempotent: webhook also fires async, second path no-ops.
- **Webhook handler shipped** at `apps/locally_twisted/locally_twisted/payments/stripe_webhook.py`. Signature-verified, reads secret from `frappe.conf.get('stripe_webhook_signing_secret')` (which lives in `site_config.json`, not in a doctype). Currently dormant (success-page reconciliation handles the demo flow); ready for production where it's the safety net for browser-closed-before-redirect.
- **`/checkout` page got two-column layout with persistent right-side order summary** (item thumbnail + name + qty + line total + grand total + "Secure payment — payment is processed by Stripe" notice). On mobile, summary stacks above form. Matches the legacy_source `/shop/cart`/`/shop/address` pattern GL referenced.
- **Agency-tier decision logged + kitchen note dropped** at `Built_by_Cameron/built-by-cameron-decisions.md` (per-client Stripe accounts; Charges API forbidden for new builds; webhook secrets in `site_config.json`) and `Built_by_Cameron/.claude/capabilities/kitchen/2026-04-29-stripe-checkout-sessions-for-frappe.md` (full pattern). Promote kitchen note to recipe when client #2 adopts.
- **Local dev webhook listener pattern:** `stripe listen --api-key "$STRIPE_TEST_SECRET_KEY" --forward-to <url>` bypasses `stripe login` 2FA when client account isn't accessible. Stripe CLI's stored auth (`stripe config --list`) is a separate context from ERPNext's runtime auth (Stripe Settings doctype, populated from `.env`).
- **NOT verified by GL with a real `4242` card.** All my checks were curl + Playwright + simulated session_id. The actual customer flow — fill form → land on Stripe's page → submit `4242` → land on `/thank-you` → SO marked Paid in desk — is GL's first task on resume.
- **Files added:** `apps/locally_twisted/locally_twisted/payments/{__init__.py, stripe_session.py, stripe_webhook.py}`, `apps/locally_twisted/locally_twisted/www/payment_success.{py,html}`, `scripts/setup/set_stripe_webhook_secret.py`.
- **Files modified:** `apps/locally_twisted/locally_twisted/www/checkout.{py,html}` (Stripe Session integration + two-column layout), `apps/locally_twisted/locally_twisted/hooks.py` (`/payment-success` route rule).

### 2026-04-29 (Stripe wiring + true guest checkout session) — Stripe configured, /checkout + /thank-you live, Customer-only flow (no User accounts)

**See `HANDOFF.md` for current state at session end.** Summary:

- **Stripe Test mode fully configured.** Stripe Settings "Test" + auto-created Payment Gateway "Stripe-Test" + Bank Account "Stripe-Test - LT" (USD) + Payment Gateway Account "Stripe-Test - USD - LT" (default). Webshop `enable_checkout=1` + `payment_gateway_account` wired. Reusable script: `scripts/setup/configure_stripe_test_mode.py`.
- **`/checkout?item=<code>&qty=<n>` page live.** Form takes name + email + phone + UT shipping + marketing-opt-in checkbox. POSTs to `submit_guest_order` whitelist endpoint which creates Customer + Contact + Address + Sales Order (order_type "Shopping Cart") + Payment Request — **NO User account created**. Returns Stripe Elements URL; JS redirects.
- **`/thank-you` (alias of `/thank_you`) page live.** Renders post-payment landing with order summary derived from `?order=<so_name>` param.
- **Marketing opt-in**: Custom Field on Customer (Check, default 0). Checkbox on `/checkout` form, unchecked by default. Future marketing campaigns filter on this flag.
- **Pivot recorded:** Option A (silent User account behind checkout) abandoned 2026-04-29 due to legal complexity; Option B (true guest checkout, no User) chosen. See `locally-twisted-decisions.md`.
- **Frappe Stripe Charges API debt:** Frappe's payments app uses the deprecated Charges API. Test mode demo OK. Production hardening: swap to Checkout Sessions in Phase 4. Logged in `locally-twisted-decisions.md`.
- **Resolved later:** post-Stripe-success redirect was verified by GL's real `4242` test purchase on 2026-04-29; see the guest-cart + Stripe-Link update above.
- **Resolved later:** receipt/operator/welcome emails ship through the `/payment-success` cascade; Slice 10 `/book` was retired as a standalone route and redirects to `/contact?intent=quick`.
- **Cleanup:** all 8 smoke-test records (SOs, customers, addresses, payment requests) deleted at session end. DB is in clean state. `SAL-ORD-2026-00009` is the next number.

### 2026-04-28 (BTFP restructure + ribbons + colors + LookBook→Portfolio) — Visible polish session

**See `lessons-learned.md` and `locally-twisted-decisions.md` for full receipts.** Summary:

- **BTFP page restructure** to match the then-current mockup: hero kicker "LIVE SERVICES" + headline "Something for the middle of the party." (left-aligned), service cards with photo carousels + spec tables (lorem placeholders awaiting Jeff's numbers), process section "Booking is straightforward." 4 steps, event types "Any Event. Any Size." 6 rows, decorative ribbons, last-minute booking banner. The old ribbon/color treatment is superseded by the 2026-05-05 style guide reset.
- **Superseded color decisions:** `--lt-near-white` token warmed `#FBFBFB` -> `#fffcfc`, with an older soft header/footer treatment. This is historical only; current color authority is `_resources/STYLE-GUIDE.md` version 4.2 or newer.
- **LookBook → Portfolio** rename in nav (URL `/lookbook` unchanged).
- **Historical font-weight error fix:** removed heading faux-bold in the old font system. This is superseded by the current Cormorant Garamond + Lato contract.
- **Ribbon margin shorthand bug fix:** `margin: 0` was defeating `.lt-fullbleed`'s negative margins; replaced with `margin-top: 0; margin-bottom: 0;`.

### 2026-04-27 (Slice 6b — Refund Policy + FAQ + framework observations) — Static portal pages with accordion + agency capabilities update

- **Slice 6b shipped:** `/refund-policy` and `/faq` (with accordion via native `<details>`/`<summary>`). Source: `legal-interview-answers.md` Part 2C + `deposits.md` + 6 confirmed policy files. All 13 FAQ Q&As trace to Jeff-confirmed policy content (no invention).
- **Agency capabilities update:** added "Layer boundaries" section to `Built_by_Cameron/.claude/capabilities/INDEX.md` (recipe vs meal discipline). Dropped kitchen note `2026-04-27-framework-shape-observations.md` with 4 open questions for the framework's evolution.
- **BTFP form copy fix:** updated cancellation note from "48 hours' notice required. Deposits are non-refundable." → "Cancel 72+ hours before your event and your deposit transfers to a new date." per GL's verbal confirmation matching legal-interview Part 2C.

### 2026-04-27 (homepage build session) — Slice 3 (Homepage) DONE; site shape locked; reviews carousel with 19 real Google quotes wired

**What landed:**
- **Slice 3 — Homepage** at `/`. Lookbook-forward shape (decided this session). 9 sections in order: Hero (cycling headline + stable tagline + photo + single inquiry CTA) → Reviews carousel (4.9 stars + 114 reviews + 19 real Google review cards in horizontal marquee, hover-pause, 5-star anchored at card bottom) → 3-dot divider → Custom Creations (5 categories with SVG icons) → Recent Celebrations (3 featured-work cards, 4:5 portrait aspect) → 3-dot divider → Client logo crawl (54 names, 270s scroll) → Closing CTA → Twisting & Face Painting spotlight (moved to bottom, de-emphasized). All sections use the `.lt-fullbleed` pattern to break out of Frappe's parent .container.
- **Site shape decision** at `.planning/decisions/site-shape.md` — lookbook-forward + small shop sidebar (sub-$300 pre-configured items only, no configurator-for-checkout). Future "Design Studio" interactive picker scoped for arches/columns/garlands/backdrops/drops/bouquets — captures customer vision, outputs an inquiry, NOT a checkout. Resolves Jeff's "customers want to see colors and pick options" instinct without the wrong checkout flow.
- **Competitor survey** at `_resources/competitor-survey-2026-04-26.md` — 9 verified live competitor sites (4 balloon decor + 3 wedding florists + 1 mixed + 1 enterprise tier). Five patterns observed across all 9: every custom-decor offering uses inquiry/quote, never configurator; portfolio is a nav item not a homepage feature; shops are sidebars; "Inquire" beats "Buy" above ~$30; social proof tier matches business tier. The survey is the receipt for the lookbook-forward decision.
- **ROADMAP.md and PLAN.md updated** to reflect the site shape and the slice reorder. `/book` moved from Phase 2 → Phase 1 (Slice 10) since the lookbook-forward shape requires the inquiry conversion path live in Phase 1. Phase 2 reframed to "form-handling depth" (Contact dedup, ack email, loud-failure audit, monitor alerts).
- **About snippet removed** from homepage. Defer until Jeff is ready (per GL).
- **5 real photos copied** from `locally-twisted-legacy_source/assets/image assets/photos for website/` (and `balloon twisting pics/`) to `apps/locally_twisted/locally_twisted/public/images/home/`: hero (Celebrate backdrop), featured-arches (Knight & Dragon), featured-garlands (Celebrate organic arch), featured-corporate (Logo arch), twisting (Twisting photo).
- **Web Page record `locally-twisted` (route="home")** set to `published=0` — was the placeholder "Site under construction" content. Deactivating let the new `www/home.html` take precedence.
- **Reviews wired into the carousel** — 19 real 5-star Google reviews verbatim from GL's paste, mix of birthday / wedding / corporate / ribbon-cutting / school / face-painting / Mother's Day / church-picnic / funeral-stand / longtime-client. Names, dates, event tags preserved. Verbatim including KJSCOTT's "Totally Twisted" typo (authenticity over correction).
- **Carousel slowed to 270s** (was 90s → 180s → 270s after iterations) for the client logo crawl. Reviews carousel runs 360s.

**What's NOT done (next session candidates):**
- Slice 6b — Refund Policy + FAQ (small static portal pages, ~15-30 min each via the meal)
- Slice 7 — Lookbook (full portfolio, organized by event type)
- Slice 8 — Service category pages (×5: Corporate, Weddings, Birthdays, Schools, Seasonal)
- Slice 9 — Color Chart (`/color-chart`, static reference, 70 balloon colors)
- Slice 10 — `/book` form page is retired as a customer-facing route; `/contact` is the surviving inquiry surface and `/book` redirects to `/contact?intent=quick`.
- Slice 11 — Small Shop browse + detail
- Slice 12 — Cart + checkout shell
- Slice 13 — Blog framework (when shipped, replaces the `HERO_CYCLING_TITLES` placeholder list with a `frappe.get_list("Blog Post", ...)` call)
- Future: Design Studio interactive picker (post-Phase-1)

**Standing rules added/refined this session:**
- Reviews carousel > client logo crawl as primary social proof. Words from real customers persuade more than corporate logos for high-touch event services.
- `/contact` is the primary inquiry conversion path. Older `/book`-primary claims are stale; `/book` redirects to `/contact?intent=quick`.
- Bouquets join the customizable categories list (6 total). Originally only 5 in the approved legacy_source XML; bouquets are also customizable in Jeff's actual business.
- About page deferred until Jeff is ready — no pressure.

**Code/file changes this session:**
- New: `apps/locally_twisted/locally_twisted/www/home.{py,html}` (Slice 3 homepage; replaces the inactive placeholder Web Page record)
- New: `apps/locally_twisted/locally_twisted/public/images/home/{hero.jpg, featured-arches.png, featured-garlands.png, featured-corporate.png, twisting.jpg}`
- New: `_resources/competitor-survey-2026-04-26.md` (9-site competitor survey)
- New: `.planning/decisions/site-shape.md` (lookbook-forward decision with full rationale)
- New: `scripts/verify/_oneshot_home.py` (mobile + desktop screenshot script with console capture)
- Modified: `.planning/ROADMAP.md`, `.planning/phases/01-customer-site-and-storefront/PLAN.md` (full rewrites for the lookbook-forward shape)
- Modified: Web Page record `locally-twisted` (set published=0) — placeholder deactivated

**Open small items (LT-tier):**
- 8 truncated reviews from GL's paste (Holly Offret, Angela Corona, Susie Jones, Connie Norton, Lisa Olsen, Al van der Beek, Dallas Yates, Kristi Johnson) — only partial text was visible. If full text becomes available, append to `home.py` `REVIEW_QUOTES` list.
- Custom Creations mobile symmetry — 2-2-1 layout has the 5th (Balloon Drops) orphaned on row 3. GL flagged but didn't pick a fix. Easy CSS one-liner when ready.

### 2026-04-26 (codification + chrome + 3 portal pages session) — Platform direction RESOLVED; Slices 1+2+4+5+6-partial DONE; agency-tier meal codified

**What landed:**
- **Codification.** Three new agency-tier capability files (`frappe-portal-implementation.md`, `license-isolated-app-architecture.md`, plus updates to `frappe-conventions.md`) + one meal (`build-frappe-portal-page.md`). Every claim verified against running Frappe v15 source. Caught one wrong claim in external research (`extend_doctype_class` is not a v15 hook) — corrected at codification time, before it bit anyone.
- **Slice 2 chrome** — Jinja partial overrides at `templates/includes/{navbar,footer}/`. Two-tier desktop header (delivery strip + centered logo + login/cart on right; main nav row centered), mobile single-row with hamburger + delivery strip below. Footer with centered brand band (3 social icons, no Twitter), 3-column links (always 3 across per GL spec — including mobile), centered copyright bar. GL iterated on logo size (2.5×), centering, padding, mobile column count; all addressed.
- **Slice 6 partial — `/accessibility`** — first portal page shipped via the meal. Static, ~15 minutes mechanical work. GL confirmed: *"the content in the middle of the page looked good!"*
- **Slice 5 — `/contact`** — full form-bearing portal page. AJAX submit to whitelisted controller method → Lead + Communication. Lead Source ensure-or-create gotcha caught at smoke test. GL confirmed: *"Holy shit! You did it!"*
- **Slice 4 — `/balloon-twisting-and-face-painting`** — second form-bearing portal page (10-field form). Aliased from underscored filename via `website_route_rules`. First-ship MVP — carousels, event-crawl, modal deliberately deferred.
- **Webshop bundles compile.** Historical receipt: Node 18 + yarn were first installed in the backend container and wrapped by `install_webshop.py --build-assets`. Current runtime supersedes that path with the custom image, where build tooling and webshop assets are image-owned. `/all-products` renders cleanly with zero console errors.
- **Platform direction RESOLVED.** Frappe-native confirmed by demonstration. Logged at `locally-twisted-decisions.md` 2026-04-26 (later, after Slice 2 + accessibility + contact build).

**What's NOT done (next session candidates):**
- Slice 3 (homepage) — content exists in legacy_source XML; meal applies cleanly
- Slice 6 remainder (`/refund-policy`, `/faq`) — small static portal pages; ~15 min each
- Slice 7-9 (products + cart + checkout) — different shape than the meal; webshop-driven; needs Website Item seeding first
- BTFP first-ship omissions: carousels, event-crawl, modal
- Contact first-ship omissions: Google Maps iframe, modal, `/privacy` link target

**Standing rules added/refined this session:**
- The meal at `Built_by_Cameron/.claude/capabilities/meals/build-frappe-portal-page.md` is the binding shape for any new portal page.
- Five "Known gotchas" with receipts now codified in the meal: text-align inheritance, underscore→dash routing, webshop bundle compilation, Lead Source ensure-or-create, browser cache.
- "Hard refresh" must be in every handoff to GL when shipping a CSS-touching change. Always.

**Code/file changes this session:**
- New: `apps/locally_twisted/locally_twisted/templates/includes/navbar/navbar.html` (Jinja override)
- New: `apps/locally_twisted/locally_twisted/templates/includes/footer/footer.html` (Jinja override)
- New: `apps/locally_twisted/locally_twisted/www/{__init__.py, accessibility.html, accessibility.py, contact.html, contact.py, balloon_twisting_and_face_painting.html, balloon_twisting_and_face_painting.py}`
- Modified: `apps/locally_twisted/locally_twisted/public/css/lt-theme.css` — appended `.lt-header__*`, `.lt-footer__*` BEM blocks (no `!important`)
- Modified: `apps/locally_twisted/locally_twisted/hooks.py` — added `website_route_rules` for the BTFP dashed-URL alias
- Modified: `scripts/setup/install_webshop.py` — added `--build-assets` flag with full Node + yarn + bench build pipeline
- New (agency-tier): `Built_by_Cameron/.claude/capabilities/meals/build-frappe-portal-page.md`
- New (agency-tier): `Built_by_Cameron/.claude/capabilities/recipes/frappe-portal-implementation.md`
- New (agency-tier): `Built_by_Cameron/.claude/capabilities/recipes/license-isolated-app-architecture.md`
- Modified (agency-tier): `Built_by_Cameron/.claude/capabilities/INDEX.md`, `Built_by_Cameron/.claude/capabilities/recipes/frappe-conventions.md`, `Built_by_Cameron/built-by-cameron-decisions.md`
- New (agency-tier): kitchen note at `Built_by_Cameron/.claude/capabilities/kitchen/2026-04-26-1830-frappe-portal-validator-skill.md`
- Deleted: 6 disposable `_oneshot_*.py` screenshot scripts (git history preserves them)
- Deleted from DB: smoke-test Leads `CRM-LEAD-2026-00001`, `CRM-LEAD-2026-00002` + linked Communications

**Open architectural question (agency-tier, not LT-blocking):**
- Two-app split (`agency_platform` + `<client>_connector`) — see `Built_by_Cameron/built-by-cameron-decisions.md` 2026-04-26 entry "License matrix verified" Finding 3. Best decided before next BBC client onboards.

**Open small item (LT-tier):**
- LT app `license.txt` is still placeholder (`Copyright (c) [year] [fullname]`). Suggested fill: `Copyright (c) 2026 Built by Cameron`.

### 2026-04-26 (closing session — long, mixed outcomes) — Webshop durable + catalog exported + Step 0 done + Jinja path validated; landing build FAILED for the second time; expedition surfaced platform-direction question now on GL's desk

**What landed:**
- **Webshop foundation locked.** Historical install path: `frappe/payments` + `frappe/webshop` were first cloned to `apps/`, bind-mounted in `pwd.yml` across 8 services, and gitignored. Current runtime supersedes that with the custom image; do not use `install_webshop.py` as a routine post-recreate step. Webshop public routes live (`/all-products` 200, `/cart` 301).
- **legacy_source catalog exported.** 51 products / 47 with attributes / 48 with images. `_resources/legacy_source-export/catalog.json` + 48 image files. `export_legacy_source_catalog.py` is idempotent and re-runnable.
- **Step 0 fully completed.** Stripped the broken navbar toggler block (lines 388-415 — used a `data:image/svg+xml;utf8,...` data URI that silently failed in real browsers). Replaced with a real SVG file at `apps/locally_twisted/locally_twisted/public/icons/menu.svg`. lt-theme.css now 608 lines (was 770). Two `!important` blocks intentionally retired this session.
- **Jinja override path validated.** Two prior HANDOFFs claimed it would work; nobody had verified. This session: dropped one test file, confirmed it resolved in served HTML, removed the test. Slice 2 redo path is now unblocked architecturally (only relevant if GL's platform direction stays Frappe).
- **Reproducible scripts.** `install_webshop.py`, `clear_website_cache.py`, `export_legacy_source_catalog.py`, `scripts/README.md`.
- **Agency conventions doc substantially upgraded.** "System-native first" standing principle added at the top. Web Page DocType complete tab map (Script + Style + Page Builder + Context). Webshop module map for Slices 7-9. Webshop+payments install pattern with `--skip-assets`. "Verified against source — 2026-04-26" appendix.
- **Full expedition completed.** 3 source-separated researchers (Web Scout / Docs & Standards / Ground Truth) → convergence analyst → devil's advocate → GL Proxy review → synthesis. Eight files in `research/expedition-frappe-theme/`.

**What FAILED (be honest):**
- **Landing page build.** Instance built with Page Builder + 4 default Web Templates + invented copy. Looked fine from DOM facts, broken in GL's actual browser, not mobile-responsive. Rolled back to "Site under construction" placeholder. Same anti-pattern as the prior Slice 2 failure: invent + band-aid + claim-done-off-DOM-facts.
- **Slice 2 visual remains in the broken-honest state from the prior session.** Website Settings has data populated; visual is still Frappe's default styling. No Jinja partial overrides built (only the test override, which was removed).
- **Catalog has not been seeded into ERPNext.** Data exists in `_resources/legacy_source-export/`; no Item / Item Group / Website Item records exist on the LT site yet.
- **Mock comparison of pills vs swatches not built.** Deferred until platform direction resolves.

**Key decision OPEN at session end (load-bearing):**
- **Platform direction.** Stay on Frappe (custom Jinja + custom CSS) OR put a different front door (WordPress / Webflow / Next.js + Medusa/Saleor) on it with ERPNext quietly running the back office. The expedition synthesis is the briefing. GL is collecting more information before deciding — they want to compare Vercel Commerce demo + Frappe Builder + Webflow templates side by side first. See `research/expedition-frappe-theme/synthesis.md`.

**Standing rules added this session (in `locally-twisted-decisions.md`):**
- All customer-facing copy comes from the legacy_source XML or live locallytwisted.com — NEVER invented.
- GL's eyes on the actual page > any DOM fact extraction.
- Per-page interactivity belongs in the Web Page DocType's Script/Style tabs, not in custom Web Templates.
- "System-native first" is the agency-tier rule for all BBC clients on Frappe (codified in agency conventions doc).

**Code/file changes this session:**
- New: `apps/locally_twisted/locally_twisted/setup_pages/{__init__.py, landing.py}` (rollback-only)
- New: `apps/locally_twisted/locally_twisted/templates/includes/footer/` (directory; empty after test removal)
- New: `apps/locally_twisted/locally_twisted/public/icons/menu.svg`
- New: `scripts/setup/install_webshop.py`
- New: `scripts/setup/export_legacy_source_catalog.py`
- New: `scripts/dev/clear_website_cache.py`
- New: `scripts/README.md`
- New: `_resources/website-page-index.md` (v2 — note: tier classifications assume Frappe path; partially invalidated if GL's platform direction goes elsewhere)
- New: `_resources/legacy_source-export/catalog.json` + `_resources/legacy_source-export/images/` (48 PNGs)
- New: `research/expedition-frappe-theme/` (8 files)
- New: `apps/payments/` + `apps/webshop/` (bind-mounted; gitignored)
- Modified: `pwd.yml` (added bind-mounts for payments + webshop in all 8 services)
- Modified: `apps/locally_twisted/locally_twisted/public/css/lt-theme.css` (down to 608 lines from 770; navbar toggler block + `.web-footer` chains stripped)
- Modified: `CLAUDE.md`, `STATE.md`, `lessons-learned.md`, `locally-twisted-decisions.md`, `locally-twisted-queue.md`, `HANDOFF.md`, agency `Built_by_Cameron/.claude/capabilities/recipes/frappe-conventions.md`
- Deleted: `scripts/setup/build_landing_page.sh` (the broken landing build orchestrator — retired)

### 2026-04-26 (webshop install + framework study session) — Three blockers resolved; Slice 2 redo unblocked

**What landed:**
- **Webshop installed durably.** `frappe/webshop` + hard dependency `frappe/payments` cloned to `apps/`, bind-mounted into all 8 frappe-image services via `pwd.yml`, installed on the `frontend` site. `/all-products` returns HTTP 200; `/cart` returns HTTP 301 (redirect to login — expected for anonymous). Phase 1 Slices 7-9 + Phase 4 unblocked.
- **Framework verification done.** Read Frappe's actual website module source in the running container (`apps/frappe/frappe/templates/includes/{footer,navbar}/`, `public/scss/website/`). Confirmed agency `frappe-conventions.md` claims; **resolved the `.web-footer` height "constraint" myth** (no `max-height` rule in Frappe's footer.scss — the previous observation came from `lt-theme.css`'s `!important` chain interacting with body's flex-column sticky-footer pattern). Slice 2 redo now unblocked.
- **Webshop module mapped.** Documented which Jinja files to override for Slices 7-9 visual customization; cart-to-Quotation-to-Sales-Order-to-Payment-Request flow noted for Phase 4 Stripe wiring. All in the agency conventions doc.
- **Reproducible scripts.** Historical receipt: `scripts/setup/install_webshop.py` handled the first fresh install and post-recreate editable re-install path. Current runtime supersedes that path with the custom image; keep the script as fallback/history only. `scripts/dev/clear_website_cache.py` remains active after editing Jinja/CSS. `scripts/README.md` indexes the full scripts dir.
- **Bookkeeping cleanup.** `CLAUDE.md` "Currently working on" updated. `STATE.md` reflects actual progress (Slice 1 done, Slice 2 in flight). Queue's stale "Waiting on GL" section trimmed (Phase 1 gates were already resolved).
- **Standing principle codified.** Per GL directive 2026-04-26: *"work WITHIN Frappe, don't fight it."* Captured in `locally-twisted-decisions.md` as the operating principle for all UI/template work going forward.

**Code/infrastructure changes:**
- Historical: `apps/payments/` and `apps/webshop/` were cloned from upstream into the project and ignored. Current runtime is image-owned for these upstream apps; do not treat host clones as current source.
- Historical: `Locally-Twisted-Backend/frappe_docker/pwd.yml` added bind-mount lines for `payments` + `webshop` next to existing `locally_twisted` lines. Current runtime removed the upstream app bind mounts and keeps only the LT app live-edit overlay.
- `.gitignore` updated for `apps/webshop/` and `apps/payments/`
- Historical: nginx Origin patch was re-applied post-recreate. Current runtime has the Origin pass-through baked into the custom image.

**Documentation added/updated:**
- `Built_by_Cameron/.claude/capabilities/recipes/frappe-conventions.md` — added `payments` dependency note, `--skip-assets` install pattern, "Customizing webshop pages" primitive map, "Verified against source — 2026-04-26" appendix (with `.web-footer` myth correction)
- `_CLIENTS/locally-twisted/lessons-learned.md` — `.web-footer` entry rewritten with RESOLVED status + root cause + path forward
- `_CLIENTS/locally-twisted/HANDOFF.md` — full rewrite reflecting current state + Slice 2 redo plan
- `_CLIENTS/locally-twisted/locally-twisted-decisions.md` — entry on webshop install + "work within Frappe" principle + `.web-footer` resolution
- `_CLIENTS/locally-twisted/scripts/README.md` — new index of all scripts

**Slice 2 visual state UNCHANGED.** The `lt-theme.css` `!important` chains and the Slice 2 setup script's `Website Settings` content from the prior session are still in place — broken-honest. The Slice 2 redo will (a) strip `!important` chains and (b) override Jinja partials. That redo is the next session's work.

### 2026-04-26 (Slice 2 build session) — Slice 2 attempted, paused mid-execution; custom Frappe app scaffolded; meta-pattern documented

This session produced more documentation than working code, by design. The instance attempting Slice 2 (header + footer) hit a cascade of Frappe / ERPNext quirks (sanitizer, CSS load order, navbar markup, footer height constraint) and band-aided each one with `!important` overrides instead of studying the framework's intended customization primitives. GL stopped the session after a sequence of confidently-wrong claims about visible state. The session pivoted from "build Slice 2" to "study the framework, document everything for the next instance, leave broken state honestly visible."

**Code/infrastructure changes:**
- Custom Frappe app `locally_twisted` scaffolded via `bench new-app` inside the backend container, copied to host at `apps/locally_twisted/`, and bind-mounted into 8 frappe-image services via `pwd.yml` (so future edits flow through and survive container recreations).
- App installed on the LT site (`bench --site frontend install-app locally_twisted`).
- Theme CSS migrated from `Website Settings.head_html` (push-via-API anti-pattern) to a real bundled asset at `apps/locally_twisted/locally_twisted/public/css/lt-theme.css`, registered via `web_include_css` in app's `hooks.py`.
- LT logo PNG copied from legacy_source source to `apps/locally_twisted/locally_twisted/public/icons/lt-logo.png` and wired via `Website Settings.brand_html`.
- Social icons converted from inline-HTML SVGs (Frappe's HTML sanitizer was stripping `<path d=...>` attributes) to real SVG files in `apps/locally_twisted/locally_twisted/public/icons/{instagram,facebook,pinterest,twitter}.svg` referenced via CSS background-image.
- Removed redundant `_resources/lt-theme.css` source-of-truth file; canonical is now the file in the app.
- Updated `scripts/setup/setup_slice2_header_footer.py` to no longer push CSS to head_html (CSS is now served by the app).
- Created `scripts/verify/playwright_home_screenshot.py` — Playwright-based real-browser screenshot capture at desktop + mobile viewports with DOM facts dump, replacing the lower-fidelity `chrome --headless --screenshot` pattern.

**Documentation added:**
- `_CLIENTS/locally-twisted/anti-gl-patterns.md` — new section 0 "Building before understanding the framework" with full receipt of this session.
- `_CLIENTS/locally-twisted/lessons-learned.md` — 11 dated entries cataloging Frappe/ERPNext quirks (license casing, parent URL constraint, content_type field-routing, sanitizer, head_html cascade order, data URI silent failure, navbar-toggler markup, copyright auto-prepend, editable pip install lifecycle, the unresolved `.web-footer` height mystery).
- `_CLIENTS/locally-twisted/HANDOFF.md` — full rewrite reflecting honest broken state.
- `Built_by_Cameron/lessons-learned.md` — cross-client Frappe gotchas with a generalizable "study the source first" rule.
- `Built_by_Cameron/.claude/capabilities/recipes/frappe-conventions.md` — agency-tier reference for Frappe v15 customization primitives, the right way to override theme CSS / navbar / footer / pages, and the v15 ecommerce surprise.
- `_CLIENTS/locally-twisted/CLAUDE.md` + `Built_by_Cameron/CLAUDE.md` — added "Stack & code conventions" blocks pointing at the conventions reference.
- `<memory>/jeff_trust_and_phase_1_demo_stakes.md` — project memory: Jeff knows about the legacy_source attempt and lived its struggles; what he doesn't know is the full platform pivot to ERPNext.

**Decisions logged (in `locally-twisted-decisions.md`):**
- Custom Frappe app scaffolding moved from "deferred until critical mass" to "active build" status. Only Frappe Cloud cutover stays deferred until Phase 6.

**Critical surprise discovered:** ERPNext v15 has NO built-in webshop / cart / checkout module. The v14 `e_commerce` module was extracted to a separate app at `https://github.com/frappe/webshop`. Phases 1.7-1.9 (products listing, product detail, cart) and Phase 4 (Stripe + invoicing) require installing that app as a hard dependency. Decision pending.

**Known broken at session end:**
- Historical Slice 2 footer bug: footer brand block / social icons / address / copyright bar rendered outside the painted footer area due to `.web-footer`'s computed height being constrained to ~305 px. Root cause was not identified in that session; current footer treatment is governed by `_resources/STYLE-GUIDE.md`.
- Approved legacy_source structure (two-tier centered-logo header, 3-column footer, 3 social icons, hours block, etc.) substantively differs from what's currently wired up.

### 2026-04-26 (late) — Phase 1 Slice 1 done; reframe complete; image set generated

- Project reframed from "legacy_source → ERPNext migration" to "First professional business platform for LT, built on ERPNext" (PROJECT.md, ROADMAP.md, HANDOFF.md, STATE.md, queue, decisions log, all corresponding sections of CLAUDE.md updated)
- Reference Disposition section added to CLAUDE.md — legacy_source dir, Hetzner deployment, GitHub legacy_source repo, current `locallytwisted.com` all documented as temporary references that will be retired
- Resources brought into the project from the legacy_source dir + scrubbed of platform-specific references: `_resources/STYLE-GUIDE.md`, `_resources/utah-tax-rates-2026q2.md`, `_resources/policies/` (6 files including the legal interview answers from Jeff's contract-design sessions)
- **Phase 1 Slice 1 — brand foundation — DONE, later superseded.** LT theme CSS installed the first full design system. Current active CSS uses the 2026-05-05 Cormorant Garamond + Lato and Civic Celebration + Slate Blue/Berry + Brand Direction reset instead of this original Slice 1 font/palette contract.
- All Phase 1 decision gates resolved (header nav B, accessibility B, blog yes, photography placeholders, customer-inquiry email = locallytwisted@gmail.com, pricing calc embedded in BTFP page)
- 15 brand-aligned placeholder images generated via Together API FLUX.1-schnell (~$0.05). Mapped slot → file → use in `_resources/images/INDEX.md`
- ERPNext user records cleaned: `locallytwisted@gmail.com` renamed "Jeff Baen" → "Jeff Kimber" (Baen was Cameron's middle name that got tangled); `locallytwisted@yahoo.com` placeholder disabled (reversible)
- Agency-tier capabilities added: `together-image-gen` ingredient + `generate-client-image-set` recipe (transferable to any future BBC client) at `Built_by_Cameron/.claude/capabilities/`
- Stale artifacts deleted: `.planning/phases/01-inventory/` (research from old framing), empty `Locally-Twisted-Frontend/`

### 2026-04-26 — Restructure: BBC root → agency-level; LT lives in `_CLIENTS/locally-twisted/`

- All LT-specific artifacts moved from BBC root into this folder; LT got its own git repo
- BBC root refactored to be agency-level (cross-client rules, port allocations, v15 standard, voice & language general rule)

### 2026-04-26 — Lead schema customization complete (carried into the new framing)

- 45+ Custom Fields on Lead with sectioned layout, Table MultiSelect for Service Type, conditional sub-section visibility, plain-text time entry for estimated event times, +Delivery Window Start/End, +Internal Only Notes, +Inspiration Photos child table connected through `custom_inspiration_photos`, label renames via Property Setter, hidden "Additional Information" tab, max upload 25 MB
- nginx /socket.io/ Origin pass-through patched

### 2026-04-25 — ERPNext install + setup wizard

- Installed LT ERPNext at `:8081` (compose project `locally-twisted-erpnext-v15`, frappe_docker pwd.yml pinned to v15.105.0)
- LT Company record seeded with real address, phone, email, website
- Off-legacy_source expedition findings reviewed (5-researcher convergence; ERPNext recommended)
