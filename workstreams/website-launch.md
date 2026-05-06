# Website Launch Workstream

Last updated: 2026-05-06 by Codex.

## Outcome

Launch the Locally Twisted website as a polished business card and sales path: customers can understand the offer, browse products with confidence, submit inquiries, and complete small-shop checkout without broken routes, inaccessible layouts, stale docs, missing policy basics, or placeholder-feeling product/category visuals.

This is the launch coordination lane. It does not replace `locally-twisted-queue.md`, `workstreams/shop.md`, or `workstreams/erpnext-backend-simplification.md`; it sequences the launch-critical parts of those lanes.

Launch scope contract: `workstreams/launch-v1-success-contract.md`. Use that file to keep V1 focused on the public website, customer trust, inquiry/checkout readiness, and measurable quality gates while preserving, but not prematurely building, the 10-year saleability infrastructure vision.

## Current Stage

Active launch lane. Baseline pass started 2026-05-02.

Known collision: another agent is auditing the form. Do not make contact/form schema changes unless that audit is handed off or explicitly merged into this lane.

Live menu/content coordination now lives in `workstreams/menu-content-coordination.md`. Agents touching menu, header, footer, public page content, or nav/content verifiers must update that file before editing so overlapping sessions do not overwrite each other.

Latest verified controller baseline:

- Docker stack is running at `http://localhost:8081`.
- Route sweep returned 200 for `/`, `/contact`, `/privacy`, `/terms-of-service`, `/refund-policy`, `/accessibility`, `/shop`, `/shop-by-category` redirected to `/shop`, `/cart`, and `/checkout`.
- `/book` redirects to `/contact?intent=quick`.
- `python scripts/verify/nav_ia.py` passed.
- `npm run test:layout-fit` passed with 60 tests.
- `python scripts/verify/smoke_shop.py` passed after updating stale chrome selectors to the current authority-first header/mobile drawer and retiring the category-card index.
- `smoke_shop.py` now verifies the desktop/mobile `Event Balloons`, `Portfolio`, `Process`, `Ready-to-Order`, `FAQ`, and `/contact` quote paths, plus the `/shop-by-category` redirect and product/variant shop contracts.
- `python scripts/verify/cart_checkout_contract.py` passed after the cart/checkout item-code contract fix.
- `python scripts/verify/variant_media_contract.py` passed after the first variant-media reconciliation pass.
- `python scripts/verify/catalog_variant_contract.py` passed: 53 products checked, 10,578 expected variants, 10,578 live variants, 4 single-SKU products.
- Current commerce rules no longer make product group the quote gate. Fixed-price products stay cartable; out-of-area delivery ZIPs redirect to a prefilled `/contact` quote path instead of Stripe. Current smoke coverage verifies product pages do not invent product-level quote gates and retail `unicorn-bouquet` option selection writes a selected variant into `LT_CART`.
- ERPNext now has 1,712 variant `Item.image` mappings from `_resources/odoo-live/images/` where Odoo image labels clearly matched product options; product detail pages swap to selected variant media when present.
- Detailed media review can be refreshed with `python scripts/setup/sync_variant_media.py --dry-run --include-details --report output/catalog-media-review.json`; latest report checked 49 products, flagged 45 for review, and skipped 6,831 unsafe-to-infer image assignments.
- Category browse imagery is not ready yet: all 11 customer-facing child Item Groups under `Shop Items` have empty image fields.
- Product option UX P0 pass completed 2026-05-02 and was reconciled with quote/retail lane rules on 2026-05-05: no per-attribute Jinja DB lookup, progressive invalid-option disabling is verified on a retail variant, and variant chips are radio/single-select where the product is checkout-enabled.
- Desktop/mobile launch screenshot baseline captured under `output/playwright/launch-baseline-20260502/`.
- Historical browser console baseline after the Webshop generated asset-map correction passed across `/`, `/shop`, `/shop-items/arches`, `/shop-items/arches/classic-arch`, `/cart`, `/checkout?item=6-color-rainbow-arch-20F&qty=1`, `/privacy`, `/refund-policy`, and `/accessibility`: all routes returned 200 with 0 console errors and 0 warnings. Current commerce behavior is governed by the 2026-05-06 delivery-zone decision: fixed-price product groups are not quote gates, and out-of-area delivery redirects to `/contact`. Report: `output/playwright/launch-baseline-20260502/console-report-after-asset-map-fix.json`.
- Webshop asset rebuild note: no Yarn package install was needed. Existing Yarn works when `/home/frappe/.nvm/versions/node/v20.19.2/bin` is added to `PATH`; build from the frontend/nginx container last so shared `assets.json` points to files nginx can actually serve.
- Final layout-fit rerun found and fixed a 320px overflow on `/shop-items/seasonal-specialty`; Webshop's stock `.item-card { min-width: 300px; }` needed the LT grid override `min-width: 0`. `npm run test:layout-fit` now passes 60/60 again.
- First brand-token reset pass completed 2026-05-02: `lt-theme.css` remaps the old pastel-heavy token values toward deep teal, slate, warm white, brass/gold, muted berry, and restrained supporting tints while preserving variable names for compatibility. Cache cleared, `nav_ia.py` passed, `npm run test:layout-fit` passed 60/60, and screenshots for `/`, `/shop`, `/contact`, and `/shop-items/arches/classic-arch` passed under `output/playwright/brand-token-20260502/`.
- Civic Celebration site-wide overhaul completed 2026-05-03. The current V1 visual direction is documented in `_resources/STYLE-GUIDE.md` and `workstreams/civic-sitewide-redesign.md`. The pass covers shared chrome, homepage, contact/book form, BTFP, portfolio, FAQ, policy/accessibility/success pages, shop, category/product pages, cart, and checkout. Screenshots were captured under `output/playwright/civic-overhaul-20260503-verified/`.
- Style-guide consolidation completed 2026-05-05. `_resources/design-guide/` was deleted because it conflicted with the approved Civic Celebration + Slate Blue/Berry + Brand Direction contract and kept reintroducing light-blue/blush styling. Current launch visuals must use `_resources/STYLE-GUIDE.md` only.
- Responsive container integrity gate completed 2026-05-05. `npm run test:layout-fit` now checks 20 public routes across 13 viewport families (260 checks), `npm run test:interactive-layout` checks 39 stateful UI cases, and `npm run test:public-verify` runs nav IA, passive layout, interactive layout, checkout experience, and shop smoke with quieter Playwright output.
- `smoke_shop.py` now matches the current commerce split: fixed-price product pages stay checkoutable, and the delivery ZIP/city gate owns the quote fallback. Retail variants still prove inline option selection and cart writes.

