# Builder CSS Build Report — Round 1
## Date: 2026-04-30
## Builder: Builder CSS (Opus 4.7)

---

### Tasks Completed

---

**Task: Remove dead CSS code (legacy `.navbar.*` block)**
- **Files Changed:** `apps/locally_twisted/locally_twisted/public/css/lt-theme.css`
- **Lines Deleted:** The block began at the `/* Phase 1, Slice 2 — Header + Footer */` section comment (originally line 293) and ran through the `.navbar`, `.navbar-brand`, `.navbar-nav`, `.navbar-toggler`, `.dropdown-menu`, `.dropdown-item`, `.dropdown-toggle`, and mobile `.navbar-collapse` rules. Approximately 172 lines removed.
- **Approach:** The `.navbar.*` selectors targeted Frappe's native navbar markup, which no longer renders — the Jinja partial override (`navbar.html`) replaced it wholesale. All `!important` flags in this block (`.navbar { background-color !important }`, `.navbar-brand { color !important }`, `.navbar-nav .nav-link { color !important }`, `.navbar-brand img.lt-logo { height !important; width !important }`) are now gone. The `prefers-reduced-motion` block at lines ~198-207 was NOT in this dead zone and was preserved intact.
- **Boundary decision:** The section comment `/* Phase 1, Slice 2 — Header + Footer */` was also deleted since the BEM replacement section has its own comment at the header block below.

---

**Task: Remove dead CSS code (legacy `.web-footer` block)**
- **Files Changed:** `apps/locally_twisted/locally_twisted/public/css/lt-theme.css`
- **Lines Deleted:** The `.web-footer` block originally ran from ~line 466 to ~line 639, approximately 174 lines.
- **Approach:** The `.web-footer` selector targets Frappe's native footer markup, which no longer renders — the footer Jinja partial override replaces it wholesale. All rules deleted: `.web-footer {}`, the `padding-top: 4rem` media query, column-title/link/list rules, `.web-footer .footer-info`, `.web-footer .footer-powered { display: none !important }`, subscribe row rules, and the mobile stacking media query.
- **Boundary decision — CRITICAL:** Lines 484-533 of the original file (`.lt-section .container`, `.web-page-content .container`, `.page-content-wrapper .container`, `.product-container`, `.cart-container`) appeared INSIDE the `.web-footer` section comment boundary but were NOT `.web-footer` selectors. These are live structural rules that control the full-bleed layout across every page and the webshop product/cart container centering. They were **preserved**. The dead-code boundary was split into two separate deletions to preserve this live block.
- **One preserved `!important`:** The legacy `.web-footer .footer-powered { display: none !important }` is now gone along with the rest of the block. The only remaining `!important` instances in the file are the documented exceptions: (a) the `prefers-reduced-motion` block (lines ~198-207), (b) `.product-list .product-code { display: none !important }` (webshop jargon suppression, ~line 1373). Both are correct per Build Brief §"Hard constraints" item 1.

---

**Task: Add `.lt-cart-count` rules (moved from navbar.html inline `<style>`)**
- **Files Changed:** `apps/locally_twisted/locally_twisted/public/css/lt-theme.css`
- **Lines Added:** ~40 lines appended after the existing `.lt-by-cat` blocks
- **Approach:** Read `navbar.html` lines 141-176 to extract the exact inline `<style>` rules. The block defined `.lt-header__util-link--cart { position: relative }`, `.lt-cart-count` (hidden badge, absolute position, red background), `.lt-cart-count.is-populated` (show when populated), and `.lt-cart-count--mobile` (static inline variant for the drawer). All four rules are now in `lt-theme.css` under a clearly labeled section. The inline `<style>` block in `navbar.html` still exists — Builder Jinja owns that file and is responsible for removing it per the build brief. This CSS file now provides the canonical source of those rules regardless of whether the template block has been deleted yet.
- **New Interfaces:** `#lt-cart-count` (desktop badge) and `.lt-cart-count--mobile` (drawer) both depend on `.lt-cart-count.is-populated` being toggled by `lt-guest-cart.js`. No change to the JS interface — CSS only.

---

