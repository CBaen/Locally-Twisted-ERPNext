# 🎨 Customizable Event Decor Design Tool — Final Surface

**Status:** Contest complete. All 4 contestants ran end-to-end through Round 1 (blind) → reflective loops → Round 2 (mutual visibility) → reflective loops → mutual peer scoring → dissent (all chose Continue) → tightening pass → render gallery (this surface).

**This is NOT a winner-pick.** GL synthesizes downstream by selecting pieces from across the 4. The contestants themselves named who amplifies whom; that synthesis pipeline is laid out below before the field.

---

## 🎯 The synthesis pipeline (already mapped by the contestants themselves)

In R2 Loop 2, each contestant committed to ONE distinctive move + named which peer moves would AMPLIFY (not compete with) it. The named amplifications composed into a natural pipeline. **GL has the synthesis path pre-mapped before reading any individual entry.**

```
[Stage 1 — Style-gate entry, low cognitive load]
                  ↓  C4's visual SVG thumbnails inside style buttons
                  ↓  (parent decides with eyes before reading words)
                  
[Stage 2 — Multi-piece moment, composition grows]
                  ↓  C2's pre-tinted cascading ghost
                  ↓  (ghost arrives in customer's palette — invitation, not pressure)
                  
[Stage 3 — Render the payoff for two audiences at once]
                  ↓  C3's dual-audience design card
                  ↓  (customer's emotional moment + Jeff's supplier-call payload, one screen)
                  
[Stage 4 — Sales context flows downstream to Jeff]
                     C1's "pieces considered" payload
                     (suggestions customer was shown but didn't pick → CRM signal)
```

If GL synthesizes by picking the strongest move at each stage, **that's the design spec for the Design Studio**.

---

## 📋 At a glance — the 4 contestants

| | Concept | Mean Score | Crown jewel | Pipeline stage |
|---|---|---:|---|---|
| **C1** | The Color Stage | 32.67 | "Pieces considered" sales-context payload | Stage 4 |
| **C2** | The Coloring Book That Assembles Itself | 34.67 | Cascading ghost with pre-tinted color inheritance | Stage 2 |
| **C3** | The Coloring Page Frame | 34.67 | Dual-audience design card (customer + Jeff, one screen) | Stage 3 |
| **C4** | The Coloring Book | 34.33 | Visual SVG thumbnails inside style buttons | Stage 1 |

**Spread:** 2.0 points across 12 individual scores. The field is roughly equal in quality, with each contestant strong on different dimensions. No mediocre work — picking "the worst" would still produce a competent tool.

---

## 🖼️ Render gallery

All 4 contestants × 7 screens × 2 viewports = **56 screenshots** at `_render/contestant-{N}/{screen}-{viewport}.png`.

Screen states (all contestants):

| File | Screen | Purpose |
|---|---|---|
| `01-entry` | Entry / shape picker | First impression, style-gate |
| `02-color-one` | Coloring single piece | Core coloring interaction |
| `03-picker` | Color picker | The 53-named-color palette surface |
| `04-composition` | Multi-piece composition | Where the ghost / inheritance / suggestion lives |
| `05-done` | Done / inquiry handoff | The Jeff-side payload screen |
| `06-upsell` | Upsell / discovery | Add-another-piece moment |
| `index` | Mockup index page | Click-through to all 6 screens |

**Direct mockup access (double-click the index.html in any of these to interact):**
- `contestant-1/mockup/index.html` — The Color Stage
- `contestant-2/mockup/index.html` — The Coloring Book That Assembles Itself
- `contestant-3/mockup/index.html` — The Coloring Page Frame
- `contestant-4/mockup/index.html` — The Coloring Book

---

## 🎬 Per-contestant deep dive — in pipeline order

### Stage 1 → Contestant 4 — "The Coloring Book"

**Crown jewel:** Visual SVG thumbnails inside style buttons. Parent sees what each style produces before reading a single word. The propagation: every subsequent style choice in the tool gets the same visual-first treatment.

**What stands out (orchestrator):**
- Tightest scope discipline in the field. 2-region floor (per Frappe-recreatable physics + customer cognitive load argument).
- "Alternating / Mixed" plain-language renaming of construction styles named "the strongest customer-respecting move" by peers in the scoring round.
- Visual decision-making works at all literacy levels — accessible by design, not by retrofit.

