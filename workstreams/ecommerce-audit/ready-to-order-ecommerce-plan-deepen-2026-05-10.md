D:2026-05-10 | Check:/plan_deepen against local artifacts + catalog_data account/source witness + ERPNext code 2026-05-10 | Confidence:high
# Ready-to-order ecommerce infrastructure plan-deepen

## Decision

**ADJUST, THEN PROCEED IN SMALL VERIFIED SLICES.**

The clearer plan is right: **direct checkout should be narrow** and reserved for simple ready-to-order products. Complex/high-ticket/event decor should stay visible through event/audience pages as examples, proof, scale, and inspiration, then route quote/invoice-first.

The implementation plan is viable only if the next work treats ERPNext as a receiving system with explicit backend contracts. Do not treat product cards, visible buttons, or catalog_data parity tables as launch proof.

## Evidence checked in this deepen pass

Primary artifacts:

- `catalog_data-backend-architecture-and-checkout-logic-2026-05-10.md`
- `ecommerce-infrastructure-readiness-packet-2026-05-10.md`
- `erpnext-receiving-build-spec-from-catalog_data-2026-05-10.md`
- `ready-to-order-checkout-scope-decision-2026-05-10.md`
- `event-pages-vs-ready-to-order-shop-contract-2026-05-10.md`
- `ready-to-order-product-candidate-list-2026-05-10.md`
- `customer-note-checkout-preservation-audit-2026-05-10.md`
- `ecommerce-infrastructure-agent-playbook-2026-05-10.md`

Current code inspected:

- `apps/locally_twisted/locally_twisted/www/checkout.py`
- `apps/locally_twisted/locally_twisted/api/cart.py`
- `apps/locally_twisted/locally_twisted/product_page_runtime.py`
- `apps/locally_twisted/locally_twisted/www/payment_success.py`
- `apps/locally_twisted/locally_twisted/verify/checkout_fulfillment_contract.py`
- `apps/locally_twisted/locally_twisted/ecommerce_pause.py`

Existing verifier evidence:

- Product-page architecture readiness verifier now passes: `ok=true`, `technical_architecture_ok=true`, `import_reopen_ok=true`, `14 pass / 0 blocked / 1 deferred`.
- `payment_cascade_contract.py` passed and rolled back generated records.
- `checkout_fulfillment_contract.py` currently fails with `KeyError: 'sales_order'`.

## The core architecture insight from catalog_data

catalog_data should be treated as a source witness for business meaning, not a schema to clone.

The critical catalog_data pattern is:

1. **True variants only for SKU/price identity.**
   - Classic Arch uses real variants for size only.
2. **Large customer-choice dimensions are no-variant structured options.**
   - 53 latex colors, design, and LED choice are preserved as order-line meaning without exploding SKU variants.
3. **Cart/order-line preservation is the proof.**
   - Existing catalog_data cart/order evidence preserved no-variant colors and custom text on the sale order line.
4. **Quote-first is a valid success path.**
   - catalog_data product inquiry creates CRM lead context instead of forcing every configurable product into checkout.
5. **Website orders must stay separated from service/deposit automation.**
   - catalog_data source explicitly skips website orders in custom invoice automation.

ERPNext/Frappe can support this, but only with the `locally_twisted` runtime/contract layer around native Webshop.

## The sharpened launch shape

### Direct checkout lane

Use only for products with:

- simple buying decision,
- bounded options,
- approved price,
- approved media,
- delivery/tax/payment path,
- backend-preserved line configuration,
- optional customer note preserved as communication,
- no hidden install/custom-design obligation.

Current product scope:

- `checkout_ready_now`: **0**
- `checkout_ready_after_small_fix`: **15**
- `quote_first`: **33**
- `hide_or_needs_review`: **5**

The first checkout tranche should be the 15 `checkout_ready_after_small_fix` products only after gates pass. Most are bouquet-family products plus Easter Balloon Cups and Mother's Day Bouquet.

### Quote/event lane

High-ticket/event/decor products should live on event/audience pages as examples and confidence-builders. They should route to quote/invoice-first instead of paid checkout.

