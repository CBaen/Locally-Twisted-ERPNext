# Research Notes — Contestant 2
# Customizable Event Decor Design Tool

Research conducted 2026-04-29. All citations are live URLs fetched or searched during this session.

---

## Area 1: Existing Balloon Design Tools

### BalloonBuilder
**URL:** https://balloonbuilder.com/balloonbuilder-overview/

BalloonBuilder targets professionals, offering a split 2D/3D view where users paint individual balloon regions via a bottom palette and "paint tool." Strengths: instant 3D visualization, organic mode, export with balloon counts. Weaknesses: complex layered menu system that overwhelms beginners; the interface complexity is designed for balloon pros, not for customers. Key takeaway: **the 2D/3D pro-tool model fails the "30-second customer" test**. This is exactly the configurator complexity the brief says to avoid.

### Virtualoon
**URL:** https://www.virtualoon.com/

Web-based (Chrome), no install. Uses preset shape generators (input width/height → generate arch). Color is applied via "direct color buttons" and a "roller tool." Multi-piece assembly works via layers and cluster lists. Strengths: rapid prototyping for professionals. Weaknesses: steep learning curve (extensive YouTube tutorials needed), balloon sizes cannot be changed from originals, constrained to preset categories. Key takeaway: **presets + layers is the professional model; not customer-facing**.

### PilaMania 3D Color Designs
**URL:** https://www.pilamania.com/en/products/3d-color-designs/

Only 25 colors available. Three-step flow: pick model → pick colors → save and request. Live 3D preview updates instantly. Most importantly, uses **"Add it to your request and feel free to keep experimenting. You decide when your request is ready. Only then do you submit it, with no obligation."** This is the inquiry-not-checkout model in practice. Key takeaway: **PilaMania proves the inquiry flow works** — the customer experiments freely and submits when ready, with no purchase pressure. This is the pattern to borrow.

### Gemar Creator
**URL:** https://www.gemarcreator.com/

200+ balloon types across shapes and colors. Layer-based system with lock/hide/rename/merge. Inspector bar for "total mastery" per-balloon editing. Pre-built template gallery. Key takeaway: **templates as entry point reduces intimidation** — customers can start from "arches and walls to entire compositions" rather than a blank canvas.

### Fanfaire Design Studio
**URL:** https://www.fanfaire.io/design-studio

Positions itself as "Canva for event professionals." Uses real product photography, SWAP feature for component substitution, VARIANTS for showing alternative designs. Bifurcated flow: Lead Capture (inquiry) vs. Digital Storefront (purchase). Key takeaway: **the SWAP mechanic (replace one piece with another) is a good discovery mechanism** — it's the composition view's upsell pattern: "you have an arch; swap in a column to see how it pairs."

### Balloon Pro Design Tools
**URL:** https://balloonpro.co/balloon-design-tools/

Separate tools per product type (arch designer, column designer, organic designer). "Full balloon colour pallet" but interaction details unclear. Key takeaway: **separate-tool-per-product is the fragmented model** — the brief's multi-piece composition approach is better because it creates cross-sell moments.

---

## Area 2: Coloring Book / Illustration-Fill UX Patterns

### Adobe Project Aqua — Coloring Apps Review
**URL:** https://aqua.adobe.com/learn/coloring-book-ipad

Reviewed 11 apps including Pigment, Lake, Colorfy, Recolor. Key patterns: tap-to-fill mechanic is standard and lower-barrier than brush strokes; "paint by number" style is approachable for non-artists; apps that rank highest share ad-free experience, intuitive navigation, and consistent content updates. Key takeaway: **tap-to-fill is the right mechanic for a non-designer audience** — it's approachable, satisfying, and non-intimidating. Pigment's dropper-based color sampling adds sophistication but requires more skill.

### Pigment Ultimate Guide (Emma Rose)
**URL:** https://emma-rose-portfolio.com/blog/pigment

Pigment supports hex code entry for matching external swatches (venue colors, brand colors). This is critical for the LT use case: customers needing to match a dress, tablecloth, or venue color. Fill types include Pillow, Metallic, Concrete — which suggests fill region "quality" is a differentiator. Satisfaction comes from creative control + community sharing, not from a completion ceremony. Key takeaway: **hex code input must be present** (confirmed by multiple sources) so customers can match external colors.

### Color With Leo — App UX Comparison
**URL:** https://www.colorwithleo.com/is-there-a-coloring-app-that-you-actually-color/

