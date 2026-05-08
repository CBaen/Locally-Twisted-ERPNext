# Locally Twisted - Coding Handoff

Last updated: 2026-05-08 by OpenClaw/Moji after GL clarified all current LT data is fake/test data and Codex identified the first record-level fail-loud hardening slice. Current peer handoff: fake data is allowed and useful; fake success is forbidden. Start backend automation work at `workstreams/fail-loud-record-level-hardening.md` before any reminder-send, Frappe Cloud trust, or live-data claim.

## State Of Reality

The ERPNext build is active at `http://localhost:8081`. The project is **a migration of Locally Twisted's business intent + catalog data into a fresh ERPNext install** (frame revised 2026-04-30 — see `locally-twisted-decisions.md`). "Fresh install" — destination is greenfield ERPNext; no auto-translated Odoo modules or DB dumps. "Migration" — catalog records (53 Website Items / 10,578 original variants / 10,613 original catalog Item Prices, ported 2026-04-30), form intent, policies, voice/brand all carried across from the prior Odoo attempt and the legacy `locallytwisted.com` site, and the new storefront replaces `locallytwisted.com` at cutover. The current live DB now has 10,672 Items and 10,654 Item Prices after delivery service Items and the optional-add-on variant repair.

The catalog port from the old Odoo test deployment appears real, but several docs had stale counts. The Odoo shop at `http://5.78.136.133/shop` was used as the catalog source/reference for that port because GL explicitly named it as the old live account/source for catalog data. That does not make Odoo the product truth for unrelated business scope.

Verified DB counts on 2026-05-08:

| Record | Count |
|---|---:|
| Website Items | 53 |
| Items total | 10,672 |
| Variant templates | 49 |
| Non-variant root Items | 6 |
| Active customer-facing variants | 10,227 |
| Disabled legacy optional-add-on variants | 390 |
| All variant records | 10,617 |
| Item Prices | 10,654 |
| Item Variant Attribute rows | 32,028 |
| Item Attributes | 26 |

Docs that still mention `10,631 Items`, `10,613 Items`, `10,633 Items`, `10,613 Item Prices`, `10,615 Item Prices`, `8,925 Item Prices`, `4 single-SKU templates`, `10,560 variants`, or `10,578 variants` as current DB totals are stale. The 6 non-variant root Items are 4 catalog single-SKU products plus 2 delivery service Items. `Add Foil Number` is now optional for bouquet-size products, so the customer-facing active variant count is lower than the original raw port; the disabled legacy add-on variants remain in the database as history.

## Current Stopping Point

Record-level fail-loud hardening is the active backend automation handoff from GL/Codex/OpenClaw. All current LT data is fake/test data for automation testing until GL explicitly says otherwise. Use it aggressively to prove automation, but do not treat it as live business truth. The next safe implementation slice is documented in `workstreams/fail-loud-record-level-hardening.md`: create a reusable backend failure recorder, then wire Lead cascade partial failures, checkout note/Lead-conversion failures, paid-order receipt failures, and record-level business automation index rows.

Category browse media is parked as of 2026-05-06. The safe prep work is done: candidate report generation, approval-template generation, dry-run Frappe sync, and unapproved-apply refusal are available. No live Item Group images were assigned, and the latest DB check still showed all 11 customer-facing child Item Groups under `Shop Items` with `image = null`.

Resume the category media lane only after GL/Jeff approve the category image selections. The resume path is: regenerate `output/category-media-candidates.md`, create or update the approval file, mark only approved rows with `approved: true`, dry-run `scripts/setup/sync_category_media.py`, then use `--apply` only for approved selections. Do not assign category media by judgment and do not revive `/shop-by-category`.

## Actually Working, Pending Re-Verification

Verified or updated during the 2026-05-01 storefront correction and contact cleanup passes:

