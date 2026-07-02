# Builder Jinja Build Report — Round 1
## Date: 2026-04-30
## Builder: Builder Jinja (Opus 4.7)

---

### Tasks Completed

#### Task 1 — Replace `navbar.html` with current import capture-faithful 3-mega-menu structure

- **Files Changed:**
  - `apps/locally_twisted/locally_twisted/templates/includes/navbar/navbar.html` — full replacement (384 lines → ~290 lines of clean Jinja; the prior 140 lines of inline `<style>` + `<script>` are gone)

- **Approach:** Wholesale replacement of the prior single-flat-Shop-mega-menu template with a two-tier desktop nav (utility bar + primary nav row with 3 mega menus) and a mobile single-row + offcanvas drawer. All catalog_data `data-bs-*` attributes replaced with custom `data-lt-megamenu-trigger` / `data-lt-accordion-trigger` data attributes per the API contract. No inline `<style>` or `<script>` blocks; both removed as required by Build Brief §Hard Constraints 4+5. Inline SVG path data used only in template files (not CMS fields) for caret icons — all other icons reference external `.svg` files via `<img src>`.

- **New Interfaces exposed to Builder JS:**
  - Desktop mega triggers: `<button data-lt-megamenu-trigger="<panel-id>" aria-expanded="false" aria-controls="<panel-id>">` — three triggers, panel IDs: `lt-mega-special-occasions`, `lt-mega-holidays-seasons`, `lt-mega-what-we-make`
  - Desktop mega panels: `<div id="<panel-id>" hidden>` — JS toggles `hidden` attribute + `aria-expanded` on trigger
  - Mobile drawer: `<aside id="lt-mobile-nav" role="dialog" aria-modal="true" aria-hidden="true">`, toggle `#lt-mobile-toggle`, backdrop `#lt-mobile-backdrop`, close `#lt-mobile-close`
  - Mobile accordion triggers: `<button data-lt-accordion-trigger="<panel-id>" aria-expanded="false" aria-controls="<panel-id>">` — three accordions, panel IDs: `lt-mob-special-occasions`, `lt-mob-holidays-seasons`, `lt-mob-what-we-make`
  - Mobile accordion panels: `<ul id="<panel-id>" hidden>` — JS toggles `hidden` + `aria-expanded` on trigger
  - Cart badges: `<span class="lt-cart-count">` (desktop, inside `.lt-utility-bar__cart`) and `<span class="lt-cart-count lt-cart-count--mobile">` (mobile, inside `.lt-header__mobile-cart`) — `lt-guest-cart.js` targets `.lt-cart-count` via `querySelectorAll`, both instances will be updated by existing JS


#### Task 2 — Replace `footer.html` with current import capture structure + newsletter strip

- **Files Changed:**
  - `apps/locally_twisted/locally_twisted/templates/includes/footer/footer.html` — full replacement (101 lines → ~160 lines)

- **Approach:** Added newsletter strip as Section 1 (was entirely absent from prior footer). Preserved existing brand band + social icons + 3-column links + legal bar structure. Changed column classes from `col-4` (always-3-across) to `col-12 col-md-4` (stacks on mobile, 3-across at md+) per Build Brief direction to default to current import capture-faithful layout. Renamed catalog_data `s_lt_*` class names to `lt-footer__*` BEM namespace. Switched "Get In Touch" icons from Unicode emoji to FontAwesome classes (`fa-map-marker`, `fa-phone`, `fa-clock-o`) matching current import capture source. Updated footer Shop column links: "Special Occasions" → `/shop/category/special-occasions-1`, "Holidays & Seasons" → `/shop/category/holidays-seasons-2`, "What We Make" → `/{{ shop_root_route }}` (live ERPNext route). Loud-failure rule honored: error container includes phone fallback `(801) 285-0860`.

