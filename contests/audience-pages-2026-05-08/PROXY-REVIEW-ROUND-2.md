# Proxy Review — Tightening Pass (Round 2)
**Contest:** audience-pages-2026-05-08
**Date:** 2026-05-08
**Top 4 advancing:** C7, C1, C2, C5

This is a tightening pass — not a redesign. Each note below names a specific polish move. Nothing here touches what's already working.

---

## C7 — The Proof is in the Place (26.71 — Field Leader)

You are the clear leader. The suite earned it. What follows is the edge between strong and outstanding.

### Tighten This

**1. Civic hero lede has a subordinate clause that softens it.**
In `civic-community/COPY.md`, the hero lede reads: "Parade routes, city plazas, Pride celebrations, chamber events, and community gatherings — Locally Twisted has been delivering civic-scale balloon installations across Utah for over two decades."

The list construction is strong. But "has been delivering" is a continuous-past verb form that feels effortful — as if the company is still mid-delivery of its own claim. The voice elsewhere is present-tense and declarative. Tighten to match: "Parade routes, city plazas, Pride celebrations, chamber events, and community gatherings. Twenty-plus years of civic-scale balloon work across Utah." Two sentences. No subordinate clause. The pause after the list hits harder than a dash.

**2. Section 3 civic subheading is generic.**
In `civic-community/COPY.md`, Section 3 opens: "Organizations that have trusted Locally Twisted with public-facing events across the Wasatch Front." That sentence is doing no work the heading "Named civic & community relationships" doesn't already do. It sounds like a database record, not editorial. Cut it, or replace it with a single sentence that names the scope differently — something like "From city halls to Pride parades, every organization here had their event in public." That's still informational but it earns the list that follows.

**3. Corporate intro repeats the client names from Section 3 too soon.**
In `corporate-events/COPY.md`, the Section 2 intro body reads: "From Zions Bank community days to KSL broadcast events..." — then Section 3 is the full sector grid, which also contains Zions Bank and KSL. Seeing the same names in prose and then immediately in a structured grid within one scroll window dilutes both. Consider changing the Section 2 intro reference to name a different proof anchor not already headlined in the sector grid, or redirect that sentence to describe what "brand-safe" means behaviorally before the names appear.

**4. Private page has two sequential section numberings both labeled "Section 5."**
In `private-celebrations/COPY.md`, "Section 5 — Install proof" and "Section 5 — Testimonials" share the same label. This is a COPY.md annotation issue, not a rendered page issue — but it will confuse the build instance that reads this file to implement the page. Renumber so the testimonials section is clearly Section 6, and shift the capability bar and service note down accordingly. The implementation phase will thank you.

**5. Schools service note contains an instruction that assumes AP-knowledge from the buyer.**
In `schools-campuses/COPY.md`, the Section 7 body reads: "Quote requests should include the event type, date, venue setup window, and your school's color values." The phrase "venue setup window" is clear to an activity director who has done this before — but a first-time event coordinator might not know what that means or how to express it. Consider a one-phrase clarification in parentheses: "(the time you have access to the space before students arrive)" — it adds eight words and removes a potential point of friction in the inquiry form.

### Don't Change

- **The civic H2: "When the city puts it on a banner, the balloons have to hold up."** This is the best single sentence in the contest. It earns a room before the body paragraph begins. Leave it alone.
- **The "Private by Default" capability pillar.** The only contestant who named privacy as a structural commitment rather than a demonstrated behavior. It makes the whole private suite feel different from the others.
- **The KJSCOTT deployment architecture.** Pull quote in the memorial section (structural proof), then again in testimonials (social proof). That is intentional double-deployment that does two different jobs. It should stay exactly as-is.
- **The civic roster four-column grouped grid.** Scanability for a city coordinator finding peer cities is materially better than a flat tag list. The groupings are logical and the brass-rule labels keep it readable.

### Stretch Goal

The corporate page names healthcare clients (IHC, Mountain Star Medical) and the loop added the latex-free capability note. That is a start. But the healthcare sector card in Section 3 currently reads: "Community health events, staff celebrations, and facility grand openings." A marketing director at a hospital reads that as generic — it describes what any balloon company claims. One sentence that names the institutional-environment constraint specifically — something like "Appropriate for clinical settings with infection-control protocols" — would differentiate the healthcare card from every other sector card on the page. You already know LT has the latex-free note. The stretch is deploying it in a way that speaks to the institutional buyer's actual concerns, not just the allergy-safe consumer concern.

---

## C1 — Audience Authority (26.00 — Three-Way Tie)

You built the strongest operational register in the field. The civic vendor-documentation cards are genuinely differentiated. The tightening work is in copy precision and one structural overlap.

### Tighten This

