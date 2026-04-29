# Research Notes — Contestant 4
## Customizable Event Decor Design Tool

---

## Area 1: Existing Balloon Design Tools

### Virtualoon
URL: https://www.virtualoon.com/

Virtualoon is the leading web-based balloon design platform for professionals. It generates arch/column/garland structures automatically from dimension inputs rather than letting customers manually drag pieces. Color is applied via a "roller" tool or "color buttons" that change balloon hues after a structure is generated. Key observation: **this is a professional tool for decorators, not customers** — the UX requires knowing balloon structure terminology (layer count, balloon diameter, etc.). It exports PNG for client presentations. The interaction model is parameter-input → auto-generate → color-tweak, which is completely the wrong direction for LT's discovery-first customer experience.

### BalloonBuilder
URL: https://balloonbuilder.com/balloonbuilder-overview/

BalloonBuilder is also professional-facing: split 2D canvas + 3D viewport, bottom palette for color, "paint tool" for clicking individual balloons. Produces export packages (balloon counts, layer breakdowns, 3D renders) for client proposals. Again: **professional tool, not customer tool**. The UX assumes the user knows what a "layer" and "topper" are. Takeaway: existing pro tools treat color application as a per-balloon or per-zone paint operation — this pattern (click region → apply color) is sound, but the frame needs to be customer-friendly, not decorator-friendly.

### Fanfaire Design Studio
URL: https://www.fanfaire.co.uk/blog/introducing-the-ultimate-balloon-business-design-studio

Fanfaire is the closest to customer-facing: clients can "choose colors, add props, and swap specialty items" in real-time, with live pricing updates. However, it integrates pricing directly — which is the configurator-as-checkout anti-pattern LT explicitly rejected. The tool leans on live pricing as its value proposition. Useful observation: customers CAN engage with color selection and piece swapping; the question is framing it as discovery rather than purchase.

### Tangled Balloons 3D Configurator
URL: https://tangledballoons.com/products/arch

Used an Angle3D third-party 3D configurator for balloon arches, but the implementation was broken ("No customization has been created for this 3D model"). The page shows arch types like "4 color spiral arch" — suggesting customers expect to specify color count/pattern, not individual balloon colors. This is a useful data point: **multi-color patterns (spiral, stripe, alternating) are a real customer mental model** for balloon arches — they think "I want teal and gold alternating" not "I want to color each balloon."

### BalloonPro Design Tool
URL: https://balloonpro.co/balloon-design-tools/

Cited in search results as offering organic textured digital balloon design with the full balloon color palette, export capabilities. Consistent with the pro-tool pattern.

### Key takeaway from Area 1:
**Zero live tools serve a customer-first, discovery-first, non-purchasing experience.** All existing tools are either professional (require decorator knowledge) or checkout-adjacent (route to pricing). The LT tool is genuinely novel in the market.

---

## Area 2: Coloring Book / Illustration-Fill UX Patterns

### Pigment App
URL: https://www.idownloadblog.com/2016/01/05/pigment-review/
URL: https://apps.apple.com/us/app/adult-coloring-book-pigment/id1062006344

Pigment's two-mode approach is instructive:
- **Tap-to-fill mode** (for beginners): tap a closed region → it fills with the selected color. The region highlights on tap to confirm selection, then fills. This is the exact pattern needed for LT's coloring-book metaphor.
- **Freehand mode** (for advanced): draw within lines without affecting outside areas.

Critical finding: Pigment has **no recently-used colors row**, which reviewers flagged as "incredibly frustrating when you've made a custom color." This is a known pain point — **LT's tool must include a recently-used colors row** to avoid the same frustration when customers switch between shapes. Pigment offers 126 colors with shadow/highlight sliders. For LT, a curated 50+ real balloon colors replaces the artistic color wheel — customers match physical balloon swatches, not create artistic gradients.

### Sarah Renae Clark coloring tutorials
URL: https://sarahrenaeclark.com/best-adult-coloring-apps/

Comprehensive review of adult coloring apps. Consistent finding: users want tap-to-fill for efficiency, but the fill must feel immediate and satisfying (no perceived lag). The "highlight the selected region" pattern (showing the active region before color is applied) is universal across successful apps — it confirms intent before committing.

---

## Area 3: Color Picker UX for 50+ Swatches

### Mobbin Color Picker Glossary
URL: https://mobbin.com/glossary/color-picker

(403 on fetch — used search results.) Key patterns from Mobbin's documented best practices:
- Circular swatches with ring indicator or check icon for selection state
- Tile/grid form for large palettes, optionally with text labels (accessibility)
- Recently-used colors row for reducing re-selection friction
- Hex input field for exact color matching (especially critical for venue/dress/brand matching)
- Color wheel occupies too much mobile space unless precise hue mixing is required

### UIinkits Color Picker Patterns
URL: https://www.uinkits.com/blog-post/what-is-a-color-picker-and-how-to-use-it-in-ui-ux-design

Color pickers can remember recent colors locally. Swatches in grid form are faster to scan than lists. Key insight: **for a curated palette of named physical colors (as opposed to infinite color space), a scrollable flat grid of swatches labeled with color name + hex is the right pattern** — not a color wheel, which implies infinite choices. The balloon color catalog is a finite curated set; the UX should reflect that.

### Key takeaway from Area 3:
- Grid of swatches (not color wheel) for named balloon colors
- Show hex code on hover/tap-hold for venue matching
- Recently-used row at the top (max 6-8 recents)
- Scrollable sheet that doesn't overwhelm — show 4 columns × N rows, or grouped by color family
- Color name label visible for accessibility
- 44px minimum tap target per iOS HIG guidelines for mobile

---

## Area 4: Multi-Piece Composition Patterns

### Blog.designfiles.co Moodboard Apps
URL: https://blog.designfiles.co/moodboard-apps/

