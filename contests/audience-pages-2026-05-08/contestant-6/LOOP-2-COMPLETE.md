# Loop 2 Complete — Contestant 6 (Buyer-Scoped Authority)

## What the feedback said

**2-1 (Unsafe choice):** The memorial block's `desc` was event-appropriate but not grief-specific. The phrase "sets the tone for the room, gives people something to gather around" could appear on any event planning page. The proxy identified the test: a sentence that could only appear on a memorial page — one a birthday vendor would never say.

**2-2 (Civic recall test):** The "Since 1998" stat was sitting flat in the stats band alongside three others. The proxy named the specific claim it contains — institutional continuity that predates most coordinators' current tenures — and asked whether the page made anything of it.

## What was applied

### Private Celebrations — Memorial block (`private_celebrations.py`)

Rewrote the `desc` for Milestones & Memorials. The original opened with generic event-decor framing. The replacement leads with the grief-specific sentence the proxy identified as the test:

> "When families are doing something impossibly hard, having one thing feel right matters more than it usually does."

Then connects it to the decor: tasteful, considered, built around what mattered to the person — not the room. The `desc_extended` (Jeff's name + the review quote) was already the strongest proof in any memorial section across the contest; it was left intact.

### Civic & Community — Roster intro (`civic_community.html`)

Added one sentence before the "partial list" qualifier in `lt-civic-roster__sub`:

> "Locally Twisted has been at Utah public events since 1998 — before most of the coordinators reading this were in their current roles."

This activates the "Since 1998" number as an institutional-continuity claim rather than letting it sit as one of four inert stats. The sentence is addressed directly to the civic coordinator — it names the specific meaning of the number for her, in her professional context.

## What was held firm

- No structural changes. The four-prose-block format on Private Celebrations was already the correct hold from Round 2 CHOICE; Loop 2 didn't challenge it.
- No new CSS. No new global styles. No `!important`.
- Style guide v4.5 palette throughout — no light-blue, no blush, no pastel.
- The `desc_extended` blockquote in the memorial section (Jeff named, review quoted) was preserved exactly. It was the strongest humanizing move in the suite and the proxy confirmed it.

## Status

Applied. Both changes are copy-level precision edits, not structural revisions. The suite's grammar — hero → dark stats → photo → named proof → service → practical note → CTA — is intact across all four pages.
