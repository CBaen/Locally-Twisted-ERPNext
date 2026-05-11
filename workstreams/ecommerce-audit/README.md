D:2026-05-10 | Check:local artifacts 2026-05-10 | Confidence:[LOCAL-PROOF]
# Ecommerce Audit Handoff — Odoo witness → native ERPNext receiving ecosystem

## Current peer state

This directory is the evidence packet for the May 10 ecommerce architecture audit. It is not a product import, not a destructive migration rehearsal, and not permission to copy Odoo code. Odoo is the source witness for business meaning; ERPNext/Frappe v15 receives that meaning through native DocTypes, custom fields, app services, templates, and verifiers.

## 2026-05-11 Post-Import Checkout Closeout

Use `post-import-checkout-launch-closeout-2026-05-11.md` as the current
front-door handoff for the local ecommerce checkout slice. It supersedes stale
pause-centric, bouquet-only, cups-exclusion, and blanket high-variant exclusion
notes for this slice.

Current closeout evidence: corrected product set is 48 kept / 5
owner-explicit Classic exclusions; the approved local import ran against the
local ERPNext `frontend` site only and completed the guarded upsert/write path
with exit 0; the final browser proof passes for Easter Balloon Cups, 7'
Butterfly Column, Graduation Grab n Go, 6' Graduation stands, and Unicorn
Bouquet. Final proof command:
`& "C:\Program Files\nodejs\node.exe" scripts/verify/post_import_checkout_proof.js`.
Backend contracts are green for `product_import_readiness_gate`,
`post_import_catalog_state`, `direct_checkout_target_contract`, and
`cart_checkout_contract`. Remaining caveats: 8 review-only add-on axes are
protected by quote-first fallback, the five Classic exclusions remain
quote-first, the local import evidence is upsert/write rather than a
delete/recreate transcript, and the shared worktree is dirty.

## 2026-05-11 Storefront Proof And Complex UI Handoff

Use `storefront-proof-and-complex-ui-handoff-2026-05-11.md` for the
storefront-owned proof and next UI slice. It captures the corrected
Ready-to-Order/search rendered proof, final post-import checkout proof, the
all-priced-page frontend audit, Classic Arch's current quote-gated state, the
quote-first lane correction, and the complex-product UI checklist.

Current storefront evidence: 53 published priced product routes rendered; 18
direct-checkout pages passed option selection, `data-item-code`, add-to-cart,
cart-line configuration, and checkout summary preservation; 35 priced pages are
currently quote-gated at the first rendered layer. `quote_first` is a
setting/lane flag, not a hard blocker. A lane flip still needs backend-truth UI
for multi-color recipes, add-ons, conditional pricing, image updates, and
cart/checkout/receipt summary parity.

## Evidence inventory

