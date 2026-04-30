# Locally Twisted — Mirror Rebuild Plan

**Date:** 2026-04-30
**Source of truth:** `_resources/odoo-live-mirror/` (the captured Hetzner site)
**Inventory reference:** `_resources/odoo-live-mirror/INVENTORY.md`
**Authorized by:** GL — *"clone my old site http://5.78.136.133/, the only page that stays is the landing page... using capabilities, rebuild the whole site. make sure it's frappe and ERPNext coded."*

This is a **mirror rebuild**: visual + IA + content + page-shapes from Hetzner are reproduced through Frappe v15 + ERPNext v15 primitives (Jinja partials, `apps/locally_twisted/.../www/` controllers, theme CSS, ERPNext webshop overrides). The rebuild is faithful to Hetzner's rendered output, not a creative re-interpretation.

---

## Frame: what stays vs what changes

### STAYS unchanged

- **Homepage at `/`** — current `apps/locally_twisted/locally_twisted/www/home.{py,html}` (lookbook-forward, reviews carousel, custom creations grid, client logo crawl). Per GL's directive: *"the only page that stays is the landing page."*
- **Backend infrastructure:**
  - 45-field Lead schema (`Lead` Custom Fields — already aligned with Hetzner's `/book` form names)
  - ERPNext webshop install + the 53 Website Items / 10,578 variants / 10,613 Item Prices ported 2026-04-30
  - Stripe Checkout Sessions wiring (`payments/stripe_session.py`, `www/payment_success.{py,html}`, webhook handler)
  - localStorage guest cart (`public/js/lt-guest-cart.js`, `api/cart.py`, `www/lt_cart.{py,html}`)
  - Email Account on smtp.gmail.com, ERPNext cascade (PR Paid → SI → emails)
  - `installed_apps` order with `locally_twisted` last
- **`_resources/` canonical resources** (style guide, policies, tax research, design guide, images) — frame is migration to ERPNext, these are migration sources
- **Voice & language relabels** in ERPNext desk (Lead form labels, etc.)

### CHANGES (replaced with Hetzner-faithful clones)

#### A. Site chrome (header + footer)

| Element | Source in mirror | Destination in Frappe |
|---|---|---|
| Header (desktop + mobile) | `pages/index.html` lines ~286–635 | `apps/locally_twisted/locally_twisted/templates/includes/navbar/navbar.html` |
| Footer (newsletter + 3-col + legal) | `pages/index.html` lines ~1111–1223 | `apps/locally_twisted/locally_twisted/templates/includes/footer/footer.html` |
| Newsletter signup endpoint | (new — replaces Odoo `js_subscribe`) | New `api/newsletter.py` whitelist + a Custom DocType `LT Newsletter Signup` |

Header structure to reproduce:
- Desktop: utility bar (delivery truck tagline left | centered logo | sign in / cart / Contact CTA right) + primary nav row (Balloon Twisting & Face Painting | Special Occasions mega menu | Holidays & Seasons mega menu | What We Make mega menu | overflow: Contact, Blog | search modal trigger)
- Mobile: single row (logo | cart | wishlist | hamburger) + offcanvas drawer with same nav items + sign-in + Contact CTA

The current LT navbar has a *different* structure (eyebrow with truck icon, but no mega menus, no separate utility bar / nav row split). It's getting replaced wholesale.

Footer structure to reproduce:
- Newsletter strip (heading + email input + Join button)
- Main: centered brand + tagline + 3 social icons + 3-column links (Shop / Company / Get In Touch)
- Legal bar (copyright + Refund Policy + Accessibility links)

The current LT footer is also getting replaced wholesale. Social icon set: Facebook, Instagram, Pinterest (3 icons, no Twitter — matches Hetzner exactly).

#### B. Pages — replace existing or build fresh

| Route | Source file | Destination | Status today | Action |
|---|---|---|---|---|
| `/about` | `pages/about.html` | `www/about.{py,html}` | Doesn't exist (deferred) | BUILD |
| `/gallery` | `pages/gallery.html` | `www/gallery.{py,html}` | Doesn't exist | BUILD |
| `/privacy` | `pages/privacy.html` | `www/privacy.{py,html}` | Doesn't exist (Stripe live-mode block) | BUILD |
| `/refund-policy` | `pages/refund-policy.html` | `www/refund_policy.{py,html}` (alias `/refund-policy`) | Exists, replace | REPLACE |
| `/accessibility` | `pages/accessibility.html` | `www/accessibility.{py,html}` | Exists, replace | REPLACE |
| `/balloon-twisting-and-face-painting` | `pages/balloon-twisting-and-face-painting.html` | `www/balloon_twisting_and_face_painting.{py,html}` | Exists, replace | REPLACE |
| `/contact` | `pages/contact.html` | `www/contact.{py,html}` | Exists, replace | REPLACE |
| `/contactus` | (alias for `/contact`) | `hooks.py website_route_rules` redirect `/contactus` → `/contact` | N/A | REDIRECT |
| `/book` | `pages/book.html` | `www/book.{py,html}` | **404 today (load-bearing)** | BUILD |
| `/services` | (Hetzner returns 404) | (skip) | Doesn't exist | NOT-CLONED — Hetzner had no published content |
| `/blog` | `pages/blog.html` | `www/blog/index.{py,html}` | Doesn't exist (deferred) | BUILD |
| `/blog/<channel>` | `pages/blog_behind-the-balloons-1.html` | `www/blog/<channel>.{py,html}` (or single dynamic controller) | Doesn't exist | BUILD |
| `/blog/<channel>/<post>` | 2 captured posts | Custom Frappe DocType `LT Blog Post` + `www/blog/post.{py,html}` | Doesn't exist | BUILD + DocType |
| `/blog/.../tag/<tag>` | (parameter view of channel) | Same `<channel>.{py,html}` with `?tag=` query | — | inline in channel template |
| `/shop` | `pages/shop.html` | Override webshop's `/all-products` template + custom CSS | Exists with custom shape | REPLACE-LAYOUT (keep existing data) |
| `/shop/category/<slug>` | 30+ category pages | Override webshop's category template | Exists with custom shape | REPLACE-LAYOUT |
| `/shop/<product>` | 53 canonical product pages | Override `templates/generators/item/item_details.html`, `item_add_to_cart.html`, `item_configure.html` (already done) — REWORK to match Hetzner | Exists with custom shape | REPLACE-LAYOUT |
| `/shop/cart` | `pages/shop_cart.html` | Custom `www/lt_cart.{py,html}` (exists) | Exists | REPLACE-LAYOUT |
| `/shop/wishlist` | (auth required) | (skip) | N/A | NOT-CLONED — auth-only, low priority |

#### C. Theme CSS overhaul

Replace the `lt-header__*` and `lt-footer__*` BEM blocks in `apps/locally_twisted/locally_twisted/public/css/lt-theme.css` with new ones derived from Hetzner's `s_lt_*` and `lt-*` classes. Preserve token system (color variables, spacing scale, typography) but reset every section block (`.lt-shop__*`, `.lt-product-detail__*`, `.lt-section__*`) to match Hetzner's actual rendered look.

The current LT CSS is ~700 lines. The replacement will be larger because Hetzner's design has more distinct sections (mega menus, utility bar, newsletter strip, etc.). Estimate: ~1200–1500 lines after rebuild.

#### D. JS additions

| Behavior | Source | Destination |
|---|---|---|
| Mega menu open/close (hover desktop, tap mobile) | Inline JS in mirror header | `public/js/lt-megamenu.js` |
| `/book` conditional show/hide on `x_services` checkboxes | Inline JS in `pages/book.html` | `public/js/lt-book-form.js` |
| `/book` file upload validation (5 × 25 MB) | Inline JS in `pages/book.html` | Same `lt-book-form.js` |
| Confirmation modal on `#received` hash | Inline JS on `/book` and `/contact` | `public/js/lt-form-confirm.js` (shared) |
| Newsletter signup submit (Hetzner used `js_subscribe`) | Replace with native fetch to our endpoint | `public/js/lt-newsletter.js` |
| Shop variant selector (already inline in our `item_configure.html`) | Reuse + adjust for any Hetzner-specific behavior | (existing — adjust) |
| Search modal | Inline JS in mirror | `public/js/lt-search.js` (uses ERPNext's `frappe.search` or webshop's product search) |

---

## Execution model

### Phase 1 — Chrome rebuild via `/triadic-construction-v2`

The header + footer + theme CSS overhaul are the highest-interdependency work. Builder agents need to coordinate (header CSS affects mobile drawer JS; footer link IDs affect nav state; theme tokens affect every page). Reviewer agents during construction catch drift before it propagates.

Triadic dispatch:
- **Builder 1 — Jinja chrome:** writes `templates/includes/navbar/navbar.html` and `templates/includes/footer/footer.html` from the mirror's verbatim markup, translating Odoo classes (`o_*`) to LT-owned BEM classes (`lt-*`) where Odoo classes carry framework-specific behavior. Preserves visible structure exactly.
- **Builder 2 — CSS:** appends to `public/css/lt-theme.css` with `lt-header__*`, `lt-utility-bar__*`, `lt-megamenu__*`, `lt-footer-newsletter__*`, `lt-footer__*`, `lt-footer-bar__*` blocks. No `!important`. Pulls computed styles from the mirror's CSS files in `_resources/odoo-live-mirror/assets/web/static/...`.
- **Builder 3 — JS:** writes `public/js/lt-megamenu.js`, `public/js/lt-newsletter.js`, `public/js/lt-search.js`. Vanilla JS, no jQuery, posts to whitelisted Frappe endpoints.
- **Reviewer 1 — Hetzner-fidelity:** loads the mirrored `pages/index.html` and renders both. Checks the rebuilt header and footer pixel-match Hetzner at desktop (1280) and mobile (375). Specific check: utility bar 3-column layout, mega menu 4-column dropdown structure, footer 3-column link structure, newsletter form alignment.
- **Reviewer 2 — Accessibility:** WCAG 2.1 AA on the chrome — keyboard navigation through nav, focus-visible outlines, ARIA labels on icon buttons, color contrast on links, mobile drawer screen-reader announce.
- **Reviewer 3 — Frappe-integration:** confirms `web_include_css` / `web_include_js` registration, partial override paths, `installed_apps` order still has `locally_twisted` last, no Odoo classes that bind to absent JS, no broken `/web/*` Odoo URLs.

Acceptance for Phase 1: all three reviewers PASS, screenshot diff against `pages/index.html` shows visual parity at desktop + mobile, no console errors, no 404 asset requests.

Atomic commit: one commit per (header, footer, css, js) bundle once the round passes review.

### Phase 2 — Page rebuilds (sequential, one agent per page)

Once chrome is in place, dispatch a focused builder agent per page in priority order. Each agent:
1. Reads the mirror source file
2. Reads the corresponding LT page (if it exists) to see what to replace
3. Writes new `www/<route>.py` controller + `www/<route>.html` template
4. Adds page-specific CSS to `lt-theme.css` (or page-scoped CSS in the controller's `PAGE_CSS` constant)
5. Adds page-specific JS if needed
6. Runs the project's `scripts/dev/clear_website_cache.py`
7. Captures Playwright viewport screenshots at desktop (1280) + mobile (375)
8. Reads the screenshots and confirms pixel-parity against the mirror
9. Commits atomically

Build order (by load-bearing-ness):

| Order | Page | Why first |
|---|---|---|
| 1 | `/book` | Load-bearing 404 today; every CTA points here; primary inquiry path |
| 2 | `/contact` | Replaces existing; secondary inquiry path |
| 3 | `/balloon-twisting-and-face-painting` | Replaces existing; second-most-visited service page |
| 4 | `/about` | New build; nav points here |
| 5 | `/privacy` | Stripe live-mode block — required for production |
| 6 | `/refund-policy` | Replaces existing; legal page |
| 7 | `/accessibility` | Replaces existing; legal page |
| 8 | `/gallery` | New build |
| 9 | `/blog` (channel index) + `LT Blog Post` DocType | New build |
| 10 | `/blog/<channel>/<post>` (1 post template) + 2 ported posts | New build |
| 11 | Webshop `/shop` layout override | Replaces existing custom shop layout |
| 12 | Webshop product detail layout | Replaces existing custom product detail |
| 13 | Webshop category landing override | Replaces existing |
| 14 | Cart/checkout layout audit | Verify it still matches Hetzner's `/shop/cart` style |

Each page commit is atomic and reverts cleanly if the audit pass flags it.

### Phase 3 — Audit pass

After all pages are built:
- Capture Playwright viewport-only screenshots of every rebuilt route at desktop (1280) + mobile (375), saved to `_resources/audit-2026-04-30/<route>-{desktop,mobile}.png`.
- Side-by-side diff: rebuilt screenshot vs `_resources/odoo-live-mirror/pages/<route>.html` rendered (capture Hetzner's actual render via Playwright pointed at the local mirrored HTML file or at the live Hetzner URL while it's still up).
- Per-product variant correctness diff: for each of 53 canonical product slugs, parse the mirrored page's `data-attribute-exclusions` JSON and compare to the variant set in our ERPNext DB (query via `bench --site frontend execute`). Mismatches noted in `VERIFICATION.md`.
- WCAG 2.1 AA pass via `axe-playwright` or equivalent on every page.
- Output: `VERIFICATION.md` with one row per route — PASS / FLAG / FAIL + screenshot path + specific findings.

### Phase 4 — Final report

Write `MIRROR-REBUILD-COMPLETE.md` with:
- What's done (every commit, with route + commit hash)
- What failed (every FAIL or FLAG row from VERIFICATION.md, with proposed remediation)
- NOT-CLONED log (final state — see template below)
- Screenshots inlined or paths cited
- Specific things GL needs to look at in their real browser (load-bearing visual claims that need real-browser verification, not just Playwright)

---

## NOT-CLONED log (running list, finalized in MIRROR-REBUILD-COMPLETE.md)

Things that exist on Hetzner but are deliberately NOT cloned, with reason:

| Hetzner surface | Reason | ERPNext equivalent / decision |
|---|---|---|
| `/web/login`, `/web/signup`, `/web/reset_password` | Odoo's auth UI — different from ERPNext's `/login` | Use ERPNext's native auth pages |
| `/services` | Hetzner returns 404 (route exists, no published content) | Skip — not a real page |
| `/shop/wishlist` | Auth-required and Hetzner shows it conditionally; ERPNext webshop has its own wishlist with different behavior | Skip for now; Phase 5 portal work |
| `/shop/event-booking-deposit-32` | Hetzner returns 404 (product was unpublished) | Skip — not a real page |
| Empty category pages (Valentine's Day, Father's Day, 4th of July, Fall, Christmas, Photo Frames) | Hetzner shows them with no products | Suppress from category tree until populated |
| Odoo's `/contactus` route | Duplicate of `/contact` | Frappe `website_route_rules` redirect |
| Odoo's bundled CSS/JS (`/web/static/src/...`) | Framework files, not LT content | Frappe ships its own; we write LT-owned CSS/JS |
| Color swatch images (`/web/image/product.attribute.value/<id>/image`) | Odoo dynamic image URLs not captured in asset crawl; ERPNext `Item Attribute Value.colour` is hex-only | Document as known gap; future enhancement uses hex tiles or custom field |

(Additions during execution will append rows here.)

---

## State tracking

Durable state for this multi-stage build:

- `MIRROR-REBUILD-PLAN.md` — this file (the plan)
- `MIRROR-REBUILD-STATE.md` — execution state, updated after each commit (which Phase, which route, last commit hash, what's next)
- Per-commit messages prefixed `mirror-rebuild: <route> — <action>` so `git log --grep="^mirror-rebuild"` is the audit trail
- `VERIFICATION.md` — written during Phase 3
- `MIRROR-REBUILD-COMPLETE.md` — final report

If context tightens before Phase 4 completes, the next session reads `MIRROR-REBUILD-STATE.md` + git log and picks up at the next pending route.

---

## Risks and pre-known issues

1. **The current homepage's nav links point at routes that don't exist yet.** Hero CTA → `/book` is currently 404. Header "Contact" → `/contact` works but will be replaced. Build order above starts with `/book` to fix the load-bearing 404 first.
2. **Mobile mega menus.** Hetzner's mobile nav uses an offcanvas drawer with the SAME mega menu items (Special Occasions, Holidays & Seasons, What We Make) expanding accordion-style. The current LT mobile nav uses a different shape. The chrome rebuild fixes this.
3. **Mega menu data source.** Hetzner's mega menus list product categories statically in the markup. ERPNext webshop has Item Group children. The mega menus should be populated dynamically from Item Groups (via `update_website_context` hook — already in place from the catalog port) so adding/removing categories doesn't require a chrome rebuild.
4. **Hetzner uses Bootstrap 5 conventions** (`d-none`, `d-lg-block`, `gx-*`, `gap-*`). Frappe v15 ships Bootstrap 4-flavored utilities. Some classes won't behave identically — the CSS rebuild needs to handle this. Specifically: `gap-*`, `g-*`, `gx-*` are Bootstrap 5; in Frappe's Bootstrap 4-flavor they're either no-ops or named differently. Builder 2 (CSS) handles the mapping.
5. **Hetzner uses Owl Carousel for hero slides.** The homepage stays as-is, but if any other page uses Owl Carousel JS (e.g., `/balloon-twisting-and-face-painting` carousels), we replace with vanilla CSS scroll-snap or Swiper.js (already considered for the design guide synthesis).
6. **The `/book` form is the most complex single deliverable.** 30+ fields, conditional show/hide, file upload validation, confirmation modal. Builder agent for `/book` gets the longest brief and a dedicated reviewer pass.
7. **Per-product variant correctness diff (Phase 3) may surface real data discrepancies** between Hetzner's offering and our DB. If found, they're fixed at the seed layer (`apps/locally_twisted/locally_twisted/seed/seed_catalog.py`), not papered over visually.
8. **Hetzner's product page shows up to 53 latex-color checkboxes inline.** Our current product page uses a dropdown for ≥9 values. The Hetzner-fidelity rebuild reverts to inline checkbox swatches for color-type attributes specifically.
9. **Newsletter signup needs a destination** — Hetzner posts to Odoo's mailing list. ERPNext doesn't have a mailing list module by default. We add a `LT Newsletter Signup` Custom DocType (single-field + email + opt-in timestamp) and a whitelisted endpoint `api/newsletter.py` that creates one record per submit.
10. **OG images and meta tags:** Hetzner has OG images per page (`og-home.png`, `og-book.png`, `og-contact.png`). Most weren't crawled (asset crawl missed dynamic OG image URLs). The page rebuilds need to set `<meta property="og:image">` to local files in `apps/locally_twisted/.../public/images/og/` — placeholders OK in v1.

---

## Verification protocol

For every page in Phase 2:

1. **DOM check** — controller renders, no Frappe template error, no 500.
2. **Cache clear** — `python scripts/dev/clear_website_cache.py` after every change.
3. **Playwright viewport screenshot** — desktop 1280×800 + mobile 375×667. Saved to `_resources/audit-2026-04-30/<route>-{desktop,mobile}.png`.
4. **Read the screenshot** — describe what's visible. If the description doesn't match Hetzner's mirrored render, the build is not done.
5. **Console clean** — Playwright capture of `console.log` and `console.error`. Any error = FAIL.
6. **Form-bearing pages also:** smoke-test the form via curl with X-Requested-With header. Lead created or 200 with success body. Loud-failure rule per `~/.claude/rules/loud-failure.md`.

The DOM saying `is_visible: True` is not the same as the pixels showing the content. Per the lessons-learned 2026-04-29: viewport-only Playwright screenshots are the verification method, NOT full-page screenshots (which compress at extreme aspect ratios and lie).

---

## Skill plan

| Phase | Skill / mechanism |
|---|---|
| Plan-deepen this plan | `/plan-deepen` skill — surfaces gotchas before building |
| Chrome (header + footer + theme CSS overhaul) | `/triadic-construction-v2` — high-interdependency work |
| Page rebuilds (sequential) | Single focused builder agents (`general-purpose` subagent) per page |
| Audit | Single audit agent + Playwright via `webapp-testing` skill / `scripts/verify/playwright_*.py` |
| Final report | Self-write `MIRROR-REBUILD-COMPLETE.md` |

GSD skills considered but NOT used: `/gsd-execute-phase` etc. — this work isn't shaped as a GSD phase (it's a wholesale rebuild dispatched outside the existing `.planning/phases/01-customer-site-and-storefront/PLAN.md`). After completion, the existing GSD phase plan needs an update to reflect the rebuilt state.

---

## Hand-off contract

When this plan is fully executed:

1. `localhost:8081/` (homepage) is unchanged.
2. Every other customer-facing route on the LT site visually matches the Hetzner mirror at desktop + mobile.
3. Backend wiring (Stripe, Lead, variants, email cascade) is unchanged.
4. `VERIFICATION.md` exists with one row per route; `FAIL` rows have remediation notes.
5. `MIRROR-REBUILD-COMPLETE.md` exists with the full state report, including the NOT-CLONED log.
6. Every commit is in `git log --grep="^mirror-rebuild"` order.
7. GL can open any route in their real browser and see Hetzner's site at that route — minus authenticated/Odoo-only pages explicitly logged in NOT-CLONED.

If any of those clauses can't be met, the failure is named and surfaced in the final report — not papered over.
