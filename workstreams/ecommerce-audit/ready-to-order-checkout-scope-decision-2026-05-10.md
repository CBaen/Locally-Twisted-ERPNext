D:2026-05-10 | Check:GL scope correction 2026-05-10 14:48 MDT + live legacy_source architecture witness | Confidence:high
# Ready-to-order checkout scope decision

## Decision

Locally Twisted should **not** try to launch all legacy_source-style configurable products as direct checkout products in ERPNext right now.

Launch checkout only for simple / ready-to-order products where:

- the customer can reasonably choose and buy without design consultation,
- the price is low enough and obvious enough for self-checkout,
- options are bounded and safe,
- fulfillment meaning can be preserved cleanly in backend records,
- payment/tax/delivery behavior is testable without operator interpretation.

Complex balloon decor, major variant products, corporate/event work, and high-dollar installations should route **quote-first / invoice-first**.

## GL rationale to preserve

- â€œEndless variants kills.â€
- Major configurable decor is usually an invoice/corporate/job-order path.
- Customers are not realistically going to self-checkout for ~$400+ balloon decor yet, especially not at the current company/system maturity.
- It is safer and more honest to collect intent, preserve details, and invoice after human/operator review than to pretend checkout can price and approve every custom build.

## Architecture impact

This narrows the ERPNext ecommerce receiving problem.

The launch target is no longer:

> recreate every legacy_source product option path as direct checkout.

The launch target is:

> prove a clean ready-to-order checkout lane, while preserving quote/invoice-first infrastructure for complex work.

## Checkout-eligible product rules

A product may be checkout-eligible only if all of these are true:

1. **Simple buying decision** â€” customer can understand and choose without back-and-forth.
2. **Bounded options** â€” no huge visual/design matrix required for safe purchase.
3. **Approved pricing** â€” base price and option prices are source-backed and operator-approved.
4. **Backend preservation** â€” selected options/custom text survive into cart/order/invoice/fulfillment fields.
5. **Delivery/tax/payment proof** â€” checkout path has backend evidence, not just visual proof.
6. **Fulfillment clarity** â€” operators know what to make/deliver from the backend record.
7. **No silent underpricing** â€” unapproved add-ons/customization route to quote, not free checkout.

## Quote/invoice-first rules

A product should be quote-first / invoice-first if any of these are true:

- many customer-choice variants would create combinatorial explosion,
- product depends on venue, install complexity, time, crew, weather, access, or corporate requirements,
- price is high enough that human review is expected,
- add-ons/design choices are not fully approved for direct checkout,
- customer text/design instructions meaningfully affect labor or materials,
- fulfillment requires internal planning rather than simple pick/build/deliver.

Quote-first is a success state, not a failure state.

## What we still need from legacy_source

For **ready-to-order checkout products**, we still need a narrow legacy_source witness slice:

- product identity and public category,
- base price and price list behavior,
- required/simple options,
- approved add-ons,
- custom text fields, if any,
- image/gallery expectations,
- cart/order-line preservation behavior,
- delivery eligibility,
- tax/payment boundary,
- operator fulfillment fields needed after purchase.

For **complex decor / major variant products**, we do not need exhaustive direct-checkout parity right now. We only need enough legacy_source evidence to route them safely:

- product page exists,
- why it is quote-first/invoice-first,
- what customer intent must be captured,
- what operator fields/quote payload must preserve.

## ERPNext implementation instruction

1. Add/verify a checkout eligibility classification on Website Item / product page contract.
2. Keep complex products visible as request-a-quote / invoice-first pages where appropriate.
3. Direct checkout only for approved ready-to-order products.
4. Do not build endless variant matrices to satisfy ecommerce completeness.
5. Add verifier gates that prove complex products cannot accidentally enter paid checkout.
6. Add verifier gates that prove ready-to-order products preserve selected intent through checkout backend records.

## Event pages vs shop split â€” GL correction at 2026-05-10 14:53 MDT

High-ticket decor belongs on the event/audience pages as **examples and inspiration**, not as direct checkout products.

Event-page customers are browsing for proof, taste, scale, and fit. They expect planning, quoting, and invoicing when custom sizing, delivery, install, venue coordination, or corporate approval is involved.

Current event-planning framing to preserve:

> Event planning
> Built for Utah gatherings that need to look ready.
> Browse by event setting, then use the quote path when the install needs custom sizing, delivery, or venue coordination.

Audience lanes:

- Civic & Community â€” city, county, chamber, Pride, and public-facing community installs.
- Corporate Events â€” brand-safe decor for launches, offices, media events, restaurants, and customer activations.
- Schools & Campuses â€” graduations, assemblies, athletics, dances, family nights, and campus moments.
- Private Celebrations â€” birthdays, weddings, showers, memorials, venues, and family milestones.

Footer rule:

> Custom decor, delivery, and install questions belong in the quote request. Start a quote.

The shop should carry simple products with low variation. The event pages carry high-ticket examples and route to quote/invoice.

## Customer note rule

Even checkout-ready products should allow a customer note.

This is not the same as opening arbitrary custom design checkout. The note is a communication field for preferences, event date, delivery details, small context, or â€œanything we should know.â€ It must be preserved in backend order records and operator view.

Implementation posture:

- Ready-to-order checkout may accept an optional order/customer note.
- A note must not silently change price, scope, or approve custom work.
- Notes that imply custom sizing/install/venue coordination should be operator-reviewed or redirected to quote-first language.
- Backend evidence must prove the note survives checkout into Sales Order/payment/fulfillment records.

Current ERPNext code already has checkout-level `order_notes` UI and Sales Order timeline transfer logic; this should be verified in the ready-to-order candidate proof, not assumed.

## Immediate next action

Create a ready-to-order product candidate list from legacy_source/ERPNext and classify each candidate as:

- `checkout_ready_now`,
- `checkout_ready_after_small_fix`,
- `quote_first`,
- `hide_or_needs_review`.

This candidate list should become the next launch-scope artifact before product import/reopen decisions.
