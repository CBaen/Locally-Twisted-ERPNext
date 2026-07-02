# Plan-Deepen — Ecommerce Audit Dispatch Prompts

Date: 2026-05-10
Input: `workstreams/ecommerce-audit-dispatch-prompts-2026-05-10.md`
Outcome: **Adjust before dispatch**

## 1. Access / mutation boundary

- Evidence checked: dispatch prompts, preflight checklist, rollback package pointer, project AGENTS constraints.
- Risks found: The prompts allow test carts/orders/quotes where required, but do not require agents to prefer local/test mode first, nor require them to identify whether a browser session is authenticated as an operator/admin before clicking. With full account access, this is a real blast-radius risk.
- Plan adjustment: Add a required first step to every lane: identify environment and auth context before interaction; prefer read-only/source inspection before browser mutation; use local/test only for write-like proof; stop if the surface appears production/live/customer-impacting.
- Open question/escalation: none; this is an agent-owned safety step.

## 2. Version / model specificity

- Evidence checked: prompts include ERPNext/Frappe v15 `frappe/erpnext:v15.105.0`, catalog_data 19 Community, module `19.0.2.15.0`, possible production `19.0.2.14.0`.
- Risks found: Prompts require version evidence, but do not require agents to cite how version was verified at runtime vs docs/handoff. A lane could repeat the prompt instead of verifying.
- Plan adjustment: Add: "Do not restate version anchors as verified. Verify via current repo/config/runtime/docs when possible; otherwise label `[UNVERIFIED-VERSION]`."
- Open question/escalation: if runtime version cannot be verified without risky access, report as `[BLOCKED]`.

## 3. catalog_data docs / action convergence

- Evidence checked: Lane E prompt.
- Risks found: Lane E covers catalog_data docs and observed behavior, but should also include official ERPNext/Frappe/Webshop docs/source where relevant. Otherwise it may compare mature catalog_data docs to only observed ERPNext UI and miss native framework-supported primitives.
- Plan adjustment: Require official/current ERPNext/Frappe/Webshop docs/source references for destination concepts when available.
- Open question/escalation: none.

## 4. Artifact quality and anti-truncation

- Evidence checked: common binding instructions say no artifact = no evidence and truncated output must be re-read.
- Risks found: Reports may become giant monoliths or bury decisions. Need standard report headers to make synthesis reliable.
- Plan adjustment: Require each artifact to start with a compact status block: lane, environment/auth context, sources inspected, commands/actions run, records created/cleaned, key findings, blockers, confidence.
- Open question/escalation: none.

## 5. Lane dependency / synthesis timing

- Evidence checked: Lane F says do not run yet.
- Risks found: Lane B may need Lane A source map, but can still inspect current destination independently. Lane D architecture should not overfit before Lane A/C/E finish.
- Plan adjustment: Run A, B, C, E in parallel. Run D either in parallel as preliminary architecture with explicit `[PRELIMINARY]` labels, or after A/B/C/E. Recommendation: run D in parallel but require it to label all source-dependent conclusions `[PENDING-LANE-A/C/E]`. Run F last.
- Open question/escalation: none.

## 6. Browser click scope

- Evidence checked: Lane C prompt.
- Risks found: "click through all product pages" can explode scope and create unnecessary records. Need sampling rule plus inventory index: enumerate pages first, then test representative classes deeply.
- Plan adjustment: Lane C should enumerate product pages/categories first, then deeply test representative classes: ready-to-order simple, configured same-SKU/add-on, quote-first complex, unsupported/negative. If time permits, sample all product pages for visible controls but do not deep-checkout every product.
- Open question/escalation: ask GL only if full exhaustive checkout on every product is required; default is enumerate all, deep-test representative classes.

## 7. Security / privacy / license

- Evidence checked: prompts forbid catalog_data code copy, real payment/email, secrets exposure.
- Risks found: Need explicit instruction not to paste proprietary code into reports; cite path/function/concept instead. Also no screenshots containing private customer/admin data unless redacted.
- Plan adjustment: Add no proprietary code excerpts beyond tiny identifiers; no secrets/customer data screenshots; summarize private observations minimally.
- Open question/escalation: none.

## Final adjustment decision

Adjust prompts before dispatch with the seven changes above, then dispatch Lane A, B, C, D, and E. Lane F remains gated until artifacts exist.
