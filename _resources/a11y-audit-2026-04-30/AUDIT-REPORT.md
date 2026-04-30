# Accessibility Audit — Locally Twisted

**Date:** 2026-04-30
**Pages tested:** 7 — `/`, `/book`, `/contact`, `/all-products`, `/shop-items/arches`, `/cart`, `/balloon-twisting-and-face-painting`
**Tool:** axe-core 4.11.4 (chrome-headless 148)
**Coverage caveat:** axe detects ~57% of WCAG criteria; manual review still required for the rest.

Raw JSON results: `full-{slug}.json` per page.

---

## 🔴 PRIORITY — Fix before shipping

| # | Criterion | Page | Element | Issue | Fix |
|---|-----------|------|---------|-------|-----|
| 1 | WCAG 4.1.2 button-name (CRITICAL) | /all-products | `#list`, `#image-view` toggle buttons | Webshop's list/grid view-toggle buttons have only an SVG icon, no text or aria-label | Add `aria-label="List view"` and `aria-label="Grid view"` via JS override or template patch in `apps/locally_twisted/locally_twisted/templates/generators/item_group.html` |
| 2 | WCAG 1.4.3 color-contrast (SERIOUS) | /balloon-twisting | `.lt-btfp__banner-link` (phone + email) | Click-to-call / email links on the banner fall under 4.5:1 contrast | Either darken the link text or change banner background. Touches brand color — design call. |
| 3 | WCAG 1.4.3 color-contrast (SERIOUS) | /balloon-twisting | `.lt-btfp__process-number` (01/02/03) | Process step numbers below 4.5:1 contrast | Darken the number color |
| 4 | WCAG 1.4.3 color-contrast (SERIOUS) | /all-products | `span[itemprop="name"]` in breadcrumb | "All Products" breadcrumb text under 4.5:1 | Override webshop breadcrumb color in `lt-theme.css` |
| 5 | WCAG 4.1.2 aria-prohibited-attr (SERIOUS) | /balloon-twisting | `.lt-btfp__carousel` (2 nodes) | Plain `<div>` can't have `aria-label` without an explicit role | Change to `<section aria-label="...">` OR add `role="region"` |
| 5b | (incomplete — likely same issue) | / | `.lt-reviews-block__quotes`, `.lt-reviews-block__quote-stars`, ~20 nodes total | Same pattern: divs with aria-label and no role | Same fix — add role or change tag |
| 6 | WCAG 1.4.1 link-in-text-block (SERIOUS) | /balloon-twisting | `<a href="/refund-policy">policies</a>` inside `.lt-btfp__expect-card` | Inline link distinguishable only by color | Add `text-decoration: underline` to in-paragraph links |

---

## 🟡 BEST PRACTICE — Fix in next iteration

| # | Criterion | Page | Issue | Fix |
|---|-----------|------|-------|-----|
| 1 | WCAG 1.3.1 page-has-heading-one (MODERATE) | /, /all-products | No `<h1>` on the page | Add a visible or visually-hidden h1. Homepage already shows a hero title — promote it to h1. /all-products needs an h1 in the LT shop template (we control that). |
| 2 | WCAG 1.3.6 landmark-complementary-is-top-level (MODERATE) | /contact, /balloon-twisting | `<aside>` element nested inside `<main>` or another landmark | Move `<aside>` outside the parent landmark, or change the tag to a plain `<div>` if it's not actually complementary content |

---

## 🔵 Manual review required

axe couldn't determine pass/fail for these — they need a human eye on the live page:

- **14 color-contrast incomplete on homepage** (CSS variables — verify against the actual rendered colors): `.lt-hero__eyebrow`, `.lt-hero__title`, `#lt-hero-tagline`, `.lt-hero__cta`, `.lt-reviews-block__stars`, `.lt-reviews-block__quote-text`, plus 8 more
- **`aria-allowed-role` on `#lt-mobile-nav`** — the `<aside aria-modal="true">` mobile drawer; review whether `aria-modal` is appropriate
- **`frame-tested` on /contact** — an iframe on the page wasn't tested (likely the Maps embed if present)
- **`aria-valid-attr-value` on /all-products** — one node with an ARIA attribute value that may be invalid

---

## ⚪ Manual checks the audit didn't cover (still needed)

Per skill: ~43% of WCAG criteria need a human eye. Not done yet:

- Alt-text *accuracy* (presence is auto-checked; meaning isn't)
- Dialog focus management — when mobile drawer or mega panels open, does focus move into them? On close, does focus return?
- Keyboard navigation flow — tab through every page, verify sensible order
- Error message association — submit the booking form invalid, check screen-reader announcement
- 200% zoom behavior across all pages

---

## ✅ Notable passes

- All form fields properly labeled (no missing-label violations on /book or /contact)
- Document language set (`lang="en-US"`)
- `/book`, `/shop-items/arches`, `/cart` clean — zero violations
- Mega menu structure has proper ARIA wiring (didn't trigger violations on home)

---

## Design decisions waiting on GL

The contrast fix on `.lt-btfp__banner-link` requires either changing the link color or the banner background — both touch brand identity. Don't change without input.

---

## Tool output disclaimer

axe-core itself states: *"only 20% to 50% of all accessibility issues can automatically be detected. Manual testing is always required."* This audit is a starting point, not a compliance certification.
