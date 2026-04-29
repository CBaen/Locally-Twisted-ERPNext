# Peer Scoring — Contestant 4

Rubric anchors from Brief Section 8:
- **Experience quality**: Does the tool feel like "design book / coloring book that's slightly nicer"? Does the customer arrive, pick colors quickly, and feel "I made this"?
- **Scope discipline**: Does it stay inside the brief's constraints — inquiry output (not cart), no wizard, no persistence design, Frappe-recreatable primitives only, discovery mechanic not configurator?
- **Frappe-native fit**: Can everything in the mockup actually be built in vanilla JS + jQuery + inline SVG + plain CSS + Web Page DocType, with no build step, no NPM, no React?
- **Customer clarity**: Does the tool communicate itself to a non-designer, first-time customer at mobile width, under time pressure?

---

## Contestant 1 — "The Color Stage"

**Experience quality: 8/10.**
The entry screen lands cleanly — "Color your event" headline, the soft orientation nudge ("Most people start with an arch") added after Loop 2-1, and recognizable illustrated shape cards. The composition stage abstraction (persistent horizontal strip across all screens) is a strong coherence device: the customer always sees their work-in-progress in the same place. The mini-stage with pre-colored suggestion chips for color inheritance is the most emotionally satisfying upsell mechanic of any contestant — seeing "your arch in your Raspberry + Reflex Champagne" waiting to be confirmed collapses the imagining gap better than any other entry. The done screen is serviceable but lower-polish than C3's dual-audience card. One genuine gap: the Backdrop-as-demo-shape for Round 2 (a sound physics-driven choice) creates a slight coherence gap — the entry screen shows all 7 shapes, but the coloring screen demo is a backdrop, which is the last shape most customers would start with. A reviewer reading the mockup has to mentally translate between what they're shown and what the Arch experience would be.

**Scope discipline: 9/10.**
Stays strictly inside the brief. Inquiry payload (not cart) with name-first color format correctly derived from PRODUCT-DETAILS. Persistence explicitly deferred. Color inheritance flagged as Stage 2. "Pieces considered" payload is the field no other contestant named — and it's the most commercially valuable addition to Jeff's morning briefing of anything in the contest. The only minor slip: the Stage 2 design snapshot (canvas rasterization via data-URI) is flagged but the flagging is so brief it could be missed; a production instance would want this tracked more prominently. Not a deduction, just a note.

**Frappe-native fit: 9/10.**
Named primitives throughout: jQuery `.attr('fill', hex)`, `data-color-name` attributes on region chips, `DesignStudio.buildPayloadLine()` reading from DOM. The explicit note about using page-scoped `<style>` blocks instead of `web_include_css` to avoid the known cascade conflict is the most sophisticated Frappe-awareness in the field — C1 did the work to know the specific failure mode and document the workaround. Color catalog as a JS `var LT_COLORS = { popular: [...], groups: [...] }` object at the top of the script is exactly the right production shape.

**Customer clarity: 7/10.**
The design-style selector (Swirl/Layered/Organic as pills with descriptor sub-labels added after Loop 2-1) is a meaningful improvement over pure vocabulary, but stops short of C4's visual thumbnail approach. A tired parent reading "spiral pattern" below "Swirl" gets more signal than pure vocabulary, but still has to read — no picture. The composition stage strip (160px tall on mobile, ~120px cards) is tight. Entry-screen shape cards at 2 per row (6 cards = 3 rows) is clean; the hint text "2–3 color zones" on the arch card front-loads physics vocabulary the customer doesn't need before they've tapped anything. The Loop 2-1 fixes (orientation nudge, duplicate card removal, "Popular colors" label) are targeted and correct.

**Total: 33/40**

**Notes:** The pieces-considered payload is genuinely the most valuable synthesis contribution from any contestant's Jeff-side thinking. The color inheritance mechanic is the strongest upsell mechanism emotionally. These two together belong in GL's synthesis regardless of whose framework wins.

---

## Contestant 2 — "The Coloring Book That Assembles Itself"