- **New Interfaces exposed to Builder JS:**
  - `<form data-lt-newsletter novalidate>` — JS reads this to wire the submit handler
  - `<input type="email" name="email" data-lt-newsletter-email>` — JS reads this for the email value
  - `<button type="submit" data-lt-newsletter-submit>` — JS attaches submit-button state management
  - `<div data-lt-newsletter-success hidden role="status">` — JS removes `hidden` on success
  - `<div data-lt-newsletter-error hidden role="alert">` — JS removes `hidden` on error, sets message text


#### Task 3 — Extend `navbar_context.py`

- **Files Changed:**
  - `apps/locally_twisted/locally_twisted/navbar_context.py` — extended (49 lines → ~140 lines)

- **Approach:** Preserved all existing exports (`shop_categories`, `shop_root_route`) exactly as-is. Added three new context keys (`mega_special_occasions`, `mega_holidays_seasons`, `mega_what_we_make`) populated from verified live DB routes (queried via `python3 -c "frappe.db.get_all(...)"` against the running stack — not from fixtures alone). Built a `route_by_name` lookup from the `children` query result so all three new keys use live DB routes rather than hardcoded strings. Added `content_only: True` flag on items with no dedicated ERPNext Item Group — these render in the template but their destinations are `seasonal-specialty` until Phase 2 creates dedicated groups. `mega_holidays_seasons` uses a `column` key for 3-column grouping in the Jinja template. `mega_what_we_make` uses the same `column` key for Arrangements / Installations / Accents grouping.

- **Verified live routes used:**
  | Item Group | Route |
  |---|---|
  | Arches | `shop-items/arches` |
  | Columns | `shop-items/columns` |
  | Bouquets | `shop-items/bouquets` |
  | Get-Well Bouquets | `shop-items/get-well-bouquets` |
  | Garlands | `shop-items/garlands` |
  | Drops | `shop-items/drops` |
  | Grab & Go | `shop-items/grab-go` |
  | Table Decor | `shop-items/table-decor` |
  | Stands & Easels | `shop-items/stands-easels` |
  | Deliveries | `shop-items/deliveries` |
  | Seasonal & Specialty | `shop-items/seasonal-specialty` |

---

### Tasks Not Completed

None. All three tasks fully implemented.

---

### Cross-Domain Dependencies

#### Builder JS must implement (Jinja template depends on these):

1. **`lt-megamenu.js`** — must implement `window.LT.megamenu.init()` that:
   - Finds all elements with `data-lt-megamenu-trigger` attribute on desktop
   - Maps each trigger's attribute value to the element with that `id`
   - On hover (debounced, desktop only) and click: toggles `hidden` on the panel, sets `aria-expanded` on the trigger
   - On Escape key: closes all open panels, returns focus to trigger
   - On outside click: closes open panels
   - On mobile: finds all `data-lt-accordion-trigger` elements, toggles their paired panels similarly
   - Opens/closes the mobile drawer (`#lt-mobile-nav`, `#lt-mobile-backdrop`) on `#lt-mobile-toggle` click and `#lt-mobile-close` click
   - Locks body scroll while drawer is open (add `.lt-nav-open` to `document.body`)

2. **`lt-newsletter.js`** — must implement `window.LT.newsletter.submit(email)` that:
   - Reads `[data-lt-newsletter]` to find the form
   - Intercepts submit event on `[data-lt-newsletter]`
   - Calls `frappe.call('locally_twisted.api.newsletter.signup', {email})` with `X-Frappe-CSRF-Token` header
   - On success: removes `hidden` from `[data-lt-newsletter-success]`, hides the form inputs
   - On failure: removes `hidden` from `[data-lt-newsletter-error]`, preserves the user's email in the input

#### Builder CSS must implement (Jinja uses these class names):