Preserve this public framing:

> Event planning
> Built for Utah gatherings that need to look ready.
> Browse by event setting, then use the quote path when the install needs custom sizing, delivery, or venue coordination.

This is not a downgrade. It is the business-safe path for work where scope, venue, labor, timing, or design can change the real cost.

## Stress test findings

### 1. The plan is safer now, but launch readiness is still blocked

Narrowing direct checkout to simple ready-to-order products removes the worst risk: pretending complex custom decor can be bought like a normal SKU.

Still blocked:

- saved Website Item classifications are still not proven as launch-ready,
- no product is currently `checkout_ready_now`,
- customer-note preservation is code-wired but not end-to-end verified from checkout submit,
- checkout fulfillment verifier is failing,
- duplicate/confusing delivery carrier mapping remains unresolved,
- public payment success is not proven,
- product price/media approvals remain row-level gates.

### 2. The `checkout_fulfillment_contract.py` failure looks like a harness/mode problem, not necessarily a fulfillment-logic failure

Current code has a safe public pause:

- `ecommerce_pause.py` defaults `ECOMMERCE_PAUSED_DEFAULT = True`.
- `checkout.py::_assert_checkout_api_open()` returns:
  - `ok: False`
  - `status: ecommerce_paused`
  - no `sales_order`.

`checkout_fulfillment_contract.py` assumes `_submit_checkout()` returns `result["sales_order"]`. If the pause guard is active, the verifier gets a normal paused-checkout payload and then crashes with `KeyError: 'sales_order'`.

Adjustment required:

- Make fulfillment/customer-note verifiers explicitly open ecommerce in the test harness or monkeypatch `is_ecommerce_paused()` to `False` inside rollback-safe runs.
- If the pause guard returns `ecommerce_paused`, the verifier should fail with a clear setup error, not `KeyError`.

This is important: the launch pause is good. The tests need a deterministic internal testing mode.

### 3. Customer notes are implemented in the right semantic place, but proof is incomplete

`checkout.py` accepts `order_notes`, composes fulfillment/date/window/tax/delivery context, and records a Sales Order-linked `Communication` with subject `Customer checkout notes - <SO>`.

`payment_success.py` reads the same `Communication` into the operator â€œNew paid orderâ€ email as `Customer notes`.

This matches the business rule: notes are communication, not pricing/scope authority.

Remaining gap:

- no single passing verifier proves `submit_guest_order(order_notes=...)` â†’ Sales Order `Communication` â†’ payment/fulfillment/operator evidence.
- no-note behavior also needs proof so the system does not invent fake customer notes.

### 4. Inference fallback is helpful, but explicit saved classifications are still required

`product_page_runtime.product_page_contract_for_website_item()` can infer checkout vs quote-first if fields are unset or `needs_review`.

That is good as a safety net, but not enough for launch governance.

Launch needs explicit Website Item fields:

- `lt_product_page_type`
- `lt_commerce_lane`

Reason: humans/operators need a durable catalog decision, not a hidden heuristic. The heuristic should protect the system; it should not be the launch authority.

### 5. Add-ons are correctly guarded, but candidate products still need family proof

The runtime currently has a priced foil-number add-on contract:

- `ADDON-FOIL-NUMBER`
- `rate: 12.0`
- eligible bouquet website items
- max add-on quantity guard

It also intentionally blocks review-only source add-ons:

- `Add ons`
- `Plush add ons`
- `Orbz toppers`
- `Add Bouquet`

This is the right shape. Next proof should verify the bouquet family, not only Unicorn Bouquet.

### 6. Delivery/tax/payment must stay backend-proven

Do not claim payment/checkout success from UI pages.

Minimum proof still needed:

- fulfillment date/window fields on Sales Order,
- delivery fee as separate non-taxable service line,
- goods-only tax calculation,
- pickup path with no delivery line,
- out-of-area delivery returns quote-required without money records,
- Payment Request links to Sales Order,
- paid-order cascade creates invoice/email/operator evidence only in safe rollback/stubbed mode,
- no live Stripe/customer-facing payment claim until deliberate payment proof.

### 7. Event pages and shop must not compete

