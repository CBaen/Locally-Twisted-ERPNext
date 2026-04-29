# RESEARCH-NOTES.md — Contestant 1

Research compiled before any mockup or reasoning was produced. All citations are from live sources accessed 2026-04-29.

---

## Research Area 1: Existing Balloon Design Tools

### Source 1 — Virtualoon (https://www.virtualoon.com/)
Virtualoon is a professional balloon mockup tool for decorators, NOT customers. The workflow is: decorator inputs dimensions, selects balloon types, uses a "roller" to bulk-change colors across a design, then exports PNG for client presentation. Key insight: **the tool is for the artist, not the buyer** — customers see the output, not the tool. Relevant anti-pattern: this is precisely the B2B assumption LT's tool must invert.

### Source 2 — BalloonBuilder (https://balloonbuilder.com/balloonbuilder-overview/)
BalloonBuilder uses a split-view interface: 2D canvas left, 3D viewport right. Color selection via "Paint Tool" (click-on-balloon in 2D view). Supports "Color Pattern" automation (Spiral, Stripes, Random). **Critical finding: BalloonBuilder separates pieces into separate apps** (Columns & Arches Designer vs. Walls Designer) — customers cannot see multi-piece compositions together. This is the gap LT's tool addresses: simultaneous multi-piece composition.

### Source 3 — Balloon Pro (https://balloonpro.co/balloon-design-tools/)
"Color each balloon / layer or bulk color to quickly see your arch come to life." Supports saving designs and exporting production schedules. The UX emphasizes "less than one minute" to a design. Speed is positioned as the main value. Still decorator-focused.

### Source 4 — Gemar Creator (https://www.gemarcreator.com/)
Provides 200+ balloon types, layer management (lock/hide/rename), preset compositions as starting points (arches, walls, entire compositions). Customers can start from presets and customize. Layer inspector gives "total mastery." However: this is a professional tool with monthly subscription pricing — not a lightweight customer-facing browser experience.

### Source 5 — Fanfaire Design Studio (https://www.fanfaire.io/design-studio + https://www.fanfaire.co.uk/blog/introducing-the-ultimate-balloon-business-design-studio)
**Closest analog to what LT wants.** Interactive mockup tool where clients "explore in real-time," choose colors, swap specialty items. Includes live pricing calculations. Key difference from LT's brief: Fanfaire routes toward checkout ("clients buy designs through the integrated digital storefront"). LT explicitly does NOT want this — inquiry first, sale later, price never during design. Fanfaire proves the demand exists; LT's version strips the transactional frame.

### Source 6 — Party City Virtual Balloon Bouquet Configurator (https://precocityllc.com/results/party-city-virtual-balloon-bouquet-configurator/)
URL returned 404 — site no longer available. The pattern (large retailer attempting a balloon visual configurator) is documented but not fetchable.

---

## Research Area 2: Coloring Book / Illustration-Fill UX Patterns

### Source 7 — Pigment App Review (https://www.idownloadblog.com/2016/01/05/pigment-review/)
Pigment offers **126 colors in themed palettes** (e.g., "Roller Rink," "Rain Forest"). Two fill modes: (a) freeform trace/scribble, (b) tap-to-activate constrained region coloring. The review's exact description of mode (b): *"tap a section of an illustration to activate the 'color-inside-the-lines' feature, which highlights the spot so that it is the only part of the illustration that will be affected by your scribbles, even if you go outside the lines."*

**What this citation supports:** The two-step mechanic — tap to activate/highlight a region, then color within it — is confirmed. Step one (tap → region highlights and becomes the active zone) maps directly to the design.

**Precision note (from Proxy Loop 1-1):** After activation, Pigment uses freeform brush strokes. The design here uses swatch-tap → instant flat fill as step two. The citation validates step one (region activation); step two is a design choice suited to balloon context where a zone is a single flat color, not a brushstroke gradient. Instant fill on swatch selection is faster and more satisfying for this use case. Pigment also supports hex entry for custom colors.

### Source 8 — Adult Coloring Apps Review (https://sarahrenaeclark.com/best-adult-coloring-apps/)
Key insight: coloring apps succeed when they "recreate the relaxing experience of actually coloring." The emotional contract is flow + satisfaction, not precision + completion. For LT: the design tool should feel like coloring a page, not filling out a form.

---

## Research Area 3: Color Picker UX for 50+ Swatches