**Experience quality: 9/10.**
The entry screen is the strongest first impression in the field: "What are you dreaming of?" is the right customer-facing question, and the "Most loved" permission badge ("Dozens of couples and parents just like you have designed here — no experience needed") removes the most common first-time hesitation before the customer does anything. The cascading ghost mechanic — one ghost, in the customer's own colors, appearing after each piece completion — is the most spatially coherent implementation of the discovery upsell. The customer never has to imagine placement or color because the ghost is already positioned and already wearing their palette. The "optional" copy fix after Loop 2-1 ("No thanks, I'm done" instead of "Skip") is a small change with real respect for the customer's agency. The composition screen (strip + canvas) feels like the most "design tool–ish" of the four entries, which cuts slightly against the coloring-book-over-configurator frame — the canvas area and strip feel closer to Canva than to a coloring page. This is a legitimate tension, not a failure.

**Scope discipline: 9/10.**
The full `buildInquiryPayload()` + `initDoneScreen()` + loud-failure error path from Loop 1-2 is the only entry that proactively addressed the loud-failure rule from the global standing rule — not because the brief asked for it, but because a correctly-reading instance noticed it applied. That's good judgment. Centerpiece removed, garland ghost correctly replaces it. Ghost style-inheritance (`initGhostInheritance()` reading design attribute from the completed piece) is well-scoped — Stage 1 implementation, not Stage 2 promise. Color cap enforcement (`wouldExceedCap()` nudge when Swirl hits 4 colors) is physics-honest. The only scope flag: the three-pill design selector (Swirl/Layered/Organic) is shown for all shapes including garlands, but per PRODUCT-DETAILS Garlands have their own style vocabulary (Solid/Two-tone/Ombré/Multi-color blend) — this mismatch is small and fixable but not yet addressed.

**Frappe-native fit: 9/10.**
`frappe.call('frappe.client.insert', { doc: { doctype: 'Lead', ... } })` is precisely the right Frappe Lead creation pattern — this is the only entry that uses the actual Frappe API call rather than a generic form POST or mailto. `pointer-events: none` on SVG stroke paths (to prevent accidental taps on structural elements) is a production-level SVG interaction detail no other entry mentions. jQuery event delegation on the SVG container reading `event.target.dataset.region` is correct and Frappe-native. The single `www/design-studio.html` + controller architecture is clean.

**Customer clarity: 8/10.**
Entry screen is the best in the field. The design selector descriptor sub-labels ("spiral pattern" / "color bands" / "mixed & flowing") are functional but, like C1's, require reading. The canvas-plus-strip composition layout requires the customer to understand two simultaneous surfaces — the strip (all pieces) and the canvas (current composition) — which is more to learn than C4's single horizontal scroll. The ghost's "optional" framing is correctly handled post-loop. The bottom sheet picker is described as "clean and genuinely good" by the Proxy and shows in the markup — 3 components (recents, hue-family tabs, hex display) in a well-structured sheet.

**Total: 35/40**

**Notes:** The strongest all-around entry. Entry screen, discovery mechanic, and Frappe API integration are each best-in-field on their dimension. The cascading ghost with color inheritance is the crown jewel and belongs in GL's synthesis as the primary discovery mechanism. The loud-failure path is an engineering contribution that should transfer to the final build regardless of which design frame wins.

---

## Contestant 3 — "The Coloring Page Frame"

**Experience quality: 8/10.**
The 3-step "how it works" strip on the entry screen (①②③ with ultra-brief labels) is the clearest onboarding of any contestant — a parent at midnight knows exactly what will happen before they tap anything. The shape cards with contextual descriptions ("The statement piece. Perfect for entrances, photo moments & backdrops.") are the most customer-voice-appropriate copy in the field; no other contestant writes the shape card descriptions from the customer's event perspective. The coloring screen with 3 fill regions (Main/Accent/Pop) and SVG mirror propagation (tap Main on left, right side auto-fills) is technically elegant — one tap does twice the work, which genuinely reduces coloring friction at mobile width. The dual-audience design card is the strongest done-screen in the field: name-first format, per-region labels, phone number in footer, screenshot-ready portrait shape. The Zeigarnik empty-slot mechanic is the most theoretically grounded discovery approach. The Loop 2-1 CTA flip (coloring screen now offers "Send this to Jeff" as primary, bypassing composition for the one-piece parent) was exactly the right fix — most contestants would have protected their composition mechanic; C3 chose the customer's exit over the feature.

