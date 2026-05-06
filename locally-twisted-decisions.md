# Locally Twisted — Decisions Log

**Append-only.** Newest entries at the top. Each entry: date, decision, reasoning, alternatives considered, and who decided.

Reasoning matters more than the decision itself. A future instance reading this should be able to tell whether the decision still applies given new context, or whether the conditions that justified it have changed.

LT-specific decisions only. Cross-client / agency-wide decisions live at `Built_by_Cameron/built-by-cameron-decisions.md`.

---

## 2026-05-06 - Business automation must be indexed and scheduled before Frappe Cloud trust

**Decision:** LT's backend automation is now governed by a code-owned automation index, not by prose handoff memory. The index classifies every important intake, CRM, checkout, payment, paperwork, finance, and checkup surface as `exists_and_connected`, `exists_but_not_connected`, `missing_needs_connection`, or `missing_should_connect`. Launch-required breakage must fail the verifier loudly, and the daily Frappe scheduler runs the checkup so failures can become visible backend attention.

**Reasoning:** GL explicitly called out that silent failures kill business relationships and reputation. The LT system is becoming an all-in-one business-management platform, so it needs a repeatable map of cascading information before moving to Frappe Cloud. A template, DocType, or native ERPNext feature is not operational just because it exists.

**Implementation:** Added `locally_twisted.verify.business_automation_index`, host wrapper `scripts/verify/business_automation_index.py`, workstream `workstreams/business-automation-index.md`, project capability `erpnext-business-automation-index`, and a daily scheduler hook for `locally_twisted.verify.business_automation_index.scheduled_checkup`. The current report indexes 17 surfaces: 12 connected, 4 exists-but-not-connected, 0 launch-required missing, 1 useful future surface missing, and 0 loud-failure gaps.

**Verification receipt:** `python scripts/verify/business_automation_index.py --report output/business-automation-index.json` passed. Frappe's hook registry showed the daily scheduled checkup. The final closeout suite also verified contact intake, payment/webhook readiness, checkout conversion, payment cascade, CRM cascade, paperwork status, outbound documents, and invoice branding.

**Decided by:** GL required fail-loud backend automation inventory; Codex implemented the indexed/scheduled contract.

---

## 2026-05-06 - Stripe hosted checkout must match ERPNext grand total exactly

**Decision:** Stripe Checkout line items must equal the ERPNext Sales Order grand total before the customer is redirected. Tax and charges can be represented as an explicit Stripe adjustment line, but Stripe must not silently omit ERPNext taxes/charges or charge more/less than the order.

**Reasoning:** The subagent money-path audit found a real risk: Stripe Session line items were built from Sales Order item rates, while ERPNext totals can include taxes and charges. That could undercharge hosted checkout while ERPNext records a higher total. Money mismatches must fail before the customer sees checkout.

**Implementation:** Added `stripe_line_items_for_sales_order()` in `locally_twisted.payments.stripe_session`. It adds a `Sales tax and charges` line when ERPNext `grand_total` is higher than the item-line total, stores `amount_expected_cents` metadata, and raises `frappe.ValidationError` if item lines would exceed the ERPNext total.

**Verification receipt:** `python scripts/verify/stripe_amount_parity_contract.py` passed for taxable, nontaxable, and negative-adjustment cases.

**Decided by:** Codex surfaced the parity risk during the backend automation audit and encoded the fail-loud payment contract.

---

## 2026-05-06 - Sales Invoices are AP documents with gray callouts

**Decision:** The default Sales Invoice is an accounts-payable document, not marketing collateral. Secondary invoice information can use the approved gray vertical callout treatment: light neutral gray background, thin gray left rule, and compact spacing. The bottom support message stays a solid black bar with white text:

`Customer Service, Continued Event Support, and Repeat Orders:`

`Reply to this invoice and we will route the request to the right person.`

No dog logo, gold bar, gold rule, navy/berry/promo accent treatment, or marketing-style decoration belongs on ordinary Sales Invoices.

**Reasoning:** Sales Invoices are for bookkeepers and AP teams to enter, route, approve, and pay without friction. The gray callout treatment highlights review information without making the invoice feel like a sales packet. Richer gold/dog-logo brand treatment can still belong in proposals, event packets, reorder follow-ups, and customer-support documents where the audience expects context and relationship-building.

**Implementation:** Updated the code-owned Sales Invoice Print Format source in `locally_twisted.seed.sync_invoice_branding` to use shared `lt-callout` gray left-rule blocks for the AP summary, policy block, and AP note. The `lt-support-banner` remains solid black with the approved service/repeat-order copy. Updated the invoice branding verifier and external document guidance so the standard is guarded by code and docs.

**Verification receipt:** `python scripts/setup/sync_invoice_branding.py` updated the Frappe Print Format. `python scripts/verify/invoice_branding_contract.py` passed against `ACC-SINV-2026-00001`, including default print rendering.

**Decided by:** GL locked the no-gold/no-dog invoice choice; Codex encoded it into the print source, verifier, and durable guidance.

---

## 2026-05-06 - Outbound paperwork must be answer-first, not automation-first

**Decision:** Every outbound document must lead with the recipient's practical answer. The visible first-pass block should identify the fields the audience cares about, such as invoice number, due date, balance, PO/reference, payment status, event date, location, approval path, next step, or reconciliation contact. Internal automation metadata must not take the high-visibility customer-facing slot.

**Reasoning:** GL approved the visual direction but caught that the preview's `Automation contract` section put our internal system concerns ahead of the recipient. That is the wrong posture for corporate-standard paperwork. Good outbound paperwork should make the recipient feel that LT understands their workflow and gave them the answer first.

**Implementation:** The outbound preview renderer now shows `Key fields to review` in the upper facts grid where `Automation contract` used to appear. The source registry now requires every outbound template to include `## Answer First` before automation notes. All current outbound templates were updated with document-specific answer-first guidance. The project capability `external-document-audience-contract` and paperwork lane now carry the standing rule.

**Verification receipt:** `python scripts/verify/outbound_documents_contract.py` passed for all 10 outbound document families. `python scripts/verify/render_outbound_document_previews.py --slug outbound-documents-answer-first-20260506 --no-open` rendered 20 fake-data review previews as HTML, PDF, and PNG. Rendered preview search confirmed no `Automation contract` label remains, and every template has `## Answer First`.

**Decided by:** GL defined the standard; Codex encoded it into source templates, verifier expectations, and project guidance.

---

## 2026-05-06 - Shop category navigation uses a rail and mobile select

**Decision:** `/shop` and `/shop-items/<group>` use the shared `templates/includes/shop_category_nav.html` component for category navigation. Desktop uses a slim left rail beside the product showcase. Mobile uses a native select above the products. `/shop` no longer uses an in-place chip filter wall, and category pages must not restore the top button/tile wall.

**Reasoning:** GL chose option B after rejecting the category buttons as horrible, cheap, and too cognitively heavy. The earlier symmetry pass fixed row math, but it preserved the wrong interaction pattern. These are product-showcase pages; customers need an obvious browse path that leaves the photos room to sell the product.

**Implementation:** Commit `b82eaf9` replaced the duplicated `/shop` chip wall and `/shop-items/<group>` category tile wall with the shared rail/select include, updated `/shop` and category templates, and cache-busted `lt-shop-showroom.css` to `v=20260506-showroom-5`.

**Verification receipt:** `python scripts/verify/smoke_shop.py` passed. Focused checks passed: `npm run test:interactive-layout -- --grep "/shop category navigation"` 4/4, `npm run test:layout-fit -- --grep shop` 26/26, and `npm run test:layout-fit -- --grep "variant-product|single-product|seasonal-category"` 39/39. Browser geometry confirmed desktop rail/mobile select behavior on `/shop` and `/shop-items/get-well-bouquets`, with no `.lt-shop__chip` controls and no old `.lt-shop__toolbar--categories` wall.

**Alternatives considered:** Keep the symmetrical button grid. Rejected because GL had already rejected the button-control treatment as unusable. Replace the whole entry with a photo category gateway. Deferred until category imagery is approved. Keep `/shop` as in-page filtering. Rejected for this pass because the chosen simple/intuitive path is category navigation to real category pages.

**Decided by:** GL chose option B; Codex implemented, verified, committed, and pushed it.

---

## 2026-05-06 - Consent UI assets must avoid blocklist-style filenames

**Decision:** The sitewide preference/consent script is named `lt-site-preferences.js`, not `lt-cookie-consent.js`. Future optional analytics, ads, and preference assets should avoid filenames that look like common blocker targets while still honoring the stored `lt_cookie_consent` choice.

**Reasoning:** GL reported `ERR_BLOCKED_BY_CLIENT` on `/shop`. The server-side asset path was not the real failure; the browser extension blocked a filename containing `cookie-consent`. Keeping that name would make the site look broken for customers using common privacy tooling.

**Implementation:** Commit `dc562e7` renamed the source asset, updated the Frappe hook include, updated the policy workstream note, and deleted the stale `lt-cookie-consent.js` source file.

**Verification receipt:** The local `/shop` page referenced `lt-site-preferences.js`, the new asset returned 200, the old asset returned 404, and browser verification no longer showed `ERR_BLOCKED_BY_CLIENT` for the consent script.

**Alternatives considered:** Keep the old filename and ignore extension noise. Rejected because the user saw it as a visible page problem. Disable the preload only. Rejected because the blocked request was filename-based and would still leave extension-console failures.

**Decided by:** GL reported the symptom; Codex traced and fixed the actual asset contract.

---

## 2026-05-06 - Shop category pages must use showroom symmetry, not ragged Webshop rows

**Decision:** `/shop`, `/shop-items`, and `/shop-items/<group>` are product-showcase pages. They may get longer to give products room, but category controls and product rows must stay symmetrical at each breakpoint. `/shop-items/<group>` category controls use equal tile rows, not variable-width chips, and include `All Ready-to-Order` so the category matrix has 12 tiles. Category tiles must match by width and height within each row. `/shop` filtered grids and category product grids must not leave a single desktop orphan card when an even 2-up split is available.

**Reasoning:** GL rejected the first showroom pass because it was technically responsive but visually cheap. Product pages need to sell the decor with large photos and breathing room; a ragged control row or isolated final card makes the product presentation feel accidental and low quality. This is a design contract, not optional polish.

**Implementation:** Updated `item_group.html` to add the neutral `All Ready-to-Order` category tile and preserve Webshop listing/update hooks. Updated `lt-shop-showroom.css` so category controls render as equal grid tiles: 2-up mobile, 3-up tablet, and 4-up desktop. Added scoped balancing logic for both `/shop` filtered grids and `/shop-items/<group>` category grids, marking even visible product counts for a desktop 2-up layout when a 3-up layout would leave one orphan card. Bumped the shop showroom CSS cache key in `hooks.py`.

**Verification receipt:** `python scripts/verify/smoke_shop.py` now checks category-control width/height symmetry, `/shop` filtered-grid orphan prevention, and category-grid orphan prevention, and passed after the repair. Focused route checks also passed: `npm run test:layout-fit -- --grep shop` 26/26, `npm run test:layout-fit -- --grep "variant-product|single-product|seasonal-category"` 39/39, and `npm run test:interactive-layout -- --grep "/shop filtered grid fits"` 4/4. Fresh browser geometry checks measured mobile Get-Well as six equal 2-tile category rows, desktop Get-Well as a 4x3 category-control grid, and desktop Arches as paired 2-card product rows on both `/shop` filtered view and `/shop-items/arches`; transient screenshot folders were not kept as source.

**Alternatives considered:** Leave category controls as flexible chips. Rejected because the row shape looked cheap and violated GL's standing symmetry rule. Keep desktop product grids always 3-up. Rejected for even 10-item categories because it leaves one orphan card. Force every category to 2-up on desktop. Rejected because 3-up still works for counts that divide cleanly and gives some categories stronger density.

**Decided by:** GL set the standing symmetry rule and rejected the first pass; Codex implemented and verified the revised showroom contract.

---

## 2026-05-06 - Portfolio designer reference remains critique input until GL closes it

**Decision:** The current `/portfolio` production source is the Frappe translation, not the Claude/designer research folder. The research folder remains available while GL sends the code back for designer critique. Do not claim it was deleted, and do not commit it as production source unless GL explicitly changes its status.

**Reasoning:** The reference code is useful because it defines the photo-placement design. It is not useful as a second production implementation. The first Codex translation mixed that reference with older local portfolio assumptions, including filters/modal language and stale cleanup claims. That confused ownership: the designer needs to critique the production translation, while Codex needs to keep the Frappe route, assets, tests, and cache behavior correct.

**Implementation:** Production source is `www/portfolio.html`, `www/portfolio.py`, `public/css/lt-portfolio-reel.css`, `public/js/lt-portfolio-reel.js`, optimized images under `public/images/portfolio/optimized/`, and `scripts/verify/portfolio_reel.spec.js`. The current page uses the strict edge-anchor reel math from the designer reply: left/right photos are allowed to bleed past the viewport, center photos are sparse statement moments, mobile resets to a full-width natural-ratio stream, and captions remain hidden by default so text does not cover the gallery photos. Category query links still filter the photo payload server-side, but there is no visible filter bar or lightbox modal in the current translation.

**Verification receipt:** Latest focused checks passed on the running local Frappe site: `/portfolio` returned `200`; page CSS, JS, and optimized image assets returned `200`; `npm run test:portfolio-reel` passed 4/4, including the edge-anchored side/scale rhythm, hidden-by-default captions, mobile stream, and scroll-driven reveal guard; `npm run test:layout-fit -- --grep portfolio` passed 13/13; and `npm run test:interactive-layout -- --grep portfolio` passed 3/3. Chrome and Brave screenshot evidence was captured under `output/playwright/portfolio-strict-v5/`.

**Decided by:** GL clarified that Claude/designer code should be used for photo placement and design critique; Codex translated and documented the Frappe-owned implementation.

---

## 2026-05-06 - Portfolio proof uses natural-ratio floating photos, not card captions

**Current status:** superseded for the active designer critique loop by the entry above, "Portfolio designer reference remains critique input until GL closes it." The current production translation does **not** include a visible filter bar or lightbox modal, and the reference folder has **not** been deleted.

**Decision:** `/portfolio` should sell trust through installed-work photos first. The V1 portfolio surface uses a floating natural-ratio photo reel with quiet filters and a modal, not cropped product-card tiles or visible captions over the work. Text remains available to screen readers and in the modal, but the main gallery should let the photos carry scale and proof.

**Reasoning:** LT is trying to look like an established event partner, not a small ecommerce catalog. Cropped cards and caption blocks make real installs feel smaller. Full natural-ratio photos better support the event-authority positioning and avoid hiding the balloon work behind UI. The temporary generated/reference folder used to translate the reel is not retained; Git history and the implemented route are the archive.

**Implementation:** Updated `www/portfolio.html` and `www/portfolio.py` with display order metadata, natural image dimensions, left/right/center reel placement, mobile full-width stacking, filter-triggered relayout, and a dedicated `portfolio_reel.spec.js` verifier. Added `disabled: 0` to Item Attribute fixtures so fixture sync/migrate is not blocked by required ERPNext fields.

**Verification receipt:** Verified locally with `python scripts/dev/clear_website_cache.py --restart`, `npm run test:portfolio-reel` (3 passed), `npm run test:layout-fit` (260 passed), `npm run test:interactive-layout` (42 passed), `python -m json.tool apps/locally_twisted/locally_twisted/fixtures/item_attribute.json`, and `bench --site frontend migrate`. The migrate run also deleted the orphaned local `LT Event Playground Design` DocType because no committed DocType file owns it.

**Decided by:** Codex implemented from the approved proof-gallery direction; GL/Jeff still need to review final photo order and image quality before launch.

---

## 2026-05-06 - Customer document policy copy uses anchored lanes and code-owned helpers

**Decision:** Customer-facing receipts, inquiry acknowledgments, and future custom invoice/document copy should not each carry their own independent policy copy. The canonical public policy pages remain `/terms-of-service` and `/refund-policy`, split into anchored lanes for event balloon decor, ready-to-order pickup/delivery, face painting/balloon twisting, and corporate invoicing. Transactional emails and customer documents link to the exact lane that applies. Do not add ERPNext Terms and Conditions or Email Template records unless a verified customer-facing invoice path truly requires them.

**Reasoning:** LT is a mixed event-service and ecommerce business. A generic "policies" link hides important differences between invoiced decor, ready-to-order products, artist-service deposits, and corporate Net 30 invoices. Shared helpers reduce copy drift and keep customer emails from implying that services, service deposits, or delivery are taxable. GL also wants the system to stay as whitelabel/code-owned as possible instead of filling ERPNext setup doctypes that are not needed by the current customer flow.

**Implementation:** Added `locally_twisted.policy_documents` as the shared policy lane helper, updated `/terms-of-service` and `/refund-policy` anchors, added policy blocks to inquiry auto-acknowledgments and paid-order receipts, and updated the checkout notice. An initial ERPNext Terms/Email Template sync path was removed after GL clarified the whitelabel preference; the local DB records/template block created during that pass were cleaned up.

**Verification receipt:** `customer_documents_contract.py` first failed on missing helper/anchors/email links, then passed. `payment_cascade_contract.py` first failed on missing receipt policy links/text, then passed. Supporting checks passed: py_compile, commerce rules, checkout fulfillment, payment webhook, cart checkout, route checks, `git diff --check`, and `npm run test:layout-fit` with 273/273 passing.

**Alternatives considered:** Create separate standalone legal pages per lane. Rejected because a single canonical Terms/Refund pair with anchors is easier to maintain and link precisely. Put full legal text in every receipt email. Rejected for ecommerce receipts; they get concise plain-language summaries plus exact links. Sync ERPNext Terms and Conditions records. Rejected after GL clarified that unnecessary ERPNext additions work against the whitelabel goal.

**Decided by:** GL approved the lane structure; Codex implemented and verified the first customer-document policy slice.

---

## 2026-05-06 - Event Playground starts as a hidden internal PlayCanvas preview

**Decision:** The first playable decor-planning route is hidden at `/event-playground`, branded as `Event Playground` for review. PlayCanvas/Vite owns the local game preview, while Frappe owns only the hidden route shell, iframe boundary, and contact-form handoff. It is not in public navigation and does not add saved design records, backend save APIs, automatic Lead creation, pricing, checkout, or a production PlayCanvas bundle.

**Reasoning:** The prior engine comparison and classic PlayCanvas prototype established PlayCanvas as the better default for a game-like event-space planner. GL's accepted direction is closer to Animal Crossing: Happy Home Paradise for event decor than CAD or a product configurator, but LT still needs honest balloon construction and plain customer expectations. An iframe-mounted local preview keeps Frappe/Webshop CSS from corrupting the canvas surface while avoiding premature persistence, Desk UX, privacy, and production-deploy decisions.

**Implementation:** Added a PlayCanvas/Vite Event Playground entry under `research/design-studio-v2/event-builder-spike/`, added the Frappe route shell at `www/event_playground.html` and `www/event_playground.py`, registered `/event-playground` in `hooks.py`, and added route-shell CSS. The game runs from the local Vite preview at `127.0.0.1:4306`. Submit Inquiry sends a `postMessage` to the Frappe wrapper; the wrapper stores `lt_event_playground_handoff_v1` in `sessionStorage` and redirects to `/contact?intent=quote&source=event-playground`, where the existing contact form is prefilled with customer details and a design summary. V1 includes school gym, corporate lobby, backyard patio, community room, and car dealership-lite levels; classic arch, column pair, balloon wall/photo moment, table centerpiece, and welcome sign balloon pieces; and context props including tables, chairs, easel/sign, scale person, and display car. Organic/twisting complexity is deferred until the renderer can model it honestly.

**Verification receipt:** The feature added pure state tests, a nested Vite build/verifier, and the root `/event-playground` Playwright route spec. The root spec starts the local Vite preview, verifies the iframe canvas is nonblank at mobile and desktop widths, exercises the core controls, and verifies Submit Inquiry lands on `/contact` with the design summary prefilled. No migration is required because this slice adds no DocType.

**Alternatives considered:** Keep the work research-only until another review. Rejected because the accepted implementation plan called for a polished playable prototype mounted into Frappe for internal review. Add save/share, Lead submission, or a DocType immediately. Rejected because those production behaviors need privacy, Desk review, and business-process decisions first. Build the planner directly inside Frappe page CSS/JS. Rejected for V1 because the game needs a protected canvas/runtime surface. Include organic garland or twisting-balloon physics as approximations. Rejected because this route should not fake physically meaningful balloon behavior.

