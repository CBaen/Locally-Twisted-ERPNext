# Witness State: Phase 5 Product Setup Operating Brand Source Contract

- Date: 2026-06-30
- Repo/path: `/home/guidingl/agent-worktrees/builtbycameron-lt/codex-20260630-lt-product-setup-brand-authority__phase5`
- Main goal: Add source-level Product Setup operating-brand authority controls so catalog automation can prove brand lane before mutation or repair.
- Trigger: Income-critical ecommerce architecture hardening after live Product Setup edits did not project to the customer-facing product page.
- Current stage: `follow-up-source-uniqueness`
- Current continuation: `source-authority-packet-reporting`
- Main agent owns: final source edits, verification, docs, scoped commit/push, and synthesis.
- Witness lanes:
  - Intent Witness: confirm this solves a real owner-management authority gap without pretending to fix live projection immediately.
  - Technical Witness: review schema/validation/apply-plan/verifier changes and catch migration/runtime risks.
- User intent summary: GL wants the shop rebuilt into a human-manageable ecommerce system where authorized backend users can manage products, prices, descriptions, photos, variants, add-ons, and options without calling a developer or AI agent for basic live updates.
- Clarification status: no blocking user question; GL granted standing approval for protective stronger contracts and asked not to stop unless approval is required.
- Questions asked / answers: none in this phase.
- Dangerous assumptions:
  - Assuming brand lane can be inferred from route, product group, or current public copy.
  - Treating a source schema change as live behavior repair.
  - Absorbing unrelated untracked three-brand boundary docs from the dirty shared checkout into this branch.
- Blocked assumptions:
  - Live ERPNext Product Setup records cannot be mutated in this phase.
  - Live website cache cannot be cleared in this phase.
  - Provider, DNS, payment, campaign, and customer-message actions are out of scope.
- Assumptions:
  - Allowed operating brand values for this source contract are `locally_twisted`, `commercial_balloon_decor`, and `memorial_balloons`, based on existing tracked decision text.
  - Existing Product Setups should default to `locally_twisted` only at source/schema level until an approved data migration or live mutation packet is prepared.
- Risks:
  - Custom DocType field changes require migration/update-site before live Desk sees them.
  - Validation can break existing tests if they construct minimal blueprints without the new required field.
  - Apply-plan output should expose authority without falsely claiming Item/Website Item persistence if those downstream fields do not yet exist.
- Truncation/artifact status: prior `rg` output was truncated but the decisive source files will be read directly in bounded ranges.
- Recovered source paths:
  - `apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_product_blueprint/lt_product_blueprint.json`
  - `apps/locally_twisted/locally_twisted/product_blueprint_validation.py`
  - `apps/locally_twisted/locally_twisted/product_blueprint_apply_plan.py`
  - relevant `scripts/verify/*product*blueprint*` files
- Recovered line ranges/chunks: source files read directly before edit; final implementation summarized in `phase-5-operating-brand-source-contract-2026-06-30.md`.
- Unverified or blocked spans: runtime Desk rendering and live ERPNext records are unverified by design in this no-deploy/no-live-mutation phase.
- Evidence checked:
  - Capability gate PASS.
  - Clean linked worktree from `origin/main` at `ecaefb6`.
  - Shared checkout has unrelated dirty files, so source edits are isolated here.
- Evidence missing:
  - Live Product Setup migration proof.
  - Owner Desk browser proof after migration.
  - Public route projection proof after cache clear/deploy.
- Open disagreements: critical witness warned that a source default can become fake evidence if future tools treat it as proved brand lane. Mitigation implemented: contract state is `source_declared`, not live proof.
- Decisions made:
  - Implement a source-level `operating_brand` field and validation contract first.
  - Add source-only active uniqueness guard for active statuses only. It blocks
    same-brand Product Setups that claim the same slug, target Item, or target
    Website Item, and runtime lookup fails closed on duplicate active matches.
  - Do not claim live/global active authority proof, route migration proof,
    live/public brand-lane proof, or database-level uniqueness from this guard.
  - Add first-class offline `source_authority` packet reporting for
    source-declared operating brand and same-brand source uniqueness.
  - Keep packet live proof, mutation approval, deploy approval, cache approval,
    and release readiness blocked unless a separate proof path exists.
  - Do not import untracked brand-boundary files from the shared checkout into this phase.
