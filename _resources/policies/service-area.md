# Service Area & Travel Fees

Confirmed by Jeff Kimber 2026-04-16.

## Free service area (no travel fee)

- Davis County
- Weber County
- Salt Lake County
- Utah County

These are the four counties along the Wasatch Front where Locally Twisted delivers without an additional travel charge.

## Travel fee applies

- Any location **outside** these four counties gets a travel fee
- **Travel fee amount: not yet set** — currently negotiated case-by-case until Jeff sets a flat rate or per-mile

## Why this matters

Customers who book from the website need to see this upfront. Surprise travel fees at invoice time = lost trust.

## How it lands in the build

- **Booking form address field:** detect county on zip code entry, warn if outside service area
- **Service page copy:** "Free delivery in Davis, Weber, Salt Lake, and Utah counties. Events outside these counties: travel fee applies — contact us for a quote."
- **Quote sheet:** travel fee as a visible line item when applicable
- **Tagline copy:** "Happily delivering along the Wasatch Front" stays — accurate to the free zone
