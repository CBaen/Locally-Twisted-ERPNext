# Ecommerce System Safety Guard Plan - 2026-05-19

Status: active coordination plan  
Owner: Codex controller with five GPT-5.5 worker lanes  
Scope: local repo and local ERPNext site only until GL explicitly approves staging/live  
Non-goals: live deploy, DNS changes, Stripe live payment, destructive catalog import

## Why This Exists

The variant price incident was not an isolated product bug. It exposed a
proof mismatch: tests and handoffs were proving that products existed or
checkout rendered, while the business needed proof that the correct product,
option, price, image, cart line, payment, ERPNext record, receipt, and owner
email all stayed tied together.

This plan turns that failure into executable guardrails before ecommerce is
opened publicly.

## Current Status

Integrated locally on 2026-05-19 with five GPT-5.5 worker lanes. No staging,
live, Frappe Cloud, DNS, Stripe live payment, destructive import, or secret
access was performed.

Resolved in this track:

- `scripts/verify/smoke_shop.py` no longer forces `7' Butterfly Column` into
  checkout navigation when the backend marks it `quote_first`.
- `scripts/verify/cart_checkout_contract.py` now uses a checkout-approved
  configured graduation product for checkout proof and separately proves
  `7-butterfly-column-REF` fails as quote-required.
- `scripts/verify/product_import_readiness_gate.py` remains read-only and no
  longer prints an apparently runnable destructive import command when blocked.
- `/thank-you?order=<Sales Order>` now derives paid/pending copy from ERPNext
  payment/invoice state before showing order details.
- Public guest endpoints and production `ignore_permissions=True` use now have
  source-only inventory/lint verifiers.

Remaining hard stops:

- `scripts/verify/product_import_readiness_gate.py` still blocks final
  destructive import because explicit approval has not been renewed for the
  2026-05-19 snapshot, backup, dry-run, and guard-path packet.

## Safety Rules

- Work on `main` only.
- Local-only until GL explicitly approves a target-site release step.
- No live deploy or Frappe Cloud site update.
- No destructive import or catalog purge.
- No Stripe live payment.
- No secret reads.
- Backend-first: ERPNext/Frappe source records, product classification, prices,
  media, cart payloads, Sales Orders, payment records, receipts, and owner
  notifications are the truth chain. Frontend rendering is proof only after it
  matches that backend chain.
- Each lane owns a disjoint file set unless the controller explicitly
  integrates changes.
- A green launch umbrella command is not enough; each critical chain needs its
  own receipt.

## Worker Lanes

### Lane 1 - Product Classification And Cart Contract

Goal: make product classification the shared authority for nav/search/cart/
checkout tests.

Owned files:
- `scripts/verify/smoke_shop.py`
- `scripts/verify/cart_checkout_contract.py`
- optional focused verifier/helper files under `scripts/verify/`

Required outcome:
- checkout tests use checkout-approved products only;
- quote-first products get a separate proof that direct cart/checkout fails
  with customer-safe copy;
- no test should force a quote-first product back into checkout just to pass.

### Lane 2 - Source Price And Import Guard Fail-Closed Behavior

Goal: make source-price proof runnable and make blocked destructive commands
impossible to misread.

Owned files:
- `scripts/verify/product_price_modifier_contract.py`
- `scripts/verify/product_import_readiness_gate.py`
- optional helper/preflight under `scripts/verify/` or `scripts/setup/`

Required outcome:
- source-price verifier clearly stages or requires source data before
  container execution;
- blocked import readiness reports do not print unblocked destructive commands;
- broad price proof cannot be claimed when source packet access failed.

### Lane 3 - Payment State And Thank-You Gate

Goal: prevent fake payment success before checkout is public.

Owned files:
- `apps/locally_twisted/locally_twisted/www/thank_you.py`
- `apps/locally_twisted/locally_twisted/www/payment_success.py`
- `apps/locally_twisted/locally_twisted/payments/stripe_webhook.py`
- matching payment verifiers under `scripts/verify/` or
  `apps/locally_twisted/locally_twisted/verify/`

Required outcome:
- `/thank-you` only shows confirmed-payment language when paid state is proven;
- pending or incomplete reconciliation shows customer-safe pending language;
- Stripe paid events compare amount/currency/metadata against ERPNext records
  before marking paid.

### Lane 4 - Public API And Permission-Bypass Inventory

Goal: turn guest APIs and `ignore_permissions=True` usage into auditable
surfaces instead of trusted-by-memory surfaces.

Owned files:
- new `scripts/verify/allow_guest_surface_inventory.py`
- new `scripts/verify/ignore_permissions_justification_lint.py`
- optional docs under `workstreams/` if needed

Required outcome:
- every public guest endpoint is inventoried with its expected guard type;
- every production `ignore_permissions=True` call has a nearby reason or is
  reported by the lint;
- verifiers fail loudly when new public mutation surfaces are added without a
  declared guard.

### Lane 5 - Documentation And Release Receipt Matrix

Goal: keep the plan, queue, and handoff aligned with the executable gates.

Owned files:
- this workstream file
- `locally-twisted-queue.md`
- `CODING-HANDOFF.md`
- relevant focused failure/capability docs only after code proof exists

Required outcome:
- queue names this P0 track clearly;
- handoff records verified, unverified, and blocked states;
- release cannot be described as ready without separate receipts for product
  classification, source price, visible price, media, cart/checkout, payment,
  receipt/email, API guard, and docs parity.

Current status:
- Lane 1 product/cart verifier changes are integrated and locally passing.
- Lane 2 import/source guards are integrated; source-price now passes and
  import readiness is blocked only on final same-day destructive approval.