- `/contact` is the canonical customer inquiry form. `/book` returns a 301 to `/contact?intent=quick`; do not rebuild `/book` as a separate public page.
- Fail loudly is now the operating law across LT: forms, automations, payments, documents, customer communication, route/container contracts, verifiers, and agent claims must block false success and leave actionable evidence. Project entrypoint: `.codex/capabilities/recipes/fail-loud-operating-law.md`.
- `/balloon-twisting-and-face-painting` is now a contact-led editorial service page using real BTFP information, an event-type crawl, and the shared inquiry form scoped to live artist service choices. It has no public deposit-checkout CTA.
- `/contact` supports guided prefill for `?service=btfp`, `?service=twisting`, and `?service=face-painting`.
- `scripts/verify/smoke_forms.py` now verifies localhost `/contact` submissions through the local Docker/Frappe bench container and cleans up the generated smoke Lead plus linked LT cascade Task. Latest run on 2026-05-06 created marker `SMOKE-TEST-1778091063`, verified it, and reported cleanup OK.
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
- Header/menu now uses the deliberate premium two-level mega-menu: full-height Locally Twisted logo image, desktop `Event Balloons` and `Ready-to-Order` mega panels, `Portfolio`, `Twisting & Face Painting`, `FAQ`, search/cart, top proof row, mobile drawer accordions, and `Free Event Quote` pointed at `/contact`. Feature handoff for the BTFP/Process correction lives at `workstreams/nav-btfp-process-correction.md`.
- Header color repair completed 2026-05-06 after GL flagged the all-black chrome as off-style. The mega-menu contract stayed intact, but `lt-mega-menu.css` now uses a style-guide split: slim deep-navy desktop proof row, warm-white desktop main nav, warm-white mobile header/drawer surfaces, berry CTA, brass borders, and ink text. `hooks.py` cache-bust is `lt-mega-menu.css?v=20260506-mega-5`, and `interactive_layout.spec.js` guards against regressing the header shell back to the black ink band.
- `/event-balloons`, `/portfolio`, and `/balloon-twisting-and-face-painting` are real public routes and return 200 locally. `/process` was unapproved and has been removed from the customer-facing site contract. `/portfolio` now keeps only the approved collage-of-imagery and movement behavior from the external prototype: native LT shell/global typography, branded compact portfolio hero, 1.5x larger desktop installed-work images, frequent center-column photos, optimized WebP derivatives, no cropped cards, no captions, no visible frame wrappers, no route-specific Inquire/Studio/Index footer block, actual image dimensions, mobile full-width slide-in reveal, and click-to-front interaction. Do not reintroduce the copied prototype hero, portfolio-specific font imports, custom cursor, fake internal nav/shell, static mobile stacking, photo captions, frame/card wrappers, forced design-slot aspect ratios that create letterbox stripes, route-local portfolio contact/index/footer sections, or full Claude/designer page styling. Category/event query links still filter the photo payload server-side. The research folder remains critique input only; the Frappe implementation, optimized assets, and verifier are the kept production source.
- The mega-menu source contract is active: `navbar_context.py`, `templates/includes/navbar/navbar.html`, `public/css/lt-mega-menu.css`, and `public/js/lt-megamenu.js` must stay in parity with `hooks.py`, `nav_ia.py`, and `smoke_shop.py`.
- Footer no longer exposes `What We Make`, `About Us`, or `Book an Event`; `All Ready-to-Order` routes to `/shop`.
- Product detail/configure templates no longer include the "Start a conversation" or "Tell us what you're imagining" sales-pitch blocks.
- `/shop-items/arches` now scopes to Arches. Root cause was missing Webshop `.item-group-content` class in the custom Item Group wrapper, not catalog data.
- `/shop` is the customer-facing all-decor hub. `/shop-items`, `/all-products`, and `/shop-by-category` route or redirect to `/shop`; individual category pages remain at `/shop-items/<group>`.
- Shop category navigation was repaired 2026-05-06 after GL rejected the button/tile treatment: `/shop` and `/shop-items/<group>` now share `templates/includes/shop_category_nav.html`; desktop uses a slim left rail, mobile uses a native select, and future work must not restore `/shop` chips or the category-page button wall.
- Project-level Codex capabilities are installed at `.codex/capabilities/` and routed from `AGENTS.md`; ephemeral Codex validation found the index and read the `screenshot` ingredient.
- `/book` is retired as a customer-facing page and redirects to `/contact?intent=quick`. Current CTAs should use `/contact`; old `/book` traffic is compatibility only.
- `/privacy` and `/terms-of-service` exist as static Frappe routes and return HTTP 200 locally. Current copy reflects GL business-proxy answers from 2026-05-06 for delivery, returns, tax wording, cookies/tracking, children/privacy, opt-out event photo use, invoice acceptance, and temporary balloon/service limitations. A sitewide cookie/tracking accept/decline notice stores `lt_cookie_consent`; future optional analytics/ads/tracking must honor that stored choice. Legal/accounting review and Stripe Dashboard URL wiring are still separate follow-ups.
- Customer-facing policy documents now use anchored lanes on `/terms-of-service` and `/refund-policy`: event balloon decor, ready-to-order pickup/delivery, face painting/balloon twisting, and corporate invoicing. `locally_twisted.policy_documents` owns reusable policy blocks for code-owned receipt/inquiry emails. Do not add ERPNext Terms/Email Template records unless a verified customer-facing invoice path truly requires them; LT should stay as whitelabel/code-owned as possible. Run `python scripts/verify/customer_documents_contract.py` after changing customer document copy.
- Branded Sales Invoice output is now code-owned. `scripts/setup/sync_invoice_branding.py` creates/updates the `Locally Twisted Sales Invoice` Print Format, `Locally Twisted` Letter Head, and the Sales Invoice `default_print_format` Property Setter. The Print Format itself carries the visible logo/contact header so the normal default print view is branded. The default invoice is intentionally black/white/gray and accounts-payable friendly; gray vertical callouts are allowed for secondary AP/terms information, and the bottom support banner stays solid black with the approved customer-service/repeat-order copy. Keep dog-logo, gold, patriotic/civic proof, and marketing-style decoration for proposals, event packets, reorder follow-ups, portfolio, and client-facing marketing surfaces, not ordinary Sales Invoices. The current format uses smaller sizing, scoped table padding, fewer outlined containers, horizontal rules, and neutral gray left-rule callouts so ordinary invoices fit one PDF page. `scripts/verify/invoice_branding_contract.py` verifies the records, default print render, logo asset, AP fields, gray callouts, black support-banner treatment, forbidden gold/dog/promo markers, and rendered invoice HTML against `ACC-SINV-2026-00001`.
- Standard outbound document source now lives at `apps/locally_twisted/locally_twisted/outbound_documents/`. It includes an automation registry plus source templates for Sales Invoice, Payment Receipt, Quote / Estimate, Event Proposal Packet, Vendor Setup / W-9 Packet, Statement Of Account, Payment Reminder Draft, Event Install Work Order, Contract Acceptance Summary, and Post-event Reorder Follow-up. These are generator-ready with review gates; they do not authorize automatic sending. The standing outbound standard is answer-first: customer-facing document previews should show `Key fields to review` before internal automation concerns, and every source template must include `## Answer First`. `scripts/verify/outbound_documents_contract.py` guards the registry and required template fields. `scripts/verify/render_outbound_document_previews.py` renders fake-data normal/outlier HTML, PDF, and PNG review artifacts; the current answer-first set is at `output/playwright/outbound-documents-answer-first-20260506/index.html`.
- Business automation indexing is now code-owned and scheduled. `workstreams/business-automation-index.md` is the cross-system map; `locally_twisted.verify.business_automation_index.run` classifies intake, CRM, checkout, payment, paperwork, finance, and checkup surfaces as connected, partially connected, missing-required, or missing-useful. `scripts/verify/business_automation_index.py --report output/business-automation-index.json` currently passes with 22 surfaces indexed, 12 launch-required, 18 connected, 4 exists-but-not-connected, 0 launch-required missing, 0 useful future surfaces missing, and 0 loud-failure gaps. `hooks.py` runs `locally_twisted.verify.business_automation_index.scheduled_checkup` daily; if a launch-required connection breaks or a loud-failure gap appears, it writes a Frappe Error Log.
- Synthetic backend operating readiness is separate from live cutover readiness. `scripts/verify/synthetic_business_pipeline.py --report output/synthetic-business-pipeline.json` runs no-live/fake-data/rollback-safe checks for Stripe amount parity, checkout-to-Lead conversion, checkout fulfillment, paid-order cascade, mocked webhook behavior, customer document policy, outbound document templates, unpaid invoice outlier packets, customer reminder dry-run outliers, and customer reminder review-report outliers. Latest result: 10 synthetic contracts, 10 pass, 0 broken piping, 9 inefficiencies/partial connections, 3 cutover-deferred items. It does not require live Stripe keys, real operator data, or real customer records.
- Stripe Checkout amount parity now has a contract. `stripe_line_items_for_sales_order()` builds hosted-checkout line items from the ERPNext Sales Order and adds a `Sales tax and charges` adjustment when needed so Stripe totals match `Sales Order.grand_total`. If item lines would exceed the ERPNext total, it raises `frappe.ValidationError` instead of under/overcharging silently. `scripts/verify/stripe_amount_parity_contract.py` covers taxable, nontaxable, and negative-adjustment cases.
- Legal/accounting review packet lives at `_resources/policies/legal-accounting-review-packet-2026-05-06.md`.
- `/event-playground` is a hidden internal-preview route for the first PlayCanvas decor planner, but GL moved the next PlayCanvas/Event Playground pass to OpenClaw. Keep it out of the ASAP website launch lane unless GL explicitly reopens it here. The PlayCanvas/Vite source lives under `research/design-studio-v2/event-builder-spike/`; the Frappe route shell is `www/event_playground.html`/`.py`; and the route wraps the local Vite preview at `127.0.0.1:4306` in an iframe. The OpenClaw handoff source now reframes the browser preview as `Plan Custom Decor`, upgrades the local payload to `event-playground-v2`, adds `design_studio_contract.schema_version = design-studio-v1`, adds event date/city contact fields, and exposes quote-honesty warnings. Render counts are explicitly visual density, not quote math. Production estimates are candidate-only, `quote_ready: false`, and `customer_visible: false` until Locally Twisted approves formulas, fill/support assumptions, overage, venue review, and pricing. Submit Inquiry still hands the design to `/contact?intent=quote&source=event-playground` through `postMessage` + `sessionStorage`; the existing contact form now pre-fills name, email, phone, ISO event date, event location/city, services, colors, decor type, package notes, and the design summary. There is no public nav entry, committed production bundle, DocType, backend save API, automatic Lead/Quote/Sales Order creation, pricing, checkout, CAD, room scanning, share link, or full organic/twisting physics in this slice.
- Product listing cards can display `lt_brand_description` through the local Webshop API wrapper in `locally_twisted.api.product_listing`.
- Variant media first pass completed 2026-05-02. ERPNext now has 1,712 variant `Item.image` values mapped from `_resources/odoo-live/images/` where Odoo image labels clearly matched product options. Product detail pages call `locally_twisted.api.variant_media.get_variant_media` after exact option selection and swap the main image when a variant image exists. Cart/checkout use the variant image when present and fall back to the parent Website Item image otherwise. The review command `python scripts/setup/sync_variant_media.py --dry-run --include-details --report output/catalog-media-review.json` currently reports 49 products checked, 35 with candidate image labels, 45 needing review, 1,712 unchanged mapped variants, and 6,831 skipped variant image assignments.
- Category browse media is still empty in ERPNext: all 11 customer-facing child Item Groups under `Shop Items` have `image = null` as of the 2026-05-06 DB recheck. `python scripts/verify/category_media_candidates.py` now creates a no-mutation approval packet from existing product-source and portfolio-proof media, with quick picks for all 11 categories in ignored local `output/category-media-candidates.md`. `scripts/setup/sync_category_media.py` creates the approval template and dry-runs the Frappe-backed Item Group image update path; `--apply` only writes rows marked `approved: true`. Do not revive `/shop-by-category`; choose representative category media for `/shop-items/<group>` or future menu treatment only after Jeff/GL approval.
- Product detail breadcrumbs now use `All Balloon Decor > category > product`; the retired `Shop by Category` label/link is blocked by `scripts/verify/smoke_shop.py`.
- Product detail pages are now company-first and clear-control, not generic ecommerce recommendation or boxed-option surfaces. The Webshop lower Additional Info/Reviews/Recommended Items panel was removed on 2026-05-07, the old auxiliary/recommendation CSS selectors are gone, and product options/variant chips/selects/price-add-to-cart groups are no longer framed boxes. Pickup/delivery is the approved framed product-page exception. `smoke_shop.py` fails if the recommendation selectors return or if product option controls regain boxed backgrounds, borders, or shadows. Use `.codex/capabilities/recipes/frappe-product-page-company-first.md` and `.codex/capabilities/recipes/frappe-product-clear-control-contract.md` before changing product detail templates or product-page CSS.
- Civic Celebration is now the V1 visual direction across the public site. See `_resources/STYLE-GUIDE.md`, `workstreams/brand-audience-style-reset.md`, and `workstreams/civic-sitewide-redesign.md`. The pass covers shared header/footer/theme CSS, homepage, contact/book form, BTFP, portfolio, FAQ, policies, accessibility, thank-you/payment success, shop, category pages, product detail, cart, and checkout. The homepage hero now uses the real optimized install photo `apps/locally_twisted/locally_twisted/public/images/portfolio/optimized/corporate-weberstock-photo-opt.webp`, not the generated Wasatch-only background.
- Compact hero standard is now implemented and guarded. Public page heroes use 220px mobile, 250px tablet, and 280px desktop standard heights, with padding/title caps documented in `_resources/STYLE-GUIDE.md` v4.5 and `.codex/capabilities/recipes/compact-hero-contract.md`. The current verifier covers `/`, `/event-balloons`, `/portfolio`, `/balloon-twisting-and-face-painting`, `/contact`, `/shop`, and `/shop-items/seasonal-specialty` through `npm run test:interactive-layout -- --grep "compact hero height contract"`. The root cause was stacked page-local hero sizing: global `section` padding, route-level min-heights, inner padding, and giant title clamps all competing.
- Homepage launch repair completed on 2026-05-07: the hero uses one visible stable H1, the first viewport shows Google reviews immediately after the hero on desktop and 320px mobile, the homepage trust/authority bar is removed for now while the icon assets are preserved, the cookie notice renders inline after reviews instead of covering CTAs, Recent Celebrations appears after review cards, the closing CTA leads with corporate/school/civic/community work, and stale homepage v2/design-studio comments were removed.
- Homepage review cards and the trusted-business client crawl both crawl left-to-right as full-stage horizontal proof lines. Review cards use the canonical `540s` loop; a homepage-only sync script measures both duplicated tracks and assigns the trusted-business crawl a proportional duration so its visible pixel speed matches the reviews. Reduced-motion mode intentionally keeps these two business-proof crawls slow, moving, horizontal/full-stage, and scrollbar-free; do not restore the static/overflow fallback that caused the recurring real-browser failure.
- Current crawl verification on 2026-05-07 proved left-to-right deltas, hidden overflow, matched visible speed, and moving reduced-motion proof crawls. The deliberate red run failed 5/5 against the previous right-to-left direction; the corrected implementation then passed focused crawl regression 5/5, home layout 13/13, homepage/cookie 12/12, compact hero 14/14, and full `npm run test:website-verify`. Live diagnostics showed positive left-to-right deltas with hidden overflow and near-zero speed delta in both `no-preference` and `reduce`; screenshots are in `output/playwright/home-crawl-left-to-right-20260507/`.
- Homepage feature handoff: `workstreams/landing-page-repair.md`. Capability contract: `.codex/capabilities/recipes/homepage-launch-proof-contract.md`.
- `_resources/STYLE-GUIDE.md` version 4.3 is the only current visual authority. The old `_resources/design-guide/`, stale shop/spec comparison docs, and generic icon-comparison resources were deleted on 2026-05-05 because they conflicted with Civic Celebration + Slate Blue/Berry + Brand Direction and kept reintroducing light-blue/blush, old-font, and weak-icon choices.
- Rendered site repair pass completed 2026-05-05: mega-menu assets are served through hooks, desktop click pins mega menus open, mobile drawer opens accordions, product/shop pages use `lt-product-polish.css`, broad route containment uses `lt-page-containment.css`, and the homepage/portfolio/newsletter mobile clipping issues were fixed.
- Responsive container integrity is now a standing launch gate, not a one-off fix. `scripts/verify/layout_helpers.js` centralizes public routes, breakpoint-edge viewports, overflow/text-fit checks, and the executable route-level container contract. After the compact hero contract, `npm run test:layout-fit` covers 247 passive route/viewport checks across the current public route list and 13 viewport families; `npm run test:container-contract` covers 57 route/viewport container checks across 19 launch public routes at 320px, 820px, and 1366px; `npm run test:interactive-layout` covers 88 stateful checks for compact heroes, platform-name leakage, header breakpoint behavior, desktop mega panels, mobile drawer accordions, shop/product controls, contact conditionals, portfolio front-photo state, homepage proof crawls, cookie placement, and reduced-motion homepage states. `npm run test:portfolio-reel` is the route-specific proof-gallery gate.
- Public containers are now code-owned, not advisory prose. `CONTAINER_CONTRACT_ROUTES` declares every visible direct `.page_content` child and each section's mode (`band`, `fullbleed`, `contained`, `clip`, `raw-band`, `root`, or `visual-field`). The first full matrix exposed real drift in homepage twisting spotlight containment, portfolio footer markup, contact/location Bootstrap containers, document narrow-width selector specificity, BTFP route surfaces, and BTFP event-crawl data. `lt-page-containment.css` now loads after product/shop CSS so it remains the final public containment layer.
- `npm run test:website-verify` is the website-only closeout gate: nav IA, passive layout, route-level container contract, interactive layout, checkout experience, portfolio reel, and shop smoke. `npm run test:public-verify` aliases to the same website-only gate. Event Playground remains separately available through `npm run test:event-playground` for the OpenClaw lane. Latest full verification on 2026-05-07 passed: nav IA, `layout-fit` 247/247, `container-contract` 57/57, `interactive-layout` 88/88, `checkout-experience` 2/2, `portfolio-reel` 4/4, and `smoke_shop.py`.
- The active theme/app source has been cleaned away from old font and UI-pastel references. Do not reintroduce `DM Serif`, `Raleway`, `Montserrat`, `Playfair`, `lt-blush`, `lt-soft-blue`, old `soft-blue`/`light-blue`, UI `blush`, or unresolved `--lt-primary` in customer-facing source.
- A 16-asset custom brass-line icon suite now lives at `apps/locally_twisted/locally_twisted/public/icons/brand/`. Balloon-specific surfaces should use balloon-form icons first: pair, cluster, arch, organic garland, column, and bouquet.
- The contact page no longer depends on an external map iframe for the main service-area proof; it uses a controlled service-area panel.
- Per-product variant correctness now compares normalized Odoo `valid_variants` to active, required-choice ERPNext variants. Current pass on 2026-05-08: 53 products checked, 10,227 expected active variants, 10,227 live active variants, 4 single-SKU products. Disabled legacy optional-add-on variants are intentionally ignored by this customer-facing contract.
- Product option UX P0 pass completed 2026-05-02 and was reconciled with the current commerce lane on 2026-05-05. `item_configure.html` no longer runs per-attribute `frappe.get_all` lookups from Jinja; it uses `get_variant_attribute_options`, a project Jinja helper backed by Webshop's `get_attributes_and_values`. Quote-required custom installs such as Arches and Garlands intentionally show a `/contact?item=...` quote CTA instead of cart selectors. Retail variants such as `unicorn-bouquet` still render inline single-select chips/selects, consume `valid_options_for_attributes`, and write selected variant codes to `LT_CART`.
- Generated Webshop asset-map drift was corrected in the running ERPNext stack on 2026-05-02. The container already has Yarn Classic at `/home/frappe/.nvm/versions/node/v20.19.2/bin/yarn`, but non-interactive `docker exec` does not include that directory in `PATH`. Use `export PATH=/home/frappe/.nvm/versions/node/v20.19.2/bin:$PATH` before `bench build --app webshop`; no package install was needed. Important Docker nuance: the frontend/nginx container must be the final Webshop build target because `sites/assets/webshop` links to each container's own app-public files while `assets.json` is shared. Building only in the backend writes asset-map names nginx cannot serve. After rebuilding from the frontend container and clearing `assets_json` plus website cache, follow-up console checks returned 200s with 0 console errors/warnings.
- `scripts/verify/layout_fit.spec.js` is the committed passive Playwright Test gate. Latest full verified command: `npm run test:layout-fit` -> 247 passed across the current route list and 13 viewport families, including `/checkout` and `/thank-you`; latest impacted rerun after the portfolio mobile fix was `npm run test:layout-fit -- --grep "home fits|portfolio fits"` -> 26 passed. `scripts/verify/container_contract.spec.js` is the route-level public container contract; latest verified command: `npm run test:container-contract` -> 57 passed. `scripts/verify/interactive_layout.spec.js` is the stateful layout gate; latest verified command: `npm run test:interactive-layout` -> 88 passed. `scripts/verify/portfolio_reel.spec.js` is the route-specific proof-gallery gate; latest verified command: `npm run test:portfolio-reel` -> 4 passed.
- Catalog variant counts match the normalized Odoo source: the raw scrape has duplicate-case latex color values, but `_resources/odoo-live/value_normalize_map.json` collapses them and the normalized expected variant counts match ERPNext.
- Website cache was cleared after Jinja/CSS changes; the backend was restarted after `home.py` route CSS changed; `hooks.py` cache-busts were bumped for `lt-site-preferences.js` and `lt-page-containment.css`.