**1. The civic hero H1 is the weakest headline in the suite.**
`civic-community/COPY.md` hero: "Utah's civic and community events, visually led." The phrase "visually led" is not quiet confidence — it is marketing phrasing that describes what LT does to the events rather than what LT delivers for them. Compare it to the corporate H1 ("Brand-safe balloon decor for Utah corporate events") and the schools H1 ("School spirit, graduation, and campus events — designed for the moment"), both of which speak to the buyer's situation. The civic H1 describes LT's positioning. Reframe toward the buyer: a civic event coordinator doesn't want events "visually led" — she wants decor that holds up in press coverage and represents her organization. Something like "Utah civic events, built to photograph." is closer to the actual buyer need.

**2. The corporate page has two CTAs in the hero and one is vestigial.**
`corporate-events/COPY.md` hero lists: "CTA 1 (primary): Request a Corporate Quote →" and "CTA 2 (secondary): View Installed Work." The secondary CTA points to installed work but the installed work gallery is already on the same page below. A buyer reading the hero does not need a second button to scroll down to a section they haven't seen yet. Remove the secondary CTA from the hero. If you want a "View installed work" anchor, place it as a text link adjacent to the photo gallery heading instead — that's where it belongs.

**3. The private memorial entry block uses the KJSCOTT review in a slightly truncated form that loses a key line.**
In `private-celebrations/COPY.md`, the memorial entry block blockquote reads: "I needed a sports themed funeral stand. I told them what I needed, they captured my vision, delivered on time, very reasonable, and had many complements." But the full review (as used by other contestants including C7 and C2) adds: "Very tasteful and meaningful." Those four words at the end are the emotional close of the review — they're what a grieving buyer needs to hear. The truncated version stops at "many complements" (also: compliments, not complements — that is a copy error in every contestant who included the review, but it should be caught here). Restore the full quote and fix the spelling.

**4. The civic "Trust Pillars" section and the "Audience Services" section cover adjacent territory without enough differentiation.**
Both sections describe what LT does for civic events — parade/entrance arches, stage decor, color-matching, outdoor durability. A buyer reading both sections feels some repetition. The Trust Pillars currently read as a visual version of the Audience Services content. One option: collapse the Trust Pillars into a brief capability bar (icons + one-line labels only, no body copy) so they function as a summary anchor rather than a second explanation. The audience services section then holds the full copy.

**5. The stats row uses "10+ years of civic events" but the body copy says "over two decades" elsewhere.**
`civic-community/COPY.md` proof stats row: "10+ | years of civic events." The Section 3 body says "8+ city governments" which is verifiable, but the hero lede says "over two decades." A buyer scanning the stats row and then reading the body will notice the year figures are inconsistent. Pick one claim and use it everywhere. If LT has been in business 20+ years, the stat should say "20+ years" not "10+."

### Don't Change

- **The civic vendor documentation cards.** The W-9, COI, PO, net-30, multi-venue specificity is precisely the operational language that differentiates this page from every other contestant's civic proof. The maintainer protection block you added is the right call. Leave the cards alone.
- **The corporate "AP-Friendly Invoicing" buyer note.** "Invoices issued through ERPNext with line items, service dates, and event details" is specific in a way that generic "AP-friendly" claims are not. The format detail matters to the buyer who has to submit for cost-center allocation.
- **The schools case story featuring WSU Weberstock.** Named event, named outcome (full entry arch and photo-opt in WSU purple and white), featured in broadcast partner coverage. That is proof structure, not description. It earns the page.

### Stretch Goal

The corporate client crawl was flagged by C7 as potentially violating the "no marquee carousels" anti-default in the brief. The brief says "Do not copy generic ecomm patterns (huge slider, marquee carousels, parallax stacks)." Whether the crawl qualifies depends on implementation — a CSS marquee or JavaScript scroll loop is a carousel pattern; a static two-row wrapping text list is not. If the crawl is implemented as a scrolling animation, it must be reconsidered. If it is a static responsive layout, it is fine. The stretch goal is to add a clarifying note to `corporate-events/DESIGN-NOTES.md` that explicitly names the implementation constraint: "static layout only — no CSS scroll animation or JS marquee." This protects the design decision in implementation phase without changing any copy.

---

## C2 — The Right Room (26.00 — Zero Variance, Style Discipline Leader)

You have the highest style discipline score in the field and the only zero-variance result. Every peer gave you exactly 26. The border-direction posture system is the suite's most elegant structural signature. Tightening here is fine-grained.

### Tighten This