- Files/systems touched:
  - `apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_product_blueprint/lt_product_blueprint.json`
  - `apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_product_blueprint/lt_product_blueprint.py`
  - `apps/locally_twisted/locally_twisted/product_blueprint_validation.py`
  - `apps/locally_twisted/locally_twisted/product_blueprint_apply_plan.py`
  - `apps/locally_twisted/locally_twisted/product_setup_runtime.py`
  - `apps/locally_twisted/locally_twisted/seed/sync_product_blueprints_from_catalog.py`
  - `apps/locally_twisted/locally_twisted/verify/product_blueprint_contract.py`
  - `apps/locally_twisted/locally_twisted/verify/product_blueprint_release_smoke.py`
  - `apps/locally_twisted/locally_twisted/verify/product_page_runtime_contract.py`
  - `scripts/verify/product_blueprint_contract.py`
  - AI-facing docs in this workstream, handoff, queue, decisions, and capability notes.
- Verification planned:
  - Product Blueprint schema/validation verifier.
  - Python compile for changed Python modules.
  - Focused tests/verifiers discovered in repo.
  - Leak/forbidden-term scan over changed files.
- Verification completed:
  - `python -m py_compile apps/locally_twisted/locally_twisted/product_blueprint_validation.py apps/locally_twisted/locally_twisted/product_blueprint_apply_plan.py apps/locally_twisted/locally_twisted/product_setup_runtime.py apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_product_blueprint/lt_product_blueprint.py apps/locally_twisted/locally_twisted/seed/sync_product_blueprints_from_catalog.py apps/locally_twisted/locally_twisted/verify/product_blueprint_contract.py apps/locally_twisted/locally_twisted/verify/product_blueprint_release_smoke.py apps/locally_twisted/locally_twisted/verify/product_page_runtime_contract.py scripts/verify/product_blueprint_contract.py`
  - `python scripts/verify/product_blueprint_contract.py` passed 24 tests.
  - `git diff --check`
  - Changed-file forbidden-term scan returned no matches.
- Follow-up verification completed:
  - `python -m py_compile apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_product_blueprint/lt_product_blueprint.py apps/locally_twisted/locally_twisted/product_setup_runtime.py scripts/verify/product_blueprint_contract.py`
  - `python scripts/verify/product_blueprint_contract.py` passed 25 tests.
  - `git diff --check`
- Source-authority packet continuation verification completed:
  - `python -m py_compile scripts/dev/lt_product_setup_authority_packet_report.py scripts/dev/lt_live_readonly_catalog_authority_audit.py scripts/dev/lt_live_readonly_product_api_audit.py scripts/verify/product_setup_authority_packet_contract.py scripts/verify/product_setup_authority_parity_contract.py`
  - `python scripts/verify/product_setup_authority_packet_contract.py` passed 5 tests.
  - Full old saved catalog authority packet report exited `1` with 47 blocked products and 265 blockers.
  - Old `large-head-missionary` authority packet report exited `1` with seven blockers.
  - Packet-aware parity verifier failed the old `large-head-missionary` packet with seven blockers.
- Active agent/session ids:
  - Intent witness `019f180a-6e44-7d51-b350-3354cb6ff506`
  - Technical witness `019f180a-abc9-7fa1-94b6-62653aa2a432`
  - Critical witness `019f180b-33eb-7a01-bd30-c45154a30c1c`
  - Follow-up technical witness `019f1813-71ad-7352-b769-a1979c926884`
  - Follow-up critical witness `019f1813-8da4-7211-8e14-f25f58c908c0`
  - Source packet technical witness `019f1820-6823-7292-911d-fb58b7240be3`
  - Source packet critical witness `019f1820-7fdc-7e70-8541-dc1b4fe9f3b9`
- Cleanup needed: close spawned agents; run process hygiene before final.
- Cleanup status: follow-up technical and critical witnesses were closed after
  reporting. Earlier Phase 5 witness IDs from the pre-follow-up packet were
  already unavailable in the current runtime when close was attempted. Source
  packet technical and critical witnesses were closed after reporting.
