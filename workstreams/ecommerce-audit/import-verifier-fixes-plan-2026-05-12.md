# Import Verifier Fixes Plan - 2026-05-12

## Goal

Fix the four reviewed import/verification failures so catalog import gates fail
loudly, rebuild from fresh source contracts, and prove color-drawer products
reach server-side checkout validation with real selected colors.

## Scope

Reviewed blockers:

- P1: add-on product contracts crash in
  `scripts/verify/catalog_purge_scope_dry_run.py` and the V1 import manifest
  generator because `AddOnContract` rejects add-on metadata fields.
- P2: `post_import_catalog_state.run()` reports `ok: True` even when included
  products are missing, unpublished, or unpriced.
- P2: `post_import_checkout_proof.js` fills the hidden compatibility color
  select instead of checking visible color choices, so `color_recipes` is not
  actually proven.
- P2: `product_import_readiness_gate.py` crashes while building the local command
  packet when no snapshot directory exists instead of returning the intended
  `fresh_catalog_snapshot` blocker.

Out of scope:

- Reworking the catalog import architecture.
- Submitting real guest orders or creating finance records.
- Changing product pricing, catalog content, or customer-facing copy.

## Plan-Deepen Outcome

Outcome: **Adjust**. The overall sequence is correct, but the first plan needed
four refinements after checking current source:

- Use the existing `scripts/verify/proof_product_contract.py` as the add-on
  metadata regression instead of adding a new one-off verifier.
- Keep add-on metadata in source/manifest contracts, but do not let browser cart
  payloads carry static add-on prices. Runtime checkout still prices add-ons from
  ERPNext `Item Price`.
- In the post-import state verifier, evaluate every included slug and distinct
  priced item coverage. Do not rely only on the five priority products.
- In the checkout proof, call
  `/api/method/locally_twisted.www.checkout.preview_checkout_totals` with the
  current Frappe response envelope (`json.message`) and a non-quote fulfillment
  path such as pickup at `West Jordan`.

## Plan-Deepen Notes

### Structure And Existing Verifiers

Evidence checked:

- `scripts/verify/proof_product_contract.py` already builds source product-page
  contracts for `unicorn-bouquet` and checks that `foil_number` exists.
- `scripts/verify/verifier_cli_contract.py` expects maintained Python verifiers
  to expose safe `--help` behavior.
- `scripts/verify/catalog_state_snapshot_contract.py` is a live artifact
  verifier, not a good no-snapshot unit regression because this machine already
  has `current-state-snapshot-2026-05-11-1050`.

Risks found:

- Adding several tiny new verifier files would make the verifier surface noisier
  than needed.
- Running `product_import_readiness_gate.py` on this machine will not prove the
  clean-checkout/no-snapshot case because a snapshot exists locally.

Plan adjustment:

- Update `proof_product_contract.py` for the add-on metadata regression.
- Add a small pure helper in `product_import_readiness_gate.py` and test that
  helper with a focused contract; do not depend on deleting or renaming snapshot
  folders.

Open question or escalation:

- None.

### Add-On Contract Data

Evidence checked:

- `addon_rules.py` returns `item_code`, `quantity_min`, `quantity_max`,
  `requires_value`, and `receipt_label` for the confirmed `Add Foil Number`
  axis.
- `models.py` currently defines `AddOnContract` without those fields.
- `source_builder.py` passes the whole rule dict to `AddOnContract(**row)`.
- A non-writing reproduction currently fails with
  `TypeError: AddOnContract.__init__() got an unexpected keyword argument
  'item_code'`.
- `product_page_runtime.py` owns runtime add-on pricing through
  `ADD_ON_ITEM_CONTRACTS` and ERPNext `Item Price`.

Risks found:

- Stripping unknown add-on fields would hide the contract that downstream
  checkout validation expects.
- Copying `unit_price` into browser cart payloads would conflict with the
  existing server-price-only rule.

Plan adjustment:

