# Builder Jinja Fix Report — Fix Round
## Date: 2026-04-30
## Builder: Builder Jinja

---

### Tasks Completed

#### Task A1 — Mobile drawer `<aside>` class rename
- **Files Changed:** `apps/locally_twisted/locally_twisted/templates/includes/navbar/navbar.html` line 381
- **BEFORE:** `class="lt-header__mobile-nav"`
- **AFTER:** `class="lt-header__mobile-nav-collapse"`
- **CSS confirmation:** `lt-theme.css:556` has `.lt-header__mobile-nav-collapse { position:fixed; transform:translateX(100%); visibility:hidden; … }` and `:574` has `.lt-header__mobile-nav-collapse.is-open { … }`. Grep for `.lt-header__mobile-nav\b` in lt-theme.css returns zero matches outside compound selectors — the old name had no rules. Rename is correct.
- **Approach:** Straight class swap on the single `<aside>` element. The JS adds/removes `is-open` on the element it finds by `id="lt-mobile-nav"`, which is unchanged — no JS edit required for this fix.

#### Task A2 — Mega `<li>` wrapper class rename (all three)
- **Files Changed:** `navbar.html` lines 117, 161, 223
- **BEFORE:** `class="lt-header__mega-item"` (3 occurrences)
- **AFTER:** `class="lt-header__has-mega"` (3 occurrences)
- **CSS confirmation:** `lt-theme.css:908` has `.lt-header__has-mega { position: relative }`. `lt-theme.css:928` has `.lt-header__has-mega.is-open .lt-header__nav-trigger { color: var(--lt-teal) }`. `lt-theme.css:942` has `.lt-header__has-mega.is-open .lt-header__nav-caret { … }`. Grep for `lt-header__mega-item` in lt-theme.css returns zero results — confirmed no rules existed for the old name. All three `<li>` elements renamed individually to avoid risk of unintended replace_all.

#### Task A3 — Mega panel outer `<div>` class rename (all three panels)
- **Files Changed:** `navbar.html` lines 137, 181, 243
- **BEFORE:** `class="lt-megamenu"` (3 occurrences on outer panel divs)
- **AFTER:** `class="lt-header__mega"` (3 occurrences)
- **CSS confirmation:** `lt-theme.css:947` has `.lt-header__mega { position:absolute; top:calc(100% + 0.5rem); background:…; box-shadow:…; z-index:1000 }`. `lt-theme.css:963` has `.lt-header__mega[hidden] { display:none }`. `lt-theme.css:966` has `.lt-header__has-mega.is-open .lt-header__mega:not([hidden]) { … }`. Grep for `.lt-megamenu` in lt-theme.css returns zero results — confirmed no CSS existed for the old name.
- **Approach:** Used `replace_all: true` for `class="lt-megamenu"` since all three occurrences are identical outer panel divs. Child classes (`lt-megamenu__inner`, `lt-megamenu__col`, `lt-megamenu__heading`, `lt-megamenu__link`, `lt-megamenu__cta`, `lt-megamenu__browse-row`) were NOT renamed — those are Builder CSS's domain; the CSS has `lt-header__mega-inner` and `lt-header__mega-link` but the child class alignment between template and CSS is a separate issue for Builder CSS to address. This fix round only aligns the outer panel class as assigned.

#### Task A4 — Cart link class rename
- **Files Changed:** `navbar.html` line 86
- **BEFORE:** `class="lt-utility-bar__cart"`
- **AFTER:** `class="lt-header__util-link--cart"`
- **CSS confirmation:** `lt-theme.css:1611` has `.lt-header__util-link--cart { position: relative }` (the positioning context that contains the `lt-cart-count` badge). `lt-theme.css:1838` also references `.lt-header__util-link--cart` in the reduced-motion block. Grep for `lt-utility-bar__cart` in lt-theme.css returns zero results — confirmed the old name had no rules.
- **Note:** The broader `lt-utility-bar__*` namespace mismatch (F005 — no CSS for the utility bar structure classes) is Builder CSS's domain. This fix only addresses the cart link's `position: relative` ancestor requirement.

