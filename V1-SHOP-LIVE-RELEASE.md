# V1 Shop Live Release

Recorded: 2026-06-10
Live verification window: 2026-06-09 evening MDT

## Release State

Locally Twisted's new Frappe/ERPNext website is live at:

- `https://locallytwisted.com`
- `https://www.locallytwisted.com`

The V1 ready-to-order ecommerce shop is live with guest checkout and Stripe Live payments enabled.

## Verified Live Proof

- Public site and shop routes returned successfully from the live domain.
- Guest checkout created a live Sales Order and Stripe Checkout session.
- A real Stripe Live payment completed.
- Customer return URL reached `https://locallytwisted.com/thank-you?order=SAL-ORD-2026-00043`.
- The thank-you page showed `Payment Received`, order `SAL-ORD-2026-00043`, `Easter Balloon Cups-FLO x 1`, and `$13.97 USD`.
- ERPNext marked Sales Order `SAL-ORD-2026-00043` as submitted and fully billed.
- ERPNext marked Payment Request `ACC-PRQ-2026-00040` as `Paid` with `$0.00` outstanding.
- Outbound email sending was repaired after a migrated Email Account password decrypt failure.
- Default outgoing email now sends as `Locally Twisted <accounting@locallytwisted.com>` using the configured Gmail SMTP login.
- A synthetic live proof email tied to `SAL-ORD-2026-00043` was queued and sent:
  - subject prefix: `SMOKESCREEN`
  - Email Queue: `1b86o9shkq`
  - sender: `Locally Twisted <accounting@locallytwisted.com>`
  - status: `Sent`
  - error: `null`

## Operational Notes

- The original order receipt/operator queues for `SAL-ORD-2026-00043` are currently `Sent`.
- Their historical `error` field still contains the first failed decrypt traceback from before the email-account repair. Treat that field as historical evidence, not current queue state.
- No card details are stored in this repo.
- Live provider/site settings changed during launch are operational state, not fixtures. Do not overwrite live Email Account, Stripe, DNS, or domain settings from stale local data.

## Go-Live Meaning

This commit marks the source-repo checkpoint for the V1 shop live release: public website, live ecommerce, live Stripe payment, ERPNext paid-order reconciliation, and live outbound email proof.
