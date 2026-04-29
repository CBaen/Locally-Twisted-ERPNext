# Reasoning — Contestant 3
## The Coloring Page Frame: Slot-Based Discovery with Tap-to-Fill

---

### My Angle

My distinct frame: this tool is **a coloring page for grown-ups, not a configurator**. The customer arrives at a page that looks like a page from a design book — stylized balloon illustrations in outlines, empty, waiting to be colored. They tap a region, choose from a curated palette, and the region fills. They add a second piece. The page comes alive with their colors. They walk away with a snapshot of an event that feels unmistakably theirs.

This frame resolves every "won't accept" in the brief:
- No checkout logic — there's nothing to add to a cart in a coloring page
- No wizard — you can start anywhere, do as little or as much as you want
- No photoreal — stylized outlines are inherently not photorealistic
- No blank canvas anxiety — the shapes are already there, waiting

The competitive research confirms no customer-facing tool in LT's tier does this [balloondesignstudio.com, gemarusa.com blog]. Our space is uncontested.

---

### Question 1: What does coloring ONE shape look like?

The customer arrives at the tool (01-entry) and sees 3-5 shape cards arranged as a vertical stack on mobile (horizontal row on desktop). Each card is a stylized SVG outline illustration — an arch, a column, a garland — rendered as a soft pencil sketch on near-white. The shapes look like they belong in a design book: deliberately illustrated, not photorealistic [Pigment app's illustrated coloring pages, emma-rose-portfolio.com/blog/pigment].

They tap "Arch." The card expands. The arch SVG fills the screen. Fill regions are visible as discrete segments — different "zones" of the arch (main balloon color, accent color, secondary accent). The regions have a very subtle dashed-stroke outline to signal "this area is fillable" — the same affordance coloring books use [Pigment Tap-to-Fill mode, pixiteapps.com].

A palette tray slides up from the bottom (mobile) or appears as a side panel (desktop). They tap a teal balloon on the palette. The main region fills immediately — no animation delay, just immediate fill. This is the satisfaction moment. The visual feedback is instant [Pigment's core satisfaction driver: "immediate visual feedback"].

The shape now has one color applied. The accent region still shows the dashed outline, waiting. This incompleteness is deliberate — it's the Zeigarnik Effect at work [Laws of UX: lawsofux.com/zeigarnik-effect/ — "provide clear signifiers of additional content"]. The brain registers the unfinished accent region as a "task open." The customer taps the accent region, picks a blush. Now the shape feels finished and theirs.

---

### Question 2: What does the COMPOSITION view look like?

After coloring an arch, the tool surfaces the "Add to composition" button. The customer taps it. The colored arch shrinks to a thumbnail and appears in a horizontal composition tray at the bottom of the screen.

They tap "Column" from the shape cards. Color it. Add it. The composition tray now holds arch + column. At any point they can tap "View full composition" — the composition view (04-composition) fills the screen, showing the arch and column illustrations side by side against a near-white surface with a thin color accent band at the top matching their chosen palette. It feels like a page in a design book: a snapshot of their event's color story.

On mobile (375px), the composition view stacks the shapes vertically in a scroll container — each occupies about 40% of viewport height so two are visible with a hint of the third below. On desktop (1280px), they arrange horizontally in a centered 3-up grid, each card sized to about 320px wide.

The brief is clear: "design book / coloring book that's slightly nicer." My composition view is literally designed to look like an open spread in a design book — the two shapes sit on facing pages, the customer's palette echoed as a thin accent band across the top.

---

### Question 3: How does the color picker handle 50+ colors?

The palette tray shows 16 swatches in a 4×4 grid on initial open — visible without scrolling. Below that grid is a "More colors" section organized into families (Reds & Pinks, Blues & Greens, Neutrals & Whites, Novelty). Each family is a horizontally scrolling row of swatches, with the rightmost swatch visibly truncated to signal "scroll for more" [Baymard Institute research, baymard.com/blog/mobile-interactive-color-swatches].

Each swatch: 40px × 40px circle (hit-target safe for thumbs), with a thin border ring appearing on tap to confirm selection. The hex code for the focused swatch appears in a pill beneath the grid: `#F4DFD7 — Blush Pink`. This persists until a different swatch is tapped, so the customer can match a venue color without hunting.

The flat unsorted 50+ grid is explicitly rejected per my research. Two sources ground this choice: (1) Baymard Institute [baymard.com/blog/mobile-interactive-color-swatches] establishes that horizontal scrolling avoids pushing content off screen and that a truncated rightmost swatch signals "more exists" — their tested pattern is a single flat scrollable row, but the principle (scroll over grid-expansion) applies per family section in my design. (2) Adobe Spectrum's design system documentation [adobe.design/stories/design-for-scale/naming-colors-in-design-systems] establishes family-based color naming as the correct organizational structure for large palettes — "use common words (blue, not oceanic)" paired with brightness scales. My implementation applies Baymard's scroll principle within Adobe-style family groupings: 16 "hot" swatches up front in a 4×4 grid, then family-labeled horizontal-scroll rows below. This is my own configuration combining both principles; Baymard did not test this exact 2D arrangement.

---

### Question 4: What does the "I'm done for now" moment look like?

The customer has colored 2+ pieces. They're looking at the composition view. There's a "Capture this design" button at the bottom — teal fill, the only teal on the page. Tapping it produces a "design card" view: the composition displayed as a tall card (portrait, phone-screenshotable) with the LT wordmark in the corner, a brief summary ("Your arch in Blush & Seafoam with a matching column"), and a "Send this to Jeff" CTA that opens the inquiry form pre-populated with their color choices.

The brief says: "Show what the 'captured' moment looks like; how it's stored is downstream." So the design card is a visual summary — it communicates "this is saved" through the card UI even though the actual persistence mechanism (session storage, URL state, or form data) is a separate concern. The card is designed to be screenshotted and texted to a friend or spouse — the sharing mechanic doesn't require us to build sharing.

---

### Question 5: What's the discovery upsell mechanic?

This is where the slot-based composition pattern earns its place. After the customer colors and adds their first piece, the composition view has empty slots with placeholder outlines: a soft gray arch-shaped silhouette in "Column" position, a soft gray round shape in "Centerpiece" position. These aren't recommendations — they're empty slots in the customer's own design.

The Zeigarnik Effect grounds why this works: people remember and are drawn to resolve uncompleted tasks [Laws of UX: lawsofux.com/zeigarnik-effect/ — "people remember uncompleted or interrupted tasks better than completed tasks"; ux-bulletin.com/zeigarnik-effect-ux/ — explicitly lists "empty states that reference incomplete workflows" as a Zeigarnik application]. The empty slot is not a recommendation card; it is a gap in the customer's own design. The distinction matters: a recommendation card asks the customer to buy something new; an empty slot tells the customer their own work is unfinished. The second framing is less salesy and more true to the coloring-page frame.

**Honest caveat:** This application — a visual placeholder slot in a design tool — is a principled extension of the Zeigarnik principle as documented in UX literature. It has not been user-tested specifically for balloon design tools. The prediction is grounded in theory; it would need testing to confirm it works at this fidelity for this audience.

The empty column silhouette says "there's a space here in your design that could have your colors on it." No text needed. The customer taps the silhouette and it opens the column shape ready to color. The upsell is implicit, not explicit.

When the customer reaches the done screen (05-done), there's also a single contextual note: "Customers who add a matching column often find they want the arch too." This is the Hick's Law application — show one suggestion, not five [Medium, Srihari GP: medium.com/@srihari45.design — the Hick's Law guidance in that article is the one claim from that source that holds up; the Zeigarnik claim in that article does not]. One suggestion is an invitation; five suggestions are a menu.

---

### Question 6: What's the simplest v1?

My v1 floor, in priority order:

1. **One shape, one fill region, the palette, the inquiry output.** A customer taps "Arch," colors it (main region only), taps "Get a quote," and the inquiry form pre-populates with "Arch in #008080." That's a complete minimum viable loop.

2. **Then: second fill region (accent color).** Now the arch has main + accent, matching what real balloon arches look like.

3. **Then: composition of 2 shapes.** Arch + column, side by side.

4. **Then: all 7 shapes, discovery mechanic, full palette.**

What I'd cut from my mockup to hit the floor: the composition view, the upsell slots, and the "capture this design" card. The core experience — tap a shape, color it, send an inquiry — is one screen and one form. Everything else is discovery enhancement on top of that floor. This aligns with the brief's "discovery mechanic, not just a configurator" framing: the floor is the configurator, the layers on top are the discovery.

---

### Frappe-Recreatability Declaration

Every primitive in my mockup is vanilla JS + inline SVG + plain CSS + jQuery. The design tool lives at `www/design-studio.html` + `www/design-studio.css` + `www/design-studio.js` in a Frappe custom app, confirmed by the portal pages documentation [docs.frappe.io/framework/user/en/portal-pages]. The page-specific CSS and JS auto-associate. No build step, no NPM, no React. The SVG shapes are inline markup that will render identically in a Frappe Jinja template.

The one area to flag: the SVG illustrations themselves (the stylized balloon shapes) need to be created as proper SVG files with named path IDs for each fill region. In the mockup I've created these as simple inline SVG shapes. In production, they'll need a designer to draw the actual LT-style illustrations — that's art direction work, not a code scope flag.

---

### What Makes My Angle Distinct

My frame is **"coloring page over configurator."** The other contestants may approach this from a UI component architecture angle (how do the controls work), from an animation/feedback angle (how does the color application feel), or from a composition/layout angle (how do multiple pieces arrange). My angle is thematic — the coloring page frame resolves the core tension in the brief (customer agency without checkout pressure) at the conceptual level, and every UX decision flows from it. A customer who arrives at a coloring page doesn't feel like they're "buying" — they feel like they're playing. That's the psychological shift the brief is asking for.