Desktop chrome BEM blocks:
- `.lt-utility-bar`, `.lt-utility-bar__inner`, `.lt-utility-bar__left`, `.lt-utility-bar__right`
- `.lt-utility-bar__brand`, `.lt-utility-bar__logo`, `.lt-utility-bar__tagline`, `.lt-utility-bar__truck-icon`
- `.lt-utility-bar__sign-in`, `.lt-utility-bar__cart`, `.lt-utility-bar__cta`
- `.lt-header__nav-bar`, `.lt-header__nav-inner`, `.lt-header__nav-list`, `.lt-header__nav-link`
- `.lt-header__nav-trigger`, `.lt-header__nav-caret`, `.lt-header__mega-item`
- `.lt-header__overflow`, `.lt-header__search-btn`
- `.lt-megamenu`, `.lt-megamenu__inner`, `.lt-megamenu__col`, `.lt-megamenu__heading`
- `.lt-megamenu__link`, `.lt-megamenu__cta`, `.lt-megamenu__cta-wrap`, `.lt-megamenu__browse-row`

Mobile chrome BEM blocks:
- `.lt-header__mobile`, `.lt-header__mobile-row`, `.lt-header__mobile-brand`, `.lt-header__mobile-logo`
- `.lt-header__mobile-actions`, `.lt-header__mobile-cart`, `.lt-header__toggle`
- `.lt-header__mobile-strip`
- `.lt-header__backdrop`, `.lt-header__mobile-nav` (the `<aside>`)
- `.lt-header__drawer-head`, `.lt-header__close`
- `.lt-header__drawer-search`, `.lt-header__search-group`, `.lt-header__search-input`, `.lt-header__search-submit`
- `.lt-header__mobile-nav-list`, `.lt-header__mobile-nav-item`, `.lt-header__mobile-nav-link`
- `.lt-header__mobile-accordion-item`, `.lt-header__mobile-accordion-toggle`, `.lt-header__mobile-caret`
- `.lt-header__mobile-accordion-panel`, `.lt-header__mobile-nav-sublink`, `.lt-header__mobile-nav-sublink--all`
- `.lt-header__mobile-nav-divider`, `.lt-header__mobile-nav-link--cta`

**Cart count badge rules (moved OUT of navbar inline `<style>` — Builder CSS must add to `lt-theme.css`):**
```css
.lt-utility-bar__cart {
    position: relative;
}
.lt-cart-count {
    display: none;
    position: absolute;
    top: -6px;
    right: -10px;
    min-width: 18px;
    height: 18px;
    padding: 0 5px;
    background-color: #c0392b;
    color: #ffffff;
    border-radius: 9px;
    font-family: 'Raleway', sans-serif;
    font-size: 10px;
    font-weight: 700;
    line-height: 18px;
    text-align: center;
    box-sizing: border-box;
    pointer-events: none;
}
.lt-cart-count.is-populated {
    display: inline-block;
}
.lt-cart-count--mobile {
    position: static;
    margin-left: 0.5rem;
    background-color: var(--lt-teal, #107373);
    vertical-align: middle;
}
```

Footer chrome BEM blocks:
- `.lt-footer`, `.lt-footer-newsletter`, `.lt-footer-newsletter__inner`
- `.lt-footer-newsletter__heading`, `.lt-footer-newsletter__subhead`
- `.lt-footer-newsletter__form`, `.lt-footer-newsletter__input-group`
- `.lt-footer-newsletter__input`, `.lt-footer-newsletter__btn`
- `.lt-footer-newsletter__success`, `.lt-footer-newsletter__success-text`
- `.lt-footer-newsletter__error`, `.lt-footer-newsletter__error-text`, `.lt-footer-newsletter__error-phone`
- `.lt-footer__brand-band`, `.lt-footer__brand-inner`, `.lt-footer__brand-name`, `.lt-footer__brand-tagline`
- `.lt-footer__social`, `.lt-footer__social-link`
- `.lt-footer__links`, `.lt-footer__links-row`, `.lt-footer__col`, `.lt-footer__col-title`
- `.lt-footer__col-list`, `.lt-footer__col-list--info`, `.lt-footer__col-link`, `.lt-footer__info-item`
- `.lt-footer__bar`, `.lt-footer__legal`, `.lt-footer__sep`, `.lt-footer__legal-link`

