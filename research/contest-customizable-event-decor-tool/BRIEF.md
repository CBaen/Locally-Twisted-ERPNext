# Contest Brief — Customizable Event Decor Design Tool

**Contestants:** 4 collaborative peers (no winner-pick — all 4 surface to GL with ratings + reasons)
**Mode:** Standard (Proxy coach + reflective loops + dissent moment + tightening pass + render gallery)
**Deliverable:** Renderable static-HTML mockup that opens by double-click, plus reasoning prose, plus mandatory research notes with citations.
**Output to GL:** All 4 contestants surfaced side-by-side with peer scoring, Proxy notes, Frappe-recreatable verdict, and orchestrator rating-with-reasons. **GL synthesizes downstream by picking pieces from each.** No top-2 cut. No orchestrator synthesis.

---

## 1. Want — what the customer experiences

A first-time customer arrives at this tool unsure what their event will look like. Within ~30 seconds they're picking colors and seeing a stylized illustration of a balloon arch in those colors. They pick a column shape and place it next to the arch — the column adopts colors they can adjust independently. They keep adding pieces — a centerpiece, a backdrop. The composition grows into THEIR event setup, viewable side-by-side. They walk away feeling **"I made this. I want to talk about it now."**

Two business effects:

- **The merchant (Jeff) opens the customer's saved composition and starts their pitch from THAT** — not from blank.
- **Customers add pieces they didn't come in for.** Coloring a column makes them realize a matching arch belongs there; adding the arch makes them realize a backdrop completes the look. **The tool is a discovery mechanic, not just a configurator.**

The aesthetic frame is **"design book / coloring book that's slightly nicer."** Stylized illustrations of each shape with discrete fill regions, colored from a curated palette. Browseable, scrapbook-feel, return-and-rearrange. Not a wizard. Not a configurator. Not a checkout.

---

## 2. Why this is hard — the prior approach failed

The previous platform (Odoo) shipped a configurator-as-checkout: cascading attribute dropdowns (size × color × add-on × etc.) that ended in "Add to Cart." The live URL is the named anti-pattern: `http://5.78.136.133/shop/what-we-make-balloon-arches-26/classic-organic-arch-99`.