Claims from older docs still need re-verification before being repeated:

- ERPNext v15.105.0 stack on port `8081`.
- `locally_twisted` custom app installed.
- Webshop + payments installed.
- 53 Website Items published.
- `/shop-by-category` compatibility redirect to `/shop`.
- Local guest cart and Stripe test-mode checkout flow.
- Payment backend launch-readiness now has a feature lane at `workstreams/payment-backend-launch-readiness.md`; use `scripts/verify/payment_launch_readiness.py` for non-secret structural checks. Local mode passes; live mode is expected to fail until production Stripe/site config exists.
- Existing pages including `/`, `/lookbook`, `/shop`, `/contact`, `/faq`, `/refund-policy`, `/accessibility`, `/cart`, `/checkout`, `/payment-success`, `/thank-you`.

Treat these as verified only after re-running smoke tests or checking the routes. Do not repeat a visual claim without screenshots.

## Paperwork / Backend Automation Focus

Current coordination lanes: `workstreams/paperwork-backend-automation.md`, `workstreams/business-automation-index.md`, `workstreams/synthetic-business-pipeline.md`, `workstreams/customer-reminder-dry-run.md`, `workstreams/customer-reminder-review-report.md`, and `workstreams/fail-loud-record-level-hardening.md`.

Fresh baseline on 2026-05-06:

- `finance_inventory.py --json`, `customer_documents_contract.py`, `payment_cascade_contract.py`, `crm_stage_cascade.py`, `backend_schema_inventory.py`, `payment_backend_config_contract.py`, `payment_webhook_contract.py`, `payment_launch_readiness.py`, `checkout_lead_conversion_contract.py`, `finance_workspace_parity.py`, and `finance_inventory_contract.py` passed locally.
- `paperwork_status.py --report output/paperwork-status.json` passed in `synthetic_without_live_credentials` mode. It does not run live payment readiness in this lane; live Stripe keys/webhook/production host/operator setup are reported under `cutover_deferred_not_blocking`.
- `business_automation_index.py --report output/business-automation-index.json` passed and generated the current cross-system automation report: 22 surfaces, 12 launch-required, 18 connected, 4 exists-but-not-connected, 0 launch-required missing, and 0 loud-failure gaps.
- `synthetic_business_pipeline.py --report output/synthetic-business-pipeline.json` passed with 10 no-live synthetic contracts, 0 broken piping, 9 inefficiencies/partial connections, and 3 cutover-deferred items.
- `stripe_amount_parity_contract.py` passed and now guards Stripe hosted-checkout totals against ERPNext Sales Order totals.
- `sync_invoice_branding.py` passed and is idempotent; `invoice_branding_contract.py` passed against rendered Sales Invoice HTML and now guards the gray invoice callouts plus black support-banner/no-gold/no-dog standard.
- `outbound_documents_contract.py` passed against the answer-first standard outbound document registry and templates.
- `render_outbound_document_previews.py --slug outbound-documents-20260506` generated 20 fake-data normal/outlier document previews for review.
- Live Stripe keys, webhook secret, production host, and real operator/customer data are cutover-only. They are intentionally not part of the current fake-data/synthetic readiness gate.
- Local finance inventory found 4 Customers, 8 Sales Orders, 1 Sales Invoice, 8 Payment Requests, 0 Payment Entries, 0 Bank Accounts, 0 Suppliers, and 0 Employees. Payment Terms exist locally; bank/supplier/payroll setup remains incomplete.
- The paperwork status report currently flags 1 unpaid/overdue Sales Invoice, 8 expected Payment Requests, Email Queue status counts of 30 Sent, and no pending email queue rows.
- The unpaid/overdue invoice review surface now exists at `locally_twisted.paperwork.unpaid_invoice_review.run` with host verifier `python scripts/verify/unpaid_invoice_review.py --report output/unpaid-invoice-review.json`. It currently returns 1 overdue-review candidate for `ACC-SINV-2026-00001`, with draft-only `payment_reminder_draft` and `statement_of_account` document candidates. It marks `read_only: true`, `send_allowed: false`, `mutation_allowed: false`, and includes a mutation guard for Email Queue, Communication, Sales Invoice, Payment Request, Payment Entry, and Journal Entry counts.
- The unpaid invoice draft packet renderer now exists at `locally_twisted.paperwork.unpaid_invoice_draft_packet.run` with host verifier `python scripts/verify/unpaid_invoice_draft_packet.py --report output/unpaid-invoice-draft-packet.json`. It turns review candidates into human-review packet sections for `payment_reminder_draft` and `statement_of_account`, still marked `draft_only_not_sent`, with `read_only: true`, `send_allowed: false`, `mutation_allowed: false`, and the same mutation guard. `python scripts/verify/unpaid_invoice_draft_packet_contract.py` covers fake normal/outlier packet behavior without touching ERPNext records.
- The internal paperwork review digest now exists at `locally_twisted.paperwork.paperwork_review_digest.run` with host verifier `python scripts/verify/paperwork_review_digest.py --report output/paperwork-review-digest.json`. It combines paperwork status, business automation index, unpaid invoice review, and draft packet output into one read-only review payload without sending customer messages or mutating accounting records. It labels live Stripe/production setup as `cutover_deferred_not_blocking`, not as a current blocker.
- The customer reminder dry-run queue now exists at `locally_twisted.paperwork.customer_reminder_dry_run.run` with host verifier `python scripts/verify/customer_reminder_dry_run.py --report output/customer-reminder-dry-run.json`. It turns the digest and draft packets into internal review queue items with cadence suggestions, draft sections, and blockers. It is explicitly `no_live_internal_review`, with `send_allowed: false`, `customer_delivery_enabled: false`, `automatic_delivery_enabled: false`, and no Email Queue, Communication, Error Log, payment, journal, or invoice mutations. `python scripts/verify/customer_reminder_dry_run_contract.py` covers fake overdue/current/missing-payment-path/malformed-send scenarios.
- The customer reminder review report now exists at `locally_twisted.paperwork.customer_reminder_review_report.run` with host verifier `python scripts/verify/customer_reminder_review_report.py --report output/customer-reminder-review-report.json`. It turns dry-run queue items into report columns, rows, and `review_now` / `hold` / `blocked_send` groups for a future Desk page or internal-only report. It is explicitly no-live/read-only, with `send_allowed: false`, `customer_delivery_enabled: false`, `automatic_delivery_enabled: false`, and no Email Queue, Communication, Error Log, payment, journal, or invoice mutations. `python scripts/verify/customer_reminder_review_report_contract.py` covers fake mixed/empty/malformed-send source scenarios.
- The business automation index currently classifies quote/proposal generation, vendor setup/W-9 packets, bank reconciliation, and payroll/HRMS as existing but not connected. These are not silent unknowns anymore.
- Customer document policy blocks, paid-order receipt/operator/welcome email cascade, and inquiry acknowledgment policy lanes are covered by verifiers.
- Sales Invoice print output defaults to the branded Locally Twisted format and includes the corporate invoicing policy lane.
- External document audience standards started at `.codex/capabilities/recipes/external-document-audience-contract.md`, with source templates in `locally_twisted/outbound_documents/`. Use those before building invoices, receipts, proposals, event packets, vendor setup/W-9 packets, statements, or other documents that leave the company.
- CRM stage movement remains operational Task-only and must not create finance records until thresholds are explicitly decided.

