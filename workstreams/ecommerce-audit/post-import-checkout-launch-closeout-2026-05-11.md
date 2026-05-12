D:2026-05-11 | Check:local ERPNext/Frappe v15 evidence | Confidence:[LOCAL-PROOF]
# Post-Import Checkout Launch Closeout

This is the current agent-facing closeout for the local ecommerce checkout slice.
Use it before reopening old pause-centric or bouquet-only handoffs.

## Current Product Scope

- Corrected product set: 48 kept products / 5 owner-explicit Classic exclusions.
- Owner-explicit excluded slugs:
  - `classic-organic-balloon-garland`
  - `classic-arch`
  - `classic-column`
  - `classic-organic-columns`
  - `classic-organic-arch`
- Excluded Classic products are not launch blockers; they remain quote-first.
- Current product records are the local ERPNext import/proof set, not final real catalog approval for public launch copy, merchandising, or seasonal truth.

## Local Import Result

Artifact: `audits/odoo-erpnext-migration-audit-2026-05-08/29-local-destructive-import-result.json`.
Final browser proof summary artifact:
`audits/odoo-erpnext-migration-audit-2026-05-08/30-post-import-checkout-proof-result.json`.

- Scope: local ERPNext container/site `frontend` only.
- Frappe Cloud/live touched: no.
- Command exit: 0.
- Import summary: 48 products seeded, 48 already present, 0 errors, 0 missing images/groups.
- Important caveat: the approved local run exercised the guarded write/import path by upserting existing records. It is not evidence of a full delete/recreate transcript for every product row.
- Post-import counts in the artifact: 48 included products, 5 excluded products, 48 included Website Items, 48 included Item templates, 6,894 included variants, 6,928 included Item Prices.

## Priority Proof Products

The final checkout browser proof covered these products end to end:

| Product | Slug | Proof status |
|---|---|---|
| Easter Balloon Cups | `easter-balloon-cups` | PASS: options, image swap, price, cart line preservation, cart, checkout summary |
| 7' Butterfly Column | `7-butterfly-column` | PASS: visible color drawer resolves to `7-butterfly-column-REF`, records `latex colors = Reflex Champage` in `color_recipes`, price $120, cart, checkout summary |
| Graduation Grab n Go | `graduation-grab-n-go` | PASS: visible color drawer resolves to `graduation-grab-n-go-REF`, records `latex colors = Reflex Champage` in `color_recipes`, price $85, cart, checkout summary |
| 6' Graduation stands | `6-graduation-stands` | PASS: variant option resolves to `6-graduation-stands-CON`, price $45, image swap, cart, checkout summary |
| Unicorn Bouquet | `unicorn-bouquet` | PASS: bouquet-size option resolves to `unicorn-bouquet-SMA`, price $35, image swap, cart, checkout summary |

Final browser proof command:

```powershell
& "C:\Program Files\nodejs\node.exe" scripts/verify/post_import_checkout_proof.js
```

Result:

```text
[POST IMPORT CHECKOUT PROOF] PASS report=C:\Users\baenb\projects\Built_by_Cameron\_CLIENTS\locally-twisted\output\playwright\post-import-checkout-proof.json
```

The proof report is ignored runtime evidence under `output/`; rerun the command when fresh evidence is needed.

2026-05-12 regression update: the proof now selects visible color drawer
checkboxes instead of the hidden compatibility select, asserts cart
`configuration.color_recipes`, and calls the non-mutating
`preview_checkout_totals` API with pickup at `West Jordan` before accepting the
checkout summary. Fresh proof artifact showed server preview `ok: true`,
subtotal `$298.00`, tax `$22.20`, and total `$320.20`.

## Backend Contracts

Current green backend contracts for this slice:

```powershell
python scripts/verify/product_import_readiness_gate.py --report output/product-import-readiness-gate.json
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.verify.post_import_catalog_state.run
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.verify.direct_checkout_target_contract.run
python scripts/verify/cart_checkout_contract.py
```

Expected current evidence:

- `product_import_readiness_gate`: PASS with 12 pass, 0 warnings, 0 blockers.
- `post_import_catalog_state`: PASS with 48 included / 5 excluded, all included products ready, and empty blocker lists.
- `direct_checkout_target_contract`: PASS for 7' Butterfly Column, Graduation Grab n Go, and 6' Graduation stands; Classic exclusions remain quote-first.
- `cart_checkout_contract`: PASS, including configured line-key preservation and Unicode/browser line-key parity.

## Remaining Caveats

- 8 included products have review-only add-on axes. They are protected by quote-first fallback, and the import gate now blocks if any of those add-ons leaks onto a direct-checkout product.
- The five owner-explicit Classic exclusions remain quote-first.
- The local approved import proved guarded upsert/write behavior, not a full delete/recreate transcript.
- The repo worktree is shared and dirty; do not use broad staging or broad cleanup.
- Frappe Cloud/live deployment, live Stripe, DNS, webhook setup, and real payment tests are separate release gates.

## Next Agent Rules

1. Do not restore blanket cups/high-variant/bouquet-only exclusions.
2. Do not describe ecommerce pause as the target state for this slice.
3. Use the corrected 48/5 manifest and the executable checkout capability rule.
4. Re-run the final browser proof and backend contracts above before claiming a fresh launch-ready state.
5. Keep final real catalog truth behind the separate catalog approval/import gate.