**Decided by:** User approved the internal-preview implementation plan; Codex implemented the first hidden PlayCanvas/Frappe slice and verifier.

---

## 2026-05-06 - Policy copy follows GL business-proxy answers until legal review

**Decision:** Delivery policy stays inside Terms/FAQ rather than a standalone route. Pickup/delivery windows are requested until LT confirms them. If LT cannot complete delivery/setup because the customer cannot be contacted or access information is wrong, the customer remains responsible. Delivered product damage must be reported the same day. Ready-to-order products have no returns once prepared, delivered, or picked up. Out-of-area delivery is available for quote. Privacy contact remains `hi@locallytwisted.com`. Launch expects analytics/ads/tracking plus cart/session storage. Inspiration photos are used for event planning. Event photos use an opt-out release model for photos/video taken by LT staff/representatives and public social/review photos LT can access. Invoice payment counts as acceptance of booking terms for now. Personal balloon decor cancellations less than 7 days before the event receive no cash refund; any funds paid transfer to another event date or product.

**Reasoning:** GL offered to act as the business proxy for policy questions except proof-of-insurance. These decisions unblock the current public copy while preserving the separate need for attorney/accountant review before final legal/live readiness claims.

**Implementation:** Updated FAQ, BTFP service copy, Terms, Privacy, Refund Policy, and `_resources/policies/` source docs so service pages show service totals instead of a service-tax line, so delivery/returns/photo/cookie/children language reflects the proxy decisions, and so the refund gap between 72 hours and 7 days is closed. Added a sitewide cookie/tracking notice that stores `lt_cookie_consent` and exposes `window.LT_COOKIE_CONSENT` for future analytics/ads wiring.

**Alternatives considered:** Create a standalone Shipping/Delivery Policy route. Rejected because GL chose Terms/FAQ. Require opt-in photo releases. Rejected because GL chose an opt-out release for LT-taken event photos and public social/review photos LT can access. Leave the decor cancellation gap for legal review only. Rejected because GL supplied the business decision.

**Decided by:** GL as business proxy; legal/accounting approval still separate where needed.

---

## 2026-05-06 - Delivery zone, not product group, owns checkout quote fallback

**Decision:** A priced product that is in the cart should not become quote-only because of its Item Group. Product group is no longer the source of `quote_required` cart behavior. The system-configured customer-facing quote fallback for checkout is fulfillment, especially a delivery ZIP outside the configured delivery zones. Out-of-area delivery redirects the customer to `/contact` with checkout details and the interested item carried forward.

**Reasoning:** GL challenged the earlier assumption directly: if a customer can put something in the cart, they reasonably expect it can be purchased. The only clear system-configurable reason for standard checkout to stop is that delivery is outside the configured service zone. Custom event/service work can still start through `/contact`, but that is a CTA and intake choice, not a stale cart failure for priced products.

**Implementation:** `commerce_rules.checkout_lane_for_item_group` now returns `retail_checkout` for product groups. `api/cart.py` no longer returns `missing: quote_required` for priced products. `/checkout` stores an out-of-area delivery handoff in `sessionStorage` and redirects to `/contact?intent=quote&source=checkout-delivery`; the contact form preloads name, phone, email, date, time window, delivery address, Delivery service, delivery notes, cart item lines as `Interested item`, and checkout notes. Lead creation belongs to `/contact` submit; checkout's out-of-area fallback avoids Sales Order, Payment Request, Stripe session, and duplicate Lead creation.

**Verification receipt:** The revised contracts first failed on the stale assumption, then passed after implementation: `commerce_rules_contract.py`, `cart_checkout_contract.py`, `contact_prefill.py --base-url http://localhost:8081`, and `npm run test:checkout-experience`.

**Alternatives considered:** Keep product-group quote gates and show a modal for quote-only cart items. Rejected because it reinforced the wrong customer assumption. Remove all quote handling from checkout. Rejected because out-of-area delivery still needs a manual quote path and must not send customers to Stripe.

**Decided by:** GL clarified the customer/business rule; Codex implemented and verified the checkout/contact handoff.

---

## 2026-05-06 - Checkout tax rate and taxable base are separate contracts

**Decision:** Checkout chooses the Utah tax rate from fulfillment ZIP/city, but applies that rate only to taxable goods. Services are not taxable. Face painting, balloon twisting, deposits for those services, and delivery charges are non-taxable. Out-of-area delivery stays quote-required instead of using a local delivery fee.

**Reasoning:** GL clarified that the business rule is not "tax everything in the order." The location still matters because Utah sales tax rates vary by jurisdiction, but the taxable base must exclude service, service-deposit, and delivery lines. ERPNext's normal Sales Order tax calculation can tax the whole net total unless non-taxable lines carry a real Item Tax Template override, so the checkout contract must verify both preview totals and the submitted Sales Order rows.

**Implementation:** `commerce_rules.py` now separates fulfillment zoning/rate lookup from `is_taxable_item`. `sync_commerce_rules` creates a 0 percent `LT Non-Taxable Sales` Item Tax Template and keeps delivery fee Items/Prices synced. `/checkout` assigns item tax templates to non-taxable lines, excludes delivery from tax, rejects past fulfillment dates, caps line quantity, and treats out-of-area ZIPs as quote-required. `/contact`/`/book` Lead handling stores payment/deposit guidance without creating service/deposit money records.

**Verification receipt:** A pre-fix checkout fulfillment contract caught West Jordan delivery taxing goods plus delivery: expected `$4.84`, found `$5.96`. After the fix, `preview_checkout_totals` for `mothers-day-bouquet` delivered to ZIP `84088` returned `$65.00` goods, `$15.00` delivery, `$4.84` tax, and `$84.84` total. The focused contracts passed for commerce rules, checkout fulfillment, cart checkout, checkout Lead conversion, Lead backend intake parity, checkout experience, payment cascade, and payment launch readiness in local/test mode.

**Alternatives considered:** Tax the whole order after selecting a ZIP rate. Rejected because service, service deposit, and delivery lines are not taxable under the clarified LT rule. Handle service deposits as checkout products immediately. Rejected for this slice because services remain inquiry/Lead-guided until the approved money flow is deliberately mapped.

**Decided by:** GL clarified the taxable/non-taxable business rule; Codex implemented and verified the ERPNext checkout contract.

---

## 2026-05-05 - Responsive container integrity is a launch gate

**Decision:** Public-site visual work must pass breakpoint-edge and stateful-container checks before it is called complete. This includes text, images, buttons, nav, drawers, mega panels, cards, forms, product controls, modals, carousels, cart, checkout, policy pages, and Webshop route wrappers. The approved gate is `npm run test:layout-fit`, `npm run test:interactive-layout`, and, for broad public-site changes, `npm run test:public-verify`.

**Reasoning:** GL's complaint was not only that one menu looked bad. The failure mode was systemic: content pushed against or outside containers, mid-breakpoints were untested, product pages could keep old behavior, and stateful UI could look fine while closed but fail once opened. This is a design requirement and accessibility risk, not a cosmetic preference.

**Implementation:** Added `scripts/verify/layout_helpers.js` as the shared route/viewport/layout audit helper. Expanded `scripts/verify/layout_fit.spec.js` to 20 public routes across 13 viewport families for 260 passive checks. Added `scripts/verify/interactive_layout.spec.js` with checks for desktop/mobile nav breakpoints, desktop mega panels, mobile drawer accordions, shop/product controls, contact conditionals, portfolio state, and reduced-motion homepage behavior. Added package scripts `test:interactive-layout`, `test:checkout-experience`, `test:shop-smoke`, and `test:public-verify`. 2026-05-06 correction: `smoke_shop.py` now verifies that fixed-price products do not invent product-level quote gates while retail variants still prove inline option selection and cart writes; the portfolio interaction check now covers the current proof-reel front-photo state instead of the superseded modal state.

**Verification receipt:** `node --check` passed for the new/rewritten Playwright specs, `python -B -m py_compile scripts\verify\smoke_shop.py` passed, `python scripts/verify/commerce_rules_contract.py` passed, `python scripts/verify/smoke_shop.py` passed, `npm run test:interactive-layout` passed 39/39, `npm run test:layout-fit` passed 260/260, `npm run test:checkout-experience` passed 1/1, and `npm run test:public-verify` passed with quieter Playwright output.

**Decided by:** GL made breakpoint/container integrity a hard design requirement; Codex implemented the standing verification gate.

---

## 2026-05-05 - Premium two-level mega menu is active and must be verified as served

**Decision:** The public header uses the deliberate two-level premium mega-menu architecture: full-height Locally Twisted logo image treatment, desktop event/product mega panels, accessible mobile drawer accordions, top proof row, and `/contact` as the quote path. The menu assets are live only when `hooks.py` serves `lt-mega-menu.css`, `lt-page-containment.css`, `lt-product-polish.css`, and `lt-megamenu.js`.

**Reasoning:** GL explicitly rejected the too-small/simple nav and preferred restoring/building the mega menu deliberately. The broken state was not only taste; the restored menu source existed but was not loaded, desktop click behavior closed hover-open panels, product pages still read like old Webshop, and several mobile components were cramped or clipped.

**Implementation:** Restored the mega-menu context and template, loaded the new CSS/JS assets through `web_include_css`/`web_include_js`, made clicked desktop mega menus pin open until outside click/Escape/another menu, kept `/contact` as quote conversion, added page containment and product/shop polish layers, fixed mobile hero/reviews/portfolio/newsletter containment, and expanded the layout-fit route list to include `/checkout` and `/thank-you`.

**Verification receipt:** Served asset checks found the new CSS/JS in the homepage HTML and returned HTTP 200 for each asset. `python scripts/verify/nav_ia.py`, `python scripts/verify/smoke_shop.py`, and `npm run test:layout-fit` passed; the later same-day responsive gate expanded layout-fit to 260 route/viewport checks. A Playwright post-fix screenshot/interaction pass covered 13 routes across 320, 375, and 1366 widths, plus open desktop event/product mega menus and the mobile drawer, with no reported failures. Screenshots and `post-fix-report.json` are under `output/playwright/full-site-fix-20260505-post/`.

**Decided by:** GL explicitly chose the deliberate mega-menu restore; Codex implemented and verified the rendered Frappe site.

---

## 2026-05-05 - Deleted old design guide; expanded icon suite must be balloon-local-event specific

**Decision:** `_resources/design-guide/` is deleted and must not be recreated as a current design reference. `_resources/STYLE-GUIDE.md` version 4.2 is the sole current visual contract. The professional SVG icon system now needs Utah/local proof, event-context proof, and multiple balloon-specific options, not only four generic proof marks.

**Reasoning:** GL rejected the first icon direction as too generic and explicitly called out that Locally Twisted is a balloon company. The old light-blue/blush design synthesis also kept conflicting with the approved Civic Celebration + Slate Blue/Berry + Brand Direction rebrand. Keeping it in active reading paths made future design agents likely to repeat the wrong font, spacing, color, and icon choices.

**Implementation:** Removed the tracked `_resources/design-guide/` tree and deleted stale shop/design comparison references that pointed at the retired look (`_resources/shop-recon-2026-04-29.md`, `_resources/webshop-state-vs-spec-2026-04-30.md`, its capture scripts, and its generated screenshot folder). Removed the old `_resources/icon-comparison-2026-04-27/` generic icon comparison because it conflicts with the new custom brass-line direction. Updated active agent/planning/workstream references to point to `_resources/STYLE-GUIDE.md` only. Replaced legacy active CSS font references with Cormorant Garamond + Lato, retired old pastel token names in active app code, and expanded `apps/locally_twisted/locally_twisted/public/icons/brand/` with a broader brass-line SVG suite: Utah rooted, design driven, professional, trusted partner, event stage, delivery/install, civic parade, corporate entrance, school spirit, premium private event, balloon pair, balloon cluster, balloon arch, organic garland, balloon column, and balloon bouquet.

**Verification receipt:** Active app source search found no remaining `DM Serif`, `Raleway`, `Montserrat`, `Playfair`, `lt-blush`, `lt-soft-blue`, `soft blue`, `light blue`, `--lt-primary`, or UI `blush` references after the cleanup. The current non-Odoo `_resources` search only finds explicit "deleted/do not use" notes in `_resources/STYLE-GUIDE.md`. SVG XML parse validation passed for all 16 brand icons. Python compile passed for `apps/locally_twisted/locally_twisted`, and LT CSS token usage had no missing `--lt-*` variables.

**Decided by:** GL required deletion of conflicting style guides/references and rejected the first generic icon pass in favor of a higher-quality Utah/local/events/balloon-specific icon suite.

---

## 2026-05-05 - Page-level style guide and professional proof icons are required before the rebrand swarm

**Decision:** `_resources/STYLE-GUIDE.md` version 4.1 now maps the approved Civic Celebration + Slate Blue/Berry + Brand Direction synthesis to every existing public page family and reusable element. The Image #3 proof-icon direction is no longer only a reference image; the repo now includes a first reusable brass-line SVG set under `apps/locally_twisted/locally_twisted/public/icons/brand/`.

**Reasoning:** GL clarified that the site needs an actual style guide for all existing pages and elements, including the professional icon quality from the Brand Direction banner. Without a route/component matrix, agents can pass layout checks while still making unrelated font, spacing, icon, photo, and page-treatment choices.

**Implementation:** Added the existing route/template coverage table, reusable element map, professional icon system, core icon asset manifest, drawing rules, and future trust-icon slots to `_resources/STYLE-GUIDE.md`. Added original SVG assets for `utah-rooted`, `design-driven`, `professional`, and `trusted-partner`.

**Verification receipt:** Documentation and asset-source change only. No route behavior, CSS, templates, or running ERPNext state were changed in this slice.

**Decided by:** GL requested a combined style guide across all pages and explicitly called out the need for the professional Image #3 icon treatment.

---

## 2026-05-05 - Style guide locks to Civic Celebration plus Brand Direction quality

**Decision:** `_resources/STYLE-GUIDE.md` is now the implementation-grade visual contract for the next rebrand pass. The approved target is Civic Celebration for Americana/Utah authority imagery, Slate Blue and Berry for restrained corporate palette discipline, and the Locally Twisted Brand Direction banner for premium typography, spacing, and crisp brass icon quality.

**Reasoning:** GL clarified that the current site is missing the concept, not only individual CSS details. Before sending multiple agents to fix pages, the guide needs to explain the actual target: civic-scale authority, premium corporate finish, real installation proof, Cormorant Garamond and Lato typography, brass line icons, and edited photos that feel crisp and trustworthy rather than generic or small-party-catalog.

**Implementation:** Updated `_resources/STYLE-GUIDE.md` to version 4.0 with a new approved visual target section, stronger rules for typography, color, buttons, navigation, trust icons, hero treatment, and a detailed photography/editing treatment. The guide explicitly de-emphasizes pastel/teal drift, generic webapp fonts, circular badge clutter, and photo crops that hide scale.

**Verification receipt:** Documentation-only change. No site route behavior or running ERPNext state was changed.

**Decided by:** GL supplied the board direction and requested the style-guide correction before the rebrand swarm.

---

## 2026-05-03 - Event-builder engine spike defaults to PlayCanvas

**Decision:** For the next research step of the Design Studio V2 event builder, use PlayCanvas as the default renderer if GL approves moving from the isolated spike to a hidden Frappe-route spike.

**Reasoning:** The spike compared PlayCanvas and Babylon.js against the same corporate-stage scene, payload facts, fixed isometric camera requirement, 1 ft scale grid, draggable pieces, and desktop/mobile verification. Both engines passed. The pre-agreed rule says that when both pass, choose PlayCanvas because the long-term product is closer to a mini event-space game than a static renderer.

**Implementation:** Added the research-only nested package at `research/design-studio-v2/event-builder-spike/`, with `playcanvas.html`, `babylon.html`, shared scene/payload code, engine-specific renderers, and `verify_spike.cjs`. The package is explicitly not a production Frappe route and does not touch `apps/`, Leads, checkout, save/share, or ERPNext data.

**Verification receipt:** `npm run build` and `npm run verify` passed from the spike folder. The verifier checked both engines at desktop and mobile widths, no console/page errors, nonblank canvas output, fixed-camera runtime state, 1 ft grid facts, payload parity, arch math of 200 balloons / 50 clusters, organic garland math of 97 balloons with size layers, drag-updated placement, and mobile overflow. Screenshots were captured under `output/playwright/design-studio-v2-event-builder-spike/`.

**Decided by:** Codex implemented the previous agent's approved spike plan and applied the engine decision rule supplied in that plan.

---

## 2026-05-03 - Civic Celebration overhaul becomes the site-wide V1 visual direction

**Decision:** The V1 public site should use the Civic Celebration palette and Utah territory posture across customer-facing routes, with Brand Direction typography polish, brass line icons, a stronger `LOCALLY TWISTED` header wordmark, and company/team-centered copy.

**Reasoning:** GL approved the synthesis of Civic Celebration as the foundation and Locally Twisted Brand Direction as the quality layer. The old pastel/small-catalog direction did not fit the priority buyers: corporate, school, civic, venue, public-event, and premium private-event customers. The company also needs to be saleable later, so the site should not make Jeff the irreplaceable brand character.

**Implementation:** Updated the shared theme CSS, header, home hero, contact/book form styling, BTFP, portfolio, FAQ, policy/accessibility/thank-you/payment surfaces, shop, category pages, product detail, cart, and checkout. Added the generated city/Wasatch hero asset at `apps/locally_twisted/locally_twisted/public/images/home/hero-wasatch-city-20260503.png`. Replaced the external contact map iframe with a controlled service-area panel so the contact page does not depend on a blank third-party embed.

**Verification receipt:** `python scripts/dev/clear_website_cache.py --restart`, route status checks for the main customer routes, `python scripts/verify/nav_ia.py`, `npm run test:layout-fit`, `python scripts/verify/smoke_shop.py`, `python scripts/verify/cart_checkout_contract.py`, `python scripts/verify/catalog_variant_contract.py`, `python scripts/verify/variant_media_contract.py`, `python scripts/verify/contact_prefill.py --base-url http://localhost:8081`, `python scripts/verify/contact_service_logic.py --base-url http://localhost:8081`, and `python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --shape-only --skip-newsletter` passed. Desktop/mobile screenshots were captured to `output/playwright/civic-overhaul-20260503-verified/`.

**Decided by:** GL approved the Civic + Brand Direction synthesis; Codex implemented the site-wide pass and verified the rendered site.

---

## 2026-05-03 - Checkout conversion moves matched Leads to Approved, not New Inquiry

**Decision:** When guest checkout reuses a Contact that is linked to an existing Lead, checkout should continue converting native `Lead.status` and setting `Lead.customer`, and it should also move `Lead.custom_pipeline_stage` to `Approved`.

**Reasoning:** Checkout already creates the operational money path: Customer, Sales Order, and Payment Request. Leaving the LT board at `New Inquiry` after that made Jeff's board contradict the ERPNext checkout records and kept the old "reply to new inquiry" Task open. `Approved` is the safest current business-stage match for "customer has moved from inquiry into an order/payment path"; it keeps the stage cascade operational only and does not create additional finance records.

**Implementation:** Added `apps/locally_twisted/locally_twisted/verify/checkout_lead_conversion_contract.py` and `scripts/verify/checkout_lead_conversion_contract.py`. The verifier first failed with the Lead still in `New Inquiry`; `apps/locally_twisted/locally_twisted/www/checkout.py` now sets the shared CRM pipeline field to `Approved` during the existing Lead conversion save, letting `stage_cascade` close the New Inquiry task and open the Approved task.

**Verification receipt:** `python scripts/verify/checkout_lead_conversion_contract.py` failed before the code change on the stale `New Inquiry` stage/task state, then passed after the code change with rollback evidence for the generated Lead, Contact, Customer, Sales Order, and Payment Request.

**Decided by:** GL agreed the next workflow step was checkout/Lead conversion parity; Codex implemented the smallest verified alignment.

---

## 2026-05-03 - Approved visual synthesis combines Civic Celebration structure with Brand Direction polish

**Decision:** The public website's brand foundation should use the Civic Celebration direction for structure and buyer posture, then apply the higher-quality Locally Twisted Brand Direction typography, brass/gold line-icon treatment, and premium hierarchy. Civic's circular trust badges are not approved as-is; use premium brass line icons instead.

