# Peer Scoring — Contestant 1

Scoring the other three contestants on the four dimensions from BRIEF.md Section 8. Generous-but-honest. High scores where earned.

---

## Contestant 2

**Experience quality** (does the customer come away feeling "I made this"?): **9/10.**
The cascading ghost with pre-tinted inheritance is the most emotionally satisfying discovery mechanic in the field — the customer sees their event "already built" one step ahead of where they are. The design-attribute selector (Swirl/Layered/Organic) on the coloring screen, with color cap enforcement and clear nudges when a cap would be exceeded, makes the tool feel honest without being limiting. One tenth off: the entry screen remains a cold gallery with no orientation nudge; the exhausted parent has no help picking a starting point.

**Scope discipline** (minimum viable, not maximalist?): **8/10.**
The v1 floor (one shape, no composition, 20-color flat grid, mailto) is well-articulated and genuinely minimal. The full build is ambitious but every piece is defended — ghost inheritance, design attribute state, loud-failure path, `buildInquiryPayload()` spec, color cap enforcement. No vanity features. One point off: the Design attribute selector + ghost-style inheritance together add meaningful JS complexity that is not strictly necessary for the v1 "send colors to Jeff" floor; the reasoning for keeping them in scope rather than marking them Stage 2 could be tighter.

**Frappe-native fit** (recreatable in production stack?): **9/10.**
The explicit `www/design-studio.html` + `www/design-studio.py` portal page architecture is the right Frappe-native pattern. `frappe.call()` for Lead creation is confirmed infrastructure. No forbidden primitives. The loud-failure `showSendError()` path is a production-quality detail no other contestant matched. One point off: the `localStorage`-backed recently-used row assumes browser storage persists between sessions, which is fine on most phones but not guaranteed; flagging this as a known caveat would have been honest.

**Customer clarity** (would a non-designer arriving cold understand the tool in <30s?): **8/10.**
The bottom sheet stays behind the illustration while the customer colors — NNG research is correctly applied. Region highlights, scale-pulse animations, dotted outlines on uncolored areas: the coloring-book affordances are well-layered. The design attribute selector (Swirl/Layered/Organic) at the top of the coloring screen is the one clarity risk — three pill labels with terminology the customer doesn't know. Contestant 4 solved this more elegantly with visual thumbnails inside the buttons. C2 uses text pills with hint text below, which is a reading task. For a 40%-brain midnight parent, this is a real friction point.

**Total: 34/40**

**Notes:** The cascading ghost with Design-style inheritance is the most technically sophisticated distinctive move in the field and it's cleanly defended. C2's synthesis pairing (ghost earns the multi-piece design; C3's card lands it) is exactly right — these two moves belong in sequence. The loud-failure path and `frappe.call()` Lead creation are the most production-ready details in the contest. Borrow the ghost mechanic. Borrow the color cap enforcement. Borrow the error path discipline.

---

## Contestant 3

**Experience quality** (does the customer come away feeling "I made this"?): **9/10.**
The dual-audience design card is the most complete "I made this" moment in the contest. It simultaneously closes the customer's emotional loop (visual composition they'd screenshot for their spouse) and Jeff's operational loop (supplier-call-ready color names, region labels, phone number in footer). The Proxy Loop 2-1 fix — flipping the CTA order so the one-piece parent has a direct exit from the coloring screen to the done screen — is the strongest customer-flow refinement in the field. The Zeigarnik empty-slot mechanic operates correctly at the composition level (shape slots), not intra-shape; the physics-honesty clarification in REASONING makes this defensible. One tenth off: the design card header names the event "Empowermint & Blush" which requires the customer to have chosen those exact colors — the mockup is hardcoded and doesn't explain how the title would be generated dynamically.

**Scope discipline** (minimum viable, not maximalist?): **9/10.**
The v1 floor is the tightest in the field: one shape, one fill region, 12 swatches, inquiry form. Each layer above it is explicitly listed with rationale. The Hick's Law single-suggestion on the done screen (one upsell, not five) is the correct application of the principle. The "screenshot-and-share" path (Path B) that requires zero build work is elegantly honest. One point off: the done-screen still says "centerpiece" in the upsell suggestion line (post-Round 2), which is a slip against the PRODUCT-DETAILS GL directive removing centerpieces from scope.

**Frappe-native fit** (recreatable in production stack?): **9/10.**
Explicit Frappe portal page architecture (`www/design-studio.html`, no NPM, no build step), correct jQuery + inline SVG, design that lives in a `<style>` block rather than `web_include_css` (avoiding the known cascade conflict). The SVG illustration flag ("the illustrations themselves need to be created as proper SVG files — this is art direction work, not a code scope flag") is the most honest Frappe-reality acknowledgment in the contest — every entry needs this caveat but C3 is the only one who names it clearly. One point off: the `frappe.call()` Lead creation path, which C2 specced out in detail, is implied but not explicitly stated in C3's reasoning. The payload data shape is thorough; the submission mechanics are left to inference.

**Customer clarity** (would a non-designer arriving cold understand the tool in <30s?): **10/10.**
"A coloring page for grown-ups, not a configurator" — this framing is the clearest cold-landing orientation in the contest. The vertical stack of shape cards on mobile (horizontal on desktop) is the cleanest entry layout. The dashed-stroke region outlines signaling "fillable" are the most direct affordance. The Zeigarnik clarification in REASONING (composition-level slots vs. intra-shape regions are different mechanics) demonstrates that the distinction was thought through. The CTA flip from Loop 2-1 means the one-piece parent has a three-tap path to Jeff with zero composition-screen pressure.

