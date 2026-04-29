# Scoring Results — Customizable Event Decor Design Tool Contest

**Status:** Mutual peer scoring complete. All 4 contestants scored each other on the 4 dimensions from BRIEF.md Section 8 (Experience quality / Scope discipline / Frappe-native fit / Customer clarity), 1-10 each.

**Format note:** GL synthesizes downstream by picking pieces from across all 4. Scores are sorting input, NOT a winner-pick. The collaborative-mode framing means scores cluster tightly — that's a feature, not a bug. The 2.0-point spread across 12 individual scores reflects "everyone strong on different dimensions" rather than any contestant being weak overall.

---

## 1. Full scoring matrix

| | Score from C1 | Score from C2 | Score from C3 | Score from C4 | **Mean** |
|---|---:|---:|---:|---:|---:|
| **C1** "The Color Stage" | — | 32 | 33 | 33 | **32.67** |
| **C2** "The Coloring Book That Assembles Itself" | 34 | — | 35 | 35 | **34.67** |
| **C3** "The Coloring Page Frame" | 37 | 34 | — | 33 | **34.67** |
| **C4** "The Coloring Book" | 35 | 34 | 34 | — | **34.33** |

**C2 and C3 tied at the top**, C4 close behind, C1 third. Full spread: 2.0 points.

## 2. Per-dimension highlights

### Experience quality ("does customer come away feeling 'I made this'?")
- **Strongest collective feedback:** C2's cascading ghost, C3's coloring-page frame
- **Notable:** all 4 deliver the "I made this" feeling per peer scoring; differences are in HOW

### Scope discipline (minimum viable, not maximalist?)
- **Field consensus winner:** C4 (multiple peers named "tightest scope discipline")
- **Notable:** every contestant scoped tightly; C4's 2-region default is the floor

### Frappe-native fit (recreatable, no forbidden primitives?)
- **Field consensus winner:** C2 (only entry with full `frappe.call()` Lead-creation code + loud-failure error path implemented proactively per project standing rule)
- **Notable:** all 4 PASS Frappe-native; C2 is most production-ready

### Customer clarity (non-designer arriving cold understands tool in <30s?)
- **Field consensus winner:** C4 (visual SVG thumbnails inside style buttons + Alternating/Mixed plain-language renaming)
- **Notable:** C3's CTA-flow refinement (Send-to-Jeff promoted to primary on coloring screen for one-piece exhausted parents) was named the strongest customer-respecting move in any loop

## 3. Self-reflection — where each contestant named their own weakness

### C1
- Done screen demonstrably weaker than C3's (no per-region attribution, no phone fallback, no two-path architecture)
- "Pieces considered" crown jewel lives in REASONING only, not in a mockup screen — most distinctive synthesis ingredient is invisible to render-gallery viewer
- 02-color-one.html still shows tap-region UX while REASONING says style-then-color-slots — **mockup and reasoning are misaligned** (real bug for tightening to fix)

### C2
- Done screen format weaker than C3's portrait card
- Style selector vocabulary weaker than C4's thumbnails
- No equivalent to C1's pieces-considered payload concept

