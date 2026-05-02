# Plan Custom Decor Flow

Status: V2 UX/product spec draft
Last updated: 2026-05-02 by Codex
Scope: background planning only. This is not a V1 launch blocker and does not prove any production route exists.

## Purpose

Plan Custom Decor should be the guided planning path for larger, consultative, multi-piece event installations. It should help a buyer shape an event look, share it with stakeholders, and send Locally Twisted enough context to start a useful sales conversation.

Ready to Order remains the simpler ecommerce path for small, already-structured products where the customer is prepared to buy without design consultation.

This flow should feel like a professional event-planning studio, not a kids' coloring game. The customer should make a small number of clear decisions, see the event composition grow, and understand that the result is a planning visualization, not a final engineering drawing.

## Verified Source Grounding

Verified from current repo files:

- `workstreams/design-studio-v2.md` defines the product split: Ready to Order is for simple ecommerce products; Plan Custom Decor is for larger consultative installations.
- `workstreams/design-studio-v2.md` names corporate, school, civic, community, venue, and premium private events as the intended higher-quality inquiry targets.
- `workstreams/design-studio-v2.md` says the production tool should stay Frappe-native where possible and should eventually feed inquiry and CRM workflow.
- `workstreams/design-studio-v2.md` identifies the desired synthesis: C4 low-load style entry, C2 palette-inheriting suggested pieces, C3 dual-audience completion, and C1 pieces-considered CRM context.
- `research/contest-customizable-event-decor-tool/FINAL-SURFACE.md` confirms all four contest concepts were Frappe-recreatable in vanilla JS/jQuery/inline SVG terms, but also states the contest is source material, not a winner-pick.
- `research/contest-customizable-event-decor-tool/PRODUCT-DETAILS.md` defines load-bearing product and construction constraints: classic arches, columns, backdrops, garlands, drops, and bouquet logic are structurally different; color names are the supplier-actionable identifier; hex values are only approximation until approved.
- `workstreams/brand-audience-style-reset.md` sets the brand frame: Locally Twisted is the brand; Jeff is an owner and process source, not the customer-facing brand center.
- Render evidence checked: C4 entry thumbnail cards, C2 pre-tinted composition suggestion, C3 completion card, and C1 pieces-considered completion state.

Inferred for this spec:

- Corporate, school, civic, venue, and premium private buyers need stakeholder approval and color matching more than playful freeform drawing.
- A low-choice, guided wizard will fit this buyer better than open drag-and-drop.
- Capturing skipped suggestions is useful sales context as long as it is not framed as pressure to the customer.

Needs GL/Jeff approval:

- Exact public name: "Plan Custom Decor" is recommended for the customer-facing path; "Design Studio" can remain the internal feature name.
- Which installation types are included in the first prototype.
- Which color-matching language is legally and operationally acceptable before official hex/Pantone mappings exist.
- Whether share links can be public token links, account-only saved designs, or both.
- Which event-context questions are required versus optional.

## Buyer Entry Flow

The entry should start from the buyer's event context, not from a blank product catalog.

Recommended entry points:

| Buyer type | Entry label | First question | Why it matters |
|---|---|---|---|
| Corporate | Corporate event decor | What kind of event are you planning? | Captures brand color, venue, stakeholder, and quote-context needs early. |
| School | School and team events | Are you matching school/team colors? | Makes color matching and approval sharing feel expected. |
| Civic/community | City, festival, and public event decor | Is this indoors, outdoors, or mixed? | Public installs often need scale, logistics, and durability context. |
| Venue/planner | Venue and photo-op installations | What space are we decorating? | Connects piece choices to entrances, stages, photo walls, and guest flow. |
| Premium private | Weddings, showers, and milestone events | What moment should the decor support? | Keeps private events elevated without making the interface childish. |

The first screen should ask for no more than:

1. Event type.
2. Event date or rough month.
3. Indoor/outdoor/unsure.
4. Organization or event name, optional.
5. Start with a primary installation piece.

The first screen should not ask for budget, full contact details, or every venue detail. Those belong after the customer has enough confidence to continue or at the final inquiry step.

## Ready to Order vs Plan Custom Decor

Use this split consistently across navigation, teaser copy, and handoff:

| Path | Customer mindset | Product types | UX promise | Output |
|---|---|---|---|---|
| Ready to Order | "I know what I need and want to buy." | Bouquets, themed items, simple delivery/pickup-friendly decor, lower-risk ecommerce products. | Browse, select options, add to cart, checkout. | Order/cart record. |
| Plan Custom Decor | "I need help shaping a bigger event look." | Arches, columns, backdrops, organic garlands, balloon drops, larger photo-op or venue installations. | Plan a look, match colors, add complementary pieces, share/save, send inquiry. | Design summary plus CRM payload for follow-up. |