**Total: 37/40**

**Notes:** The strongest customer-arrival clarity and the strongest Jeff-side payload in the field. The dual-audience framing is load-bearing — it's not a design flourish, it's the reason every field on the card exists. The C3 + C2 sequence (ghost earns the multi-piece design, C3's card lands it) is the right synthesis pairing. The "Or call: (801) 285-0860" in the card footer is a detail that respects Jeff's existing contact preference and adds zero build complexity — take it in any synthesis. Borrow the CTA flip (coloring screen → done screen directly for one-piece parents). Borrow the phone number in the footer. Borrow the dual-audience framing as the organizing principle for the done screen.

---

## Contestant 4

**Experience quality** (does the customer come away feeling "I made this"?): **8/10.**
The horizontal spread metaphor ("pages in a scrapbook") is the clearest expression of the brief's "design book / coloring book that's slightly nicer" language in the field. Each piece as a card, ~280px wide at 375px (showing 1.3 visible, clear scroll affordance), with "Edit Colors" re-entry on any card — this is the non-wizard, return-and-rearrange experience the brief asked for. The visual thumbnails INSIDE the style toggle buttons (Alternating / Mixed) are the single best plain-language UX refinement in Round 2 — the parent decides with their eyes before their vocabulary engages. Two points off: the recently-used row is empty on first visit (light gray circles), which the REASONING correctly sources to Pigment's top complaint, but on first open the row reads as a loading failure rather than "nothing yet." A subtle "your recent picks will appear here" label would close this. Also: the composition view at 1.3-cards-visible requires a scroll to see more than one piece, which on first arrival may read as "only one piece" to a cold visitor.

**Scope discipline** (minimum viable, not maximalist?): **9/10.**
V1 floor is explicitly articulated: 2 shapes, 1 fill region each, 12 swatches, composition, inquiry form — "~100 lines of CSS and ~80 lines of JS." This is the tightest line-count estimate in the field and it's honest. The "I flag this explicitly per Brief Section 3" SVG illustration caveat is the correct discipline: if the illustrations aren't good, nothing else matters. One point off: the recently-used row (localStorage-backed) is listed as a full-palette feature, not an explicit Stage 2 item. It adds real complexity (state management, localStorage access, defensive coding for first-visit state) relative to the value — could have been clearer about whether it's V1 or V2.

**Frappe-native fit** (recreatable in production stack?): **9/10.**
Bottom sheet as CSS-positioned `div` with `transform: translateY` toggle — no framework, correct pattern. Inline SVG in Jinja template confirmed. jQuery for DOM selectors. The design-style toggle buttons (two pill buttons, no framework) are the most Frappe-native implementation of a design choice selector in the field. One point off: the `data-page="color-one"` attribute on body suggests a JS routing pattern that may be more complex than what the mockup shows — the reasoning doesn't explain how this scales to multiple shapes if each needs its own SVG and fill-region definitions.

**Customer clarity** (would a non-designer arriving cold understand the tool in <30s?): **9/10.**
The visual thumbnails inside the style buttons are the clearest style-choice affordance in the contest — a parent at midnight reads the Alternating pattern (A B A B circles) without knowing the word "Swirl." The plain-language header "How do you want the colors arranged?" is correctly framed as a question about the customer's event, not a category label. The residual risk (C4 names it honestly) is that the Alternating thumbnail is hardcoded and goes stale once the parent changes colors — acceptable for a mockup, Stage 2 fix in production. One point off: entry screen has no orientation nudge for the undecided parent, and unlike C3's direct coloring-page framing, C4's entry relies entirely on the shape cards communicating themselves.

**Total: 35/40**

**Notes:** The thumbnail-inside-toggle button is the most borrowable single UX refinement in the contest — it should be in every synthesis. C4's honest acknowledgment of the stale-thumbnail residual risk is the most epistemically trustworthy disclosure in the field. The scrapbook horizontal-spread metaphor and the SVG illustration caveat are both clean expressions of brief fidelity. Borrow the thumbnails. Borrow the "How do you want the colors arranged?" framing. Borrow the SVG-quality-as-hard-dependency caveat for any implementation notes.

---

## Self-Reflection — Where My Work Is Weakest

**Relative to the field, my weakest dimension is the done screen / handoff.**

C3's dual-audience design card is demonstrably superior to my 05-done.html. C3 closes both loops — customer screenshot moment AND Jeff's supplier-call payload — on one screen, with the color names and region labels in a format that is immediately actionable. My done screen lists piece names and color names but doesn't have the per-region attribution (which color is "main," which is "accent"), doesn't have the phone number fallback, and doesn't have C3's clean two-path architecture (form submit vs. screenshot-and-share). My "pieces considered" crown jewel is also Stage 2, not V1 — it exists only in REASONING.md as a described mechanic, not in a mockup screen. If GL is evaluating what is demonstrable now, C3 wins the done-screen dimension cleanly.

**Second weakness: physics reconciliation stayed in REASONING, not in the mockup HTML.**

02-color-one.html still shows tap-region UX for an Arch, which REASONING.md now says should be a style-then-color-slots flow. The mockup and the reasoning are misaligned. C2 and C4 both updated their coloring screens to show the Design attribute selector. I documented the reconciliation but didn't implement it. That's a gap — a reviewer who opens 02-color-one.html without reading REASONING will see a tap-region Arch that doesn't match the physics section.

**Third: the "Popular colors" label fix was reactive, not proactive.**

The Proxy had to surface the swatch-row label gap. C3 and C4 both had clearer picker labeling from Round 1. I should have caught this before Loop 2-1.
