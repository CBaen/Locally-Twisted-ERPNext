# Ecommerce Finished Experience Roadmap

Date: 2026-05-11
Current update: 2026-05-17 all-legacy_source sellable local reimport supersedes the
old 18-checkout / 35-quote-first product baseline. Keep the layer standard, but
use the 2026-05-17 handoff for current product scope.
Scope: Locally Twisted ERPNext/Frappe ecommerce architecture, storefront runtime, checkout, ERPNext documents, and proof gates.

This roadmap defines what must be true before an agent can honestly say:

> The entire ecommerce experience is finished.

The standard is not that a product page renders. The standard is that every checkout-eligible product pattern can be imported, rendered, configured, priced, added to cart, checked out, stored in ERPNext, and fulfilled from the resulting records without hidden assumptions, product-specific hacks, or silent loss of customer choices.

## Current Baseline

Verified gates at the time this plan was written:

- `python scripts\verify\product_pattern_contract.py` passes.
- `python scripts\verify\cart_checkout_contract.py` passes.
- Current architecture includes a generic multi-color recipe contract.
- Single-select color is not allowed to clear checkout readiness for color-recipe products.
- Source mapper slug checkout overrides are guarded against.
- ProductPatternContract is the eligibility authority; frontend code must not invent checkout eligibility.

Current ProductPatternContract summary:

- Source products: 53.
- Local all-legacy_source sellable import target products: 53.
- Excluded products: 0.
- Priced sale units: 290.
- Older staged-contract baseline: 18 direct-checkout / 35 quote-first was a
  temporary architecture proof and is no longer the current product model.
- Checkout gate: passing for the current contract set.

Important boundary:

- This does not yet prove the entire customer-facing ecommerce experience is finished. It proves the core backend contract and checkout guard architecture are now in the right shape.

## Plan-Deepen Notes

### Structure

- Evidence checked:
  - `AGENTS.md` fail-loud law and backend-source-of-truth guidance.
  - `ProductPatternContract` verifier output.
  - `cart_checkout_contract.py` verifier output.
  - Recent commits `cb05559` and `b02a0c4`.
- Risks found:
  - A green backend contract can be mistaken for finished ecommerce.
  - Product-specific exceptions can re-enter through import, source-builder, product-page templates, or browser-only logic.
  - Large catch-all implementation files can become brittle if every later requirement is added to the same module.
- Plan adjustment:
  - Split work by architecture layer and proof gate.
  - Each layer needs one source of truth, one runtime path, and one verifier.
  - No product-specific branch is acceptable except fixtures/test data used to prove a generic rule.
- Open question or escalation:
  - None for architecture direction. Multi-color is mandatory and backend-driven.

### Data And Source Contract

- Evidence checked:
  - legacy_source option-pattern mapper contract.
  - ProductPatternContract report.
  - Checkout guard proving no source mapper slug checkout override.
- Risks found:
  - Import can lose legacy_source source semantics if source IDs, axis hashes, variant pointers, and pattern classes are not preserved.
  - Historical quote-first architecture language can be misread as the current
    business product model.
  - Add-ons, media, and conditional prices can be silently flattened into variants.
- Plan adjustment:
  - Make source pattern preservation a permanent import gate.
  - Keep required sale-unit axes, customization axes, add-ons, review-only axes, media roles, and pricing provenance separate.
  - Treat every legacy_source-imported product as a product unless GL explicitly
    excludes it; unclear pricing/media/add-ons should fail loudly inside the
    sellable product contract, not remove the product from scope.
- Open question or escalation:
  - Owner approval is needed only for business pricing or whether a review-only add-on should become a priced checkout add-on.

### Integration

- Evidence checked:
  - Cart checkout contract.
  - Product page runtime contract from recent work.
  - ERPNext SO/SI custom line fields already used for configuration preservation.
- Risks found:
  - Frontend can render a control that backend does not accept.
  - Cart can preserve a JSON payload while the customer/operator summary is incomplete.
  - Add-on lines can price correctly but fail to appear clearly in ERPNext documents.
- Plan adjustment:
  - Product page, cart, checkout, Sales Order, Sales Invoice, receipt, and operator view must all consume the same resolved configuration.
  - Every configured line needs both durable JSON and readable summary.
  - Cart-line identity must include the full configuration, including multi-color recipes.