- Runtime brand-aware lookup continuation verification completed:
  - Intent/risk witness `019f1855-f451-7da0-8cd7-f2909370d142`
    confirmed the phase must block wrong-brand runtime authority and must not
    claim live projection repair.
  - Technical witness `019f1856-0905-7d61-9095-bea6df278dfd` identified
    Product Setup resolver call sites, the old gallery/media shortcut, and the
    target-item ambiguity fallthrough risk.
  - Implemented source-only runtime lookup using explicit or source-declared
    Website Item `operating_brand`.
  - Added Website Item `operating_brand` and
    `operating_brand_authority_state` fields to `sync_commerce_rules` and
    registered patch `sync_product_setup_brand_runtime_fields_20260630`.
  - `python -m py_compile apps/locally_twisted/locally_twisted/product_setup_runtime.py apps/locally_twisted/locally_twisted/api/product_setup.py apps/locally_twisted/locally_twisted/product_options.py apps/locally_twisted/locally_twisted/seed/sync_commerce_rules.py apps/locally_twisted/locally_twisted/patches/sync_product_setup_brand_runtime_fields_20260630.py scripts/verify/product_blueprint_contract.py`
  - `python scripts/verify/product_blueprint_contract.py` passed 26 tests.
  - `git diff --check`
- Owner-visible runtime authority blocker continuation verification completed:
  - Intent/risk witness `019f1860-5060-7ec2-8358-7eddf1155bd2` confirmed the
    owner-facing blocker should say Product Setup cannot be treated as ready
    because the site cannot safely tell which brand/product setup controls the
    public product.
  - Technical witness `019f1860-7414-7012-9d4e-74a4b49c8f80` recommended
    controller-level runtime row checks because the guard depends on Website
    Item metadata and target identity, not pure in-record validation alone.
  - Implemented `product_blueprint_runtime_authority.py` and wired active
    source-state blockers into `LT Product Blueprint.validate`.
  - Active Product Setup saves now block when linked Website Item runtime brand
    fields are missing, mismatched, not `source_declared`, or target identity
    disagrees. Drafts and new preview plans without existing Website Items are
    not blocked by this guard.
  - `python -m py_compile apps/locally_twisted/locally_twisted/product_blueprint_runtime_authority.py apps/locally_twisted/locally_twisted/locally_twisted/doctype/lt_product_blueprint/lt_product_blueprint.py scripts/verify/product_blueprint_contract.py`
  - `python scripts/verify/product_blueprint_contract.py` passed 27 tests.
- Resume instruction: Continue source-only ecommerce Product Setup hardening in
  the isolated worktree. Phase 8 owner-visible runtime authority blockers are
  complete locally. Next safe slice is variant-axis classification/collapse
  planning, starting with Birthday Deliveries, plus row-level rollback target
  capture before any catalog mutation. Do not deploy, mutate live ERPNext
  records, clear cache, or touch provider/payment/DNS/customer-message paths.
- Variant-axis classification continuation verification completed:
  - Intent/risk witness `019f1868-6a43-7df1-b3f2-b43c677d1ed3` confirmed
    Phase 9 must remain source-only planning evidence, Birthday Deliveries must
    stay blocked for mutation, and collapse plans must preserve cart/order/
    document/payment identity before any future write.
  - Technical witness `019f1868-78e8-7bc1-9bb4-6e9b24731379` identified the
    existing authority packet, projection preview, runtime schema, apply-plan,
    validation, and source-era axis projection code as the right support
    surfaces. It also flagged that `Add Bouquet` should not remain SKU-defining
    by default merely because it changes price; it needs a clear add-on/runtime
    pricing decision before mutation.
  - Implemented `lt_product_setup_variant_axis_classification_report.py` and
    `product_setup_variant_axis_classification_contract.py`.
  - Saved Birthday Deliveries artifact result: current 2,430 variants / 2,430
    Item Prices; candidate no-write model has 3 SKU variants from `Delivery
    Size`, `Delivery themes` as configuration payload, and `Add Foil Number` /
    `Add Bouquet` as paid add-on candidates.
  - The report intentionally exits nonzero with
    `current_sku_axes_need_reclassification` and
    `variant_explosion_requires_no_write_plan`.
  - `python -m py_compile scripts/dev/lt_product_setup_variant_axis_classification_report.py scripts/verify/product_setup_variant_axis_classification_contract.py`
  - `python scripts/verify/product_setup_variant_axis_classification_contract.py`
    passed 2 tests.