Do not move every customizable item into Plan Custom Decor. Bouquet and small-product customization can stay in Ready to Order unless the specific use case is a larger logo/corporate package.

Recommended V1 relationship:

- V1 should not expose a half-working design studio.
- V1 can include a polished "Plan Custom Decor" guided inquiry entry that explains the consultative path and routes into the existing inquiry/Lead workflow.
- A small teaser can say customers will be able to save/share planned designs later, but it should not imply the V2 studio is live.
- Ready to Order should remain visibly available for simple products so the V2 concept does not add friction to normal ecommerce.

## Recommended V2 Prototype Flow

### 1. Context gate

Customer sees a calm, professional entry screen:

- "Plan Custom Decor"
- "Build a starting point for a larger event installation."
- Event type chips: Corporate, School, City/community, Venue/photo op, Wedding/private, Not sure.
- Indoor/outdoor/unsure.
- Event date or rough month.
- Organization/event name, optional.

Locally Twisted receives:

- buyer segment
- event context
- rough timing
- indoor/outdoor uncertainty
- organization/event name if provided

### 2. Primary piece selection

Customer chooses one primary installation piece from visual cards. The first prototype should keep this narrow:

1. Classic arch.
2. Pair of classic columns.
3. Backdrop or photo-op wall.

Organic garland should be a controlled expansion after classic arch, columns, and backdrop prove the interaction and renderer constraints. Balloon drop can be a later event-context-specific option because it is representational and indoor/logistics-sensitive.

Customer sees:

- piece cards with realistic plain-language labels
- short use-case hint, such as entrance, stage, photo wall, check-in, dance floor, or reveal moment
- no construction jargon as the main label

Locally Twisted receives:

- selected primary piece
- reason/context if selected through a use-case card
- any piece cards viewed or hovered/tapped long enough to indicate interest, if captured respectfully

### 3. Style and scale

Customer chooses a style and approximate scale. This should use visual cards and a few common reference points instead of technical calculators.

For classic arch and columns:

- choose style: Swirl, Alternating, Color-blocked, or Organic-inspired if included later
- choose approximate size: small/standard/large, with optional "not sure"
- show reference context: doorway, stage, gym entrance, photo backdrop, or venue entrance

For backdrop/photo-op wall:

- choose layout: solid, vertical stripes, horizontal stripes, large blocks, diagonal, lattice if approved
- choose approximate dimensions or a guided size chip: 8x8, 10x10, wide wall, custom/not sure

The tool should not show final cluster counts to customers by default. It can store estimated size/math internally for follow-up, but the UI should avoid making the planning sketch feel like an engineering quote.

### 4. Organization color matching

Color matching should be framed as "starting palette," not certified brand matching.

Customer sees:

- "Match an organization, school, team, or event palette."
- Option A: choose from Locally Twisted balloon color names.
- Option B: enter brand/team colors as names or rough hex values.
- Option C: upload an inspiration image later if approved.
- Clear helper copy: "We will confirm final balloon colors with you before production."

Required picker behavior:

- Show balloon color names prominently.
- Store color names as the load-bearing value.
- Use hex/visual swatches only as approximate aids until Locally Twisted approves official mappings.
- Let the customer mark colors as "must match closely" versus "close enough / same feeling."

Locally Twisted receives:

- selected LT balloon color names
- customer-entered brand/team color references
- whether the customer needs close brand matching
- unresolved colors needing follow-up

### 5. First piece preview

Customer sees one clear preview of the primary piece with the selected palette applied.

The preview should communicate:

- approximate look
- chosen color names
- selected style
- scale context
- "Planning preview. Final design and installation details are confirmed by Locally Twisted."

Customer can:

- continue with this piece
- adjust colors/style
- skip styling details and send as a starting point

Locally Twisted receives:

- primary piece configuration
- selected colors and color source
- skipped/unknown fields
- whether the customer chose "send as starting point"

### 6. Complementary piece suggestion

After the primary piece is configured, the composition grows by invitation.

Recommended behavior:

- Show one complementary piece at a time, pre-tinted with the customer's palette.
- Keep the prompt optional and calm.
- Always provide skip/not now.
- Do not use pressure copy such as "complete your design."

Example suggestion logic:

| Primary piece | Suggested next piece | Reason |
|---|---|---|
| Arch | Pair of columns | Frames an entrance or stage without making the customer start over. |
| Backdrop/photo wall | Garland or columns | Creates a fuller photo-op moment. |
| Columns | Arch or backdrop | Helps customers understand how columns support a larger scene. |
| Drop | Stage or entrance decor | Keeps balloon drop from feeling isolated, if drop is supported later. |

Customer actions:

- Add suggested piece.
- Skip this suggestion.
- See another option, limited to one alternate.
- Finish with current design.