- Open question or escalation:
  - Final receipt/customer-facing copy may need owner approval, but the data path should not.

### Security, Privacy, And Payment Trust

- Evidence checked:
  - Fail-loud law in `AGENTS.md`.
  - Current checkout contract behavior for unsupported configurations and
    invalid add-ons.
- Risks found:
  - Checkout can create business trust failures if it accepts unpriced add-ons, unsupported customizations, missing prices, or invalid quantities.
  - Freeform customer fields can leak unsafe or unusable fulfillment data if not constrained.
  - Payment readiness cannot be claimed from product-page proof alone.
- Plan adjustment:
  - Checkout must reject unsupported or unpriced choices before payment.
  - Freeform fields require explicit whitelist, length limits, safe summary, storage, and operator visibility.
  - Payment proof must include ERPNext order/invoice inspection, not just a browser success path.
- Open question or escalation:
  - Payment provider/live-payment decisions remain release-gate decisions, not architecture assumptions.

### Dependency And ERPNext Behavior

- Evidence checked:
  - ERPNext/Frappe local stack behavior through existing verifiers.
  - Current pattern report and cart checkout gates.
- Risks found:
  - Frappe/Webshop updates or template override order can break the path after architecture work.
  - Generated output artifacts can drift from committed source.
  - Manual Desk edits can hide import or fixture gaps.
- Plan adjustment:
  - Keep verifiers executable from committed source.
  - Treat generated `output/` reports as evidence artifacts, not source of truth.
  - Add import/reimport proof before claiming the system survives catalog changes.
- Open question or escalation:
  - None.

### Performance And Maintainability

- Evidence checked:
  - Current 53-product / 10,824 source-variant scale.
  - Existing verifier runtime is acceptable for local gates.
- Risks found:
  - Exploding multi-color recipes into ERPNext variants is not maintainable.
  - Browser proof across every variant combination can become wasteful and slow.
  - One verifier trying to prove every layer can become unreadable.
- Plan adjustment:
  - Multi-color recipe remains configuration/customization payload, not variant explosion.
  - Use pattern-level fixtures for deep proof and full inventory scans for coverage.
  - Keep verifiers layered: source, contract, runtime, cart/checkout, documents, browser, reimport.
- Open question or escalation:
  - None.

## Layer 1 - Product Contract Layer

Goal: one backend contract describes every sellable or configurable product pattern.

Build plan:

1. Finalize the ProductPatternContract schema as the authority for ecommerce behavior.
2. Keep these concerns separate in the contract:
   - sale-unit axes
   - color recipe axes
   - add-ons
   - customizations
   - conditional pricing
   - media roles
   - checkout lane
   - review/hold state
   - fail-loud states
3. Ensure every published Website Item resolves to one of:
   - checkout-ready
   - lane-mapping-only
   - needs add-on pricing
   - needs customization payload
   - explicit fail-loud review state
4. Keep source mapper semantics attached to ERPNext-side contract rows.

Proof gate:

- `scripts\verify\product_pattern_contract.py`
- `scripts\verify\product_pattern_contract_report.py`

Pass condition:

- Every published product has a pattern, lane, price state, source trace, and fail-loud reason if it cannot checkout.
- No product slug override decides checkout readiness.

## Layer 2 - Backend-Driven Product Page

Goal: product pages render from backend contract only.

Build plan:

1. Define the product-page contract emitted to templates/JS.
2. Map selectors from contract primitives:
   - chips/selectors for finite sale-unit axes
   - multi-color recipe builder for color recipe axes
   - add-on rows only for priced add-on contracts
   - blocked/review copy for review-only axes
3. Remove or guard against frontend-only eligibility decisions.
4. Ensure the frontend can display blocked/review states without implying
   checkout success.

Proof gate:

- Product-page architecture readiness verifier.
- Browser product-page fixture proof.
- Static guard for product-specific branches in selector logic.

Pass condition:

- A product page cannot show a checkout path unless the backend contract says the product/configuration is checkout-ready.
- Color recipe products cannot be represented by a single color select.

## Layer 3 - Checkout Configuration Contract

Goal: one durable payload shape survives from product page through checkout.

Build plan:

1. Lock the selected configuration schema:
   - `selected_options`
   - `color_recipes`
   - `add_ons`
   - `customizations`
   - resolved `item_code`
   - price provenance
   - readable summary
   - canonical cart-line key
