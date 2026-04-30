# Synthesis Render Report

**Rendered:** 2026-04-26  
**Server:** Next.js 16.2.1 (Turbopack) on port 3001  
**Screenshots:** 4 pages × 2 viewports = 8 PNGs

---

## Pages Rendered

| Page | Desktop | Mobile | Status |
|------|---------|--------|--------|
| landing | `landing-desktop.png` (250 KB) | `landing-mobile.png` (177 KB) | Clean |
| lookbook | `lookbook-desktop.png` (198 KB) | `lookbook-mobile.png` (181 KB) | Clean |
| shop | `shop-desktop.png` (198 KB) | `shop-mobile.png` (176 KB) | Clean |
| balloon-twisting | `balloon-twisting-desktop.png` (347 KB) | `balloon-twisting-mobile.png` (276 KB) | Clean (after fix) |

---

## Structural Fixes Applied

Only compile-blocking issues were fixed. Design content is unchanged.

### 1. Import path adjustment (all 4 pages)

**Why:** The synthesis `layout.tsx` file could not serve double duty as both the App Router route layout (auto-applied to all children) and the named component imported by pages. Using it as both would double-render the nav and footer.

**Fix:** Copied `layout.tsx` to `layout-shell.tsx`. Created a thin passthrough `layout.tsx` for App Router (just `<>{children}</>`). Updated all four page imports from `'../layout'` to `'../layout-shell'`.

**Files changed:**
- `synthesis/layout-shell.tsx` — new file (copy of layout.tsx content)
- `synthesis/layout.tsx` — new thin App Router passthrough
- `synthesis/landing/page.tsx` — import path updated
- `synthesis/lookbook/page.tsx` — import path updated
- `synthesis/shop/page.tsx` — import path updated
- `synthesis/balloon-twisting/page.tsx` — import path updated

### 2. Single-quoted JS strings with apostrophes (balloon-twisting only)

**Why:** Turbopack's parser strict mode — ASCII apostrophes (`'`) inside single-quoted string literals terminate the string early. This is valid in JSX text nodes but a parse error in JS string values.

**Affected lines (PROCESS_STEPS data, FAQ data):**
- L244: `'Date, ... you're imagining ...'` → backtick
- L249: `'We'll let you know ...'` → backtick
- L259: `'We arrive early ... don't manage us ... that's not your job ...'` → backtick
- L338: `note: 'High-volume ... we're built for it.'` → backtick (note value only)
- L405: FAQ answer 1 (multiple contractions) → backtick
- L410: FAQ answer 2 (contraction) → backtick
- L420: FAQ answer 4 (contraction) → backtick

**What was NOT changed:** JSX text nodes (inside `<p>`, `<h2>`, etc.) with apostrophes are valid and were left as-is. CSS value strings, style prop strings, class names, and all visual/design content are untouched.

---

## Screenshot Paths

All PNGs at: `C:\Users\baenb\projects\zoho-locally-twisted\gallery\screenshots\synthesis\`

- `landing-desktop.png` — 1440×900
- `landing-mobile.png` — 375×812
- `lookbook-desktop.png` — 1440×900
- `lookbook-mobile.png` — 375×812
- `shop-desktop.png` — 1440×900
- `shop-mobile.png` — 375×812
- `balloon-twisting-desktop.png` — 1440×900
- `balloon-twisting-mobile.png` — 375×812

---

## Visual Notes

- **Landing:** Hero renders with blush-tint photo placeholder + bottom-anchored copy block (D3 photo-first principle intact). Proof strip, 3-column work grid, services callout, about strip, inquiry CTA, and footer all present.
- **Lookbook:** Portfolio grid with filter chips visible. Configurator section (step 1 — mood pills) rendered in its initial state.
- **Shop:** Product grid (3-up desktop, 2-up mobile), cart trigger button, category filter pills all rendered. Cart drawer off-screen (not open by default).
- **Balloon Twisting:** Page header, dual service split with spec tables (dl/dt/dd), numbered process steps, event types list, FAQ accordion (collapsed), and booking section with service/event-type chips all rendered correctly.

All fonts loaded (DM Serif Display + Raleway via Google Fonts or CSS). CSS custom properties (`--color-*`, `--font-*`, `--space-*`) resolved correctly from `globals.css`.

---

## Refinement Pass — 2026-04-26

Three GL-specified fixes applied to both source (`gallery/synthesis/`) and render mirror (`gallery/_render/src/app/synthesis/`). Screenshots overwritten.

### Fix 1 — 3 colors + derived tints removed from design system

**Removed from `globals.css` (both locations):**
- `--color-seafoam: #88FED0`
- `--color-sky-cyan: #A0E9FF`
- `--color-soft-lemon: #F9F871`
- `--color-mint-tint: #EEFEF5` (derived from seafoam)
- `--color-lemon-tint: #FDFDE3` (derived from soft-lemon)