### Source 9 — Baymard Research on Mobile Color Swatches (https://baymard.com/blog/mobile-interactive-color-swatches)
**Specific findings from this post:**
- 57% of ecommerce sites fail to make all swatches available in mobile list views
- Horizontal scrolling with clearly truncated rightmost swatch works best for mobile
- "+8" indicators fail — users assume visible swatches are ALL options
- Expandable downward sections fail at many colors — pushes content off screen
- **Inline scrollable areas risk scroll hijacking** — avoid
- The post describes "large hit areas and generous spacing between swatches" qualitatively (citing a Walgreens example) but **does not state a numerical minimum size**

**Sourcing correction (from Proxy Loop 1-1):** The 7mm minimum touch target figure originally attributed to this URL is not in this post. The 7mm figure comes from Baymard's separate button/touch-target research at https://baymard.com/learn/button-design, which states: "Our research finds a minimum hit area of 7mm by 7mm reduces the number of tap issues." That is general mobile touch target guidance, applied here to swatches as tappable elements — a reasonable application, but sourced from the button article, not the swatch article.

**Design decision for LT:** Show 8-10 swatches in a horizontally scrollable row. Truncate visibly to signal more. 44px swatch size (well above 7mm at standard screen DPI). Separate "browse all" trigger opens grouped full-palette sheet.

### Source 10 — Designing a Good Color Picker (https://medium.com/design-bootcamp/designing-a-good-color-picker-4c08573dcb7b)
The key insight: most users don't need to pick *any* color — they need to pick the *right* color from an established palette. Shared palettes, version-controlled, prevent errors. For LT: the 50+ balloon colors ARE the palette. The customer is not choosing from infinity — they're choosing from LT's actual catalog. This frames the picker as a *catalog browser*, not a color wheel.

### Source 11 — Mobbin Color Picker Glossary (https://mobbin.com/glossary/color-picker)
Returned 403. Could not access. Cross-referencing other sources instead.

---

## Research Area 4: Multi-Piece Composition Patterns

### Source 12 — Milanote Moodboarding (https://milanote.com/product/moodboarding)
Milanote's key design philosophy: **"boards don't have any restrictions — you can arrange things any way you like."** Mobile apps for capture-on-the-go. Templates reduce blank-canvas anxiety. For LT: a rigid grid (vs. freeform) removes intimidation. The customer doesn't need to "arrange" — they just add pieces to a stage and see them together.

### Source 13 — Wedding Mood Board Tools Survey (https://creately.com/guides/wedding-mood-board/ and others)
Most wedding mood board tools (Milanote, Canva, StudioBinder) use drag-and-drop on desktop, simplified tap-to-add on mobile. The composition view is a "board" that accumulates pieces. Key finding: **templates significantly reduce abandonment** on blank-canvas tools. Starting with a pre-populated "party starter" composition (e.g., "arch + column in teal") gives the customer a baseline to modify rather than building from zero.

### Source 14 — Fanfaire Variants Feature (https://www.fanfaire.io/design-studio)
Fanfaire allows "variants" — the page states: "Offer different versions of a design for more flexibility." The swap feature lets "clients swap elements (e.g., iridescent shimmer wall for gold)." These are Jeff's pre-made alternative design options, not a customer's live palette projected forward onto untouched shapes.