2. Validate every section server-side.
3. Reject selected color axes placed in `selected_options` when they require `color_recipes`.
4. Keep same SKU with different configurations as separate cart lines.

Proof gate:

- `scripts\verify\cart_checkout_contract.py`
- runtime resolver tests for selected configuration validation.

Pass condition:

- Invalid/missing payloads fail loudly.
- Same item code with different configuration stays distinct.
- Unicode/color names serialize consistently between browser and server.

## Layer 4 - Cart, Checkout, And ERPNext Document Parity

Goal: customer choices survive into ERPNext records and fulfillment surfaces.

Build plan:

1. Trace product page to cart to checkout to Sales Order to Sales Invoice.
2. Ensure custom line fields are always populated for configured products:
   - `custom_lt_product_template_item`
   - `custom_lt_product_page_type`
   - `custom_lt_configuration_version`
   - `custom_lt_configuration_summary`
   - `custom_lt_configuration_json`
3. Ensure add-on line details are represented clearly.
4. Ensure receipt/operator summary is readable without parsing raw JSON.

Proof gate:

- Rollback-safe runtime verifier creating representative Sales Order and Sales Invoice records.
- Document/receipt inspection verifier.

Pass condition:

- The selected configuration is present in durable JSON and readable summary on ERPNext documents.
- Fulfillment can read what to make from ERPNext without consulting browser state or logs.

## Layer 5 - Add-On And Conditional Pricing Engine

Goal: optional charges and conditional prices are generic, priced, validated, and preserved.

Build plan:

1. Define the add-on registry contract:
   - source axis
   - add-on key
   - ERPNext Item
   - Item Price
   - eligibility
   - quantity/value limits
   - line summary
2. Keep review-only source add-ons blocked from checkout.
3. Define conditional pricing provenance:
   - live Item Price
   - source flat price
   - materialized variant price
   - approved rule
   - quote-only
4. Add totals proof for base item plus add-ons.

Proof gate:

- Add-on dependency contract verifier.
- Cart/checkout add-on total verifier.
- ERPNext SO/SI line proof for add-ons.

Pass condition:

- Unpriced or unapproved add-ons cannot checkout.
- Priced add-ons show quantity, unit price, total, and ERPNext line detail.
- Conditional price uncertainty fails loudly.

## Layer 6 - Media And Variant Display Contract

Goal: product media is classified and backend-driven.

Build plan:

1. Define media roles:
   - primary
   - gallery
   - variant image
   - reference
   - ignored artifact
2. Attach media only when source role is known.
3. Do not infer variant media from filename/order alone.
4. Ensure product page display does not imply an image changed unless backend proves the media mapping.

Proof gate:

- Media classification report.
- Product page rendered media verifier.

Pass condition:

- Every published product has a primary media state.
- Gallery/variant media is either classified and rendered or held back with a fail-loud reason.

## Layer 7 - Import, Purge, And Reimport Safety

Goal: the architecture survives catalog purge and future product import.

Build plan:

1. Treat source mapper output as the import contract input.
2. Preserve source IDs, axis hashes, variant pointers, and pattern class.
3. Remove manual Desk-only assumptions from checkout eligibility.
4. Prove import can classify by architecture, not product names.
5. Prove purge/reimport does not lose checkout lanes, prices, media state, or configuration contracts.

Proof gate:

- Catalog state snapshot.
- Purge scope dry run.
- Product import readiness gate.
- Post-import checkout proof.

Pass condition:

- A fresh import recreates the same architecture decisions from source contracts and ERPNext records.
- No manual product-specific patch is required after import.

## Layer 8 - Storefront UX Completion

Goal: the customer-facing experience is complete and contract-driven.

Build plan:

1. Product cards reflect checkout/quote lane accurately.
2. Product pages render selectors, multi-color recipes, add-ons, totals, media, and errors from contract.
3. Cart shows readable selected configuration and pricing.
4. Checkout blocks incomplete or invalid configurations before payment.
5. Customer-facing fail states use plain warm language and do not imply success.
6. Desktop and mobile states must both pass.

Proof gate:

- Product page browser proof.
- Cart browser proof.
- Checkout browser proof.
- Responsive layout proof.
- Search/menu/listing proof.

Pass condition:

- A customer can configure and buy every checkout-ready pattern without losing choices.
- Products with incomplete pricing, add-ons, media, or configuration contracts
  fail loudly without implying checkout success.

## Layer 9 - Full Proof Ladder

Goal: one proof bundle can support or reject the finished-ecommerce claim.

Build plan:

1. Define the proof command list by layer.
2. Separate results:
   - `inventory_ok`
   - `checkout_gate_ok`
   - `runtime_ok`
   - `browser_ok`
   - `document_parity_ok`
   - `reimport_ok`
3. Each failure must name the owner layer and the missing contract.
4. Keep output artifacts in ignored `output/` unless they are intentionally published evidence.

Proof gate:

- Final proof bundle script or documented command sequence.

Pass condition:

- All layer gates pass from committed source.
- Failures are actionable and not hidden inside prose.

## Layer 10 - Finished Claim Standard

Goal: define the exact bar for saying ecommerce is finished.

The finished claim is allowed only when all of these are true:

1. Every published product is mapped to a generic ProductPatternContract.
2. Every checkout-lane product is priced, configurable, and server-validatable.
3. Multi-color products use a multi-color recipe contract, not a single-select shortcut.
4. Add-ons are either priced and preserved or blocked/review-only.
5. Conditional pricing is proven or explicitly blocked with a customer-safe
   review state.
6. Product page controls come from backend contract data.
7. Cart lines preserve the full selected configuration.
8. Checkout rejects incomplete, unsupported, or unpriced selections.
9. ERPNext Sales Order and Sales Invoice records preserve JSON and readable summaries.
10. Customer receipt/operator view contains enough information to fulfill the order.
11. Import/purge/reimport can reproduce the architecture without manual product fixes.
12. Browser proof passes desktop and mobile for product page, cart, checkout, and failure states.

## Execution Rules

- Work layer by layer.
- Do not start a dependent layer until the prior layer's proof gate passes or the dependency is explicitly documented.
- No product-specific code branches.
- No Classic Arch special handling.
- No source-builder checkout slug override.
- No single-select color checkout shortcut for multi-color/color-recipe products.
- No silent fallback that looks like success.
- Backend contract informs frontend behavior.
- Review/hold states are setup states, not product exclusions.
- Generated reports are evidence, not source of truth.

## Suggested Task Breakdown

### Task A - Contract Completeness Audit

Check current ProductPatternContract fields against this roadmap and list missing fields, stale fields, and fields that should move into smaller helpers.

Exit gate:

- Written audit with exact file references and proposed code tasks.

### Task B - Product Page Contract Audit

Check templates and JS for any selector logic not driven by backend contract.

Exit gate:

- Verifier or report proves no product-specific checkout selector logic and no single-select color fallback for recipe axes.

### Task C - Runtime And Document Parity Audit

Trace selected configuration through cart, checkout, Sales Order, Sales Invoice, and receipt/operator surfaces.

Exit gate:

- Rollback-safe proof verifies JSON and summary fields for configured lines and add-ons.

### Task D - Add-On And Pricing Contract Expansion

Map review-only add-on classes into either priced add-on contracts or explicit
customer-safe review states.

Exit gate:

- Every add-on axis has a priced contract or fail-loud review state.

### Task E - Media Contract Implementation

Classify and gate media publishing by role.

Exit gate:

- Rendered product proof cannot publish unclassified variant/gallery media.

### Task F - Reimport Proof

Run source-contract import readiness and purge/reimport dry-run proof.

Exit gate:

- Reimport can reproduce lanes, prices, source pattern semantics, and checkout contracts without product-specific fixes.

### Task G - Browser Completion Proof

Run product page, cart, checkout, search/menu, and responsive proof across desktop and mobile.

Exit gate:

- Browser proof confirms the customer-facing experience matches the backend contract.

### Task H - Finished Ecommerce Closeout

Run the full proof ladder and publish the closeout only if all gates pass.

Exit gate:

- Root or workstream closeout names exact commands, artifacts, pass/fail summary, and remaining non-blocking follow-ups.

## Current Outcome

Outcome: Adjust.

The architecture is now on the correct path, but the roadmap must keep backend contract proof separate from full ecommerce completion. The next work should proceed through the layers above, with implementation blocked from claiming completion until browser UX, ERPNext document parity, add-on/conditional pricing, media, and reimport gates all pass.
