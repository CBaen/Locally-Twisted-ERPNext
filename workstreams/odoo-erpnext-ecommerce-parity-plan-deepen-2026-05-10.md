# Plan-Deepen — Odoo Commerce Source Extraction + ERPNext/Frappe Ecommerce Parity/Safety Audit

Date: 2026-05-10
Input brief: `workstreams/odoo-erpnext-ecommerce-parity-research-brief.md`
Status: completed before presenting brief to GL

## Executive Result

The brief is directionally correct and dispatchable, but only if the research team is constrained to artifact-first evidence and forbidden from treating Odoo parity as a simple field-mapping/import problem.

The most important strengthening is this:

> The audit must prove the receiving architecture, not the migration. A product is not “migrated” until ERPNext can preserve or intentionally reject every customer-facing and operator-facing unit of meaning that product can generate.

The plan should proceed, but with seven added guardrails:

1. Separate **source extraction**, **destination mapping**, **runtime preservation**, **native architecture**, and **synthesis** lanes.
2. Require durable named artifacts from every lane.
3. Make quote-first / hold / blocked outcomes first-class success states, not failures to be hidden.
4. Treat cart/checkout/order/invoice/operator records as the proof path, not just product pages.
5. Forbid copying Odoo code or blindly reproducing Odoo data model quirks.
6. Make exact Odoo / ERPNext / Frappe / Webshop version evidence mandatory before version-sensitive claims.
7. Keep product import and public launch blocked until the synthesis packet names what is safe.

## Stress Test 1 — Schema/Data Risk

### Risk

Researchers may over-focus on visible product fields and miss nested behavior:
- valid variant combinations,
- conditional add-ons,
- multi-option dependencies,
- price transformations,
- media rules,
- quote-only business logic,
- operator review meaning.

### Failure mode

A product appears on the ERPNext site and can be added to cart, but the backend receives a flattened SKU/quantity/price without the selected meaning needed to fulfill the order.

### Required countermeasure

The parity matrix must be behavior-based, not field-name-based. Each row should answer:

- What customer/operator meaning exists?
- Where does that meaning come from?
- Where does it land in ERPNext?
- What proves it survives or is intentionally blocked?

### Added dispatch instruction

Do not report “field mapped” as success unless the mapped value is proven through the business flow that uses it.

## Stress Test 2 — Odoo Source Extraction Boundaries

### Risk

Odoo may contain useful source behavior mixed with stale implementation details, obsolete workarounds, hardcoded IDs, old production mistakes, and version divergence. Local source currently shows Odoo 19 Community module version `19.0.2.15.0`, while prior risk notes warn production may still be `19.0.2.14.0`; source files, live pages, captured mirrors, exports, and production database notes may disagree.

### Failure mode

The team imports the old system’s accidental architecture into the new stack instead of preserving the business meaning behind it.

### Required countermeasure

Odoo is a witness, not the law. Researchers must classify each source finding as:

- business meaning to preserve,
- implementation artifact to avoid,
- stale/unclear behavior needing GL or Jeff review,
- source bug/regression not to reproduce.

### Added dispatch instruction

When source evidence conflicts, preserve the customer/operator meaning and mark the implementation as disputed instead of forcing parity with a possibly broken Odoo behavior.

## Stress Test 3 — ERPNext Native Architecture Risk

### Risk

Frappe/ERPNext Webshop may be too shallow for Locally Twisted’s real product logic, and behavior is version-specific. Destination is documented as ERPNext/Frappe v15 using `frappe/erpnext:v15.105.0`, with `payments`, `webshop`, and `locally_twisted`. Researchers may try to cram complex behavior into generic Website Item fields or unversioned JSON without checking how this exact v15 stack handles cart, checkout, custom fields, hooks, and invoice copying.

### Failure mode

The architecture works for Unicorn Bouquet / Classic Arch proof slices but collapses for complex decor, source add-on families, event-specific terms, or quote-first flows.

### Required countermeasure

The native architecture lane must explicitly decide ownership boundaries:

- ERPNext standard fields for simple stable commerce attributes,
- custom fields for operator-visible page/commerce classifications,
- child tables for repeatable structured business rows,
- versioned JSON payloads for snapshotting customer-selected configuration,
- Python services for validation/pricing/dependency execution,
- Jinja/frontend controls for rendering backend truth only,
- fail-loud backend records for rejected or malformed flows.

### Added dispatch instruction