## Owner

Unassigned next agent/session.

Work from:

`C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\locally-twisted`

## User-Facing Impact

Launch succeeds when a real customer can:

- land on the site and understand Locally Twisted quickly
- navigate on desktop and mobile without broken IA
- browse categories and products without placeholder or incorrect media undermining trust
- submit an inquiry through `/contact`
- use `/book` only as a redirect/quick-intent alias, not a separate form
- view policy/legal pages needed for trust and Stripe readiness
- use cart/checkout for small-shop items without guest-login traps

## Launch Gates

### Gate 1 - Reality Baseline

Verify before building:

- Current running site is reachable at `http://localhost:8081`.
- Current git status is understood; do not overwrite another agent's changes.
- Queue and workstreams are read.
- Form audit ownership is respected.
- Catalog counts or route states are rechecked before being quoted as current.

### Gate 2 - Inquiry Path

Launch blocker if broken:

- `/contact` loads and submits correctly.
- `/book` redirects to `/contact?intent=quick`.
- Lead records get the intended service/taxonomy values.
- Customer-facing success/error states are loud enough that silent failure is unlikely.

Coordinate with the active form audit before changing this area.

### Gate 3 - Trust And Policy Surface

Launch blocker if missing or obviously stale:

- `/privacy`
- `/terms-of-service`
- `/refund-policy`
- `/accessibility`
- Stripe Dashboard URLs after GL/legal approval.

Policy text must come from approved project resources or GL/legal approval. Do not invent legal terms.

### Gate 4 - Shop Confidence

Launch blocker if it breaks purchase confidence:

- Product/category navigation works; broad browse traffic lands on `/shop`.
- Variant options are valid and purchasable.
- Guest cart does not redirect customers to login.
- Checkout and payment-success path still work in test mode.
- Products and customer-facing category/detail pages do not rely on obvious placeholder imagery where source media exists.