| Lane | Required artifact | Current state | Use it for |
|---|---|---|---|
| A — Odoo source commerce map | `odoo-source-commerce-map-2026-05-10.md` | Present, read back | Cite for Odoo source/product/page/option/pricing/media/cart meaning, with version mismatch labels. |
| B — ERPNext receiving parity matrix | `erpnext-receiving-parity-matrix-2026-05-10.md` | Present | Destination parity, custom-field/service/verifier matrix, blockers. |
| C — Cart/checkout intent preservation | `cart-checkout-intent-preservation-audit-2026-05-10.md` | Present | Browser/backend proof slice for configured checkout and quote-first paths. |
| D — Native Frappe template architecture | `native-frappe-product-template-architecture-2026-05-10.md` | Present | Smallest safe native architecture and required custom layer. |
| E — Odoo/docs/agent-action convergence | `odoo-docs-agent-action-convergence-2026-05-10.md` | Present, parent-created / recovered artifact-first | Cite for converged Odoo witness → ERPNext receiving architecture, including no-variant options, cart intent, quote-first, checkout/payment boundary, automations, and verifier state. |
| Infrastructure doc map + synthesis | `ecommerce-infrastructure-doc-map-and-synthesis-2026-05-10.md` | Present, parent-created | Front-door map of every infrastructure artifact, the recovered plan, current evidence, sequencing, and what remains blocked. Start here. |
| Infrastructure plan v2 | `ecommerce-infrastructure-plan-v2-2026-05-10.md` | Present, parent-created | New infrastructure-first action plan: source authority, receiving contract register, runtime payloads, cart/checkout/quote proof, human approval packets, import/reopen gates, and launch decision packet. |
| Live Odoo backend architecture witness | `odoo-backend-architecture-and-checkout-logic-2026-05-10.md` | Present, parent-created / live read-only backend + source proof | Direct Odoo backend/public read-only observations: product/variant/no-variant architecture, 53-color behavior, cart/order-line preservation, checkout/payment boundary, delivery, CRM fields, automations, and ERPNext receiving requirements. |
| Infrastructure readiness packet | `ecommerce-infrastructure-readiness-packet-2026-05-10.md` | Present, parent-created | Current launch-readiness packet: what is proven, what remains blocked, Odoo logic to preserve, verifier state, and next engineering gates. |
| ERPNext receiving build spec from Odoo | `erpnext-receiving-build-spec-from-odoo-2026-05-10.md` | Present, parent-created | Converts live Odoo backend logic into concrete ERPNext/Frappe object model, gaps, gates, and coding order. |
| Ready-to-order checkout scope decision | `ready-to-order-checkout-scope-decision-2026-05-10.md` | Present, GL-directed / parent-recorded | Narrows launch scope: direct checkout only for ready-to-order/simple products; complex/high-variant/high-dollar decor routes quote-first/invoice-first. |
| Ready-to-order product candidate list | `ready-to-order-product-candidate-list-2026-05-10.md` | Present, subagent-created / parent-read | Classifies all 53 source products: 0 checkout-ready-now, 15 checkout-after-small-fix, 33 quote-first, 5 hide/needs-review. |
| Event pages vs ready-to-order shop contract | `event-pages-vs-ready-to-order-shop-contract-2026-05-10.md` | Present, GL-directed / parent-recorded | Public IA/merchandising rule: high-ticket decor lives as examples on event pages with quote CTAs; shop stays simple/low-variation and preserves customer notes. |
| Customer note checkout preservation audit | `customer-note-checkout-preservation-audit-2026-05-10.md` | Present, subagent-created / parent-read | Finds optional `order_notes` is code-wired to Sales Order timeline Communication and operator/payment-success lookup, but lacks a single passing end-to-end checkout-note verifier. |
| Ecommerce infrastructure agent playbook | `ecommerce-infrastructure-agent-playbook-2026-05-10.md` | Present, subagent-created / parent-read | Reusable future-agent playbook: scope rules, Odoo witness rules, ready-to-order vs event quote split, customer-note rule, artifact-first behavior, verifier gates, and failure modes. |
| Ready-to-order ecommerce plan-deepen | `ready-to-order-ecommerce-plan-deepen-2026-05-10.md` | Present, parent-created after `/plan_deepen` | Deepens the narrowed plan: direct checkout only for simple products, event decor quote-first, Phase 1 verifier repair before product edits, explicit Website Item classification sequence, delivery/payment/operator gates, and current `checkout_fulfillment_contract.py` pause-harness diagnosis. |
| Phase 1 verifier foundation result | `phase-1-verifier-foundation-result-2026-05-10.md` | Present, subagent-created / verifier-backed | Repairs checkout fulfillment pause harness/KeyError failure and adds rollback-safe customer-note checkout preservation proof with exact verifier output. |
| Phase 2 Website Item classification result | `phase-2-website-item-classification-result-2026-05-10.md` | Present, verifier-backed / applied | Adds targeted dry-run/apply classifier, applies the exact 53 Website Item lane/type decisions, and proves stored counts: 15 checkout, 33 quote-first, 5 needs-review. |
| Phase 3 checkout product-family proof result | `phase-3-checkout-product-family-proof-result-2026-05-10.md` + `phase-3-checkout-product-family-contract-20260510.json` | Present, verifier-backed / parent-verified | Proves the scoped first direct-checkout family: 13 approved foil-number bouquet pages, Mother's Day simple no-add-on path, Sales Order/Sales Invoice line preservation, rollback, and Easter seasonal deferral; public launch remains blocked. |
| Phase 4 quote/event path hardening result | `phase-4-quote-event-path-hardening-result-2026-05-10.md` + `phase-4-quote-event-checkout-boundary-contract-20260510.json` | Present, verifier-backed / parent-verified | Proves 33 quote-first + 5 needs-review products cannot enter paid checkout through product page controls, cart API, direct checkout URL, or stale localStorage; fail-closed precedence prevents inferred/partial checkout drift. |
| Verifier failure diagnosis | `product-page-architecture-readiness-failure-diagnosis-2026-05-10.md` | Present, parent/subagent-created then parent-verified | Explains why the prior `bench execute failed` no longer reproduces; latest exact verifier command passes. |
| Phase 5 delivery/payment/operator packet | `phase-5-delivery-payment-operator-packet-2026-05-10.md` | Present, parent-verified / local proof | Proves delivery fee mapping, pickup, tax boundaries, payment backend config, mocked webhook, paid cascade, payment-success reconciliation, operator quote review/send control, customer quote delivery BCC safety, local launch readiness, and pause-state safety. |
| Post-import checkout launch closeout | `post-import-checkout-launch-closeout-2026-05-11.md` | Present, local proof / backend-owned closeout | Current 48 kept / 5 Classic-excluded import and checkout proof packet; records final browser proof PASS, backend contract gates, priority products, upsert/write caveat, and remaining caveats. |
| Storefront proof and complex UI handoff | `storefront-proof-and-complex-ui-handoff-2026-05-11.md` | Present, rendered storefront proof / frontend-owned handoff | Captures Ready-to-Order/search proof, final post-import checkout proof, all-priced-page audit, Classic Arch proof, quote-first lane correction, complex UI requirements, and regression proof ladder. |
| Phase 6 launch decision packet | `phase-6-launch-decision-packet-2026-05-10.md` | Present, parent decision | Keeps public ecommerce paused; live checkout remains blocked until production HTTPS host, explicit live Stripe/site config, policy approval, webhook setup, and one intentional real payment test pass. |
| Infrastructure synthesis | `ecommerce-infrastructure-research-synthesis-2026-05-10.md` | Present, parent-created | Corrected synthesis for the real question: ERPNext receiving infrastructure, contract/runtime layers, line-level preservation, quote/checkout bridges, fail-loud evidence, and verifier gates. |
| Knowledge base index | `ecommerce-knowledge-base-index-2026-05-10.md` | Present, parent-created | Supporting index of recalled memory, local artifacts, source repos, verified docs, blockers, and next actions. |
| Product proof matrix | `ecommerce-product-proof-matrix-2026-05-10.md` | Present, parent-created / downstream only | 53-row source/product matrix. Use only after infrastructure gates; not the architecture decision artifact. |
| User-provided Odoo surfaces | `user-provided-odoo-surfaces-2026-05-10.md` | Present | Read-only surface references supplied by GL; do not click admin/auth surfaces without preflight. |

