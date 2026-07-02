D:2026-05-10 | Check:local artifacts/source/runtime code 2026-05-10 | Confidence:[LOCAL-PROOF]
# Ready-to-order product candidate list — Locally Twisted ecommerce launch scope

## Scope / non-scope

This is a launch-scope candidate list, not import approval, public launch approval, price approval, media approval, payment proof, or permission to mutate catalog_data/ERPNext. catalog_data is used only as read-only source witness.

Classification values:

- `checkout_ready_now` — safe for direct checkout with current stored catalog state and backend proof.
- `checkout_ready_after_small_fix` — low-variation/source-backed candidate, but needs narrow launch fixes before public checkout.
- `quote_first` — should be visible as quote/invoice-first product or event-page example; do not expose paid checkout.
- `hide_or_needs_review` — do not feature in launch shop until source/product-family decision is made.

## Bottom line

- `checkout_ready_now`: **0 products**.
- `checkout_ready_after_small_fix`: **15 products** from the current source `checkout` lane.
- `quote_first`: **33 products** should stay quote-first/event-page/inspiration scoped.
- `hide_or_needs_review`: **5 products** need product-family/add-on/seasonal visibility review before launch featuring.

Reason no product is `checkout_ready_now`: Lane C found all 53 published ERPNext Website Items still stored `lt_product_page_type=needs_review` and `lt_commerce_lane=needs_review`; runtime inference proves representative paths, but saved product classifications and exact ready-to-order note proof are still launch gates.

## Evidence used

- `workstreams/ecommerce-audit/agent-brief-ready-to-order-ecommerce-infrastructure-2026-05-10.md` — direct checkout only for simple low-variation products; complex decor quote/invoice-first.
- `workstreams/ecommerce-audit/ready-to-order-checkout-scope-decision-2026-05-10.md` — customer notes allowed but not pricing/scope authority; required classification values.
- `workstreams/ecommerce-audit/event-pages-vs-ready-to-order-shop-contract-2026-05-10.md` — high-ticket decor belongs on event/audience pages with quote CTAs.
- `workstreams/ecommerce-audit/ecommerce-product-proof-matrix-2026-05-10.md` — 53-row source matrix: 15 checkout-lane / 38 quote-first.
- `audits/catalog-import-audit-2026-05-08/15-product-page-contract-source-audit.json` — destructive import blocked; warning counts: `missing_resolver_prices=49`, `unclassified_gallery_images=49`, `axis_needs_review=9`, `color_axis_customization=25`.
- `audits/catalog-import-audit-2026-05-08/21-product-page-price-enrichment-candidates.json` — candidate units and live ERPNext snapshot prices used below.
- `workstreams/ecommerce-audit/cart-checkout-intent-preservation-audit-2026-05-10.md` — Unicorn Bouquet + foil number proof; Classic Arch quote-first proof; stored Website Item classifications still `needs_review`.
- `output/product-page-architecture-readiness-infrastructure-research-20260510.json` — readiness verifier currently `ok=true`, 14 pass / 0 blocked / 1 deferred; payment/finance deferred.
- Runtime code: `product_page_runtime.py`, `api/cart.py`, `www/checkout.py`, `product_quote_runtime.py` — line-level payload fields, quote-first blocking, add-on guard, optional `order_notes` path.

## Direct-checkout launch candidates

These are the products I would put in the first ready-to-order shop tranche **after small fixes**, not now. They are low-variation, have source-enriched prices, and avoid custom color/design/install choices.

