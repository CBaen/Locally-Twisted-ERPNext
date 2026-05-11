D:2026-05-10 | Check:GL 14:53 merchandising correction + current navbar/event-page code + Odoo research | Confidence:high
# Event pages vs ready-to-order shop contract

## Decision

High-ticket balloon decor belongs on event/audience pages as examples, proof, and inspiration.

Ready-to-order shop belongs to simple, low-variation products that a customer can buy without planning a full event install.

## Why

Odoo showed that Locally Twisted has enough configuration depth to drown checkout in variants and options. That does not mean ERPNext should expose all of that as direct purchase.

GL correction:

- high-ticket items are already represented by event pages,
- people browsing those pages want examples and confidence,
- they understand custom decor needs planning and invoicing,
- major variants and install work should not be forced into checkout,
- simple products should stay low-variation,
- customers should still be able to leave a note.

## Public IA contract

### Event Balloons / Event Planning

Purpose: show examples, scale, proof, taste, event/audience fit, and route to quote.

Current framing to preserve:

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

### Ready-to-Order shop

Purpose: sell bounded products that are safe for self-checkout.

Allowed posture:

- simple pickup/delivery products,
- low variation,
- clear price,
- clear fulfillment path,
- optional customer note,
- fail-loud if custom work is implied.

Disallowed posture:

- high-ticket decor sold as if it were a simple SKU,
- endless variant matrices,
- unpriced add-ons,
- venue/install coordination hidden inside checkout,
- customer notes that silently change scope.

## Customer note rule

Every ready-to-order checkout should allow a note, but the note is communication, not pricing authority.

Examples of safe note intent:

- preferred delivery window,
- event date/context,
- color preference when already allowed,
- recipient/location details,
- â€œanything we should know.â€

Examples that should push operator review / quote language:

- custom sizing,
- install request,
- venue access/rigging,
- corporate invoicing/PO constraints,
- complex theme/design direction,
- major material/labor changes.

## Backend proof required

Before claiming the shop is launch-ready:

1. A ready-to-order item can be bought with no note.
2. A ready-to-order item can be bought with a customer note.
3. The note is preserved in backend Sales Order/payment/fulfillment evidence.
4. Complex event products route quote-first and cannot accidentally enter direct checkout.
5. Event pages show examples and quote CTAs rather than pretending to be product checkout pages.

## Implementation note

Current code already contains:

- Event megamenu copy matching the event-planning framing in `templates/includes/navbar/navbar.html`.
- Event audience pages for Civic, Corporate, Schools, and Private Celebration routes.
- Checkout-level `order_notes` field and Sales Order timeline transfer logic in `www/checkout.html` / `www/checkout.py`.

These are good bones. Next work should verify them end-to-end instead of expanding checkout scope.
