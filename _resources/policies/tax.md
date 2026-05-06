# Tax Rules — Utah Sales Tax

Confirmed by Jeff Kimber 2026-04-16.

## How tax appears on orders

- **Tax is added at checkout for ready-to-order shop orders** and on the quote or invoice for event services
- **Location-based auto-calculation** — the system calculates based on delivery, pickup, or event city
- Utah combined rate is typically **~7.25%** (state 4.85% + local county / city add-ons)

## Open item — sales tax classification for SERVICES

Sales tax classification for SERVICES (twisting, face painting) is **still an open question**. Needs either a Utah Tax Commission ruling or CPA consultation before launch. Currently treated as taxable to be safe; revisit before going live.

## Reference: Utah tax data

The detailed Utah tax research and per-jurisdiction rate data lives at `_resources/utah-tax-rates-2026q2.md`.

## Why this matters

Pricing copy on the website must show when tax is added so customers aren't surprised. Checkout and quote views should show the subtotal clearly and note that tax is added.

## How it lands in the build

- **Pricing calculator:** show subtotal, annotate "+ Utah sales tax"
- **Invoice line items:** tax as its own visible line
- **Location-based tax map:** the new system applies the right rate per delivery, pickup, or event city
- **QuickBooks transition:** Jeff currently enters orders manually in QB and picks a city tax rate per order. The new system replaces this — auto-calc removes the manual step and the error rate that comes with it.
