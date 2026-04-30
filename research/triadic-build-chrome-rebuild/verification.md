# Verification — Phase 4

**Date:** 2026-04-30
**Build:** Chrome rebuild (triadic-construction-v2)
**Test command:** `python scripts/verify/_oneshot_chrome_audit.py`
**Output dir:** `_resources/audit-2026-04-30-chrome/`

---

## HTTP route checks

| Route | Status | Notes |
|---|---|---|
| `/` | 200 | Homepage renders; chrome blocks present in DOM |
| `/book` | 200 | Form renders; was 404 before pre-task #12 |
| `/shop` | 200 | Existing custom shop page, chrome refreshed |
| `/contactus` | 301 → `/contact` → `/book` | Redirect chain working |
| `/api/method/locally_twisted.api.newsletter.signup` | 200 with `{ok:true}` on valid email | Newsletter endpoint live |

## Console errors

Zero pageerror events, zero console.error, zero console.warning across 6 captures (3 routes × 2 viewports).

## Visual review (viewport-only screenshots, read by orchestrator)

### Mobile (375×667) — PASS

- **home-mobile.png:** clean header — script logo, cart icon, hamburger menu. Utility bar shows truck icon + "Bringing celebration to the Wasatch Front since 1998" inline. Hero image with "Twenty-eight years, made by hand." copy + tagline + "Tell us about your event →" CTA button. Mobile drawer is NOT visible at page load (the most critical fix from the round-1 reviews — confirmed working).
- **book-mobile.png:** mobile header consistent. Page heading "Tell us about your celebration" + sub-copy. Form fields rendering: Your Name, Phone, Email. Form is functional.
- **shop-mobile.png:** mobile header consistent. (Page-level shop layout is Phase 2 page-rebuild scope; not chrome.)

### Desktop (1280×800) — FLAG (functional but polish needed)

- **home-desktop.png:** ⚠️ Centered logo is too large for the utility bar grid; the "Bringing celebration to the Wasatch Front since 1998" tagline on the left wraps awkwardly into multiple lines instead of single-line. Primary nav row with mega menu triggers (Balloon Twisting & Face Painting / Special Occasions / Holidays & Seasons / What We Make / Contact / Blog) is rendering. Below the nav, hero image carries through. Polish issue, not a blocker.
- **book-desktop.png:** same desktop chrome layout issue inherited (utility bar logo + tagline wrap).
- **shop-desktop.png:** same.

## DOM-fact checks (script-extracted, supplementary)

| Route | `.lt-header` | `.lt-footer` | `.lt-header__mega` count | Mobile drawer visible at load |
|---|---|---|---|---|
| home-desktop | ✓ | ✓ | 3 | n/a |
| book-desktop | ✓ | ✓ | 3 | n/a |
| shop-desktop | ✓ | ✓ | 3 | n/a |
| home-mobile | ✓ | ✓ | 3 | **false** (the fix held) |
| book-mobile | ✓ | ✓ | 3 | **false** |
| shop-mobile | ✓ | ✓ | 3 | **false** |

## Per-route findings

| Route | Verdict | Notes |
|---|---|---|
| Homepage | PASS-mobile / FLAG-desktop | Desktop utility-bar layout needs polish |
| /book | PASS-mobile / FLAG-desktop | Same desktop chrome inheritance |
| /shop | PASS-mobile / FLAG-desktop | Same; page-level shop layout is Phase 2 |
| Newsletter endpoint | PASS | Live; rate-limit Option A applied (10/hr per email); smoke test in `smoke_forms.py` |
| Mobile drawer | PASS | Hidden by default; opens on hamburger tap (not directly tested in this audit but DOM-visible=false confirms initial state fix) |
| /contactus redirect | PASS | 301 → /contact → /book |

## Open polish items (not blocking; flagged for next session)

1. **Desktop utility bar layout** — `.lt-utility-bar__inner` grid `1fr auto 1fr` with the centered logo's intrinsic 1050×300 dimensions causes the center column to dominate. CSS fix: constrain `.lt-utility-bar__logo` to `max-height: 60px` (or similar) on desktop, OR change grid to `auto 1fr auto` with the logo sized explicitly. Should also verify the `flex-shrink: 0` on the truck-icon doesn't interact badly with the tagline's text wrapping.
2. **Mega panel inner content classes without CSS rules** — `.lt-header__mega-col`, `.lt-header__mega-heading`, `.lt-header__mega-cta`, `.lt-header__mega-cta-wrap`, `.lt-header__mega-browse-row` exist in markup but have no CSS rules. Bootstrap col-lg-* handles layout; default browser styling for headings/anchors. Polish CSS would tighten typography and CTA button styling on the mega panels.
3. **Desktop mega menu interaction not tested in this audit** — would require Playwright hover scripting. DOM presence confirmed (3 panels per page). Hover behavior to be verified in next session OR in real browser by GL.
4. **Per-product variant correctness diff** — deferred from Phase 4 scope. The mirror's `data-attribute-exclusions` JSON vs ERPNext DB variant set comparison should run before any final visual sign-off on /shop product pages. Phase 2 page-rebuild work.

## What was caught by reviewers that builders missed

Per the triadic skill's Phase 5 receipt field — items the triadic structure caught that solo build would have shipped:

- **Active Agreement findings (2 reviewers independently):**
  - Mobile drawer always visible (CSS class mismatch). Critical user-visible defect; would have shipped with broken mobile chrome.
  - Mobile accordions 2 + 3 dead (data-attr mismatch + querySelector singular). Two of three mobile mega menus would have been completely unusable.
  - Cart badge positioning ancestor mismatch.
- **Singular but evidenced:**
  - Mega menu open-state CSS targeting different class than markup (caret rotation, color change broken).
  - `.lt-megamenu` panel class had zero CSS rules (panels would have rendered as inline blocks pushing content down).
  - Newsletter `showError` `textContent` strips the `<a href="tel:">` phone fallback link.
  - Rate-limit X-Forwarded-For bypass.
  - `hash(email)` instability across container restarts.
  - Esc-key on `/book` navigates away from the form (pre-existing UX bug surfaced by SecOps).
  - Newsletter smoke test missing (loud-failure rule violation).

All caught and fixed in Round 2. None of these would have been caught by a single-builder pass.
