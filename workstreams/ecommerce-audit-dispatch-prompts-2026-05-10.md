# LT Ecommerce Audit Exact Dispatch Prompts — 2026-05-10

Status: plan-deepened and adjusted before dispatch
Rollback anchor for every lane: `lt-ecommerce-audit-pre-dispatch-20260510-0841`
Rollback package: `C:\Users\baenb\.openclaw\workspace\reports\rollback\lt-ecommerce-audit-pre-dispatch-20260510-0841`
Repo: `C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\locally-twisted`
legacy_source witness repo: `C:\Users\baenb\projects\locally-twisted-legacy_source`

## Common binding instructions for every lane

Required first line in every lane report/artifact:
`D:YYYY-MM-DD | Check:<source/date> | Confidence:<label>`

Parent accountability: Moji/parent is responsible for injecting this contract into the spawned-agent prompt and rejecting missing-header/missing-evidence reports. Do not treat omissions as “agent fault” if the prompt failed to require them.

You are working on Locally Twisted ecommerce launch safety. This is high-blast-radius work. Treat this as a configuration-and-promise system, not simple “pick a size, add to cart” retail.

Use current evidence only. Cite paths, commands, browser observations, docs URLs/titles, and record identifiers where safe. If output is truncated, re-read the missing span. No artifact = no evidence. Do not paste proprietary legacy_source implementation code into reports; cite path/function/concept instead. Do not include screenshots or excerpts containing secrets or private customer/admin data unless redacted.

Software model anchors:
- Destination: Locally Twisted ERPNext/Frappe v15, documented as Docker image `frappe/erpnext:v15.105.0`, apps `frappe`, `erpnext`, `payments`, `webshop`, `locally_twisted`.
- Source witness: Locally Twisted legacy_source 19 Community, local module `addons/locally_twisted` currently `19.0.2.15.0`; prior notes warn production DB may be `19.0.2.14.0`.
- Any version mismatch or docs/source/live mismatch must be labeled `[VERSION-MISMATCH]`, `[UNVERIFIED-VERSION]`, `[DOCS-MISMATCH]`, `[SOURCE-MISMATCH]`, `[LIVE-MISMATCH]`, `[ERPNext-GAP]`, or `[UNKNOWN]`. Do not restate these version anchors as verified. Verify through current repo/config/runtime/docs where possible; otherwise label `[UNVERIFIED-VERSION]` or `[BLOCKED]`.

Access boundaries:
- First identify environment and auth context before interaction: local/test vs live/production, guest vs operator/admin, and whether actions can create records or trigger external effects. Prefer read-only/source inspection before browser mutation. Use local/test only for write-like proof. Stop if a surface appears production/live/customer-impacting.
- You may read docs/source, run read-only searches, inspect current code, use local/test browser flows, and create test carts/orders/quotes only if your lane needs backend proof and you record cleanup/rollback evidence.
- You must not send real customer email, submit live payment, change DNS, deploy, push commits, approve prices/add-ons, delete/reimport products, mutate legacy_source, or touch real customer data except minimal read-only inspection if unavoidable and explicitly noted.
- legacy_source is read-only source witness and conceptual teacher. Do not copy legacy_source code into ERPNext/Frappe. We are translating business meaning, not stealing implementation.

Stop and report immediately if you hit: real payment path, real customer data mutation risk, secrets exposure, legacy_source write temptation, product deletion/reimport temptation, unsupported add-on/variant accepted visually, backend customer intent loss, or version/source/live/docs disagreement that changes conclusions.

Every artifact must start with the required `D:YYYY-MM-DD | Check:<source/date> | Confidence:<label>` header, then a compact status block: lane, environment/auth context, sources inspected, commands/actions run, records created/cleaned, key findings, blockers, confidence.

Before reporting success, inspect downstream blast radius relevant to your lane: product page UI, variant/combination resolver, add-on/accessory logic, cart line identity, checkout payload, Sales Order rows, Sales Invoice rows, Quotation/Lead quote-first records, operator review surfaces, receipt/thank-you/customer-facing labels, and failure records/loud errors.

Banned success phrase: “checkout passed” unless you name the backend records inspected and state what customer intent survived into each.

## Lane A — legacy_source Source Mapper

Task:
Extract source commerce meaning from the legacy_source witness without proposing ERPNext implementation first.

Required artifact:
`workstreams/ecommerce-audit/legacy_source-source-commerce-map-2026-05-10.md`

Must include:
- exact legacy_source edition/version/module evidence used, and whether each claim comes from source file, docs, public/live page, captured mirror, export, or production DB note;
- product/page classes;
- variant axes and valid-combination rules;
- add-on/accessory/options families and affected products;
- optional vs required choices;
- price sources and gaps;
- media/gallery/variant-image signals;
- quote vs checkout behavior;
- backend order/invoice/operator data that mattered;
- explicit unknowns and source paths/records.