**Task: Add newsletter strip BEM blocks**
- **Files Changed:** `apps/locally_twisted/locally_twisted/public/css/lt-theme.css`
- **Lines Added:** ~190 lines appended
- **Approach:** Added complete BEM blocks for:
  - `.lt-footer-newsletter` — wrapper with blush-tint background, centered, responsive padding
  - `.lt-footer-newsletter__heading` — DM Serif Display, weight 400 (per constraint: no `font-weight` override on single-weight heading fonts), responsive size 1.5rem → 1.875rem
  - `.lt-footer-newsletter__subhead` — Raleway, soft-gray
  - `.lt-footer-newsletter__form` — flex row with `gap: 0.5rem` (explicit CSS, not BS5 `gap-*` utility)
  - `.lt-footer-newsletter__input` — blush-tint background, min-height 44px, focus-visible with teal outline
  - `.lt-footer-newsletter__button` — teal primary, 44px min-height, hover darkens to `#006666` (pre-computed hex, no `color-mix()`)
  - `.lt-footer-newsletter__error` — red feedback, user-visible with colored border (Loud Failure rule compliance)
  - `.lt-footer-newsletter__success` — green feedback
  - Both feedback states use `[hidden]` attribute to hide (`display: none` on `[hidden]`), matching Builder JS's toggle pattern
  - `.lt-footer-bar`, `.lt-footer-bar__legal`, `.lt-footer-bar__link` — legal/copyright bar
- **Loud Failure compliance:** Error state is visually distinct (red background, red border, red text). Builder JS must set the error message content to include the phone number fallback `(801) 285-0860` per the Loud Failure rule — that's a JS responsibility, not CSS.

---

**Task: Bump cache-bust version**
- **Files Changed:** `apps/locally_twisted/locally_twisted/hooks.py` — single line
- **Change:** `?v=20260430-3` → `?v=20260430-4`
- **Approach:** Single-line edit. Did NOT touch `web_include_js` line (Builder JS owns that). Did not touch any other line in hooks.py.

---

### Tasks Not Completed

**BEM blocks the build brief listed but already existed:** The build brief's Task 2 listed a large set of `.lt-header` and `.lt-footer` BEM blocks to add. On reading the current `lt-theme.css` before any edits, these blocks were already present from a prior build session (the 2026-04-30 mega menu and footer build). Specifically already present:
- All `.lt-header__*` blocks (utility bar, brand, nav, mobile, drawer, backdrop, mega menu, accordion) — lines ~352-1080 of the pre-edit file
- All `.lt-footer__*` blocks (brand-band, social, columns, bar, sep) — lines ~980-1175 of the pre-edit file

These were preserved intact. Adding them again would have created duplicate selectors. Build report is honest about what was actually written vs what pre-existed.

**Builder Jinja's inline `<style>` removal:** The `<style>` block in `navbar.html` lines 141-176 still exists. I extracted its rules into `lt-theme.css` (done). Removing the `<style>` block from `navbar.html` is Builder Jinja's domain — I did not touch that file.

---

### Cross-Domain Dependencies