- Add fields to `AddOnContract` with safe defaults.
- Preserve those fields in the V1 manifest add-on section.
- Extend `proof_product_contract.py` so `unicorn-bouquet` proves
  `foil_number.item_code == "ADDON-FOIL-NUMBER"`, quantity bounds, required
  value behavior, and receipt label.
- Do not change runtime cart payload pricing behavior.

Open question or escalation:

- None.

### Post-Import Catalog State

Evidence checked:

- `post_import_catalog_state.py` currently returns `"ok": True` unconditionally.
- It only expands `_product_status()` for five priority slugs.
- `_product_status()` already exposes enough facts to fail on missing Website
  Item, unpublished Website Item, missing Item, disabled Item, and zero prices.
- The seed path creates template `Website Item` rows and variant/single-SKU
  `Item Price` rows, so post-import checks should look at all included slugs and
  distinct priced item codes.

Risks found:

- Checking only priority products can miss a broken included product.
- Comparing raw Item Price row count can be misleading if duplicate price rows
  exist. Distinct priced item code coverage is safer.
- A full exact sale-unit-to-ERPNext-variant mapping is not present in the
  manifest, so the first fix should not invent a brittle exact mapping.

Plan adjustment:

- Build `statuses_by_slug` for every included slug, not just priority products.
- Compute blocker lists from actual status facts:
  `missing_website_item_slugs`, `unpublished_website_item_slugs`,
  `missing_item_slugs`, `disabled_item_slugs`, and `unpriced_slugs`.
- Add manifest/count blockers:
  `website_items_included != included_count`,
  `item_templates_included != included_count`, and distinct priced item coverage
  below manifest source-ready sale-unit count.
- Keep `priority_products` as a highlighted subset, but do not use it as the
  only readiness proof.

Open question or escalation:

- None for this reviewed fix. A future stricter gate could add exact
  sale-unit-to-variant mapping if the manifest starts storing generated
  ERPNext item codes.

### Checkout Color Proof

Evidence checked:

- `item_configure.html` renders color drawers as
  `.lt-product__attr[data-display-type="color-drawer"]` with a hidden
  `.js-lt-color-hidden` select before visible `.js-lt-color-radio` checkboxes.
- `selectedColorRecipeRows()` builds `color_recipes` from checked visible color
  inputs.
- `selectedSaleUnitAttrs()` intentionally removes color-drawer axes from normal
  `selected_options`.
- `preview_checkout_totals()` is `allow_guest=True`, non-mutating, and calls
  `_resolve_sale_lines(cart_items)`.
- The checkout page reads the preview response through `json.message`.

Risks found:

- The existing proof picks the hidden select first and therefore does not prove
  visible colors or `color_recipes`.
- A direct server-preview assertion must unwrap `json.message`; checking the raw
  top-level JSON would be a false failure.
- Delivery can return `quote_required` depending on zip, so the proof should use
  a known non-quote path.

Plan adjustment:

- Branch selection by `data-display-type`.
- For color drawers, check the first visible enabled `.js-lt-color-radio`, wait
  for the hidden select to match that value, and record the selected color.
- After cart add, assert `line.configuration.color_recipes` contains the visible
  color and `selected_options` does not contain that color axis.
- Before accepting checkout summary, POST `items_json` to the preview endpoint
  with `fulfillment_method=pickup` and `pickup_location=West Jordan`; unwrap
  `json.message` and require `message.ok === true`.

Open question or escalation:

- None.

### No-Snapshot Readiness Gate

Evidence checked:

- `_snapshot_row()` already returns the intended `fresh_catalog_snapshot`
  blocker when no snapshot exists.
- `_local_only_command_packet()` currently calls
  `Path("<snapshot>").relative_to(ROOT)` when no snapshot exists.
- A non-writing reproduction confirms `Path("<snapshot>").relative_to(ROOT)`
  raises `ValueError` because the placeholder is not under the repo root.

Risks found:

- Current local state has a snapshot, so a normal gate run can mask the reviewed
  clean-checkout bug.
- Patching this only inside `_snapshot_row()` would not fix report construction
  because `_local_only_command_packet()` is built unconditionally.

