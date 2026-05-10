D:2026-05-10 | Check:local artifacts 2026-05-10 | Confidence:[LOCAL-PROOF]
# Ecommerce Audit Handoff — Odoo witness → native ERPNext receiving ecosystem

## Current peer state

This directory is the evidence packet for the May 10 ecommerce architecture audit. It is not a product import, not a destructive migration rehearsal, and not permission to copy Odoo code. Odoo is the source witness for business meaning; ERPNext/Frappe v15 receives that meaning through native DocTypes, custom fields, app services, templates, and verifiers.

## Evidence inventory

| Lane | Required artifact | Current state | Use it for |
|---|---|---|---|
| A — Odoo source commerce map | `odoo-source-commerce-map-2026-05-10.md` | **Missing** / `[NO EVIDENCE]` | Do not cite source-product findings from this lane until rerun artifact-first. |
| B — ERPNext receiving parity matrix | `erpnext-receiving-parity-matrix-2026-05-10.md` | Present | Destination parity, custom-field/service/verifier matrix, blockers. |
| C — Cart/checkout intent preservation | `cart-checkout-intent-preservation-audit-2026-05-10.md` | Present | Browser/backend proof slice for configured checkout and quote-first paths. |
| D — Native Frappe template architecture | `native-frappe-product-template-architecture-2026-05-10.md` | Present | Smallest safe native architecture and required custom layer. |
| E — Odoo/docs/agent-action convergence | `odoo-docs-agent-action-convergence-2026-05-10.md` | **Missing** / `[NO EVIDENCE]` | Do not cite docs/source convergence from this lane until rerun artifact-first. |
| User-provided Odoo surfaces | `user-provided-odoo-surfaces-2026-05-10.md` | Present | Read-only surface references supplied by GL; do not click admin/auth surfaces without preflight. |

## Version anchors and mismatch labels

- Destination runtime verified by Lane B/C: `frappe 15.106.0`, `erpnext 15.105.0`, `payments 0.0.1`, `webshop 0.0.1`, `locally_twisted 0.0.1`.
- Dispatch anchor was `frappe/erpnext:v15.105.0`; local container image reported `locally-twisted-erpnext:v15`, so downstream claims should carry `[VERSION-MISMATCH]` unless the image digest/source is resolved.
- Odoo source witness local module is `addons/locally_twisted` `19.0.2.15.0`; prior handoff warns production DB may still be `19.0.2.14.0`, so source parity remains `[VERSION-MISMATCH]` until resolved.

## Current conclusion

Native ERPNext/Frappe can receive the proof-slice ecommerce meaning safely when the `locally_twisted` contract layer is kept in charge: two product-page lanes, versioned line payload fields, source-backed dependency/add-on/pricing/media services, quote-first bridges, and fail-loud verifiers. Full catalog import/reimport and public launch remain blocked until missing lanes are rerun or explicitly marked `[NO EVIDENCE]` in synthesis, version mismatches are handled, and final import/public-state gates pass.

## Next safe actions

1. Rerun Lane A and Lane E artifact-first with the required `D:YYYY-MM-DD | Check:<source/date> | Confidence:<label>` first line and explicit `[NO EVIDENCE]` rule.
2. Rerun or accept Lane B's aggregate readiness `[LIVE-MISMATCH]` only after a clean top-level `product_page_architecture_readiness.py` run in the same intended ecommerce mode.
3. Run Lane F synthesis only after all lanes have named artifacts or are deliberately carried as `[NO EVIDENCE]` process failures.
4. Do not delete/reimport products, click admin-like Odoo URLs, or mutate authenticated systems for this audit without a fresh rollback/preflight.
