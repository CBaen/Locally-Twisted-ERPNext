# Service Area, Pickup, and Delivery Fees

Confirmed by Odoo policy reference and Guiding Light on 2026-05-05.

## Ready-to-order checkout

- **Pickup:** free. Customer chooses West Jordan or Riverdale, then requests a date and 30-minute pickup window. The request is not confirmed until Locally Twisted follows up.
- **Standard Delivery:** $15 for the standard local delivery zone covering Davis, Weber, Salt Lake, and Utah counties.
- **Park City Delivery:** $50 for ZIP codes 84060, 84068, and 84098.
- **Out-of-area delivery:** quote required before payment. The checkout should not send these customers to Stripe.

## Event and service quotes

Custom decor, installs, face painting, balloon twisting, corporate, school, civic, venue, and larger event work should start through `/contact`, not the cart. Delivery, setup, venue access, travel, timing, tax, deposit, and payment terms are handled on the quote.

## Why this matters

Customers need delivery cost and payment timing before they commit. Surprise delivery fees after checkout create distrust and should be avoided.

## How it lands in the build

- **Checkout:** detects pickup, standard delivery, Park City delivery, and out-of-area delivery by ZIP/city.
- **Out-of-area checkout:** creates a CRM Lead with the cart contents and customer details instead of creating a Sales Order or Stripe session.
- **Product pages:** retail products explain pickup/delivery; quote-lane products route to `/contact`.
- **Terms/FAQ/service pages:** repeat the same pickup/$15/$50/out-of-area quote model.
