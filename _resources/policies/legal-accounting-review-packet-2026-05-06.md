# Legal and Accounting Review Packet - 2026-05-06

Purpose: give Jeff, legal counsel, and accounting/CPA one reviewable summary of the current Locally Twisted public policy and checkout-rule decisions before Stripe/live launch claims.

Status: business-approved by Guiding Light as proxy on 2026-05-06. Not attorney-approved or CPA-approved yet.

Primary live routes:

- `/terms-of-service`
- `/privacy`
- `/refund-policy`
- `/faq`
- `/balloon-twisting-and-face-painting`
- `/checkout`

Primary source files:

- `_resources/policies/legal-interview-answers.md`
- `_resources/policies/deposits.md`
- `_resources/policies/service-area.md`
- `_resources/policies/tax.md`
- `_resources/policies/pricing-formula.md`
- `workstreams/policy-trust.md`
- `locally-twisted-decisions.md`

## Executive Summary

Locally Twisted is not a pure ecommerce business. The public site supports two lanes:

- Ready-to-order products: cart/checkout, pickup or delivery, payment before fulfillment.
- Event/service work: quote/contact-led, with deposit/payment guidance and event-specific terms.

The checkout code now selects the Utah sales-tax rate from the pickup/delivery location but applies that rate only to taxable goods. Services, face painting, balloon twisting, service deposits, and delivery charges are treated as non-taxable under the current business rule. Public copy avoids saying service tax is added.

Delivery policy remains in Terms/FAQ, not a standalone shipping page. A sitewide cookie/tracking notice exists because launch expects analytics/ads/tracking plus cart/session storage.

## Legal Review Items

### Terms of Service

Current business-approved positions:

- Form submission does not confirm a booking.
- Booking is confirmed when Locally Twisted accepts the job and required payment/deposit is complete.
- For jobs requiring a contract, invoice payment is treated as acceptance of booking terms unless a separate written agreement says otherwise.
- Pickup dates, delivery dates, and 30-minute windows are requested until Locally Twisted confirms them.
- If Locally Twisted cannot complete pickup, delivery, or setup because the on-site contact cannot be reached or access information is wrong, the customer remains responsible for the order and delivery charges.
- Ready-to-order balloon products are not returnable once prepared, delivered, or picked up.
- Delivered product damage must be reported the same day.
- Balloon decor and live services are temporary and can be affected by weather, heat, cold, wind, sunlight, altitude, venue conditions, handling, intended use, guest interaction, interference, third-party movement, and changes after setup.

Legal questions:

- Is invoice payment as acceptance enforceable enough for MVP, especially for larger event/corporate work?
- Should larger event/corporate work require a separate click-through or signed event contract before payment?
- Is the no-access/no-contact responsibility language strong enough?
- Should the temporary-material/event-condition language include a clearer liability cap or warranty disclaimer?
- Should dispute venue, arbitration, class-action waiver, or limitation-of-liability clauses be added before launch?

### Refund and Cancellation

Current business-approved positions:

- Face painting and balloon twisting:
  - 7+ days before event: deposit transfers to a new date; no refund.
  - 72 hours to 7 days before event: deposit transfers to a new date; no refund.
  - Less than 72 hours before event: deposit is forfeited unless Locally Twisted makes a case-by-case exception.
- Balloon decor:
  - 14+ days before event: full refund.
  - 7 to 14 days before event: full refund.
  - Less than 7 days before event: no cash refund; funds paid transfer to another event date or product.
- Transferred funds must be used within 6 months of the original event date.
- If Locally Twisted cancels: full refund plus goodwill gesture.
- If weather affects an event once setup/service is already underway: no partial refund obligation.
- Corporate cancellation is relationship-driven; no standard late cancellation fee for consistent clients.

Legal questions:

- Is the less-than-7-days decor transfer/no-refund rule clear enough?
- Should the policy preserve any materials-cost deduction language, or does the transfer/no-refund rule replace it?
- Should goodwill language for Locally Twisted cancellation stay public, or move into internal/customer-service discretion?
- Should weather language distinguish outdoor decor, artist services, and customer-requested continuation?

### Delivery and Returns

Current business-approved positions:

- Pickup is free.
- Standard local delivery is `$15` for Davis, Weber, Salt Lake, and Utah counties.
- Park City delivery is `$50` for ZIP codes `84060`, `84068`, and `84098`.
- Out-of-area delivery is available for quote.
- Checkout should not take payment for out-of-area delivery; it should send the customer to `/contact` with cart/request details.
- Ready-to-order products have no returns once prepared, delivered, or picked up.
- Damage reports must happen the same day.

Legal questions:

- Is it acceptable to keep delivery policy inside Terms/FAQ rather than a standalone shipping page?
- Does the no-return rule need exceptions for legal compliance, product defect, failed delivery, or order error?
- Is same-day damage reporting reasonable and enforceable for delivered balloon products?