**1. The civic hero H1 and lede work together but neither is quotable.**
`civic-community/COPY.md` hero: "Built for public events. Designed to photograph." That is accurate and on-register, but compared to your private H1 ("Designed for the moment. Made to last in the photos."), the civic line is describing a capability rather than naming a truth. The private H1 is stronger because it names what the buyer is actually buying. The civic equivalent would name what a city events coordinator is actually protecting — her organization's public image. "Built for public events. Designed to photograph." is close; consider whether "public events" can be sharpened to name the civic-professional context more precisely. One option: "The decor the city photographs. The install the coordinator stands behind." That is more specific about the attribution chain.

**2. "It is not a department. It is part of the work." needs whitespace protection.**
Your `LOOP-2-COMPLETE.md` explicitly notes this line should have "air on both sides." Verify that in the HTML implementation the surrounding paragraph breaks are enforced — this sentence must not appear mid-paragraph or adjacent to a list item. The copy file shows it embedded in a panel body. In the rendered page, if the CMS or Frappe's Rich Text strips surrounding `<p>` tags into a single block, the sentence loses its weight. Add a note to `private-celebrations/DESIGN-NOTES.md` specifying that this sentence must render as an isolated paragraph with no adjacent content — so the build instance knows this is a layout constraint, not just copy.

**3. The civic procurement cards have a heading-level ambiguity.**
`civic-community/COPY.md` Section "Civic Procurement Notes" shows four cards (Invoicing, Insurance, Logistics, Permitting). Each card has a bold label and an italic category title above it (e.g., "*City & County Accounts*" above "Invoicing"). The italic category label appears to be a sub-eyebrow inside the card. If both the bold label and the italic subtitle are rendered at the same visual level, the hierarchy collapses and the card reads as a wall of text. Add a note to `civic-community/DESIGN-NOTES.md` specifying the render hierarchy: italic subtitle is eyebrow-weight (Lato, tracked, small), bold label is card H3 (Cormorant Garamond or Lato semibold), body is Lato regular. Without that specification, a build instance will make a guess.

**4. Schools page Trust Pillars and Service Notes are duplicated content.**
In `schools-campuses/COPY.md`, the Trust Pillars section (four pillars) and the Service Notes section (four cards) contain identical text: "School Colors. Exactly." / "On Schedule for School Logistics" / "Family-Friendly and Safe" / "Budget-Aware Builds." The COPY.md even notes "(Four service cards repeat the trust pillar content in card format)." Two sections with identical content in two different visual treatments on the same page is a structural echo — the buyer reads it twice without gaining new information. Either collapse one of the sections, or differentiate the card bodies so they add operational detail the pillar text doesn't carry.

### Don't Change

- **The border-direction posture system.** Left-rule (civic), top-rule (corporate), bottom-rule (schools), full-border (private). This is the only suite-level structural signature in the contest that communicates audience relationship through form. It is documented, intentional, and elegant. Do not let implementation simplify it away — but that protection note in the README is already there, so you're ahead of it.
- **"Something beautiful for a hard day."** The celebration-of-life H2. It is quiet, specific, and exactly right. Nothing should replace it.
- **The schools "intentionally short roster" framing.** Acknowledging the small roster as a depth signal ("each relationship involves multiple events per year, color-matched builds, and a coordinator who already has our number saved") is honest in a way that avoids the padding problem. Leave it.

### Stretch Goal

The civic page Loop 2 added a quotable sentence to the SLC Pride story: "When SLC Pride is on the news that night, these are the arches in the frame." That sentence names the attribution chain specifically — the arches, the news, the frame. Your `civic-community/COPY.md` proof story for SLC Pride currently reads: "Full balloon arches sized for public parade clearance — designed to read at distance and photograph well from the street. Coordinated with Pride Center and Equality Utah on multi-year installs." The multi-year relationship note is strong proof. The stretch goal is to add one sentence before that closes the circle the way your new Loop 2 line does — naming the specific visibility stakes of the install. Something like: "When the parade coverage runs, these arches are in every photograph." That's not a redesign — it's one sentence that makes the existing proof feel earned rather than listed.

---

## C5 — Proof-First Buyer Suite (26.00 — Proof Density Leader, Zero Variance)

You have the highest proof density score in the field (9.00, perfect peer consensus). The AP/billing section is the only standalone named procurement section in the contest. The tightening here is about voice register and one structural gap.

### Tighten This

**1. The civic hero H1 is the quietest headline in the suite and it shows.**
`civic-community/COPY.md` hero H1: "Balloon decor for Utah public events." Compare to your corporate H1 ("Custom balloon decor for professional events.") and schools H1 ("Balloon decor for schools and campuses.") — the suite has a consistent construction that is accurate but not editorial. The hero lede does more work than the H1 on every page. The civic H1 in particular is the most under-written headline of the top four: every other contestant named the stakes or the audience posture; this one names only the product and location. Consider lifting one idea from the lede — "City celebrations, Pride events, chamber gatherings, and community milestones" — into the H1 level in condensed form. Even "Utah public events, built for the record." is more specific than the current version without departing from the quiet confidence register.

