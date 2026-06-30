# Operating Brief - Owner-Operated Ecommerce Hardening

Date: 2026-06-30

Status: accepted feature-lane brief, sanitized for LT docs.

## Goal

Fix LT ecommerce so it reaches professional ecommerce/ERP expectations:

- authorized backend users can manage the shop without developer or AI-agent intervention;
- product changes project to the live public site immediately when approved and valid;
- products, prices, photos, options, add-ons, cart, checkout, documents, payment, and receipts stay connected;
- the current product/variant chaos is reduced by using the right distinction between sellable SKUs and structured configuration.

## Context

The current ecommerce layer has useful parts, but the scaffold is muddled:

- some hard-coded or historical decisions now hurt the owner workflow;
- some implementations do nothing visible for the public shop;
- some designs are irrelevant to how a business owner actually operates;
- raw ERPNext catalog edits are dangerous and guarded, but the replacement owner workflow is not complete enough;
- current product records reflect earlier import/scaffold decisions, including excessive variant records.

## Known Facts

- Product Setup exists and is the intended owner surface.
- Raw ERPNext Item, Website Item, Item Price, option/category/gallery/settings edits can desync public ecommerce behavior.
- Public product pages read custom LT fields and runtime schemas, not every standard backend field a human might edit.
- Cart and checkout trust server-side Item Price, so they can faithfully propagate wrong backend price data.
- Variant explosion is not the target architecture. True sellable SKU axes become variants; colors, configuration, add-ons, measurements, uploads, and review-only options become structured payloads or quote context.
- Product media has multiple public projections: main image, gallery, selected variant image, shop card, cart, payment, and receipt/customer image.

## Unknowns To Resolve

- Which current products can migrate from excessive variant rows to SKU-only variants without losing quote/cart/order meaning?
- Which owner product actions should be instant live projection versus reviewed publish?
- Which fields in Product Setup need to become the only owner-editable authority?
- Which existing verifiers can be reused, and which proof gaps require new verifiers?
- Where are the complete external-drive prior-research docs/source materials mounted, and what can be learned without copying implementation?
- Which open-source ecommerce admin patterns should influence LT Product Setup UX?

## Hard Constraints

- The public site cannot go down.
- No live product mutation, deploy, DNS, payment, provider, or customer-facing change without explicit scoped approval.
- Do not use the restricted platform name in LT docs, paths, branches, comments, or normal conversation.
- Treat prior ERP research as architecture evidence only, not code or naming to copy.
- No secrets, raw auth/session files, payment keys, customer data dumps, or production data-loss actions.
- Any customer-visible success must be backed by a real downstream record/path.

## Optimized Approach

Treat the proposed method as a clue, not a constraint:

1. Use prior ERP research and backend access to identify owner-friendly product-management behaviors.
2. Compare those behaviors against official docs/primary sources from open-source ecommerce systems.
3. Translate only the useful behavior into LT-native architecture.
4. Make Product Setup the owner operating surface.
5. Keep raw ERPNext records as protected projections.
6. Build the smallest proof slice first:
   - one existing product,
   - one price change,
   - one description change,
   - one main image change,
   - one selected-option/variant image behavior,
   - one add-on only if approved.
7. Expand only after proof crosses product page, shop card, cart, checkout, Sales Order, payment, invoice, and receipt/customer-facing output.

## Proceed Rules

Proceed with research, mapping, docs, dry-run plans, and local-only proof.

Stop before:

- access gaps;
- possible data loss;
- money/payment behavior;
- production mutation;
- legal/compliance ambiguity;
- customer promises or customer-visible changes;
- external account writes;
- any action that would expose checkout/payment without a separate launch gate.

## Current Default Decisions

- Future model: SKU-only variants plus structured configuration.
- Product Setup is the owner source of truth.
- Immediate live change means validated projection plus public proof, not simply saving a field.
- Raw ERPNext table editing stays guarded.
- Existing 10k+ variant shape is migration debt.
