# Loop 2 Complete — Contestant 5

## What changed

### Schools page — occasions grid specificity upgrade

The proxy noted that the occasions grid read like a capability list while the story block ("7am install window") held the real specificity. The fix was to rewrite all six card bodies to carry the same operational texture as the story block:

- **Graduation:** setup timeline framed around ceremony prep windows, not "before guests arrive"
- **Back-to-School:** the 7am window named directly in the card, not only in the story block
- **Homecoming:** the pep rally window constraint named explicitly ("between the lunch bell and the pep rally")
- **Prom:** student leadership approval flow named — the actual mechanism that prevents color surprises
- **PTA/Carnivals:** "kid-tested for durability" carried from copy into operational framing (families arrive ready)
- **Athletic Milestones:** shorter lead time reality acknowledged — the card earns trust from activity directors who know how milestone events actually come together

The H2 ("School colors aren't suggestions") is unchanged — it earned its place.

### Civic page — voice upgrade on the story block

The proxy identified that the civic page had structural proof density (5-category client groupings) but still explained the accountability stakes rather than embodying them. The fix:

- **H2 changed:** "Public events have a different pressure." → "When the city photographs it, the coordinator owns the result." The new H2 names who is on the line — not LT, the coordinator who hired LT. That's the actual anxiety a city event coordinator carries into a vendor decision.
- **Opening paragraph rewritten:** shifted from explaining why civic events are photographed to naming the attribution reality — "the person who hired the vendor is the one answering for it." One sentence the coordinator will read once and remember two weeks later.
- Remaining paragraphs retain the proof specificity (8 municipalities, Pride, chambers) and the delivery/install/teardown standard.

## What held

- Hero contract honored on all four pages (220/250/280px)
- No `!important`, no new global CSS, no off-guide fonts, no light-blue/blush/pastel
- Private celebrations structural overhaul from Round 2 is unchanged — opening act section with KJSCOTT pull-quote, dual memorial address, hero lede reaching both buyers
- Corporate AP/billing section isolation unchanged — still the only contestant with a named procurement section
- Civic client grid with 5-category groupings unchanged — proof density still the highest in the field for this page

## Technical compliance

- ✓ Hero contract: 220/250/280px across all four pages
- ✓ No `!important` anywhere
- ✓ No new global CSS — page-scoped `<style>` blocks with unique root classes
- ✓ No adjacent full-width colored sections
- ✓ All clients from approved roster only
- ✓ All photos reference real file paths
- ✓ Cormorant Garamond headings, Lato body/UI throughout
- ✓ No light-blue, blush, pastel, or off-guide colors
- ✓ Controllers: `no_cache = 1`, `sitemap = 1`, `get_context(context)` pattern
