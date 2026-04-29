# Research Notes — Contestant 3
## Customizable Event Decor Design Tool — Round 1

---

## Area 1: Existing Balloon Design Tools

### Source 1: Virtualoon
**URL:** https://www.virtualoon.com/
**What I learned:** Virtualoon is a professional balloon design tool with a Sales Tool mode that embeds on customer-facing sites. Customers can pick pre-made design templates and change colors via "color buttons" (swatches), generating an automated mock-up confirmation email. Key UX finding: the Sales Tool limits customers to color-swapping a PRE-MADE composition rather than building from scratch. This is the pattern we should learn from but go beyond — the template-first approach reduces blank-canvas anxiety, which is real. The limitation: customers can't compose multiple pieces independently.

### Source 2: Gemar Creator / gemarcreator.com
**URL:** https://www.gemarcreator.com/
**What I learned:** Gemar Creator is pro-facing (B2B), not customer-facing. It has 200+ balloon types, preset gallery of complete compositions, and an "Inspector bar" for individual balloon control. The preset gallery pattern is the UX finding worth borrowing: users don't start from nothing — they start from a recognizable arrangement and personalize. Limitation: 15-day free trial, account creation required — completely wrong model for a customer landing page where you want zero-friction entry.

### Source 3: BalloonBuilder
**URL:** https://balloonbuilder.com/
**What I learned:** BalloonBuilder targets professionals and features 3D rendering, real-time 3D scene (SceneBuilder in beta), and auto-count calculators. Explicitly noted as "optimized for computer screens" with mobile controls "not perfectly suited for small touchscreens." This is the canonical failure mode: building a design tool for desktop professionals and calling it customer-facing. The 3D photoreal rendering approach is what the brief calls a "won't accept" (overpromises fixed dimensions/textures). What to take: the idea of a "scene" as the unit of composition — multiple pieces placed together — is correct. The execution (3D rendering) is wrong for our context.

### Source 4: Balloon Design Studio (balloondesignstudio.com)
**URL:** https://www.balloondesignstudio.com/
**What I learned:** This studio, like all 9 competitors in LT's tier noted in the brief, uses pure consultation model — browse gallery, then contact. No configurator, no design tool. This confirms the brief's claim that "9 of 9 route custom work through consultation." Our design tool is genuinely differentiated in this market — no one has done this in the customer-facing way the brief describes.

### Source 5: Gemar USA tools overview
**URL:** https://gemarusa.com/blog/online-tools-for-balloon-decorators/
**What I learned:** The industry consensus is that Gemar Creator is the only balloon-specific design tool of note. General tools (Canva, Procreate, Photoshop) are used for mockup photography and social media, not customer-facing design. The gap this project fills is real and uncontested.

---

## Area 2: Coloring Book / Illustration-Fill UX Patterns

### Source 6: Pigment App — Emma Rose guide
**URL:** https://emma-rose-portfolio.com/blog/pigment
**What I learned:** Pigment's core satisfaction driver is "immediate visual feedback combined with creative flexibility and community recognition." Key UX mechanics: (1) Tap-to-Fill mode for beginners (tap a region, it fills — dead simple), (2) multiple fill types beyond solid (fade, metallic, etc.) for power users, (3) gamification via "Dailies" (small completion loops), (4) freemium upsell via feature gating. For our context: Tap-to-Fill is the right primitive for our audience (non-designers). The discovery mechanic maps directly: in Pigment, completing one page suggests the next; in our tool, coloring one shape should surface what goes with it.

### Source 7: Best coloring apps 2026 comparison
**URL:** https://coloringfun.net/content/2025/12/19/best-coloring-apps-in-2026-15-apps-tested-free-paid-options-compared/
**What I learned:** The best-reviewed coloring apps share two patterns: (1) discrete, clearly bounded fill regions — users never wonder "what will I fill when I tap here," and (2) a curated default palette with the ability to drill deeper. Apps that front-load a massive palette before the user has even started coloring score poorly. The "start simple, unlock more" palette pattern is the research-backed approach.