Locally Twisted receives:

- suggestion shown
- suggestion added, skipped, or replaced
- inherited palette state at the time of suggestion
- pieces considered but not selected

### 7. Multi-piece composition

The composition screen should behave like a planning board, not a freeform drawing tool.

Customer sees:

- selected pieces arranged in a simple scene or list-plus-preview
- each piece as editable
- shared palette visible
- "Add another piece" with a short curated list
- "Finish and send" always available

Rules:

- No drag-and-drop in the first prototype unless the architecture lane approves it.
- No open canvas that implies exact placement or engineering feasibility.
- No final price promise.
- No balloon twisting mixed into balloon decor composition. Twisting can be a separate service add-on/inquiry checkbox later.

Customer can:

- edit primary piece
- add complementary piece
- skip remaining suggestions
- remove a piece
- mark a piece as "maybe" if GL approves this state

Locally Twisted receives:

- selected pieces
- removed pieces if they were previously selected
- skipped suggestions
- maybe pieces if supported
- final sequence of decisions

### 8. Save and stakeholder share

The share/save flow is important for corporate, school, civic, venue, and premium private buyers because they often need approval before booking.

Recommended first behavior:

- Let a customer save without requiring a full account first.
- Ask for email only when saving or sharing.
- Generate a private share link with a clear expiration or token policy if approved.
- Allow "send a copy to myself."
- Allow stakeholder emails as optional, not required.

Customer sees:

- "Save this design"
- "Share for approval"
- "Send to Locally Twisted"
- short note field: "Anything your team should know?"

Locally Twisted receives:

- saved design/session ID
- share state
- stakeholder count or emails if customer enters them and consent rules allow
- notes added for approvers
- whether the design was submitted or only saved

Open privacy/legal decision:

- Whether stakeholder emails can be captured before the primary customer submits an inquiry.
- Whether public token links should expire.
- Whether saved designs require account login in production.

### 9. Completion summary

The final screen should serve two audiences at once.

Customer sees:

- design name or event name
- event context and rough date
- primary preview
- selected pieces
- selected colors by name
- items still to confirm
- save/share controls
- "Send to Locally Twisted" or "Request a planning follow-up"
- plain caveat: "This is a planning preview. We will confirm final design, sizing, installation details, and availability with you."

Locally Twisted receives:

- concise customer-readable summary
- structured sales payload
- per-piece configuration
- color names and any customer brand references
- scale/venue context
- pieces considered but not selected
- skipped/unknown fields
- save/share history
- contact details when submitted

The customer-facing screen should use "Locally Twisted" and "we/us." Internal notes can mention owner review or sales follow-up without putting Jeff at the center of the brand.

## CRM Payload Recommendation

The CRM payload should include both the final selected design and the decision trail that helps follow-up.

Recommended top-level fields:

```json
{
  "source": "plan_custom_decor_v2",
  "studio_version": "prototype_flow_2026_05_02",
  "status": "submitted",
  "customer": {
    "name": "",
    "email": "",
    "phone": "",
    "organization": ""
  },
  "event": {
    "type": "corporate|school|civic|venue|premium_private|unsure",
    "date_or_month": "",
    "venue_name": "",
    "city": "",
    "indoor_outdoor": "indoor|outdoor|mixed|unsure",
    "decision_deadline": ""
  },
  "color_matching": {
    "needs_close_match": true,
    "organization_palette": [],
    "selected_lt_colors": [],
    "unresolved_colors": [],
    "customer_notes": ""
  },
  "selected_pieces": [],
  "pieces_considered": [],
  "pieces_removed": [],
  "customer_summary": "",
  "sales_follow_up_summary": "",
  "share_state": {
    "saved": false,
    "shared": false,
    "stakeholder_count": 0
  },
  "disclaimers_acknowledged": {
    "planning_preview_not_final_engineering": true,
    "colors_confirmed_before_production": true
  }
}
```

Recommended selected piece shape:

```json
{
  "piece_type": "classic_arch",
  "role": "primary",
  "style": "swirl",
  "scale": {
    "customer_label": "standard entrance",
    "approx_width_ft": null,
    "approx_height_ft": null,
    "exactness": "rough"
  },
  "colors": [
    {
      "lt_color_name": "Reflex Gold",
      "customer_reference": "school gold",
      "match_priority": "close"
    }
  ],
  "customer_notes": "",
  "unknowns": ["final dimensions", "venue access"]
}
```

Recommended considered piece shape:

```json
{
  "piece_type": "pair_classic_columns",
  "suggested_after": "classic_arch",
  "suggestion_reason": "frames entrance",
  "palette_inherited": true,
  "customer_action": "skipped",
  "shown_at_step": "complementary_piece_suggestion"
}
```

CRM display should translate this into plain language, for example:

