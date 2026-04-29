# Proxy Loop 2-1 Reply — Contestant 2

---

## Assessment: Both probes land. Changes made.

---

## Probe 1: "Swirl" doesn't self-explain at midnight

**Lands.** The Proxy is right. "Swirl" is an insider word. A tired parent taps it and hopes — that is not a confident choice, it's a guess. The word means something to Jeff and to balloon decorators. It doesn't mean the same thing to a 35-year-old phone-in-bed.

The fix does not remove the Design selector. Swirl/Layered/Organic is a real product distinction that governs color count and construction — it needs to be there. What it needed was a descriptor underneath each pill that shows what the word means without requiring the customer to already know.

**Change made to `02-color-one.html`:**
- Label changed from "Design" to "Look" — slightly warmer, slightly less technical
- Each pill now shows a two-line label: the name + a short descriptor in smaller text
  - Swirl → "spiral pattern"
  - Layered → "color bands"
  - Organic → "mixed & flowing"
- CSS added for `.design-pill__desc` — smaller, lower opacity, block display under the label
- Pills sized to accommodate two lines

The customer at midnight now sees three options with enough visual context to know which one they're imagining. They don't need to know balloon construction physics — "spiral pattern" is enough.

**What I did not do:** I did not add preview thumbnails of each Design style inside the pills. That would be the next level of clarity (a tiny arch silhouette showing the spiral vs banded vs organic arrangement). That is a tightening-pass enhancement, not a fix that belongs here. The descriptor line is the minimum effective change.

---

## Probe 2: The pre-dressed ghost feels like obligation, not invitation

**Lands precisely.** The Proxy named the mechanism exactly: "already dressed in my colors" makes it feel expected. That is the sharpest possible version of the problem. The ghost inheriting the palette is the B-lean feature — it's doing real work. But "already dressed" without a clear "you can say no" signal reads as the tool having assumed the customer's answer.

The difference between invitation and obligation at midnight is, as the Proxy said, one word. "Optional" is that word.

**Changes made:**

**`04-composition.html`:**
- Ghost label: "Garland in your colors?" → "Add garland? / *totally optional*" — the italic secondary line at lower opacity makes explicit that no is a fine answer
- Scene label: "Your event — tap a piece to edit it" → "Your design is ready — tap to edit, or send it as-is" — this tells the customer they are already done before they even see the ghost. The ghost now appears in a context where completion has already been named. The ghost is bonus, not requirement.

**`06-upsell.html`:**
- Ghost tap label: "+ Add column" → "+ Add one? *optional*" — same pattern, smaller secondary text
- Panel header title: "Complete the look" → "Want to add more? totally optional" — "Complete the look" implies incompleteness. That is exactly the pressure the Proxy flagged. "Want to add more?" is a genuine question with a genuine no available.
- Skip button: "Skip" → "No thanks, I'm done" — "Skip" implies something is being avoided. "I'm done" is the customer's own voice, claiming completion. It names done as a good outcome, not a departure from the expected path.

---

## What was not changed

**The ghost mechanic itself.** The Proxy's verdict: "Strongest midnight-entry experience in the field." The pre-tinted ghost is doing its job. The problem was not the ghost — it was the absence of permission to not tap it. All changes are copy and framing. The SVG pre-tinting, the Design-style inheritance, the cascade timing — untouched.

**The bottom sheet picker.** The Proxy called it "clean and genuinely good." No changes.

**The entry screen.** "What are you dreaming of?" + "Most loved" badge — the Proxy described these as doing real work. No changes.

---

## One thing the Proxy named that I want to hold for the tightening pass

The Proxy said "Strongest midnight-entry experience in the field" — this is after reading the field summary, which means the entry screen is a genuine competitive advantage. That headline and the permission-slip badge are load-bearing. If a tightening pass touches the entry screen, those two elements should be the last things to change.

---

*Proxy loop 2-1 complete. Ready for mutual peer scoring.*
