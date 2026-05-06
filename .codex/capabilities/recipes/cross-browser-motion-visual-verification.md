---
id: cross-browser-motion-visual-verification
name: Cross-Browser Motion Visual Verification
schema_version: 2.0
level: recipe
maturity: candidate
scope: Locally Twisted ERPNext/Frappe public-site animated or stateful visual behavior
currently_true: yes
verification_level: 2
last_verified: 2026-05-06
evidence_quality: direct
successful_uses: 1
failed_uses: 0
regressions: 0
depends_on:
  - frappe-public-container-contract
  - responsive-container-audit
used_by: []
tags:
  - Locally Twisted
  - cross-browser
  - animation
  - reduced motion
  - visual QA
  - Playwright
  - Frappe
---

# Cross-Browser Motion Visual Verification

Use this recipe when a public-site change depends on animation, marquee movement, carousel behavior, hover/focus pause, reduced-motion media queries, scroll containers, sticky chrome, or any visual state that can differ by browser session.

For crawls, marquees, review tracks, or other animated bands, read `frappe-public-container-contract.md` first and classify the surface as contained workflow/reading mode or deliberate full-bleed band mode. Motion verification then proves the chosen layout across browser and media-query states.

## When To Use

- GL reports that Chrome, Brave, or another browser does not match what the verifier said.
- A component uses CSS animation, transform, marquee/crawl behavior, carousel tracks, or `prefers-reduced-motion`.
- A fix relies on `overflow`, masks, scrollbars, duplicated tracks, or hidden offscreen content.
- A screenshot shows stale layout or a browser-specific difference after the repo tests passed.

## Core Rule

Do not treat a fresh headless Playwright pass as proof of the user's browser-visible behavior. It proves one browser profile, one media state, and one cache state. Animated visual work needs evidence from the actual served page, the relevant media-query branches, and at least the installed Chrome and Brave binaries when both are available.

## Verification Pattern

1. Confirm the running site is serving the expected HTML/CSS, not just that disk files changed.
2. Clear Frappe website cache after Jinja/CSS/controller edits:

```powershell
python scripts/dev/clear_website_cache.py
```

Use `--restart` when hooks or controller import state changed.

3. Check the exact browser state for each target browser:

- `matchMedia('(prefers-reduced-motion: reduce)').matches`
- `matchMedia('(prefers-reduced-motion: no-preference)').matches`
- computed `animation-name`, `animation-duration`, and `animation-play-state`
- computed `overflow-x`, `scrollWidth`, and `clientWidth`
- element positions before and after a short wait when movement is required
- whether visible scrollbars or wrapped rows appear in screenshots

4. Verify both media branches in Playwright:

```js
await page.emulateMedia({ reducedMotion: "no-preference" });
await page.emulateMedia({ reducedMotion: "reduce" });
```

5. Use the installed browser executables when browser-specific behavior matters:

```powershell
C:\Program Files\Google\Chrome\Application\chrome.exe
C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe
```

6. Capture or inspect real screenshots after the dynamic state is visible. Computed style alone is not enough.

7. If the user's already-open browser differs from fresh-profile Chrome/Brave, suspect stale rendered HTML/CSS, persistent browser settings, extensions, cache, or OS/browser accessibility preferences. Say that clearly and verify the branch before changing code.

## Marquee And Carousel Checks

For crawl/marquee behavior, prove all of these:

- the track has the intended animation name and duration
- the track transform changes in the intended direction over time
- the first visible cards share one row when the contract says no stacking
- the viewport hides the offscreen track without exposing a scrollbar unless that is intentionally accepted
- reduced-motion mode still has an acceptable visual layout

## LT Receipt

On 2026-05-06, the homepage review marquee initially passed a fresh Playwright normal-motion check, but GL showed Chrome exposing a horizontal scrollbar and Brave showing stacked cards. The cause was a verification gap around real browser sessions, stale rendered state, and the reduced-motion fallback. The durable lesson is to verify motion-dependent UI across Chrome, Brave, `no-preference`, and `reduce`, and to inspect visible scrollbars/wrapping, not only computed animation values.