Do not solve all complexity in the frontend. Frontend controls are the waiter taking the order; ERPNext backend is the kitchen ticket. If the kitchen ticket cannot hold the order, the waiter is not allowed to pretend the order was taken.

## Stress Test 4 — Silent-Failure / Cart / Checkout Integrity Risk

### Risk

Visual checkout can pass while business data is lost after add-to-cart, during line merging, at Sales Order creation, at invoice creation, or during quote acceptance. Version-specific framework behavior can create false confidence: Odoo `website_sale` combination behavior and ERPNext/Frappe v15 Webshop cart/checkout behavior are not interchangeable models.

### Failure mode

Customer sees success; Jeff/operator sees an incomplete or misleading order.

### Required countermeasure

The checkout auditor must test negative and same-SKU cases:

- same SKU with different options remains separate,
- unsupported add-ons are rejected or quote-first,
- quote-first variants cannot become paid checkout because a price exists,
- add-ons expand into separate lines only when approved,
- payload survives into Sales Order Item and Sales Invoice Item,
- visible cart/receipt/thank-you labels match backend payload,
- internal codes/custom-field names do not leak in customer-facing errors.

### Added dispatch instruction

“Checkout passed” is banned language unless the report names the backend records inspected and what customer intent survived into each.

## Stress Test 5 — Security / Privacy / License Risk

### Risk

The audit may touch old Odoo `.env`, production secrets, customer data, or code with licensing assumptions.

### Failure mode

A research lane over-reads secrets/private data or proposes copying code instead of reimplementing native behavior.

### Required countermeasure

- Do not read secrets unless explicitly required and approved.
- Prefer source code, sanitized exports, verifier output, and local test data.
- Do not copy Odoo implementation code into Frappe.
- Treat real customer/order data as private; summarize minimally if encountered.
- Use Odoo only to identify behavior and business meaning.

### Added dispatch instruction

If sensitive data is needed, stop and request a narrow approval instead of proceeding broadly.

## Stress Test 6 — Agent Process Risk

### Risk

Multi-agent dispatch can produce long prose, stale claims, or truncated unusable output. Previous expedition lanes failed/timed out and cannot be treated as evidence.

### Failure mode

The team generates impressive-looking research that does not change implementation safety.

### Required countermeasure

Every lane must write a named artifact under:

`workstreams/ecommerce-audit/`

Each artifact must include:

- evidence paths,
- exact commands run,
- current blockers,
- unknowns,
- recommended next build gate.

No artifact means no finding.

### Added dispatch instruction

If a lane times out, truncates, or fails to produce the named artifact, mark it `[NO EVIDENCE]` and replace with direct repo investigation or a narrower rerun.

## Revised Dispatch Shape

Recommended lanes:

1. Odoo Source Mapper
2. ERPNext/Frappe Receiving Parity Auditor
3. Cart / Checkout / Silent-Failure Auditor
4. Native Product Template Architecture Designer
5. Referee / Synthesis

Run source-mapping and receiving-parity in parallel only after the brief is accepted. Run synthesis last after artifacts exist.

## Version / Model Gate Clarification

Before any lane makes claims about product behavior, it must name the exact software model it is reasoning from:

- Odoo edition/version/module version and whether evidence is from source code, live/public page, captured mirror, export, or production DB note.
- ERPNext/Frappe/Webshop/app versions and whether evidence is from docs, source, local running stack, verifier output, or DB metadata.
- Any version mismatch must be treated as `[VERSION-MISMATCH]` until reconciled.

This matters because we are translating business meaning between systems, not porting code. The same visible product behavior may be produced by totally different framework machinery.

## Launch Gate Clarification

The audit can produce three different kinds of green lights, and they must not be confused:

1. **Architecture proof green** — ERPNext can technically preserve a class of meaning.
2. **Business approval green** — GL/Jeff have approved a behavior/price/add-on/visibility choice.
3. **Launch green** — customer-facing ecommerce can safely accept money or quote intent without silent loss.

Current proof slices may support architecture green for some paths. They do not automatically grant business approval or public launch green for the full catalog.

## Final Recommendation

Proceed with the research brief as written, with the guardrails above treated as binding dispatch requirements.

Do not allow product deletion/reimport or public ecommerce launch to ride on this audit until the synthesis artifact explicitly says:

- which products/classes are safe for checkout,
- which products/classes must stay quote-first,
- which add-ons are checkout-approved,
- which source behaviors remain blocked/unknown,
- which verifier commands passed,
- what GL decisions are still needed.
