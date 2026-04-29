# Contestant 2 — Peer Scoring

Rubric per BRIEF.md Section 8. Four dimensions, 1–10 each, max 40.

---

## Contestant 1 — "The Color Stage"

**Experience quality: 8/10**
The coloring mechanic is cohesive. Physics reconciliation (Backdrop as demo shape, Arch/Column/Garland left as-is) is intellectually honest. The pieces-considered payload — surfacing unchosen items rendered in the customer's own colors — is the most novel operator-side idea in the field. It earns its score. Docked two points: two different coloring mechanics on one tool (Backdrop behavior differs from Arch behavior) is a design split that the exhausted parent will not understand, even if it's invisible to them. The risk isn't today — it's the moment Jeff sees the inquiry and the numbers don't map to the piece they're looking at.

**Scope discipline: 8/10**
Centerpiece correctly removed. Balloon Drop added (with the right size hints: 250/500/1000). Duplicate Drop card bug caught and self-corrected in Proxy Loop 2-1 — good epistemic hygiene. Entry screen nudge ("Most people start with an arch") is lightweight and effective. "Popular colors" label above the swatch row is one line of markup, exactly the right weight. No scope creep.

**Frappe-native fit: 9/10**
`data-color-name` / `data-color-hex` attribute pattern is clean and idiomatic — stores the right payload shape directly in the DOM without a separate state object. Frappe Lead field names used natively (`lead_name`, `email_id`, etc.) with no legacy shim needed. The pieces-considered data is two lines of JS and one textarea in the Lead payload — genuinely minimal implementation, not "Stage 2 someday."

**Customer clarity: 7/10**
The two-region model (Main / Accent) is fast and clean. The exhausted parent doesn't need to know construction vocabulary to fill it out. But "Design Style" selector still uses vocabulary that requires translation. C4's visual thumbnail approach (56×16px inline SVG, actual A-B-A-B pattern vs. varied colors) solves this better than any label change. C1 didn't go there. The pieces-considered concept, while genuinely novel, is visible to Jeff but invisible to the customer — which is arguably correct (the customer doesn't need to understand what Jeff sees), but means the customer experience gain is zero.

**Total: 32/40**

---

## Contestant 3 — "The Coloring Page Frame"

**Experience quality: 9/10**
The dual-audience design card is the best Jeff-side handoff artifact in the field. One screen, two jobs: customer screenshots it to show their spouse, Jeff reads it Tuesday morning before calling his supplier. The phone number in the card footer — the one that solves "customer screenshots and loses the submission path" — is the sharpest single detail in the entire contest. The CTA flip after Proxy Loop 2-1 (Send to Jeff as primary, bypass the composition screen on single-piece designs) is operationally correct and will close real sales that would otherwise have been lost to tab-close. Zeigarnik at composition level is the right cognitive model.

**Scope discipline: 8/10**
Centerpiece correctly out. Color names foregrounded with hex as annotation throughout. No scope creep in either round. The CTA flip is additive, not expansive — it shortens the required path rather than adding a new one. The dual-audience framing disciplines every field on the card ("why does this field exist? because Jeff or the customer needs it at a specific moment") — that framing prevents future simplification-away of necessary fields.

**Frappe-native fit: 9/10**
"Empowermint" as SKU — color NAME as the supplier-actionable identifier — maps directly to how Jeff orders from his supplier. The card format is designed to reduce Jeff's Tuesday-morning phone call time, which is exactly the operator-side value ERPNext is supposed to deliver. The Lead payload carries both name + hex, which gives the operator flexibility without requiring them to know the hex.

**Customer clarity: 8/10**
The Zeigarnik open loop ("it looks like a coloring page waiting to be filled") is clean as an entry principle. The design card's customer-facing half is warm and specific ("Here's what you designed"). The CTA flip — making Send to Jeff primary after a single piece — is the right call for the midnight parent who just wants to be done. Docked two points: the coloring mechanic itself (Zeigarnik, composition-level tension) is sophisticated enough that it may not survive contact with a distracted 11:47 PM session on a 375px screen. The theory is right; the implementation pressure-test is incomplete.

**Total: 34/40**

---

## Contestant 4 — "The Coloring Book"

**Experience quality: 7/10**
The 2-region model (`gcd(2,4)=2`) is the best-defended physics argument in the field. Horizontal spread layout is the right call for a mobile-first tool showing multiple balloon types side by side. The Swirl/Organic toggle is load-bearing and the Proxy Loop 2-1 response to it — visual thumbnails inside the style buttons, "Alternating" / "Mixed" as labels, "How do you want the colors arranged?" as the section header — is the strongest single clarity move in the contest. But: the 8-swatch quick-color row without the "Popular colors" label context (that's C1's fix) leaves the midnight parent wondering what they're looking at. And the per-piece attribution table in the inquiry payload is correct and useful but may be the most complex field-level spec in the field — the right payload for Jeff but a lot of architecture for what the customer sees as "tap tap tap, send."

**Scope discipline: 9/10**
Scope commitment is the tightest in the field. The 2-region simplicity is defended on physics, not taste. Garland replaces Centerpiece. The tool doesn't try to do more than its scope requires. The Proxy Loop 2-1 response is precisely targeted: two changes to the toggle, zero unrelated additions. The "We Don't Do Time" discipline maps cleanly here — this tool is built for what's needed now, not staged for later features.

**Frappe-native fit: 9/10**
53 real LT named colors in the catalog — this was a required correction and C4 made it cleanly. The Swirl/Organic (now Alternating/Mixed) toggle state maps directly to how Jeff's supplier orders work: Alternating = two specific colors alternating, Mixed = palette with organic arrangement. The per-piece attribution table in the payload gives Jeff exactly what he needs for a Tuesday-morning supplier call: piece type, style, colors, attribution.

**Customer clarity: 9/10**
Visual thumbnails inside style buttons is the best answer to the vocabulary problem in the field. The 56×16px inline SVG showing A-B-A-B circles (in the actual current session colors) vs. 4 different colors at 55% opacity is a complete communication that requires zero balloon construction vocabulary. "How do you want the colors arranged?" is the right question. The active color inheritance — thumbnail updates to show the current session colors, not hardcoded demo colors — is the right direction (acknowledged as Stage 2 in the mockup but correctly identified as the production fix).

**Total: 34/40**

---

## Self-Reflection — Where Contestant 2's Work Is Weakest

Three places where the field has me:

**Done screen.** C3's dual-audience card (warm customer half / Jeff-actionable half, phone number in footer, portrait-shaped for screenshotting) is the best completion artifact in the field. My done screen delivers the right payload (name-primary colors, piece list, custom notes field) but in a format the customer can't easily screenshot and send to their spouse, and Jeff can't read in 30 seconds before a supplier call. The format matters as much as the content. I didn't build the format.

**Style selector vocabulary.** I have "Swirl / Layered / Organic" with `.design-pill__desc` spans ("spiral pattern", "color bands", "mixed & flowing"). C4 has visual thumbnails inside the button — 5 circles in the actual current session colors, A-B-A-B vs. varied — that communicate before the reading brain engages. The thumbnails are unambiguously stronger. My pill descriptors are still a reading task.

**Pieces-considered payload.** C1's concept — surfacing unchosen items that were rendered in the customer's own colors — is genuinely novel and genuinely useful to Jeff. The customer saw the garland in Blush and Dusk Blue and still didn't add it. That's a softer sell, not a harder one. I have no equivalent. My ghost mechanic creates the multi-piece moment but doesn't capture the "considered but passed" signal that C1 named.