**Scope discipline: 8/10.**
Dual-audience design card is a genuine scope win — it handles the persistence problem by making the screenshot itself the sharing artifact, which requires zero backend work and zero Frappe complexity. The path-A/path-B split (form submission vs. screenshot) is the most elegant "no persistence required" solution in the contest. Minor flag: the done-screen upsell note says "Customers who add a matching centerpiece often find it ties the whole look together" — centerpiece is out of scope per PRODUCT-DETAILS Section 2.7. This was flagged in the field summary; it's not fixed in the visible mockup. Not a major deduction but it's a scope miss that survived through Round 2.

**Frappe-native fit: 8/10.**
All primitives are valid — inline SVG, jQuery, plain CSS, portal page. The mirror propagation mechanic (`data-mirrors="arch-accent"` attribute on circles, iterated by `$('.fill-region[data-mirrors]')`) is a clever vanilla-JS pattern that requires no additional libraries. The Frappe portal pages confirmation is cited. One note: C3's mockup is the most visually complete of the four entries (colored illustrations on the done card, entry screen with ① ② ③ strip, detailed shape cards) — this creates a higher art-direction dependency than other entries. The Frappe-native code is fine; the visual quality implies SVG illustration work that will need a designer in production. This is noted and flagged in the REASONING, so it's not a surprise — just worth naming.

**Customer clarity: 9/10.**
Best in the field on this dimension. The "how it works" trio at the top of the entry screen is the only entry that makes the tool's flow legible before the first tap. Shape card copy is the most human-voice. The dual-audience card is legible to both customer and Jeff simultaneously without one audience crowding out the other. The coloring screen region key (Main / Accent / Pop as small labeled dots in the top corner of the canvas) is unobtrusive and clear. The Loop 2-1 CTA flip was the single most customer-respecting change in any loop across all contestants — the one-piece parent now has a three-tap path to done. The "Or" in empty-slot copy ("Want a centerpiece too? Or a garland?") subordinates the suggestion correctly without hiding it.

**Total: 33/40**

**Notes:** The dual-audience design card is the crown jewel and belongs in GL's synthesis as the done-screen frame regardless of whose discovery mechanic wins. The Zeigarnik open-from-start mechanic is the only theoretically grounded upsell that works before any coloring has happened — this is distinct from every other entry's "after first completion" trigger. The CTA inversion (coloring screen → done screen directly) is the most decisive customer-respect move of any loop across all contestants.

---

## Self-Reflection — Where C4 is weakest relative to the field

Three genuine gaps:

**1. Discovery mechanic is the weakest in the field.**
The "Add a Piece" card with updated contextual text suggestion and ghost arch SVG preview is functional, but it is the most passive of the four approaches. C2's ghost is already dressed in the customer's colors and already positioned spatially. C3's Zeigarnik slots are present from the start and require no completion trigger. C1's pre-colored suggestion chips carry the customer's color names. My suggestion card is text-first ("Garlands pair beautifully with an arch — add one to your design?") with a ghosted SVG, but the ghost is generic (not in the customer's current palette), and the trigger (appearing in the Add card) is the weakest of the four because the card is always visible — there's no earned moment when it appears. The discovery mechanic is load-bearing for the brief's second business effect ("customers add pieces they didn't come in for"), and I'm the weakest on this dimension by a meaningful margin.

**2. Done screen is the second weakest.**
The per-piece attribution table is correct and Jeff-actionable, but it is purely informational. It does not serve a dual audience the way C3's card does (customer emotional moment + Jeff supplier payload on the same screen). It does not feel screenshot-worthy. It does not carry the phone number. The headline "You made something beautiful" is serviceable but not as disarming as C3's "It's looking beautiful" or C2's "This is your event."

**3. Entry screen lacks C2's first-impression warmth.**
My entry screen has the shape cards and an instruction band. C2's "What are you dreaming of?" + permission badge addresses the first-timer's biggest hesitation (am I allowed to be here, do I need experience?) before they do anything. I don't have an equivalent. C1's orientation nudge is warmer than mine. My entry screen is the most functional and least emotionally welcoming of the four.

What I have that others don't: the visual thumbnails inside style buttons (the Alternating/Mixed toggle) is the most portable principle of the contest and the one most likely to propagate to every style choice in the final tool. The construction-physics defense of 2-region simplicity is sound and the only physics-grounded argument in the field. The per-piece attribution table format is cleaner than any other entry's inquiry payload layout. These contributions are real but they are refinements on a frame that the other contestants execute more warmly.
