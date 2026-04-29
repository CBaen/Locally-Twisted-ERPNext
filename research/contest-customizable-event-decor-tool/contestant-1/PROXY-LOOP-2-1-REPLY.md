# Proxy Loop 2-1 Reply — Contestant 1

Three probes. All three land. Responses and actions below.

---

## Probe 1: Entry screen doesn't help the undecided parent

**Probe:** The exhausted parent taps "Balloon Arch" because it's first and recognizable — not because they actually wanted it. Nothing on the screen orients toward common use cases. If they pick wrong and get four steps in, they close the tab.

**Assessment: Lands fully.**

The intro copy ("Pick a piece. Choose your colors. See what your celebration looks like before we talk") tells the parent what the tool does but not where to start. A 40%-brain parent at midnight needs one sentence of permission to pick the obvious thing, plus reassurance they're not locked in.

The fix is not a recommendation engine — that's over-engineering a problem a single line of copy solves. I added a soft orientation line directly above the shape grid:

> "Most people start with an arch. Not sure? Pick anything — you can always add more pieces."

This does two things:
1. Gives the undecided parent a nudge without forcing a decision ("most people start with an arch" is social proof, not a gate)
2. Removes the fear of picking wrong ("you can always add more pieces") — the fear of irreversibility is a tab-close trigger at midnight

What I chose not to do: add a "Most popular for birthdays" badge on the Arch card. That's a meaningful UI addition that implies a recommendation system and creates visual noise. The copy line is lighter and just as effective.

**File changed:** `01-entry.html` — added one orientation paragraph above the shape grid.

---

## Probe 2: Duplicate Balloon Drop cards

**Probe:** Two Balloon Drop cards appear in the entry list with different color palettes.

**Assessment: Lands fully. This is a real bug I introduced.**

When I added the Balloon Drop card in Round 2 to replace Centerpiece, I didn't notice the original gallery already had a Balloon Drop (the Round 1 version in pink/FFD1DC palette, with hint "Single palette"). I added a second one in the Reflex Gold palette with hint "250 / 500 / 1000".

Removing the original (Round 1 pink version). Keeping the Round 2 version — it uses LT catalog approximation colors and the more accurate "250 / 500 / 1000" hint that reflects the real product's size tiers.

**File changed:** `01-entry.html` — removed duplicate original Balloon Drop card.

---

## Probe 3: Quick-row swatches are unlabeled

**Probe:** The horizontal swatch row below "Color for: Main balloons" has no context label. The parent can't tell if these are recent picks, featured colors, or random.

**Assessment: Lands fully.**

The parent is seeing a horizontal strip of colored circles with no explanation. The `color-picker-panel__label` ("Color for: Main balloons") explains which region is active — it doesn't explain what the swatches are. There's a gap between "I know I'm coloring the main balloons" and "I know what these circles are."

The fix is the smallest possible signal: a "Popular colors" eyebrow label above the swatch row in the same style as other secondary labels in the UI (11px uppercase, letter-spaced, #BBBBBB). One line of markup, no new CSS class needed.

This also pays off the color name mechanic: once the parent understands "these are popular balloon colors," the tooltip/title behavior (which shows the full name on hover/long-press) has context. They're not random colors — they're the colors most customers choose.

**File changed:** `02-color-one.html` — added "Popular colors" label above `swatch-quick-row`.

---

## What was not changed

**The entry screen shape count.** After removing the duplicate Drop, the grid has 6 cards (Arch, Column, Garland, Backdrop, Bouquet, Drop). Six is fine for a 375px grid — it renders as 3 rows of 2 on mobile, which is a clean scroll. No reordering needed: Arch first is the right call, confirmed by the probe ("Balloon Arch" first and most recognizable is the correct default position, not a problem to fix).

**The two-region coloring model.** The probe confirmed: "the two-region model (Main / Accent) is clean and fast. At midnight, fast is the right call." No change.

**The bottom sheet palette.** "The bottom sheet feels like a native phone UI — I don't have to learn anything new." No change.

**Color inheritance / upsell mechanic.** Not reached in the exhausted-parent walk-through — the probe covers the entry → first coloring flow only. The mechanic is intact.

---

## Summary of Round 2 + Loop 2-1 changes

After this loop, the tool is tighter on customer arrival:

| Gap | Fix |
|---|---|
| Undecided parent picks wrong shape and tab-closes | Soft copy nudge: "Most people start with an arch. Not sure? Pick anything." |
| Duplicate Balloon Drop cards | Removed original; kept Round 2 version with correct hint |
| Swatch row context unknown | "Popular colors" label above Quick Row |
| Color catalog wrong (Round 2) | Replaced with actual 53 LT named colors |
| Centerpiece in scope (Round 2) | Removed from gallery and upsell |
| Hex as primary in payload (Round 2) | Names-first format; hex as visual aid only |
| Physics mismatch for Arch/Column/Garland (Round 2) | REASONING updated; Backdrop used as demo shape |