## Version anchors and mismatch labels

- Destination runtime verified by Lane B/C: `frappe 15.106.0`, `erpnext 15.105.0`, `payments 0.0.1`, `webshop 0.0.1`, `locally_twisted 0.0.1`.
- Dispatch anchor was `frappe/erpnext:v15.105.0`; local container image reported `locally-twisted-erpnext:v15`, so downstream claims should carry `[VERSION-MISMATCH]` unless the image digest/source is resolved.
- Odoo source witness local module is `addons/locally_twisted` `19.0.2.15.0`; prior handoff warns production DB may still be `19.0.2.14.0`, so source parity remains `[VERSION-MISMATCH]` until resolved.

## Current conclusion

Native ERPNext/Frappe can receive the proof-slice ecommerce meaning safely when the `locally_twisted` contract layer is kept in charge: two product-page lanes, versioned line payload fields, source-backed dependency/add-on/pricing/media services, quote-first bridges, and fail-loud verifiers. The live Odoo backend witness now sharpens the receiving target: true variants only for SKU/price identity, no-variant structured options for large/customer-specific choices, backend-preserved cart/order-line intent, quote-first escape hatches, delivery/payment boundaries, and guarded automations. GL has narrowed launch scope further: direct checkout should launch only for ready-to-order/simple products; complex/high-variant/high-dollar decor should route quote-first/invoice-first. Lane E is now recovered artifact-first. After Phase 4, the scoped first direct-checkout family is backend-proven for 13 foil-number bouquet pages and Mother's Day simple checkout, while 33 quote-first + 5 needs-review products are backend-proven unable to enter paid checkout through product-page controls, cart API, direct checkout URL, or stale localStorage. Easter remains seasonally deferred. Phase 5 now proves the delivery/payment/operator packet locally: delivery fees, pickup, tax boundaries, payment backend config, mocked webhook, paid cascade, payment-success reconciliation, operator/customer quote controls, local launch readiness, and pause-state safety. Phase 6 decision keeps public ecommerce paused. The exact product-page architecture readiness verifier still reports `technical_architecture_ok: True` and `import_reopen_ok: False` because public ecommerce is intentionally paused. Full catalog import/reimport and live checkout remain blocked until production HTTPS host, explicit live Stripe/site config, policy approval, webhook setup, and one intentional real payment test pass.