**Distinctive moves to remember (for synthesis):**
- ⭐ **SVG thumbnails inside style cards** — the single move every other contestant said they'd borrow
- ⭐ **2-region floor** — physics-grounded, defensible, defaults to simple
- **Plain-language style names** ("Alternating" not "Swirl Pattern", "Mixed" not "Layered")
- **"View Design" 7th tile** in the entry grid — surfaces composition-in-progress without a separate nav

**What this contestant lacks (per their own self-assessment):**
- Discovery mechanic is the weakest of the four (text suggestion + generic ghost, no color inheritance)
- Done screen is informational rather than dual-audience
- Entry screen is functionally clear but least emotionally welcoming

**Peer scoring:** 35 (from C1), 34 (from C2), 34 (from C3) — mean 34.33

**Frappe-recreatable:** ✅ PASS — vanilla JS+jQuery+inline SVG, no build step, no React. All 6 screens render in a Frappe portal page.

**Renders to look at first:** `_render/contestant-4/01-entry-mobile.png` (crown jewel visible — SVG thumbnails inside cards)

---

### Stage 2 → Contestant 2 — "The Coloring Book That Assembles Itself"

**Crown jewel:** Cascading ghost with pre-tinted color inheritance. The composition grows by invitation: when the customer finishes coloring their first piece, a ghost outline of a complementary piece appears — already wearing the customer's chosen palette colors at low opacity. The customer either taps to add it or dismisses it. No pressure language. No "complete your design" obligation copy.

