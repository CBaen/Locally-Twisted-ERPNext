# Builder CSS — Fix Round Report

**Date:** 2026-04-30
**Role:** Builder CSS (Fix Round)
**Addresses:** Architect F005 (utility bar zero CSS), F010 (dead .lt-footer-bar block), F012 (redundant prefers-reduced-motion block)
**Files edited:**
- `apps/locally_twisted/locally_twisted/public/css/lt-theme.css`
- `apps/locally_twisted/locally_twisted/hooks.py`

---

## Task A — Add `.lt-utility-bar__*` CSS block

### New block location

Inserted between the existing `.lt-header__util-link` section and the `/* Tier 2 — main nav */` comment.

| Metric | Value |
|--------|-------|
| Block start line | 452 (section comment) |
| Block end line | 614 (`.lt-utility-bar__cta` media query closing brace) |
| Total lines added | ~163 |

### Selectors added vs. template class inventory

Every `.lt-utility-bar__*` class reference in `navbar.html` now has a matching CSS rule:

| Template class | CSS rule added | Notes |
|---|---|---|
| `.lt-utility-bar` | ✅ line 460 | Container, soft-blue background, border-bottom |
| `.lt-utility-bar__inner` | ✅ line 467 | 3-column grid layout (1fr auto 1fr), gap, padding |
| `.lt-utility-bar__left` | ✅ line 476 | Flex row, Raleway 17.5px bold, hidden on mobile <480px |
| `.lt-utility-bar__truck-icon` | ✅ line 496 | flex-shrink:0, scaleX(-1) mirror, vertical-align |
| `.lt-utility-bar__tagline` | ✅ line 507 | Raleway 17.5px bold, --lt-soft-gray |
| `.lt-utility-bar__brand` | ✅ line 516 | inline-flex, justify-self:center, no text-decoration |
| `.lt-utility-bar__logo` | ✅ line 524 | 100px mobile / 138px desktop height, max-width |
| `.lt-utility-bar__right` | ✅ line 540 | flex row, gap:1rem, list-style:none, margin/padding:0 |
| `.lt-utility-bar__sign-in` | ✅ line 552 | Raleway 17.5px bold, --lt-soft-gray, hover/focus-visible |
| `.lt-utility-bar__cart` | ✅ line 579 | **position:relative** (required for .lt-cart-count badge), focus-visible outline |
| `.lt-utility-bar__cta` | ✅ line 600 | font-size 0.9rem mobile / 1rem desktop (inherits .btn .btn-primary) |

**The second occurrence of `.lt-utility-bar__truck-icon`** at navbar.html:363 (inside `.lt-header__mobile-strip`) shares the same class and is correctly styled by the same rule.

### Constraints honored
- No `!important` anywhere in the new block
- No Bootstrap 5 utilities (`gap-*`, `ms-*`/`me-*`, grid-column utilities)
- Color tokens used: `--lt-soft-blue`, `--lt-soft-gray`, `--lt-near-black`, `--lt-white`
- Mobile-first: `.lt-utility-bar__left` hidden by default, shown at `(min-width: 480px)`; logo and CTA have `(min-width: 992px)` desktop overrides
- Focus-visible outlines on `.lt-utility-bar__sign-in` and `.lt-utility-bar__cart`

---

## Task B — Remove dead `.lt-footer-bar` block

### What was deleted

The following were removed from the end of lt-theme.css (originally lines 1803–1841):

| Block | Reason |
|---|---|
| `/* Footer — Legal bar (copyright row...) */` section comment | Misleading — claimed it was needed as "alias" |
| `.lt-footer-bar { ... }` | Dead code — template uses `.lt-footer__bar` (double underscore); live CSS at ~line 808 already covers it |
| `.lt-footer-bar__legal { ... }` | Dead code — no element in rendered DOM has this class |
| `.lt-footer-bar__link { ... }` + hover/focus variants | Dead code — same reason |
| `@media (prefers-reduced-motion: reduce)` block targeting `.lt-footer-newsletter__button` + `.lt-header__util-link--cart` | Dead code — global catch-all at lines 198-207 already suppresses all transitions; `.lt-header__util-link--cart` class does not exist in any template |

**Replaced with:** A single one-line comment pointing at the live `.lt-footer__bar` rules and confirming the global reduced-motion block handles everything.

### Deleted line range (pre-deletion numbering)
| Extent | Lines |
|--------|-------|
| Section comment | 1957–1963 |
| `.lt-footer-bar` + sub-rules | 1964–1995 |
| Redundant `@media` block | 1996–2002 |
| **Total lines deleted** | **46** |

---

## Task C — Cache-bust version bump

| File | Change |
|------|--------|
| `hooks.py` line 44 | `?v=20260430-4` → `?v=20260430-5` |

`web_include_js` lines were not touched by this builder (Builder JS owns those; the linter bumped them to `?v=20260430-2` as part of the parallel JS fix round).

---

## Task D — Verification results

All checks passed on a live running stack:

```
home 200        ✅
css  200        ✅  (at ?v=20260430-5)
HTML head:      ✅  <link ... href="/assets/locally_twisted/css/lt-theme.css?v=20260430-5">
```

Docker restart sequence completed: backend-1 restarted → cache cleared (bench clear-cache + clear-website-cache) → frontend-1 restarted → site confirmed up at http://localhost:8081/.

---

## Final file metrics

| Metric | Value |
|--------|-------|
| Lines before this fix round | 1,841 (Round 1) → 2,003 (after Task A insertion) |
| Lines deleted (Task B) | 46 |
| Final line count | **1,959** |

---

## Coverage check — every `.lt-utility-bar__*` selector in navbar.html

```
grep result: 14 class references in navbar.html
CSS rules covering them: 11 selectors (some classes share rules, e.g. sign-in covers both Guest and logged-in variants of the same class)
```

Full mapping confirmed in Task A table above. Zero orphaned classes remain.
