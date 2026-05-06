# Tax Rules - Utah Sales Tax

Confirmed by Jeff Kimber 2026-04-16; updated by Guiding Light business proxy 2026-05-06.

## How tax appears on orders

- **Tax is estimated at checkout for taxable ready-to-order goods.**
- **Location-based rate selection** - the system selects the Utah rate based on delivery or pickup location.
- **Taxable base is separate from location** - the selected rate applies only to taxable goods.
- **Services, face painting, balloon twisting, service deposits, and delivery charges are non-taxable under the current LT business rule.**
- Utah combined rate is typically **~7.25%** (state 4.85% + local county / city add-ons), but the exact rate depends on the pickup or delivery location.

## Services and deposits

Do not add service sales-tax wording to public service pricing pages. Customer-facing copy should show the service total, deposit, balance timing, and event-specific fees without claiming a service tax line.

Legal/accounting review is still appropriate before live tax-policy claims, but the active checkout contract follows the current business rule: only goods are taxable.

## Reference: Utah tax data

The detailed Utah tax research and per-jurisdiction rate data lives at `_resources/utah-tax-rates-2026q2.md`.

## Why this matters

Pricing copy on the website must not surprise customers. Checkout should show product subtotal, delivery fee, estimated tax on taxable goods, and total before payment. Service quotes should show service total, deposit, balance timing, and any event-specific fees.

## How it lands in the build

- **Pricing calculator:** for goods, show subtotal and estimated Utah sales tax; for services, show service total and payment timing.
- **Invoice line items:** tax as its own visible line only where tax applies.
- **Location-based tax map:** the new system applies the right rate per delivery or pickup location, then applies that rate only to taxable goods.
- **QuickBooks transition:** Jeff currently enters orders manually in QB and picks a city tax rate per order. The new system replaces this - auto-calc removes the manual step and the error rate that comes with it.
