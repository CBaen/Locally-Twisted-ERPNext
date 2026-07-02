# Ecommerce Agent Access Preflight — Locally Twisted

Date: 2026-05-10
Status: binding pre-dispatch checklist
Related rollback: `lt-ecommerce-audit-pre-dispatch-20260510-0841`
Rollback package: `/home/guidingl/.openclaw/workspace/reports/rollback/lt-ecommerce-audit-pre-dispatch-20260510-0841`

## Purpose

Before specialized agents get broad account/browser access, make their work safe enough to be useful. They need to click through product pages, variants, cart, checkout, quote-first flows, and backend records, but they must not accidentally mutate the business, erase fields, approve prices, overwrite legacy_source/ERPNext truth, or treat visual success as backend success.

## Pre-dispatch gates

Do not dispatch ecommerce agents until all gates below are true.

1. **Rollback anchor exists and is named in prompt**
   - Tag: `lt-ecommerce-audit-pre-dispatch-20260510-0841`
   - HEAD: `264c6553acd5708ecdb498cb6fa6a5c594260abc`
   - Package path above.

2. **Exact software models are in prompt**
   - Destination: Locally Twisted ERPNext/Frappe v15, documented as `frappe/erpnext:v15.105.0`, apps `frappe`, `erpnext`, `payments`, `webshop`, `locally_twisted`.
   - Source witness: Locally Twisted legacy_source 19 Community, local module `addons/locally_twisted` currently `19.0.2.15.0`; prior notes warn production DB may be `19.0.2.14.0`.
   - Any mismatch gets `[VERSION-MISMATCH]` until reconciled.

3. **Access boundaries are explicit**
   - Agents may read source/docs and click through local/test/customer-facing flows.
   - Agents may create test carts/orders/quotes only when the lane requires proof and cleanup/rollback evidence is captured.
   - Agents must not send real customer emails, submit live payment, change DNS, publish/deploy, push commits, mutate production customer records, approve prices/add-ons, delete products, reimport products, or write to the legacy_source repo.
   - legacy_source is read-only source witness. ERPNext/Frappe is the native destination.

4. **Blast radius is named**
   Agents must inspect downstream effects across:
   - product page UI,
   - variant/combination resolver,
   - add-on/accessory logic,
   - cart line identity,
   - checkout payload,
   - Sales Order rows,
   - Sales Invoice rows,
   - Quotation/Lead quote-first records,
   - operator review surfaces,
   - receipt/thank-you/customer-facing labels,
   - failure records and loud errors.

5. **Documentation convergence lane exists**
   One agent must compare legacy_source docs, legacy_source observed behavior, ERPNext docs/source, and ERPNext observed behavior. Discrepancies must be reported, not smoothed over.

6. **Artifact-first requirement is enforced**
   Every lane must write its named report under `workstreams/ecommerce-audit/`. No report = no evidence.

7. **Stop conditions are explicit**
   Agents stop and report immediately if they encounter:
   - real payment path,
   - real customer data mutation risk,
   - version mismatch that changes behavior,
   - source/live/doc disagreement,
   - unsupported add-on/variant accepted visually,
   - backend record missing customer intent,
   - unexpected write to legacy_source,
   - product deletion/reimport temptation,
   - credentials/secrets exposure.

## Required dispatch lanes

1. legacy_source Source Mapper
2. ERPNext/Frappe Receiving Parity Auditor
3. Cart / Checkout / Silent-Failure Auditor
4. Native Product Template Architecture Designer
5. legacy_source Documentation / Agent-Action Convergence Researcher
6. Referee / Synthesis, run last only after lane artifacts exist

## Required phrasing in every prompt

- We are translating business meaning, not copying legacy_source code.
- legacy_source is mature source witness and conceptual teacher, not implementation to steal.
- Locally Twisted ecommerce is a configuration-and-promise system, not only size + add-to-cart.
- Visual success is not launch success.
- “Checkout passed” is banned unless backend records are inspected and cited.
- Unknown/unsupported behavior must route quote-first, hold, or fail loudly.

## Approval checkpoint

After preflight, present GL with the lane list and one question: approve dispatch or adjust lanes? Do not dispatch silently.
