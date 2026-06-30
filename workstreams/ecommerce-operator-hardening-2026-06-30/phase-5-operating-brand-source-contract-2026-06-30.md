# Phase 5 Operating Brand Source Contract

Date: 2026-06-30

Status: source-only Product Setup brand-lane authority contract implemented and verified, with follow-up source guard for same-brand active Product Setup ambiguity. No deploy, cache clear, live ERPNext mutation, provider/payment/DNS/Frappe Cloud change, customer message, or product-scope decision occurred.

## Purpose

Remove one unsafe ambiguity from Product Setup authority packets: every Product Setup must declare which operating brand lane owns the product before later tooling can reason about public routes, payment/document identity, files/media, portals, automation, or release packets.

This phase does not prove live brand lane. It creates source authority only.

## Triad / Witness Result

Review type: real multi-agent triad / witnessed work.

Convergence:

- Intent witness agreed `operating_brand` is a real prerequisite for owner-manageable ecommerce.
- Technical witness recommended a required Product Setup field, validation fail-closed behavior, dry-run plan propagation, runtime schema propagation, and no schema-version bump.
- Critical witness warned that a populated field must not become fake proof. A defaulted source value must be treated as `source_declared`, not `proved`.

Decision:

- Add required `operating_brand` to `LT Product Blueprint`.
- Allowed values are `locally_twisted`, `commercial_balloon_decor`, and `memorial_balloons`.
- Contract state is `source_declared` for valid source values, `missing` when absent, and `invalid` when outside the allowed list.
- Do not add or imply `brand_lane_proved`, live projection approval, active uniqueness proof, or repair readiness from this field alone.
- Follow-up witness review approved a source-only active uniqueness guard for
  active statuses only. It blocks same-brand active Product Setups that claim
  the same source slug, target Item, or target Website Item. This is not global
  live active-authority proof.

## Source Changes

- `apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_product_blueprint/lt_product_blueprint.json`
  - Adds required `Operating Brand` Select field in the Product Setup basics section.
  - Default is `locally_twisted` for source-created records.
- `apps/locally_twisted/locally_twisted/product_setup_runtime.py`
  - Adds shared `OPERATING_BRAND_OPTIONS`.
  - Adds `operating_brand_authority_state`.
  - Includes operating brand authority in the runtime Product Setup schema.
- `apps/locally_twisted/locally_twisted/product_blueprint_validation.py`
  - Reads Product Setup `operating_brand`.
  - Fails validation when the value is missing or outside the allowed lanes.
  - Adds `operating_brand` and `operating_brand_authority_state` to validation contract output.
- `apps/locally_twisted/locally_twisted/product_blueprint_apply_plan.py`
  - Carries operating brand authority into dry-run planned Item and Website Item metadata.
- `apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_product_blueprint/lt_product_blueprint.py`
  - Includes operating brand in Desk preview payloads.
  - Blocks saving active Product Setup authority when another active Product Setup in the same source-declared operating brand already claims the same slug, target Item, or target Website Item.
- `apps/locally_twisted/locally_twisted/product_setup_runtime.py`
  - Runtime active lookup no longer silently picks the most recently modified Product Setup when multiple active records match the same runtime key; it logs the ambiguity and returns no setup.
- `apps/locally_twisted/locally_twisted/seed/sync_product_blueprints_from_catalog.py`
  - Adds source-declared `locally_twisted` for generated Product Setup records from current LT catalog sync.
- `scripts/verify/product_blueprint_contract.py`
  - Verifies the DocType field, allowed values, fail-closed validation, dry-run propagation, and runtime schema propagation.
- `apps/locally_twisted/locally_twisted/verify/product_blueprint_contract.py`
- `apps/locally_twisted/locally_twisted/verify/product_blueprint_release_smoke.py`
- `apps/locally_twisted/locally_twisted/verify/product_page_runtime_contract.py`
  - Add explicit operating-brand values to Product Setup fixtures so runtime verifiers do not depend on implicit Frappe defaults.

## Verification

Commands passed:

```bash
python -m py_compile apps/locally_twisted/locally_twisted/product_blueprint_validation.py apps/locally_twisted/locally_twisted/product_blueprint_apply_plan.py apps/locally_twisted/locally_twisted/product_setup_runtime.py apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_product_blueprint/lt_product_blueprint.py apps/locally_twisted/locally_twisted/seed/sync_product_blueprints_from_catalog.py apps/locally_twisted/locally_twisted/verify/product_blueprint_contract.py apps/locally_twisted/locally_twisted/verify/product_blueprint_release_smoke.py apps/locally_twisted/locally_twisted/verify/product_page_runtime_contract.py scripts/verify/product_blueprint_contract.py
python scripts/verify/product_blueprint_contract.py
git diff --check
```

`product_blueprint_contract.py` ran 25 tests and passed.
Changed-file forbidden-term scan returned no matches.

Capability gate: PASS.

Loaded resources:

- `capabilities/INDEX.md`
- `capabilities/failures/product-setup-projection-authority-drift.md`
- `capabilities/recipes/erpnext-product-blueprint-authoring.md`
- `capabilities/recipes/erpnext-catalog-variant-price-parity.md`
- `capabilities/recipes/erpnext-ecommerce-receiving-architecture.md`
- `workstreams/ecommerce-operator-hardening-2026-06-30/protective-contracts.md`

## Not Fixed

This phase does not fix or prove:

- live Product Setup migration;
- owner Desk rendering after migration;
- public product-page price/copy/media projection;
- cache behavior;
- live/global active Product Setup uniqueness by target item/route/brand lane;
- runtime brand-aware lookup;
- database-level uniqueness constraints;
- rollback packet completeness;
- Item Price mutation or parity;
- cart/checkout/payment/document identity;
- customer-facing route proof;
- provider, DNS, Frappe Cloud, payment, or customer-message behavior.

## Next Safe Work

Continue Phase 1 source authority controls:

- make runtime Product Setup lookup brand-aware before cross-brand same-slug active setups are allowed;
- add owner-visible blocker reporting using the same blocker categories;
- start variant-axis classification on Birthday Deliveries before any variant-collapse or price repair write.

Completed follow-up:

- Phase 6 updated saved-artifact authority packet logic so `source_declared`
  operating brand and same-brand source uniqueness are reported separately from
  live proof.
- Phase 7 completed runtime brand-aware lookup.
- Phase 8 completed the first owner-visible runtime authority blockers in Desk.
  Current next safe work is variant-axis classification/collapse planning
  starting with Birthday Deliveries, plus rollback target capture before any
  catalog mutation.
