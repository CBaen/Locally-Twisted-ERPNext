# 2026-05-24 Staging Owner-Review Recovery Decisions

Audience: peer Codex/GPT agents working the Locally Twisted staging and checkout
release path.

Status: current project-level decision packet. This packet exists because the
legacy decision log is already a monolith; do not expand it for these details.

## Decision 1 - Restart From The Trusted Restore Commit

The staging owner-review recovery is anchored to
`c668543 Restore trusted staging source`, then to the narrow follow-up commits
`273cb25`, `4d5c287`, `70b8869`, and `203127a`.

Future agents must treat older post-restore staging-failure commits as
historical archive unless a specific file or decision is reintroduced with
current proof.

Reasoning: GL explicitly approved the trusted restore point as the source to
move forward from. The recovery then made small staging fixes for mobile footer
columns, product gallery behavior, checkout product flow, and checkout
error-safety. Re-reading older failed attempts as authority was adding
confusion and risk.

Implementation boundary:

- Start future staging work from current `main` and the current Frappe app
  mirror.
- Verify the hosted staging URL before claiming owner-review state.
- Do not revive older staging prep artifacts as launch authority.
- Do not use the app mirror alone as source truth; compare full repo source,
  mirror commits, and hosted route proof.

## Decision 2 - Configured Checkout Resolves Priced ERPNext Variants Before Label Parsing

When a Product Setup option group represents real SKU-defining ERPNext
variants, checkout resolution must match the priced ERPNext variant attributes.
Stored/display labels with commas must not be split into fake option values
that block an otherwise valid configured product.

Reasoning: the hosted staging configured bouquet failed checkout with a generic
product setup review message even though the customer selection mapped to real
priced variants. The failure was caused by stale label parsing and resolution
behavior, not by customer choice or missing product setup.

Implementation boundary:

- This does not make arbitrary text selections checkout-safe.
- The resolver must still require a valid priced variant.
- Fail loudly when Product Setup, variant attributes, or prices do not match.
- Frontend controls submit configuration; ERPNext/backend variant and pricing
  truth remain authoritative.

## Decision 3 - Payment-Secret Proof Is Separate From Product/Cart Proof

Hosted staging is not owner card-test ready until staging payment
secrets/configuration decrypt and one authorized test-mode checkout proves the
ERPNext payment cascade. Passing product, gallery, cart, and checkout route
tests does not prove the Stripe provider handoff.

Reasoning: after the product setup blocker was repaired, final submit reached
the payment setup layer and failed because staging could not decrypt
`Stripe Settings.Test.secret_key`. This is a staging configuration failure and
must stay visible as such.

Implementation boundary:

- Repair staging payment configuration only in the staging context.
- Do not touch live payment settings from a staging repair.
- Do not print secrets.
- Do not expose raw provider/decryption text to customer UI.
- After config repair, rerun hosted route proof, backend payment contracts, and
  one authorized Stripe test-mode checkout before owner review.

## Receipts

- `workstreams/frappe-cloud-staging-owner-review-2026-05-24.md`
- `workstreams/mobile-footer-columns-staging-2026-05-24.md`
- `workstreams/ecommerce-audit/product-gallery-staging-followup-2026-05-24.md`
- `workstreams/ecommerce-audit/staging-checkout-product-flow-2026-05-24.md`
- `capabilities/failures/frappe-cloud-staging-stripe-secret-drift.md`
- `capabilities/recipes/frappe-cloud-cloudflare-stripe-launch-gate.md`
- `workstreams/payment-backend-launch-readiness.md`
- `CODING-HANDOFF.md`
- `ECOMMERCE-SHOP-HANDOFF.md`