**2. The private opening act has three paragraphs and a pull-quote, and the third paragraph after the pull-quote breaks the emotional sequence.**
`private-celebrations/COPY.md` opening act: Para 1 (claims the full range including grief buyer) → Para 2 (direct address to grief buyer) → KJSCOTT pull-quote → Para 3 ("For every other kind of personal celebration..."). The third paragraph is a pivot back to the main buyer after the grief buyer has been addressed — but the phrasing "For every other kind of personal celebration" positions the grief buyer as an exception and everyone else as "every other." That is a small register problem: a grieving person reading Para 2 and then seeing "for every other kind" next will feel slightly moved aside. Consider cutting Para 3 or moving the category guide reference into a transition that doesn't frame memorials as a special case. Something like: "Below, the full range of occasions the team handles across the Wasatch Front." — neutral, doesn't re-sort the buyer types hierarchically.

**3. The corporate story block names FanX as a multi-day foot-traffic install but the sector grid categorizes FanX under Entertainment.**
`corporate-events/COPY.md` story block: "The FanX install has to hold for days of foot traffic." That is a genuinely differentiated proof claim — multi-day durability under convention traffic is different from a one-day ribbon cutting. But FanX appears in the sector grid under "Entertainment" alongside Megaplex and Paramount without that operational detail surfacing. The story block names the durability claim; the sector grid omits it. A one-word parenthetical addition to the FanX sector card note ("multi-day convention install") would close the gap between what the story claims and what the proof grid shows.

**4. The schools color-matching section opens with "Color-matching for school events starts with the school's official palette, not the balloon catalog's nearest option." — but the icon proof bar four lines later repeats the same claim.**
`schools-campuses/COPY.md` School Color Note H2 body, and Icon Proof Bar first entry ("School Spirit Ready: University red, institutional navy — sourced to the school's official palette, not the catalog's nearest option.") use near-identical language. This is an echo within a small page section. Either the icon label carries the summary ("School Colors. Exactly.") without a copy echo in the body, or the section body develops the idea further than the icon copy can. Both at the same specificity level creates redundancy.

**5. The "usually within one business day" claim in the corporate CTA is the only time-estimate in the suite.**
`corporate-events/COPY.md` CTA section: "The team returns a formal quote, usually within one business day." This is a commitment the page cannot verify and the implementation cannot enforce. It also introduces a time framing that the brief's "We Don't Do Time" rule would flag in a GL-facing context. In a buyer-facing context, a turnaround commitment is reasonable — but "usually" softens it to the point of meaninglessness for a procurement buyer who needs to plan around it. Either firm it up ("within one business day for most requests") or drop it and let the CTA stand without a turnaround promise.

### Don't Change

- **The AP/billing section isolation on the corporate page.** "AP-friendly by design" as a named section — not a bullet inside a trust pillar — is the right architectural choice. It signals that procurement routing is a first-class concern for LT, not an afterthought. This is the only contestant who built it that way. Protect it in implementation.
- **The schools occasions grid after the Loop 2 upgrade.** The operational texture added to each card body (7am install window, pep rally timing, student leadership approval flow) is the kind of specificity that reads as institutional knowledge, not feature claims. That texture is the work that earned the proof density score.
- **The civic five-category client grouping.** Five groupings (Pride & Equality / Wasatch Front Municipalities / Chambers & Civic Organizations / Public Venues & Institutions / Community Districts & Retail Centers) with work-type context per category is the most detailed civic proof architecture in the field. The parenthetical work-type notes ("ribbon cuttings, city celebrations, outdoor civic events") add the layer of context that C7 and C2's civic rosters don't carry.

### Stretch Goal

The private page's opening act contains some of the best private-buyer writing in the contest ("Some occasions announce themselves months in advance. Others arrive without warning..."). But the hero lede ("The celebrations that call for something beautiful. And the days that need it most.") is doing a lot of work implicitly — it is the only part of the hero that reaches the grief buyer without naming them. The stretch goal is to make sure the hero and the opening act feel like one continuous register, not two tones. Read them aloud in sequence: the hero lede has editorial compression; the opening act Para 1 expands into full sentences. The transition lands naturally. But the eyebrow in the hero — "Birthdays · Weddings · Showers · Milestones · Remembrance" — uses "Remembrance" where the rest of the suite uses "Celebrations of Life" or "Memorial." Eyebrow vocabulary should match section vocabulary. Change "Remembrance" to "Celebration of Life" to close the small naming gap between the hero and the section below.

---

*These notes are for polish — the work is already strong. Each item above has a specific fix. None requires a structural change. The contestants who built this far did something real. The job now is to honor that by closing the small gaps before GL sees it.*