Best mobile moodboard apps (Moodboard iOS, Milanote, Shuffles, Morpholio Board) use:
- **Drag-and-drop** on a free canvas (feels natural on touch)
- **Layering** — items stack, can be reordered
- **Shuffles** (Pinterest's mobile app) uses cutout-based assembly — items feel tactile, like digital scrapbooking

Critical distinction: apps that feel like "scrapbooking" vs. apps that feel like "design tools" — the difference is in process joy. Scrapbooking apps prioritize the feel of the creative process; design tools prioritize output quality. LT's brief explicitly calls for "scrapbook-feel, return-and-rearrange."

### Milanote Wedding Moodboard
URL: https://milanote.com/templates/moodboards/wedding-moodboard

Milanote uses a flexible canvas where elements snap loosely. The feel is "arrange pieces on a table" — no strict grid, no wizard, pieces exist independently and can be rearranged. This maps closely to the LT brief: each shape (arch, column, centerpiece) is a discrete card or panel that can be colored independently, then viewed together.

### Key takeaway from Area 4:
- The composition view should feel like pieces on a table / items in a scrapbook spread
- **Horizontal row (scroll right) works better on mobile than a 2D free canvas** — avoids accidental drag, works with thumb scroll
- Each piece has its own panel with a colored illustration + piece name + "edit colors" affordance
- Adding a new piece is like adding a page to a scrapbook — satisfying, low commitment

---

## Area 5: Mobile-First Interactive SVG Patterns

### SVG Tutorial: Interaction
URL: https://svg-tutorial.com/svg/interaction

SVG elements in the DOM respond to standard click/touch events via `addEventListener`. The pattern for color fill:
```javascript
element.addEventListener("click", () => {
  element.setAttribute("fill", selectedColor);
});
```
This works on mobile (touch events fire click on tap). No special touch handling needed for single-tap fill — the browser maps touch-tap to click automatically. For 375px width, SVG paths need to be large enough to be tappable (44px minimum for meaningful regions).

### SVG Pointer Events (Smashing Magazine)
URL: https://www.smashingmagazine.com/2018/05/svg-interaction-pointer-events-property/

The `pointer-events` CSS property controls which SVG elements receive touch/click. For overlapping SVG elements (e.g., a balloon illustration with fill regions that overlap), setting `pointer-events: none` on decorative strokes ensures only the fill regions receive taps.

### SVG Micro-interactions (SVG Genie)
URL: https://www.svggenie.com/blog/svg-micro-interactions-ux-guide

Hover states don't translate to touch — use `@media (hover: none)` to show active states on mobile instead of hover states. CSS transitions on fill color changes provide visual satisfaction without JavaScript animation libraries. Media query: `@media (hover: hover)` for desktop hover; `@media (hover: none) { :active { ... } }` for mobile tap.

### MDN SVG Fills and Strokes
URL: https://developer.mozilla.org/en-US/docs/Web/SVG/Tutorial/Fills_and_Strokes

`setAttribute("fill", "#hex")` is the standard pattern. Fill can be set directly on SVG paths, groups (`<g>` elements), or `<use>` references. Using CSS classes for fill state (`.selected`, `.highlighted`) is cleaner than attribute-setting inline, and survives CSS specificity better.

### Key takeaway from Area 5:
- Inline SVG with named regions (`id="balloon-fill-1"`) is fully viable for Frappe web pages
- `click` event listener on named SVG paths handles both desktop click and mobile tap
- CSS transitions (`transition: fill 0.2s ease`) make color changes satisfying
- Minimum tappable region: 44px. For mobile, balloon shapes need to be drawn at sizes where the tappable fill area is at least 44×44px.
- Groups of balloons (e.g., an arch) can be targeted as a unit by applying fill to a `<g>` parent

---

## Area 6: Frappe Website Asset Capabilities

### Frappe Portal Pages Docs
URL: https://docs.frappe.io/framework/v15/user/en/portal-pages

Key confirmation: Frappe v15 portal pages support:
- Co-located `.css` and `.js` files loaded automatically when a page loads (same-name convention)
- Jinja2 templates in `www/` folder for server-rendered pages
- Static assets via `/assets/<app>/` path

Inline SVG is valid HTML — it embeds in any Jinja template or Web Page record. No documentation restriction exists against it. Since inline SVG is part of the HTML document, it has full DOM access (JavaScript can query it by `id`).

The `web_include_css` hook in `hooks.py` loads a CSS file globally across the website — this is the right primitive for shared theme styles. Per-page CSS lives in the co-located `.css` file.

### Key confirmation for Frappe:
- Inline SVG in HTML templates: YES, confirmed
- Custom CSS: YES, via co-located `.css` or `web_include_css` in hooks.py
- Custom JS: YES, via co-located `.js` file
- jQuery 3.x: YES, bundled in Frappe's frontend
- No build step needed: YES, plain CSS + JS files are served as-is
- `setAttribute` on SVG elements via vanilla JS: YES, standard DOM API
- No NPM, no framework: confirmed compatible with the Frappe stack

---

## Summary Across All 6 Areas

| Research Area | Key Finding |
|---|---|
| Existing tools | All are pro-facing or checkout-adjacent — LT's tool is genuinely novel |
| Coloring book UX | Tap-to-fill + region highlight + recently-used colors row is the proven pattern |
| 50+ color picker | Scrollable grid of named swatches, hex code visible, recents at top, 44px targets |
| Multi-piece composition | Horizontal scroll of independent piece-cards, scrapbook feel, no strict grid |
| Mobile SVG | Inline SVG + click listeners + CSS fill transitions — fully viable at 375px |
| Frappe capabilities | Confirmed: inline SVG, co-located CSS/JS, jQuery, no build step needed |
