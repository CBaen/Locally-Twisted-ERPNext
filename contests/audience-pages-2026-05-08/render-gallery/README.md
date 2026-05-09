# Render Gallery — Audience Pages Contest 2026-05-08

## What was rendered

8 contestants × 4 pages × 2 viewports = **64 screenshots**.

Pages: `civic-community`, `corporate-events`, `private-celebrations`, `schools-campuses`
Viewports: mobile (390px wide, full-page), desktop (1440px wide, full-page)

## How to view

Open `index.html` in any browser (double-click or `file:///` URL). Contestants appear in peer-score rank order. Click any thumbnail to expand full-size in a modal. Screenshots are in `screenshots/contestant-N/`.

## Gallery structure

```
render-gallery/
├── index.html               ← open this to browse
├── README.md                ← this file
├── build_previews.py        ← script that generated preview HTML
├── render.spec.js           ← Playwright spec that captured screenshots
├── preview/                 ← static HTML (one per page per contestant)
│   ├── contestant-1/
│   │   ├── civic-community.html
│   │   ├── corporate-events.html
│   │   ├── private-celebrations.html
│   │   └── schools-campuses.html
│   └── contestant-2/ ... contestant-8/ (same)
└── screenshots/             ← 64 PNGs
    ├── contestant-1/
    │   ├── civic-community-mobile.png      (390px)
    │   ├── civic-community-desktop.png     (1440px)
    │   ├── corporate-events-mobile.png
    │   ├── corporate-events-desktop.png
    │   ├── private-celebrations-mobile.png
    │   ├── private-celebrations-desktop.png
    │   ├── schools-campuses-mobile.png
    │   └── schools-campuses-desktop.png
    └── contestant-2/ ... contestant-8/ (same, 8 files each)
```

## Peer scores (for reference)

| Rank | C# | Concept | Score |
|------|-----|---------|-------|
| 1 | C7 | The Proof is in the Place | 26.71 |
| 2 (tie) | C1 | Audience Authority | 26.00 |
| 2 (tie) | C2 | The Right Room | 26.00 |
| 2 (tie) | C5 | Proof-First Buyer Suite | 26.00 |
| 5 | C6 | Buyer-Scoped Authority | 24.71 |
| 6 | C4 | One System, Four Buyers | 24.57 |
| 7 (tie) | C3 | Made For You (anxiety-first) | 24.29 |
| 7 (tie) | C8 | Made For You (named-promise) | 24.29 |

## Harness limitations — what isn't faithful

This gallery was produced by a static preview harness, not by running Frappe. The following limitations apply to every screenshot:

1. **Portfolio images replaced with colored placeholders.** All `/assets/locally_twisted/images/portfolio/...` URLs become `placehold.co` solid-color blocks. The CSS layout, aspect ratios, grid structures, and overlay text are accurate; the photography is not present.

2. **Icons replaced with small placeholder squares.** `/assets/locally_twisted/icons/brand/...` SVG icons become `placehold.co` 44×44 squares. Card layouts and icon positions render correctly.

3. **Navbar and footer are simplified placeholders.** The real LT mega-menu (sticky, search, hamburger mobile) is not rendered. Screenshots show a minimal two-element bar at top and a text footer at bottom.

4. **LT theme CSS tokens are inlined.** The real site's `lt-theme.css` loads ~40 CSS custom properties. The harness inlines those same token values directly so colors and typography are accurate (Cormorant Garamond + Cinzel + Lato via Google Fonts CDN). Border-radius, spacing, and color palette match the real theme.

5. **Dynamic Frappe data not present.** Contestant pages use Python controllers (`get_context`) to populate template variables. The harness executes those Python files directly (without Frappe installed), capturing all data structures defined in the controller. This worked for all 32 pages — context data is fully rendered. The `frappe` module import produces a warning but does not block data extraction.

6. **C2 civic-community and corporate-events pages.** Jinja render produced a `'str' object is not callable` warning, triggering fallback tag-stripping for those two pages. Layout renders but some dynamic content may be flat text rather than structured HTML. Check `preview/contestant-2/civic-community.html` and `preview/contestant-2/corporate-events.html` for the stripped version.

7. **C6 corporate-events page.** A `'corp_photo_proof' is undefined` warning — that variable was referenced in the template but not populated by the controller. The section renders empty rather than erroring.

8. **Google Fonts CDN required.** The preview HTML files load fonts from fonts.googleapis.com. Screenshots were taken with network access; offline viewing will fall back to Georgia/system-ui.

## Screenshot capture

Run `npx playwright test render.spec.js` from the LT project root (`C:/Users/baenb/projects/Built_by_Cameron/_CLIENTS/locally-twisted/`) to regenerate. Uses the project's existing `playwright.config.js` (Chromium, headless, Windows Chrome/Edge executable detection).

Total screenshots confirmed: **64** (8 contestants × 4 pages × 2 viewports).