Plan adjustment:

- Extract snapshot display path selection into a pure helper that accepts an
  optional list of snapshot paths for tests.
- Make the empty-list case return a placeholder string such as
  `<fresh current-state-snapshot-* required>`.
- Add a focused contract that calls the helper with an empty list and confirms
  no `ValueError`.

Open question or escalation:

- None.

## Implementation Order

### 1. Repair add-on contract serialization

Files:

- `apps/locally_twisted/locally_twisted/catalog_contract/models.py`
- `apps/locally_twisted/locally_twisted/catalog_contract/source_builder.py`
  (read/check; edit only if normalization is needed after the model fix)
- `scripts/verify/proof_product_contract.py`
- `scripts/verify/v1_legacy_source_erpnext_import_manifest.py`
- `scripts/verify/catalog_purge_scope_dry_run.py`

Steps:

1. Add the known optional add-on metadata fields to `AddOnContract` instead of
   dropping them:
   - `item_code`
   - `quantity_min`
   - `quantity_max`
   - `requires_value`
   - `receipt_label`
2. Keep defaults backward compatible so existing add-on contract readers do not
   have to supply every field.
3. Update the V1 manifest add-on serialization to preserve the new fields when
   present.
4. Extend `proof_product_contract.py` to assert the confirmed `foil_number`
   add-on keeps its ERPNext item code, quantity bounds, required value flag, and
   receipt label.
5. Run proof and artifact generators to prove they no longer read stale JSON:

```powershell
python scripts/verify/proof_product_contract.py
python scripts/verify/catalog_purge_scope_dry_run.py
python scripts/verify/v1_legacy_source_erpnext_import_manifest.py
```

Expected result:

- No `TypeError` for `AddOnContract.__init__`.
- Fresh purge-scope and V1 import artifacts are regenerated from current source
  data.

Regression proof:

- `proof_product_contract.py` builds `unicorn-bouquet` from the current source
  catalog and proves the add-on metadata survives in the resulting
  `ProductPageContract`.

### 2. Make post-import catalog state fail loudly

Files:

- `apps/locally_twisted/locally_twisted/verify/post_import_catalog_state.py`
- New focused contract verifier if needed:
  `scripts/verify/post_import_catalog_state_contract.py`

Steps:

1. Split the pass/fail decision into a small pure helper so missing products can
   be tested without a live database.
2. Treat these as blockers:
   - an included slug has no published `Website Item`;
   - an included slug has no enabled source `Item`;
   - an included slug has no price coverage;
   - included Website Item or Item counts do not match the manifest;
   - distinct priced item code coverage is below the manifest's source-ready
     sale-unit count;
   - priority products are not ready.
3. Evaluate every included slug; keep priority products only as a highlighted
   subset of the full result.
4. Return `ok: False` when any blocker exists.
5. Include machine-readable evidence fields such as `blockers`,
   `missing_included_slugs`, `unready_priority_products`, and current counts.
6. Keep successful output shape compatible with existing callers by retaining
   the current count and `priority` fields.

Regression proof:

```powershell
python scripts/verify/post_import_catalog_state_contract.py
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.verify.post_import_catalog_state.run
```

Expected result:

- The contract verifier proves a fake missing included slug returns `ok: False`.
- The live bench command returns `ok: True` only if the imported catalog is
  actually complete, published, and priced.

### 3. Exercise real color selections in checkout proof

Files:

- `scripts/verify/post_import_checkout_proof.js`
- Existing product configuration template and JS only if the proof exposes a
  real product-side bug:
  - `apps/locally_twisted/locally_twisted/templates/pages/item_configure.html`
  - `apps/locally_twisted/locally_twisted/public/js/lt_product_configure.js`

Steps:

1. Update `chooseFirstOptionForEachAttribute(page)` to branch on
   `data-display-type`.
2. For `color-drawer` attributes:
   - click the first visible enabled `.js-lt-color-radio`;
   - assert the hidden `.js-lt-color-hidden` bridge synchronizes afterward;
   - record the selected color value as a color recipe expectation.
