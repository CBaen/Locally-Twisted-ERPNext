# Staging Shop Audit Master List - 2026-05-29

Status: current master list recovered from the May 29 staging checkout audit
conversation and promoted to a durable workstream record after item 4 approval.

This is the shop staging audit list for the staged customer purchase process.
It is not live checkout approval, staging deployment approval, provider-change
approval, DNS approval, Search Console approval, live Stripe approval, product
data approval, or remediation approval.

## Why This File Exists

After context compaction, the audit items were visible only through scattered
conversation state, coordination notes, and individual item handoffs. That made
it too easy for an agent to forget the master list, invent a new list, or ask
Guiding Light to re-explain it.

This file is the durable front door for the item sequence.

## Master Item Count

There are currently `5` items on the shop staging audit list.

Items `1` through `4` are approved complete for staging test-mode proof only.
Item `5` has an executed release/no-go packet. The packet recommendation is
`BLOCKED/NO-GO` for staging release execution unless Guiding Light explicitly
approves the named evidence deferrals.

## Item List

| Item | Status | Plain-English Purpose | Durable Evidence |
|---|---|---|---|
| 1. Receipt and internal email delivery | Approved complete by Guiding Light | Prove paid staging purchases send the customer receipt and internal order email, and that the important links work. This included the staging scheduler/email reliability issue. | Current-session proof and `capabilities/failures/frappe-cloud-staging-email-secret-drift.md`; future agents should not treat Email Queue rows as inbox proof without receipt/link confirmation. |
| 2. Penny parity | Approved complete by Guiding Light | Fix and prove the checkout preview total matches the final Sales Order, Stripe test amount, thank-you page, receipt, and internal notification to the cent. | `staging-checkout-penny-parity-2026-05-29.md` |
| 3. Product diversity | Approved complete by Guiding Light after triad `PASS WITH NOTES` | Prove staging checkout handles different product types: pickup, delivery-only, mixed carts, variants, approved foil-number add-ons, and quote-first bypass prevention. | `staging-checkout-product-diversity-item-3-2026-05-29.md` |
| 4. Internal processing | Approved complete by Guiding Light after triad `PASS WITH NOTES` | Prove the internal ERPNext trail after paid checkout: Sales Order, Payment Request, Payment Entry, Sales Invoice, Customer/Contact, Email Queue, Communication, notes, fulfillment, errors, and duplicates. | `staging-checkout-internal-processing-item-4-proof-2026-05-29.md` |
| 5. Combined staging release/no-go packet | Packet complete; release execution `BLOCKED/NO-GO` unless named deferrals are approved | Build the business-readable packet for the one larger staging push/review decision: exact commits included, what changed for customers/operators, proof required, what is excluded, stop conditions, and rollback path. | `staging-shop-audit-item-5-release-no-go-packet-2026-05-29.md` |

## Current Boundary

The first four items prove staging test-mode behavior only. They do not approve:

- live checkout;
- staging deployment or another Frappe Cloud pull;
- provider dashboard changes;
- DNS or Search Console changes;
- live Stripe;
- product data mutation;
- remediation discovered during proof.

Item 5 must keep those exclusions unless Guiding Light explicitly changes the
boundary.

## Item 5 Scoping Prompt

Before executing item 5, ask for approval using this kind of boundary:

> I approve item 5 scope for a staging release/no-go packet only. This does not
> approve live checkout, staging deployment, provider changes, DNS, Search
> Console, live Stripe, product data changes, or remediation work found during
> item 5.

Item 5 produced a decision packet and did not perform the staging push. The
scope is `staging-shop-audit-item-5-release-no-go-scope-2026-05-29.md`; the
packet is `staging-shop-audit-item-5-release-no-go-packet-2026-05-29.md`.