Event/audience pages should carry the high-ticket decor storytelling. The shop should not become a dumping ground for every catalog_data product just because it exists.

Practical rule:

- Event page = inspiration + proof + quote CTA.
- Shop page = bounded ready-to-order purchase.
- Product note = communication.
- Quote form = scope/design/pricing authority.

## Adjusted implementation sequence

### Phase 0 â€” Freeze and test-mode clarity

Goal: prevent accidental launch or mutation while enabling local proof.

Actions:

1. Keep public ecommerce paused by default.
2. Add/confirm an explicit internal verifier mode that opens checkout APIs only inside rollback-safe tests.
3. Preserve rollback checkpoint and avoid broad `git add .`.
4. Document every generated artifact under `workstreams/ecommerce-audit/`.

Exit gate:

- verifier failures distinguish real logic failures from `ecommerce_paused` setup state.

### Phase 1 â€” Repair verifier foundation before product edits

Goal: prove the backend machinery before touching catalog classifications.

Actions:

1. Fix `checkout_fulfillment_contract.py` harness behavior:
   - monkeypatch `locally_twisted.ecommerce_pause.is_ecommerce_paused` false, or set test config for the run;
   - fail clearly if checkout remains paused;
   - avoid `KeyError` by checking `ok/status` first.
2. Add focused `customer_note_checkout_preservation_contract.py` or extend fulfillment contract:
   - submit ready-to-order item with no note;
   - submit ready-to-order item with unique note;
   - assert Sales Order exists;
   - assert linked Communication exists and contains note;
   - assert Payment Request links to same Sales Order;
   - safely run/stub paid-order cascade;
   - assert operator evidence can read note;
   - rollback and prove no generated money/customer/note records survive.
3. Rerun:
   - `python scripts/verify/payment_cascade_contract.py`
   - repaired fulfillment verifier
   - focused customer-note verifier.

Exit gate:

- no-note and note checkout paths pass in rollback-safe mode.

### Phase 2 â€” Save explicit Website Item classifications safely

Goal: turn the 53-row decision into durable ERPNext catalog state without purge/reimport.

Actions:

1. Build a dry-run classification updater that targets only `Website Item` fields:
   - 15 products â†’ `simple_product` / `checkout`
   - 33 products â†’ quote-first product/page lane
   - 5 products â†’ hidden/review or `needs_review` with no checkout exposure.
2. Produce a before/after report listing every changed Website Item.
3. Refuse to run if expected Website Item identity is missing or ambiguous.
4. Do not delete, purge, reimport, publish, or expose product records.

Exit gate:

- report shows exact saved classifications and no unrelated catalog changes.

### Phase 3 â€” Prove first checkout product family

Goal: prove one bounded family, not the whole catalog.

Actions:

1. Run a bouquet-family verifier across the 14 bouquet candidates:
   - size variant/cart behavior,
   - optional foil number add-on,
   - same SKU with different configuration stays distinct when needed,
   - Sales Order Item/Sales Invoice Item preserve configuration JSON/summary,
   - add-on line links back to template item.
2. Run single-product checks for:
   - Mother's Day Bouquet â€” simplest no-option path,
   - Easter Balloon Cups â€” bounded design-axis path, if seasonally approved.
3. Produce a product readiness report with per-row gates:
   - classification saved,
   - price approved,
   - primary/gallery media approved,
   - note verifier covered,
   - delivery eligibility covered,
   - public copy safe.

Exit gate:

- candidate rows can move from `checkout_ready_after_small_fix` to `checkout_ready_now` only with artifact-backed proof.

### Phase 4 â€” Quote/event path hardening

Goal: make complex decor visible and compelling without leaking into paid checkout.

Actions:

1. Keep event/audience pages as the main high-ticket decor surface.
2. Ensure quote CTAs carry useful context:
   - event lane,
   - product/example context where applicable,
   - customer notes/design prompt,
   - optional inspiration media path if available.
3. Verify quote-first product pages cannot enter direct checkout through:
   - product page buttons,
   - cart API,
   - direct `/checkout?item=...`,
   - stale localStorage cart lines.