---

## Area 3: Color Picker UX for 50+ Swatches

### Source 8: Baymard Institute — Mobile Color Swatches
**URL:** https://baymard.com/blog/mobile-interactive-color-swatches
**What I learned:** This is the most critical research finding for the color picker. Baymard's research (from live e-commerce audits) found that 57% of sites fail to show all color options on mobile, forcing extra page loads. Their recommended pattern for large palettes: **horizontal scrolling with a truncated rightmost swatch as a visual affordance** that more swatches exist. Expandable sections work for small palettes; for 50+ colors horizontal scroll is the right primitive. "Inline scroll hijacking" (a scrollable color panel inside a scrolling page) is explicitly flagged as a failure mode to avoid.

### Source 9: Mobbin glossary — Color Picker patterns
**URL:** https://mobbin.com/glossary/color-picker
**What I learned:** (The page returned a 403 for full content, but the search summary captured key patterns.) Four main design variants: palette, color slider, color wheel, color area. For our use case (curated brand balloon colors, not arbitrary hex picking), the palette variant is correct — swatches with circular indicators and a ring/check mark for selection. Text labels alongside swatches help colorblind users.

### Source 10: IxDF — UI Color Palette 2026
**URL:** https://ixdf.org/literature/article/ui-color-palette
**What I learned:** For 2025-2026, structured color systems use primitive tokens (named color families). For our balloon palette, this suggests grouping colors by family: reds, pinks, blues, greens, neutrals. Grouped categories outperform a flat unsorted grid of 50+ for navigation. WCAG 2.1 AA compliance is now an active compliance requirement (European Accessibility Act, June 2025). Each swatch needs sufficient contrast on its label.

---

## Area 4: Multi-Piece Composition Patterns

### Source 11: DesignFiles Blog — Moodboard Apps
**URL:** https://blog.designfiles.co/moodboard-apps/
**What I learned:** Mobile-first moodboarding apps that work use: drag-and-drop for adding pieces, one-tap background removal, freeform canvas. But for our context, freeform drag-and-drop is WRONG — it introduces "design tool in the intimidating sense" anxiety the brief explicitly warns against. The moodboard app that maps best to our need: Canva's grid-based templates, where structure exists (N slots) but the user fills each slot. Key finding: **slot-based composition beats freeform for non-designer users**. Users know "I have 3 slots to fill" rather than facing an infinite canvas.

### Source 12: The Knot — Wedding Mood Board
**URL:** https://www.theknot.com/content/how-to-make-an-inspiration-board
**What I learned:** Wedding planning tools succeed by giving customers a "here's what goes together" starting frame, not a blank canvas. The pattern: "here are the slots for ceremony + reception + florals" — predefined categories give structure. For balloon decor: "here's your arch slot, your column slot, your centerpiece slot" — same structure applied to event decor. The goal is "I see what my event could look like" not "I built something from scratch."

### Source 13: Upsell/discovery UX — Medium article by Srihari GP
**URL:** https://medium.com/@srihari45.design/the-ultimate-playbook-for-upselling-cross-selling-in-e-commerce-ux-design-a-user-experience-1ed388ea4dc7
**What I learned:** Two critical findings: (1) The Zeigarnik Effect — people remember incomplete tasks better than completed ones. An empty slot in the composition view is more compelling as an upsell mechanic than a product recommendation card, because the user's brain treats the empty slot as an unfinished task that needs completing. (2) Hick's Law — limit to 2 alternatives maximum when suggesting additions, to avoid choice paralysis. Don't show "here are 4 shapes that would go with your arch" — show "an arch in these colors would complete this."

---

## Area 5: Mobile-First Interactive SVG Patterns

### Source 14: SVG Tutorial — Interactivity
**URL:** https://svg-tutorial.com/svg/interaction
**What I learned:** Inline SVG in HTML supports `document.getElementById()` targeting of path elements by ID. The standard pattern for fill-region click: assign IDs to path elements, add click event listeners, change `element.style.fill` or `element.setAttribute('fill', color)` on click. This is confirmed working with vanilla JS and jQuery. Touch events: the `click` event fires on tap on mobile (with ~300ms delay in older browsers, but modern mobile browsers fire it immediately with `touch-action: manipulation` CSS).