Why it failed (from the project's own decision log):

> *"Choice overload kills conversion at this price point. Customers buying $400+ custom installations don't configure online; they consult."* — `.planning/decisions/site-shape.md`

The competitor survey (9 live sites in LT's tier) confirmed the pattern: **9 of 9 route custom work through consultation, never through configurator**. None of LT's competitors have anything like this tool, because they've all chosen the inquiry-form path.

GL's framing of what the tool actually solves:

> *"The 'Design Studio' concept resolves Jeff's 'customers want to see colors and pick options' instinct without the wrong checkout flow: pick mood + colors + scale → output is an inquiry, not a cart."* — `locally-twisted-decisions.md` 2026-04-27

**You are designing the path none of LT's competitors have taken.** The tool is an inquiry-discovery experience, not an e-commerce surface.

---

## 3. Have — the constraints you're designing within

### Stack (HARD — Frappe-recreatable rule)

You're designing for Frappe v15 / ERPNext v15 with these constraints. Your mockup must use ONLY these primitives — anything else is not recreatable in the production system:

- Plain CSS via `web_include_css` (or a single page-scoped `<style>` block)
- Inline `<style>` and `<script>` blocks on individual pages
- Vanilla JavaScript + jQuery 3.x (already in Frappe's bundle)
- SVG inline rendering
- Bootstrap 4 utility classes
- Single-file CSS or JS includes — no NPM, no module imports from CDN-bundled chains
- Static images (PNG/SVG/WebP) referenceable from `/assets/locally_twisted/`

### NOT available — anything that would force "we can't actually build this in production"

- ❌ React / Vue / Svelte / Angular / SolidJS / any frontend framework
- ❌ Build steps (esbuild, Webpack, Rollup, Vite, Parcel, Snowpack)
- ❌ TypeScript that needs compilation (vanilla `.js` only)
- ❌ CSS-in-JS (styled-components, emotion, etc.)
- ❌ NPM module imports (`import x from 'package'`)
- ❌ Fancy UI libs that pull in React under the hood (shadcn, Material UI, Chakra, etc.)
- ❌ Tailwind unless served from a single pre-built CSS file (no PostCSS pipeline)
- ❌ WebGL, Three.js, Canvas-heavy frameworks if a vanilla SVG approach would carry the experience
- ❌ Any feature requiring a backend mutation during the customer's design experience (e.g., "saves to DB on every click") — read-only client-side state is fine; persistence is downstream

If you find yourself *needing* a forbidden primitive to make the experience work, **flag it explicitly in your reasoning**. Don't silently exceed scope. The point of raising it is so GL can weigh whether the experience is worth a scope shift, not so you can quietly do it anyway.

### The 7 parametric shapes in scope

- Balloon Arches
- Columns
- Garlands
- Picture Perfect Backdrops (also called walls)
- Balloon Drops
- Balloon Bouquets
- Centerpieces

### The color catalog

- 50+ unique balloon colors with hex codes (the canonical catalog is being assembled separately as Slice 9 — `/color-chart`)
- Customers must be able to **see the hex code** while picking — they often match a venue, dress, or brand color and need to verify against an external swatch
- Your mockup can use a representative subset (12-20 sample swatches) since the canonical catalog isn't yet built — but design for "50+, scalable to more"

### Mobile is the primary surface

- 375px is the design baseline
- Customers discover decor on phones (Pinterest browsing, planning during commutes)
- Desktop is secondary — your mockup must include both viewports where the experience meaningfully differs

### LT brand anchors (apply as if production)

- **Teal `#008080`** — primary CTA fill ONLY. Never as text, never as a border.
- **Soft Gray `#595A5C`** — body text
- **Near Black `#1A1A1A`** — headings
- **White `#FFFFFF` / Near White `#FBFBFB`** — page surfaces
- **Accent palette**: Blush #F4DFD7, Soft Blue #C3DCF3, Soft Lemon #F9F871, Lime Pastel #B8FF9E, Seafoam #88FED0, Aqua #80F5F3, Sky Cyan #A0E9FF — used sparingly as thin bands, slider panels, surface tints
- **Headings**: DM Serif Display 400 (single weight — don't apply `font-weight: 600`, it produces faux-bold)
- **Body**: Raleway 300/400/500/600/700
- **8px spacing scale**

The brand frame is "quiet confidence" — photography is the star, color is used sparingly, white space dominates. Your tool exists inside that frame; don't fight it.

---

## 4. Won't Accept (anti-defaults)

- **Configurator-as-checkout.** No "Add to Cart" button. No price displayed during design. The customization happens BEFORE the conversation, not at point of sale.
- **Photoreal rendering.** Stylized illustration only. Photoreal overpromises fixed dimensions/textures and is infeasible to build.
- **Wizard / linear flow.** No "step 1 of 4" framing. Customers must enter, do a little, leave, come back, do more — at any point.
- **Single-product focus.** This is a multi-piece composition tool. A design that only works for "your one arch" misses the point.
- **Visual overload.** Endless dropdowns, walls of 50+ swatches at once, overlapping selectors. Holds up at mobile width or it doesn't ship.
- **Hardware dependencies.** No camera, AR, or device-specific features. Runs on a typical mobile browser.
- **Build-pipeline dependencies.** See section 3 — this is the Frappe-recreatable hard rule.
- **Save/share/return persistence design.** That's a separate problem; don't propose mechanisms for it. Show what the "captured" moment LOOKS like to the customer; how it's actually stored is downstream.
- **Training-data-only design choices.** See section 5 — research is mandatory, citations required.

---

## 5. Mandatory Research — you cannot rely on training data

GL named this directly: **"They cannot rely on their own training data."** The contest exists because prior approaches failed; defaulting to "what design tools usually look like" risks repeating those failures. Your design must be grounded in **what actually works in 2025-2026**, not in patterns from your training corpus.

### What you must research (with cited URLs in your `RESEARCH-NOTES.md`)

1. **Existing balloon design tools** — find the live ones (BalloonAds, Balloons.online configurator, Lush Balloons design tools, any DIY balloon decor tool you can find). Document what they do well and what they do badly. URLs required.
2. **Coloring book / illustration-fill UX patterns** — Pigment, Recolor, kids' coloring apps, design coloring tools. How do they handle fill regions, color picking, "I'm done"? URLs required.
3. **Color picker UX research for 50+ swatches** — when does a flat grid of swatches stop working? How do real design tools (Figma, Canva, Adobe) handle large palettes on mobile? URLs required (find UX studies, design system docs, or actual product screenshots).
4. **Multi-piece composition patterns** — Pinterest pins, scrapbook apps, wedding-planning mood-board tools, Canva. How does a customer arrange multiple pieces without it feeling like a "design tool" in the intimidating sense? URLs required.
5. **Mobile-first interactive SVG patterns** — what works at 375px width with touch input? What breaks? URLs required.
6. **Frappe website asset capabilities** — confirm what you're designing within. Can you embed inline SVG in a Web Page record? Can `web_include_css` carry the CSS? `WebFetch` against `https://frappeframework.com/docs/v15/user/en/website` and the relevant subpages. URLs required.

### How research figures into the deliverable

- Your `RESEARCH-NOTES.md` is a deliverable in Round 1.
- Each major design choice in your mockup must have a citation linking back to research that informed it. Example: "Color picker uses recently-used row at top because [BalloonAds URL] proved it reduces re-pick clicks by 40% in their published data" — not "Color picker uses recently-used row because that's a common pattern."
- The Proxy coach's first reflective loop will probe research quality. Claims that look training-data-derived ("most design tools do X") will be flagged. Expect the question: *"Where did you read that? Cite the URL."*
- It's fine to cite research that contradicts what you ultimately did — argue why your context overrides the broader pattern. Examples beat platitudes.

### Tools available for research

- `WebSearch` — find sources
- `WebFetch` — read sources end-to-end (use this for Frappe docs at `frappeframework.com/docs/v15/user/en/website`)
- If a `context7` or similar docs MCP is available in your tool list, you may use it — but don't depend on it; WebFetch covers the same ground.

---

## 6. Open To (the design space)

The contest is **collaborative, not competitive.** Every contestant wants every other contestant to win. Bring your distinct angle; score peers generously. The output is "all 4 perspectives surfaced" — GL picks pieces from across the field.

You are open architecturally:

- **SVG-based composition** is the likely strongest fit, but other directions (CSS grid + sprite color-mask, vanilla canvas, etc.) are welcome if you can defend them.
- **Color picker patterns** — palette tiles, hex-input boxes, recently-used row, eyedropper-from-image — propose what fits "design book" feel.
- **Composition layout patterns** — fixed grid, free-arrange, horizontal scroll of "pages" — propose what holds up on mobile and feels book-like.
- **Number of fill regions per shape** — 1 (whole shape one color), 2-3 (main + accent), or many (per-balloon control) — your call. Argue for the level you pick.
- **The Proxy coach can suggest pivots** if a direction isn't producing the experience above. Listen.
- **Flag where you'd want to escape Frappe-native** if a primitive can't carry your experience cleanly. Don't silently exceed scope; raise it explicitly.

---

## 7. Questions you must answer (in your reasoning + your mockup screens)

Each contestant produces stylized renderable mockups + concise reasoning answering:

1. **What does coloring ONE shape look like?** Show the customer entering, picking a shape, applying colors from the palette. How do fill regions communicate themselves? How does the shape respond to selection?

2. **What does the COMPOSITION view look like?** Show 2-3 colored shapes living together — an arch + matching column + centerpiece. How does the customer see them side-by-side? How does the surface scale on mobile vs. desktop?

3. **How does the color picker handle 50+ colors?** Show how many are visible at once, how the customer navigates them, how the hex code surfaces, how a chosen color gets committed. Address scaling without overwhelming.

4. **What does the customer's "I'm done for now" moment look like?** They've designed something. They want to walk away (and probably return later). What does the tool show them? How does the design feel "captured" without specifying the persistence mechanic?

5. **What's the discovery upsell mechanic?** A customer who came for a column finishes coloring one. How does the tool surface that "an arch in these same colors would belong here"? Subtle suggestion? Visual hint? Empty placeholder waiting to be filled?

6. **What's the simplest version that captures the essence?** Articulate a v1 scope that's MINIMUM viable — not maximalist. Where would you cut to ship sooner? Defend your floor.

---

## 8. Deliverables — what to produce in your `contestant-{N}/` directory

### Round 1 (blind) — write these files

```
contestant-{N}/
├── RESEARCH-NOTES.md       # Your research summary with cited URLs (mandatory FIRST)
├── REASONING.md            # ~500-700 words covering the 6 questions in section 7
├── mockup/
│   ├── index.html          # Gallery page that links to each screen state
│   ├── styles.css          # All your CSS (single file)
│   ├── script.js           # All your JS (single file, vanilla + jQuery only)
│   ├── 01-entry.html       # Customer arrives at the tool
│   ├── 02-color-one.html   # Coloring a single shape
│   ├── 03-picker.html      # Color picker open with hex + 50+ colors
│   ├── 04-composition.html # 2-3 shapes living together
│   ├── 05-done.html        # The "captured for later" moment
│   └── 06-upsell.html      # Discovery moment (next-piece-suggested)
├── ROUND-1-COMPLETE.md     # One-paragraph summary; signals to orchestrator
└── (optional sketches, notes)
```

**Render check:** every screen above must open in Chrome/Edge by double-click without a server, build step, or NPM install. The orchestrator runs Playwright across all screens (mobile 375px + desktop 1280px) for the gallery — so the screens MUST self-render. Broken renders flag the contestant for tightening.

### Round 2 (mutual visibility) — additional files

```
contestant-{N}/
├── ROUND-2-CHOICE.md       # Path A (refine) / B-lean (commit) / B-pivot (change frame) + reasoning
├── (refined or replaced files per path)
└── ROUND-2-COMPLETE.md
```

### Reflective loops

The Proxy coach will send 2-3 perspective-shift prompts per round. Each writes a `PROXY-LOOP-{round}-{n}.md` file to your dir. You read, reflect, optionally adjust your work. Each loop is a chance to push the work further — you don't have to make changes, but document why if the loop didn't move you.

### Peer scoring

You score the other 3 contestants on 4 dimensions (1-10 each):
- **Experience quality** — does the customer come away feeling "I made this"?
- **Scope discipline** — minimum viable, not maximalist?
- **Frappe-native fit** — recreatable in production stack? No forbidden primitives?
- **Customer clarity** — would a non-designer arriving cold understand the tool in <30s?

Score generously. Score honestly. Lowballing peers to look better undermines the exercise.

### Dissent moment

After scoring, you choose: Continue / Step Away / Wildcard Pivot. See orchestrator's dissent message when it arrives.

### Tightening pass (top contestants only — see note below)

**Adapted for collaborative mode:** in normal contest format, only top-K get tightening. Since GL wants ALL 4 surfaced, **all 4 contestants get a Proxy tightening pass** — Proxy writes a "tighten this, keep this" note for each, and each contestant applies the tightening.

---

## 9. Collaborative Tone — how this differs from a competitive bake-off

This contest is collaborative. Translation:

- Don't position your work as superior to peers in your reasoning. Position your work as your distinct angle.
- When you score peers, find what to BORROW, not what to reject. The synthesis (which GL does, not the orchestrator) is "absorb the best of all 4." Score generously.
- If a peer's idea makes you reconsider yours, that's a Round 2 opportunity, not a Round 1 mistake.
- The Proxy coach is encouraging, not adversarial. They push you toward better, not toward submission. If their note doesn't land, document why; don't apologize.

---

## 10. Output to GL (what surfaces at the end)

Not a top-2. Not an orchestrator synthesis. **All 4 contestants side-by-side**, with for each:

- Concept name + one-line elevator summary
- Render gallery (Playwright screenshots at mobile + desktop for all 6 screen states)
- Direct double-click access to the contestant's `mockup/index.html`
- Peer scoring summary (mean + per-dimension breakdown + standout praise quotes)
- Proxy notes (loop notes + tightening notes)
- Frappe-recreatable verdict (PASS / CONCERNS — with specific concerns flagged)
- Research grounding (citation count, cited URL highlights)
- Orchestrator's rating-with-reasons (1-10 across 4 dimensions, with one-paragraph rationale per dimension — NOT to pick a winner, but to give GL a structured map of strengths/weaknesses)
- Distinctive moves (what THIS contestant brings that others don't)

GL synthesizes. GL picks pieces from across the 4 to inform the implementation phase (separate session).

---

## 11. Honesty Pact

If at any point during the contest you realize:

- The brief is structurally flawed
- A constraint forces a bad design
- You're producing something you don't believe in
- The Proxy coach's note doesn't move you and you can't articulate why
- You can't research enough to ground a claim and you're tempted to fall back on training memory

**Say it.** Write it in your `REASONING.md` or in a dedicated `CONCERNS.md`. Better to surface friction than to ship a polished thing you don't stand behind.

---

*Brief authored by orchestrator 2026-04-29 from `research/contest-customizable-event-decor-tool/research-brief.md` (the seed brief written earlier) + GL's 2026-04-29 contest configuration directives + project decision log + style guide. Approved by GL before contestant dispatch.*