### Photos, Inspiration Uploads, and Marketing Use

Current business-approved positions:

- Customer-uploaded inspiration photos are used to plan the event.
- Event photos use an opt-out release model, not opt-in.
- Unless the customer opts out in writing before or during the event, Locally Twisted may use:
  - photos/video taken by Locally Twisted staff or representatives;
  - public photos, reviews, or social posts about the event that Locally Twisted can access.
- Allowed uses: website, portfolio, social media, advertising, and marketing.

Legal questions:

- Is the opt-out release enforceable for customer/event photos?
- Should identifiable minors, private venues, corporate events, schools, or public/civic events have separate release handling?
- Should the event contract have a more explicit photo-release section than the website Terms?
- Does use of public social/review photos require additional attribution, platform-specific compliance, or separate consent?

### Privacy and Cookies

Current business-approved positions:

- Privacy contact remains `hi@locallytwisted.com`.
- The site collects contact details, event details, inspiration photos, cart/order/payment status, newsletter details, and website activity.
- The site may use cookies, pixels, local browser storage, analytics, advertising, tracking, marketing measurement, retargeting, cart/session storage, and preference storage.
- The site is intended for adults arranging orders/events.
- Locally Twisted does not knowingly collect personal information directly from children under 13; adults should submit forms, checkout orders, and contact requests.
- A cookie/tracking notice stores `lt_cookie_consent` as `accepted` or `declined`.

Legal questions:

- Is the current privacy copy enough for Utah/US launch, or should it include more formal consumer-rights language?
- Does analytics/ads/tracking require a fuller cookie policy or consent-management behavior?
- Should optional trackers be blocked until `lt_cookie_consent` is accepted? The technical hook exists and future trackers should honor it.
- Is the children-under-13 language sufficient for a site that may serve birthday-event customers but expects adults to submit information?

## Accounting/CPA Review Items

### Sales Tax

Current business-approved and locally verified checkout behavior:

- Utah tax rate is selected by pickup/delivery location.
- Tax applies only to taxable goods.
- Face painting is non-taxable.
- Balloon twisting is non-taxable.
- Deposits for those services are non-taxable.
- Delivery charges are non-taxable.
- Ready-to-order product checkout shows estimated tax before payment.
- Service/event quote copy shows service total, deposit, balance timing, and event-specific fees without adding service-tax language.

Accounting questions:

- Is the goods-only taxable base correct for Locally Twisted's product/service mix?
- Are delivery charges non-taxable in this exact business context?
- Should any productized event decor, installation, or bundled goods/service package be treated differently?
- Should ERPNext item groups or item tax templates be reviewed before live launch?
- Is the current location-rate data sufficient for launch, or should CPA/accountant confirm the current Utah jurisdiction rates?

### Payment Timing

Current business-approved positions:

- Personal face painting / balloon twisting: `$50` per artist deposit; balance due 72 hours before event.
- Personal balloon decor: 100% upfront before prep starts.
- Small ready-to-order deliveries under `$100`: 100% upfront at order.
- Corporate clients: no deposit; Net 30 after event.
- Corporate late fee: may add 10% simple late fee on original balance after Net 30; may waive case by case.

Accounting questions:

- Should deposits be posted as liabilities/deferred revenue until event completion?
- Should transferred funds for canceled decor jobs be tracked as credit, liability, gift-credit style balance, or a tagged customer credit?
- Should the 10% late fee require a specific ERPNext item/account?

## Technical Evidence Already Run

These checks passed during the policy/trust implementation pass:

- `node --check apps\locally_twisted\locally_twisted\public\js\lt-site-preferences.js`
- `python scripts\verify\commerce_rules_contract.py`
- `python scripts\verify\checkout_fulfillment_contract.py`
- `python scripts\verify\cart_checkout_contract.py`
- Route checks returned `200` for `/privacy`, `/terms-of-service`, `/refund-policy`, `/faq`, `/balloon-twisting-and-face-painting`, and `/checkout`.
- Cookie script is included live and the asset returns `200`.
- Layout coverage passed in split Playwright batches: `78 + 104 + 65 + 13 = 260/260`.
- Targeted desktop/mobile browser check passed for cookie banner visibility, no horizontal overflow, decline storage, and reload persistence.

## Known Non-Review Blockers

- Proof of insurance / COI PDF is still outside this packet; Jeff or the business owner must obtain it.
- Stripe Dashboard policy URLs should not be treated as final until legal/accounting review is complete.
- Future analytics/ads/tracking code must honor `window.LT_COOKIE_CONSENT.hasAcceptedOptional()` before optional trackers load.
- This packet summarizes current public copy and business rules; it does not replace an attorney-drafted Client Event Contract.