Primary coordination file: `workstreams/shop.md`.

### Gate 5 - Visual And Accessibility Quality

Launch blocker if customer-facing:

- Desktop and mobile layouts do not overlap, clip text, or show broken spacing.
- Header/footer/navigation are consistent.
- Core pages feel like one brand, not stitched-together ERPNext defaults.
- Important buttons, links, forms, and menus are keyboard and screen-reader reasonable.
- Images have usable alt text or are clearly decorative.

### Gate 6 - Backend Readiness For Jeff

Not every backend cleanup must block public launch, but Jeff-facing handoff should not be confusing or unsafe:

- Inquiry records are readable.
- Backend labels avoid ERPNext jargon where possible.
- Demo/sample data is only created after schema cleanup.
- Stale scripts are not rerun blindly.

Primary coordination file: `workstreams/erpnext-backend-simplification.md`.

## Launch Board

| Lane | Status | Current evidence | Blocker / next action |
|---|---|---|---|
| Controller baseline | Passing after verifier update | Route sweep 200s, `/book` redirect verified, `nav_ia.py` passed, `layout-fit` 60 passed, `smoke_shop.py` passed | Keep this file current after every lane return |
| Form audit | Owned by separate agent | Do not edit `/contact` or Lead schema from this lane yet | Wait for form audit handoff before inquiry-path changes |
| Policy/trust | Routes load, content not launch-approved | Policy audit found `/privacy`, `/terms-of-service`, `/refund-policy`, `/accessibility` exist; source trace lives in `workstreams/policy-trust.md` | Get GL/legal decisions on unresolved privacy, cookie, shipping/delivery, and refund terms before Stripe URL wiring |
| Shop/media | Variant cart contract fixed; broad browse routes use `/shop`; first variant-media pass, variant correctness diff, and option UX P0 pass completed | `cart_checkout_contract.py`, `variant_media_contract.py`, `catalog_variant_contract.py`, and `smoke_shop.py` passed; 1,712 variant images mapped; detailed media report generated; `/shop-by-category` redirects to `/shop`; exact variant checkout URL returns 200 while template checkout URL is blocked | Review the 45 flagged products / 6,831 skipped assignments, select category browse imagery for 11 empty Item Groups, then continue product/category visual polish |
| Visual/accessibility QA | Civic site-wide visual pass implemented and locally verified; `/portfolio` proof-gallery reel added as a route-specific visual slice | `output/playwright/launch-baseline-20260502/`, `output/playwright/brand-token-20260502/`, and `output/playwright/civic-overhaul-20260503-verified/` have desktop/mobile evidence; `nav_ia.py`, `layout-fit`, shop/cart/checkout/catalog/variant/contact checks passed in the Civic pass; `npm run test:portfolio-reel` verifies the portfolio reel contract | Do manual keyboard/focus/alt/zoom checks and rerun screenshots after final media/content changes; review portfolio photo order/quality with GL/Jeff |
| Backend readiness | Pending | Backend workstream exists | Keep separate from public form audit; simplify after schema/source reality is clear |
| Release gate | Not started | No integrated launch report yet | Run final route, form, shop, visual, accessibility, and policy-source gates after implementation lanes land |

## Higher-Quality Launch Additions

These are the best "more professional, more big business" upgrades before launch:

1. Review skipped/unmatched product/category media from `output/catalog-media-review.json` where source photos exist but labels were not safe enough to auto-map.
2. Representative category media for `/shop-items/<group>` pages or a future image-rich mega menu, without reviving the retired category-card index.
3. Hetzner-faithful refresh of `/refund-policy` and `/accessibility`.
4. Webshop product-detail/layout cleanup after variant/media correctness.
5. Visual QA pass across homepage, portfolio, contact, policy pages, shop, category, product detail, cart, and checkout.
6. Accessibility pass focused on real customer paths, not theoretical coverage.

The broad Civic redesign has landed. Do not start another broad visual direction change before launch unless GL explicitly reverses the Civic decision; spend remaining launch time on proof photos, content accuracy, accessibility, and final verification.

## Coordinated Take-Live Workflow

Use this lane as the launch controller board when multiple agents or sessions are working at once.

### What Supports This