3. For normal select attributes:
   - ignore hidden selects and select the first real enabled option.
4. After adding each color-drawer product to the cart, assert the cart line
   configuration contains `color_recipes` with the selected visible color.
5. Assert the color drawer axis is not falsely counted as a normal selected
   option.
6. Add a non-mutating server validation step through the checkout total preview
   API before accepting the checkout summary proof. Use pickup fulfillment:
   `fulfillment_method=pickup`, `pickup_location=West Jordan`, and assert
   `json.message.ok === true`.

Regression proof:

```powershell
node scripts/verify/post_import_checkout_proof.js
```

Expected result:

- Color products such as `7-butterfly-column` and `graduation-grab-n-go` have
  visible color selections in the browser proof.
- Cart JSON includes `color_recipes`.
- The server preview accepts the cart payload before the proof reaches the
  checkout summary.

### 4. Return a readiness blocker when no snapshot exists

Files:

- `scripts/verify/product_import_readiness_gate.py`
- New focused contract verifier if needed:
  `scripts/verify/product_import_readiness_gate_contract.py`

Steps:

1. Extract snapshot display-path selection into a small helper.
2. When no `current-state-snapshot-*` directory exists, return a placeholder
   label for the local command packet instead of calling `.relative_to(ROOT)` on
   `Path("<snapshot>")`.
3. Preserve the existing `_snapshot_row()` blocker behavior:
   `fresh_catalog_snapshot`.
4. Add a focused no-snapshot regression check that proves report construction
   does not crash when the snapshot list is empty.

Regression proof:

```powershell
python scripts/verify/product_import_readiness_gate_contract.py
python scripts/verify/product_import_readiness_gate.py
```

Expected result:

- A clean checkout with no snapshot returns a report containing the
  `fresh_catalog_snapshot` blocker.
- The readiness gate exits through its normal fail-loud path instead of raising
  `ValueError`.

## Final Verification

Run the smallest complete verifier set after implementation:

```powershell
python scripts/verify/product_import_readiness_gate_contract.py
python scripts/verify/post_import_catalog_state_contract.py
python scripts/verify/proof_product_contract.py
python scripts/verify/catalog_purge_scope_dry_run.py
python scripts/verify/v1_legacy_source_erpnext_import_manifest.py
python scripts/verify/product_import_readiness_gate.py
docker exec locally-twisted-erpnext-v15-backend-1 bench --site frontend execute locally_twisted.verify.post_import_catalog_state.run
node scripts/verify/post_import_checkout_proof.js
git diff --check -- apps/locally_twisted/locally_twisted/catalog_contract/models.py apps/locally_twisted/locally_twisted/catalog_contract/source_builder.py apps/locally_twisted/locally_twisted/verify/post_import_catalog_state.py scripts/verify/catalog_purge_scope_dry_run.py scripts/verify/v1_legacy_source_erpnext_import_manifest.py scripts/verify/post_import_checkout_proof.js scripts/verify/product_import_readiness_gate.py
```

If `product_import_readiness_gate.py` returns nonzero because it correctly finds
real current blockers, treat that as a valid fail-loud result and report the
blocker list instead of calling it a pass.

## Documentation Closeout

Update only after the verifiers above run:

- `scripts/README.md` with any new contract verifier commands.
- `workstreams/ecommerce-audit/product-import-hardening-gate-2026-05-11.md`
  with the final evidence.
- `workstreams/ecommerce-audit/post-import-checkout-launch-closeout-2026-05-11.md`
  with the final checkout proof evidence.
- `locally-twisted-queue.md` if these review blockers change the active queue
  state.

## Risks

- The artifact generators may rewrite existing JSON or Markdown outputs. Review
  those diffs separately so generated updates do not hide source-code changes.
- The live post-import catalog state verifier depends on the running ERPNext
  database. If the local stack is down, finish the pure contract tests first and
  mark live verification blocked until the stack is available.
- The checkout proof should use preview validation, not order submission, so the
  proof stays non-mutating.
