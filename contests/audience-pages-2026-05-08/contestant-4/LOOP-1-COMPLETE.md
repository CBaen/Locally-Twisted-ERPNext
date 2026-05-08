# Loop 1 Complete — Contestant 4: "One System, Four Buyers"

## What the proxies said

**Proxy-1:** The schools chip container is wrong at five items. Chips signal breadth; five named relationships need room to be substantial. Referenced the editorial ledger with brass rule separators as a better container for depth over scan.

**Proxy-2:** Corporate has no room-specific furniture — it shares the same structure as civic with different chip names. The test: which section could not be transplanted to another page without feeling wrong? Private has testimonials. Schools has moment cards. Corporate had nothing.

---

## What I applied

### Schools — chip list → editorial ledger

The proxy was right. Five chips (three of which carry all the named-school weight) minimizes what should be maximized. Rebuilt the roster section as a ledger: each named school relationship occupies a full row with a brass rule separator, the institution name in heading type, and a context label (event type) set in uppercase gold. Each row reads as a deep relationship, not an item in a scan list.

Data shape updated in the controller to `{"name": ..., "context": ...}` per row.

### Corporate — added brand-color matching section

Identified what only a corporate buyer needs: a brand kit. Schools don't bring Pantone numbers. Civic organizations don't have franchise color standards. Private clients don't care if the arch matches a logo. Only the marketing director evaluating LT for a grand opening or broadcaster activation is thinking "will this match our exact brand colors?"

Added a `color-strip` section between the proof bar and case cards. Dark background (ink), two-column at desktop: copy on the left ("Your brand colors. Precisely." + a direct statement about matching KSL navy, Zions red, Chick-fil-A's specific shade), color swatches on the right showing five real client brand colors by name + "+25". The swatches are visual proof — not a decorative element but a demonstration of the matching capability.

This section cannot be transplanted to civic, schools, or private without feeling wrong. That's the test. It passes.

---

## What I held firm on

**The shared skeleton.** Proxy-2 acknowledged that the "same furniture" observation isn't a failure — it's the "One System" promise. A marketing director who cross-reads corporate and schools should recognize the brand. I'm not introducing structural divergence for its own sake. The divergence is in the furniture that only fits one room.

**Schools moment cards vs. civic/corporate case study cards.** The proxy didn't distinguish these, but they are different containers: moment cards (4:3 ratio, "Back to School / Graduation / Spirit" tag taxonomy, client attribution as a line item) vs. case study narrative cards (16:9 ratio, industry-cluster client groupings, longer body copy explaining the business challenge). The schools page already had room-specific furniture in the card format and content strategy — the proxy missed it because the visual format (card grid) reads similar at a distance. I left this intact.

**Sandstone on private only.** The Proxy-1 affirmed this as correct palette discipline. No change.

---

## Four-room audit after loop

| Page | Room-specific furniture |
|---|---|
| `/civic-community` | Authority band headline — "Trusted by Utah cities, chambers, and community organizations" — positions LT in the public-event trust frame; civic buyers care about public accountability in a way no other buyer does. |
| `/corporate-events` | Brand-color matching strip — exists only because corporate buyers bring brand kits. |
| `/schools-campuses` | Editorial ledger roster (named institution + event type context per row) + moment card taxonomy (Back to School / Graduation / Spirit). |
| `/private-celebrations` | Testimonials section — peer trust replaces client logo lists; the memorial balloon review is placed deliberately. |

All four rooms now have furniture that could not be moved to another room without feeling wrong.
