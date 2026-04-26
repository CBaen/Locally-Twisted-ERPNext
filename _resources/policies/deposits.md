# Deposit Rules

Confirmed by Jeff Kimber 2026-04-16. Cancellation policy resolved in legal interview 2026-04-23 (see `legal-interview-answers.md` Part 2C).

## Artist services (twisting, face painting)

- **Deposit:** $50 per artist at time of booking
- **Balance due:** 72 hours before the event
- Example: 2 artists = $100 deposit, balance of (total - $100) due 72h pre-event
- Deposit collected via Stripe link in invoice email

## Personal balloon decor (arches, columns, big installs)

- **100% upfront** — NOT a deposit split; full payment required before prep starts

## Personal small deliveries (bouquets, cups, under $100 website products)

- **100% upfront at time of order**

## Corporate clients (any service)

- **No deposit**
- **Net 30** invoicing — they can pay sooner
- Invoice sent on delivery / event completion
- **Late fee:** 10% simple (never compounded) on original balance; clock starts day 31. "May waive" language gives Jeff discretion.

## Why this matters

- Deposits + balance dates need to appear on the **Terms page**, the **booking confirmation email**, and **before** customers commit on the booking form. Customers ask before booking, not after.
- Cancellation rules tied to deposits are in `legal-interview-answers.md` Part 2C — both files together cover the customer-facing policy story.

## How it lands in the build

- Booking form collects deposit before event is locked in
- Balance-due reminder email auto-sends 72h before event for artist services
- Quote sheets show deposit + balance + due dates explicitly
- Refund policy page on the customer site mirrors the legal-interview-answers.md cancellation rules in plain language
