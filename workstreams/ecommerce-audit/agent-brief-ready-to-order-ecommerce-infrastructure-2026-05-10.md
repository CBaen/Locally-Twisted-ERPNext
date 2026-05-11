D:2026-05-10 | Check:GL 15:01 agent-training direction + current ecommerce audit artifacts | Confidence:high
# Agent brief â€” ready-to-order ecommerce infrastructure

## Mission

Continue Locally Twisted ecommerce work without drifting back into full catalog migration or product-row obsession.

We are building/verifying an ERPNext/Frappe **receiving infrastructure**:

- ready-to-order checkout for simple low-variation products,
- quote/invoice-first for complex/high-ticket/event decor,
- optional customer notes preserved safely,
- backend record proof before launch claims,
- reusable infrastructure/knowledge for future agents.

## Non-negotiable constraints

- Work on `main`.
- Preserve unrelated changes.
- No broad `git add .`.
- No destructive product purge/delete/reimport.
- No public launch/payment success claims without backend proof.
- Odoo is read-only source witness only.
- Do not save/create/delete/send/post/pay/import/publish in Odoo.
- Do not expose customer/admin PII, access tokens, Stripe keys, or live checkout details.
- No artifact = no evidence.
- If using subagents: each agent must leave a named artifact under `workstreams/ecommerce-audit/`.

## Current strategic decision

Direct checkout is **not** for all Odoo product complexity.

### Ready-to-order shop

Use for simple, low-variation, checkout-safe products.

A customer may always add an optional note, but the note is communication, not pricing/scope authority.

### Event/audience pages

High-ticket decor belongs here as examples, proof, scale, and inspiration, with quote CTA.

Preserve this framing:

> Event planning
> Built for Utah gatherings that need to look ready.
> Browse by event setting, then use the quote path when the install needs custom sizing, delivery, or venue coordination.

Audience lanes:

- Civic & Community
- Corporate Events
- Schools & Campuses
- Private Celebrations

Footer rule:

> Custom decor, delivery, and install questions belong in the quote request. Start a quote.

## Source artifacts to read first

Read these before making claims:

1. `workstreams/ecommerce-audit/README.md`
2. `workstreams/ecommerce-audit/ready-to-order-checkout-scope-decision-2026-05-10.md`
3. `workstreams/ecommerce-audit/event-pages-vs-ready-to-order-shop-contract-2026-05-10.md`
4. `workstreams/ecommerce-audit/odoo-backend-architecture-and-checkout-logic-2026-05-10.md`
5. `workstreams/ecommerce-audit/ecommerce-infrastructure-readiness-packet-2026-05-10.md`
6. `workstreams/ecommerce-audit/erpnext-receiving-build-spec-from-odoo-2026-05-10.md`
7. `workstreams/ecommerce-audit/cart-checkout-intent-preservation-audit-2026-05-10.md`

Useful code:

- `apps/locally_twisted/locally_twisted/product_page_runtime.py`
- `apps/locally_twisted/locally_twisted/product_quote_runtime.py`
- `apps/locally_twisted/locally_twisted/api/cart.py`
- `apps/locally_twisted/locally_twisted/www/checkout.html`
- `apps/locally_twisted/locally_twisted/www/checkout.py`
- `apps/locally_twisted/locally_twisted/templates/includes/navbar/navbar.html`
- `apps/locally_twisted/locally_twisted/verify/product_page_architecture_readiness.py`

## Odoo witness summary

Odoo taught us the pattern:

- true variants only for SKU/price identity,
- no-variant options for big/customer-choice dimensions,
- cart/order-line preservation matters more than UI appearance,
- quote-first/invoice-first is legitimate for complex work,
- website orders must be separated from service/deposit automation.

Classic Arch proof:

- 4 actual variants for size,
- 53 latex colors as no-variant multi-select options,
- Design and LED as no-variant options,
- LED +$50 is an option price extra,
- color selection does not change product id.

Catalog-wide proof:

- 128 saleable Odoo templates checked,
- 48 have no-variant attributes,
- 45 have multi-select attributes,
- option complexity is systemic, not a one-off.

## Expected agent outputs

Agents should produce concise, source-backed artifacts only. Good outputs:

- ready-to-order product candidate list,
- customer note preservation audit,
- reusable ecommerce infrastructure playbook/capability,
- verifier gap list / proposed gates.

Bad outputs:

- generic strategy memo,
- claims without files/tests/source lines,
- full catalog launch recommendation,
- direct checkout expansion for high-ticket decor,
- copying Odoo code/schema.

## Parent integration rule

The parent session must inspect every artifact before presenting it as evidence. Subagent completion messages are not evidence by themselves.