### C3
- Implementation depth weaker than C2 (placeholder vs. C2's full Lead-creation code)
- Upsell warmth weaker than C1 (grey silhouettes vs. colored ghosts showing customer's own palette extended)
- Entry screen tells parents what the tool DOES, not what to do FIRST

### C4
- Discovery mechanic weakest of the four (text suggestion, generic ghost, no color inheritance)
- Done screen informational rather than dual-audience
- Entry screen least emotionally welcoming
- Self-named: contributions are "refinements, not structural advantages"

**Pattern:** every contestant could name a peer's specific strength they lacked. The field's self-awareness is high.

## 4. Crown jewels (R2 Loop 2 — synthesis-signal probe)

Each contestant committed to ONE distinctive move they would defend as essential to the synthesis:

| Contestant | Crown jewel | What it does | What amplifies it (named by contestant) |
|---|---|---|---|
| **C1** | **"Pieces considered" payload** | Carries upsell suggestions the customer was shown but didn't pick → flows to Jeff as sales context | Color inheritance is the mechanism that produces the visible suggestion |
| **C2** | **Cascading ghost with pre-tinted inheritance** | Composition grows by invitation; ghosts arrive in customer's palette | C3's dual-audience completion card ("turns the moment into a finished, sendable thing") |
| **C3** | **Dual-audience design card framing** | Customer's emotional moment + Jeff's supplier-call payload on one screen, simultaneously | C2's ghost mechanic (fills the card with richer data through less customer effort) |
| **C4** | **Visual thumbnails inside style buttons** | Parent decides with eyes before reading a word; propagates to every style choice in the final tool | C2's ghost (earns the second piece after first choice) + C3's done-screen (lands the payoff before attention expires) |

## 5. The synthesis pipeline that emerged

The crown jewels compose into a natural pipeline. **The contestants themselves named who amplifies whom, and the named amplifications line up:**

```
[Style-gate entry — low cognitive load]    (C4's visual thumbnails)
                  ↓
[Multi-piece moment — composition grows]    (C2's pre-tinted cascading ghost)
                  ↓
[Render the payoff — customer + Jeff]    (C3's dual-audience design card)
                  ↓
[Signal flowing to Jeff — sales context]    (C1's pieces-considered payload)
```

This is not the orchestrator's synthesis — this is what the contestants surfaced as their own picture of how their crown jewels fit together. **GL has the synthesis path pre-mapped before they see the renders.**

## 6. Observations

### What stands out about the field

1. **No mediocre work.** The 2.0-point spread + 32-37 individual range means every entry is strong. Picking "the worst" would still produce a competent design tool.

2. **Cross-pollination on the record.** C2 absorbed C1's color-inheritance into their ghost mechanic + credited C3 for handoff leadership. C1 borrowed C4's "they pair beautifully" copy. C3 referenced C4's reframing logic. Every contestant credited at least one peer.

3. **Self-honesty was high.** Every contestant named at least one specific weakness in their work relative to the field. C1 surfaced their own mockup-vs-reasoning misalignment unprompted.

4. **The crown-jewel pipeline is composable.** GL's synthesis isn't picking 4 independent things — it's stitching together 4 stages of one experience. The contestants designed orthogonally enough that the pieces don't conflict.

### What the tightening pass should address

- **C1**: bring "pieces considered" into a mockup screen (currently invisible to render-gallery viewer); resolve mockup-vs-reasoning misalignment in 02-color-one.html
- **C2**: minor — design selector text could borrow C4's visual thumbnails; done-screen could borrow elements from C3's portrait card
- **C3**: minor — entry screen could add "what to do first" orientation
- **C4**: minor — empty-state recently-used row reads as loading failure; entry could add emotional welcome

The tightening pass is an orchestrator-coached polish, not a redesign. Each contestant gets a specific "tighten this, keep this" note from the Proxy, applies it, marks complete.

## 7. Next phases

1. **Dissent moment** — each contestant chooses Continue / Step Away / Wildcard Pivot. Default is Continue; the option to step away or pivot exists for honoring agency.
2. **Tightening pass for ALL 4** — Proxy writes per-contestant "tighten this, keep this" notes; contestants apply.
3. **Render gallery via Playwright** — screenshots of all 4 contestants × 6 screen states × mobile (375px) + desktop (1280px). Plus direct double-click access to each `mockup/index.html`.
4. **Surface to GL** — `FINAL-SURFACE.md` with all 4 contestants side-by-side: render gallery + scoring summary + Proxy notes + crown jewels + the pipeline above + Frappe-recreatable verdict + orchestrator rating-with-reasons.

GL synthesizes from there.

---

*Scoring aggregated by orchestrator 2026-04-29 after all 4 contestants completed `scoring.md`. Replaces no prior file. Input to dissent moment + tightening pass + final surface to GL.*