**Correction (from Proxy Loop 1-1):** This source was originally cited as a seed for the color-inheritance upsell mechanic (suggested pieces shown in the customer's chosen palette). That citation does not hold — Fanfaire variants show pre-authored design alternatives, not palette-aware dynamic previews. The color-inheritance mechanic is a design invention, not a pattern sourced here. Source 14 remains valid for the general point that showing design alternatives before commitment is an established pattern in this space; it does not support the specific palette-inheritance behavior.

---

## Research Area 5: Mobile-First Interactive SVG Patterns

### Source 15 — SVG Pointer Events (Smashing Magazine) (https://www.smashingmagazine.com/2018/05/svg-interaction-pointer-events-property/)
The `pointer-events` CSS property controls which SVG regions receive touch/click events. For fill-region interactions, `pointer-events: all` makes the full bounding box interactive. `pointer-events: visibleFill` restricts to only painted fill areas (useful for excluding transparent gaps between balloon clusters). Chrome 65+ supports `pointer-events: bounding-box` — eliminates need for invisible hit-rect overlays.

**Implementation for LT:** Each balloon cluster in the SVG illustration gets its own `<g class="fill-region" id="region-main" pointer-events="all">`. A click/tap listener on the SVG container uses `event.target.closest('[data-region]')` to identify the tapped region. Fill color applied via `setAttribute('fill', hexColor)`.

### Source 16 — SVG vanilla JS click + fill pattern (multiple sources)
From gomakethings.com (https://gomakethings.com/detecting-click-events-on-svgs-with-vanilla-js-event-delegation/) and xjavascript.com:
- SVG elements are in the DOM; `addEventListener('click')` works
- Event delegation at the SVG container level catches all child clicks
- `event.target.closest('[data-region]')` traverses up to find the clickable group
- Fill change: `element.setAttribute('fill', color)` or CSS variable `--fill-color: #hex`
- jQuery: `$(element).attr('fill', color)` equivalent

### Source 17 — SVGator interactive SVG examples (https://www.svgator.com/blog/interactive-svg-examples/)
Interactive SVGs respond to tap on mobile. The key constraint: SVG must be **inline** (not `<img src="...">`) for JavaScript to access the DOM elements. `<object>` and `<img>` tags create isolated DOMs. For LT: balloon illustrations must be inline SVG directly in the HTML — not referenced as external files. This is fully compatible with Frappe's Web Page DocType (content_type = HTML), which allows raw HTML including inline SVG.

---

## Research Area 6: Frappe Website Asset Capabilities

### Source 18 — Frappe v15 Hooks Documentation (https://docs.frappe.io/framework/v15/user/en/python-api/hooks)
`web_include_css` and `web_include_js` inject assets into `web.html` (the portal wrapper). Syntax:
```python
web_include_css = "assets/locally_twisted/css/design-studio.css"
web_include_js = "assets/locally_twisted/js/design-studio.js"
```
Multiple files via list. All values collected across apps. **This is the clean path for the LT design studio:** CSS in `public/css/`, JS in `public/js/`, referenced in hooks.

### Source 19 — ERPNext Web Page DocType (https://docs.frappe.io/erpnext/user/manual/en/web-page)
Web Page DocType supports:
- Content types: Rich Text, Markdown, **HTML** (raw markup, inline SVG supported)
- Script section for custom JavaScript (inside `frappe.ready` callback)
- CSS styling field
- The tool can be a Web Page with `content_type = HTML`, inline SVG in the content, and custom JS in the Script section

**Key finding:** The script section IS available for Web Pages. Inline SVG in the HTML content field is valid. This means the LT design studio can be a single Web Page DocType record with: (a) inline SVG illustration in content, (b) custom CSS in the CSS field or via `web_include_css`, (c) custom JS in the script section.

### Source 20 — Frappe Forum: CSS theme conflict (https://discuss.frappe.io/t/website-theme-and-hooks-web-include-css-conflict/84622)
Known issue: `web_include_css` can conflict with Website Theme CSS. Workaround: use `web_include_css` from hooks (loads after bundle, more specific). For scoped tool pages, page-scoped `<style>` blocks inside the HTML content are the safest approach — they load inline with the page and don't depend on the theme/bundle cascade order.

**Decision for LT mockup:** Use a page-scoped `<style>` block within the Web Page HTML content for the design studio CSS. Avoids the theme-conflict risk documented in the forum.

---

## Summary of Key Research Findings

1. **No existing tool does what LT wants.** Professional tools (Virtualoon, BalloonBuilder, Gemar) are decorator-facing, not customer-facing. Fanfaire comes closest but routes to checkout — LT wants inquiry.

2. **SVG tap-to-fill is technically proven.** Inline SVG + `pointer-events` + event delegation is a well-documented vanilla JS pattern. No library needed.

3. **Mobile color pickers must scroll horizontally, not expand.** Baymard swatch post: horizontal scroll + visible truncation signals "more colors exist"; qualitative guidance on large hit areas. Baymard button research (separate post): 7mm minimum touch target, applied to swatches as tappable elements.

4. **The palette is the product.** LT has 50+ real balloon colors — the picker is a catalog browser, not a color wheel. Customers don't pick from infinity; they pick from LT's actual inventory.

5. **Composition is "accumulate, not arrange."** Customer taps a piece to add it; it joins the stage. No drag-and-drop needed. Reduces mobile friction significantly.

6. **The tool outputs an inquiry, not a cart.** This is the defining architectural choice. "I made this" + "send to Jeff" = the emotional contract.

7. **Frappe can carry this.** Inline SVG in Web Page HTML content, script section for JS, `web_include_css` for shared CSS — no forbidden primitives needed.