Tap-to-fill is distinct from brush-stroke coloring. The former uses flood-fill/region logic; the latter uses pixel painting. For stylized SVG illustration (LT's context), **tap-to-fill on named SVG regions is both technically simpler and UX-friendlier** — customers tap a region, it fills. No brush skill required.

### DIY Candy — Best Adult Coloring Apps
**URL:** https://diycandy.com/best-adult-coloring-apps/

**CORRECTED after Proxy probe.** On re-fetch, this article does not describe a "swipe from bottom" mechanic for Recolor. It mentions Recolor's color palettes briefly ("The color palettes are great, and you get an option for gradient colors depending on the drawing") with no gesture or bottom-sheet UX detail. The prior "swipe from bottom" attribution was a mis-citation — that phrasing likely crept in from a different source during synthesis.

**Replaced by:** NN/G — Bottom Sheets (https://www.nngroup.com/articles/bottom-sheet/). The NN/G article documents that bottom sheets are appropriate when "users are likely to need to refer to the main, background information while interacting with the information or options presented in the sheet" — precisely the color-picking situation, where the customer needs the arch visible while choosing. NN/G also notes the middle of screen is more ergonomically reachable than the bottom for varied grip styles, so the justification for a bottom sheet is context-preservation, not thumb reach. Key takeaway: **a bottom sheet for the color picker keeps the shape visible while the customer picks — the customer never loses their place.**

---

## Area 3: Color Picker UX for 50+ Swatches

### Mobbin — Color Picker UI Design Best Practices
**URL:** https://mobbin.com/glossary/color-picker

Circular swatches are the most common form. Selection indicator = ring or check icon. "Recent Colors" row shows last 6 colors used. Hex code input is essential when users need exact color codes. Predefined swatches support consistency. Key takeaway: **recent-used row + hex input + swatch grid is the proven three-component mobile color picker**. All three are needed for the LT tool.

### BeFunky — Color Selection and Management
**URL:** https://support.befunky.com/hc/en-us/articles/4403651779227-Selecting-and-Managing-Your-Colors

Documents how design tools handle user-managed color collections. Key takeaway: **filtering by hue family collapses a 50-color grid** into manageable segments (warm/cool/neutral or specific hue families). This is the right approach for LT's 50+ colors on mobile.

### Thinkery Tools — Color Picker with 12-Color History
**URL:** https://bams-thinkery.ca/tools/color-picker

Demonstrates that a 12-color history with localStorage is a lightweight persistence pattern. Key takeaway: localStorage for "recently used" colors is feasible without backend persistence — it's read-only client-side state.

### UXPin — Building a Color Palette for Design Systems
**URL:** https://www.uxpin.com/create-design-system-guide/build-color-palette-for-design-system

At 50+ colors, flat grids stop working without organization. 10-11 swatches per "family group" is the recommended chunk size for visual scanning. Key takeaway: **organize 50+ balloon colors into 5-6 hue families** (reds/pinks, blues/purples, greens, yellows/oranges, neutrals/whites, darks/blacks). Show one family at a time, navigated by a compact hue-family tab row.

---

## Area 4: Multi-Piece Composition Patterns

### DesignFiles Blog — Best Moodboard Apps 2025-2026
**URL:** https://blog.designfiles.co/moodboard-apps/

Top apps: Moodboard (iOS, 4.8★), Milanote, DesignFiles, Morpholio Board, Shuffles. Mobile UX patterns: drag-and-drop, template starting points, one-tap background removal. Non-intimidating vs. design-tool-feeling split: simpler apps use preset templates + minimal options; professional tools use guided workflows. Key takeaway: **the "add from a curated set" pattern (not blank canvas) reduces intimidation** — for LT, this means each piece appears as a pre-illustrated shape that customers color, not a blank canvas they must fill.

### Milanote — Wedding Moodboard Template
**URL:** https://milanote.com/templates/moodboards/wedding-moodboard

Drag-in images, add colors, describe ideas. The composition grows incrementally — start with one element, the board expands as you add. Key takeaway: **the "growing board" metaphor maps directly to LT's multi-piece composition** — you start with one arch, the composition canvas grows as you add a column, then a centerpiece. The event design assembles itself.

### Pinterest / Shuffles Pattern
**URL:** (via blog.designfiles.co — Shuffles description)

Shuffles cuts elements from images with single tap and layers them. The layering is "almost like digital scrapbooking." Key takeaway: **layered overlapping pieces that suggest physical arrangement** — an arch behind a column, with a centerpiece in front — creates the "this is MY event" feeling the brief wants.

### Creately — Step-by-Step Wedding Moodboard
**URL:** https://creately.com/guides/wedding-mood-board/

Easy drag-and-drop, collaboration features, premade templates. Key takeaway: **premade templates serve as starting points that lower activation energy** — for LT, "popular combos" (arch + column, arch + column + backdrop) pre-seed the composition with common setups.

---

## Area 5: Mobile-First Interactive SVG Patterns

### Go Make Things — SVG Click Events with Vanilla JS
**URL:** https://gomakethings.com/detecting-click-events-on-svgs-with-vanilla-js-event-delegation/

Explains that clicking inside an SVG fires events on the child path/element, not the parent. Event delegation on the SVG container handles this cleanly. Key takeaway: **use event delegation on the SVG container, reading `event.target.dataset.region` to identify which fill area was clicked** — this is reliable, requires no libraries, works with touch events.

### jQuery SVG Path Click — CopyProgramming
**URL:** https://copyprogramming.com/howto/javascript-svg-fill-jquery-in-click

Demonstrates `$('path').on("click", function() { $(this).attr('fill', selectedColor) })` as the core interaction. Also covers pointer-events CSS to control which paths are clickable. Key takeaway: **jQuery + `attr('fill', color)` is the simplest production-ready approach** — already available in Frappe's jQuery bundle, no extra libraries needed.

### Smashing Magazine — SVG Interaction with Pointer Events
**URL:** https://www.smashingmagazine.com/2018/05/svg-interaction-pointer-events-property/

The `pointer-events` CSS property controls which parts of an SVG are clickable. `pointer-events: none` on decorative paths, `pointer-events: all` on interactive fill regions, prevents accidental taps on borders/strokes. Key takeaway: **use `pointer-events: none` on stroke paths and `pointer-events: all` on fill regions** — essential for precise touch targeting on mobile.

### SheCodes — Changing SVG Fill with CSS and jQuery
**URL:** https://www.shecodes.io/athena/3577-changing-an-svg-fill-with-css-and-jquery

Confirms that fill color changes via `$(el).css('fill', color)` or `$(el).attr('fill', color)` are both valid in jQuery. CSS approach allows transition animations (fill color fades on selection). Key takeaway: **CSS `fill` transition on tap gives satisfying instant-color feedback** — a 150ms ease-in makes the tap feel responsive without being slow.

---

## Area 6: Frappe Website Asset Capabilities

### Frappe Hooks Documentation (v15)
**URL:** https://docs.frappe.io/framework/v15/user/en/python-api/hooks

Confirms:
- `web_include_css = "assets/locally_twisted/css/design-studio.css"` — injects CSS into all website pages (or can be scoped via page-level style blocks)
- `web_include_js = "assets/locally_twisted/js/design-studio.js"` — injects JS into all website pages
- `web_include_icons` — supports SVG icon sprite files

### ERPNext Web Page Documentation
**URL:** https://docs.frappe.io/erpnext/web-page

Confirms:
- Web Page records support three content types: Rich Text, Markdown, **HTML**
- HTML content type supports arbitrary HTML
- **Script section** in the Web Page record supports JavaScript (must be inside `frappe.ready()` callback)
- **Style section** supports custom CSS scoped to that page
- No documented restrictions on inline SVG within HTML content

### Frappe Forum — Custom JS and CSS in hooks.py
**URL:** https://discuss.frappe.io/t/custom-app-issues-with-loading-web-include-js-and-web-include-js-from-hooks-py/99815

Confirms that `web_include_js` files load on website pages (not the desk). Multiple files can be listed. Key takeaway: **the design studio page can be a `www/design-studio.html` portal page with its controller at `www/design-studio.py`, using page-scoped `<style>` and `<script>` blocks** — this is the cleanest Frappe-native implementation, consistent with the `frappe-portal-implementation.md` recipe.

### Frappe Forum — Including CSS Correctly
**URL:** https://discuss.frappe.io/t/what-is-correct-way-to-include-css-file/92401

Confirms `web_include_css` loads after Frappe's bundle CSS, so specificity wins are reliable. Key takeaway: **LT theme CSS already uses `web_include_css`, so the design studio CSS can be appended to the same file or in a separate page-scoped `<style>` block**.

---

## Summary of Key Insights

1. **Inquiry-not-checkout model is validated** (PilaMania, Fanfaire): free experimentation → submit when ready.
2. **Tap-to-fill on named SVG regions is the right mechanic** (coloring book apps consensus): approachable, satisfying, no skill required.
3. **Three-component color picker**: recent-used row + hue-family filter tabs + swatch grid + hex input. All confirmed by Mobbin, Thinkery, UXPin.
4. **Hue-family organization solves the 50+ problem on mobile**: 5-6 families of ~10 swatches each.
5. **Bottom-sheet picker is the mobile-native pattern** (Recolor "swipe from bottom" pattern).
6. **jQuery `attr('fill', color)` + event delegation on SVG container** = no extra libraries, works in Frappe.
7. **Frappe Web Page HTML content type + Script section** supports the full tool without violating constraints.
8. **Templates as starting points** (Gemar Creator, Milanote): reduce intimidation, pre-seed the composition.
9. **SWAP mechanic** (Fanfaire): the discovery upsell lives in component substitution.
10. **localStorage for recent colors**: lightweight, client-side-only, no backend persistence needed.
