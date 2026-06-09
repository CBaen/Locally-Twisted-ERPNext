D:2026-05-10 | Check:local ecommerce-audit artifacts + AGENTS/CODING-HANDOFF/capability recipe 2026-05-10 | Confidence:[LOCAL-PROOF]
# Ecommerce infrastructure agent playbook

Use this when a future agent touches Locally Twisted ecommerce infrastructure, product-page checkout, cart/checkout preservation, or legacy_source-derived ecommerce research.

## Sources inspected for this playbook

- `AGENTS.md`
- `CODING-HANDOFF.md`
- `capabilities/INDEX.md`
- `capabilities/recipes/erpnext-ecommerce-receiving-architecture.md`
- `workstreams/ecommerce-audit/agent-brief-ready-to-order-ecommerce-infrastructure-2026-05-10.md`
- `workstreams/ecommerce-audit/README.md`
- `workstreams/ecommerce-audit/ready-to-order-checkout-scope-decision-2026-05-10.md`
- `workstreams/ecommerce-audit/event-pages-vs-ready-to-order-shop-contract-2026-05-10.md`
- `workstreams/ecommerce-audit/legacy_source-backend-architecture-and-checkout-logic-2026-05-10.md`
- `workstreams/ecommerce-audit/ecommerce-infrastructure-readiness-packet-2026-05-10.md`
- `workstreams/ecommerce-audit/erpnext-receiving-build-spec-from-legacy_source-2026-05-10.md`
- `workstreams/ecommerce-audit/cart-checkout-intent-preservation-audit-2026-05-10.md`

## Scope rules

Do:

- Treat ecommerce as a receiving infrastructure problem, not a product-row migration problem.
- Work artifact-first under `workstreams/ecommerce-audit/` for research, decisions, verifier gaps, and handoffs.
- Keep legacy_source as a behavioral witness and ERPNext/Frappe as the implementation target.
- Preserve ready-to-order checkout, quote-first inquiry, backend line payloads, and verifier gates as separate concerns.

Do not:

- Purge, delete, reimport, launch, publish, pay, send customer messages, or mutate legacy_source/ERPNext unless explicitly assigned with rollback/preflight.
- Copy legacy_source schema/code directly into ERPNext.
- Expose customer/admin PII, access tokens, checkout tokens, Stripe keys, raw sessions, caches, logs, or browser profiles.
- Claim live payment, launch readiness, or full catalog safety from UI appearance alone.

## legacy_source witness rules

legacy_source evidence is useful only as a source witness for business meaning. It must be read-only unless a fresh task explicitly authorizes otherwise.

Preserve these witnessed patterns:

- True variants are only for SKU/price identity.
- Large customer-choice dimensions belong in no-variant structured option payloads, not variant explosions.
- Cart/order-line preservation matters more than product-page appearance.
- Quote-first and invoice-first are legitimate success paths for complex work.
- Website checkout orders must stay separate from service/deposit automation.

Classic Arch is the proof slice: 4 size variants, 53 latex colors as no-variant multi-select options, Design/LED as no-variant options, LED +$50 as an option price extra, and color choices that do not change product id.

## Ready-to-order vs event quote split

Direct checkout is only for simple, bounded, approved, low-interpretation products where backend records preserve what the customer chose.

A checkout-ready item needs:

1. simple buying decision,
2. bounded options,
3. approved pricing,
4. backend preservation through cart/Sales Order/payment/fulfillment records,
5. delivery/tax/payment proof,
6. clear fulfillment meaning,
7. no silent underpricing.

Complex/high-ticket/event decor belongs on audience/event pages as proof, scale, inspiration, and quote CTAs. Preserve the framing:

> Event planning
> Built for Utah gatherings that need to look ready.
> Browse by event setting, then use the quote path when the install needs custom sizing, delivery, or venue coordination.

Audience lanes: Civic & Community, Corporate Events, Schools & Campuses, Private Celebrations.