- Lane 3 payment/thank-you changes are integrated and locally passing.
- Lane 4 API/permission inventory verifiers are integrated; guest endpoint
  inventory and permission-bypass lint now pass.
- Lane 5 docs are integrated and updated with the controller verification
  receipts below.
- Final local umbrella proof now passes with `npm run test:ecommerce-full`.

## Coordination Snapshot

This file is the P0 coordination source of truth for the ecommerce safety
guard track until it is replaced by a newer dated workstream. Future GPT-5.5 /
Codex agents should start here, then read only the lane-specific files needed
for their assigned worker lane.

Current posture:
- local repo and local ERPNext `frontend` site only;
- no staging, live, Frappe Cloud, DNS, Stripe live-mode, webhook, or public
  exposure work in this track without separate GL approval;
- backend-first proof required before frontend or launch claims;
- checkout/payment/catalog release is blocked until the receipt matrix below
  is complete or has explicit accepted blockers.

Verified by controller on 2026-05-19:
- git branch is `main`;
- touched Python files compile;
- worker lane diffs stayed within their intended ownership sets;
- local browser/cart/checkout/payment/API verifier receipts are listed in the
  matrix below.

Unverified by this track:
- target-site staging/live behavior;
- live Stripe, production webhooks, DNS, Frappe Cloud release, and public
  customer exposure;
- destructive import execution, because the 2026-05-19 packet has not received
  renewed explicit approval.

Blocked for release:
- any statement that checkout, payment, catalog, receipts, or public ecommerce
  are release-ready before the matrix below has receipts from the actual owning
  verifiers;
- any staging/live deploy, destructive import, Stripe live payment, or secret
  access inside this track without explicit approval.

## Local Verification Target

Do not collapse this into one vague pass/fail. The minimum local proof packet is:

- `python scripts/verify/website_item_classification_contract.py`
- `npm run test:shop-smoke`
- `python scripts/verify/cart_checkout_contract.py`
- `npm run test:product-prices`
- `npm run test:product-price-display`
- `python scripts/verify/variant_media_contract.py`
- `python scripts/verify/stripe_amount_parity_contract.py`
- `python scripts/verify/payment_webhook_contract.py`
- `python scripts/verify/payment_success_reconciliation_contract.py`
- new public API / permission-bypass inventory verifiers

## Release Receipt Matrix

Use this matrix as the release receipt ledger. "Receipt required" means the
owning lane must provide the exact command/output artifact or blocker before
release language changes from pending to verified.

| Receipt | Owning lane | Current status | Required proof before release |
|---|---:|---|---|
| Product classification authority | 1 | verified local | `python scripts/verify/website_item_classification_contract.py` PASS dry-run; `npm run test:shop-smoke` PASS. |
| Source price parity | 2 | verified local | `python scripts/verify/product_price_modifier_contract.py` PASS for 49 products / 10,186 active variants after `python scripts/setup/stage_seed_data.py`. |
| Visible price parity | 2 | verified local | `python scripts/verify/product_variant_price_contract.py` PASS; `npm run test:product-price-display` PASS. |
| Catalog import guard | 2 | blocked safely | `python scripts/verify/product_import_readiness_gate_contract.py` PASS; fresh snapshot `current-state-snapshot-2026-05-19-2314`, purge-scope dry run, backup `20260519_171525`, and guard-path dry run passed; `python scripts/verify/product_import_readiness_gate.py` is 11 pass / 1 blocker because final destructive approval has not been renewed. |
| Variant/media identity | 1 or 2, as assigned | verified local | `python scripts/verify/variant_media_contract.py` PASS. |
| Cart and checkout identity | 1 | verified local | `python scripts/verify/cart_checkout_contract.py` PASS; `npm run test:checkout-experience` PASS. |
| Payment amount/state | 3 | verified local | `python scripts/verify/stripe_amount_parity_contract.py` PASS; `python scripts/verify/payment_webhook_contract.py` PASS; `python scripts/verify/payment_success_reconciliation_contract.py` PASS. |
| Thank-you and receipt/email truth | 3 | verified local | `python scripts/verify/thank_you_payment_state_contract.py` PASS; `python scripts/verify/payment_cascade_contract.py` PASS; `python scripts/verify/simple_purchasable_payment_cascade_contract.py` PASS. |
| Public API and permission bypass inventory | 4 | verified local | `python scripts/verify/allow_guest_surface_inventory.py` PASS with 11 guest endpoints and 3 public write endpoints; `python scripts/verify/ignore_permissions_justification_lint.py` PASS with 150 bypasses scanned / 0 requiring attention after explicit guard comments were added to existing bypass sites. |
| Docs parity | 5 | verified local | This workstream, `locally-twisted-queue.md`, and `CODING-HANDOFF.md` name the same local-only posture and blockers. |

Final local umbrella: `npm run test:ecommerce-full` passed after the
source-price mount, same-day import-readiness evidence refresh, and
permission-bypass guard comments.

Release wording rule: until every required row is verified or explicitly
accepted as blocked, agents must say "local ecommerce safety guard active" or
"pending release receipts", not "ready for release", "safe to launch", or
"checkout approved".

## Stop Conditions

Stop and report instead of continuing if:

- a required business classification is ambiguous;
- a worker needs to mutate live/staging;
- a destructive command is needed;
- a verifier can only pass by weakening the business invariant;
- source data is missing and the test would become a proxy proof.

## Completion Definition

This track is locally complete only when:

1. all five lanes are integrated;
2. the local proof packet is green or has explicit, accepted blockers;
3. docs say exactly what is proven and what remains blocked;
4. no staging/live deploy has been performed unless GL separately approves it.