Next safe paperwork/backend slice: implement the reusable backend failure recorder and record-level automation checkup rows from `workstreams/fail-loud-record-level-hardening.md`. The reviewed Desk page for reminder report rows comes after the failure-recorder/checkup backbone, because the report UI should consume loud blocker state rather than inventing its own judgment. Keep using synthetic/fake data to flush out cascading fields and broken piping. Do not send reminders, create live bank sync, auto-submit accounting records, wire CRM stages to finance, or mix live credentials/real customer data into this work.

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
- Review skipped/unmatched catalog media with GL/Jeff: parked until approval. The automated pass only mapped photos whose Odoo labels clearly matched product options. Refresh `output/catalog-media-review.json` with the detailed dry-run command before assigning anything. Regenerate `output/category-media-candidates.md` for the 11 category quick picks before the approval conversation. Do not assign generic gallery images by guess.
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
cd research/design-studio-v2/event-builder-spike
npm run test:classic
npm run build
npm run verify:event-playground
npm run verify:v2
cd ..\..\..
npm run test:event-playground
```

Contact form logic regression checks:

```powershell
python scripts/verify/contact_service_logic.py --base-url http://localhost:8081
python scripts/verify/contact_prefill.py --base-url http://localhost:8081
python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --form-path /contact --skip-newsletter
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