> Customer planned a corporate entrance look for June. Selected a classic arch in Reflex Gold, Black, and White. Considered matching columns but skipped them. Needs close match to school colors. Final dimensions and venue access need follow-up.

Do not call this an "Opportunity" in customer-facing or simplified backend copy. Use plain labels such as "Design Summary," "Pieces Selected," "Also Considered," "Colors to Confirm," and "Next Follow-Up."

## Customer Sees vs Locally Twisted Receives

| Step | Customer sees | Locally Twisted receives |
|---|---|---|
| Entry | Event type, date/month, indoor/outdoor, organization optional. | Buyer segment, timing, install context, organization/event name. |
| Primary piece | Visual cards for arch, columns, backdrop/photo wall. | Selected primary piece and any considered starting points. |
| Style/scale | Plain style labels and approximate scale references. | Style, rough scale, unknowns for follow-up. |
| Colors | Named LT balloon colors plus organization color references. | Supplier-actionable color names and brand-match priority. |
| Preview | Planning visualization and editable choices. | Configured primary piece and skipped fields. |
| Suggested piece | Optional pre-tinted complementary piece with skip/add. | Suggestion shown, added/skipped state, inherited palette. |
| Composition | Selected pieces, simple planning board, finish anytime. | Final pieces, removed pieces, decision sequence. |
| Save/share | Save, share for approval, send to Locally Twisted. | Session/share state and stakeholder metadata if approved. |
| Completion | Customer-readable summary and clear next step. | CRM payload, sales follow-up summary, pieces considered but not selected. |

## Key Decisions

- Customer-facing name should be "Plan Custom Decor." "Design Studio" can remain internal or secondary.
- Keep Ready to Order and Plan Custom Decor separate in purpose, navigation, and CRM output.
- Start with a guided wizard plus planning board, not an open canvas.
- First prototype should focus on classic arch, pair of classic columns, and backdrop/photo-op wall.
- Complementary pieces should be suggested one at a time and inherit the customer's palette.
- Skip behavior is first-class. Skipped suggestions become sales context, not customer pressure.
- Color names are the primary payload value. Hex and swatches are only approximate until approved.
- Completion must serve both the customer and Locally Twisted sales follow-up.
- The tool must state that outputs are planning previews, not final drawings, engineering plans, or confirmed quotes.

## Risks and Contradictions

- Contest mockups often use "Jeff" in customer-facing CTAs. Current brand reset says Locally Twisted is the brand, so V2 should use "Send to Locally Twisted" or "Request a planning follow-up."
- Some contest screens feel parent/kid-party oriented. The V2 target is higher-value corporate, school, civic, venue, and premium private buyers, so the tone needs to be calmer and more professional.
- The render concepts include bouquets and balloon drops in the same entry grid. Product details say bouquets are mostly theme/SKU-bundle logic and drops are representational/logistics-sensitive, so they should not lead the first prototype.
- Color hex values in mockups are approximations. Product details say Locally Twisted color names are load-bearing and official hex/Pantone mappings need later approval.
- Backdrops, arches, garlands, and columns can be any size, but asking for exact dimensions too early will increase cognitive load. The flow should capture "rough/not sure" first and let sales follow-up refine it.
- Save/share is important but not designed in the contest field. It needs privacy, token, expiration, and account decisions before production.
- Capturing stakeholder emails before inquiry submission may create consent and privacy questions.
- Showing pieces considered is valuable for sales, but the UI must not make skipped pieces feel like customer failure or upsell pressure.

## Questions for GL/Jeff

1. Should the public label be "Plan Custom Decor," "Plan Event Decor," or another phrase?
2. Is the first prototype allowed to include organic garland, or should it wait until classic arch/columns/backdrop are proven?
3. Which buyer contexts should appear on the first screen: corporate, school, civic/community, venue, premium private, wedding, or other?
4. What color-match promise is acceptable before official LT hex/Pantone mappings exist?
5. Should saved designs be available through public token links, account login, emailed PDF/summary, or a combination?
6. Can stakeholder emails be stored before the customer formally submits an inquiry?
7. Which scale references are approved for public use: doorway, stage, gym entrance, city event, venue entrance, vehicle, people, or other?
8. Should "pieces considered but not selected" be visible to the customer on the completion summary, or only stored internally?
9. What minimum contact fields are required when a customer sends the design to Locally Twisted?
10. Should balloon twisting or face painting be offered as separate add-on inquiry prompts, or kept completely outside this studio?

## Recommended Next UX Artifacts

After GL/controller review, the next UX outputs should be:

1. Low-fidelity step map for desktop and mobile.
2. Copy deck for each step, using "Locally Twisted" and "we/us."
3. CRM field mapping against the current Lead schema.
4. Share/save state diagram.
5. Error and empty-state copy, especially for failed save/share/submit.
