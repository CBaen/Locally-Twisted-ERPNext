# Tax Rules — Utah Sales Tax

Confirmed by Jeff Kimber 2026-04-16.

## How tax appears on orders

- **Tax is added at checkout**, NOT baked into quoted prices
- **City-based auto-calculation** — the system calculates based on delivery / event city
- Utah combined rate is typically **~7.25%** (state 4.85% + local county / city add-ons)

## Open item — sales tax classification for SERVICES

Sales tax classification for SERVICES (twisting, face painting) is **still an open question**. Needs either a Utah Tax Commission ruling or CPA consultation before launch. Currently treated as taxable to be safe; revisit before going live.

## Reference: Utah tax data

The detailed Utah tax research and per-jurisdiction rate data lives at `_resources/utah-tax-rates-2026q2.md` (to be copied during the move; until then, the source is the prior project's research folder).

## Why this matters

Pricing copy on the website must show "tax calculated at checkout" so customers aren't surprised. The pricing calculator should show the subtotal clearly and note that tax is added.

## How it lands in the build

- **Pricing calculator:** show subtotal, annotate "+ Utah sales tax (calculated at checkout)"
- **Invoice line items:** tax as its own visible line
- **City-based tax map:** the new system applies the right rate per delivery / event city
- **QuickBooks transition:** Jeff currently enters orders manually in QB and picks a city tax rate per order. The new system replaces this — auto-calc removes the manual step and the error rate that comes with it.
