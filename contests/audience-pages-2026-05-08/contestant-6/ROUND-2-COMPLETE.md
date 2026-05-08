# Round 2 Complete — Contestant 6 (Buyer-Scoped Authority)

## Path taken: A (Refine) with targeted B-lean on the memorial test

## What changed

**Private Celebrations page — three targeted changes to close the memorial test:**

1. **Hero lede rewritten.** Original listed occasion types. Revised lede names the full emotional range — including celebrations of life — and closes with "Whatever brought you here, you're in the right place." The grief buyer is claimed in the first paragraph, before they scroll through birthday and wedding content.

2. **KJSCOTT review placed into the Milestones & Memorials prose block.** Previously referenced in design notes only. Now rendered as a brass-ruled blockquote (`lt-private-moment__memorial-note`) inside the fourth occasion block — the structural position where the memorial buyer is looking. Not a generic testimonials band. The exact section that answers what they came to find.

3. **Memorial block extended to two paragraphs.** `desc_extended` adds a second paragraph that speaks to the grief buyer directly, contextualizes the KJSCOTT review in narrative form, and names Jeff — making it personal rather than institutional.

**CSS:** Blockquote style added under `.lt-page-private` scope — brass left border (3px), italic body, no `!important`, no new global styles.

**Other pages:** No changes. Civic, Corporate, Schools passed Round 1 proxy loops clean and hold their architecture.

## What's unchanged and why

The four-prose-block private architecture is unchanged. Collapsing to cards or panels would cost the structural differentiator that makes this page the most reading-depth private page in the field. The architecture was the right call in Round 1; Round 2 closes the three remaining gaps without disrupting it.

## Memorial test status after Round 2

- ✅ Grief buyer claimed early (hero lede, first sentence of the page)
- ✅ KJSCOTT's words in structural position (brass-ruled blockquote inside the memorial occasion block)
- ✅ Memorial container commensurate with its weight (full prose block + 3-photo cluster, same investment as birthday and wedding)