- Machine-wide Guiding Light Codex protocol: communication, attention protection, decision boundary, and verification discipline.
- Project `AGENTS.md`: LT-specific source routing, ERPNext/Frappe rules, and stale-doc warnings.
- Project capability: `.codex/capabilities/recipes/take-live-coordinated-workflows.md`.
- `locally-twisted-queue.md`: active work selection.
- `workstreams/*.md`: feature-lane handoffs by user-facing outcome.
- `workstreams/policy-trust.md`: policy source trace and Stripe/legal readiness lane.
- Superpowers-style parallel pattern: one controller, bounded sidecar agents, explicit ownership, review before integration.
- Existing verification scripts: nav, layout fit, shop smoke, contact/form checks, backend parity, compile checks, and browser screenshots.
- Optional read-only Claude reference library: `C:\Users\baenb\.claude\skills\README.md` and specific Frappe safety skills when they help decide what to verify.

### Controller Role

One agent/session must act as launch controller.

Controller owns:

- keeping this file current
- choosing the next non-colliding lane
- assigning read-only audits or implementation scopes
- preventing two agents from editing the same files or behavior
- integrating returned work in dependency order
- running or coordinating final release verification

The controller should continue doing non-overlapping work while sidecar agents run. Do not hand off the immediate blocking task if the controller cannot move forward without it.

### Parallel Lanes

| Lane | Parallel-safe work | Write scope rule | Launch value |
|---|---|---|---|
| Form audit | Read-only `/contact`, `/book` redirect, Lead/service behavior | No form/schema edits unless handed off by current form auditor | Protects inquiry conversion |
| Policy/trust | `/refund-policy`, `/accessibility`, `/privacy`, `/terms-of-service` review and refresh | Do not invent legal terms; use approved sources | Builds customer and Stripe trust |
| Shop/media | Variant correctness, product/category media inventory, category browse imagery | Coordinate through `workstreams/shop.md`; avoid checkout/form files unless assigned | Raises product confidence |
| Visual/accessibility QA | Screenshots, layout fit, nav, keyboard basics, image/alt checks | Read-only unless assigned a narrow CSS/template fix | Prevents launch embarrassment |
| Backend readiness | Jeff-facing Lead/Contact/order clarity, stale script audit, sample data timing | Coordinate through backend workstream; avoid public form edits unless assigned | Makes handoff usable |
| Release gate | Final integrated verification and launch-readiness report | Read-only except docs/checklist updates | Prevents false launch claims |

### Dispatch Rules

- Dispatch read-only auditors freely when their lanes do not depend on each other.
- Dispatch implementation agents only with a disjoint write scope.
- Never dispatch two implementation agents to the same template, CSS file, JS flow, DocType schema, seed script, fixture, checkout path, or form path at the same time.
- Each agent must return: changed files, exact verification run, evidence summary, blockers, and next handoff note.
- The controller reviews every returned result before treating it as launch evidence.

### Review Rules

Implementation lanes need two reviews before integration:

1. Spec review: did the work solve the assigned launch lane and stay in scope?
2. Quality review: is it maintainable, Frappe/ERPNext-native, accessible, and consistent with LT style?

Read-only audit lanes need evidence review:

- exact route or file checked
- exact command or browser path used
- clear pass/fail/blocker result
- no claims beyond what was checked

### Integration Order

Default launch order:

1. Reality baseline and collision check.
2. Inquiry/form audit result.
3. Policy/trust pages and Stripe URL readiness.
4. Shop variant/media correctness.
5. Product/category visual polish.
6. Visual/accessibility QA after visual changes.
7. Backend handoff readiness.
8. Final release gate from the integrated workspace.

Policy/trust and shop/media can run while the form audit continues, as long as they do not touch `/contact`, Lead schema, or shared checkout behavior.

## Touched Areas

Launch-critical surfaces:

- `/`
- `/contact`
- `/book`
- `/privacy`
- `/terms-of-service`
- `/refund-policy`
- `/accessibility`
- `/shop`
- `/shop-by-category` compatibility redirect to `/shop`
- `/shop-items/<group>`
- `/shop-items/<group>/<slug>`
- `/cart`
- `/checkout`
- `/payment-success`
- `/thank-you`

Primary references:

- `AGENTS.md`
- `locally-twisted-queue.md`
- `CODING-HANDOFF.md`
- `locally-twisted-decisions.md`
- `workstreams/shop.md`
- `workstreams/erpnext-backend-simplification.md`
- `_resources/STYLE-GUIDE.md`
- `_resources/STYLE-GUIDE.md` version 4.2 or newer. The old `_resources/design-guide/` synthesis was deleted on 2026-05-05 and must not be used.
- `workstreams/responsive-container-integrity.md`
- `_resources/policies/`
- `_resources/odoo-live/`
- `C:\Users\baenb\projects\locally-twisted-odoo\` as the read-only business-detail source of truth for customer-facing business claims, policies, product/service details, voice, and legacy business decisions

## Dependencies And Collision Points

- Form audit owns current `/contact` and Lead-submission review until handed off.
- Shop lane owns catalog correctness, media, product detail, cart, and checkout polish.
- Backend simplification owns Jeff-facing Desk and stale Lead/schema cleanup.
- Policy/legal pages require the Odoo business-detail source, approved current project resources that trace back to it, or GL/legal approval.
- Business details from the old Odoo project drive are source-of-truth evidence for business meaning, not app-build instructions. Do not modify `C:\Users\baenb\projects\locally-twisted-odoo\` from this repo.
- Media/render work must stay honest to balloon construction and product reality; do not attach generated concepts to products as factual photos.

## Do Not Do

- Do not call the site launch-ready from docs alone.
- Do not rebuild `/book` as a separate public form.
- Do not change form schema while another agent owns the audit unless coordinated.
- Do not bury launch blockers in `PROJECT-STATUS.md`.
- Do not let beautiful visuals hide broken product options, inquiry submission, cart, or checkout.
- Do not invent policy/legal language, product capabilities, or business promises.

## Verification

Run the exact checks tied to the changed surface.

Core launch verification:

```powershell
python scripts/verify/nav_ia.py
npm run test:layout-fit
npm run test:interactive-layout
npm run test:checkout-experience
python scripts/verify/smoke_shop.py
npm run test:public-verify
```

Form path verification, coordinated with the form audit:

```powershell
python scripts/verify/contact_prefill.py --base-url http://localhost:8081
python scripts/verify/contact_service_logic.py --base-url http://localhost:8081
python scripts/verify/smoke_forms.py --base-url http://localhost:8081 --form-path /contact --skip-newsletter
```

Backend/contact parity verification when Lead schema or backend routing changes:

```powershell
python scripts/setup/sync_contact_intake_backend.py
python scripts/verify/lead_backend_intake_parity.py
```

Python syntax check after Python edits:

```powershell
python -m compileall apps\locally_twisted\locally_twisted scripts\verify scripts\setup
```

After Jinja/CSS/Web Page edits:

```powershell
python scripts/dev/clear_website_cache.py
```

Visual verification:

- Browser screenshots at desktop and mobile widths.
- Breakpoint-edge layout checks at 320, 360, 375, 390, 414, 768, 820, 991, 992, 1024, 1199, 1200, and 1366px through the shared layout helper.
- Open-state checks for nav, drawers, modals, filters, forms, product controls, and reduced-motion states where relevant.
- Check homepage, contact, policies, shop, category, product detail, cart, and checkout.
- Confirm no text overlap, clipped buttons, smashed images, placeholder category/detail surfaces where better media exists, or ERPNext-looking default surfaces on launch-critical pages.

## Decisions And References

- Active tasks: `locally-twisted-queue.md`.
- Project rules: `AGENTS.md`.
- Durable reasoning: `locally-twisted-decisions.md`.
- Compact technical startup: `CODING-HANDOFF.md`.
- Shop lane: `workstreams/shop.md`.
- Policy/trust lane: `workstreams/policy-trust.md`.
- Backend lane: `workstreams/erpnext-backend-simplification.md`.
- Take-live coordination recipe: `.codex/capabilities/recipes/take-live-coordinated-workflows.md`.
- Legacy whole-project maps: `HANDOFF.md`, `PROJECT-STATUS.md`.

## Next Handoff Stage

First non-colliding launch slice:

1. Do a read-only launch baseline across route availability, queue/workstreams, and current git state.
2. Confirm form audit ownership and avoid `/contact` edits unless handed off.
3. Work on policy/trust or shop/media quality while the form audit continues.
4. Update this file with exact changed surfaces, verification commands, and remaining launch blockers.
