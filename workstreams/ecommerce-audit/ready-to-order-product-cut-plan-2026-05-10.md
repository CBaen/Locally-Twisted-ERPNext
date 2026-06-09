D:2026-05-10 | Check:ready-to-order candidate list + Phase 6 launch decision packet 2026-05-10 | Confidence:[LOCAL-PROOF]
# Ready-to-order product cut plan — no-port status

## Purpose

Help GL/Locally Twisted cut the ecommerce launch scope without pretending every product belongs in direct checkout.

This is a planning/status artifact only. It does **not** approve product import, product deletion, legacy_source mutation, ERPNext catalog mutation, public launch, or live checkout.

GL correction at 2026-05-10 22:18 MDT: the current ERPNext products are **test products only**. Future product work must prove a controlled purge/reupload/import path where products that fit the LT schema fill the correct Website Item/custom fields, use cascading/dependency information, and trigger the intended automations. This plan narrows what should be tested first; it is not permission to trust or preserve the current product records as final catalog truth.

## Current status

The backend ecommerce infrastructure is real and verifier-backed for the scoped ready-to-order lane:

- checkout lane classification exists;
- quote-first/event products are blocked from paid checkout;
- ready-to-order checkout preserves product/customer intent into backend records;
- delivery/pickup/tax/payment/operator paths are locally proven;
- public ecommerce remains paused until production/live-payment cutover gates pass.

The right next move is **not** “port all products.” The right next move is to curate a small launchable checkout shelf and keep option-heavy work quote-first.

## Recommended launch shelf

Use only simple ready-to-order products for direct checkout after final owner/media/price sanity review.

### Keep for first checkout tranche

These are the 15 direct-checkout candidates already classified/proven by the ecommerce packet:

1. Unicorn Bouquet
2. Mickey Mouse Bouquet
3. Minion Bouquet
4. Encanto Bouquet
5. Stitch Bouquet
6. Flamingo Bouquet
7. Football Bouquet
8. Soccer Bouquet
9. Space Bouquet
10. Over the Hill Bouquet
11. Paw Patrol Bouquet
12. Elsa Bouquet
13. Holy COW!! Bouquet
14. Easter Balloon Cups — seasonal review before showing
15. Mother's Day Bouquet — seasonal review before showing

### Recommended practical cut for public launch

For the actual public first shelf, start even smaller:

- Character/sports/theme bouquet family only, if images/prices look acceptable.
- Hold Easter Balloon Cups unless it is seasonally appropriate.
- Hold Mother's Day Bouquet unless it is seasonally appropriate.

This gives a clean, boring-in-the-best-way checkout lane: package size, optional foil number where appropriate, delivery/pickup, customer note, payment.

## Keep quote-first / event-page only

Do not force these into direct checkout. They are useful marketing/product examples, but the checkout button should stay off.

Cut from direct checkout because they have too many options, install/context risk, color/design ambiguity, venue/labor implications, high-ticket quote needs, or add-on mapping uncertainty:

- Arches: Classic Arch, Premium Organic Arch, Classic Organic Arch, Basketball/Easter/Halloween/Pride/Rainbow arches, etc.
- Garlands: Classic Organic Garland, Premium Organic Garland, Baby Shower Garland, Organic Grab n' Go, Large Garland.
- Columns: Classic Column, Organic Columns, Butterfly/Epic/Star/Large columns, Number Balloon Columns.
- Event/installation pieces: Balloon Drop, Baby Shower Combination Photo Op, Graduation stands, yard/front-display installs.
- Logo/custom/personalized pieces: Logo 3 layered bouquet, Large Head Missionary, anything with significant color/personalization dependencies.
- Small decor that still depends on custom styling: Baby Table Decor, Sleepy Baby Column, easel decor.

These can still be shown as inspiration with quote CTAs on event/audience pages.

## Hide / needs review before featuring

Do not feature these in the first shop until a human product-family decision is made:

- Birthday Deliveries — too many combinations / Add Bouquet mapping unclear.
- Marble table decor — Orbz/topper mapping unclear.
- Butterfly GET WELL Bouquet, Bandage GET WELL Bouquet, Shooting star GET WELL Bouquet — simple-looking but plush add-ons need a clean decision first.

## Decision rule

A product is allowed into direct checkout only if all are true:

1. The customer can understand exactly what they are buying without a human design conversation.
2. Options are bounded and priced.
3. Delivery/pickup is standard enough for checkout.
4. Customer note cannot change scope/price/install requirements.
5. Backend verifier can prove the selected meaning survives into Sales Order / invoice / operator view.
6. GL/Jeff are comfortable with the image, price, and seasonal visibility.

If any one of those fails: quote-first, event-page example, or hide.

## Good status wording

> We are not trying to port the whole old catalog into checkout. We now have a real backend ecommerce foundation for a curated ready-to-order shelf. The first checkout shelf should be simple bouquet-style products only. Complex decor, high-option products, event installs, color-heavy builds, and uncertain add-on products stay quote-first or hidden until intentionally redesigned.

## Next no-port actions

1. GL/Jeff review the 15 candidate names only for taste/seasonality.
2. Choose the first public shelf: recommended default is the 13 bouquet-family products; hold Easter/Mother's Day unless timely.
3. Confirm product images/prices for that shelf.
4. Before treating the catalog as real, run a controlled purge/reupload/import proof that verifies schema fields, cascading logic, and automations using only products that fit this narrowed schema.
5. Keep all option-heavy decor quote-first.
6. Only after production/live payment gates pass, temporarily open checkout for that shelf and run one low-risk live payment test.