| Product / source id | Classification | Price / options | Rationale | Small fix before public checkout | catalog_data/source evidence still needed |
|---|---|---|---|---|---|
| Unicorn Bouquet / 115 | `checkout_ready_after_small_fix` | Bouquet Size: Small $35 / Medium $70 / Large $85; optional foil number +$12 each | Representative proof slice already verified cart, checkout display, Sales Order Item / Sales Invoice Item payload, and foil-number add-on expansion. | Save Website Item lane/type; verify checkout with and without customer `order_notes`; final price/media signoff. | Confirm catalog_data product identity/category and cart/order-line preservation for selected size + foil number. |
| Mickey Mouse Bouquet / 116 | `checkout_ready_after_small_fix` | Same bouquet sizes/prices; optional foil number +$12 each | Same bounded bouquet pattern as Unicorn; no customization axes. | Same as above; run at least one non-Unicorn bouquet smoke proof or family verifier. | Same as above for this product/page. |
| Minion Bouquet / 117 | `checkout_ready_after_small_fix` | Same bouquet sizes/prices; optional foil number +$12 each | Same bounded bouquet pattern; source media has more extra images, so image choice needs review. | Save classification; choose launch gallery/primary image; note proof. | Confirm catalog_data public category/image expectations and size/foil cart payload. |
| Encanto Bouquet / 118 | `checkout_ready_after_small_fix` | Same bouquet sizes/prices; optional foil number +$12 each | Bounded character bouquet pattern. | Save classification; final image/price signoff; note proof. | Confirm catalog_data size/foil behavior and no hidden customization axis. |
| Stitch Bouquet / 119 | `checkout_ready_after_small_fix` | Same bouquet sizes/prices; optional foil number +$12 each | Bounded character bouquet pattern. | Save classification; final image/price signoff; note proof. | Confirm catalog_data size/foil behavior and no hidden customization axis. |
| Flamingo Bouquet / 120 | `checkout_ready_after_small_fix` | Same bouquet sizes/prices; optional foil number +$12 each | Bounded bouquet pattern, no color/design matrix. | Save classification; final image/price signoff; note proof. | Confirm catalog_data size/foil behavior and delivery eligibility. |
| Football Bouquet / 121 | `checkout_ready_after_small_fix` | Same bouquet sizes/prices; optional foil number +$12 each | Bounded sports bouquet pattern. | Save classification; final image/price signoff; note proof. | Confirm catalog_data size/foil behavior and no team/color custom dependency. |
| Soccer Bouquet / 122 | `checkout_ready_after_small_fix` | Same bouquet sizes/prices; optional foil number +$12 each | Bounded sports bouquet pattern. | Save classification; final image/price signoff; note proof. | Confirm catalog_data size/foil behavior and no team/color custom dependency. |
| Space Bouquet / 123 | `checkout_ready_after_small_fix` | Same bouquet sizes/prices; optional foil number +$12 each | Bounded character/theme bouquet pattern. | Save classification; final image/price signoff; note proof. | Confirm catalog_data size/foil behavior and no hidden customization axis. |
| Over the Hill Bouquet / 124 | `checkout_ready_after_small_fix` | Same bouquet sizes/prices; optional foil number +$12 each | Bounded birthday bouquet pattern. | Save classification; final image/price signoff; note proof. | Confirm catalog_data size/foil behavior and customer text boundaries. |
| Paw Patrol Bouquet / 141 | `checkout_ready_after_small_fix` | Same bouquet sizes/prices; optional foil number +$12 each | Bounded character bouquet pattern. | Save classification; final image/price signoff; note proof. | Confirm catalog_data size/foil behavior and no hidden customization axis. |
| Elsa Bouquet / 142 | `checkout_ready_after_small_fix` | Same bouquet sizes/prices; optional foil number +$12 each | Bounded character bouquet pattern. | Save classification; final image/price signoff; note proof. | Confirm catalog_data size/foil behavior and no hidden customization axis. |
| Holy COW!! Bouquet / 143 | `checkout_ready_after_small_fix` | Same bouquet sizes/prices; optional foil number +$12 each | Bounded character/theme bouquet pattern. | Save classification; final image/price signoff; note proof. | Confirm catalog_data size/foil behavior and no hidden customization axis. |
| Easter Balloon Cups / 130 | `checkout_ready_after_small_fix` | Easter Designs: 7 choices; $13 | Low price, bounded single design axis, no add-ons/customization. Seasonal visibility is the main launch question. | Save classification; decide if current-season enough to show; verify design choice survives cart/order; final image signoff. | Confirm catalog_data design values and whether all 7 are orderable/in stock. |
| Mother's Day Bouquet / 165 | `checkout_ready_after_small_fix` | Single SKU; $65 | Simplest checkout candidate: no required/customization axes and source price gate already passes. | Save classification; decide post-Mother's-Day visibility; verify no-note/note checkout proof; final image signoff. | Confirm catalog_data page/category and whether sale window remains open. |

## Quote-first / event-page products

These should not be direct checkout launch products. They have high-ticket decor, install/venue/design implications, balloon color/customization axes, multiple variant dependencies, or source quote-first classification. They can be shown as examples/inspiration with quote CTAs, especially on event/audience pages.