- Resume instruction: Continue source-only ecommerce Product Setup hardening in
  the isolated worktree. Phase 9 variant-axis classification is complete
  locally. Next safe slice is Birthday Deliveries dependency/rollback target
  capture and no-write replacement model design. Do not deploy, mutate live
  ERPNext records, clear cache, touch provider/payment/DNS/customer-message
  paths, or disable/delete/rename/collapse current variants from Phase 9 output
  alone.
- Dependency/rollback capture continuation verification completed:
  - Technical builder `019f1896-f9d8-7d41-a450-1b1c9ac734fd` implemented the
    source-only offline dependency/rollback report and verifier.
  - Documentation builder `019f1897-1775-7f70-a3c7-7c52e78ce64d` wrote the
    Phase 10 receipt/plan.
  - Critical verifier `019f1897-2d07-7be0-9e77-ea346934901a` wrote the Phase 10
    overclaim and blocker review.
  - Implemented `lt_product_setup_dependency_rollback_report.py` and
    `product_setup_dependency_rollback_contract.py`.
  - Saved Birthday Deliveries artifact result: row-level saved-artifact
    rollback rows included for 2,430 variants, 2,430 Item Prices, four Product
    Setup option rows, and nine media/gallery/pointer rows.
  - The report intentionally exits nonzero with 20 blockers because live route
    proof, brand-lane proof, historical references, File/slideshow references,
    add-on/runtime proof, and mutation approval remain missing.
  - `python -m py_compile scripts/dev/lt_product_setup_dependency_rollback_report.py scripts/verify/product_setup_dependency_rollback_contract.py`
  - `python scripts/verify/product_setup_dependency_rollback_contract.py`
    passed 3 tests.
- Resume instruction: Continue source-only ecommerce Product Setup hardening in
  the isolated worktree. Phase 10 dependency/rollback target capture is
  complete locally as blocked planning evidence. Next safe slice is Birthday
  Deliveries no-write replacement model design. Do not deploy, mutate live
  ERPNext records, clear cache, touch provider/payment/DNS/customer-message
  paths, or disable/delete/rename/collapse current variants from Phase 9/10
  output alone.

## Route Record

Mode: `triadic-review` plus witnessed construction
Decision needed: how to add the smallest source-level operating-brand authority contract that blocks guessing without pretending live projection is fixed.
Scope owner: Locally Twisted child/client repo.
System/project/runtime classification: single project, source-only; no runtime mutation.
Allowed actions: edit Product Setup source schema, validation/apply-plan code, verifiers, and AI-facing docs in this isolated worktree; run local static/compile verifiers.
Forbidden actions: deploy, cache clear, ERPNext/Frappe DB mutation, live API mutation, provider/payment/DNS/Frappe Cloud changes, customer messages, secrets, product-scope decisions, and absorbing unrelated dirty shared-checkout files.
Evidence bar: checked source diff, focused verifier success, compile success, docs updated with exact limitations, and independent witness review.
Stop condition: stop before live migration/projection/cache/deploy or if validation requires a business decision beyond the three already tracked operating brands.
Lane owner: Codex main agent with two witness lanes.
Artifact path: this file plus the Phase 5 closeout note under `workstreams/ecommerce-operator-hardening-2026-06-30/`.
Coordination path: `/home/guidingl/agent-coordination/LIVE-BOARD.md` and `/home/guidingl/agent-coordination/SESSION-REGISTRY.md`.
File/system ownership: isolated worktree branch `codex/lt-product-setup-brand-authority-20260630`; shared main checkout remains untouched.
Dependencies: existing Product Setup authority docs and tracked three-brand decision text.
Anti-overlap rule: do not touch Meta, portal, paperwork, checkout UI, marketing tracking, or untracked brand-boundary files.
Escalation trigger: need for live mutation, data migration execution, provider/deploy/cache action, product-scope choice, or missing operating-brand business values.