Footer rule:

> Custom decor, delivery, and install questions belong in the quote request. Start a quote.

## Customer-note rule

Ready-to-order checkout may accept an optional note, but the note is communication, not pricing or scope authority.

Safe note meanings: delivery window, event date/context, allowed color preference, recipient/location detail, small operator context.

Operator-review/quote meanings: custom sizing, install/rigging, venue access, corporate invoicing/PO constraints, complex theme/design direction, labor/material changes.

Verifier requirement: prove a ready-to-order purchase path both with and without a note, and prove the note survives into backend Sales Order/payment/fulfillment evidence before saying it works.

## Artifact-first agent rules

- No artifact = no evidence.
- Subagent completion text is not evidence; the parent must inspect named artifacts before citing them.
- Every agent doing ecommerce audit work should leave one named artifact under `workstreams/ecommerce-audit/` unless explicitly assigned a code/verifier change.
- Keep artifacts short, source-backed, and operational: what was checked, what is proven, what remains blocked, and exact files/commands.
- Do not turn a product proof matrix into a launch verdict. Product candidates come after infrastructure gates.
- Preserve unrelated work and never use broad `git add .`.

## Required verifier gates before stronger claims

For a representative ready-to-order path:

- Product page exposes only approved options/add-ons.
- Cart line has stable identity for same-SKU different configurations.
- Selected options/add-ons are visible in cart and checkout.
- Sales Order Item stores configuration version, summary, JSON, page type, and product template item.
- Sales Invoice Item copies line configuration from Sales Order Item when payment success creates invoice.
- Checkout rejects quote-first products and unapproved/review-only add-ons with customer-safe loud failure.
- Delivery, tax, and payment boundaries are backend-proven, not assumed from UI.
- Generated test records are rolled back or cleaned.

For quote-first/event paths:

- Complex product pages do not expose direct paid checkout controls.
- Selected options, product context, custom/design notes, and review flags reach `/contact` or Lead/Quotation payloads.
- Draft quote/proposal paths do not submit, email, invoice, request payment, or imply customer success until reviewed.

Current key verifier family to consider, depending on scope:

```powershell
python scripts/verify/product_page_architecture_readiness.py --report output/product-page-architecture-readiness.json
python scripts/verify/product_page_runtime_contract.py
python scripts/verify/cart_checkout_contract.py
python scripts/verify/product_quote_customization_contract.py
python scripts/verify/checkout_fulfillment_contract.py
python scripts/verify/checkout_lead_conversion_contract.py
npm run test:checkout-experience
npm run test:product-quote-first
npm run test:ecommerce-full
```

## Failure modes to avoid

- Variant explosion: treating 50+ colors/design/customer-choice dimensions as ERPNext Item Variants.
- UI-only proof: product page looks right but Sales Order/Invoice loses selected meaning.
- Silent free add-ons: priced or unapproved options visually selectable but not priced/preserved server-side.
- Generic checkout expansion: forcing high-ticket decor into paid checkout because a price exists.
- Note laundering: letting customer notes silently change scope, labor, delivery/install obligations, or price.
- Automation collision: website orders triggering quote/deposit/service invoice automation.
- Payment overclaim: observing a payment page or Payment Request and calling payment success without transaction/backend proof.
- Artifactless delegation: citing a child-agent summary without a named inspected artifact.
- PII/token leakage: copying checkout DOM datasets, access tokens, customer details, Stripe tokens, or raw session data into artifacts.
- Launch-language drift: saying â€œsafe,â€ â€œready,â€ â€œworking,â€ or â€œverifiedâ€ without a specific artifact/verifier witness.

## Bottom line

Future agents should preserve the lesson: Locally Twisted ecommerce is safe when ERPNext receives customer intent through a verified contract layer. Ready-to-order checkout is a narrow, proven lane; complex event decor is quote/invoice-first; legacy_source is a witness; artifacts and backend proof decide claims.