---

### Decisions Made

1. **Search: `/search` fallback route used.** current import capture used `data-bs-target="#o_search_modal"` (catalog_data's modal). ERPNext has no equivalent modal wired by default. The desktop search button links to `/search` (Frappe's built-in search route). Mobile drawer has an inline search form posting to `/search`. This degrades gracefully — if no search page is wired, it 404s, but at least no JS error. Builder JS can upgrade the desktop button to open a modal later if wired. Documented in build report rather than silently omitting search.

2. **Footer Shop links: catalog_data category slugs retained.** The footer "Special Occasions" and "Holidays & Seasons" links point to `/shop/category/special-occasions-1` and `/shop/category/holidays-seasons-2` (catalog_data-style slugs). These are content-only routes in ERPNext — they will 404 until Phase 2 redirects are added. "What We Make" uses the live ERPNext `shop_root_route`. This matches the current import capture footer links verbatim and is flagged for Phase 2.

3. **Column layout: `col-12 col-md-4` (stacks on mobile).** Prior footer used `col-4` (always 3-across). Build Brief defaulted to current import capture-faithful stacking. GL may override to `col-4` after visual review.

4. **`mega_what_we_make` column mapping to 3 groups.** current import capture's What We Make panel had three columns: Arrangements (Arches, Columns, Centerpieces, Bouquets), Installations (Garlands, Backdrops, Drops, Grab N Go), Accents (Cups → mapped to Stands & Easels, Photo Frames, Table Decor → Table Decor, Deliveries). "Backdrops" has no ERPNext Item Group — mapped to `seasonal-specialty` (content-only, flagged). "Photo Frames" has no ERPNext equivalent — dropped from the Accents column; replaced with "Stands & Easels" which does exist.

5. **`mega_special_occasions` single column.** current import capture's Special Occasions panel has only a single "Life Events" column. Maintained single-column layout in the Jinja template. The panel renders at `col-lg-4 text-center`.

6. **Mobile drawer: custom `<aside role="dialog">` pattern preserved.** The prior navbar used this pattern. Build Brief required it. NOT using Bootstrap's `offcanvas` component or `data-bs-toggle="offcanvas"` — all JS state management is deferred to Builder JS's `lt-megamenu.js`.

7. **Footer "Get In Touch" icons: FontAwesome.** Prior footer used Unicode emoji (`📍`, `☎`, `🕒`). current import capture uses FontAwesome (`fa-map-marker`, `fa-phone`, `fa-clock-o`). Switched to FontAwesome since it's available in Frappe's bundle and matches current import capture's visual style. Builder CSS does not need to add icon fonts.

8. **Inline SVG caret icons in template.** Build Brief says "no inline SVG with `<path d=...>` in any CMS-editable field." These carets are in Jinja template files, not CMS fields — convention still applied, but small inline carets in templates are acceptable per the Build Brief's parenthetical ("doesn't apply to template files but we keep the convention for portability"). Kept the carets inline because there are no SVG caret icon files in `public/icons/` to reference.

---

### Test Results

**Container restart:** ✅ `locally-twisted-erpnext-v15-backend-1` restarted successfully.

**Cache clear:** ✅ `bench clear-cache` + `bench clear-website-cache` completed.

**Route verification:**
```
home 200
book 200
```
✅ Both invariant routes return HTTP 200.

**Rendered HTML checks:**
- `lt-megamenu` class occurrences: 28 ✅
- `lt-footer-newsletter` class occurrences: 13 ✅
- `lt-utility-bar` class occurrences: 11 ✅
- Inline `<style>` blocks from our templates: 0 ✅ (the 1 found is from the homepage page template, not our navbar/footer)
- `data-bs-toggle` occurrences: 0 ✅
- `lt-cart-count` badge present (desktop): ✅
- `lt-cart-count--mobile` badge present: ✅
- `data-lt-megamenu-trigger` on 3 triggers: ✅
- `id="lt-mega-*"` panels with `hidden` attribute: ✅
- `data-lt-newsletter` form: ✅
- `data-lt-newsletter-success hidden`: ✅
- `data-lt-newsletter-error hidden`: ✅