## Pre-Phase-5 hygiene verification (2026-05-10 18:xx MDT)

Parent reran the Phase 1-4 owned gates after documentation cleanup and stale ignored-output cleanup. All passed:

- `python -m py_compile ...` for ecommerce runtime/verifier/runner files.
- `python scripts/verify/product_page_runtime_contract.py` PASS.
- `python scripts/verify/website_item_classification_contract.py --report output/phase-4-website-item-classification-contract-20260510.json` PASS; generated JSON matched durable workstream copy, then the ignored output duplicate was removed.
- `python scripts/verify/checkout_fulfillment_contract.py` PASS; rollback confirmed.
- `python scripts/verify/payment_cascade_contract.py` PASS; rollback confirmed.
- `python scripts/verify/customer_note_checkout_preservation_contract.py` PASS; survivor counts stayed zero.
- `python scripts/verify/checkout_product_family_contract.py --report output/phase-3-checkout-product-family-contract-20260510.json` PASS; generated JSON matched durable workstream copy, then the ignored output duplicate was removed.
- `python scripts/verify/quote_event_checkout_boundary_contract.py --report output/phase-4-quote-event-checkout-boundary-contract-20260510.json` PASS; generated JSON matched durable workstream copy, then the ignored output duplicate was removed.

Current durable JSON evidence remains only under this workstream directory. Ignored `output/phase-*20260510.json` duplicates are regenerated proof artifacts, not source, and were deleted after equality checks.

## Next safe actions

1. Treat Lane A as present only through the parent-verified artifact `odoo-source-commerce-map-2026-05-10.md`; do not trust the earlier artifactless child completion event.
2. Use recovered Lane E (`odoo-docs-agent-action-convergence-2026-05-10.md`) as the convergence artifact; no longer carry Lane E as `[NO EVIDENCE]`.
3. Use `ecommerce-infrastructure-doc-map-and-synthesis-2026-05-10.md` as the front-door architecture map, `ecommerce-infrastructure-plan-v2-2026-05-10.md` as the active action plan, `ecommerce-infrastructure-readiness-packet-2026-05-10.md` for the current proof/gate packet, and `erpnext-receiving-build-spec-from-odoo-2026-05-10.md` for the concrete coding order; use product matrices only downstream of infrastructure gates.
4. Treat the earlier `product_page_architecture_readiness.py` `bench execute failed` as transient unless it recurs; current exact command passes and the diagnosis artifact explains the failure mode.
5. Rerun the readiness verifier immediately before any import/public launch decision in the same intended ecommerce mode.
6. Run Lane F/final synthesis only after version mismatches and final launch gates are either resolved or explicitly labeled.
7. Do not delete/reimport products, click admin-like Odoo mutation paths, or mutate authenticated systems for this audit without a fresh rollback/preflight.
8. Use `ready-to-order-product-candidate-list-2026-05-10.md` as the product-scope artifact; do not build a full complex-product checkout parity list.
9. The first checkout tranche is 15 products after small fixes, not 53 products: character/sports/theme bouquets plus Easter Balloon Cups and Mother's Day Bouquet; all complex decor stays quote-first or review/hidden.
10. Treat the focused customer-note verifier as Phase 1 complete: `customer_note_checkout_preservation_contract.py` now passes in rollback-safe mode.
11. Use `ready-to-order-ecommerce-plan-deepen-2026-05-10.md`, `ready-to-order-ecommerce-goal-progress-2026-05-10.md`, `phase-5-delivery-payment-operator-packet-2026-05-10.md`, and `phase-6-launch-decision-packet-2026-05-10.md` as active sequencing gates: Phases 1-5 are locally verifier-backed; Phase 6 keeps public checkout paused until production/access cutover gates pass.