#### Task A5 — Primary nav bar wrapper class rename
- **Files Changed:** `navbar.html` lines 105–106
- **BEFORE:** `class="lt-header__nav-bar"` (outer div) and `class="container lt-header__nav-inner"` (inner div)
- **AFTER:** `class="lt-header__nav"` (outer div) and `class="container lt-header__nav-row"` (inner div)
- **CSS confirmation:** `lt-theme.css:452` has `.lt-header__nav { background-color: var(--lt-white); … }`. `lt-theme.css:456` has `.lt-header__nav-row { display:flex; align-items:center; … }`. Grep for `lt-header__nav-bar` in lt-theme.css returns zero results. Grep for `lt-header__nav-inner` in lt-theme.css returns zero results.

#### Task B — Accordion trigger data-attribute rename (all three)
- **Files Changed:** `navbar.html` lines 443, 473, 503
- **BEFORE:** `data-lt-accordion-trigger="lt-mob-*"` (3 occurrences)
- **AFTER:** `data-lt-drawer-accordion-trigger="lt-mob-*"` (3 occurrences)
- **JS confirmation:** `lt-megamenu.js:415` queries `[data-lt-drawer-accordion-trigger]`. With this rename, the new-API path in the JS now finds all three accordion buttons. The legacy `querySelector` singular fallback path (which was binding only the first button) becomes unreachable for the new-API elements, fixing accordions 2 and 3.
- **Approach:** Used `replace_all: true` on the attribute name string. All three occurrences correctly updated. The comment in the Jinja file header at line 31 already used the correct `data-lt-drawer-accordion-trigger` name (it was the template element that was wrong, not the comment).

#### Task C — Newsletter button class rename
- **Files Changed:** `apps/locally_twisted/locally_twisted/templates/includes/footer/footer.html` line 67
- **BEFORE:** `class="lt-footer-newsletter__btn btn btn-primary"`
- **AFTER:** `class="lt-footer-newsletter__button btn btn-primary"`
- **CSS confirmation:** `lt-theme.css:1723` has `.lt-footer-newsletter__button { … }`. `lt-theme.css:1738` has hover/focus-visible rules. `lt-theme.css:1751` has disabled-state rule. Grep for `lt-footer-newsletter__btn\b` in lt-theme.css returns zero results — confirmed old name had no custom rules.

#### Task D — `book.html` Esc-key guard
- **Files Changed:** `apps/locally_twisted/locally_twisted/www/book.html` lines 854–858
- **BEFORE:**
  ```javascript
  document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') dismissModal();
  });
  ```
- **AFTER:**
  ```javascript
  document.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape') return;
      var modal = document.getElementById('received');
      if (!modal || !modal.classList.contains('lt-book__modal--open')) return;
      dismissModal();
  });
  ```
- **Approach:** Guard reads the modal element by its known id (`received`) and checks for `lt-book__modal--open` — the same class that `showModal()` adds at line 835 and that is the canonical open-state marker. `dismissModal()` only fires when the modal is actually open. Esc on the desktop mega menu (or anywhere on the /book page before form submission) no longer navigates to `/`.
- **CSS confirmation:** `lt-theme.css:250` (within book.html inline `<style>`) confirms `.lt-book__modal--open` is the correct open-state class name.

---

### Tasks Not Completed

None. All 7 assigned renames + the Esc guard are complete.

---

### Cross-Domain Dependencies