**Reasoning:** GL rejected the first token-only pass because it still showed too much of the old pale/pastel site behavior. The approved target is Utah civic/event authority with city/mountain/territory confidence, but with the more professional font, icon, and brass detail quality from the Brand Direction board.

**Implementation:** `_resources/STYLE-GUIDE.md`, `workstreams/brand-audience-style-reset.md`, the shared theme CSS, and the homepage hero/proof bar were updated toward the approved synthesis. The work keeps Zurchers-style clarity contained to ready-to-order shopping flows, not the company identity.

**Verification receipt:** `python scripts/dev/clear_website_cache.py --restart`, `python scripts/verify/nav_ia.py`, `npm run test:layout-fit`, `python -B -m py_compile apps\locally_twisted\locally_twisted\www\home.py`, and `python scripts/verify/playwright_screenshot.py --base-url http://localhost:8081 --paths /,/shop,/contact,/shop-items/arches/classic-arch --output-dir output/playwright/brand-synthesis-20260503` passed. Screenshot artifacts are in `output/playwright/brand-synthesis-20260503/`. The first local screenshot revealed the authority SVGs rendering too large because the Python homepage controller had not reloaded; fixed with explicit SVG dimensions and a backend restart.

**Decided by:** GL approved the corrected synthesis; Codex implemented the first foundation slice.

---

## 2026-05-03 - Finance operating system starts with inventory, review queues, and accountant approval gates

**Decision:** Build LT's ERPNext finance layer as the business finance operating system, but keep automation controlled. ERPNext can surface unpaid invoices, overdue invoices, expected payments, paid-order review, bank reconciliation, QuickBooks cutover checklists, and payroll feasibility. It must not silently submit accounting documents, send reminders, import bank data, or run payroll/tax filing without GL/accountant approval of the exact rules.

**Reasoning:** The existing checkout/payment-success/webhook path already creates real finance records, so adding more money automation from CRM stages can duplicate Customers, Sales Orders, Payment Requests, Sales Invoices, or emails if it is not coordinated. QuickBooks is the historical archive until the accountant approves the migration depth. HRMS payroll remains the preferred ERPNext direction, but the local stack currently has `Employee` only; payroll DocTypes are not installed.

**Implementation:** Added `workstreams/finance-payroll-quickbooks-migration.md`, `scripts/verify/finance_inventory.py`, `scripts/verify/finance_inventory_contract.py`, `apps/locally_twisted/locally_twisted/seed/sync_finance_workspace.py`, `scripts/setup/sync_finance_workspace.py`, and `scripts/verify/finance_workspace_parity.py`. The live `LT Accountant Home` workspace now has finance cards for unpaid invoices, overdue invoices, expected payments, and recent paid orders, plus shortcuts for invoices, payment requests, payments, banking/reconciliation, suppliers, purchase invoices, employees, payment terms, statements, and chart of accounts.

**Verification receipt:** `python scripts/verify/finance_inventory_contract.py`, `python -B -m py_compile scripts/verify/finance_inventory.py scripts/verify/finance_inventory_contract.py scripts/verify/finance_workspace_parity.py scripts/setup/sync_finance_workspace.py apps/locally_twisted/locally_twisted/seed/sync_finance_workspace.py`, `python scripts/setup/sync_finance_workspace.py`, `python scripts/verify/finance_workspace_parity.py`, and `python scripts/verify/finance_inventory.py` passed against the local ERPNext stack. The first pre-sync finance workspace parity run failed on the missing cards/shortcuts, then passed after the sync.

**Decided by:** Codex implementing the finance/payroll/QuickBooks migration plan supplied by the previous agent, with existing LT finance safety decisions preserved.

---

## 2026-05-02 - Stage-to-finance automation must coordinate with existing checkout/payment cascades

**Decision:** Do not wire manual CRM stage movement directly to Quotes, Sales Orders, Sales Invoices, Payment Requests, Customers, or payment/accounting state until the existing checkout/payment-success cascade is explicitly mapped and protected from duplication.

**Reasoning:** The backend inventory confirmed that LT already has a finance path outside manual CRM stage movement: `/checkout` creates/reuses Customer/Contact records, creates a Sales Order and Payment Request, and sends the customer to Stripe; `/payment-success` and the Stripe webhook reconcile paid orders by marking the Payment Request paid, creating a Sales Invoice, and sending paid-order emails. Adding stage-to-finance automation without coordinating with that path could create duplicate records or contradictory Lead state.

**Implementation:** Added `scripts/verify/backend_schema_inventory.py` and its contract test. The backend simplification workstream now records the current trigger map and flags checkout/Lead conversion parity as the next slice before manual stage-to-finance automation.

**Verification receipt:** `python scripts/verify/backend_schema_inventory_contract.py`, `python -B -m py_compile scripts/verify/backend_schema_inventory.py scripts/verify/backend_schema_inventory_contract.py`, and `python scripts/verify/backend_schema_inventory.py` passed against the live local ERPNext stack.

**Decided by:** Codex made this as a safety boundary after GL approved continuing backend wiring and asked for the next work to be committed and pushed.

---

## 2026-05-02 - Brand palette moves from pastel catalog energy to professional event authority

**Decision:** Locally Twisted's main website chrome should move away from the pastel-heavy teal/blush/lemon/seafoam/cyan direction as the company-level color system. The working launch direction is a more neutral professional base with deep teal, slate, warm white, brass/gold, muted berry, and restrained supporting tints. Balloon color should come primarily from real photography, product imagery, and customer-selected palettes.

**Reasoning:** GL clarified that the target buyer priority is corporate, school, civic, venue, large-scale, and premium private event work, not only small catalog purchases. Jeff's Zurchers reference is useful for retail clarity in `Ready to Order`, but the company brand should not look like a sterile party-supply catalog. The site needs consultative event authority with enough warmth to show experience, trust, and Utah-specific scale.

**Implementation:** `workstreams/brand-audience-style-reset.md` now records the Zurchers comparison, the accepted visual synthesis, and the segmented behavior for homepage/custom decor/shop/BTFP lanes. `apps/locally_twisted/locally_twisted/public/css/lt-theme.css` keeps existing variable names for compatibility but remaps the token values toward the accepted direction.

**Verification receipt:** `python scripts/dev/clear_website_cache.py`, `python scripts/verify/nav_ia.py`, `npm run test:layout-fit`, and `python scripts/verify/playwright_screenshot.py --base-url http://localhost:8081 --paths /,/shop,/contact,/shop-items/arches/classic-arch --output-dir output/playwright/brand-token-20260502` passed. Screenshot artifacts are in `output/playwright/brand-token-20260502/`.

**Decided by:** GL approved moving away from the old pastel direction and accepted the professional Utah event authority synthesis; Codex made the first token-level implementation pass.

---

## 2026-05-02 - CRM stage cascades start with operational Tasks only

**Decision:** The first LT CRM stage cascade should create and close ERPNext `Task` records for operator follow-up. It should not create or modify Quotes, Sales Orders, Sales Invoices, Payment Requests, Customers, or win/loss reporting state.

**Reasoning:** GL wants stage movement to cascade into the rest of the business system, but the exact financial threshold still needs deliberate mapping. Tasks are safe operational wiring: they help Jeff and staff know what to do next without silently creating revenue, accounting, or conversion stats. This keeps the CRM useful immediately while protecting finance/reporting from wrong assumptions.

**Implementation:** `locally_twisted.stage_cascade` now runs from Lead insert/update. It creates one idempotent Task for the active non-Archive stage, closes prior stage cascade Tasks as the Lead advances, and closes open cascade Tasks when the Lead moves to `Archive`. Task records link back to the Lead through code-owned Task Custom Fields synced by `locally_twisted.seed.sync_stage_cascade`.

**Verification receipt:** `python scripts/setup/sync_crm_pipeline.py`, `python scripts/dev/clear_website_cache.py --restart`, `python scripts/verify/crm_stage_cascade.py`, `python scripts/verify/crm_pipeline_parity.py`, `python scripts/verify/backend_workspace_parity.py`, `python scripts/verify/lead_backend_intake_parity.py`, `python scripts/verify/contact_service_logic.py --base-url http://localhost:8081`, `python scripts/verify/contact_prefill.py --base-url http://localhost:8081`, `python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --shape-only --skip-newsletter`, and `npm run test:desk-owner` passed. The cascade verifier also confirmed test records were cleaned up and Sales Order, Sales Invoice, and Payment Request counts did not change during stage movement.

**Decided by:** GL asked to continue with wiring after accepting the finance-safe pipeline separation; Codex implemented the first safe operational cascade.

---

## 2026-05-02 - V1 launch prioritizes the public website while preserving the 10-year saleability path

**Decision:** V1 launch work should prioritize a high-quality public website, customer trust, inquiry/checkout readiness, policy visibility, SEO/local/AEO foundations, and visual quality. The longer ERPNext goal is to support a saleable, less founder-dependent company over the next 10 years, but that full operating-system maturity must not delay the website unless it directly protects launch trust, payments, policies, inquiry handling, or handoff safety.

**Reasoning:** LT currently carries several valid goals at once: ecommerce, custom event decor, balloon twisting/face painting, reviews/proof, backend operations, future saleability, and ERPNext adoption. Trying to mature all of ERPNext before launch creates too much scope and slows the immediate need: a credible website geared toward the right demographics with strong measurable quality.

**Implementation:** Added `workstreams/launch-v1-success-contract.md` and linked it from the website launch workstream and project index. The contract defines buyer priority, commercial lanes, quality targets, launch blockers, deferred post-launch work, and the immediate redesign sequence.

**Alternatives considered:** Keep working from broad queue items only. Rejected because broad items allow future agents to drift into the entire 10-year system before the public website is ready. Freeze backend work entirely. Rejected because inquiry, checkout, payment, policy, and handoff safety still need enough backend support for launch.

**Decided by:** GL approved the website-first / future-safe framing; Codex documented it as the launch scope contract.

---

## 2026-05-02 - LT CRM stages use a custom business field, not Lead.status

**Decision:** Translate the approved six-stage Odoo CRM concept into ERPNext as `Lead.custom_pipeline_stage` with these values: `New Inquiry`, `Quote Sent/Awaiting Approval`, `Approved`, `In Production`, `Event/Post Event`, and `Archive`. Keep ERPNext's native `Lead.status` intact.

**Reasoning:** GL clarified that Odoo's `Archive` was meant to remove a lead from the active Kanban, not necessarily to mark revenue, win rate, or accounting state. Repurposing ERPNext `Lead.status` would risk fighting ERPNext's own conversion/reporting behavior. A custom business-stage field gives Jeff the simple board he needs while leaving finance/reporting triggers to be wired deliberately at the correct business threshold later.

**Implementation:** `locally_twisted.seed.sync_crm_pipeline` now creates/updates `custom_pipeline_stage`, normalizes existing Leads, and points `LT Inquiry Board` at that field. The `Archive` column is archived/off-board. Website inquiries still use native `status = Open` and now also set `custom_pipeline_stage = New Inquiry`. Owner Home inquiry counts use the custom field.

**Verification receipt:** `python scripts/setup/sync_crm_pipeline.py`, `python scripts/verify/crm_pipeline_parity.py`, `python scripts/setup/sync_backend_workspaces.py`, `python scripts/verify/backend_workspace_parity.py`, `python scripts/verify/lead_backend_intake_parity.py`, `python scripts/verify/contact_service_logic.py --base-url http://localhost:8081`, `python scripts/verify/contact_prefill.py --base-url http://localhost:8081`, `python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --shape-only --skip-newsletter`, and `npm run test:desk-owner` passed.

**Decided by:** GL accepted the integration approach after clarifying the purpose of Archive; Codex implemented the safe custom-field pipeline.

---

## 2026-05-02 - Irregular contractors do not get backend accounts by default

**Decision:** Locally Twisted contractors who help irregularly should not have an ERPNext Desk/backend login by default. They should receive job information through text, email, and calendar invites unless a future workflow proves they need direct system access.

**Reasoning:** Contractors are not a daily operating tier like Owner, Manager, Employee, or Accountant. A backend profile for them adds account-management burden and exposes confusing ERPNext surfaces without a clear benefit. The simpler and safer workflow is to automate or manually send only the information they need for a job.

**Implementation:** The temporary contractor login `lt-contractor-temp@example.com` was disabled in the local ERPNext database. `scripts/verify/backend_workspace_parity.py` now fails if that temp user exists and is enabled, has a role/module profile, or has `Desk User` access.

**Decided by:** GL clarified the contractor workflow during ERPNext backend simplification; Codex disabled the temp login and added the parity guard.

---

## 2026-05-02 - Lead estimated times use plain text, not Frappe Time controls

**Decision:** Customer-facing inquiry time fields should ask for start/end estimates in friendly text, while ERPNext Lead Desk fields should use plain internal labels and `Data` fieldtype text inputs. Do not put customer helper copy such as "(even an estimate is helpful!)" into backend employee labels.

**Reasoning:** Frappe renders `Time` Custom Fields in Desk with an awkward time control/slider. That is too much friction for Jeff and staff when the value is only an estimate. Existing Time fields also held machine-style values with seconds/microseconds, which looked authoritative but were not customer intent.

**Implementation:** `locally_twisted.seed.sync_contact_intake_backend` now converts the relevant Lead time Custom Fields from `Time` to `Data` through a guarded safe conversion, updates labels/descriptions, normalizes old machine-style Lead values to blank or readable text, and clears Lead cache. The public `/contact` form now has `Event Start Time` and `Event End Time` text fields with the customer helper copy.

**Verification receipt:** `python scripts/setup/sync_contact_intake_backend.py`, `python scripts/verify/lead_backend_intake_parity.py`, a Playwright browser check against `/app/lead/CRM-LEAD-2026-00013`, `python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --shape-only --skip-newsletter`, `python scripts/verify/contact_service_logic.py --base-url http://localhost:8081`, and `python scripts/verify/contact_prefill.py --base-url http://localhost:8081` passed. The writing smoke test also passed; its test Lead/newsletter records were deleted afterward.

**Decided by:** GL identified the confusing Lead time controls and clarified customer copy versus employee copy; Codex implemented the backend/form parity fix.

---

## 2026-05-02 - Owner Home combines command center with guided next actions

**Decision:** Jeff's Owner Home should use a basic command-center overview with the guided checklist built into the same first screen. The workspace should show live cards for `New Inquiries`, `Bookings`, `Customers`, and `Overdue Follow-ups`, one small incoming-inquiries chart, and a plain-language "What Jeff does next" flow before secondary catalog tools.

**Reasoning:** GL liked the basic overview but clarified that Jeff lives in the checklist/action layer. The Owner Home still needs enough visual context to prevent disorientation, but it should not become a full analytics dashboard. This keeps Jeff focused on the next operating action while still showing what is happening in the business.

**Implementation:** `locally_twisted.seed.sync_backend_workspaces` now creates the Owner Home Number Cards, the `LT Incoming Inquiries` Dashboard Chart, and the Workspace content blocks. `scripts/setup/sync_backend_workspaces.py` applies the sync to the running site.

**Verification receipt:** `python scripts/setup/sync_backend_workspaces.py`, `python scripts/verify/backend_workspace_parity.py`, and `npm run test:desk-owner` passed on 2026-05-02. The owner API login check showed `Owner Home` first and live counts of 12 Leads, 8 Sales Orders, 4 Customers, and 0 Tasks.

**Decided by:** GL approved the A+C visual direction; Codex implemented it as native ERPNext Workspace records.

---

## 2026-05-02 - Simplified workspaces use one booking calendar language

**Decision:** Owner, Manager, and Employee workspaces should use the same business labels for shared actions: `Booking Calendar` points at `Sales Order` Calendar view by `delivery_date`, `Customers` points at Customer records, and `People to Contact` points at Contact records. Accountant remains finance-focused and does not inherit operational workspace clutter.

**Reasoning:** The owner account was fixed first, but Manager and Employee still showed the old `Event Calendar`, `Clients & Customers`, and `Contacts` labels. That recreated the same confusion Jeff hit: bookings existed as Sales Orders, while the visible calendar could point to empty Event records.

**Verification receipt:** `python scripts/verify/backend_workspace_parity.py` failed before the sync on Manager/Employee stale labels, `python scripts/setup/sync_backend_workspaces.py` updated those workspaces, the verifier passed after, and a second sync no-opped.

**Decided by:** Codex during ERPNext backend simplification after GL asked to continue fixing the backend.

---

## 2026-05-02 - Lead photo wiring lives in the current backend sync

**Decision:** The Lead `Inspiration Photos` section should remain, but it must be backed by the `custom_inspiration_photos` Table field pointing at the `LT Lead Photo` child DocType. The current idempotent backend sync owns that wiring. Old one-off Lead translation/fix scripts are not operational code and were removed.

**Reasoning:** The live Lead form had an empty `Inspiration Photos` section because the child DocType existed but the Table field was missing. Keeping executable historical scripts that still referenced `/book`, `Delivery Only`, and `Event Package` made the backend fragile for future handoffs.

**Verification receipt:** `python scripts/setup/sync_contact_intake_backend.py` created `custom_inspiration_photos`; `python scripts/verify/lead_backend_intake_parity.py` passed and confirmed the `LT Lead Photo` child table wiring.

**Decided by:** Codex during the ERPNext backend simplification cleanup after GL asked to continue fixing the backend.

---

## 2026-05-02 - Variant media maps only when the source label is defensible

**Decision:** Product detail pages should switch the main image when the selected ERPNext variant has its own `Item.image`. The first media sync maps scraped Odoo extra images onto variants only when the image URL/filename label clearly matches an option such as size, height, length, design, LED lights, topper, or theme. Generic or ambiguous gallery images remain unmapped until GL/Jeff review.

**Reasoning:** GL clarified that multiple photos usually belong to the size/variant option and that balloon decor images must respect the real product structure rather than random color/photo assignment. The Odoo scrape includes many extra images, but not all filenames describe a variant. A conservative mapper preserves customer trust: use specific evidence, fall back to the parent product image when uncertain, and leave the rest for human/business review.

**Implementation:** `scripts/setup/sync_variant_media.py` stages `_resources/odoo-live/images/` into Docker and runs `locally_twisted.seed.sync_variant_media`. The first pass set 1,712 variant `Item.image` values. Product detail JS calls `locally_twisted.api.variant_media.get_variant_media` after exact option selection. Cart/checkout use variant images when present and otherwise fall back to the parent Website Item image.

**Verification receipt:** `python scripts/verify/variant_media_contract.py`, `python scripts/verify/cart_checkout_contract.py`, `python scripts/verify/smoke_shop.py`, `python scripts/verify/nav_ia.py`, and `npm run test:layout-fit` passed. Visual receipts: `output/playwright/variant-media-classic-arch-desktop.png` and `output/playwright/variant-media-classic-arch-mobile.png`.

**Decided by:** GL approved continuing with variant media implementation; Codex chose the conservative auto-map boundary and logged the remaining review work.

---

## 2026-05-02 - Owner Desk uses business labels and booking calendar on Sales Orders

**Decision:** Jeff's simplified Owner Desk should expose business actions, not ERPNext internals. `Customer` is labeled `Customers`, `Contact` is labeled `People to Contact`, product creation is exposed only when the owner role has native `Item Manager` permission, and the visible booking calendar uses `Sales Order.delivery_date` rather than the generic `Event` DocType.

**Reasoning:** In ERPNext, Customers are the billable/client records used by orders and invoices; Contacts are individual people, phone numbers, and emails that can attach to a customer. For Locally Twisted, this distinction matters most for corporate events where the customer may be a company and the contacts may be the planner, accounts payable person, or day-of contact. The prior Owner Home showed `Bookings` as Sales Orders but `Event Calendar` as empty Event records, creating the confusing state of 8 bookings and no calendar entries.

**Verification receipt:** As `lt-owner-temp@example.com`, `/app/Workspaces` returned 200, the sidebar showed `Owner Home` then `Home`, Item metadata loaded with `Item Manager` create/write permission, and the Sales Order calendar endpoint returned the 8 current bookings on `2026-05-06`. The generic `Event` count remained 0, confirming the old calendar target was the mismatch.

**Operational impact:** These are live local DB changes, not exported fixtures yet. Before production/cutover, decide whether Role Profile, Workspace, and Calendar View records should be exported or recreated by an idempotent setup script.

**Decided by:** GL raised the owner-account confusion during backend simplification; implemented by Codex.

---

