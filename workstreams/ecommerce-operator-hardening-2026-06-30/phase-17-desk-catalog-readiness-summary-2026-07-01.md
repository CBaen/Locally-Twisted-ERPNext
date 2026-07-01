# Phase 17 Desk Catalog Readiness Summary

Date: 2026-07-01

Status: source-only Desk summary surface complete.

## Scope

This phase added a read-only Product Setup Desk catalog readiness summary over
saved `LT Product Blueprint.validation_json` rows. It does not collect live
data and does not change Product Setup, Website Item, Item, Item Price,
provider, payment, DNS, cache, deploy, or customer-message state.

No live mutation was performed.

## Capability Gate

Capability gate: PASS.

Loaded resources:

- `capabilities/INDEX.md`
- `capabilities/recipes/erpnext-product-blueprint-authoring.md`
- `capabilities/failures/product-setup-projection-authority-drift.md`

## Files

- `apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_product_blueprint/lt_product_blueprint.py`
- `apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_product_blueprint/lt_product_blueprint.js`
- `scripts/verify/product_blueprint_contract.py`
- `workstreams/ecommerce-operator-hardening-2026-06-30/phase-17-desk-catalog-readiness-summary-2026-07-01.md`

## Behavior

The controller exposes `get_catalog_readiness_summary` for signed-in `System
Manager` or `Item Manager` users. It reads only these Product Setup fields:
`name`, `product_name`, `product_slug`, `target_item_code`,
`target_website_item`, `publish_status`, `validation_status`,
`validation_json`, and `modified`.

The summary parses saved validation JSON safely. Malformed or non-object JSON
becomes a blocked product row with a saved-packet read blocker. Product rows
carry clipped blockers, owner state, public-success flag count, live-apply flag
count, source/saved proof mode, saved evidence time, next owner step, developer
next step, developer-help flag, and false read-only approval fields.

Desk adds a `Show Catalog Readiness` button under Product Setup. The dialog
shows total products checked, blocked count, saved owner-state counts, public
success claim count, live publish/apply count, source/saved proof mode, and
the first blocked products with saved evidence time and next steps. It calls
only the read-only summary method.

## Verification

Commands run from the linked worktree:

```bash
python /home/guidingl/codex-framework/tools/capability_context_gate.py --cwd "$PWD" --task "Phase 17 source-only Product Setup Desk catalog readiness summary from saved validation_json rows" --loaded "capabilities/INDEX.md" --loaded "capabilities/recipes/erpnext-product-blueprint-authoring.md" --loaded "capabilities/failures/product-setup-projection-authority-drift.md"
```

Exit: `0`.

Focused verification for this phase:

```bash
python scripts/verify/product_blueprint_contract.py
python scripts/verify/product_setup_publish_readiness_contract.py
python scripts/verify/product_setup_catalog_readiness_contract.py
python scripts/verify/product_setup_release_packet_contract.py
python scripts/verify/product_setup_authority_packet_contract.py
python -m py_compile apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_product_blueprint/lt_product_blueprint.py scripts/verify/product_blueprint_contract.py
node --check apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_product_blueprint/lt_product_blueprint.js
python -m json.tool verifier-manifest.json
git diff --check
```

Exit: `0` for all. `product_blueprint_contract.py` ran 29 tests. The
publish-readiness, catalog-readiness, release-packet, and authority-packet
contracts also passed.

Covered: summary method/button exists, method reads `validation_json`, parse
errors become blocked rows, false approval fields are present, the catalog
dashboard does not call apply preview or apply endpoints, and the local apply
confirmation token remains server-only.

Forbidden ERP UI terms check against the changed files found no matches.

## Residual Risk

This is a source/Desk display surface over saved validation rows. It does not
prove current live catalog state, public routes, cart, checkout, payment,
documents, customer receipts, cache state, provider-hosted deploy state, or
rollback execution.

Saved validation JSON can be stale until the Product Setup row is revalidated.
A passing verifier proves the read-only summary contract; it does not approve
any write.