**What stands out (orchestrator):**
- Most production-ready Frappe-native implementation in the field. The only entry that wrote a full `frappe.call()` Lead-creation handler with loud-failure error path *proactively* (per the project's standing rule), without prompting.
- Self-hosts the inheritance mechanic: when ghost appears, it's already in the customer's palette — not a separate choice the customer has to opt into.
- "Permission to ignore" copy on every ghost — the ghost is invitation, not requirement.
- Cross-pollinated heavily during scoring round: absorbed C4's thumbnails, C3's per-region attribution, C1's "pieces considered" concept.

**Distinctive moves to remember (for synthesis):**
- ⭐ **Pre-tinted cascading ghost** — composition grows by invitation, in the customer's palette
- ⭐ **Production-ready `frappe.call()` Lead-creation** — the implementation depth that proves Frappe-native is feasible
- **"Permission to ignore" copy pattern** — every additive prompt has a "skip / not this time" affordance
- **Add-piece flow that doesn't break the ghost mechanic** — the ghost is the discovery; adding a piece keeps inheritance going

**What this contestant lacks (per their own self-assessment):**
- Done-screen format weaker than C3's portrait card
- Style selector vocabulary weaker than C4's thumbnails
- No equivalent to C1's "pieces-considered" payload concept

**Peer scoring:** 34 (from C1), 35 (from C3), 35 (from C4) — mean 34.67 (tied for top)

**Frappe-recreatable:** ✅ PASS — vanilla JS+jQuery+inline SVG, full Lead-creation code provided

**Renders to look at first:** `_render/contestant-2/04-composition-desktop.png` (crown jewel — ghost visible, pre-tinted)

---

### Stage 3 → Contestant 3 — "The Coloring Page Frame"

**Crown jewel:** Dual-audience design card framing. The completion screen serves the customer's emotional moment ("Look at what you made") AND Jeff's supplier-call payload (per-region color names, hex codes, design summary in plain language Jeff can read aloud while sourcing) on a single screen. One artifact, two audiences, no compromise.

**What stands out (orchestrator):**
- The completion-card framing was named the field standard for handoff quality. Two contestants borrowed elements during R2.
- CTA-flow refinement promoting "Send to Jeff" to primary action on the coloring screen — recognized by peers as the strongest customer-respecting move (lets exhausted parents finish in one piece without composing a multi-element design).
- After tightening pass: added an explicit "← What Jeff sees at 9 AM" annotation calling out the supplier-call data block. Crown jewel is now *legible* in screenshots, not just inferable from REASONING.
- Color picker uses LT-catalog named colors visibly (Empowermint, Blush, etc.) — closest to GL's "Color Name is the only requirement" directive.

**Distinctive moves to remember (for synthesis):**
- ⭐ **Dual-audience completion card** — single screen, two simultaneously-served readers
- ⭐ **Annotated mockups** — "← What Jeff sees at 9 AM" callout makes the principle visible to anyone evaluating the work
- **3-step orientation header** (Pick a shape → Color it → Share with Jeff) — clear progress cue
- **"Or call (801) 285-0860" fallback** under the Send button — non-internet-comfortable customer path
- **In-mockup design notes** explaining UX research sourcing (e.g., Baymard Institute on grouped vs flat color grids)

**What this contestant lacks (per their own self-assessment):**
- Implementation depth weaker than C2 (placeholder vs. C2's full Lead-creation)
- Upsell warmth weaker than C1 (grey silhouettes vs. C1's colored ghosts in customer palette)
- Entry screen tells parents what the tool DOES, not what to do FIRST (partially addressed in tightening)

**Peer scoring:** 37 (from C1), 34 (from C2), 33 (from C4) — mean 34.67 (tied for top)

**Frappe-recreatable:** ✅ PASS — vanilla JS+jQuery+inline SVG, no React

**Renders to look at first:** `_render/contestant-3/05-done-desktop.png` (crown jewel + the "What Jeff sees" annotation)

---

### Stage 4 → Contestant 1 — "The Color Stage"

**Crown jewel:** "Pieces considered" payload field. The customer's `Lead` record receives not only the design they completed, but the suggestions they were shown and didn't pick. Jeff's CRM call has expanded sales context: "I see you considered a garland with this arch — would you like me to quote that as an add-on?"

**What stands out (orchestrator):**
- Most distinctive on the SALES-OPS side. The other 3 are designing for the customer; C1 is also designing for Jeff's downstream funnel.
- Two-interaction-pattern split: backdrop uses tap-region UX (because backdrops have spatial regions), arches/columns/garlands use style-then-color slots (because they have repeating units). The split is ergonomically correct — different shapes warrant different interaction modes.
- After tightening: rewrote `02-color-one.html` to resolve mockup-vs-REASONING misalignment. Added per-region attribution on `05-done.html`. Crown jewel is now visible in `05-done.html` ("Also considered — not added" row).

**Distinctive moves to remember (for synthesis):**
- ⭐ **"Pieces considered" payload** — show-but-not-picked suggestions flow to Jeff's CRM as sales context
- ⭐ **Per-region attribution** on the completion screen (Column · Main: Dusk Lilac · Accent: Blush)
- **Two-pattern interaction split** — tap-region for backdrops, style-then-color-slots for arches/columns
- **Color-inheritance mechanism** — color choices carry forward to suggested next pieces (the upstream of the "pieces considered" payload)

**What this contestant lacks (per their own self-assessment):**
- Done screen weaker than C3's portrait card (no Jeff-side framing originally; partially addressed in tightening)
- Color picker doesn't show all-swatch names visibly (only the selected swatch shows name+hex; relies on hover/long-press) — partial divergence from GL's "Color Name is the only requirement" directive
- Distinctive lives in the CRM payload, not in the customer-facing UI — least visible to a render-gallery viewer (partially addressed in tightening)

**Peer scoring:** 32 (from C2), 33 (from C3), 33 (from C4) — mean 32.67

**Frappe-recreatable:** ✅ PASS — vanilla JS+jQuery+inline SVG. The "pieces considered" payload is a single hidden field on the inquiry form that ships to the Frappe `Lead` record.

**Renders to look at first:** `_render/contestant-1/05-done-desktop.png` (crown jewel — "Also considered — not added" row visible)

---

## 📊 Peer scoring matrix

| | from C1 | from C2 | from C3 | from C4 | **Mean** |
|---|---:|---:|---:|---:|---:|
| **C1** | — | 32 | 33 | 33 | **32.67** |
| **C2** | 34 | — | 35 | 35 | **34.67** |
| **C3** | 37 | 34 | — | 33 | **34.67** |
| **C4** | 35 | 34 | 34 | — | **34.33** |

**Per-dimension consensus winners (peer-scoring round):**
- **Experience quality:** C2 (cascading ghost) + C3 (coloring-page frame) named co-strongest
- **Scope discipline:** C4 (2-region floor, plain-language renaming)
- **Frappe-native fit:** C2 (only contestant with full `frappe.call()` Lead-creation + loud-failure error path)
- **Customer clarity:** C4 (visual SVG thumbnails + plain-language renaming)

**Strongest single peer move named in the round:** C3's "Send to Jeff" promoted to primary CTA on the coloring screen (gives exhausted parents a one-piece exit). Multiple peers cited this as the most customer-respecting move in any contestant's work.

---

## 🎯 Orchestrator's rating with reasons

Per GL's contest configuration: ratings + reasons, **NOT a winner-pick.** This is sorting input for synthesis, not adjudication.

| Dimension (1-10) | C1 | C2 | C3 | C4 |
|---|---:|---:|---:|---:|
| **Customer "I made this" feeling** | 7 | 9 | 9 | 8 |
| **Scope discipline / minimum viable** | 7 | 8 | 8 | 9 |
| **Frappe-native implementation depth** | 8 | 9 | 7 | 8 |
| **Customer clarity for non-designer parents** | 7 | 8 | 8 | 9 |

**Why these:**
- **C1 — 29/40.** Crown jewel is the most distinctive on the sales-ops dimension but invisible from the customer's seat; the customer-facing experience scores middle-of-field. Two-pattern interaction split is correct but adds load. Color-name visibility partially diverges from GL's directive.
- **C2 — 34/40.** Highest implementation depth; ghost mechanic is the field's strongest customer-side move. Loses points only on style-selection vocabulary (text labels where C4 has SVG thumbnails).
- **C3 — 32/40.** Highest dual-audience score; tightening-pass annotation made the crown jewel legible. Loses points on implementation depth (placeholder Lead-creation vs. C2's full code).
- **C4 — 34/40.** Highest scope discipline + customer clarity; thumbnail-inside-button move is the field's most-borrowable refinement. Loses points on discovery mechanic (text suggestion vs. C2's pre-tinted cascade).

**Tightest spread is on customer "I made this" feeling.** That's not weakness — that's "every contestant solved the customer-facing problem." The field's actual differentiation is on the surrounding dimensions (Jeff-side payload, scope, implementation, clarity).

---

## 🧩 Distinctive moves to remember — synthesis cheat sheet

If GL synthesizes by picking pieces, these are the moves worth picking:

| Move | Owner | Why pick it |
|---|---|---|
| Visual SVG thumbnails inside style buttons | C4 | Style choice without vocabulary gating |
| Plain-language style names (Alternating / Mixed) | C4 | Customer-side translation of construction terminology |
| 2-region floor on multi-color shapes | C4 | Defensible scope minimum, physics-grounded |
| Pre-tinted cascading ghost | C2 | Composition grows by invitation, palette-aware |
| "Permission to ignore" copy pattern | C2 | Removes obligation language across additive prompts |
| Production-ready `frappe.call()` Lead-creation | C2 | Proves Frappe-native is shippable; loud-failure compliant |
| Dual-audience completion card | C3 | One screen, two readers, no compromise |
| "Send to Jeff" as primary CTA on coloring screen | C3 | Exhausted-parent one-piece exit |
| "← What Jeff sees" annotation pattern | C3 | Makes Jeff-side framing legible to evaluators |
| LT-catalog named colors visibly displayed | C3 | Closest to GL's "Color Name is the only requirement" |
| "Or call (801) 285-0860" fallback under Send button | C3 | Non-internet-comfortable customer path |
| In-mockup design-note annotations citing research | C3 | Pattern for future contestant work |
| "Pieces considered" payload on Lead record | C1 | Sales context for Jeff's CRM call |
| Per-region attribution on completion screen | C1 | (Also C3) — supplier-call clarity |
| Two-pattern interaction split (tap-region vs. style-then-color) | C1 | Different shapes, different interaction modes |
| Color inheritance carrying forward to suggestions | C1 | Upstream of the pieces-considered payload |

---

## ⚠️ Gaps in the field — what NO contestant did

Worth flagging before synthesis. None of the 4 produced these; if GL wants them in the eventual Design Studio, they need to be designed in.

| Gap | Why it matters |
|---|---|
| **Backdrop sizing input UI** | Backdrops are sqft-priced and "any size" per LT catalog. None of the 4 has a length × height input + computed cluster grid. C1 has tap-region UX but no sizing input. |
| **Save-as-draft / share-with-partner flow** | Multi-stakeholder weddings + corporate events likely need it; nobody built it. Future iteration. |
| **Mobile-only photo upload of inspiration** | LT's existing Lead schema has the field; no contestant wired the Design Studio to it. Could be added at the inquiry form on screen 05. |
| **Indoor-vs-outdoor venue toggle** | Affects which decor types LT recommends (helium drops indoors only, etc.). Could be added as a preliminary step before shape picker. |
| **Cluster-count math display** | The 4-balloon cluster atomic unit is the construction physics the contest grounded itself in, but the customer never sees a cluster count. None of the 4 surfaced this — likely correct for customer-side, but worth confirming GL doesn't want it shown. |
| **Color-from-inspiration-photo extraction** | The Lead schema has the inspiration photos field. No contestant built a "pull palette from this photo" UX. Future iteration. |

---

## ✅ What's signed off

- All 4 contestants chose **Continue** at the dissent moment with thoughtful reasoning. None withdrew. None pivoted.
- All 4 declared **Frappe-recreatable PASS** in Round 1 and held the line through tightening (no React, no build step, vanilla JS+jQuery+inline SVG only).
- All 4 produced research-grounded work with cited URLs (proxy probes in R1 Loop 1 surfaced two extrapolated claims; both contestants honestly removed them).
- All 4 wrote `TIGHTEN-COMPLETE.md` files confirming the proxy's tightening notes were applied.
- The synthesis pipeline above was named *by the contestants themselves* in R2 Loop 2, not by the orchestrator. The pipeline composes naturally from their own crown jewels.

---

## 📂 Where to find everything

| Artifact | Path |
|---|---|
| **This document** | `research/contest-customizable-event-decor-tool/FINAL-SURFACE.md` |
| **Render gallery (56 PNGs)** | `research/contest-customizable-event-decor-tool/_render/contestant-{1,2,3,4}/` |
| **Interactive mockups** (double-click index.html) | `research/contest-customizable-event-decor-tool/contestant-{1,2,3,4}/mockup/index.html` |
| Brief (source of truth contestants read) | `research/contest-customizable-event-decor-tool/BRIEF.md` |
| Product details (catalog + physics + your directives) | `research/contest-customizable-event-decor-tool/PRODUCT-DETAILS.md` |
| Round 1 cheat sheet (orchestrator's field summary) | `research/contest-customizable-event-decor-tool/FIELD-AT-ROUND-1.md` |
| Mutual peer scoring + crown jewels + pipeline | `research/contest-customizable-event-decor-tool/SCORING-RESULTS.md` |
| Dissent results (all 4 chose Continue) | `research/contest-customizable-event-decor-tool/DISSENT-RESULTS.md` |
| Proxy tightening notes per contestant | `research/contest-customizable-event-decor-tool/PROXY-REVIEW-ROUND-2.md` |
| Per-contestant work | `research/contest-customizable-event-decor-tool/contestant-{N}/` (RESEARCH-NOTES, REASONING, mockup/, ROUND-1/2-COMPLETE, PROXY-LOOP-* notes + replies, scoring.md, DISSENT-CHOICE.md, TIGHTEN-COMPLETE.md) |

---

## 🧭 Suggested reading order for synthesis

1. **This file** (you're here)
2. **`SCORING-RESULTS.md`** — the contestants' own crown-jewel pipeline mapping (Section 5)
3. **The 4 mockup index.html files** — click through interactively, one at a time
4. The render gallery in `_render/` — for side-by-side comparison
5. Optional: the per-contestant `REASONING.md` files — for "why this design choice" depth on any move you want to borrow

When ready to commit to a synthesis, the orchestrator can dispatch a follow-up to capture the spec for the Design Studio implementation.

---

*Final surface compiled 2026-04-29 by the Opus 4.7 instance who took the baton for the render gallery + final surface. The contest skill ran end-to-end through 4 contestants, a persistent Proxy coach, 2 reflective loops per round, mutual peer scoring, dissent moment, tightening pass, and this surface. Total: ~25-35in tokens across all phases. The collaborative-mode framing produced cross-pollination as designed; the "no winner picked" framing left the synthesis to where it belongs — with GL.*