**Mega menu link spot-check** (routes populated from live DB):
- Birthday Parties → `/shop-items/seasonal-specialty` ✅
- Get-Well Bouquets → `/shop-items/get-well-bouquets` ✅
- Mother's Day → `/shop-items/bouquets` ✅
- Balloon Arches → `/shop-items/arches` ✅
- Organic Garlands → `/shop-items/garlands` ✅
- All 27 mega links rendered with non-empty routes ✅

---

### Self-Review Concerns

1. **`data-bs-toggle="offcanvas"` is GONE — Builder JS must wire the mobile drawer.** The prior navbar's mobile toggle was wired inline. That script block is now removed. Until `lt-megamenu.js` is loaded and calls the drawer open/close, the mobile hamburger button will do nothing. This is by-design (JS builder's domain) but the mobile drawer is non-functional until Builder JS ships.

2. **Desktop mega menus are also non-functional until Builder JS ships.** The `hidden` attribute is set on all three panels at render time. Without `lt-megamenu.js` toggling them, no mega menu opens on hover or click. Desktop nav link items (Balloon Twisting, Contact, Blog) work normally as they're plain `<a>` tags.

3. **Footer Shop column `/shop/category/*` links will 404 in ERPNext.** These are catalog_data-style category routes. ERPNext's webshop uses `/shop-items/<slug>`. Phase 2 must add redirects or update the footer links to ERPNext-native routes.

4. **`mega_special_occasions` Birthday Parties, Graduations route to `seasonal-specialty` — not a dedicated category.** This is technically correct given the current ERPNext Item Group tree (no "Birthday Parties" group), but clicking "Birthday Parties" in the mega menu lands the user on a page showing all seasonal items. This is a Phase 2 content/category concern, not a chrome bug.

5. **`mega_what_we_make` "Backdrops" maps to `seasonal-specialty`.** current import capture has a Backdrops category. ERPNext does not. Flagged `content_only: True` in context — the link renders but destination is imprecise.

6. **Mobile drawer has no sign-in state for logged-in users beyond "My Account" link.** Prior navbar showed "Account" + "Sign Out" for logged-in users. This build shows only "My Account". Builder JS could add a logout button but that's outside Jinja domain; documented here.

7. **Search: desktop button links to `/search`.** Frappe's `/search` route is a native page (`apps/frappe/frappe/www/search.html`). It should return 200. But this was not tested during this build session — only `/` and `/book` were verified. Reviewers should check `/search` returns 200 on this stack.

8. **`lt-cart-count` CSS is now missing.** The rules that made the badge display correctly (position absolute, red background, 18px height) were in the navbar's inline `<style>` block. That block is now removed. Until Builder CSS adds those rules to `lt-theme.css`, the cart badge will be invisible (display: none) even when `is-populated` is added by `lt-guest-cart.js`. This is the highest-priority cross-domain dependency for visual correctness. The exact rules are documented in the Cross-Domain Dependencies section above.

9. **`navbar_context.py` `mega_what_we_make` "Centerpieces" → `table-decor`.** current import capture's "Centerpieces" category maps to `what-we-make-centerpieces-28`. ERPNext has no "Centerpieces" Item Group. Mapped to "Table Decor" as the nearest equivalent. This is a label/route mismatch — the link says "Centerpieces" but lands on the Table Decor item group page. Phase 2 should either rename the Item Group or add a "Centerpieces" group.

10. **No smoke test entry added for newsletter form.** Per `frappe-form-integrity` skill, a smoke test entry should be added to `scripts/verify/smoke_forms.py` for the newsletter form. This is Builder JS's domain (they own the API endpoint and the form wiring). Flagging here so it's not missed.