**Builder CSS still needs to address:**
- The `lt-megamenu__*` child class names in the template do not match the CSS's `lt-header__mega-*` child class names. This is outside my domain — I only renamed the outer panel class. Builder CSS should either rename the CSS child rules to `lt-megamenu__*` or the template child classes to `lt-header__mega-*`. The outer panel now correctly resolves as `.lt-header__mega`, so CSS layout/positioning works; the inner content styling (link hover colors, column layout within the panel) depends on this child-class alignment.
- The `lt-utility-bar__*` namespace (breadth of F005) — the utility bar structural elements (`lt-utility-bar`, `lt-utility-bar__inner`, `lt-utility-bar__left`, `lt-utility-bar__brand`, etc.) still have no CSS rules. Only the cart link was in my domain. Builder CSS needs to add rules for the full utility bar namespace or rename those template classes to the existing `lt-header__utility*` names.

---

### Decisions Made

1. **Task A3 — outer panel only.** The assignment says rename `lt-megamenu` panel class. I did exactly that — outer `<div class="lt-megamenu">` → `<div class="lt-header__mega">`. Child classes (`lt-megamenu__inner` etc.) were not touched because (a) they are not in the synthesis assignment, (b) touching them without knowing whether Builder CSS added `lt-megamenu__*` rules or `lt-header__mega-*` rules would risk breaking things. The child class alignment is cross-domain and noted above for Builder CSS.

2. **Task A4 — cart only, not full utility bar.** The synthesis assigns only the cart link to Jinja. The rest of the utility bar namespace is F005 and assigned to Builder CSS. I didn't touch `lt-utility-bar`, `lt-utility-bar__inner`, etc.

3. **Task B — replace_all safe.** The string `data-lt-accordion-trigger` is unique enough that replace_all is safe — it only appears on the three mobile accordion `<button>` elements, not on any other element. Confirmed correct by post-edit grep output.

---

### Test Results

**Route smoke test (Task E):**
```
home 200
book 200
```
Both routes return HTTP 200 after backend restart + cache clear + frontend restart.

**Live rendered HTML verification:**
All 7 renamed class/attribute names confirmed present in `curl http://localhost:8081/` output:
- `class="lt-header__util-link--cart"` ✅
- `class="lt-header__nav"` ✅
- `class="lt-header__nav-row"` ✅
- `class="lt-header__has-mega"` (3 × `<li>`) ✅
- `class="lt-header__mega"` (3 × panel `<div>`) ✅
- `class="lt-header__mobile-nav-collapse"` (`<aside>`) ✅
- `data-lt-drawer-accordion-trigger` (3 × accordion `<button>`) ✅
- `class="lt-footer-newsletter__button"` ✅

**Stale-name confirmation:** grep for old names (`lt-header__mega-item`, `lt-header__mobile-nav"`, `lt-header__nav-bar`, `lt-header__nav-inner`, `data-lt-accordion-trigger\b`, `lt-utility-bar__cart`, `lt-megamenu"`, `lt-footer-newsletter__btn\b`) returns zero results in the modified files.

---

### Self-Review Concerns

1. **Child class mismatches in mega panels remain.** The template uses `lt-megamenu__inner`, `lt-megamenu__col`, `lt-megamenu__heading`, `lt-megamenu__link`, `lt-megamenu__cta`, `lt-megamenu__browse-row` inside the panels. The CSS has `lt-header__mega-inner` and `lt-header__mega-link`. This is not my task but it will affect panel content styling. Builder CSS needs to reconcile.

2. **Utility bar structural classes still unmatched.** The template's `lt-utility-bar`, `lt-utility-bar__inner`, `lt-utility-bar__left`, `lt-utility-bar__brand`, `lt-utility-bar__logo`, `lt-utility-bar__tagline`, `lt-utility-bar__right`, `lt-utility-bar__sign-in`, `lt-utility-bar__cta` all have zero CSS rules. This is F005, Builder CSS's domain.

3. **Esc guard in book.html is correct and confirmed safe.** The guard checks `classList.contains('lt-book__modal--open')` which is exactly the class `showModal()` adds. The guard does not affect the click-close or backdrop-click paths — those are wired inside `showModal()` after the class is added. No regression risk.

4. **No renames made that weren't needed.** I verified each of the 7 items against the CSS before renaming. None of the new names were invented — all were taken directly from grep output confirming matching CSS rules exist.
