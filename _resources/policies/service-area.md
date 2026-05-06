# Service Area, Pickup, and Delivery Fees

Confirmed by Odoo policy reference and Guiding Light on 2026-05-05.

## Ready-to-order checkout

- **Pickup:** free. Customer chooses West Jordan or Riverdale, then requests a date and 30-minute pickup window. The request is not confirmed until Locally Twisted follows up.
- **Standard Delivery:** $15 for the standard local delivery zone covering Davis, Weber, Salt Lake, and Utah counties.
- **Park City Delivery:** $50 for ZIP codes 84060, 84068, and 84098.
- **Out-of-area delivery:** quote required before payment. The checkout should not send these customers to Stripe; the customer should be sent to `/contact` with checkout details and cart items carried forward.

## Event and service quotes

Face painting, balloon twisting, corporate, school, civic, venue, and larger custom event work should start through `/contact`, not the cart. Delivery, setup, venue access, travel, timing, tax, deposit, and payment terms are handled on the quote.

Fixed-price products that are already in the cart should not become quote-only because of product group alone. The system-configured quote fallback for checkout is the fulfillment/delivery zone, especially ZIPs outside the configured delivery area.

## Why this matters

Customers need delivery cost and payment timing before they commit. Surprise delivery fees after checkout create distrust and should be avoided.

## How it lands in the build

- **Checkout:** detects pickup, standard delivery, Park City delivery, and out-of-area delivery by ZIP/city.
- **Out-of-area checkout:** routes the customer to `/contact` with cart contents, delivery address, requested timing, and contact details prefilled. Lead creation happens when the customer submits `/contact`; checkout must not create a Sales Order, Payment Request, Stripe session, or duplicate Lead for this branch.
- **Product pages:** fixed-price products remain cartable; custom event/service CTAs route to `/contact`.
- **Terms/FAQ/service pages:** repeat the same pickup/$15/$50/out-of-area quote model.