4. Preserve customer-safe error language: quote-required, not broken setup.

Exit gate:

- complex/event products are browseable as examples and impossible to accidentally buy directly.

### Phase 5 â€” Delivery/payment/operator packet

Goal: prove money and fulfillment boundaries before any launch language.

Actions:

1. Resolve duplicate/confusing `Standard delivery` mapping.
2. Confirm delivery service items and prices:
   - pickup/free,
   - standard delivery,
   - Park City delivery,
   - out-of-area quote behavior.
3. Confirm tax only applies to goods, not delivery service lines.
4. Confirm paid-order cascade:
   - Payment Request â†’ Payment Entry â†’ Sales Invoice,
   - receipt email,
   - operator email,
   - welcome email only when appropriate,
   - notes visible to operator,
   - rollback/stubs during verifier runs.

Exit gate:

- backend money/fulfillment packet passes without live customer/payment side effects.

### Phase 6 â€” Launch decision packet

Goal: decide whether to open the ready-to-order shop, not the full ecommerce universe.

Required packet:

- readiness verifier pass,
- payment cascade pass,
- fulfillment contract pass,
- customer-note verifier pass,
- product family readiness report,
- saved Website Item classification report,
- quote-first block report,
- delivery mapping report,
- media/price approval packet,
- public pause/opening plan,
- rollback plan.

Only then consider setting `lt_ecommerce_paused` open for public direct checkout.

## Key risks and mitigations

| Risk | Why it matters | Mitigation |
|---|---|---|
| Variant explosion | 50+ colors/design axes would create unmaintainable ERPNext items | Keep catalog_data no-variant dimensions as configuration payloads; only true SKU/price identity becomes Item Variant |
| UI-only confidence | Product page/cart can look right while Sales Order loses meaning | Require Sales Order/Invoice custom field proof for selected options/add-ons |
| Customer note laundering | Customers may request custom scope in a simple checkout note | Note is communication only; operator copy says requested/not confirmed; complex note patterns should route review/quote language later |
| Paused checkout breaking tests | Safe public pause causes verifier `KeyError` instead of logic proof | Add deterministic test-mode bypass and clear setup failure |
| Silent free add-ons | Unmapped source add-ons could sell labor/material as free | Keep review-only add-ons blocked; only explicit priced add-on contracts are checkout-safe |
| Complex decor underpricing | High-ticket work can require install/venue/design labor | Keep event/decor products quote-first/invoice-first |
| Automation collision | Website orders could trigger quote/deposit/service automations | Guard website checkout orders explicitly; preserve Shopping Cart order type/automation separation |
| Delivery confusion | Duplicate Standard delivery can misprice or confuse operators | Resolve carrier/service item mapping before launch |
| PII/token leakage | Cart/order/account observations contain sensitive info | Redact notes, addresses, customer details, tokens, Stripe/session data in artifacts |
| Destructive catalog moves | Purge/reimport can lose work or publish wrong products | No purge/delete/reimport; use targeted dry-run updater and exact reports |

## Recommended immediate next build task

Start with **Phase 1**, not product edits.

The smallest high-value implementation task is:

> Repair the checkout fulfillment verifier harness and add the focused customer-note preservation verifier, with ecommerce pause explicitly bypassed only inside rollback-safe tests.

Why first:

- It converts the current `KeyError: 'sales_order'` into useful evidence.
- It proves the backend logic GL cares about: customer intent survives checkout.
- It keeps public ecommerce paused.
- It avoids spending product/editing energy before the proof gate exists.

## Bottom line

The new scope insight is strong. It turns this from â€œmake all catalog_data ecommerce work in ERPNextâ€ into a safer architecture:

- **Shop:** small, bounded, ready-to-order products with backend proof.
- **Event pages:** high-ticket/custom decor examples with quote CTAs.
- **Backend:** ERPNext receives structured customer intent through verified custom contracts.
- **catalog_data:** witness/teacher, not code to copy.

Proceed, but only after fixing the verifier foundation. No product launch, purge, reimport, payment claim, or public checkout opening until the Phase 1â€“6 gates produce artifacts.