### Source 15: GeeksforGeeks — SVG color change on click
**URL:** https://www.geeksforgeeks.org/javascript/how-to-change-svg-icon-color-on-click-in-javascript/
**What I learned:** Two equivalent techniques: `element.setAttribute('fill', color)` and `element.style.fill = color`. Both work for inline SVG path elements. For our multi-region balloon shapes, the pattern is: assign ID to each fill region (`data-region="main"`, `data-region="accent"`), listen for click/tap on each, apply the currently selected palette color. This is completely achievable with vanilla JS — no framework needed.

### Source 16: MDN — SVG in HTML
**URL:** https://developer.mozilla.org/en-US/docs/Web/SVG/Guides/SVG_in_HTML
**What I learned:** Inline SVG is embedded by pasting the full SVG markup into HTML. CSS properties (fill, stroke, fill-opacity, transform) work directly on SVG elements. The `viewBox` attribute makes SVG scale correctly to any container width — critical for responsive mobile design. No JavaScript framework needed; inline SVG + vanilla JS is a complete, standards-compliant approach.

---

## Area 6: Frappe Website Asset Capabilities

### Source 17: Frappe Forum — CSS include method
**URL:** https://discuss.frappe.io/t/what-is-correct-way-to-include-css-file/92401
**What I learned:** The confirmed pattern for website-scoped CSS in Frappe v15: place CSS in `app_name/public/css/`, add `web_include_css = "/assets/app_name/css/filename.css"` to `hooks.py`, then run `bench build --app appname`. This loads the CSS on all website pages. For page-scoped CSS, `custom_page.css` alongside `custom_page.html` in `www/` auto-associates. Both patterns confirmed by forum contributors as working in v15.

### Source 18: Frappe Docs — Portal Pages
**URL:** https://docs.frappe.io/framework/user/en/portal-pages
**What I learned:** This is the definitive confirmation of what we can build. From the docs: "Every frappe app including frappe comes with a `www` folder which directly maps to website urls." Page-specific JS: create `custom_page.js` alongside `custom_page.html` — automatically associated. This means our design tool lives at `www/design-studio.html` + `www/design-studio.js` + `www/design-studio.css`. Inline SVG can be embedded directly in the `.html` template (Frappe renders the HTML as-is). The Python controller (`design-studio.py`) provides any server-side data. **Conclusion: the full design tool is buildable within Frappe's native www/ pattern with no forbidden primitives.**

### Source 19: Frappe Agiliq — How webpages render
**URL:** https://www.agiliq.com/blog/2018/08/frappe-how-webpages-render/
**What I learned:** Frappe web pages extend `base.html` which includes Bootstrap CSS and Frappe's own CSS bundles. The "Style using CSS" field in a Web Page record is a page-scoped style block. jQuery is already in Frappe's bundle on website pages. This confirms that our mockup's approach — inline SVG + page-scoped CSS + jQuery — maps exactly to what's buildable in Frappe without any additional setup beyond a bench build.

---

## Summary of Key Research Findings

1. **No customer-facing balloon design tool exists** that does what the brief describes. The market is wide open.
2. **Tap-to-fill (Pigment's Tap-to-Fill mode)** is the right UX primitive for non-designer users coloring SVG regions.
3. **Horizontal scrolling swatches** (Baymard) beat collapsible sections for 50+ colors on mobile.
4. **Slot-based composition** (wedding moodboard pattern) beats freeform canvas for non-designers.
5. **Empty slots trigger the Zeigarnik Effect** (upsell research) — they're more compelling than recommendation cards.
6. **Inline SVG + vanilla JS** is technically complete for fill-region interactivity, and fully Frappe-recreatable via `www/` pages.
7. **Frappe www/ pages** support page-scoped CSS and JS files — our entire tool fits inside one `www/design-studio.html` + supporting files.
