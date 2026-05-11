D:2026-05-10 | Check:parent-run Phase 1-5 gates 2026-05-10 | Confidence:[LOCAL-PROOF]
# Phase 6 — Ecommerce launch decision packet

## Decision

Do **not** open public/live checkout yet.

The ready-to-order ecommerce architecture and local proof stack are complete through Phase 5, but live checkout remains intentionally blocked by launch authority/access gates: production host, explicit live Stripe configuration, owner/legal policy approval, webhook setup, and one intentional low-risk real payment test.

The safe current launch posture remains pages/forms-first with `lt_ecommerce_paused=1`.

## What is complete

- Phase 1 — Verifier foundation: PASS.
- Phase 2 — Website Item classification: PASS / applied.
- Phase 3 — First ready-to-order checkout family proof: PASS / scoped.
- Phase 4 — Quote/event checkout boundary hardening: PASS / scoped.
- Phase 5 — Delivery/payment/operator packet: PASS locally.

## What remains blocked

- Public ecommerce reopen: blocked by `lt_ecommerce_paused=1`, intentionally.
- Live Stripe: blocked by test-mode Stripe settings and missing explicit live site-config keys.
- Production host proof: blocked locally by `host_name: http://localhost:8081`; live mode requires HTTPS production host.
- Real payment success claim: blocked until one intentional real checkout is run in the intended environment and audited.

## Safe wording

Use this externally/internal-handoff wording:

> Ready-to-order ecommerce is locally architecture-complete and verifier-backed through delivery, payment backend, and operator controls. Public checkout remains paused until production Stripe, HTTPS host, webhook, policy, and one real payment test are approved and pass.

Do **not** say:

- "Live checkout is ready."
- "Payments are live."
- "The shop can be opened now."
- "All products are checkout-ready."

## Cutover checklist

1. Keep `lt_ecommerce_paused=1` for pages/forms-first launch unless GL/Jeff explicitly reopen checkout.
2. Configure production Frappe host and HTTPS `host_name`.
3. Configure live Stripe Settings, Payment Gateway Account, Stripe payment method configuration, webhook signing secret, and operator email via explicit site config.
4. Confirm public policy URLs with owner/legal approval.
5. Run `python scripts/verify/payment_launch_readiness.py --mode live --base-url https://locallytwisted.com`.
6. Temporarily open only the intended checkout tranche.
7. Run one low-risk live checkout and verify ERPNext Sales Order, Payment Request, Payment Entry, Sales Invoice, receipt email queue, operator email queue, and checkout-note preservation.
8. Refund the test payment if appropriate.
9. Restore or keep pause if any live gate fails.

## Final local verifier posture

- Ecommerce pause: PASS.
- Product-page technical architecture: PASS.
- Public reopen/import readiness: BLOCKED only because ecommerce is intentionally paused.
- Delivery/payment/operator proof: PASS locally.
- Live payment launch readiness: FAIL expected cutover blockers.

Conclusion: local ecommerce implementation is finished to the safe non-live boundary; live launch is an owner/access cutover, not a remaining local architecture task.