## 2026-05-02 - `/shop` is the all-decor hub; `/shop-by-category` is retired

**Decision:** The visible customer browse hub is `/shop`. Header, mobile drawer, footer, `/shop-items`, and `/all-products` should send broad browse traffic to `/shop`. `/shop-by-category` stays only as a compatibility route and redirects to `/shop`; it should not render the old category-card index.

**Reasoning:** GL reviewed the category-card page and called the cards unacceptable. Live inspection confirmed the page looked placeholder-like and even displayed broken count copy, while `/shop` already had a stronger product grid plus category filters. For launch, a thin category-index page creates a worse first impression than sending customers straight to the all-product shop and preserving individual category pages under `/shop-items/<group>`.

**Alternatives considered:** Redesign `/shop-by-category` immediately; rejected for launch because it duplicates `/shop` and would require real category imagery/content before it helps. Keep the page for SEO; rejected as a primary surface because individual category and product pages carry the useful SEO value without exposing a low-quality index.

**Verification receipt:** `python scripts/verify/nav_ia.py`, `python scripts/verify/smoke_shop.py`, and `npm run test:layout-fit` passed after the change. Fresh desktop and mobile screenshots were captured at `output/playwright/nav-balloon-decor-desktop.png` and `output/playwright/nav-balloon-decor-mobile.png`.

**Decided by:** GL approved Codex's recommendation to implement the launch-safe route/nav cleanup.

---

## 2026-05-02 - Variant cart contract uses sellable Item codes with parent Website Item display

**Decision:** Guest cart and checkout use the actual sellable `Item.item_code` for pricing and Sales Order lines. For variants that do not have their own Website Item row, cart display resolves the parent Website Item for customer-facing name, image, and route. Variant template codes are not directly purchasable from `/shop`.

**2026-05-05 update, superseded 2026-05-06:** This cart contract still applies to checkout-enabled retail variants. A short-lived follow-up treated custom install groups such as Arches and Garlands as quote-required under `commerce_rules.py`; the 2026-05-06 delivery-zone decision supersedes that product-group gate.

**Reasoning:** A shop/media audit found variant templates were visible but not purchase-trustworthy: `/shop` card buttons could add unpriced template codes, while configured variant codes such as `6-color-rainbow-arch-20F` existed and had prices but were rejected by the cart API because they lacked Website Item rows. The correct boundary is: variants are what ERPNext sells; parent Website Items are what the website uses to display the product page.

**Verification:** `python scripts/verify/cart_checkout_contract.py` passes. At the time, `python scripts/verify/smoke_shop.py` included a real option-selection add-to-cart check for `6-color-rainbow-arch-20F`. Current smoke coverage uses `unicorn-bouquet` for the retail variant add-to-cart proof and checks that fixed-price product pages do not present product-level quote gates.

**Decided by:** Codex implementation after 2026-05-02 shop/media audit; aligned with launch goal that customers must not be able to believe an unreconciled purchase path.

---

## 2026-05-02 - Odoo folder is the business source of truth, not an app build target

**Decision:** `C:\Users\baenb\projects\locally-twisted-odoo\` is the source of truth for Locally Twisted business details. The ERPNext repo remains the app build target for launch.

**Reasoning:** The Odoo project drive contains the business discovery, catalog detail, policy detail, voice, and historical business context. The ERPNext repo may contain copied or rewritten business content, but that content is suspect unless it can be traced back to the Odoo business-detail source, current `_resources/` material that was pulled from it, or GL/legal approval. Keeping business truth separate from app builds prevents agents from treating accidental ERPNext copy as authoritative.

**Operational impact:** Agents may read the Odoo directory when business details are needed, but must not modify it from this ERPNext project. When customer-facing copy, policies, product/service claims, or business positioning matter, prefer the Odoo business-detail source over app-build prose. Verify implementation behavior in ERPNext separately; Odoo is business truth, not current app-state truth.

**Decided by:** GL clarified the source boundary during the take-live coordination pass; implemented by Codex.

---

## 2026-05-02 - Documentation ownership moves to queue plus workstreams

**Decision:** Full parity across `HANDOFF.md`, `PROJECT-STATUS.md`, and `locally-twisted-queue.md` is no longer the operating goal. The project will use single ownership by kind of truth:

- `AGENTS.md` - project rules, source routing, and verification rules.
- `locally-twisted-queue.md` - active work lanes only.
- `workstreams/<feature>.md` - feature-specific current state and multi-handoff coordination.
- `locally-twisted-decisions.md` - durable decisions and why they were made.
- `CODING-HANDOFF.md` - compact technical bootstrap for a new coding agent.
- `HANDOFF.md` and `PROJECT-STATUS.md` - legacy whole-project surfaces, kept as historical/contextual references until deliberately retired or extracted.

**Reasoning:** Multiple instances can work in the repo at the same time, and the project has too many facets for a single monolithic status file to stay current. Trying to keep every doc in full parity creates stale authority and wastes effort. A feature-lane model makes parity possible inside each workstream without forcing every global file to restate the same facts.

**Operational impact:** Do not rewrite old global handoff/status files to chase complete parity. Update the one file that owns the fact: queue for active lanes, workstream file for feature state, decisions log for durable reasoning, and `CODING-HANDOFF.md` for compact technical startup. If a legacy file is useful, add a short pointer/banner rather than duplicating live state.

**Alternatives considered:** Keep `PROJECT-STATUS.md` as the active README/status/handoff hybrid; rejected because it is already part current map, part historical receipt, and part stale project detail. Delete `PROJECT-STATUS.md` or `HANDOFF.md` immediately; rejected because they still contain useful historical receipts. Future cleanup can extract stable architecture into a smaller `PROJECT-MAP.md` if needed.

**Decided by:** GL approved the documentation architecture pivot; implemented by Codex.

---

## 2026-05-01 - Public service selections populate Lead `custom_event_type`

**Decision:** Website inquiry submissions populate the Lead `custom_event_type` Table MultiSelect child rows, not only text notes. `custom_event_type` is the backend source of truth for selected services because Lead Desk conditional sections depend on those child rows.

**Reasoning:** The public form was current, but the live ERPNext backend still had stale `LT Service Type` records (`Delivery Only`, `Event Package`) and Desk conditions tied to those values. The submit handler also wrote service labels as text but did not populate the Table MultiSelect, so a real web inquiry could land without opening the relevant Desk sections for Jeff. Mapping into `custom_event_type` fixes the actual CRM usability gap.

**Implementation notes:** `locally_twisted.seed.sync_contact_intake_backend.execute` renames stale service records, adds `Pickup`, updates Lead Custom Field labels/depends_on logic, and clears Lead cache. `submit_book_inquiry` now builds `custom_event_type` child rows from selected public services. No new Lead fields were added.

**Verification receipt:** `python scripts/verify/lead_backend_intake_parity.py` passed after the sync. A direct endpoint submission with `Delivery`, `Pickup`, and `Events Inquiry` created a Lead whose `custom_event_type` rows matched those three services; the test Lead and related artifacts were deleted.

**Decided by:** GL approved the backend parity slice; implemented by Codex.

---

## 2026-05-01 - Contact services are stackable; Events Inquiry is the high-value package path

**Decision:** `/contact` is the canonical inquiry surface and its service choices are stackable: Balloon Decor, Balloon Twisting, Face Painting, Delivery, Pickup, Events Inquiry, and Something Else. `Events Inquiry` replaces `Event Package` and is the package-planning path for larger, multi-piece purchases. Delivery and Pickup do not use "Only" labels. `/book` redirects to `/contact?intent=quick`, and `/balloon-twisting-and-face-painting` routes interested customers to guided contact URLs instead of embedding a separate form.

**Reasoning:** GL corrected the form logic: "Only" implies mutual exclusion, but Delivery and Pickup can stack with other services. Large corporate and multi-piece event packages are the ideal customer path, so Events Inquiry should be structured and inviting instead of a freeform decor note. Questions should only appear when relevant; shade/environment applies to live artists, not outside balloon decor, delivery, pickup, or Something Else.

**Implementation notes:** Events Inquiry uses package-piece checkboxes from the homepage custom categories (Balloon Arches, Columns, Garlands, Picture Perfect Backdrops, Balloon Drops, Balloon Bouquets, Centerpieces, Custom Sculptures), asks for colors with more playful copy, and aggregates selected pieces/colors/notes into the existing Lead text fields. Pickup has its own panel and points customers to the location information below the form. Riverdale location copy is `Northern Utah Location (Residential Address)`.

**Alternatives considered:** Keep `Event Package` and a freeform "What type of decor?" field; rejected because it underserves the ideal large-package buyer. Keep `Delivery Only` / `Pickup Only`; rejected because it promises mutual exclusion the UI does not enforce. Add new ERPNext schema fields immediately for every Events Inquiry sub-answer; deferred until the backend Desk/CRM form parity pass verifies whether new fields are worth the schema churn.

**Verification receipt:** Public form logic passed `python scripts/verify/contact_service_logic.py --base-url http://localhost:8081`, `python scripts/verify/contact_prefill.py --base-url http://localhost:8081`, `python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --form-path /contact --skip-newsletter`, and `npm run test:layout-fit`. Backend record verification in `smoke_forms.py` requires `LT_ADMIN_PASSWORD`; Desk CRM presentation still needs a visual parity pass.

**Decided by:** GL directives during 2026-05-01 form cleanup; implemented by Codex in commits `b473690`, `89d9870`, `9ec272b`, and `ca2e951`.

---

## 2026-05-01 - Runtime packaging clarified: custom image plus LT live-edit overlay

**Decision:** Current local runtime uses the custom image `locally-twisted-erpnext:v15` for Frappe, ERPNext, payments, webshop, build tooling, assets, and the nginx Origin pass-through patch. It also still bind-mounts `apps/locally_twisted` into Frappe services as a development live-edit overlay. Payments and Webshop are image-owned upstream apps, not host bind-mounted.

**Reasoning:** A prior decision entry said all three app bind-mounts were removed. The important durable change was removing the fragile post-recreate editable-install pattern for upstream apps and baking the stack into the image. The LT app overlay remains useful for local development and is visible in both `pwd.yml` and `docker inspect`.

**Verification receipt:** `Locally-Twisted-Backend/frappe_docker/pwd.yml` uses `image: locally-twisted-erpnext:v15` and mounts `../../apps/locally_twisted:/home/frappe/frappe-bench/apps/locally_twisted`. `docker inspect locally-twisted-erpnext-v15-backend-1` and frontend show the same bind mount. `docker exec locally-twisted-erpnext-v15-frontend-1 grep -n -E "proxy_set_header Origin|http_origin|Origin" /etc/nginx/conf.d/frappe.conf` returned `proxy_set_header Origin $http_origin;`.

**Operational impact:** Do not run `scripts/setup/install_webshop.py` or `scripts/fix/patch_nginx_socketio_origin.py` as routine post-recreate rituals on the current stack. Keep them only as historical/fallback tools.

**Decided by:** Codex reconciliation pass under GL directive to clean stale claims before moving forward.

---

## 2026-05-01 - Layout-fit gate restored and verified

**Decision:** `scripts/verify/layout_fit.spec.js` is now a real committed Playwright Test gate, with a local Node project wrapper in `package.json`. Use `npm run test:layout-fit` for the customer-site layout fit check.

**Reasoning:** The earlier layout-fit gate reference was a valid need but an invalid claim: the file was missing. Recreating the spec turns that claim back into executable evidence. The gate checks 15 public/shop/cart routes at 320px, 375px, tablet, and desktop widths for HTTP availability, document horizontal overflow, visible element overflow outside the viewport, and direct text overflow.

**Verification receipt:** TDD red run: `npx playwright test scripts/verify/layout_fit.spec.js --reporter=line` failed with "No tests found" before the file existed. First green attempt produced 52 passed / 8 failed, catching real text overflow in `.lt-contact__icon` on `/contact` and `/book`. After widening the icon slot in `apps/locally_twisted/locally_twisted/www/contact.html` and clearing website cache, `npm run test:layout-fit` passed all 60 checks.

**Decided by:** GL directive to reconcile the claim first; implemented by Codex.

---

## 2026-05-01 - Historical red check before layout-fit restoration

**Superseded later on 2026-05-01:** the gate was restored as `scripts/verify/layout_fit.spec.js` and verified via `npm run test:layout-fit` with 60 passing checks. Keep this entry only as the receipt that the earlier doc claim was properly challenged before restoration.

**Decision at that point in the session:** the prior `scripts/verify/layout_fit.spec.js` claim had to be challenged before anyone relied on it. Verification at that moment found no matching file in the working tree and no git history for `layout_fit` / layout-fit spec paths.

**Reasoning:** A future agent could otherwise believe a browser-fit gate exists and skip screenshots or real browser checks. The project trust rule is stricter: a claimed gate that cannot be found is not a gate.

**Verification receipt:** `rg --files -g '*layout*' -g '*fit*' -g '*.spec.js' -g 'package.json' -g 'playwright.config.*'` found only `_resources/design-guide/synthesis/layout.tsx`; `git log --all --name-status -- '*layout_fit*' '*fit*.spec.js' '*layout*.spec.js'` returned no matching file history.

**Follow-up:** Either recreate and commit the intended Playwright layout-fit spec, or remove remaining operational references to it. Until then, visible work still requires route checks plus desktop/mobile screenshots inspected by the agent and, for customer-facing claims, real-browser confirmation.

**Decided by:** GL directive to reconcile the claim first; implemented by Codex.

---

## 2026-05-01 - Codex project capabilities are routed through AGENTS.md

**Decision:** LT now has a project-level Codex capability install at `.codex/capabilities/`, routed from `AGENTS.md`. Codex should read `.codex/capabilities/INDEX.md` when a task depends on local tools, reusable workflows, operating knowledge, or prior lessons, then open only the specific capability files needed.

**Reasoning:** GL wants the Claude-era capabilities framework translated into a clean Codex-compatible workshop. Codex does not use Claude Code's eager `@import` behavior, so the correct project-level pattern is explicit `AGENTS.md` routing plus on-demand reads. This preserves the multi-tier model without loading the whole capability tree into every turn.

**Verification receipt:** An ephemeral Codex run in this repo found `.codex/capabilities/INDEX.md` from the project-level `AGENTS.md` section and read `.codex/capabilities/ingredients/screenshot.md`.

**Decided by:** GL approved adapting the framework for Codex; implemented by Codex.

---

## 2026-05-01 - Layout fit is a browser-gated contract, not a visual impression

**Correction 2026-05-01:** The gate named below was missing when challenged earlier in the session, then restored later the same day. Use the newer "Layout-fit gate restored and verified" entry above for current state.

**Decision:** Customer-facing fit checks now live in `scripts/verify/layout_fit.spec.js`. The gate covers the main public pages, the new policy pages, shop/category/product routes, and cart at 320px, 375px, tablet, and desktop widths. The check fails on horizontal document overflow, visible element overflow outside the viewport, and text overflow inside visible elements. It intentionally ignores descendants clipped by an overflow-hidden/scroll/auto ancestor, so carousels can keep offscreen track content without creating false positives.

**Reasoning:** GL reported real visible breakage: the Seasonal category `Next` button was half off screen, and product breadcrumbs/title text escaped the viewport. One-off screenshots were not enough; the project needed a repeatable gate that catches this class of defect before anyone claims a page fits.

**Alternatives considered:** Rely on manual screenshot review only. Rejected because screenshot review is necessary but not durable. Add broad `overflow-x: hidden` to the body. Rejected because it hides evidence instead of fixing or identifying the source. The implemented gate checks actual layout geometry and forces specific fixes.

**Verification receipt:** Latest direct Playwright run: 60 tests passed using `C:\Users\baenb\AppData\Local\npm-cache\_npx\420ff84f11983ee5\node_modules\.bin\playwright.cmd`.

**Decided by:** GL directive 2026-05-01 ("Everything needs to be checked for actual fit") and implemented by Codex.

---

## 2026-05-01 - Privacy and Terms are static Frappe routes, with legal approval still separate

**Decision:** `/privacy` and `/terms-of-service` are static Frappe `www/` routes in the `locally_twisted` app. They are plain-language readiness pages for Stripe live-mode URL requirements. The dashed `/terms-of-service` URL aliases to `terms_of_service` through `website_route_rules` because Frappe does not auto-map underscored filenames to dashed URLs.

**Reasoning:** Stripe Dashboard had placeholder policy URLs, and both routes were 404. The captured Hetzner `privacy.html` was itself a 404 shell, so there was no old policy copy to port. The pages therefore use verified local sources: form behavior, payment flow, deposit rules, cancellation/refund policy, service area, and Jeff's legal-interview answers. Copy stays conservative and operational, not lawyer-reviewed final legal language.

**Alternatives considered:** Wait for attorney-ready pages before adding routes. Rejected because Stripe live-mode readiness needs working URLs now, and the pages clearly state operational policy using existing verified sources. Invent broader legal terms. Rejected because the project rule forbids inventing business/legal facts.

**Follow-up:** GL/legal review, then update Stripe Dashboard "Privacy policy URL" and "Terms of service URL" away from placeholders.

**Decided by:** Queue P0/P1 Stripe-readiness blockers and implemented by Codex from verified project policy sources.

---

## 2026-05-01 - Occasion navigation must be product-backed; `/contact` is the inquiry path

**Decision:** `Plan by Occasion` is product discovery navigation, not a shortcut into the inquiry form. Current occasion links point to real product/category pages: Birthdays -> Birthday Deliveries; Baby Showers & Reveals -> Baby Shower Garland; Graduations -> Graduation Grab n Go; Get Well -> Get-Well Bouquets; Missionary Farewells & Homecomings -> Large head Missionary; Church Events/Weddings -> Garlands; Religious Celebrations -> Easter Arch; Corporate Events -> Logo 3 layered bouquet; Schools & Community -> Basketball Arch; Holidays & Seasons -> Seasonal & Specialty.

**Reasoning:** GL corrected the contact-first interpretation directly: if a customer opens an occasion menu in a shop, they expect products. Routing every occasion to `/contact?occasion=...` made the menu feel empty and evasive. The contact path already exists in the top utility bar and primary CTAs; the occasion dropdown should keep customers browsing purchasable or inspectable products.

**Alternatives considered:** Keep all occasion links as prefilled contact form URLs. Rejected by GL. Create new occasion landing pages now. Deferred because current ERPNext Website Items already provide concrete product/category targets and new landing pages would add more surface before the shop IA is stable.

**Parity rule:** Run `python scripts/verify/nav_ia.py` after nav changes. The verifier now fails if occasion routes regress to `contact?occasion=...`, if `/book` returns to nav, or if duplicate Contact links appear in the mobile drawer.

**Decided by:** GL directive 2026-05-01; implemented by Codex against verified Website Item/Item Group routes.

---

## 2026-05-01 - `/book` retired; `/contact` is the surviving customer inquiry surface

**Decision:** `/contact` is the standard solo customer contact form. `/book` is no longer a customer-facing destination and exists only as a route alias to `/contact` for legacy/internal traffic. Current site CTAs and navigation should point to `/contact`.

**Reasoning:** GL corrected the inherited `/book` framing: "The `/book` contact form is now the standard solo contact form." Continuing to treat `/book` as the primary conversion page kept queue/status docs and CTAs out of parity with the current site direction. The existing Lead submission machinery can still be reused behind the contact form; the public route decision is separate.

**Alternatives considered:** Keep both `/book` and `/contact` as first-class surfaces. Rejected because it duplicates the same customer action and keeps stale nav/docs alive. Delete all `/book` code immediately. Deferred because `/contact` still imports the shared form/submission machinery from `www/book.py`; deeper code rename can be a later cleanup if worth the churn.

**Decided by:** GL directive 2026-05-01.

---

## 2026-05-01 - Root shop browse routes alias to `/shop-by-category`

**Superseded 2026-05-02:** `/shop` is now the all-decor hub and `/shop-by-category` is a compatibility redirect to `/shop`. Keep this entry as historical context only; do not use it as current routing guidance.

**Decision:** `/shop-items` and `/all-products` route to `/shop-by-category`. The far-left primary nav label is `Shop Balloon Decor`, and its "All Balloon Decor" CTA also uses `/shop-by-category`.

**Reasoning:** GL flagged `/shop-items` as pointless/empty. ERPNext's root Item Group page is too thin as a customer browse landing page, while the custom `/shop-by-category` route gives the intended category-card browse surface. Keeping the thin route visible would preserve a bad first impression.