Do not write to the legacy_source repo.

## Lane B — ERPNext/Frappe Receiving Parity Auditor

Task:
Map each source meaning from the brief/current repo to the current ERPNext/Frappe receiving destination or mark it missing/blocked.

Required artifact:
`workstreams/ecommerce-audit/erpnext-receiving-parity-matrix-2026-05-10.md`

Must include matrix columns:
- exact ERPNext/Frappe/Webshop/app version evidence;
- source behavior / field / rule;
- current ERPNext destination;
- owner module/service/template/verifier;
- status: preserved / transformed / quote-first / missing / blocked;
- evidence path;
- required gate before import or launch.

Do not change implementation code. If a verifier must be proposed, describe it rather than editing code.

## Lane C — Cart / Checkout / Silent-Failure Auditor

Task:
Use browser and backend inspection to prove whether customer intent survives runtime journeys in local/test ERPNext/Frappe.

Required artifact:
`workstreams/ecommerce-audit/cart-checkout-intent-preservation-audit-2026-05-10.md`

Must include:
- environment/auth context before clicking;
- product/category inventory enumerated first;
- pages/actions clicked;
- product page payload examples;
- variant/option/add-on selections tested;
- cart line identity and same-SKU configured-line behavior;
- add-on line expansion behavior;
- checkout translation into Sales Order Item rows;
- invoice copying behavior where safe/test-only;
- quote-first rejection/handoff paths;
- customer-facing labels on cart/receipt/thank-you;
- operator-facing record evidence;
- negative tests for unsupported options/add-ons;
- cleanup/rollback evidence for any test records created.

Default scope: enumerate all product pages/categories and visible controls, then deeply test representative classes: ready-to-order simple, configured same-SKU/add-on, quote-first complex, and unsupported/negative. Do not deep-checkout every product unless explicitly justified and safe.

Do not submit live payment or send real email. If payment path appears, stop before payment submission and report.

## Lane D — Native Product Template Architecture Designer

Task:
Propose the smallest native Frappe/ERPNext architecture that can safely receive the catalog meaning found by current evidence.

Required artifact:
`workstreams/ecommerce-audit/native-frappe-product-template-architecture-2026-05-10.md`

Must include:
- recommended product-page classes;
- required custom fields / child tables / DocTypes;
- versioned payload schema boundaries;
- pricing and dependency service boundaries;
- media destination strategy;
- add-on approval workflow;
- quote-first vs checkout decision tree;
- migration/import staging plan;
- rollback/fail-loud gates;
- what remains business-review required.

Do not edit implementation. This is architecture, not build. Because this may run before source/action lanes finish, label source-dependent conclusions `[PENDING-LANE-A/C/E]` unless directly evidenced.

## Lane E — legacy_source Documentation / Agent-Action Convergence Researcher

Task:
Compare legacy_source documentation, legacy_source observed behavior, and ERPNext/Frappe observed behavior. Find discrepancies and risks.

Required artifact:
`workstreams/ecommerce-audit/legacy_source-docs-agent-action-convergence-2026-05-10.md`

Must include:
- exact legacy_source documentation pages/versions consulted;
- exact legacy_source local/source/live/captured surfaces clicked or inspected;
- official/current ERPNext/Frappe/Webshop documentation or source references consulted where relevant;
- exact ERPNext/Frappe docs/source/pages/actions clicked or inspected;
- convergence table: documented behavior / observed legacy_source behavior / observed ERPNext behavior / discrepancy / risk / required decision;
- special attention to variants, `website_sale` combination behavior, add-ons/accessories/options, cart preservation, checkout payloads, order/invoice semantics, and customer-visible promises;
- every discrepancy labeled `[DOCS-MISMATCH]`, `[SOURCE-MISMATCH]`, `[LIVE-MISMATCH]`, `[ERPNext-GAP]`, or `[UNKNOWN]`.

Do not copy legacy_source code. Use docs and observations to translate concepts.

## Lane F — Referee / Synthesis — DO NOT RUN YET

Run only after Lane A-E artifacts exist.

Required artifact:
`workstreams/ecommerce-audit/ecommerce-launch-readiness-synthesis-2026-05-10.md`

Must reconcile all lanes and state:
- what is safe now;
- what is only technically proven but not business-approved;
- what is missing;
- what must stay quote-first;
- what blocks product import;
- what blocks public launch;
- exact verifier commands that must pass;
- exact GL decisions needed;
- discrepancies between legacy_source documentation, legacy_source observed behavior, and ERPNext observed behavior.