| Product(s) | Classification | Why | Key options/notes |
|---|---|---|---|
| Baby Shower Combination Photo opt / 14 | `quote_first` | High-ticket/custom decor; color customization. | Latex colors; $650 source price. |
| Classic Organic Balloon Garland / 19; Premium Organic Garland / 52; Baby Shower Garland / 71; Organic Grab n' Go / 127; Large Garland / 177 | `quote_first` | Garland length + color/design decisions are custom decor, not ready checkout. | Garland Length; latex colors or Color Palette; prices range from $70 to $216 base snapshot. |
| Basketball Arch / 21; Easter Balloon Arch - Bunny Ear / 30; Halloween arch / 39; Pride progress Rainbow Balloon Arch / 55; 6 color rainbow arch / 135; Easter Arch / 158; Pride Arch / 179 | `quote_first` | Arch products imply scale, setup, delivery/install, and/or event-page inspiration fit. | Arch Size where present; prices from $250 to $375+; Halloween includes latex colors. |
| Premium Organic Arch / 53; Classic Organic Arch / 99 | `quote_first` | Organic arch + colors + add-on review is custom/quote territory. | Arch Size; latex colors; `Add ons` needs mapping. |
| Classic Arch / 57 | `quote_first` | catalog_data proof shows 4 true sizes plus 53 colors, Design, LED +$50; this is exactly the no-variant/custom quote pattern. | Keep as product quote/event-page example; do not force direct checkout. |
| Pemium Organic Column / 54; Classic Column / 58; Classic Organic columns / 65; 7' Butterfly Column / 125; 7' Epic Column / 126; Star Column / 131; Large Organic Column / 178 | `quote_first` | Columns are decor/install examples; several carry height/topper/color/add-on complexity. | Column Height/topper/latex colors/Color Palette; Star has Orbz topper review. |
| Number Balloon Columns / 22 | `quote_first` | Customer-specific number/color choices; quote-first protects fulfillment meaning. | Number colors + latex colors; source price $55 is not enough to make it checkout-safe. |
| Large head Missionary / 45 | `quote_first` | 30 combinations and personalization attributes; not ready-order simple. | Missionary, skin color, hair color. |
| Graduation Grab n Go / 38; Logo 3 layered bouquet / 134; Classic organic for easel / 152 | `quote_first` | Color/custom/logo/easel context can change labor/materials; capture intent first. | Latex colors. |
| Balloon Drop / 74 | `quote_first` | Event install/drop size and venue conditions need human review. | Drop Size; latex colors. |
| Sleepy Baby Column / 132; Baby Table decor / 133 | `quote_first` | Small decor but still color/custom event styling; should route quote until a ready-order package is explicitly approved. | Latex colors or Baby color. |
| 6' Graduation stands / 149 | `quote_first` | Stand selection and event/school fulfillment should be reviewed. | Graduation stands; 2 units. |
| Mother's day front yard 7' Column / 137 | `quote_first` | Yard/front-display install and seasonal context; not low-risk cart until reviewed. | Single unit, $140, media review. |

## Hide or needs review before launch featuring

These may later become checkout or quote-first pages, but I would not feature them in the first launch shop/event IA until their specific source warning is resolved.

| Product(s) | Classification | Why | Required decision |
|---|---|---|---|
| Birthday Deliveries / 128 | `hide_or_needs_review` | Source has 81 combinations plus `Add Bouquet` review; despite delivery/bouquet hints, the current matrix classifies it quote-first. | Decide whether this becomes a curated ready-order delivery package or stays quote-first; map Add Bouquet safely. |
| Marble table decor / 140 | `hide_or_needs_review` | Orbz topper warning and unclear product-family fit. | Map Orbz topper or remove/hide until quote-first copy is written. |
| Butterfly "GET WELL" Bouquet (Latex free) / 144; Bandage "GET WELL" Bouquet (Latex free) / 146; Shooting star "GET WELL" Bouquet (Latex free) / 147 | `hide_or_needs_review` | Simple $35 items, but source has `Plush add ons` review; existing source classified quote-first. | Decide whether plush is removed, quote-only, or mapped as a priced add-on; then these could become good checkout candidates. |

## Customer note considerations

- Every checkout-ready product should allow an optional customer/order note.
- The note must be preserved in backend order records and operator view.
- The note must not change price, approve custom sizing/install, or convert a simple package into custom decor.
- Current code has checkout `order_notes` handling and Sales Order timeline transfer; candidate launch still needs a ready-to-order proof with **no note** and **with note**.

## Launch-useful next gates

1. Save explicit Website Item classifications for the 15 direct-checkout candidates; keep all others `quote_first` or hidden/review.
2. Run a family verifier for all character/sports bouquet variants with foil-number add-on, not just Unicorn.
3. Verify one checkout candidate with no note and one with a note; prove Sales Order/payment/fulfillment record preservation without exposing PII/secrets.
4. Confirm launch gallery/primary image choices for the 15 candidates; media remains a row-level blocker in existing packets.
5. Keep payment success unclaimed until deliberate payment/backend transaction proof exists.