**Alternatives considered:** Build a richer root Item Group page at `/shop-items`. Deferred because `/shop-by-category` already exists and is the intended browse surface. Redirecting/aliasing is lower blast radius and keeps category detail routes under `/shop-items/<group>` intact.

**Decided by:** GL directive 2026-05-01; implemented by Codex.

---

## 2026-05-01 - No Gallery in current navigation

**Decision:** Gallery is not part of current nav or Phase 2 page-rebuild priority. Do not add a Gallery link until GL reopens that scope.

**Reasoning:** GL explicitly said "no gallery for now." The mirror has gallery material, but exposing another route before the core shop/contact/policy surfaces are stable adds clutter and more unfinished surface area.

**Alternatives considered:** Keep Gallery as a placeholder because the mirror has a page. Rejected because current nav must reflect active scope, not inherited mirror shape.

**Decided by:** GL directive 2026-05-01.

---

## 2026-05-01 — Customer chrome IA cleanup: no `What We Make`, no About, no Book an Event links

**Decision:** The current header/footer navigation does not include `What We Make`, `About Us`, or `Book an Event`. The footer Shop column keeps `All Products`; Company links stay limited to real, currently supported surfaces.

**Reasoning:** GL explicitly corrected the footer and menu: `What We Make` is no longer a menu item, there is no About Us page, and there is no Book an Event page. Leaving links to nonexistent pages creates broken navigation and makes the footer look like copied site furniture rather than the current ERPNext storefront.

**Alternatives considered:** Keep the Hetzner mirror's historical menu labels as placeholders for future Phase 2 pages. Rejected because current navigation must only expose real or intentionally active routes.

**Decided by:** GL directive during the 2026-04-30/2026-05-01 storefront correction session.

---

## 2026-05-01 — Product listing cards use `lt_brand_description` surfaced through a local Webshop API override

**Decision:** Product listing cards should show the product's brand description, not only the product title and not generic sales-pitch copy. The implementation wraps Webshop's `webshop.webshop.api.get_product_filter_data` via Frappe `override_whitelisted_methods`, delegates to the stock API, then appends `lt_brand_description` for returned Website Items. Listing JavaScript prefers `lt_brand_description`, with fallback to existing Webshop description fields.

**Reasoning:** GL asked for the brand description on the listing card, not just the detail page. The least invasive path is a local app override that preserves Webshop's filtering/sorting behavior while adding one LT-specific field to the response. Editing Webshop core or replacing the listing endpoint would increase maintenance risk.

**Alternatives considered:** Patch Webshop source directly; rejected because Webshop is an upstream app and this project has a standing "work within Frappe/ERPNext" rule. Rebuild the whole listing pipeline; rejected because the needed behavior is a small data enrichment.

**Decided by:** Codex implementation under GL directive.

---

## 2026-05-01 — `/shop-items/<group>` filtering depends on Webshop's `.item-group-content` wrapper contract

**Decision:** Custom Item Group wrapper markup must keep Webshop's `item-group-content` class when rendering `/shop-items/<group>` pages.

**Reasoning:** The Arches category bug was not a product-data issue. Webshop's `all-products/index.js` reads the active Item Group from `.item-group-content`; the LT override had moved the group value to a custom `.lt-shop` wrapper without the class Webshop's JavaScript expects. The result: `/shop-items/arches` fell back to unscoped product results and returned non-arches. Restoring the expected class fixes category filtering without touching catalog data.

**Alternatives considered:** Add a second custom category-detection path in JavaScript. Rejected because preserving the framework contract is simpler and less fragile.

**Decided by:** Codex implementation after debugging the actual Webshop listing behavior.

---

## 2026-05-01 — Accessibility sizing is a hard constraint, not a layout variable

**Decision:** Layout fixes must preserve legal-accessibility-sized text, controls, and hit targets. Do not "fix" footer/header/listing density by shrinking text or interactive controls below accessible sizes. For touch/click targets, use at least 44px practical target height where controls are interactive.

**Reasoning:** GL explicitly corrected the bad instinct to make the footer smaller by shrinking everything. The correct fix is layout, spacing, alignment, and content removal, not illegible text or undersized controls.

**Alternatives considered:** Reduce font sizes and control heights to visually balance header/footer. Rejected as inaccessible and against GL's directive.

**Decided by:** GL directive, promoted into local/global memory for future sessions.

---

## 2026-04-30 (late evening) — Container reversion: bind-mount + post-recreate-reinstall pattern replaced by self-contained custom Docker image

**Correction 2026-05-01:** the current compose file uses the custom image and still bind-mounts `apps/locally_twisted` as a local live-edit overlay. Payments and Webshop are image-owned. The intended current rule is "no fragile upstream-app bind-mount plus post-recreate reinstall ritual."

**Decision:** Replace the fragile upstream-app bind-mount-and-pip-install-after-every-recreate pattern with a custom Docker image (`locally-twisted-erpnext:v15`, built from `docker/Dockerfile`). The image bakes in frappe + erpnext (from base `frappe/erpnext:v15.105.0`), payments + webshop (cloned from upstream), locally_twisted image content, Node 18 + yarn, compiled bench assets, and the nginx Origin pass-through patch. The compose file (`Locally-Twisted-Backend/frappe_docker/pwd.yml`) references the custom image. Current local development still overlays `apps/locally_twisted` with a bind mount for live edits; `payments` and `webshop` do not need host bind mounts. `scripts/setup/install_webshop.py` and `scripts/fix/patch_nginx_socketio_origin.py` are historical/fallback scripts, not routine steps against the current stack.

**Reasoning:** GL directive: *"There's constantly breaking of containers because ERPNext naturally contains everything. We need to revert to that. An instance said that they made a 'structural change' so that container issue wouldn't happen and all it did was break everything. We need to fix that first and revert back to frappe's native containers."* The structural change was the bind-mount pattern: apps lived on the host, were mounted into the container, and an editable pip install + Node + yarn install + nginx patch had to be replayed in the container's writable layer after every `docker compose up --force-recreate` (because the writable layer is destroyed on recreate). The previous instance who shipped webshop documented this in the install script's own docstring: *"Long-term fix: bake Node + yarn into a custom Docker image."* That long-term fix is now done. Verified: a `--force-recreate` round-trip produces a fully-working stack with all 5 apps registered, all key URLs returning HTTP 200, and the nginx Origin pass-through line correctly rendered into `/etc/nginx/conf.d/frappe.conf` — with NO post-recreate scripts.

**Trade-off accepted:** Payments/Webshop/runtime patches are image-owned, so those changes need an image rebuild. `apps/locally_twisted/` remains live-editable through the local development bind mount. The trade is worth it for eliminating recurring upstream-app reinstall and nginx repatch rituals while keeping LT app iteration fast.

**Alternatives considered:** (a) Keep bind-mount but auto-run `install_webshop.py` from the configurator service's command — would still leave Node + yarn in the writable layer (broken on recreate) and still leave editable pip installs vulnerable; not actually native. (b) Push locally_twisted to a private GitHub repo and use upstream `images/custom/Containerfile` with apps.json — required GL to set up GitHub plumbing, rejected per the global "don't make GL the engineer" rule.

**Reversibility:** The previous pwd.yml is at `Locally-Twisted-Backend/frappe_docker/pwd.yml.bak-pre-image-bake`. To roll back: copy that over `pwd.yml`, recreate the stack, run `install_webshop.py` to reinstate editable installs, run `patch_nginx_socketio_origin.py` to reinstate the runtime nginx patch. Data volumes (sites, db-data, redis-queue-data, logs) are unchanged by the swap.

**Decided by:** Claude Opus 4.7 under GL autonomous-engineering authorization (2026-04-30: *"this session it is acceptable to break the cache rule"* + the new global hard rule *"Don't Make GL the Engineer."*).

---

## 2026-04-30 (evening) — Mega menu IA: flat 11-Item-Group structure preserved + template-level grouping into 3 panels

**Decision:** The Hetzner mirror has 3 mega menu panels (Special Occasions / Holidays & Seasons / What We Make) with 2-level hierarchy. Our ERPNext catalog has 11 flat children under "Shop Items" (Arches, Columns, Bouquets, etc. — verified by the catalog port: 53 Website Items, 10,578 variants, 10,613 Item Prices). Rather than restructuring the Item Group tree to add Special Occasions + Holidays & Seasons parents (and reassigning all 53 Website Items), we keep the flat 11 and group them into the 3 Hetzner panels at the **template layer** via three new context keys exposed by `navbar_context.py`: `mega_special_occasions`, `mega_holidays_seasons`, `mega_what_we_make`. Each is a list of `{label, route}` dicts. Some leafs (Birthdays, Showers, Graduations, Missionary, Get-Well) point at content-only routes that may not have published pages yet — those will resolve via Phase 2 page builds OR remain as 404 placeholders until populated.

**Reasoning:** Lower blast radius. Restructuring the catalog tree would risk the just-verified data integrity (53/10,578/10,613). Template-level grouping is reversible — if GL prefers the 2-level Item Group tree structure later, we restructure `fixtures/item_group.json` and re-tag the 53 Website Items, and the navbar template adjusts. The "flat + template-group" choice preserves all existing investment in catalog data while delivering Hetzner's 3-panel UX.

**Alternatives considered:** Restructure the Item Group tree with Special Occasions + Holidays & Seasons as new parents under "Shop Items," reassign the 11 children appropriately. Rejected because it touches the data layer that was just verified at high cost.

**Decided by:** Claude Opus 4.7 (orchestrator), under GL's autonomous-decision authorization for the chrome rebuild session. **Reversible** — see `MIRROR-REBUILD-PLAN.md` Decision A.

---

## 2026-04-30 (evening) — Category URL shape: ERPNext-native `/shop-items/<slug>` retained, NOT Hetzner's `/shop/category/<slug>-<id>`

**Decision:** ERPNext webshop's `WebshopItemGroup.make_route()` auto-generates `/shop-items/<slug>` from the Item Group's `route` field (no Odoo-style numeric IDs). The Hetzner mirror uses `/shop/category/<slug>-<id>` URLs. Rather than mimic Hetzner's URLs exactly, we use ERPNext-native `/shop-items/<slug>` everywhere. Mega menu links + footer Shop column links + breadcrumbs all use the ERPNext shape.

To handle inbound references to Hetzner-shaped URLs (none exist externally today, but mirror markup contains them and Phase 2 page rebuilds may reference them):  add `website_route_rules` redirects from `/shop/category/<slug>` → `/shop-items/<slug>` for the 11 known categories when a real referrer surfaces.

**Reasoning:** Doesn't fight ERPNext's `make_route()` convention. No need to manually set `route` on each Item Group (which would be operator-state-sensitive — Jeff might rename a category later and the URL would break). Lower blast than redirect rules per category. Pre-launch — no external bookmarks to preserve. Hetzner-shape URL preservation can be added later via redirects if real inbound traffic appears.

**Alternatives considered:**
- Manually set `route="shop/category/arches"` etc. on each of the 11 Item Groups via fixture override. Rejected — operator-state-sensitive (per `frappe-fixture-discipline`).
- Add 11 `website_route_rules` redirect entries today. Rejected — no inbound traffic yet; would be premature complexity.

**Decided by:** Claude Opus 4.7 (orchestrator), under GL's autonomous-decision authorization. **Reversible** — see `MIRROR-REBUILD-PLAN.md` Decision B.

---

## 2026-04-30 (evening) — Blog: use Frappe's NATIVE `Blog Post` DocType, NOT a custom `LT Blog Post`

**Decision:** Frappe core ships a fully-functional blog system: `Blog Post` + `Blog Category` + `Blogger` + `Blog Settings` DocTypes, plus `blog_post.html` and `blog_post_list.html` templates. Use the native DocType. Add a `tags` field via `Customize Form` (Table MultiSelect linking to a tiny `LT Blog Tag` DocType — 1 field) for the tag-filtering feature Hetzner has but Frappe's blog lacks. Add a thin template override at `apps/locally_twisted/locally_twisted/templates/pages/blog_post.html` for the SEO meta tags Frappe's native template doesn't emit (canonical link, article:published_time/modified_time/tag OG metas, Twitter `summary_large_image`, BreadcrumbList JSON-LD).

**Reasoning:** Frappe's native `Blog Post` provides for free: schema.org BlogPosting itemscope, OG meta tags with auto-fallback, `read_time` auto-calc, RSS/Atom feeds per category, "Load More" pagination, browse_by_category dropdown, full-text search, breadcrumbs, social sharing toggles, likes, comments, blog_intro 200-char excerpt, `Blogger` author block. Building a custom `LT Blog Post` would duplicate all of that and lose the framework integration. The original `MIRROR-REBUILD-PLAN.md` called for a custom DocType; `/plan-deepen` caught this regression vs the website-page-index.md (which had already classified blog as Tier 3 native).

**Alternatives considered:** Custom `LT Blog Post` DocType. Rejected — reinvents the wheel.

**Decided by:** Claude Opus 4.7 (orchestrator) following /plan-deepen finding. Plan section "Phase 2 — orders #9/#10" rewritten accordingly.

---

## 2026-04-30 — Project frame: this IS a migration, not a new build

**Decision:** Frame Locally Twisted's ERPNext project as **a migration of business intent + catalog data into a fresh ERPNext install** — superseding the 2026-04-26 "first professional business platform / new build, not a migration" reframe.

**Reasoning:** GL directive 2026-04-30: *"it is a migration, not a new build."* The 2026-04-26 reframe was motivated by (a) Jeff-disclosure concerns — the failed Odoo attempt is BBC-internal context Jeff hasn't been briefed on yet — and (b) avoiding a too-mechanical "translate Odoo → ERPNext" mental model. Both concerns remain valid, but neither justifies denying the technical reality:

- Catalog data was ported from the prior Odoo deployment to ERPNext on 2026-04-30 (53 Website Items, 10,631 Items, 10,578 variants, 10,613 Item Prices — verified against the running DB).
- Form intent (the 45-field Lead schema, the `/book` + `/contact` form shapes) was carried forward from the Hetzner Odoo `arch_db` snapshots in `_resources/odoo-live-snapshot/`.
- Business policies, brand identity, voice rules, and the legal interview answers all originated in the Odoo phase and were brought across into `_resources/`.
- At cutover (Phase 6), the new ERPNext storefront replaces `locallytwisted.com` at the same domain.

The right framing: **migration of business intent + catalog data into a fresh ERPNext install.** "Fresh install" captures that we did NOT auto-translate Odoo modules / DB dumps / configuration — the destination was greenfield ERPNext, hand-built informed by Odoo discovery. "Migration" captures the truth about catalog records, form schema, policies, and the eventual domain cutover.

**What stays from the 2026-04-26 reframe:**

- **Jeff-disclosure stealth.** Jeff knows there's an audit; he doesn't know the prior Odoo attempt failed in testing. Internal docs use migration framing; Jeff-facing communications still don't leak that context until Phase 1 is demo-ready.
- **Hand-build, not auto-translate.** No automated Odoo-to-ERPNext module/data conversion tooling. Catalog data was the only record-level port; everything else was hand-built from discovery.
- **`_resources/` is canonical and platform-agnostic** in language. Anything from the Odoo dir that applies has been copied + scrubbed.
- **Reference Disposition stands.** `locally-twisted-odoo/` clone, `5.78.136.133` Hetzner deployment, `CBaen/locally-twisted-odoo` GitHub repo, and current `locallytwisted.com` all retire at/post-cutover.

**Alternatives considered:** keep the "new build" frame. Rejected — denying the migration reality cost token-spend across multiple sessions and contributed to Codex's `CHATGPT.md` / `CODING-HANDOFF.md` push to "verify before relying on" the Claude-era docs.

**Files updated** to carry the new framing: `CLAUDE.md`, `HANDOFF.md`, `PROJECT-STATUS.md`, `CODING-HANDOFF.md`, `AGENTS.md`, `.planning/PROJECT.md`, `.planning/ROADMAP.md`, `locally-twisted-index.md`. Historical entries (prior decisions log entries, lessons-learned entries, `research/` artifacts) preserved as-is — they record what was true at writing time. This entry supersedes the 2026-04-26 reframe entry below.

**Decided by:** GL.

---

## 2026-04-30 — Catalog rebuild from live Odoo (no exceptions)

**Decision:** Live Odoo (`http://5.78.136.133/shop`) is the catalog source of truth. The cached `_resources/odoo-export/catalog.json` (2026-04-26) is historical reference. Fresh scrape lives at `_resources/odoo-live/catalog.json`. Re-scrape via `scripts/setup/scrape_odoo_live.py` before any catalog work.

**Reasoning:** GL directive 2026-04-30: *"the only source of truth is the live site... pull every product from the live site... with every single variation that a product has."* The cached catalog had 51 products; the live re-scrape on 2026-04-30 found 53 (Odoo had added `birthday-deliveries`, `large-head-missionary` since the cache). 5 products had `image_url=null` cached but DO have images on the live site (the original scraper missed lazy-loaded `data-src` patterns). Also Odoo's per-product `data-attribute-exclusions` JSON was not captured in the original scraper — the new live scrape captures and respects it.

**Alternatives considered:** keep the cached catalog and patch missing fields. Rejected — caches drift, GL was explicit.

**Decided by:** GL.

---

## 2026-04-30 — Full Item Variant model, no skipping

**Decision:** Every Odoo-valid attribute combination becomes an `Item Variant` record. Honoring Odoo's `data-attribute-exclusions` to filter forbidden combinations from the cartesian product. Verified DB counts on 2026-04-30: 53 Website Items, 10,631 Items total, 49 variant templates, 4 single-SKU templates, 10,578 variants, 10,613 Item Prices, and 32,002 Item Variant Attribute child rows.

**Reasoning:** GL directive 2026-04-30: *"ALL VARIANTS DO NOT SKIP ANY."* Earlier in the same session I had proposed a "form-fed options" alternative (treat each product as single Item, render LT-owned color/size selectors at order time) — GL named it as me trying to "divert" from the task. Rebuild Odoo accurately means full ERPNext variant model.

**Alternatives considered:** form-fed options (simpler, no variant explosion). Rejected.

**Decided by:** GL.

---

## 2026-04-30 — 11-category Item Group hierarchy

**Decision:** `Shop Items` becomes a parent (`is_group=1`) with 11 children: Arches (10), Columns (10), Bouquets (16), Get-Well Bouquets (3), Garlands (4), Drops (1), Grab & Go (2), Table Decor (3), Stands & Easels (2), Deliveries (1), Seasonal & Specialty (1). Each `show_in_website=1`. Routes auto-generated as `shop-items/<scrubbed-name>`.

**Reasoning:** GL directive: mega menu populated from Odoo's natural taxonomy. The taxonomy is implied by Odoo product slug patterns (`*-arch`, `*-column`, `*-bouquet`, etc.) — formalized as 11 explicit BBC-decision Item Groups. Captured as a fixture so it's reproducible on transfer.

**Slug→group mapping:** lives at `_resources/odoo-live/slug_to_group.json` for review.

**Decided by:** Claude (taxonomy proposal), confirmed by GL via "Shape A" answer.

---

## 2026-04-30 — Routes change to `/shop-items/<group>/<item>`

**Decision:** All Website Items re-route from `shop/<item_code>` (the prior pattern) to `shop-items/<group_slug>/<item_slug>` for IA cleanliness. Pre-launch site has no public bookmarks; old `/shop/<item>` returns 404 from this date forward.

**Implementation gotcha:** webshop's `WebsiteItem.make_route()` appends `random_string(5)` to every auto-generated route. Override by setting `wi.route = clean_route` BEFORE save. Captured in `lessons-learned.md` 2026-04-30 Lesson 3.