**Builder Jinja must:**
- Remove the inline `<style>` block from `navbar.html` lines 141-176. The CSS rules it contains are now canonical in `lt-theme.css`. Leaving the inline block is harmless (inline styles load after `web_include_css` so there's no cascade conflict), but it violates Build Brief constraint §5 and creates a maintenance split.
- Ensure footer.html uses `.lt-footer-newsletter`, `.lt-footer-newsletter__heading`, etc. for the newsletter strip, and `.lt-footer-bar`, `.lt-footer-bar__legal`, `.lt-footer-bar__link` for the legal bar. These are the class names this CSS provides.

**Builder JS must:**
- When toggling newsletter error/success states: set `element.removeAttribute('hidden')` (not `element.style.display = 'block'`) — the CSS hides via `[hidden]` attribute, not a class.
- Include `(801) 285-0860` in the error message text for Loud Failure compliance.
- For the `web_include_js` line in hooks.py: add the two new JS files. The `web_include_css` line is now `?v=20260430-4` — do not touch it.

**lt-guest-cart.js (existing, no changes needed):**
- Continues to call `paintBadges()` which sets `.lt-cart-count.is-populated`. The CSS now properly covers both the desktop badge (`position: absolute`) and mobile variant (`position: static`). No JS changes needed.

---

### Decisions Made

1. **Split deletion, not contiguous wipe.** The "dead code" from lines ~293-639 was not uniformly dead — the `.lt-section .container` / `.page-content-wrapper` / `.product-container` structural rules sat in the middle (originally written under the `.web-footer` section comment but not `.web-footer` selectors). Wiping lines 293-639 wholesale would have deleted live layout rules. Split into two targeted deletions preserving the structural block.

2. **Section comment also deleted.** The `/* Phase 1, Slice 2 — Header + Footer */` section header comment at line 293 was deleted with the dead code. The BEM blocks that replaced the dead code already have their own well-labeled section comments. Keeping the old comment would have been confusing (it would precede live structural rules, not a header/footer section).

3. **`.lt-footer-newsletter__heading` uses `font-weight: 400` (implicit via inheritance from the global `h1-h3` rule).** The heading class sets `font-family: 'DM Serif Display'` and size, but does NOT set `font-weight`. This is correct per constraint §6 (no `font-weight` override on DM Serif Display classes).

4. **Newsletter feedback `[hidden]` toggle vs class toggle.** Used `element[hidden] { display: none }` CSS pattern (matches Builder JS contract which uses `hidden` attribute). Consistent with how the mega menu panel and drawer accordion panels already work in this codebase.

5. **`color-mix()` not used anywhere.** Hover darkening of teal (`#008080` → `#006666`) is a pre-computed hex. Consistent with existing codebase pattern (the same `#006666` value already appears 3 times in `lt-theme.css` for `.btn-primary:hover`).

6. **`gap` written as explicit CSS property.** `.lt-footer-newsletter__form { gap: 0.5rem }` — explicit CSS, not a Bootstrap 5 `gap-*` utility. Consistent with constraint §3.

---

### Test Results

```
docker restart locally-twisted-erpnext-v15-backend-1
→ Container restarted

clear_website_cache.py
→ "Done. Next page request will re-resolve templates and re-render."

curl -I "http://localhost:8081/assets/locally_twisted/css/lt-theme.css?v=20260430-4"
→ HTTP/1.1 200 OK  Content-Type: text/css  Content-Length: 46644

curl "http://localhost:8081/" | grep "lt-theme.css?v="
→ <link type="text/css" rel="stylesheet" href="/assets/locally_twisted/css/lt-theme.css?v=20260430-4">

curl home → 200
curl book → 200

grep dead selectors (.navbar, .web-footer) → zero matches
grep new selectors (.lt-cart-count, .lt-footer-newsletter, .lt-footer-bar) → all present
```

Final file: **1,841 lines** (was 1,898 before this build; net -57 lines after deletions + additions).

---

### Self-Review Concerns

1. **Inline `<style>` still in navbar.html.** I verified and extracted the rules. The template block is Builder Jinja's to remove. Until they remove it, the badge styles exist in two places — no functional conflict, but reviewers should flag it for Builder Jinja's attention.

2. **`.lt-footer-bar` vs `.lt-footer__bar`.** The existing BEM footer already has `.lt-footer__bar` (double-underscore, child of `.lt-footer`). I added `.lt-footer-bar` (single-hyphen, a top-level block) as the alias matching Hetzner's markup classes. If Builder Jinja uses `.lt-footer__bar` in the template, these new `.lt-footer-bar` rules won't apply. The Architect reviewer should verify which class name Builder Jinja actually uses in `footer.html` and confirm one of the two is redundant (the existing `.lt-footer__bar` handles the same visual treatment; these new aliases may be unnecessary if Builder Jinja reuses the existing classes).

3. **Newsletter strip `prefers-reduced-motion`.** I added a `@media (prefers-reduced-motion: reduce)` block at the end that sets `transition: none` on `.lt-footer-newsletter__button` and `.lt-header__util-link--cart`. The existing reduced-motion block at lines ~198-207 uses `!important` on `transition-duration: 0.01ms` which is a global catch-all — it already covers these elements. My additional block is technically redundant but explicit. Reviewers may flag it as a lint concern; it is harmless.

4. **No visual verification.** I ran HTTP checks and confirmed classes exist in the file. I did not run a Playwright screenshot to verify the newsletter strip renders correctly because Builder Jinja has not yet added the newsletter HTML to `footer.html`. The CSS will be dead (no matching elements) until Builder Jinja ships their work. This is the correct build sequence — CSS first, template second.