**Kept:** Blush (#F4DFD7), Lime Pastel (#B8FF9E), Aqua (#80F5F3), Soft Blue (#C3DCF3), Blush Tint (#FBF5F2), Blue Tint (#EEF4FB).

**Replacement logic for thin accent bands and photo placeholders (references replaced in TSX):**

| Page | Old token | New token | Rationale |
|------|-----------|-----------|-----------|
| landing | `--color-seafoam` (band after hero) | `--color-aqua` | cool, similar hue family |
| landing | `--color-soft-lemon` (band before about) | `--color-lime-pastel` | warm-green replaces warm-yellow |
| landing | `--color-sky-cyan` (band before CTA) | `--color-soft-blue` | cool section close |
| landing | `--color-mint-tint` (twisting photo placeholder) | `--color-blush-tint` | warm service card |
| landing | `--color-lemon-tint` (face painting photo placeholder) | `--color-blue-tint` | cool contrast with twisting card |
| lookbook | `--color-sky-cyan` (soft mood pill accent) | `--color-soft-blue` | cool, same register |
| lookbook | `--color-soft-lemon` (festive mood pill accent) | `--color-lime-pastel` | warm-celebratory |
| lookbook | `--color-seafoam` (elegant mood pill accent) | `--color-aqua` | refined cool |
| lookbook | `--color-lemon-tint` (Autumn Garland card bg) | `--color-blush-tint` | warm birthday piece |
| lookbook | `--color-mint-tint` (Teal Sculpture card bg) | `--color-blue-tint` | cool corporate piece |
| lookbook | `--color-sky-cyan` (band before configurator) | `--color-soft-blue` | cool section |
| lookbook | `--color-seafoam` (band before bottom CTA) | `--color-aqua` | cool |
| shop | `--color-seafoam` (band before cross-sell) | `--color-aqua` | cool |
| balloon-twisting | `--color-lemon-tint` (face painting photo placeholder) | `--color-blush-tint` | warm service |
| balloon-twisting | `--color-soft-lemon` (band before event types) | `--color-lime-pastel` | celebratory |
| balloon-twisting | `--color-mint-tint` (band before FAQ) | `--color-aqua` | cool |
| balloon-twisting | `--color-sky-cyan` (band before booking) | `--color-soft-blue` | cool close |

**Total inline color references changed:** 17 across 4 pages (both source and mirror).

### Fix 2 — "installation/installations" terminology replaced

Replacement table applied across all 4 TSX pages + mood.md and voice.md:

| Page | Location | Old text | New text |
|------|----------|----------|----------|
| landing | `FEATURED_WORKS` category | `Organic Installations` | `Organic Garlands` |
| landing | `FEATURED_WORKS` title | `Blush Cloud Installation` | `Blush Cloud Arrangement` |
| landing | `AboutStrip` body copy | `making balloon installations along...` | `making balloon decor along...` |
| lookbook | `MOODS` step 1 helper | `Most installations begin as a mood` | `Most balloon decor begins as a mood` |
| lookbook | `SCALE_OPTIONS` gala description | `statement installations` | `statement balloon decor` |
| lookbook | `LOOK_ITEMS` organic-cloud category | `Organic Installations` | `Organic Garlands` |
| lookbook | `LOOK_ITEMS` organic-cloud title | `Blush Cloud Installation` | `Blush Cloud Arrangement` |
| lookbook | `LOOK_ITEMS` installation-corporate category | `Organic Installations` | `Organic Garlands` |
| lookbook | `ALL_CATEGORIES` filter option | `Organic Installations` | `Organic Garlands` |
| lookbook | result count label | `installation` / `installations` | `piece` / `pieces` |
| lookbook | page header body | `Custom balloon installations for...` | `Custom balloon decor for...` |
| shop | page header body | `For a custom event installation, start with` | `For custom balloon decor, start with` |
| shop | cross-sell heading | `Custom event installations start with a conversation` | `Custom balloon decor starts with a conversation` |
| voice.md | wedding planner notes | `Most installations begin as a mood` | `Most balloon decor begins as a mood` |
| voice.md | event types row entry | `Most events. Any size.` | `Any Event. Any Size.` |
| mood.md | accent palette description | `Blush, Soft Lemon, Lime Pastel, Seafoam, Aqua, Sky Cyan, Soft Blue` | `Blush, Lime Pastel, Aqua, Soft Blue` |

**Per-page "installation" replacement count:** landing: 3, lookbook: 8, shop: 2, balloon-twisting: 0 (none were present).

Note: `slug: 'installation-corporate-teal'` retained as a data identifier/anchor hash (not visible copy).

### Fix 3 — Balloon-twisting copy swap

| Page | Location | Old | New |
|------|----------|-----|-----|
| balloon-twisting | `EventTypes` section `<h2>` | `Most events. Any size.` | `Any Event. Any Size.` |

Applied to both source and mirror. Also updated in `voice.md` to match.