**Decided by:** Claude (implementation choice within GL's "Shape A" routing decision).

---

## 2026-04-30 — `installed_apps` order changed: `locally_twisted` last

**Decision:** Reordered Frappe's `installed_apps` global JSON list to put `locally_twisted` LAST: `["frappe", "erpnext", "payments", "webshop", "locally_twisted"]`. Required for our template overrides at `apps/locally_twisted/.../templates/generators/item/...` to win the reversed-app-order ChoiceLoader resolution against webshop's stock templates.

**Reasoning:** `template_page.py:53` does `for app in reversed(frappe.get_installed_apps())` and picks the first match. Default order placed locally_twisted in middle; reversed put webshop first. Empirically verified: a marker class in our override file did NOT render until apps order was changed.

**Side-effect:** any future new app installed AFTER this change will appear AFTER locally_twisted in the list — meaning the new app would WIN over our overrides for any template path it defines. If a new app is installed, re-set the global to keep `locally_twisted` last.

**Decided by:** Claude (necessary technical fix to enable template overrides).

---

## 2026-04-30 — "Item Code" jargon and "/Nos" UoM stripped from customer-facing surfaces

**Decision:** Strip both via:

| Surface | Mechanism |
|---|---|
| Product detail title block | Jinja override at `templates/generators/item/item_details.html` (deletes the `<p class="product-code">` block) |
| Product detail price block | Jinja override at `item_add_to_cart.html` (deletes the `(...$X / Nos)` line) |
| Listing cards (JS-rendered) | CSS hide `.product-code` in lt-theme.css — webshop's compiled JS bundle can't be Jinja-overridden |

The CSS-hide is `display: none !important` — the only such chain we kept. It's contained: it removes the jargon at customer-render time without forking webshop's compiled JS bundle.

**Reasoning:** GL flagged "Shop Items | Item Code : baby-shower-garland" and "$ 150.00 / Nos" as customer-facing leakage of internal naming. Both are stock webshop chrome. Three different override mechanisms because three different render paths.

**Decided by:** GL (the flag), Claude (the implementation choice).

---

## 2026-04-30 — Variant selectors render INLINE, not behind a dialog

**Superseded implementation detail 2026-05-02:** inline selectors remain, but the template no longer performs per-attribute `frappe.get_all` calls from Jinja. It now uses `get_variant_attribute_options`, consumes `valid_options_for_attributes` for progressive disabling, and renders single-select options as radio controls rather than checkbox inputs.

**Decision:** Override webshop's `item_configure.html` to render attribute selectors inline (chips for ≤8 values, dropdown for 9+) via Jinja iteration over `doc.attributes` × `frappe.get_all("Item Attribute Value", parent=<attr>)`. JS validates selection via `webshop.webshop.variant_selector.utils.get_next_attribute_and_values` and updates Add-to-Cart with the matched variant + price.

**Reasoning:** Webshop's stock pattern is a "Select Variant" button that opens a Frappe Dialog modal — customer perception is "options are hidden." GL flagged this as "missing options." Inline selectors solve the perception problem without rebuilding the underlying variant matching logic.

**Decided by:** Claude (implementation choice).

---

## 2026-04-30 — Webshop Settings managed via setup script, not fixture

**Decision:** `enable_variants=1`, `enable_attribute_filters=1`, `show_attribute_dropdowns=1` set via `scripts/setup/enable_webshop_variants.py` (one-shot, idempotent). NOT fixtured.

**Reasoning:** Webshop Settings is a Singles doctype with many fields Jeff might tweak (Stripe gateway account, checkout behavior flags, recommendations, etc.). Fixturing the whole record would risk overwriting his other config on the next `bench migrate`. Targeted setup script is precise and won't fight Jeff's edits.

**Decided by:** Claude (per fixture-discipline skill — operator-state-sensitive fields stay out of fixtures).

---

## 2026-04-30 — Phase 6 cutover work item: prune `Item Attribute Value` from fixtures

**Decision (forward-looking):** Before Jeff's first deploy after Phase 6 takeover, REMOVE `Item Attribute` from `hooks.py fixtures = [...]` for the operator-state-sensitive subset (especially `latex colors` — 51 values Jeff is most likely to add/rename as his supplier inventory shifts). Document in `NOUPDATE-DRIFT.md`.

**Reasoning:** Per `frappe-fixture-discipline` skill: BBC fixture sync uses `force=True`, which silently overwrites DB records on every migrate. If Jeff renames "Empowermint" via UI and BBC's deploy chain later runs, his rename gets reverted with no warning. Today's risk is zero (no Jeff edits yet); future risk is real.

**Decided by:** Claude (per fixture-discipline skill).

---

## 2026-04-29 (mobile-responsiveness session) — LT design competition synthesis imported as `_resources/design-guide/`

**Decision:** The 2026-04-26 LT design competition output (synthesis dir + 8 approved screenshots) is imported into this project's `_resources/design-guide/` and signposted from `CLAUDE.md` reading order step 6. Original location at `C:\Users\baenb\projects\zoho-locally-twisted\gallery\` will be deleted by GL. Treated as reference inspiration / taste calibration, not as a contract to implement verbatim.

**Reasoning:** Multiple build instances (including this one) failed to find the design contest output because it lived in a separate project directory (`zoho-locally-twisted/gallery/`) outside our LT working tree. Phase 1 PLAN.md line 47 referenced "GL's Opus Competition Redesign concept" with no path. The standard reading order on arrival (CLAUDE.md → HANDOFF.md → PROJECT.md → PLAN.md → decisions log → git log) led every instance THROUGH every artifact, and not one of them pointed at the gallery. Instances either skipped the design reference or worked without it — measurable trust cost on the resulting customer-facing pages.

GL's directive 2026-04-29: *"they should live in our directory as a design guide, not as gospel."* — affirms the inspiration framing and the agency client-isolation rule (each client folder is self-contained for transfer).

**What was imported:**
- `_resources/design-guide/synthesis/` — 4 page TSXs (landing, lookbook, shop, balloon-twisting), layout.tsx, globals.css, 5 markdown docs (rationale, mood, voice, menu, SYNTHESIS-BRIEF, SYNTHESIS-COMPLETE)
- `_resources/design-guide/screenshots/` — 8 approved PNGs (4 pages × 2 viewports) + RENDER-REPORT.md
- `_resources/design-guide/README.md` — framing note (guide, not gospel) + per-file purpose

**What was NOT imported:**
- `take_screenshots.py` (utility specific to the source project's Next.js dev server)
- `WINNER.md`, `BRIEF.md`, `SCORING-RESULTS.md`, designer-1 through designer-7 outputs — the contest provenance was preserved in this entry; the only artifact the build phase needs is the synthesis itself

**Updates to standing artifacts:**
- `CLAUDE.md` "Reference Disposition" — added `_resources/design-guide/` as a canonical resource, reading order step 6 now requires skimming the README + voice/mood/rationale before any frontend work
- `.planning/phases/01-customer-site-and-storefront/PLAN.md` line 47 — replaced vague "Opus Competition Redesign concept" reference with concrete file paths inside `_resources/design-guide/`

**Trust-cost receipt that drove this:** mobile-responsiveness session 2026-04-29. GL had to point me at the contest output explicitly because no signpost existed in the project. Every prior instance had the same gap. The fix is structural — once the README is in the standard reading order, future instances will encounter it during the normal arrival path.

**Decided by:** GL directive 2026-04-29.

---

## 2026-04-29 (guest-cart + Stripe-Link + cascade session) — Path B (true cookie cart) over the cheap Buy-Now-only alternative

**Decision:** Build a real localStorage-backed multi-item guest cart (Path B) rather than removing webshop's Add-to-Cart UI and routing all flows through the single-item buy-now `/checkout?item=...` path (Path A).

**Reasoning:** GL: *"Path B is the only answer. Quality is ALWAYS the answer."* The cheaper Path A would have shipped today but locked the customer experience to one item per checkout. For LT's small-shop tier (sub-$200 themed bouquets, kits) that's acceptable for a single purchase but blocks the natural "I'll add a few things while I'm here" multi-item shopping behavior. Path B took the rest of the session to build but matches what customers expect from any e-commerce site.

**Architecture committed:**
- Cart stored in browser localStorage (versioned schema, in-memory fallback for Safari Private Mode)
- Server-side state created ONCE at checkout submit (Customer + Contact + Address + SO + PR + Stripe Session)
- Webshop's `update_cart` JS function overridden at runtime; `.btn-add-to-cart-list` clicks intercepted in capture phase BEFORE webshop's bubble-phase login redirect
- `/cart` page LT-owned (overrides webshop's via `website_route_rules`, file named `lt_cart.{py,html}` to avoid name collision)
- `/checkout` operates in two modes: buy-now (server-renders single line from `?item=&qty=`) or cart (JS hydrates summary from localStorage)
- `submit_guest_order` accepts EITHER buy-now params OR `items_json` array

**Alternatives rejected:**
- Path A: hide webshop's stock product pages from nav, convert LT `/shop` Add-to-Cart buttons to Buy Now, drop multi-item entirely. (Rejected: loses the natural multi-item UX customers expect.)
- Path C: change `redirect_on_action` to /contact instead of /login. (Rejected: still bounces the customer off the cart, doesn't actually solve the requirement.)
- Modifying webshop directly: `apps/webshop/` is bind-mounted from a gitignored upstream clone; modifications would be wiped on next install/restart.

**Decided by:** GL 2026-04-29. *"Quality is ALWAYS the answer."*

---

## 2026-04-29 (guest-cart session) — Stripe Link disabled at the ACCOUNT level via custom PMC, not per-Session

**Decision:** Disable Link via a custom Stripe Payment Method Configuration on LT's account (`pmc_1TRZH2DfnlZQv66ncb001soG` "LT No Link", `link.display_preference="off"`), passed on every Checkout Session. Do NOT rely on `payment_method_types=["card"]` on the Session.

**Reasoning:** GL hit the Stripe-hosted Checkout page and saw Link "Save info" + "Pay with Bank via Link" + "By paying, you agree to Link's Terms and Privacy" UI rendering on top of the card form. *"I hate Link, it's not going to gatekeep our checkout. 'Pay without link' is not going to be forced upon anyone."*

I shipped `payment_method_types=["card"]` first; GL caught it ("straight to link again"). Rendered the page in Playwright, confirmed Link UI persisted regardless of the Session-level restriction. Per Stripe documentation and a knowledge gem in the `stripe:stripe-best-practices` skill: *"Link is controlled through the Dashboard. Create a custom payment method configuration with Link off."*

**Pattern:**
1. Create a top-level PMC on the account: `stripe.PaymentMethodConfiguration.create(name=..., card={"display_preference": {"preference": "on"}}, link={"display_preference": {"preference": "off"}})`
2. Pass `payment_method_configuration: <pmc_id>` on every Checkout Session
3. Verify by rendering the page in Playwright and grepping for "Link" — the SDK Session response is misleading (it'll say `payment_method_types: ["card"]` even when Link UI is showing)

**Side effects accepted:**
- No Klarna / Affirm / Cash App Pay / Bank-via-ACH (could be added by enabling those individually on the PMC if GL ever wants them)
- Apple Pay + Google Pay still work — they're card wallets, surface automatically on supported devices, independent of Link

**Constraint discovered:** PMC parent-child API has ownership rules. Pre-existing platform-managed PMCs on the account cannot be modified or used as parents for child configs ("Child configurations can only be created by the parent configuration's owner"). Workaround: create a NEW top-level PMC without specifying parent — succeeds because the account owns it.

**Decided by:** GL 2026-04-29. The PMC pattern was implementation-level; the "kill Link entirely, sign-in is optional" product rule came from GL.

---

## 2026-04-29 (cascade session) — ERPNext "everything cascades" pattern wired in `/payment-success`

**Decision:** Beyond marking PR paid, `/payment-success` now also: creates Sales Invoice from SO (idempotent), sends transactional receipt email to customer, sends operator notification to `locallytwisted@gmail.com` (overridable via `site_config.lt_operator_email`), sends welcome email if first-time customer. All four wrapped in try/except so a backend reconciliation glitch never blocks the customer's `/thank-you` redirect.

**Reasoning:** GL's framing: *"This is one of the things we need to utilize HEAVILY with this software. That's why I picked it."* Per the discussion-tier ambition, every paid order should propagate into ERPNext's accounting + comms + analytics surfaces automatically — not as discrete subsequent tasks. The cascade is the foundation for "one source of truth" customer records.

**What cascades automatically post-decision:**
- Customer dedup at /checkout (3-case: returning / Contact-from-Lead / fresh) — closes the orphan-customer hole
- SO submit → ERPNext's standard chain (Customer record updated, address attached)
- PR.set_as_paid → Payment Entry (auto via ERPNext) → posts to AR + Bank account in GL
- SI submit → posts to Sales income + Tax payable in GL
- Each email send → Communication record on SO/Customer (auto via `frappe.sendmail` reference_doctype/name)

**What's deliberately deferred:**
- Calendar Event from SO delivery_date — Phase 3 (operator workflow)
- Project + Task from big-ticket SOs — Phase 3
- Stock movement / Delivery Note — Phase 4 (when stock-tracking turns on; currently `allow_items_not_in_stock=1`)

**Idempotency principle:** Every email helper checks for existing Communication with the exact subject before sending. Means: backfill is safe, webhook double-fire is safe, retry is safe. Same principle for SI: check existing Sales Invoice Item rows for this SO before creating.

**Trap avoided:** wkhtmltopdf-in-Docker. Set `mute_email = True` on Sales Invoice and never pass `attach_print` on `frappe.sendmail`. The HTML body of the email IS the receipt; production should configure `host_name` in `site_config.json` to a docker-internal hostname so PDF rendering works, but for the demo flow the HTML email is sufficient.

**Operator email recipient:** Hardcoded constant `OPERATOR_EMAIL = "locallytwisted@gmail.com"` in `payment_success.py`, with override path via `frappe.conf.get("lt_operator_email")`. When LT routes to a different inbox, set via `bench --site frontend set-config lt_operator_email <addr>` rather than editing the constant.

**Decided by:** GL 2026-04-29. The cascade architecture, the file structure, and the idempotency pattern are all implementation choices; the "utilize HEAVILY" ambition came from GL.

---

## 2026-04-29 (Stripe migration session) — Migrate Charges API → Checkout Sessions NOW, not in Phase 4

**Decision:** The migration from Frappe's bundled Stripe Charges API integration to Stripe Checkout Sessions (Stripe-hosted page) happens BEFORE the demo to Jeff, not in Phase 4 hardening. The previous instance had logged this as Phase 4 debt (entry below 2026-04-29 "Frappe payments app uses legacy Charges API"); GL pulled it forward when they saw the customer experience.

**Reasoning:** GL hit `/stripe_checkout` (Frappe's bundled card form, legacy Charges API) during a real test purchase and stopped. *"This looks unprofessional. I don't trust it."* Compared against the Odoo `/shop/cart` → `/shop/address` → `/shop/payment` flow which had branded LT chrome + persistent order summary throughout. The Frappe form had the LT header but a barebones unbranded panel below — no order summary, no item visual, no security indicators, no "Powered by Stripe" badge.

The professionalism gap is bigger than the dev-effort cost. Jeff will react the same way GL did. Migration cannot wait.

**What it commits us to:**
- `submit_guest_order` returns a `https://checkout.stripe.com/c/pay/cs_test_...` URL instead of Frappe's `pr.payment_url`
- Customer sees Stripe's hosted page with their full production UI: dynamic payment methods (Card / Klarna / Affirm / Cash App Pay / Bank / Link), real-time card validation, "Powered by Stripe" footer, security badges
- URL bar reads `checkout.stripe.com` — recognized trust signal
- Sales Order + Payment Request creation stays as-is (auditable record); only the customer-facing URL changes
- Webhook handler shipped at `apps/locally_twisted/locally_twisted/payments/stripe_webhook.py` (signature-verified, idempotent) for production reconciliation
- Server-side reconciliation on `/payment-success` route makes webhook OPTIONAL for the demo flow — the moment a customer lands after Stripe success, we retrieve the session via Stripe API, verify `payment_status == 'paid'`, and call `pr.set_as_paid()` synchronously. Idempotent: if the webhook also fires, it no-ops because the PR is already Paid.

**Alternatives considered:**
- Polish the existing Frappe `/stripe_checkout` template via CSS overrides (rejected — customer still doesn't see `checkout.stripe.com`, still legacy Charges API, still no Apple Pay / Link / 3DS, looks "homemade" no matter how well styled)
- Stripe Payment Element (embedded) instead of hosted Checkout (rejected for now — keeping customer on our domain is nice but the trust signal of `checkout.stripe.com` in the URL bar is the bigger win for LT's customer base of one-off occasional buyers)

**Decided by:** GL 2026-04-29, after seeing the side-by-side comparison (Odoo's flow vs. our Frappe form vs. Stripe's hosted page).

---

## 2026-04-29 (Stripe migration session) — `/payment-success` overridden via website_route_rules

**Decision:** `/payment-success` is overridden in our app (not Frappe's bundled template). Custom controller at `apps/locally_twisted/locally_twisted/www/payment_success.py` handles two paths: Stripe Checkout Session redirect (`?session_id=cs_test_...`) and a legacy fallback for the Frappe payments redirect URL.

**Reasoning:** Frappe's `payments` app has TWO upstream bugs that converge on this route:
1. `apps/payments/.../stripe_settings.py:272` unconditionally appends `?redirect_to=None` (literal "None") to the redirect URL even when the URL already has `?` — produces a malformed double-`?` URL
2. The bundled `/payment-success` controller calls `frappe.get_doc("Payment Request", ...)` under the GUEST session — 403s because Payment Request is restricted

We can't patch upstream cleanly: `apps/payments/` is bind-mounted from a gitignored upstream clone. The agency rule "work WITHIN Frappe, don't fight it" still applies — the right move is to use Frappe's documented mechanism (`website_route_rules` in `hooks.py`) to claim the route in our app.

**The override does:**
- Strips any `?redirect_to=None` tail off the `docname` form_dict value (defends against the upstream URL malformation if it ever fires)
- Verifies the linked `Integration Request` is `Completed` OR the Stripe session reports `payment_status == 'paid'` — proves the charge actually succeeded; defends against guessing PR/SO names
- Looks up the SO with elevated read perms (we never read PR as guest)
- Marks the PR Paid synchronously (creates Payment Entry)
- Redirects to `/thank-you?order=<so_name>` (already exists, works for guests)

**Trade-off:** when (if) Frappe fixes the upstream bugs, our override is still useful — it gives guests a clean post-checkout landing without exposing Payment Request, and handles `session_id`-based redirects that the Frappe controller doesn't.

**Decided by:** This instance, 2026-04-29, after debugging GL's `/payment-success?...?redirect_to=None` 403 report.

---

## 2026-04-29 (Stripe migration session) — Each LT integration uses LT's own Stripe account, not BBC's

**Decision:** LT's customer-facing payments flow through LT's own Stripe account. BBC's Stripe account is only ever used to bill GL's clients for agency work — never to process customer charges to LT (or any other BBC client).

**Reasoning:** This is the agency-wide standard codified during the same session at `Built_by_Cameron/built-by-cameron-decisions.md`. For LT specifically, the previous instance configured Stripe Settings 'Test' from `.env` keys provided by GL. Those keys ARE LT's. The Stripe CLI's stored auth (via `stripe login`) is a SEPARATE auth context — it can be (and currently is) authed to BBC for development convenience without affecting ERPNext's runtime.

**Practical implications:**
- ERPNext's Stripe Settings 'Test' uses LT's `pk_test_...` and `sk_test_...` from `.env` — verified by the Stripe Checkout page rendering the line item under LT's account name
- The Stripe Dashboard's public business name shown on the Checkout page comes from LT's account profile (currently "Locally twisted llc" — rename to "Locally Twisted" when Jeff's available for 2FA)
- For Stripe CLI tasks (e.g., webhook listening), use `stripe listen --api-key $SK_TEST_FROM_ENV` to point at LT's account WITHOUT needing CLI auth — bypasses the 2FA blocker
- At Frappe Cloud cutover (Phase 6), LT's live mode keys go in `.env` and Stripe Settings 'Live'; webhook endpoint is configured in Stripe Dashboard against LT's account; signing secret goes in production `site_config.json`

**Decided by:** GL 2026-04-29, in response to my mistakenly assuming BBC's CLI auth was the right credentials. *"the Built by Cameron account is for my personal business not locally twisted. they have their own account. we need to keep them separate."*

---

## 2026-04-29 (Stripe + guest checkout session) — Option B (true guest checkout) over Option A (silent User account)

**Decision:** No User account is created during checkout — ever. Guest checkout creates only Customer + Contact + Address + Sales Order + Payment Request. The customer is identified by email; they cannot log in to a portal because no User record exists for their email.

**Reasoning:** GL initially greenlit Option A (silently create User with `send_welcome_email=0` so the customer experiences "guest checkout" without a registration form, but a User record exists). I drafted a research brief at `research/expedition-guest-checkout-legal/research-brief.md` to scope the legal compliance — 50 state privacy laws, CAN-SPAM, UCPA, the silent-account-creation gray area. GL read the framing and pulled the cord: *"Oh, this is too complex legally. We cannot deal with that. There needs to be a genuine guest checkout. I'm not dealing with this research being wrong."*

Option B is well-trodden e-commerce territory: collect customer data for order fulfillment + send transactional receipt + don't market without explicit opt-in. No account-creation gray area. No silent-User state to defend in court. The legal surface stays small and uniform across all 50 US states.

**Trade-off accepted:** customer cannot self-serve their order history through a portal. Communications and receipts go through email only. For LT's customer base (one-off occasional sub-$200 buyers), this is fine — most never come back to a portal anyway.

**Decided by:** GL.

---

## 2026-04-29 (Stripe session) — Frappe payments app uses legacy Charges API; accepted for test demo, swap before live launch

**Decision:** For the demo to Jeff and through Phase 1, use Frappe's built-in Stripe integration as-is. Do not refactor to Stripe Checkout Sessions or Payment Intents during the customer-site phase.

**Reasoning:** Frappe's Stripe controller at `apps/payments/payments/payment_gateways/doctype/stripe_settings/stripe_settings.py:create_charge_on_stripe` calls `stripe.Charge.create()` — the LEGACY Charges API. Per the `stripe-best-practices` skill (invoked this session): *"Never recommend the Charges API. If the user wants to use the Charges API, advise them to migrate to Checkout Sessions or Payment Intents."* The reasons modern Stripe pushes off Charges:
- No 3DS / Strong Customer Authentication support (will fail in EU; may fail with US issuers requiring 3DS)
- No dynamic payment methods (no Apple Pay, Google Pay, Link auto-injection)
- No fraud signals as rich as PaymentIntents

For test mode + a US-only customer base in Utah at sub-$300 transaction sizes, Charges API still works and serves the demo. **For production hardening (Phase 4 — Stripe + invoicing slice), this gets fixed first.** Either:
- Build a custom controller in our app that uses CheckoutSessions, register it via `override_payment_gateway_controller` (or wrap the existing Stripe Settings via subclass)
- Wait for Frappe community to update the payments app and rebase

**Alternatives considered:**
- Build CheckoutSessions integration NOW, bypassing the payments app entirely — too much work for the demo timeline; would require reimplementing the Sales Order → Payment Request → Payment Entry plumbing
- Use Stripe Payment Links per product, sidestepping ERPNext checkout — loses the "ERPNext is doing the work" framing for the demo

**Decided by:** This instance, ratified by demo timeline. Logged as known debt for Phase 4.

---

## 2026-04-29 (Stripe session) — Order type "Shopping Cart" + flags.mute_email pattern for guest-checkout Payment Requests

**Decision:** Sales Orders created via `submit_guest_order` MUST have `order_type = "Shopping Cart"`. Payment Request submission MUST set `pr.flags.mute_email = True` AND a manual `pr.set_payment_request_url()` call after `pr.submit()` to populate `payment_url`.

**Reasoning:** Frappe's Payment Request `on_submit` hook (apps/erpnext/...payment_request.py:215) calls `send_email() → attach_print() → wkhtmltopdf` regardless of test/live mode. Inside the LT Docker stack, wkhtmltopdf cannot reach `localhost:8081` from the container's network namespace → `ConnectionRefusedError`. Both `order_type="Shopping Cart"` (line 211) AND `flags.mute_email` short-circuit `send_mail` to False, skipping the email/PDF render.

But: `set_payment_request_url()` is INSIDE the same `if send_mail:` branch. Suppressing the email also suppresses URL generation. So we must call it manually after submit, then `pr.reload()` to refresh `payment_url`.

This pattern is documented inline in `apps/locally_twisted/locally_twisted/www/checkout.py` for the next instance.

**Long-term fix (deferred):** configure `host_name` in `site_config.json` to a docker-internal hostname so wkhtmltopdf can reach back to the site without the workaround. Until that's done, every PDF-generating operation in the container will need the same pattern.

**Decided by:** This instance, after debugging three failed smoke tests and reading the Frappe payments source.

---

## 2026-04-28 (BTFP restructure session) — Background warmer (`--lt-near-white: #fffcfc`) + header matches footer blue

**Decision:** `--lt-near-white` token changed from `#FBFBFB` (cold grey) to `#fffcfc` (warm pink-tinted off-white). `.lt-header` background changed from `var(--lt-white)` to `var(--lt-soft-blue)` (the same color as `.lt-footer`). `.lt-footer__bar` (copyright bar) changed to use `var(--lt-near-white)` instead of `rgba(26, 26, 26, 0.04)` — establishing `--lt-near-white` as the new "base white" token.

**Reasoning:** GL: *"the main white background is so white it's bluish and/or gray... Try fffcfc for the main background."* The chrome (header) being matched to the footer creates a "wrap" feeling — the page is bookended by the same brand color. The copyright bar uses the new warm white to break visually from the soft-blue footer band above it.

**Tokens after this decision (for the next instance to know):**
- `--lt-white: #FFFFFF` — pure white, used for cards and panels that need to pop
- `--lt-near-white: #fffcfc` — warm base white, used for body / off-white sections / copyright bar
- `--lt-soft-blue: #C3DCF3` — the brand soft blue, used for header + footer band
- `--lt-blush-tint: #FBF5F2` — used for hero bands

**Decided by:** GL.

---

## 2026-04-28 (BTFP restructure session) — Aqua + green ribbons rejected; blush + soft-blue kept

**Decision:** When adding decorative thin ribbons (full-bleed colored bands as visual separators), use ONLY blush (`.lt-band--blush`) and soft-blue (`.lt-band--soft-blue`). Aqua (`.lt-band--aqua`) and lime/green (`.lt-band--lime`) are not used in the LT visual identity.

**Reasoning:** GL specified: *"The Aqua ribbon and green ribbon have to go."* The brand palette includes those colors but they don't serve the calm/celebratory tone of the LT site. The blush + soft-blue alternation matches the brand identity and the customer base (event clients, parents, corporate event coordinators).

**Decided by:** GL.

---

## 2026-04-27 (LookBook → Portfolio rename) — Menu name changed; URL /lookbook stays

**Decision:** The navigation link previously labeled "LookBook" now reads "Portfolio" in both desktop and mobile menus. Same homepage CTAs that read "lookbook" now read "portfolio." The URL path `/lookbook` is unchanged — clicking "Portfolio" goes to `/lookbook`.

**Reasoning:** GL: *"I prefer 'Portfolio' over 'LookBook' or 'Gallery.' Jeff charges art prices so he might as well act like an artist haha. No he really is."* "Lookbook" is physical-book terminology; "portfolio" matches an artist's positioning and Jeff's actual price tier ($400+ custom installations, $130/$115 hourly per artist).

**URL trade-off:** keeping `/lookbook` avoids 301 redirect chains and any SEO disruption (though the page wasn't getting indexed yet). When Slice 7 is iterated again, GL can reconsider renaming the route to `/portfolio` with a redirect.

**Decided by:** GL.

---

## 2026-04-27 (homepage build session — late) — Bouquets added as 6th customizable category for the future Design Studio

**Decision:** Bouquets join Balloon Arches, Columns & Pillars, Organic Garlands, Picture Perfect Backdrops, and Balloon Drops as the customizable categories that will eventually get the interactive "Design Studio" experience.

**Reasoning:** GL realized 2026-04-27 that bouquets are also customizable in Jeff's actual business (size of bouquet, number of balloons, mylar add-ons, themed toppers, etc.). The original 5-category list came from the approved Odoo `s_lt_categories` snippet which didn't include bouquets explicitly. Adding it to the future Design Studio scope; the homepage Custom Creations grid stays at 5 for now until the Lookbook surface (Slice 7) is the right place to surface the 6th.

**Decided by:** GL.

---

## 2026-04-27 (homepage build session) — Reviews carousel chosen over expanded client logo crawl as primary social proof

**Decision:** The reviews block on the homepage uses a horizontal-scrolling carousel of full review cards (currently 19 real Google 5-star reviews × 2 for seamless loop = 38 cards in the DOM). The client logo crawl stays at the bottom of the page but is now visually subordinated to the reviews.

**Reasoning:** GL's instinct: "He's been in business 28 years; the man can have a carousel of praise that matters more than the carousel of businesses at the bottom." For a high-touch event-decor business, customer *words* persuade prospective clients more than corporate *logos*. Logos prove "we worked with X"; quotes prove "X said this thing about working with us." The latter is harder to fake and harder to ignore.

**Implementation:** Same CSS marquee pattern as the client crawl (overflow:hidden + flex track + animation:translateX + duplicate set with aria-hidden + edge-fade mask + pause-on-hover) but with full review cards (320px wide, fixed). 360s for full loop so cards have reading time. Reduced-motion users see all cards stacked statically.

**Alternatives considered:** Single-card fade carousel (simpler, less visible content); page-based fade (5 cards visible, fade to next 5); arrow-controlled manual carousel (more complex). Horizontal marquee won because it matches the existing client crawl pattern and lets the user pause-on-hover to read whichever card catches their eye.

**Decided by:** GL.

---

## 2026-04-27 (homepage build session) — Twisting & Face Painting moved to bottom of homepage

**Decision:** The Balloon Twisting & Face Painting spotlight section moved from mid-page (after Recent Celebrations) to the bottom of the homepage (after the Closing CTA).

**Reasoning:** Per GL's strategic frame: balloon twisting and face painting are Jeff's love but are not the high-margin work and don't grow the business. Big-event corporate/wedding/birthday work is where the revenue is and where the business can be set up for sale. The homepage should lead with the lookbook-forward shape (hero → reviews → categories → recent work) and only mention the live-services side at the bottom for visitors specifically looking for it. Quote: *"That is not where this is right now. I do not think people who buy a balloon event company want to deal with a face-painting company run by white Mormon women who are all very self-important."*

The `/balloon-twisting-and-face-painting` page itself is still a first-class surface (already built); just no longer mid-homepage.

**Decided by:** GL. Strategic frame for the rebuild.

---

## 2026-04-27 (homepage build session) — `/book` moved from Phase 2 → Phase 1 (Slice 10)

**Decision:** The `/book` form (the deep 45-field inquiry intake) is now part of Phase 1 (Customer site), specifically Slice 10. It was originally Phase 2 (Lead Intake).

**Reasoning:** The lookbook-forward shape requires `/book` to be live on day one. Every "Tell us about your event" CTA on the site (hero, closing, future service-category pages, future Color Chart, future Lookbook) points at `/book` as the inquiry conversion path. Without `/book`, the inquiries go nowhere. Phase 1 cannot be demoed to Jeff without the conversion path working.

**Phase 2 reframed:** Phase 2 is now "form-handling depth" — Contact dedup logic, customer acknowledgment email automation, loud-failure compliance audit across all forms, monitor alerts. The forms exist in Phase 1; the depth around them lives in Phase 2.

**Decided by:** This instance, ratified by the lookbook-forward direction GL had already locked. ROADMAP.md and PLAN.md updated to reflect.

---

## 2026-04-27 (homepage build session) — About page deferred until Jeff is ready

**Decision:** No About page or About snippet ships in v1 of the homepage. Contact page covers the basics. The previously-coded "About" section on the homepage was removed.

**Reasoning:** Jeff hasn't approved the About copy. GL's frame: *"We will make an about page when Jeff is ready. We don't need to pressure him. There's a contact page. No about section, no about page for now. It doesn't need to ship with v1."* The synthesis design instances had filler "Built by hand. Built by people who love this." copy; that's voice-OK but not GL-confirmed about the actual team. Better to omit than to invent.

**Decided by:** GL.

---

## 2026-04-27 (homepage build session, earlier) — Site shape: lookbook-forward + small shop sidebar

**Decision:** LT's website shape is portfolio/lookbook-forward, with a small e-commerce sidebar for sub-$300 pre-configured items. Configurator UI for custom arches/columns/etc. is rejected as a checkout flow but accepted as a future "Design Studio" inquiry-capture experience.

**Reasoning:** Surveyed 9 live competitor sites in the events-decor / luxury-floral / balloon-decor category (`_resources/competitor-survey-2026-04-26.md`). Five patterns emerged across all 9: (1) every high-dollar custom item routes through consultation/quote, never a configurator; (2) portfolio is a nav item, not a homepage feature; (3) shops, when they exist, are sidebars, never headlines; (4) "Inquire" beats "Buy" above ~$30; (5) social proof tier (testimonials → Google reviews → press) matches business tier.

LT's revenue concentration is in big-ticket events ($400-15,000 custom arches, walls, drops, garlands) sold through pitch decks → invoices → phone calls. Customers don't configure $400+ on a website. The "Design Studio" concept resolves Jeff's "customers want to see colors and pick options" instinct without the wrong checkout flow: pick mood + colors + scale → output is an inquiry, not a cart.

Full rationale: `.planning/decisions/site-shape.md`. Cover story for Jeff: *"We couldn't use Odoo, so we had to rebuild on a different program. While I was rebuilding, I looked at how every other custom-balloon and event-decor company in our tier is structured today — Partistry, Balloon Emporium, the wedding florists. None of them sell custom installs through a checkout flow."*

**Decided by:** GL, with concurrence from this instance after competitor survey.

---

## 2026-04-26 (later, after Slice 2 + accessibility + contact build) — Platform direction RESOLVED: stay Frappe-native

**Decision:** LT's customer-facing website stays inside Frappe / Frappe webshop. The platform-direction question that the previous instance left open at session end is now answered by demonstration.

**Reasoning:** The codified Frappe-native technique passed three independent visual gates this session:

1. **`/accessibility` static portal page** — built end-to-end as `apps/locally_twisted/locally_twisted/www/accessibility.{html,py}`, GL confirmed: *"the content in the middle of the page looked good!"*
2. **Slice 2 chrome (header + footer)** — Jinja partial overrides at `templates/includes/{navbar,footer}/`, replaced Frappe's defaults with the approved Odoo two-tier desktop / single-row mobile structure. GL iterated on logo size, footer centering, footer padding, and 3-column-on-mobile spec; technique held under those iterations. GL confirmed: *"so far so good! It's getting better."*
3. **`/contact` form-bearing portal page** — full pipeline working: AJAX form → whitelisted controller → Lead + linked Communication created, zero console errors, smoke test confirmed `CRM-LEAD-2026-00001` persisted with the message body. GL confirmed: *"Holy shit! You did it!"*

The two prior failed attempts on this stack failed by *technique*, not *architecture*. The codification work earlier this session (`frappe-portal-implementation.md`, `frappe-conventions.md` updates, `license-isolated-app-architecture.md`, plus the `Built_by_Cameron/.claude/capabilities/meals/build-frappe-portal-page.md` meal) made the right technique discoverable and enforceable. The architecture was always sound.

**What this commits us to:**
- All Phase 1 customer-facing surfaces continue on Frappe + webshop. The remaining slices (refund-policy, FAQ, BTFP service page, products browse, product detail, cart, checkout) build on the meal pattern.
- Phase 2 (`/book` lead intake form) follows the same form-bearing portal page shape as `/contact`, with the larger Lead schema.
- Phase 4 (Stripe via webshop's payments-app integration) stays in scope; webshop's bundles are now compiled (Node + yarn installed in the backend container) so storefront pages render correctly.
- The agency-tier "two-app split" question (`agency_platform` + `<client>_connector`) stays open as a future architectural decision per the agency decisions log; not blocking for LT's current Phase 1 work.

**What's NOT committed:**
- The platform decision is *Frappe-native for the customer-facing website*. It does NOT preclude a future pivot if a specific page or workflow proves Frappe-impossible. The off-ramp condition GL set ("if Frappe can't deliver this visual + UX bar, GL pivots away from ERPNext") still applies — it just hasn't fired yet.
- Newsletter signup, Google Maps embed, modal-with-auto-redirect, and a few other polish items were deliberately skipped on the contact page and are documented as future work; they don't change the platform decision.

**Decided by:** GL by demonstration. The contact-page success was the implicit affirmation; this entry makes it written.

---

## 2026-04-26 (post-session research) — License posture clarified: ERPNext is GPL-3.0, Frappe is MIT, AGPL concern was Builder-specific (not installed)

**Decision:** The expedition's Flag 8 raised an AGPL concern. Research + direct verification against `apps/<app>/license.txt` in the running LT stack establishes the actual license set:

| App | License | Notes |
|---|---|---|
| frappe (Framework) | MIT | Custom code on Frappe sits closest to MIT territory |
| erpnext | GPL-3.0 | Derivative-work exposure if our app derives from ERPNext internals |
| webshop | GPL-3.0 | Same |
| payments | MIT | No copyleft pressure |
| locally_twisted (custom) | MIT | License placeholder in license.txt — owner field needs filling |

**The AGPL claim was specifically about Frappe Builder** (a separate optional app) — NOT about ERPNext or Frappe Framework core. Builder is not installed on LT. The AGPL concern only re-applies if a future BBC client adopts Builder; it does not apply to LT's current stack.

**Reasoning:** the expedition's Flag 8 left this ambiguous, and a downstream reading could have absorbed "ERPNext / Frappe might be AGPL." Direct verification corrects that. Our Build → Sell → Transfer model deals with GPL-3.0 derivative-work analysis (a more conventional, well-documented legal posture), not the AGPL network-use clause.

**Operational consequence for LT specifically:**
- Continue building `locally_twisted` as a Frappe-first custom app
- Interact with ERPNext / Webshop via documented hooks, public APIs, DocType reads, NOT by editing core or subclassing internals
- When Phase 4 (payments) wires up Stripe, that goes through the `payments` app's `Payment Gateway Account` DocType (MIT-licensed surface)
- When the catalog seeds, query through Webshop's `Website Item` API (GPL-3.0 read), don't copy Webshop internals into our app

**Open architectural question for the agency tier (not LT's call alone):** whether to split custom code into `agency_platform` (reusable) + `locally_twisted_connector` (thin adapter) for stronger license isolation. Tracked at `Built_by_Cameron/built-by-cameron-decisions.md` 2026-04-26 entry "License matrix verified..." Finding 3.

**Decided by:** Perplexity research surfaced the license question; verification done by reading license files directly in the running LT container 2026-04-26. Codified at agency-tier conventions doc.

---

## 2026-04-26 (session end) — Platform-direction question is OPEN; landing build approach was wrong on three counts

**Decision:** No platform direction decided this session. The question is now explicitly on GL's desk for the next conversation.

**The question, verbatim from the synthesis:** *Do you want to keep building the customer-facing website inside Frappe + webshop, OR explore a simpler front door (WordPress / Webflow / Next.js) with ERPNext quietly running the back office?*

**Reasoning:** A full expedition (3 source-separated researchers + convergence + devil's advocate + GL Proxy) found:

1. The Frappe theme ecosystem is THIN. No turnkey polished customer-facing themes exist. Every Frappe-built site that looks polished was built by Frappe employees for Frappe properties (frappe.io, fossunited.org, cloud.frappe.io). No documented case of a small business successfully running a polished customer-facing site on Frappe was found.
2. Two LT homepage builds have failed in two consecutive sessions. Both failed by the same pattern: invented placeholder copy + band-aid CSS overrides + declaring "done" off DOM facts before GL opened the page in a real browser. The architecture wasn't the problem; the technique was.
3. The Phase 1 off-ramp condition GL set ("if ERPNext can't deliver this visual + UX bar, GL pivots away from ERPNext") is exactly what the Devil's Advocate questioned. It has not been answered consciously.

The GL Proxy flagged the convergence's tendency to route past the platform question and steelman the Frappe path. This decision entry surfaces it as the open question it is.

**What's known:**
- Frappe + custom Jinja + custom CSS will work eventually but requires substantial custom CSS work and Jeff cannot maintain it post-handoff.
- WordPress + WooCommerce has the most off-the-shelf plugins for service booking + ecommerce but is the most-hacked CMS in the world (security maintenance burden).
- Webflow is designer-first and Jeff can edit pages himself, but its ecommerce is light for complex variant catalogs.
- Next.js + headless commerce (Vercel Commerce, Saleor, Medusa.js) gives best design freedom and best SEO but is Cameron-maintained forever and adds a sync layer to ERPNext.

**Alternatives considered:** Keep building on Frappe without surfacing the question (rejected — would repeat the two-session failure pattern). Pre-decide for GL based on convergence (rejected — the choice depends on trade-offs only GL can weigh). Run more research first (rejected — the expedition was thorough; what's missing is GL's input, not more data).

**Decided by:** No decision yet. GL is collecting more information. They asked specifically about webshop architecture, SEO/GEO/AEO of decoupled, service-scheduling needs, GitHub catalog import patterns, and whether Next.js works for ecommerce. All answered in the session transcript before this entry was written. They want to compare Vercel Commerce demo + Frappe Builder + Webflow templates side by side before deciding.

**Status:** PENDING. Blocks all build tasks (#11, #12, #13, #14 in the session-end queue). Next instance must read `research/expedition-frappe-theme/synthesis.md` and confirm direction with GL before any visible build work resumes.

---

## 2026-04-26 (session end) — Approved Jeff content is NEVER invented — pull from Odoo XML or live locallytwisted.com

**Decision:** All customer-facing copy on the LT site comes from one of two authoritative sources, never from instance imagination:
1. **`C:/Users/baenb/projects/locally-twisted-odoo/addons/locally_twisted/views/`** (XML view files in the local Odoo project) — the most recent Jeff-approved Odoo update, captured verbatim in `research/expedition-frappe-theme/ground-truth-findings.md`. Per CLAUDE.md, this is authoritative for the new build.
2. **`https://locallytwisted.com/`** (the live WordPress site Jeff still uses) — actively in front of customers today, captured verbatim in `research/expedition-frappe-theme/web-scout-findings.md`. The two sources diverge on hero copy, social icon count (3 vs 4), and credential framing ("since 1998" vs "Over 22 years"). GL has NOT yet picked which is "the" version.

**Reasoning:** Two consecutive instances invented placeholder copy ("Make Your Celebration Unforgettable", "Three services. One promise: you get the moment, we handle the magic", "Ready to plan something unforgettable?") when the actual approved copy was sitting on disk. GL caught both. The trust cost was real both times. The pattern needs to die.

**What this means in practice:**
- Before writing any text that will appear on a customer-facing page, READ the Odoo XML or scrape the live site and use the actual content.
- For copy that needs to be slightly adapted to fit a new layout, do the adaptation but preserve voice + key phrases verbatim.
- If neither source has copy for a new surface, ASK GL — do not invent.

**Open sub-decision for GL:** Which of the two sources is "the" approved version when they disagree? Specifically:
- Hero copy: "Utah's Balloon Specialists" / "Making celebrations unforgettable since 1998" (Odoo) vs "Make Your Party POP!" / "Anything you imagine, we can shape into reality" (live site)
- Social icons: 3 (Facebook, Instagram, Pinterest — Odoo) vs 4 (+ Twitter — live site)
- Credentials: "since 1998" / 28 years (Odoo) vs "Over 22 years" (live site)
- Tagline: "Utah's Balloon Specialists since 1998." (Odoo) vs different framings on live site

**Decided by:** Lessons-learned pattern from this session + GL's explicit "did you make it up?" callout. The decision becomes a standing rule once GL confirms which source is authoritative.

---

## 2026-04-26 (Web Page tabs finding) — Per-page interactivity belongs in the DocType, not a custom Web Template

**Decision:** All per-page interactivity (JavaScript, CSS, server-side data fetching) for one-off pages goes into the corresponding `Web Page` record's native tabs (`javascript`, `css`, `context_script`, `header`), NOT into a custom Web Template or a custom controller. Custom Web Templates are reserved for layouts that genuinely need cross-page reuse.

**Reasoning:** GL surfaced this 2026-04-26 after noticing that the previous instance's homepage Web Page record (`/app/web-page/locally-twisted`) used only `main_section` (Rich Text) and ignored the Script + Style + Page Builder tabs. Reading the actual `Web Page` DocType schema confirmed the framework natively provides:
- `javascript` (Code field) — per-page JavaScript at page load
- `css` (Code field) + `insert_style` (Check) — per-page CSS
- `page_blocks` (Table) — Page Builder for layout
- `header` (HTML editor) — custom hero HTML
- `context_script` (Code, Python) — server-side data fetching that injects into the Jinja context BEFORE render
- Plus full meta-tag, breadcrumb, and sidebar control

**Concrete impact on this project:**
- The pricing calculator on the BTFP service page was classified as the only tier-4 piece in Phase 1 (per the v2 website-page-index.md). It now collapses to tier 1: Page Builder for static layout + `javascript` field for math + `css` field for styling. No custom Web Template, no hooks, no app code.
- Phase 1 may have **zero tier-4 pieces**. Color swatches are the only remaining candidate, and even that may be reachable via `context_script` + a custom field on `Item Attribute Value`.
- Future page builds (landing, BTFP, contact) all use the right tabs from the start. The previous instance's content-field-only pattern is a documented anti-pattern.

**Alternatives considered:**
- Custom Web Template per interactive page (rejected — strictly worse than using the DocType's native fields; more files, more breakage surfaces, no benefit).
- Per-page `<script>` tags injected into `main_section_html` (rejected — works but harder to maintain than the dedicated `javascript` field; loses the structural separation Frappe provides).
- Custom controller per page (rejected — `context_script` does this natively without registering a controller).

**Generalizable to agency tier:** This decision motivated promoting "System-native first" to a standing principle at the top of `Built_by_Cameron/.claude/capabilities/recipes/frappe-conventions.md`, with a concrete rule: "before writing custom code, read the relevant DocType's full schema." Every BBC client benefits.

**Decided by:** GL directive 2026-04-26 ("you can use java on these pages!") + framework verification by reading the Web Page DocType schema.

---

## 2026-04-26 (webshop install + framework study) — Webshop installed durably; "work within Frappe" is the standing principle

**Decision:** Three reinforcing decisions taken in one session.

1. **`frappe/webshop` and `frappe/payments` are installed on the LT site as durable infrastructure.** Historical install path used host clones plus bind mounts. Current runtime supersedes that with the custom image: payments and webshop are image-owned, and `scripts/setup/install_webshop.py` is fallback/history only. Phase 1 Slices 7-9 (products + cart + checkout) and Phase 4 (payments) are unblocked.

2. **"Work within Frappe, don't fight it" is the standing principle for all UI/template work.** GL directive 2026-04-26: *"I don't want to fight Frappe or ERPNext and their code. I want to work within it."* Operationalized as: use Jinja partial overrides (templates/includes/...) as the primary surface for header/footer/page customization; use `web_include_css` (loads after the bundle) or `website_theme_scss` (compiles into the bundle) for theme CSS; refuse `!important` chains as the receipt of fighting the framework; use Webshop's existing hooks for cart/checkout customization rather than replacing the cart pipeline.

3. **The `.web-footer` height "constraint" was never a framework constraint.** Reading `apps/frappe/frappe/public/scss/website/footer.scss` in the running container confirmed there is no `max-height` rule. The previous instance's observation came from `lt-theme.css`'s own `!important` chain interacting with the body's flex-column sticky-footer pattern. The `.web-footer` block in `lt-theme.css` (lines 477-503) and the related `.web-footer ul/li/footer-group` blocks (505-526) should be removed before the Slice 2 redo. Documented in `lessons-learned.md` 2026-04-26 entry (RESOLVED) + agency `frappe-conventions.md` "Verified against source" appendix.

**Reasoning:** Webshop install was already a known requirement (per the prior Slice 2 build session's queue + the agency capability). The install proved: (a) `bench get-app` requires `--skip-assets` to avoid the Node-not-in-image error; (b) `payments` is a hard `webshop` dependency missed in the original conventions doc; (c) `apps/` is NOT shared across frappe-image services in pwd.yml — each service needs its own bind-mount + editable pip install. All three discoveries are now in the agency conventions doc.

The "work within Frappe" principle locks in what the previous Slice 2 attempt failed to do. It is non-negotiable going forward — the band-aid pattern doubles trust damage by inheriting brittle code into the next session.

The `.web-footer` resolution unblocks the Slice 2 redo: the next instance can override the Jinja partial with their own structure (any class names, no inheritance from `.web-footer`'s SCSS) without needing to chase a phantom framework bug.

**Alternatives considered:**
- Skip webshop, run an external storefront (rejected — destroys the value of an integrated ERPNext build).
- Bake webshop into a custom Docker image instead of bind-mounting (deferred to Phase 6 Frappe Cloud cutover work — bind-mount is consistent with the existing `locally_twisted` pattern).
- Keep the `.web-footer` `!important` chains "just in case" (rejected — they actively interfere with the redo).

**Decided by:** GL directive 2026-04-26 ("we want the workshop", "I don't want to fight Frappe or ERPNext and their code. I want to work within it") + framework verification by current session.

---

## 2026-04-26 (Slice 2 build) — Custom Frappe app scaffolding is on; only Frappe Cloud cutover stays deferred

**Decision:** Custom Frappe app scaffolding (`locally_twisted` as an installable app inside the local bench) is part of the active build, not deferred. What stays deferred until Phase 6 is the Frappe Cloud signup, production deployment, and transfer-to-Jeff machinery.

**Reasoning:** GL clarified directly during the Slice 2 build session: "Frappe can and should be added. It's the cloud migration that isn't a priority until there's something to show." The earlier 2026-04-25 evening entry below conflated two things — local app scaffolding and cloud cutover — and deferred both. Only the latter should have been deferred.

The shape of the work changes with this correction:
- Theme CSS migrates from `Website Settings.head_html` (current Slice 2 implementation) to a real bundled asset at `apps/locally_twisted/locally_twisted/public/css/lt-theme.css`, registered via `hooks.py`, served through Frappe's asset pipeline.
- Custom DocTypes (`Dashboard Reviewed Item`, `LT Service Type`, `LT Lead Photo`) export as fixtures owned by the app.
- The 45+ Custom Fields on Lead export as Custom Field fixtures.
- Future Server Scripts (Phase 2 lead intake, Phase 3 cascades) live in the app, not as one-off DocType records.
- The whole customization surface becomes one installable unit (`bench install-app locally_twisted`).

**What this means in practice for Slices 3-9:** Better to scaffold the app *before* Slice 3 (landing page) so Slices 3-9 build natively into the app structure rather than as records that later need migration. Doing it now is hours of work; deferring it costs more later when the customization surface is larger.

**Supersedes:** the relevant clauses of the 2026-04-25 evening entry below ("No custom Frappe app scaffolding, no bench planning"). What that entry got right: keep all build work against the local `:8081` install, defer Frappe Cloud / transfer machinery until Phase 6. What it got wrong: lumping app scaffolding in with the cloud-side deferrals.

**Decided by:** GL directive during Slice 2 build, 2026-04-26.

---

## 2026-04-26 (later) — Phase 1 decision gates resolved

**Decision:** All four Phase 1 decision gates surfaced earlier today are resolved.

1. **Header navigation:** Option B — single "What We Make" mega-menu by product type; "Special Occasions" and "Holidays & Seasons" become filtered landing pages reachable from a "Browse by occasion" header link. See `.planning/decisions/header-navigation.md` for the full analysis.

2. **Accessibility statement:** Option B — brief intent-only statement with a working `accessibility@locallytwisted.com` contact + actually meeting WCAG 2.1 AA on the live site. Statement text drafted. See `.planning/decisions/accessibility-statement.md`.

3. **Blog presence in Phase 1:** YES — ship the blog framework with live posts (not deferred, not empty framework). Adds Slice 5b to the Phase 1 plan.

4. **Real photography sourcing:** placeholders. GL's exact words: "Generate fake quality images please... leave most images blank except everything on the main pages and 1 product image on product pages." 15 placeholder images generated via Together AI's FLUX.1-schnell, committed to `_resources/images/`. Real photography is "possibly a project for another instance" — these placeholders carry the demo until then.

5. **Customer-inquiry email destination:** `locallytwisted@gmail.com` (GL's account; GL handles inquiries currently).

6. **Pricing calculator placement:** embedded in the Balloon Twisting + Face Painting service page (Slice 4), NOT a standalone `/pricing` URL. GL's call: "the pricing calculator would be perfect for the face painting and balloon twisting page!" Better placement — customers already on that page are asking the cost question. Standalone Slice 10 removed; calculator scope folded into Slice 4.

**Reasoning:** GL chose all four answers explicitly in the green-light turn. Recommendations from `.planning/decisions/header-navigation.md` (Option B) and `.planning/decisions/accessibility-statement.md` (Option B) were accepted. Blog framework + live posts gives Phase 1 more substance for Jeff's eventual demo. Placeholder images close the visual-demo gap without committing to real photography sourcing yet.

**Decided by:** GL directive 2026-04-26.

---

## 2026-04-26 (later) — All clients default to ERPNext native payroll; Gusto removed from project scope

**Decision:** All Built by Cameron client builds default to ERPNext's native HRMS / Payroll module. Gusto is removed from the LT ERPNext-side project scope: no Gusto credential fields, no `gusto_service` Python helper, no Gusto CSV export job. The Gusto integration in the failed Odoo attempt was **never wired or used** (per GL clarification 2026-04-26) — the Odoo files are dead code on a never-launched test deployment.

**Reasoning:** GL directive 2026-04-26: "All clients will default to the ERP's native payroll. Please delete anything labeled 'Gusto.'" ERPNext HRMS supports salary structures, payroll periods, leave, attendance, and direct deposit natively. One less third-party integration to learn, configure, document, and hand off. Since Gusto never went live, there is no production behavior to preserve — clean slate.

**Alternatives considered:** Keep Gusto on ERPNext side as a CSV-export Server Script (rejected — perpetuates a third-party-payroll pattern the agency standard now overrides).

**What this means in practice:**
- `res_config_settings.py` translation drops any `gusto_*` fields; only `twilio_*` credentials carry over.
- A future phase (after the core build is stable) installs Frappe HRMS and configures it for LT.
- No accountant conversation needed — Gusto was never the system of record for LT's payroll.

**Supersedes:** the earlier 2026-04-26 entry that treated `gusto_service` as Phase 3 scope. The earlier entry has been rewritten to cover only `twilio_service`.

**Decided by:** GL directive 2026-04-26.

---

## 2026-04-26 — `twilio_service.py` is NOT a new DocType — it's an abstract service class

**Decision:** When the Phase 2 translation reaches `twilio_service.py`, do NOT create a new DocType for it. It was `models.AbstractModel` in Odoo (no records, only methods bound to a model namespace for `env["..."].method()` invocation). The Frappe-equivalent is Python helper functions inside a custom Frappe app, OR Server Scripts bound to a hook — not a DocType.

**Reasoning:** HANDOFF.md and the queue originally claimed "3 custom domain models need new DocTypes" — counting `dashboard_review` (done), `twilio_service`, and (formerly) `gusto_service`. Reading the actual sources confirmed that only `dashboard_review` stores records. `twilio_service` is a stub-and-ready service abstraction: it reads `ir.config_parameter` for credentials and calls the Twilio SDK. In Frappe it becomes a Python utility module referencing `frappe.db.get_single_value('LT Settings', '...')`.

**Alternatives considered:** Create an empty DocType that holds nothing and exists just to namespace the methods (rejected — pointless, breaks the Frappe pattern). Skip Twilio entirely (rejected — SMS notifications are real product scope).

**Decided by:** Trellis-successor (this session), 2026-04-26, after reading the actual model files. Documents the correction so the next instance doesn't re-introduce the wrong assumption.

---

## 2026-04-26 — GSD execution mode for translation work: lighter than `/gsd-execute-phase`

**Decision:** Translation phases (Phase 2 onward) execute via direct script-write-and-run rather than `/gsd-execute-phase`'s planner-checker-revision loop. Strategic GSD frame stays intact (PROJECT.md, ROADMAP.md, REQUIREMENTS.md, STATE.md, decisions log). Heavier GSD process is reserved for genuinely architectural choices.

**Reasoning:** Trellis's session burned tokens running `/gsd-execute-phase` on Phase 1 (inventory). The planner-checker-revision loop produced six PLAN files for what was conceptually mechanical work and never moved a deliverable. For translation work where the source is a file on disk and the destination is configurable through an API, the translation script *is* the plan: executable, testable, reviewable. The script doubles as commit-able evidence of the work.

The pattern that worked: read the Odoo source → write a Python script targeting Frappe's REST API → run it → verify in the UI → commit (auto-commit hook). When something needed revision (multi-select + conditional visibility, GL feedback), the revision was another script — keeps both the original translation and the revision as separate, replayable artifacts.

**Alternatives considered:** Stay on `/gsd-execute-phase` (rejected — caused the drift Trellis named). Drop GSD entirely for translation phases (rejected — the strategic artifacts answer "what does done look like" and stay valuable). Use `/gsd-quick` for each translation (acceptable but adds ceremony for what is single-file work).

**When to escalate to heavier GSD process:** When a decision is genuinely architectural and reversible-only-with-cost. Examples: choosing Server Script vs Notification framework for porting the 17 base.automations (Phase 3); the Phase 5 storefront UI direction; the Phase 9 Frappe Cloud deploy strategy.

**Decided by:** Trellis-successor proposed; GL accepted with "you are my partner and collaborator with all things technical. I need you to lead!" 2026-04-26.

---

## 2026-04-25 evening — Build locally first; defer bench/transferables until real

**Decision:** All translation work (Odoo → ERPNext) happens against the local LT install at `:8081`. No custom Frappe app scaffolding, no bench planning, no Frappe Cloud setup, no transfer-to-Jeff machinery until there is something real to transfer.

**Reasoning:** GL explicitly called this out after the session drifted: "we will deal with the bench and transferables when THERE ARE." Building deployment scaffolding for nothing wastes tokens and creates the illusion of progress. Local-first means: configure DocTypes/fields/automations/theme directly in the running ERPNext at `:8081`, prove each piece works, then formalize the packaging much later when the rebuild is far enough along to make packaging meaningful.

**Alternatives considered:** Set up custom Frappe app first (rejected — premature optimization for transfer when nothing exists yet). Plan elaborate phase machinery first (rejected — see other decision below).

**Decided by:** GL explicitly.

---

## 2026-04-25 evening — Skip Phase 1 entirely; use existing expedition inventory

**Decision:** Phase 1 (Inventory, INV-01 + INV-02) plans exist on disk but will NOT be executed. The off-Odoo expedition's `locally-twisted-odoo/research/extended-expedition-off-odoo-replacement/inventory-findings.md` is treated as the working inventory baseline. INV-02 (production arch_db read) is deferred to a late phase — content migration concern, not rebuild concern.

**Reasoning:** Phase 1 was elaborately planned (6 plans across 5 waves, parallel execution, threat models, validation strategies, two checker iterations) but it never produced code or DocTypes. GL named the drift: "you haven't even rebuilt the site in ERPNext?!" The expedition inventory covers ~65% of what INV-01 was meant to produce. The remaining 35% can be filled by reading source files inline during translation phases — no separate inventory document needed. INV-02 is about Jeff's UI-edited content, which only matters at content-migration time near cutover.

**Alternatives considered:** Compress Phase 1 to a single quick plan (rejected — even one plan is more inventory ceremony when we already have one). Stay the course on Phase 1 as planned (rejected — was the source of the drift GL just called out).

**Decided by:** GL chose "Skip Phase 1 entirely" from a pivot question.

---

## 2026-04-25 evening — Don't modify anything in locally-twisted-odoo

**Decision:** All scripts, tools, and code written in service of the migration go in `_CLIENTS/locally-twisted/`. The Odoo project at `C:\Users\baenb\projects\locally-twisted-odoo\` is read-only reference. Even "operational" tooling like `deploy.py` is off-limits.

**Reasoning:** GL: "leave odoo specific scripts and skills alone. we need to create ERPNext specific ones." The Odoo project is in production, has its own deploy gates and trust history with Jeff, and any modification — even additive — risks the same trust damage that motivated this migration. ERPNext-side tools are separate concerns and stay separate.

**Alternatives considered:** Modify `deploy.py` to add an `--inventory` subcommand (rejected by GL for the rule above). Use Odoo's MCP server (currently disconnected, status uncertain).

**Decided by:** GL explicitly.

---

## 2026-04-25 — LT Standard with Numbers chart of accounts; Calendar fiscal year; Services domain

**Decision:** ERPNext Company "Locally Twisted" uses Standard with Numbers chart of accounts, Calendar fiscal year (Jan 1 – Dec 31, 2026), Services as the industry domain.

**Reasoning:** Standard with Numbers matches Odoo's default convention (carryover for Jeff's familiarity). Calendar year is US small-business default; no indication LT has a different fiscal year. Services is the closest fit for event services (balloon decor, twisting, face painting); Retail is less natural (LT is mostly service work, not goods sale).

**Decided by:** GL confirmed via AskUserQuestion 2026-04-26.
